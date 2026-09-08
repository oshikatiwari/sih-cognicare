import 'package:flutter/material.dart';

class RemindersScreen extends StatefulWidget {
  const RemindersScreen({Key? key}) : super(key: key);

  @override
  State<RemindersScreen> createState() => _RemindersScreenState();
}

class _RemindersScreenState extends State<RemindersScreen> {
  final List<Map<String, dynamic>> _reminders = [
    {
      'title': 'Morning Memory Support Pill',
      'subtitle': 'Take 1 tablet after breakfast with water',
      'time': '08:30 AM',
      'type': 'medication',
      'completed': true,
    },
    {
      'title': 'Hydration Reminder',
      'subtitle': 'Drink 250ml of warm water',
      'time': '02:00 PM',
      'type': 'hydration',
      'completed': true,
    },
    {
      'title': 'Cognitive Game Session',
      'subtitle': 'Play Memory Matching for 10 minutes',
      'time': '05:00 PM',
      'type': 'game',
      'completed': false,
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Reminders & Schedule"),
        backgroundColor: const Color(0xFF2D6A4F),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Safe-Zone Location Chip
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFE8F5E9),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF52B788)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.location_on, color: Color(0xFF2D6A4F), size: 32),
                  SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "GPS Safe-Zone Status",
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF1B4332)),
                        ),
                        SizedBox(height: 2),
                        Text(
                          "In Safe-Zone (45m from home perimeter)",
                          style: TextStyle(fontSize: 14, color: Color(0xFF2D6A4F)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            const Text(
              "Today's Care Schedule",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF1B4332)),
            ),
            const SizedBox(height: 14),

            ..._reminders.asMap().entries.map((entry) {
              int idx = entry.key;
              Map<String, dynamic> rem = entry.value;
              bool isCompleted = rem['completed'];

              return Padding(
                padding: const EdgeInsets.only(bottom: 14),
                child: Card(
                  elevation: 2,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 10),
                    leading: Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: isCompleted ? Colors.green[100] : Colors.amber[100],
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        isCompleted ? Icons.check_circle : Icons.schedule,
                        color: isCompleted ? Colors.green[800] : Colors.amber[900],
                        size: 28,
                      ),
                    ),
                    title: Text(
                      rem['title'],
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        decoration: isCompleted ? TextDecoration.lineThrough : null,
                      ),
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 4),
                        Text(rem['subtitle']),
                        const SizedBox(height: 4),
                        Text(
                          "Time: ${rem['time']}",
                          style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF2D6A4F)),
                        ),
                      ],
                    ),
                    trailing: Checkbox(
                      value: isCompleted,
                      activeColor: const Color(0xFF2D6A4F),
                      onChanged: (val) {
                        setState(() {
                          _reminders[idx]['completed'] = val;
                        });
                      },
                    ),
                  ),
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }
}
