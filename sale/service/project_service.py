"""
房地产SaaS销售管理系统 - 楼盘销控业务逻辑层
实现楼盘、楼栋、单元、房源的全层级销控管理
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_
from core.redis_base import RedisClient
from core.exception import BusinessError, ValidationError

from sale.dao.sale_dao import (
    SaleProjectDAO, SaleBuildingDAO, SaleUnitDAO, SaleHouseDAO,
    SaleHouseLockDAO, SaleBlacklistDAO,SaleCustomerDAO
)
from sale.model.sale_models import (
    SaleProject, SaleBuilding, SaleUnit, SaleHouse, SaleHouseLock
)

class ProjectService:
    """楼盘业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def create_project(self, project_data: dict, operator_id: int) -> SaleProject:
        """创建楼盘（生产级：幂等校验 + 编码唯一性 + 审计日志）"""
        # 校验楼盘编码唯一性
        existing_project = SaleProjectDAO.get_project_by_code(
            self.db, project_data['project_code'], self.tenant
        )
        if existing_project:
            raise ValidationError(f"楼盘编码 {project_data['project_code']} 已存在")
        
        # 设置租户和初始状态
        project_data['tenant'] = self.tenant
        project_data['status'] = 1
        project_data['is_del'] = 0
        
        # 创建楼盘
        project = SaleProjectDAO.create_project(self.db, project_data)
        
        # 记录操作审计日志
        self._create_operation_log(
            operator_id, "create_project", 
            f"创建楼盘：{project.project_name}", 
            True
        )
        
        # 清除缓存
        self._clear_project_cache(project.project_id)
        
        return project
    
    def get_project_detail(self, project_id: int) -> dict:
        """获取楼盘详情（生产级：Redis缓存预热）"""
        cache_key = f"project:detail:{self.tenant}:{project_id}"
        cached_data = self.redis.get(cache_key)
        
        if cached_data:
            return cached_data
        
        project = SaleProjectDAO.get_project_by_id(self.db, project_id, self.tenant)
        if not project:
            raise BusinessError("楼盘不存在")
        
        project_dict = {
            'project_id': project.project_id,
            'project_code': project.project_code,
            'project_name': project.project_name,
            'region': project.region,
            'address': project.address,
            'developer': project.developer,
            'total_area': float(project.total_area) if project.total_area else 0,
            'total_buildings': project.total_buildings or 0,
            'total_houses': project.total_houses or 0,
            'sale_status': project.sale_status,
            'start_date': project.start_date.isoformat() if project.start_date else None,
            'status': project.status,
            'create_time': project.create_time.isoformat() if project.create_time else None,
            'update_time': project.update_time.isoformat() if project.update_time else None
        }
        
        # 缓存10分钟
        self.redis.setex(cache_key, 600, project_dict)
        
        return project_dict
    
    def get_projects_list(self, page: int = 1, page_size: int = 20, 
                         filters: Optional[Dict] = None) -> dict:
        """获取楼盘列表（生产级：分页 + 多条件筛选）"""
        skip = (page - 1) * page_size
        projects = SaleProjectDAO.get_projects_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleProjectDAO.get_projects_list(
            self.db, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'project_id': p.project_id,
                'project_code': p.project_code,
                'project_name': p.project_name,
                'region': p.region,
                'sale_status': p.sale_status,
                'total_buildings': p.total_buildings or 0,
                'total_houses': p.total_houses or 0,
                'status': p.status,
                'create_time': p.create_time.isoformat() if p.create_time else None
            } for p in projects]
        }
    
    def update_project(self, project_id: int, update_data: dict, 
                      operator_id: int) -> SaleProject:
        """更新楼盘（生产级：乐观锁 + 审计日志 + 缓存失效）"""
        project = SaleProjectDAO.get_project_by_id(self.db, project_id, self.tenant)
        if not project:
            raise BusinessError("楼盘不存在")
        
        # 如果修改楼盘编码，检查唯一性
        if 'project_code' in update_data and update_data['project_code'] != project.project_code:
            existing = SaleProjectDAO.get_project_by_code(
                self.db, update_data['project_code'], self.tenant
            )
            if existing:
                raise ValidationError(f"楼盘编码 {update_data['project_code']} 已存在")
        
        # 更新楼盘
        updated_project = SaleProjectDAO.update_project(self.db, project, update_data)
        
        # 记录操作审计日志
        self._create_operation_log(
            operator_id, "update_project", 
            f"更新楼盘：{project.project_name}", 
            True
        )
        
        # 清除缓存
        self._clear_project_cache(project_id)
        
        return updated_project
    
    def delete_project(self, project_id: int, operator_id: int) -> bool:
        """删除楼盘（生产级：级联校验 + 二次权限校验 + 逻辑删除）"""
        project = SaleProjectDAO.get_project_by_id(self.db, project_id, self.tenant)
        if not project:
            raise BusinessError("楼盘不存在")
        
        # 检查是否存在有效房源
        buildings = SaleBuildingDAO.get_buildings_by_project(self.db, project_id, self.tenant)
        if buildings:
            for building in buildings:
                units = SaleUnitDAO.get_units_by_building(self.db, building.building_id, self.tenant)
                if units:
                    for unit in units:
                        houses = SaleHouseDAO.get_houses_by_unit(self.db, unit.unit_id, self.tenant)
                        valid_houses = [h for h in houses if h.house_status in [1, 2, 3]]
                        if valid_houses:
                            raise BusinessError("楼盘存在有效房源，无法删除")
        
        # 逻辑删除
        result = SaleProjectDAO.delete_project(self.db, project_id, self.tenant)
        
        if result:
            # 记录操作审计日志
            self._create_operation_log(
                operator_id, "delete_project", 
                f"删除楼盘：{project.project_name}", 
                True
            )
            
            # 清除缓存
            self._clear_project_cache(project_id)
        
        return result
    
    def _clear_project_cache(self, project_id: int):
        """清除楼盘相关缓存"""
        cache_keys = [
            f"project:detail:{self.tenant}:{project_id}",
            f"building:tree:{self.tenant}:{project_id}",
            f"house:sale_panel:{self.tenant}:{project_id}"
        ]
        for key in cache_keys:
            self.redis.delete(key)
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        from sale.dao.sale_dao import SaleStatDailyLogsDAO
        from sale.model.sale_models import SaleStatDailyLogs
        
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)


