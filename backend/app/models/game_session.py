import uuid

from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func

from backend.app.db.base import Base


class GameSession(Base):
    __tablename__ = "game_sessions"

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

    game_type = Column(
        String,
        nullable=False,
    )

    difficulty_level = Column(
        String,
        nullable=True,
    )

    score = Column(
        Float,
        nullable=True,
    )

    accuracy = Column(
        Float,
        nullable=True,
    )

    response_time = Column(
        Float,
        nullable=True,
    )

    completion_rate = Column(
        Float,
        nullable=True,
    )

    attempts = Column(
        Integer,
        default=0,
    )

    errors = Column(
        Integer,
        default=0,
    )

    hints_used = Column(
        Integer,
        default=0,
    )

    is_memory_game = Column(
        Boolean,
        default=False,
    )

    memory_specific_accuracy = Column(
        Float,
        nullable=True,
    )

    status = Column(
        String,
        default="completed",
    )

    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
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