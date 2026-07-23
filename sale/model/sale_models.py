"""
房地产SaaS销售管理系统 - 数据库模型层
楼盘销控、客户管理、交易流程、分销佣金、业绩统计相关表
"""

from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Numeric, Text, ForeignKey, Index, SmallInteger
Decimal = Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db_base import Base


# ========== 1. 楼盘销控模块 ==========

class SaleProject(Base):
    """楼盘表"""
    __tablename__ = 'sale_project'
    
    project_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='楼盘ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    project_code = Column(String(50), nullable=False, comment='楼盘编码')
    project_name = Column(String(100), nullable=False, comment='楼盘名称')
    region = Column(String(100), comment='区域位置')
    address = Column(String(255), comment='详细地址')
    developer = Column(String(100), comment='开发商名称')
    total_area = Column(Decimal(10, 2), comment='总占地面积（㎡）')
    total_buildings = Column(Integer, default=0, comment='总楼栋数')
    total_houses = Column(Integer, default=0, comment='总房源数')
    sale_status = Column(SmallInteger, default=1, comment='销售状态：1-在售 2-停售 3-售罄 4-未开盘')
    start_date = Column(DateTime, comment='开盘时间')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    # 关联关系
    buildings = relationship("SaleBuilding", back_populates="project")
    
    __table_args__ = (
        Index('idx_tenant_code', 'tenant', 'project_code'),
        Index('idx_tenant_status', 'tenant', 'status'),
        {'comment': '楼盘表'}
    )


class SaleBuilding(Base):
    """楼栋表"""
    __tablename__ = 'sale_building'
    
    building_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='楼栋ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), nullable=False, comment='楼盘ID')
    building_code = Column(String(50), nullable=False, comment='楼栋编号')
    building_name = Column(String(100), comment='楼栋名称')
    total_floors = Column(Integer, comment='总层数')
    total_units = Column(Integer, default=0, comment='总单元数')
    total_houses = Column(Integer, default=0, comment='总房源数')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    # 关联关系
    project = relationship("SaleProject", back_populates="buildings")
    units = relationship("SaleUnit", back_populates="building")
    
    __table_args__ = (
        Index('idx_tenant_project', 'tenant', 'project_id'),
        Index('idx_tenant_code', 'tenant', 'building_code'),
        {'comment': '楼栋表'}
    )


class SaleUnit(Base):
    """单元表"""
    __tablename__ = 'sale_unit'
    
    unit_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='单元ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    building_id = Column(BigInteger, ForeignKey('sale_building.building_id'), nullable=False, comment='楼栋ID')
    unit_code = Column(String(50), nullable=False, comment='单元编号')
    unit_name = Column(String(100), comment='单元名称')
    total_houses = Column(Integer, default=0, comment='总房源数')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    # 关联关系
    building = relationship("SaleBuilding", back_populates="units")
    houses = relationship("SaleHouse", back_populates="unit")
    
    __table_args__ = (
        Index('idx_tenant_building', 'tenant', 'building_id'),
        Index('idx_tenant_code', 'tenant', 'unit_code'),
        {'comment': '单元表'}
    )


class SaleHouse(Base):
    """房源表"""
    __tablename__ = 'sale_house'
    
    house_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='房源ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), nullable=False, comment='楼盘ID')
    building_id = Column(BigInteger, ForeignKey('sale_building.building_id'), nullable=False, comment='楼栋ID')
    unit_id = Column(BigInteger, ForeignKey('sale_unit.unit_id'), nullable=False, comment='单元ID')
    house_code = Column(String(50), nullable=False, comment='房源编号')
    house_name = Column(String(100), comment='房源名称')
    floor = Column(Integer, comment='所在楼层')
    room_type = Column(String(50), comment='户型（如：3室2厅1卫）')
    building_area = Column(Decimal(10, 2), comment='建筑面积（㎡）')
    usage_area = Column(Decimal(10, 2), comment='套内面积（㎡）')
    orientation = Column(String(20), comment='朝向')
    total_price = Column(Decimal(12, 2), comment='总价（元）')
    unit_price = Column(Decimal(8, 2), comment='单价（元/㎡）')
    house_status = Column(SmallInteger, default=1, comment='房源状态：1-可售 2-锁定 3-已定 4-已售 5-已预订')
    lock_user_id = Column(BigInteger, comment='锁定人ID')
    lock_time = Column(DateTime, comment='锁定时间')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    # 关联关系
    unit = relationship("SaleUnit", back_populates="houses")
    
    __table_args__ = (
        Index('idx_tenant_project', 'tenant', 'project_id'),
        Index('idx_tenant_building', 'tenant', 'building_id'),
        Index('idx_tenant_unit', 'tenant', 'unit_id'),
        Index('idx_tenant_status', 'tenant', 'house_status'),
        Index('idx_tenant_code', 'tenant', 'house_code'),
        {'comment': '房源表'}
    )


