from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from backend.app.services.cps_calculator import SessionMetrics, calculate_cps
from backend.app.services.anomaly_detector import check_trend

from backend.app.db.session import SessionLocal
from backend.app.models.cognitive_score import CognitiveScore


router = APIRouter(prefix="/analysis", tags=["analysis"])


class CPSRequest(BaseModel):
    session_id: str
    patient_id: str
    accuracy: float = Field(..., ge=0, le=100)
    response_time: float = Field(..., ge=0)
    completion_rate: float = Field(..., ge=0, le=100)
    attempts: int = 0
    errors: int = 0
    hints_used: int = 0
    is_memory_game: bool = False
    memory_specific_accuracy: Optional[float] = None


class CPSResponse(BaseModel):
    cps: float
    difficulty_tier: str
    sub_scores: dict


class TrendResponse(BaseModel):
    scores: List[dict]
    alert: Optional[str] = None


@router.post("/cps", response_model=CPSResponse)
def calculate_and_store_cps(payload: CPSRequest):
    """Calculate CPS and store it in the database."""

    db = SessionLocal()

    try:
        # Get previous scores for consistency calculation
        previous_scores = (
            db.query(CognitiveScore)
            .filter(CognitiveScore.patient_id == payload.patient_id)
            .order_by(CognitiveScore.created_at.desc())
            .limit(5)
            .all()
        )

        # Reverse so they are chronological
        previous_scores.reverse()

        recent_accuracies = [
            score.accuracy
            for score in previous_scores
        ]

        # Calculate CPS using the existing AI logic
        metrics = SessionMetrics(
            accuracy=payload.accuracy,
            response_time=payload.response_time,
            completion_rate=payload.completion_rate,
            attempts=payload.attempts,
            errors=payload.errors,
            hints_used=payload.hints_used,
            is_memory_game=payload.is_memory_game,
            memory_specific_accuracy=payload.memory_specific_accuracy,
        )

        result = calculate_cps(
            metrics,
            recent_accuracies=recent_accuracies,
        )

        # Save the cognitive score
        cognitive_score = CognitiveScore(
            session_id=payload.session_id,
            patient_id=payload.patient_id,
            cps=result["cps"],
            accuracy=payload.accuracy,
            difficulty_tier=result["difficulty_tier"],
        )

        db.add(cognitive_score)
        db.commit()
        db.refresh(cognitive_score)

        return CPSResponse(
            cps=result["cps"],
            difficulty_tier=result["difficulty_tier"],
            sub_scores=result["sub_scores"],
        )

    finally:
        db.close()


@router.get("/trend/{patient_id}", response_model=TrendResponse)
def get_trend(patient_id: str):
    """Return CPS history and anomaly alerts for a patient."""

    db = SessionLocal()

    try:
        history = (
            db.query(CognitiveScore)
            .filter(CognitiveScore.patient_id == patient_id)
            .order_by(CognitiveScore.created_at.asc())
            .all()
        )

        if not history:
            raise HTTPException(
                status_code=404,
                detail="No score history for this patient",
            )

        scores = [
            {
                "session_id": score.session_id,
                "cps": score.cps,
                "timestamp": score.created_at.isoformat()
                if score.created_at
                else None,
            }
            for score in history
        ]

        cps_values = [
            score.cps
            for score in history
        ]

        anomaly = check_trend(cps_values)

        alert_message = (
            anomaly["message"]
            if anomaly
            else None
        )

        return TrendResponse(
            scores=scores,
            alert=alert_message,
        )

    finally:
        db.close()