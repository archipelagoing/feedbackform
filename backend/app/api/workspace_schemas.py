from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, SecretStr

from app.api.schemas import Body, Contract, ShortText


class LoginRequest(Contract):
    login_name: Annotated[str, Field(min_length=1, max_length=120, pattern=r"^[a-z0-9_.-]+$")]
    password: SecretStr = Field(min_length=12, max_length=256)


class UserView(Contract):
    id: UUID
    display_name: str
    login_name: str


class AuthView(Contract):
    user: UserView
    csrf_token: str


class MemberView(Contract):
    user: UserView
    role: Literal["owner", "participant"]


class WorkspaceView(Contract):
    id: UUID
    title: str
    goal: str
    input_revision: int
    members: list[MemberView]


class IdeaView(Contract):
    id: UUID
    workspace_id: UUID
    version_id: UUID
    version: int
    title: str | None
    body: str
    author: UserView
    created_at: datetime
    updated_at: datetime


class IdeaHistoryView(Contract):
    version_id: UUID
    version: int
    title: str | None
    body: str
    created_at: datetime


class PilotMember(Contract):
    login_name: Annotated[str, Field(min_length=1, max_length=120, pattern=r"^[a-z0-9_.-]+$")]
    display_name: Annotated[str, Field(min_length=1, max_length=120, pattern=r"\S")]
    password: SecretStr = Field(min_length=12, max_length=256)


class PilotSetup(Contract):
    title: ShortText
    goal: Body
    members: Annotated[list[PilotMember], Field(min_length=4, max_length=4)]
