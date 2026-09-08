import 'package:flutter/material.dart';

class PatternGameScreen extends StatefulWidget {
  const PatternGameScreen({Key? key}) : super(key: key);

  @override
  State<PatternGameScreen> createState() => _PatternGameScreenState();
}

class _PatternGameScreenState extends State<PatternGameScreen> {
  final List<String> _sequence = ['🔴', '🔵', '🔴', '🔵', '❓'];
  final List<String> _options = ['🔴', '🔵', '🟢', '🟡'];
  String? _selectedOption;

  void _checkAnswer(String option) {
    setState(() {
      _selectedOption = option;
    });

    final isCorrect = option == '🔴';
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Text(isCorrect ? "Correct Pattern!" : "Try Again"),
        content: Text(isCorrect ? "Great job completing the sequence." : "Look closely at the repeating pattern."),
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
        title: const Text("Pattern Recognition"),
        backgroundColor: const Color(0xFF2D6A4F),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Complete the Pattern Sequence:",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF1B4332)),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: _sequence
                  .map((item) => Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFF52B788), width: 2),
                        ),
                        child: Text(item, style: const TextStyle(fontSize: 32)),
                      ))
                  .toList(),
            ),
            const SizedBox(height: 40),
            const Text(
              "Which symbol comes next?",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 20),
            GridView.builder(
              shrinkWrap: true,
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: _options.length,
              itemBuilder: (context, index) {
                return ElevatedButton(
                  onPressed: () => _checkAnswer(_options[index]),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    side: const BorderSide(color: Color(0xFF2D6A4F), width: 2),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                  ),
                  child: Text(_options[index], style: const TextStyle(fontSize: 40)),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
