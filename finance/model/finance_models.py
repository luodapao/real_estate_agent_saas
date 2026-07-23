"""
财务模块ORM模型定义
遵循SQLAlchemy 2.0异步开发标准
所有模型均包含租户隔离、逻辑删除、乐观锁字段
"""
from sqlalchemy import (
    Column, BigInteger, String, Numeric, SmallInteger, Integer, DateTime, Date, Text, 
    func, Index, Boolean
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# ==================== 财务基础档案模块 ====================

class FinProjectFinConfig(Base):
    """楼盘财务配置表"""
    __tablename__ = "fin_project_fin_config"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，顶层数据隔离")
    project_id = Column(BigInteger, nullable=False, comment="关联楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余，减少联表查询")
    finance_status = Column(SmallInteger, nullable=False, default=1, comment="财务启用状态：1启用 2停用")
    calc_mode = Column(SmallInteger, nullable=False, default=1, comment="计税模式：1一般计税 2简易计税")
    default_tax_rate_id = Column(BigInteger, comment="默认计税税率模板ID，fin_tax_rate")
    default_income_subject_id = Column(BigInteger, comment="默认收入科目ID，fin_subject")
    default_receive_account_id = Column(BigInteger, comment="默认通用收款账户ID，fin_account")
    default_mortgage_account_id = Column(BigInteger, comment="按揭回款专用收款账户ID")
    default_supervise_account_id = Column(BigInteger, comment="预售资金监管专户ID")
    default_cap_cost_subject_id = Column(BigInteger, comment="资本化开发成本默认科目ID")
    default_market_subject_id = Column(BigInteger, comment="广告营销费用默认科目ID")
    default_payable_subject_id = Column(BigInteger, comment="供应商应付账款科目ID")
    default_advance_subject_id = Column(BigInteger, comment="供应商预付账款科目ID")
    default_channel_subject_id = Column(BigInteger, comment="分销渠道佣金往来科目ID")
    default_tax_subject_id = Column(BigInteger, comment="应交税费总账科目ID")
    deposit_ratio = Column(Numeric(5,4), default=0.0, comment="定金比例上限")
    installment_rule = Column(Text, comment="分期规则JSON配置")
    max_advance_ratio = Column(Numeric(5,4), default=0.0, comment="供应商预付工程款比例上限")
    settle_cycle_type = Column(SmallInteger, default=1, comment="默认供应商结算周期：1月结 2季结 3竣工一次性结算")
    close_status = Column(SmallInteger, default=0, comment="项目财务归档状态：0在建未结账 1竣工已结账归档")
    remark = Column(Text, comment="财务配置备注说明")
    create_user_id = Column(BigInteger, nullable=False, comment="配置创建人sys_user ID")
    update_user_id = Column(BigInteger, comment="配置最后修改人sys_user ID")
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index("uk_tenant_project", "tenant", "project_id", "is_del", unique=True),
        Index("idx_tenant", "tenant"),
        {"comment": "楼盘财务配置表"}
    )



class FinAccount(Base):
    """财务账户表（开发商自有资金账户，不含供应商/渠道乙方收款账户）"""
    __tablename__ = "fin_account"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，集团多主体隔离")
    account_code = Column(String(64), nullable=False, comment="账户编码，租户内唯一")
    account_name = Column(String(100), nullable=False, comment="账户名称")
    project_id = Column(BigInteger, comment="归属楼盘ID，通用多项目共用账户为空")
    project_name = Column(String(128), comment="楼盘名称冗余，减少联表查询")
    account_type = Column(SmallInteger, nullable=False, comment="账户大类：1现金 2银行存款 3支付宝 4微信")
    account_use_type = Column(SmallInteger, nullable=False, default=2, comment="账户用途：1预售监管户 2一般经营户 3融资专户 4保证金户")
    bank_name = Column(String(100), comment="开户银行名称")
    bank_account = Column(String(50), comment="银行账号（脱敏存储，不展示完整卡号）")
    cnaps_code = Column(String(20), comment="银行联行号，用于网银转账报文导出")
    account_holder = Column(String(100), comment="开户人姓名")
    mobile = Column(String(20), comment="联系电话")
    subject_id = Column(BigInteger, comment="对应银行存款会计科目ID，fin_subject")
    subject_name = Column(String(256), comment="科目名称冗余")
    tax_rate_id = Column(BigInteger, comment="手续费、利息收入适用税率ID，fin_tax_rate")
    account_status = Column(SmallInteger, nullable=False, default=1, comment="账户状态：1启用 2停用，停用后收付款单据不可选用")
    is_default = Column(SmallInteger, default=0, comment="是否项目默认收款账户：0否 1是")
    remark = Column(Text, comment="账户备注、开户日期、监管备案编号等说明")
    create_user_id = Column(BigInteger, nullable=False, comment="档案创建人sys_user ID")
    update_user_id = Column(BigInteger, comment="档案最后修改人sys_user ID")
    version = Column(Integer, default=0, comment="乐观锁版本号，并发编辑防覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常有效 1逻辑删除销户账户")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_account_code", "tenant", "account_code", "is_del", unique=True),
        Index("idx_tenant", "tenant"),
        Index("idx_tenant_type", "tenant", "account_type"),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_use_type", "tenant", "account_use_type"),
        {"comment": "财务账户表（开发商自有资金账户，不含外部合作方对公收款账户）"}
    )



