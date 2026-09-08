from backend.app.db.session import SessionLocal
from backend.app.models.patient import Patient
from backend.app.models.game_session import GameSession
from backend.app.models.cognitive_score import CognitiveScore


db = SessionLocal()

try:
    # Create a test patient
    patient = Patient(
        full_name="Test Patient",
        age="70",
        preferred_language="English",
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    print("Patient created:", patient.id)

    # Create a test game session
    game_session = GameSession(
        patient_id=patient.id,
        game_type="Memory Match",
        difficulty_level="Easy",
        score=85.0,
        accuracy=90.0,
        response_time=2500.0,
        completion_rate=100.0,
        attempts=10,
        errors=1,
        hints_used=0,
        is_memory_game=True,
        memory_specific_accuracy=90.0,
    )

    db.add(game_session)
    db.commit()
    db.refresh(game_session)

    print("Game session created:", game_session.id)

    # Create a cognitive score
    cognitive_score = CognitiveScore(
        session_id=game_session.id,
        patient_id=patient.id,
        cps=87.5,
        accuracy=90.0,
        difficulty_tier="Easy",
    )

    db.add(cognitive_score)
    db.commit()
    db.refresh(cognitive_score)

    print("Cognitive score created:", cognitive_score.id)

    print("\nSUCCESS! Database relationships are working correctly.")

finally:
    db.close()