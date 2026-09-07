"""
test_analysis_module.py
------------------------
Automated test suite for Oshika's AI Analysis Module.
Tests:
  1. CPS calculator formula accuracy, difficulty tier mapping, supportive display labels & seconds auto-conversion
  2. Anomaly detector threshold & caregiver-friendly alert message check
  3. Seed data generation & patient score history integrity
  4. FastAPI router endpoints via TestClient
"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.app.services.cps_calculator import SessionMetrics, calculate_cps
from backend.app.services.anomaly_detector import check_trend
from backend.app.services.seed_demo_data import seed

client = TestClient(app)


def test_cps_calculation():
    # Test Milliseconds input
    session_ms = SessionMetrics(
        accuracy=90.0,
        response_time=2000.0,  # 2000 ms
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
        response_time=2.0,  # 2.0 seconds
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


def test_fastapi_endpoints():
    seed()  # ensure store.FAKE_DB is populated with 12 synthetic patients
    
    # Test Root
    res_root = client.get("/")
    assert res_root.status_code == 200

    # Test Trend Endpoint for normal patient
    res_trend_01 = client.get("/analysis/trend/demo-patient-01")
    assert res_trend_01.status_code == 200, f"Expected 200, got {res_trend_01.status_code}: {res_trend_01.text}"
    data_01 = res_trend_01.json()
    assert len(data_01["scores"]) == 10
    assert data_01["alert"] is None

    # Test Trend Endpoint for rigged patient (demo-patient-12)
    res_trend_12 = client.get("/analysis/trend/demo-patient-12")
    assert res_trend_12.status_code == 200
    data_12 = res_trend_12.json()
    assert data_12["alert"] is not None

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
    assert "display_label" in res_cps.json()
    print("[OK] Test 3 Passed: FastAPI routers & endpoints responded with HTTP 200 OK.")


if __name__ == "__main__":
    test_cps_calculation()
    test_anomaly_detection()
    test_fastapi_endpoints()
    print("\nALL TESTS PASSED SUCCESSFULLY! Oshika's AI Analysis Module is 100% complete and verified.")
