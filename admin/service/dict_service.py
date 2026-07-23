"""
数据字典业务服务层
"""
from sqlalchemy.orm import Session
from admin.model.sys_dict import SysDict
from admin.dao.dict_dao import DictDAO
from admin.schemas.dict_schemas import DictItemCreate, DictItemUpdate, DictItemResponse
from config.exception import BusinessException, ParamException


class DictService:
    """数据字典业务服务"""
    
    @staticmethod
    def get_dict(db: Session, dict_id: int) -> DictItemResponse:
        """查询字典详情"""
        dict_item = DictDAO.get(db, dict_id)
        if not dict_item:
            raise BusinessException("字典不存在")
        return DictItemResponse.from_orm(dict_item)
    
    @staticmethod
    def get_dict_by_type(db: Session, tenant_id: int, dict_type: str):
        """根据字典类型查询字典列表"""
        items = DictDAO.get_by_type(db, tenant_id, dict_type)
        return [DictItemResponse.from_orm(item).model_dump() for item in items]
    
    @staticmethod
    def get_dict_list(db: Session, tenant_id: int, dict_type: str = None, dict_label: str = None, 
                     status: int = None, page: int = 1, size: int = 10):
        """分页查询字典列表"""
        total, data = DictDAO.get_list(db, tenant_id, dict_type, dict_label, status, page, size)
        dict_list = [DictItemResponse.from_orm(item).model_dump() for item in data]
        return {
            'total': total,
            'page': page,
            'size': size,
            'data': dict_list
        }
    
    @staticmethod
    def create_dict(db: Session, tenant_id: int, data: DictItemCreate) -> DictItemResponse:
        """创建字典"""
        dict_item = SysDict(
            tenant_id=tenant_id,
            dict_type=data.dict_type,
            dict_label=data.dict_label,
            dict_value=data.dict_value,
            sort_order=data.sort_order,
            status=data.status,
            remark=data.remark
        )
        
        created_item = DictDAO.create(db, dict_item)
        return DictItemResponse.from_orm(created_item)
    
    @staticmethod
    def update_dict(db: Session, dict_id: int, data: DictItemUpdate) -> DictItemResponse:
        """更新字典"""
        dict_item = DictDAO.get(db, dict_id)
        if not dict_item:
            raise BusinessException("字典不存在")
        
        update_dict = data.model_dump(exclude_unset=True)
        updated_item = DictDAO.update(db, dict_id, update_dict)
        
        return DictItemResponse.from_orm(updated_item)
    
    @staticmethod
    def delete_dict(db: Session, dict_id: int) -> DictItemResponse:
        """删除字典"""
        dict_item = DictDAO.get(db, dict_id)
        if not dict_item:
            raise BusinessException("字典不存在")
        
        DictDAO.delete(db, dict_id)
        return DictItemResponse.from_orm(dict_item)