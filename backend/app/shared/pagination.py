import math
from typing import Any, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


async def paginate(
    session: AsyncSession,
    query: Select[Any],
    params: PaginationParams,
) -> dict[str, Any]:
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    offset = (params.page - 1) * params.per_page
    paginated_query = query.offset(offset).limit(params.per_page)
    result = await session.execute(paginated_query)
    items = list(result.scalars().all())

    return {
        "items": items,
        "total": total,
        "page": params.page,
        "per_page": params.per_page,
        "pages": math.ceil(total / params.per_page) if total > 0 else 0,
    }