# ========== 2. 客户管理模块 ==========

class SaleCustomer(Base):
    """客户档案表"""
    __tablename__ = 'sale_customer'
    
    customer_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='客户ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    report_id = Column(BigInteger, ForeignKey('sale_report.report_id'), comment='报备ID（关联报备记录）')
    customer_name = Column(String(50), nullable=False, comment='客户姓名')
    mobile = Column(String(11), nullable=False, comment='手机号')
    id_card = Column(String(18), comment='身份证号')
    gender = Column(SmallInteger, comment='性别：1-男 2-女')
    age = Column(Integer, comment='年龄')
    customer_level = Column(String(20), default='C', comment='客户等级：A-高意向 B-中意向 C-低意向')
    customer_source = Column(String(50), comment='客户来源')
    belong_user_id = Column(BigInteger, comment='归属销售ID')
    belong_team_id = Column(BigInteger, comment='归属团队ID')
    first_visit_time = Column(DateTime, comment='首次到访时间')
    last_visit_time = Column(DateTime, comment='最后到访时间')
    last_follow_time = Column(DateTime, comment='最后跟进时间')
    customer_status = Column(SmallInteger, default=1, comment='客户状态：1-跟进中 2-已成交 3-已流失 4-公海')
    is_blacklist = Column(SmallInteger, default=0, comment='是否黑名单：0-否 1-是')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    # 关联关系
    tags = relationship("SaleCustomerTag", back_populates="customer")
    demands = relationship("SaleCustomerDemand", back_populates="customer")
    
    __table_args__ = (
        Index('idx_tenant_mobile', 'tenant', 'mobile'),
        Index('idx_tenant_belong_user', 'tenant', 'belong_user_id'),
        Index('idx_tenant_status', 'tenant', 'customer_status'),
        Index('idx_report_id', 'report_id'),
        {'comment': '客户档案表'}
    )


class SaleCustomerTag(Base):
    """客户标签表"""
    __tablename__ = 'sale_customer_tag'
    
    tag_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='标签ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    customer_id = Column(BigInteger, ForeignKey('sale_customer.customer_id'), nullable=False, comment='客户ID')
    tag_name = Column(String(50), nullable=False, comment='标签名称')
    tag_type = Column(String(20), comment='标签类型：自定义/系统')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关联关系
    customer = relationship("SaleCustomer", back_populates="tags")
    
    __table_args__ = (
        Index('idx_tenant_customer', 'tenant', 'customer_id'),
        {'comment': '客户标签表'}
    )


class SaleCustomerDemand(Base):
    """购房需求表"""
    __tablename__ = 'sale_customer_demand'
    
    demand_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='需求ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    customer_id = Column(BigInteger, ForeignKey('sale_customer.customer_id'), nullable=False, comment='客户ID')
    intent_project = Column(String(100), comment='意向楼盘')
    intent_room_type = Column(String(50), comment='意向户型')
    intent_area_min = Column(Decimal(10, 2), comment='意向面积最小值（㎡）')
    intent_area_max = Column(Decimal(10, 2), comment='意向面积最大值（㎡）')
    budget_min = Column(Decimal(12, 2), comment='预算最小值（元）')
    budget_max = Column(Decimal(12, 2), comment='预算最大值（元）')
    purchase_purpose = Column(String(50), comment='购房目的：自住/投资/改善')
    remark = Column(Text, comment='备注信息')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关联关系
    customer = relationship("SaleCustomer", back_populates="demands")
    
    __table_args__ = (
        Index('idx_tenant_customer', 'tenant', 'customer_id'),
        {'comment': '购房需求表'}
    )


