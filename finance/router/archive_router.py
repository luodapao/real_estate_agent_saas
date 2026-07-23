﻿"""
房地产SaaS财务管理系统 - 财务基础档案模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_finance_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from finance.service.archive_service import ArchiveService
from finance.schemas.archive_schemas import (
    ProjectFinConfigCreate,
    ProjectFinConfigUpdate,
    AccountCreate,
    AccountUpdate,
    SubjectCreate,
    SubjectUpdate,
    TaxRateCreate,
    TaxRateUpdate,
    BankInfoCreate,
    BankInfoUpdate,
    DiscountRuleCreate,
    DiscountRuleUpdate,
)
from finance.schemas.base_schemas import PageRequest

router = APIRouter(prefix="/archive", tags=["财务基础档案"])


# ========== 项目财务配置接口 ==========

@router.post("/config/create")
async def create_project_finance_config(
    data: ProjectFinConfigCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建项目财务配置"""
    try:
        result = ArchiveService.create_project_fin_config(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="项目财务配置创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/config/list")
async def list_project_finance_config(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取项目财务配置列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = ArchiveService.list_project_fin_config(db, current_user['tenant'], page_request)
        return success_response(data={
            'total': result.total,
            'page': result.page,
            'page_size': result.size,
            'items': [item.model_dump(mode='json') for item in result.data]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/config/{id}")
async def get_project_finance_config(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取项目财务配置详情"""
    try:
        result = ArchiveService.get_project_fin_config(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "项目财务配置不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/config/{id}")
async def update_project_finance_config(
    id: int,
    data: ProjectFinConfigUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新项目财务配置"""
    try:
        result = ArchiveService.update_project_fin_config(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="项目财务配置更新成功")
        return error_response(-1, "项目财务配置不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/config/{id}")
async def delete_project_finance_config(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除项目财务配置"""
    try:
        success = ArchiveService.delete_project_fin_config(db, current_user['tenant'], id)
        if success:
            return success_response(message="项目财务配置删除成功")
        return error_response(-1, "项目财务配置不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 财务账户接口 ==========

@router.post("/account/create")
async def create_finance_account(
    data: AccountCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建财务账户"""
    try:
        result = ArchiveService.create_account(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="财务账户创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/account/list")
async def list_finance_account(
    page: int = 1,
    page_size: int = 20,
    account_type: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取财务账户列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = ArchiveService.list_accounts(db, current_user['tenant'], page_request)
        return success_response(data={
            'total': result.total,
            'page': result.page,
            'page_size': result.size,
            'items': [item.model_dump(mode='json') for item in result.data]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/account/{id}")
async def get_finance_account(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取财务账户详情"""
    try:
        result = ArchiveService.get_account(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "财务账户不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/account/{id}")
async def update_finance_account(
    id: int,
    data: AccountUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新财务账户"""
    try:
        result = ArchiveService.update_account(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="财务账户更新成功")
        return error_response(-1, "财务账户不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/account/{id}")
async def delete_finance_account(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除财务账户"""
    try:
        success = ArchiveService.delete_account(db, current_user['tenant'], id)
        if success:
            return success_response(message="财务账户删除成功")
        return error_response(-1, "财务账户不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 财务科目接口 ==========

@router.post("/subject/create")
async def create_finance_subject(
    data: SubjectCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建财务科目"""
    try:
        result = ArchiveService.create_subject(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="财务科目创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/subject/list")
async def list_finance_subject(
    page: int = 1,
    page_size: int = 20,
    subject_level: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取财务科目列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = ArchiveService.list_subjects(db, current_user['tenant'], page_request)
        return success_response(data={
            'total': result.total,
            'page': result.page,
            'page_size': result.size,
            'items': [item.model_dump(mode='json') for item in result.data]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/subject/{id}")
async def get_finance_subject(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取财务科目详情"""
    try:
        result = ArchiveService.get_subject(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "财务科目不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/subject/{id}")
async def update_finance_subject(
    id: int,
    data: SubjectUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新财务科目"""
    try:
        result = ArchiveService.update_subject(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="财务科目更新成功")
        return error_response(-1, "财务科目不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/subject/{id}")
async def delete_finance_subject(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除财务科目"""
    try:
        success = ArchiveService.delete_subject(db, current_user['tenant'], id)
        if success:
            return success_response(message="财务科目删除成功")
        return error_response(-1, "财务科目不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 税率配置接口 ==========

@router.post("/tax-rate/create")
async def create_tax_rate(
    data: TaxRateCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建税率配置"""
    try:
        result = ArchiveService.create_tax_rate(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="税率配置创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/tax-rate/list")
async def list_tax_rate(
    page: int = 1,
    page_size: int = 20,
    tax_type: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取税率配置列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = ArchiveService.list_tax_rates(db, current_user['tenant'], page_request)
        return success_response(data={
            'total': result.total,
            'page': result.page,
            'page_size': result.size,
            'items': [item.model_dump(mode='json') for item in result.data]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/tax-rate/{id}")
async def get_tax_rate(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取税率配置详情"""
    try:
        result = ArchiveService.get_tax_rate(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "税率配置不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/tax-rate/{id}")
async def update_tax_rate(
    id: int,
    data: TaxRateUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新税率配置"""
    try:
        result = ArchiveService.update_tax_rate(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="税率配置更新成功")
        return error_response(-1, "税率配置不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/tax-rate/{id}")
async def delete_tax_rate(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除税率配置"""
    try:
        success = ArchiveService.delete_tax_rate(db, current_user['tenant'], id)
        if success:
            return success_response(message="税率配置删除成功")
        return error_response(-1, "税率配置不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 银行信息接口 ==========

@router.post("/bank/create")
async def create_bank_info(
    data: BankInfoCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建银行信息"""
    try:
        result = ArchiveService.create_bank_info(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="银行信息创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/bank/list")
async def list_bank_info(
    page: int = 1,
    page_size: int = 20,
    bank_name: Optional[str] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取银行信息列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = ArchiveService.list_bank_info(db, current_user['tenant'], page_request)
        return success_response(data={
            'total': result.total,
            'page': result.page,
            'page_size': result.size,
            'items': [item.model_dump(mode='json') for item in result.data]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/bank/{id}")
async def get_bank_info(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取银行信息详情"""
    try:
        result = ArchiveService.get_bank_info(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "银行信息不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/bank/{id}")
async def update_bank_info(
    id: int,
    data: BankInfoUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新银行信息"""
    try:
        result = ArchiveService.update_bank_info(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="银行信息更新成功")
        return error_response(-1, "银行信息不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/bank/{id}")
async def delete_bank_info(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除银行信息"""
    try:
        success = ArchiveService.delete_bank_info(db, current_user['tenant'], id)
        if success:
            return success_response(message="银行信息删除成功")
        return error_response(-1, "银行信息不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 优惠规则接口 ==========

@router.post("/preferential-rule/create")
async def create_preferential_rule(
    data: DiscountRuleCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建优惠规则"""
    try:
        result = ArchiveService.create_discount_rule(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="优惠规则创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/preferential-rule/list")
async def list_preferential_rule(
    page: int = 1,
    page_size: int = 20,
    rule_type: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取优惠规则列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = ArchiveService.list_discount_rules(db, current_user['tenant'], page_request)
        return success_response(data={
            'total': result.total,
            'page': result.page,
            'page_size': result.size,
            'items': [item.model_dump(mode='json') for item in result.data]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/preferential-rule/{id}")
async def get_preferential_rule(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取优惠规则详情"""
    try:
        result = ArchiveService.get_discount_rule(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "优惠规则不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/preferential-rule/{id}")
async def update_preferential_rule(
    id: int,
    data: DiscountRuleUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新优惠规则"""
    try:
        result = ArchiveService.update_discount_rule(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="优惠规则更新成功")
        return error_response(-1, "优惠规则不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/preferential-rule/{id}")
async def delete_preferential_rule(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除优惠规则"""
    try:
        success = ArchiveService.delete_discount_rule(db, current_user['tenant'], id)
        if success:
            return success_response(message="优惠规则删除成功")
        return error_response(-1, "优惠规则不存在")
    except Exception as e:
        return error_response(-1, str(e))
