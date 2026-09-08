import 'dart:convert';
import 'package:http/http.dart' as http;

/// STTService handles Speech-to-Text conversion and connects mic queries
/// directly to the backend AI Intent Engine.
class STTService {
  final String backendUrl;

  STTService({this.backendUrl = 'http://10.0.2.2:8000'});

  /// Sends recognized voice text to backend POST /voice/intent endpoint
  Future<Map<String, dynamic>> sendVoiceQuery({
    required String patientId,
    required String spokenPhrase,
    String? languageCode,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$backendUrl/voice/intent'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'patient_id': patientId,
          'spoken_phrase': spokenPhrase,
          'lang': languageCode,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'detected_intent': 'UNKNOWN',
          'response_text': 'Could not connect to voice service.',
          'action': {'route': '/home'}
        };
      }
    } catch (e) {
      return {
        'detected_intent': 'OFFLINE',
        'response_text': 'Working offline. Tap the green button to start your game.',
        'action': {'route': '/home'}
      };
    }
  }

  /// Fetches step-by-step spoken guidance for elderly patients entering a screen
  Future<Map<String, dynamic>> fetchScreenGuidance({
    required String screenId,
    required String languageCode,
    required String patientId,
  }) async {
    try {
      final uri = Uri.parse(
        '$backendUrl/analysis/voice-guidance/$screenId?lang=$languageCode&patient_id=$patientId',
      );
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (_) {}

    return {
      'spoken_guidance': 'Welcome to Smriti. Tap the green button to play.',
      'next_step_instruction': 'Tap green button.'
    };
  }
}
