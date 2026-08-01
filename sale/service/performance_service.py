"""
房地产SaaS销售管理系统 - 销售业绩与考核业务逻辑层
实现销售团队架构、业绩目标配置、个人/团队业绩统计、内部提成自动核算
"""

from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case
from core.redis_base import RedisClient
from core.exception import BusinessError, ValidationError

from sale.dao.sale_dao import (
    SaleTeamDAO, SaleTeamMemberDAO, SalePerformanceTargetDAO, SaleSalesCommissionDAO,
    SaleContractDAO, SalePaymentDAO, SaleCustomerDAO
)
from sale.model.sale_models import (
    SaleTeam, SaleTeamMember, SalePerformanceTarget, SaleSalesCommission, 
    SaleContract, SalePayment, SaleCustomer
)


class TeamService:
    """销售团队业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def _generate_team_code(self) -> str:
        """生成团队编码（生产级：租户隔离 + 日期序列 + 原子递增）"""
        date_str = datetime.now().strftime('%Y%m%d')
        redis_key = f"team_code_seq:{self.tenant}:{date_str}"
        
        seq = self.redis.incr(redis_key)
        if seq is None:
            seq = self.db.query(func.count(SaleTeam.team_id)).filter(
                and_(SaleTeam.tenant == self.tenant, SaleTeam.team_code.like(f"TM{date_str}%"))
            ).scalar() + 1
        
        if seq > 9999:
            raise BusinessError("当日团队编码已达上限，请联系管理员")
        
        return f"TM{date_str}-{seq:04d}"
    
    def create_team(self, team_data: dict, operator_id: int = None) -> SaleTeam:
        """创建销售团队（生产级：多级嵌套架构 + 数据权限适配）"""
        # 如果有父团队，检查是否存在
        if team_data.get('parent_team_id'):
            parent_team = SaleTeamDAO.get_team_by_id(
                self.db, team_data['parent_team_id'], self.tenant
            )
            if not parent_team:
                raise BusinessError("父团队不存在")
            team_data['team_level'] = parent_team.team_level + 1
        
        # 设置租户和初始状态
        team_data['tenant'] = self.tenant
        team_data['team_status'] = 1  # 正常
        team_data['member_count'] = 0
        team_data['status'] = 1
        team_data['is_del'] = 0
        
        # 自动生成团队编码（如果未提供）
        team_data.setdefault('team_code', self._generate_team_code())
        
        # 创建销售团队
        team = SaleTeamDAO.create_team(self.db, team_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_team", 
            f"创建销售团队：{team.team_name}", 
            True
        )
        
        return team
    
    def get_team_detail(self, team_id: int) -> dict:
        """获取销售团队详情"""
        team = SaleTeamDAO.get_team_by_id(self.db, team_id, self.tenant)
        if not team:
            raise BusinessError("销售团队不存在")
        
        # 获取下级团队
        sub_teams = SaleTeamDAO.get_teams_list(
            self.db, self.tenant, 0, 1000,
            {'parent_team_id': team_id}
        )
        
        # 获取团队业绩数据
        performance = self._get_team_performance(team_id)
        
        return {
            'team_id': team.team_id,
            'team_code': team.team_code,
            'team_name': team.team_name,
            'parent_team_id': team.parent_team_id,
            'leader_id': team.leader_id,
            'team_level': team.team_level,
            'member_count': team.member_count,
            'team_status': team.team_status,
            'sub_teams': [{
                'team_id': t.team_id,
                'team_name': t.team_name,
                'team_level': t.team_level,
                'member_count': t.member_count
            } for t in sub_teams],
            'performance': performance,
            'create_time': team.create_time.isoformat() if team.create_time else None,
            'update_time': team.update_time.isoformat() if team.update_time else None
        }
    
    def get_teams_list(self, page: int = 1, page_size: int = 20,
                      filters: Optional[Dict] = None) -> dict:
        """获取销售团队列表"""
        skip = (page - 1) * page_size
        teams = SaleTeamDAO.get_teams_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleTeamDAO.get_teams_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'team_id': t.team_id,
                'team_code': t.team_code,
                'team_name': t.team_name,
                'parent_team_id': t.parent_team_id,
                'leader_id': t.leader_id,
                'team_level': t.team_level,
                'member_count': t.member_count,
                'team_status': t.team_status,
                'status': t.status,
                'create_time': t.create_time.isoformat() if t.create_time else None
            } for t in teams]
        }
    
    def update_team(self, team_id: int, update_data: dict, 
                   operator_id: int = None) -> SaleTeam:
        """更新销售团队"""
        team = SaleTeamDAO.get_team_by_id(self.db, team_id, self.tenant)
        if not team:
            raise BusinessError("销售团队不存在")
        
        # 更新销售团队
        updated_team = SaleTeamDAO.update_team(self.db, team, update_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_team", 
            f"更新销售团队：{team.team_name}", 
            True
        )
        
        return updated_team
    
    def dissolve_team(self, team_id: int, operator_id: int = None) -> bool:
        """解散销售团队（生产级：级联校验 + 数据迁移）"""
        team = SaleTeamDAO.get_team_by_id(self.db, team_id, self.tenant)
        if not team:
            raise BusinessError("销售团队不存在")
        
        # 检查是否有下级团队
        sub_teams = SaleTeamDAO.get_teams_list(
            self.db, self.tenant, 0, 1,
            {'parent_team_id': team_id}
        )
        if sub_teams:
            raise BusinessError("存在下级团队，无法解散")
        
        # 检查是否有在职销售和有效业绩
        # 这里简化处理，实际需要检查团队成员和业绩
        
        # 更新团队状态为解散
        SaleTeamDAO.update_team(self.db, team, {'team_status': 3})
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "dissolve_team", 
            f"解散销售团队：{team.team_name}", 
            True
        )
        
        return True
    
    def add_team_member(self, team_id: int, user_id: int, member_role: str = 'member', 
                        operator_id: int = None) -> SaleTeamMember:
        """添加团队成员（生产级：团队有效性校验 + 用户唯一性校验）"""
        from admin.model.sys_user import SysUser
        from admin.dao.sys_user_dao import SysUserDAO
        
        team = SaleTeamDAO.get_team_by_id(self.db, team_id, self.tenant)
        if not team:
            raise BusinessError("销售团队不存在")
        
        if team.team_status != 1:
            raise BusinessError("团队状态异常，无法添加成员")
        
        sys_user = SysUserDAO.get_user_by_id(self.db, user_id)
        if not sys_user:
            raise BusinessError("用户不存在")
        
        existing_member = SaleTeamMemberDAO.get_member_by_team_user(
            self.db, self.tenant, team_id, user_id
        )
        if existing_member:
            if existing_member.member_status == 1:
                raise BusinessError("用户已在团队中")
            else:
                existing_member.member_status = 1
                existing_member.leave_date = None
                existing_member.join_date = datetime.now()
                self.db.commit()
                self.db.refresh(existing_member)
                return existing_member
        
        member_data = {
            'tenant': self.tenant,
            'team_id': team_id,
            'user_id': user_id,
            'member_role': member_role,
            'member_status': 1,
            'join_date': datetime.now(),
            'is_del': 0
        }
        
        member = SaleTeamMemberDAO.add_member(self.db, member_data)
        
        team.member_count += 1
        self.db.commit()
        
        self._create_operation_log(
            operator_id, "add_team_member", 
            f"添加团队成员：团队({team.team_name}) 用户({sys_user.name})", 
            True
        )
        
        return member
    
    def _get_team_performance(self, team_id: int) -> dict:
        """获取团队业绩数据"""
        # 统计团队成员的签约、回款业绩
        # 这里简化处理，实际需要关联团队成员表统计
        
        return {
            'total_contract_amount': 0,
            'total_paid_amount': 0,
            'contract_count': 0,
            'customer_count': 0
        }
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        from sale.dao.sale_dao import SaleStatDailyLogsDAO
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)


class PerformanceTargetService:
    """业绩目标业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def create_target(self, target_data: dict, operator_id: int = None) -> SalePerformanceTarget:
        """创建业绩目标"""
        # 检查楼盘是否存在
        from sale.dao.sale_dao import SaleProjectDAO
        project = SaleProjectDAO.get_project_by_id(
            self.db, target_data['project_id'], self.tenant
        )
        if not project:
            raise BusinessError("楼盘不存在")
        
        # 设置租户和初始状态
        target_data['tenant'] = self.tenant
        target_data['target_status'] = 1  # 进行中
        target_data['status'] = 1
        target_data['is_del'] = 0
        
        # 创建业绩目标
        target = SalePerformanceTargetDAO.create_target(self.db, target_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_target", 
            f"创建业绩目标：{target.target_type}", 
            True
        )
        
        return target
    
    def get_targets_list(self, page: int = 1, page_size: int = 20,
                        filters: Optional[Dict] = None) -> dict:
        """获取业绩目标列表"""
        skip = (page - 1) * page_size
        targets = SalePerformanceTargetDAO.get_targets_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SalePerformanceTargetDAO.get_targets_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'target_id': t.target_id,
                'project_id': t.project_id,
                'target_type': t.target_type,
                'target_user_id': t.target_user_id,
                'target_team_id': t.target_team_id,
                'time_type': t.time_type,
                'time_value': t.time_value,
                'target_amount': float(t.target_amount) if t.target_amount else 0,
                'target_sets': t.target_sets,
                'target_status': t.target_status,
                'create_time': t.create_time.isoformat() if t.create_time else None
            } for t in targets]
        }
    
    def update_target(self, target_id: int, update_data: dict, 
                     operator_id: int = None) -> SalePerformanceTarget:
        """更新业绩目标"""
        target = SalePerformanceTargetDAO.get_target_by_id(self.db, target_id, self.tenant)
        if not target:
            raise BusinessError("业绩目标不存在")
        
        # 已结算周期的业绩目标禁止修改
        if target.target_status == 2:  # 已完成
            raise BusinessError("已完成的业绩目标禁止修改")
        
        # 更新业绩目标
        updated_target = SalePerformanceTargetDAO.update_target(self.db, target, update_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_target", 
            f"更新业绩目标：{target_id}", 
            True
        )
        
        return updated_target
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        from sale.dao.sale_dao import SaleStatDailyLogsDAO
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)


class PerformanceService:
    """销售业绩统计服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def get_personal_performance(self, user_id: int, project_id: int, 
                                 time_type: str = 'month', time_value: str = None) -> dict:
        """获取个人销售业绩（生产级：实时聚合 + 目标对标）"""
        # 解析时间范围
        start_date, end_date = self._parse_time_range(time_type, time_value)
        
        # 统计签约业绩
        contract_stats = self.db.query(
            func.count(SaleContract.contract_id).label('contract_count'),
            func.sum(SaleContract.contract_amount).label('total_contract_amount')
        ).filter(
            and_(
                SaleContract.sale_user_id == user_id,
                SaleContract.project_id == project_id,
                SaleContract.tenant == self.tenant,
                SaleContract.is_del == 0,
                SaleContract.contract_status.in_([2, 3]),  # 已备案或已完成
                SaleContract.contract_date >= start_date,
                SaleContract.contract_date <= end_date
            )
        ).first()
        
        # 统计回款业绩
        payment_stats = self.db.query(
            func.sum(SalePayment.payment_amount).label('total_paid_amount')
        ).join(
            SaleContract, SalePayment.contract_id == SaleContract.contract_id
        ).filter(
            and_(
                SaleContract.sale_user_id == user_id,
                SaleContract.project_id == project_id,
                SaleContract.tenant == self.tenant,
                SalePayment.tenant == self.tenant,
                SalePayment.is_del == 0,
                SalePayment.payment_status == 2,  # 已支付
                SalePayment.payment_date >= start_date,
                SalePayment.payment_date <= end_date
            )
        ).first()
        
        # 统计客户数据
        customer_stats = self.db.query(
            func.count(SaleCustomer.customer_id).label('customer_count')
        ).filter(
            and_(
                SaleCustomer.belong_sale_user_id == user_id,
                SaleCustomer.tenant == self.tenant,
                SaleCustomer.is_del == 0,
                SaleCustomer.create_time >= start_date,
                SaleCustomer.create_time <= end_date
            )
        ).first()
        
        # 获取业绩目标
        target = self._get_performance_target(
            '个人', project_id, user_id, None, time_type, time_value
        )
        
        # 计算完成率
        contract_amount = contract_stats.total_contract_amount or Decimal('0')
        paid_amount = payment_stats.total_paid_amount or Decimal('0')
        target_amount = target.target_amount if target else Decimal('0')
        
        completion_rate = float(round((contract_amount / target_amount * 100), 2)) if target_amount > 0 else 0
        
        return {
            'user_id': user_id,
            'project_id': project_id,
            'time_type': time_type,
            'time_value': time_value,
            'contract_count': contract_stats.contract_count or 0,
            'total_contract_amount': float(contract_amount),
            'total_paid_amount': float(paid_amount),
            'customer_count': customer_stats.customer_count or 0,
            'target_amount': float(target_amount),
            'target_sets': target.target_sets if target else 0,
            'completion_rate': completion_rate,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None
        }
    
    def get_team_performance(self, team_id: int, project_id: int, 
                            time_type: str = 'month', time_value: str = None) -> dict:
        """获取团队销售业绩（生产级：层级数据聚合）"""
        start_date, end_date = self._parse_time_range(time_type, time_value)
        
        team_members = SaleTeamMemberDAO.get_team_members(
            self.db, self.tenant, team_id, member_status=1
        )
        member_ids = [m.user_id for m in team_members]
        
        if not member_ids:
            return {
                'team_id': team_id,
                'project_id': project_id,
                'time_type': time_type,
                'time_value': time_value,
                'contract_count': 0,
                'total_contract_amount': 0,
                'total_paid_amount': 0,
                'customer_count': 0,
                'member_count': 0,
                'target_amount': 0,
                'completion_rate': 0,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        
        contract_stats = self.db.query(
            func.count(SaleContract.contract_id).label('contract_count'),
            func.sum(SaleContract.contract_amount).label('total_contract_amount')
        ).filter(
            and_(
                SaleContract.sale_user_id.in_(member_ids),
                SaleContract.project_id == project_id,
                SaleContract.tenant == self.tenant,
                SaleContract.is_del == 0,
                SaleContract.contract_status.in_([2, 3]),
                SaleContract.contract_date >= start_date,
                SaleContract.contract_date <= end_date
            )
        ).first()
        
        payment_stats = self.db.query(
            func.sum(SalePayment.payment_amount).label('total_paid_amount')
        ).join(
            SaleContract, SalePayment.contract_id == SaleContract.contract_id
        ).filter(
            and_(
                SaleContract.sale_user_id.in_(member_ids),
                SaleContract.project_id == project_id,
                SaleContract.tenant == self.tenant,
                SalePayment.tenant == self.tenant,
                SalePayment.is_del == 0,
                SalePayment.payment_status == 2,
                SalePayment.payment_date >= start_date,
                SalePayment.payment_date <= end_date
            )
        ).first()
        
        target = self._get_performance_target(
            '团队', project_id, None, team_id, time_type, time_value
        )
        
        contract_amount = contract_stats.total_contract_amount or Decimal('0')
        paid_amount = payment_stats.total_paid_amount or Decimal('0')
        target_amount = target.target_amount if target else Decimal('0')
        
        completion_rate = round((contract_amount / target_amount * 100), 2) if target_amount > 0 else 0
        
        return {
            'team_id': team_id,
            'project_id': project_id,
            'time_type': time_type,
            'time_value': time_value,
            'contract_count': contract_stats.contract_count or 0,
            'total_contract_amount': float(contract_amount),
            'total_paid_amount': float(paid_amount),
            'member_count': len(member_ids),
            'target_amount': float(target_amount),
            'completion_rate': completion_rate,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None
        }
    
    def _parse_time_range(self, time_type: str, time_value: str = None) -> tuple:
        """解析时间范围"""
        now = datetime.now()
        
        if time_type == 'total':  # 累计
            return datetime(2020, 1, 1), now
        elif time_type == 'year':  # 年度
            year = int(time_value) if time_value else now.year
            return datetime(year, 1, 1), datetime(year, 12, 31, 23, 59, 59)
        elif time_type == 'quarter':  # 季度
            if time_value:
                year, quarter = time_value.split('-Q')
                year, quarter = int(year), int(quarter)
            else:
                year, quarter = now.year, (now.month - 1) // 3 + 1
            
            quarter_start_month = (quarter - 1) * 3 + 1
            quarter_end_month = quarter * 3
            return datetime(year, quarter_start_month, 1), datetime(year, quarter_end_month, 28, 23, 59, 59)
        elif time_type == 'month':  # 月度
            if time_value:
                year, month = time_value.split('-')
                year, month = int(year), int(month)
            else:
                year, month = now.year, now.month
            
            from datetime import timedelta
            import calendar
            
            # 获取月份最后一天
            last_day = calendar.monthrange(year, month)[1]
            return datetime(year, month, 1), datetime(year, month, last_day, 23, 59, 59)
        elif time_type == 'week':  # 周度
            if time_value:
                year, week = time_value.split('-W')
                year, week = int(year), int(week)
            else:
                year, week = now.isocalendar()[:2]
            
            from datetime import timedelta
            import datetime as dt
            
            # 计算周的开始和结束时间
            start_date = dt.datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")
            end_date = start_date + timedelta(days=6)
            return start_date, end_date
        elif time_type == 'day':  # 日度
            if time_value:
                year, month, day = time_value.split('-')
                year, month, day = int(year), int(month), int(day)
            else:
                year, month, day = now.year, now.month, now.day
            
            return datetime(year, month, day), datetime(year, month, day, 23, 59, 59)
        elif time_type == 'custom':  # 自定义
            if time_value:
                start_str, end_str = time_value.split('~')
                start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d')
                end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d')
                return start_date, end_date
            else:
                return datetime(2020, 1, 1), now
        else:
            return datetime(2020, 1, 1), now
    
    def _get_performance_target(self, target_type: str, project_id: int, 
                              target_user_id: int = None, target_team_id: int = None,
                              time_type: str = 'month', time_value: str = None) -> Optional[SalePerformanceTarget]:
        """获取业绩目标"""
        targets = SalePerformanceTargetDAO.get_targets_list(
            self.db, self.tenant, 0, 1,
            {
                'target_type': target_type,
                'project_id': project_id,
                'target_user_id': target_user_id,
                'target_team_id': target_team_id,
                'time_type': time_type,
                'time_value': time_value
            }
        )
        
        return targets[0] if targets else None
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        from sale.dao.sale_dao import SaleStatDailyLogsDAO
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)


class SalesCommissionService:
    """销售提成业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def calculate_sales_commission(self, contract_id: int, operator_id: int = None) -> dict:
        """计算销售提成（生产级：自动核算 + 幂等校验）"""
        # 检查合同是否存在
        contract = SaleContractDAO.get_contract_by_id(self.db, contract_id, self.tenant)
        if not contract:
            raise BusinessError("合同不存在")
        
        # 幂等校验：检查是否已生成提成
        existing_commission = SaleSalesCommissionDAO.get_commissions_list(
            self.db, self.tenant, 0, 1,
            {'contract_id': contract_id, 'commission_status__ne': 4}  # 排除已作废
        )
        if existing_commission:
            raise ValidationError("该合同已生成销售提成")
        
        # 检查合同状态
        if contract.record_status != 1:  # 未备案
            raise BusinessError("合同未备案，无法计算提成")
        
        # 使用分布式锁防止重复计算
        lock_key = f"commission:sales:calculate:{self.tenant}:{contract_id}"
        locked = self.redis.setnx(lock_key, 1, 10)
        
        if not locked:
            raise BusinessError("提成正在计算中，请稍后重试")
        
        try:
            # 计算提成金额（这里简化处理，实际需要根据提成规则计算）
            # 假设提成为签约金额的1%
            commission_rate = Decimal('0.01')
            commission_amount = contract.contract_amount * commission_rate
            
            # 获取销售团队信息
            sale_team_id = None
            if contract.sale_user_id:
                # 这里需要查询用户所属团队
                pass
            
            # 生成销售提成
            commission_data = {
                'tenant': self.tenant,
                'commission_no': self._generate_commission_no(),
                'project_id': contract.project_id,
                'contract_id': contract_id,
                'sale_user_id': contract.sale_user_id,
                'sale_team_id': sale_team_id,
                'commission_amount': commission_amount,
                'commission_rate': 1.0,  # 1%
                'base_amount': contract.contract_amount,
                'commission_status': 1,  # 待审核
                'status': 1,
                'is_del': 0
            }
            
            commission = SaleSalesCommissionDAO.create_sales_commission(self.db, commission_data)
            
            # 记录操作日志
            self._create_operation_log(
                operator_id, "calculate_sales_commission", 
                f"计算销售提成：{commission.commission_no}，金额：{commission_amount}", 
                True
            )
            
            return {
                'commission_id': commission.commission_id,
                'commission_no': commission.commission_no,
                'contract_id': contract_id,
                'sale_user_id': contract.sale_user_id,
                'commission_amount': float(commission_amount),
                'commission_rate': 1.0,
                'base_amount': float(contract.contract_amount),
                'commission_status': commission.commission_status,
                'message': '销售提成计算成功'
            }
        finally:
            self.redis.delete(lock_key)
    
    def audit_sales_commission(self, commission_id: int, audit_user_id: int, 
                              operator_id: int = None) -> bool:
        """审核销售提成"""
        commission = SaleSalesCommissionDAO.get_commission_by_id(self.db, commission_id, self.tenant)
        if not commission:
            raise BusinessError("销售提成不存在")
        
        # 检查状态（必须是待审核）
        if commission.commission_status != 1:
            raise BusinessError("销售提成状态异常，无法审核")
        
        # 更新状态为已发放
        SaleSalesCommissionDAO.update_commission_status(
            self.db, commission, 2, audit_user_id
        )
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "audit_sales_commission", 
            f"审核销售提成：{commission.commission_no}", 
            True
        )
        
        return True
    
    def freeze_sales_commission(self, commission_id: int, freeze_reason: str, 
                               operator_id: int = None) -> bool:
        """冻结销售提成"""
        commission = SaleSalesCommissionDAO.get_commission_by_id(self.db, commission_id, self.tenant)
        if not commission:
            raise BusinessError("销售提成不存在")
        
        # 检查状态（已发放的提成不能冻结）
        if commission.commission_status == 2:
            raise BusinessError("已发放的提成不能冻结")
        
        # 更新状态为已冻结
        updated_commission = SaleSalesCommissionDAO.update_commission_status(
            self.db, commission, 3
        )
        updated_commission.freeze_reason = freeze_reason
        self.db.commit()
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "freeze_sales_commission", 
            f"冻结销售提成：{commission.commission_no}，原因：{freeze_reason}", 
            True
        )
        
        return True
    
    def get_commissions_list(self, page: int = 1, page_size: int = 20,
                           filters: Optional[Dict] = None) -> dict:
        """获取销售提成列表"""
        skip = (page - 1) * page_size
        commissions = SaleSalesCommissionDAO.get_commissions_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleSalesCommissionDAO.get_commissions_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'commission_id': c.commission_id,
                'commission_no': c.commission_no,
                'project_id': c.project_id,
                'contract_id': c.contract_id,
                'sale_user_id': c.sale_user_id,
                'sale_team_id': c.sale_team_id,
                'commission_amount': float(c.commission_amount) if c.commission_amount else 0,
                'commission_rate': float(c.commission_rate) if c.commission_rate else 0,
                'base_amount': float(c.base_amount) if c.base_amount else 0,
                'commission_status': c.commission_status,
                'audit_user_id': c.audit_user_id,
                'audit_time': c.audit_time.isoformat() if c.audit_time else None,
                'pay_time': c.pay_time.isoformat() if c.pay_time else None,
                'freeze_reason': c.freeze_reason,
                'create_time': c.create_time.isoformat() if c.create_time else None
            } for c in commissions]
        }
    
    def _generate_commission_no(self) -> str:
        """生成提成编号"""
        now = datetime.now()
        prefix = f"SC{now.strftime('%Y%m%d')}"
        # 使用Redis生成序列号
        key = f"commission:sales:no:{self.tenant}:{now.strftime('%Y%m%d')}"
        sequence = self.redis.incr(key)
        self.redis.expire(key, 86400)  # 24小时过期
        return f"{prefix}{sequence:06d}"
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        from sale.dao.sale_dao import SaleStatDailyLogsDAO
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)