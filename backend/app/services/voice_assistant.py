"""
voice_assistant.py
------------------
AI Multilingual Voice Guidance, On-Demand Translation & Bluetooth Speaker Assistance Engine for Smriti (स्मृति / 💾).

Features:
  1. 5-Language Support: English (en), Hindi (hi), Assamese (as), Mizo (mzo), Khasi (kha).
  2. Duolingo-Style Language Selector & On-Demand Text Translation.
  3. Bluetooth Audio Speaker & Hearing Aid Pairing Guidance for Elderly Patients.
  4. Step-by-Step Screen Guidance & Multilingual Voice Intent Parsing.
"""

from typing import Dict, Any, Optional, List
from backend.app.services.store import FAKE_DB


# Supported Languages Catalog (Duolingo-style Selection Metadata)
SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English", "native_name": "English", "flag": "🇬🇧", "description": "Global English guidance"},
    {"code": "hi", "name": "Hindi", "native_name": "हिन्दी", "flag": "🇮🇳", "description": "राष्ट्रीय भाषा मार्गदर्शन"},
    {"code": "as", "name": "Assamese", "native_name": "অসমীয়া", "flag": "🌾", "description": "অসমীয়া ভাষাত নিৰ্দেশনা"},
    {"code": "mzo", "name": "Mizo", "native_name": "Mizo ṭawng", "flag": "🏔️", "description": "Mizo tawngakaihhruaina"},
    {"code": "kha", "name": "Khasi", "native_name": "Ka Ktien Khasi", "flag": "🌲", "description": "Jingkyntiew ha ka ktien Khasi"},
]


# Step-by-Step Screen Guidance Prompts for Elderly Patients
SCREEN_GUIDANCE_PROMPTS = {
    "home": {
        "en": "Welcome to Smriti! Tap the big green game button to start your daily brain exercise, or tap the microphone anytime to talk to me.",
        "hi": "स्मृति में आपका स्वागत है! अपनी दैनिक दिमागी कसरत शुरू करने के लिए बड़े हरे बटन को दबाएं, या मुझसे बात करने के लिए माइक दबाएं।",
        "as": "স্মৃতিলৈ আপোনাক স্বাগতম! আপোনাৰ দৈনিক মগজুৰ অনুশীলন আৰম্ভ কৰিবলৈ ডাঙৰ সেউজীয়া বুটামটো টিপক, নতুবা কথা ক'বলৈ মাইক্ৰ'ফ'নত টিপক।",
        "mzo": "Smriti-ah lo lawm rawh le! Ni tin hriatna tihhmasawnna infiamna tan turin a hring lian hmet rawh, a nih loh chuan mi biak turin mic hmet rawh.",
        "kha": "Pdiang burom sha Smriti! Pynkiat iaphi ban pynkyntiew iaka jingmut da kaba kynton iaka button haing, lada kwah ban kren kynton iaka microphone.",
        "next_step": "Select green game button or tap microphone to speak."
    },
    "games_menu": {
        "en": "Here are your Smriti memory activities. Tap 'Memory Matching' with the card icons to begin a comfortable round.",
        "hi": "यहाँ आपके स्मृति खेल हैं। अभ्यास शुरू करने के लिए ताश के पत्तों वाले 'मेमोरी मैचिंग' बटन पर टैप करें।",
        "as": "ইয়ালৈ আপোনাৰ স্মৃতি খেলসমূহ আছে। আৰম্ভ কৰিবলৈ কাৰ্ড চিন থকা 'মেম'ৰী মেচিং' বুটামত টিপক।",
        "mzo": "Hian hriatrengna infiamnate a awm e. A awlsam zawnga tan turin card lem awmna 'Memory Matching' hmet rawh.",
        "kha": "Hane ki jingialeh pynkynmaw jong phi. Kynton ia ka 'Memory Matching' ban sdang ia ka jingialeh.",
        "next_step": "Select Memory Matching game."
    },
    "gameplay": {
        "en": "Take your time. Gently tap two cards to flip them and find a matching pair. There is no rush at all.",
        "hi": "आराम से खेलें। दो कार्ड्स को मिलाकर जोड़ी खोजें। कोई जल्दी नहीं है, आराम से खेलें।",
        "as": "ধৈৰ্য্যেৰে খেলক। দুখন কাৰ্ড উলটাই মিলা জোৰা বিচাৰি উলিয়াওক। কোনো খৰখেদা নাই।",
        "mzo": "Hmanhmawh duh suh. Card pahnih hmet la, a inhnim hnai tur zawn chhuah tum rawh.",
        "kha": "Wat pynhap jingmut. Kynton ia ar ki card ban wad ia kiba iadei. Ym don jingkloi stet.",
        "next_step": "Tap two matching cards."
    },
    "game_results": {
        "en": "Fantastic effort! Your practice score today is {cps}. Take a short rest and drink some water.",
        "hi": "बहुत बढ़िया प्रयास! आज आपका अभ्यास स्कोर {cps} है। थोड़ा आराम करें और पानी पी लें।",
        "as": "অতি সুন্দৰ প্ৰচেষ্টা! আজি আপোনাৰ অনুশীলন স্ক'ৰ হ'ল {cps}। অলপ জিৰণি লওক আৰু পানী খাওক।",
        "mzo": "Thawk tha hle mai! Vawiina i mark hmuh chu {cps} a ni e. Chawl hlek la, tui in rawh.",
        "kha": "Jingkyntiew babha! Ka jingtynjuh jong phi mynta ka long {cps}. Shongthait shisyndon bad dih um.",
        "next_step": "Rest or choose another game."
    },
    "reminders": {
        "en": "Here is your care schedule. Please take your morning medication with water, then tap 'Completed'.",
        "hi": "यह आपकी देखभाल का समय है। कृपया अपनी सुबह की दवा पानी के साथ लें, फिर 'पूरा हुआ' पर टैप करें।",
        "as": "এইয়া আপোনাৰ যত্নৰ সময়সূচী। পুৱাৰ ঔষধ পানীৰ সৈতে লওক, তাৰ পিছত 'সম্পূৰ্ণ হ'ল'ত টিপক।",
        "mzo": "Hian i damdawi ei hun a awm e. Khawngaihin i tukthuan damdawi ei la, 'Completed' tih hmet rawh.",
        "kha": "Hane ka por dih dawai jong phi. Sngewbha dih ia ka dawai mynta step, nangta kynton 'Completed'.",
        "next_step": "Take medicine and confirm."
    },
}


