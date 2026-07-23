"""
数据字典数据访问层
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from admin.model.sys_dict import SysDict


class DictDAO:
    """数据字典数据访问对象"""
    
    @staticmethod
    def get(db: Session, dict_id: int):
        """根据ID查询字典"""
        return db.query(SysDict).filter(
            SysDict.dict_id == dict_id,
            SysDict.is_del == 0
        ).first()
    
    @staticmethod
    def get_by_type(db: Session, tenant_id: int, dict_type: str):
        """根据字典类型查询字典列表"""
        return db.query(SysDict).filter(
            SysDict.tenant_id == tenant_id,
            SysDict.dict_type == dict_type,
            SysDict.is_del == 0,
            SysDict.status == 1
        ).order_by(SysDict.sort_order).all()
    
    @staticmethod
    def get_list(db: Session, tenant_id: int, dict_type: str = None, dict_label: str = None, 
                status: int = None, page: int = 1, size: int = 10):
        """分页查询字典列表"""
        query = db.query(SysDict).filter(
            SysDict.tenant_id == tenant_id,
            SysDict.is_del == 0
        )
        
        if dict_type:
            query = query.filter(SysDict.dict_type.like(f"%{dict_type}%"))
        if dict_label:
            query = query.filter(SysDict.dict_label.like(f"%{dict_label}%"))
        if status is not None:
            query = query.filter(SysDict.status == status)
        
        total = query.count()
        
        data = query.order_by(SysDict.dict_type, SysDict.sort_order)\
            .offset((page - 1) * size)\
            .limit(size)\
            .all()
        
        return total, data
    
    @staticmethod
    def create(db: Session, dict_item: SysDict):
        """创建字典"""
        db.add(dict_item)
        db.commit()
        db.refresh(dict_item)
        return dict_item
    
    @staticmethod
    def update(db: Session, dict_id: int, update_data: dict):
        """更新字典"""
        db.query(SysDict).filter(SysDict.dict_id == dict_id)\
            .update(update_data)
        db.commit()
        return DictDAO.get(db, dict_id)
    
    @staticmethod
    def delete(db: Session, dict_id: int):
        """软删除字典"""
        return DictDAO.update(db, dict_id, {'is_del': 1})