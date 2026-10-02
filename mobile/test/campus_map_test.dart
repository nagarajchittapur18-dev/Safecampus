// SafeCampus AI — Phase 9 Campus Map Tests
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:safecampus_ai/models/campus_location.dart';
import 'package:safecampus_ai/models/route_recommendation.dart';
import 'package:safecampus_ai/providers/locations_provider.dart';
import 'package:safecampus_ai/providers/route_provider.dart';
import 'package:safecampus_ai/screens/map/campus_map_screen.dart';

void main() {
  const locMainGate = CampusLocation(
    id: 1,
    name: 'Main Gate',
    latitude: 12.9716,
    longitude: 77.5946,
    locationType: 'gate',
    description: 'Primary entrance',
  );
  const locAdmin = CampusLocation(
    id: 2,
    name: 'Admin Block',
    latitude: 12.9720,
    longitude: 77.5950,
    locationType: 'building',
    description: 'Administrative building',
  );
  const locCanteen = CampusLocation(
    id: 8,
    name: 'Canteen',
    latitude: 12.9722,
    longitude: 77.5956,
    locationType: 'canteen',
    description: 'Cafeteria',
  );

  const testLocations = [locMainGate, locAdmin, locCanteen];

  const testRecommendation = RouteRecommendation(
    sourceId: 1,
    destinationId: 8,
    preference: 'balanced',
    weights: {'wD': 0.2, 'wT': 0.2, 'wC': 0.2, 'wS': 0.2, 'wA': 0.2},
    route: [1, 2, 8],
    routeNames: ['Main Gate', 'Admin Block', 'Canteen'],
    distanceM: 260.0,
    travelTimeMin: 3.25,
    crowdScore: 0.35,
    crowdLevel: 'LOW',
    safetyScore: 0.90,
    accessibilityScore: 1.0,
    totalCost: 0.45,
    executionTimeMs: 0.42,
    algorithm: 'personalized_multi_objective_a_star',
    usedMlCrowd: true,
    alternatives: [
      AlternativeRoute(
        label: 'Shortest Path',
        preference: 'shortest',
        route: [1, 2, 8],
        routeNames: ['Main Gate', 'Admin Block', 'Canteen'],
        distanceM: 260.0,
        travelTimeMin: 3.25,
        crowdScore: 0.35,
        crowdLevel: 'LOW',
        safetyScore: 0.90,
        accessibilityScore: 1.0,
        totalCost: 0.45,
      ),
      AlternativeRoute(
        label: 'Safest Route',
        preference: 'safest',
        route: [1, 2, 8],
        routeNames: ['Main Gate', 'Admin Block', 'Canteen'],
        distanceM: 310.0,
        travelTimeMin: 3.80,
        crowdScore: 0.20,
        crowdLevel: 'LOW',
        safetyScore: 0.98,
        accessibilityScore: 0.95,
        totalCost: 0.38,
      ),
    ],
  );

  Widget createTestWidget({RouteState? initialRouteState}) {
    return ProviderScope(
      overrides: [
        locationsProvider.overrideWith((ref) => Future.value(testLocations)),
        if (initialRouteState != null)
          routeProvider.overrideWith(
            (ref) => _MockRouteNotifier(initialRouteState),
          ),
      ],
      child: const MaterialApp(
        home: CampusMapScreen(),
      ),
    );
  }

  group('CampusMapScreen Tests (Phase 9 OpenStreetMap Integration)', () {
    testWidgets('CampusMapScreen renders FlutterMap, controls and attribution', (tester) async {
      await tester.binding.setSurfaceSize(const Size(800, 1000));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Verify Screen Title and Map Widget
      expect(find.text('Campus Map'), findsOneWidget);
      expect(find.byType(FlutterMap), findsOneWidget);

      // Verify Attribution disclaimer (OpenStreetMap Zero-Cost & Simulated Crowd)
      expect(find.textContaining('OpenStreetMap'), findsOneWidget);
      expect(find.textContaining('Simulated Crowd'), findsOneWidget);

      // Verify Zoom and Navigation FABs
      expect(find.byIcon(Icons.add_rounded), findsOneWidget);
      expect(find.byIcon(Icons.remove_rounded), findsOneWidget);
      expect(find.byIcon(Icons.my_location_rounded), findsOneWidget);
      expect(find.text('Find Route'), findsOneWidget);
    });

    testWidgets('Offline schematic grid mode toggles and renders successfully', (tester) async {
      await tester.binding.setSurfaceSize(const Size(800, 1000));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Tap Offline Grid toggle button in App Bar
      final gridToggle = find.byTooltip('Switch to Schematic Grid (Offline Mode)');
      expect(gridToggle, findsOneWidget);
      await tester.tap(gridToggle);
      await tester.pumpAndSettle();

      // Verify Offline Schematic banner appears
      expect(find.textContaining('Schematic Grid View (Offline Compatible'), findsOneWidget);
    });

    testWidgets('Renders START and DEST marker tags when route is set', (tester) async {
      await tester.binding.setSurfaceSize(const Size(800, 1000));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      const stateWithEndpoints = RouteState(
        source: locMainGate,
        destination: locCanteen,
        recommendation: AsyncData(testRecommendation),
      );

      await tester.pumpWidget(createTestWidget(initialRouteState: stateWithEndpoints));
      await tester.pumpAndSettle();

      // Verify START and DEST badge tags are rendered
      expect(find.text('START'), findsOneWidget);
      expect(find.text('DEST'), findsOneWidget);

      // Verify Active Route Summary Card
      expect(find.textContaining('Main Gate → Canteen'), findsOneWidget);
      expect(find.textContaining('260m'), findsAtLeastNWidgets(1));

      // Verify Route Selector Filter Chips
      expect(find.textContaining('Recommended'), findsOneWidget);
      expect(find.textContaining('Shortest Path'), findsOneWidget);
      expect(find.textContaining('Safest Route'), findsOneWidget);
    });

    testWidgets('Tapping campus directory opens offline searchable location list', (tester) async {
      await tester.binding.setSurfaceSize(const Size(800, 1000));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Tap Directory button
      final dirBtn = find.byIcon(Icons.list_alt_rounded);
      expect(dirBtn, findsOneWidget);
      await tester.tap(dirBtn);
      await tester.pumpAndSettle();

      // Directory bottom sheet is open with locations
      expect(find.textContaining('Campus Directory'), findsOneWidget);
      expect(find.text('Main Gate'), findsOneWidget);
      expect(find.text('Admin Block'), findsOneWidget);
      expect(find.text('Canteen'), findsOneWidget);
    });
  });
}

class _MockRouteNotifier extends StateNotifier<RouteState> implements RouteNotifier {
  _MockRouteNotifier(super.state);

  @override
  void selectRouteIndex(int index) {
    state = state.copyWith(selectedRouteIndex: index);
  }

  @override
  void setSource(CampusLocation loc) {
    state = state.copyWith(source: loc);
  }

  @override
  void setDestination(CampusLocation loc) {
    state = state.copyWith(destination: loc);
  }

  @override
  void swapLocations() {}

  @override
  void setPreference(String pref) {}

  @override
  void setCustomWeights(Map<String, double> weights) {}

  @override
  void setSimulationHour(int? hour) {}

  @override
  void setEventFlag(int flag) {}

  @override
  void setClassActivity(int? flag) {}

  @override
  void setExamFlag(int flag) {}

  @override
  void setUseMlCrowd(bool use) {}

  @override
  void setNavigationIndex(int index) {}

  @override
  void nextNavigationStep() {}

  @override
  void previousNavigationStep() {}

  @override
  Future<RouteRecommendation?> findBestRoute() async => state.recommendation.valueOrNull;
}
