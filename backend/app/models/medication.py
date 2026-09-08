import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from backend.app.db.base import Base


class Medication(Base):
    __tablename__ = "medication"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    patient_id = Column(
        String,
        ForeignKey("patients.id"),
        nullable=False,
    )

    name = Column(String, nullable=False)

    dosage = Column(String, nullable=True)

    schedule = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )