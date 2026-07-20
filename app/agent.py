from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from openai import OpenAI

from app.config import settings
from app.stub_calculator import generate_birth_map
from app.azure_client import get_openai_client


REQUIRED_FIELDS = ["birthdate", "birth_time", "location"]


@dataclass
class SessionState:
    session_id: str
    birthdate: str | None = None
    birth_time: str | None = None
    location: str | None = None
    status: str = "collecting"
    prompt: str = "Please provide your birthdate (YYYY-MM-DD)."
    result: dict | None = None
    history: list[dict] = field(default_factory=list)

    def missing_fields(self) -> list[str]:
        return [name for name in REQUIRED_FIELDS if getattr(self, name) in (None, "")]


class AgentOrchestrator:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}
        self._client = self._build_client()

    def _build_client(self) -> OpenAI | None:
        try:
            return get_openai_client()
        except Exception:
            return None

    def create_session(self) -> SessionState:
        session_id = str(uuid.uuid4())
        state = SessionState(session_id=session_id)
        self._sessions[session_id] = state
        return state

    def get_session(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    def submit_input(
        self,
        session_id: str,
        birthdate: str | None,
        birth_time: str | None,
        location: str | None,
    ) -> SessionState | None:
        state = self._sessions.get(session_id)
        if not state:
            return None

        if birthdate:
            state.birthdate = birthdate
        if birth_time:
            state.birth_time = birth_time
        if location:
            state.location = location

        state.history.append(
            {
                "time": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "input": {
                    "birthdate": birthdate,
                    "birth_time": birth_time,
                    "location": location,
                },
            }
        )

        missing = state.missing_fields()
        if missing:
            state.status = "collecting"
            state.prompt = self._ask_next_question_with_llm(state, missing)
            return state

        state.status = "ready"
        normalized = self._normalize_with_llm(state)
        state.birthdate = normalized["birthdate"]
        state.birth_time = normalized["birth_time"]
        state.location = normalized["location"]
        state.result = generate_birth_map(state.birthdate, state.birth_time, state.location)
        state.status = "complete"
        state.prompt = "Birth map generated."
        return state

    def _ask_next_question_with_llm(self, state: SessionState, missing: list[str]) -> str:
        fallback = f"Please provide your {missing[0].replace('_', ' ')}."
        if not self._client:
            return fallback

        msg = (
            "You are a concise assistant collecting three fields for a birth-map demo: "
            "birthdate (YYYY-MM-DD), birth_time (HH:MM 24h), location (City, Country). "
            "Ask for only the next missing field in one sentence."
        )
        user_ctx = (
            f"Known values: birthdate={state.birthdate}, birth_time={state.birth_time}, "
            f"location={state.location}. Missing={missing}."
        )
        try:
            response = self._client.responses.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                input=[
                    {"role": "system", "content": msg},
                    {"role": "user", "content": user_ctx},
                ],
            )
            text = (response.output_text or "").strip()
            return text or fallback
        except Exception:
            return fallback

    def _normalize_with_llm(self, state: SessionState) -> dict[str, str]:
        fallback = {
            "birthdate": state.birthdate or "",
            "birth_time": state.birth_time or "",
            "location": state.location or "",
        }

        if not self._client:
            return fallback

        prompt = (
            "Normalize the following user inputs without changing meaning. "
            "Output strict JSON with keys: birthdate, birth_time, location. "
            "birthdate format YYYY-MM-DD, birth_time format HH:MM (24h)."
        )
        user_ctx = (
            f"birthdate={state.birthdate}\n"
            f"birth_time={state.birth_time}\n"
            f"location={state.location}"
        )

        try:
            response = self._client.responses.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                input=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_ctx},
                ],
            )
            payload = (response.output_text or "").strip()
            if payload.startswith("```"):
                payload = payload.strip("`")
                if payload.startswith("json"):
                    payload = payload[4:].strip()
            import json

            data = json.loads(payload)
            return {
                "birthdate": str(data.get("birthdate", fallback["birthdate"])),
                "birth_time": str(data.get("birth_time", fallback["birth_time"])),
                "location": str(data.get("location", fallback["location"])),
            }
        except Exception:
            return fallback


orchestrator = AgentOrchestrator()
