"""
房地产SaaS财务管理系统 - Finance模块DAO包初始化
"""

# 财务基础档案模块DAO
from .finance_dao import (
    FinProjectFinConfigDAO,
    FinAccountDAO,
    FinSubjectDAO,
    FinTaxRateDAO,
    FinBankInfoDAO,
    FinDiscountRuleDAO,
)

# 房款收支模块DAO
from .finance_dao import (
    FinInstallmentPlanDAO,
    FinPriceDiffDAO,
    FinReceiptRecordDAO,
    FinRefundRecordDAO,
    FinDepositAccountDAO,
)

# 票据税务合规模块DAO
from .finance_dao import (
    FinInvoiceDAO,
    FinInvoiceRedDAO,
    FinReceiptDAO,
    FinMaintainFundDAO,
    FinTaxDeclareDAO,
)

# 佣金支付模块DAO
from .finance_dao_ext import (
    FinCommissionPayDAO,
    FinCommissionDeductDAO,
    FinSalesCommissionDAO,
)

# 项目成本模块DAO
from .finance_dao_ext import (
    FinCostExpenseDAO,
    FinExpenseReimbursementDAO,
    FinCostPayDAO,
    FinAdCostDAO,
    FinProjectEngCostDAO,
)

# 应收应付往来台账模块DAO
from .finance_dao_ext import (
    FinAccountReceivableDAO,
    FinAccountPayableDAO,
    FinAdvancePayDAO,
    FinOtherLoanDAO,
)

# 资金对账模块DAO
from .finance_dao_ext import (
    FinBankCheckDAO,
    FinDailyCashAccountDAO,
    FinChannelReconcileDAO,
)

# 会计凭证模块DAO
from .finance_dao_ext import (
    FinVoucherDAO,
    FinVoucherItemDAO,
)

# 财务审计追溯模块DAO
from .finance_dao_ext import (
    FinOperateLogDAO,
    FinDataChangeLogDAO,
)

# 财务统计报表模块DAO
from .finance_dao_ext import (
    FinCashFlowDAO,
    FinReceivableStatDAO,
    FinTaxStatDAO,
    FinCommissionStatDAO,
    FinCashFlowStatementDAO,
    FinProfitStatementDAO,
    FinBalanceSheetDAO,
    FinFinancialReportDAO,
)

__all__ = [
    # 财务基础档案模块
    'FinProjectFinConfigDAO',
    'FinAccountDAO',
    'FinSubjectDAO',
    'FinTaxRateDAO',
    'FinBankInfoDAO',
    'FinDiscountRuleDAO',
    # 房款收支模块
    'FinInstallmentPlanDAO',
    'FinPriceDiffDAO',
    'FinReceiptRecordDAO',
    'FinRefundRecordDAO',
    'FinDepositAccountDAO',
    # 票据税务合规模块
    'FinInvoiceDAO',
    'FinInvoiceRedDAO',
    'FinReceiptDAO',
    'FinMaintenanceFundDAO',
    'FinTaxDeclareDAO',
    # 佣金支付模块
    'FinCommissionPayDAO',
    'FinCommissionDeductDAO',
    'FinSalesCommissionDAO',
    # 项目成本模块
    'FinCostExpenseDAO',
    'FinExpenseReimbursementDAO',
    'FinCostPayDAO',
    'FinAdCostDAO',
    'FinProjectEngCostDAO',
    # 应收应付往来台账模块
    'FinAccountReceivableDAO',
    'FinAccountPayableDAO',
    'FinAdvancePayDAO',
    'FinOtherLoanDAO',
    # 资金对账模块
    'FinBankCheckDAO',
    'FinDailyCashAccountDAO',
    'FinChannelReconcileDAO',
    # 会计凭证模块
    'FinVoucherDAO',
    'FinVoucherItemDAO',
    # 财务审计追溯模块
    'FinOperateLogDAO',
    'FinDataChangeLogDAO',
    # 财务统计报表模块
    'FinCashFlowDAO',
    'FinReceivableStatDAO',
    'FinTaxStatDAO',
    'FinCommissionStatDAO',
    'FinCashFlowStatementDAO',
    'FinProfitStatementDAO',
    'FinBalanceSheetDAO',
    'FinFinancialReportDAO',
]