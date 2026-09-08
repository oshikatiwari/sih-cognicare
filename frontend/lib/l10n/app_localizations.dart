import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// AppLocalizations handles dynamic 5-language localization loading
/// (English, Hindi, Assamese, Mizo, Khasi) for Mrunaala's Multilingual Module.
class AppLocalizations {
  final Locale locale;
  late Map<String, String> _localizedStrings;

  AppLocalizations(this.locale);

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  Future<bool> load() async {
    String langCode = locale.languageCode;
    if (!['en', 'hi', 'as', 'mzo', 'kha'].contains(langCode)) {
      langCode = 'en';
    }

    String jsonString =
        await rootBundle.loadString('assets/lang/$langCode.json');
    Map<String, dynamic> jsonMap = json.decode(jsonString);

    _localizedStrings = jsonMap.map((key, value) {
      return MapEntry(key, value.toString());
    });

    return true;
  }

  String translate(String key) {
    return _localizedStrings[key] ?? key;
  }
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['en', 'hi', 'as', 'mzo', 'kha'].contains(locale.languageCode);
  }

  @override
  Future<AppLocalizations> load(Locale locale) async {
    AppLocalizations localizations = AppLocalizations(locale);
    await localizations.load();
    return localizations;
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}
