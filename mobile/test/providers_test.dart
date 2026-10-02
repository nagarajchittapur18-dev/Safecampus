// SafeCampus AI — Providers & State Logic Unit Tests
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:safecampus_ai/core/constants/app_constants.dart';
import 'package:safecampus_ai/models/campus_location.dart';
import 'package:safecampus_ai/models/route_recommendation.dart';
import 'package:safecampus_ai/providers/route_provider.dart';

void main() {
  group('RouteState & RouteNotifier Tests', () {
    const loc1 = CampusLocation(
      id: 1,
      name: 'Main Gate',
      latitude: 12.9716,
      longitude: 77.5946,
      locationType: 'gate',
    );

    const loc8 = CampusLocation(
      id: 8,
      name: 'Canteen',
      latitude: 12.9730,
      longitude: 77.5960,
      locationType: 'canteen',
    );

    test('Initial RouteState has balanced preference and null locations', () {
      const state = RouteState();
      expect(state.preference, equals(AppConstants.prefBalanced));
      expect(state.source, isNull);
      expect(state.destination, isNull);
      expect(state.useMlCrowd, isTrue);
      expect(state.navigationIndex, equals(0));
    });

    test('Location swap swaps source and destination', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final notifier = container.read(routeProvider.notifier);
      notifier.setSource(loc1);
      notifier.setDestination(loc8);

      expect(container.read(routeProvider).source?.id, equals(1));
      expect(container.read(routeProvider).destination?.id, equals(8));

      notifier.swapLocations();
      expect(container.read(routeProvider).source?.id, equals(8));
      expect(container.read(routeProvider).destination?.id, equals(1));
    });

    test('Setting preference resets custom weights', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final notifier = container.read(routeProvider.notifier);
      notifier.setCustomWeights({'wD': 0.5, 'wT': 0.5, 'wC': 0.0, 'wS': 0.0, 'wA': 0.0});
      expect(container.read(routeProvider).customWeights, isNotNull);

      notifier.setPreference(AppConstants.prefSafest);
      expect(container.read(routeProvider).preference, equals(AppConstants.prefSafest));
      expect(container.read(routeProvider).customWeights, isNull);
    });

    test('Simulated navigation advances step by step', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final notifier = container.read(routeProvider.notifier);

      const mockRec = RouteRecommendation(
        sourceId: 1,
        destinationId: 8,
        preference: 'safest',
        weights: {},
        route: [1, 16, 17, 8],
        routeNames: ['Main Gate', 'Parking Lot', 'Corridor C', 'Canteen'],
        distanceM: 300,
        travelTimeMin: 3.7,
        crowdScore: 0.5,
        crowdLevel: 'MEDIUM',
        safetyScore: 0.85,
        accessibilityScore: 0.9,
        totalCost: 0.7,
        executionTimeMs: 0.3,
        algorithm: 'personalized_multi_objective_a_star',
        usedMlCrowd: true,
      );

      // Set mock recommendation directly on state
      notifier.state = notifier.state.copyWith(recommendation: const AsyncData(mockRec));

      expect(container.read(routeProvider).navigationIndex, equals(0));

      notifier.nextNavigationStep();
      expect(container.read(routeProvider).navigationIndex, equals(1));

      notifier.nextNavigationStep();
      expect(container.read(routeProvider).navigationIndex, equals(2));

      notifier.nextNavigationStep();
      expect(container.read(routeProvider).navigationIndex, equals(3));

      // Should not advance beyond last step
      notifier.nextNavigationStep();
      expect(container.read(routeProvider).navigationIndex, equals(3));

      notifier.previousNavigationStep();
      expect(container.read(routeProvider).navigationIndex, equals(2));
    });
  });
}
