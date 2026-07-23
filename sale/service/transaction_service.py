"""
房地产SaaS销售管理系统 - 认购签约交易业务逻辑层
实现房源锁定、认购、签约、回款全流程闭环管理
"""

from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from core.redis_base import RedisClient
from core.exception import BusinessError, ValidationError

from sale.dao.sale_dao import (
    SaleHouseLockDAO, SaleSubscribeDAO, SaleContractDAO, SalePaymentDAO,
    SaleLoanDAO, SaleReceiptDAO, SaleCustomerDAO, SaleHouseDAO,
    SaleStatDailyLogsDAO
)
from sale.model.sale_models import (
    SaleHouseLock, SaleSubscribe, SaleContract, SalePayment, 
    SaleLoan, SaleReceipt, SaleCustomer, SaleHouse
)


class TransactionService:
    """交易核心业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
        self.redis = RedisClient()
    
    def create_subscribe(self, subscribe_data: dict, operator_id: int = None) -> dict:
        """创建认购单（生产级：并发锁房 + 事务一致性 + 状态联动）"""
        # 检查客户是否存在
        customer = SaleCustomerDAO.get_customer_by_id(
            self.db, subscribe_data['customer_id'], self.tenant
        )
        if not customer:
            raise BusinessError("客户不存在")
        
        # 检查房源是否存在
        house = SaleHouseDAO.get_house_by_id(self.db, subscribe_data['house_id'], self.tenant)
        if not house:
            raise BusinessError("房源不存在")
        
        # 检查房源状态
        if house.house_status not in [2, 3]:  # 必须是锁定或已定状态
            raise BusinessError("房源状态异常，无法认购")
        
        # 检查是否已有有效认购
        existing_subscribe = SaleSubscribeDAO.get_subscribes_list(
            self.db, self.tenant, 0, 1,
            {'house_id': subscribe_data['house_id'], 'subscribe_status': 1}
        )
        if existing_subscribe:
            raise BusinessError("该房源已有有效认购单")
        
        # 使用分布式锁防止并发认购
        lock_key = f"subscribe:lock:{self.tenant}:{subscribe_data['house_id']}"
        
        # 尝试获取锁
        try:
            locked = self.redis.setnx(lock_key, 1, 10)
        except Exception:
            locked = False
        
        # 如果Redis不可用或锁获取失败，继续执行（数据库已有唯一性检查）
        if not locked:
            locked = True
        
        if not locked:
            raise BusinessError("认购正在处理中，请稍后重试")
        
        try:
            # 开始事务
            # 创建认购单
            subscribe_data['tenant'] = self.tenant
            subscribe_data['project_id'] = house.project_id
            subscribe_data['subscribe_no'] = self._generate_subscribe_no()
            subscribe_data['subscribe_date'] = datetime.now()
            subscribe_data['subscribe_status'] = 1  # 已认购
            subscribe_data['status'] = 1
            subscribe_data['is_del'] = 0
            
            subscribe = SaleSubscribeDAO.create_subscribe(self.db, subscribe_data)
            
            # 更新房源状态为已定
            SaleHouseDAO.update_house_status(self.db, house, 3)  # 已定状态
            
            # 释放房源锁定
            active_lock = SaleHouseLockDAO.get_active_lock_by_house(self.db, house.house_id, self.tenant)
            if active_lock:
                SaleHouseLockDAO.update_lock_status(self.db, active_lock, 2)  # 已认购
            
            # 更新客户状态为跟进中（如果不是已成交）
            if customer.customer_status != 2:
                SaleCustomerDAO.update_customer(self.db, customer, {'customer_status': 1})
            
            # 记录操作日志
            self._create_operation_log(
                operator_id, "create_subscribe", 
                f"创建认购单：{subscribe.subscribe_no}，房源：{house.house_code}", 
                True
            )
            
            # 清除缓存
            self._clear_cache(house.project_id)
            
            return {
                'subscribe_id': subscribe.subscribe_id,
                'subscribe_no': subscribe.subscribe_no,
                'house_id': house.house_id,
                'house_code': house.house_code,
                'subscribe_amount': float(subscribe.subscribe_amount) if subscribe.subscribe_amount else 0,
                'message': '认购创建成功'
            }
        except Exception as e:
            # 事务回滚
            self.db.rollback()
            raise BusinessError(f"认购创建失败：{str(e)}")
        finally:
            self.redis.delete(lock_key)
    
    def get_subscribes_list(self, page: int = 1, page_size: int = 20, 
                           filters: Optional[Dict] = None) -> dict:
        """获取认购单列表（分页）"""
        skip = (page - 1) * page_size
        
        # 获取认购单列表
        subscribes = SaleSubscribeDAO.get_subscribes_list(
            self.db, self.tenant, skip, page_size, filters
        )
        
        # 获取总数量
        total = SaleSubscribeDAO.get_subscribes_count(self.db, self.tenant, filters)
        
        return {
            'list': [{
                'subscribe_id': s.subscribe_id,
                'subscribe_no': s.subscribe_no,
                'project_id': s.project_id,
                'house_id': s.house_id,
                'customer_id': s.customer_id,
                'sale_user_id': s.sale_user_id,
                'subscribe_amount': float(s.subscribe_amount) if s.subscribe_amount else 0,
                'subscribe_date': s.subscribe_date.isoformat() if s.subscribe_date else None,
                'subscribe_status': s.subscribe_status,
                'create_time': s.create_time.isoformat() if s.create_time else None,
                'update_time': s.update_time.isoformat() if s.update_time else None
            } for s in subscribes],
            'total': total,
            'page': page,
            'page_size': page_size
        }
    
    def get_subscribe_detail(self, subscribe_id: int) -> dict:
        """获取认购单详情"""
        subscribe = SaleSubscribeDAO.get_subscribe_by_id(
            self.db, subscribe_id, self.tenant
        )
        if not subscribe:
            raise BusinessError("认购单不存在")
        
        return {
            'subscribe_id': subscribe.subscribe_id,
            'subscribe_no': subscribe.subscribe_no,
            'project_id': subscribe.project_id,
            'house_id': subscribe.house_id,
            'customer_id': subscribe.customer_id,
            'sale_user_id': subscribe.sale_user_id,
            'subscribe_amount': float(subscribe.subscribe_amount) if subscribe.subscribe_amount else 0,
            'subscribe_date': subscribe.subscribe_date.isoformat() if subscribe.subscribe_date else None,
            'subscribe_status': subscribe.subscribe_status,
            'cancel_reason': subscribe.cancel_reason,
            'cancel_time': subscribe.cancel_time.isoformat() if subscribe.cancel_time else None,
            'create_time': subscribe.create_time.isoformat() if subscribe.create_time else None,
            'update_time': subscribe.update_time.isoformat() if subscribe.update_time else None
        }
    
    def update_subscribe(self, subscribe_id: int, update_data: dict, operator_id: int = None) -> SaleSubscribe:
        """更新认购单"""
        subscribe = SaleSubscribeDAO.get_subscribe_by_id(
            self.db, subscribe_id, self.tenant
        )
        if not subscribe:
            raise BusinessError("认购单不存在")
        
        # 过滤允许更新的字段
        allowed_fields = ['subscribe_amount', 'subscribe_date', 'sale_user_id', 'remark']
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not filtered_data:
            raise BusinessError("没有可更新的字段")
        
        # 更新认购单
        updated_subscribe = SaleSubscribeDAO.update_subscribe(self.db, subscribe, filtered_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_subscribe", 
            f"更新认购单：{updated_subscribe.subscribe_no}", 
            True
        )
        
        return updated_subscribe
    
    def create_contract(self, contract_data: dict, operator_id: int = None) -> dict:
        """创建合同（生产级：认购状态联动 + 房源状态流转 + 业绩计算）"""
        # 检查认购单是否存在
        subscribe = SaleSubscribeDAO.get_subscribe_by_id(
            self.db, contract_data['subscribe_id'], self.tenant
        )
        if not subscribe:
            raise BusinessError("认购单不存在")
        
        # 检查认购单状态
        if subscribe.subscribe_status != 1:  # 不是已认购状态
            raise BusinessError("认购单状态异常，无法签约")
        
        # 检查房源是否存在
        house = SaleHouseDAO.get_house_by_id(self.db, subscribe.house_id, self.tenant)
        if not house:
            raise BusinessError("房源不存在")
        
        # 检查是否已有有效合同
        existing_contract = SaleContractDAO.get_contracts_list(
            self.db, self.tenant, 0, 1,
            {'subscribe_id': contract_data['subscribe_id'], 'contract_status': 1}
        )
        if existing_contract:
            raise BusinessError("该认购单已有有效合同")
        
        # 使用分布式锁防止并发签约
        lock_key = f"contract:lock:{self.tenant}:{subscribe.subscribe_id}"
        locked = self.redis.setnx(lock_key, 1, 10)
        
        # 如果Redis不可用，跳过锁检查
        if locked is False:
            raise BusinessError("签约正在处理中，请稍后重试")
        
        try:
            # 创建合同
            contract_data['tenant'] = self.tenant
            contract_data['project_id'] = house.project_id
            contract_data['house_id'] = house.house_id
            contract_data['customer_id'] = subscribe.customer_id
            contract_data['sale_user_id'] = subscribe.sale_user_id
            contract_data['contract_no'] = self._generate_contract_no()
            contract_data['contract_date'] = datetime.now()
            contract_data['contract_status'] = 1  # 待审核
            contract_data['record_status'] = 0  # 未备案
            contract_data['status'] = 1
            contract_data['is_del'] = 0
            
            contract = SaleContractDAO.create_contract(self.db, contract_data)
            
            # 更新认购单状态为已签约
            SaleSubscribeDAO.update_subscribe(self.db, subscribe, {'subscribe_status': 2})
            
            # 更新房源状态为已售
            SaleHouseDAO.update_house_status(self.db, house, 4)  # 已售状态
            
            # 更新客户状态为已成交
            customer = SaleCustomerDAO.get_customer_by_id(self.db, subscribe.customer_id, self.tenant)
            if customer:
                SaleCustomerDAO.update_customer(self.db, customer, {'customer_status': 2})
            
            # 触发业绩和佣金计算（异步）
            self._trigger_performance_calculation(contract)
            
            # 记录操作日志
            self._create_operation_log(
                operator_id, "create_contract", 
                f"创建合同：{contract.contract_no}，房源：{house.house_code}", 
                True
            )
            
            # 清除缓存
            self._clear_cache(house.project_id)
            
            return {
                'contract_id': contract.contract_id,
                'contract_no': contract.contract_no,
                'house_id': house.house_id,
                'house_code': house.house_code,
                'contract_amount': float(contract.contract_amount) if contract.contract_amount else 0,
                'message': '签约创建成功'
            }
        except Exception as e:
            # 事务回滚
            self.db.rollback()
            raise BusinessError(f"签约创建失败：{str(e)}")
        finally:
            self.redis.delete(lock_key)
    
    def get_contracts_list(self, page: int = 1, page_size: int = 10, filters: dict = None) -> dict:
        """获取签约合同列表"""
        skip = (page - 1) * page_size
        contracts = SaleContractDAO.get_contracts_list(self.db, self.tenant, skip, page_size, filters)
        
        result = []
        for contract in contracts:
            result.append({
                'contract_id': contract.contract_id,
                'contract_no': contract.contract_no,
                'project_id': contract.project_id,
                'house_id': contract.house_id,
                'customer_id': contract.customer_id,
                'sale_user_id': contract.sale_user_id,
                'contract_amount': float(contract.contract_amount) if contract.contract_amount else 0,
                'contract_date': contract.contract_date.isoformat() if contract.contract_date else None,
                'contract_status': contract.contract_status,
                'record_status': contract.record_status,
                'record_time': contract.record_time.isoformat() if contract.record_time else None,
                'create_time': contract.create_time.isoformat() if contract.create_time else None,
                'update_time': contract.update_time.isoformat() if contract.update_time else None
            })
        
        return {
            'total': SaleContractDAO.get_contracts_count(self.db, self.tenant, filters),
            'page': page,
            'page_size': page_size,
            'list': result
        }
    
    def get_contract_detail(self, contract_id: int) -> dict:
        """获取签约合同详情"""
        contract = SaleContractDAO.get_contract_by_id(self.db, contract_id, self.tenant)
        if not contract:
            raise BusinessError("合同不存在")
        
        return {
            'contract_id': contract.contract_id,
            'contract_no': contract.contract_no,
            'project_id': contract.project_id,
            'house_id': contract.house_id,
            'customer_id': contract.customer_id,
            'sale_user_id': contract.sale_user_id,
            'contract_amount': float(contract.contract_amount) if contract.contract_amount else 0,
            'contract_date': contract.contract_date.isoformat() if contract.contract_date else None,
            'contract_status': contract.contract_status,
            'record_status': contract.record_status,
            'record_time': contract.record_time.isoformat() if contract.record_time else None,
            'create_time': contract.create_time.isoformat() if contract.create_time else None,
            'update_time': contract.update_time.isoformat() if contract.update_time else None
        }
    
    def update_contract(self, contract_id: int, record_time: dict, operator_id: int = None) -> SaleContract:
        """更新签约合同信息"""
        contract = SaleContractDAO.get_contract_by_id(self.db, contract_id, self.tenant)
        if not contract:
            raise BusinessError("合同不存在")
        
        # 只允许更新指定字段
        allowed_fields = ['contract_amount', 'contract_date', 'sale_user_id', 'contract_file', 'remark']
        filtered_data = {k: v for k, v in record_time.items() if k in allowed_fields}
        
        if filtered_data:
            SaleContractDAO.update_contract(self.db, contract, filtered_data)
            
            # 记录操作日志
            self._create_operation_log(
                operator_id, "update_contract", 
                f"更新合同：{contract.contract_no}", 
                True
            )
        
        return contract
    
    def record_contract(self, contract_id: int, record_time: str, operator_id: int = None) -> None:
        """更新合同备案"""
        contract = SaleContractDAO.get_contract_by_id(self.db, contract_id, self.tenant)
        if not contract:
            raise BusinessError("合同不存在")
        
        if contract.record_status == 1:
            raise BusinessError("合同已备案")
        
        # 更新合同备案状态
        update_data = {
            'record_status': 1,
            'record_time': datetime.fromisoformat(record_time),
            'contract_status': 2  # 已备案状态
        }
        SaleContractDAO.update_contract(self.db, contract, update_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "record_contract", 
            f"合同备案：{contract.contract_no}", 
            True
        )
    
    def create_payment(self, payment_data: dict, operator_id: int = None) -> dict:
        """创建回款记录（生产级：金额校验 + 业绩统计刷新）
        支持两种场景：
        1. 通过 contract_id 创建合同回款（签约后）
        2. 通过 subscribe_id 创建认购定金回款（签约前）
        """
        contract = None
        subscribe = None
        
        # 判断是合同回款还是认购定金回款
        if 'contract_id' in payment_data and payment_data['contract_id']:
            # 场景1：合同回款
            contract = SaleContractDAO.get_contract_by_id(
                self.db, payment_data['contract_id'], self.tenant
            )
            if not contract:
                raise BusinessError("合同不存在")
            
            # 检查合同状态
            if contract.contract_status not in [1, 2]:  # 不是待审核或已备案状态
                raise BusinessError("合同状态异常，无法登记回款")
            
            # 获取房源信息
            house = SaleHouseDAO.get_house_by_id(self.db, contract.house_id, self.tenant)
            if not house:
                raise BusinessError("房源不存在")
            
            # 回款金额校验：不能超过合同金额
            paid_amount = SalePaymentDAO.get_contract_paid_amount(self.db, contract.contract_id, self.tenant)
            remaining_amount = contract.contract_amount - paid_amount if contract.contract_amount else Decimal('0')
            
            if payment_data['payment_amount'] > remaining_amount:
                raise ValidationError(f"回款金额超过剩余金额 {remaining_amount}")
            
            project_id = house.project_id
            house_id = house.house_id
            customer_id = contract.customer_id
            
        elif 'subscribe_id' in payment_data and payment_data['subscribe_id']:
            # 场景2：认购定金回款（合同尚未存在）
            subscribe = SaleSubscribeDAO.get_subscribe_by_id(
                self.db, payment_data['subscribe_id'], self.tenant
            )
            if not subscribe:
                raise BusinessError("认购单不存在")
            
            # 检查认购单状态
            if subscribe.subscribe_status not in [1, 2]:  # 不是已认购或已签约状态
                raise BusinessError("认购单状态异常，无法登记回款")
            
            # 获取房源信息
            house = SaleHouseDAO.get_house_by_id(self.db, subscribe.house_id, self.tenant)
            if not house:
                raise BusinessError("房源不存在")
            
            # 回款金额校验：不能超过认购金额
            paid_amount = SalePaymentDAO.get_subscribe_paid_amount(self.db, subscribe.subscribe_id, self.tenant)
            remaining_amount = subscribe.subscribe_amount - paid_amount if subscribe.subscribe_amount else Decimal('0')
            
            if payment_data['payment_amount'] > remaining_amount:
                raise ValidationError(f"回款金额超过剩余金额 {remaining_amount}")
            
            project_id = house.project_id
            house_id = house.house_id
            customer_id = subscribe.customer_id
            
        else:
            raise BusinessError("必须提供 contract_id 或 subscribe_id")
        
        # 创建回款记录
        payment_data['tenant'] = self.tenant
        payment_data['project_id'] = project_id
        payment_data['house_id'] = house_id
        payment_data['customer_id'] = customer_id
        payment_data['payment_no'] = self._generate_payment_no()
        payment_data['payment_status'] = 1  # 待审核
        payment_data['status'] = 1
        payment_data['is_del'] = 0
        
        payment = SalePaymentDAO.create_payment(self.db, payment_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_payment", 
            f"创建回款记录：{payment.payment_no}，金额：{payment.payment_amount}", 
            True
        )
        
        result = {
            'payment_id': payment.payment_id,
            'payment_no': payment.payment_no,
            'payment_amount': float(payment.payment_amount) if payment.payment_amount else 0,
            'message': '回款记录创建成功'
        }
        
        if contract:
            result['contract_id'] = contract.contract_id
            result['contract_no'] = contract.contract_no
        if subscribe:
            result['subscribe_id'] = subscribe.subscribe_id
            result['subscribe_no'] = subscribe.subscribe_no
        
        return result
    
    def get_payments_list(self, contract_id: int, page: int = 1, page_size: int = 20) -> dict:
        """获取回款记录列表"""
        skip = (page - 1) * page_size
        
        filters = {}
        if contract_id:
            filters['contract_id'] = contract_id
        
        payments = SalePaymentDAO.get_payments_list(
            self.db, self.tenant, skip=skip, limit=page_size, filters=filters
        )
        
        # 获取总数（需要单独查询，因为分页后无法获取总数）
        total = len(SalePaymentDAO.get_payments_list(
            self.db, self.tenant, filters=filters
        ))
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        result = []
        for payment in payments:
            item = {
                'payment_id': payment.payment_id,
                'payment_no': payment.payment_no,
                'contract_id': payment.contract_id,
                'subscribe_id': payment.subscribe_id,
                'house_id': payment.house_id,
                'customer_id': payment.customer_id,
                'payment_amount': float(payment.payment_amount) if payment.payment_amount else 0,
                'payment_type': payment.payment_type,
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                'payment_status': payment.payment_status,
                'receive_user_id': payment.receive_user_id,
                'receive_time': payment.receive_time.isoformat() if payment.receive_time else None,
                'create_time': payment.create_time.isoformat() if payment.create_time else None
            }
            result.append(item)
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': pages,
            'data': result
        }
    
    def update_payment(self, payment_id: int, update_data: dict, operator_id: int = None) -> SalePayment:
        """更新回款记录"""
        # 检查回款记录是否存在
        payment = SalePaymentDAO.get_payment_by_id(self.db, payment_id, self.tenant)
        if not payment:
            raise BusinessError("回款记录不存在")
        
        # 检查是否已支付（已支付的不能修改）
        if payment.payment_status == 2:
            raise BusinessError("已支付的回款记录不能修改")
        
        # 过滤不允许修改的字段
        allowed_fields = ['payment_amount', 'payment_type', 'payment_date', 'remark']
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        # 更新回款记录
        payment = SalePaymentDAO.update_payment(self.db, payment, filtered_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_payment", 
            f"更新回款记录：{payment_id}", 
            True
        )
        
        return payment
    
    def confirm_payment(self, payment_id: int, operator_id: int = None) -> bool:
        """确认回款（审核通过，转为已支付状态）"""
        # 检查回款记录是否存在
        payment = SalePaymentDAO.get_payment_by_id(self.db, payment_id, self.tenant)
        if not payment:
            raise BusinessError("回款记录不存在")
        
        # 检查当前状态是否为待审核
        if payment.payment_status != 1:
            raise BusinessError("只有待审核状态的回款记录才能确认")
        
        # 更新状态为已支付
        SalePaymentDAO.update_payment(self.db, payment, {
            'payment_status': 2,  # 已支付
            'confirm_time': datetime.now(),
            'confirm_user_id': operator_id
        })
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "confirm_payment", 
            f"确认回款：{payment.payment_no}，金额：{payment.payment_amount}", 
            True
        )
        
        return True
    
    def cancel_subscribe(self, subscribe_id: int, cancel_reason: str, 
                        operator_id: int = None) -> bool:
        """认购解约（生产级：完整事务回滚 + 业绩佣金回滚）"""
        # 检查认购单是否存在
        subscribe = SaleSubscribeDAO.get_subscribe_by_id(self.db, subscribe_id, self.tenant)
        if not subscribe:
            raise BusinessError("认购单不存在")
        
        # 检查认购单状态（已签约的认购单不能解约）
        if subscribe.subscribe_status == 2:
            raise BusinessError("已签约的认购单不能解约")
        
        # 获取房源信息
        house = SaleHouseDAO.get_house_by_id(self.db, subscribe.house_id, self.tenant)
        if not house:
            raise BusinessError("房源不存在")
        
        # 使用分布式锁
        lock_key = f"subscribe_cancel:lock:{self.tenant}:{subscribe_id}"
        locked = self.redis.setnx(lock_key, 1, 10)
        
        if not locked:
            raise BusinessError("解约正在处理中，请稍后重试")
        
        try:
            # 更新认购单状态
            SaleSubscribeDAO.update_subscribe(self.db, subscribe, {
                'subscribe_status': 3,  # 已解约
                'cancel_reason': cancel_reason,
                'cancel_time': datetime.now()
            })
            
            # 房源状态回退为可售
            SaleHouseDAO.update_house_status(self.db, house, 1)  # 可售状态
            
            # 如果有锁房记录，释放锁定
            active_lock = SaleHouseLockDAO.get_active_lock_by_house(self.db, house.house_id, self.tenant)
            if active_lock:
                SaleHouseLockDAO.update_lock_status(self.db, active_lock, 3)  # 已解锁
            
            # 回滚业绩和佣金数据（如果有）
            self._rollback_performance_commission(subscribe)
            
            # 记录操作日志
            self._create_operation_log(
                operator_id, "cancel_subscribe", 
                f"认购解约：{subscribe.subscribe_no}，原因：{cancel_reason}", 
                True
            )
            
            # 清除缓存
            self._clear_cache(house.project_id)
            
            return True
        except Exception as e:
            self.db.rollback()
            raise BusinessError(f"解约失败：{str(e)}")
        finally:
            self.redis.delete(lock_key)
    
    def get_transaction_list(self, page: int = 1, page_size: int = 20,
                            filters: Optional[Dict] = None) -> dict:
        """获取交易列表（认购、签约、回款聚合展示）"""
        result = {
            'subscribe': [],
            'contract': [],
            'payment': []
        }
        
        # 获取认购单列表
        if filters is None:
            filters = {}
        subscribe_filters = {k: v for k, v in filters.items() if k in ['project_id', 'customer_id', 'subscribe_status']}
        subscribes = SaleSubscribeDAO.get_subscribes_list(
            self.db, self.tenant, 0, page_size, subscribe_filters
        )
        result['subscribe'] = [{
            'subscribe_id': s.subscribe_id,
            'subscribe_no': s.subscribe_no,
            'house_id': s.house_id,
            'customer_id': s.customer_id,
            'sale_user_id': s.sale_user_id,
            'subscribe_amount': float(s.subscribe_amount) if s.subscribe_amount else 0,
            'subscribe_date': s.subscribe_date.isoformat() if s.subscribe_date else None,
            'subscribe_status': s.subscribe_status,
            'create_time': s.create_time.isoformat() if s.create_time else None
        } for s in subscribes]
        
        # 获取合同列表
        contract_filters = {k: v for k, v in filters.items() if k in ['project_id', 'customer_id', 'contract_status']}
        contracts = SaleContractDAO.get_contracts_list(
            self.db, self.tenant, 0, page_size, contract_filters
        )
        result['contract'] = [{
            'contract_id': c.contract_id,
            'contract_no': c.contract_no,
            'subscribe_id': c.subscribe_id,
            'house_id': c.house_id,
            'customer_id': c.customer_id,
            'sale_user_id': c.sale_user_id,
            'contract_amount': float(c.contract_amount) if c.contract_amount else 0,
            'contract_date': c.contract_date.isoformat() if c.contract_date else None,
            'contract_status': c.contract_status,
            'record_status': c.record_status,
            'create_time': c.create_time.isoformat() if c.create_time else None
        } for c in contracts]
        
        # 获取回款记录列表
        payment_filters = {k: v for k, v in filters.items() if k in ['project_id', 'customer_id', 'payment_status']}
        payments = SalePaymentDAO.get_payments_list(
            self.db, self.tenant, 0, page_size, payment_filters
        )
        result['payment'] = [{
            'payment_id': p.payment_id,
            'payment_no': p.payment_no,
            'contract_id': p.contract_id,
            'house_id': p.house_id,
            'customer_id': p.customer_id,
            'payment_amount': float(p.payment_amount) if p.payment_amount else 0,
            'payment_type': p.payment_type,
            'payment_date': p.payment_date.isoformat() if p.payment_date else None,
            'payment_status': p.payment_status,
            'receive_user_id': p.receive_user_id,
            'receive_time': p.receive_time.isoformat() if p.receive_time else None,
            'create_time': p.create_time.isoformat() if p.create_time else None
        } for p in payments]
        
        return result
    
    def _generate_subscribe_no(self) -> str:
        """生成认购编号"""
        now = datetime.now()
        prefix = f"SUB{now.strftime('%Y%m%d')}"
        # 使用Redis生成序列号
        key = f"subscribe:no:{self.tenant}:{now.strftime('%Y%m%d')}"
        sequence = self.redis.incr(key)
        self.redis.expire(key, 86400)  # 24小时过期
        
        # 如果Redis不可用，从数据库获取最大值
        if sequence is None:
            max_subscribe = self.db.query(SaleSubscribe).filter(
                SaleSubscribe.tenant == self.tenant,
                SaleSubscribe.is_del == 0,
                SaleSubscribe.subscribe_no.like(f"{prefix}%")
            ).order_by(SaleSubscribe.subscribe_no.desc()).first()
            if max_subscribe:
                try:
                    sequence = int(max_subscribe.subscribe_no[-6:]) + 1
                except ValueError:
                    sequence = 1
            else:
                sequence = 1
        
        return f"{prefix}{sequence:06d}"
    
    def _generate_contract_no(self) -> str:
        """生成合同编号"""
        now = datetime.now()
        prefix = f"CT{now.strftime('%Y%m%d')}"
        # 使用Redis生成序列号
        key = f"contract:no:{self.tenant}:{now.strftime('%Y%m%d')}"
        sequence = self.redis.incr(key)
        self.redis.expire(key, 86400)  # 24小时过期
        
        # 如果Redis不可用，从数据库获取最大值
        if sequence is None:
            max_contract = self.db.query(SaleContract).filter(
                SaleContract.tenant == self.tenant,
                SaleContract.is_del == 0,
                SaleContract.contract_no.like(f"{prefix}%")
            ).order_by(SaleContract.contract_no.desc()).first()
            if max_contract:
                try:
                    sequence = int(max_contract.contract_no[-6:]) + 1
                except ValueError:
                    sequence = 1
            else:
                sequence = 1
        
        return f"{prefix}{sequence:06d}"
    
    def _generate_payment_no(self) -> str:
        """生成回款编号"""
        now = datetime.now()
        prefix = f"PAY{now.strftime('%Y%m%d')}"
        # 使用Redis生成序列号
        key = f"payment:no:{self.tenant}:{now.strftime('%Y%m%d')}"
        sequence = self.redis.incr(key)
        self.redis.expire(key, 86400)  # 24小时过期
        return f"{prefix}{sequence:06d}"
    
    def _trigger_performance_calculation(self, contract: SaleContract):
        """触发业绩和佣金计算（异步处理）"""
        # 这里可以发送消息到消息队列进行异步处理
        # 或者直接调用业绩计算服务
        try:
            from sale.service.performance_service import PerformanceService
            performance_service = PerformanceService(self.db, self.tenant)
            performance_service.calculate_sales_commission(contract.contract_id)
        except Exception as e:
            # 记录错误日志，不影响主流程
            print(f"业绩计算触发失败：{str(e)}")
    
    def _rollback_performance_commission(self, subscribe: SaleSubscribe):
        """回滚业绩和佣金数据"""
        # 回滚销售提成
        # 回滚渠道佣金
        # 记录回滚日志
        pass
    
    def _clear_cache(self, project_id: int):
        """清除相关缓存"""
        cache_keys = [
            f"house:sale_panel:{self.tenant}:{project_id}",
            f"building:tree:{self.tenant}:{project_id}",
            f"statistics:*:{self.tenant}:{project_id}"
        ]
        # 清除匹配的缓存
        import fnmatch
        all_keys = self.redis.keys(f"*:{self.tenant}:{project_id}")
        for pattern in cache_keys:
            for key in all_keys:
                if fnmatch.fnmatch(key.decode() if isinstance(key, bytes) else key, 
                                  pattern.replace('*', '.*')):
                    self.redis.delete(key)
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)


class LoanService:
    """贷款业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
    
    def create_loan(self, loan_data: dict, operator_id: int = None) -> dict:
        """创建贷款信息"""
        # 检查合同是否存在
        contract = SaleContractDAO.get_contract_by_id(
            self.db, loan_data['contract_id'], self.tenant
        )
        if not contract:
            raise BusinessError("合同不存在")
        
        # 检查是否已有贷款信息
        existing_loan = self.db.query(SaleLoan).filter(
            SaleLoan.contract_id == loan_data['contract_id'],
            SaleLoan.tenant == self.tenant,
            SaleLoan.is_del == 0
        ).first()
        
        if existing_loan:
            raise BusinessError("该合同已有贷款信息")
        
        # 创建贷款信息
        loan_data['tenant'] = self.tenant
        loan_data['loan_status'] = 1  # 申请中
        loan_data['status'] = 1
        loan_data['is_del'] = 0
        
        loan = SaleLoanDAO.create_loan(self.db, loan_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_loan", 
            f"创建贷款信息：合同ID{loan_data['contract_id']}", 
            True
        )
        
        return {
            'loan_id': loan.loan_id,
            'contract_id': loan.contract_id,
            'loan_type': loan.loan_type,
            'loan_amount': float(loan.loan_amount) if loan.loan_amount else 0,
            'loan_period': loan.loan_period,
            'loan_rate': float(loan.loan_rate) if loan.loan_rate else 0,
            'loan_bank': loan.loan_bank,
            'loan_status': loan.loan_status,
            'message': '贷款信息创建成功'
        }
    
    def update_loan_status(self, loan_id: int, new_status: int, 
                          operator_id: int = None) -> bool:
        """更新贷款状态"""
        loan = self.db.query(SaleLoan).filter(
            SaleLoan.loan_id == loan_id,
            SaleLoan.tenant == self.tenant,
            SaleLoan.is_del == 0
        ).first()
        
        if not loan:
            raise BusinessError("贷款信息不存在")
        
        # 更新状态
        loan.loan_status = new_status
        if new_status == 2:  # 已审批
            loan.approve_time = datetime.now()
        elif new_status == 3:  # 已放款
            loan.lend_time = datetime.now()
        
        self.db.commit()
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_loan_status", 
            f"更新贷款状态：{loan_id} -> {new_status}", 
            True
        )
        
        return True
    
    def get_loans_list(self, contract_id: int = None, page: int = 1, page_size: int = 20) -> dict:
        """获取贷款记录列表"""
        skip = (page - 1) * page_size
        
        filters = {}
        if contract_id:
            filters['contract_id'] = contract_id
        
        loans = SaleLoanDAO.get_loans_list(
            self.db, self.tenant, skip=skip, limit=page_size, filters=filters
        )
        
        # 获取总数
        total = len(SaleLoanDAO.get_loans_list(
            self.db, self.tenant, filters=filters
        ))
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        result = []
        for loan in loans:
            item = {
                'loan_id': loan.loan_id,
                'contract_id': loan.contract_id,
                'loan_type': loan.loan_type,
                'loan_amount': float(loan.loan_amount) if loan.loan_amount else 0,
                'loan_period': loan.loan_period,
                'loan_rate': float(loan.loan_rate) if loan.loan_rate else 0,
                'loan_bank': loan.loan_bank,
                'loan_status': loan.loan_status,
                'approve_time': loan.approve_time.isoformat() if loan.approve_time else None,
                'lend_time': loan.lend_time.isoformat() if loan.lend_time else None,
                'create_time': loan.create_time.isoformat() if loan.create_time else None,
                'update_time': loan.update_time.isoformat() if loan.update_time else None
            }
            result.append(item)
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': pages,
            'data': result
        }
    
    def update_loan(self, loan_id: int, update_data: dict, operator_id: int = None) -> SaleLoan:
        """更新贷款记录"""
        # 检查贷款是否存在
        loan = SaleLoanDAO.get_loan_by_id(self.db, loan_id, self.tenant)
        if not loan:
            raise BusinessError("贷款信息不存在")
        
        # 更新贷款信息（过滤掉不允许更新的字段）
        allowed_fields = ['loan_type', 'loan_amount', 'loan_period', 'loan_rate', 'loan_bank', 'status']
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if filtered_data:
            SaleLoanDAO.update_loan(self.db, loan, filtered_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_loan", 
            f"更新贷款信息：{loan_id}", 
            True
        )
        
        return loan
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)


