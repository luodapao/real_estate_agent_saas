"""
SQLAlchemy全局数据库连接和会话管理
支持多数据库连接：admin、sale、finance
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config.settings import DB_CONFIG

# 构建主数据库连接URL（admin）
DATABASE_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset=utf8mb4"

# 创建主数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=50,
    pool_timeout=30,
    pool_recycle=1800
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类（admin）
Base = declarative_base()


# ========== Sale数据库连接 ==========
SALE_DB_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/sale?charset=utf8mb4"

sale_engine = create_engine(
    SALE_DB_URL,
    echo=False,
    pool_size=20,
    max_overflow=50,
    pool_timeout=30,
    pool_recycle=1800
)

SessionLocalSale = sessionmaker(autocommit=False, autoflush=False, bind=sale_engine)

# 创建基础模型类（sale）
SaleBase = declarative_base()


# ========== Finance数据库连接 ==========
FINANCE_DB_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/finance?charset=utf8mb4"

finance_engine = create_engine(
    FINANCE_DB_URL,
    echo=False,
    pool_size=20,
    max_overflow=50,
    pool_timeout=30,
    pool_recycle=1800
)

SessionLocalFinance = sessionmaker(autocommit=False, autoflush=False, bind=finance_engine)


def get_db():
    """获取admin数据库会话（FastAPI依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_sale_db():
    """获取sale数据库会话（FastAPI依赖注入）"""
    db = SessionLocalSale()
    try:
        yield db
    finally:
        db.close()


def get_finance_db():
    """获取finance数据库会话（FastAPI依赖注入）"""
    db = SessionLocalFinance()
    try:
        yield db
    finally:
        db.close()


class CRUDBase:
    """CRUD基础类"""
    
    def __init__(self, model):
        self.model = model
    
    def get(self, db: Session, id: int):
        """根据ID获取单条记录"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_by_field(self, db: Session, field: str, value):
        """根据指定字段获取单条记录"""
        return db.query(self.model).filter(getattr(self.model, field) == value).first()
    
    def list(self, db: Session, skip: int = 0, limit: int = 100):
        """获取记录列表"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in):
        """创建记录"""
        obj = self.model(**obj_in.dict())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    
    def update(self, db: Session, db_obj, obj_in):
        """更新记录"""
        obj_data = obj_in.dict(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int):
        """删除记录"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj