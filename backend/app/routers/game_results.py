from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from backend.app.db.dependencies import get_db
from backend.app.models.game_session import GameSession
from backend.app.models.game_result import GameResult


router = APIRouter(
    prefix="/game-results",
    tags=["game results"],
)


class GameResultCreate(BaseModel):
    session_id: str

    score: Optional[float] = None
    accuracy: Optional[float] = Field(None, ge=0, le=100)
    response_time: Optional[float] = Field(None, ge=0)
    completion_rate: Optional[float] = Field(None, ge=0, le=100)

    attempts: int = Field(0, ge=0)
    errors: int = Field(0, ge=0)
    hints_used: int = Field(0, ge=0)

    completed: bool = True


@router.post("/")
def create_game_result(
    payload: GameResultCreate,
    db: Session = Depends(get_db),
):
    game_session = (
        db.query(GameSession)
        .filter(GameSession.id == payload.session_id)
        .first()
    )

    if not game_session:
        raise HTTPException(
            status_code=404,
            detail="Game session not found",
        )

    game_result = GameResult(
        session_id=payload.session_id,
        score=payload.score,
        accuracy=payload.accuracy,
        response_time=payload.response_time,
        completion_rate=payload.completion_rate,
        attempts=payload.attempts,
        errors=payload.errors,
        hints_used=payload.hints_used,
        completed=payload.completed,
    )

    db.add(game_result)
    db.commit()
    db.refresh(game_result)

    return {
        "id": game_result.id,
        "session_id": game_result.session_id,
        "score": game_result.score,
        "accuracy": game_result.accuracy,
        "response_time": game_result.response_time,
        "completion_rate": game_result.completion_rate,
        "attempts": game_result.attempts,
        "errors": game_result.errors,
        "hints_used": game_result.hints_used,
        "completed": game_result.completed,
        "synced": game_result.synced,
        "created_at": game_result.created_at,
    }