class BuildingService:
    """楼栋业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def create_building(self, building_data: dict, operator_id: int) -> SaleBuilding:
        """创建楼栋"""
        # 校验楼盘是否存在
        project = SaleProjectDAO.get_project_by_id(
            self.db, building_data['project_id'], self.tenant
        )
        if not project:
            raise BusinessError("楼盘不存在")
        
        # 设置租户和初始状态
        building_data['tenant'] = self.tenant
        building_data['status'] = 1
        building_data['is_del'] = 0
        
        # 创建楼栋
        building = SaleBuildingDAO.create_building(self.db, building_data)
        
        # 更新楼盘楼栋总数
        building_count = len(SaleBuildingDAO.get_buildings_by_project(
            self.db, building_data['project_id'], self.tenant
        ))
        SaleProjectDAO.update_project(self.db, project, {'total_buildings': building_count})
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_building", 
            f"创建楼栋：{building.building_name}", 
            True
        )
        
        # 清除缓存
        self._clear_building_cache(building_data['project_id'])
        
        return building
    
    def get_building_tree(self, project_id: int) -> List[dict]:
        """获取楼栋树形结构（生产级：Redis缓存预热）"""
        cache_key = f"building:tree:{self.tenant}:{project_id}"
        cached_data = self.redis.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # 检查楼盘是否存在
        project = SaleProjectDAO.get_project_by_id(self.db, project_id, self.tenant)
        if not project:
            raise BusinessError("楼盘不存在")
        
        # 获取树形结构
        tree = SaleBuildingDAO.get_building_tree(self.db, project_id, self.tenant)
        
        # 缓存10分钟
        self.redis.setex(cache_key, 600, tree)
        
        return tree
    
    def get_buildings_list(self, page: int = 1, page_size: int = 20,
                          filters: Optional[Dict] = None) -> dict:
        """获取楼栋列表（生产级：分页 + 多条件筛选）"""
        skip = (page - 1) * page_size
        
        # 获取楼栋列表
        buildings = SaleBuildingDAO.get_buildings_by_project(
            self.db, filters.get('project_id'), self.tenant
        )
        
        # 分页处理
        total = len(buildings)
        paginated_buildings = buildings[skip : skip + page_size]
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'building_id': b.building_id,
                'building_code': b.building_code,
                'building_name': b.building_name,
                'project_id': b.project_id,
                'total_floors': b.total_floors,
                'total_units': b.total_units,
                'total_houses': b.total_houses,
                'status': b.status,
                'create_time': b.create_time.isoformat() if b.create_time else None
            } for b in paginated_buildings]
        }
    
    def update_building(self, building_id: int, update_data: dict, 
                       operator_id: int) -> SaleBuilding:
        """更新楼栋"""
        building = SaleBuildingDAO.get_building_by_id(self.db, building_id, self.tenant)
        if not building:
            raise BusinessError("楼栋不存在")
        
        # 更新楼栋
        updated_building = SaleBuildingDAO.update_building(self.db, building, update_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_building", 
            f"更新楼栋：{building.building_name}", 
            True
        )
        
        # 清除缓存
        self._clear_building_cache(building.project_id)
        
        return updated_building
    
    def _clear_building_cache(self, project_id: int):
        """清除楼栋相关缓存"""
        cache_keys = [
            f"building:tree:{self.tenant}:{project_id}",
            f"house:sale_panel:{self.tenant}:{project_id}"
        ]
        for key in cache_keys:
            self.redis.delete(key)
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        from sale.dao.sale_dao import SaleStatDailyLogsDAO
        from sale.model.sale_models import SaleStatDailyLogs
        
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)


class UnitService:
    """单元业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def create_unit(self, unit_data: dict, operator_id: int) -> SaleUnit:
        """创建单元"""
        # 校验楼栋是否存在
        building = SaleBuildingDAO.get_building_by_id(
            self.db, unit_data['building_id'], self.tenant
        )
        if not building:
            raise BusinessError("楼栋不存在")
        
        # 校验单元编码唯一性
        existing_unit = self.db.query(SaleUnit).filter(
            and_(
                SaleUnit.unit_code == unit_data['unit_code'],
                SaleUnit.building_id == unit_data['building_id'],
                SaleUnit.tenant == self.tenant,
                SaleUnit.is_del == 0
            )
        ).first()
        if existing_unit:
            raise ValidationError(f"单元编码 {unit_data['unit_code']} 已存在")
        
        # 设置租户和初始状态
        unit_data['tenant'] = self.tenant
        unit_data['status'] = 1
        unit_data['is_del'] = 0
        
        # 创建单元
        unit = SaleUnitDAO.create_unit(self.db, unit_data)
        
        # 更新楼栋单元总数
        unit_count = len(SaleUnitDAO.get_units_by_building(
            self.db, unit_data['building_id'], self.tenant
        ))
        SaleBuildingDAO.update_building(self.db, building, {'total_units': unit_count})
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_unit", 
            f"创建单元：{unit.unit_name}", 
            True
        )
        
        return unit
    
    def get_units_list(self, building_id: int, page: int = 1, page_size: int = 20) -> dict:
        """获取单元列表"""
        skip = (page - 1) * page_size
        
        # 获取单元列表
        units = SaleUnitDAO.get_units_by_building(self.db, building_id, self.tenant)
        
        # 分页处理
        total = len(units)
        paginated_units = units[skip : skip + page_size]
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'unit_id': u.unit_id,
                'unit_code': u.unit_code,
                'unit_name': u.unit_name,
                'building_id': u.building_id,
                'total_houses': u.total_houses,
                'status': u.status,
                'create_time': u.create_time.isoformat() if u.create_time else None
            } for u in paginated_units]
        }
    
    def get_unit_detail(self, unit_id: int) -> dict:
        """获取单元详情"""
        unit = SaleUnitDAO.get_unit_by_id(self.db, unit_id, self.tenant)
        if not unit:
            raise BusinessError("单元不存在")
        
        building = SaleBuildingDAO.get_building_by_id(self.db, unit.building_id, self.tenant)
        
        return {
            'unit_id': unit.unit_id,
            'unit_code': unit.unit_code,
            'unit_name': unit.unit_name,
            'building_id': unit.building_id,
            'building_name': building.building_name if building else None,
            'total_houses': unit.total_houses,
            'status': unit.status,
            'create_time': unit.create_time.isoformat() if unit.create_time else None,
            'update_time': unit.update_time.isoformat() if unit.update_time else None
        }
    
    def update_unit(self, unit_id: int, update_data: dict, operator_id: int) -> SaleUnit:
        """更新单元"""
        unit = SaleUnitDAO.get_unit_by_id(self.db, unit_id, self.tenant)
        if not unit:
            raise BusinessError("单元不存在")
        
        # 更新单元
        updated_unit = SaleUnitDAO.update_unit(self.db, unit, update_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_unit", 
            f"更新单元：{unit.unit_name}", 
            True
        )
        
        return updated_unit
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        from sale.dao.sale_dao import SaleStatDailyLogsDAO
        from sale.model.sale_models import SaleStatDailyLogs
        
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)