class FinSubject(Base):
    """会计科目表，企业标准化总账科目档案，控制凭证分录、辅助核算、自动计税规则"""
    __tablename__ = "fin_subject"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团账务隔离")
    subject_code = Column(String(64), nullable=False, comment="科目编码，租户内唯一，树形层级编码")
    subject_name = Column(String(100), nullable=False, comment="科目名称")
    subject_level = Column(SmallInteger, nullable=False, default=1, comment="科目层级：1一级 2二级 3三级 4四级")
    parent_id = Column(BigInteger, default=0, comment="上级父科目ID，顶级科目parent_id=0")
    subject_type = Column(SmallInteger, nullable=False, comment="科目大类：1资产 2负债 3权益 4成本 5损益")
    subject_nature = Column(SmallInteger, nullable=False, comment="科目余额方向：1借方 2贷方")
    is_leaf = Column(SmallInteger, nullable=False, default=1, comment="是否末级科目：1是(可制单) 0否(仅汇总，禁止分录)")
    is_enabled = Column(SmallInteger, nullable=False, default=1, comment="启用状态：1启用 2停用，停用不可新增凭证")
    aux_project = Column(SmallInteger, nullable=False, default=0, comment="是否开启项目辅助核算：0否 1是")
    aux_supplier = Column(SmallInteger, nullable=False, default=0, comment="是否开启供应商往来辅助核算：0否 1是")
    aux_customer = Column(SmallInteger, nullable=False, default=0, comment="是否开启购房客户辅助核算：0否 1是")
    aux_bank = Column(SmallInteger, nullable=False, default=0, comment="是否开启银行账户辅助核算：0否 1是")
    account_id = Column(BigInteger, comment="关联账户ID，fin_account")
    default_tax_rate_id = Column(BigInteger, comment="科目默认适用税率ID，关联fin_tax_rate")
    business_scene = Column(SmallInteger, comment="适用业务场景：1房款收入 2开发成本 3营销费用 4往来应付预付 5融资收支 6税费计提缴纳")
    remark = Column(Text, comment="科目备注、使用说明、财税特殊规则备注")
    create_user_id = Column(BigInteger, nullable=False, comment="科目档案创建人sys_user ID")
    update_user_id = Column(BigInteger, comment="科目最后修改操作人sys_user ID")
    version = Column(Integer, default=0, comment="乐观锁版本号，并发编辑防数据覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常有效 1逻辑删除，历史凭证关联科目不可物理删除")
    create_time = Column(DateTime, server_default=func.now(), comment="记录创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="记录更新时间")

    __table_args__ = (
        Index("uk_tenant_subject_code", "tenant", "subject_code", "is_del", unique=True),
        Index("idx_tenant", "tenant"),
        Index("idx_tenant_type", "tenant", "subject_type"),
        Index("idx_tenant_parent", "tenant", "parent_id"),
        Index("idx_tenant_leaf", "tenant", "is_leaf"),
        Index("idx_tenant_enabled", "tenant", "is_enabled"),
        {"comment": "会计科目表，企业标准化总账科目档案，控制凭证分录、辅助核算、自动计税规则"}
    )




class FinTaxRate(Base):
    """税率配置表，存储增值税、附加税、印花税等全税种计税模板，业务单据自动计税依据"""
    __tablename__ = "fin_tax_rate"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团数据隔离")
    tax_code = Column(String(64), nullable=False, comment="税率编码，租户内唯一")
    tax_name = Column(String(100), nullable=False, comment="税率模板名称")
    tax_type = Column(SmallInteger, nullable=False, comment="税种类型：1增值税 2附加税 3印花税")
    tax_rate = Column(Numeric(5,4), nullable=False, comment="税率比例，如0.09代表9%")
    # 新增：区分一般/简易计税，房企项目核心字段
    calc_mode = Column(SmallInteger, nullable=False, default=1, comment="计税模式：1一般计税 2简易计税")
    tax_desc = Column(String(255), comment="税率描述说明、政策依据备注")
    # 新增：绑定对应会计科目，自动生成税费凭证
    bind_subject_id = Column(BigInteger, comment="关联会计科目ID，fin_subject")
    # 新增：适用业务场景，单据自动匹配税率模板
    biz_scope = Column(SmallInteger, comment="适用业务：1不动产销售 2建安工程 3广告服务 4利息收入 5印花税计提")
    is_default = Column(SmallInteger, default=0, comment="是否租户全局默认税率：0否 1是")
    tax_status = Column(SmallInteger, nullable=False, default=1, comment="模板状态：1启用 2停用，停用后单据不可选用")
    remark = Column(Text, comment="税率政策、特殊抵扣规则备注")
    # 新增审计操作人字段
    create_user_id = Column(BigInteger, nullable=False, comment="模板创建人sys_user ID")
    update_user_id = Column(BigInteger, comment="模板最后修改人sys_user ID")
    # 统一乐观锁类型，全财务系统规范对齐
    version = Column(Integer, default=0, comment="乐观锁版本号，并发编辑防覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常有效 1逻辑删除作废模板")
    create_time = Column(DateTime, server_default=func.now(), comment="记录创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="记录更新时间")

    __table_args__ = (
        Index("uk_tenant_tax_code", "tenant", "tax_code", "is_del", unique=True),
        Index("idx_tenant", "tenant"),
        Index("idx_tenant_type", "tenant", "tax_type"),
        Index("idx_tenant_calc_mode", "tenant", "calc_mode"),
        Index("idx_tenant_subject", "tenant", "bind_subject_id"),
        {"comment": "税率配置表，存储增值税、附加税、印花税等全税种计税模板，业务单据自动计税依据"}
    )



class FinBankInfo(Base):
    """合作方对公银行档案表，存储供应商/渠道等乙方收款账户，与我方自有账户FinAccount完全隔离"""
    __tablename__ = "fin_bank_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团数据隔离")
    bank_info_code = Column(String(64), nullable=False, comment="银行档案编码，租户内唯一")
    bank_name = Column(String(100), nullable=False, comment="开户银行名称")
    bank_account = Column(String(50), nullable=False, comment="银行账号（脱敏存储，前端不展示完整卡号）")
    account_name = Column(String(100), nullable=False, comment="对公账户户名（合作企业全称）")
    cnaps_code = Column(String(20), comment="银行联行号，用于批量付款导出网银转账报文")
    company_type = Column(SmallInteger, nullable=False, comment="账户主体类型：1开发商自有(极少使用) 2分销渠道 3工程/材料供应商")
    company_id = Column(BigInteger, comment="关联主体ID，对应渠道/供应商主键")
    company_name = Column(String(128), comment="主体名称冗余，列表展示无需联表查询")
    project_id = Column(BigInteger, comment="限定适用楼盘ID，空代表全项目通用")
    is_default_settle = Column(SmallInteger, default=0, comment="是否该主体默认收款账户：0否 1是，付款单自动优先带出")
    settle_subject_id = Column(BigInteger, comment="往来结算会计科目ID，关联fin_subject应付/预付科目")
    tax_rate_id = Column(BigInteger, comment="合作方固定进项税率ID，关联fin_tax_rate")
    bank_status = Column(SmallInteger, nullable=False, default=1, comment="账户档案状态：1启用 2停用，停用付款单不可选择")
    remark = Column(Text, comment="账户备注、结算周期、发票开票信息备注")
    create_user_id = Column(BigInteger, nullable=False, comment="档案创建人sys_user ID")
    update_user_id = Column(BigInteger, comment="档案最后修改人sys_user ID")
    version = Column(Integer, default=0, comment="乐观锁版本号，并发编辑防数据覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常有效 1逻辑删除废弃账户档案")
    create_time = Column(DateTime, server_default=func.now(), comment="记录创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="记录更新时间")

    __table_args__ = (
        Index("uk_tenant_bank_code", "tenant", "bank_info_code", "is_del", unique=True),
        Index("idx_tenant", "tenant"),
        Index("idx_tenant_company_type", "tenant", "company_type"),
        Index("idx_tenant_company", "tenant", "company_type", "company_id"),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_default", "tenant", "company_id", "is_default_settle"),
        {"comment": "合作方对公银行档案表，存储供应商/渠道等乙方收款账户，与我方自有账户FinAccount完全隔离"}
    )



class FinDiscountRule(Base):
    """优惠规则配置表，楼盘销售折扣/一口价/减免活动配置，控制房款收入冲减及红字计税凭证生成"""
    __tablename__ = "fin_discount_rule"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团数据隔离")
    project_id = Column(BigInteger, nullable=False, comment="关联楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余，减少报表联表查询")
    discount_code = Column(String(64), nullable=False, comment="优惠规则编码，租户内唯一")
    discount_name = Column(String(100), nullable=False, comment="优惠活动名称")
    discount_type = Column(SmallInteger, nullable=False, comment="优惠类型：1比例折扣 2一口价特惠 3现金减免 4多种优惠组合")
    property_type = Column(String(30), nullable=False, comment="适用物业类型，多类型逗号分隔存储")
    discount_rate = Column(Numeric(5,4), default=1.0, comment="折扣比例，0.9代表9折，仅折扣类型生效")
    fixed_price = Column(Numeric(14,2), default=0, comment="一口价成交总价，仅一口价类型生效")
    max_discount_amount = Column(Numeric(14,2), default=0, comment="单房源最大优惠上限")
    contract_type = Column(SmallInteger, comment="适用签约类型：1全款 2按揭 3分期，空=全部适用")
    start_time = Column(DateTime, nullable=False, comment="优惠规则生效起始时间")
    end_time = Column(DateTime, comment="优惠规则失效截止时间，空代表长期有效")
    is_stack = Column(SmallInteger, default=0, comment="是否可与其他优惠叠加：0不可叠加 1允许叠加")
    offset_income = Column(SmallInteger, default=1, comment="优惠是否冲减主营业务收入：1是(生成红字收入凭证) 0否(视同销售不计冲减)")
    discount_subject_id = Column(BigInteger, comment="优惠冲减对应收入会计科目ID，关联fin_subject")
    tax_rate_id = Column(BigInteger, comment="优惠红字销项税税率模板ID，关联fin_tax_rate")
    rule_status = Column(SmallInteger, nullable=False, default=1, comment="规则状态：1启用 2停用，停用后签约无法选用该优惠")
    remark = Column(Text, comment="活动说明、优惠限制、财务特殊处理备注")
    create_user_id = Column(BigInteger, nullable=False, comment="规则创建人sys_user ID")
    update_user_id = Column(BigInteger, comment="规则最后修改人sys_user ID")
    version = Column(Integer, default=0, comment="乐观锁版本号，并发编辑防数据覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常有效 1逻辑删除作废活动规则")
    create_time = Column(DateTime, server_default=func.now(), comment="记录创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="记录更新时间")

    __table_args__ = (
        Index("uk_tenant_discount_code", "tenant", "discount_code", "is_del", unique=True),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_status", "tenant", "rule_status"),
        Index("idx_tenant_valid_time", "tenant", "rule_status", "start_time", "end_time"),
        {"comment": "优惠规则配置表，楼盘销售折扣/一口价/减免活动配置，控制房款收入冲减及红字计税凭证生成"}
    )


# ==================== 房款收支核心模块 ====================



class FinInstallmentPlan(Base):
    """客户分期回款计划表：签约分期单期应收明细，支撑分期催收、回款匹配、分步确认收入计税"""
    __tablename__ = "fin_installment_plan"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团数据隔离")
    plan_no = Column(String(64), nullable=False, comment="分期单据编号，租户内唯一")
    # 房源客户楼盘基础维度 + 冗余名称减少联表
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID，关联sale_project")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    house_id = Column(BigInteger, nullable=False, comment="房源ID")
    house_no = Column(String(60), nullable=False, comment="房源房号冗余")
    customer_id = Column(BigInteger, nullable=False, comment="客户ID")
    customer_name = Column(String(80), nullable=False, comment="客户姓名冗余")
    contract_id = Column(BigInteger, nullable=False, comment="签约合同单ID")
    # 财务配置关联
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID fin_project_fin_config")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="计税税率模板ID fin_tax_rate")
    calc_mode = Column(SmallInteger, nullable=False, default=1, comment="计税模式：1一般计税 2简易计税，冗余避免联查配置")
    income_subject_id = Column(BigInteger, nullable=False, comment="应收收入会计科目ID fin_subject")
    discount_rule_id = Column(BigInteger, comment="分期适用优惠规则ID fin_discount_rule")
    receive_account_id = Column(BigInteger, comment="分期回款默认收款账户ID fin_account")
    installment_rule_json = Column(Text, comment="生成本期分期使用的规则快照JSON，留存规则变更依据")
    # 分期期数字段（重命名消除歧义）
    total_period = Column(SmallInteger, nullable=False, comment="整套分期总期数")
    period_no = Column(SmallInteger, nullable=False, comment="当前明细对应期号（原current_period重命名）")
    due_date = Column(DateTime, nullable=False, comment="本期应收回款到期日")
    # 拆分含税/不含税房款，消除计税混淆，删除冗余可计算字段period_tax_total
    period_untax_amt = Column(Numeric(16,2), nullable=False, comment="本期应收不含税房款本金")
    period_vat = Column(Numeric(16,2), nullable=False, comment="本期对应增值税销项税额")
    period_maintain = Column(Numeric(16,2), default=0, comment="本期代收维修基金（单独代收，不计房款计税基数）")
    period_total = Column(Numeric(16,2), nullable=False, comment="本期应收总金额=不含税房款+增值税+维修基金")
    # 回款实收余额
    received_amount = Column(Numeric(16,2), default=0, comment="本期已实际收款金额")
    unpaid_amount = Column(Numeric(16,2), nullable=False, comment="本期剩余未收余额")
    settle_time = Column(DateTime, comment="本期实际结清完成时间")
    # 逾期罚息管控字段
    overdue_days = Column(Integer, default=0, comment="当前逾期天数，定时任务自动更新")
    overdue_rate = Column(Numeric(8,6), default=0, comment="逾期罚息日利率，用于自动计算罚息")
    overdue_interest = Column(Numeric(16,2), default=0, comment="累计产生逾期罚息总额")
    overdue_calc_flag = Column(SmallInteger, default=1, comment="是否开启自动计息：0关闭 1开启")
    # 单据状态细化枚举
    plan_status = Column(SmallInteger, default=1, comment="分期状态：1待收款 2正常结清 3逾期未收 4手动作废 5逾期结清")
    offset_record_no = Column(String(64), comment="作废/冲销关联退款/红字单据编号")
    remark = Column(Text, comment="分期业务备注、特殊约定说明")
    settle_remark = Column(Text, comment="本期结清备注、回款说明")
    # 操作人审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="分期计划制单人sys_user ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    audit_user_id = Column(BigInteger, comment="分期财务审核人sys_user ID")
    # 统一全系统乐观锁规范，BigInteger改为Integer
    version = Column(Integer, default=0, comment="乐观锁版本号，并发更新防覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常有效 1逻辑删除作废分期计划")
    create_time = Column(DateTime, server_default=func.now(), comment="记录创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="记录更新时间")

    __table_args__ = (
        Index("uk_tenant_plan_no", "tenant", "plan_no", "is_del", unique=True),
        Index("idx_tenant_contract", "tenant", "contract_id"),
        Index("idx_tenant_due_date", "tenant", "due_date"),
        Index("idx_tenant_customer", "tenant", "customer_id"),
        Index("idx_tenant_house", "tenant", "house_id"),
        Index("idx_tenant_status", "tenant", "plan_status"),
        Index("idx_tenant_overdue", "tenant", "plan_status", "due_date"),
        {"comment": "客户分期回款计划表：签约分期单期应收明细，支撑分期催收、回款匹配、分步确认收入计税"}
    )



class FinPriceDiff(Base):
    """面积差价调整单据表，支持实测面积补差/退差、车位储藏室溢价调整，作为收入红字/蓝字计税凭证源头"""
    __tablename__ = "fin_price_diff"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团数据隔离")
    diff_no = Column(String(64), nullable=False, comment="差价单据编号，租户内唯一")
    # 楼盘房源客户基础维度+冗余名称优化联表查询
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID，关联sale_project")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    house_id = Column(BigInteger, nullable=False, comment="房源ID")
    house_no = Column(String(60), nullable=False, comment="房源房号冗余")
    contract_id = Column(BigInteger, nullable=False, comment="购房合同ID")
    customer_id = Column(BigInteger, nullable=False, comment="购房客户ID")
    customer_name = Column(String(80), nullable=False, comment="客户姓名冗余")
    # 财务核算关联配置
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID fin_project_fin_config")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="差价计税税率模板ID fin_tax_rate")
    calc_mode = Column(SmallInteger, nullable=False, default=1, comment="计税模式：1一般计税 2简易计税")
    income_subject_id = Column(BigInteger, nullable=False, comment="差价收入对应会计科目ID fin_subject")
    discount_rule_id = Column(BigInteger, comment="差价适用优惠规则ID fin_discount_rule")
    # 面积测绘核心数据
    predict_area = Column(Numeric(10,2), nullable=False, comment="合同预测建筑面积(㎡)")
    actual_area = Column(Numeric(10,2), nullable=False, comment="竣工实测建筑面积(㎡)")
    diff_area = Column(Numeric(10,2), nullable=False, comment="面积差额，正数面积增加、负数面积减少")
    unit_price = Column(Numeric(14,2), nullable=False, comment="合同成交不含税单价")
    # 差价金额拆分（区分不含税本金、税额，消除计税混淆）
    diff_untax_amt = Column(Numeric(16,2), nullable=False, comment="差价不含税本金（原diff_principal）")
    diff_vat = Column(Numeric(16,2), nullable=False, comment="差价对应增值税销项税额")
    diff_total = Column(Numeric(16,2), nullable=False, comment="差价总金额=不含税差价+增值税，正数补差价、负数退差价")
    # 差价类型扩展，兼容面积/车位/储藏室溢价
    diff_type = Column(SmallInteger, nullable=False, comment="差价类型：1实测面积补差价 2实测面积退差价 3车位/储藏室溢价补差")
    # 业务调整控制开关
    adjust_commission = Column(SmallInteger, default=1, comment="是否同步调整渠道佣金计算基数：0否 1是")
    adjust_tax = Column(SmallInteger, default=1, comment="是否同步调整计税收入及销项税额：0否 1是")
    # 测绘档案附件溯源字段
    survey_no = Column(String(64), comment="房产测绘报告编号，土增清算必备")
    survey_org = Column(String(200), comment="出具测绘报告机构名称")
    survey_file_url = Column(String(1024), comment="测绘报告PDF/图片OSS附件链接")
    # 回款/退款单据关联溯源
    receipt_record_no = Column(String(64), comment="补差价关联收款单编号fin_receipt_record")
    refund_record_no = Column(String(64), comment="退差价关联退款单编号fin_refund_record")
    # 审核流程字段
    audit_status = Column(SmallInteger, default=1, comment="单据审核状态：1待审核 2已审核通过 3审核驳回 4已作废冲销")
    audit_time = Column(DateTime, comment="财务审核完成时间")
    audit_user_id = Column(BigInteger, comment="审核人sys_user ID")
    # 审计操作人
    create_user_id = Column(BigInteger, nullable=False, comment="差价单据制单人sys_user ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    remark = Column(Text, comment="差价调整说明、测绘差异备注、特殊财务处理说明")
    # 统一全系统乐观锁规范，BigInteger改为Integer
    version = Column(Integer, default=0, comment="乐观锁版本号，并发编辑防数据覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常有效 1逻辑删除作废单据")
    create_time = Column(DateTime, server_default=func.now(), comment="记录创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="记录更新时间")

    __table_args__ = (
        Index("uk_tenant_diff_no", "tenant", "diff_no", "is_del", unique=True),
        Index("idx_tenant_contract", "tenant", "contract_id"),
        Index("idx_tenant_house", "tenant", "house_id"),
        Index("idx_tenant_customer", "tenant", "customer_id"),
        Index("idx_tenant_audit_status", "tenant", "audit_status"),
        Index("idx_tenant_diff_type", "tenant", "diff_type"),
        {"comment": "面积差价调整单据表，支持实测面积补差/退差、车位储藏室溢价调整，作为收入红字/蓝字计税凭证源头"}
    )



class FinReceiptRecord(Base):
    """收款记录表：客户购房款项实收凭证，支撑收款对账、资金入账、收入确认、佣金结算全流程"""
    __tablename__ = "fin_receipt_record"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团数据隔离")
    receipt_no = Column(String(64), nullable=False, comment="收款单据编号，租户内唯一")
    # 楼盘房源客户基础维度+冗余名称优化联表查询
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID，关联sale_project")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    house_id = Column(BigInteger, nullable=False, comment="房源ID")
    house_no = Column(String(60), nullable=False, comment="房源房号冗余")
    contract_id = Column(BigInteger, nullable=False, comment="购房合同ID")
    customer_id = Column(BigInteger, nullable=False, comment="购房客户ID")
    customer_name = Column(String(80), nullable=False, comment="客户姓名冗余")
    # 财务账户与核算配置
    account_id = Column(BigInteger, nullable=False, comment="收款账户ID fin_account")
    account_name = Column(String(100), nullable=False, comment="收款账户名称冗余")
    account_type = Column(SmallInteger, nullable=False, comment="账户类型：1监管账户 2经营账户 3其他")
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID fin_project_fin_config")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="收款计税税率模板ID fin_tax_rate")
    income_subject_id = Column(BigInteger, nullable=False, comment="收款对应会计科目ID fin_subject")
    # 收款核心信息
    receipt_date = Column(DateTime, nullable=False, server_default=func.now(), comment="实际收款日期")
    receipt_type = Column(SmallInteger, nullable=False, comment="收款类型：1定金 2首付 3分期 4面积补差 5车位款 6储藏室款 7其他")
    pay_way = Column(SmallInteger, nullable=False, comment="支付方式：1现金 2银行卡转账 3微信 4支付宝 5POS刷卡 6银行按揭 7银行汇票")
    payer_name = Column(String(80), nullable=False, comment="实际付款人姓名，可能与客户不一致")
    payer_account = Column(String(50), comment="付款人银行账号（脱敏）")
    # 金额字段标准化拆分（区分不含税/税额/代收款项）
    receipt_amount = Column(Numeric(16,2), nullable=False, comment="实收总金额（含税+代收）")
    untax_principal = Column(Numeric(16,2), nullable=False, comment="房款不含税本金")
    tax_amount = Column(Numeric(16,2), nullable=False, comment="代收增值税销项税额")
    maintain_amount = Column(Numeric(16,2), default=0, comment="代收维修基金（不计入收入计税）")
    other_fee_amount = Column(Numeric(16,2), default=0, comment="代收其他费用（如工本费、印花税等）")
    # 业务关联溯源
    deposit_account_id = Column(BigInteger, comment="抵扣首付的认筹/定金台账ID fin_deposit_account")
    installment_id = Column(BigInteger, comment="关联分期计划ID fin_installment_plan")
    diff_id = Column(BigInteger, comment="关联差价单据ID fin_price_diff")
    order_id = Column(BigInteger, comment="关联认购单ID sale_order")
    discount_rule_id = Column(BigInteger, comment="收款适用优惠规则ID fin_discount_rule")
    # 对账与资金核验
    verify_status = Column(SmallInteger, default=1, comment="对账状态：1未对账 2已对账一致 3对账异常 4待补单")
    verify_time = Column(DateTime, comment="对账完成时间")
    verify_user_id = Column(BigInteger, comment="对账操作人ID")
    bank_flow_id = Column(BigInteger, comment="关联银行流水ID fin_bank_flow")
    bank_flow_no = Column(String(64), comment="银行流水单号冗余，便于快速核对")
    reconcile_remark = Column(Text, comment="对账差异说明、异常处理记录")
    # 财务审核流程
    audit_status = Column(SmallInteger, default=1, comment="审核状态：1待审核 2已通过 3已驳回 4已作废 5已冲销")
    audit_time = Column(DateTime, comment="审核完成时间")
    audit_user_id = Column(BigInteger, comment="审核人sys_user ID")
    # 凭证与附件管理
    receipt_file_url = Column(String(1024), comment="收款凭证PDF/图片OSS附件链接，支持多文件")
    receipt_voucher_no = Column(String(64), comment="对应财务凭证编号，自动生成")
    # 操作审计
    create_user_id = Column(BigInteger, nullable=False, comment="收款单据制单人sys_user ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    operate_time = Column(DateTime, server_default=func.now(), comment="收款操作时间")
    remark = Column(Text, comment="收款备注、特殊情况说明")
    # 统一全系统乐观锁规范，BigInteger改为Integer
    version = Column(Integer, default=0, comment="乐观锁版本号，并发编辑防数据覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常有效 1逻辑删除作废单据")
    create_time = Column(DateTime, server_default=func.now(), comment="记录创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="记录更新时间")

    __table_args__ = (
        Index("uk_tenant_receipt_no", "tenant", "receipt_no", "is_del", unique=True),
        Index("idx_tenant_contract", "tenant", "contract_id"),
        Index("idx_tenant_customer", "tenant", "customer_id"),
        Index("idx_tenant_house", "tenant", "house_id"),
        Index("idx_tenant_receipt_date", "tenant", "receipt_date"),
        Index("idx_tenant_audit_verify", "tenant", "audit_status", "verify_status"),
        Index("idx_tenant_receipt_type", "tenant", "receipt_type"),
        Index("idx_tenant_account", "tenant", "account_id"),
        Index("idx_tenant_deposit_rel", "tenant", "deposit_account_id"),
        {"comment": "收款记录表：客户购房款项实收凭证，支撑收款对账、资金入账、收入确认、佣金结算全流程"}
    )



class FinRefundRecord(Base):
    """退款记录表：房款原路退款、退房/面积补差/认筹退费业务单据，生成红字冲销收入凭证，监管资金原路退回管控"""
    __tablename__ = "fin_refund_record"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团数据隔离")
    refund_no = Column(String(64), nullable=False, comment="退款单据编号，租户内唯一")
    # 楼盘/房源/客户维度 + 冗余名称，减少报表联表查询
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID，关联sale_project")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    house_id = Column(BigInteger, nullable=False, comment="房源ID")
    house_no = Column(String(60), nullable=False, comment="房源房号冗余")
    contract_id = Column(BigInteger, nullable=False, comment="购房合同ID")
    customer_id = Column(BigInteger, nullable=False, comment="购房客户ID")
    customer_name = Column(String(80), nullable=False, comment="客户姓名冗余")
    # 退款我方付款账户信息
    account_id = Column(BigInteger, nullable=False, comment="我方退款支出账户ID fin_account")
    account_name = Column(String(100), nullable=False, comment="账户名称冗余")
    account_use_type = Column(SmallInteger, nullable=False, comment="账户用途：1预售监管户 2一般经营户，监管资金仅允许原路退回")
    # 财务核算配置关联，自动生成红字冲销凭证
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID fin_project_fin_config")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="红字销项税税率模板ID fin_tax_rate")
    income_subject_id = Column(BigInteger, nullable=False, comment="冲减收入对应会计科目ID fin_subject")
    # 原始业务单据溯源（核心关联）
    source_receipt_id = Column(BigInteger, nullable=False, comment="关联原始收款单ID fin_receipt_record")
    diff_id = Column(BigInteger, comment="关联面积差价单据ID fin_price_diff，补差退费专用")
    deposit_account_id = Column(BigInteger, comment="关联认筹/定金台账ID fin_deposit_account，退认筹专用")
    installment_id = Column(BigInteger, comment="关联分期回款计划ID fin_installment_plan，分期部分退款")
    # 退款基础时间维度
    refund_apply_date = Column(DateTime, nullable=False, comment="客户退款申请日期")
    actual_refund_time = Column(DateTime, comment="银行实际出账退款完成时间")
    # 退款收款方客户银行卡信息（网银批量导出使用）
    refund_payer_name = Column(String(80), nullable=False, comment="退款收款户名（客户本人）")
    refund_bank_name = Column(String(100), nullable=False, comment="客户收款开户行")
    refund_bank_account = Column(String(50), nullable=False, comment="客户收款银行卡号（脱敏存储）")
    cnaps_code = Column(String(20), comment="客户银行卡联行号，转账报文导出")
    # 退款类型细化，覆盖全退费场景
    refund_type = Column(SmallInteger, nullable=False, comment="退款类型：1全额退房退款 2面积补差退费 3认筹金退还 4分期部分退款 5挞定余款返还 6车位/储藏室退费")
    # 标准化拆分退款金额（区分不含税本金、税费、代收费用）
    total_refund_amount = Column(Numeric(16,2), nullable=False, comment="退款总应付金额（含税+代收）")
    untax_refund_principal = Column(Numeric(16,2), nullable=False, comment="退款不含税房款本金（原refund_principal重命名）")
    refund_tax = Column(Numeric(16,2), nullable=False, comment="红字冲销增值税销项税额")
    refund_maintain = Column(Numeric(16,2), default=0, comment="同步退还代收维修基金")
    refund_other_fee = Column(Numeric(16,2), default=0, comment="同步退还工本费、印花税等其他代收费用")
    # 扣款明细：退款时扣除各类违约金、佣金
    deduct_commission = Column(Numeric(16,2), default=0, comment="扣减已结算渠道佣金")
    deduct_forfeit = Column(Numeric(16,2), default=0, comment="挞定/违约扣款金额")
    deduct_other = Column(Numeric(16,2), default=0, comment="其他杂项扣款")
    real_pay_amount = Column(Numeric(16,2), nullable=False, comment="实际最终退款金额=总退款-各项扣款")
    # 双层状态拆分：审核状态 + 资金执行状态，逻辑解耦
    audit_status = Column(SmallInteger, default=1, comment="单据审核状态：1待审核 2审核通过 3审核驳回 4作废冲销")
    refund_exec_status = Column(SmallInteger, default=1, comment="退款资金执行状态：1待发起付款 2银行处理中 3退款成功 4退款失败退回")
    # 审核、对账、凭证关联字段
    audit_time = Column(DateTime, comment="财务审核通过时间")
    audit_user_id = Column(BigInteger, comment="单据审核人sys_user ID")
    bank_flow_id = Column(BigInteger, comment="退款对应银行流水ID fin_daily_cash_account")
    bank_flow_no = Column(String(64), comment="银行流水单号冗余，快速对账")
    refund_voucher_no = Column(String(64), comment="红字冲销财务凭证编号，自动生成回填")
    # 附件与备注
    refund_file_url = Column(String(1024), comment="退款申请、退房协议、银行回单OSS附件，支持多文件")
    reconcile_remark = Column(Text, comment="银行退款失败、对账差异说明")
    remark = Column(Text, comment="退款业务备注、特殊财务处理说明")
    # 审计操作人字段
    create_user_id = Column(BigInteger, nullable=False, comment="退款单据制单人sys_user ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 统一全系统乐观锁规范，BigInteger改为Integer
    version = Column(Integer, default=0, comment="乐观锁版本号，并发编辑防数据覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常有效 1逻辑删除作废单据")
    create_time = Column(DateTime, server_default=func.now(), comment="单据创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="单据更新时间")

    __table_args__ = (
        Index("uk_tenant_refund_no", "tenant", "refund_no", "is_del", unique=True),
        Index("idx_tenant_contract", "tenant", "contract_id"),
        Index("idx_tenant_source_receipt", "tenant", "source_receipt_id"),
        Index("idx_tenant_customer", "tenant", "customer_id"),
        Index("idx_tenant_house", "tenant", "house_id"),
        Index("idx_tenant_audit_exec", "tenant", "audit_status", "refund_exec_status"),
        Index("idx_tenant_refund_date", "tenant", "refund_apply_date"),
        Index("idx_tenant_account", "tenant", "account_id"),
        Index("idx_tenant_refund_type", "tenant", "refund_type"),
        {"comment": "退款记录表：房款原路退款、退房/面积补差/认筹退费业务单据，生成红字冲销收入凭证，监管资金原路退回管控"}
    )



class FinDepositAccount(Base):
    """认筹定金台账表：管理开盘认筹金、购房担保定金，支持转首付、全额退筹、违约挞定结转收入全业务闭环"""
    __tablename__ = "fin_deposit_account"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团数据隔离")
    deposit_no = Column(String(64), nullable=False, comment="定金单据编号，租户内唯一")
    # 楼盘客户房源维度 + 冗余名称，减少报表联表查询
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID，关联sale_project")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    house_id = Column(BigInteger, comment="锁定意向房源ID，认筹可未指定房源则为空")
    house_no = Column(String(60), comment="房源房号冗余")
    customer_id = Column(BigInteger, nullable=False, comment="购房客户ID")
    customer_name = Column(String(80), nullable=False, comment="客户姓名冗余")
    # 收款账户信息
    account_id = Column(BigInteger, nullable=False, comment="收款账户ID fin_account")
    account_name = Column(String(100), nullable=False, comment="账户名称冗余")
    account_use_type = Column(SmallInteger, nullable=False, comment="账户用途：1预售监管户 2一般经营户，认筹资金优先归集监管户")
    # 财务核算配置，自动生成预收定金凭证
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID fin_project_fin_config")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="预收定金计税税率模板ID fin_tax_rate")
    deposit_subject_id = Column(BigInteger, nullable=False, comment="预收定金对应会计科目ID fin_subject")
    # 付款基础信息
    pay_time = Column(DateTime, nullable=False, comment="定金实际缴纳时间")
    pay_way = Column(SmallInteger, nullable=False, comment="支付方式：1现金 2银行卡 3微信 4支付宝 5POS 6银行转账")
    payer_name = Column(String(80), nullable=False, comment="实际付款人姓名，可与购房客户不一致")
    payer_account = Column(String(50), comment="付款人银行卡号（脱敏存储）")
    # 定金类型、标准化拆分金额（含税总额/不含税本金/税额）
    deposit_type = Column(SmallInteger, nullable=False, comment="定金类型：1可退认筹金 2不可退购房担保定金")
    deposit_total_amt = Column(Numeric(16,2), nullable=False, comment="实收定金含税总金额（原deposit_amount重命名）")
    deposit_untax_amt = Column(Numeric(16,2), nullable=False, comment="定金不含税预收本金")
    deposit_tax = Column(Numeric(16,2), nullable=False, comment="定金对应增值税销项税额")
    other_fee = Column(Numeric(16,2), default=0, comment="代收工本费等杂费，不计入预收房款")
    # 违约挞定专属字段（仅type=2购房定金生效）
    forfeit_amount = Column(Numeric(16,2), default=0, comment="客户违约没收挞定金额，结转营业外收入")
    forfeit_time = Column(DateTime, comment="挞定确认生效时间")
    forfeit_voucher_no = Column(String(64), comment="挞定结转营业外收入凭证编号")
    # 业务流转关联溯源字段
    use_status = Column(SmallInteger, default=1, comment="台账使用状态：1未使用 2已转房款抵扣首付 3已全额退还 4客户违约挞定没收 5作废台账")
    relation_contract_id = Column(BigInteger, comment="转房款后关联购房合同ID sale_contract")
    relation_receipt_id = Column(BigInteger, comment="转房款抵扣首付对应的收款单ID fin_receipt_record")
    refund_record_id = Column(BigInteger, comment="退筹/退定金关联退款单据ID fin_refund_record")
    # 资金对账与凭证关联
    bank_flow_id = Column(BigInteger, comment="对应银行资金流水ID fin_daily_cash_account")
    bank_flow_no = Column(String(64), comment="银行流水单号冗余，快速对账")
    deposit_voucher_no = Column(String(64), comment="预收定金财务凭证编号，自动回填")
    # 附件与备注
    deposit_file_url = Column(String(1024), comment="认筹收据、认购协议OSS附件链接，支持多文件")
    reconcile_remark = Column(Text, comment="对账差异、挞定处理专项说明")
    remark = Column(Text, comment="认筹/定金业务备注、特殊约定说明")
    # 审计操作人字段
    create_user_id = Column(BigInteger, nullable=False, comment="定金台账制单人sys_user ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 统一全系统乐观锁规范，BigInteger改为Integer
    version = Column(Integer, default=0, comment="乐观锁版本号，并发编辑防数据覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常有效 1逻辑删除作废台账")
    create_time = Column(DateTime, server_default=func.now(), comment="台账创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="台账更新时间")

    __table_args__ = (
        Index("uk_tenant_deposit_no", "tenant", "deposit_no", "is_del", unique=True),
        Index("idx_tenant_customer", "tenant", "customer_id"),
        Index("idx_tenant_status", "tenant", "use_status"),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_house", "tenant", "house_id"),
        Index("idx_tenant_pay_time", "tenant", "pay_time"),
        Index("idx_tenant_account", "tenant", "account_id"),
        Index("idx_tenant_deposit_type", "tenant", "deposit_type"),
        {"comment": "认筹定金台账表：管理开盘认筹金、购房担保定金，支持转首付、全额退筹、违约挞定结转收入全业务闭环"}
    )


# ==================== 票据税务合规模块 ====================

class FinInvoice(Base):
    """蓝字发票主表"""
    __tablename__ = "fin_invoice"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    invoice_no = Column(String(64), nullable=False, comment="系统开票单号")
    invoice_code = Column(String(32), nullable=False, comment="发票代码")
    invoice_num = Column(String(32), nullable=False, comment="发票号码")
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    contract_id = Column(BigInteger, nullable=False, comment="合同ID")
    house_id = Column(BigInteger, nullable=False, comment="房源ID")
    customer_id = Column(BigInteger, nullable=False, comment="客户ID")
    seller_name = Column(String(100), nullable=False, comment="销售方名称")
    seller_credit_code = Column(String(50), nullable=False, comment="销售方信用代码")
    buyer_name = Column(String(100), nullable=False, comment="购买方名称")
    buyer_credit_code = Column(String(50), comment="购买方信用代码/身份证")
    buyer_phone = Column(String(20), comment="购买方电话")
    buyer_address = Column(String(255), comment="购买方地址")
    invoice_type = Column(SmallInteger, nullable=False, comment="1专票 2普票")
    invoice_amount = Column(Numeric(16,2), nullable=False, comment="含税总金额")
    tax_amount = Column(Numeric(16,2), nullable=False, comment="税额")
    ex_tax_amount = Column(Numeric(16,2), nullable=False, comment="不含税金额")
    tax_rate = Column(Numeric(5,4), nullable=False, comment="开票税率")
    invoice_item = Column(String(100), nullable=False, comment="开票商品名称")
    invoice_status = Column(SmallInteger, default=1, comment="1正常 2已红冲 3作废 4异常")
    red_count = Column(SmallInteger, default=0, comment="已红冲次数")
    invoice_time = Column(DateTime, nullable=False, comment="开票时间")
    make_user_id = Column(BigInteger, nullable=False, comment="开票操作员ID")
    invoice_file_url = Column(String(255), comment="电子发票链接")
    remark = Column(Text, comment="开票备注")
    version = Column(BigInteger, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index("uk_tenant_invoice_code_num", "tenant", "invoice_code", "invoice_num", "is_del", unique=True),
        Index("uk_tenant_invoice_no", "tenant", "invoice_no", "is_del", unique=True),
        Index("idx_tenant_contract", "tenant", "contract_id"),
        {"comment": "蓝字发票主表"}
    )


class FinInvoiceRed(Base):
    """红字冲销发票表"""
    __tablename__ = "fin_invoice_red"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    red_invoice_no = Column(String(64), nullable=False, comment="红字开票单号")
    source_invoice_id = Column(BigInteger, nullable=False, comment="关联蓝字发票ID")
    invoice_code = Column(String(32), nullable=False, comment="红字发票代码")
    invoice_num = Column(String(32), nullable=False, comment="红字发票号码")
    red_invoice_time = Column(DateTime, nullable=False, comment="红冲开票时间")
    red_amount = Column(Numeric(16,2), nullable=False, comment="红冲含税金额")
    red_tax = Column(Numeric(16,2), nullable=False, comment="红冲税额")
    red_reason = Column(SmallInteger, nullable=False, comment="1开票错误 2退房退款 3金额调整 4其他")
    remark = Column(Text, nullable=False, comment="红冲详细原因")
    red_file_url = Column(String(255), comment="红字发票附件")
    make_user_id = Column(BigInteger, nullable=False, comment="操作人ID")
    version = Column(BigInteger, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index("uk_tenant_red_no", "tenant", "red_invoice_no", "is_del", unique=True),
        Index("idx_tenant_source_invoice", "tenant", "source_invoice_id"),
        {"comment": "红字冲销发票表"}
    )


class FinReceipt(Base):
    """内部收据表"""
    __tablename__ = "fin_receipt"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    receipt_no = Column(String(64), nullable=False, comment="收据编号")
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    customer_id = Column(BigInteger, comment="客户ID")
    receipt_type = Column(SmallInteger, nullable=False, comment="收据类型")
    receipt_amount = Column(Numeric(16,2), nullable=False, comment="收据金额")
    receipt_content = Column(String(255), nullable=False, comment="收费内容")
    receipt_status = Column(SmallInteger, default=1, comment="1正常 2已换发票 3已作废")
    receipt_time = Column(DateTime, nullable=False, comment="开据时间")
    make_user_id = Column(BigInteger, nullable=False, comment="开据人ID")
    receipt_file_url = Column(String(255), comment="收据附件链接")
    remark = Column(Text, comment="备注")
    version = Column(BigInteger, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index("uk_tenant_receipt_no", "tenant", "receipt_no", "is_del", unique=True),
        {"comment": "内部收据表"}
    )


class FinMaintainFund(Base):
    """维修基金台账表"""
    __tablename__ = "fin_maintain_fund"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    fund_no = Column(String(64), nullable=False, comment="维修基金单据编号")
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    house_id = Column(BigInteger, nullable=False, comment="房源ID")
    contract_id = Column(BigInteger, nullable=False, comment="合同ID")
    customer_id = Column(BigInteger, nullable=False, comment="客户ID")
    fund_amount = Column(Numeric(16,2), nullable=False, comment="维修基金金额")
    pay_status = Column(SmallInteger, default=1, comment="1待缴 2已缴 3已上缴")
    pay_time = Column(DateTime, comment="缴纳时间")
    pay_way = Column(SmallInteger, comment="支付方式")
    transfer_time = Column(DateTime, comment="上缴房管部门时间")
    remark = Column(Text, comment="备注")
    version = Column(BigInteger, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index("uk_tenant_fund_no", "tenant", "fund_no", "is_del", unique=True),
        Index("idx_tenant_house", "tenant", "house_id"),
        {"comment": "维修基金台账表"}
    )


class FinTaxDeclare(Base):
    """税务申报表"""
    __tablename__ = "fin_tax_declare"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    declare_no = Column(String(64), nullable=False, comment="申报单据编号")
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    declare_year = Column(BigInteger, nullable=False, comment="申报年份")
    declare_month = Column(SmallInteger, nullable=False, comment="申报月份")
    declare_quarter = Column(SmallInteger, comment="申报季度")
    total_invoice_amount = Column(Numeric(18,2), default=0, comment="本期开票总金额")
    total_tax_amount = Column(Numeric(18,2), default=0, comment="本期计税总金额")
    vat_amount = Column(Numeric(18,2), default=0, comment="增值税总额")
    additional_tax_amount = Column(Numeric(18,2), default=0, comment="附加税总额")
    stamp_tax_amount = Column(Numeric(18,2), default=0, comment="印花税总额")
    declare_status = Column(SmallInteger, default=1, comment="1待生成 2已生成 3已申报 4已作废")
    declare_time = Column(DateTime, comment="实际申报时间")
    declare_user_id = Column(BigInteger, comment="申报人ID")
    declare_file_url = Column(String(255), comment="申报表附件")
    remark = Column(Text, comment="申报备注")
    version = Column(BigInteger, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index("uk_tenant_declare_no", "tenant", "declare_no", "is_del", unique=True),
        Index("uk_tenant_project_period", "tenant", "project_id", "declare_year", "declare_month", "is_del", unique=True),
        {"comment": "税务申报表"}
    )


# ==================== 渠道佣金&内部提成支付模块 ====================



class FinCommissionPay(Base):
    """渠道佣金付款单：分销渠道月度汇总应付佣金付款头单"""
    __tablename__ = "fin_commission_pay"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团隔离")
    pay_no = Column(String(64), nullable=False, comment="佣金付款单号，租户唯一")
    # 楼盘维度+冗余名称
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    building_scope = Column(String(512), comment="本次结算覆盖楼栋ID，逗号分隔，报表筛选使用")
    # 渠道维度
    channel_id = Column(BigInteger, nullable=False, comment="分销渠道ID")
    channel_name = Column(String(100), nullable=False, comment="渠道名称冗余")
    bank_info_id = Column(BigInteger, nullable=False, comment="渠道对公收款账户ID fin_bank_info")
    # 财务核算配置
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID")
    cost_subject_id = Column(BigInteger, nullable=False, comment="营销费用成本科目ID fin_subject")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="渠道服务费进项税率模板ID fin_tax_rate")
    pay_account_id = Column(BigInteger, nullable=False, comment="我方付款账户ID fin_account")
    # 结算周期（补充起止日期替代纯字符串）
    settle_cycle = Column(String(32), nullable=False, comment="结算周期文本，如2026-06")
    settle_start = Column(Date, nullable=False, comment="结算周期起始日")
    settle_end = Column(Date, nullable=False, comment="结算周期截止日")
    settle_type = Column(SmallInteger, nullable=False, comment="1按月结算 2按回款结算")
    refund_deduct_flag = Column(SmallInteger, default=0, comment="0不含退房扣佣 1包含退房扣减佣金")
    # 标准化佣金金额拆分
    total_commission_untax = Column(Numeric(16,2), nullable=False, comment="应付佣金不含税总额")
    total_commission_tax = Column(Numeric(16,2), nullable=False, comment="渠道服务费进项税额")
    total_commission = Column(Numeric(16,2), nullable=False, comment="应付佣金含税总金额")
    deduct_amount = Column(Numeric(16,2), default=0, comment="退房/违规扣减含税总额")
    actual_pay_untax = Column(Numeric(16,2), nullable=False, comment="实付不含税佣金")
    actual_pay_tax = Column(Numeric(16,2), nullable=False, comment="实付对应进项税额")
    actual_pay_amount = Column(Numeric(16,2), nullable=False, comment="实际含税应付付款金额")
    # 审核+付款双状态解耦
    audit_status = Column(SmallInteger, default=1, comment="1待审核 2已通过 3已驳回 4作废")
    pay_status = Column(SmallInteger, default=1, comment="1待付款 2付款中 3付款完成 4付款失败退回")
    pay_time = Column(DateTime, comment="银行实际付款出账时间")
    # 操作人审计
    create_user_id = Column(BigInteger, nullable=False, comment="结算制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    audit_user_id = Column(BigInteger, comment="财务审核人ID")
    pay_user_id = Column(BigInteger, comment="出纳付款操作人ID")
    # 资金&凭证溯源
    bank_flow_id = Column(BigInteger, comment="付款对应银行流水ID fin_daily_cash_account")
    bank_flow_no = Column(String(64), comment="银行流水单号冗余")
    voucher_no = Column(String(64), comment="营销费用财务凭证编号")
    # 附件与备注
    pay_file_url = Column(String(1024), comment="结算单、银行代发明细OSS附件")
    remark = Column(Text, comment="渠道佣金结算备注、扣佣说明")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号，并发防覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除作废单据")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_pay_no", "tenant", "pay_no", "is_del", unique=True),
        Index("idx_tenant_channel", "tenant", "channel_id"),
        Index("idx_tenant_cycle_date", "tenant", "settle_start", "settle_end"),
        Index("idx_tenant_audit_pay", "tenant", "audit_status", "pay_status"),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_pay_account", "tenant", "pay_account_id"),
        {"comment": "渠道佣金付款单：分销渠道月度汇总应付佣金付款头单"}
    )


class FinCommissionDeduct(Base):
    """佣金扣罚记录表：单套合同退房/违规产生的佣金扣减明细，必须绑定房源、合同、楼栋"""
    __tablename__ = "fin_commission_deduct"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    deduct_no = Column(String(64), nullable=False, comment="扣罚单号，租户唯一")
    # 楼盘楼栋房源合同核心维度（生产报表必备）
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    building_id = Column(BigInteger, nullable=False, comment="楼栋ID，成本分摊核心维度")
    building_name = Column(String(60), nullable=False, comment="楼栋名称冗余")
    house_id = Column(BigInteger, nullable=False, comment="房源ID")
    house_no = Column(String(60), nullable=False, comment="房号冗余")
    contract_id = Column(BigInteger, nullable=False, comment="对应退房购房合同ID")
    sales_user_id = Column(BigInteger, nullable=False, comment="成交置业顾问员工ID")
    sales_user_name = Column(String(80), nullable=False, comment="置业顾问姓名冗余")
    # 渠道与汇总付款单关联
    channel_id = Column(BigInteger, nullable=False, comment="分销渠道ID")
    channel_name = Column(String(100), nullable=False, comment="渠道名称冗余")
    commission_pay_id = Column(BigInteger, comment="归属佣金汇总付款单ID FinCommissionPay")
    # 扣罚业务溯源
    deduct_type = Column(SmallInteger, nullable=False, comment="扣罚类型：1客户退房 2业绩不达标 3渠道违规罚款")
    relate_biz_type = Column(SmallInteger, nullable=False, default=1, comment="关联单据类型：1购房合同 2认购单")
    relate_biz_id = Column(BigInteger, nullable=False, comment="关联业务单据ID（合同/认购单）")
    # 扣罚金额拆分
    deduct_untax_amt = Column(Numeric(16,2), nullable=False, comment="扣罚不含税佣金金额")
    deduct_tax_amt = Column(Numeric(16,2), nullable=False, comment="对应进项税额转出金额")
    deduct_amount = Column(Numeric(16,2), nullable=False, comment="扣罚含税总金额")
    deduct_status = Column(SmallInteger, default=1, comment="1待确认 2已确认抵扣佣金付款单")
    # 审计操作人
    create_user_id = Column(BigInteger, nullable=False, comment="扣罚记录制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    remark = Column(Text, comment="扣罚详细原因、退房时间说明")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_deduct_no", "tenant", "deduct_no", "is_del", unique=True),
        Index("idx_tenant_channel", "tenant", "channel_id"),
        Index("idx_tenant_contract", "tenant", "contract_id"),
        Index("idx_tenant_building", "tenant", "building_id"),
        Index("idx_tenant_sales", "tenant", "sales_user_id"),
        Index("idx_tenant_pay_rel", "tenant", "commission_pay_id"),
        {"comment": "佣金扣罚记录表：单套合同退房/违规产生的佣金扣减明细，绑定房源、合同、楼栋"}
    )


class FinSalesCommission(Base):
    """销售提成支付明细：单套房源置业顾问提成底层计算明细，强制楼栋/合同/销售维度"""
    __tablename__ = "fin_sales_commission"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    # 楼盘楼栋房源合同核心维度（生产必备）
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    building_id = Column(BigInteger, nullable=False, comment="楼栋ID，营销费用分摊维度")
    building_name = Column(String(60), nullable=False, comment="楼栋名称冗余")
    house_id = Column(BigInteger, nullable=False, comment="房源ID")
    house_no = Column(String(60), nullable=False, comment="房号冗余")
    contract_id = Column(BigInteger, nullable=False, comment="购房合同ID")
    order_id = Column(BigInteger, nullable=False, comment="认购订单ID")
    # 置业顾问员工维度
    employee_id = Column(BigInteger, nullable=False, comment="成交销售员工ID")
    employee_name = Column(String(80), nullable=False, comment="销售姓名冗余")
    # 财务核算配置
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID")
    cost_subject_id = Column(BigInteger, nullable=False, comment="销售提成费用科目ID fin_subject")
    # 提成金额拆分
    commission_untax = Column(Numeric(16,2), nullable=False, comment="提成不含税金额")
    commission_tax = Column(Numeric(16,2), nullable=False, default=0, comment="提成对应个税/服务费税额")
    commission_amount = Column(Numeric(16,2), nullable=False, comment="提成含税总金额")
    # 结算付款关联
    bonus_pay_id = Column(BigInteger, comment="归属月度提成汇总付款单ID FinSalesBonusPay")
    commission_status = Column(SmallInteger, default=1, comment="1待结算 2已汇总至付款单 3已完成代发支付")
    settle_time = Column(DateTime, comment="提成汇总结算时间")
    pay_time = Column(DateTime, comment="银行代发实际支付时间")
    # 审计操作人
    create_user_id = Column(BigInteger, nullable=False, comment="提成计算制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    remark = Column(Text, comment="提成计算规则、特殊折扣备注")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除作废提成记录")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("idx_tenant_order", "tenant", "order_id"),
        Index("idx_tenant_employee", "tenant", "employee_id"),
        Index("idx_tenant_contract", "tenant", "contract_id"),
        Index("idx_tenant_building", "tenant", "building_id"),
        Index("idx_tenant_bonus_pay", "tenant", "bonus_pay_id"),
        Index("idx_tenant_status", "tenant", "commission_status"),
        {"comment": "销售提成支付明细：单套房源置业顾问提成底层计算明细，含楼栋、合同、销售完整维度"}
    )


class FinSalesBonusPay(Base):
    """内部销售提成付款单：员工月度提成汇总代发头单"""
    __tablename__ = "fin_sales_bonus_pay"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    pay_no = Column(String(64), nullable=False, comment="提成付款单号，租户唯一")
    # 楼盘维度
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    building_scope = Column(String(512), comment="本次代发覆盖楼栋ID，逗号分隔")
    # 员工维度
    staff_id = Column(BigInteger, nullable=False, comment="销售员工ID")
    staff_name = Column(String(80), nullable=False, comment="员工姓名冗余")
    # 财务核算配置
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID")
    cost_subject_id = Column(BigInteger, nullable=False, comment="销售提成费用科目ID fin_subject")
    pay_account_id = Column(BigInteger, nullable=False, comment="我方代发付款账户ID fin_account")
    # 结算周期标准化
    settle_cycle = Column(String(32), nullable=False, comment="结算周期文本，如2026-06")
    settle_start = Column(Date, nullable=False, comment="结算周期起始日")
    settle_end = Column(Date, nullable=False, comment="结算周期截止日")
    # 提成金额拆分
    total_bonus_untax = Column(Numeric(16,2), nullable=False, comment="应付提成不含税总额")
    total_bonus_tax = Column(Numeric(16,2), nullable=False, comment="代扣个人所得税总额")
    total_bonus = Column(Numeric(16,2), nullable=False, comment="应付提成含税总额")
    deduct_amount = Column(Numeric(16,2), default=0, comment="扣款（迟到/违规）含税总额")
    actual_pay_untax = Column(Numeric(16,2), nullable=False, comment="实发不含税提成")
    actual_pay_tax = Column(Numeric(16,2), nullable=False, comment="实发对应代扣个税")
    actual_pay_amount = Column(Numeric(16,2), nullable=False, comment="银行代发实际净额")
    # 审核+付款双状态
    audit_status = Column(SmallInteger, default=1, comment="1待审核 2已通过 3已驳回 4作废")
    pay_status = Column(SmallInteger, default=1, comment="1待代发 2付款中 3代发完成 4代发失败退回")
    pay_time = Column(DateTime, comment="银行代发完成时间")
    # 操作人审计
    create_user_id = Column(BigInteger, nullable=False, comment="提成汇总制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    audit_user_id = Column(BigInteger, comment="财务审核人ID")
    pay_user_id = Column(BigInteger, comment="出纳代发操作人ID")
    # 资金凭证溯源
    bank_flow_id = Column(BigInteger, comment="代发对应银行流水ID")
    bank_flow_no = Column(String(64), comment="银行流水单号冗余")
    voucher_no = Column(String(64), comment="销售费用财务凭证编号")
    # 备注
    remark = Column(Text, comment="月度提成代发备注、扣款说明")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除作废单据")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_sales_bonus_no", "tenant", "pay_no", "is_del", unique=True),
        Index("idx_tenant_staff", "tenant", "staff_id"),
        Index("idx_tenant_cycle_date", "tenant", "settle_start", "settle_end"),
        Index("idx_tenant_audit_pay", "tenant", "audit_status", "pay_status"),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_pay_account", "tenant", "pay_account_id"),
        {"comment": "内部销售提成付款单：员工月度提成汇总银行代发头单"}
    )

# ==================== 项目成本&运营费用模块 ====================


class FinCostExpense(Base):
    """通用费用申请表【事前审批】：办公/差旅/营销零星支出事前预算申请，无发票，先批后花"""
    __tablename__ = "fin_cost_expense"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团隔离")
    expense_no = Column(String(64), nullable=False, comment="费用申请单号，租户唯一")
    # 楼盘楼栋分摊维度
    project_id = Column(BigInteger, comment="归属楼盘ID，集团行政费用可空")
    project_name = Column(String(128), comment="楼盘名称冗余")
    building_id = Column(BigInteger, comment="分摊楼栋ID，多楼栋逗号分隔存入扩展字段")
    building_name = Column(String(512), comment="分摊楼栋名称冗余")
    # 申请人信息
    apply_user_id = Column(BigInteger, nullable=False, comment="申请人员工ID")
    apply_user_name = Column(String(80), nullable=False, comment="申请人姓名冗余")
    dept_id = Column(BigInteger, comment="申请人部门ID，部门费用统计")
    # 财务核算配置
    project_fin_config_id = Column(BigInteger, comment="楼盘财务配置ID fin_project_fin_config")
    expense_subject_id = Column(BigInteger, nullable=False, comment="费用归属会计科目ID fin_subject")
    tax_tpl_id = Column(BigInteger, comment="预计进项税率模板ID fin_tax_rate")
    # 费用基础信息
    expense_type = Column(SmallInteger, nullable=False, comment="费用类型：1办公费 2差旅费 3业务招待 4营销杂费 5行政水电")
    apply_time = Column(DateTime, nullable=False, comment="申请提交时间")
    expense_start_date = Column(Date, nullable=False, comment="费用发生起始日期")
    expense_end_date = Column(Date, nullable=False, comment="费用发生截止日期")
    # 标准化拆分金额
    total_amount = Column(Numeric(16,2), nullable=False, comment="申请含税总金额")
    untax_amount = Column(Numeric(16,2), nullable=False, comment="申请不含税成本金额")
    tax_amount = Column(Numeric(16,2), nullable=False, default=0, comment="预计可抵扣进项税额")
    # 业务关联：事后报销单关联ID
    reimburse_id = Column(BigInteger, comment="核销后关联报销单ID FinExpenseReimbursement")
    # 审批流程状态细化
    audit_status = Column(SmallInteger, default=1, comment="1待审核 2已通过 3已驳回 4作废取消")
    audit_user_id = Column(BigInteger, comment="审批人sys_user ID")
    audit_time = Column(DateTime, comment="审批完成时间")
    # 附件与备注
    expense_file_url = Column(String(1024), comment="申请预算说明、报价单附件OSS链接")
    remark = Column(Text, comment="费用用途、分摊楼栋说明")
    # 审计操作人
    create_user_id = Column(BigInteger, nullable=False, comment="单据制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号，并发防覆盖")
    is_del = Column(SmallInteger, default=0, comment="0正常有效 1逻辑删除作废单据")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_expense_no", "tenant", "expense_no", "is_del", unique=True),
        Index("idx_tenant_apply_user", "tenant", "apply_user_id"),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_audit_status", "tenant", "audit_status"),
        Index("idx_tenant_expense_date", "tenant", "expense_start_date", "expense_end_date"),
        {"comment": "通用费用申请表【事前审批】：办公/差旅/营销零星支出事前预算申请，无发票，先批后花"}
    )


class FinExpenseReimbursement(Base):
    """费用报销单【事后核销】：员工凭发票报销，关联事前申请，承载进项税、成本楼栋分摊"""
    __tablename__ = "fin_expense_reimbursement"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    reimburse_no = Column(String(64), nullable=False, comment="报销单号，租户唯一")
    # 楼盘楼栋分摊维度
    project_id = Column(BigInteger, comment="归属楼盘ID，集团行政费用可空")
    project_name = Column(String(128), comment="楼盘名称冗余")
    building_id = Column(BigInteger, comment="分摊楼栋ID")
    building_name = Column(String(512), comment="分摊楼栋名称冗余")
    # 报销人信息
    employee_id = Column(BigInteger, nullable=False, comment="报销员工ID")
    employee_name = Column(String(80), nullable=False, comment="报销人姓名冗余")
    dept_id = Column(BigInteger, comment="报销人部门ID")
    # 关联事前申请单
    cost_expense_id = Column(BigInteger, comment="关联事前费用申请单ID FinCostExpense")
    # 财务核算配置
    project_fin_config_id = Column(BigInteger, comment="楼盘财务配置ID")
    expense_subject_id = Column(BigInteger, nullable=False, comment="费用会计科目ID fin_subject")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="发票进项税率模板ID fin_tax_rate")
    # 报销基础信息
    expense_type = Column(SmallInteger, nullable=False, comment="费用类型：1办公费 2差旅费 3业务招待 4营销杂费 5行政水电")
    reimburse_date = Column(Date, nullable=False, comment="费用实际发生日期")
    invoice_no = Column(String(256), comment="增值税发票号码，多张逗号分隔")
    invoice_date = Column(Date, comment="发票开具日期")
    # 标准化拆分报销金额
    total_amount = Column(Numeric(16,2), nullable=False, comment="报销含税总金额（发票价税合计）")
    untax_amount = Column(Numeric(16,2), nullable=False, comment="报销不含税入账成本")
    tax_amount = Column(Numeric(16,2), nullable=False, default=0, comment="可抵扣增值税进项税额")
    deduct_amount = Column(Numeric(16,2), default=0, comment="不予抵扣/个人扣款金额")
    actual_reimburse_amount = Column(Numeric(16,2), nullable=False, comment="实际应报销净额")
    # 资金&付款关联
    cost_pay_id = Column(BigInteger, comment="核销后关联费用付款单ID FinCostPay")
    voucher_no = Column(String(64), comment="费用报销财务凭证编号")
    # 审批状态细化
    audit_status = Column(SmallInteger, default=1, comment="1待审核 2已通过待付款 3已驳回 4作废红冲")
    audit_user_id = Column(BigInteger, comment="财务审核人ID")
    audit_time = Column(DateTime, comment="审核完成时间")
    # 附件与备注
    reimburse_file_url = Column(String(1024), comment="发票、行程单、消费凭证多附件链接")
    remark = Column(Text, comment="费用用途、楼栋分摊、发票特殊说明")
    # 审计操作人
    create_user_id = Column(BigInteger, nullable=False, comment="报销单制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除作废单据")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_reimburse_no", "tenant", "reimburse_no", "is_del", unique=True),
        Index("idx_tenant_employee", "tenant", "employee_id"),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_audit_status", "tenant", "audit_status"),
        Index("idx_tenant_cost_exp_rel", "tenant", "cost_expense_id"),
        Index("idx_tenant_pay_rel", "tenant", "cost_pay_id"),
        {"comment": "费用报销单【事后核销】：员工凭发票报销，关联事前申请，承载进项税、成本楼栋分摊"}
    )


class FinCostPay(Base):
    """费用付款单【资金执行层】：统一对公/对私付款载体，一对多关联多条报销/费用申请"""
    __tablename__ = "fin_cost_pay"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    pay_no = Column(String(64), nullable=False, comment="付款单号，租户唯一")
    # 楼盘维度
    project_id = Column(BigInteger, comment="归属楼盘ID，集团行政费用可空")
    project_name = Column(String(128), comment="楼盘名称冗余")
    building_scope = Column(String(512), comment="本次付款分摊楼栋ID，逗号分隔")
    # 付款账户（我方资金账户）
    account_id = Column(BigInteger, nullable=False, comment="我方付款账户ID fin_account")
    account_name = Column(String(100), nullable=False, comment="账户名称冗余")
    # 财务核算配置
    project_fin_config_id = Column(BigInteger, comment="楼盘财务配置ID")
    cost_subject_id = Column(BigInteger, nullable=False, comment="费用付款对应总账科目ID fin_subject")
    # 上游单据汇总关联（一对多，存储逗号分隔ID，明细单独中间表）
    reimburse_ids = Column(String(1024), comment="批量付款关联报销单ID集合")
    expense_ids = Column(String(1024), comment="批量付款关联费用申请单ID集合")
    ad_cost_ids = Column(String(1024), comment="批量付款关联广告成本ID集合")
    eng_cost_ids = Column(String(1024), comment="批量付款关联工程成本ID集合")
    # 付款金额拆分
    total_pay_untax = Column(Numeric(16,2), nullable=False, comment="本次付款不含税总成本汇总")
    total_pay_tax = Column(Numeric(16,2), nullable=False, default=0, comment="本次付款进项税总额汇总")
    total_pay_amount = Column(Numeric(16,2), nullable=False, comment="应付含税付款总额")
    deduct_total = Column(Numeric(16,2), default=0, comment="扣款合计金额")
    pay_amount = Column(Numeric(16,2), nullable=False, comment="银行实际出账净额")
    # 收款方信息（区分员工报销/供应商对公）
    pay_target_type = Column(SmallInteger, nullable=False, comment="1内部员工报销 2外部供应商对公付款")
    target_name = Column(String(100), nullable=False, comment="收款户名（员工/供应商）")
    target_bank_info_id = Column(BigInteger, comment="外部供应商对公账户ID fin_bank_info，员工报销为空")
    target_bank_card = Column(String(50), comment="员工报销收款银行卡（脱敏）")
    # 付款执行状态双层解耦
    audit_status = Column(SmallInteger, default=1, comment="单据审核：1待审 2通过 3驳回 4作废")
    pay_status = Column(SmallInteger, default=1, comment="资金执行：1待付款 2付款中 3付款完成 4付款失败退回")
    pay_time = Column(DateTime, comment="银行实际出账时间")
    pay_user_id = Column(BigInteger, comment="出纳付款操作人ID")
    audit_user_id = Column(BigInteger, comment="财务审核人ID")
    # 资金与凭证溯源
    bank_flow_id = Column(BigInteger, comment="对应银行资金流水ID fin_daily_cash_account")
    bank_flow_no = Column(String(64), comment="银行流水单号冗余，快速对账")
    voucher_no = Column(String(64), comment="费用付款财务凭证编号")
    # 附件与备注
    pay_file_url = Column(String(1024), comment="付款审批单、网银回单、批量代发明细附件")
    remark = Column(Text, comment="批量付款汇总说明、付款失败原因备注")
    # 审计操作人
    create_user_id = Column(BigInteger, nullable=False, comment="付款单制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除作废单据")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_cost_pay_no", "tenant", "pay_no", "is_del", unique=True),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_account", "tenant", "account_id"),
        Index("idx_tenant_audit_pay", "tenant", "audit_status", "pay_status"),
        Index("idx_tenant_pay_target", "tenant", "pay_target_type"),
        {"comment": "费用付款单【资金执行层】：统一对公/对私付款载体，一对多关联多条报销/费用申请/专项成本"}
    )


class FinAdCost(Base):
    """广告推广成本专项台账：营销广告投放明细，营销费用底层成本源，土增营销费用分摊依据"""
    __tablename__ = "fin_ad_cost"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    cost_no = Column(String(64), nullable=False, comment="广告成本单号，租户唯一")
    # 楼盘楼栋分摊核心维度
    project_id = Column(BigInteger, nullable=False, comment="归属楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    building_id = Column(BigInteger, comment="分摊楼栋ID，多楼栋逗号分隔")
    building_name = Column(String(512), comment="分摊楼栋名称冗余")
    # 供应商信息（广告服务商）
    supplier_id = Column(BigInteger, nullable=False, comment="广告渠道供应商ID")
    supplier_name = Column(String(100), nullable=False, comment="供应商名称冗余")
    bank_info_id = Column(BigInteger, comment="供应商对公收款账户ID fin_bank_info")
    # 财务核算配置
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID")
    cost_subject_id = Column(BigInteger, nullable=False, comment="营销费用会计科目ID fin_subject")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="广告服务进项税率模板ID fin_tax_rate")
    # 广告投放业务信息
    ad_type = Column(SmallInteger, nullable=False, comment="广告类型：1线上媒体 2线下活动 3户外大牌 4分销推广")
    ad_channel = Column(String(100), comment="投放渠道名称")
    ad_contract_id = Column(BigInteger, comment="广告合作合同ID")
    ad_start_date = Column(Date, nullable=False, comment="广告投放起始日期")
    ad_end_date = Column(Date, nullable=False, comment="广告投放结束日期")
    cost_date = Column(Date, nullable=False, comment="成本入账归属日期")
    invoice_no = Column(String(256), comment="广告服务费发票号码")
    invoice_date = Column(Date, comment="发票开具日期")
    # 标准化拆分广告成本金额
    total_amount = Column(Numeric(16,2), nullable=False, comment="广告含税总金额")
    untax_amount = Column(Numeric(16,2), nullable=False, comment="广告不含税营销成本")
    tax_amount = Column(Numeric(16,2), nullable=False, default=0, comment="可抵扣进项税额")
    deduct_amount = Column(Numeric(16,2), default=0, comment="扣款、违约金金额")
    actual_cost_amount = Column(Numeric(16,2), nullable=False, comment="应付实际成本净额")
    # 核销&付款关联
    cost_status = Column(SmallInteger, default=1, comment="1待核销 2已核销待付款 3已付款结清 4作废")
    relate_pay_id = Column(BigInteger, comment="核销后关联费用付款单ID FinCostPay")
    voucher_no = Column(String(64), comment="广告成本财务凭证编号")
    # 附件与备注
    ad_file_url = Column(String(1024), comment="广告合同、投放排期、发票、验收单附件")
    remark = Column(Text, comment="投放内容、楼栋分摊比例、结算特殊约定")
    # 审计操作人
    create_user_id = Column(BigInteger, nullable=False, comment="广告成本录入制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除作废成本记录")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_ad_cost_no", "tenant", "cost_no", "is_del", unique=True),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_supplier", "tenant", "supplier_id"),
        Index("idx_tenant_cost_status", "tenant", "cost_status"),
        Index("idx_tenant_ad_date", "tenant", "ad_start_date", "ad_end_date"),
        Index("idx_tenant_pay_rel", "tenant", "relate_pay_id"),
        {"comment": "广告推广成本专项台账：营销广告投放明细，营销费用底层成本源，土增营销费用分摊依据"}
    )


