"""
voice_assistant.py
------------------
AI Multilingual Voice Guidance, On-Demand Translation & Bluetooth Speaker Assistance Engine for Smriti (স্মৃতি / 💾).

Features:
  1. 5-Language Support: English (en), Hindi (hi), Assamese (as), Mizo (mzo), Khasi (kha).
  2. Duolingo-Style Language Selector & On-Demand Text Translation.
  3. Bluetooth Audio Speaker & Hearing Aid Pairing Guidance for Elderly Patients.
  4. Step-by-Step Screen & Game Guidance Prompts walking elderly patients through every action.
  5. Intent Parser & Voice Query Processing for hands-free app navigation.
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


# Step-by-Step Screen & Game Guidance Prompts for Elderly Patients (5 Languages)
SCREEN_GUIDANCE_PROMPTS = {
    "home": {
        "en": "Welcome to Smriti! Tap the big green game button to start your daily brain exercise, or tap the microphone anytime to talk to me.",
        "hi": "स्मृति में आपका स्वागत है! अपनी दैनिक दिमागी कसरत शुरू करने के लिए बड़े हरे बटन को दबाएं, या मुझसे बात करने के लिए माइक दबाएं।",
        "as": "স্মৃতিলৈ আপোনাক স্বাগতম! আপোনাৰ দৈনিক মগজুৰ অনুশীলন আৰম্ভ কৰিবলৈ ডাঙৰ সেউজীয়া বুটামটো টিপক, নতুবা কথা ক'বলৈ মাইক্ৰ'ফ'নত টিপক।",
        "mzo": "Smriti-ah lo lawm rawh le! Ni tin hriatna tihhmasawnna infiamna tan turin a hring lian hmet rawh, a nih loh chuan mi biak turin mic hmet rawh.",
        "kha": "Pdiang burom sha Smriti! Pynkiat iaphi ban pynkyntiew iaka jingmut da kaba kynton iaka button haing, lada kwah ban kren kynton iaka microphone.",
        "next_step": "Select green game button or tap microphone to speak."
    },
    "language_selection": {
        "en": "Select your language. Tap English, Hindi, Assamese, Mizo, or Khasi to hear all instructions in your mother tongue.",
        "hi": "अपनी भाषा चुनें। अपनी मातृभाषा में सभी निर्देश सुनने के लिए हिंदी, अंग्रेजी, असमिया, मिज़ो या खासी पर टैप करें।",
        "as": "আপোনাৰ ভাষা বাছি লওক। আপোনাৰ মাতৃভাষাত সকলো নিৰ্দেশনা শুনিবলৈ অসমীয়া, হিন্দী, ইংৰাজী, মিজো বা খাচী টিপক।",
        "mzo": "I ṭawng duh thlang rawh. I nu ṭawngngeia hriat turin English, Hindi, Assamese, Mizo, a nih loh chuan Khasi hmet rawh.",
        "kha": "Jied ia ka ktien jong phi. Kynton English, Hindi, Assamese, Mizo, lane Khasi ban sngap ia ki jingbthah ha ka ktien haing.",
        "next_step": "Tap on your preferred language flag."
    },
    "mode_selection": {
        "en": "Choose your mode. Tap 'Patient' for brain games, or tap 'Caregiver' to view progress reports.",
        "hi": "अपना मोड चुनें। खेलों के लिए 'रोगी (Patient)' दबाएं, या रिपोर्ट देखने के लिए 'केयरगिवर' दबाएं।",
        "as": "আপোনাৰ ম'ড বাছি লওক। খেলৰ বাবে 'ৰোগী' বাছি লওক, নতুবা প্ৰতিবেদন চাবলৈ 'তত্ত্বাৱধানকাৰী' টিপক।",
        "mzo": "I hmanning thlang rawh. Infiamna tan 'Patient' hmet la, report pekkawng en turin 'Caregiver' hmet rawh.",
        "kha": "Jied ia ka rukom. Kynton 'Patient' na bynta ki jingialeh, lane 'Caregiver' ban peit iaki kaiphriot.",
        "next_step": "Select Patient or Caregiver mode."
    },
    "difficulty_selection": {
        "en": "Select difficulty. Tap Easy for a relaxed pace, Medium for steady practice, or Hard for a gentle challenge.",
        "hi": "कठिनाई चुनें। आसान अभ्यास के लिए Easy, मध्यम के लिए Medium, या चुनौती के लिए Hard दबाएं।",
        "as": "কঠিনতা বাছি লওক। সহজ অনুশীলনৰ বাবে Easy, মধ্যমৰ বাবে Medium, বা প্ৰত্যাহ্বানৰ বাবে Hard টিপক।",
        "mzo": "A harsat zawng thlang rawh. Awlsam tak tan Easy, a chawp tan Medium, a harsat tak tan Hard hmet rawh.",
        "kha": "Jied ia ka jingeh. Kynton Easy na bynta ka jingialeh jem, Medium na bynta ka jingmlien, lane Hard.",
        "next_step": "Tap Easy, Medium, or Hard."
    },
    "memory_match": {
        "en": "Memory Match Game: Gently tap two cards to flip them and match pairs of Assam flowers, tea leaves, or family faces.",
        "hi": "मेमोरी मैच खेल: ताश के दो पत्तों को पलटकर असम के फूलों, चाय की पत्तियों या परिवार की तस्वीरों की जोड़ी मिलाएं।",
        "as": "মেম'ৰী মেচ খেল: অসমৰ ফুল, চাহ পাত বা পৰিয়ালৰ ছবিৰ জোৰা মিলাবলৈ দুখন কাৰ্ড উলটাই টিপক।",
        "mzo": "Memory Match Infiamna: Card pahnih hmet la, Assam pangpar, thingpui hnah, a nih loh chuan chhungte hmai inhnim zawn chhuah tum rawh.",
        "kha": "Memory Match: Kynton ia ar ki card ban wad ia ki synrop tiew Assam, sla cha, lane dur ki kur ki kha.",
        "next_step": "Tap two cards to find a pair."
    },
    "number_sequence": {
        "en": "Number Sequence Game: Listen carefully to the numbers spoken to you, then repeat them by tapping the number keys.",
        "hi": "नंबर अनुक्रम खेल: बोले गए नंबरों को ध्यान से सुनें, फिर नंबर बटन दबाकर उन्हें दोहराएं।",
        "as": "নম্বৰ অনুক্ৰম খেল: কোৱা নম্বৰবোৰ মনোযোগেৰে শুনক, তাৰ পিছত নম্বৰ বুটাম টিপি সেইবোৰ পুনৰাবৃত্তি কৰক।",
        "mzo": "Number Sequence Infiamna: Nomba an sawite chu uluk takin ngaithla la, nomba hmehna hmangin sawi nawn leh rawh.",
        "kha": "Number Sequence: Sngap bha ia ki dak jingkhein ba la kren, nangta pynkynmaw da kaba kynton ia ki button.",
        "next_step": "Listen to spoken numbers and tap keys."
    },
    "word_recall": {
        "en": "Word Recall Game: Read or listen to traditional heritage words, then select the matching cultural meaning.",
        "hi": "शब्द स्मरण खेल: पारंपरिक शब्दों को पढ़ें या सुनें, फिर उनके सही सांस्कृतिक अर्थ का चयन करें।",
        "as": "শব্দ স্মৰণ খেল: পৰম্পৰাগত শব্দবোৰ পঢ়ক বা শুনক, তাৰ পিছত শুদ্ধ সাংস্কৃতিক অৰ্থ বাছি লওক।",
        "mzo": "Word Recall Infiamna: Tualchhung tawng thu awmzia te ngaithla la, a awmzia inhnim thlang rawh.",
        "kha": "Word Recall: Pule lane sngap ia ki kyntien thymmai, nangta jied ia ka jingmut kaba dei.",
        "next_step": "Select the correct traditional word meaning."
    },
    "picture_association": {
        "en": "Picture Association Game: Look at the traditional picture, then tap the symbol or story that matches its meaning.",
        "hi": "चित्र संगति खेल: पारंपरिक चित्र देखें, फिर उसके अर्थ से मेल खाने वाले प्रतीक पर टैप करें।",
        "as": "ছবি সংগতি খেল: পৰম্পৰাগত ছবিখন চাওক, তাৰ পিছত ইয়াৰ অৰ্থৰ সৈতে মিলা প্ৰতীকটো টিপক।",
        "mzo": "Picture Association Infiamna: Lem awm chu en la, a awmzia inhnim mil tak hmet rawh.",
        "kha": "Picture Association: Peit ia ka dur, nangta kynton ia u dak lane ka jingthoh kaba iadei.",
        "next_step": "Tap the matching picture story."
    },
    "caregiver_dashboard": {
        "en": "Caregiver Monitoring Dashboard: Review daily cognitive performance scores, domain breakdowns, and alert logs.",
        "hi": "केयरगिवर मॉनिटरिंग डैशबोर्ड: दैनिक संज्ञानात्मक स्कोर, गेम ब्रेकडाउन और अलर्ट लॉग देखें।",
        "as": "তত্ত্বাৱধানকাৰী নিৰীক্ষণ ডেচব'ৰ্ড: দৈনিক স্ক'ৰ, খেলৰ ভাগ আৰু সতৰ্কবাৰ্তা চাওক।",
        "mzo": "Enkawltu Enzuina Dashboard: Ni tin hriatrengna mark, infiamna thliah hrang leh hriattirnate en rawh.",
        "kha": "Caregiver Dashboard: Peit ia ki jingtynjuh jong ka sngi, ki rukom ialeh bad ki jingma.",
        "next_step": "Review cognitive domain charts and alert notes."
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
    "START_GAME": ["game", "play", "start", "खेल", "गेम", "শুরু", "খেল", "infiamna", "tan", "jingialeh", "sdang", "memory", "number", "word", "picture"],
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
            "en": "Let's start a new game! Choose Memory Match, Number Sequence, Word Recall, or Picture Association.",
            "hi": "चलिए एक नया गेम शुरू करते हैं! मेमोरी मैच, नंबर सीक्वेंस, वर्ड रिकॉल या पिक्चर एसोसिएशन चुनें।",
            "as": "ব'লক এটা নতুন খেল আৰম্ভ কৰোঁ! মেম'ৰী মেচ, নম্বৰ অনুক্ৰম, শব্দ স্মৰণ বা ছবি সংগতি বাছি লওক।",
            "mzo": "Infiamna thar i tan ang u! Memory Match, Number Sequence, Word Recall, a nih loh chuan Picture Association thlang rawh.",
            "kha": "Kha ngin sdang ia ka jingialeh thymmai! Jied Memory Match, Number Sequence, Word Recall, lane Picture Association.",
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
            "en": "Hello! I am your Smriti assistant. Which game would you like to play today?",
            "hi": "नमस्ते! मैं आपकी स्मृति मदद हूँ। आज आप कौन सा खेल खेलना चाहेंगे?",
            "as": "নমস্কাৰ! মই আপোনাৰ স্মৃতি সহায়ক। আজি আপুনি কোনটো খেল খেলিব বিচাৰিব?",
            "mzo": "Chibai! Smriti tanpuitu ka ni e. Vawiin hian eng infiamna nge i khelh duh ang?",
            "kha": "Khublei! Nga long u nongiarap Smriti. Kaei ka jingialeh ba phi kwah ban ialeh mynta?",
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
