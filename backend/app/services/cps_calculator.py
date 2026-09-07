"""
cps_calculator.py
------------------
Rule-based Cognitive Performance Score (CPS) engine.

This is intentionally NOT machine learning. Per the project report,
Phase 1 uses a deterministic weighted formula; Random Forest/XGBoost
is documented as Phase 2 future work. This file IS the "AI" for the
4-day demo: a transparent, explainable scoring pipeline.

Pipeline: Raw session metrics -> normalized sub-scores -> weighted CPS
          -> difficulty tier.
"""

from dataclasses import dataclass
from statistics import pstdev, mean
from typing import List, Optional


# ---- Weights, exactly as specified in the report ----
WEIGHTS = {
    "accuracy": 0.30,
    "response_speed": 0.20,
    "completion_rate": 0.20,
    "consistency": 0.15,
    "memory_performance": 0.15,
}

# ---- Difficulty tier thresholds (CPS 0-100) ----
DIFFICULTY_TIERS = [
    (85, "Hard"),
    (65, "Medium-Hard"),
    (40, "Moderate"),
    (0, "Easy"),
]


@dataclass
class SessionMetrics:
    """
    Raw input for a single completed game session.

    Handles response times passed either in MILLISECONDS (e.g. 2500)
    or in SECONDS (e.g. 2.5), auto-adapting to match Praveen's Flutter game payload.
    """
    accuracy: float              # 0-100, % correct
    response_time: float         # ms or seconds per action/answer
    completion_rate: float       # 0-100, % of session completed
    attempts: int
    errors: int
    hints_used: int
    is_memory_game: bool = False
    memory_specific_accuracy: Optional[float] = None  # only for memory games


def _normalize_response_speed(response_time: float,
                               best_ms: float = 1500,
                               worst_ms: float = 8000) -> float:
    """
    Converts raw response time into a 0-100 'speed score'.
    Faster (lower ms) = higher score. Clamped between best/worst
    reference points.
    
    Auto-adapts if response_time is passed in seconds (< 60s) instead of ms.
    """
    if response_time < 60.0:  # Auto-convert seconds to milliseconds
        response_time = response_time * 1000.0

    if response_time <= best_ms:
        return 100.0
    if response_time >= worst_ms:
        return 0.0

    # linear interpolation between best and worst
    span = worst_ms - best_ms
    return round(100.0 * (worst_ms - response_time) / span, 2)


def _consistency_score(recent_accuracies: List[float]) -> float:
    """
    Consistency = inverse of variance across recent sessions.
    Low variance (stable performance) -> high score.
    Needs at least 2 past sessions; defaults to 100 (neutral/no penalty)
    if there isn't enough history yet (e.g. patient's first session).
    """
    if len(recent_accuracies) < 2:
        return 100.0
    spread = pstdev(recent_accuracies)
    # cap spread contribution at 50 points of stdev -> 0 score
    score = max(0.0, 100.0 - (spread / 50.0) * 100.0)
    return round(score, 2)


def calculate_cps(session: SessionMetrics,
                   recent_accuracies: Optional[List[float]] = None) -> dict:
    """
    Main entry point. Takes one session's metrics plus recent accuracy
    history (for consistency), returns CPS + sub-scores + difficulty tier.
    """
    recent_accuracies = recent_accuracies or []

    accuracy_score = max(0.0, min(100.0, session.accuracy))
    speed_score = _normalize_response_speed(session.response_time)
    completion_score = max(0.0, min(100.0, session.completion_rate))
    consistency_score = _consistency_score(recent_accuracies)

    # Memory performance: use memory-specific accuracy if this was a
    # memory game, otherwise fall back to general accuracy so the
    # formula still works for non-memory games (Pattern Recognition etc).
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

    return {
        "cps": cps,
        "difficulty_tier": map_to_difficulty(cps),
        "sub_scores": {
            "accuracy": accuracy_score,
            "response_speed": speed_score,
            "completion_rate": completion_score,
            "consistency": consistency_score,
            "memory_performance": memory_score,
        },
    }


def map_to_difficulty(cps: float) -> str:
    """Maps a CPS value to a difficulty tier label."""
    for threshold, label in DIFFICULTY_TIERS:
        if cps >= threshold:
            return label
    return "Easy"


if __name__ == "__main__":
    demo_session = SessionMetrics(
        accuracy=88,
        response_time=2.2,  # seconds or ms
        completion_rate=100,
        attempts=12,
        errors=2,
        hints_used=1,
        is_memory_game=True,
        memory_specific_accuracy=91,
    )
    result = calculate_cps(demo_session, recent_accuracies=[80, 85, 82])
    print(result)
