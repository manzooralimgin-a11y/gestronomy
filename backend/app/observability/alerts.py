import logging
from typing import Any

logger = logging.getLogger("app.observability.alerts")

async def trigger_alert(alert_type: str, severity: str, message: str, context: dict[str, Any] | None = None) -> None:
    """
    Trigger an alert for the observability system.
    This serves as a foundational stub for integrating with tools like PagerDuty or Slack.
    
    Args:
        alert_type: The category of the alert (e.g., "high_error_rate", "queue_lag").
        severity: "info", "warning", "critical".
        message: Human-readable alert description.
        context: Additional metadata.
    """
    payload = {
        "event": "system_alert",
        "alert_type": alert_type,
        "severity": severity,
        "message": message,
        "context": context or {},
    }
    
    # Log the alert payload as JSON
    logger.error(str(payload)) if severity == "critical" else logger.warning(str(payload))
    
    # TODO: Add specific integrations here (e.g., Slack Webhook, PagerDuty API)
