import logging
import resend

from app.config import settings
from app.vouchers.qr_service import generate_qr_base64

logger = logging.getLogger(__name__)

def send_voucher_email(voucher_id: int, code: str, amount: float, email: str, name: str | None = None):
    """
    Sends the digital voucher using the Resend Python SDK.
    Executes in a FastAPI BackgroundTask.
    """
    logger.info(f"Preparing to send Voucher {code} (€{amount}) to {email}")
    
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not configured. Skipping live email delivery.")
        return

    resend.api_key = settings.resend_api_key
    
    qr_b64 = generate_qr_base64(code)
    
    customer_name = name or 'lieber Gast'
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; color: #1e293b; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #0f172a; letter-spacing: 2px; text-transform: uppercase;">DAS ELB</h1>
            <p style="font-size: 18px; color: #64748b;">Dein digitaler Gutschein</p>
        </div>

        <p>Hallo {customer_name},</p>
        <p>vielen Dank für deine Bestellung! Anbei erhältst du deinen digitalen Gutschein für tolle Momente im DAS ELB.</p>
        
        <div style="background: #f8fafc; padding: 30px; border-radius: 12px; margin: 30px 0; border: 1px solid #e2e8f0; text-align: center;">
            <h2 style="margin: 0 0 15px 0; color: #10b981; font-size: 32px;">{amount:.2f} €</h2>
            <div style="background: #ffffff; padding: 15px; border-radius: 8px; display: inline-block; border: 2px dashed #cbd5e1;">
                <img src="{qr_b64}" alt="Gutschein QR Code" style="display: block; margin: 0 auto 15px auto; width: 150px; height: 150px;" />
                <p style="margin: 0; font-size: 24px; font-family: monospace; font-weight: bold; letter-spacing: 2px;">{code}</p>
            </div>
        </div>

        <p>Zeige diesen Code bei deinem nächsten Besuch einfach bei unserem Personal vor oder scanne den QR-Code vor Ort, um den Betrag von deiner Rechnung abziehen zu lassen.</p>
        
        <p style="margin-top: 40px;">Wir freuen uns auf deinen Besuch!<br /><br />Herzliche Grüße,<br /><strong>Dein DAS ELB Team</strong></p>
    </div>
    """
    try:
        response = resend.Emails.send({
            "from": "DAS ELB <onboarding@resend.dev>",
            "to": [email],
            "subject": "Dein DAS ELB Gutschein 🎁",
            "html": html_content
        })
        logger.info(f"✅ EMAIL SENT SUCCESSFULLY -> TO: {email} | RESEND ID: {response.get('id')}")
    except Exception as e:
        logger.error(f"❌ Failed to send email via Resend: {e}")
