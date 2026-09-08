"""
test_analysis_module.py
------------------------
Automated test suite verifying:
  1. Multi-game Cognitive Performance Score (CPS) calculation & difficulty scaling.
  2. Non-diagnostic caregiver anomaly detection & domain monitoring breakdown.
  3. Multilingual voice guidance & step-by-step instructions in 5 languages (en, hi, as, mzo, kha).
  4. Intent parser & Bluetooth audio pairing notifications.
"""

import sys
import os

# Ensure UTF-8 output encoding for Windows terminal compatibility
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add root directory to python path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.services.cps_calculator import calculate_cps, SessionMetrics
from backend.app.services.anomaly_detector import detect_cps_anomalies, get_game_monitoring_breakdown
from backend.app.services.voice_assistant import (
    get_screen_voice_guidance,
    process_voice_query,
    detect_language_and_intent,
    get_supported_languages,
    get_bluetooth_audio_guidance,
)


def test_multi_game_cps_calculator():
    print("Testing Multi-Game CPS Calculation & Difficulty Multipliers...")
    
    # Test Memory Match Game (Medium)
    session_mm = SessionMetrics(
        game_type="memory_match",
        difficulty="medium",
        accuracy=90.0,
        response_time=2.5,
        completion_rate=100.0,
    )
    result_mm = calculate_cps(session_mm, recent_accuracies=[85.0, 88.0])
    assert 0 <= result_mm["cps"] <= 100.0
    assert result_mm["game_type"] == "memory_match"
    assert result_mm["difficulty"] == "Medium"
    assert "Visual Paired Memory" in result_mm["cognitive_domain"]

    # Test Number Sequence Game (Hard)
    session_ns = SessionMetrics(
        game_type="number_sequence",
        difficulty="hard",
        accuracy=95.0,
        response_time=1.8,
        completion_rate=100.0,
    )
    result_ns = calculate_cps(session_ns, recent_accuracies=[90.0, 92.0])
    assert result_ns["cps"] >= result_mm["cps"]
    assert "Working Auditory Memory" in result_ns["cognitive_domain"]

    print("[PASS] Multi-Game CPS Calculation Test Passed!")


def test_domain_anomaly_detector():
    print("Testing Domain Anomaly Detector & Caregiver Monitoring...")
    
    history_normal = [
        {"cps": 85.0, "game_type": "memory_match"},
        {"cps": 84.0, "game_type": "number_sequence"},
        {"cps": 86.0, "game_type": "word_recall"},
    ]
    eval_normal = detect_cps_anomalies(history_normal)
    assert not eval_normal["anomaly_detected"]

    # Test domain drop detection
    history_drop = [
        {"cps": 88.0, "game_type": "number_sequence"},
        {"cps": 87.0, "game_type": "number_sequence"},
        {"cps": 60.0, "game_type": "number_sequence"},  # >15% drop
    ]
    eval_drop = detect_cps_anomalies(history_drop)
    assert eval_drop["anomaly_detected"]
    assert "Working Auditory Memory" in eval_drop["alert_message"]

    # Test monitoring breakdown
    breakdown = get_game_monitoring_breakdown(history_normal)
    assert "game_breakdown" in breakdown
    assert "memory_match" in breakdown["game_breakdown"]

    print("[PASS] Domain Anomaly Detector Test Passed!")


def test_multilingual_voice_guidance():
    print("Testing 5-Language Step-by-Step Voice Guidance...")
    
    languages = ["en", "hi", "as", "mzo", "kha"]
    game_screens = ["home", "language_selection", "memory_match", "number_sequence", "word_recall", "picture_association"]

    for lang in languages:
        for screen in game_screens:
            guidance = get_screen_voice_guidance(screen_id=screen, lang=lang)
            assert guidance["language"] == lang
            assert len(guidance["spoken_guidance"]) > 5

    # Test Bluetooth audio notice
    bt_notice = get_bluetooth_audio_guidance(lang="as")
    assert "অডিঅ'" in bt_notice["spoken_bluetooth_notice"] or "সংসংযুক্ত" in bt_notice["spoken_bluetooth_notice"] or len(bt_notice["spoken_bluetooth_notice"]) > 0

    print("[PASS] 5-Language Voice Guidance Test Passed!")


def test_voice_intent_parser():
    print("Testing Voice Intent Parsing Across Languages...")
    
    intent_hi = detect_language_and_intent("नमस्ते मुझे खेल खेलना है")
    assert intent_hi["language"] == "hi"

    intent_as = detect_language_and_intent("নমস্কাৰ মোৰ স্ক'ৰ কিমান")
    assert intent_as["language"] == "as"

    print("[PASS] Voice Intent Parser Test Passed!")


if __name__ == "__main__":
    print("\n================ RUNNING AI ANALYSIS MODULE TESTS ================")
    test_multi_game_cps_calculator()
    test_domain_anomaly_detector()
    test_multilingual_voice_guidance()
    test_voice_intent_parser()
    print("================ 100% ALL TESTS PASSED SUCCESSFULLY! ================\n")