class SaleReport(Base):
    """报备记录表"""
    __tablename__ = 'sale_report'
    
    report_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='报备ID')
    report_no = Column(String(50), nullable=False, comment='报备编号')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    customer_id = Column(BigInteger, ForeignKey('sale_customer.customer_id'), nullable=True, comment='客户ID（确客后关联）')
    customer_name = Column(String(50), nullable=False, comment='客户姓名（报备时录入）')
    mobile = Column(String(11), nullable=False, comment='手机号（报备时录入）')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), nullable=False, comment='楼盘ID')
    report_user_id = Column(BigInteger, comment='报备人ID')
    channel_id = Column(BigInteger, comment='渠道ID')
    broker_id = Column(BigInteger, comment='经纪人ID')
    qrcode_url = Column(String(255), comment='二维码URL')
    report_time = Column(DateTime, server_default=func.now(), comment='报备时间')
    protect_expire_time = Column(DateTime, comment='保护期过期时间')
    visit_status = Column(SmallInteger, default=0, comment='到访状态：0-未到访 1-已到访 2-已失效')
    visit_time = Column(DateTime, comment='实际到访时间')
    report_status = Column(SmallInteger, default=1, comment='报备状态：1-有效 2-失效')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    # 关联关系
    
    __table_args__ = (
        Index('idx_tenant_customer', 'tenant', 'customer_id'),
        Index('idx_tenant_project', 'tenant', 'project_id'),
        Index('idx_tenant_status', 'tenant', 'report_status'),
        Index('idx_tenant_mobile', 'tenant', 'mobile'),
        {'comment': '报备记录表'}
    )


class SaleVisit(Base):
    """到访记录表"""
    __tablename__ = 'sale_visit'
    
    visit_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='到访ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    customer_id = Column(BigInteger, ForeignKey('sale_customer.customer_id'), nullable=False, comment='客户ID')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), nullable=False, comment='楼盘ID')
    report_id = Column(BigInteger, ForeignKey('sale_report.report_id'), comment='关联报备ID')
    receive_user_id = Column(BigInteger, comment='接待销售ID')
    visit_time = Column(DateTime, server_default=func.now(), comment='到访时间')
    visit_type = Column(String(20), comment='到访类型：首次到访/多次到访')
    reception_score = Column(Decimal(3, 1), comment='接待评分')
    protect_expire_time = Column(DateTime, comment='保护期过期时间（到访时可重新计算）')
    visit_status = Column(SmallInteger, default=1, comment='到访状态：1-有效 2-无效 3-虚假')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_customer', 'tenant', 'customer_id'),
        Index('idx_tenant_project', 'tenant', 'project_id'),
        Index('idx_tenant_time', 'tenant', 'visit_time'),
        {'comment': '到访记录表'}
    )


class SaleFollow(Base):
    """跟进记录表"""
    __tablename__ = 'sale_follow'
    
    follow_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='跟进ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    customer_id = Column(BigInteger, ForeignKey('sale_customer.customer_id'), nullable=False, comment='客户ID')
    follow_user_id = Column(BigInteger, comment='跟进人ID')
    follow_time = Column(DateTime, server_default=func.now(), comment='跟进时间')
    follow_method = Column(String(20), comment='跟进方式：电话/微信/面谈/短信')
    follow_content = Column(Text, comment='跟进内容')
    customer_intention = Column(String(20), comment='客户意向度')
    next_follow_time = Column(DateTime, comment='下次跟进时间')
    follow_status = Column(SmallInteger, default=1, comment='跟进状态：1-正常 2-已完成')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        Index('idx_tenant_customer', 'tenant', 'customer_id'),
        Index('idx_tenant_user', 'tenant', 'follow_user_id'),
        Index('idx_tenant_time', 'tenant', 'follow_time'),
        {'comment': '跟进记录表'}
    )


