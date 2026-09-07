"""
anomaly_detector.py
--------------------
Patient & Caregiver Progress Monitoring Engine.

Evaluates trends in session activity over time to notice significant changes.
Uses compassionate, non-diagnostic wording designed to reassure family members
and caregivers while highlighting when a gentle check-in may be helpful.
"""

from statistics import mean
from typing import List, Optional

# If CPS drops by 15% or more across recent sessions, highlight for caregiver review.
DROP_THRESHOLD_PCT = 15.0

CAREGIVER_FRIENDLY_ALERT_MESSAGE = (
    "Noticeable change in recent activity patterns — a gentle check-in or caregiver review is recommended."
)


def check_trend(score_history: List[float], window: int = 3) -> Optional[dict]:
    """
    Evaluates historical scores to detect significant changes in patient engagement.

    score_history: chronological list of past session scores.
    window: session count for comparing recent vs. baseline performance.

    Returns a supportive alert dictionary if a change is detected, else None.
    """
    if len(score_history) < window * 2:
        return None

    prior = score_history[-(window * 2):-window]
    recent = score_history[-window:]

    prior_avg = mean(prior)
    recent_avg = mean(recent)

    if prior_avg == 0:
        return None

    pct_change = ((recent_avg - prior_avg) / prior_avg) * 100.0

    if pct_change <= -DROP_THRESHOLD_PCT:
        return {
            "alert": True,
            "message": CAREGIVER_FRIENDLY_ALERT_MESSAGE,
            "prior_avg": round(prior_avg, 2),
            "recent_avg": round(recent_avg, 2),
            "pct_change": round(pct_change, 2),
        }

    return None


if __name__ == "__main__":
    history = [78, 80, 82, 79, 81, 55, 50, 48]
    print(check_trend(history))
