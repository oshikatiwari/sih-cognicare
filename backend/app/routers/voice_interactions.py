from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.app.db.dependencies import get_db
from backend.app.models.patient import Patient
from backend.app.models.voice_interaction import VoiceInteraction


router = APIRouter(
    prefix="/voice-interactions",
    tags=["voice interactions"],
)


class VoiceInteractionCreate(BaseModel):
    patient_id: str
    transcript: Optional[str] = None
    intent: Optional[str] = None


@router.post("/")
def create_voice_interaction(
    payload: VoiceInteractionCreate,
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

    voice_interaction = VoiceInteraction(
        patient_id=payload.patient_id,
        transcript=payload.transcript,
        intent=payload.intent,
    )

    db.add(voice_interaction)
    db.commit()
    db.refresh(voice_interaction)

    return {
        "id": voice_interaction.id,
        "patient_id": voice_interaction.patient_id,
        "transcript": voice_interaction.transcript,
        "intent": voice_interaction.intent,
        "created_at": voice_interaction.created_at,
    }