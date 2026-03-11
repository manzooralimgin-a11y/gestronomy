from datetime import datetime

from sqlalchemy import JSON, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    event_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_payload: Mapped[dict | list] = mapped_column(JSON, nullable=False)
    headers: Mapped[dict | list] = mapped_column(JSON, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(20), default="received", nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

class WebhookAudit(Base):
    __tablename__ = "webhook_audit"

    event_id: Mapped[str] = mapped_column(String(50), ForeignKey("webhook_events.event_id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    actor: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
