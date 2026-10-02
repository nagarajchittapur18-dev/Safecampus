// SafeCampus AI — Flutter Models Unit Tests
import 'package:flutter_test/flutter_test.dart';
import 'package:safecampus_ai/models/campus_location.dart';
import 'package:safecampus_ai/models/crowd_prediction.dart';
import 'package:safecampus_ai/models/route_history_item.dart';
import 'package:safecampus_ai/models/route_recommendation.dart';
import 'package:safecampus_ai/models/user_model.dart';

void main() {
  group('CampusLocation Model Tests', () {
    test('CampusLocation deserializes from JSON correctly', () {
      final json = {
        'id': 1,
        'name': 'Main Gate',
        'latitude': 12.9716,
        'longitude': 77.5946,
        'location_type': 'gate',
        'description': 'Primary campus entrance',
        'is_active': true,
      };

      final loc = CampusLocation.fromJson(json);
      expect(loc.id, equals(1));
      expect(loc.name, equals('Main Gate'));
      expect(loc.latitude, equals(12.9716));
      expect(loc.longitude, equals(77.5946));
      expect(loc.locationType, equals('gate'));
      expect(loc.description, equals('Primary campus entrance'));
      expect(loc.isActive, isTrue);

      final outJson = loc.toJson();
      expect(outJson['name'], equals('Main Gate'));
      expect(outJson['id'], equals(1));
    });
  });

  group('RouteRecommendation Model Tests', () {
    test('RouteRecommendation deserializes from API JSON with metrics', () {
      final json = {
        'source_id': 1,
        'destination_id': 8,
        'preference': 'safest',
        'weights': {'wD': 0.1, 'wT': 0.05, 'wC': 0.05, 'wS': 0.7, 'wA': 0.1},
        'route': [1, 16, 17, 8],
        'route_names': ['Main Gate', 'Parking Lot', 'Corridor C', 'Canteen'],
        'distance_m': 300.0,
        'travel_time_min': 3.73,
        'crowd_score': 0.5965,
        'crowd_level': 'HIGH',
        'safety_score': 0.82,
        'accessibility_score': 0.8667,
        'total_cost': 0.7117,
        'execution_time_ms': 0.313,
        'algorithm': 'personalized_multi_objective_a_star',
        'used_ml_crowd': true,
        'model_name': 'GradientBoostingClassifier',
      };

      final rec = RouteRecommendation.fromJson(json);
      expect(rec.sourceId, equals(1));
      expect(rec.destinationId, equals(8));
      expect(rec.preference, equals('safest'));
      expect(rec.route.length, equals(4));
      expect(rec.routeNames.first, equals('Main Gate'));
      expect(rec.routeNames.last, equals('Canteen'));
      expect(rec.distanceM, equals(300.0));
      expect(rec.travelTimeMin, closeTo(3.73, 0.01));
      expect(rec.crowdScore, closeTo(0.5965, 0.001));
      expect(rec.crowdLevel, equals('HIGH'));
      expect(rec.safetyScore, equals(0.82));
      expect(rec.accessibilityScore, closeTo(0.8667, 0.001));
      expect(rec.totalCost, closeTo(0.7117, 0.001));
      expect(rec.usedMlCrowd, isTrue);
      expect(rec.modelName, equals('GradientBoostingClassifier'));
      expect(rec.alternatives, isEmpty);
    });

    test('RouteRecommendation deserializes with alternative routes', () {
      final json = {
        'source_id': 1,
        'destination_id': 8,
        'preference': 'balanced',
        'weights': {'wD': 0.2, 'wT': 0.2, 'wC': 0.2, 'wS': 0.2, 'wA': 0.2},
        'route': [1, 2, 8],
        'route_names': ['Main Gate', 'Admin Block', 'Canteen'],
        'distance_m': 260.0,
        'travel_time_min': 3.25,
        'crowd_score': 0.35,
        'crowd_level': 'LOW',
        'safety_score': 0.90,
        'accessibility_score': 1.0,
        'total_cost': 0.45,
        'execution_time_ms': 0.42,
        'algorithm': 'personalized_multi_objective_a_star',
        'used_ml_crowd': true,
        'alternatives': [
          {
            'label': 'Shortest Path',
            'preference': 'shortest',
            'route': [1, 2, 8],
            'route_names': ['Main Gate', 'Admin Block', 'Canteen'],
            'distance_m': 260.0,
            'travel_time_min': 3.25,
            'crowd_score': 0.35,
            'crowd_level': 'LOW',
            'safety_score': 0.90,
            'accessibility_score': 1.0,
            'total_cost': 0.45,
          },
          {
            'label': 'Safest Route',
            'preference': 'safest',
            'route': [1, 16, 11, 20, 8],
            'route_names': ['Main Gate', 'Parking', 'Auditorium', 'West Gate', 'Canteen'],
            'distance_m': 340.0,
            'travel_time_min': 4.10,
            'crowd_score': 0.22,
            'crowd_level': 'LOW',
            'safety_score': 0.96,
            'accessibility_score': 0.95,
            'total_cost': 0.38,
          },
        ],
      };

      final rec = RouteRecommendation.fromJson(json);
      expect(rec.alternatives.length, equals(2));
      expect(rec.alternatives[0].label, equals('Shortest Path'));
      expect(rec.alternatives[0].distanceM, equals(260.0));
      expect(rec.alternatives[1].label, equals('Safest Route'));
      expect(rec.alternatives[1].safetyScore, equals(0.96));
      expect(rec.alternatives[1].route.length, equals(5));

      final outJson = rec.toJson();
      expect((outJson['alternatives'] as List).length, equals(2));
    });
  });

  group('CrowdPrediction Model Tests', () {
    test('CrowdPrediction parses numeric and string crowd levels', () {
      final json = {
        'location_id': 4,
        'location_name': 'Central Library',
        'predicted_crowd_level': 'MEDIUM',
        'predicted_crowd_score': 0.45,
        'confidence': 0.94,
        'model_name': 'GradientBoostingClassifier',
        'features_used': {'hour': 14, 'day_of_week': 2},
      };

      final pred = CrowdPrediction.fromJson(json);
      expect(pred.locationId, equals(4));
      expect(pred.locationName, equals('Central Library'));
      expect(pred.predictedCrowdLevel, equals('MEDIUM'));
      expect(pred.predictedCrowdScore, equals(0.45));
      expect(pred.confidence, equals(0.94));
    });
  });

  group('UserModel Tests', () {
    test('UserModel guest default and copyWith mobility preferences', () {
      final guest = UserModel.guest();
      expect(guest.id, equals(0));
      expect(guest.role, equals('visitor'));
      expect(guest.preferRamps, isFalse);

      final updated = guest.copyWith(preferRamps: true, avoidStairs: true);
      expect(updated.preferRamps, isTrue);
      expect(updated.avoidStairs, isTrue);
      expect(updated.role, equals('visitor'));
    });
  });

  group('RouteHistoryItem Tests', () {
    test('Creates RouteHistoryItem from RouteRecommendation', () {
      const rec = RouteRecommendation(
        sourceId: 1,
        destinationId: 8,
        preference: 'balanced',
        weights: {'wD': 0.2, 'wT': 0.2, 'wC': 0.2, 'wS': 0.2, 'wA': 0.2},
        route: [1, 8],
        routeNames: ['Main Gate', 'Canteen'],
        distanceM: 250.0,
        travelTimeMin: 3.1,
        crowdScore: 0.35,
        crowdLevel: 'LOW',
        safetyScore: 0.85,
        accessibilityScore: 0.9,
        totalCost: 0.55,
        executionTimeMs: 0.25,
        algorithm: 'personalized_multi_objective_a_star',
        usedMlCrowd: true,
      );

      final item = RouteHistoryItem.fromRecommendation(
        rec: rec,
        sourceName: 'Main Gate',
        destinationName: 'Canteen',
      );

      expect(item.sourceId, equals(1));
      expect(item.destinationId, equals(8));
      expect(item.sourceName, equals('Main Gate'));
      expect(item.destinationName, equals('Canteen'));
      expect(item.preference, equals('balanced'));

      final json = item.toJson();
      final restored = RouteHistoryItem.fromJson(json);
      expect(restored.sourceName, equals('Main Gate'));
      expect(restored.destinationName, equals('Canteen'));
    });
  });
}
