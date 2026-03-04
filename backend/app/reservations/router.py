from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.database import get_db
from app.dependencies import get_current_tenant_user
from app.reservations.schemas import (
    FloorSectionCreate,
    FloorSectionRead,
    FloorSectionUpdate,
    FloorSummary,
    ReservationCreate,
    ReservationRead,
    ReservationUpdate,
    TableCreate,
    TableRead,
    TableSessionCreate,
    TableSessionRead,
    TableStatusUpdate,
    TableUpdate,
    WaitlistEntryCreate,
    WaitlistEntryRead,
)
from app.reservations.service import (
    add_to_waitlist,
    cancel_reservation,
    check_availability,
    close_session,
    complete_reservation,
    create_reservation,
    create_section,
    create_session,
    create_table,
    delete_section,
    delete_table,
    get_active_sessions,
    get_floor_summary,
    get_reservation_by_id,
    get_reservations,
    get_sections,
    get_table_by_id,
    get_tables,
    get_waitlist,
    remove_from_waitlist,
    seat_reservation,
    seat_waitlist_entry,
    update_reservation,
    update_section,
    update_table,
    update_table_status,
)

router = APIRouter()


@router.get("/sections", response_model=list[FloorSectionRead])
async def list_sections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_sections(db, current_user.restaurant_id)


@router.post("/sections", response_model=FloorSectionRead, status_code=201)
async def add_section(
    payload: FloorSectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await create_section(db, current_user.restaurant_id, payload)


@router.put("/sections/{section_id}", response_model=FloorSectionRead)
async def edit_section(
    section_id: int,
    payload: FloorSectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await update_section(db, current_user.restaurant_id, section_id, payload)


@router.delete("/sections/{section_id}", status_code=204)
async def remove_section(
    section_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    await delete_section(db, current_user.restaurant_id, section_id)


@router.get("/tables", response_model=list[TableRead])
async def list_tables(
    section_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_tables(db, current_user.restaurant_id, section_id)


@router.post("/tables", response_model=TableRead, status_code=201)
async def add_table(
    payload: TableCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await create_table(db, current_user.restaurant_id, payload)


@router.get("/tables/{table_id}", response_model=TableRead)
async def table_detail(
    table_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_table_by_id(db, current_user.restaurant_id, table_id)


@router.put("/tables/{table_id}", response_model=TableRead)
async def edit_table(
    table_id: int,
    payload: TableUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await update_table(db, current_user.restaurant_id, table_id, payload)


@router.patch("/tables/{table_id}/status", response_model=TableRead)
async def change_table_status(
    table_id: int,
    payload: TableStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await update_table_status(db, current_user.restaurant_id, table_id, payload.status)


@router.delete("/tables/{table_id}", status_code=204)
async def remove_table(
    table_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    await delete_table(db, current_user.restaurant_id, table_id)


@router.get("/floor-summary", response_model=FloorSummary)
async def floor_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_floor_summary(db, current_user.restaurant_id)


@router.get("", response_model=list[ReservationRead])
async def list_reservations(
    reservation_date: date | None = None,
    table_id: int | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_reservations(
        db,
        current_user.restaurant_id,
        reservation_date,
        table_id,
        status,
    )


@router.post("", response_model=ReservationRead, status_code=201)
async def add_reservation(
    payload: ReservationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await create_reservation(db, current_user.restaurant_id, payload)


@router.get("/availability")
async def availability(
    reservation_date: date,
    party_size: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await check_availability(db, current_user.restaurant_id, reservation_date, party_size)


@router.get("/{reservation_id}", response_model=ReservationRead)
async def reservation_detail(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_reservation_by_id(db, current_user.restaurant_id, reservation_id)


@router.put("/{reservation_id}", response_model=ReservationRead)
async def edit_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await update_reservation(db, current_user.restaurant_id, reservation_id, payload)


@router.post("/{reservation_id}/seat", response_model=ReservationRead)
async def seat(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await seat_reservation(db, current_user.restaurant_id, reservation_id)


@router.post("/{reservation_id}/complete", response_model=ReservationRead)
async def complete(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await complete_reservation(db, current_user.restaurant_id, reservation_id)


@router.post("/{reservation_id}/cancel", response_model=ReservationRead)
async def cancel(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await cancel_reservation(db, current_user.restaurant_id, reservation_id)


@router.get("/waitlist/active", response_model=list[WaitlistEntryRead])
async def list_waitlist(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_waitlist(db, current_user.restaurant_id)


@router.post("/waitlist", response_model=WaitlistEntryRead, status_code=201)
async def add_to_wait(
    payload: WaitlistEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await add_to_waitlist(db, current_user.restaurant_id, payload)


@router.post("/waitlist/{entry_id}/seat")
async def seat_from_waitlist(
    entry_id: int,
    table_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await seat_waitlist_entry(db, current_user.restaurant_id, entry_id, table_id)


@router.delete("/waitlist/{entry_id}", status_code=204)
async def remove_waitlist(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    await remove_from_waitlist(db, current_user.restaurant_id, entry_id)


@router.get("/sessions/active", response_model=list[TableSessionRead])
async def active_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_active_sessions(db, current_user.restaurant_id)


@router.post("/sessions", response_model=TableSessionRead, status_code=201)
async def start_session(
    payload: TableSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await create_session(db, current_user.restaurant_id, payload)


@router.post("/sessions/{session_id}/close", response_model=TableSessionRead)
async def end_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await close_session(db, current_user.restaurant_id, session_id)
