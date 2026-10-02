// SafeCampus AI — Explanation Engine Unit & Widget Tests (Phase 11)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:safecampus_ai/core/constants/fallback_campus_data.dart';
import 'package:safecampus_ai/models/route_recommendation.dart';
import 'package:safecampus_ai/providers/locations_provider.dart';
import 'package:safecampus_ai/providers/route_provider.dart';
import 'package:safecampus_ai/screens/explanation/route_explanation_screen.dart';
import 'package:safecampus_ai/services/explanation_engine.dart';

void main() {
  group('RouteExplanationEngine Unit Tests', () {
    const mockRecommendation = RouteRecommendation(
      sourceId: 1,
      destinationId: 8,
      preference: 'least_crowded',
      weights: {'wD': 0.1, 'wT': 0.1, 'wC': 0.5, 'wS': 0.2, 'wA': 0.1},
      route: [1, 2, 3, 6, 4, 9, 8],
      routeNames: ['Main Gate', 'Admin', 'Library', 'Fountain', 'CSE', 'ECE', 'Canteen'],
      distanceM: 520.0,
      travelTimeMin: 6.2,
      crowdScore: 0.18,
      crowdLevel: 'LOW',
      safetyScore: 0.92,
      accessibilityScore: 0.85,
      totalCost: 0.28,
      executionTimeMs: 1.4,
      algorithm: 'personalized_multi_objective_a_star',
      usedMlCrowd: true,
      alternatives: [
        AlternativeRoute(
          label: 'Shortest Path',
          preference: 'shortest',
          route: [1, 16, 17, 4, 9, 8],
          routeNames: ['Main Gate', 'Security', 'Alley', 'CSE', 'ECE', 'Canteen'],
          distanceM: 480.0,
          travelTimeMin: 5.8,
          crowdScore: 0.65,
          crowdLevel: 'HIGH',
          safetyScore: 0.72,
          accessibilityScore: 0.60,
          totalCost: 0.45,
        ),
      ],
    );

    final mockDijkstraBaseline = {
      'route': [1, 16, 17, 4, 9, 8],
      'route_names': ['Main Gate', 'Security', 'Alley', 'CSE', 'ECE', 'Canteen'],
      'distance_m': 480.0,
      'travel_time_min': 5.8,
      'crowd_score': 0.65,
      'crowd_level': 'HIGH',
      'safety_score': 0.72,
      'accessibility_score': 0.60,
    };

    test('generates dynamic explanation with actual differences against shortest route', () {
      final exp = RouteExplanationEngine.generate(
        recommendation: mockRecommendation,
        dijkstraBaseline: mockDijkstraBaseline,
      );

      expect(exp.shortestBaseline.distanceM, equals(480.0));
      expect(exp.tradeoffs['distance']['difference'], equals(40.0)); // 520 - 480
      expect(exp.tradeoffs['distance']['percentage_difference'], closeTo(8.33, 0.1));

      expect(exp.tradeoffs['travel_time']['difference'], closeTo(0.4, 0.05)); // 6.2 - 5.8
      expect(exp.tradeoffs['safety']['difference'], closeTo(0.20, 0.05)); // 0.92 - 0.72
      expect(exp.tradeoffs['crowd']['difference'], closeTo(-0.47, 0.05)); // 0.18 - 0.65 (reduced!)
      expect(exp.tradeoffs['accessibility']['difference'], closeTo(0.25, 0.05)); // 0.85 - 0.60
    });

    test('fulfills required dynamic summary phrasing when crowd is low and safety is high', () {
      final exp = RouteExplanationEngine.generate(
        recommendation: mockRecommendation,
        dijkstraBaseline: mockDijkstraBaseline,
      );

      // Example requirement from prompt:
      // "Recommended because predicted crowd is low and the route has a high safety score."
      expect(exp.summary, equals('Recommended because predicted crowd is low and the route has a high safety score.'));
    });

    test('dynamic trade-off text contains calculated numbers without hardcoding', () {
      final exp = RouteExplanationEngine.generate(
        recommendation: mockRecommendation,
        dijkstraBaseline: mockDijkstraBaseline,
      );

      expect(exp.distanceTradeoff, contains('40m'));
      expect(exp.distanceTradeoff, contains('480m'));
      expect(exp.safetyTradeoff, contains('92%'));
      expect(exp.crowdTradeoff, contains('LOW'));
      expect(exp.accessibilityTradeoff, contains('85%'));
    });

    test('generateForAlternative produces dynamic explanation for selected candidate', () {
      final baseExp = RouteExplanationEngine.generate(
        recommendation: mockRecommendation,
        dijkstraBaseline: mockDijkstraBaseline,
      );

      final altExp = RouteExplanationEngine.generateForAlternative(
        alternative: mockRecommendation.alternatives.first,
        weights: mockRecommendation.weights,
        baseline: baseExp.shortestBaseline,
      );

      // Alternative is the shortest path itself (480m)
      expect(altExp.tradeoffs['distance']['difference'], closeTo(0.0, 0.01));
      expect(altExp.distanceTradeoff, contains('0m detour'));
    });

    test('RouteRecommendation JSON deserialization handles populated explanation', () {
      final jsonMap = {
        'source_id': 1,
        'destination_id': 8,
        'preference': 'least_crowded',
        'weights': {'wD': 0.1, 'wT': 0.1, 'wC': 0.5, 'wS': 0.2, 'wA': 0.1},
        'route': [1, 2, 8],
        'route_names': ['Main Gate', 'Admin', 'Canteen'],
        'distance_m': 300.0,
        'travel_time_min': 3.5,
        'crowd_score': 0.2,
        'crowd_level': 'LOW',
        'safety_score': 0.9,
        'accessibility_score': 0.8,
        'total_cost': 0.25,
        'execution_time_ms': 1.1,
        'algorithm': 'personalized_multi_objective_a_star',
        'used_ml_crowd': true,
        'explanation': {
          'summary': 'Recommended because predicted crowd is low and the route has a high safety score.',
          'why_selected': 'Optimal least-crowded path.',
          'distance_tradeoff': 'Adds 20m (+7.1%) over shortest path.',
          'time_tradeoff': 'Equivalent walking time.',
          'crowd_tradeoff': 'Reduces crowd congestion by 40%.',
          'safety_tradeoff': 'Improves safety by +12%.',
          'accessibility_tradeoff': 'Step-free ramp corridor.',
          'reasons': ['Reason 1', 'Reason 2'],
          'tradeoffs': {
            'distance': {'difference': 20.0, 'percentage_difference': 7.1},
          },
          'shortest_baseline': {
            'route': [1, 8],
            'route_names': ['Main Gate', 'Canteen'],
            'distance_m': 280.0,
            'travel_time_min': 3.3,
            'crowd_score': 0.5,
            'crowd_level': 'MEDIUM',
            'safety_score': 0.8,
            'accessibility_score': 0.8,
          },
        },
      };

      final rec = RouteRecommendation.fromJson(jsonMap);
      expect(rec.explanation, isNotNull);
      expect(rec.explanation!.summary, equals('Recommended because predicted crowd is low and the route has a high safety score.'));
      expect(rec.explanation!.shortestBaseline.distanceM, equals(280.0));
      expect(rec.explanation!.distanceTradeoff, contains('20m'));
    });
  });

  group('RouteExplanationScreen Widget Tests', () {
    testWidgets('renders empty state when no recommendation exists', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            locationsProvider.overrideWith((ref) => Future.value(FallbackCampusData.locations)),
          ],
          child: const MaterialApp(
            home: RouteExplanationScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('No Route Recommended Yet'), findsOneWidget);
      expect(find.text('Find a Route'), findsOneWidget);
    });

    testWidgets('renders full dynamic explanation screen when route is available', (tester) async {
      const mockRec = RouteRecommendation(
        sourceId: 1,
        destinationId: 8,
        preference: 'least_crowded',
        weights: {'wD': 0.1, 'wT': 0.1, 'wC': 0.5, 'wS': 0.2, 'wA': 0.1},
        route: [1, 2, 3, 6, 4, 9, 8],
        routeNames: ['Main Gate', 'Admin', 'Library', 'Fountain', 'CSE', 'ECE', 'Canteen'],
        distanceM: 520.0,
        travelTimeMin: 6.2,
        crowdScore: 0.18,
        crowdLevel: 'LOW',
        safetyScore: 0.92,
        accessibilityScore: 0.85,
        totalCost: 0.28,
        executionTimeMs: 1.4,
        algorithm: 'personalized_multi_objective_a_star',
        usedMlCrowd: true,
        alternatives: [
          AlternativeRoute(
            label: 'Shortest Path',
            preference: 'shortest',
            route: [1, 16, 17, 4, 9, 8],
            routeNames: ['Main Gate', 'Security', 'Alley', 'CSE', 'ECE', 'Canteen'],
            distanceM: 480.0,
            travelTimeMin: 5.8,
            crowdScore: 0.65,
            crowdLevel: 'HIGH',
            safetyScore: 0.72,
            accessibilityScore: 0.60,
            totalCost: 0.45,
          ),
        ],
      );

      final mockBaseline = {
        'route': [1, 16, 17, 4, 9, 8],
        'route_names': ['Main Gate', 'Security', 'Alley', 'CSE', 'ECE', 'Canteen'],
        'distance_m': 480.0,
        'travel_time_min': 5.8,
        'crowd_score': 0.65,
        'crowd_level': 'HIGH',
        'safety_score': 0.72,
        'accessibility_score': 0.60,
      };

      final container = ProviderContainer(
        overrides: [
          locationsProvider.overrideWith((ref) => Future.value(FallbackCampusData.locations)),
        ],
      );
      addTearDown(container.dispose);
      final loc1 = FallbackCampusData.locations[0]; // Main Gate (1)
      final loc2 = FallbackCampusData.locations[7]; // Canteen (8)

      // Set state directly
      final notifier = container.read(routeProvider.notifier);
      notifier.setSource(loc1);
      notifier.setDestination(loc2);
      notifier.state = notifier.state.copyWith(
        recommendation: const AsyncData(mockRec),
        dijkstraBaseline: mockBaseline,
      );

      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: container,
          child: const MaterialApp(
            home: RouteExplanationScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify Screen Title
      expect(find.text('Why This Route?'), findsOneWidget);

      // Verify AI Recommendation Rationale card
      expect(find.text('AI RECOMMENDATION RATIONALE'), findsOneWidget);

      // Verify Trade-Off section header
      expect(find.text('Quantified Trade-Offs vs Shortest Path'), findsOneWidget);

      // Verify 5 Factor Trade-Off Cards
      expect(find.text('Distance Trade-Off'), findsOneWidget);
      expect(find.text('Walking Time Trade-Off'), findsOneWidget);
      expect(find.text('Crowd Density Trade-Off'), findsOneWidget);
      expect(find.text('Safety Level Trade-Off'), findsOneWidget);
      expect(find.text('Accessibility Trade-Off'), findsOneWidget);

      // Verify Objective Comparison Matrix
      expect(find.text('Objective Trade-Off Matrix'), findsOneWidget);
      expect(find.text('Distance'), findsOneWidget);
      expect(find.text('Walking Time'), findsOneWidget);
      expect(find.text('Safety Level'), findsOneWidget);

      // Verify Weight Vector Distribution
      expect(find.textContaining('Weight Vector Distribution'), findsOneWidget);
      expect(find.textContaining('wD + wT + wC + wS + wA = 1.00'), findsOneWidget);

      // Verify Pareto-Optimal Verification callout
      expect(find.textContaining('Pareto-Optimal Verification'), findsOneWidget);

      // Verify Navigation action buttons
      expect(find.text('View on Map'), findsOneWidget);
      expect(find.text('Start Navigation'), findsOneWidget);
    });
  });
}
