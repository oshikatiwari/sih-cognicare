from backend.app.db.base import Base
from backend.app.db.session import engine

# Import all models so SQLAlchemy registers them with Base
from backend.app.models.user import User
from backend.app.models.patient import Patient
from backend.app.models.caregiver import Caregiver
from backend.app.models.game import Game
from backend.app.models.game_session import GameSession
from backend.app.models.game_result import GameResult
from backend.app.models.cognitive_score import CognitiveScore
from backend.app.models.reminder import Reminder
from backend.app.models.medication import Medication
from backend.app.models.alert import Alert
from backend.app.models.language import Language
from backend.app.models.voice_interaction import VoiceInteraction


def init_db():
    Base.metadata.create_all(bind=engine)

    print("Database created successfully!")
    print("Tables created:")

    for table_name in Base.metadata.tables.keys():
        print(f"- {table_name}")


if __name__ == "__main__":
    init_db()