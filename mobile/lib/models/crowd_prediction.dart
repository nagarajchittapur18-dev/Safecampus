// SafeCampus AI — Crowd Prediction Model
class CrowdPrediction {
  final int locationId;
  final String locationName;
  final String predictedCrowdLevel;
  final double predictedCrowdScore;
  final double confidence;
  final String modelName;
  final Map<String, dynamic> featuresUsed;

  const CrowdPrediction({
    required this.locationId,
    required this.locationName,
    required this.predictedCrowdLevel,
    required this.predictedCrowdScore,
    required this.confidence,
    required this.modelName,
    required this.featuresUsed,
  });

  factory CrowdPrediction.fromJson(Map<String, dynamic> json) {
    final rawLevel = json['predicted_crowd_level'];
    String levelStr;
    if (rawLevel is int) {
      const levels = ['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'];
      levelStr = rawLevel >= 0 && rawLevel < levels.length ? levels[rawLevel] : 'MEDIUM';
    } else {
      levelStr = rawLevel?.toString() ?? 'MEDIUM';
    }

    return CrowdPrediction(
      locationId: json['location_id'] as int? ?? 1,
      locationName: json['location_name'] as String? ?? 'Campus Facility',
      predictedCrowdLevel: levelStr,
      predictedCrowdScore: (json['predicted_crowd_score'] as num?)?.toDouble() ?? 0.3,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.85,
      modelName: json['model_name'] as String? ?? 'GradientBoostingClassifier',
      featuresUsed: json['features_used'] as Map<String, dynamic>? ?? {},
    );
  }
}
