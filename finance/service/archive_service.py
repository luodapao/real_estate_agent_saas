﻿"""
房地产SaaS财务管理系统 - 财务基础档案服务层
"""
import time
import random
from typing import List, Optional
from sqlalchemy.orm import Session
from ..dao import (
    FinProjectFinConfigDAO,
    FinAccountDAO,
    FinSubjectDAO,
    FinTaxRateDAO,
    FinBankInfoDAO,
    FinDiscountRuleDAO,
)
from ..schemas.archive_schemas import (
    ProjectFinConfigCreate,
    ProjectFinConfigUpdate,
    ProjectFinConfigResponse,
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    TaxRateCreate,
    TaxRateUpdate,
    TaxRateResponse,
    BankInfoCreate,
    BankInfoUpdate,
    BankInfoResponse,
    DiscountRuleCreate,
    DiscountRuleUpdate,
    DiscountRuleResponse,
)
from ..schemas.base_schemas import PageRequest, PageResponse


class ArchiveService:
    """财务基础档案服务类"""

    @staticmethod
    def _generate_account_code() -> str:
        """生成账户编码 - ACC + 时间戳 + 随机数"""
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(100, 999)
        return f"ACC{timestamp}{random_suffix}"

    @staticmethod
    def _generate_subject_code() -> str:
        """生成科目编码 - SUB + 时间戳 + 随机数"""
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(100, 999)
        return f"SUB{timestamp}{random_suffix}"

    @staticmethod
    def _generate_tax_code() -> str:
        """生成税率编码 - TAX + 时间戳 + 随机数"""
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(100, 999)
        return f"TAX{timestamp}{random_suffix}"

    @staticmethod
    def _generate_bank_info_code() -> str:
        """生成银行信息编码 - BNK + 时间戳 + 随机数"""
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(100, 999)
        return f"BNK{timestamp}{random_suffix}"

    @staticmethod
    def _generate_discount_code() -> str:
        """生成优惠规则编码 - DIS + 时间戳 + 随机数"""
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(100, 999)
        return f"DIS{timestamp}{random_suffix}"

    @staticmethod
    def create_project_fin_config(db: Session, tenant_id: int, data: ProjectFinConfigCreate, create_user_id: int = 1) -> ProjectFinConfigResponse:
        """创建项目财务配置"""
        data_dict = data.model_dump()
        data_dict['tenant'] = tenant_id
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinProjectFinConfigDAO.create(db, data_dict)
        return ProjectFinConfigResponse.from_orm(entity)

    @staticmethod
    def get_project_fin_config(db: Session, tenant_id: int, id: int) -> Optional[ProjectFinConfigResponse]:
        """获取项目财务配置详情"""
        entity = FinProjectFinConfigDAO.get_by_id(db, id, tenant_id)
        return ProjectFinConfigResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_project_fin_config(db: Session, tenant_id: int, id: int, data: ProjectFinConfigUpdate) -> Optional[ProjectFinConfigResponse]:
        """更新项目财务配置"""
        record = FinProjectFinConfigDAO.get_by_id(db, id, tenant_id)
        if not record:
            return None
        entity = FinProjectFinConfigDAO.update(db, record, data.model_dump(exclude_unset=True))
        return ProjectFinConfigResponse.from_orm(entity)

    @staticmethod
    def delete_project_fin_config(db: Session, tenant_id: int, id: int) -> bool:
        """删除项目财务配置"""
        return FinProjectFinConfigDAO.delete(db, id, tenant_id)

    @staticmethod
    def list_project_fin_config(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[ProjectFinConfigResponse]:
        """分页查询项目财务配置列表"""
        skip = (page_request.page - 1) * page_request.page_size
        items = FinProjectFinConfigDAO.get_list(db, tenant_id, skip, page_request.page_size)
        return PageResponse(
            total=len(items),
            page=page_request.page,
            size=page_request.page_size,
            data=[ProjectFinConfigResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_account(db: Session, tenant_id: int, data: AccountCreate, create_user_id: int = 1) -> AccountResponse:
        """创建账户信息 - 自动生成账户编码"""
        data_dict = data.model_dump()
        data_dict['tenant'] = tenant_id
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        # 自动生成账户编码，不使用外部传参
        data_dict['account_code'] = ArchiveService._generate_account_code()
        entity = FinAccountDAO.create(db, data_dict)
        return AccountResponse.from_orm(entity)

    @staticmethod
    def get_account(db: Session, tenant_id: int, id: int) -> Optional[AccountResponse]:
        """获取账户详情"""
        entity = FinAccountDAO.get_by_id(db, id, tenant_id)
        return AccountResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_account(db: Session, tenant_id: int, id: int, data: AccountUpdate) -> Optional[AccountResponse]:
        """更新账户信息"""
        record = FinAccountDAO.get_by_id(db, id, tenant_id)
        if not record:
            return None
        entity = FinAccountDAO.update(db, record, data.model_dump(exclude_unset=True))
        return AccountResponse.from_orm(entity)

    @staticmethod
    def delete_account(db: Session, tenant_id: int, id: int) -> bool:
        """删除账户"""
        return FinAccountDAO.delete(db, id, tenant_id)

    @staticmethod
    def list_accounts(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[AccountResponse]:
        """分页查询账户列表"""
        skip = (page_request.page - 1) * page_request.page_size
        items = FinAccountDAO.get_list(db, tenant_id, skip, page_request.page_size)
        return PageResponse(
            total=len(items),
            page=page_request.page,
            size=page_request.page_size,
            data=[AccountResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_subject(db: Session, tenant_id: int, data: SubjectCreate, create_user_id: int = 1) -> SubjectResponse:
        """创建科目信息 - 自动生成科目编码"""
        data_dict = data.model_dump()
        data_dict['tenant'] = tenant_id
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        # 自动生成科目编码，不使用外部传参
        data_dict['subject_code'] = ArchiveService._generate_subject_code()
        entity = FinSubjectDAO.create(db, data_dict)
        return SubjectResponse.from_orm(entity)

    @staticmethod
    def get_subject(db: Session, tenant_id: int, id: int) -> Optional[SubjectResponse]:
        """获取科目详情"""
        entity = FinSubjectDAO.get_by_id(db, id, tenant_id)
        return SubjectResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_subject(db: Session, tenant_id: int, id: int, data: SubjectUpdate) -> Optional[SubjectResponse]:
        """更新科目信息"""
        record = FinSubjectDAO.get_by_id(db, id, tenant_id)
        if not record:
            return None
        entity = FinSubjectDAO.update(db, record, data.model_dump(exclude_unset=True))
        return SubjectResponse.from_orm(entity)

    @staticmethod
    def delete_subject(db: Session, tenant_id: int, id: int) -> bool:
        """删除科目"""
        return FinSubjectDAO.delete(db, id, tenant_id)

    @staticmethod
    def list_subjects(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[SubjectResponse]:
        """分页查询科目列表"""
        skip = (page_request.page - 1) * page_request.page_size
        items = FinSubjectDAO.get_list(db, tenant_id, skip, page_request.page_size)
        return PageResponse(
            total=len(items),
            page=page_request.page,
            size=page_request.page_size,
            data=[SubjectResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_tax_rate(db: Session, tenant_id: int, data: TaxRateCreate, create_user_id: int = 1) -> TaxRateResponse:
        """创建税率信息 - 自动生成税率编码"""
        data_dict = data.model_dump()
        data_dict['tenant'] = tenant_id
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        data_dict['tax_code'] = ArchiveService._generate_tax_code()
        data_dict['tax_name'] = data_dict.pop('tax_rate_name', '')
        data_dict['tax_rate'] = data_dict.pop('rate_value', 0.0)
        data_dict.pop('tax_rate_code', None)
        entity = FinTaxRateDAO.create(db, data_dict)
        return TaxRateResponse.from_orm(entity)

    @staticmethod
    def get_tax_rate(db: Session, tenant_id: int, id: int) -> Optional[TaxRateResponse]:
        """获取税率详情"""
        entity = FinTaxRateDAO.get_by_id(db, id, tenant_id)
        return TaxRateResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_tax_rate(db: Session, tenant_id: int, id: int, data: TaxRateUpdate) -> Optional[TaxRateResponse]:
        """更新税率信息"""
        record = FinTaxRateDAO.get_by_id(db, id, tenant_id)
        if not record:
            return None
        entity = FinTaxRateDAO.update(db, record, data.model_dump(exclude_unset=True))
        return TaxRateResponse.from_orm(entity)

    @staticmethod
    def delete_tax_rate(db: Session, tenant_id: int, id: int) -> bool:
        """删除税率"""
        return FinTaxRateDAO.delete(db, id, tenant_id)

    @staticmethod
    def list_tax_rates(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[TaxRateResponse]:
        """分页查询税率列表"""
        skip = (page_request.page - 1) * page_request.page_size
        items = FinTaxRateDAO.get_list(db, tenant_id, skip, page_request.page_size)
        return PageResponse(
            total=len(items),
            page=page_request.page,
            size=page_request.page_size,
            data=[TaxRateResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_bank_info(db: Session, tenant_id: int, data: BankInfoCreate, create_user_id: int = 1) -> BankInfoResponse:
        """创建银行信息 - 自动生成银行档案编码"""
        data_dict = data.model_dump()
        data_dict['tenant'] = tenant_id
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        # 自动生成银行档案编码，不使用外部传参
        data_dict['bank_info_code'] = ArchiveService._generate_bank_info_code()
        entity = FinBankInfoDAO.create(db, data_dict)
        return BankInfoResponse.from_orm(entity)

    @staticmethod
    def get_bank_info(db: Session, tenant_id: int, id: int) -> Optional[BankInfoResponse]:
        """获取银行信息详情"""
        entity = FinBankInfoDAO.get_by_id(db, id, tenant_id)
        return BankInfoResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_bank_info(db: Session, tenant_id: int, id: int, data: BankInfoUpdate) -> Optional[BankInfoResponse]:
        """更新银行信息"""
        record = FinBankInfoDAO.get_by_id(db, id, tenant_id)
        if not record:
            return None
        entity = FinBankInfoDAO.update(db, record, data.model_dump(exclude_unset=True))
        return BankInfoResponse.from_orm(entity)

    @staticmethod
    def delete_bank_info(db: Session, tenant_id: int, id: int) -> bool:
        """删除银行信息"""
        return FinBankInfoDAO.delete(db, id, tenant_id)

    @staticmethod
    def list_bank_info(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[BankInfoResponse]:
        """分页查询银行信息列表"""
        skip = (page_request.page - 1) * page_request.page_size
        items = FinBankInfoDAO.get_list(db, tenant_id, skip, page_request.page_size)
        return PageResponse(
            total=len(items),
            page=page_request.page,
            size=page_request.page_size,
            data=[BankInfoResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_discount_rule(db: Session, tenant_id: int, data: DiscountRuleCreate, create_user_id: int = 1) -> DiscountRuleResponse:
        """创建优惠规则 - 自动生成优惠规则编码"""
        data_dict = data.model_dump()
        data_dict['tenant'] = tenant_id
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        # 自动生成优惠规则编码，不使用外部传参
        data_dict['discount_code'] = ArchiveService._generate_discount_code()
        entity = FinDiscountRuleDAO.create(db, data_dict)
        return DiscountRuleResponse.from_orm(entity)

    @staticmethod
    def get_discount_rule(db: Session, tenant_id: int, id: int) -> Optional[DiscountRuleResponse]:
        """获取优惠规则详情"""
        entity = FinDiscountRuleDAO.get_by_id(db, id, tenant_id)
        return DiscountRuleResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_discount_rule(db: Session, tenant_id: int, id: int, data: DiscountRuleUpdate) -> Optional[DiscountRuleResponse]:
        """更新优惠规则"""
        record = FinDiscountRuleDAO.get_by_id(db, id, tenant_id)
        if not record:
            return None
        entity = FinDiscountRuleDAO.update(db, record, data.model_dump(exclude_unset=True))
        return DiscountRuleResponse.from_orm(entity)

    @staticmethod
    def delete_discount_rule(db: Session, tenant_id: int, id: int) -> bool:
        """删除优惠规则"""
        return FinDiscountRuleDAO.delete(db, id, tenant_id)

    @staticmethod
    def list_discount_rules(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[DiscountRuleResponse]:
        """分页查询优惠规则列表"""
        skip = (page_request.page - 1) * page_request.page_size
        items = FinDiscountRuleDAO.get_list(db, tenant_id, skip, page_request.page_size)
        return PageResponse(
            total=len(items),
            page=page_request.page,
            size=page_request.page_size,
            data=[DiscountRuleResponse.from_orm(item) for item in items]
        )
