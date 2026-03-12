import json
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Header, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.integrations.schemas import VoiceBookerEvent, WebhookResponse
from app.integrations.service import verify_signature, store_webhook_event

router = APIRouter(prefix="/webhooks", tags=["integrations"])

@router.post("/voicebooker", response_model=WebhookResponse)
async def receive_voicebooker_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_vb_signature: str = Header(None, alias="X-VB-Signature"),
    x_vb_timestamp: str = Header(None, alias="X-VB-Timestamp"),
    db: AsyncSession = Depends(get_db)
):
    raw_body = await request.body()
    
    # 1. Verify Timestamp Skew (5 mins)
    if not x_vb_timestamp:
        raise HTTPException(status_code=401, detail="Missing X-VB-Timestamp header")
    try:
        ts = datetime.fromisoformat(x_vb_timestamp.replace('Z', '+00:00'))
        skew = abs((datetime.now(timezone.utc) - ts).total_seconds())
        if skew > 300:
            raise HTTPException(status_code=401, detail="Timestamp skew too large")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid timestamp format")

    # 2. Verify Signature
    secret = getattr(settings, "voicebooker_secret", "dev_secret_key")
    if not verify_signature(raw_body, x_vb_signature, x_vb_timestamp, secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    # 3. Parse JSON
    try:
        payload_dict = json.loads(raw_body)
        evt = VoiceBookerEvent(**payload_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON or schema")
        
    # 4. Idempotent Storage
    try:
        headers_dict = dict(request.headers.items())
        inserted = await store_webhook_event(db, evt.event_id, payload_dict, headers_dict)
        
        if inserted:
            from app.integrations.tasks import process_voicebooker_event
            process_voicebooker_event.delay(evt.event_id)

        return WebhookResponse(status="accepted", event_id=evt.event_id)
    except Exception as e:
        await db.rollback()
        import traceback
        return WebhookResponse(status=f"error: {str(e)} | trace: {traceback.format_exc()}", event_id=evt.event_id)
