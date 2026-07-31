"""
房地产SaaS销售管理系统 - 客户全生命周期管理业务逻辑层
实现客户档案、报备到访、跟进维护、公海管理、黑名单风控全生命周期闭环
"""

import os
import qrcode
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from core.redis_base import RedisClient
from core.exception import BusinessError, ValidationError

from sale.dao.sale_dao import (
    SaleCustomerDAO, SaleCustomerTagDAO, SaleCustomerDemandDAO, 
    SaleReportDAO, SaleVisitDAO, SaleFollowDAO, SaleFollowRemindDAO, 
    SaleBlacklistDAO, SaleStatDailyLogsDAO, SaleProjectRuleDAO
)
from sale.model.sale_models import (
    SaleCustomer, SaleCustomerTag, SaleCustomerDemand, SaleReport, 
    SaleVisit, SaleFollow, SaleFollowRemind, SaleBlacklist
)


class CustomerService:
    """客户档案业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def create_customer(self, customer_data: dict, tags: List[str] = None, 
                       demands: List[dict] = None, operator_id: int = None) -> SaleCustomer:
        """创建客户（生产级：防撞客 + 幂等校验 + 审计日志）"""
        # 检查黑名单
        if SaleBlacklistDAO.check_is_blacklist(self.db, customer_data['mobile'], self.tenant):
            raise BusinessError("客户在黑名单中，无法建档")
        
        # 防撞客：检查手机号是否已存在
        existing_customer = SaleCustomerDAO.get_customer_by_mobile(
            self.db, customer_data['mobile'], self.tenant
        )
        if existing_customer:
            raise ValidationError(f"客户手机号 {customer_data['mobile']} 已存在")
        
        # 设置租户和初始状态
        customer_data['tenant'] = self.tenant
        customer_data['customer_level'] = 'C'  # 默认C级客户
        customer_data['customer_status'] = 1  # 跟进中
        customer_data['is_blacklist'] = 0
        customer_data['status'] = 1
        customer_data['is_del'] = 0
        
        # 创建客户
        customer = SaleCustomerDAO.create_customer(self.db, customer_data)
        
        # 创建客户标签
        if tags:
            for tag_name in tags:
                tag_data = {
                    'tenant': self.tenant,
                    'customer_id': customer.customer_id,
                    'tag_name': tag_name,
                    'tag_type': '自定义',
                    'status': 1,
                    'is_del': 0
                }
                SaleCustomerTagDAO.create_tag(self.db, tag_data)
        
        # 创建购房需求
        if demands:
            for demand in demands:
                demand_data = {
                    **demand,
                    'tenant': self.tenant,
                    'customer_id': customer.customer_id,
                    'status': 1,
                    'is_del': 0
                }
                SaleCustomerDemandDAO.create_demand(self.db, demand_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_customer", 
            f"创建客户：{customer.customer_name}", 
            True
        )
        
        return customer
    
    def get_customer_detail(self, customer_id: int) -> dict:
        """获取客户详情（生产级：手机号身份证脱敏）"""
        customer = SaleCustomerDAO.get_customer_by_id(self.db, customer_id, self.tenant)
        if not customer:
            raise BusinessError("客户不存在")
        
        # 获取客户标签
        tags = SaleCustomerTagDAO.get_tags_by_customer(self.db, customer_id, self.tenant)
        
        # 获取购房需求
        demands = SaleCustomerDemandDAO.get_demands_by_customer(self.db, customer_id, self.tenant)
        
        return {
            'customer_id': customer.customer_id,
            'customer_name': customer.customer_name,
            'mobile': self._mask_mobile(customer.mobile),
            'id_card': self._mask_id_card(customer.id_card) if customer.id_card else None,
            'gender': customer.gender,
            'age': customer.age,
            'customer_level': customer.customer_level,
            'customer_source': customer.customer_source,
            'belong_user_id': customer.belong_user_id,
            'belong_team_id': customer.belong_team_id,
            'first_visit_time': customer.first_visit_time.isoformat() if customer.first_visit_time else None,
            'last_visit_time': customer.last_visit_time.isoformat() if customer.last_visit_time else None,
            'last_follow_time': customer.last_follow_time.isoformat() if customer.last_follow_time else None,
            'customer_status': customer.customer_status,
            'is_blacklist': customer.is_blacklist,
            'tags': [{'tag_id': t.tag_id, 'tag_name': t.tag_name} for t in tags],
            'demands': [{
                'demand_id': d.demand_id,
                'intent_project': d.intent_project,
                'intent_room_type': d.intent_room_type,
                'intent_area_min': float(d.intent_area_min) if d.intent_area_min else None,
                'intent_area_max': float(d.intent_area_max) if d.intent_area_max else None,
                'budget_min': float(d.budget_min) if d.budget_min else None,
                'budget_max': float(d.budget_max) if d.budget_max else None,
                'purchase_purpose': d.purchase_purpose,
                'remark': d.remark
            } for d in demands],
            'create_time': customer.create_time.isoformat() if customer.create_time else None
        }
    
    def get_customers_list(self, page: int = 1, page_size: int = 20,
                          filters: Optional[Dict] = None) -> dict:
        """获取客户列表（生产级：数据权限拦截）"""
        skip = (page - 1) * page_size
        customers = SaleCustomerDAO.get_customers_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleCustomerDAO.get_customers_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'customer_id': c.customer_id,
                'customer_name': c.customer_name,
                'mobile': self._mask_mobile(c.mobile),
                'customer_level': c.customer_level,
                'customer_source': c.customer_source,
                'belong_user_id': c.belong_user_id,
                'belong_team_id': c.belong_team_id,
                'customer_status': c.customer_status,
                'last_follow_time': c.last_follow_time.isoformat() if c.last_follow_time else None,
                'create_time': c.create_time.isoformat() if c.create_time else None
            } for c in customers]
        }
    
    def update_customer(self, customer_id: int, update_data: dict, 
                       operator_id: int = None) -> SaleCustomer:
        """更新客户（生产级：关键信息变更审计日志）"""
        customer = SaleCustomerDAO.get_customer_by_id(self.db, customer_id, self.tenant)
        if not customer:
            raise BusinessError("客户不存在")
        
        # 已成交客户禁止修改核心信息
        if customer.customer_status == 2:  # 已成交
            protected_fields = ['mobile', 'id_card', 'belong_user_id']
            for field in protected_fields:
                if field in update_data and update_data[field] != getattr(customer, field):
                    raise BusinessError("已成交客户禁止修改核心信息")
        
        # 关键信息变更记录审计日志
        key_fields = ['mobile', 'id_card', 'belong_user_id', 'belong_team_id']
        for field in key_fields:
            if field in update_data and update_data[field] != getattr(customer, field):
                self._create_operation_log(
                    operator_id, "update_customer_key_info", 
                    f"修改客户{field}：{customer.customer_name}，从{getattr(customer, field)}改为{update_data[field]}", 
                    True
                )
        
        # 更新客户
        updated_customer = SaleCustomerDAO.update_customer(self.db, customer, update_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_customer", 
            f"更新客户：{customer.customer_name}", 
            True
        )
        
        return updated_customer
    
    def delete_customer(self, customer_id: int, operator_id: int = None) -> bool:
        """删除客户（生产级：已成交客户禁止删除 + 黑名单逻辑）"""
        customer = SaleCustomerDAO.get_customer_by_id(self.db, customer_id, self.tenant)
        if not customer:
            raise BusinessError("客户不存在")
        
        # 已成交客户禁止删除
        if customer.customer_status == 2:
            raise BusinessError("已成交客户禁止删除")
        
        # 逻辑删除并加入黑名单
        result = SaleCustomerDAO.delete_customer(self.db, customer_id, self.tenant)
        
        if result:
            # 添加到黑名单
            blacklist_data = {
                'tenant': self.tenant,
                'customer_id': customer_id,
                'customer_name': customer.customer_name,
                'mobile': customer.mobile,
                'id_card': customer.id_card,
                'blacklist_reason': '客户删除',
                'blacklist_type': '其他',
                'add_user_id': operator_id,
                'add_time': datetime.now(),
                'status': 1,
                'is_del': 0
            }
            SaleBlacklistDAO.create_blacklist(self.db, blacklist_data)
            
            # 记录操作日志
            self._create_operation_log(
                operator_id, "delete_customer", 
                f"删除客户：{customer.customer_name}", 
                True
            )
        
        return result
    
    def transfer_customer(self, customer_id: int, target_user_id: int, 
                          operator_id: int = None) -> SaleCustomer:
        """转移客户归属"""
        customer = SaleCustomerDAO.get_customer_by_id(self.db, customer_id, self.tenant)
        if not customer:
            raise BusinessError("客户不存在")
        
        # 检查目标用户是否存在
        # TODO: 调用用户服务验证目标用户是否存在
        
        # 更新客户归属
        update_data = {
            'belong_user_id': target_user_id,
            'customer_status': 1  # 跟进中
        }
        updated_customer = SaleCustomerDAO.update_customer(self.db, customer, update_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "transfer_customer", 
            f"转移客户归属：{customer.customer_name} -> 用户ID {target_user_id}", 
            True
        )
        
        return updated_customer
    
    def release_to_sea(self, customer_id: int, operator_id: int = None) -> bool:
        """释放客户到公海"""
        customer = SaleCustomerDAO.get_customer_by_id(self.db, customer_id, self.tenant)
        if not customer:
            raise BusinessError("客户不存在")
        
        # 已成交、已流失客户禁止释放
        if customer.customer_status in [2, 3]:
            raise BusinessError("已成交、已流失客户禁止释放到公海")
        
        # 释放到公海
        result = SaleCustomerDAO.release_to_sea(self.db, customer_id, self.tenant)
        
        if result:
            # 终止所有跟进提醒
            reminds = SaleFollowRemindDAO.get_reminds_by_customer(self.db, customer_id, self.tenant)
            for remind in reminds:
                SaleFollowRemindDAO.complete_remind(self.db, remind.remind_id, self.tenant)
            
            # 记录操作日志
            self._create_operation_log(
                operator_id, "release_to_sea", 
                f"释放客户到公海：{customer.customer_name}", 
                True
            )
        
        return result
    
    def receive_from_sea(self, customer_id: int, user_id: int, team_id: int = None, 
                        operator_id: int = None) -> SaleCustomer:
        """从公海领取客户（生产级：限流控制）"""
        customer = SaleCustomerDAO.get_customer_by_id(self.db, customer_id, self.tenant)
        if not customer:
            raise BusinessError("客户不存在")
        
        # 检查客户是否在公海
        if customer.customer_status != 4:  # 不是公海状态
            raise BusinessError("客户不在公海中")
        
        # 每日领取限流控制
        today = datetime.now().date()
        cache_key = f"sea:receive:daily:{self.tenant}:{user_id}:{today}"
        daily_count = self.redis.get(cache_key) or 0
        if int(daily_count) >= 10:  # 每日最多领取10个
            raise BusinessError("每日领取公海客户数量已达上限")
        
        # 领取客户
        update_data = {
            'belong_user_id': user_id,
            'belong_team_id': team_id,
            'customer_status': 1  # 跟进中
        }
        updated_customer = SaleCustomerDAO.update_customer(self.db, customer, update_data)
        
        # 更新限流计数
        self.redis.incr(cache_key)
        self.redis.expire(cache_key, 86400)  # 24小时过期
        
        # 记录操作日志
        self._create_operation_log(
            operator_id or user_id, "receive_from_sea", 
            f"从公海领取客户：{customer.customer_name}", 
            True
        )
        
        return updated_customer
    
    def _mask_mobile(self, mobile: str) -> str:
        """手机号脱敏"""
        if not mobile or len(mobile) != 11:
            return mobile
        return f"{mobile[:3]}****{mobile[7:]}"
    
    def _mask_id_card(self, id_card: str) -> str:
        """身份证号脱敏"""
        if not id_card or len(id_card) != 18:
            return id_card
        return f"{id_card[:6]}********{id_card[14:]}"
    
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


class ReportVisitService:
    """报备到访业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
        # 依赖注入 CustomerService，复用客户创建逻辑
        self.customer_service = CustomerService(db, tenant)
    
    def _generate_report_no(self) -> str:
        """生成报备编号"""
        date_str = datetime.now().strftime("%Y%m%d")
        seq = 1
        while True:
            report_no = f"RP{date_str}{seq:04d}"
            existing = self.db.query(SaleReport).filter(
                and_(SaleReport.report_no == report_no, SaleReport.tenant == self.tenant)
            ).first()
            if not existing:
                return report_no
            seq += 1
            if seq > 9999:
                raise BusinessError("当日报备编号已达上限")
    
    def create_report(self, report_data: dict, operator_id: int = None) -> SaleReport:
        """创建报备（经纪人报备成功后，先生成报备记录表数据，再生成二维码，确客后再生成客户档案表）"""
        mobile = report_data.get('mobile')
        customer_name = report_data.get('customer_name')
        
        if not mobile or not customer_name:
            raise BusinessError("客户姓名和手机号不能为空")
        
        # 第一步：检查客户档案表中是否存在相同手机号的客户记录
        existing_report = SaleCustomerDAO.get_customer_by_mobile(self.db, mobile, self.tenant)
        
        if existing_report:
            # 第二步：存在客户记录，检查客户档案表的last_visit_time是否超过到访保护期
            customer = SaleCustomerDAO.get_customer_by_mobile(self.db, mobile, self.tenant)
            if customer and customer.last_visit_time:
                # 获取到访保护期规则（优先项目规则，其次全局规则，默认30天）
                project_id = report_data.get('project_id')
                visit_protect_days = SaleProjectRuleDAO.get_rule_value(
                    self.db, project_id, 'visit_protect_days', self.tenant, default_value=30
                )
                days_diff = (datetime.now() - customer.last_visit_time).days
                if days_diff < visit_protect_days:
                    raise BusinessError(f"该客户{visit_protect_days}天内已有到访记录，无法重复报备")
            # 如果last_visit_time为空或超过保护期，继续报备流程
        
        # 设置租户和初始状态（客户ID在确客后再关联）
        report_data['tenant'] = self.tenant
        report_data['customer_name'] = customer_name
        report_data['mobile'] = mobile
        report_data['customer_id'] = None  # 报备阶段不关联客户档案
        report_data['report_time'] = datetime.now()
        report_data['report_status'] = 1  # 有效
        report_data['visit_status'] = 0  # 未到访
        report_data['status'] = 1
        report_data['is_del'] = 0
        
        # 获取报备保护期规则（优先项目规则，其次全局规则，默认1天）
        project_id = report_data.get('project_id')
        protect_days = SaleProjectRuleDAO.get_rule_value(
            self.db, project_id, 'report_protect_days', self.tenant, default_value=1
        )
        report_data['protect_expire_time'] = datetime.now() + timedelta(days=protect_days)
        
        # 生成报备编号
        report_data['report_no'] = self._generate_report_no()
        
        # 创建报备记录（先生成报备表数据）
        report = SaleReportDAO.create_report(self.db, report_data)
        
        # 生成二维码（报备成功后生成二维码）
        qrcode_url = self._generate_qrcode(report.report_id)
        report.qrcode_url = qrcode_url
        SaleReportDAO.update_report(self.db, report, {'qrcode_url': qrcode_url})
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_report", 
            f"创建报备：报备ID{report.report_id} 手机号{mobile} 楼盘ID{report_data['project_id']} 渠道ID{report_data.get('channel_id')}", 
            True
        )
        
        return report
    
    def _generate_qrcode(self, report_id: int) -> str:
        """生成报备二维码URL（使用qrcode库生成实际二维码）"""
        # 生成二维码数据（包含报备ID和租户信息）
        qrcode_data = f"report_id={report_id}&tenant={self.tenant}&timestamp={datetime.now().timestamp()}"
        
        # 创建二维码存储目录
        qrcode_dir = "static/qrcodes"
        if not os.path.exists(qrcode_dir):
            os.makedirs(qrcode_dir)
        
        # 生成二维码图片
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qrcode_data)
        qr.make(fit=True)
        
        # 生成并保存二维码图片
        img = qr.make_image(fill_color='black', back_color='white')
        qrcode_path = f"{qrcode_dir}/report_{report_id}.png"
        img.save(qrcode_path)
        
        # 返回二维码访问URL
        return f"/{qrcode_path}"
    
    def confirm_visit(self, report_id: int, visit_data: dict, operator_id: int = None) -> SaleVisit:
        """确客到访（扫码到访：创建客户档案 + 创建到访记录 + 关联报备）"""
        # 1. 查询报备记录
        report = SaleReportDAO.get_report_by_id(self.db, report_id, self.tenant)
        if not report:
            raise BusinessError("报备记录不存在")
        
        # 2. 检查报备是否已到访
        if report.visit_status == 1:
            raise BusinessError("该报备已完成到访")
        
        # 3. 检查报备是否过期（超过保护期）
        if report.protect_expire_time and datetime.now() > report.protect_expire_time:
            raise BusinessError("报备已过期")
        
        # 4. 检查或创建客户档案（复用 CustomerService.create_customer 方法）
        customer = SaleCustomerDAO.get_customer_by_mobile(self.db, report.mobile, self.tenant)
        if not customer:
            # 创建客户档案（调用 CustomerService，自动处理黑名单检查和防撞客）
            customer_data = {
                'customer_name': report.customer_name,
                'mobile': report.mobile,
                'first_visit_time': datetime.now(),
                'last_visit_time': datetime.now(),
                'report_id': report.report_id  # 关联报备记录
            }
            customer = self.customer_service.create_customer(customer_data, operator_id=operator_id)
        
        # 5. 更新报备记录，关联客户ID
        SaleReportDAO.update_report(self.db, report, {'customer_id': customer.customer_id})
        
        # 6. 调用 create_visit 创建到访记录（复用已有逻辑）
        visit_data['customer_id'] = customer.customer_id
        visit_data['report_id'] = report.report_id
        visit_data['project_id'] = report.project_id
        visit = self.create_visit(visit_data, operator_id)
        
        # 7. 记录确客到访操作日志（与 create_visit 的日志区分）
        self._create_operation_log(
            operator_id, "confirm_visit",
            f"确客到访：报备ID{report_id} 客户ID{customer.customer_id} 楼盘ID{report.project_id}",
            True
        )
        
        return visit
    
    def create_visit(self, visit_data: dict, operator_id: int = None) -> SaleVisit:
        """创建到访记录（生产级：自动核销报备 + 保护期释放）"""
        # 检查客户是否存在
        customer = SaleCustomerDAO.get_customer_by_id(
            self.db, visit_data['customer_id'], self.tenant
        )
        if not customer:
            raise BusinessError("客户不存在")
        
        # 设置租户和初始状态
        visit_data['tenant'] = self.tenant
        visit_data['visit_time'] = datetime.now()
        visit_data['visit_status'] = 1  # 有效
        visit_data['status'] = 1
        visit_data['is_del'] = 0
        
        # 获取到访保护期规则（优先项目规则，其次全局规则，默认30天）
        project_id = visit_data.get('project_id')
        protect_expire_time_rule = SaleProjectRuleDAO.get_rule_value(
            self.db, project_id, 'visit_protect_days', self.tenant, default_value=30
        )
        
        # 计算保护期过期时间 = 创建时间 + 保护期规则天数
        visit_data['protect_expire_time'] = datetime.now() + timedelta(days=protect_expire_time_rule)
        
        # 确定到访类型
        existing_visits = SaleVisitDAO.get_visits_list(
            self.db, self.tenant, 0, 1, 
            {'customer_id': visit_data['customer_id'], 'project_id': visit_data['project_id']}
        )
        if existing_visits:
            visit_data['visit_type'] = '多次到访'
        else:
            visit_data['visit_type'] = '首次到访'
            
            # 更新客户首次到访时间
            if not customer.first_visit_time:
                SaleCustomerDAO.update_customer(self.db, customer, {'first_visit_time': datetime.now()})
        
        # 创建到访记录
        visit = SaleVisitDAO.create_visit(self.db, visit_data)
        
        # 更新客户最后到访时间
        SaleCustomerDAO.update_customer(self.db, customer, {'last_visit_time': datetime.now()})
        
        # 核销关联报备
        if visit_data.get('report_id'):
            report = SaleReportDAO.get_report_by_id(self.db, visit_data['report_id'], self.tenant)
            if report:
                SaleReportDAO.update_report(self.db, report, {
                    'visit_status': 1,  # 已到访
                    'visit_time': datetime.now()
                })
                
                # 失效同一手机号下所有未过期报备（多渠道报备场景）
                all_reports = SaleReportDAO.get_reports_by_mobile(
                    self.db, report.mobile, visit_data['project_id'], self.tenant
                )
                for r in all_reports:
                    if r.report_id != visit_data['report_id'] and r.report_status == 1:
                        SaleReportDAO.update_report(self.db, r, {'report_status': 2})  # 失效
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_visit", 
            f"创建到访：客户ID{visit_data['customer_id']} 楼盘ID{visit_data['project_id']}", 
            True
        )
        
        return visit
    
    def get_reports_list(self, page: int = 1, page_size: int = 20,
                        filters: Optional[Dict] = None) -> dict:
        """获取报备列表"""
        skip = (page - 1) * page_size
        reports = SaleReportDAO.get_reports_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleReportDAO.get_reports_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'report_id': r.report_id,
                'customer_id': r.customer_id,
                'project_id': r.project_id,
                'report_user_id': r.report_user_id,
                'channel_id': r.channel_id,
                'broker_id': r.broker_id,
                'customer_name': r.customer_name,
                'mobile': r.mobile,
                'report_time': r.report_time.isoformat() if r.report_time else None,
                'protect_expire_time': r.protect_expire_time.isoformat() if r.protect_expire_time else None,
                'visit_status': r.visit_status,
                'visit_time': r.visit_time.isoformat() if r.visit_time else None,
                'report_status': r.report_status,
                'create_time': r.create_time.isoformat() if r.create_time else None
            } for r in reports]
        }
    
    def get_visits_list(self, page: int = 1, page_size: int = 20,
                       filters: Optional[Dict] = None) -> dict:
        """获取到访列表"""
        skip = (page - 1) * page_size
        visits = SaleVisitDAO.get_visits_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleVisitDAO.get_visits_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'visit_id': v.visit_id,
                'customer_id': v.customer_id,
                'project_id': v.project_id,
                'report_id': v.report_id,
                'receive_user_id': v.receive_user_id,
                'visit_time': v.visit_time.isoformat() if v.visit_time else None,
                'visit_type': v.visit_type,
                'reception_score': float(v.reception_score) if v.reception_score else None,
                'protect_expire_time': v.protect_expire_time.isoformat() if v.protect_expire_time else None,
                'visit_status': v.visit_status,
                'create_time': v.create_time.isoformat() if v.create_time else None
            } for v in visits]
        }
    
    def get_visit_statistics(self, project_id: int, start_date: datetime, 
                            end_date: datetime) -> dict:
        """获取到访统计数据"""
        return SaleVisitDAO.get_visit_statistics(
            self.db, project_id, self.tenant, start_date, end_date
        )
    
    def get_report_statistics(self, project_id: int, start_date: datetime, 
                            end_date: datetime) -> dict:
        """获取报备统计数据"""
        return SaleReportDAO.get_report_statistics(
            self.db, project_id, self.tenant, start_date, end_date
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


class FollowService:
    """跟进维护业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def create_follow(self, follow_data: dict, create_remind: bool = True, 
                     operator_id: int = None) -> SaleFollow:
        """创建跟进记录（生产级：自动更新客户最后跟进时间 + 意向等级调整）"""
        # 检查客户是否存在
        customer = SaleCustomerDAO.get_customer_by_id(
            self.db, follow_data['customer_id'], self.tenant
        )
        if not customer:
            raise BusinessError("客户不存在")
        
        # 设置租户和初始状态
        follow_data['tenant'] = self.tenant
        follow_data['follow_time'] = datetime.now()
        follow_data['follow_status'] = 1  # 正常
        follow_data['status'] = 1
        follow_data['is_del'] = 0
        
        # 创建跟进记录
        follow = SaleFollowDAO.create_follow(self.db, follow_data)
        
        # 更新客户最后跟进时间
        SaleCustomerDAO.update_customer(self.db, customer, {'last_follow_time': datetime.now()})
        
        # 根据客户意向变化自动调整客户等级
        if follow_data.get('customer_intention'):
            intention_level_map = {
                '高意向': 'A',
                '中意向': 'B',
                '低意向': 'C'
            }
            new_level = intention_level_map.get(follow_data['customer_intention'])
            if new_level and new_level != customer.customer_level:
                SaleCustomerDAO.update_customer(self.db, customer, {'customer_level': new_level})
        
        # 创建跟进提醒
        if create_remind and follow_data.get('next_follow_time'):
            remind_data = {
                'tenant': self.tenant,
                'customer_id': follow_data['customer_id'],
                'follow_id': follow.follow_id,
                'remind_user_id': follow_data['follow_user_id'],
                'remind_time': follow_data['next_follow_time'],
                'remind_content': f"跟进提醒：{follow_data.get('follow_content', '')[:50]}",
                'remind_status': 0,  # 待跟进
                'status': 1,
                'is_del': 0
            }
            SaleFollowRemindDAO.create_remind(self.db, remind_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_follow", 
            f"创建跟进记录：客户ID{follow_data['customer_id']}", 
            True
        )
        
        return follow
    
    def get_follows_list(self, page: int = 1, page_size: int = 20,
                        filters: Optional[Dict] = None) -> dict:
        """获取跟进记录列表"""
        skip = (page - 1) * page_size
        follows = SaleFollowDAO.get_follows_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleFollowDAO.get_follows_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'follow_id': f.follow_id,
                'customer_id': f.customer_id,
                'follow_user_id': f.follow_user_id,
                'follow_time': f.follow_time.isoformat() if f.follow_time else None,
                'follow_method': f.follow_method,
                'follow_content': f.follow_content,
                'customer_intention': f.customer_intention,
                'next_follow_time': f.next_follow_time.isoformat() if f.next_follow_time else None,
                'follow_status': f.follow_status,
                'create_time': f.create_time.isoformat() if f.create_time else None
            } for f in follows]
        }
    
    def get_reminds_list(self, user_id: int, page: int = 1, page_size: int = 20) -> dict:
        """获取待跟进提醒列表（生产级：超时提醒置顶）"""
        skip = (page - 1) * page_size
        reminds = SaleFollowRemindDAO.get_reminds_list(self.db, self.tenant, user_id, skip, page_size)
        
        # 获取超时提醒并置顶
        timeout_reminds = SaleFollowRemindDAO.get_timeout_reminds(self.db, self.tenant)
        timeout_reminds = [r for r in timeout_reminds if r.remind_user_id == user_id]
        
        total = len(reminds) + len(timeout_reminds)
        
        # 超时提醒在前，正常提醒在后
        all_reminds = timeout_reminds + [r for r in reminds if r.remind_id not in [t.remind_id for t in timeout_reminds]]
        page_reminds = all_reminds[skip:skip + page_size]
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'remind_id': r.remind_id,
                'customer_id': r.customer_id,
                'follow_id': r.follow_id,
                'remind_user_id': r.remind_user_id,
                'remind_time': r.remind_time.isoformat() if r.remind_time else None,
                'remind_content': r.remind_content,
                'remind_status': r.remind_status,
                'is_timeout': r.remind_time < datetime.now(),
                'complete_time': r.complete_time.isoformat() if r.complete_time else None,
                'create_time': r.create_time.isoformat() if r.create_time else None
            } for r in page_reminds]
        }
    
    def complete_remind(self, remind_id: int, operator_id: int = None) -> bool:
        """完成跟进提醒"""
        result = SaleFollowRemindDAO.complete_remind(self.db, remind_id, self.tenant)
        
        if result:
            # 记录操作日志
            self._create_operation_log(
                operator_id, "complete_remind", 
                f"完成跟进提醒：{remind_id}", 
                True
            )
        
        return result
    
    def auto_recycle_sea_customers(self) -> int:
        """自动回收超时未跟进客户到公海（定时任务）"""
        # 获取超时未跟进的客户（30天未跟进）
        timeout_date = datetime.now() - timedelta(days=30)
        customers = SaleCustomerDAO.get_customers_list(
            self.db, self.tenant, 0, 10000,
            {'last_follow_time_max': timeout_date, 'customer_status': 1}  # 跟进中
        )
        
        recycle_count = 0
        for customer in customers:
            try:
                SaleCustomerDAO.release_to_sea(self.db, customer.customer_id, self.tenant)
                recycle_count += 1
                
                # 记录操作日志
                self._create_operation_log(
                    0, "auto_recycle_sea", 
                    f"自动回收超时未跟进客户：{customer.customer_name}", 
                    True
                )
            except Exception as e:
                continue
        
        return recycle_count
    
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


class SeaCustomerService:
    """公海客户业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
    
    def add_customer_to_sea(self, customer_id: int, operator_id: int = None) -> bool:
        """添加客户到公海（释放客户归属）"""
        customer = SaleCustomerDAO.get_customer_by_id(self.db, customer_id, self.tenant)
        if not customer:
            raise BusinessError("客户不存在")
        
        # 已在公海的客户不能重复添加
        if customer.customer_status == 4:
            raise BusinessError("客户已在公海中")
        
        # 已成交、已流失客户禁止释放
        if customer.customer_status in [2, 3]:
            raise BusinessError("已成交、已流失客户禁止释放到公海")
        
        # 释放到公海
        result = SaleCustomerDAO.release_to_sea(self.db, customer_id, self.tenant)
        
        if result:
            # 终止所有跟进提醒
            reminds = SaleFollowRemindDAO.get_reminds_by_customer(self.db, customer_id, self.tenant)
            for remind in reminds:
                SaleFollowRemindDAO.complete_remind(self.db, remind.remind_id, self.tenant)
            
            # 记录操作日志
            log_data = {
                'tenant': self.tenant,
                'user_id': operator_id,
                'operation_type': 'add_customer_to_sea',
                'operation_content': f"添加客户到公海：{customer.customer_name}",
                'operation_result': 1,
                'create_time': datetime.now()
            }
            SaleStatDailyLogsDAO.create_log(self.db, log_data)
        
        return result
    
    def pick_customer_from_sea(self, customer_id: int, user_id: int, 
                               operator_id: int = None) -> SaleCustomer:
        """从公海认领客户"""
        customer = SaleCustomerDAO.get_customer_by_id(self.db, customer_id, self.tenant)
        if not customer:
            raise BusinessError("客户不存在")
        
        # 检查客户是否在公海
        if customer.customer_status != 4:
            raise BusinessError("客户不在公海中，无法认领")
        
        # 认领客户
        update_data = {
            'belong_user_id': user_id,
            'customer_status': 1  # 跟进中
        }
        updated_customer = SaleCustomerDAO.update_customer(self.db, customer, update_data)
        
        # 记录操作日志
        log_data = {
            'tenant': self.tenant,
            'user_id': operator_id or user_id,
            'operation_type': 'pick_customer_from_sea',
            'operation_content': f"从公海认领客户：{customer.customer_name}",
            'operation_result': 1,
            'create_time': datetime.now()
        }
        SaleStatDailyLogsDAO.create_log(self.db, log_data)
        
        return updated_customer
    
    def get_sea_customers_list(self, page: int = 1, page_size: int = 20,
                              filters: Optional[Dict] = None) -> dict:
        """获取公海客户列表"""
        if filters is None:
            filters = {}
        filters['customer_status'] = 4  # 公海状态
        
        skip = (page - 1) * page_size
        customers = SaleCustomerDAO.get_customers_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleCustomerDAO.get_customers_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'customer_id': c.customer_id,
                'customer_name': c.customer_name,
                'mobile': CustomerService(self.db, self.tenant)._mask_mobile(c.mobile),
                'customer_level': c.customer_level,
                'last_follow_time': c.last_follow_time.isoformat() if c.last_follow_time else None,
                'create_time': c.create_time.isoformat() if c.create_time else None
            } for c in customers]
        }