class FinProjectEngCost(Base):
    """工程建设成本专项台账：土建/园林/配套工程资本化成本，土地增值税清算核心台账"""
    __tablename__ = "fin_project_eng_cost"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    cost_no = Column(String(64), nullable=False, comment="工程成本单号，租户唯一")
    # 楼盘楼栋分摊维度（土增清算核心）
    project_id = Column(BigInteger, nullable=False, comment="归属楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    building_id = Column(BigInteger, nullable=False, comment="分摊楼栋ID，单条工程可分摊多楼栋")
    building_name = Column(String(512), nullable=False, comment="分摊楼栋名称冗余")
    # 施工供应商信息
    supplier_id = Column(BigInteger, nullable=False, comment="施工单位供应商ID")
    supplier_name = Column(String(100), nullable=False, comment="施工单位名称冗余")
    bank_info_id = Column(BigInteger, comment="施工方对公收款账户ID fin_bank_info")
    # 财务核算配置（资本化开发成本）
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID")
    cost_subject_id = Column(BigInteger, nullable=False, comment="资本化开发成本科目ID fin_subject")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="工程建安进项税率模板ID fin_tax_rate")
    # 工程核心业务信息
    eng_type = Column(SmallInteger, nullable=False, comment="工程类型：1土建总包 2园林景观 3配套道路管网 4水电安装 5监理设计")
    eng_name = Column(String(100), nullable=False, comment="分项工程名称")
    eng_contract_id = Column(BigInteger, nullable=False, comment="工程施工合同ID")
    settle_cycle = Column(String(32), nullable=False, comment="本期结算周期，如2026-06")
    settle_start = Column(Date, nullable=False, comment="结算周期起始日")
    settle_end = Column(Date, nullable=False, comment="结算周期截止日")
    cost_date = Column(Date, nullable=False, comment="成本资本化入账日期")
    invoice_no = Column(String(256), comment="建安工程款增值税发票号码")
    invoice_date = Column(Date, comment="发票开具日期")
    # 标准化拆分工程成本金额
    total_amount = Column(Numeric(16,2), nullable=False, comment="本期结算含税工程款总额")
    untax_amount = Column(Numeric(16,2), nullable=False, comment="资本化不含税开发成本（土增清算基数）")
    tax_amount = Column(Numeric(16,2), nullable=False, default=0, comment="建安进项可抵扣税额")
    deduct_amount = Column(Numeric(16,2), default=0, comment="质保金、违约金扣款金额")
    actual_cost_amount = Column(Numeric(16,2), nullable=False, comment="本期应付工程净额")
    # 核销付款关联
    cost_status = Column(SmallInteger, default=1, comment="1待核销 2已核销待付款 3已付款结清 4作废红冲")
    relate_pay_id = Column(BigInteger, comment="核销后关联费用付款单ID FinCostPay")
    voucher_no = Column(String(64), comment="开发成本资本化财务凭证编号")
    # 附件与备注
    eng_file_url = Column(String(1024), comment="工程合同、结算单、验收单、工程款发票附件")
    remark = Column(Text, comment="工程内容、楼栋成本分摊比例、质保金约定说明")
    # 审计操作人
    create_user_id = Column(BigInteger, nullable=False, comment="工程成本录入制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除作废结算记录")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_eng_cost_no", "tenant", "cost_no", "is_del", unique=True),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_building", "tenant", "building_id"),
        Index("idx_tenant_supplier", "tenant", "supplier_id"),
        Index("idx_tenant_cost_status", "tenant", "cost_status"),
        Index("idx_tenant_settle_cycle", "tenant", "settle_start", "settle_end"),
        Index("idx_tenant_pay_rel", "tenant", "relate_pay_id"),
        {"comment": "工程建设成本专项台账：土建/园林/配套工程资本化成本，土地增值税清算核心台账"}
    )



