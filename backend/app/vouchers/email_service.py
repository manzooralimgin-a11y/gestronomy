import asyncio
import logging

from app.vouchers.models import Voucher

logger = logging.getLogger(__name__)

async def send_voucher_email(voucher_id: int, code: str, amount: float, email: str, name: str | None = None):
    """
    STUB: Simulates sending an email with the digital voucher and QR code securely.
    In a production setting, this would integrate with AWS SES, SendGrid, or Postmark.
    """
    logger.info(f"Preparing to send Voucher {code} (€{amount}) to {email}")
    
    # Simulate network latency for SMTP Delivery
    await asyncio.sleep(1.5)
    
    html_content = f"""
    <html>
      <body>
        <h1>Hello {name or 'Valued Customer'},</h1>
        <p>Your digital voucher for <strong>€{amount:.2f}</strong> has been successfully generated!</p>
        <p>Voucher Code: <strong>{code}</strong></p>
        <p>Please present this code or the attached QR code to our staff when checking out.</p>
        <p>Thank you for choosing DAS ELB.</p>
      </body>
    </html>
    """
    logger.info(f"✅ EMAIL SENT SUCCESSFULLY -> TO: {email} | SUBJECT: Your DAS ELB Voucher | CODE: {code}")
    # In production, payload would include the embedded base64 QR string as a CID attachment.
