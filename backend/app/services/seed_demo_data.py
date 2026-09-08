import random
from datetime import datetime, timedelta

from backend.app.db.session import SessionLocal
from backend.app.models.patient import Patient
from backend.app.models.game_session import GameSession
from backend.app.models.cognitive_score import CognitiveScore

from backend.app.services.cps_calculator import (
    SessionMetrics,
    calculate_cps,
)

random.seed(42)


def _make_session(
    accuracy: float,
    is_memory_game: bool = False,
):
    return SessionMetrics(
        accuracy=accuracy,
        response_time=random.uniform(1800, 4500),
        completion_rate=random.uniform(85, 100),
        attempts=random.randint(8, 15),
        errors=random.randint(0, 4),
        hints_used=random.randint(0, 2),
        is_memory_game=is_memory_game,
        memory_specific_accuracy=(
            accuracy + random.uniform(-5, 5)
            if is_memory_game
            else None
        ),
    )


def seed(
    num_patients: int = 12,
    sessions_per_patient: int = 10,
):

    db = SessionLocal()

    try:

        # Remove old demo data first
        demo_patients = (
            db.query(Patient)
            .filter(Patient.id.like("demo-patient-%"))
            .all()
        )

        for patient in demo_patients:

            sessions = (
                db.query(GameSession)
                .filter(GameSession.patient_id == patient.id)
                .all()
            )

            for session in sessions:
                (
                    db.query(CognitiveScore)
                    .filter(
                        CognitiveScore.session_id == session.id
                    )
                    .delete()
                )

            (
                db.query(GameSession)
                .filter(
                    GameSession.patient_id == patient.id
                )
                .delete()
            )

            db.delete(patient)

        db.commit()

        base_time = (
            datetime.now()
            - timedelta(days=sessions_per_patient * 2)
        )

        for p in range(1, num_patients + 1):

            patient_id = f"demo-patient-{p:02d}"

            patient = Patient(
                id=patient_id,
                full_name=f"Demo Patient {p:02d}",
                age=str(random.randint(60, 85)),
                preferred_language="English",
            )

            db.add(patient)
            db.commit()

            recent_accuracies = []

            start_acc = random.uniform(60, 75)
            end_acc = random.uniform(80, 95)

            for s in range(sessions_per_patient):

                progress = (
                    s
                    / max(
                        1,
                        sessions_per_patient - 1,
                    )
                )

                target_acc = (
                    start_acc
                    + (end_acc - start_acc)
                    * progress
                )

                # Force a sharp decline
                # for demo-patient-12
                if (
                    p == num_patients
                    and s >= sessions_per_patient - 3
                ):
                    target_acc *= 0.55

                target_acc = max(
                    0,
                    min(
                        100,
                        target_acc
                        + random.uniform(-4, 4),
                    ),
                )

                is_memory = (s % 2 == 0)

                metrics = _make_session(
                    target_acc,
                    is_memory_game=is_memory,
                )

                result = calculate_cps(
                    metrics,
                    recent_accuracies=recent_accuracies[-5:],
                )

                # Create game session
                game_session = GameSession(
                    patient_id=patient_id,
                    game_type=(
                        "Memory Match"
                        if is_memory
                        else "Cognitive Puzzle"
                    ),
                    difficulty_level=result[
                        "difficulty_tier"
                    ],
                    score=result["cps"],
                    accuracy=metrics.accuracy,
                    response_time=metrics.response_time,
                    completion_rate=metrics.completion_rate,
                    attempts=metrics.attempts,
                    errors=metrics.errors,
                    hints_used=metrics.hints_used,
                    is_memory_game=is_memory,
                    memory_specific_accuracy=(
                        metrics.memory_specific_accuracy
                    ),
                    status="completed",
                    started_at=(
                        base_time
                        + timedelta(days=s * 2)
                    ),
                )

                db.add(game_session)
                db.commit()
                db.refresh(game_session)

                # Create cognitive score
                cognitive_score = CognitiveScore(
                    session_id=game_session.id,
                    patient_id=patient_id,
                    cps=result["cps"],
                    accuracy=metrics.accuracy,
                    difficulty_tier=result[
                        "difficulty_tier"
                    ],
                    created_at=(
                        base_time
                        + timedelta(days=s * 2)
                    ),
                )

                db.add(cognitive_score)
                db.commit()

                recent_accuracies.append(
                    metrics.accuracy
                )

        print(
            f"Seeded {num_patients} demo patients "
            "into the database."
        )

    finally:
        db.close()


if __name__ == "__main__":
    seed()