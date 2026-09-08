import uuid

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func

from backend.app.db.base import Base


class VoiceInteraction(Base):
    __tablename__ = "voice_interactions"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    patient_id = Column(
        String,
        ForeignKey("patients.id"),
        nullable=False,
    )

    transcript = Column(
        String,
        nullable=True,
    )

    intent = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    synced = Column(
        Boolean,
        default=False,
    )