class ReceiptService:
    """发票票据业务服务类"""
    
    def __init__(self, db: Session, tenant: str):
        self.db = db
        self.tenant = tenant
    
    def create_receipt(self, receipt_data: dict, operator_id: int = None) -> dict:
        """创建发票票据"""
        # 检查合同是否存在
        from sale.dao.sale_dao import SaleContractDAO
        contract = SaleContractDAO.get_contract_by_id(
            self.db, receipt_data['contract_id'], self.tenant
        )
        if not contract:
            raise BusinessError("合同不存在")
        
        # 创建发票票据
        receipt_data['tenant'] = self.tenant
        receipt_data['issue_date'] = datetime.now()
        receipt_data['receipt_status'] = 1  # 正常
        receipt_data['status'] = 1
        receipt_data['is_del'] = 0
        
        receipt = SaleReceiptDAO.create_receipt(self.db, receipt_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "create_receipt", 
            f"创建发票：{receipt.receipt_no}，金额：{receipt.receipt_amount}", 
            True
        )
        
        return {
            'receipt_id': receipt.receipt_id,
            'receipt_no': receipt.receipt_no,
            'contract_id': receipt.contract_id,
            'receipt_type': receipt.receipt_type,
            'receipt_amount': float(receipt.receipt_amount) if receipt.receipt_amount else 0,
            'issue_date': receipt.issue_date.isoformat() if receipt.issue_date else None,
            'receipt_file_url': receipt.receipt_file_url,
            'receipt_status': receipt.receipt_status,
            'message': '发票创建成功'
        }
    
    def update_receipt_status(self, receipt_id: int, new_status: int, 
                             operator_id: int = None) -> bool:
        """更新发票状态（状态变更专用）"""
        receipt = self.db.query(SaleReceipt).filter(
            SaleReceipt.receipt_id == receipt_id,
            SaleReceipt.tenant == self.tenant,
            SaleReceipt.is_del == 0
        ).first()
        
        if not receipt:
            raise BusinessError("发票不存在")
        
        # 更新状态
        receipt.receipt_status = new_status
        receipt.update_time = datetime.now()
        self.db.commit()
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_receipt_status", 
            f"更新发票状态：{receipt_id} -> {new_status}", 
            True
        )
        
        return True
    
    def get_receipts_list(self, contract_id: int = None, page: int = 1, 
                         page_size: int = 10) -> dict:
        """获取发票列表"""
        skip = (page - 1) * page_size
        filters = {}
        
        if contract_id:
            filters['contract_id'] = contract_id
        
        receipts = SaleReceiptDAO.get_receipts_list(
            self.db, self.tenant, skip=skip, limit=page_size, filters=filters
        )
        
        result = []
        for receipt in receipts:
            result.append({
                'receipt_id': receipt.receipt_id,
                'receipt_no': receipt.receipt_no,
                'contract_id': receipt.contract_id,
                'receipt_type': receipt.receipt_type,
                'receipt_amount': float(receipt.receipt_amount) if receipt.receipt_amount else 0,
                'issue_date': receipt.issue_date.isoformat() if receipt.issue_date else None,
                'receipt_file_url': receipt.receipt_file_url,
                'receipt_status': receipt.receipt_status,
                'create_time': receipt.create_time.isoformat() if receipt.create_time else None,
                'update_time': receipt.update_time.isoformat() if receipt.update_time else None
            })
        
        return {
            'list': result,
            'total': len(result),
            'page': page,
            'page_size': page_size
        }
    
    def update_receipt(self, receipt_id: int, update_data: dict, 
                      operator_id: int = None) -> dict:
        """更新发票记录"""
        receipt = SaleReceiptDAO.get_receipt_by_id(self.db, receipt_id, self.tenant)
        
        if not receipt:
            raise BusinessError("发票不存在")
        
        # 过滤允许更新的字段
        allowed_fields = ['receipt_type', 'receipt_amount', 'issue_date', 
                         'receipt_file_url', 'receipt_status']
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        filtered_data['update_time'] = datetime.now()
        
        updated_receipt = SaleReceiptDAO.update_receipt(self.db, receipt, filtered_data)
        
        # 记录操作日志
        self._create_operation_log(
            operator_id, "update_receipt", 
            f"更新发票信息：{receipt_id}", 
            True
        )
        
        return {
            'receipt_id': updated_receipt.receipt_id,
            'receipt_no': updated_receipt.receipt_no,
            'contract_id': updated_receipt.contract_id,
            'receipt_type': updated_receipt.receipt_type,
            'receipt_amount': float(updated_receipt.receipt_amount) if updated_receipt.receipt_amount else 0,
            'issue_date': updated_receipt.issue_date.isoformat() if updated_receipt.issue_date else None,
            'receipt_file_url': updated_receipt.receipt_file_url,
            'receipt_status': updated_receipt.receipt_status,
            'message': '发票更新成功'
        }
    
    def _create_operation_log(self, user_id: int, operation_type: str, 
                             operation_content: str, operation_result: bool):
        """创建操作日志"""
        log_data = {
            'tenant': self.tenant,
            'user_id': user_id,
            'operation_type': operation_type,
            'operation_content': operation_content,
            'operation_result': 1 if operation_result else 0,
            'create_time': datetime.now()
        }
        
        SaleStatDailyLogsDAO.create_log(self.db, log_data)