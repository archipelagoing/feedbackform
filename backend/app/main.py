import os
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text, update
from sqlalchemy.exc import SQLAlchemyError

from app.api.annotations import router as annotation_router
from app.api.preferences import router as preference_router
from app.api.routes import router
from app.api.setup import router as setup_router
from app.auth import hash_password
from app.config import database_url
from app.db import models as m
from app.db.connection import build_engine
from app.domain.extraction import OpenAIExtractor
from app.domain.login_limits import LoginLimiter

EXPECTED_REVISION = "0001_foundation"


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str
    database: str
    schema_revision: str | None


def create_app(
    url: str | None = None, allowed_origins: set[str] | None = None, extractor=None
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.engine = build_engine(url or database_url())
        app.state.allowed_origins = (
            allowed_origins
            if allowed_origins is not None
            else {
                value.strip()
                for value in os.environ.get(
                    "FEEDBACKFORM_ALLOWED_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000"
                ).split(",")
                if value.strip()
            }
        )
        app.state.dummy_password_hash = hash_password(secrets.token_urlsafe(32))
        app.state.login_limiter = LoginLimiter()
        app.state.extractor = extractor if extractor is not None else OpenAIExtractor()
        # Local pilot runs one API process; interrupted jobs must not block all retries.
        try:
            with app.state.engine.begin() as connection:
                connection.execute(
                    update(m.AgentRun)
                    .where(m.AgentRun.status.in_(["queued", "running"]))
                    .values(status="failed", error_code="interrupted")
                )
        except SQLAlchemyError:
            pass  # Readiness reports missing migrations; startup must still serve health.
        yield
        app.state.engine.dispose()

    app = FastAPI(title="FeedbackForm API", version="0.1.0", lifespan=lifespan)
    app.include_router(router)
    app.include_router(annotation_router)
    app.include_router(setup_router)
    app.include_router(preference_router)

    @app.middleware("http")
    async def private_responses(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_request, exception):
        # Validation errors must not reflect login passwords or private source text.
        errors = [
            {key: error[key] for key in ("loc", "msg", "type")} for error in exception.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": errors})

    @app.get("/api/health", response_model=HealthResponse)
    def health():
        try:
            with app.state.engine.connect() as connection:
                revision = connection.execute(
                    text("SELECT version_num FROM alembic_version")
                ).scalar()
            if revision == EXPECTED_REVISION:
                return HealthResponse(status="ok", database="ready", schema_revision=revision)
        except SQLAlchemyError:
            pass
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "database": "migration_required",
                "schema_revision": None,
            },
        )

    return app


app = create_app()
