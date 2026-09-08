from sqlalchemy.orm import Session

from backend.app.models.patient import Patient
from backend.app.models.game_session import GameSession
from backend.app.models.game_result import GameResult
from backend.app.models.cognitive_score import CognitiveScore
from backend.app.models.voice_interaction import VoiceInteraction
from backend.app.models.reminder import Reminder


SYNCABLE_MODELS = {
    "patients": Patient,
    "game_sessions": GameSession,
    "game_results": GameResult,
    "cognitive_scores": CognitiveScore,
    "voice_interactions": VoiceInteraction,
    "reminders": Reminder,
}


def get_unsynced_records(db: Session):
    """
    Collect all records that have not yet been synced.
    """

    records = {}

    for name, model in SYNCABLE_MODELS.items():
        unsynced = (
            db.query(model)
            .filter(model.synced == False)
            .all()
        )

        records[name] = unsynced

    return records


def mark_records_synced(records, db: Session):
    """
    Mark successfully processed records as synced.
    """

    for record_list in records.values():
        for record in record_list:
            record.synced = True

    db.commit()


def sync_local_records(db: Session):
    """
    Simplified offline sync process.

    For the demo:
    1. Find all locally stored unsynced records.
    2. Treat them as successfully uploaded.
    3. Mark them as synced.

    This represents:
        SQLite Local Database -> Cloud Sync
    """

    records = get_unsynced_records(db)

    summary = {
        "patients": len(records["patients"]),
        "game_sessions": len(records["game_sessions"]),
        "game_results": len(records["game_results"]),
        "cognitive_scores": len(records["cognitive_scores"]),
        "voice_interactions": len(records["voice_interactions"]),
        "reminders": len(records["reminders"]),
    }

    mark_records_synced(records, db)

    return summary