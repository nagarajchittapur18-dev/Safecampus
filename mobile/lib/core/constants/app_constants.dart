// SafeCampus AI — App Constants & Configuration
import 'package:flutter/foundation.dart';

abstract class AppConstants {
  // Dynamic host: supports --dart-define=API_URL=https://... for production cloud deployments
  static String get baseUrl {
    const envUrl = String.fromEnvironment('API_URL');
    if (envUrl.isNotEmpty) {
      return envUrl.endsWith('/') ? envUrl.substring(0, envUrl.length - 1) : envUrl;
    }
    if (kIsWeb) return 'http://127.0.0.1:8000';
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return 'http://10.0.2.2:8000';
      default:
        return 'http://127.0.0.1:8000';
    }
  }

  static const String apiVersion = '/api';
  static String get apiBaseUrl => '$baseUrl$apiVersion';

  // App Metadata
  static const String appName = 'SafeCampus AI';
  static const String appTagline = 'Smart, Safe & Accessible Campus Navigation';
  static const String appVersion = '1.0.0';
  static const String academicCitation =
      'A Multi-Objective AI-Based Personalized Safe Route Recommendation Framework for Smart Campus Navigation';

  // Campus Default Geo Coordinates (Bangalore Campus Placeholder)
  static const double campusCenterLat = 12.9720;
  static const double campusCenterLon = 77.5950;
  static const double defaultZoom = 17.5;

  // Preference Presets
  static const String prefBalanced = 'balanced';
  static const String prefSafest = 'safest';
  static const String prefFastest = 'fastest';
  static const String prefShortest = 'shortest';
  static const String prefLeastCrowded = 'least_crowded';
  static const String prefAccessible = 'accessible';

  static const List<String> preferences = [
    prefBalanced,
    prefSafest,
    prefFastest,
    prefShortest,
    prefLeastCrowded,
    prefAccessible,
  ];

  static const Map<String, String> preferenceLabels = {
    prefBalanced: 'Balanced',
    prefSafest: 'Safest',
    prefFastest: 'Fastest',
    prefShortest: 'Shortest',
    prefLeastCrowded: 'Least Crowded',
    prefAccessible: 'Wheelchair / Accessible',
  };

  static const Map<String, String> preferenceDescriptions = {
    prefBalanced: 'Equal balance of distance, travel time, safety & crowd density.',
    prefSafest: 'Prioritizes well-lit corridors, active surveillance & secure pathways.',
    prefFastest: 'Optimized for minimum travel time, accounting for congestion.',
    prefShortest: 'Pure shortest physical distance path.',
    prefLeastCrowded: 'Steers away from high-traffic cafeterias, gates & choke points.',
    prefAccessible: 'Guarantees step-free, ramp-equipped, wheelchair-friendly paths.',
  };
}
