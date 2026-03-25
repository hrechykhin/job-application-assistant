import time
import uuid
from contextvars import ContextVar

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_request_id_var: ContextVar[str] = ContextVar("request_id", default="")

logger = structlog.get_logger(__name__)


def get_request_id() -> str:
    return _request_id_var.get()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = _request_id_var.set(request_id)
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        status_code = 500
        logger.info("request.start", method=request.method, path=request.url.path)

        try:
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception:
            logger.exception(
                "request.unhandled_error",
                method=request.method,
                path=request.url.path,
            )
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            logger.info(
                "request.end",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            structlog.contextvars.clear_contextvars()
            _request_id_var.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response
