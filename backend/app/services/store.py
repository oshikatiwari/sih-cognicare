"""
store.py
--------
Single shared in-memory store so both analysis.py (the API) and
seed_demo_data.py read/write the same data.

Includes helper accessors `get_patient_history` and `save_patient_session`.
"""

from typing import Dict, List, Any
import datetime

# patient_id -> list of session dictionaries
FAKE_DB: Dict[str, List[Dict[str, Any]]] = {
    "demo-patient-01": [
        {"cps": 82.0, "game_type": "memory_match", "difficulty": "Medium", "accuracy": 85.0, "response_time": 2.5, "completion_rate": 100.0, "display_label": "Steady Practice", "timestamp": "2026-09-01T10:00:00"},
        {"cps": 85.0, "game_type": "number_sequence", "difficulty": "Medium", "accuracy": 88.0, "response_time": 2.2, "completion_rate": 100.0, "display_label": "Steady Practice", "timestamp": "2026-09-02T10:00:00"},
        {"cps": 88.0, "game_type": "word_recall", "difficulty": "Hard", "accuracy": 90.0, "response_time": 2.0, "completion_rate": 100.0, "display_label": "Gentle Challenge", "timestamp": "2026-09-03T10:00:00"},
    ],
    "demo-patient-12": [
        {"cps": 88.0, "game_type": "memory_match", "difficulty": "Medium", "accuracy": 90.0, "response_time": 2.0, "completion_rate": 100.0, "display_label": "Gentle Challenge", "timestamp": "2026-09-01T10:00:00"},
        {"cps": 86.0, "game_type": "number_sequence", "difficulty": "Medium", "accuracy": 88.0, "response_time": 2.2, "completion_rate": 100.0, "display_label": "Steady Practice", "timestamp": "2026-09-02T10:00:00"},
        {"cps": 62.0, "game_type": "number_sequence", "difficulty": "Medium", "accuracy": 60.0, "response_time": 5.5, "completion_rate": 80.0, "display_label": "Comfortable Pace", "timestamp": "2026-09-03T10:00:00"},
    ]
}


def get_patient_history(patient_id: str) -> List[Dict[str, Any]]:
    """Returns session history list for a patient ID."""
    return FAKE_DB.get(patient_id, [])


def save_patient_session(patient_id: str, session: Dict[str, Any]) -> None:
    """Appends a new game session record to patient's history."""
    if patient_id not in FAKE_DB:
        FAKE_DB[patient_id] = []
    if "timestamp" not in session:
        session["timestamp"] = datetime.datetime.now().isoformat()
    FAKE_DB[patient_id].append(session)
