"""
房地产SaaS销售管理系统 - 数据访问层（DAO）
所有业务表的CRUD操作
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from sale.model.sale_models import (
    # 楼盘销控模块
    SaleProject, SaleBuilding, SaleUnit, SaleHouse,
    # 客户管理模块
    SaleCustomer, SaleCustomerTag, SaleCustomerDemand, SaleReport, SaleVisit, 
    SaleFollow, SaleFollowRemind, SaleBlacklist,
    # 认购签约交易模块
    SaleHouseLock, SaleSubscribe, SaleContract, SalePayment, SaleLoan, SaleReceipt,
    # 分销渠道与佣金模块
    SaleChannel, SaleBroker, SaleCommissionRule, SaleCommissionBill,
    # 项目规则模块
    SaleProjectRule,
    # 销售业绩与考核模块
    SaleTeam, SaleTeamMember, SalePerformanceTarget, SaleSalesCommission,
    # 统计报表模块
    SaleStatDailyLogs
)


class SaleProjectDAO:
    """楼盘表数据访问对象"""
    
    @staticmethod
    def create_project(db: Session, project_data: dict) -> SaleProject:
        """创建楼盘"""
        project = SaleProject(**project_data)
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def get_project_by_id(db: Session, project_id: int, tenant: str) -> Optional[SaleProject]:
        """根据ID获取楼盘"""
        return db.query(SaleProject).filter(
            and_(
                SaleProject.project_id == project_id,
                SaleProject.tenant == tenant,
                SaleProject.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_project_by_code(db: Session, project_code: str, tenant: str) -> Optional[SaleProject]:
        """根据编码获取楼盘"""
        return db.query(SaleProject).filter(
            and_(
                SaleProject.project_code == project_code,
                SaleProject.tenant == tenant,
                SaleProject.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_projects_list(db: Session, tenant: str, skip: int = 0, limit: int = 100, 
                          filters: Optional[Dict] = None) -> List[SaleProject]:
        """获取楼盘列表"""
        query = db.query(SaleProject).filter(
            and_(
                SaleProject.tenant == tenant,
                SaleProject.is_del == 0
            )
        )
        
        if filters:
            if filters.get('project_name'):
                query = query.filter(SaleProject.project_name.like(f"%{filters['project_name']}%"))
            if filters.get('region'):
                query = query.filter(SaleProject.region.like(f"%{filters['region']}%"))
            if filters.get('sale_status'):
                query = query.filter(SaleProject.sale_status == filters['sale_status'])
            if filters.get('status'):
                query = query.filter(SaleProject.status == filters['status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_project(db: Session, project: SaleProject, update_data: dict) -> SaleProject:
        """更新楼盘"""
        for key, value in update_data.items():
            setattr(project, key, value)
        project.version += 1
        db.commit()
        db.refresh(project)
        return project
    
    @staticmethod
    def delete_project(db: Session, project_id: int, tenant: str) -> bool:
        """删除楼盘（逻辑删除）"""
        project = SaleProjectDAO.get_project_by_id(db, project_id, tenant)
        if project:
            project.is_del = 1
            project.version += 1
            db.commit()
            return True
        return False


class SaleBuildingDAO:
    """楼栋表数据访问对象"""
    
    @staticmethod
    def create_building(db: Session, building_data: dict) -> SaleBuilding:
        """创建楼栋"""
        building = SaleBuilding(**building_data)
        db.add(building)
        db.commit()
        db.refresh(building)
        return building
    
    @staticmethod
    def get_building_by_id(db: Session, building_id: int, tenant: str) -> Optional[SaleBuilding]:
        """根据ID获取楼栋"""
        return db.query(SaleBuilding).filter(
            and_(
                SaleBuilding.building_id == building_id,
                SaleBuilding.tenant == tenant,
                SaleBuilding.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_buildings_by_project(db: Session, project_id: int, tenant: str) -> List[SaleBuilding]:
        """根据楼盘ID获取楼栋列表"""
        return db.query(SaleBuilding).filter(
            and_(
                SaleBuilding.project_id == project_id,
                SaleBuilding.tenant == tenant,
                SaleBuilding.is_del == 0
            )
        ).all()
    
    @staticmethod
    def get_building_tree(db: Session, project_id: int, tenant: str) -> List[dict]:
        """获取楼盘的楼栋树形结构"""
        buildings = SaleBuildingDAO.get_buildings_by_project(db, project_id, tenant)
        tree = []
        for building in buildings:
            units = SaleUnitDAO.get_units_by_building(db, building.building_id, tenant)
            building_dict = {
                'building_id': building.building_id,
                'building_code': building.building_code,
                'building_name': building.building_name,
                'total_floors': building.total_floors,
                'total_units': building.total_units,
                'units': []
            }
            for unit in units:
                houses = SaleHouseDAO.get_houses_by_unit(db, unit.unit_id, tenant)
                building_dict['units'].append({
                    'unit_id': unit.unit_id,
                    'unit_code': unit.unit_code,
                    'unit_name': unit.unit_name,
                    'houses': [{'house_id': h.house_id, 'house_code': h.house_code, 
                               'house_status': h.house_status} for h in houses]
                })
            tree.append(building_dict)
        return tree
    
    @staticmethod
    def update_building(db: Session, building: SaleBuilding, update_data: dict) -> SaleBuilding:
        """更新楼栋"""
        for key, value in update_data.items():
            setattr(building, key, value)
        building.version += 1
        db.commit()
        db.refresh(building)
        return building


class SaleUnitDAO:
    """单元表数据访问对象"""
    
    @staticmethod
    def create_unit(db: Session, unit_data: dict) -> SaleUnit:
        """创建单元"""
        unit = SaleUnit(**unit_data)
        db.add(unit)
        db.commit()
        db.refresh(unit)
        return unit
    
    @staticmethod
    def get_unit_by_id(db: Session, unit_id: int, tenant: str) -> Optional[SaleUnit]:
        """根据ID获取单元"""
        return db.query(SaleUnit).filter(
            and_(
                SaleUnit.unit_id == unit_id,
                SaleUnit.tenant == tenant,
                SaleUnit.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_units_by_building(db: Session, building_id: int, tenant: str) -> List[SaleUnit]:
        """根据楼栋ID获取单元列表"""
        return db.query(SaleUnit).filter(
            and_(
                SaleUnit.building_id == building_id,
                SaleUnit.tenant == tenant,
                SaleUnit.is_del == 0
            )
        ).all()
    
    @staticmethod
    def update_unit(db: Session, unit: SaleUnit, update_data: dict) -> SaleUnit:
        """更新单元"""
        for key, value in update_data.items():
            setattr(unit, key, value)
        unit.version += 1
        db.commit()
        db.refresh(unit)
        return unit


class SaleHouseDAO:
    """房源表数据访问对象"""
    
    @staticmethod
    def create_house(db: Session, house_data: dict) -> SaleHouse:
        """创建房源（单条）"""
        house = SaleHouse(**house_data)
        db.add(house)
        db.commit()
        db.refresh(house)
        return house
    
    @staticmethod
    def bulk_create_houses(db: Session, house_list: List[dict]) -> int:
        """批量创建房源（bulk_insert，一栋楼几千户快速落库）"""
        if not house_list:
            return 0
        # SQLAlchemy bulk_insert_mappings：不走ORM生命周期，性能高
        db.bulk_insert_mappings(SaleHouse, house_list)
        db.commit()
        return len(house_list)
    
    @staticmethod
    def exists_house_by_code(db: Session, tenant: str, project_id: int,
                             building_id: int, unit_id: int, house_code: str) -> bool:
        """校验某单元下是否已存在该房号（用于预览后确认前冲突检测）"""
        return db.query(SaleHouse).filter(
            and_(
                SaleHouse.tenant == tenant,
                SaleHouse.project_id == project_id,
                SaleHouse.building_id == building_id,
                SaleHouse.unit_id == unit_id,
                SaleHouse.house_code == house_code,
                SaleHouse.is_del == 0
            )
        ).first() is not None
    
    @staticmethod
    def get_house_by_id(db: Session, house_id: int, tenant: str) -> Optional[SaleHouse]:
        """根据ID获取房源"""
        return db.query(SaleHouse).filter(
            and_(
                SaleHouse.house_id == house_id,
                SaleHouse.tenant == tenant,
                SaleHouse.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_houses_by_unit(db: Session, unit_id: int, tenant: str) -> List[SaleHouse]:
        """根据单元ID获取房源列表"""
        return db.query(SaleHouse).filter(
            and_(
                SaleHouse.unit_id == unit_id,
                SaleHouse.tenant == tenant,
                SaleHouse.is_del == 0
            )
        ).all()
    
    @staticmethod
    def get_houses_by_building(db: Session, building_id: int, tenant: str) -> List[SaleHouse]:
        """根据楼栋ID获取房源列表"""
        return db.query(SaleHouse).filter(
            and_(
                SaleHouse.building_id == building_id,
                SaleHouse.tenant == tenant,
                SaleHouse.is_del == 0
            )
        ).all()
    
    @staticmethod
    def get_houses_by_project(db: Session, project_id: int, tenant: str, 
                              skip: int = 0, limit: int = 100, 
                              filters: Optional[Dict] = None) -> List[SaleHouse]:
        """根据楼盘ID获取房源列表"""
        query = db.query(SaleHouse).filter(
            and_(
                SaleHouse.project_id == project_id,
                SaleHouse.tenant == tenant,
                SaleHouse.is_del == 0
            )
        )
        
        if filters:
            if filters.get('house_status'):
                query = query.filter(SaleHouse.house_status == filters['house_status'])
            if filters.get('room_type'):
                query = query.filter(SaleHouse.room_type.like(f"%{filters['room_type']}%"))
            if filters.get('area_min'):
                query = query.filter(SaleHouse.building_area >= filters['area_min'])
            if filters.get('area_max'):
                query = query.filter(SaleHouse.building_area <= filters['area_max'])
            if filters.get('price_min'):
                query = query.filter(SaleHouse.total_price >= filters['price_min'])
            if filters.get('price_max'):
                query = query.filter(SaleHouse.total_price <= filters['price_max'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_sale_panel_stats(db: Session, project_id: int, tenant: str) -> dict:
        """获取销控面板统计"""
        stats = db.query(
            func.count(SaleHouse.house_id).label('total'),
            func.sum(case((SaleHouse.house_status == 1, 1), else_=0)).label('available'),
            func.sum(case((SaleHouse.house_status == 2, 1), else_=0)).label('locked'),
            func.sum(case((SaleHouse.house_status == 3, 1), else_=0)).label('reserved'),
            func.sum(case((SaleHouse.house_status == 4, 1), else_=0)).label('sold')
        ).filter(
            and_(
                SaleHouse.project_id == project_id,
                SaleHouse.tenant == tenant,
                SaleHouse.is_del == 0
            )
        ).first()
        
        return {
            'total': stats.total or 0,
            'available': stats.available or 0,
            'locked': stats.locked or 0,
            'reserved': stats.reserved or 0,
            'sold': stats.sold or 0
        }
    
    @staticmethod
    def update_house(db: Session, house: SaleHouse, update_data: dict) -> SaleHouse:
        """更新房源信息"""
        for key, value in update_data.items():
            if hasattr(house, key):
                setattr(house, key, value)
        house.version += 1
        house.update_time = datetime.now()
        db.commit()
        db.refresh(house)
        return house

    @staticmethod
    def update_house_status(db: Session, house: SaleHouse, new_status: int, 
                           lock_user_id: Optional[int] = None) -> SaleHouse:
        """更新房源状态"""
        house.house_status = new_status
        if lock_user_id:
            house.lock_user_id = lock_user_id
            house.lock_time = datetime.now()
        house.version += 1
        db.commit()
        db.refresh(house)
        return house
    
    @staticmethod
    def lock_house_optimistic(db: Session, house: SaleHouse, user_id: int, 
                             expire_minutes: int = 30) -> bool:
        """乐观锁方式锁定房源"""
        if house.house_status != 1:  # 不是可售状态
            return False
        
        expected_version = house.version
        house.house_status = 2  # 锁定状态
        house.lock_user_id = user_id
        house.lock_time = datetime.now()
        house.version += 1
        
        try:
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False


class SaleCustomerDAO:
    """客户档案数据访问对象"""
    
    @staticmethod
    def create_customer(db: Session, customer_data: dict) -> SaleCustomer:
        """创建客户"""
        customer = SaleCustomer(**customer_data)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    
    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int, tenant: str) -> Optional[SaleCustomer]:
        """根据ID获取客户"""
        return db.query(SaleCustomer).filter(
            and_(
                SaleCustomer.customer_id == customer_id,
                SaleCustomer.tenant == tenant,
                SaleCustomer.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_customer_by_mobile(db: Session, mobile: str, tenant: str) -> Optional[SaleCustomer]:
        """根据手机号获取客户"""
        return db.query(SaleCustomer).filter(
            and_(
                SaleCustomer.mobile == mobile,
                SaleCustomer.tenant == tenant,
                SaleCustomer.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_customers_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                          filters: Optional[Dict] = None) -> List[SaleCustomer]:
        """获取客户列表"""
        query = db.query(SaleCustomer).filter(
            and_(
                SaleCustomer.tenant == tenant,
                SaleCustomer.is_del == 0
            )
        )
        
        if filters:
            if filters.get('customer_name'):
                query = query.filter(SaleCustomer.customer_name.like(f"%{filters['customer_name']}%"))
            if filters.get('mobile'):
                query = query.filter(SaleCustomer.mobile.like(f"%{filters['mobile']}%"))
            if filters.get('customer_level'):
                query = query.filter(SaleCustomer.customer_level == filters['customer_level'])
            if filters.get('customer_status'):
                query = query.filter(SaleCustomer.customer_status == filters['customer_status'])
            if filters.get('belong_sale_user_id'):
                query = query.filter(SaleCustomer.belong_sale_user_id == filters['belong_sale_user_id'])
            if filters.get('belong_team_id'):
                query = query.filter(SaleCustomer.belong_team_id == filters['belong_team_id'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_customer(db: Session, customer: SaleCustomer, update_data: dict) -> SaleCustomer:
        """更新客户"""
        for key, value in update_data.items():
            setattr(customer, key, value)
        customer.version += 1
        db.commit()
        db.refresh(customer)
        return customer
    
    @staticmethod
    def delete_customer(db: Session, customer_id: int, tenant: str) -> bool:
        """删除客户（逻辑删除）"""
        customer = SaleCustomerDAO.get_customer_by_id(db, customer_id, tenant)
        if customer:
            customer.is_del = 1
            customer.is_blacklist = 1
            customer.version += 1
            db.commit()
            return True
        return False
    
    @staticmethod
    def release_to_sea(db: Session, customer_id: int, tenant: str) -> bool:
        """释放客户到公海"""
        customer = SaleCustomerDAO.get_customer_by_id(db, customer_id, tenant)
        if customer:
            customer.customer_status = 4  # 公海状态
            customer.belong_sale_user_id = None
            customer.belong_team_id = None
            customer.version += 1
            db.commit()
            return True
        return False


class SaleCustomerTagDAO:
    """客户标签数据访问对象"""
    
    @staticmethod
    def create_tag(db: Session, tag_data: dict) -> SaleCustomerTag:
        """创建客户标签"""
        tag = SaleCustomerTag(**tag_data)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag
    
    @staticmethod
    def get_tags_by_customer(db: Session, customer_id: int, tenant: str) -> List[SaleCustomerTag]:
        """根据客户ID获取标签列表"""
        return db.query(SaleCustomerTag).filter(
            and_(
                SaleCustomerTag.customer_id == customer_id,
                SaleCustomerTag.tenant == tenant,
                SaleCustomerTag.is_del == 0
            )
        ).all()
    
    @staticmethod
    def delete_tag(db: Session, tag_id: int, tenant: str) -> bool:
        """删除客户标签（逻辑删除）"""
        tag = db.query(SaleCustomerTag).filter(
            and_(
                SaleCustomerTag.tag_id == tag_id,
                SaleCustomerTag.tenant == tenant,
                SaleCustomerTag.is_del == 0
            )
        ).first()
        if tag:
            tag.is_del = 1
            db.commit()
            return True
        return False


class SaleCustomerDemandDAO:
    """客户需求数据访问对象"""
    
    @staticmethod
    def create_demand(db: Session, demand_data: dict) -> SaleCustomerDemand:
        """创建客户需求"""
        demand = SaleCustomerDemand(**demand_data)
        db.add(demand)
        db.commit()
        db.refresh(demand)
        return demand
    
    @staticmethod
    def get_demands_by_customer(db: Session, customer_id: int, tenant: str) -> List[SaleCustomerDemand]:
        """根据客户ID获取需求列表"""
        return db.query(SaleCustomerDemand).filter(
            and_(
                SaleCustomerDemand.customer_id == customer_id,
                SaleCustomerDemand.tenant == tenant,
                SaleCustomerDemand.is_del == 0
            )
        ).all()


class SaleReportDAO:
    """报备记录数据访问对象"""
    
    @staticmethod
    def create_report(db: Session, report_data: dict) -> SaleReport:
        """创建报备"""
        report = SaleReport(**report_data)
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
    
    @staticmethod
    def get_report_by_id(db: Session, report_id: int, tenant: str) -> Optional[SaleReport]:
        """根据ID获取报备"""
        return db.query(SaleReport).filter(
            and_(
                SaleReport.report_id == report_id,
                SaleReport.tenant == tenant,
                SaleReport.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_reports_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                        filters: Optional[Dict] = None) -> List[SaleReport]:
        """获取报备列表"""
        query = db.query(SaleReport).filter(
            and_(
                SaleReport.tenant == tenant,
                SaleReport.is_del == 0
            )
        )
        
        if filters:
            if filters.get('customer_id'):
                query = query.filter(SaleReport.customer_id == filters['customer_id'])
            if filters.get('project_id'):
                query = query.filter(SaleReport.project_id == filters['project_id'])
            if filters.get('channel_id'):
                query = query.filter(SaleReport.channel_id == filters['channel_id'])
            if filters.get('report_status'):
                query = query.filter(SaleReport.report_status == filters['report_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def check_duplicate_report(db: Session, mobile: str, project_id: int, 
                              tenant: str) -> bool:
        """检查是否重复报备（保护期内，按手机号查询）"""
        now = datetime.now()
        report = db.query(SaleReport).join(
            SaleCustomer, SaleReport.customer_id == SaleCustomer.customer_id
        ).filter(
            and_(
                SaleCustomer.mobile == mobile,
                SaleCustomer.tenant == tenant,
                SaleCustomer.is_del == 0,
                SaleReport.project_id == project_id,
                SaleReport.tenant == tenant,
                SaleReport.report_status == 1,  # 有效报备
                SaleReport.protect_expire_time > now
            )
        ).first()
        return report is not None
    
    @staticmethod
    def get_reports_by_mobile(db: Session, mobile: str, project_id: int, 
                             tenant: str) -> List[SaleReport]:
        """根据手机号和项目ID查询报备记录（用于多渠道报备场景）"""
        reports = db.query(SaleReport).filter(
            and_(
                SaleReport.mobile == mobile,
                SaleReport.project_id == project_id,
                SaleReport.tenant == tenant,
                SaleReport.is_del == 0
            )
        ).all()
        return reports
    
    @staticmethod
    def update_report(db: Session, report: SaleReport, update_data: dict) -> SaleReport:
        """更新报备"""
        for key, value in update_data.items():
            setattr(report, key, value)
        report.version += 1
        db.commit()
        db.refresh(report)
        return report
    
    @staticmethod
    def get_report_statistics(db: Session, project_id: int, tenant: str, 
                            start_date: datetime, end_date: datetime) -> dict:
        """获取报备统计数据"""
        stats = db.query(
            func.count(SaleReport.report_id).label('total'),
            func.sum(case((SaleReport.report_status == 0, 1), else_=0)).label('pending'),  # 待确客
            func.sum(case((SaleReport.report_status == 1, 1), else_=0)).label('valid'),    # 有效
            func.sum(case((SaleReport.report_status == 2, 1), else_=0)).label('invalid'),  # 失效
            func.sum(case((SaleReport.report_status == 3, 1), else_=0)).label('expired')  # 过期
        ).filter(
            and_(
                SaleReport.project_id == project_id,
                SaleReport.tenant == tenant,
                SaleReport.is_del == 0,
                SaleReport.create_time >= start_date,
                SaleReport.create_time <= end_date
            )
        ).first()
        
        return {
            'total': stats.total or 0,
            'pending': stats.pending or 0,
            'valid': stats.valid or 0,
            'invalid': stats.invalid or 0,
            'expired': stats.expired or 0
        }


class SaleVisitDAO:
    """到访记录数据访问对象"""
    
    @staticmethod
    def create_visit(db: Session, visit_data: dict) -> SaleVisit:
        """创建到访记录"""
        visit = SaleVisit(**visit_data)
        db.add(visit)
        db.commit()
        db.refresh(visit)
        return visit
    
    @staticmethod
    def get_visit_by_id(db: Session, visit_id: int, tenant: str) -> Optional[SaleVisit]:
        """根据ID获取到访记录"""
        return db.query(SaleVisit).filter(
            and_(
                SaleVisit.visit_id == visit_id,
                SaleVisit.tenant == tenant,
                SaleVisit.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_visits_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                       filters: Optional[Dict] = None, order_by: Optional[str] = None) -> List[SaleVisit]:
        """获取到访列表"""
        query = db.query(SaleVisit).filter(
            and_(
                SaleVisit.tenant == tenant,
                SaleVisit.is_del == 0
            )
        )
        
        if filters:
            if filters.get('customer_id'):
                query = query.filter(SaleVisit.customer_id == filters['customer_id'])
            if filters.get('project_id'):
                query = query.filter(SaleVisit.project_id == filters['project_id'])
            if filters.get('visit_status'):
                query = query.filter(SaleVisit.visit_status == filters['visit_status'])
            if filters.get('start_date'):
                query = query.filter(SaleVisit.visit_time >= filters['start_date'])
            if filters.get('end_date'):
                query = query.filter(SaleVisit.visit_time <= filters['end_date'])
        
        # 排序：支持 "字段 asc/desc"，默认按到访时间倒序
        column_name = 'visit_time'
        direction = 'desc'
        if order_by:
            parts = order_by.split()
            column_name = parts[0]
            if len(parts) > 1:
                direction = parts[1].lower()
        order_column = getattr(SaleVisit, column_name, SaleVisit.visit_time)
        query = query.order_by(order_column.asc() if direction == 'asc' else order_column.desc())
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_visit_statistics(db: Session, project_id: int, tenant: str, 
                           start_date: datetime, end_date: datetime) -> dict:
        """获取到访统计数据"""
        stats = db.query(
            func.count(SaleVisit.visit_id).label('total'),
            func.sum(case((SaleVisit.visit_status == 1, 1), else_=0)).label('valid'),
            func.sum(case((SaleVisit.visit_status == 2, 1), else_=0)).label('invalid'),
            func.sum(case((SaleVisit.visit_status == 3, 1), else_=0)).label('fake')
        ).filter(
            and_(
                SaleVisit.project_id == project_id,
                SaleVisit.tenant == tenant,
                SaleVisit.is_del == 0,
                SaleVisit.visit_time >= start_date,
                SaleVisit.visit_time <= end_date
            )
        ).first()
        
        return {
            'total': stats.total or 0,
            'valid': stats.valid or 0,
            'invalid': stats.invalid or 0,
            'fake': stats.fake or 0
        }


class SaleFollowDAO:
    """跟进记录数据访问对象"""
    
    @staticmethod
    def create_follow(db: Session, follow_data: dict) -> SaleFollow:
        """创建跟进记录"""
        follow = SaleFollow(**follow_data)
        db.add(follow)
        db.commit()
        db.refresh(follow)
        return follow
    
    @staticmethod
    def get_follow_by_id(db: Session, follow_id: int, tenant: str) -> Optional[SaleFollow]:
        """根据ID获取跟进记录"""
        return db.query(SaleFollow).filter(
            and_(
                SaleFollow.follow_id == follow_id,
                SaleFollow.tenant == tenant,
                SaleFollow.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_follows_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                        filters: Optional[Dict] = None) -> List[SaleFollow]:
        """获取跟进记录列表"""
        query = db.query(SaleFollow).filter(
            and_(
                SaleFollow.tenant == tenant,
                SaleFollow.is_del == 0
            )
        )
        
        if filters:
            if filters.get('customer_id'):
                query = query.filter(SaleFollow.customer_id == filters['customer_id'])
            if filters.get('follow_user_id'):
                query = query.filter(SaleFollow.follow_user_id == filters['follow_user_id'])
            if filters.get('start_date'):
                query = query.filter(SaleFollow.follow_time >= filters['start_date'])
            if filters.get('end_date'):
                query = query.filter(SaleFollow.follow_time <= filters['end_date'])
        
        return query.order_by(SaleFollow.follow_time.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_follow(db: Session, follow: SaleFollow, update_data: dict) -> SaleFollow:
        """更新跟进记录"""
        for key, value in update_data.items():
            setattr(follow, key, value)
        db.commit()
        db.refresh(follow)
        return follow


class SaleFollowRemindDAO:
    """跟进提醒数据访问对象"""
    
    @staticmethod
    def create_remind(db: Session, remind_data: dict) -> SaleFollowRemind:
        """创建跟进提醒"""
        remind = SaleFollowRemind(**remind_data)
        db.add(remind)
        db.commit()
        db.refresh(remind)
        return remind
    
    @staticmethod
    def get_remind_by_id(db: Session, remind_id: int, tenant: str) -> Optional[SaleFollowRemind]:
        """根据ID获取提醒"""
        return db.query(SaleFollowRemind).filter(
            and_(
                SaleFollowRemind.remind_id == remind_id,
                SaleFollowRemind.tenant == tenant,
                SaleFollowRemind.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_reminds_list(db: Session, tenant: str, user_id: int, 
                        skip: int = 0, limit: int = 100) -> List[SaleFollowRemind]:
        """获取用户的提醒列表"""
        return db.query(SaleFollowRemind).filter(
            and_(
                SaleFollowRemind.tenant == tenant,
                SaleFollowRemind.remind_user_id == user_id,
                SaleFollowRemind.is_del == 0,
                SaleFollowRemind.remind_status == 0  # 待跟进
            )
        ).order_by(SaleFollowRemind.remind_time.asc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def complete_remind(db: Session, remind_id: int, tenant: str) -> bool:
        """完成提醒"""
        remind = SaleFollowRemindDAO.get_remind_by_id(db, remind_id, tenant)
        if remind:
            remind.remind_status = 1  # 已完成
            remind.complete_time = datetime.now()
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_timeout_reminds(db: Session, tenant: str) -> List[SaleFollowRemind]:
        """获取超时未跟进的提醒"""
        now = datetime.now()
        return db.query(SaleFollowRemind).filter(
            and_(
                SaleFollowRemind.tenant == tenant,
                SaleFollowRemind.is_del == 0,
                SaleFollowRemind.remind_status == 0,
                SaleFollowRemind.remind_time < now
            )
        ).all()
    
    @staticmethod
    def get_reminds_by_customer(db: Session, customer_id: int, tenant: str) -> List[SaleFollowRemind]:
        """获取客户的所有跟进提醒"""
        return db.query(SaleFollowRemind).filter(
            and_(
                SaleFollowRemind.tenant == tenant,
                SaleFollowRemind.customer_id == customer_id,
                SaleFollowRemind.is_del == 0,
                SaleFollowRemind.remind_status == 0  # 待跟进
            )
        ).all()


class SaleBlacklistDAO:
    """黑名单数据访问对象"""
    
    @staticmethod
    def create_blacklist(db: Session, blacklist_data: dict) -> SaleBlacklist:
        """添加黑名单"""
        blacklist = SaleBlacklist(**blacklist_data)
        db.add(blacklist)
        db.commit()
        db.refresh(blacklist)
        return blacklist
    
    @staticmethod
    def get_blacklist_by_mobile(db: Session, mobile: str, tenant: str) -> Optional[SaleBlacklist]:
        """根据手机号获取黑名单"""
        return db.query(SaleBlacklist).filter(
            and_(
                SaleBlacklist.mobile == mobile,
                SaleBlacklist.tenant == tenant,
                SaleBlacklist.is_del == 0
            )
        ).first()
    
    @staticmethod
    def check_is_blacklist(db: Session, mobile: str, tenant: str) -> bool:
        """检查是否在黑名单中"""
        blacklist = SaleBlacklistDAO.get_blacklist_by_mobile(db, mobile, tenant)
        return blacklist is not None


class SaleHouseLockDAO:
    """房源锁定数据访问对象"""
    
    @staticmethod
    def create_house_lock(db: Session, lock_data: dict) -> SaleHouseLock:
        """创建房源锁定"""
        lock = SaleHouseLock(**lock_data)
        db.add(lock)
        db.commit()
        db.refresh(lock)
        return lock
    
    @staticmethod
    def get_lock_by_id(db: Session, lock_id: int, tenant: str) -> Optional[SaleHouseLock]:
        """根据ID获取锁定记录"""
        return db.query(SaleHouseLock).filter(
            and_(
                SaleHouseLock.lock_id == lock_id,
                SaleHouseLock.tenant == tenant,
                SaleHouseLock.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_active_lock_by_house(db: Session, house_id: int, tenant: str) -> Optional[SaleHouseLock]:
        """获取房源的有效锁定"""
        now = datetime.now()
        return db.query(SaleHouseLock).filter(
            and_(
                SaleHouseLock.house_id == house_id,
                SaleHouseLock.tenant == tenant,
                SaleHouseLock.is_del == 0,
                SaleHouseLock.lock_status == 1,  # 锁定中
                SaleHouseLock.expire_time > now
            )
        ).first()
    
    @staticmethod
    def get_locks_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                      filters: Optional[Dict] = None) -> List[SaleHouseLock]:
        """获取锁定记录列表"""
        query = db.query(SaleHouseLock).filter(
            and_(
                SaleHouseLock.tenant == tenant,
                SaleHouseLock.is_del == 0
            )
        )
        
        if filters:
            if filters.get('house_id'):
                query = query.filter(SaleHouseLock.house_id == filters['house_id'])
            if filters.get('customer_id'):
                query = query.filter(SaleHouseLock.customer_id == filters['customer_id'])
            if filters.get('lock_status'):
                query = query.filter(SaleHouseLock.lock_status == filters['lock_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_lock_status(db: Session, lock: SaleHouseLock, new_status: int) -> SaleHouseLock:
        """更新锁定状态"""
        lock.lock_status = new_status
        lock.version += 1
        db.commit()
        db.refresh(lock)
        return lock


class SaleSubscribeDAO:
    """认购单数据访问对象"""
    
    @staticmethod
    def create_subscribe(db: Session, subscribe_data: dict) -> SaleSubscribe:
        """创建认购单"""
        subscribe = SaleSubscribe(**subscribe_data)
        db.add(subscribe)
        db.commit()
        db.refresh(subscribe)
        return subscribe
    
    @staticmethod
    def get_subscribe_by_id(db: Session, subscribe_id: int, tenant: str) -> Optional[SaleSubscribe]:
        """根据ID获取认购单"""
        return db.query(SaleSubscribe).filter(
            and_(
                SaleSubscribe.subscribe_id == subscribe_id,
                SaleSubscribe.tenant == tenant,
                SaleSubscribe.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_subscribe_by_no(db: Session, subscribe_no: str, tenant: str) -> Optional[SaleSubscribe]:
        """根据认购编号获取认购单"""
        return db.query(SaleSubscribe).filter(
            and_(
                SaleSubscribe.subscribe_no == subscribe_no,
                SaleSubscribe.tenant == tenant,
                SaleSubscribe.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_subscribes_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                           filters: Optional[Dict] = None) -> List[SaleSubscribe]:
        """获取认购单列表"""
        query = db.query(SaleSubscribe).filter(
            and_(
                SaleSubscribe.tenant == tenant,
                SaleSubscribe.is_del == 0
            )
        )
        
        if filters:
            if filters.get('project_id'):
                query = query.filter(SaleSubscribe.project_id == filters['project_id'])
            if filters.get('house_id'):
                query = query.filter(SaleSubscribe.house_id == filters['house_id'])
            if filters.get('customer_id'):
                query = query.filter(SaleSubscribe.customer_id == filters['customer_id'])
            if filters.get('subscribe_status'):
                query = query.filter(SaleSubscribe.subscribe_status == filters['subscribe_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_subscribes_count(db: Session, tenant: str, filters: Optional[Dict] = None) -> int:
        """获取认购单数量"""
        query = db.query(SaleSubscribe).filter(
            and_(
                SaleSubscribe.tenant == tenant,
                SaleSubscribe.is_del == 0
            )
        )
        
        if filters:
            if filters.get('project_id'):
                query = query.filter(SaleSubscribe.project_id == filters['project_id'])
            if filters.get('house_id'):
                query = query.filter(SaleSubscribe.house_id == filters['house_id'])
            if filters.get('customer_id'):
                query = query.filter(SaleSubscribe.customer_id == filters['customer_id'])
            if filters.get('subscribe_status'):
                query = query.filter(SaleSubscribe.subscribe_status == filters['subscribe_status'])
        
        return query.count()
    
    @staticmethod
    def update_subscribe(db: Session, subscribe: SaleSubscribe, update_data: dict) -> SaleSubscribe:
        """更新认购单"""
        for key, value in update_data.items():
            setattr(subscribe, key, value)
        subscribe.version += 1
        db.commit()
        db.refresh(subscribe)
        return subscribe


class SaleContractDAO:
    """签约合同数据访问对象"""
    
    @staticmethod
    def create_contract(db: Session, contract_data: dict) -> SaleContract:
        """创建合同"""
        contract = SaleContract(**contract_data)
        db.add(contract)
        db.commit()
        db.refresh(contract)
        return contract
    
    @staticmethod
    def get_contract_by_id(db: Session, contract_id: int, tenant: str) -> Optional[SaleContract]:
        """根据ID获取合同"""
        return db.query(SaleContract).filter(
            and_(
                SaleContract.contract_id == contract_id,
                SaleContract.tenant == tenant,
                SaleContract.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_contract_by_no(db: Session, contract_no: str, tenant: str) -> Optional[SaleContract]:
        """根据合同编号获取合同"""
        return db.query(SaleContract).filter(
            and_(
                SaleContract.contract_no == contract_no,
                SaleContract.tenant == tenant,
                SaleContract.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_contracts_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                          filters: Optional[Dict] = None) -> List[SaleContract]:
        """获取合同列表"""
        query = db.query(SaleContract).filter(
            and_(
                SaleContract.tenant == tenant,
                SaleContract.is_del == 0
            )
        )
        
        if filters:
            if filters.get('project_id'):
                query = query.filter(SaleContract.project_id == filters['project_id'])
            if filters.get('customer_id'):
                query = query.filter(SaleContract.customer_id == filters['customer_id'])
            if filters.get('contract_status'):
                query = query.filter(SaleContract.contract_status == filters['contract_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_contracts_count(db: Session, tenant: str, filters: Optional[Dict] = None) -> int:
        """获取合同数量"""
        query = db.query(SaleContract).filter(
            and_(
                SaleContract.tenant == tenant,
                SaleContract.is_del == 0
            )
        )
        
        if filters:
            if filters.get('project_id'):
                query = query.filter(SaleContract.project_id == filters['project_id'])
            if filters.get('customer_id'):
                query = query.filter(SaleContract.customer_id == filters['customer_id'])
            if filters.get('contract_status'):
                query = query.filter(SaleContract.contract_status == filters['contract_status'])
        
        return query.count()
    
    @staticmethod
    def update_contract(db: Session, contract: SaleContract, update_data: dict) -> SaleContract:
        """更新合同"""
        for key, value in update_data.items():
            setattr(contract, key, value)
        contract.version += 1
        db.commit()
        db.refresh(contract)
        return contract


class SalePaymentDAO:
    """回款记录数据访问对象"""
    
    @staticmethod
    def create_payment(db: Session, payment_data: dict) -> SalePayment:
        """创建回款记录"""
        payment = SalePayment(**payment_data)
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def get_payment_by_id(db: Session, payment_id: int, tenant: str) -> Optional[SalePayment]:
        """根据ID获取回款记录"""
        return db.query(SalePayment).filter(
            and_(
                SalePayment.payment_id == payment_id,
                SalePayment.tenant == tenant,
                SalePayment.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_payments_by_contract(db: Session, contract_id: int, tenant: str) -> List[SalePayment]:
        """根据合同ID获取回款记录"""
        return db.query(SalePayment).filter(
            and_(
                SalePayment.contract_id == contract_id,
                SalePayment.tenant == tenant,
                SalePayment.is_del == 0
            )
        ).all()
    
    @staticmethod
    def get_payments_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                         filters: Optional[Dict] = None) -> List[SalePayment]:
        """获取回款记录列表"""
        query = db.query(SalePayment).filter(
            and_(
                SalePayment.tenant == tenant,
                SalePayment.is_del == 0
            )
        )
        
        if filters:
            if filters.get('project_id'):
                query = query.filter(SalePayment.project_id == filters['project_id'])
            if filters.get('customer_id'):
                query = query.filter(SalePayment.customer_id == filters['customer_id'])
            if filters.get('payment_status'):
                query = query.filter(SalePayment.payment_status == filters['payment_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_contract_paid_amount(db: Session, contract_id: int, tenant: str) -> Decimal:
        """获取合同已支付金额"""
        result = db.query(
            func.sum(SalePayment.payment_amount)
        ).filter(
            and_(
                SalePayment.contract_id == contract_id,
                SalePayment.tenant == tenant,
                SalePayment.is_del == 0,
                SalePayment.payment_status == 2  # 已支付
            )
        ).first()
        
        return result[0] or Decimal('0.00')
    
    @staticmethod
    def get_subscribe_paid_amount(db: Session, subscribe_id: int, tenant: str) -> Decimal:
        """获取认购单已支付金额"""
        result = db.query(
            func.sum(SalePayment.payment_amount)
        ).filter(
            and_(
                SalePayment.subscribe_id == subscribe_id,
                SalePayment.tenant == tenant,
                SalePayment.is_del == 0,
                SalePayment.payment_status == 2  # 已支付
            )
        ).first()
        
        return result[0] or Decimal('0.00')
    
    @staticmethod
    def update_payment(db: Session, payment: SalePayment, update_data: dict) -> SalePayment:
        """更新回款记录"""
        for key, value in update_data.items():
            setattr(payment, key, value)
        payment.version += 1
        db.commit()
        db.refresh(payment)
        return payment


class SaleChannelDAO:
    """渠道公司数据访问对象"""
    
    @staticmethod
    def create_channel(db: Session, channel_data: dict) -> SaleChannel:
        """创建渠道公司"""
        channel = SaleChannel(**channel_data)
        db.add(channel)
        db.commit()
        db.refresh(channel)
        return channel
    
    @staticmethod
    def get_channel_by_id(db: Session, channel_id: int, tenant: str) -> Optional[SaleChannel]:
        """根据ID获取渠道公司"""
        return db.query(SaleChannel).filter(
            and_(
                SaleChannel.channel_id == channel_id,
                SaleChannel.tenant == tenant,
                SaleChannel.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_channels_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                         filters: Optional[Dict] = None) -> List[SaleChannel]:
        """获取渠道公司列表"""
        query = db.query(SaleChannel).filter(
            and_(
                SaleChannel.tenant == tenant,
                SaleChannel.is_del == 0
            )
        )
        
        if filters:
            if filters.get('channel_name'):
                query = query.filter(SaleChannel.channel_name.like(f"%{filters['channel_name']}%"))
            if filters.get('cooperation_status'):
                query = query.filter(SaleChannel.cooperation_status == filters['cooperation_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_channel(db: Session, channel: SaleChannel, update_data: dict) -> SaleChannel:
        """更新渠道公司"""
        for key, value in update_data.items():
            setattr(channel, key, value)
        channel.version += 1
        db.commit()
        db.refresh(channel)
        return channel


class SaleBrokerDAO:
    """经纪人数据访问对象"""
    
    @staticmethod
    def create_broker(db: Session, broker_data: dict) -> SaleBroker:
        """创建经纪人"""
        broker = SaleBroker(**broker_data)
        db.add(broker)
        db.commit()
        db.refresh(broker)
        return broker
    
    @staticmethod
    def get_broker_by_id(db: Session, broker_id: int, tenant: str) -> Optional[SaleBroker]:
        """根据ID获取经纪人"""
        return db.query(SaleBroker).filter(
            and_(
                SaleBroker.broker_id == broker_id,
                SaleBroker.tenant == tenant,
                SaleBroker.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_brokers_by_channel(db: Session, channel_id: int, tenant: str) -> List[SaleBroker]:
        """根据渠道ID获取经纪人列表"""
        return db.query(SaleBroker).filter(
            and_(
                SaleBroker.channel_id == channel_id,
                SaleBroker.tenant == tenant,
                SaleBroker.is_del == 0
            )
        ).all()
    
    @staticmethod
    def get_brokers_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                        filters: Optional[Dict] = None) -> List[SaleBroker]:
        """获取经纪人列表"""
        query = db.query(SaleBroker).filter(
            and_(
                SaleBroker.tenant == tenant,
                SaleBroker.is_del == 0
            )
        )
        
        if filters:
            if filters.get('channel_id'):
                query = query.filter(SaleBroker.channel_id == filters['channel_id'])
            if filters.get('broker_name'):
                query = query.filter(SaleBroker.broker_name.like(f"%{filters['broker_name']}%"))
            if filters.get('work_status'):
                query = query.filter(SaleBroker.work_status == filters['work_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_broker(db: Session, broker: SaleBroker, update_data: dict) -> SaleBroker:
        """更新经纪人"""
        for key, value in update_data.items():
            setattr(broker, key, value)
        broker.version += 1
        db.commit()
        db.refresh(broker)
        return broker


class SaleCommissionRuleDAO:
    """佣金规则数据访问对象"""
    
    @staticmethod
    def create_commission_rule(db: Session, rule_data: dict) -> SaleCommissionRule:
        """创建佣金规则"""
        rule = SaleCommissionRule(**rule_data)
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule
    
    @staticmethod
    def get_rule_by_id(db: Session, rule_id: int, tenant: str) -> Optional[SaleCommissionRule]:
        """根据ID获取佣金规则"""
        return db.query(SaleCommissionRule).filter(
            and_(
                SaleCommissionRule.rule_id == rule_id,
                SaleCommissionRule.tenant == tenant,
                SaleCommissionRule.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_rules_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                      filters: Optional[Dict] = None) -> List[SaleCommissionRule]:
        """获取佣金规则列表"""
        query = db.query(SaleCommissionRule).filter(
            and_(
                SaleCommissionRule.tenant == tenant,
                SaleCommissionRule.is_del == 0
            )
        )
        
        if filters:
            if filters.get('project_id'):
                query = query.filter(SaleCommissionRule.project_id == filters['project_id'])
            if filters.get('rule_type'):
                query = query.filter(SaleCommissionRule.rule_type == filters['rule_type'])
            if filters.get('rule_status'):
                query = query.filter(SaleCommissionRule.rule_status == filters['rule_status'])
        
        return query.order_by(SaleCommissionRule.rule_level.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_applicable_rule(db: Session, project_id: int, room_type: str, tenant: str) -> Optional[SaleCommissionRule]:
        """获取适用的佣金规则"""
        return db.query(SaleCommissionRule).filter(
            and_(
                SaleCommissionRule.tenant == tenant,
                SaleCommissionRule.is_del == 0,
                SaleCommissionRule.rule_status == 1,
                or_(
                    and_(
                        SaleCommissionRule.project_id == project_id,
                        SaleCommissionRule.rule_type == '楼盘专属',
                        or_(
                            SaleCommissionRule.room_type.is_(None),
                            SaleCommissionRule.room_type == room_type
                        )
                    ),
                    and_(
                        SaleCommissionRule.project_id.is_(None),
                        SaleCommissionRule.rule_type == '全局'
                    )
                )
            )
        ).order_by(SaleCommissionRule.rule_level.desc()).first()


class SaleProjectRuleDAO:
    """项目规则数据访问对象"""
    
    @staticmethod
    def create_rule(db: Session, rule_data: dict) -> SaleProjectRule:
        """创建项目规则"""
        rule = SaleProjectRule(**rule_data)
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule
    
    @staticmethod
    def get_rule_by_id(db: Session, rule_id: int, tenant: str) -> Optional[SaleProjectRule]:
        """根据ID获取项目规则"""
        return db.query(SaleProjectRule).filter(
            and_(
                SaleProjectRule.rule_id == rule_id,
                SaleProjectRule.tenant == tenant,
                SaleProjectRule.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_rules_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                      filters: Optional[Dict] = None) -> List[SaleProjectRule]:
        """获取项目规则列表"""
        query = db.query(SaleProjectRule).filter(
            and_(
                SaleProjectRule.tenant == tenant,
                SaleProjectRule.is_del == 0
            )
        )
        
        if filters:
            if filters.get('project_id'):
                query = query.filter(SaleProjectRule.project_id == filters['project_id'])
            if filters.get('rule_key'):
                query = query.filter(SaleProjectRule.rule_key == filters['rule_key'])
            if filters.get('rule_status'):
                query = query.filter(SaleProjectRule.rule_status == filters['rule_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_rule_value(db: Session, project_id: int, rule_key: str, tenant: str,
                      default_value: int = 30) -> int:
        """获取规则值（优先项目规则，其次全局规则，最后返回默认值）"""
        rule = db.query(SaleProjectRule).filter(
            and_(
                SaleProjectRule.tenant == tenant,
                SaleProjectRule.is_del == 0,
                SaleProjectRule.rule_status == 1,
                SaleProjectRule.rule_key == rule_key,
                or_(
                    SaleProjectRule.project_id == project_id,
                    SaleProjectRule.project_id.is_(None)
                )
            )
        ).order_by(SaleProjectRule.project_id.is_(None)).first()
        
        return rule.rule_value if rule else default_value
    
    @staticmethod
    def update_rule(db: Session, rule: SaleProjectRule, update_data: dict) -> SaleProjectRule:
        """更新项目规则"""
        for key, value in update_data.items():
            setattr(rule, key, value)
        rule.version += 1
        db.commit()
        db.refresh(rule)
        return rule
    
    @staticmethod
    def delete_rule(db: Session, rule_id: int, tenant: str) -> bool:
        """删除项目规则（逻辑删除）"""
        rule = SaleProjectRuleDAO.get_rule_by_id(db, rule_id, tenant)
        if rule:
            rule.is_del = 1
            rule.version += 1
            db.commit()
            return True
        return False


class SaleCommissionBillDAO:
    """佣金结算单数据访问对象"""
    
    @staticmethod
    def create_commission_bill(db: Session, bill_data: dict) -> SaleCommissionBill:
        """创建佣金结算单"""
        bill = SaleCommissionBill(**bill_data)
        db.add(bill)
        db.commit()
        db.refresh(bill)
        return bill
    
    @staticmethod
    def get_bill_by_id(db: Session, bill_id: int, tenant: str) -> Optional[SaleCommissionBill]:
        """根据ID获取佣金结算单"""
        return db.query(SaleCommissionBill).filter(
            and_(
                SaleCommissionBill.bill_id == bill_id,
                SaleCommissionBill.tenant == tenant,
                SaleCommissionBill.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_bills_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                      filters: Optional[Dict] = None) -> List[SaleCommissionBill]:
        """获取佣金结算单列表"""
        query = db.query(SaleCommissionBill).filter(
            and_(
                SaleCommissionBill.tenant == tenant,
                SaleCommissionBill.is_del == 0
            )
        )
        
        if filters:
            if filters.get('project_id'):
                query = query.filter(SaleCommissionBill.project_id == filters['project_id'])
            if filters.get('channel_id'):
                query = query.filter(SaleCommissionBill.channel_id == filters['channel_id'])
            if filters.get('broker_id'):
                query = query.filter(SaleCommissionBill.broker_id == filters['broker_id'])
            if filters.get('bill_status'):
                query = query.filter(SaleCommissionBill.bill_status == filters['bill_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_bill_status(db: Session, bill: SaleCommissionBill, new_status: int, 
                          audit_user_id: Optional[int] = None) -> SaleCommissionBill:
        """更新结算单状态"""
        bill.bill_status = new_status
        if audit_user_id:
            bill.audit_user_id = audit_user_id
            bill.audit_time = datetime.now()
        if new_status == 2:  # 已结算
            bill.pay_time = datetime.now()
        bill.version += 1
        db.commit()
        db.refresh(bill)
        return bill


class SaleTeamDAO:
    """销售团队数据访问对象"""
    
    @staticmethod
    def create_team(db: Session, team_data: dict) -> SaleTeam:
        """创建销售团队"""
        team = SaleTeam(**team_data)
        db.add(team)
        db.commit()
        db.refresh(team)
        return team
    
    @staticmethod
    def get_team_by_id(db: Session, team_id: int, tenant: str) -> Optional[SaleTeam]:
        """根据ID获取销售团队"""
        return db.query(SaleTeam).filter(
            and_(
                SaleTeam.team_id == team_id,
                SaleTeam.tenant == tenant,
                SaleTeam.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_teams_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                      filters: Optional[Dict] = None) -> List[SaleTeam]:
        """获取销售团队列表"""
        query = db.query(SaleTeam).filter(
            and_(
                SaleTeam.tenant == tenant,
                SaleTeam.is_del == 0
            )
        )
        
        if filters:
            if filters.get('team_name'):
                query = query.filter(SaleTeam.team_name.like(f"%{filters['team_name']}%"))
            if filters.get('team_status'):
                query = query.filter(SaleTeam.team_status == filters['team_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_team(db: Session, team: SaleTeam, update_data: dict) -> SaleTeam:
        """更新销售团队"""
        for key, value in update_data.items():
            setattr(team, key, value)
        team.version += 1
        db.commit()
        db.refresh(team)
        return team


class SaleTeamMemberDAO:
    """销售团队成员数据访问对象"""
    
    @staticmethod
    def add_member(db: Session, member_data: dict) -> SaleTeamMember:
        """添加团队成员"""
        member = SaleTeamMember(**member_data)
        db.add(member)
        db.commit()
        db.refresh(member)
        return member
    
    @staticmethod
    def get_member_by_id(db: Session, member_id: int, tenant: str) -> Optional[SaleTeamMember]:
        """根据ID获取团队成员"""
        return db.query(SaleTeamMember).filter(
            and_(
                SaleTeamMember.member_id == member_id,
                SaleTeamMember.tenant == tenant,
                SaleTeamMember.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_team_members(db: Session, tenant: str, team_id: int, 
                        member_status: Optional[int] = None) -> List[SaleTeamMember]:
        """获取团队成员列表"""
        query = db.query(SaleTeamMember).filter(
            and_(
                SaleTeamMember.tenant == tenant,
                SaleTeamMember.team_id == team_id,
                SaleTeamMember.is_del == 0
            )
        )
        
        if member_status is not None:
            query = query.filter(SaleTeamMember.member_status == member_status)
        
        return query.all()
    
    @staticmethod
    def get_member_by_team_user(db: Session, tenant: str, team_id: int, user_id: int) -> Optional[SaleTeamMember]:
        """根据团队ID和用户ID获取成员"""
        return db.query(SaleTeamMember).filter(
            and_(
                SaleTeamMember.tenant == tenant,
                SaleTeamMember.team_id == team_id,
                SaleTeamMember.user_id == user_id,
                SaleTeamMember.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_user_teams(db: Session, tenant: str, user_id: int, 
                      member_status: Optional[int] = None) -> List[SaleTeamMember]:
        """获取用户所属团队列表"""
        query = db.query(SaleTeamMember).filter(
            and_(
                SaleTeamMember.tenant == tenant,
                SaleTeamMember.user_id == user_id,
                SaleTeamMember.is_del == 0
            )
        )
        
        if member_status is not None:
            query = query.filter(SaleTeamMember.member_status == member_status)
        
        return query.all()
    
    @staticmethod
    def update_member(db: Session, member: SaleTeamMember, update_data: dict) -> SaleTeamMember:
        """更新团队成员"""
        for key, value in update_data.items():
            setattr(member, key, value)
        member.version += 1
        db.commit()
        db.refresh(member)
        return member
    
    @staticmethod
    def remove_member(db: Session, member: SaleTeamMember) -> bool:
        """移除团队成员（逻辑删除）"""
        member.is_del = 1
        db.commit()
        return True


class SalePerformanceTargetDAO:
    """业绩目标数据访问对象"""
    
    @staticmethod
    def create_target(db: Session, target_data: dict) -> SalePerformanceTarget:
        """创建业绩目标"""
        target = SalePerformanceTarget(**target_data)
        db.add(target)
        db.commit()
        db.refresh(target)
        return target
    
    @staticmethod
    def get_target_by_id(db: Session, target_id: int, tenant: str) -> Optional[SalePerformanceTarget]:
        """根据ID获取业绩目标"""
        return db.query(SalePerformanceTarget).filter(
            and_(
                SalePerformanceTarget.target_id == target_id,
                SalePerformanceTarget.tenant == tenant,
                SalePerformanceTarget.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_targets_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                        filters: Optional[Dict] = None) -> List[SalePerformanceTarget]:
        """获取业绩目标列表"""
        query = db.query(SalePerformanceTarget).filter(
            and_(
                SalePerformanceTarget.tenant == tenant,
                SalePerformanceTarget.is_del == 0
            )
        )
        
        if filters:
            if filters.get('project_id'):
                query = query.filter(SalePerformanceTarget.project_id == filters['project_id'])
            if filters.get('target_type'):
                query = query.filter(SalePerformanceTarget.target_type == filters['target_type'])
            if filters.get('target_user_id'):
                query = query.filter(SalePerformanceTarget.target_user_id == filters['target_user_id'])
            if filters.get('target_team_id'):
                query = query.filter(SalePerformanceTarget.target_team_id == filters['target_team_id'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_target(db: Session, target: SalePerformanceTarget, update_data: dict) -> SalePerformanceTarget:
        """更新业绩目标"""
        for key, value in update_data.items():
            setattr(target, key, value)
        if hasattr(target, 'version') and target.version is not None:
            target.version += 1
        db.commit()
        db.refresh(target)
        return target


class SaleSalesCommissionDAO:
    """销售提成数据访问对象"""
    
    @staticmethod
    def create_sales_commission(db: Session, commission_data: dict) -> SaleSalesCommission:
        """创建销售提成"""
        commission = SaleSalesCommission(**commission_data)
        db.add(commission)
        db.commit()
        db.refresh(commission)
        return commission
    
    @staticmethod
    def get_commission_by_id(db: Session, commission_id: int, tenant: str) -> Optional[SaleSalesCommission]:
        """根据ID获取销售提成"""
        return db.query(SaleSalesCommission).filter(
            and_(
                SaleSalesCommission.commission_id == commission_id,
                SaleSalesCommission.tenant == tenant,
                SaleSalesCommission.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_commissions_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                            filters: Optional[Dict] = None) -> List[SaleSalesCommission]:
        """获取销售提成列表"""
        query = db.query(SaleSalesCommission).filter(
            and_(
                SaleSalesCommission.tenant == tenant,
                SaleSalesCommission.is_del == 0
            )
        )
        
        if filters:
            if filters.get('project_id'):
                query = query.filter(SaleSalesCommission.project_id == filters['project_id'])
            if filters.get('sale_user_id'):
                query = query.filter(SaleSalesCommission.sale_user_id == filters['sale_user_id'])
            if filters.get('commission_status'):
                query = query.filter(SaleSalesCommission.commission_status == filters['commission_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_commission_status(db: Session, commission: SaleSalesCommission, new_status: int,
                                 audit_user_id: Optional[int] = None) -> SaleSalesCommission:
        """更新提成状态"""
        commission.commission_status = new_status
        if audit_user_id:
            commission.audit_user_id = audit_user_id
            commission.audit_time = datetime.now()
        if new_status == 2:  # 已发放
            commission.pay_time = datetime.now()
        commission.version += 1
        db.commit()
        db.refresh(commission)
        return commission


class SaleLoanDAO:
    """贷款信息数据访问对象"""
    
    @staticmethod
    def create_loan(db: Session, loan_data: dict) -> SaleLoan:
        """创建贷款信息"""
        loan = SaleLoan(**loan_data)
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan
    
    @staticmethod
    def get_loan_by_id(db: Session, loan_id: int, tenant: str) -> Optional[SaleLoan]:
        """根据ID获取贷款信息"""
        return db.query(SaleLoan).filter(
            and_(
                SaleLoan.loan_id == loan_id,
                SaleLoan.tenant == tenant,
                SaleLoan.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_loans_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                       filters: Optional[Dict] = None) -> List[SaleLoan]:
        """获取贷款列表"""
        query = db.query(SaleLoan).filter(
            and_(
                SaleLoan.tenant == tenant,
                SaleLoan.is_del == 0
            )
        )
        
        if filters:
            if filters.get('contract_id'):
                query = query.filter(SaleLoan.contract_id == filters['contract_id'])
            if filters.get('loan_status'):
                query = query.filter(SaleLoan.loan_status == filters['loan_status'])
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_loan(db: Session, loan: SaleLoan, update_data: dict) -> SaleLoan:
        """更新贷款信息"""
        for key, value in update_data.items():
            setattr(loan, key, value)
        # SaleLoan 表无乐观锁 version 字段，防御性判断避免 AttributeError
        if hasattr(loan, 'version') and loan.version is not None:
            loan.version += 1
        db.commit()
        db.refresh(loan)
        return loan


class SaleReceiptDAO:
    """发票票据数据访问对象"""
    
    @staticmethod
    def create_receipt(db: Session, receipt_data: dict) -> SaleReceipt:
        """创建发票票据"""
        receipt = SaleReceipt(**receipt_data)
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        return receipt
    
    @staticmethod
    def get_receipt_by_id(db: Session, receipt_id: int, tenant: str) -> Optional[SaleReceipt]:
        """根据ID获取发票"""
        return db.query(SaleReceipt).filter(
            and_(
                SaleReceipt.receipt_id == receipt_id,
                SaleReceipt.tenant == tenant,
                SaleReceipt.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_receipts_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                         filters: Optional[Dict] = None) -> List[SaleReceipt]:
        """获取发票列表"""
        query = db.query(SaleReceipt).filter(
            and_(
                SaleReceipt.tenant == tenant,
                SaleReceipt.is_del == 0
            )
        )
        
        if filters:
            if filters.get('contract_id'):
                query = query.filter(SaleReceipt.contract_id == filters['contract_id'])
            if filters.get('receipt_status'):
                query = query.filter(SaleReceipt.receipt_status == filters['receipt_status'])
        
        return query.order_by(SaleReceipt.create_time.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_receipt(db: Session, receipt: SaleReceipt, update_data: dict) -> SaleReceipt:
        """更新发票信息"""
        for key, value in update_data.items():
            setattr(receipt, key, value)
        if hasattr(receipt, 'version') and receipt.version is not None:
            receipt.version += 1
        db.commit()
        db.refresh(receipt)
        return receipt


class SaleStatDailyLogsDAO:
    """系统操作日志数据访问对象"""
    
    @staticmethod
    def create_log(db: Session, log_data: dict) -> SaleStatDailyLogs:
        """创建操作日志"""
        log = SaleStatDailyLogs(**log_data)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_logs_list(db: Session, tenant: str, skip: int = 0, limit: int = 100,
                     filters: Optional[Dict] = None) -> List[SaleStatDailyLogs]:
        """获取操作日志列表"""
        query = db.query(SaleStatDailyLogs).filter(
            and_(
                SaleStatDailyLogs.tenant == tenant
            )
        )
        
        if filters:
            if filters.get('user_id'):
                query = query.filter(SaleStatDailyLogs.user_id == filters['user_id'])
            if filters.get('operation_type'):
                query = query.filter(SaleStatDailyLogs.operation_type.like(f"%{filters['operation_type']}%"))
            if filters.get('start_date'):
                query = query.filter(SaleStatDailyLogs.create_time >= filters['start_date'])
            if filters.get('end_date'):
                query = query.filter(SaleStatDailyLogs.create_time <= filters['end_date'])
        
        return query.order_by(SaleStatDailyLogs.create_time.desc()).offset(skip).limit(limit).all()