from typing import Literal

from pydantic import BaseModel, Field


class SessionCreateResponse(BaseModel):
    session_id: str
    status: Literal["collecting", "ready", "complete"]
    message: str
    missing_fields: list[str] = Field(default_factory=list)


class SessionInputRequest(BaseModel):
    birthdate: str | None = None
    birth_time: str | None = None
    location: str | None = None


class SessionStateResponse(BaseModel):
    session_id: str
    status: Literal["collecting", "ready", "complete"]
    birthdate: str | None = None
    birth_time: str | None = None
    location: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    prompt: str
    result: dict | None = None


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str
