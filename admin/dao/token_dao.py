"""
令牌数据访问层
"""
from sqlalchemy.orm import Session
from admin.model.sys_token import SysToken


class TokenDAO:
    """令牌数据访问对象"""
    
    @staticmethod
    def get(db: Session, token_id: int):
        """根据ID查询令牌"""
        return db.query(SysToken).filter(SysToken.token_id == token_id).first()
    
    @staticmethod
    def get_by_access_token(db: Session, access_token: str):
        """根据访问令牌查询"""
        return db.query(SysToken).filter(
            SysToken.access_token == access_token,
            SysToken.is_invalid == 0
        ).first()
    
    @staticmethod
    def get_by_refresh_token(db: Session, refresh_token: str):
        """根据刷新令牌查询"""
        return db.query(SysToken).filter(
            SysToken.refresh_token == refresh_token,
            SysToken.is_invalid == 0
        ).first()
    
    @staticmethod
    def get_by_user_id(db: Session, user_id: int):
        """根据用户ID查询令牌列表"""
        return db.query(SysToken).filter(
            SysToken.user_id == user_id,
            SysToken.is_invalid == 0
        ).all()
    
    @staticmethod
    def create(db: Session, token: SysToken):
        """创建令牌记录"""
        db.add(token)
        db.commit()
        db.refresh(token)
        return token
    
    @staticmethod
    def update(db: Session, token_id: int, update_data: dict):
        """更新令牌"""
        db.query(SysToken).filter(SysToken.token_id == token_id).update(update_data)
        db.commit()
        return TokenDAO.get(db, token_id)
    
    @staticmethod
    def invalidate(db: Session, token_id: int):
        """作废令牌"""
        return TokenDAO.update(db, token_id, {'is_invalid': 1})
    
    @staticmethod
    def invalidate_by_user(db: Session, user_id: int):
        """作废用户所有令牌"""
        db.query(SysToken).filter(
            SysToken.user_id == user_id,
            SysToken.is_invalid == 0
        ).update({'is_invalid': 1})
        db.commit()
    
    @staticmethod
    def delete_expired(db: Session):
        """删除过期令牌"""
        from datetime import datetime
        db.query(SysToken).filter(
            SysToken.expires_time < datetime.now()
        ).delete()
        db.commit()