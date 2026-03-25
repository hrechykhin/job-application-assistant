import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import router
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import configure_logging
from app.middleware.logging import RequestLoggingMiddleware

configure_logging()

app = FastAPI(
    title="Job Application Assistant API",
    description="AI-powered EU job application assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Attach limiter to app state (required by slowapi)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.getLogger(__name__).exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
