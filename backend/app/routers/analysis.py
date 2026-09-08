"""
analysis.py
-----------
FastAPI Router exposing AI Cognitive Scoring, Multilingual Voice Intent Guidance,
Bluetooth Speaker Pairing, and Caregiver Monitoring endpoints for Smriti (স্মৃতি).
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.app.services.cps_calculator import (
    calculate_cps,
    SessionMetrics,
    map_to_difficulty_info,
)
from backend.app.services.anomaly_detector import (
    detect_cps_anomalies,
    get_game_monitoring_breakdown,
)
from backend.app.services.voice_assistant import (
    get_supported_languages,
    get_bluetooth_audio_guidance,
    get_screen_voice_guidance,
    process_voice_query,
    translate_text,
)
from backend.app.services.store import FAKE_DB, get_patient_history, save_patient_session


router = APIRouter(prefix="/analysis", tags=["AI Analysis & Voice Guidance"])


class CPSRequest(BaseModel):
    patient_id: str = Field(default="demo-patient-01", description="Unique identifier for patient")
    game_type: str = Field(default="memory_match", description="Game key: memory_match, number_sequence, word_recall, picture_association")
    difficulty: str = Field(default="medium", description="Difficulty: easy, medium, hard")
    accuracy: float = Field(..., ge=0.0, le=100.0, description="Percentage of correct actions (0-100)")
    response_time: float = Field(..., gt=0.0, description="Average response time per action in seconds or ms")
    completion_rate: float = Field(default=100.0, ge=0.0, le=100.0, description="Session completion percentage")
    attempts: int = Field(default=10, ge=1, description="Total attempts in session")
    errors: int = Field(default=0, ge=0, description="Total errors in session")
    hints_used: int = Field(default=0, ge=0, description="Total hints requested")
    memory_specific_accuracy: Optional[float] = Field(default=None, description="Optional domain recall accuracy")


class VoiceQueryRequest(BaseModel):
    patient_id: str = Field(default="demo-patient-01", description="Patient ID")
    spoken_phrase: str = Field(..., description="Spoken voice phrase transcribed by STT")
    language: Optional[str] = Field(default=None, description="Optional language override code (en, hi, as, mzo, kha)")


class TranslationRequest(BaseModel):
    text: str = Field(..., description="Source text to translate")
    source_lang: str = Field(default="en", description="Source language code")
    target_lang: str = Field(..., description="Target language code (en, hi, as, mzo, kha)")


@router.post("/cps", response_model=Dict[str, Any])
def calculate_session_score(payload: CPSRequest):
    """
    Calculates Cognitive Performance Score (CPS) for any game session,
    checks for domain anomalies, and persists session record.
    """
    session = SessionMetrics(
        game_type=payload.game_type,
        difficulty=payload.difficulty,
        accuracy=payload.accuracy,
        response_time=payload.response_time,
        completion_rate=payload.completion_rate,
        attempts=payload.attempts,
        errors=payload.errors,
        hints_used=payload.hints_used,
        is_memory_game=True,
        memory_specific_accuracy=payload.memory_specific_accuracy,
    )

    history = get_patient_history(payload.patient_id)
    recent_accuracies = [h.get("accuracy", 80.0) for h in history[-5:]]

    cps_result = calculate_cps(session, recent_accuracies=recent_accuracies)

    # Persist session to store
    session_record = {
        "cps": cps_result["cps"],
        "game_type": payload.game_type,
        "difficulty": payload.difficulty,
        "accuracy": payload.accuracy,
        "response_time": payload.response_time,
        "completion_rate": payload.completion_rate,
        "display_label": cps_result["display_label"],
    }
    save_patient_session(payload.patient_id, session_record)

    # Check for domain anomalies
    updated_history = get_patient_history(payload.patient_id)
    anomaly_status = detect_cps_anomalies(updated_history)

    return {
        "status": "success",
        "patient_id": payload.patient_id,
        "cps_score": cps_result["cps"],
        "game_type": payload.game_type,
        "difficulty": payload.difficulty,
        "cognitive_domain": cps_result["cognitive_domain"],
        "difficulty_tier": cps_result["difficulty_tier"],
        "display_label": cps_result["display_label"],
        "caregiver_summary": cps_result["caregiver_summary"],
        "sub_scores": cps_result["sub_scores"],
        "anomaly_status": anomaly_status,
    }


@router.get("/trend/{patient_id}", response_model=Dict[str, Any])
def get_patient_trend(patient_id: str):
    """Returns longitudinal trend history and anomaly evaluation for caregiver review."""
    history = get_patient_history(patient_id)
    if not history:
        raise HTTPException(status_code=404, detail=f"No patient history found for {patient_id}")

    cps_trend = [round(h["cps"], 1) for h in history]
    anomaly_eval = detect_cps_anomalies(history)

    return {
        "patient_id": patient_id,
        "total_sessions": len(history),
        "latest_cps": cps_trend[-1],
        "cps_history": cps_trend,
        "anomaly_status": anomaly_eval,
    }


@router.get("/monitoring/{patient_id}", response_model=Dict[str, Any])
def get_monitoring_dashboard(patient_id: str):
    """Returns per-game monitoring breakdown for caregiver dashboards."""
    history = get_patient_history(patient_id)
    breakdown = get_game_monitoring_breakdown(history)
    anomaly_status = detect_cps_anomalies(history)

    return {
        "patient_id": patient_id,
        "monitoring_breakdown": breakdown,
        "anomaly_status": anomaly_status,
    }


@router.get("/languages", response_model=List[Dict[str, str]])
def list_languages():
    """Returns catalog of supported languages for Duolingo-style picker."""
    return get_supported_languages()


@router.get("/voice-guidance/{screen_id}", response_model=Dict[str, Any])
def get_voice_guidance(
    screen_id: str,
    lang: str = Query(default="en", description="Language code: en, hi, as, mzo, kha"),
    patient_id: str = Query(default="demo-patient-01", description="Patient ID"),
):
    """Returns step-by-step spoken guidance prompt for any screen or game in 5 languages."""
    return get_screen_voice_guidance(screen_id=screen_id, lang=lang, patient_id=patient_id)


@router.post("/voice-intent", response_model=Dict[str, Any])
def parse_voice_intent(payload: VoiceQueryRequest):
    """Parses spoken phrase, detects intent & language, and provides TTS response."""
    return process_voice_query(
        patient_id=payload.patient_id,
        spoken_phrase=payload.spoken_phrase,
        forced_lang=payload.language,
    )


@router.post("/translate", response_model=Dict[str, str])
def handle_translation(payload: TranslationRequest):
    """Translates text or guidance phrase on-demand."""
    return translate_text(
        text=payload.text,
        source_lang=payload.source_lang,
        target_lang=payload.target_lang,
    )


@router.get("/bluetooth-guidance", response_model=Dict[str, str])
def get_bluetooth_guidance(lang: str = Query(default="en", description="Language code")):
    """Returns spoken notification prompt for Bluetooth speaker / hearing aid pairing."""
    return get_bluetooth_audio_guidance(lang=lang)
