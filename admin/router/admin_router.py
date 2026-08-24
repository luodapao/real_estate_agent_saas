"""
软商用户路由 - 平台管理入口
业务逻辑：
1. 平台超级管理员（tenant_id=0, user_type=0）：创建租户、管理租户、创建超级用户
2. 认证接口（公开）：登录、登出、刷新令牌、修改密码、预登录、长轮询等待登录
3. 不开放自主注册，由超级用户创建账号
"""
import uuid
import json
import asyncio
import time
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from core.db_base import get_db
from core.redis_base import redis_client
from admin.service.user_service import UserService
from admin.service.tenant_service import TenantService
from admin.service.log_service import LogService
from admin.schemas.user_schemas import (
    LoginRequest, LoginResponse, ChangePasswordRequest,
    RefreshTokenRequest, PlatformUserCreate, PlatformUserUpdate,
    UserCreate, UserResponse, UserDetailResponse,
    PrepareLoginReq, PrepareLoginResp, WaitLoginReq
)
from admin.schemas.tenant_schemas import (
    TenantCreate, TenantUpdate, TenantResponse, TenantListResponse
)
from config.exception import success_response, error_response
from config.constants import LOGIN_TYPE
from core.auth_deps import require_platform_admin


# ========== 主路由 ==========
router = APIRouter(prefix="/api/admin", tags=["软商用户管理"])


# ========== 认证接口（公开）==========

