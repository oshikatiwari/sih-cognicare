"""
models_cognitive_scores.py
----------------------------
SQLAlchemy model for the CognitiveScores table, matching exactly what
store.py currently produces. Hand this to Meghna to add to her schema
file (app/models/) -- when her DB session is ready, swapping store.py's
FAKE_DB for real queries against this table is a small, mechanical change.

Assumes she's using SQLAlchemy's declarative Base + Postgres (per the
report's stack). Adjust the import path for `Base` to match wherever
she defines it (likely app/db/base.py or similar).
"""

import uuid
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

# from app.db.base import Base   # <-- uncomment and point at Meghna's actual Base
from sqlalchemy.orm import declarative_base
Base = declarative_base()  # <-- DELETE this line once wired to Meghna's real Base


class CognitiveScore(Base):
    __tablename__ = "cognitive_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)   # FK -> GameSessions.id
    patient_id = Column(UUID(as_uuid=True), nullable=False)   # FK -> Patients.id
    cps = Column(Float, nullable=False)                       # 0-100
    accuracy = Column(Float, nullable=False)                  # raw accuracy this session, kept for consistency calc
    difficulty_tier = Column(String, nullable=True)           # Easy / Moderate / Medium-Hard / Hard
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # NOTE for Meghna: add real ForeignKey() constraints once GameSessions
    # and Patients tables exist in the same Base metadata, e.g.:
    #   session_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id"))
    #   patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
