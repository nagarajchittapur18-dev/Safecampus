// SafeCampus AI — Route History Item Model
import 'route_recommendation.dart';

class RouteHistoryItem {
  final String id;
  final int sourceId;
  final int destinationId;
  final String sourceName;
  final String destinationName;
  final String preference;
  final double distanceM;
  final double travelTimeMin;
  final double safetyScore;
  final String crowdLevel;
  final DateTime timestamp;
  final RouteRecommendation recommendation;

  const RouteHistoryItem({
    required this.id,
    required this.sourceId,
    required this.destinationId,
    required this.sourceName,
    required this.destinationName,
    required this.preference,
    required this.distanceM,
    required this.travelTimeMin,
    required this.safetyScore,
    required this.crowdLevel,
    required this.timestamp,
    required this.recommendation,
  });

  factory RouteHistoryItem.fromRecommendation({
    required RouteRecommendation rec,
    required String sourceName,
    required String destinationName,
  }) {
    return RouteHistoryItem(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      sourceId: rec.sourceId,
      destinationId: rec.destinationId,
      sourceName: sourceName,
      destinationName: destinationName,
      preference: rec.preference,
      distanceM: rec.distanceM,
      travelTimeMin: rec.travelTimeMin,
      safetyScore: rec.safetyScore,
      crowdLevel: rec.crowdLevel,
      timestamp: DateTime.now(),
      recommendation: rec,
    );
  }

  factory RouteHistoryItem.fromJson(Map<String, dynamic> json) {
    return RouteHistoryItem(
      id: json['id'] as String,
      sourceId: json['source_id'] as int,
      destinationId: json['destination_id'] as int,
      sourceName: json['source_name'] as String,
      destinationName: json['destination_name'] as String,
      preference: json['preference'] as String,
      distanceM: (json['distance_m'] as num).toDouble(),
      travelTimeMin: (json['travel_time_min'] as num).toDouble(),
      safetyScore: (json['safety_score'] as num).toDouble(),
      crowdLevel: json['crowd_level'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      recommendation: RouteRecommendation.fromJson(json['recommendation'] as Map<String, dynamic>),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'source_id': sourceId,
        'destination_id': destinationId,
        'source_name': sourceName,
        'destination_name': destinationName,
        'preference': preference,
        'distance_m': distanceM,
        'travel_time_min': travelTimeMin,
        'safety_score': safetyScore,
        'crowd_level': crowdLevel,
        'timestamp': timestamp.toIso8601String(),
        'recommendation': recommendation.toJson(),
      };
}
