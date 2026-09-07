"""
voice_assistant.py
------------------
AI Multilingual Voice Intent Recognition & Spoken Response Engine for CogniCare.

Supports English & Hindi spoken queries for elderly dementia patients who prefer
voice interaction over typing. Parses intents (game navigation, score checks,
medicine reminders, emergency assistance) and returns warm, encouraging TTS-ready responses.
"""

from typing import Dict, Any, Optional
from backend.app.services.store import FAKE_DB


# Supported Intents
INTENTS = {
    "START_GAME": ["game", "play", "start", "खेल", "गेम", "शुरू"],
    "CHECK_SCORE": ["score", "progress", "how am i doing", "स्कोर", "प्रदर्शन", "कैसा"],
    "CHECK_REMINDERS": ["medicine", "pill", "reminder", "water", "दवा", "याद दिलाओ", "पानी"],
    "CALL_CAREGIVER": ["help", "caregiver", "call", "doctor", "मदद", "केयरगिवर", "डॉक्टर"],
    "GREETING": ["hello", "hi", "namaste", "नमस्ते", "हेलो"],
}


def detect_language_and_intent(spoken_phrase: str) -> Dict[str, str]:
    """Detects primary language (English vs Hindi) and matching intent from spoken input."""
    phrase_lower = spoken_phrase.lower().strip()

    # Simple Hindi character detection heuristic
    contains_devanagari = any('\u0900' <= char <= '\u097f' for char in spoken_phrase)
    lang = "hi" if contains_devanagari else "en"

    # Match intent keywords
    detected_intent = "UNKNOWN"
    for intent, keywords in INTENTS.items():
        if any(kw in phrase_lower for kw in keywords):
            detected_intent = intent
            break

    return {"language": lang, "intent": detected_intent}


def process_voice_query(patient_id: str, spoken_phrase: str) -> Dict[str, Any]:
    """
    Processes spoken query from patient, fetches context (e.g. latest CPS score),
    and returns intent, action route, and warm spoken response text (TTS-ready).
    """
    parsing = detect_language_and_intent(spoken_phrase)
    lang = parsing["language"]
    intent = parsing["intent"]

    # Fetch patient CPS context if available
    history = FAKE_DB.get(patient_id, [])
    latest_cps = round(history[-1]["cps"], 1) if history else 75.0

    if intent == "START_GAME":
        if lang == "hi":
            response_text = "चलिए एक नया गेम शुरू करते हैं! अपनी पसंद का खेल चुनें।"
        else:
            response_text = "Let's start a new game! Choose your favorite game to begin."
        action = {"route": "/games", "type": "navigate"}

    elif intent == "CHECK_SCORE":
        if lang == "hi":
            response_text = f"बहुत बढ़िया! आपका आज का अभ्यास स्कोर {latest_cps} है। आप बहुत अच्छा कर रहे हैं।"
        else:
            response_text = f"Wonderful job! Your practice score today is {latest_cps}. You are doing great."
        action = {"route": "/progress", "type": "display_score", "score": latest_cps}

    elif intent == "CHECK_REMINDERS":
        if lang == "hi":
            response_text = "आपकी सुबह की दवा पूरी हो चुकी है। शाम को गेम खेलने का समय 5 बजे है।"
        else:
            response_text = "Your morning medication is completed. Next activity is scheduled for 5:00 PM."
        action = {"route": "/reminders", "type": "display_reminders"}

    elif intent == "CALL_CAREGIVER":
        if lang == "hi":
            response_text = "कोई बात नहीं, हम तुरंत आपके केयरगिवर को संदेश भेज रहे हैं।"
        else:
            response_text = "Don't worry, we are sending a message to your caregiver right now."
        action = {"route": "/alert_caregiver", "type": "trigger_alert"}

    elif intent == "GREETING":
        if lang == "hi":
            response_text = "नमस्ते! मैं आपकी कॉग्नीकेयर मदद हूँ। आज आप क्या करना चाहेंगे?"
        else:
            response_text = "Hello! I am your CogniCare assistant. What would you like to do today?"
        action = {"route": "/home", "type": "welcome"}

    else:
        if lang == "hi":
            response_text = "मैं समझ गया! आप होम स्क्रीन पर खेल खेल सकते हैं या अपना स्कोर देख सकते हैं।"
        else:
            response_text = "I understand! You can play games or check your practice score anytime."
        action = {"route": "/home", "type": "fallback"}

    return {
        "patient_id": patient_id,
        "input_phrase": spoken_phrase,
        "detected_language": lang,
        "detected_intent": intent,
        "response_text": response_text,
        "action": action,
    }


if __name__ == "__main__":
    # Test English query
    print(process_voice_query("demo-patient-01", "How am I doing today?"))
    # Test Hindi query
    print(process_voice_query("demo-patient-01", "खेल शुरू करें"))
