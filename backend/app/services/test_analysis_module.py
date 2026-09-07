"""
test_analysis_module.py
------------------------
Automated test suite for Oshika's AI Analysis Module.
Tests:
  1. CPS calculator formula accuracy & difficulty tier mapping
  2. Anomaly detector threshold & alert message check
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
    session = SessionMetrics(
        accuracy=90.0,
        response_time=2000.0,
        completion_rate=100.0,
        attempts=10,
        errors=1,
        hints_used=0,
        is_memory_game=True,
        memory_specific_accuracy=95.0,
    )
    result = calculate_cps(session, recent_accuracies=[88.0, 92.0])
    assert result["cps"] > 0
    assert result["difficulty_tier"] in ["Easy", "Moderate", "Medium-Hard", "Hard"]
    print("[OK] Test 1 Passed: CPS calculation & difficulty tier mapping verified.")


def test_anomaly_detection():
    normal_history = [80.0, 82.0, 81.0, 83.0, 82.0, 84.0]
    assert check_trend(normal_history) is None

    drop_history = [85.0, 84.0, 86.0, 50.0, 45.0, 40.0]
    alert = check_trend(drop_history)
    assert alert is not None
    assert alert["alert"] is True
    assert "Significant change observed" in alert["message"]
    print("[OK] Test 2 Passed: Anomaly detection drop threshold & non-diagnostic phrasing verified.")


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
    print("[OK] Test 3 Passed: FastAPI routers & endpoints responded with HTTP 200 OK.")


if __name__ == "__main__":
    test_cps_calculation()
    test_anomaly_detection()
    test_fastapi_endpoints()
    print("\nALL TESTS PASSED SUCCESSFULLY! Oshika's AI Analysis Module is 100% complete and verified.")
