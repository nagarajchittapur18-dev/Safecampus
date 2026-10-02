// SafeCampus AI — Phase 10 Location Service & Nearest Node Unit Tests
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:safecampus_ai/core/constants/fallback_campus_data.dart';
import 'package:safecampus_ai/models/campus_location.dart';
import 'package:safecampus_ai/providers/locations_provider.dart';
import 'package:safecampus_ai/providers/user_location_provider.dart';
import 'package:safecampus_ai/screens/home/home_screen.dart';
import 'package:safecampus_ai/screens/search/destination_search_screen.dart';
import 'package:safecampus_ai/services/location_service.dart';

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
  const locLibrary = CampusLocation(
    id: 7,
    name: 'Library',
    latitude: 12.9735,
    longitude: 77.5948,
    locationType: 'library',
    description: 'Central library',
  );
  const locCanteen = CampusLocation(
    id: 8,
    name: 'Canteen',
    latitude: 12.9722,
    longitude: 77.5956,
    locationType: 'canteen',
    description: 'Cafeteria',
  );

  final testLocations = [locMainGate, locAdmin, locLibrary, locCanteen];

  group('LocationService Math & Nearest Node Tests', () {
    test('calculateDistanceMeters computes reasonable distance between campus coordinates', () {
      // Main Gate (12.9716, 77.5946) to Admin Block (12.9720, 77.5950)
      final dist = LocationService.calculateDistanceMeters(12.9716, 77.5946, 12.9720, 77.5950);
      // Distance is approximately 63 metres
      expect(dist, inInclusiveRange(50.0, 75.0));

      // Same point distance is 0
      final zeroDist = LocationService.calculateDistanceMeters(12.9716, 77.5946, 12.9716, 77.5946);
      expect(zeroDist, closeTo(0.0, 0.001));
    });

    test('findNearestNode finds Main Gate when near entrance', () {
      // Near Main Gate with slight GPS drift (10 metres away)
      const userLat = 12.97165;
      const userLon = 77.59462;

      final nearest = LocationService.findNearestNode(userLat, userLon, testLocations);
      expect(nearest.id, equals(1));
      expect(nearest.name, equals('Main Gate'));
    });

    test('findNearestNode finds Library when in north academic area', () {
      // Near Library
      const userLat = 12.97348;
      const userLon = 77.59479;

      final nearest = LocationService.findNearestNode(userLat, userLon, testLocations);
      expect(nearest.id, equals(7));
      expect(nearest.name, equals('Library'));
    });

    test('findNearestNode finds Canteen when near cafeteria', () {
      // Near Canteen
      const userLat = 12.97218;
      const userLon = 77.59558;

      final nearest = LocationService.findNearestNode(userLat, userLon, testLocations);
      expect(nearest.id, equals(8));
      expect(nearest.name, equals('Canteen'));
    });

    test('findNearestNode works across all 20 campus nodes', () {
      // Near West Gate (12.9725, 77.5932)
      const userLat = 12.97251;
      const userLon = 77.59321;

      final nearest = LocationService.findNearestNode(
        userLat,
        userLon,
        FallbackCampusData.locations,
      );
      expect(nearest.id, equals(20));
      expect(nearest.name, equals('West Gate'));
    });
  });

  group('UserLocationState & Notifier Tests', () {
    test('UserLocationState initial state is clean and non-tracking', () {
      const state = UserLocationState();
      expect(state.hasLocation, isFalse);
      expect(state.isLoading, isFalse);
      expect(state.isUsingGpsSource, isFalse);
      expect(state.result, isNull);
    });

    test('UserLocationState copyWith preserves or updates values', () {
      const state = UserLocationState();
      final updated = state.copyWith(
        status: LocationServiceStatus.ready,
        isUsingGpsSource: true,
        result: const UserLocationResult(
          latitude: 12.9716,
          longitude: 77.5946,
          accuracy: 5.0,
          nearestNode: locMainGate,
          distanceToNodeM: 4.2,
        ),
      );

      expect(updated.hasLocation, isTrue);
      expect(updated.isUsingGpsSource, isTrue);
      expect(updated.result?.nearestNode.name, equals('Main Gate'));
    });

    test('UserLocationState clearGps resets location safely', () {
      const state = UserLocationState(
        status: LocationServiceStatus.ready,
        isUsingGpsSource: true,
        result: UserLocationResult(
          latitude: 12.9716,
          longitude: 77.5946,
          accuracy: 5.0,
          nearestNode: locMainGate,
          distanceToNodeM: 4.2,
        ),
      );

      final cleared = state.copyWith(
        status: LocationServiceStatus.initial,
        clearResult: true,
        isUsingGpsSource: false,
      );

      expect(cleared.hasLocation, isFalse);
      expect(cleared.result, isNull);
      expect(cleared.isUsingGpsSource, isFalse);
    });
  });

  group('Phase 10 UI Widget Integration Tests', () {
    testWidgets('HomeScreen renders Use Current Location button and manual fallback', (tester) async {
      await tester.binding.setSurfaceSize(const Size(800, 1100));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            locationsProvider.overrideWith((ref) => Future.value(testLocations)),
          ],
          child: const MaterialApp(
            home: HomeScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify "Use Current Location" button is visible
      expect(find.textContaining('Use Current Location'), findsOneWidget);
      expect(find.byIcon(Icons.my_location_rounded), findsWidgets);
    });

    testWidgets('HomeScreen displays GPS active badge when GPS origin is snapped', (tester) async {
      await tester.binding.setSurfaceSize(const Size(800, 1100));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      const gpsActiveState = UserLocationState(
        status: LocationServiceStatus.ready,
        isUsingGpsSource: true,
        result: UserLocationResult(
          latitude: 12.97165,
          longitude: 77.59462,
          accuracy: 4.5,
          nearestNode: locMainGate,
          distanceToNodeM: 6.0,
        ),
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            locationsProvider.overrideWith((ref) => Future.value(testLocations)),
            userLocationProvider.overrideWith((ref) => _MockUserLocationNotifier(gpsActiveState)),
          ],
          child: const MaterialApp(
            home: HomeScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify GPS active indicator is displayed
      expect(find.textContaining('GPS Origin: Near Main Gate'), findsOneWidget);
      expect(find.text('Manual Mode'), findsOneWidget);
    });

    testWidgets('DestinationSearchScreen shows Use Current Location when searching origin', (tester) async {
      await tester.binding.setSurfaceSize(const Size(800, 1000));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            locationsProvider.overrideWith((ref) => Future.value(testLocations)),
          ],
          child: const MaterialApp(
            home: DestinationSearchScreen(isOrigin: true),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify "Use Current Location" item is presented at the top of the search list
      expect(find.text('Use Current Location'), findsOneWidget);
      expect(find.text('Detect GPS & snap to nearest campus facility'), findsOneWidget);
    });

    testWidgets('DestinationSearchScreen does NOT show Current Location when searching destination', (tester) async {
      await tester.binding.setSurfaceSize(const Size(800, 1000));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            locationsProvider.overrideWith((ref) => Future.value(testLocations)),
          ],
          child: const MaterialApp(
            home: DestinationSearchScreen(isOrigin: false),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Destinations are specific facilities, not current location
      expect(find.text('Use Current Location'), findsNothing);
      expect(find.text('Main Gate'), findsOneWidget);
    });
  });
}

class _MockUserLocationNotifier extends StateNotifier<UserLocationState> implements UserLocationNotifier {
  _MockUserLocationNotifier(super.state);

  @override
  void clearGps() {
    state = state.copyWith(clearResult: true, isUsingGpsSource: false);
  }

  @override
  Future<({String message, CampusLocation? nearestNode, bool success})> detectLocationAndSnapSource({
    bool autoSetSource = true,
  }) async {
    return (
      success: true,
      message: 'Located near Main Gate',
      nearestNode: state.result?.nearestNode,
    );
  }

  @override
  void notifyManualSelection() {
    state = state.copyWith(isUsingGpsSource: false);
  }
}