# ==================== 应收应付往来台账模块 ====================


class FinAccountReceivable(Base):
    """客户应收台账表：购房合同房款应收总账，单房源单合同唯一，支撑账龄、逾期、回款结清统计"""
    __tablename__ = "fin_account_receivable"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团数据隔离")
    # 核心楼盘楼栋房源维度（土增清算分摊必备）
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    building_id = Column(BigInteger, nullable=False, comment="楼栋ID，成本分摊核心维度")
    building_name = Column(String(60), nullable=False, comment="楼栋名称冗余")
    house_id = Column(BigInteger, nullable=False, comment="房源ID")
    house_no = Column(String(60), nullable=False, comment="房源房号冗余")
    contract_id = Column(BigInteger, nullable=False, comment="购房合同ID")
    # 客户维度冗余
    customer_id = Column(BigInteger, nullable=False, comment="客户ID")
    customer_name = Column(String(80), nullable=False, comment="客户姓名冗余")
    customer_phone = Column(String(20), comment="客户手机号冗余")
    # 财务核算配置（自动生成应收凭证）
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="房款销项税率模板ID")
    receivable_subject_id = Column(BigInteger, nullable=False, comment="应收账款会计科目ID")
    # 账期&逾期风控字段
    first_receivable_date = Column(Date, nullable=False, comment="首期应收账期起始日")
    last_receivable_date = Column(Date, nullable=False, comment="尾款应收截止日")
    overdue_date = Column(Date, comment="逾期起始日期")
    max_overdue_days = Column(Integer, default=0, comment="当前最大逾期天数")
    # 标准化应收金额拆分（完全对齐财务计税口径）
    total_receivable = Column(Numeric(16,2), nullable=False, comment="应收含税总金额")
    principal_receivable = Column(Numeric(16,2), nullable=False, comment="应收不含税房款本金")
    tax_receivable = Column(Numeric(16,2), nullable=False, comment="应收增值税销项税额")
    total_received = Column(Numeric(16,2), default=0, comment="累计已收含税金额")
    total_unpaid = Column(Numeric(16,2), nullable=False, comment="剩余未收含税金额")
    overdue_amount = Column(Numeric(16,2), default=0, comment="当前逾期未收金额")
    # 罚息&违约金
    overdue_interest = Column(Numeric(16,2), default=0, comment="逾期罚息/违约金金额")
    # 状态细化（覆盖所有业务场景）
    account_status = Column(SmallInteger, default=1, comment="1正常未结清 2全额结清 3部分逾期 4全部逾期 5作废红冲")
    settle_time = Column(DateTime, comment="全款结清时间")
    # 资金&凭证溯源
    voucher_no = Column(String(64), comment="应收入账凭证编号")
    settle_voucher_no = Column(String(64), comment="回款结清核销凭证编号")
    # 业务备注与对账说明
    reconcile_remark = Column(Text, comment="账龄差异、逾期特殊说明")
    remark = Column(Text, comment="应收台账业务备注")
    # 审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="台账制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_house_contract", "tenant", "house_id", "contract_id", "is_del", unique=True),
        Index("idx_tenant_customer", "tenant", "customer_id"),
        Index("idx_tenant_project_building", "tenant", "project_id", "building_id"),
        Index("idx_tenant_status", "tenant", "account_status"),
        Index("idx_tenant_overdue", "tenant", "overdue_date"),
        Index("idx_tenant_settle_time", "tenant", "settle_time"),
        {"comment": "客户应收台账表：购房合同房款应收总账，支撑账龄分析、逾期风控、回款结清核算"}
    )


