"""Local pilot password hashing and opaque server-side cookie sessions."""

import hashlib
import hmac
import os
import secrets
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models as m

COOKIE_NAME = "feedbackform_session"
SESSION_SECONDS = 8 * 60 * 60
SCRYPT_N = 2**17


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode(), salt=salt, n=SCRYPT_N, r=8, p=1, maxmem=256 * 1024 * 1024, dklen=32
    )
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, salt, expected = encoded.split("$")
        if algorithm != "scrypt" or len(salt) != 32 or len(expected) != 64:
            return False
        digest = hashlib.scrypt(
            password.encode(),
            salt=bytes.fromhex(salt),
            n=SCRYPT_N,
            r=8,
            p=1,
            maxmem=256 * 1024 * 1024,
            dklen=32,
        )
        return hmac.compare_digest(digest, bytes.fromhex(expected))
    except (ValueError, TypeError):
        return False


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def csrf_token(raw_session: str) -> str:
    return hmac.new(raw_session.encode(), b"feedbackform:csrf", hashlib.sha256).hexdigest()


def secure_cookies() -> bool:
    return os.environ.get("FEEDBACKFORM_SECURE_COOKIES", "0") == "1"


def get_db(request: Request):
    with Session(request.app.state.engine) as session:
        try:
            yield session
            session.commit()
        except BaseException:
            session.rollback()
            raise


DB = Annotated[Session, Depends(get_db)]


def require_browser_write(request: Request):
    # Require an explicit configured origin and a custom header even for login.
    # No CORS permission is granted to other sites.
    if (
        request.headers.get("origin") not in request.app.state.allowed_origins
        or request.headers.get("x-feedbackform-request") != "1"
    ):
        raise HTTPException(403, "Request origin or browser header is invalid")


def current_session(request: Request, db: DB) -> m.Session:
    raw = request.cookies.get(COOKIE_NAME, "")
    if not raw or len(raw) > 128:
        raise HTTPException(401, "Sign in to continue")
    session = db.scalar(select(m.Session).where(m.Session.token_hash == token_hash(raw)))
    if session is None or session.revoked_at is not None or session.expires_at <= datetime.now(UTC):
        raise HTTPException(401, "Your session has expired. Sign in again.")
    return session


AUTH = Annotated[m.Session, Depends(current_session)]


def require_csrf(request: Request, auth: AUTH):
    require_browser_write(request)
    expected = csrf_token(request.cookies[COOKIE_NAME])
    supplied = request.headers.get("x-csrf-token", "")
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(403, "Refresh your session before making changes")


def member_or_404(db: Session, workspace_id: str, actor_id: str) -> m.Membership:
    membership = db.scalar(
        select(m.Membership).where(
            m.Membership.workspace_id == workspace_id,
            m.Membership.user_id == actor_id,
        )
    )
    if membership is None:
        raise HTTPException(404, "Workspace not found")
    return membership