@router.post("/prepare-login", summary="预登录（生成一次性登录票据）", response_model=PrepareLoginResp)
async def prepare_login(req: PrepareLoginReq):
    """预登录接口，生成一次性票据 loginTicket（UUID）并返回登录页URL"""
    try:
        login_ticket = str(uuid.uuid4())
        expire_seconds = req.expireSeconds or 600

        ticket_data = {
            "mcpSessionId": req.mcpSessionId,
            "status": "pending",
            "token": None
        }

        redis_client.setex(
            f"login:ticket:{login_ticket}",
            expire_seconds,
            json.dumps(ticket_data)
        )

        # 公网地址，默认端口8000
        login_url = f"http://14.103.221.98:8000/login?ticket={login_ticket}"

        return success_response(data={
            "loginUrl": login_url,
            "ticket": login_ticket
        })
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/login", summary="用户登录", response_model=LoginResponse)
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录接口（平台超级管理员和租户管理员通用）"""
    try:
        agent_identifier = request.headers.get('X-Agent-Identifier', 'default')
        ip = request.client.host if request.client else "unknown"
        result = UserService.login(db, login_data.account, login_data.password, agent_identifier, ip)

        # 如果登录请求携带了 ticket（MCP扫码登录场景）
        ticket = login_data.ticket
        if ticket:
            # 查询票据
            raw = redis_client.get(f"login:ticket:{ticket}")
            if raw:
                ticket_data = json.loads(raw)
                biz_token = result.get('access_token')
                ticket_data["status"] = "success"
                ticket_data["token"] = biz_token
                # 保留300秒后过期，给长轮询留时间
                redis_client.setex(f"login:ticket:{ticket}", 300, json.dumps(ticket_data))
                # 通知：使用redis pubsub唤醒长轮询
                redis_client.publish(f"login_notify:{ticket}", json.dumps(ticket_data))

        # 记录登录日志
        LogService.add_login_log(db, result['user']['tenant_id'], result['user']['user_id'],
                               login_data.account, LOGIN_TYPE['NORMAL'], 1,
                               "登录成功", ip)

        return success_response(data=result)
    except Exception as e:
        # 登录失败：不更新 Redis ticket 状态，保持 pending，允许用户在浏览器重试
        # （只有登录成功才写 success + publish，否则 MCP 侧会立即拿到 failed 终态，无法再重试）

        # 记录登录失败日志
        ip = request.client.host if request.client else "unknown"
        LogService.add_login_log(db, 0, 0, login_data.account,
                               LOGIN_TYPE['NORMAL'], 0, str(e), ip)
        return error_response(5000, str(e))


@router.post("/wait-login", summary="长轮询等待登录结果")
async def wait_login(req: WaitLoginReq):
    """长轮询接口：优先 Redis Pub/Sub 等待，超时降级轮询"""
    ticket = req.ticket
    timeout = req.timeout or 30
    timeout = min(max(timeout, 5), 60)

    # 先快速检查一次，避免已登录的情况下还要等
    raw = redis_client.get(f"login:ticket:{ticket}")
    if raw:
        ticket_data = json.loads(raw)
        # 只有 status == success 才视为终态，立即返回并删除一次性票据
        # 其它状态（pending / 历史残留的 failed）都继续等待，允许用户在登录页重试多次
        if ticket_data["status"] == "success":
            redis_client.delete(f"login:ticket:{ticket}")
            return success_response(data=ticket_data)
    else:
        return error_response(4000, "链接已过期，请重新在AI窗口发起登录")

    loop = asyncio.get_event_loop()

    def _sync_subscribe_and_wait():
        """同步订阅，在子线程中执行，避免阻塞事件循环"""
        try:
            raw_client = redis_client.get_client()
            if not raw_client:
                return None
            pubsub = raw_client.pubsub()
            channel = f"login_notify:{ticket}"
            pubsub.subscribe(channel)
            start_time = time.time()
            try:
                while True:
                    elapsed = time.time() - start_time
                    remaining = timeout - elapsed
                    if remaining <= 0:
                        break
                    message = pubsub.get_message(timeout=min(remaining, 2.0))
                    if message and message.get("type") == "message":
                        try:
                            return json.loads(message.get("data"))
                        except Exception:
                            return message.get("data")
            finally:
                try:
                    pubsub.unsubscribe(channel)
                    pubsub.close()
                except Exception:
                    pass
        except Exception:
            return None
        return None

    try:
        sub_result = await asyncio.wait_for(
            loop.run_in_executor(None, _sync_subscribe_and_wait),
            timeout=timeout + 2
        )
    except asyncio.TimeoutError:
        sub_result = None

    # 如果 pubsub 收到结果：只有 status == success 才立即终态返回并消费票据
    # 否则（历史残留的 failed 等）不返回，继续走降级轮询等待用户重试登录成功
    if sub_result is not None:
        ticket_data = sub_result if isinstance(sub_result, dict) else {}
        if isinstance(sub_result, str):
            try:
                ticket_data = json.loads(sub_result)
            except Exception:
                ticket_data = {}
        if ticket_data.get("status") == "success":
            redis_client.delete(f"login:ticket:{ticket}")
            return success_response(data=ticket_data)

    # Pub/Sub 未收到或未等到成功，降级为定期检查 Redis Key
    start_time = time.time()
    check_interval = 1.0
    while (time.time() - start_time) < timeout:
        raw = redis_client.get(f"login:ticket:{ticket}")
        if not raw:
            return error_response(4000, "链接已过期，请重新在AI窗口发起登录")
        ticket_data = json.loads(raw)
        # 只把成功当作终态返回；其余（pending/failed）继续等
        if ticket_data["status"] == "success":
            redis_client.delete(f"login:ticket:{ticket}")
            return success_response(data=ticket_data)
        await asyncio.sleep(check_interval)

    # 超时返回当前状态
    raw = redis_client.get(f"login:ticket:{ticket}")
    if not raw:
        return error_response(4000, "链接已过期，请重新在AI窗口发起登录")
    ticket_data = json.loads(raw)
    return success_response(data=ticket_data)


@router.post("/refresh-token", summary="刷新令牌")
async def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """刷新访问令牌接口"""
    try:
        result = UserService.refresh_token(db, data.refresh_token)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/logout", summary="用户登出")
async def logout(request: Request, db: Session = Depends(get_db)):
    """用户登出接口"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        UserService.logout(db, token)
        return success_response(message="登出成功")
    except Exception as e:
        return error_response(str(e))


@router.post("/change-password", summary="修改密码")
async def change_password(request: Request, data: ChangePasswordRequest, db: Session = Depends(get_db)):
    """修改密码接口（所有已登录用户）"""
    try:
        user_info = request.state.user_info
        UserService.change_password(db, user_info['user_id'], data.old_password, data.new_password)

        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'],
                                    user_info['login_name'], "系统管理", "POST",
                                    "/api/admin/change-password", str(data.dict()), 1,
                                    "修改密码成功", request.client.host if request.client else "unknown")

        return success_response(message="密码修改成功")
    except Exception as e:
        return error_response(str(e))


# ========== 平台管理路由组（仅平台超级管理员）==========
platform_router = APIRouter(prefix="/platform", tags=["平台管理"])


# 平台超级用户管理（放开鉴权，用于初始化平台超级账号）
@platform_router.post("/users", summary="创建平台超级用户", response_model=UserResponse)
async def create_platform_user(request: Request, data: PlatformUserCreate,
                               db: Session = Depends(get_db)):
    """创建平台超级用户（开放注册，用于初始化平台超级账号）"""
    try:
        result = UserService.create_platform_user(db, data)

        # 记录操作日志
        LogService.add_operation_log(db, 0, 0,
                                    data.account, "系统管理", "POST",
                                    "/api/admin/platform/users", str(data.model_dump()), 1,
                                    "创建平台超级用户成功", request.client.host if request.client else "unknown")

        return success_response(data=result, message="创建成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.get("/users", summary="分页查询平台超级用户列表")
async def get_platform_user_list(request: Request, user_name: Optional[str] = None,
                                 login_name: Optional[str] = None, status: Optional[int] = None,
                                 page: int = 1, size: int = 10, db: Session = Depends(get_db),
                                 admin_info: dict = Depends(require_platform_admin)):
    """分页查询平台超级用户列表（仅平台超级管理员）"""
    try:
        result = UserService.get_platform_user_list(db, user_name, login_name, status, page, size)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.get("/users/{user_id}", summary="查询平台超级用户详情", response_model=UserDetailResponse)
async def get_platform_user(user_id: int, db: Session = Depends(get_db),
                            admin_info: dict = Depends(require_platform_admin)):
    """查询平台超级用户详情（仅平台超级管理员）"""
    try:
        result = UserService.get_user(db, user_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.put("/users/{user_id}", summary="更新平台超级用户", response_model=UserResponse)
async def update_platform_user(request: Request, user_id: int, data: PlatformUserUpdate,
                               db: Session = Depends(get_db),
                               admin_info: dict = Depends(require_platform_admin)):
    """更新平台超级用户（仅平台超级管理员）"""
    try:
        result = UserService.update_platform_user(db, user_id, data)

        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'],
                                    admin_info['login_name'], "系统管理", "PUT",
                                    f"/api/admin/platform/users/{user_id}", str(data.model_dump()), 1,
                                    "更新平台超级用户成功", request.client.host if request.client else "unknown")

        return success_response(data=result, message="更新成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.delete("/users/{user_id}", summary="删除平台超级用户")
async def delete_platform_user(request: Request, user_id: int, db: Session = Depends(get_db),
                               admin_info: dict = Depends(require_platform_admin)):
    """删除平台超级用户（仅平台超级管理员）"""
    try:
        result = UserService.delete_user(db, user_id)

        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'],
                                    admin_info['login_name'], "系统管理", "DELETE",
                                    f"/api/admin/platform/users/{user_id}", "", 1,
                                    "删除平台超级用户成功", request.client.host if request.client else "unknown")

        return success_response(data=result, message="删除成功")
    except Exception as e:
        return error_response(5000, str(e))


# 租户管理（平台超级管理员管理租户）
@platform_router.post("/tenants", summary="创建租户", response_model=TenantResponse)
async def create_tenant(request: Request, data: TenantCreate,
                        db: Session = Depends(get_db),
                        admin_info: dict = Depends(require_platform_admin)):
    """创建租户（仅平台超级管理员）"""
    try:
        result = TenantService.create_tenant(db, data)

        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'],
                                    admin_info['login_name'], "系统管理", "POST",
                                    "/api/admin/platform/tenants", str(data.model_dump()), 1,
                                    "创建租户成功", request.client.host if request.client else "unknown")

        return success_response(data=result, message="创建成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.get("/tenants", summary="分页查询租户列表", response_model=TenantListResponse)
async def get_tenant_list(request: Request, tenant_name: Optional[str] = None,
                          status: Optional[int] = None, page: int = 1, size: int = 10,
                          db: Session = Depends(get_db),
                          admin_info: dict = Depends(require_platform_admin)):
    """分页查询租户列表（仅平台超级管理员）"""
    try:
        result = TenantService.get_tenant_list(db, tenant_name, status, page, size)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.get("/tenants/{tenant_id}", summary="查询租户详情", response_model=TenantResponse)
async def get_tenant(tenant_id: int, db: Session = Depends(get_db),
                     admin_info: dict = Depends(require_platform_admin)):
    """查询租户详情（仅平台超级管理员）"""
    try:
        result = TenantService.get_tenant(db, tenant_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.put("/tenants/{tenant_id}", summary="更新租户", response_model=TenantResponse)
async def update_tenant(request: Request, tenant_id: int, data: TenantUpdate,
                        db: Session = Depends(get_db),
                        admin_info: dict = Depends(require_platform_admin)):
    """更新租户（仅平台超级管理员）"""
    try:
        result = TenantService.update_tenant(db, tenant_id, data)

        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'],
                                    admin_info['login_name'], "系统管理", "PUT",
                                    f"/api/admin/platform/tenants/{tenant_id}", str(data.model_dump()), 1,
                                    "更新租户成功", request.client.host if request.client else "unknown")

        return success_response(data=result, message="更新成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.delete("/tenants/{tenant_id}", summary="删除租户")
async def delete_tenant(request: Request, tenant_id: int, db: Session = Depends(get_db),
                        admin_info: dict = Depends(require_platform_admin)):
    """删除租户（仅平台超级管理员）"""
    try:
        result = TenantService.delete_tenant(db, tenant_id)

        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'],
                                    admin_info['login_name'], "系统管理", "DELETE",
                                    f"/api/admin/platform/tenants/{tenant_id}", "", 1,
                                    "删除租户成功", request.client.host if request.client else "unknown")

        return success_response(data=result, message="删除成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.put("/tenants/{tenant_id}/enable", summary="启用租户", response_model=TenantResponse)
async def enable_tenant(request: Request, tenant_id: int, db: Session = Depends(get_db),
                        admin_info: dict = Depends(require_platform_admin)):
    """启用租户（仅平台超级管理员）"""
    try:
        result = TenantService.enable_tenant(db, tenant_id)

        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'],
                                    admin_info['login_name'], "系统管理", "PUT",
                                    f"/api/admin/platform/tenants/{tenant_id}/enable", "", 1,
                                    "启用租户成功", request.client.host if request.client else "unknown")

        return success_response(data=result, message="启用成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.put("/tenants/{tenant_id}/disable", summary="禁用租户", response_model=TenantResponse)
async def disable_tenant(request: Request, tenant_id: int, db: Session = Depends(get_db),
                         admin_info: dict = Depends(require_platform_admin)):
    """禁用租户（仅平台超级管理员）"""
    try:
        result = TenantService.disable_tenant(db, tenant_id)

        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'],
                                    admin_info['login_name'], "系统管理", "PUT",
                                    f"/api/admin/platform/tenants/{tenant_id}/disable", "", 1,
                                    "禁用租户成功", request.client.host if request.client else "unknown")

        return success_response(data=result, message="禁用成功")
    except Exception as e:
        return error_response(5000, str(e))


# 平台超管为指定租户创建租户管理员
@platform_router.post("/tenants/{tenant_id}/users", summary="创建租户管理员", response_model=UserResponse)
async def create_tenant_admin(request: Request, tenant_id: int, data: UserCreate,
                              db: Session = Depends(get_db),
                              admin_info: dict = Depends(require_platform_admin)):
    """为指定租户创建管理员（仅平台超级管理员）"""
    try:
        # 设置用户类型为租户超级管理员（user_type=1）
        data.user_type = 1

        result = UserService.create_user(db, tenant_id, data)

        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'],
                                    admin_info['login_name'], "系统管理", "POST",
                                    f"/api/admin/platform/tenants/{tenant_id}/users", str(data.model_dump()), 1,
                                    "创建租户管理员成功", request.client.host if request.client else "unknown")

        return success_response(data=result, message="创建成功")
    except Exception as e:
        return error_response(5000, str(e))


# 挂载平台管理子路由
router.include_router(platform_router)
