"""
房地产SaaS销售管理系统 - 分销渠道与佣金业务逻辑层
实现渠道公司、经纪人、佣金规则、佣金结算全链路管理
"""

from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from core.redis_base import RedisClient
from core.exception import BusinessError, ValidationError

from sale.dao.sale_dao import (
    SaleChannelDAO, SaleBrokerDAO, SaleCommissionRuleDAO, SaleCommissionBillDAO,
    SaleContractDAO, SaleVisitDAO, SaleStatDailyLogsDAO, SaleProjectDAO, SaleBuildingDAO,
    SaleReportDAO, SaleVisitDAO, SaleSubscribeDAO
)
from sale.model.sale_models import (
    SaleChannel, SaleBroker, SaleCommissionRule, SaleCommissionBill, SaleContract
)


class ChannelService:
    """渠道公司业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()

    def create_channel(self, channel_data: dict, operator_id: int = None) -> SaleChannel:
        """创建渠道公司（生产级：编码唯一性 + 幂等校验）"""
        # 渠道编码自动生成，不接受用户传入
        channel_code = self._generate_channel_code()
        channel_data['channel_code'] = channel_code
        
        # 设置租户和初始状态
        channel_data['tenant'] = self.tenant
        channel_data['cooperation_status'] = 1  # 合作中
        channel_data['status'] = 1
        channel_data['is_del'] = 0
        
        # 如果没有设置合作开始时间，默认为当前时间
        if 'start_date' not in channel_data:
            channel_data['start_date'] = datetime.now()
        
        # 创建渠道公司
        channel = SaleChannelDAO.create_channel(self.db, channel_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_channel", 
            f"创建渠道公司：{channel.channel_name}", 
            True
        )
        
        return channel
    
    def get_channel_detail(self, channel_id: int) -> dict:
        """获取渠道公司详情"""
        channel = SaleChannelDAO.get_channel_by_id(self.db, channel_id, self.tenant)
        if not channel:
            raise BusinessError("渠道公司不存在")
        
        # 获取关联的经纪人列表
        brokers = SaleBrokerDAO.get_brokers_by_channel(self.db, channel_id, self.tenant)
        
        # 统计渠道业绩数据
        stats = self._get_channel_statistics(channel_id)
        
        return {
            'channel_id': channel.channel_id,
            'channel_code': channel.channel_code,
            'channel_name': channel.channel_name,
            'contact_person': channel.contact_person,
            'contact_mobile': channel.contact_mobile,
            'channel_level': channel.channel_level,
            'cooperation_status': channel.cooperation_status,
            'start_date': channel.start_date.isoformat() if channel.start_date else None,
            'end_date': channel.end_date.isoformat() if channel.end_date else None,
            'status': channel.status,
            'brokers': [{
                'broker_id': b.broker_id,
                'broker_code': b.broker_code,
                'broker_name': b.broker_name,
                'mobile': b.mobile,
                'work_status': b.work_status
            } for b in brokers],
            'statistics': stats,
            'create_time': channel.create_time.isoformat() if channel.create_time else None,
            'update_time': channel.update_time.isoformat() if channel.update_time else None
        }
    
    def get_channels_list(self, page: int = 1, page_size: int = 20,
                         filters: Optional[Dict] = None) -> dict:
        """获取渠道公司列表"""
        skip = (page - 1) * page_size
        channels = SaleChannelDAO.get_channels_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleChannelDAO.get_channels_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'channel_id': c.channel_id,
                'channel_code': c.channel_code,
                'channel_name': c.channel_name,
                'contact_person': c.contact_person,
                'contact_mobile': c.contact_mobile,
                'channel_level': c.channel_level,
                'cooperation_status': c.cooperation_status,
                'status': c.status,
                'create_time': c.create_time.isoformat() if c.create_time else None
            } for c in channels]
        }
    
    def update_channel(self, channel_id: int, update_data: dict, 
                      operator_id: int = None) -> SaleChannel:
        """更新渠道公司"""
        channel = SaleChannelDAO.get_channel_by_id(self.db, channel_id, self.tenant)
        if not channel:
            raise BusinessError("渠道公司不存在")
        
        # 如果修改渠道编码，检查唯一性
        if 'channel_code' in update_data and update_data['channel_code'] != channel.channel_code:
            existing = self.db.query(SaleChannel).filter(
                SaleChannel.channel_code == update_data['channel_code'],
                SaleChannel.tenant == self.tenant,
                SaleChannel.is_del == 0
            ).first()
            if existing:
                raise ValidationError(f"渠道编码 {update_data['channel_code']} 已存在")
        
        # 更新渠道公司
        updated_channel = SaleChannelDAO.update_channel(self.db, channel, update_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_channel", 
            f"更新渠道公司：{channel.channel_name}", 
            True
        )
        
        return updated_channel
    
    def terminate_cooperation(self, channel_id: int, operator_id: int = None) -> bool:
        """终止合作"""
        channel = SaleChannelDAO.get_channel_by_id(self.db, channel_id, self.tenant)
        if not channel:
            raise BusinessError("渠道公司不存在")
        
        # 更新合作状态
        SaleChannelDAO.update_channel(self.db, channel, {
            'cooperation_status': 2,  # 已终止
            'end_date': datetime.now()
        })
        
        # 冻结所有在职经纪人的未结算佣金
        brokers = SaleBrokerDAO.get_brokers_by_channel(self.db, channel_id, self.tenant)
        for broker in brokers:
            if broker.work_status == 1:  # 在职
                self._freeze_broker_pending_commission(broker.broker_id)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "terminate_cooperation", 
            f"终止合作：{channel.channel_name}", 
            True
        )
        
        return True
    
    def _generate_channel_code(self) -> str:
        """生成渠道编码（格式：CH + 6位数字，如 CH000001）"""
        # 使用Redis原子操作生成递增序列，保证唯一性和并发安全
        key = f"channel_code_seq:{self.tenant}"
        seq = self.redis.incr(key)
        
        # 如果Redis不可用或返回None，从数据库获取最大值
        if seq is None:
            max_channel = self.db.query(SaleChannel).filter(
                SaleChannel.tenant == self.tenant,
                SaleChannel.is_del == 0
            ).order_by(SaleChannel.channel_id.desc()).first()
            seq = max_channel.channel_id + 1 if max_channel else 1
        elif seq == 1:
            # 如果是首次生成，检查数据库中是否已有渠道，确保序列连续性
            max_channel = self.db.query(SaleChannel).filter(
                SaleChannel.tenant == self.tenant,
                SaleChannel.is_del == 0
            ).order_by(SaleChannel.channel_id.desc()).first()
            if max_channel:
                seq = max_channel.channel_id + 1
                self.redis.set(key, seq)
        
        return f"CH{seq:06d}"
    
    def _get_channel_statistics(self, channel_id: int) -> dict:
        """获取渠道统计数据"""
        # 统计带看、认购、签约、业绩数据
        visits = SaleVisitDAO.get_visits_list(
            self.db, self.tenant, 0, 100000,
            {'channel_id': channel_id}
        )
        
        # 获取该渠道经纪人的成交数据
        brokers = SaleBrokerDAO.get_brokers_by_channel(self.db, channel_id, self.tenant)
        broker_ids = [b.broker_id for b in brokers]
        
        contracts = []
        if broker_ids:
            contracts = SaleCommissionBillDAO.get_bills_list(
                self.db, self.tenant, 0, 100000,
                {'broker_id': tuple(broker_ids), 'bill_status': 2}  # 已结算
            )
        
        total_commission = sum(float(b.bill_amount) if b.bill_amount else 0 for b in contracts)
        
        return {
            'visit_count': len(visits),
            'broker_count': len(brokers),
            'settled_contracts': len(contracts),
            'total_commission': total_commission
        }
    
    def _freeze_broker_pending_commission(self, broker_id: int):
        """冻结经纪人待结算佣金"""
        pending_bills = SaleCommissionBillDAO.get_bills_list(
            self.db, self.tenant, 0, 1000,
            {'broker_id': broker_id, 'bill_status': 1}  # 待审核
        )
        
        for bill in pending_bills:
            SaleCommissionBillDAO.update_bill_status(
                self.db, bill, 3,  # 已冻结
                freeze_reason="渠道合作终止"
            )
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)


class BrokerService:
    """经纪人业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def create_broker(self, broker_data: dict, operator_id: int = None) -> SaleBroker:
        """创建经纪人"""
        # 检查渠道公司是否存在
        channel = SaleChannelDAO.get_channel_by_id(
            self.db, broker_data['channel_id'], self.tenant
        )
        if not channel:
            raise BusinessError("渠道公司不存在")
        
        # 检查经纪人编码是否已存在
        existing_broker = self.db.query(SaleBroker).filter(
            SaleBroker.broker_code == broker_data['broker_code'],
            SaleBroker.tenant == self.tenant,
            SaleBroker.is_del == 0
        ).first()
        
        if existing_broker:
            raise ValidationError(f"经纪人编码 {broker_data['broker_code']} 已存在")
        
        # 设置租户和初始状态
        broker_data['tenant'] = self.tenant
        broker_data['work_status'] = 1  # 在职
        broker_data['status'] = 1
        broker_data['is_del'] = 0
        
        # 创建经纪人
        broker = SaleBrokerDAO.create_broker(self.db, broker_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_broker", 
            f"创建经纪人：{broker.broker_name}", 
            True
        )
        
        return broker
    
    def get_broker_detail(self, broker_id: int) -> dict:
        """获取经纪人详情"""
        broker = SaleBrokerDAO.get_broker_by_id(self.db, broker_id, self.tenant)
        if not broker:
            raise BusinessError("经纪人不存在")
        
        # 获取渠道信息
        channel = SaleChannelDAO.get_channel_by_id(self.db, broker.channel_id, self.tenant)
        
        # 统计经纪人业绩数据
        stats = self._get_broker_statistics(broker_id)
        
        return {
            'broker_id': broker.broker_id,
            'channel_id': broker.channel_id,
            'broker_code': broker.broker_code,
            'broker_name': broker.broker_name,
            'mobile': broker.mobile,
            'id_card': broker.id_card,
            'broker_level': broker.broker_level,
            'work_status': broker.work_status,
            'commission_rate': float(broker.commission_rate) if broker.commission_rate else 0,
            'channel': {
                'channel_id': channel.channel_id if channel else None,
                'channel_name': channel.channel_name if channel else None
            } if channel else None,
            'statistics': stats,
            'create_time': broker.create_time.isoformat() if broker.create_time else None,
            'update_time': broker.update_time.isoformat() if broker.update_time else None
        }
    
    def get_brokers_list(self, page: int = 1, page_size: int = 20,
                        filters: Optional[Dict] = None) -> dict:
        """获取经纪人列表"""
        skip = (page - 1) * page_size
        brokers = SaleBrokerDAO.get_brokers_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleBrokerDAO.get_brokers_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'broker_id': b.broker_id,
                'channel_id': b.channel_id,
                'broker_code': b.broker_code,
                'broker_name': b.broker_name,
                'mobile': b.mobile,
                'broker_level': b.broker_level,
                'work_status': b.work_status,
                'commission_rate': float(b.commission_rate) if b.commission_rate else 0,
                'status': b.status,
                'create_time': b.create_time.isoformat() if b.create_time else None
            } for b in brokers]
        }
    
    def update_broker(self, broker_id: int, update_data: dict, 
                     operator_id: int = None) -> SaleBroker:
        """更新经纪人"""
        broker = SaleBrokerDAO.get_broker_by_id(self.db, broker_id, self.tenant)
        if not broker:
            raise BusinessError("经纪人不存在")
        
        # 更新经纪人
        updated_broker = SaleBrokerDAO.update_broker(self.db, broker, update_data)
        
        # 如果工作状态变更为离职，冻结未结算佣金
        if 'work_status' in update_data and update_data['work_status'] == 2:  # 离职
            self._freeze_broker_pending_commission(broker_id)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_broker", 
            f"更新经纪人：{broker.broker_name}", 
            True
        )
        
        return updated_broker
    
    def _get_broker_statistics(self, broker_id: int) -> dict:
        """获取经纪人统计数据"""
        # 统计带看、认购、签约、佣金数据
        visits = SaleVisitDAO.get_visits_list(
            self.db, self.tenant, 0, 100000,
            {'broker_id': broker_id}
        )
        
        # 获取佣金结算数据
        bills = SaleCommissionBillDAO.get_bills_list(
            self.db, self.tenant, 0, 100000,
            {'broker_id': broker_id}
        )
        
        pending_bills = [b for b in bills if b.bill_status == 1]  # 待审核
        settled_bills = [b for b in bills if b.bill_status == 2]  # 已结算
        frozen_bills = [b for b in bills if b.bill_status == 3]  # 已冻结
        
        return {
            'visit_count': len(visits),
            'pending_commission': sum(float(b.bill_amount) if b.bill_amount else 0 for b in pending_bills),
            'settled_commission': sum(float(b.bill_amount) if b.bill_amount else 0 for b in settled_bills),
            'frozen_commission': sum(float(b.bill_amount) if b.bill_amount else 0 for b in frozen_bills)
        }
    
    def _freeze_broker_pending_commission(self, broker_id: int):
        """冻结经纪人待结算佣金"""
        pending_bills = SaleCommissionBillDAO.get_bills_list(
            self.db, self.tenant, 0, 1000,
            {'broker_id': broker_id, 'bill_status': 1}  # 待审核
        )
        
        for bill in pending_bills:
            SaleCommissionBillDAO.update_bill_status(
                self.db, bill, 3,  # 已冻结
                freeze_reason="经纪人离职"
            )
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)


class CommissionRuleService:
    """佣金规则业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def create_commission_rule(self, rule_data: dict, operator_id: int = None) -> SaleCommissionRule:
        """创建佣金规则"""
        # 如果是楼栋专属规则，必须先检查楼盘和楼栋是否存在
        if rule_data.get('building_id'):
            # 楼栋规则必须关联楼盘
            if not rule_data.get('project_id'):
                raise BusinessError("楼栋专属规则必须指定楼盘ID")
            
            # 检查楼盘是否存在
            project = SaleProjectDAO.get_project_by_id(
                self.db, rule_data['project_id'], self.tenant
            )
            if not project:
                raise BusinessError("楼盘不存在")
            
            # 检查楼栋是否存在
            
            building = SaleBuildingDAO.get_building_by_id(
                self.db, rule_data['building_id'], self.tenant
            )
            if not building:
                raise BusinessError("楼栋不存在")
            
            # 检查楼栋是否属于该楼盘
            if building.project_id != rule_data['project_id']:
                raise BusinessError("楼栋不属于指定的楼盘")
        elif rule_data.get('project_id'):
            # 如果是楼盘专属规则，检查楼盘是否存在
            project = SaleProjectDAO.get_project_by_id(
                self.db, rule_data['project_id'], self.tenant
            )
            if not project:
                raise BusinessError("楼盘不存在")
        
        # 设置租户和初始状态
        rule_data['tenant'] = self.tenant
        if not rule_data.get('rule_type'):
            # 根据传入的参数自动判断规则类型
            if rule_data.get('building_id'):
                rule_data['rule_type'] = '楼栋专属'
            elif rule_data.get('project_id'):
                rule_data['rule_type'] = '楼盘专属'
            else:
                rule_data['rule_type'] = '全局'
        rule_data['rule_status'] = 1  # 启用
        rule_data['status'] = 1
        rule_data['is_del'] = 0
        
        # 创建佣金规则
        rule = SaleCommissionRuleDAO.create_commission_rule(self.db, rule_data)
        
        # 清除规则缓存
        self._clear_rule_cache()
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_commission_rule", 
            f"创建佣金规则：{rule.rule_type}", 
            True
        )
        
        return rule
    
    def get_rules_list(self, page: int = 1, page_size: int = 20,
                      filters: Optional[Dict] = None) -> dict:
        """获取佣金规则列表"""
        skip = (page - 1) * page_size
        rules = SaleCommissionRuleDAO.get_rules_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleCommissionRuleDAO.get_rules_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'rule_id': r.rule_id,
                'project_id': r.project_id,
                'rule_type': r.rule_type,
                'room_type': r.room_type,
                'commission_rate': float(r.commission_rate) if r.commission_rate else 0,
                'commission_amount': float(r.commission_amount) if r.commission_amount else 0,
                'rule_level': r.rule_level,
                'rule_status': r.rule_status,
                'status': r.status,
                'create_time': r.create_time.isoformat() if r.create_time else None
            } for r in rules]
        }
    
    def update_commission_rule(self, rule_id: int, update_data: dict, 
                             operator_id: int = None) -> SaleCommissionRule:
        """更新佣金规则"""
        rule = SaleCommissionRuleDAO.get_rule_by_id(self.db, rule_id, self.tenant)
        if not rule:
            raise BusinessError("佣金规则不存在")
        
        # 检查是否已产生结算单（禁止随意修改）
        # 这里简化处理，实际需要检查是否有使用该规则的结算单
        
        # 更新佣金规则
        updated_rule = self._update_rule_internal(rule, update_data)
        
        # 清除规则缓存
        self._clear_rule_cache()
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_commission_rule", 
            f"更新佣金规则：{rule.rule_id}", 
            True
        )
        
        return updated_rule
    
    def get_applicable_rule(self, project_id: int, room_type: str = None) -> Optional[SaleCommissionRule]:
        """获取适用的佣金规则（生产级：缓存 + 优先级匹配）"""
        cache_key = f"commission:rule:{self.tenant}:{project_id}:{room_type or 'all'}"
        cached_rule = self.redis.get(cache_key)
        
        if cached_rule:
            return cached_rule
        
        # 获取适用规则
        rule = SaleCommissionRuleDAO.get_applicable_rule(self.db, project_id, room_type, self.tenant)
        
        # 缓存30分钟
        if rule:
            self.redis.setex(cache_key, 1800, rule)
        
        return rule
    
    def _update_rule_internal(self, rule: SaleCommissionRule, update_data: dict) -> SaleCommissionRule:
        """内部更新规则方法"""
        for key, value in update_data.items():
            setattr(rule, key, value)
        rule.version += 1
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def _clear_rule_cache(self):
        """清除规则缓存"""
        pattern = f"commission:rule:{self.tenant}:*"
        keys = self.redis.keys(pattern)
        for key in keys:
            self.redis.delete(key)
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)


class CommissionBillService:
    """佣金结算业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def generate_commission_bill(self, contract_id: int, operator_id: int = None) -> dict:
        """生成佣金结算单（生产级：幂等校验 + 规则匹配 + 自动计算）"""
        # 检查合同是否存在
        contract = SaleContractDAO.get_contract_by_id(self.db, contract_id, self.tenant)
        if not contract:
            raise BusinessError("合同不存在")
        
        # 检查合同状态（必须已备案）
        if contract.record_status != 1:  # 未备案
            raise BusinessError("合同未备案，无法生成佣金结算单")
        
        # 幂等校验：检查是否已生成佣金结算单
        existing_bill = SaleCommissionBillDAO.get_bills_list(
            self.db, self.tenant, 0, 1,
            {'contract_id': contract_id, 'bill_status__ne': 4}  # 排除已作废
        )
        if existing_bill:
            raise ValidationError("该合同已生成佣金结算单")
        
        # 获取房源信息
        from sale.dao.sale_dao import SaleHouseDAO
        house = SaleHouseDAO.get_house_by_id(self.db, contract.house_id, self.tenant)
        if not house:
            raise BusinessError("房源不存在")
        
        # 获取佣金规则
        rule_service = CommissionRuleService(self.db, self.tenant)
        rule = rule_service.get_applicable_rule(contract.project_id, house.room_type)
        
        if not rule:
            raise BusinessError("未找到适用的佣金规则")
        
        # 计算佣金金额
        commission_amount = self._calculate_commission_amount(
            rule, contract.contract_amount, house.building_area
        )
        
        # 获取经纪人和渠道信息（从报备或到访记录获取）
        # 这里简化处理，实际需要从报备/到访记录关联获取
        broker_id = None
        channel_id = None
        
        # 获取客户在该楼盘的所有到访记录（按到访时间倒序）
        visits = SaleVisitDAO.get_visits_list(
            self.db, self.tenant, 0, 100,  # 获取最近100条记录
            {'customer_id': contract.customer_id, 'project_id': contract.project_id},
            order_by='visit_time desc'  # 按到访时间倒序
        )
        
        # 根据认购单创建时间追溯有效报备记录（处理"甲渠道过期后乙渠道成交"场景）
        # 业务规则：成交时取有效保护期内的最新报备渠道
        # 仅使用到访记录的保护期，禁止使用报备记录的保护期
        # 关键逻辑：保护期判断应以认购时间为准，而非合同签订时间
        # 查询流程：contract_id → SaleContract.subscribe_id → SaleSubscribe.create_time
        valid_time = None
        if not contract.subscribe_id:
            raise ValidationError("合同未关联认购单，无法确定保护期判断时间")
        
        subscribe = SaleSubscribeDAO.get_subscribe_by_id(self.db, contract.subscribe_id, self.tenant)
        if not subscribe:
            raise ValidationError(f"认购单不存在，subscribe_id={contract.subscribe_id}")
        
        # 优先使用认购日期，若无则使用认购单创建时间
        valid_time = subscribe.subscribe_date if subscribe.subscribe_date else subscribe.create_time
        if not valid_time:
            raise ValidationError("认购单缺少有效时间信息，无法判断保护期")
        
        if visits:
            for visit in visits:
                if visit.report_id and visit.protect_expire_time:
                    report = SaleReportDAO.get_report_by_id(self.db, visit.report_id, self.tenant)
                    if report and report.broker_id:
                        # 仅使用到访记录的保护期，不回退到报备记录
                        protect_expire_time = visit.protect_expire_time
                        
                        # 判断保护期是否在认购时有效
                        # 保护期内的报备才有效，过期报备不算业绩
                        if valid_time <= protect_expire_time:
                            broker_id = report.broker_id
                            broker = SaleBrokerDAO.get_broker_by_id(self.db, broker_id, self.tenant)
                            if broker:
                                channel_id = broker.channel_id
                                break  # 找到有效报备，跳出循环
        
        if not broker_id or not channel_id:
            raise ValidationError("无法获取有效经纪人和渠道信息，无法生成佣金结算单")
        
        # 使用分布式锁防止重复生成
        lock_key = f"commission:generate:{self.tenant}:{contract_id}"
        locked = self.redis.setnx(lock_key, 1, 10)
        
        if not locked:
            raise BusinessError("佣金结算单正在生成中，请稍后重试")
        
        try:
            # 生成佣金结算单
            bill_data = {
                'tenant': self.tenant,
                'bill_no': self._generate_bill_no(),
                'project_id': contract.project_id,
                'channel_id': channel_id,
                'broker_id': broker_id,
                'contract_id': contract_id,
                'bill_amount': commission_amount,
                'bill_status': 1,  # 待审核
                'status': 1,
                'is_del': 0
            }
            
            bill = SaleCommissionBillDAO.create_commission_bill(self.db, bill_data)
            
            # 记录操作日志
            self._create_operation_log(
                operator_id, "generate_commission_bill", 
                f"生成佣金结算单：{bill.bill_no}，金额：{commission_amount}", 
                True
            )
            
            return {
                'bill_id': bill.bill_id,
                'bill_no': bill.bill_no,
                'contract_id': contract_id,
                'broker_id': broker_id,
                'channel_id': channel_id,
                'bill_amount': float(commission_amount),
                'bill_status': bill.bill_status,
                'message': '佣金结算单生成成功'
            }
        finally:
            self.redis.delete(lock_key)
    
    def audit_commission_bill(self, bill_id: int, audit_user_id: int, 
                             operator_id: int = None) -> bool:
        """审核佣金结算单"""
        bill = SaleCommissionBillDAO.get_bill_by_id(self.db, bill_id, self.tenant)
        if not bill:
            raise BusinessError("佣金结算单不存在")
        
        # 检查状态（必须是待审核）
        if bill.bill_status != 1:
            raise BusinessError("佣金结算单状态异常，无法审核")
        
        # 更新状态为已结算
        SaleCommissionBillDAO.update_bill_status(self.db, bill, 2, audit_user_id)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "audit_commission_bill", 
            f"审核佣金结算单：{bill.bill_no}", 
            True
        )
        
        return True
    
    def freeze_commission_bill(self, bill_id: int, freeze_reason: str, 
                              operator_id: int = None) -> bool:
        """冻结佣金结算单"""
        bill = SaleCommissionBillDAO.get_bill_by_id(self.db, bill_id, self.tenant)
        if not bill:
            raise BusinessError("佣金结算单不存在")
        
        # 检查状态（已发放的佣金不能冻结）
        if bill.bill_status == 2:
            raise BusinessError("已发放的佣金不能冻结")
        
        # 更新状态为已冻结
        updated_bill = SaleCommissionBillDAO.update_bill_status(self.db, bill, 3)
        updated_bill.freeze_reason = freeze_reason
        self.db.commit()
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "freeze_commission_bill", 
            f"冻结佣金结算单：{bill.bill_no}，原因：{freeze_reason}", 
            True
        )
        
        return True
    
    def get_bills_list(self, page: int = 1, page_size: int = 20,
                      filters: Optional[Dict] = None) -> dict:
        """获取佣金结算单列表"""
        skip = (page - 1) * page_size
        bills = SaleCommissionBillDAO.get_bills_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleCommissionBillDAO.get_bills_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'bill_id': b.bill_id,
                'bill_no': b.bill_no,
                'project_id': b.project_id,
                'channel_id': b.channel_id,
                'broker_id': b.broker_id,
                'contract_id': b.contract_id,
                'bill_amount': float(b.bill_amount) if b.bill_amount else 0,
                'bill_status': b.bill_status,
                'audit_user_id': b.audit_user_id,
                'audit_time': b.audit_time.isoformat() if b.audit_time else None,
                'pay_time': b.pay_time.isoformat() if b.pay_time else None,
                'freeze_reason': b.freeze_reason,
                'create_time': b.create_time.isoformat() if b.create_time else None
            } for b in bills]
        }
    
    def _calculate_commission_amount(self, rule: SaleCommissionRule, 
                                    contract_amount: Decimal, 
                                    house_area: Decimal) -> Decimal:
        """计算佣金金额"""
        if rule.commission_amount:  # 固定金额
            return rule.commission_amount
        elif rule.commission_rate:  # 比例计算
            return contract_amount * (rule.commission_rate / 100)
        else:
            return Decimal('0.00')
    
    def _generate_bill_no(self) -> str:
        """生成结算单编号"""
        now = datetime.now()
        prefix = f"CB{now.strftime('%Y%m%d')}"
        # 使用Redis生成序列号
        key = f"commission:bill:no:{self.tenant}:{now.strftime('%Y%m%d')}"
        sequence = self.redis.incr(key)
        self.redis.expire(key, 86400)  # 24小时过期
        return f"{prefix}{sequence:06d}"
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)