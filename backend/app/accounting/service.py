from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounting.models import Budget, ChartOfAccount, GLEntry, Invoice
from app.accounting.schemas import BudgetCreate, GLEntryCreate, InvoiceCreate


async def get_gl_entries(db: AsyncSession, limit: int = 100) -> list[GLEntry]:
    result = await db.execute(
        select(GLEntry).order_by(GLEntry.date.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def create_gl_entry(db: AsyncSession, payload: GLEntryCreate) -> GLEntry:
    entry = GLEntry(**payload.model_dump())
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return entry


async def get_invoices(
    db: AsyncSession, status_filter: str | None = None, limit: int = 100
) -> list[Invoice]:
    query = select(Invoice).order_by(Invoice.date.desc()).limit(limit)
    if status_filter:
        query = query.where(Invoice.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_invoice(db: AsyncSession, payload: InvoiceCreate) -> Invoice:
    invoice = Invoice(**payload.model_dump())
    db.add(invoice)
    await db.flush()
    await db.refresh(invoice)
    return invoice


async def get_pl_report(db: AsyncSession, period: str | None = None) -> dict:
    revenue_result = await db.execute(
        select(GLEntry).join(ChartOfAccount).where(ChartOfAccount.type == "revenue")
    )
    revenue_entries = revenue_result.scalars().all()

    expense_result = await db.execute(
        select(GLEntry).join(ChartOfAccount).where(ChartOfAccount.type == "expense")
    )
    expense_entries = expense_result.scalars().all()

    total_revenue = sum(e.credit - e.debit for e in revenue_entries)
    total_expenses = sum(e.debit - e.credit for e in expense_entries)

    return {
        "period": period or "all",
        "total_revenue": float(total_revenue),
        "total_expenses": float(total_expenses),
        "net_income": float(total_revenue - total_expenses),
    }


async def get_budgets(db: AsyncSession, period: str | None = None) -> list[Budget]:
    query = select(Budget).order_by(Budget.period)
    if period:
        query = query.where(Budget.period == period)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_budget(db: AsyncSession, payload: BudgetCreate) -> Budget:
    budget = Budget(**payload.model_dump())
    db.add(budget)
    await db.flush()
    await db.refresh(budget)
    return budget


async def get_cash_flow(db: AsyncSession) -> dict:
    result = await db.execute(select(GLEntry).order_by(GLEntry.date.desc()))
    entries = result.scalars().all()

    inflows = sum(float(e.debit) for e in entries)
    outflows = sum(float(e.credit) for e in entries)

    return {
        "total_inflows": inflows,
        "total_outflows": outflows,
        "net_cash_flow": inflows - outflows,
        "entry_count": len(entries),
    }
