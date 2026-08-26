"""
房地产SaaS销售管理系统 - 楼盘销控模块路由
"""

import uuid
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_sale_db as get_db
from core.redis_base import redis_client
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from sale.service.project_service import ProjectService, BuildingService, UnitService, HouseService
from sale.dao.sale_dao import SaleProjectRuleDAO
from sale.schemas.project_schemas import (
    PrepareProjectCreateReq, PrepareProjectCreateResp,
    VerifyProjectCreateReq
)

router = APIRouter(prefix="/project", tags=["楼盘销控"])


# ========== 预创建接口（公开，供 Agent 调用生成楼栋创建票据）==========

@router.post("/prepare-project-create", summary="预创建楼栋（生成一次性票据）",
             response_model=PrepareProjectCreateResp)
async def prepare_project_create(req: PrepareProjectCreateReq, db: Session = Depends(get_db)):
    """预创建接口：生成一次性票据 projectCreateTicket（UUID），返回楼栋创建页URL
    与 prepare-login 不同：不使用长轮询，用户通过 Agent 下发的链接直接在浏览器操作创建页"""
    try:
        ticket = str(uuid.uuid4())
        expire_seconds = req.expireSeconds or 600

        ticket_data = {
            "tenantId": req.tenantId,
            "projectId": req.projectId,
            "mcpSessionId": req.mcpSessionId,
            "status": "pending"
        }

        redis_client.setex(
            f"project:ticket:{ticket}",
            expire_seconds,
            json.dumps(ticket_data)
        )

        # 公网地址，默认端口8000
        control_url = f"http://14.103.221.98:8000/project-create?ticket={ticket}"

        return success_response(data={
            "controlUrl": control_url,
            "ticket": ticket
        })
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/verify-project-create", summary="校验楼栋创建票据")
async def verify_project_create(req: VerifyProjectCreateReq):
    """校验创建票据，返回票据数据（用于创建页判断票据有效性、预选楼盘）"""
    try:
        raw = redis_client.get(f"project:ticket:{req.ticket}")
        if not raw:
            return error_response(4000, "链接已过期，请重新在AI窗口发起楼栋创建")
        ticket_data = json.loads(raw)
        return success_response(data=ticket_data)
    except Exception as e:
        return error_response(5000, str(e))


# ========== 楼盘管理接口 ==========