class FinAccountPayable(Base):
    """供应商应付台账表：工程/广告/营销费用应付账款，供应商往来对账核心台账"""
    __tablename__ = "fin_account_payable"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    payable_no = Column(String(64), nullable=False, comment="应付台账单号，租户唯一")
    # 项目楼栋维度
    project_id = Column(BigInteger, nullable=False, comment="归属楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    building_id = Column(BigInteger, comment="分摊楼栋ID，多楼栋逗号分隔")
    building_name = Column(String(512), comment="分摊楼栋名称冗余")
    # 供应商维度冗余
    supplier_id = Column(BigInteger, nullable=False, comment="供应商ID")
    supplier_name = Column(String(100), nullable=False, comment="供应商名称冗余")
    supplier_type = Column(SmallInteger, nullable=False, comment="供应商类型：1工程总包 2营销服务 3设计监理 4物资采购")
    # 业务关联溯源
    relate_biz_type = Column(SmallInteger, nullable=False, comment="关联业务类型：1工程成本 2广告营销 3通用费用")
    relate_biz_id = Column(BigInteger, nullable=False, comment="关联业务单据ID")
    contract_id = Column(BigInteger, comment="对应供应商合同ID")
    # 财务核算配置
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID")
    cost_subject_id = Column(BigInteger, nullable=False, comment="应付账款对应会计科目ID")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="进项税税率模板ID")
    # 账期时间
    bill_date = Column(Date, nullable=False, comment="应付账单入账日期")
    due_date = Column(Date, nullable=False, comment="付款到期日，账龄计算依据")
    overdue_date = Column(Date, comment="逾期起始日期")
    overdue_days = Column(Integer, default=0, comment="当前逾期天数")
    # 标准化应付金额拆分
    payable_total_amt = Column(Numeric(16,2), nullable=False, comment="应付含税总金额")
    payable_untax_amt = Column(Numeric(16,2), nullable=False, comment="应付不含税成本金额")
    payable_tax_amt = Column(Numeric(16,2), nullable=False, comment="可抵扣进项税额")
    paid_amount = Column(Numeric(16,2), default=0, comment="累计已付含税金额")
    unpaid_amount = Column(Numeric(16,2), nullable=False, comment="剩余未付余额")
    deduct_amount = Column(Numeric(16,2), default=0, comment="质保金/违约金扣减总额")
    # 状态细化
    payable_status = Column(SmallInteger, default=1, comment="1未结清 2已结清 3部分结清 4逾期挂账 5作废")
    settle_time = Column(DateTime, comment="全额结清时间")
    # 资金凭证溯源
    bank_flow_ids = Column(String(1024), comment="关联付款银行流水ID集合")
    voucher_no = Column(String(64), comment="应付入账凭证编号")
    settle_voucher_no = Column(String(64), comment="付款核销凭证编号")
    # 附件与备注
    payable_file_url = Column(String(1024), comment="结算单、发票、验收单附件")
    reconcile_remark = Column(Text, comment="往来对账差异说明")
    remark = Column(Text, comment="应付台账业务备注")
    # 审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="台账制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_payable_no", "tenant", "payable_no", "is_del", unique=True),
        Index("idx_tenant_supplier", "tenant", "supplier_id"),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_status", "tenant", "payable_status"),
        Index("idx_tenant_due_date", "tenant", "due_date"),
        Index("idx_tenant_biz_rel", "tenant", "relate_biz_id"),
        {"comment": "供应商应付台账表：工程/营销费用应付账款，支撑供应商对账、账龄分析、逾期付款管控"}
    )


