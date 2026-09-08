import uuid

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from backend.app.db.base import Base


class Caregiver(Base):
    __tablename__ = "caregivers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    full_name = Column(String, nullable=False)

    phone = Column(String, nullable=True)

    email = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )