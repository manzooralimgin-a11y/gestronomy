from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.schemas import AgentActionRead
from app.dependencies import get_current_tenant_user
from app.dashboard.schemas import (
    AlertRead,
    AlertUpdate,
    AuditTimelineEvent,
    ExceptionInboxItem,
    ExceptionWorkflowUpdate,
    ExplainableRecommendation,
    KPISnapshotRead,
    NLQueryRequest,
    NLQueryResponse,
    SLODashboardResponse,
)
from app.dashboard.service import (
    get_audit_timeline,
    get_alerts,
    get_exception_inbox,
    get_kpi_history,
    get_live_kpis,
    get_recent_agent_activity,
    get_slo_dashboard,
    get_explainable_recommendations,
    process_nl_query,
    update_exception_workflow,
    update_alert,
)
from app.database import get_db

router = APIRouter()


@router.get("/live", response_model=list[KPISnapshotRead])
async def live_kpis(db: AsyncSession = Depends(get_db)):
    return await get_live_kpis(db)


@router.get("/alerts", response_model=list[AlertRead])
async def list_alerts(
    is_read: bool | None = None, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await get_alerts(db, is_read, limit)


@router.put("/alerts/{alert_id}", response_model=AlertRead)
async def edit_alert(
    alert_id: int, payload: AlertUpdate, db: AsyncSession = Depends(get_db)
):
    return await update_alert(db, alert_id, payload)


@router.post("/query", response_model=NLQueryResponse)
async def nl_query(payload: NLQueryRequest, db: AsyncSession = Depends(get_db)):
    return await process_nl_query(db, payload)


@router.get("/activity", response_model=list[AgentActionRead])
async def recent_activity(limit: int = 20, db: AsyncSession = Depends(get_db)):
    return await get_recent_agent_activity(db, limit)


@router.get("/kpis", response_model=list[KPISnapshotRead])
async def kpi_history(
    metric_name: str | None = None, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await get_kpi_history(db, metric_name, limit)


@router.get("/exceptions", response_model=list[ExceptionInboxItem])
async def exception_inbox(
    severity: str | None = None,
    status: str = "open",
    owner: str | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    _ = current_user
    return await get_exception_inbox(db, severity, status, owner, limit)


@router.patch("/exceptions/{exception_id}", response_model=ExceptionInboxItem)
async def update_exception(
    exception_id: int,
    payload: ExceptionWorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await update_exception_workflow(db, exception_id, payload, current_user.id)


@router.get("/recommendations", response_model=list[ExplainableRecommendation])
async def explainable_recommendations(
    status: str | None = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    _ = current_user
    return await get_explainable_recommendations(db, status, limit)


@router.get("/audit-timeline", response_model=list[AuditTimelineEvent])
async def audit_timeline(
    entity_type: str | None = None,
    entity_id: int | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    _ = current_user
    return await get_audit_timeline(db, entity_type, entity_id, limit)


@router.get("/slo", response_model=SLODashboardResponse)
async def slo_dashboard(
    window_minutes: int = 15,
    current_user: User = Depends(get_current_tenant_user),
):
    _ = current_user
    return await get_slo_dashboard(window_minutes)
