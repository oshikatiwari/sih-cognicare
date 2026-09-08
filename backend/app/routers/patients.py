from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from backend.app.db.dependencies import get_db
from backend.app.models.patient import Patient


router = APIRouter(
    prefix="/patients",
    tags=["patients"],
)


class PatientCreate(BaseModel):
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    age: Optional[str] = Field(
        None,
        max_length=3,
    )

    preferred_language: Optional[str] = Field(
        "English",
        max_length=50,
    )


@router.post("/")
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
):
    patient = Patient(
        full_name=payload.full_name.strip(),
        age=payload.age,
        preferred_language=payload.preferred_language,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return {
        "id": patient.id,
        "full_name": patient.full_name,
        "age": patient.age,
        "preferred_language": patient.preferred_language,
        "created_at": patient.created_at,
        "updated_at": patient.updated_at,
        "synced": patient.synced,
    }


@router.get("/{patient_id}")
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    return {
        "id": patient.id,
        "full_name": patient.full_name,
        "age": patient.age,
        "preferred_language": patient.preferred_language,
        "created_at": patient.created_at,
        "updated_at": patient.updated_at,
        "synced": patient.synced,
    }