"""
cps_calculator.py
------------------
Cognitive Performance & Supportive Engagement Calculator.

Designed with a patient-first and caregiver-first approach. Converts gameplay
metrics (accuracy, response timing, session completion, consistency, and memory recall)
into an explainable Cognitive Performance Score (CPS) and supportive engagement level.

Maintains technical precision while using warm, encouraging feedback labels suitable
for elderly users and family caregivers.
"""

from dataclasses import dataclass
from statistics import pstdev, mean
from typing import List, Optional


# ---- Weighted Formula (strictly matching report specifications) ----
WEIGHTS = {
    "accuracy": 0.30,
    "response_speed": 0.20,
    "completion_rate": 0.20,
    "consistency": 0.15,
    "memory_performance": 0.15,
}

# ---- Difficulty tier thresholds with empathetic, patient-friendly display labels ----
DIFFICULTY_TIERS = [
    (85, "Hard", "Gentle Challenge"),
    (65, "Medium-Hard", "Steady Practice"),
    (40, "Moderate", "Comfortable Pace"),
    (0, "Easy", "Relaxed Practice"),
]


@dataclass
class SessionMetrics:
    """
    Performance metrics recorded during a patient's game session.
    Auto-adapts whether response timing is provided in seconds or milliseconds.
    """
    accuracy: float              # 0-100, % correct answers
    response_time: float         # timing per action (seconds or ms)
    completion_rate: float       # 0-100, % of session completed
    attempts: int
    errors: int
    hints_used: int
    is_memory_game: bool = False
    memory_specific_accuracy: Optional[float] = None


def _normalize_response_speed(response_time: float,
                               best_ms: float = 1500,
                               worst_ms: float = 8000) -> float:
    """
    Converts response time into a 0-100 speed indicator.
    Clamped between supportive reference points so patients are never penalized for taking a thoughtful moment.
    """
    if response_time < 60.0:  # Auto-convert seconds to milliseconds
        response_time = response_time * 1000.0

    if response_time <= best_ms:
        return 100.0
    if response_time >= worst_ms:
        return 0.0

    span = worst_ms - best_ms
    return round(100.0 * (worst_ms - response_time) / span, 2)


def _consistency_score(recent_accuracies: List[float]) -> float:
    """
    Measures stability across recent sessions.
    Steadier performance rewards higher consistency scores to encourage regular practice.
    """
    if len(recent_accuracies) < 2:
        return 100.0
    spread = pstdev(recent_accuracies)
    score = max(0.0, 100.0 - (spread / 50.0) * 100.0)
    return round(score, 2)


def calculate_cps(session: SessionMetrics,
                   recent_accuracies: Optional[List[float]] = None) -> dict:
    """
    Calculates overall Cognitive Performance Score (CPS 0-100) and maps it
    to both technical tier names and warm, patient-facing display labels.
    """
    recent_accuracies = recent_accuracies or []

    accuracy_score = max(0.0, min(100.0, session.accuracy))
    speed_score = _normalize_response_speed(session.response_time)
    completion_score = max(0.0, min(100.0, session.completion_rate))
    consistency_score = _consistency_score(recent_accuracies)

    if session.is_memory_game and session.memory_specific_accuracy is not None:
        memory_score = max(0.0, min(100.0, session.memory_specific_accuracy))
    else:
        memory_score = accuracy_score

    cps = (
        accuracy_score * WEIGHTS["accuracy"]
        + speed_score * WEIGHTS["response_speed"]
        + completion_score * WEIGHTS["completion_rate"]
        + consistency_score * WEIGHTS["consistency"]
        + memory_score * WEIGHTS["memory_performance"]
    )
    cps = round(cps, 2)

    tier_info = map_to_difficulty_info(cps)

    return {
        "cps": cps,
        "difficulty_tier": tier_info["tier"],
        "display_label": tier_info["display_label"],
        "sub_scores": {
            "accuracy": accuracy_score,
            "response_speed": speed_score,
            "completion_rate": completion_score,
            "consistency": consistency_score,
            "memory_performance": memory_score,
        },
    }


def map_to_difficulty_info(cps: float) -> dict:
    """Maps a CPS score to technical tier and supportive display label."""
    for threshold, tier, label in DIFFICULTY_TIERS:
        if cps >= threshold:
            return {"tier": tier, "display_label": label}
    return {"tier": "Easy", "display_label": "Relaxed Practice"}


def map_to_difficulty(cps: float) -> str:
    """Legacy helper for backward compatibility."""
    return map_to_difficulty_info(cps)["tier"]


if __name__ == "__main__":
    demo_session = SessionMetrics(
        accuracy=88,
        response_time=2.2,
        completion_rate=100,
        attempts=12,
        errors=2,
        hints_used=1,
        is_memory_game=True,
        memory_specific_accuracy=91,
    )
    result = calculate_cps(demo_session, recent_accuracies=[80, 85, 82])
    print(result)