class SaleFollowRemind(Base):
    """跟进提醒表"""
    __tablename__ = 'sale_follow_remind'
    
    remind_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='提醒ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    customer_id = Column(BigInteger, ForeignKey('sale_customer.customer_id'), nullable=False, comment='客户ID')
    follow_id = Column(BigInteger, ForeignKey('sale_follow.follow_id'), comment='关联跟进ID')
    remind_user_id = Column(BigInteger, comment='提醒人ID')
    remind_time = Column(DateTime, comment='提醒时间')
    remind_content = Column(String(255), comment='提醒内容')
    remind_status = Column(SmallInteger, default=0, comment='提醒状态：0-待跟进 1-已完成 2-已过期')
    complete_time = Column(DateTime, comment='完成时间')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        Index('idx_tenant_user', 'tenant', 'remind_user_id'),
        Index('idx_tenant_status', 'tenant', 'remind_status'),
        {'comment': '跟进提醒表'}
    )


class SaleBlacklist(Base):
    """黑名单表"""
    __tablename__ = 'sale_blacklist'
    
    blacklist_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='黑名单ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    customer_id = Column(BigInteger, ForeignKey('sale_customer.customer_id'), comment='客户ID')
    customer_name = Column(String(50), comment='客户姓名')
    mobile = Column(String(11), comment='手机号')
    id_card = Column(String(18), comment='身份证号')
    blacklist_reason = Column(String(255), comment='加入黑名单原因')
    blacklist_type = Column(String(20), comment='黑名单类型：撞单/恶意/虚假/其他')
    add_user_id = Column(BigInteger, comment='添加人ID')
    add_time = Column(DateTime, server_default=func.now(), comment='添加时间')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        Index('idx_tenant_mobile', 'tenant', 'mobile'),
        {'comment': '黑名单表'}
    )


# ========== 3. 认购签约交易模块 ==========

class SaleHouseLock(Base):
    """房源锁定表"""
    __tablename__ = 'sale_house_lock'
    
    lock_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='锁定ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    house_id = Column(BigInteger, ForeignKey('sale_house.house_id'), nullable=False, comment='房源ID')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), nullable=False, comment='楼盘ID')
    customer_id = Column(BigInteger, ForeignKey('sale_customer.customer_id'), nullable=False, comment='客户ID')
    lock_user_id = Column(BigInteger, comment='锁定人ID')
    lock_time = Column(DateTime, server_default=func.now(), comment='锁定时间')
    expire_time = Column(DateTime, comment='锁定过期时间')
    lock_status = Column(SmallInteger, default=1, comment='锁定状态：1-锁定中 2-已认购 3-已解锁 4-已过期')
    lock_reason = Column(String(255), comment='锁定原因')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_house', 'tenant', 'house_id'),
        Index('idx_tenant_customer', 'tenant', 'customer_id'),
        Index('idx_tenant_status', 'tenant', 'lock_status'),
        {'comment': '房源锁定表'}
    )


class SaleSubscribe(Base):
    """认购单表"""
    __tablename__ = 'sale_subscribe'
    
    subscribe_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='认购ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    subscribe_no = Column(String(50), nullable=False, comment='认购编号')
    house_id = Column(BigInteger, ForeignKey('sale_house.house_id'), nullable=False, comment='房源ID')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), nullable=False, comment='楼盘ID')
    customer_id = Column(BigInteger, ForeignKey('sale_customer.customer_id'), nullable=False, comment='客户ID')
    sale_user_id = Column(BigInteger, ForeignKey('sys_user.user_id'), comment='销售ID')
    subscribe_amount = Column(Decimal(12, 2), comment='认购金额（元）')
    subscribe_date = Column(DateTime, comment='认购日期')
    subscribe_status = Column(SmallInteger, default=1, comment='认购状态：1-已认购 2-已签约 3-已解约 4-已退订')
    cancel_reason = Column(String(255), comment='解约原因')
    cancel_time = Column(DateTime, comment='解约时间')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_no', 'tenant', 'subscribe_no'),
        Index('idx_tenant_house', 'tenant', 'house_id'),
        Index('idx_tenant_customer', 'tenant', 'customer_id'),
        Index('idx_tenant_status', 'tenant', 'subscribe_status'),
        {'comment': '认购单表'}
    )


