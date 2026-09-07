"""
voice_assistant.py
------------------
AI Multilingual Voice Guidance & Elderly Patient Assistance Engine for Smriti (स्मृति).

Provides step-by-step spoken instructions (English & Hindi) for elderly patients
with dementia who need gentle, natural voice guidance on every screen of the app
(e.g., home navigation, starting a game, gameplay instructions, post-game summary,
and medication reminders).
"""

from typing import Dict, Any, Optional
from backend.app.services.store import FAKE_DB


# Step-by-Step Screen Guidance Prompts for Elderly Patients in Smriti (स्मृति)
SCREEN_GUIDANCE_PROMPTS = {
    "home": {
        "en": "Welcome to Smriti! Tap the big green game button to start your daily brain exercise, or tap the microphone anytime to talk to me.",
        "hi": "स्मृति में आपका स्वागत है! अपनी दैनिक दिमागी कसरत शुरू करने के लिए बड़े हरे बटन को दबाएं, या मुझसे बात करने के लिए माइक दबाएं।",
        "next_step": "Tap green button to play or microphone to speak."
    },
    "games_menu": {
        "en": "Here are your Smriti memory activities. Tap 'Memory Matching' with the card icons to begin a comfortable round.",
        "hi": "यहाँ आपके स्मृति खेल हैं। अभ्यास शुरू करने के लिए ताश के पत्तों वाले 'मेमोरी मैचिंग' बटन पर टैप करें।",
        "next_step": "Select Memory Matching game."
    },
    "gameplay": {
        "en": "Take your time. Gently tap two cards to flip them and find a matching pair. There is no rush at all.",
        "hi": "आराम से खेलें। दो कार्ड्स को मिलाकर जोड़ी खोजें। कोई जल्दी नहीं है, आराम से खेलें।",
        "next_step": "Tap two matching cards."
    },
    "game_results": {
        "en": "Fantastic effort! Your practice score today is {cps}. Take a short rest and drink some water.",
        "hi": "बहुत बढ़िया प्रयास! आज आपका अभ्यास स्कोर {cps} है। थोड़ा आराम करें और पानी पी लें।",
        "next_step": "Rest or choose another game."
    },
    "reminders": {
        "en": "Here is your care schedule. Please take your morning medication with water, then tap 'Completed'.",
        "hi": "यह आपकी देखभाल का समय है। कृपया अपनी सुबह की दवा पानी के साथ लें, फिर 'पूरा हुआ' पर टैप करें।",
        "next_step": "Take medicine and confirm."
    },
}


# Supported Voice Intents
INTENTS = {
    "START_GAME": ["game", "play", "start", "खेल", "गेम", "शुरू"],
    "CHECK_SCORE": ["score", "progress", "how am i doing", "स्कोर", "प्रदर्शन", "कैसा"],
    "CHECK_REMINDERS": ["medicine", "pill", "reminder", "water", "दवा", "याद दिलाओ", "पानी"],
    "CALL_CAREGIVER": ["help", "caregiver", "call", "doctor", "मदद", "केयरगिवर", "डॉक्टर"],
    "GREETING": ["hello", "hi", "namaste", "smriti", "नमस्ते", "हेलो", "स्मृति"],
}


def get_screen_voice_guidance(screen_id: str, lang: str = "en", patient_id: str = "demo-patient-01") -> Dict[str, Any]:
    """
    Returns step-by-step spoken guidance for elderly dementia patients navigating any screen in Smriti.
    Includes patient score context if on the results screen.
    """
    screen_key = screen_id.lower().strip()
    prompts = SCREEN_GUIDANCE_PROMPTS.get(screen_key, SCREEN_GUIDANCE_PROMPTS["home"])

    history = FAKE_DB.get(patient_id, [])
    latest_cps = round(history[-1]["cps"], 1) if history else 80.0

    prompt_template = prompts.get(lang, prompts["en"])
    spoken_guidance = prompt_template.format(cps=latest_cps)

    return {
        "patient_id": patient_id,
        "screen_id": screen_key,
        "language": lang,
        "spoken_guidance": spoken_guidance,
        "next_step_instruction": prompts.get("next_step", ""),
    }


def detect_language_and_intent(spoken_phrase: str) -> Dict[str, str]:
    """Detects primary language (English vs Hindi) and matching intent from spoken input."""
    phrase_lower = spoken_phrase.lower().strip()
    contains_devanagari = any('\u0900' <= char <= '\u097f' for char in spoken_phrase)
    lang = "hi" if contains_devanagari else "en"

    detected_intent = "UNKNOWN"
    for intent, keywords in INTENTS.items():
        if any(kw in phrase_lower for kw in keywords):
            detected_intent = intent
            break

    return {"language": lang, "intent": detected_intent}


def process_voice_query(patient_id: str, spoken_phrase: str) -> Dict[str, Any]:
    """
    Processes spoken query from patient, fetches context (e.g. latest CPS score),
    and returns intent, action route, and warm spoken response text (TTS-ready) for Smriti.
    """
    parsing = detect_language_and_intent(spoken_phrase)
    lang = parsing["language"]
    intent = parsing["intent"]

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
            response_text = "नमस्ते! मैं आपकी स्मृति मदद हूँ। आज आप क्या करना चाहेंगे?"
        else:
            response_text = "Hello! I am your Smriti assistant. What would you like to do today?"
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
    print(get_screen_voice_guidance("home", lang="en"))
    print(get_screen_voice_guidance("home", lang="hi"))
