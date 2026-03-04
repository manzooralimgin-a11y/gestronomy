from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.digital_twin.models import Scenario, SimulationRun
from app.digital_twin.schemas import ScenarioCreate, SimulationRunCreate


async def get_scenarios(db: AsyncSession, limit: int = 100) -> list[Scenario]:
    result = await db.execute(
        select(Scenario).order_by(Scenario.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def create_scenario(db: AsyncSession, payload: ScenarioCreate) -> Scenario:
    scenario = Scenario(**payload.model_dump())
    db.add(scenario)
    await db.flush()
    await db.refresh(scenario)
    return scenario


async def run_simulation(
    db: AsyncSession, payload: SimulationRunCreate
) -> SimulationRun:
    result = await db.execute(
        select(Scenario).where(Scenario.id == payload.scenario_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found"
        )
    run = SimulationRun(scenario_id=payload.scenario_id, status="pending")
    db.add(run)
    await db.flush()
    await db.refresh(run)
    return run


async def get_simulation_results(db: AsyncSession, run_id: int) -> SimulationRun:
    result = await db.execute(
        select(SimulationRun).where(SimulationRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Simulation run not found"
        )
    return run
