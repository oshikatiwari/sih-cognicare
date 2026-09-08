import 'package:flutter/material.dart';

/// VoiceButtonWidget renders an elderly-accessible glowing microphone button
/// supporting tap-to-talk voice interactions in Smriti.
class VoiceButtonWidget extends StatefulWidget {
  final VoidCallback onTap;
  final bool isListening;
  final bool isSpeaking;

  const VoiceButtonWidget({
    Key? key,
    required this.onTap,
    this.isListening = false,
    this.isSpeaking = false,
  }) : super(key: key);

  @override
  State<VoiceButtonWidget> createState() => _VoiceButtonWidgetState();
}

class _VoiceButtonWidgetState extends State<VoiceButtonWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Color buttonColor = const Color(0xFF2D6A4F);
    IconData iconData = Icons.mic;
    String statusLabel = "Tap to Talk to Smriti";

    if (widget.isListening) {
      buttonColor = Colors.orange;
      iconData = Icons.graphic_eq;
      statusLabel = "Listening...";
    } else if (widget.isSpeaking) {
      buttonColor = Colors.blue;
      iconData = Icons.volume_up;
      statusLabel = "Smriti is Speaking...";
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        GestureDetector(
          onTap: widget.onTap,
          child: AnimatedBuilder(
            animation: _animController,
            builder: (context, child) {
              final scale = (widget.isListening || widget.isSpeaking)
                  ? 1.0 + (_animController.value * 0.15)
                  : 1.0;
              return Transform.scale(
                scale: scale,
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: buttonColor,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: buttonColor.withOpacity(0.4),
                        blurRadius: 18,
                        spreadRadius: 4,
                      )
                    ],
                  ),
                  child: Icon(
                    iconData,
                    color: Colors.white,
                    size: 40,
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 8),
        Text(
          statusLabel,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: buttonColor,
          ),
        ),
      ],
    );
  }
}
