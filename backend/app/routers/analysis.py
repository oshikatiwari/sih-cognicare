"""
app/routers/analysis.py
------------------------
FastAPI router for the AI Analysis Module.

Exposes:
  POST /analysis/cps                 -> calculate + store a CPS score
  GET  /analysis/trend/{patient_id}  -> return score history + alert flag

Resilient default values added to support seamless integration with
Flutter mobile app UI and React Caregiver Dashboard demo calls.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from backend.app.services.cps_calculator import SessionMetrics, calculate_cps
from backend.app.services.anomaly_detector import check_trend
from backend.app.services.store import FAKE_DB  # shared with seed_demo_data.py

router = APIRouter(prefix="/analysis", tags=["analysis"])


class CPSRequest(BaseModel):
    session_id: str = Field("demo-session-01", description="Unique session ID")
    patient_id: str = Field("demo-patient-01", description="Patient ID")
    accuracy: float = Field(80.0, ge=0, le=100, description="% correct")
    response_time: float = Field(2500.0, ge=0, description="ms or seconds per answer")
    completion_rate: float = Field(100.0, ge=0, le=100, description="% completed")
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
    """Calculates CPS for one session, stores it, returns score + tier."""
    history = FAKE_DB.get(payload.patient_id, [])
    recent_accuracies = [h["accuracy"] for h in history[-5:]]  # last 5 sessions

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

    result = calculate_cps(metrics, recent_accuracies=recent_accuracies)

    # store for trend/history lookups
    FAKE_DB.setdefault(payload.patient_id, []).append({
        "session_id": payload.session_id,
        "cps": result["cps"],
        "accuracy": payload.accuracy,
        "timestamp": datetime.now().isoformat(),
    })

    return CPSResponse(
        cps=result["cps"],
        difficulty_tier=result["difficulty_tier"],
        sub_scores=result["sub_scores"],
    )


@router.get("/trend/{patient_id}", response_model=TrendResponse)
def get_trend(patient_id: str):
    """Returns CPS history for a patient plus an alert if a significant drop occurred."""
    history = FAKE_DB.get(patient_id, [])
    if not history:
        # Return clean empty structure instead of 404 error for graceful UI rendering
        return TrendResponse(scores=[], alert=None)

    scores = [{"session_id": h["session_id"], "cps": h["cps"], "timestamp": h["timestamp"]}
              for h in history]
    cps_values = [h["cps"] for h in history]

    anomaly = check_trend(cps_values)
    alert_message = anomaly["message"] if anomaly else None

    return TrendResponse(scores=scores, alert=alert_message)
