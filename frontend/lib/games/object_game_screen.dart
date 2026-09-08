import 'package:flutter/material.dart';

class ObjectGameScreen extends StatefulWidget {
  const ObjectGameScreen({Key? key}) : super(key: key);

  @override
  State<ObjectGameScreen> createState() => _ObjectGameScreenState();
}

class _ObjectGameScreenState extends State<ObjectGameScreen> {
  final String _currentObjectIcon = '🛖'; // Traditional Assamese/NE Hut
  final String _correctName = 'Traditional House (Ghar)';
  final List<String> _options = [
    'Traditional House (Ghar)',
    'Bamboo Basket (Kholi)',
    'Tea Pot (Cha Pot)',
    'Hand Loom (Taat)'
  ];

  void _checkAnswer(String option) {
    final isCorrect = option == _correctName;
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Text(isCorrect ? "Correct Identification!" : "Try Again"),
        content: Text(isCorrect ? "You correctly identified the traditional structure." : "Think about traditional North Eastern regional homes."),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              if (isCorrect) Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2D6A4F)),
            child: const Text("Continue", style: TextStyle(color: Colors.white)),
          )
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Object Recognition"),
        backgroundColor: const Color(0xFF2D6A4F),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Identify the Regional Object:",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF1B4332)),
            ),
            const SizedBox(height: 24),
            Center(
              child: Container(
                width: 150,
                height: 150,
                decoration: BoxDecoration(
                  color: const Color(0xFFE8F5E9),
                  shape: BoxShape.circle,
                  border: Border.all(color: const Color(0xFF52B788), width: 3),
                ),
                child: Center(
                  child: Text(_currentObjectIcon, style: const TextStyle(fontSize: 80)),
                ),
              ),
            ),
            const SizedBox(height: 32),
            const Text(
              "Select the correct item name below:",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 16),
            ..._options.map((opt) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: ElevatedButton(
                    onPressed: () => _checkAnswer(opt),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: const Color(0xFF1B4332),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      side: const BorderSide(color: Color(0xFF2D6A4F), width: 1.5),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    ),
                    child: Text(opt, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  ),
                )),
          ],
        ),
      ),
    );
  }
}
