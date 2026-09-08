import uuid

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from backend.app.db.base import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    name = Column(
        String,
        nullable=False,
    )

    category = Column(
        String,
        nullable=True,
    )

    description = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )