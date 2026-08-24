"""
登录模块路由
"""
import uuid
import json
import asyncio
import time
from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
from core.db_base import get_db
from core.redis_base import redis_client
from admin.service.user_service import UserService
from admin.service.log_service import LogService
from admin.schemas.user_schemas import (
    LoginRequest, LoginResponse, ChangePasswordRequest,
    RefreshTokenRequest, PrepareLoginReq, PrepareLoginResp,
    WaitLoginReq
)
from config.exception import success_response, error_response
from config.constants import LOGIN_TYPE


router = APIRouter(tags=["登录模块"])


@router.post("/prepare-login", summary="预登录（生成一次性登录票据）", response_model=PrepareLoginResp)
async def prepare_login(req: PrepareLoginReq):
    """预登录接口，生成一次性票据 loginTicket（UUID，只能使用一次），返回登录URL"""
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
    """用户登录接口"""
    try:
        agent_identifier = request.headers.get('X-Agent-Identifier', 'default')
        ip = request.client.host if request.client else "unknown"
        result = UserService.login(db, login_data.account, login_data.password, agent_identifier, ip)

        # 如果登录请求携带了 ticket（MCP扫码登录场景）
        ticket = login_data.ticket
        if ticket:
            # 查询票据
            raw = redis_client.get(f"login:ticket:{ticket}")
            if not raw:
                # 票据已过期，仍然返回登录成功（不影响正常登录流程），但提示一下
                pass
            else:
                ticket_data = json.loads(raw)
                # 更新票据状态，写入token
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
    """长轮询接口，等待用户使用票据完成登录后返回结果
    优先使用 Redis Pub/Sub 等待，超时后降级为定期检查 Redis Key"""
    ticket = req.ticket
    timeout = req.timeout or 30
    # 确保超时时间不超过合理范围
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

    # 使用 Redis Pub/Sub 等待通知
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
                    # get_message 非阻塞检查
                    message = pubsub.get_message(timeout=min(remaining, 2.0))
                    if message and message.get("type") == "message":
                        # 收到消息
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

    # 在子线程中运行阻塞的 pubsub 订阅
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
    check_interval = 1.0  # 每秒检查一次
    while (time.time() - start_time) < timeout:
        raw = redis_client.get(f"login:ticket:{ticket}")
        if not raw:
            return error_response(4000, "链接已过期，请重新在AI窗口发起登录")
        ticket_data = json.loads(raw)
        # 只把成功当作终态返回；其余（pending/failed）继续等
        if ticket_data["status"] == "success":
            redis_client.delete(f"login:ticket:{ticket}")
            return success_response(data=ticket_data)
        # 短暂休眠，避免空转
        await asyncio.sleep(check_interval)

    # 超时：返回当前票据状态（仍是 pending）
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
    """修改密码接口"""
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
