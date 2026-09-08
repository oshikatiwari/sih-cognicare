from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from backend.app.db.dependencies import get_db
from backend.app.models.patient import Patient
from backend.app.models.game_session import GameSession


router = APIRouter(
    prefix="/game-sessions",
    tags=["game sessions"],
)


class GameSessionCreate(BaseModel):
    patient_id: str

    game_type: str = Field(..., min_length=1)
    difficulty_level: Optional[str] = None

    score: Optional[float] = Field(None, ge=0)

    accuracy: Optional[float] = Field(
        None,
        ge=0,
        le=100,
    )

    response_time: Optional[float] = Field(
        None,
        ge=0,
    )

    completion_rate: Optional[float] = Field(
        None,
        ge=0,
        le=100,
    )

    attempts: int = Field(
        0,
        ge=0,
    )

    errors: int = Field(
        0,
        ge=0,
    )

    hints_used: int = Field(
        0,
        ge=0,
    )

    is_memory_game: bool = False

    memory_specific_accuracy: Optional[float] = Field(
        None,
        ge=0,
        le=100,
    )


@router.post("/")
def create_game_session(
    payload: GameSessionCreate,
    db: Session = Depends(get_db),
):

    patient = (
        db.query(Patient)
        .filter(Patient.id == payload.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    game_session = GameSession(
        patient_id=payload.patient_id,

        game_type=payload.game_type,
        difficulty_level=payload.difficulty_level,

        score=payload.score,
        accuracy=payload.accuracy,
        response_time=payload.response_time,
        completion_rate=payload.completion_rate,

        attempts=payload.attempts,
        errors=payload.errors,
        hints_used=payload.hints_used,

        is_memory_game=payload.is_memory_game,
        memory_specific_accuracy=payload.memory_specific_accuracy,
    )

    db.add(game_session)
    db.commit()
    db.refresh(game_session)

    return {
        "id": game_session.id,
        "patient_id": game_session.patient_id,
        "game_type": game_session.game_type,
        "difficulty_level": game_session.difficulty_level,
        "score": game_session.score,
        "accuracy": game_session.accuracy,
        "response_time": game_session.response_time,
        "completion_rate": game_session.completion_rate,
        "attempts": game_session.attempts,
        "errors": game_session.errors,
        "hints_used": game_session.hints_used,
        "is_memory_game": game_session.is_memory_game,
        "memory_specific_accuracy": game_session.memory_specific_accuracy,
        "status": game_session.status,
        "synced": game_session.synced,
        "started_at": game_session.started_at,
        "updated_at": game_session.updated_at,
    }


@router.get("/{session_id}")
def get_game_session(
    session_id: str,
    db: Session = Depends(get_db),
):

    game_session = (
        db.query(GameSession)
        .filter(GameSession.id == session_id)
        .first()
    )

    if not game_session:
        raise HTTPException(
            status_code=404,
            detail="Game session not found",
        )

    return {
        "id": game_session.id,
        "patient_id": game_session.patient_id,
        "game_type": game_session.game_type,
        "difficulty_level": game_session.difficulty_level,
        "score": game_session.score,
        "accuracy": game_session.accuracy,
        "response_time": game_session.response_time,
        "completion_rate": game_session.completion_rate,
        "attempts": game_session.attempts,
        "errors": game_session.errors,
        "hints_used": game_session.hints_used,
        "is_memory_game": game_session.is_memory_game,
        "memory_specific_accuracy": game_session.memory_specific_accuracy,
        "status": game_session.status,
        "synced": game_session.synced,
        "started_at": game_session.started_at,
        "completed_at": game_session.completed_at,
        "updated_at": game_session.updated_at,
    }
