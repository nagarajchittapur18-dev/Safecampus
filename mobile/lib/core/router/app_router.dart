// SafeCampus AI — Complete App Router (GoRouter)
// Maps all 14 application screens seamlessly.
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../screens/auth/login_screen.dart';
import '../../screens/auth/register_screen.dart';
import '../../screens/explanation/route_explanation_screen.dart';
import '../../screens/heatmap/crowd_heatmap_screen.dart';
import '../../screens/history/route_history_screen.dart';
import '../../screens/home/home_screen.dart';
import '../../screens/map/campus_map_screen.dart';
import '../../screens/navigation/navigation_screen.dart';
import '../../screens/onboarding/onboarding_screen.dart';
import '../../screens/preferences/route_preferences_screen.dart';
import '../../screens/profile/profile_screen.dart';
import '../../screens/results/route_results_screen.dart';
import '../../screens/search/destination_search_screen.dart';
import '../../screens/splash/splash_screen.dart';

// ---------------------------------------------------------------------------
// Route Paths — Single Source of Truth
// ---------------------------------------------------------------------------
abstract class AppRoutes {
  static const splash = '/';
  static const onboarding = '/onboarding';
  static const login = '/login';
  static const register = '/register';
  static const home = '/home';
  static const map = '/map';
  static const search = '/search';
  static const preferences = '/preferences';
  static const results = '/results';
  static const navigation = '/navigation';
  static const explanation = '/explanation';
  static const crowd = '/crowd';
  static const history = '/history';
  static const profile = '/profile';
}

// ---------------------------------------------------------------------------
// Router Provider
// ---------------------------------------------------------------------------
final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: AppRoutes.splash,
    debugLogDiagnostics: false,
    routes: [
      // 1. Splash
      GoRoute(
        path: AppRoutes.splash,
        builder: (context, state) => const SplashScreen(),
      ),

      // 2. Onboarding
      GoRoute(
        path: AppRoutes.onboarding,
        builder: (context, state) => const OnboardingScreen(),
      ),

      // 3. Login
      GoRoute(
        path: AppRoutes.login,
        builder: (context, state) => const LoginScreen(),
      ),

      // 4. Register
      GoRoute(
        path: AppRoutes.register,
        builder: (context, state) => const RegisterScreen(),
      ),

      // 5. Home
      GoRoute(
        path: AppRoutes.home,
        builder: (context, state) => const HomeScreen(),
      ),

      // 6. Campus Map
      GoRoute(
        path: AppRoutes.map,
        builder: (context, state) => const CampusMapScreen(),
      ),

      // 7. Destination Search
      GoRoute(
        path: AppRoutes.search,
        builder: (context, state) {
          final isOrigin = state.uri.queryParameters['isOrigin'] == 'true';
          return DestinationSearchScreen(isOrigin: isOrigin);
        },
      ),

      // 8. Route Preferences & Weights
      GoRoute(
        path: AppRoutes.preferences,
        builder: (context, state) => const RoutePreferencesScreen(),
      ),

      // 9. Route Results
      GoRoute(
        path: AppRoutes.results,
        builder: (context, state) => const RouteResultsScreen(),
      ),

      // 10. Navigation Guidance
      GoRoute(
        path: AppRoutes.navigation,
        builder: (context, state) => const NavigationScreen(),
      ),

      // 11. Route Explanation (Trade-off breakdown)
      GoRoute(
        path: AppRoutes.explanation,
        builder: (context, state) => const RouteExplanationScreen(),
      ),

      // 12. Crowd Heatmap
      GoRoute(
        path: AppRoutes.crowd,
        builder: (context, state) => const CrowdHeatmapScreen(),
      ),

      // 13. Route History
      GoRoute(
        path: AppRoutes.history,
        builder: (context, state) => const RouteHistoryScreen(),
      ),

      // 14. Profile & Accessibility Settings
      GoRoute(
        path: AppRoutes.profile,
        builder: (context, state) => const ProfileScreen(),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      appBar: AppBar(title: const Text('Navigation Error')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline_rounded, size: 48, color: Colors.red),
            const SizedBox(height: 12),
            Text('Route not found: ${state.uri}'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => context.go(AppRoutes.home),
              child: const Text('Go Home'),
            ),
          ],
        ),
      ),
    ),
  );
});