# Bluetooth Speaker Pairing Guidance Prompts
BLUETOOTH_PAIRING_PROMPTS = {
    "en": "Bluetooth Audio Connected: Voice guidance is now playing through your external Bluetooth speaker for loud and clear hearing.",
    "hi": "ब्लूटूथ ऑडियो कनेक्टेड: स्पष्ट आवाज के लिए वॉयस गाइडेंस अब आपके बाहरी ब्लूटूथ स्पीकर पर प्ले हो रहा है।",
    "as": "ব্লুটুথ অডিঅ' সংসংযুক্ত: স্পষ্ট শব্দৰ বাবে এতিয়া আপোনাৰ ব্লুটুথ স্পীকাৰত সৱল নিৰ্দেশনা বাজিছে।",
    "mzo": "Bluetooth Audio thlun zawm a ni e: Hriat nuam tak turin aw kaihhruaina hi bluetooth speaker atangin a chhuak mek e.",
    "kha": "Bluetooth Audio la pyniasoh: Ka jingkren ialam burom ka nang wan lyngba u bluetooth speaker jong phi.",
}


# Supported Voice Intent Keywords
INTENTS = {
    "START_GAME": ["game", "play", "start", "खेल", "गेम", "শুরু", "খেল", "infiamna", "tan", "jingialeh", "sdang"],
    "CHECK_SCORE": ["score", "progress", "how am i doing", "स्कोर", "प्रदर्शन", "স্ক'ৰ", "হিসাপ", "mark", "hmuh", "jingtynjuh"],
    "CHECK_REMINDERS": ["medicine", "pill", "reminder", "water", "दवा", "पानी", "ঔষধ", "পানী", "damdawi", "tui", "dawai", "um"],
    "CALL_CAREGIVER": ["help", "caregiver", "call", "doctor", "मदद", "सहायता", "সহায়", "ডাক্তৰ", "tanpui", "bual", "iarap", "doctor"],
    "GREETING": ["hello", "hi", "namaste", "smriti", "नमस्ते", "নমস্কাৰ", "স্মৃতি", "chibai", "khublei"],
}


def get_supported_languages() -> List[Dict[str, str]]:
    """Returns Duolingo-style language selection catalog."""
    return SUPPORTED_LANGUAGES


