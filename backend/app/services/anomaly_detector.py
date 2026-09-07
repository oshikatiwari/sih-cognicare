"""
anomaly_detector.py
--------------------
Simple % change trend check on CPS history. Flags a caregiver alert
when performance drops significantly. Uses cautious, non-diagnostic
language exactly as the report specifies - this NEVER claims a
dementia-progression diagnosis, only "review recommended."
"""

from statistics import mean
from typing import List, Optional

# If CPS drops by this % or more (recent avg vs prior avg), flag it.
DROP_THRESHOLD_PCT = 15.0

NON_DIAGNOSTIC_ALERT_MESSAGE = (
    "Significant change observed — caregiver review recommended."
)


def check_trend(score_history: List[float], window: int = 3) -> Optional[dict]:
    """
    score_history: chronological list of past CPS scores, oldest first.
    window: how many recent sessions count as "recent" vs "prior".

    Returns an alert dict if a significant drop is detected, else None.
    Needs at least 2*window sessions of history to compare meaningfully;
    returns None (no alert - not enough data) otherwise.
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
            "message": NON_DIAGNOSTIC_ALERT_MESSAGE,
            "prior_avg": round(prior_avg, 2),
            "recent_avg": round(recent_avg, 2),
            "pct_change": round(pct_change, 2),
        }

    return None


if __name__ == "__main__":
    # Quick manual test
    history = [78, 80, 82, 79, 81, 55, 50, 48]  # sharp drop at the end
    print(check_trend(history))
