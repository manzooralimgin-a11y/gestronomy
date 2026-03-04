from __future__ import annotations

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.dashboard.models import AuditEvent

logger = logging.getLogger("app.audit")


def emit_sensitive_audit(
    *,
    action: str,
    tenant_id: int | None,
    user_id: int | None,
    agent_id: str | None,
    status: str,
    detail: str,
    metadata: dict | None = None,
) -> None:
    logger.info(
        json.dumps(
            {
                "event": "sensitive_action_audit",
                "action": action,
                "tenant_id": tenant_id,
                "user_id": user_id,
                "agent_id": agent_id,
                "status": status,
                "detail": detail,
                "metadata": metadata or {},
            }
        )
    )


async def log_human_action(
    db: AsyncSession,
    *,
    action: str,
    detail: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
    source_module: str | None = None,
    restaurant_id: int | None = None,
    actor_name: str = "Authenticated User",
    actor_user_id: int | None = None,
    metadata_json: dict | None = None,
) -> AuditEvent:
    emit_sensitive_audit(
        action=action,
        tenant_id=restaurant_id,
        user_id=actor_user_id,
        agent_id=None,
        status="recorded",
        detail=detail,
        metadata=metadata_json,
    )
    event = AuditEvent(
        restaurant_id=restaurant_id,
        actor_type="human",
        actor_name=actor_name,
        actor_user_id=actor_user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        detail=detail,
        source_module=source_module,
        metadata_json=metadata_json,
    )
    db.add(event)
    await db.flush()
    return event
