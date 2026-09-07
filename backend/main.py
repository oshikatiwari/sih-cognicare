"""
main.py
-------
Standalone runnable entrypoint for the AI Analysis Module.
Auto-seeds demo data on startup so /analysis/trend/{patient_id}
returns real data immediately.

Exposes:
  - GET /analysis/trend/{patient_id}
  - POST /analysis/cps
  - POST /analysis/voice-intent (and /voice/intent alias for Mrunaala's Flutter app)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.routers.analysis import router
from backend.app.services.seed_demo_data import seed
from backend.app.services.voice_assistant import process_voice_query

app = FastAPI(title="Cognitive Care - AI Analysis Module")

# Enable CORS for Caregiver Dashboard & Mobile App clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


class VoiceQueryRequest(BaseModel):
    patient_id: str = Field("demo-patient-01", description="Patient profile ID")
    spoken_phrase: str = Field("How am I doing today?", description="Spoken text query in English or Hindi")


@app.post("/voice/intent", tags=["voice"])
def voice_intent_alias(payload: VoiceQueryRequest):
    """
    Direct alias endpoint matching the roadmap spec for Mrunaala's Flutter Voice Module
    (lib/voice/stt_service.dart -> POST /voice/intent -> backend AI intent parser).
    """
    return process_voice_query(payload.patient_id, payload.spoken_phrase)


@app.on_event("startup")
def startup_seed():
    seed(num_patients=12, sessions_per_patient=10)
    print("Demo data seeded: demo-patient-01 through demo-patient-12")
    print("demo-patient-12 is rigged with a sharp late drop to demo the anomaly alert.")


@app.get("/")
def root():
    return {
        "status": "ok",
        "try": [
            "GET /analysis/trend/demo-patient-01",
            "GET /analysis/trend/demo-patient-12  (shows the anomaly alert)",
            "POST /analysis/cps  (see /docs for body schema)",
            "POST /voice/intent  (Mrunaala's Flutter voice pipeline endpoint)",
        ],
    }
