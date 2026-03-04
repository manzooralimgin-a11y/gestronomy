from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.workforce.models import Applicant, Employee, Schedule, Shift, TrainingModule, TrainingProgress
from app.workforce.schemas import ApplicantCreate, EmployeeCreate, ScheduleCreate, ShiftCreate


async def get_employees(
    db: AsyncSession, status_filter: str | None = None, limit: int = 100
) -> list[Employee]:
    query = select(Employee).order_by(Employee.name).limit(limit)
    if status_filter:
        query = query.where(Employee.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_employee(db: AsyncSession, payload: EmployeeCreate) -> Employee:
    employee = Employee(**payload.model_dump())
    db.add(employee)
    await db.flush()
    await db.refresh(employee)
    return employee


async def get_schedules(
    db: AsyncSession, status_filter: str | None = None
) -> list[Schedule]:
    query = select(Schedule).order_by(Schedule.week_start.desc())
    if status_filter:
        query = query.where(Schedule.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


async def generate_schedule(db: AsyncSession, payload: ScheduleCreate) -> Schedule:
    schedule = Schedule(
        week_start=payload.week_start,
        status="draft",
        auto_generated=True,
    )
    db.add(schedule)
    await db.flush()
    await db.refresh(schedule)
    return schedule


async def approve_schedule(
    db: AsyncSession, schedule_id: int, approver_id: int
) -> Schedule:
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found"
        )
    schedule.status = "approved"
    schedule.approved_by = approver_id
    await db.flush()
    await db.refresh(schedule)
    return schedule


async def get_shifts(
    db: AsyncSession, schedule_id: int | None = None
) -> list[Shift]:
    query = select(Shift).order_by(Shift.date)
    if schedule_id:
        query = query.where(Shift.schedule_id == schedule_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_shift(db: AsyncSession, payload: ShiftCreate) -> Shift:
    shift = Shift(**payload.model_dump())
    db.add(shift)
    await db.flush()
    await db.refresh(shift)
    return shift


async def get_labor_tracker(db: AsyncSession) -> dict:
    employee_count = await db.execute(
        select(func.count(Employee.id)).where(Employee.status == "active")
    )
    shift_count = await db.execute(select(func.count(Shift.id)))
    total_hours = await db.execute(select(func.sum(Schedule.total_hours)))
    total_cost = await db.execute(select(func.sum(Schedule.total_cost)))

    return {
        "active_employees": employee_count.scalar() or 0,
        "total_shifts": shift_count.scalar() or 0,
        "total_scheduled_hours": float(total_hours.scalar() or 0),
        "total_labor_cost": float(total_cost.scalar() or 0),
    }


async def get_applicants(
    db: AsyncSession, status_filter: str | None = None
) -> list[Applicant]:
    query = select(Applicant).order_by(Applicant.created_at.desc())
    if status_filter:
        query = query.where(Applicant.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_applicant(db: AsyncSession, payload: ApplicantCreate) -> Applicant:
    applicant = Applicant(**payload.model_dump())
    db.add(applicant)
    await db.flush()
    await db.refresh(applicant)
    return applicant


async def get_training_overview(db: AsyncSession) -> dict:
    modules = await db.execute(select(TrainingModule).order_by(TrainingModule.title))
    progress = await db.execute(select(TrainingProgress))

    return {
        "modules": [m.__dict__ for m in modules.scalars().all()],
        "progress": [p.__dict__ for p in progress.scalars().all()],
    }
