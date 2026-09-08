import 'package:flutter_tts/flutter_tts.dart';

/// TTSService manages Text-to-Speech audio playback for elderly patients across 5 languages
/// (English, Hindi, Assamese, Mizo, Khasi) with Bluetooth speaker support.
class TTSService {
  late FlutterTts _flutterTts;
  bool isSpeaking = false;

  TTSService() {
    _flutterTts = FlutterTts();
    _initTts();
  }

  void _initTts() async {
    await _flutterTts.setSpeechRate(0.42); // Slower rate for elderly dementia patients
    await _flutterTts.setVolume(1.0);       // Maximum volume for clear hearing
    await _flutterTts.setPitch(1.0);

    _flutterTts.setStartHandler(() {
      isSpeaking = true;
    });

    _flutterTts.setCompletionHandler(() {
      isSpeaking = false;
    });

    _flutterTts.setErrorHandler((msg) {
      isSpeaking = false;
    });
  }

  /// Speaks prompt aloud in the requested language
  Future<void> speak(String text, {String langCode = 'en'}) async {
    if (text.isEmpty) return;

    String ttsLang;
    switch (langCode.toLowerCase()) {
      case 'hi':
        ttsLang = 'hi-IN';
        break;
      case 'as':
        ttsLang = 'bn-IN'; // Fallback to Bengali/Assamese phonetic engine
        break;
      case 'mzo':
      case 'kha':
      case 'en':
      default:
        ttsLang = 'en-IN';
        break;
    }

    await _flutterTts.setLanguage(ttsLang);
    await _flutterTts.speak(text);
  }

  /// Stops current audio playback
  Future<void> stop() async {
    await _flutterTts.stop();
    isSpeaking = false;
  }
}