def get_bluetooth_audio_guidance(lang: str = "en") -> Dict[str, str]:
    """Returns spoken notification prompt when Bluetooth speaker/hearing aid is connected."""
    lang_clean = lang.lower().strip()
    prompt = BLUETOOTH_PAIRING_PROMPTS.get(lang_clean, BLUETOOTH_PAIRING_PROMPTS["en"])
    return {
        "status": "connected",
        "language": lang_clean,
        "spoken_bluetooth_notice": prompt,
    }


def translate_text(text: str, source_lang: str, target_lang: str) -> Dict[str, str]:
    """Translates text or guidance phrase on-demand between supported languages."""
    target_clean = target_lang.lower().strip()
    if target_clean not in ["en", "hi", "as", "mzo", "kha"]:
        target_clean = "en"

    # Match predefined guidance phrase translations or fallback with language metadata tag
    for screen, lang_dict in SCREEN_GUIDANCE_PROMPTS.items():
        for l_code, val in lang_dict.items():
            if isinstance(val, str) and text.strip().lower() in val.strip().lower():
                return {
                    "source_lang": source_lang,
                    "target_lang": target_clean,
                    "original_text": text,
                    "translated_text": lang_dict.get(target_clean, text),
                }

    # Default fallback translation wrapper
    return {
        "source_lang": source_lang,
        "target_lang": target_clean,
        "original_text": text,
        "translated_text": f"[{target_clean.upper()}] {text}",
    }


def detect_language_and_intent(spoken_phrase: str) -> Dict[str, str]:
    """Detects language and intent from spoken phrase."""
    phrase_lower = spoken_phrase.lower().strip()

    has_assamese = any('\u0980' <= char <= '\u09ff' for char in spoken_phrase) or any(w in phrase_lower for w in ["নমস্কাৰ", "স্মৃতি", "খেল", "স্ক'ৰ", "ঔষধ"])
    has_hindi = any('\u0900' <= char <= '\u097f' for char in spoken_phrase)
    has_mizo = any(w in phrase_lower for w in ["chibai", "infiamna", "damdawi", "hmet", "rawh", "tan", "tui"])
    has_khasi = any(w in phrase_lower for w in ["khublei", "jingialeh", "dawai", "kynton", "phi", "por", "um"])

    if has_assamese:
        lang = "as"
    elif has_hindi:
        lang = "hi"
    elif has_mizo:
        lang = "mzo"
    elif has_khasi:
        lang = "kha"
    else:
        lang = "en"

    detected_intent = "UNKNOWN"
    for intent, keywords in INTENTS.items():
        if any(kw in phrase_lower for kw in keywords):
            detected_intent = intent
            break

    return {"language": lang, "intent": detected_intent}


def get_screen_voice_guidance(screen_id: str, lang: str = "en", patient_id: str = "demo-patient-01") -> Dict[str, Any]:
    """Returns step-by-step spoken guidance in any of the 5 supported languages."""
    screen_key = screen_id.lower().strip()
    prompts = SCREEN_GUIDANCE_PROMPTS.get(screen_key, SCREEN_GUIDANCE_PROMPTS["home"])

    history = FAKE_DB.get(patient_id, [])
    latest_cps = round(history[-1]["cps"], 1) if history else 80.0

    lang_clean = lang.lower().strip()
    if lang_clean not in ["en", "hi", "as", "mzo", "kha"]:
        lang_clean = "en"

    prompt_template = prompts.get(lang_clean, prompts["en"])
    spoken_guidance = prompt_template.format(cps=latest_cps)

    return {
        "patient_id": patient_id,
        "screen_id": screen_key,
        "language": lang_clean,
        "spoken_guidance": spoken_guidance,
        "next_step_instruction": prompts.get("next_step", ""),
    }


