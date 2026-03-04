from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.digital_twin.schemas import (
    ScenarioCreate,
    ScenarioRead,
    SimulationRunCreate,
    SimulationRunRead,
)
from app.digital_twin.service import (
    create_scenario,
    get_scenarios,
    get_simulation_results,
    run_simulation,
)

router = APIRouter()


@router.get("/scenarios", response_model=list[ScenarioRead])
async def list_scenarios(limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_scenarios(db, limit)


@router.post("/scenarios", response_model=ScenarioRead, status_code=201)
async def add_scenario(payload: ScenarioCreate, db: AsyncSession = Depends(get_db)):
    return await create_scenario(db, payload)


@router.post("/run", response_model=SimulationRunRead, status_code=201)
async def start_simulation(
    payload: SimulationRunCreate, db: AsyncSession = Depends(get_db)
):
    return await run_simulation(db, payload)


@router.get("/results/{run_id}", response_model=SimulationRunRead)
async def simulation_results(run_id: int, db: AsyncSession = Depends(get_db)):
    return await get_simulation_results(db, run_id)
