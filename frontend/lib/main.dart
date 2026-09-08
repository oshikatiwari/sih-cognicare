import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'l10n/app_localizations.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';
import 'screens/reminders_screen.dart';
import 'screens/caregiver_dashboard_screen.dart';
import 'games/memory_game_screen.dart';
import 'games/pattern_game_screen.dart';
import 'games/object_game_screen.dart';

void main() {
  runApp(const SmritiApp());
}

class SmritiApp extends StatefulWidget {
  const SmritiApp({Key? key}) : super(key: key);

  static void setLocale(BuildContext context, Locale newLocale) {
    _SmritiAppState? state = context.findAncestorStateOfType<_SmritiAppState>();
    state?.setLocale(newLocale);
  }

  @override
  State<SmritiApp> createState() => _SmritiAppState();
}

class _SmritiAppState extends State<SmritiApp> {
  Locale _locale = const Locale('en');

  void setLocale(Locale locale) {
    setState(() {
      _locale = locale;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smriti (स्मृति)',
      debugShowCheckedModeBanner: false,
      locale: _locale,
      supportedLocales: const [
        Locale('en'),
        Locale('hi'),
        Locale('as'),
        Locale('mzo'),
        Locale('kha'),
      ],
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      theme: ThemeData(
        primaryColor: const Color(0xFF2D6A4F),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2D6A4F),
          primary: const Color(0xFF2D6A4F),
          secondary: const Color(0xFF52B788),
          surface: const Color(0xFFF8F9FA),
        ),
        scaffoldBackgroundColor: const Color(0xFFF4F6F4),
        fontFamily: 'Roboto',
        textTheme: const TextTheme(
          displayLarge: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFF1B4332)),
          titleLarge: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF1B4332)),
          bodyLarge: TextStyle(fontSize: 18, color: Color(0xFF2D6A4F)),
        ),
      ),
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginScreen(),
        '/home': (context) => const HomeScreen(),
        '/reminders': (context) => const RemindersScreen(),
        '/caregiver': (context) => const CaregiverDashboardScreen(),
        '/game/memory': (context) => const MemoryGameScreen(),
        '/game/pattern': (context) => const PatternGameScreen(),
        '/game/object': (context) => const ObjectGameScreen(),
      },
    );
  }
}
