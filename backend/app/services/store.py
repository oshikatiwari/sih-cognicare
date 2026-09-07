"""
store.py
--------
Single shared in-memory store so both analysis.py (the API) and
seed_demo_data.py (fake data generator) read/write the same data.

REPLACE THIS FILE'S CONTENTS with real SQLAlchemy queries once
Meghna's `CognitiveScores` table + DB session are ready. Every other
file imports `FAKE_DB` from here, so that's the only place you'll
need to change the storage mechanism later.
"""

from typing import Dict, List

# patient_id -> list of {session_id, cps, accuracy, timestamp}
FAKE_DB: Dict[str, List[dict]] = {}
