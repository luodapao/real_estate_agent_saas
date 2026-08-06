"""
房地产SaaS财务管理系统 - 主路由
聚合所有Finance业务模块的子路由
"""

from fastapi import APIRouter

from finance.router.archive_router import router as archive_router
from finance.router.payment_router import router as payment_router
from finance.router.invoice_router import router as invoice_router
from finance.router.commission_router import router as commission_router
from finance.router.cost_router import router as cost_router
from finance.router.ar_ap_router import router as ar_ap_router
from finance.router.reconciliation_router import router as reconciliation_router
from finance.router.voucher_router import router as voucher_router
from finance.router.audit_router import router as audit_router
from finance.router.report_router import router as report_router

router = APIRouter(prefix="/finance", tags=["财务管理系统"])

# 注册子路由（各子路由已自带二级前缀，如 /archive、/payment 等）
router.include_router(archive_router)
router.include_router(payment_router)
router.include_router(invoice_router)
router.include_router(commission_router)
router.include_router(cost_router)
router.include_router(ar_ap_router)
router.include_router(reconciliation_router)
router.include_router(voucher_router)
router.include_router(audit_router)
router.include_router(report_router)


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "success",
        "message": "财务管理系统运行正常",
        "version": "1.0.0"
    }