@router.post("/create")
async def create_project(
    project_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建楼盘"""
    try:
        service = ProjectService(db, current_user['tenant'])
        project = service.create_project(project_data, current_user['user_id'])
        return success_response(data={
            "project_id": project.project_id,
            "project_code": project.project_code,
            "project_name": project.project_name
        }, message="楼盘创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/list")
async def get_projects_list(
    page: int = 1,
    page_size: int = 20,
    project_name: Optional[str] = None,
    project_status: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取楼盘列表"""
    try:
        service = ProjectService(db, current_user['tenant'])
        filters = {}
        if project_name:
            filters['project_name'] = project_name
        if project_status is not None:
            filters['project_status'] = project_status
        
        result = service.get_projects_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/detail/{project_id}")
async def get_project_detail(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取楼盘详情"""
    try:
        service = ProjectService(db, current_user['tenant'])
        detail = service.get_project_detail(project_id)
        return success_response(data=detail)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/update/{project_id}")
async def update_project(
    project_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新楼盘"""
    try:
        service = ProjectService(db, current_user['tenant'])
        project = service.update_project(project_id, update_data, current_user['user_id'])
        return success_response(data={
            "project_id": project.project_id,
            "project_name": project.project_name
        }, message="楼盘更新成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/delete/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除楼盘"""
    try:
        service = ProjectService(db, current_user['tenant'])
        service.delete_project(project_id, current_user['user_id'])
        return success_response(message="楼盘删除成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 楼栋管理接口 ==========

@router.post("/building/create")
async def create_building(
    building_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建楼栋"""
    try:
        service = BuildingService(db, current_user['tenant'])
        building = service.create_building(building_data, current_user['user_id'])
        return success_response(data={
            "building_id": building.building_id,
            "building_name": building.building_name
        }, message="楼栋创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/building/generate-preview")
async def generate_buildings_preview(
    params: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    参数化楼栋批量生成（预览）—— 不落库。
    前端先调用此接口展示待生成的楼栋，用户在弹窗编辑楼栋名称后确认，
    再调用 /building/batch-create。
    params:
      project_id: 楼盘ID（必填）
      start_building_no: 起始楼栋编号（数字字符串，如 "1"）
      generate_count: 生成数量（1~50）
      units_per_building: 每栋单元数
      total_floors: 每栋总层数
    """
    try:
        service = BuildingService(db, current_user['tenant'])
        result = service.generate_buildings_preview(params)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/building/batch-create")
async def batch_create_buildings(
    params: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    批量确认楼栋落库（事务一致：全部成功/全部回滚）。
    params:
      project_id: 楼盘ID（必填）
      buildings: 前端编辑后的预览列表（推荐传入），元素含
                 building_code / building_name / total_floors / total_units
      若不传 buildings，则按批量参数（start_building_no 等）重新生成。
    """
    try:
        service = BuildingService(db, current_user['tenant'])
        result = service.batch_create_buildings(params, current_user['user_id'])
        return success_response(data=result, message=f"楼栋批量创建成功（{result.get('inserted_count',0)}栋）")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/building/list")
async def get_buildings_list(
    project_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取楼栋列表"""
    try:
        service = BuildingService(db, current_user['tenant'])
        result = service.get_buildings_list(page, page_size, {'project_id': project_id})
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/building/update/{building_id}")
async def update_building(
    building_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新楼栋"""
    try:
        service = BuildingService(db, current_user['tenant'])
        building = service.update_building(building_id, update_data, current_user['user_id'])
        return success_response(data={
            "building_id": building.building_id,
            "building_name": building.building_name
        }, message="楼栋更新成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 单元管理接口 ==========

@router.post("/unit/create")
async def create_unit(
    unit_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建单元"""
    try:
        service = UnitService(db, current_user['tenant'])
        unit = service.create_unit(unit_data, current_user['user_id'])
        return success_response(data={
            "unit_id": unit.unit_id,
            "unit_code": unit.unit_code,
            "unit_name": unit.unit_name
        }, message="单元创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/unit/list")
async def get_units_list(
    building_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单元列表"""
    try:
        service = UnitService(db, current_user['tenant'])
        result = service.get_units_list(building_id, page, page_size)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/unit/detail/{unit_id}")
async def get_unit_detail(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单元详情"""
    try:
        service = UnitService(db, current_user['tenant'])
        detail = service.get_unit_detail(unit_id)
        return success_response(data=detail)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/unit/update/{unit_id}")
async def update_unit(
    unit_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新单元"""
    try:
        service = UnitService(db, current_user['tenant'])
        unit = service.update_unit(unit_id, update_data, current_user['user_id'])
        return success_response(data={
            "unit_id": unit.unit_id,
            "unit_name": unit.unit_name
        }, message="单元更新成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 房源管理接口（参数化自动生成 + 手动单条） ==========

@router.post("/house/generate-preview")
async def generate_houses_preview(
    params: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    参数化房源生成（预览）—— 不落库。
    前端先调用此接口展示待生成的房号，用户确认无误后再调用 /house/batch-create。
    params:
      building_id: 楼栋ID（必填）
      units: 各单元配置（可不同单元不同层数），示例：
        [{"unit_code": "1", "total_floors": 33, "start_floor": 1, "houses_per_floor": 4,
          "room_number_sequence": "01,02,03,04", "underground_floors": 2,
          "underground_houses_per_floor": 10, "underground_room_sequence": "01..10",
          "underground_house_type": 2, "house_number_format": "{unit_code}-{floor}{room}"},
         {"unit_code": "2", "total_floors": 28, ..., "house_number_format": "..."}]
    """
    try:
        service = HouseService(db, current_user['tenant'])
        result = service.generate_houses_preview(params)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/house/batch-create")
async def batch_create_houses(
    params: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    批量确认房源落库。
    params 结构与 /house/generate-preview 完全一致即可，
    后端内部会重新生成并检测冲突，bulk_insert 批量入库。
    """
    try:
        service = HouseService(db, current_user['tenant'])
        result = service.batch_create_houses(params, current_user['user_id'])
        return success_response(data=result, message=f"房源批量创建成功（{result.get('inserted_count',0)}套）")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/house/create")
async def create_house(
    house_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建房源（单条手动，保留用于补齐/异常房源）"""
    try:
        service = HouseService(db, current_user['tenant'])
        house = service.create_house(house_data, current_user['user_id'])
        return success_response(data={
            "house_id": house.house_id,
            "house_code": house.house_code
        }, message="房源创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/house/list")
async def get_houses_list(
    project_id: int,
    building_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取房源列表"""
    try:
        service = HouseService(db, current_user['tenant'])
        filters = {}
        if building_id:
            filters['building_id'] = building_id
        if unit_id:
            filters['unit_id'] = unit_id
        
        result = service.get_houses_list(project_id, page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/house/detail/{house_id}")
async def get_house_detail(
    house_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取房源详情"""
    try:
        service = HouseService(db, current_user['tenant'])
        detail = service.get_house_detail(house_id)
        return success_response(data=detail)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/house/update/{house_id}")
async def update_house(
    house_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新房源"""
    try:
        service = HouseService(db, current_user['tenant'])
        house = service.update_house(house_id, update_data, current_user['user_id'])
        return success_response(data={
            "house_id": house.house_id,
            "house_code": house.house_code
        }, message="房源更新成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/house/lock")
async def lock_house(
    house_id: int,
    customer_id: int,
    expire_minutes: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """锁定房源"""
    try:
        service = HouseService(db, current_user['tenant'])
        result = service.lock_house(
            house_id, customer_id, current_user['user_id'], 
            expire_minutes, current_user['user_id']
        )
        return success_response(data=result, message="房源锁定成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/house/unlock")
async def unlock_house(
    house_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """解锁房源"""
    try:
        service = HouseService(db, current_user['tenant'])
        service.unlock_house(house_id, current_user['user_id'])
        return success_response(message="房源解锁成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/house/control/{project_id}")
async def get_house_control_panel(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取销控面板"""
    try:
        service = HouseService(db, current_user['tenant'])
        result = service.get_sale_panel(project_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


# ========== 项目规则管理接口 ==========

@router.post("/rule/create")
async def create_project_rule(
    rule_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建项目规则"""
    try:
        rule_data['tenant'] = current_user['tenant']
        rule_data['status'] = 1
        rule_data['is_del'] = 0
        rule = SaleProjectRuleDAO.create_rule(db, rule_data)
        return success_response(data={
            "rule_id": rule.rule_id,
            "rule_key": rule.rule_key,
            "rule_value": rule.rule_value
        }, message="项目规则创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/rule/list")
async def get_project_rules_list(
    project_id: Optional[int] = None,
    rule_key: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目规则列表"""
    try:
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if rule_key:
            filters['rule_key'] = rule_key
        
        rules = SaleProjectRuleDAO.get_rules_list(db, current_user['tenant'], 
                                                  (page - 1) * page_size, page_size, filters)
        total = len(SaleProjectRuleDAO.get_rules_list(db, current_user['tenant'], 0, 100000, filters))
        
        return success_response(data={
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'data': [{
                'rule_id': r.rule_id,
                'project_id': r.project_id,
                'rule_key': r.rule_key,
                'rule_value': r.rule_value,
                'rule_desc': r.rule_desc,
                'rule_status': r.rule_status,
                'create_time': r.create_time.isoformat() if r.create_time else None,
                'update_time': r.update_time.isoformat() if r.update_time else None
            } for r in rules]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/rule/detail/{rule_id}")
async def get_project_rule_detail(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目规则详情"""
    try:
        rule = SaleProjectRuleDAO.get_rule_by_id(db, rule_id, current_user['tenant'])
        if not rule:
            return error_response(-1, "规则不存在")
        
        return success_response(data={
            'rule_id': rule.rule_id,
            'project_id': rule.project_id,
            'rule_key': rule.rule_key,
            'rule_value': rule.rule_value,
            'rule_desc': rule.rule_desc,
            'rule_status': rule.rule_status,
            'create_time': rule.create_time.isoformat() if rule.create_time else None,
            'update_time': rule.update_time.isoformat() if rule.update_time else None
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/rule/update/{rule_id}")
async def update_project_rule(
    rule_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新项目规则"""
    try:
        rule = SaleProjectRuleDAO.get_rule_by_id(db, rule_id, current_user['tenant'])
        if not rule:
            return error_response(-1, "规则不存在")
        
        updated_rule = SaleProjectRuleDAO.update_rule(db, rule, update_data)
        return success_response(data={
            "rule_id": updated_rule.rule_id,
            "rule_key": updated_rule.rule_key,
            "rule_value": updated_rule.rule_value
        }, message="项目规则更新成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/rule/delete/{rule_id}")
async def delete_project_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除项目规则"""
    try:
        result = SaleProjectRuleDAO.delete_rule(db, rule_id, current_user['tenant'])
        if not result:
            return error_response(-1, "规则不存在")
        
        return success_response(message="项目规则删除成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/rule/get-value")
async def get_project_rule_value(
    project_id: int,
    rule_key: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取规则值"""
    try:
        value = SaleProjectRuleDAO.get_rule_value(db, project_id, rule_key, current_user['tenant'])
        return success_response(data={"rule_key": rule_key, "rule_value": value})
    except Exception as e:
        return error_response(-1, str(e))