def process_voice_query(patient_id: str, spoken_phrase: str, forced_lang: Optional[str] = None) -> Dict[str, Any]:
    """Processes spoken query and returns intent, action, and TTS response."""
    parsing = detect_language_and_intent(spoken_phrase)
    lang = forced_lang if forced_lang else parsing["language"]
    intent = parsing["intent"]

    history = FAKE_DB.get(patient_id, [])
    latest_cps = round(history[-1]["cps"], 1) if history else 75.0

    if intent == "START_GAME":
        responses = {
            "en": "Let's start a new game! Choose your favorite game to begin.",
            "hi": "चलिए एक नया गेम शुरू करते हैं! अपनी पसंद का खेल चुनें।",
            "as": "ব'লক এটা নতুন খেল আৰম্ভ কৰোঁ! খেলিবলৈ মনপছন্দ খেল বাছি লওক।",
            "mzo": "Infiamna thar i tan ang u! Bullian tan turin i ngainat ber thlang rawh.",
            "kha": "Kha ngin sdang ia ka jingialeh thymmai! Jied ia ka jingialeh ba phi sngewtynnad.",
        }
        action = {"route": "/games", "type": "navigate"}

    elif intent == "CHECK_SCORE":
        responses = {
            "en": f"Wonderful job! Your practice score today is {latest_cps}. You are doing great.",
            "hi": f"बहुत बढ़िया! आपका आज का अभ्यास स्कोर {latest_cps} है। आप बहुत अच्छा कर रहे हैं।",
            "as": f"অতি সুন্দৰ! আজি আপোনাৰ অনুশীলন স্ক'ৰ হ'ল {latest_cps}। আপুনি খুব ভাল কৰিছে।",
            "mzo": f"Thawk tha hle mai! Vawiina i mark hmuh chu {latest_cps} a ni e. I ti tha hle mai.",
            "kha": f"Jingkyntiew babha! Ka jingtynjuh jong phi mynta ka long {latest_cps}. Phi ialeh bha.",
        }
        action = {"route": "/progress", "type": "display_score", "score": latest_cps}

    elif intent == "CHECK_REMINDERS":
        responses = {
            "en": "Your morning medication is completed. Next activity is scheduled for 5:00 PM.",
            "hi": "आपकी सुबह की दवा पूरी हो चुकी है। शाम को गेम खेलने का समय 5 बजे है।",
            "as": "আপোনাৰ পুৱাৰ ঔষধ লোৱা সম্পূৰ্ণ হ'ল। পৰৱৰ্তী কাৰ্যসূচী বিয়লি ৫ বজাত।",
            "mzo": "I tukthuan damdawi ei zawh a ni e. Infiamna dawt leh chu tlai dar 5 a ni ang.",
            "kha": "Ka dawai mynta step ka la dep. Ka jingialeh nangta ka long ha ka por 5 PM.",
        }
        action = {"route": "/reminders", "type": "display_reminders"}

    elif intent == "CALL_CAREGIVER":
        responses = {
            "en": "Don't worry, we are sending a message to your caregiver right now.",
            "hi": "कोई बात नहीं, हम तुरंत आपके केयरगिवर को संदेश भेज रहे हैं।",
            "as": "চিন্তা নকৰিব, আমি এতিয়াই আপোনাৰ তত্ত্বাৱধানকাৰীলৈ বাৰ্তা প্ৰেৰণ কৰিছোঁ।",
            "mzo": "Mangang suh, i enkawltu hnena thuthawn kan thawn mek e.",
            "kha": "Wat sngewsyier, ngi phah khubor sha u nongsumar jong phi mynta.",
        }
        action = {"route": "/alert_caregiver", "type": "trigger_alert"}

    elif intent == "GREETING":
        responses = {
            "en": "Hello! I am your Smriti assistant. What would you like to do today?",
            "hi": "नमस्ते! मैं आपकी स्मृति मदद हूँ। आज आप क्या करना चाहेंगे?",
            "as": "নমস্কাৰ! মই আপোনাৰ স্মৃতি সহায়ক। আজি আপুনি কি কৰিব বিচাৰিব?",
            "mzo": "Chibai! Smriti tanpuitu ka ni e. Vawiin hian eng nge tih i duh ang?",
            "kha": "Khublei! Nga long u nongiarap Smriti. Kiei ba phi kwah ban leh mynta?",
        }
        action = {"route": "/home", "type": "welcome"}

    else:
        responses = {
            "en": "I understand! You can play games or check your practice score anytime.",
            "hi": "मैं समझ गया! आप होम स्क्रीन पर खेल खेल सकते हैं या अपना स्कोर देख सकते हैं।",
            "as": "মই বুজি পালোঁ! আপুনি যিকোনো সময়তে খেল খেলিব পাৰে নতুবা স্ক'ৰ চাব পাৰে।",
            "mzo": "Ka hrethiam e! Hun eng tik ah pawh infiamna i khel thei a ni.",
            "kha": "Nga sngewthuh! Phi lah ban ialeh jingialeh lane peit ia ka jingtynjuh jong phi.",
        }
        action = {"route": "/home", "type": "fallback"}

    response_text = responses.get(lang, responses["en"])

    return {
        "patient_id": patient_id,
        "input_phrase": spoken_phrase,
        "detected_language": lang,
        "detected_intent": intent,
        "response_text": response_text,
        "action": action,
    }
