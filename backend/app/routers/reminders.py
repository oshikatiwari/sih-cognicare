from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from backend.app.db.dependencies import get_db
from backend.app.models.patient import Patient
from backend.app.models.reminder import Reminder


router = APIRouter(
    prefix="/reminders",
    tags=["reminders"],
)


class ReminderCreate(BaseModel):
    patient_id: str
    message: str
    scheduled_time: Optional[datetime] = None


@router.post("/")
def create_reminder(
    payload: ReminderCreate,
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

    reminder = Reminder(
        patient_id=payload.patient_id,
        message=payload.message,
        scheduled_time=payload.scheduled_time,
        completed=False,
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return {
        "id": reminder.id,
        "patient_id": reminder.patient_id,
        "message": reminder.message,
        "scheduled_time": reminder.scheduled_time,
        "completed": reminder.completed,
        "created_at": reminder.created_at,
    }


@router.put("/{reminder_id}/complete")
def complete_reminder(
    reminder_id: str,
    db: Session = Depends(get_db),
):

    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id)
        .first()
    )

    if not reminder:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found",
        )

    reminder.completed = True

    db.commit()
    db.refresh(reminder)

    return {
        "id": reminder.id,
        "patient_id": reminder.patient_id,
        "message": reminder.message,
        "scheduled_time": reminder.scheduled_time,
        "completed": reminder.completed,
    }