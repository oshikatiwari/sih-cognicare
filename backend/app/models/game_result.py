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


class GameResult(Base):
    __tablename__ = "game_results"

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

    completed = Column(
        Boolean,
        default=True,
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
