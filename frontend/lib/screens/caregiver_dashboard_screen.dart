import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class CaregiverDashboardScreen extends StatefulWidget {
  const CaregiverDashboardScreen({Key? key}) : super(key: key);

  @override
  State<CaregiverDashboardScreen> createState() => _CaregiverDashboardScreenState();
}

class _CaregiverDashboardScreenState extends State<CaregiverDashboardScreen> {
  String _selectedPatientId = 'demo-patient-12';
  List<dynamic> _scores = [];
  String? _alertMessage = "Noticeable change in recent activity patterns — a gentle check-in or caregiver review is recommended.";
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchPatientTrend();
  }

  void _fetchPatientTrend() async {
    setState(() {
      _loading = true;
    });

    try {
      final response = await http.get(
        Uri.parse('http://10.0.2.2:8000/analysis/trend/$_selectedPatientId'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _scores = data['scores'] ?? [];
          _alertMessage = data['alert'];
          _loading = false;
        });
      }
    } catch (_) {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Caregiver Overview"),
        backgroundColor: const Color(0xFF1B4332),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Patient Selector Dropdown
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Row(
                  children: [
                    const Icon(Icons.person_pin, color: Color(0xFF2D6A4F), size: 32),
                    const SizedBox(width: 12),
                    const Text("Select Patient:", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    const SizedBox(width: 12),
                    Expanded(
                      child: DropdownButton<String>(
                        value: _selectedPatientId,
                        isExpanded: true,
                        underline: const SizedBox(),
                        items: const [
                          DropdownMenuItem(value: 'demo-patient-01', child: Text("Aarav Sharma (Improving)")),
                          DropdownMenuItem(value: 'demo-patient-12', child: Text("Kamala Devi (Alert Triggered)")),
                        ],
                        onChanged: (val) {
                          if (val != null) {
                            setState(() {
                              _selectedPatientId = val;
                            });
                            _fetchPatientTrend();
                          }
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Anomaly Alert Banner
            if (_alertMessage != null)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.amber[50],
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: Colors.amber[800]!, width: 1.5),
                ),
                child: Row(
                  children: [
                    Icon(Icons.warning_amber, color: Colors.amber[900], size: 36),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Caregiver Support Notice",
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.amber[900]),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _alertMessage!,
                            style: const TextStyle(fontSize: 14, color: Colors.black87),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            const SizedBox(height: 24),

            const Text(
              "Cognitive Engagement Score (CPS) History",
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF1B4332)),
            ),
            const SizedBox(height: 14),

            // Score History List / Chart summary
            _loading
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _scores.length,
                    itemBuilder: (context, idx) {
                      final item = _scores[idx];
                      final cps = item['cps'] ?? 80.0;
                      return Card(
                        margin: const EdgeInsets.only(bottom: 10),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: cps >= 75 ? const Color(0xFF2D6A4F) : Colors.orange,
                            child: Text(
                              "${cps.toInt()}",
                              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                            ),
                          ),
                          title: Text("Session #${idx + 1} — Score: $cps"),
                          subtitle: Text("Timestamp: ${item['timestamp']?.toString().split('T')[0]}"),
                        ),
                      );
                    },
                  ),
          ],
        ),
      ),
    );
  }
}
