from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.schemas import AgentActionRead, AgentConfigRead, AgentConfigUpdate
from app.core.service import (
    approve_action,
    get_agent_actions,
    get_all_agents,
    update_agent_config,
)
from app.core.schemas import (
    RevenueControlPolicyRead,
    RevenueControlPolicyUpdate,
    RevenueExperimentCreate,
    RevenueExperimentDashboardResponse,
    RevenueExperimentEventCreate,
    RevenueExperimentRead,
    RevenueExperimentStopResponse,
    ServiceAutopilotActionExecuteResponse,
    ServiceAutopilotPredictionResponse,
    ServiceAutopilotSuggestResponse,
    RevenueUpsellOptimizerResponse,
)
from app.core.service_autopilot import (
    approve_service_action,
    execute_service_action,
    predict_service_delay,
    suggest_service_actions,
)
from app.core.service_revenue_control import (
    create_revenue_experiment,
    get_revenue_control_policy,
    get_revenue_experiment_dashboard,
    optimize_upsell_candidates,
    record_revenue_experiment_event,
    start_revenue_experiment,
    stop_revenue_experiment,
    update_revenue_control_policy,
)
from app.database import get_db
from app.dependencies import get_current_tenant_user

router = APIRouter()


@router.get("/service-autopilot/predict", response_model=ServiceAutopilotPredictionResponse)
async def service_autopilot_predict(
    horizon_minutes: int = 15,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await predict_service_delay(db, current_user.restaurant_id, horizon_minutes)


@router.post("/service-autopilot/suggest", response_model=ServiceAutopilotSuggestResponse)
async def service_autopilot_suggest(
    horizon_minutes: int = 15,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await suggest_service_actions(db, current_user.restaurant_id, horizon_minutes)


@router.post(
    "/service-autopilot/actions/{action_id}/approve",
    response_model=ServiceAutopilotActionExecuteResponse,
)
async def service_autopilot_approve(
    action_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await approve_service_action(db, current_user.restaurant_id, action_id, current_user.id)


@router.post(
    "/service-autopilot/actions/{action_id}/execute",
    response_model=ServiceAutopilotActionExecuteResponse,
)
async def service_autopilot_execute(
    action_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await execute_service_action(db, current_user.restaurant_id, action_id, current_user.id)


@router.get(
    "/revenue-control-tower/upsell-candidates",
    response_model=RevenueUpsellOptimizerResponse,
)
async def revenue_upsell_candidates(
    guest_id: int | None = None,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await optimize_upsell_candidates(db, current_user.restaurant_id, guest_id, limit)


@router.get(
    "/revenue-control-tower/policy",
    response_model=RevenueControlPolicyRead,
)
async def revenue_control_policy(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_revenue_control_policy(db, current_user.restaurant_id)


@router.put(
    "/revenue-control-tower/policy",
    response_model=RevenueControlPolicyRead,
)
async def revenue_control_policy_update(
    payload: RevenueControlPolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await update_revenue_control_policy(
        db, current_user.restaurant_id, payload, current_user.id
    )


@router.post(
    "/revenue-control-tower/experiments",
    response_model=RevenueExperimentRead,
    status_code=201,
)
async def revenue_experiment_create(
    payload: RevenueExperimentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await create_revenue_experiment(db, current_user.restaurant_id, payload, current_user.id)


@router.post(
    "/revenue-control-tower/experiments/{experiment_id}/start",
    response_model=RevenueExperimentRead,
)
async def revenue_experiment_start(
    experiment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await start_revenue_experiment(db, current_user.restaurant_id, experiment_id, current_user.id)


@router.post(
    "/revenue-control-tower/experiments/{experiment_id}/stop",
    response_model=RevenueExperimentStopResponse,
)
async def revenue_experiment_stop(
    experiment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await stop_revenue_experiment(db, current_user.restaurant_id, experiment_id, current_user.id)


@router.post(
    "/revenue-control-tower/experiments/{experiment_id}/events",
    response_model=RevenueExperimentRead,
)
async def revenue_experiment_record_event(
    experiment_id: int,
    payload: RevenueExperimentEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await record_revenue_experiment_event(
        db, current_user.restaurant_id, experiment_id, payload, current_user.id
    )


@router.get(
    "/revenue-control-tower/experiments/{experiment_id}/uplift-dashboard",
    response_model=RevenueExperimentDashboardResponse,
)
async def revenue_experiment_uplift_dashboard(
    experiment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_revenue_experiment_dashboard(db, current_user.restaurant_id, experiment_id)


@router.get("", response_model=list[AgentConfigRead])
async def list_agents(db: AsyncSession = Depends(get_db)):
    return await get_all_agents(db)


@router.get("/{name}", response_model=AgentConfigRead)
async def agent_detail(name: str, db: AsyncSession = Depends(get_db)):
    agents = await get_all_agents(db)
    for agent in agents:
        if agent.agent_name == name:
            return agent
    from fastapi import HTTPException, status
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")


@router.get("/{name}/actions", response_model=list[AgentActionRead])
async def agent_actions(name: str, limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await get_agent_actions(db, name, limit)


@router.post("/{name}/approve/{action_id}", response_model=AgentActionRead)
async def approve_agent_action(
    name: str, action_id: int, user_id: int = 0, db: AsyncSession = Depends(get_db)
):
    return await approve_action(db, action_id, user_id)


@router.put("/{name}/config", response_model=AgentConfigRead)
async def update_config(
    name: str, payload: AgentConfigUpdate, db: AsyncSession = Depends(get_db)
):
    return await update_agent_config(db, name, payload)
