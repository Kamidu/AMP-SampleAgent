from fastapi import APIRouter, HTTPException

from app.agent import orchestrator
from app.models import SessionCreateResponse, SessionInputRequest, SessionStateResponse
from app.config import settings
import os


router = APIRouter()


def _to_state_response(state) -> SessionStateResponse:
    return SessionStateResponse(
        session_id=state.session_id,
        status=state.status,
        birthdate=state.birthdate,
        birth_time=state.birth_time,
        location=state.location,
        missing_fields=state.missing_fields(),
        prompt=state.prompt,
        result=state.result,
    )


@router.post("/sessions", response_model=SessionCreateResponse)
def create_session() -> SessionCreateResponse:
    state = orchestrator.create_session()
    return SessionCreateResponse(
        session_id=state.session_id,
        status=state.status,
        message=state.prompt,
        missing_fields=state.missing_fields(),
    )


@router.post("/run", response_model=SessionStateResponse)
def run_once(payload: SessionInputRequest) -> SessionStateResponse:
    """Fast single-run endpoint: accepts all fields and returns the final result.
    If fields are missing, returns status collecting and the next prompt."""
    # create a transient session to reuse the existing orchestrator logic
    s = orchestrator.create_session()
    state = orchestrator.submit_input(
        s.session_id,
        birthdate=payload.birthdate,
        birth_time=payload.birth_time,
        location=payload.location,
    )
    return SessionStateResponse(
        session_id=state.session_id,
        status=state.status,
        birthdate=state.birthdate,
        birth_time=state.birth_time,
        location=state.location,
        missing_fields=state.missing_fields(),
        prompt=state.prompt,
        result=state.result,
    )


@router.post("/sessions/{session_id}/input", response_model=SessionStateResponse)
def submit_input(session_id: str, payload: SessionInputRequest) -> SessionStateResponse:
    state = orchestrator.submit_input(
        session_id=session_id,
        birthdate=payload.birthdate,
        birth_time=payload.birth_time,
        location=payload.location,
    )
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    return _to_state_response(state)


@router.get("/sessions/{session_id}", response_model=SessionStateResponse)
def get_session(session_id: str) -> SessionStateResponse:
    state = orchestrator.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    return _to_state_response(state)
