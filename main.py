"""
房地产Agent自主调用SaaS管理平台 - 全局入口文件
负责挂载四大子系统路由、初始化中间件、配置全局异常处理
"""

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

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
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 自动创建所有表（如果不存在）
    Base.metadata.create_all(bind=engine)
    print("数据库表初始化完成")from admin.router.log_router import router as log_router
from sale.router.sale_router import router as sale_router

# 导入子系统模型（确保表定义被注册到Base.metadata）
import sale.model.sale_models
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
# 
# try:
#     from cash.router import router as cash_router
# except ImportError:
#     cash_router = None
# 
# try:
#     from engineer.router import router as engineer_router
# except ImportError:
#     engineer_router = None
# 
# # 财务管理模块路由
# try:
#     from finance.router.archive_router import router as finance_archive_router
#     from finance.router.payment_router import router as finance_payment_router
#     from finance.router.invoice_router import router as finance_invoice_router
#     from finance.router.commission_router import router as finance_commission_router
#     from finance.router.cost_router import router as finance_cost_router
#     from finance.router.ar_ap_router import router as finance_ar_ap_router
#     from finance.router.reconciliation_router import router as finance_reconciliation_router
#     from finance.router.voucher_router import router as finance_voucher_router
#     from finance.router.audit_router import router as finance_audit_router
#     from finance.router.report_router import router as finance_report_router
# except ImportError:
#     finance_archive_router = None
#     finance_payment_router = None
#     finance_invoice_router = None
#     finance_commission_router = None
#     finance_cost_router = None
#     finance_ar_ap_router = None
#     finance_reconciliation_router = None
#     finance_voucher_router = None
#     finance_audit_router = None
#     finance_report_router = None

# 定时任务初始化（暂时注释，避免导入错误）
# from tasks.task_scheduler import start_scheduler

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
    # if cash_router:
    #     app.include_router(cash_router, prefix="/api/cash", tags=["Cash - 财务管理"])
    # if engineer_router:
    #     app.include_router(engineer_router, prefix="/api/engineer", tags=["Engineer - 工程管理"])
    # 
    # # 注册财务管理模块路由
    # if finance_archive_router:
    #     app.include_router(finance_archive_router, prefix="/api/finance", tags=["Finance - 财务基础档案"])
    # if finance_payment_router:
    #     app.include_router(finance_payment_router, prefix="/api/finance", tags=["Finance - 房款收支管理"])
    # if finance_invoice_router:
    #     app.include_router(finance_invoice_router, prefix="/api/finance", tags=["Finance - 票据税务合规"])
    # if finance_commission_router:
    #     app.include_router(finance_commission_router, prefix="/api/finance", tags=["Finance - 佣金支付管理"])
    # if finance_cost_router:
    #     app.include_router(finance_cost_router, prefix="/api/finance", tags=["Finance - 项目成本管理"])
    # if finance_ar_ap_router:
    #     app.include_router(finance_ar_ap_router, prefix="/api/finance", tags=["Finance - 应收应付往来台账"])
    # if finance_reconciliation_router:
    #     app.include_router(finance_reconciliation_router, prefix="/api/finance", tags=["Finance - 资金对账管理"])
    # if finance_voucher_router:
    #     app.include_router(finance_voucher_router, prefix="/api/finance", tags=["Finance - 会计凭证管理"])
    # if finance_audit_router:
    #     app.include_router(finance_audit_router, prefix="/api/finance", tags=["Finance - 财务审计追溯"])
    # if finance_report_router:
    #     app.include_router(finance_report_router, prefix="/api/finance", tags=["Finance - 财务统计报表"])

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