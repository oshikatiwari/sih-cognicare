import 'package:flutter/material.dart';
import '../l10n/language_picker_widget.dart';
import '../voice/voice_button_widget.dart';
import '../voice/stt_service.dart';
import '../voice/tts_service.dart';
import '../main.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _currentLang = 'en';
  late TTSService _ttsService;
  late STTService _sttService;
  bool _isListening = false;
  bool _isSpeaking = false;
  String _voicePromptText = "Welcome to Smriti! Tap green button or mic.";

  @override
  void initState() {
    super.initState();
    _ttsService = TTSService();
    _sttService = STTService();
    _loadVoiceGuidance();
  }

  void _loadVoiceGuidance() async {
    final result = await _sttService.fetchScreenGuidance(
      screenId: 'home',
      languageCode: _currentLang,
      patientId: 'demo-patient-01',
    );

    setState(() {
      _voicePromptText = result['spoken_guidance'] ?? "Welcome to Smriti!";
    });

    _ttsService.speak(_voicePromptText, langCode: _currentLang);
  }

  void _openLanguagePicker() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => LanguagePickerWidget(
        currentLangCode: _currentLang,
        onLanguageChanged: (selectedLang) {
          setState(() {
            _currentLang = selectedLang;
          });
          SmritiApp.setLocale(context, Locale(selectedLang));
          _loadVoiceGuidance();
        },
      ),
    );
  }

  void _handleMicTap() async {
    setState(() {
      _isListening = true;
    });

    // Simulate speech-to-text recognition & backend AI voice intent call
    final result = await _sttService.sendVoiceQuery(
      patientId: 'demo-patient-01',
      spokenPhrase: _currentLang == 'hi' ? 'मेरा आज का स्कोर क्या है?' : 'How am I doing today?',
      languageCode: _currentLang,
    );

    setState(() {
      _isListening = false;
      _isSpeaking = true;
      _voicePromptText = result['response_text'] ?? "You are doing great!";
    });

    await _ttsService.speak(_voicePromptText, langCode: _currentLang);

    setState(() {
      _isSpeaking = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF2D6A4F),
        elevation: 0,
        title: Row(
          children: [
            const Icon(Icons.psychology, color: Colors.white, size: 28),
            const SizedBox(width: 8),
            const Text(
              "Smriti (स्मृति)",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 22, color: Colors.white),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.language, color: Colors.white, size: 28),
            onPressed: _openLanguagePicker,
            tooltip: "Change Language",
          ),
          IconButton(
            icon: const Icon(Icons.bluetooth_audio, color: Colors.lightGreenAccent, size: 28),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("Bluetooth Speaker Connected for clear audio")),
              );
            },
            tooltip: "Bluetooth Speaker Connected",
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Voice Guidance Card
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: const Color(0xFFE8F5E9),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFF52B788), width: 1.5),
              ),
              child: Row(
                children: [
                  const Icon(Icons.volume_up, color: Color(0xFF2D6A4F), size: 36),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Text(
                      _voicePromptText,
                      style: const TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF1B4332),
                        height: 1.3,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            const Text(
              "Daily Activities",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF1B4332)),
            ),
            const SizedBox(height: 14),

            // Large Elderly-Friendly Activity Buttons
            _buildActivityButton(
              title: "Memory Matching",
              subtitle: "Flip cards to find familiar matching pairs",
              icon: Icons.style,
              color: const Color(0xFF2D6A4F),
              onTap: () => Navigator.pushNamed(context, '/game/memory'),
            ),
            const SizedBox(height: 14),

            _buildActivityButton(
              title: "Pattern Recognition",
              subtitle: "Complete sequences of traditional patterns",
              icon: Icons.extension,
              color: const Color(0xFF40916C),
              onTap: () => Navigator.pushNamed(context, '/game/pattern'),
            ),
            const SizedBox(height: 14),

            _buildActivityButton(
              title: "Object Recognition",
              subtitle: "Identify North Eastern regional tools & items",
              icon: Icons.category,
              color: const Color(0xFF52B788),
              onTap: () => Navigator.pushNamed(context, '/game/object'),
            ),
            const SizedBox(height: 14),

            _buildActivityButton(
              title: "Reminders & Medication",
              subtitle: "Check daily care schedule & water intake",
              icon: Icons.medication,
              color: const Color(0xFF1B4332),
              onTap: () => Navigator.pushNamed(context, '/reminders'),
            ),
            const SizedBox(height: 24),

            // Mic Assistant Button
            Center(
              child: VoiceButtonWidget(
                onTap: _handleMicTap,
                isListening: _isListening,
                isSpeaking: _isSpeaking,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActivityButton({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Icon(icon, color: color, size: 36),
              ),
              const SizedBox(width: 18),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: color),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: TextStyle(fontSize: 14, color: Colors.grey[700]),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.arrow_forward_ios, color: Colors.grey, size: 20),
            ],
          ),
        ),
      ),
    );
  }
}
