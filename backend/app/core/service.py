from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import AgentAction, AgentConfig, AgentLog
from app.core.schemas import AgentConfigUpdate


async def get_all_agents(db: AsyncSession) -> list[AgentConfig]:
    result = await db.execute(select(AgentConfig).order_by(AgentConfig.agent_name))
    return list(result.scalars().all())


async def get_agent_actions(
    db: AsyncSession, agent_name: str, limit: int = 50
) -> list[AgentAction]:
    result = await db.execute(
        select(AgentAction)
        .where(AgentAction.agent_name == agent_name)
        .order_by(AgentAction.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def approve_action(db: AsyncSession, action_id: int, user_id: int) -> AgentAction:
    result = await db.execute(select(AgentAction).where(AgentAction.id == action_id))
    action = result.scalar_one_or_none()
    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Action not found"
        )
    action.status = "approved"
    action.approved_by = user_id
    action.executed_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(action)
    return action


async def update_agent_config(
    db: AsyncSession, agent_name: str, payload: AgentConfigUpdate
) -> AgentConfig:
    result = await db.execute(
        select(AgentConfig).where(AgentConfig.agent_name == agent_name)
    )
    config = result.scalar_one_or_none()
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent config not found"
        )
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    await db.flush()
    await db.refresh(config)
    return config