class SaleContract(Base):
    """签约合同表"""
    __tablename__ = 'sale_contract'
    
    contract_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='合同ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    contract_no = Column(String(50), nullable=False, comment='合同编号')
    subscribe_id = Column(BigInteger, ForeignKey('sale_subscribe.subscribe_id'), comment='关联认购ID')
    house_id = Column(BigInteger, ForeignKey('sale_house.house_id'), nullable=False, comment='房源ID')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), nullable=False, comment='楼盘ID')
    customer_id = Column(BigInteger, ForeignKey('sale_customer.customer_id'), nullable=False, comment='客户ID')
    sale_user_id = Column(BigInteger, ForeignKey('sys_user.user_id'), comment='销售ID')
    contract_amount = Column(Decimal(12, 2), comment='合同金额（元）')
    contract_date = Column(DateTime, comment='签约日期')
    contract_status = Column(SmallInteger, default=1, comment='合同状态：1-待审核 2-已备案 3-已完成 4-已作废')
    record_status = Column(SmallInteger, default=0, comment='备案状态：0-未备案 1-已备案')
    record_time = Column(DateTime, comment='备案时间')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_no', 'tenant', 'contract_no'),
        Index('idx_tenant_house', 'tenant', 'house_id'),
        Index('idx_tenant_customer', 'tenant', 'customer_id'),
        Index('idx_tenant_status', 'tenant', 'contract_status'),
        {'comment': '签约合同表'}
    )


class SalePayment(Base):
    """回款记录表"""
    __tablename__ = 'sale_payment'
    
    payment_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='回款ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    contract_id = Column(BigInteger, ForeignKey('sale_contract.contract_id'), nullable=True, comment='合同ID')
    subscribe_id = Column(BigInteger, ForeignKey('sale_subscribe.subscribe_id'), nullable=True, comment='认购单ID')
    house_id = Column(BigInteger, ForeignKey('sale_house.house_id'), nullable=False, comment='房源ID')
    customer_id = Column(BigInteger, ForeignKey('sale_customer.customer_id'), nullable=False, comment='客户ID')
    payment_no = Column(String(50), nullable=False, comment='回款编号')
    payment_amount = Column(Decimal(12, 2), comment='回款金额（元）')
    payment_type = Column(String(20), comment='付款方式：现金/转账/刷卡/其他')
    payment_date = Column(DateTime, comment='付款日期')
    payment_status = Column(SmallInteger, default=1, comment='付款状态：1-待审核 2-已支付 3-已驳回')
    receive_user_id = Column(BigInteger, comment='收款人ID')
    receive_time = Column(DateTime, comment='收款时间')
    confirm_user_id = Column(BigInteger, comment='确认人ID')
    confirm_time = Column(DateTime, comment='确认时间')
    remark = Column(String(255), comment='备注')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_contract', 'tenant', 'contract_id'),
        Index('idx_tenant_customer', 'tenant', 'customer_id'),
        Index('idx_tenant_status', 'tenant', 'payment_status'),
        {'comment': '回款记录表'}
    )


