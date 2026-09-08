from fastapi import FastAPI

from backend.app.routers.analysis import router as analysis_router
from backend.app.routers.patients import router as patients_router
from backend.app.routers.game_sessions import router as game_sessions_router
from backend.app.routers.game_results import router as game_results_router
from backend.app.routers.voice_interactions import router as voice_interactions_router
from backend.app.routers.reminders import router as reminders_router
from backend.app.routers.sync import router as sync_router

from backend.app.services.seed_demo_data import seed


app = FastAPI(
    title="Cognitive Care Backend",
)


# Routers
app.include_router(analysis_router)
app.include_router(patients_router)
app.include_router(game_sessions_router)
app.include_router(game_results_router)
app.include_router(voice_interactions_router)
app.include_router(reminders_router)
app.include_router(sync_router)


@app.on_event("startup")
def startup_seed():
    seed(num_patients=12, sessions_per_patient=10)

    print("Demo data seeded: demo-patient-01 through demo-patient-12")


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Cognitive Care Backend is running.",
        "available_endpoints": [
            "POST /patients/",
            "GET /patients/{patient_id}",
            "POST /game-sessions/",
            "GET /game-sessions/{session_id}",
            "POST /game-results/",
            "POST /voice-interactions/",
            "POST /reminders/",
            "PUT /reminders/{reminder_id}/complete",
            "POST /sync/",
            "POST /analysis/cps",
            "GET /analysis/trend/{patient_id}",
        ],
    }