import uuid

from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func

from backend.app.db.base import Base


class CognitiveScore(Base):
    __tablename__ = "cognitive_scores"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    session_id = Column(
        String,
        ForeignKey("game_sessions.id"),
        nullable=False,
    )

    patient_id = Column(
        String,
        ForeignKey("patients.id"),
        nullable=False,
    )

    cps = Column(
        Float,
        nullable=False,
    )

    accuracy = Column(
        Float,
        nullable=False,
    )

    difficulty_tier = Column(
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