class SaleLoan(Base):
    """贷款信息表"""
    __tablename__ = 'sale_loan'
    
    loan_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='贷款ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    contract_id = Column(BigInteger, ForeignKey('sale_contract.contract_id'), nullable=False, comment='合同ID')
    loan_type = Column(String(20), comment='贷款类型：商业贷款/公积金贷款/组合贷款')
    loan_amount = Column(Decimal(12, 2), comment='贷款金额（元）')
    loan_period = Column(Integer, comment='贷款期限（月）')
    loan_rate = Column(Decimal(5, 2), comment='贷款利率（%）')
    loan_bank = Column(String(50), comment='贷款银行')
    loan_status = Column(SmallInteger, default=1, comment='贷款状态：1-申请中 2-已审批 3-已放款 4-已驳回')
    approve_time = Column(DateTime, comment='审批时间')
    lend_time = Column(DateTime, comment='放款时间')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        Index('idx_tenant_contract', 'tenant', 'contract_id'),
        {'comment': '贷款信息表'}
    )


class SaleReceipt(Base):
    """发票票据表"""
    __tablename__ = 'sale_receipt'
    
    receipt_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='发票ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    contract_id = Column(BigInteger, ForeignKey('sale_contract.contract_id'), nullable=False, comment='合同ID')
    receipt_no = Column(String(50), nullable=False, comment='发票号码')
    receipt_type = Column(String(20), comment='发票类型：增值税专用发票/增值税普通发票')
    receipt_amount = Column(Decimal(12, 2), comment='发票金额（元）')
    issue_date = Column(DateTime, comment='开票日期')
    receipt_file_url = Column(String(255), comment='发票文件OSS地址')
    receipt_status = Column(SmallInteger, default=1, comment='发票状态：1-正常 2-作废 3-红冲')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        Index('idx_tenant_contract', 'tenant', 'contract_id'),
        {'comment': '发票票据表'}
    )


# ========== 4. 分销渠道与佣金模块 ==========

class SaleChannel(Base):
    """渠道公司表"""
    __tablename__ = 'sale_channel'
    
    channel_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='渠道ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    channel_code = Column(String(50), nullable=False, comment='渠道编码')
    channel_name = Column(String(100), nullable=False, comment='渠道名称')
    contact_person = Column(String(50), comment='联系人')
    contact_mobile = Column(String(11), comment='联系电话')
    channel_level = Column(String(20), comment='渠道等级：一级/二级/三级')
    cooperation_status = Column(SmallInteger, default=1, comment='合作状态：1-合作中 2-已终止')
    start_date = Column(DateTime, comment='合作开始时间')
    end_date = Column(DateTime, comment='合作结束时间')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_code', 'tenant', 'channel_code'),
        Index('idx_tenant_status', 'tenant', 'cooperation_status'),
        {'comment': '渠道公司表'}
    )


class SaleBroker(Base):
    """经纪人表"""
    __tablename__ = 'sale_broker'
    
    broker_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='经纪人ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    channel_id = Column(BigInteger, ForeignKey('sale_channel.channel_id'), nullable=False, comment='渠道ID')
    broker_code = Column(String(50), nullable=False, comment='经纪人编码')
    broker_name = Column(String(50), nullable=False, comment='经纪人姓名')
    mobile = Column(String(11), nullable=False, comment='手机号')
    id_card = Column(String(18), comment='身份证号')
    broker_level = Column(String(20), comment='经纪人等级')
    work_status = Column(SmallInteger, default=1, comment='工作状态：1-在职 2-离职 3-冻结')
    commission_rate = Column(Decimal(5, 2), comment='佣金比例（%）')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_channel', 'tenant', 'channel_id'),
        Index('idx_tenant_mobile', 'tenant', 'mobile'),
        {'comment': '经纪人表'}
    )


class SaleCommissionRule(Base):
    """佣金规则表"""
    __tablename__ = 'sale_commission_rule'
    
    rule_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='规则ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), comment='楼盘ID')
    building_id = Column(BigInteger, ForeignKey('sale_building.building_id'), comment='楼栋ID')
    rule_type = Column(String(20), comment='规则类型：全局/楼盘专属/楼栋专属')
    room_type = Column(String(50), comment='适用户型')
    commission_rate = Column(Decimal(5, 2), comment='佣金比例（%）')
    commission_amount = Column(Decimal(12, 2), comment='固定佣金金额（元）')
    rule_level = Column(Integer, default=1, comment='规则优先级：数字越大优先级越高')
    rule_status = Column(SmallInteger, default=1, comment='规则状态：1-启用 2-停用')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_project', 'tenant', 'project_id'),
        {'comment': '佣金规则表'}
    )