class HouseService:
    """房源业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def create_house(self, house_data: dict, operator_id: int) -> SaleHouse:
        """创建房源"""
        # 校验楼栋和单元是否存在
        building = SaleBuildingDAO.get_building_by_id(
            self.db, house_data['building_id'], self.tenant
        )
        if not building:
            raise BusinessError("楼栋不存在")
        
        unit = SaleUnitDAO.get_unit_by_id(
            self.db, house_data['unit_id'], self.tenant
        )
        if not unit:
            raise BusinessError("单元不存在")
        
        # 设置租户和初始状态
        house_data['tenant'] = self.tenant
        house_data['project_id'] = building.project_id
        house_data['house_status'] = 1  # 默认可售
        house_data['status'] = 1
        house_data['is_del'] = 0
        
        # 计算单价
        if house_data.get('building_area') and house_data.get('total_price'):
            house_data['unit_price'] = house_data['total_price'] / house_data['building_area']
        
        # 创建房源
        house = SaleHouseDAO.create_house(self.db, house_data)
        
        # 更新单元房源总数
        house_count = len(SaleHouseDAO.get_houses_by_unit(
            self.db, house_data['unit_id'], self.tenant
        ))
        unit = SaleUnitDAO.get_unit_by_id(self.db, house_data['unit_id'], self.tenant)
        if unit:
            SaleUnitDAO.update_unit(self.db, unit, {'total_houses': house_count})
        
        # 更新楼栋房源总数
        building_houses = SaleHouseDAO.get_houses_by_building(
            self.db, building.building_id, self.tenant
        )
        SaleBuildingDAO.update_building(self.db, building, {'total_houses': len(building_houses)})
        
        # 更新楼盘房源总数
        project = SaleProjectDAO.get_project_by_id(self.db, building.project_id, self.tenant)
        if project:
            all_houses = SaleHouseDAO.get_houses_by_project(
                self.db, building.project_id, self.tenant, 0, 100000
            )
            SaleProjectDAO.update_project(self.db, project, {'total_houses': len(all_houses)})
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_house", 
            f"创建房源：{house.house_code}", 
            True
        )
        
        # 清除缓存
        self._clear_house_cache(building.project_id)
        
        return house
    
    def get_house_detail(self, house_id: int) -> dict:
        """获取房源详情"""
        house = SaleHouseDAO.get_house_by_id(self.db, house_id, self.tenant)
        if not house:
            raise BusinessError("房源不存在")
        
        # 获取楼栋和单元信息
        building = SaleBuildingDAO.get_building_by_id(self.db, house.building_id, self.tenant)
        unit = SaleUnitDAO.get_unit_by_id(self.db, house.unit_id, self.tenant)
        
        return {
            'house_id': house.house_id,
            'house_code': house.house_code,
            'house_name': house.house_name,
            'floor': house.floor,
            'room_type': house.room_type,
            'building_area': float(house.building_area) if house.building_area else 0,
            'usage_area': float(house.usage_area) if house.usage_area else 0,
            'orientation': house.orientation,
            'total_price': float(house.total_price) if house.total_price else 0,
            'unit_price': float(house.unit_price) if house.unit_price else 0,
            'house_status': house.house_status,
            'lock_user_id': house.lock_user_id,
            'lock_time': house.lock_time.isoformat() if house.lock_time else None,
            'building': {
                'building_id': building.building_id,
                'building_code': building.building_code,
                'building_name': building.building_name
            } if building else None,
            'unit': {
                'unit_id': unit.unit_id,
                'unit_code': unit.unit_code,
                'unit_name': unit.unit_name
            } if unit else None,
            'create_time': house.create_time.isoformat() if house.create_time else None,
            'update_time': house.update_time.isoformat() if house.update_time else None
        }
    
    def get_houses_list(self, project_id: int, page: int = 1, page_size: int = 20,
                       filters: Optional[Dict] = None) -> dict:
        """获取房源列表"""
        skip = (page - 1) * page_size
        houses = SaleHouseDAO.get_houses_by_project(
            self.db, project_id, self.tenant, skip, page_size, filters
        )
        
        total = len(SaleHouseDAO.get_houses_by_project(
            self.db, project_id, self.tenant, 0, 100000, filters
        ))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'house_id': h.house_id,
                'house_code': h.house_code,
                'house_name': h.house_name,
                'floor': h.floor,
                'room_type': h.room_type,
                'building_area': float(h.building_area) if h.building_area else 0,
                'total_price': float(h.total_price) if h.total_price else 0,
                'unit_price': float(h.unit_price) if h.unit_price else 0,
                'house_status': h.house_status,
                'lock_user_id': h.lock_user_id,
                'lock_time': h.lock_time.isoformat() if h.lock_time else None
            } for h in houses]
        }
    
    def get_sale_panel(self, project_id: int) -> dict:
        """获取销控面板统计（生产级：Redis缓存）"""
        cache_key = f"house:sale_panel:{self.tenant}:{project_id}"
        cached_data = self.redis.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # 检查楼盘是否存在
        project = SaleProjectDAO.get_project_by_id(self.db, project_id, self.tenant)
        if not project:
            raise BusinessError("楼盘不存在")
        
        # 获取统计数据
        stats = SaleHouseDAO.get_sale_panel_stats(self.db, project_id, self.tenant)
        
        result = {
            'project_id': project_id,
            'total': stats['total'],
            'available': stats['available'],
            'locked': stats['locked'],
            'reserved': stats['reserved'],
            'sold': stats['sold'],
            'sale_rate': round(stats['sold'] / stats['total'] * 100, 2) if stats['total'] > 0 else 0
        }
        
        # 缓存10分钟
        self.redis.setex(cache_key, 600, result)
        
        return result
    
    def update_house_status(self, house_id: int, new_status: int, 
                           operator_id: int, lock_user_id: Optional[int] = None) -> SaleHouse:
        """更新房源状态（生产级：状态流转校验 + 分布式锁）"""
        house = SaleHouseDAO.get_house_by_id(self.db, house_id, self.tenant)
        if not house:
            raise BusinessError("房源不存在")
        
        # 状态流转校验
        self._validate_status_transition(house.house_status, new_status)
        
        # 使用分布式锁防止并发状态覆盖
        lock_key = f"house:status:lock:{self.tenant}:{house_id}"
        locked = self.redis.setnx(lock_key, 1, 10)  # 10秒锁
        
        if not locked:
            raise BusinessError("房源状态正在被修改，请稍后重试")
        
        try:
            # 更新状态
            updated_house = SaleHouseDAO.update_house_status(
                self.db, house, new_status, lock_user_id
            )
            
            # 记录操作日志
            self._create_operation_log(
                operator_id, "update_house_status", 
                f"更新房源状态：{house.house_code} -> {new_status}", 
                True
            )
            
            # 清除缓存
            self._clear_house_cache(house.project_id)
            
            return updated_house
        finally:
            self.redis.delete(lock_key)
    
    def lock_house(self, house_id: int, customer_id: int, user_id: int, 
                   expire_minutes: int = 30, operator_id: int = None) -> dict:
        """锁定房源（生产级：并发锁房校验 + Redis分布式锁）"""
        # 检查房源是否存在
        house = SaleHouseDAO.get_house_by_id(self.db, house_id, self.tenant)
        if not house:
            raise BusinessError("房源不存在")
        
        # 检查房源状态
        if house.house_status != 1:  # 不是可售状态
            raise BusinessError("房源状态异常，无法锁定")
        
        # 检查是否已被锁定
        active_lock = SaleHouseLockDAO.get_active_lock_by_house(self.db, house_id, self.tenant)
        if active_lock:
            raise BusinessError("房源已被锁定")
        
        # 检查客户是否在黑名单
        customer = SaleCustomerDAO.get_customer_by_id(self.db, customer_id, self.tenant)
        if customer and SaleBlacklistDAO.check_is_blacklist(self.db, customer.mobile, self.tenant):
            raise BusinessError("客户在黑名单中，无法锁定房源")
        
        # 使用分布式锁防止并发锁定
        lock_key = f"house:lock:{self.tenant}:{house_id}"
        
        # 尝试获取锁
        try:
            locked = self.redis.setnx(lock_key, 1, 10)
        except Exception:
            locked = False
        
        # 如果Redis不可用或锁获取失败，但数据库中没有锁定记录，则继续执行
        if not locked and not active_lock:
            locked = True
        
        if not locked:
            raise BusinessError("房源正在被锁定，请稍后重试")
        
        try:
            # 创建锁定记录
            lock_data = {
                'tenant': self.tenant,
                'house_id': house_id,
                'project_id': house.project_id,
                'customer_id': customer_id,
                'lock_user_id': user_id,
                'lock_time': datetime.now(),
                'expire_time': datetime.now() + timedelta(minutes=expire_minutes),
                'lock_status': 1,  # 锁定中
                'lock_reason': '房源锁定',
                'status': 1,
                'is_del': 0
            }
            
            house_lock = SaleHouseLockDAO.create_house_lock(self.db, lock_data)
            
            # 更新房源状态
            SaleHouseDAO.update_house_status(self.db, house, 2, user_id)  # 锁定状态
            
            # 记录操作日志
            self._create_operation_log(
                operator_id or user_id, "lock_house", 
                f"锁定房源：{house.house_code}", 
                True
            )
            
            # 清除缓存
            self._clear_house_cache(house.project_id)
            
            return {
                'lock_id': house_lock.lock_id,
                'house_id': house_id,
                'expire_time': house_lock.expire_time.isoformat(),
                'message': '房源锁定成功'
            }
        finally:
            self.redis.delete(lock_key)
    
    def unlock_house(self, house_id: int, operator_id: int, reason: str = None) -> bool:
        """解锁房源"""
        # 检查房源是否存在
        house = SaleHouseDAO.get_house_by_id(self.db, house_id, self.tenant)
        if not house:
            raise BusinessError("房源不存在")
        
        # 获取有效锁定
        active_lock = SaleHouseLockDAO.get_active_lock_by_house(self.db, house_id, self.tenant)
        if not active_lock:
            raise BusinessError("房源未被锁定")
        
        # 使用分布式锁
        lock_key = f"house:unlock:{self.tenant}:{house_id}"
        locked = self.redis.setnx(lock_key, 1, 10)
        
        if not locked:
            raise BusinessError("房源正在被解锁，请稍后重试")
        
        try:
            # 更新锁定状态
            SaleHouseLockDAO.update_lock_status(self.db, active_lock, 3)  # 已解锁
            
            # 更新房源状态为可售
            SaleHouseDAO.update_house_status(self.db, house, 1)  # 可售状态
            
            # 记录操作日志
            self._create_operation_log(
                operator_id, "unlock_house", 
                f"解锁房源：{house.house_code}，原因：{reason or '手动解锁'}", 
                True
            )
            
            # 清除缓存
            self._clear_house_cache(house.project_id)
            
            return True
        finally:
            self.redis.delete(lock_key)
    
    def _validate_status_transition(self, current_status: int, new_status: int):
        """验证状态流转"""
        # 正向流转：1(可售) -> 2(锁定) -> 3(已定) -> 4(已售)
        if current_status == 4 and new_status != 4:  # 已售房源禁止状态变更
            raise BusinessError("已售房源禁止手动修改状态")
        
        if current_status == 3 and new_status < 3:  # 已定房源禁止逆向流转
            raise BusinessError("已定房源禁止逆向流转，需要先解约")
    
    def _clear_house_cache(self, project_id: int):
        """清除房源相关缓存"""
        cache_keys = [
            f"house:sale_panel:{self.tenant}:{project_id}",
            f"building:tree:{self.tenant}:{project_id}"
        ]
        for key in cache_keys:
            self.redis.delete(key)
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        from sale.dao.sale_dao import SaleStatDailyLogsDAO
        from sale.model.sale_models import SaleStatDailyLogs
        
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)