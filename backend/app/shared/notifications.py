import logging

logger = logging.getLogger(__name__)


class NotificationService:
    async def send_push(self, user_id: int, title: str, body: str) -> None:
        logger.info("Push notification to user %d: %s - %s", user_id, title, body)

    async def send_email(self, to: str, subject: str, body: str) -> None:
        logger.info("Email to %s: %s", to, subject)

    async def send_sms(self, phone: str, message: str) -> None:
        logger.info("SMS to %s: %s", phone, message)


notifications = NotificationService()
