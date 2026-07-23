"""
房地产SaaS财务管理系统 - Finance模块Schemas包初始化
"""

# 基础模型
from .base_schemas import (
    PageRequest,
    PageResponse,
    ApiResponse
)

# 财务基础档案模块
from .archive_schemas import (
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
    DiscountRuleResponse
)

# 房款收支模块
from .payment_schemas import (
    InstallmentPlanCreate,
    InstallmentPlanUpdate,
    InstallmentPlanResponse,
    PriceDiffCreate,
    PriceDiffUpdate,
    PriceDiffResponse,
    ReceiptRecordCreate,
    ReceiptRecordUpdate,
    ReceiptRecordResponse,
    RefundRecordCreate,
    RefundRecordResponse,
    DepositAccountCreate,
    DepositAccountUpdate,
    DepositAccountResponse
)

# 票据税务合规模块
from .invoice_schemas import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceRedCreate,
    InvoiceRedResponse,
    ReceiptCreate,
    ReceiptResponse,
    MaintenanceFundCreate,
    MaintenanceFundUpdate,
    MaintenanceFundResponse,
    TaxDeclareCreate,
    TaxDeclareUpdate,
    TaxDeclareResponse
)

# 佣金支付模块
from .commission_schemas import (
    CommissionPayCreate,
    CommissionPayUpdate,
    CommissionPayResponse,
    CommissionDeductCreate,
    CommissionDeductResponse,
    SalesBonusPayCreate,
    SalesBonusPayUpdate,
    SalesBonusPayResponse
)

# 项目成本模块
from .cost_schemas import (
    CostExpenseCreate,
    CostExpenseUpdate,
    CostExpenseResponse,
    CostPayCreate,
    CostPayUpdate,
    CostPayResponse,
    AdCostCreate,
    AdCostUpdate,
    AdCostResponse,
    ProjectEngCostCreate,
    ProjectEngCostUpdate,
    ProjectEngCostResponse
)

# 应收应付往来台账模块
from .ar_ap_schemas import (
    AccountReceivableCreate,
    AccountReceivableUpdate,
    AccountReceivableResponse,
    AccountPayableCreate,
    AccountPayableUpdate,
    AccountPayableResponse,
    AdvancePayCreate,
    AdvancePayUpdate,
    AdvancePayResponse,
    OtherLoanCreate,
    OtherLoanResponse
)

# 资金对账模块
from .reconciliation_schemas import (
    BankCheckCreate,
    BankCheckUpdate,
    BankCheckResponse,
    DailyCashAccountCreate,
    DailyCashAccountUpdate,
    DailyCashAccountResponse,
    ChannelReconcileCreate,
    ChannelReconcileUpdate,
    ChannelReconcileResponse
)

# 会计凭证模块
from .voucher_schemas import (
    VoucherCreate,
    VoucherUpdate,
    VoucherResponse,
    VoucherItemCreate,
    VoucherItemResponse,
    VoucherWithItemsResponse
)

# 财务审计追溯模块
from .audit_schemas import (
    OperateLogCreate,
    OperateLogUpdate,
    OperateLogResponse
)

# 财务统计报表模块
from .report_schemas import (
    CashFlowResponse,
    ReceivableStatResponse,
    TaxStatResponse,
    CommissionStatResponse,
    ReportQuery
)

__all__ = [
    # 基础模型
    'PageRequest',
    'PageResponse',
    'ApiResponse',
    # 财务基础档案
    'ProjectFinConfigCreate',
    'ProjectFinConfigUpdate',
    'ProjectFinConfigResponse',
    'AccountCreate',
    'AccountUpdate',
    'AccountResponse',
    'SubjectCreate',
    'SubjectUpdate',
    'SubjectResponse',
    'TaxRateCreate',
    'TaxRateUpdate',
    'TaxRateResponse',
    'BankInfoCreate',
    'BankInfoUpdate',
    'BankInfoResponse',
    'DiscountRuleCreate',
    'DiscountRuleUpdate',
    'DiscountRuleResponse',
    # 房款收支
    'InstallmentPlanCreate',
    'InstallmentPlanUpdate',
    'InstallmentPlanResponse',
    'PriceDiffCreate',
    'PriceDiffUpdate',
    'PriceDiffResponse',
    'ReceiptRecordCreate',
    'ReceiptRecordUpdate',
    'ReceiptRecordResponse',
    'RefundRecordCreate',
    'RefundRecordResponse',
    'DepositAccountCreate',
    'DepositAccountUpdate',
    'DepositAccountResponse',
    # 票据税务合规
    'InvoiceCreate',
    'InvoiceUpdate',
    'InvoiceResponse',
    'InvoiceRedCreate',
    'InvoiceRedResponse',
    'ReceiptCreate',
    'ReceiptResponse',
    'MaintenanceFundCreate',
    'MaintenanceFundUpdate',
    'MaintenanceFundResponse',
    'TaxDeclareCreate',
    'TaxDeclareUpdate',
    'TaxDeclareResponse',
    # 佣金支付
    'CommissionPayCreate',
    'CommissionPayUpdate',
    'CommissionPayResponse',
    'CommissionDeductCreate',
    'CommissionDeductResponse',
    'SalesBonusPayCreate',
    'SalesBonusPayUpdate',
    'SalesBonusPayResponse',
    # 项目成本
    'CostExpenseCreate',
    'CostExpenseUpdate',
    'CostExpenseResponse',
    'CostPayCreate',
    'CostPayUpdate',
    'CostPayResponse',
    'AdCostCreate',
    'AdCostUpdate',
    'AdCostResponse',
    'ProjectEngCostCreate',
    'ProjectEngCostUpdate',
    'ProjectEngCostResponse',
    # 应收应付往来台账
    'AccountReceivableCreate',
    'AccountReceivableUpdate',
    'AccountReceivableResponse',
    'AccountPayableCreate',
    'AccountPayableUpdate',
    'AccountPayableResponse',
    'AdvancePayCreate',
    'AdvancePayUpdate',
    'AdvancePayResponse',
    'OtherLoanCreate',
    'OtherLoanResponse',
    # 资金对账
    'BankCheckCreate',
    'BankCheckUpdate',
    'BankCheckResponse',
    'DailyCashAccountCreate',
    'DailyCashAccountUpdate',
    'DailyCashAccountResponse',
    'ChannelReconcileCreate',
    'ChannelReconcileUpdate',
    'ChannelReconcileResponse',
    # 会计凭证
    'VoucherCreate',
    'VoucherUpdate',
    'VoucherResponse',
    'VoucherItemCreate',
    'VoucherItemResponse',
    'VoucherWithItemsResponse',
    # 财务审计追溯
    'OperateLogCreate',
    'OperateLogUpdate',
    'OperateLogResponse',
    # 财务统计报表
    'CashFlowResponse',
    'ReceivableStatResponse',
    'TaxStatResponse',
    'CommissionStatResponse',
    'ReportQuery'
]