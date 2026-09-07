# Oshika — AI Analysis Module (CPS + Anomaly Detection)

## What this is
The "AI" for the 4-day MVP is a **rule-based, explainable scoring engine** —
not a trained model. This matches the report's own Phase 1 recommendation
(ML/Random Forest is explicitly Phase 2, out of scope for the hackathon).

## Files
- `cps_calculator.py` — the weighted CPS formula (Accuracy 30%, Response
  Speed 20%, Completion Rate 20%, Consistency 15%, Memory Performance 15%)
  and the CPS → difficulty tier mapping. Field names match the roadmap's
  own Section 8 API spec (`response_time`, assumed milliseconds — confirm
  with Praveen).
- `anomaly_detector.py` — compares recent vs. prior average CPS; flags a
  caregiver alert on a significant drop, using the report's exact
  non-diagnostic wording.
- `store.py` — single shared in-memory data store. Swap this file's
  contents for real DB queries once Meghna's `CognitiveScores` table is
  ready; nothing else needs to change.
- `seed_demo_data.py` — generates 12 synthetic patients with realistic
  session history, run through the *real* CPS formula. One patient is
  rigged with a sharp late drop so the anomaly alert has something to
  fire on during the demo.
- `analysis.py` — FastAPI router exposing `POST /analysis/cps` and
  `GET /analysis/trend/{patient_id}`.
- `main.py` — runnable entrypoint. Auto-seeds demo data on startup, so
  the whole module works standalone with zero dependency on Praveen's
  game or Meghna's real database.

## Run it right now (tested, works end-to-end)
```bash
pip install fastapi uvicorn --break-system-packages
uvicorn main:app --reload
```
Then try:
```bash
curl http://localhost:8000/analysis/trend/demo-patient-01
curl http://localhost:8000/analysis/trend/demo-patient-12   # shows the anomaly alert
```
Or open `http://localhost:8000/docs` for interactive Swagger UI —
useful for demoing to teammates before Meghna's full backend is wired up.

Just testing the formula logic directly, no server:
```bash
python cps_calculator.py
python anomaly_detector.py
python seed_demo_data.py   # prints all 12 patients' score histories
```

## Integration checklist (Day 1–2)
1. **Praveen** — his `POST /game-sessions` result payload must match the
   `CPSRequest` fields in `analysis.py` (accuracy, response_time_ms,
   completion_rate, attempts, errors, hints_used). Confirm field names
   with him before he finishes his result-submission code.
2. **Meghna** — replace `FAKE_DB` (in-memory dict) with real writes/reads
   to her `CognitiveScores` table. The function signatures won't need to
   change — only the storage lines inside `calculate_and_store_cps` and
   `get_trend`.
3. **Dashboard (React)** — consumes `GET /analysis/trend/{patient_id}`
   directly for the trend chart + alert banner.

## Tuning notes
- `_normalize_response_speed()` in `cps_calculator.py` has `best_ms=1500`
  and `worst_ms=8000` as reference points — adjust these after a couple
  of real playtests of Praveen's games so "fast" and "slow" feel right
  for your actual game timings.
- `DROP_THRESHOLD_PCT = 15.0` in `anomaly_detector.py` controls how
  sensitive the caregiver alert is — 15% is a reasonable demo default,
  tune if it fires too often/rarely on your seeded demo data.

## If a judge asks "where's the AI?"
Say this, verbatim if useful:
> "This stage uses a rule-based, explainable scoring pipeline — weighted
> feature combination and threshold-based difficulty mapping — exactly
> as our project report specifies for Phase 1. The architecture is
> designed so the same input pipeline feeds a trained Random Forest/
> XGBoost model in Phase 2 without changing the API contract."

This is a *strength* to lead with, not something to hide: it's honest,
matches your own report, and shows you understand the responsible way
to introduce ML into a care product (rule-based baseline before opaque
models, especially for something touching dementia care).

## What NOT to build in 4 days
- No model training (Random Forest/XGBoost) — Phase 2, documented only.
- No passive-sensing features feeding into CPS.
- No elaborate validation frameworks — FastAPI/Pydantic range checks
  (already in `analysis.py`) are sufficient.