class SaleProjectRule(Base):
    """项目规则表（动态配置规则）"""
    __tablename__ = 'sale_project_rule'
    
    rule_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='规则ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), comment='楼盘ID（为空表示全局规则）')
    rule_key = Column(String(50), nullable=False, comment='规则键：visit_protect_days（到访保护期天数）/ report_protect_days（报备保护期天数）')
    rule_value = Column(Integer, comment='规则值（天数）')
    rule_desc = Column(String(255), comment='规则描述')
    rule_status = Column(SmallInteger, default=1, comment='规则状态：1-启用 2-停用')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_project', 'tenant', 'project_id'),
        Index('idx_tenant_key', 'tenant', 'rule_key'),
        {'comment': '项目规则表'}
    )


class SaleCommissionBill(Base):
    """佣金结算单表"""
    __tablename__ = 'sale_commission_bill'
    
    bill_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='结算单ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    bill_no = Column(String(50), nullable=False, comment='结算单编号')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), nullable=False, comment='楼盘ID')
    channel_id = Column(BigInteger, ForeignKey('sale_channel.channel_id'), nullable=False, comment='渠道ID')
    broker_id = Column(BigInteger, ForeignKey('sale_broker.broker_id'), nullable=False, comment='经纪人ID')
    contract_id = Column(BigInteger, ForeignKey('sale_contract.contract_id'), nullable=False, comment='合同ID')
    bill_amount = Column(Decimal(12, 2), comment='结算金额（元）')
    bill_status = Column(SmallInteger, default=1, comment='结算状态：1-待审核 2-已结算 3-已冻结 4-已作废')
    audit_user_id = Column(BigInteger, comment='审核人ID')
    audit_time = Column(DateTime, comment='审核时间')
    pay_time = Column(DateTime, comment='支付时间')
    freeze_reason = Column(String(255), comment='冻结原因')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_no', 'tenant', 'bill_no'),
        Index('idx_tenant_project', 'tenant', 'project_id'),
        Index('idx_tenant_broker', 'tenant', 'broker_id'),
        Index('idx_tenant_status', 'tenant', 'bill_status'),
        {'comment': '佣金结算单表'}
    )


# ========== 5. 销售业绩与考核模块 ==========

class SaleTeam(Base):
    """销售团队表"""
    __tablename__ = 'sale_team'
    
    team_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='团队ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    team_code = Column(String(50), nullable=False, comment='团队编码')
    team_name = Column(String(100), nullable=False, comment='团队名称')
    parent_team_id = Column(BigInteger, comment='父团队ID')
    leader_id = Column(BigInteger, comment='团队负责人ID')
    team_level = Column(Integer, default=1, comment='团队层级')
    member_count = Column(Integer, default=0, comment='成员数量')
    team_status = Column(SmallInteger, default=1, comment='团队状态：1-正常 2-停用 3-解散')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_code', 'tenant', 'team_code', unique=True),
        Index('idx_tenant_leader', 'tenant', 'leader_id'),
        {'comment': '销售团队表'}
    )


class SaleTeamMember(Base):
    """销售团队成员关联表"""
    __tablename__ = 'sale_team_member'
    
    member_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='成员ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    team_id = Column(BigInteger, ForeignKey('sale_team.team_id'), nullable=False, comment='团队ID')
    user_id = Column(BigInteger, ForeignKey('sys_user.user_id'), nullable=False, comment='用户ID')
    member_role = Column(String(20), default='member', comment='成员角色：leader-负责人 member-普通成员')
    join_date = Column(DateTime, comment='入队时间')
    leave_date = Column(DateTime, comment='离队时间')
    member_status = Column(SmallInteger, default=1, comment='成员状态：1-在岗 2-离岗 3-转调')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_team', 'tenant', 'team_id'),
        Index('idx_tenant_user', 'tenant', 'user_id'),
        Index('idx_team_user', 'team_id', 'user_id'),
        {'comment': '销售团队成员关联表'}
    )