class FinAdvancePay(Base):
    """预付款台账表：供应商预付工程款、预付营销款、质保金预付核销台账"""
    __tablename__ = "fin_advance_pay"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    advance_no = Column(String(64), nullable=False, comment="预付款单号，租户唯一")
    # 项目楼栋维度
    project_id = Column(BigInteger, nullable=False, comment="归属楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    building_id = Column(BigInteger, comment="成本分摊楼栋ID")
    building_name = Column(String(512), comment="分摊楼栋名称冗余")
    # 供应商信息
    supplier_id = Column(BigInteger, nullable=False, comment="供应商ID")
    supplier_name = Column(String(100), nullable=False, comment="供应商名称冗余")
    # 预付业务类型细化
    advance_type = Column(SmallInteger, nullable=False, comment="1工程预付款 2营销预付款 3质保金预付 4其他预付")
    # 财务核算配置
    project_fin_config_id = Column(BigInteger, nullable=False, comment="楼盘财务配置ID")
    advance_subject_id = Column(BigInteger, nullable=False, comment="预付账款会计科目ID")
    tax_tpl_id = Column(BigInteger, nullable=False, comment="进项税税率模板ID")
    # 时间维度
    advance_date = Column(Date, nullable=False, comment="预付付款日期")
    expire_date = Column(Date, comment="预付核销过期日期")
    # 标准化预付金额拆分
    advance_total_amt = Column(Numeric(16,2), nullable=False, comment="预付含税总金额")
    advance_untax_amt = Column(Numeric(16,2), nullable=False, comment="预付不含税成本金额")
    advance_tax_amt = Column(Numeric(16,2), nullable=False, comment="预付可抵扣进项税额")
    used_amount = Column(Numeric(16,2), default=0, comment="已核销含税金额")
    balance_amount = Column(Numeric(16,2), nullable=False, comment="剩余可核销余额")
    # 关联单据
    relate_pay_id = Column(BigInteger, nullable=False, comment="关联预付款付款单ID")
    relate_payable_ids = Column(String(1024), comment="核销关联应付台账ID集合")
    # 发票核销信息
    invoice_no = Column(String(256), comment="核销对应发票号码")
    invoice_date = Column(Date, comment="发票开具日期")
    # 状态细化
    advance_status = Column(SmallInteger, default=1, comment="1使用中可核销 2已全额核销 3过期作废 4红冲取消")
    settle_time = Column(DateTime, comment="全额核销完成时间")
    # 凭证溯源
    voucher_no = Column(String(64), comment="预付入账凭证编号")
    settle_voucher_no = Column(String(64), comment="核销冲抵凭证编号")
    # 附件备注
    advance_file_url = Column(String(1024), comment="预付协议、付款回单、核销结算附件")
    reconcile_remark = Column(Text, comment="核销差异、过期说明")
    remark = Column(Text, comment="预付款业务备注")
    # 审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="台账制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_advance_no", "tenant", "advance_no", "is_del", unique=True),
        Index("idx_tenant_supplier", "tenant", "supplier_id"),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_status", "tenant", "advance_status"),
        Index("idx_tenant_pay_rel", "tenant", "relate_pay_id"),
        Index("idx_tenant_expire_date", "tenant", "expire_date"),
        {"comment": "预付款台账表：供应商预付工程款、营销款、质保金核销台账，支撑预付冲应付核算"}
    )


class FinOtherLoan(Base):
    """其他往来款台账表：员工借款、集团往来、临时挂账、保证金其他应收应付"""
    __tablename__ = "fin_other_loan"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    loan_no = Column(String(64), nullable=False, comment="往来款单号，租户唯一")
    # 项目维度（集团往来可空）
    project_id = Column(BigInteger, comment="归属楼盘ID，集团总部往来为空")
    project_name = Column(String(128), comment="楼盘名称冗余")
    # 往来主体类型区分
    loan_counterparty_type = Column(SmallInteger, nullable=False, comment="1内部员工 2外部供应商 3集团公司 4外部机构")
    counterparty_id = Column(BigInteger, nullable=False, comment="对方主体ID")
    counterparty_name = Column(String(100), nullable=False, comment="对方名称冗余")
    counterparty_dept = Column(String(100), comment="对方部门/所属单位")
    # 往来类型细化
    loan_type = Column(SmallInteger, nullable=False, comment="1员工借款 2保证金 3集团拆借 4临时挂账 5押金")
    loan_direction = Column(SmallInteger, nullable=False, comment="1其他应收 2其他应付")
    # 财务核算配置
    project_fin_config_id = Column(BigInteger, comment="楼盘财务配置ID")
    loan_subject_id = Column(BigInteger, nullable=False, comment="往来款对应会计科目ID")
    # 账期时间
    loan_date = Column(Date, nullable=False, comment="往来挂账日期")
    due_date = Column(Date, comment="结清截止日期")
    # 金额标准化拆分
    loan_total_amt = Column(Numeric(16,2), nullable=False, comment="往来含税总金额")
    loan_untax_amt = Column(Numeric(16,2), nullable=False, comment="往来不含税金额")
    loan_tax_amt = Column(Numeric(16,2), default=0, comment="往来对应税额")
    settle_amt = Column(Numeric(16,2), default=0, comment="已结清金额")
    balance_amt = Column(Numeric(16,2), nullable=False, comment="剩余挂账余额")
    # 状态细化
    loan_status = Column(SmallInteger, default=1, comment="1挂账中 2部分结清 3全额结清 4作废红冲")
    settle_time = Column(DateTime, comment="最终结清时间")
    # 资金凭证溯源
    relate_flow_id = Column(BigInteger, comment="关联银行流水ID")
    voucher_no = Column(String(64), comment="往来挂账凭证编号")
    settle_voucher_no = Column(String(64), comment="结清冲销凭证编号")
    # 附件备注
    loan_file_url = Column(String(1024), comment="借款单、协议、收据附件")
    reconcile_remark = Column(Text, comment="往来对账差异、结清说明")
    remark = Column(Text, comment="往来款业务备注")
    # 审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="台账制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 统一乐观锁
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_loan_no", "tenant", "loan_no", "is_del", unique=True),
        Index("idx_tenant_counterparty", "tenant", "counterparty_id"),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_loan_type", "tenant", "loan_type", "loan_direction"),
        Index("idx_tenant_status", "tenant", "loan_status"),
        Index("idx_tenant_due_date", "tenant", "due_date"),
        {"comment": "其他往来款台账表：员工借款、集团往来、保证金、押金等非房款非工程类往来核算"}
    )



# ==================== 资金对账模块 ====================



class FinBankCheck(Base):
    """银行对账记录表：银行流水与系统业务单据逐笔对账，解决账实不符、流水溯源、差异排查"""
    __tablename__ = "fin_bank_check"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团隔离")
    check_no = Column(String(64), nullable=False, comment="银行对账单号，租户唯一")
    # 银行账户维度
    account_id = Column(BigInteger, nullable=False, comment="银行账户ID")
    account_name = Column(String(100), nullable=False, comment="银行账户名称冗余")
    account_bank = Column(String(100), comment="开户银行冗余")
    # 对账核心时间
    check_date = Column(Date, nullable=False, comment="对账所属日期")
    check_finish_time = Column(DateTime, comment="对账完成时间")
    # 银行流水核心信息
    bank_flow_no = Column(String(64), nullable=False, comment="银行官方流水号")
    bank_flow_type = Column(SmallInteger, nullable=False, comment="流水类型：1收款 2付款 3退款 4手续费")
    bank_trade_time = Column(DateTime, nullable=False, comment="银行交易发生时间")
    # 标准化金额（统一全系统精度）
    bank_amount = Column(Numeric(16,2), nullable=False, comment="银行流水交易金额")
    system_amount = Column(Numeric(16,2), default=0, comment="系统匹配业务金额")
    diff_amount = Column(Numeric(16,2), default=0, comment="对账差异金额")
    # 业务关联溯源（打通全模块链路）
    relate_biz_type = Column(SmallInteger, nullable=False, comment="业务类型：1房款收款 2佣金付款 3费用报销 4工程付款 5渠道结算 6其他往来")
    relate_biz_id = Column(BigInteger, comment="关联系统业务单据ID")
    relate_biz_no = Column(String(64), comment="关联系统业务单据编号")
    voucher_no = Column(String(64), comment="对应财务凭证编号")
    # 对账状态细化（覆盖全场景）
    check_status = Column(SmallInteger, default=1, comment="1未匹配 2已匹配对账一致 3对账差异 4手动调平 5作废")
    # 差异处理信息
    diff_reason = Column(Text, comment="对账差异原因说明")
    solve_remark = Column(Text, comment="差异处理方案、调平备注")
    # 操作人审计
    check_user_id = Column(BigInteger, comment="对账操作人ID")
    create_user_id = Column(BigInteger, nullable=False, comment="单据制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 附件存证
    check_file_url = Column(String(1024), comment="银行回单、对账调节表、差异处理附件")
    remark = Column(Text, comment="对账通用备注")
    # 统一系统规范
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_check_no", "tenant", "check_no", "is_del", unique=True),
        Index("idx_tenant_account_date", "tenant", "account_id", "check_date"),
        Index("idx_tenant_flow_no", "tenant", "bank_flow_no"),
        Index("idx_tenant_biz_rel", "tenant", "relate_biz_type", "relate_biz_id"),
        Index("idx_tenant_check_status", "tenant", "check_status"),
        {"comment": "银行对账记录表：银行流水与系统业务单据逐笔对账，支撑资金账实核对、差异调平、流水溯源"}
    )


class FinDailyCashAccount(Base):
    """每日资金轧账表：按【银行账户+日期】日结轧账，房企资金日清日结核心台账"""
    __tablename__ = "fin_daily_cash_account"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    # 核心维度：修复原表无银行账户致命缺陷
    account_id = Column(BigInteger, nullable=False, comment="银行账户ID")
    account_name = Column(String(100), nullable=False, comment="账户名称冗余")
    # 项目维度（集团统一账户可空）
    project_id = Column(BigInteger, comment="楼盘ID")
    project_name = Column(String(128), comment="楼盘名称冗余")
    # 轧账核心日期（纯日期，杜绝时分秒问题）
    account_date = Column(Date, nullable=False, comment="资金轧账日期")
    # 期初期末余额
    beginning_balance = Column(Numeric(16,2), default=0, comment="当日期初账户余额")
    ending_balance = Column(Numeric(16,2), default=0, comment="当日系统期末余额")
    bank_ending_balance = Column(Numeric(16,2), default=0, comment="银行官方期末余额")
    balance_diff = Column(Numeric(16,2), default=0, comment="账实余额差异")
    # 当日收支明细拆分（精细化资金统计）
    total_receipt = Column(Numeric(16,2), default=0, comment="当日收款总额")
    house_receipt = Column(Numeric(16,2), default=0, comment="当日房款收款")
    other_receipt = Column(Numeric(16,2), default=0, comment="当日其他收款")
    
    total_refund = Column(Numeric(16,2), default=0, comment="当日退款总额")
    house_refund = Column(Numeric(16,2), default=0, comment="当日房款退款")
    
    total_pay = Column(Numeric(16,2), default=0, comment="当日付款总额")
    commission_pay = Column(Numeric(16,2), default=0, comment="当日佣金提成付款")
    cost_pay = Column(Numeric(16,2), default=0, comment="当日费用/工程付款")
    other_pay = Column(Numeric(16,2), default=0, comment="当日其他付款")
    # 轧账状态细化
    account_status = Column(SmallInteger, default=1, comment="1未轧账 2轧账正常 3余额差异 4已审核归档 5作废重轧")
    # 审核操作人
    create_user_id = Column(BigInteger, nullable=False, comment="轧账制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    audit_user_id = Column(BigInteger, comment="资金审核人ID")
    audit_time = Column(DateTime, comment="审核归档时间")
    # 凭证与附件
    voucher_no = Column(String(64), comment="日结汇总凭证编号")
    account_file_url = Column(String(1024), comment="日结报表、对账表附件")
    diff_remark = Column(Text, comment="余额差异原因及处理说明")
    remark = Column(Text, comment="轧账通用备注")
    # 统一系统规范
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        # 修复原表唯一索引缺陷：账户+日期+楼盘 唯一约束
        Index("uk_tenant_account_date_proj", "tenant", "account_id", "account_date", "project_id", "is_del", unique=True),
        Index("idx_tenant_account", "tenant", "account_id"),
        Index("idx_tenant_date_status", "tenant", "account_date", "account_status"),
        Index("idx_tenant_project", "tenant", "project_id"),
        {"comment": "每日资金轧账表：按银行账户日结轧账，实现资金日清日结、账实核对、每日资金监控"}
    )


