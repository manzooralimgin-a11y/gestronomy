from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/webhook")
async def stripe_webhook(request: Request) -> JSONResponse:
    """Placeholder for Stripe webhook endpoint."""
    return JSONResponse(content={"status": "not_configured"}, status_code=200)