class SalePerformanceTarget(Base):
    """业绩目标表"""
    __tablename__ = 'sale_performance_target'
    
    target_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='目标ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), nullable=False, comment='楼盘ID')
    target_type = Column(String(20), nullable=False, comment='目标类型：个人/团队')
    target_user_id = Column(BigInteger, comment='目标用户ID（个人）')
    target_team_id = Column(BigInteger, comment='目标团队ID（团队）')
    time_type = Column(String(20), comment='时间类型：月度/季度/年度')
    time_value = Column(String(20), comment='时间值（如：2025-09）')
    target_amount = Column(Decimal(12, 2), comment='目标金额（元）')
    target_sets = Column(Integer, comment='目标套数')
    target_status = Column(SmallInteger, default=1, comment='目标状态：1-进行中 2-已完成 3-已过期')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        Index('idx_tenant_project', 'tenant', 'project_id'),
        Index('idx_tenant_user', 'tenant', 'target_user_id'),
        Index('idx_tenant_team', 'tenant', 'target_team_id'),
        {'comment': '业绩目标表'}
    )


class SaleSalesCommission(Base):
    """销售提成表"""
    __tablename__ = 'sale_sales_commission'
    
    commission_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='提成ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    commission_no = Column(String(50), nullable=False, comment='提成编号')
    project_id = Column(BigInteger, ForeignKey('sale_project.project_id'), nullable=False, comment='楼盘ID')
    contract_id = Column(BigInteger, ForeignKey('sale_contract.contract_id'), nullable=False, comment='合同ID')
    sale_user_id = Column(BigInteger, ForeignKey('sys_user.user_id'), comment='销售ID')
    sale_team_id = Column(BigInteger, ForeignKey('sale_team.team_id'), comment='销售团队ID')
    commission_amount = Column(Decimal(12, 2), comment='提成金额（元）')
    commission_rate = Column(Decimal(5, 2), comment='提成比例（%）')
    base_amount = Column(Decimal(12, 2), comment='提成基数（元）')
    commission_status = Column(SmallInteger, default=1, comment='提成状态：1-待审核 2-已发放 3-已冻结 4-已作废')
    audit_user_id = Column(BigInteger, comment='审核人ID')
    audit_time = Column(DateTime, comment='审核时间')
    pay_time = Column(DateTime, comment='发放时间')
    freeze_reason = Column(String(255), comment='冻结原因')
    status = Column(SmallInteger, default=1, comment='状态：1-正常 2-停用')
    is_del = Column(SmallInteger, default=0, comment='逻辑删除：0-正常 1-删除')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    version = Column(Integer, default=0, comment='乐观锁版本号')
    
    __table_args__ = (
        Index('idx_tenant_no', 'tenant', 'commission_no'),
        Index('idx_tenant_project', 'tenant', 'project_id'),
        Index('idx_tenant_user', 'tenant', 'sale_user_id'),
        Index('idx_tenant_status', 'tenant', 'commission_status'),
        {'comment': '销售提成表'}
    )


# ========== 6. 统计报表模块 ==========

class SaleStatDailyLogs(Base):
    """系统操作日志表"""
    __tablename__ = 'sale_stat_daily_logs'
    
    log_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    tenant = Column(String(32), nullable=False, index=True, comment='租户编码')
    user_id = Column(BigInteger, comment='操作人ID')
    operation_type = Column(String(50), comment='操作类型')
    operation_content = Column(Text, comment='操作内容')
    operation_ip = Column(String(50), comment='操作IP')
    operation_result = Column(SmallInteger, comment='操作结果：0-失败 1-成功')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    
    __table_args__ = (
        Index('idx_tenant_user', 'tenant', 'user_id'),
        Index('idx_tenant_time', 'tenant', 'create_time'),
        {'comment': '系统操作日志表'}
    )