class FinChannelReconcile(Base):
    """渠道月度对账表：分销渠道月度业绩、佣金对账，支撑渠道结算、差异核对、付款依据"""
    __tablename__ = "fin_channel_reconcile"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    reconcile_no = Column(String(64), nullable=False, comment="渠道对账单号，租户唯一")
    # 项目楼栋维度（土增/成本分摊必备）
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    building_scope = Column(String(512), comment="本次对账覆盖楼栋ID，逗号分隔")
    # 渠道维度
    channel_id = Column(BigInteger, nullable=False, comment="分销渠道ID")
    channel_name = Column(String(100), nullable=False, comment="渠道名称冗余")
    # 结算周期标准化
    reconcile_month = Column(String(32), nullable=False, comment="对账月份")
    settle_start = Column(Date, nullable=False, comment="对账周期起始日")
    settle_end = Column(Date, nullable=False, comment="对账周期截止日")
    # 业绩明细统计（对账核心数据）
    channel_deal_num = Column(Integer, default=0, comment="渠道申报成交套数")
    system_deal_num = Column(Integer, default=0, comment="系统审核成交套数")
    refund_num = Column(Integer, default=0, comment="周期内退房套数")
    # 对账金额体系
    channel_amount = Column(Numeric(16,2), default=0, comment="渠道自主申报佣金金额")
    system_amount = Column(Numeric(16,2), default=0, comment="系统核算合规佣金金额")
    deduct_amount = Column(Numeric(16,2), default=0, comment="周期退房/违规扣减金额")
    diff_amount = Column(Numeric(16,2), default=0, comment="对账差异金额")
    # 关联结算付款单
    commission_pay_id = Column(BigInteger, comment="关联渠道佣金付款单ID")
    voucher_no = Column(String(64), comment="对账结算凭证编号")
    # 对账状态细化
    reconcile_status = Column(SmallInteger, default=1, comment="1待渠道确认 2已对账无差异 3对账存在差异 4差异已处理 5作废")
    # 对账操作信息
    reconcile_user_id = Column(BigInteger, comment="对账负责人ID")
    create_user_id = Column(BigInteger, nullable=False, comment="制单人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    reconcile_time = Column(DateTime, comment="对账最终确认时间")
    # 差异处理
    diff_reason = Column(Text, comment="金额/套数差异原因")
    solve_plan = Column(Text, comment="差异调整方案、下期抵扣说明")
    # 附件存证
    reconcile_file_url = Column(String(1024), comment="渠道对账表、结算明细、沟通回执附件")
    remark = Column(Text, comment="月度对账通用备注")
    # 统一系统规范
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_reconcile_no", "tenant", "reconcile_no", "is_del", unique=True),
        Index("idx_tenant_channel_month", "tenant", "channel_id", "reconcile_month"),
        Index("idx_tenant_project", "tenant", "project_id"),
        Index("idx_tenant_status", "tenant", "reconcile_status"),
        Index("idx_tenant_pay_rel", "tenant", "commission_pay_id"),
        {"comment": "渠道月度对账表：分销渠道月度成交业绩、佣金对账，作为渠道结算付款核心依据"}
    )



# ==================== 会计凭证模块 ====================


class FinVoucher(Base):
    """会计凭证主表：所有业务单据生成财务凭证总台账，支持自动/手工凭证、审核、结账、红冲、作废"""
    __tablename__ = "fin_voucher"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团数据隔离")
    # 财务标准凭证字段（会计准则规范）
    voucher_no = Column(String(64), nullable=False, comment="凭证编号，租户唯一")
    voucher_word = Column(String(16), default="记", comment="凭证字：收/付/转/记")
    voucher_type = Column(SmallInteger, nullable=False, comment="凭证类型：1收款凭证 2付款凭证 3转账凭证")
    voucher_year = Column(Integer, nullable=False, comment="会计年度")
    voucher_month = Column(String(32), nullable=False, comment="会计月份")
    voucher_date = Column(Date, nullable=False, comment="凭证做账日期")
    attach_num = Column(Integer, default=0, comment="附件张数")
    # 凭证来源业务溯源（全覆盖系统所有业务模块）
    source_type = Column(SmallInteger, nullable=False, comment="来源类型：1收款 2退款 3销售佣金 4费用报销 5工程成本 6广告成本 7应收应付 8预付核销 9往来款 10手工录入")
    source_biz_id = Column(BigInteger, nullable=False, comment="关联上游业务单据ID")
    source_biz_no = Column(String(64), nullable=False, comment="关联上游业务单据编号")
    # 红冲机制（财务核心）
    is_red_flush = Column(SmallInteger, default=0, comment="0正常凭证 1红字冲销凭证")
    red_flush_voucher_id = Column(BigInteger, comment="对应被红冲的原凭证ID")
    red_flush_reason = Column(Text, comment="红冲作废原因说明")
    # 凭证属性
    is_manual = Column(SmallInteger, default=0, comment="0系统自动生成 1财务手工录入")
    summary = Column(String(255), nullable=False, comment="凭证总摘要")
    # 完整状态链路（适配做账-审核-结账-红冲全流程）
    voucher_status = Column(SmallInteger, default=1, comment="1草稿 2已审核 3已结账 4已作废 5已红冲 6反结账")
    # 操作审计人员（全链路留痕）
    make_user_id = Column(BigInteger, nullable=False, comment="制单人ID")
    audit_user_id = Column(BigInteger, comment="审核人ID")
    audit_time = Column(DateTime, comment="凭证审核时间")
    settle_user_id = Column(BigInteger, comment="月末结账人ID")
    settle_time = Column(DateTime, comment="月末结账时间")
    # 备注与附件
    voucher_file_url = Column(String(1024), comment="凭证附件、单据扫描件、对账资料")
    remark = Column(Text, comment="凭证备注、特殊账务处理说明")
    # 系统统一规范
    create_user_id = Column(BigInteger, nullable=False, comment="创建人ID")
    update_user_id = Column(BigInteger, comment="更新人ID")
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_voucher_no", "tenant", "voucher_no", "is_del", unique=True),
        Index("idx_tenant_source_biz", "tenant", "source_type", "source_biz_id"),
        Index("idx_tenant_voucher_month", "tenant", "voucher_year", "voucher_month"),
        Index("idx_tenant_voucher_status", "tenant", "voucher_status"),
        Index("idx_tenant_red_flush", "tenant", "is_red_flush", "red_flush_voucher_id"),
        {"comment": "会计凭证主表：财务凭证头部信息，支撑月末结账、凭证红冲、账务审计"}
    )


class FinVoucherItem(Base):
    """凭证明细表：凭证借贷分录行，支持房企全维度辅助核算，总账明细账核心数据"""
    __tablename__ = "fin_voucher_item"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    voucher_id = Column(BigInteger, nullable=False, comment="关联凭证主表ID")
    # 会计科目信息（冗余优化，减少联表）
    subject_id = Column(BigInteger, nullable=False, comment="会计科目ID")
    subject_code = Column(String(64), nullable=False, comment="科目编码冗余")
    subject_name = Column(String(128), nullable=False, comment="科目名称冗余")
    subject_type = Column(SmallInteger, nullable=False, comment="科目类型：1资产 2负债 3权益 4成本 5损益")
    # 标准化借贷金额（统一系统精度16,2）
    borrow_amount = Column(Numeric(16,2), default=0, comment="借方发生金额")
    lend_amount = Column(Numeric(16,2), default=0, comment="贷方发生金额")
    # 多币种适配（集团房企通用）
    original_currency = Column(String(32), default="CNY", comment="原币币种")
    original_amount = Column(Numeric(16,2), default=0, comment="原币金额")
    exchange_rate = Column(Numeric(10,4), default=1.0000, comment="记账汇率")
    # 【房企核心】全维度辅助核算（全覆盖业务场景、土增清算）
    project_id = Column(BigInteger, comment="辅助核算-楼盘ID")
    project_name = Column(String(128), comment="楼盘名称冗余")
    building_id = Column(BigInteger, comment="辅助核算-楼栋ID，土增成本分摊核心")
    building_name = Column(String(128), comment="楼栋名称冗余")
    customer_id = Column(BigInteger, comment="辅助核算-购房客户ID")
    supplier_id = Column(BigInteger, comment="辅助核算-供应商ID")
    channel_id = Column(BigInteger, comment="辅助核算-分销渠道ID")
    staff_id = Column(BigInteger, comment="辅助核算-员工ID")
    dept_id = Column(BigInteger, comment="辅助核算-部门ID")
    # 明细信息
    item_summary = Column(String(255), comment="分录行明细摘要")
    item_sort = Column(Integer, default=0, comment="分录行排序号")
    item_remark = Column(Text, comment="分录明细备注、账务说明")
    # 系统统一规范
    create_user_id = Column(BigInteger, nullable=False, comment="创建人ID")
    update_user_id = Column(BigInteger, comment="更新人ID")
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("idx_tenant_voucher_id", "tenant", "voucher_id"),
        Index("idx_tenant_subject", "tenant", "subject_id"),
        Index("idx_tenant_project_building", "tenant", "project_id", "building_id"),
        Index("idx_tenant_customer_supplier", "tenant", "customer_id", "supplier_id"),
        Index("idx_tenant_channel_staff", "tenant", "channel_id", "staff_id"),
        {"comment": "凭证明细表：凭证借贷分录明细，支持楼盘/楼栋/客户/供应商/渠道多维辅助核算"}
    )



# ==================== 财务审计追溯模块 ====================


class FinOperateLog(Base):
    """财务操作审计日志表：全财务模块操作永久留痕，支撑凭证变更、单据操作、配置变更审计追溯"""
    __tablename__ = "fin_operate_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码，多集团数据隔离")
    operate_no = Column(String(64), nullable=False, comment="审计日志唯一编号，租户唯一")
    # 操作人信息（完整审计留痕）
    operate_user_id = Column(BigInteger, nullable=False, comment="操作人ID")
    operate_user_name = Column(String(50), nullable=False, comment="操作人姓名冗余")
    operate_dept_id = Column(BigInteger, comment="操作人所属部门ID")
    operate_dept_name = Column(String(100), comment="操作人所属部门名称冗余")
    # 操作环境溯源（安全审计必备）
    operate_ip = Column(String(64), comment="操作客户端IP地址")
    operate_mac = Column(String(64), comment="设备MAC地址")
    terminal_type = Column(SmallInteger, default=1, comment="操作终端：1PC端 2移动端 3后台管理端")
    request_url = Column(String(255), comment="操作请求接口地址")
    # 业务模块枚举（数字化统一，替代字符串）
    biz_module = Column(SmallInteger, nullable=False, comment="业务模块：1收款管理 2退款管理 3应付应收台账 4预付款管理 5其他往来款 6资金对账 7会计凭证 8佣金结算 9费用报销 10财务配置")
    # 操作类型细化（覆盖财务全场景操作）
    operate_type = Column(SmallInteger, nullable=False, comment="1新增 2修改 3删除 4审核 5反审核 6作废 7红冲 8结账 9反结账 10配置变更 11批量操作")
    # 关联业务单据（精准溯源，适配凭证模块）
    biz_type = Column(SmallInteger, comment="业务单据类型：1收款单 2退款单 3应付台账 4应收台账 5预付款单 6往来款单 7会计凭证 8渠道对账 9资金轧账")
    biz_id = Column(BigInteger, comment="关联业务单据主ID")
    biz_no = Column(String(64), comment="关联业务单据编号")
    voucher_id = Column(BigInteger, comment="关联会计凭证ID，凭证操作专属溯源")
    voucher_no = Column(String(64), comment="关联会计凭证编号")
    # 操作内容数据快照（核心审计字段）
    operate_summary = Column(String(255), nullable=False, comment="操作简短摘要")
    operate_content = Column(Text, nullable=False, comment="操作详细描述、变更说明")
    old_data = Column(Text, comment="操作前完整数据JSON快照")
    new_data = Column(Text, comment="操作后完整数据JSON快照")
    # 操作结果状态细化
    operate_status = Column(SmallInteger, default=1, comment="1操作成功 2操作失败 3部分成功")
    error_msg = Column(Text, comment="操作失败异常信息、报错详情")
    # 系统统一规范字段（对齐全财务模块）
    create_user_id = Column(BigInteger, nullable=False, comment="创建人ID")
    update_user_id = Column(BigInteger, comment="更新人ID")
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除，日志默认不删除")
    create_time = Column(DateTime, server_default=func.now(), comment="操作创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="日志更新时间")

    __table_args__ = (
        Index("uk_tenant_operate_no", "tenant", "operate_no", "is_del", unique=True),
        Index("idx_tenant_biz_module", "tenant", "biz_module"),
        Index("idx_tenant_user", "tenant", "operate_user_id"),
        Index("idx_tenant_biz_rel", "tenant", "biz_type", "biz_id"),
        Index("idx_tenant_voucher_rel", "tenant", "voucher_id"),
        Index("idx_tenant_operate_type", "tenant", "operate_type"),
        Index("idx_tenant_create_time", "tenant", "create_time"),
        {"comment": "财务操作审计日志表：全财务模块操作永久留痕，支撑凭证红冲、结账、审核、单据变更合规审计追溯"}
    )



# ==================== 财务统计报表模块 ====================



class FinCashFlow(Base):
    """现金流统计表（日/月预聚合）：日常资金流水预统计，支撑现金流大屏、资金趋势分析"""
    __tablename__ = "fin_cash_flow"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    # 业务维度冗余
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    # 统计周期规范
    stat_date = Column(Date, nullable=False, comment="统计日期（日统计维度）")
    stat_month = Column(String(32), nullable=False, comment="统计月份（YYYY-MM）")
    stat_type = Column(SmallInteger, default=1, comment="统计类型：1日统计 2月统计")
    # 精细化现金流拆分（房企专用）
    total_receipt = Column(Numeric(16,2), default=0, comment="收款总金额")
    house_receipt = Column(Numeric(16,2), default=0, comment="房款销售收入")
    other_receipt = Column(Numeric(16,2), default=0, comment="其他经营收款")
    
    total_refund = Column(Numeric(16,2), default=0, comment="退款总金额")
    house_refund = Column(Numeric(16,2), default=0, comment="房款退款金额")
    
    total_pay = Column(Numeric(16,2), default=0, comment="付款总金额")
    commission_pay = Column(Numeric(16,2), default=0, comment="渠道佣金支付金额")
    cost_pay = Column(Numeric(16,2), default=0, comment="工程/营销费用支付")
    admin_pay = Column(Numeric(16,2), default=0, comment="管理费用支付")
    other_pay = Column(Numeric(16,2), default=0, comment="其他付款金额")
    
    # 核心现金流指标
    operating_net_cash = Column(Numeric(16,2), default=0, comment="经营活动净现金流")
    investing_net_cash = Column(Numeric(16,2), default=0, comment="投资活动净现金流")
    financing_net_cash = Column(Numeric(16,2), default=0, comment="筹资活动净现金流")
    net_cash_flow = Column(Numeric(16,2), default=0, comment="当期总净现金流")
    
    # 统计状态与批次
    stat_status = Column(SmallInteger, default=1, comment="1正常 2待重算 3数据异常")
    stat_batch = Column(String(64), comment="统计批次号，重算溯源")
    # 审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="统计生成人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 系统统一规范
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_project_date", "tenant", "project_id", "stat_date", "stat_type", "is_del", unique=True),
        Index("idx_tenant_project_month", "tenant", "project_id", "stat_month"),
        Index("idx_tenant_stat_status", "tenant", "stat_status"),
        {"comment": "现金流统计表（日/月预聚合）"}
    )


