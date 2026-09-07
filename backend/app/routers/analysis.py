"""
app/routers/analysis.py
------------------------
FastAPI router for Smriti AI Analysis, Caregiver Support, 5-Language Voice Engine & Bluetooth Speaker Guidance.

Features:
  - Duolingo-style 5-Language Catalog (en, hi, as, mzo, kha)
  - On-Demand Translation Service
  - Bluetooth Speaker & Hearing Aid Audio Guidance for Elderly Patients
  - Step-by-Step Screen Guidance per screen
  - CPS Scoring & Caregiver Progress History
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from backend.app.services.cps_calculator import SessionMetrics, calculate_cps
from backend.app.services.anomaly_detector import check_trend
from backend.app.services.store import FAKE_DB
from backend.app.services.voice_assistant import (
    process_voice_query,
    get_screen_voice_guidance,
    get_supported_languages,
    get_bluetooth_audio_guidance,
    translate_text,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


class CPSRequest(BaseModel):
    session_id: str = Field("demo-session-01", description="Unique session ID")
    patient_id: str = Field("demo-patient-01", description="Patient profile ID")
    accuracy: float = Field(80.0, ge=0, le=100, description="Percentage of correct answers (%)")
    response_time: float = Field(2500.0, ge=0, description="Average response timing per action (seconds or ms)")
    completion_rate: float = Field(100.0, ge=0, le=100, description="Percentage of session completed (%)")
    attempts: int = Field(0, description="Total attempts taken")
    errors: int = Field(0, description="Number of minor errors")
    hints_used: int = Field(0, description="Number of hints requested")
    is_memory_game: bool = Field(False, description="True if session was a memory recall activity")
    memory_specific_accuracy: Optional[float] = Field(None, description="Memory recall accuracy score (%)")


class CPSResponse(BaseModel):
    cps: float = Field(..., description="Overall Cognitive Performance Score (0-100)")
    difficulty_tier: str = Field(..., description="Technical engagement level name (Easy, Moderate, Medium-Hard, Hard)")
    display_label: Optional[str] = Field(None, description="Warm, patient-facing display label (e.g. Comfortable Pace, Gentle Challenge)")
    sub_scores: dict = Field(..., description="Detailed breakdowns across accuracy, speed, completion, consistency, and memory")


class TrendResponse(BaseModel):
    scores: List[dict] = Field(..., description="Chronological progress history")
    alert: Optional[str] = Field(None, description="Caregiver notification message if a gentle check-in is recommended")


class VoiceQueryRequest(BaseModel):
    patient_id: str = Field("demo-patient-01", description="Patient profile ID")
    spoken_phrase: str = Field("How am I doing today?", description="Spoken text query in English, Hindi, Assamese, Mizo, or Khasi")
    lang: Optional[str] = Field(None, description="Optional language override code: en, hi, as, mzo, kha")


class VoiceQueryResponse(BaseModel):
    patient_id: str
    input_phrase: str
    detected_language: str
    detected_intent: str
    response_text: str
    action: dict


class VoiceGuidanceResponse(BaseModel):
    patient_id: str
    screen_id: str
    language: str
    spoken_guidance: str
    next_step_instruction: str


class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text or guidance phrase to translate")
    source_lang: str = Field("en", description="Source language code")
    target_lang: str = Field("hi", description="Target language code: en, hi, as, mzo, kha")


class TranslationResponse(BaseModel):
    source_lang: str
    target_lang: str
    original_text: str
    translated_text: str


@router.get("/languages")
def get_language_catalog():
    """Returns Duolingo-style 5-language selection catalog (en, hi, as, mzo, kha)."""
    return get_supported_languages()


@router.get("/bluetooth-guidance")
def get_bluetooth_pairing_guidance(lang: str = Query("en", description="Language code: en, hi, as, mzo, kha")):
    """Returns spoken notification prompt when Bluetooth speaker, hearing aid, phone, or PC is paired."""
    return get_bluetooth_audio_guidance(lang=lang)


@router.post("/translate", response_model=TranslationResponse)
def translate_guidance(payload: TranslationRequest):
    """Translates text or guidance phrase on-demand between any of the 5 supported languages."""
    return translate_text(payload.text, payload.source_lang, payload.target_lang)


@router.post("/cps", response_model=CPSResponse)
def calculate_and_store_cps(payload: CPSRequest):
    """
    Evaluates gameplay metrics from a finished activity round, computes a supportive
    Cognitive Performance Score (CPS), and updates the patient's recommended practice level.
    """
    history = FAKE_DB.get(payload.patient_id, [])
    recent_accuracies = [h["accuracy"] for h in history[-5:]]

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

    FAKE_DB.setdefault(payload.patient_id, []).append({
        "session_id": payload.session_id,
        "cps": result["cps"],
        "accuracy": payload.accuracy,
        "timestamp": datetime.now().isoformat(),
    })

    return CPSResponse(
        cps=result["cps"],
        difficulty_tier=result["difficulty_tier"],
        display_label=result.get("display_label"),
        sub_scores=result["sub_scores"],
    )


@router.get("/trend/{patient_id}", response_model=TrendResponse)
def get_trend(patient_id: str):
    """
    Returns progress trend history for family caregivers and highlights when extra
    support or a gentle check-in may be helpful.
    """
    history = FAKE_DB.get(patient_id, [])
    if not history:
        return TrendResponse(scores=[], alert=None)

    scores = [{"session_id": h["session_id"], "cps": h["cps"], "timestamp": h["timestamp"]}
              for h in history]
    cps_values = [h["cps"] for h in history]

    anomaly = check_trend(cps_values)
    alert_message = anomaly["message"] if anomaly else None

    return TrendResponse(scores=scores, alert=alert_message)


@router.post("/voice-intent", response_model=VoiceQueryResponse)
def process_voice_intent(payload: VoiceQueryRequest):
    """
    Processes spoken voice queries from elderly dementia patients in English, Hindi, Assamese, Mizo, or Khasi.
    Detects intent, fetches patient context (e.g. current CPS score), and returns a TTS-ready response.
    """
    result = process_voice_query(payload.patient_id, payload.spoken_phrase, forced_lang=payload.lang)
    return VoiceQueryResponse(
        patient_id=result["patient_id"],
        input_phrase=result["input_phrase"],
        detected_language=result["detected_language"],
        detected_intent=result["detected_intent"],
        response_text=result["response_text"],
        action=result["action"],
    )


@router.get("/voice-guidance/{screen_id}", response_model=VoiceGuidanceResponse)
def get_voice_guidance_for_screen(
    screen_id: str,
    lang: str = Query("en", description="Language code: en, hi, as, mzo, kha"),
    patient_id: str = Query("demo-patient-01", description="Patient profile ID"),
):
    """
    Provides step-by-step spoken navigation guidance across 5 languages (English, Hindi, Assamese, Mizo, Khasi)
    for elderly dementia patients entering any screen (home, games_menu, gameplay, game_results, reminders).
    """
    result = get_screen_voice_guidance(screen_id=screen_id, lang=lang, patient_id=patient_id)
    return VoiceGuidanceResponse(
        patient_id=result["patient_id"],
        screen_id=result["screen_id"],
        language=result["language"],
        spoken_guidance=result["spoken_guidance"],
        next_step_instruction=result["next_step_instruction"],
    )
