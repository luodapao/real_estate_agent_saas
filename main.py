"""
房地产Agent自主调用SaaS管理平台 - 全局入口文件
负责挂载四大子系统路由、初始化中间件、配置全局异常处理
"""

import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse, FileResponse

# 全局配置和核心组件
from config.settings import settings
from config.exception import CustomException, ErrorCode
from core.auth_middleware import auth_middleware
from core.db_base import engine, SessionLocal, Base
from core.redis_base import redis_client
# from core.mq_producer import mq_producer

# 子系统路由
from admin.router.admin_router import router as admin_router
from admin.router.tenant_router import router as tenant_router
from admin.router.role_router import router as role_router
from admin.router.menu_router import router as menu_router
from admin.router.dict_router import router as dict_router
from admin.router.log_router import router as log_router
from sale.router.sale_router import router as sale_router

# Finance子系统主路由（聚合全部子路由，全部放开）
from finance.router.finance_router import router as finance_router

# 导入子系统模型（确保表定义被注册到Base.metadata）
import sale.model.sale_models
import finance.model.finance_models
import admin.model.sys_user
import admin.model.sys_role
import admin.model.sys_menu
import admin.model.sys_dict
import admin.model.sys_log_operation
import admin.model.sys_log_login
import admin.model.sys_tenant
import admin.model.sys_token
import admin.model.sys_user_role
import admin.model.sys_role_menu
import admin.model.sys_dept

def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title="房地产Agent自主调用SaaS管理平台",
        description="基于Python+FastAPI开发，适配ArkClaw智能Agent自主对话调用接口",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # 配置CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册全局鉴权中间件（排除登录、刷新Token等公开接口）
    auth_exclude_paths = [
        "/api/admin/login",
        "/api/admin/refresh-token",
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
    app.middleware("http")(auth_middleware)

    # 注册子系统路由
    app.include_router(admin_router, tags=["Admin - 软商用户管理"])
    app.include_router(tenant_router, tags=["Admin - 租户管理"])
    app.include_router(role_router, prefix="/api/admin", tags=["Admin - 角色管理"])
    app.include_router(menu_router, prefix="/api/admin", tags=["Admin - 菜单管理"])
    app.include_router(dict_router, prefix="/api/admin", tags=["Admin - 数据字典"])
    app.include_router(log_router, prefix="/api/admin", tags=["Admin - 日志管理"])

    # ========== 注册预留子系统路由 ==========
    app.include_router(sale_router, prefix="/api", tags=["Sale - 销售管理"])

    # ========== 注册Finance子系统路由（全部放开，统一前缀 /api/finance）==========
    app.include_router(finance_router, prefix="/api", tags=["Finance - 财务管理"])

    # ========== 挂载前端静态页面（登录Demo等）==========
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    if os.path.isdir(frontend_dir):
        app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")

    # ========== 登录页快捷入口：/login 直接跳转 login.html ==========
    @app.get("/login", include_in_schema=False)
    async def login_page(ticket: str = None):
        login_html = os.path.join(frontend_dir, "login.html")
        if os.path.isfile(login_html):
            return FileResponse(login_html)
        return JSONResponse(status_code=404, content={"code": 404, "message": "登录页未找到"})

    # ========== 超级用户管理页快捷入口：/superuser-control 直接返回管理页 ==========
    @app.get("/superuser-control", include_in_schema=False)
    async def superuser_control_page(ticket: str = None):
        control_html = os.path.join(frontend_dir, "superuser-control.html")
        if os.path.isfile(control_html):
            return FileResponse(control_html)
        return JSONResponse(status_code=404, content={"code": 404, "message": "管理页未找到"})

    # ========== 楼栋创建页快捷入口：/project-create 直接返回创建页 ==========
    @app.get("/project-create", include_in_schema=False)
    async def project_create_page(ticket: str = None):
        create_html = os.path.join(frontend_dir, "project-create.html")
        if os.path.isfile(create_html):
            return FileResponse(create_html)
        return JSONResponse(status_code=404, content={"code": 404, "message": "楼栋创建页未找到"})

    return app

def init_app(app: FastAPI):
    """初始化应用资源"""
    pass

# 创建应用实例
app = create_app()

# 全局异常处理
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    """自定义异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.error_code,
            "message": exc.message,
            "data": None
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """参数校验异常处理"""
    error_messages = []
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown"
        message = error.get("msg", "参数校验失败")
        error_messages.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=400,
        content={
            "code": ErrorCode.PARAM_VALID_ERROR,
            "message": ", ".join(error_messages),
            "data": None
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常兜底处理"""
    return JSONResponse(
        status_code=500,
        content={
            "code": ErrorCode.SYSTEM_ERROR,
            "message": "系统内部错误",
            "data": None
        }
    )

# 应用启动时初始化
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    init_app(app)
    print("房地产Agent SaaS管理平台启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("房地产Agent SaaS管理平台正在关闭...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS
    )