class FinReceivableStat(Base):
    """应收款统计表（预聚合）：客户应收、逾期、回款数据预统计，支撑应收账龄、风控分析"""
    __tablename__ = "fin_receivable_stat"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    # 维度冗余
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    # 统计周期
    stat_date = Column(Date, nullable=False, comment="统计日期")
    stat_month = Column(String(32), nullable=False, comment="统计月份（YYYY-MM）")
    stat_type = Column(SmallInteger, default=1, comment="统计类型：1日统计 2月统计")
    # 应收核心指标
    total_receivable = Column(Numeric(16,2), default=0, comment="累计应收总额")
    current_period_receivable = Column(Numeric(16,2), default=0, comment="当期新增应收")
    total_received = Column(Numeric(16,2), default=0, comment="累计已收总额")
    current_period_received = Column(Numeric(16,2), default=0, comment="当期回款金额")
    unpaid_amount = Column(Numeric(16,2), default=0, comment="当前未收余额")
    # 逾期风控指标
    overdue_amount = Column(Numeric(16,2), default=0, comment="当前逾期总金额")
    overdue_count = Column(Integer, default=0, comment="逾期单据笔数")
    max_overdue_days = Column(Integer, default=0, comment="当期最大逾期天数")
    # 回款率指标
    receive_rate = Column(Numeric(10,4), default=0, comment="当期回款率")
    # 统计状态
    stat_status = Column(SmallInteger, default=1, comment="1正常 2待重算 3数据异常")
    stat_batch = Column(String(64), comment="统计批次号")
    # 审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="统计生成人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 系统规范
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_project_date", "tenant", "project_id", "stat_date", "stat_type", "is_del", unique=True),
        Index("idx_tenant_project_month", "tenant", "project_id", "stat_month"),
        Index("idx_tenant_overdue", "tenant", "overdue_amount"),
        {"comment": "应收款统计表（预聚合）"}
    )


class FinTaxStat(Base):
    """税务统计表（预聚合）：进销项税额、开票、申报数据统计，支撑税务申报、税负分析"""
    __tablename__ = "fin_tax_stat"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    # 维度冗余
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    # 统计周期
    stat_month = Column(String(32), nullable=False, comment="统计月份（YYYY-MM）")
    stat_year = Column(Integer, nullable=False, comment="统计年度")
    # 开票数据
    invoice_amount = Column(Numeric(16,2), default=0, comment="当期含税开票总额")
    invoice_untax_amount = Column(Numeric(16,2), default=0, comment="当期不含税开票金额")
    # 税费数据拆分
    output_tax = Column(Numeric(16,2), default=0, comment="销项税额")
    input_tax = Column(Numeric(16,2), default=0, comment="进项税额")
    deduct_tax = Column(Numeric(16,2), default=0, comment="当期抵扣税额")
    tax_amount = Column(Numeric(16,2), default=0, comment="当期应缴税额")
    # 申报状态数据
    declare_amount = Column(Numeric(16,2), default=0, comment="已申报税额")
    declared_status = Column(SmallInteger, default=1, comment="1未申报 2已申报 3申报异常")
    # 税负率
    tax_burden_rate = Column(Numeric(10,4), default=0, comment="当期税负率")
    # 统计状态
    stat_status = Column(SmallInteger, default=1, comment="1正常 2待重算 3数据异常")
    stat_batch = Column(String(64), comment="统计批次号")
    # 审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="统计生成人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 系统规范
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_project_month", "tenant", "project_id", "stat_month", "is_del", unique=True),
        Index("idx_tenant_tax_year", "tenant", "stat_year"),
        Index("idx_tenant_declare_status", "tenant", "declared_status"),
        {"comment": "税务统计表（预聚合）"}
    )


class FinCommissionStat(Base):
    """佣金统计表（预聚合）：渠道佣金月度统计，支撑渠道结算、成本核算"""
    __tablename__ = "fin_commission_stat"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    # 多维维度冗余
    project_id = Column(BigInteger, nullable=False, comment="楼盘ID")
    project_name = Column(String(128), nullable=False, comment="楼盘名称冗余")
    channel_id = Column(BigInteger, nullable=False, comment="渠道ID")
    channel_name = Column(String(100), nullable=False, comment="渠道名称冗余")
    channel_type = Column(SmallInteger, nullable=False, comment="渠道类型：1全民分销 2中介渠道 3内部销售")
    # 统计周期
    stat_month = Column(String(32), nullable=False, comment="统计月份（YYYY-MM）")
    stat_year = Column(Integer, nullable=False, comment="统计年度")
    # 成交业绩指标
    deal_num = Column(Integer, default=0, comment="当期成交套数")
    deal_amount = Column(Numeric(16,2), default=0, comment="当期成交总额")
    # 佣金核心指标
    total_commission = Column(Numeric(16,2), default=0, comment="当期应付佣金总额")
    deduct_commission = Column(Numeric(16,2), default=0, comment="当期扣减佣金（退房/违规）")
    real_commission = Column(Numeric(16,2), default=0, comment="当期实际应付佣金")
    paid_amount = Column(Numeric(16,2), default=0, comment="当期已支付佣金")
    unpaid_amount = Column(Numeric(16,2), default=0, comment="当期未付佣金余额")
    # 统计状态
    stat_status = Column(SmallInteger, default=1, comment="1正常 2待重算 3数据异常")
    stat_batch = Column(String(64), comment="统计批次号")
    # 审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="统计生成人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    # 系统规范
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("uk_tenant_channel_month", "tenant", "channel_id", "stat_month", "is_del", unique=True),
        Index("idx_tenant_project_month", "tenant", "project_id", "stat_month"),
        Index("idx_tenant_channel_type", "tenant", "channel_type"),
        {"comment": "佣金统计表（预聚合）"}
    )


class FinDataChangeLog(Base):
    """数据变更记录表：统计报表底层数据变更溯源，适配报表数据核对、差异排查"""
    __tablename__ = "fin_data_change_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    # 变更主体
    table_name = Column(String(100), nullable=False, comment="变更数据表名")
    record_id = Column(BigInteger, nullable=False, comment="变更数据主键ID")
    # 标准化枚举类型
    change_type = Column(SmallInteger, nullable=False, comment="变更类型：1新增 2修改 3删除")
    # 数据快照
    before_data = Column(Text, comment="变更前完整JSON数据")
    after_data = Column(Text, comment="变更后完整JSON数据")
    # 操作人审计冗余
    operator_id = Column(BigInteger, nullable=False, comment="操作人ID")
    operator_name = Column(String(100), nullable=False, comment="操作人姓名冗余")
    operator_dept = Column(String(100), comment="操作人部门")
    operate_ip = Column(String(64), comment="操作IP地址")
    # 变更说明
    change_remark = Column(Text, comment="数据变更原因、业务说明")
    # 系统规范字段
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="变更时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("idx_tenant_table", "tenant", "table_name"),
        Index("idx_tenant_record", "tenant", "record_id"),
        Index("idx_tenant_change_time", "tenant", "create_time"),
        Index("idx_tenant_operator", "tenant", "operator_id"),
        {"comment": "数据变更记录表：报表底层数据变更全追溯"}
    )


class FinCashFlowStatement(Base):
    """正式现金流量表：会计准则标准财报，月度/年度正式出具"""
    __tablename__ = "fin_cash_flow_statement"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    report_period = Column(String(7), nullable=False, comment="报表期间（YYYY-MM）")
    report_year = Column(Integer, nullable=False, comment="报表年度")
    # 经营活动现金流
    operating_cash_in = Column(Numeric(16,2), default=0, comment="经营活动现金流入")
    operating_cash_out = Column(Numeric(16,2), default=0, comment="经营活动现金流出")
    operating_cash_flow = Column(Numeric(16,2), default=0, comment="经营活动净现金流")
    # 投资活动现金流
    investing_cash_in = Column(Numeric(16,2), default=0, comment="投资活动现金流入")
    investing_cash_out = Column(Numeric(16,2), default=0, comment="投资活动现金流出")
    investing_cash_flow = Column(Numeric(16,2), default=0, comment="投资活动净现金流")
    # 筹资活动现金流
    financing_cash_in = Column(Numeric(16,2), default=0, comment="筹资活动现金流入")
    financing_cash_out = Column(Numeric(16,2), default=0, comment="筹资活动现金流出")
    financing_cash_flow = Column(Numeric(16,2), default=0, comment="筹资活动净现金流")
    # 汇总指标
    net_cash_flow = Column(Numeric(16,2), default=0, comment="当期净现金流量")
    last_period_net_flow = Column(Numeric(16,2), default=0, comment="上期同期净现金流（对比分析）")
    # 报表状态
    report_status = Column(SmallInteger, default=1, comment="1草稿 2已审核 3已归档 4作废")
    # 审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="制表人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    audit_user_id = Column(BigInteger, comment="审核人ID")
    audit_time = Column(DateTime, comment="审核时间")
    # 系统规范
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("idx_cash_flow_tenant", "tenant"),
        Index("idx_cash_flow_period", "tenant", "report_period"),
        Index("idx_cash_flow_status", "tenant", "report_status"),
        {"comment": "现金流量表（正式会计准则报表）"}
    )


class FinProfitStatement(Base):
    """正式利润表：标准企业会计准则利润报表"""
    __tablename__ = "fin_profit_statement"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    report_period = Column(String(7), nullable=False, comment="报表期间（YYYY-MM）")
    report_year = Column(Integer, nullable=False, comment="报表年度")
    # 营收成本
    revenue = Column(Numeric(16,2), default=0, comment="营业收入")
    other_business_revenue = Column(Numeric(16,2), default=0, comment="其他业务收入")
    cost = Column(Numeric(16,2), default=0, comment="营业成本")
    other_business_cost = Column(Numeric(16,2), default=0, comment="其他业务成本")
    business_tax = Column(Numeric(16,2), default=0, comment="营业税金及附加")
    # 利润指标
    gross_profit = Column(Numeric(16,2), default=0, comment="销售毛利润")
    # 费用支出
    operating_expense = Column(Numeric(16,2), default=0, comment="营业费用")
    admin_expense = Column(Numeric(16,2), default=0, comment="管理费用")
    financial_expense = Column(Numeric(16,2), default=0, comment="财务费用")
    # 最终利润
    operating_profit = Column(Numeric(16,2), default=0, comment="营业利润")
    total_profit = Column(Numeric(16,2), default=0, comment="利润总额")
    income_tax = Column(Numeric(16,2), default=0, comment="企业所得税")
    net_profit = Column(Numeric(16,2), default=0, comment="净利润")
    # 同期对比
    last_period_net_profit = Column(Numeric(16,2), default=0, comment="上期同期净利润")
    # 报表状态
    report_status = Column(SmallInteger, default=1, comment="1草稿 2已审核 3已归档 4作废")
    # 审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="制表人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    audit_user_id = Column(BigInteger, comment="审核人ID")
    audit_time = Column(DateTime, comment="审核时间")
    # 系统规范
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("idx_profit_tenant", "tenant"),
        Index("idx_profit_period", "tenant", "report_period"),
        Index("idx_profit_status", "tenant", "report_status"),
        {"comment": "利润表（正式会计准则报表）"}
    )


class FinBalanceSheet(Base):
    """正式资产负债表：标准企业会计准则资产负债报表"""
    __tablename__ = "fin_balance_sheet"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    report_period = Column(String(7), nullable=False, comment="报表期间（YYYY-MM）")
    report_year = Column(Integer, nullable=False, comment="报表年度")
    # 资产类
    current_assets = Column(Numeric(16,2), default=0, comment="流动资产合计")
    non_current_assets = Column(Numeric(16,2), default=0, comment="非流动资产合计")
    total_assets = Column(Numeric(16,2), default=0, comment="资产总计")
    # 负债类
    current_liabilities = Column(Numeric(16,2), default=0, comment="流动负债合计")
    non_current_liabilities = Column(Numeric(16,2), default=0, comment="非流动负债合计")
    total_liabilities = Column(Numeric(16,2), default=0, comment="负债总计")
    # 权益类
    owner_equity = Column(Numeric(16,2), default=0, comment="所有者权益合计")
    # 平衡校验
    asset_equity_balance = Column(Numeric(10,4), default=0, comment="资产权益平衡差值（校验用）")
    # 期初结转数据
    begin_total_assets = Column(Numeric(16,2), default=0, comment="期初资产总额")
    begin_total_liabilities = Column(Numeric(16,2), default=0, comment="期初负债总额")
    begin_equity = Column(Numeric(16,2), default=0, comment="期初权益总额")
    # 报表状态
    report_status = Column(SmallInteger, default=1, comment="1草稿 2已审核 3已归档 4作废")
    # 审计字段
    create_user_id = Column(BigInteger, nullable=False, comment="制表人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    audit_user_id = Column(BigInteger, comment="审核人ID")
    audit_time = Column(DateTime, comment="审核时间")
    # 系统规范
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("idx_balance_tenant", "tenant"),
        Index("idx_balance_period", "tenant", "report_period"),
        Index("idx_balance_status", "tenant", "report_status"),
        {"comment": "资产负债表（正式会计准则报表）"}
    )


class FinFinancialReport(Base):
    """财务报表主表：三大核心报表汇总管理，统一报表生命周期"""
    __tablename__ = "fin_financial_report"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tenant = Column(String(32), nullable=False, comment="租户编码")
    # 报表基础信息
    report_name = Column(String(100), nullable=False, comment="报表名称")
    report_type = Column(SmallInteger, nullable=False, comment="报表类型：1现金流量表 2利润表 3资产负债表 4综合财报")
    report_period = Column(String(7), nullable=False, comment="报表期间（YYYY-MM）")
    report_year = Column(Integer, nullable=False, comment="报表年度")
    # 关联子报表ID
    cash_flow_statement_id = Column(BigInteger, comment="现金流量表ID")
    profit_statement_id = Column(BigInteger, comment="利润表ID")
    balance_sheet_id = Column(BigInteger, comment="资产负债表ID")
    # 报表文件
    report_file_url = Column(String(1024), comment="导出报表附件文件")
    # 标准化报表状态
    status = Column(SmallInteger, default=1, comment="1草稿 2已编制 3已审核 4已归档 5作废")
    # 审计流程字段
    create_user_id = Column(BigInteger, nullable=False, comment="报表编制人ID")
    update_user_id = Column(BigInteger, comment="最后修改人sys_user ID")
    audit_user_id = Column(BigInteger, comment="报表审核人ID")
    audit_time = Column(DateTime, comment="报表审核时间")
    archive_user_id = Column(BigInteger, comment="报表归档人ID")
    archive_time = Column(DateTime, comment="报表归档时间")
    # 备注说明
    remark = Column(Text, comment="报表编制说明、数据异常备注")
    # 系统统一规范
    version = Column(Integer, default=0, comment="乐观锁版本号")
    is_del = Column(SmallInteger, default=0, comment="0正常 1逻辑删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("idx_fin_report_tenant", "tenant"),
        Index("idx_fin_report_type", "tenant", "report_type"),
        Index("idx_fin_report_period", "tenant", "report_period"),
        Index("idx_fin_report_status", "tenant", "status"),
        {"comment": "财务报表主表：统一管理三大核心财务报表生命周期"}
    )



# 导出所有模型
__all__ = [
    # 财务基础档案模块
    "FinProjectFinConfig",
    "FinAccount",
    "FinSubject",
    "FinTaxRate",
    "FinBankInfo",
    "FinDiscountRule",
    # 房款收支核心模块
    "FinInstallmentPlan",
    "FinPriceDiff",
    "FinReceiptRecord",
    "FinRefundRecord",
    "FinDepositAccount",
    # 票据税务合规模块
    "FinInvoice",
    "FinInvoiceRed",
    "FinReceipt",
    "FinMaintainFund",
    "FinTaxDeclare",
    # 渠道佣金&内部提成支付模块
    "FinCommissionPay",
    "FinCommissionDeduct",
    "FinSalesBonusPay",
    # 项目成本&运营费用模块
    "FinCostExpense",
    "FinCostPay",
    "FinAdCost",
    "FinProjectEngCost",
    # 应收应付往来台账模块
    "FinAccountReceivable",
    "FinAccountPayable",
    "FinAdvancePay",
    "FinOtherLoan",
    # 资金对账模块
    "FinBankCheck",
    "FinDailyCashAccount",
    "FinChannelReconcile",
    # 会计凭证模块
    "FinVoucher",
    "FinVoucherItem",
    # 财务审计追溯模块
    "FinOperateLog",
    "FinDataChangeLog",
    # 财务统计报表模块
    "FinCashFlow",
    "FinReceivableStat",
    "FinTaxStat",
    "FinCommissionStat",
    "FinCashFlowStatement",
    "FinProfitStatement",
    "FinBalanceSheet",
    "FinFinancialReport",
]
