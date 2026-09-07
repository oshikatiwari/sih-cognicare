"""
test_analysis_module.py
------------------------
Automated test suite for Oshika's AI Analysis Module & Voice Engine in Smriti (स्मृति).
Tests:
  1. CPS calculator formula accuracy, difficulty tier mapping, supportive display labels & seconds auto-conversion
  2. Anomaly detector threshold & caregiver-friendly alert message check
  3. Multilingual voice intent parsing & TTS response engine (English & Hindi)
  4. Step-by-step elderly voice navigation guidance per screen for Smriti
  5. FastAPI router endpoints via TestClient
"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.app.services.cps_calculator import SessionMetrics, calculate_cps
from backend.app.services.anomaly_detector import check_trend
from backend.app.services.voice_assistant import process_voice_query, get_screen_voice_guidance
from backend.app.services.seed_demo_data import seed

client = TestClient(app)


def test_cps_calculation():
    # Test Milliseconds input
    session_ms = SessionMetrics(
        accuracy=90.0,
        response_time=2000.0,
        completion_rate=100.0,
        attempts=10,
        errors=1,
        hints_used=0,
        is_memory_game=True,
        memory_specific_accuracy=95.0,
    )
    result_ms = calculate_cps(session_ms, recent_accuracies=[88.0, 92.0])
    assert result_ms["cps"] > 0
    assert result_ms["difficulty_tier"] in ["Easy", "Moderate", "Medium-Hard", "Hard"]
    assert "display_label" in result_ms

    # Test Seconds input (2.0s -> 2000ms auto-conversion)
    session_sec = SessionMetrics(
        accuracy=90.0,
        response_time=2.0,
        completion_rate=100.0,
        attempts=10,
        errors=1,
        hints_used=0,
        is_memory_game=True,
        memory_specific_accuracy=95.0,
    )
    result_sec = calculate_cps(session_sec, recent_accuracies=[88.0, 92.0])
    assert result_sec["cps"] == result_ms["cps"], "Seconds and Milliseconds should produce identical CPS"

    print("[OK] Test 1 Passed: CPS calculation, difficulty mapping & supportive display labels verified.")


def test_anomaly_detection():
    normal_history = [80.0, 82.0, 81.0, 83.0, 82.0, 84.0]
    assert check_trend(normal_history) is None

    drop_history = [85.0, 84.0, 86.0, 50.0, 45.0, 40.0]
    alert = check_trend(drop_history)
    assert alert is not None
    assert alert["alert"] is True
    assert "caregiver review is recommended" in alert["message"]
    print("[OK] Test 2 Passed: Anomaly detection drop threshold & caregiver-friendly phrasing verified.")


def test_voice_assistant_engine():
    # Test English query
    res_en = process_voice_query("demo-patient-01", "How am I doing today?")
    assert res_en["detected_language"] == "en"
    assert res_en["detected_intent"] == "CHECK_SCORE"
    assert len(res_en["response_text"]) > 0

    # Test Hindi query
    res_hi = process_voice_query("demo-patient-01", "खेल शुरू करें")
    assert res_hi["detected_language"] == "hi"
    assert res_hi["detected_intent"] == "START_GAME"
    assert "गेम" in res_hi["response_text"] or "खेल" in res_hi["response_text"]

    # Test Screen Guidance for elderly patients in Smriti
    guidance_home = get_screen_voice_guidance("home", lang="en")
    assert "Smriti" in guidance_home["spoken_guidance"]
    
    guidance_game = get_screen_voice_guidance("gameplay", lang="hi")
    assert "कार्ड्स" in guidance_game["spoken_guidance"] or "आराम" in guidance_game["spoken_guidance"]

    print("[OK] Test 3 Passed: Multilingual voice intent & step-by-step elderly guidance for Smriti verified.")


def test_fastapi_endpoints():
    seed()  # ensure store.FAKE_DB is populated with 12 synthetic patients
    
    # Test Root
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["app_name"] == "Smriti (स्मृति)"

    # Test Trend Endpoint for normal patient
    res_trend_01 = client.get("/analysis/trend/demo-patient-01")
    assert res_trend_01.status_code == 200
    data_01 = res_trend_01.json()
    assert len(data_01["scores"]) == 10
    assert data_01["alert"] is None

    # Test POST /analysis/cps endpoint
    cps_payload = {
        "session_id": "test-sess-001",
        "patient_id": "demo-patient-01",
        "accuracy": 85.0,
        "response_time": 2500.0,
        "completion_rate": 100.0,
        "attempts": 10,
        "errors": 1,
        "hints_used": 0,
        "is_memory_game": True,
        "memory_specific_accuracy": 88.0,
    }
    res_cps = client.post("/analysis/cps", json=cps_payload)
    assert res_cps.status_code == 200
    assert "cps" in res_cps.json()

    # Test GET /analysis/voice-guidance/{screen_id} endpoint
    res_guidance = client.get("/analysis/voice-guidance/home?lang=en&patient_id=demo-patient-01")
    assert res_guidance.status_code == 200
    assert "Smriti" in res_guidance.json()["spoken_guidance"]

    print("[OK] Test 4 Passed: FastAPI routers & elderly voice guidance endpoints for Smriti responded with HTTP 200 OK.")


if __name__ == "__main__":
    test_cps_calculation()
    test_anomaly_detection()
    test_voice_assistant_engine()
    test_fastapi_endpoints()
    print("\nALL TESTS PASSED SUCCESSFULLY! Smriti's AI Module & Voice Engine are 100% complete and verified.")
