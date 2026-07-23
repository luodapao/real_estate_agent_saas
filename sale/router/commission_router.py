"""
房地产SaaS销售管理系统 - 分销渠道与佣金模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from sale.service.commission_service import (
    ChannelService, BrokerService, CommissionRuleService, CommissionBillService
)

router = APIRouter(prefix="/commission", tags=["分销渠道与佣金"])


# ========== 渠道公司管理接口 ==========

@router.post("/channel/create")
async def create_channel(
    channel_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建渠道公司"""
    try:
        service = ChannelService(db, current_user['tenant'])
        channel = service.create_channel(channel_data, current_user['user_id'])
        return success_response(data={
            "channel_id": channel.channel_id,
            "channel_code": channel.channel_code,
            "channel_name": channel.channel_name
        }, message="渠道公司创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/channel/list")
async def get_channels_list(
    page: int = 1,
    page_size: int = 20,
    channel_name: Optional[str] = None,
    cooperation_status: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取渠道公司列表"""
    try:
        service = ChannelService(db, current_user['tenant'])
        filters = {}
        if channel_name:
            filters['channel_name'] = channel_name
        if cooperation_status is not None:
            filters['cooperation_status'] = cooperation_status
        
        result = service.get_channels_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/channel/detail/{channel_id}")
async def get_channel_detail(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取渠道公司详情"""
    try:
        service = ChannelService(db, current_user['tenant'])
        detail = service.get_channel_detail(channel_id)
        return success_response(data=detail)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/channel/update/{channel_id}")
async def update_channel(
    channel_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新渠道公司"""
    try:
        service = ChannelService(db, current_user['tenant'])
        channel = service.update_channel(channel_id, update_data, current_user['user_id'])
        return success_response(data={
            "channel_id": channel.channel_id,
            "channel_name": channel.channel_name
        }, message="渠道公司更新成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/channel/terminate/{channel_id}")
async def terminate_cooperation(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """终止合作"""
    try:
        service = ChannelService(db, current_user['tenant'])
        service.terminate_cooperation(channel_id, current_user['user_id'])
        return success_response(message="合作终止成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 经纪人管理接口 ==========

@router.post("/broker/create")
async def create_broker(
    broker_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建经纪人"""
    try:
        service = BrokerService(db, current_user['tenant'])
        broker = service.create_broker(broker_data, current_user['user_id'])
        return success_response(data={
            "broker_id": broker.broker_id,
            "broker_code": broker.broker_code,
            "broker_name": broker.broker_name
        }, message="经纪人创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/broker/list")
async def get_brokers_list(
    page: int = 1,
    page_size: int = 20,
    broker_name: Optional[str] = None,
    channel_id: Optional[int] = None,
    work_status: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取经纪人列表"""
    try:
        service = BrokerService(db, current_user['tenant'])
        filters = {}
        if broker_name:
            filters['broker_name'] = broker_name
        if channel_id:
            filters['channel_id'] = channel_id
        if work_status is not None:
            filters['work_status'] = work_status
        
        result = service.get_brokers_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/broker/detail/{broker_id}")
async def get_broker_detail(
    broker_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取经纪人详情"""
    try:
        service = BrokerService(db, current_user['tenant'])
        detail = service.get_broker_detail(broker_id)
        return success_response(data=detail)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/broker/update/{broker_id}")
async def update_broker(
    broker_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新经纪人"""
    try:
        service = BrokerService(db, current_user['tenant'])
        broker = service.update_broker(broker_id, update_data, current_user['user_id'])
        return success_response(data={
            "broker_id": broker.broker_id,
            "broker_name": broker.broker_name
        }, message="经纪人更新成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 佣金规则管理接口 ==========

@router.post("/rule/create")
async def create_commission_rule(
    rule_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建佣金规则"""
    try:
        service = CommissionRuleService(db, current_user['tenant'])
        rule = service.create_commission_rule(rule_data, current_user['user_id'])
        return success_response(data={
            "rule_id": rule.rule_id,
            "rule_type": rule.rule_type
        }, message="佣金规则创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/rule/list")
async def get_rules_list(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    rule_type: Optional[str] = None,
    rule_status: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取佣金规则列表"""
    try:
        service = CommissionRuleService(db, current_user['tenant'])
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if rule_type:
            filters['rule_type'] = rule_type
        if rule_status is not None:
            filters['rule_status'] = rule_status
        
        result = service.get_rules_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/rule/update/{rule_id}")
async def update_commission_rule(
    rule_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新佣金规则"""
    try:
        service = CommissionRuleService(db, current_user['tenant'])
        rule = service.update_commission_rule(rule_id, update_data, current_user['user_id'])
        return success_response(data={
            "rule_id": rule.rule_id,
            "rule_type": rule.rule_type
        }, message="佣金规则更新成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 佣金结算接口 ==========

@router.post("/bill/generate/{contract_id}")
async def generate_commission_bill(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """生成佣金结算单"""
    try:
        service = CommissionBillService(db, current_user['tenant'])
        result = service.generate_commission_bill(contract_id, current_user['user_id'])
        return success_response(data=result, message="佣金结算单生成成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/bill/list")
async def get_bills_list(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    broker_id: Optional[int] = None,
    bill_status: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取佣金结算单列表"""
    try:
        service = CommissionBillService(db, current_user['tenant'])
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if channel_id:
            filters['channel_id'] = channel_id
        if broker_id:
            filters['broker_id'] = broker_id
        if bill_status is not None:
            filters['bill_status'] = bill_status
        
        result = service.get_bills_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/bill/audit/{bill_id}")
async def audit_commission_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """审核佣金结算单"""
    try:
        service = CommissionBillService(db, current_user['tenant'])
        service.audit_commission_bill(bill_id, current_user['user_id'], current_user['user_id'])
        return success_response(message="佣金结算单审核成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/bill/freeze/{bill_id}")
async def freeze_commission_bill(
    bill_id: int,
    freeze_reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """冻结佣金结算单"""
    try:
        service = CommissionBillService(db, current_user['tenant'])
        service.freeze_commission_bill(bill_id, freeze_reason, current_user['user_id'])
        return success_response(message="佣金结算单冻结成功")
    except Exception as e:
        return error_response(-1, str(e))
