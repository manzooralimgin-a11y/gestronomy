from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.food_safety.schemas import (
    AllergenAlertRead,
    ComplianceAskRequest,
    ComplianceAskResponse,
    ComplianceScoreRead,
    HACCPLogCreate,
    HACCPLogRead,
    TemperatureReadingRead,
)
from app.food_safety.service import (
    ask_compliance_question,
    create_haccp_log,
    get_allergen_alerts,
    get_compliance_score,
    get_haccp_logs,
    get_temperature_readings,
)

router = APIRouter()


@router.get("/haccp", response_model=list[HACCPLogRead])
async def list_haccp_logs(
    check_type: str | None = None, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await get_haccp_logs(db, check_type, limit)


@router.post("/haccp", response_model=HACCPLogRead, status_code=201)
async def add_haccp_log(payload: HACCPLogCreate, db: AsyncSession = Depends(get_db)):
    return await create_haccp_log(db, payload)


@router.get("/temperatures", response_model=list[TemperatureReadingRead])
async def list_temperatures(
    location: str | None = None, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await get_temperature_readings(db, location, limit)


@router.get("/allergens", response_model=list[AllergenAlertRead])
async def list_allergens(limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_allergen_alerts(db, limit)


@router.get("/compliance-score", response_model=list[ComplianceScoreRead])
async def compliance_score(limit: int = 30, db: AsyncSession = Depends(get_db)):
    return await get_compliance_score(db, limit)


@router.post("/ask", response_model=ComplianceAskResponse)
async def ask_compliance(
    payload: ComplianceAskRequest, db: AsyncSession = Depends(get_db)
):
    return await ask_compliance_question(db, payload)
