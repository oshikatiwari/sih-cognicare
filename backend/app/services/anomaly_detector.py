"""
anomaly_detector.py
-------------------
Caregiver Cognitive Monitoring & Anomaly Detection Engine for Smriti (স্মৃতি).

Monitors longitudinal CPS trends over recent gameplay sessions to identify noticeable
performance drops (>= 15% drop overall or domain-specific) across all 4 cognitive games:
  - Memory Match (Visual Paired Memory)
  - Number Sequence (Working Auditory Memory)
  - Word Recall (Semantic Traditional Memory)
  - Picture Association (Visual Semantic Association)

Strictly non-diagnostic: outputs compassionate, supportive caregiver notifications
focusing on gentle check-ins and comfortable practice pacing.
"""

from typing import List, Dict, Any, Optional
from statistics import mean


DROP_THRESHOLD_PERCENT = 15.0  # 15% shift triggers supportive caregiver review


GAME_DOMAIN_NAMES = {
    "memory_match": "Visual Paired Memory (Memory Match)",
    "number_sequence": "Working Auditory Memory (Number Sequence)",
    "word_recall": "Semantic Memory (Word Recall)",
    "picture_association": "Visual Semantic Association (Picture Association)",
    "pattern_game": "Spatial Reasoning (Pattern Game)",
    "object_id": "Object Recognition (Object Identification)",
}


def detect_cps_anomalies(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates patient's session history for overall and per-domain performance shifts.
    """
    if len(history) < 2:
        return {
            "anomaly_detected": False,
            "drop_percentage": 0.0,
            "domain_affected": None,
            "alert_message": "Sufficient baseline activity is being gathered for ongoing caregiver insights.",
            "caregiver_action_recommendation": "Encourage regular practice at a comfortable, relaxed pace.",
        }

    # Sort history chronologically if timestamp present
    sorted_history = sorted(history, key=lambda x: x.get("timestamp", ""))

    cps_scores = [float(s.get("cps", 80.0)) for s in sorted_history]
    latest_cps = cps_scores[-1]

    # Calculate baseline average from preceding sessions
    baseline_cps = mean(cps_scores[:-1])

    if baseline_cps <= 0:
        drop_percent = 0.0
    else:
        drop_percent = ((baseline_cps - latest_cps) / baseline_cps) * 100.0

    drop_percent = round(drop_percent, 2)

    # Check for game domain specific shifts
    latest_game = sorted_history[-1].get("game_type", "memory_match")
    domain_label = GAME_DOMAIN_NAMES.get(latest_game, "Cognitive Activity")

    # Evaluate domain specific history
    domain_sessions = [s for s in sorted_history if s.get("game_type") == latest_game]
    domain_drop = False
    if len(domain_sessions) >= 2:
        domain_baseline = mean([float(s.get("cps", 80.0)) for s in domain_sessions[:-1]])
        domain_latest = float(domain_sessions[-1].get("cps", 80.0))
        if domain_baseline > 0 and ((domain_baseline - domain_latest) / domain_baseline) * 100.0 >= DROP_THRESHOLD_PERCENT:
            domain_drop = True

    is_anomaly = (drop_percent >= DROP_THRESHOLD_PERCENT) or domain_drop

    if is_anomaly:
        alert_message = (
            f"Noticeable change in recent activity patterns in {domain_label} "
            f"({max(drop_percent, 15.0)}% drop) — a gentle check-in or caregiver review is recommended."
        )
        recommendation = (
            "Suggested Action: Initiate a warm check-in, review sleep and hydration, "
            "and offer a relaxed game session on Easy difficulty."
        )
    else:
        alert_message = f"Activity patterns remain steady and consistent across {domain_label}."
        recommendation = "Maintain regular daily practice and offer supportive encouragement."

    return {
        "anomaly_detected": is_anomaly,
        "drop_percentage": max(0.0, drop_percent),
        "latest_cps": round(latest_cps, 1),
        "baseline_cps": round(baseline_cps, 1),
        "domain_affected": domain_label if is_anomaly else None,
        "alert_message": alert_message,
        "caregiver_action_recommendation": recommendation,
    }


def get_game_monitoring_breakdown(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates per-game performance monitoring breakdown for caregiver dashboards.
    """
    game_breakdown = {}
    for game_key, domain_title in GAME_DOMAIN_NAMES.items():
        game_sessions = [s for s in history if s.get("game_type") == game_key]
        if game_sessions:
            avg_cps = mean([float(s.get("cps", 80.0)) for s in game_sessions])
            avg_accuracy = mean([float(s.get("accuracy", 80.0)) for s in game_sessions])
            latest_difficulty = game_sessions[-1].get("difficulty", "Medium")
            count = len(game_sessions)
        else:
            avg_cps = 80.0
            avg_accuracy = 85.0
            latest_difficulty = "Medium"
            count = 0

        game_breakdown[game_key] = {
            "title": domain_title,
            "session_count": count,
            "average_cps": round(avg_cps, 1),
            "average_accuracy": round(avg_accuracy, 1),
            "difficulty": latest_difficulty,
        }

    return {
        "overall_status": "Steady Practice",
        "total_sessions": len(history),
        "game_breakdown": game_breakdown,
    }


if __name__ == "__main__":
    sample_history = [
        {"timestamp": "2026-09-01", "cps": 85, "game_type": "memory_match"},
        {"timestamp": "2026-09-02", "cps": 84, "game_type": "number_sequence"},
        {"timestamp": "2026-09-03", "cps": 88, "game_type": "memory_match"},
        {"timestamp": "2026-09-04", "cps": 62, "game_type": "number_sequence"},  # Drop in Number Sequence
    ]
    print(detect_cps_anomalies(sample_history))
