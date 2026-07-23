"""
房地产SaaS财务管理系统 - Finance模块包初始化

模块结构：
- models: 数据模型层，定义数据库表映射
- schemas: 数据校验层，定义请求/响应数据结构
- dao: 数据访问层，封装数据库操作
- service: 业务逻辑层，实现核心业务逻辑
- router: API路由层，定义RESTful接口

功能模块：
1. 财务基础档案（archive）
2. 房款收支管理（payment）
3. 票据税务合规（invoice）
4. 佣金支付管理（commission）
5. 项目成本管理（cost）
6. 应收应付往来台账（ar_ap）
7. 资金对账管理（reconciliation）
8. 会计凭证管理（voucher）
9. 财务审计追溯（audit）
10. 财务统计报表（report）
"""

# 导入子模块
from . import model as models
from . import schemas
from . import dao
from . import service
from . import router

# 版本信息
__version__ = "1.0.0"
__author__ = "Real Estate SaaS Team"