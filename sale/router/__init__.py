"""
房地产SaaS销售管理系统 - 路由层
聚合所有业务模块的子路由
"""

from fastapi import APIRouter

from sale.router.project_router import router as project_router
from sale.router.customer_router import router as customer_router
from sale.router.transaction_router import router as transaction_router
from sale.router.commission_router import router as commission_router
from sale.router.performance_router import router as performance_router
from sale.router.statistics_router import router as statistics_router

router = APIRouter(tags=["Sale - 销售管理"])

router.include_router(project_router)
router.include_router(customer_router)
router.include_router(transaction_router)
router.include_router(commission_router)
router.include_router(performance_router)
router.include_router(statistics_router)


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "success",
        "message": "销售管理系统运行正常",
        "version": "1.0.0"
    }