import uuid
import contextvars

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(rid)
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response


def get_request_id() -> str:
    return request_id_var.get()
