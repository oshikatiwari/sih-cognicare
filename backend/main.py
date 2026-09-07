"""
main.py
-------
Standalone runnable entrypoint for the AI Analysis Module.
Auto-seeds demo data on startup so /analysis/trend/{patient_id}
returns real data immediately.

IMPORTANT: run this from the REPO ROOT (the sih-cognicare folder),
not from inside backend/ -- the imports are structured as a package
(backend.app.services.*, backend.app.routers.*) so Python needs to
see the repo root to resolve them.

Run (from repo root):
    pip install fastapi uvicorn --break-system-packages
    uvicorn backend.main:app --reload

Then open http://localhost:8000/docs, or try:
    curl http://localhost:8000/analysis/trend/demo-patient-01
    curl http://localhost:8000/analysis/trend/demo-patient-12   # rigged to show an alert
"""

from fastapi import FastAPI
from backend.app.routers.analysis import router
from backend.app.services.seed_demo_data import seed

app = FastAPI(title="Cognitive Care - AI Analysis Module")
app.include_router(router)


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
        ],
    }
