import uuid

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func

from backend.app.db.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    full_name = Column(
        String,
        nullable=False,
    )

    age = Column(
        String,
        nullable=True,
    )

    preferred_language = Column(
        String,
        nullable=True,
        default="English",
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