from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.food_safety.models import AllergenAlert, ComplianceScore, HACCPLog, TemperatureReading
from app.food_safety.schemas import (
    ComplianceAskRequest,
    ComplianceAskResponse,
    HACCPLogCreate,
    TemperatureReadingCreate,
)


async def get_haccp_logs(
    db: AsyncSession, check_type: str | None = None, limit: int = 100
) -> list[HACCPLog]:
    query = select(HACCPLog).order_by(HACCPLog.created_at.desc()).limit(limit)
    if check_type:
        query = query.where(HACCPLog.check_type == check_type)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_haccp_log(db: AsyncSession, payload: HACCPLogCreate) -> HACCPLog:
    log = HACCPLog(**payload.model_dump())
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


async def get_temperature_readings(
    db: AsyncSession, location: str | None = None, limit: int = 100
) -> list[TemperatureReading]:
    query = select(TemperatureReading).order_by(
        TemperatureReading.timestamp.desc()
    ).limit(limit)
    if location:
        query = query.where(TemperatureReading.location == location)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_allergen_alerts(
    db: AsyncSession, limit: int = 100
) -> list[AllergenAlert]:
    result = await db.execute(
        select(AllergenAlert).order_by(AllergenAlert.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def get_compliance_score(
    db: AsyncSession, limit: int = 30
) -> list[ComplianceScore]:
    result = await db.execute(
        select(ComplianceScore).order_by(ComplianceScore.date.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def ask_compliance_question(
    db: AsyncSession, payload: ComplianceAskRequest
) -> ComplianceAskResponse:
    return ComplianceAskResponse(
        question=payload.question,
        answer="This is a stub response. LLM integration pending.",
        references=None,
    )
