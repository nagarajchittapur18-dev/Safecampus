// SafeCampus AI — End-to-End Primary Flow Integration Test
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:safecampus_ai/core/constants/app_constants.dart';
import 'package:safecampus_ai/models/campus_location.dart';
import 'package:safecampus_ai/models/route_recommendation.dart';
import 'package:safecampus_ai/providers/history_provider.dart';
import 'package:safecampus_ai/providers/locations_provider.dart';
import 'package:safecampus_ai/providers/route_provider.dart';
import 'package:safecampus_ai/services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class MockApiService extends ApiService {
  @override
  Future<bool> checkHealth() async => true;

  @override
  Future<List<CampusLocation>> getLocations() async {
    return const [
      CampusLocation(id: 1, name: 'Main Gate', latitude: 12.9716, longitude: 77.5946, locationType: 'gate'),
      CampusLocation(id: 8, name: 'Canteen', latitude: 12.9730, longitude: 77.5960, locationType: 'canteen'),
      CampusLocation(id: 16, name: 'Parking Lot', latitude: 12.9718, longitude: 77.5942, locationType: 'outdoor'),
      CampusLocation(id: 17, name: 'Corridor C', latitude: 12.9725, longitude: 77.5955, locationType: 'corridor'),
    ];
  }

  @override
  Future<RouteRecommendation> recommendRoute({
    required int sourceId,
    required int destinationId,
    String preference = 'balanced',
    Map<String, double>? weights,
    int? hour,
    int? dayOfWeek,
    int eventFlag = 0,
    int? classActivity,
    int examFlag = 0,
    int holidayFlag = 0,
    bool useMlCrowd = true,
  }) async {
    return RouteRecommendation(
      sourceId: sourceId,
      destinationId: destinationId,
      preference: preference,
      weights: {'wD': 0.1, 'wT': 0.05, 'wC': 0.05, 'wS': 0.7, 'wA': 0.1},
      route: [1, 16, 17, 8],
      routeNames: ['Main Gate', 'Parking Lot', 'Corridor C', 'Canteen'],
      distanceM: 300.0,
      travelTimeMin: 3.73,
      crowdScore: 0.5965,
      crowdLevel: 'HIGH',
      safetyScore: 0.82,
      accessibilityScore: 0.8667,
      totalCost: 0.7117,
      executionTimeMs: 0.313,
      algorithm: 'personalized_multi_objective_a_star',
      usedMlCrowd: useMlCrowd,
      modelName: 'GradientBoostingClassifier',
    );
  }

  @override
  Future<Map<String, dynamic>> getDijkstraRoute({
    required int sourceId,
    required int destinationId,
  }) async {
    return {
      'route': [1, 2, 3, 8],
      'distance_m': 285.0,
      'travel_time_min': 3.56,
    };
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('Primary User Flow End-to-End Test', () {
    test('Executes Home → From → To → Preference → Find Route → Results → History', () async {
      final container = ProviderContainer(
        overrides: [
          apiServiceProvider.overrideWithValue(MockApiService()),
        ],
      );
      addTearDown(container.dispose);

      // 1. Fetch campus locations
      final locations = await container.read(locationsProvider.future);
      expect(locations.length, equals(4));

      final origin = locations.firstWhere((l) => l.id == 1);
      final dest = locations.firstWhere((l) => l.id == 8);

      // 2. Select From (Origin) and To (Destination) on RouteProvider
      final notifier = container.read(routeProvider.notifier);
      notifier.setSource(origin);
      notifier.setDestination(dest);

      expect(container.read(routeProvider).source?.id, equals(1));
      expect(container.read(routeProvider).destination?.id, equals(8));

      // 3. Select Preference: Safest
      notifier.setPreference(AppConstants.prefSafest);
      expect(container.read(routeProvider).preference, equals(AppConstants.prefSafest));

      // 4. Trigger Find Best Route
      final rec = await notifier.findBestRoute();
      expect(rec, isNotNull);

      // 5. Verify Recommended Route properties
      expect(rec!.sourceId, equals(1));
      expect(rec.destinationId, equals(8));
      expect(rec.preference, equals(AppConstants.prefSafest));
      expect(rec.route, equals([1, 16, 17, 8]));
      expect(rec.routeNames, equals(['Main Gate', 'Parking Lot', 'Corridor C', 'Canteen']));
      expect(rec.distanceM, equals(300.0));
      expect(rec.safetyScore, equals(0.82));
      expect(rec.usedMlCrowd, isTrue);
      expect(rec.modelName, equals('GradientBoostingClassifier'));

      // 6. Verify Dijkstra trade-off baseline is captured
      final dijkstra = container.read(routeProvider).dijkstraBaseline;
      expect(dijkstra, isNotNull);
      expect(dijkstra!['distance_m'], equals(285.0));

      // 7. Verify Route History was automatically stored
      await Future.delayed(const Duration(milliseconds: 50));
      final history = container.read(historyProvider);
      expect(history.length, equals(1));
      expect(history.first.sourceName, equals('Main Gate'));
      expect(history.first.destinationName, equals('Canteen'));
      expect(history.first.preference, equals('safest'));
    });
  });
}
