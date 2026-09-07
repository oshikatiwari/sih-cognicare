"""
seed_demo_data.py
------------------
Generates synthetic patients with realistic session history, run
through the REAL cps_calculator (not fake numbers) so your trend
chart and anomaly alert have something to show from Day 1 -- with
zero dependency on Praveen's game or Meghna's real database.

Matches the report's own demo-dataset recommendation: 10-20 seeded
patients, one of which shows the Day1/7/14/21-style progression, and
at least one whose scores dip sharply so the anomaly alert has
something to actually trigger on during the demo.

Usage:
    python seed_demo_data.py        # populates store.FAKE_DB, prints summary
"""

import random
import uuid
from datetime import datetime, timedelta

from backend.app.services.cps_calculator import SessionMetrics, calculate_cps
from backend.app.services.store import FAKE_DB

random.seed(42)  # reproducible demo data -- don't change unless you want fresh numbers


def _make_session(accuracy: float, is_memory_game: bool = False) -> SessionMetrics:
    """Builds one plausible session around a target accuracy level."""
    return SessionMetrics(
        accuracy=accuracy,
        response_time=random.uniform(1800, 4500),
        completion_rate=random.uniform(85, 100),
        attempts=random.randint(8, 15),
        errors=random.randint(0, 4),
        hints_used=random.randint(0, 2),
        is_memory_game=is_memory_game,
        memory_specific_accuracy=accuracy + random.uniform(-5, 5) if is_memory_game else None,
    )


def seed(num_patients: int = 12, sessions_per_patient: int = 10) -> None:
    """
    Populates store.FAKE_DB with synthetic patients.

    - Most patients get a gentle upward trend (improving over time) --
      matches the report's own Day1/7/14/21 example table concept.
    - One patient (the last one) gets a sharp late drop, specifically
      so the anomaly alert has something real to fire on during the demo.
    """
    FAKE_DB.clear()
    base_time = datetime.now() - timedelta(days=sessions_per_patient * 2)

    for p in range(1, num_patients + 1):
        patient_id = f"demo-patient-{p:02d}"
        FAKE_DB[patient_id] = []

        # baseline accuracy trend: starts around 60-75, improves toward 80-95
        start_acc = random.uniform(60, 75)
        end_acc = random.uniform(80, 95)

        for s in range(sessions_per_patient):
            progress = s / max(1, sessions_per_patient - 1)
            target_acc = start_acc + (end_acc - start_acc) * progress

            # last patient: force a sharp drop in the final 3 sessions
            # so the anomaly alert has a real trigger to demo
            if p == num_patients and s >= sessions_per_patient - 3:
                target_acc = target_acc * 0.55

            target_acc = max(0, min(100, target_acc + random.uniform(-4, 4)))
            is_memory = (s % 2 == 0)  # alternate games for variety

            session = _make_session(target_acc, is_memory_game=is_memory)
            recent_accuracies = [h["accuracy"] for h in FAKE_DB[patient_id][-5:]]
            result = calculate_cps(session, recent_accuracies=recent_accuracies)

            FAKE_DB[patient_id].append({
                "session_id": str(uuid.uuid4()),
                "cps": result["cps"],
                "accuracy": session.accuracy,
                "timestamp": (base_time + timedelta(days=s * 2)).isoformat(),
            })


if __name__ == "__main__":
    seed()
    print(f"Seeded {len(FAKE_DB)} demo patients.\n")
    for patient_id, history in FAKE_DB.items():
        scores = [round(h["cps"], 1) for h in history]
        print(f"{patient_id}: {scores}")

    # quick sanity check: confirm the anomaly detector actually fires
    # on the patient we rigged to drop
    from backend.app.services.anomaly_detector import check_trend
    last_patient = list(FAKE_DB.keys())[-1]
    cps_values = [h["cps"] for h in FAKE_DB[last_patient]]
    print(f"\nAnomaly check for {last_patient}: {check_trend(cps_values)}")
