import 'dart:async';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class MemoryGameScreen extends StatefulWidget {
  const MemoryGameScreen({Key? key}) : super(key: key);

  @override
  State<MemoryGameScreen> createState() => _MemoryGameScreenState();
}

class _MemoryGameScreenState extends State<MemoryGameScreen> {
  final List<String> _cardIcons = [
    '☕', '☕', '🌸', '🌸', '🦏', '🦏', '🎋', '🎋', '🪘', '🪘', '🛖', '🛖'
  ];

  late List<bool> _cardFlipped;
  late List<bool> _cardMatched;
  int? _previousIndex;
  bool _busy = false;

  int _attempts = 0;
  int _matchesFound = 0;
  int _errors = 0;
  final Stopwatch _stopwatch = Stopwatch();

  @override
  void initState() {
    super.initState();
    _cardIcons.shuffle();
    _cardFlipped = List.generate(_cardIcons.length, (_) => false);
    _cardMatched = List.generate(_cardIcons.length, (_) => false);
    _stopwatch.start();
  }

  void _onCardTap(int index) {
    if (_busy || _cardFlipped[index] || _cardMatched[index]) return;

    setState(() {
      _cardFlipped[index] = true;
    });

    if (_previousIndex == null) {
      _previousIndex = index;
    } else {
      _attempts++;
      _busy = true;
      int prev = _previousIndex!;
      _previousIndex = null;

      if (_cardIcons[prev] == _cardIcons[index]) {
        // Match found!
        setState(() {
          _cardMatched[prev] = true;
          _cardMatched[index] = true;
          _matchesFound++;
          _busy = false;
        });

        if (_matchesFound == _cardIcons.length ~/ 2) {
          _stopwatch.stop();
          _submitGameResult();
        }
      } else {
        // Wrong match
        _errors++;
        Timer(const Duration(milliseconds: 900), () {
          setState(() {
            _cardFlipped[prev] = false;
            _cardFlipped[index] = false;
            _busy = false;
          });
        });
      }
    }
  }

  Future<void> _submitGameResult() async {
    final responseTimeMs = _stopwatch.elapsedMilliseconds.toDouble();
    final accuracy = ((_cardIcons.length ~/ 2) / (_attempts > 0 ? _attempts : 1) * 100).clamp(0.0, 100.0);

    try {
      final res = await http.post(
        Uri.parse('http://10.0.2.2:8000/analysis/cps'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'session_id': 'sess-memory-${DateTime.now().millisecondsSinceEpoch}',
          'patient_id': 'demo-patient-01',
          'accuracy': accuracy,
          'response_time': responseTimeMs,
          'completion_rate': 100.0,
          'attempts': _attempts,
          'errors': _errors,
          'hints_used': 0,
          'is_memory_game': true,
          'memory_specific_accuracy': accuracy,
        }),
      );

      Map<String, dynamic> result = {};
      if (res.statusCode == 200) {
        result = json.decode(res.body);
      }

      _showResultDialog(accuracy, result);
    } catch (_) {
      _showResultDialog(accuracy, {'cps': 85.0, 'display_label': 'Gentle Challenge'});
    }
  }

  void _showResultDialog(double accuracy, Map<String, dynamic> apiResult) {
    final cps = apiResult['cps'] ?? 85.0;
    final displayLabel = apiResult['display_label'] ?? 'Gentle Challenge';

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        title: const Row(
          children: [
            Icon(Icons.stars, color: Colors.amber, size: 36),
            SizedBox(width: 10),
            Text("Activity Completed!"),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Accuracy: ${accuracy.toStringAsFixed(1)}%", style: const TextStyle(fontSize: 18)),
            const SizedBox(height: 8),
            Text("Cognitive Score: $cps", style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF2D6A4F))),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: const Color(0xFFE8F5E9),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                "Next Level: $displayLabel",
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1B4332)),
              ),
            ),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF2D6A4F),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: const Text("Return Home", style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Memory Matching"),
        backgroundColor: const Color(0xFF2D6A4F),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                Text("Matches: $_matchesFound / 6", style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                Text("Attempts: $_attempts", style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 20),
            Expanded(
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                ),
                itemCount: _cardIcons.length,
                itemBuilder: (context, index) {
                  final isRevealed = _cardFlipped[index] || _cardMatched[index];
                  return GestureDetector(
                    onTap: () => _onCardTap(index),
                    child: Container(
                      decoration: BoxDecoration(
                        color: isRevealed ? Colors.white : const Color(0xFF2D6A4F),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: const Color(0xFF52B788), width: 2),
                      ),
                      child: Center(
                        child: Text(
                          isRevealed ? _cardIcons[index] : '❓',
                          style: const TextStyle(fontSize: 36),
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
