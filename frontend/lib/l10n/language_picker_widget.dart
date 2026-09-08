import 'package:flutter/material.dart';

/// LanguagePickerWidget renders a Duolingo-style language selector modal
/// allowing elderly users or caregivers to switch between English, Hindi, Assamese, Mizo, and Khasi.
class LanguagePickerWidget extends StatelessWidget {
  final String currentLangCode;
  final Function(String selectedLangCode) onLanguageChanged;

  const LanguagePickerWidget({
    Key? key,
    required this.currentLangCode,
    required this.onLanguageChanged,
  }) : super(key: key);

  static const List<Map<String, String>> languages = [
    {'code': 'en', 'name': 'English', 'native': 'English', 'flag': '🇬🇧'},
    {'code': 'hi', 'name': 'Hindi', 'native': 'हिन्दी', 'flag': '🇮🇳'},
    {'code': 'as', 'name': 'Assamese', 'native': 'অসমীয়া', 'flag': '🌾'},
    {'code': 'mzo', 'name': 'Mizo', 'native': 'Mizo ṭawng', 'flag': '🏔️'},
    {'code': 'kha', 'name': 'Khasi', 'native': 'Ka Ktien Khasi', 'flag': '🌲'},
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 45,
            height: 5,
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(10),
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            "Choose Language / भाषा चुनें",
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1B4332),
            ),
          ),
          const SizedBox(height: 16),
          ...languages.map((lang) {
            final isSelected = currentLangCode == lang['code'];
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: ListTile(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(
                    color: isSelected ? const Color(0xFF2D6A4F) : Colors.grey[300]!,
                    width: isSelected ? 2 : 1,
                  ),
                ),
                tileColor: isSelected ? const Color(0xFFE8F5E9) : Colors.white,
                leading: Text(
                  lang['flag']!,
                  style: const TextStyle(fontSize: 28),
                ),
                title: Text(
                  lang['native']!,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    color: const Color(0xFF1B4332),
                  ),
                ),
                subtitle: Text(lang['name']!),
                trailing: isSelected
                    ? const Icon(Icons.check_circle, color: Color(0xFF2D6A4F), size: 28)
                    : null,
                onTap: () {
                  onLanguageChanged(lang['code']!);
                  Navigator.pop(context);
                },
              ),
            );
          }).toList(),
        ],
      ),
    );
  }
}
