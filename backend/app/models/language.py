import uuid

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from backend.app.db.base import Base


class Language(Base):
    __tablename__ = "languages"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    name = Column(
        String,
        nullable=False,
        unique=True,
    )

    code = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )