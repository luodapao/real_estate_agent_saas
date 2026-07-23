"""
房地产SaaS财务管理系统 - Finance模块Router包初始化
"""

# 导入所有router模块
from .archive_router import router as archive_router
from .payment_router import router as payment_router
from .invoice_router import router as invoice_router
from .commission_router import router as commission_router
from .cost_router import router as cost_router
from .ar_ap_router import router as ar_ap_router
from .reconciliation_router import router as reconciliation_router
from .voucher_router import router as voucher_router
from .audit_router import router as audit_router
from .report_router import router as report_router

# 导出所有router
__all__ = [
    "archive_router",
    "payment_router",
    "invoice_router",
    "commission_router",
    "cost_router",
    "ar_ap_router",
    "reconciliation_router",
    "voucher_router",
    "audit_router",
    "report_router"
]
