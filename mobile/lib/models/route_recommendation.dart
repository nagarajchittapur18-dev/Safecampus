// SafeCampus AI — Alternative Route Model
class AlternativeRoute {
  final String label;
  final String preference;
  final List<int> route;
  final List<String> routeNames;
  final double distanceM;
  final double travelTimeMin;
  final double crowdScore;
  final String crowdLevel;
  final double safetyScore;
  final double accessibilityScore;
  final double totalCost;

  const AlternativeRoute({
    required this.label,
    required this.preference,
    required this.route,
    required this.routeNames,
    required this.distanceM,
    required this.travelTimeMin,
    required this.crowdScore,
    required this.crowdLevel,
    required this.safetyScore,
    required this.accessibilityScore,
    required this.totalCost,
  });

  factory AlternativeRoute.fromJson(Map<String, dynamic> json) {
    return AlternativeRoute(
      label: json['label'] as String? ?? 'Alternative',
      preference: json['preference'] as String? ?? 'custom',
      route: (json['route'] as List<dynamic>?)?.map((e) => e as int).toList() ?? [],
      routeNames: (json['route_names'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      distanceM: (json['distance_m'] as num?)?.toDouble() ?? 0.0,
      travelTimeMin: (json['travel_time_min'] as num?)?.toDouble() ?? 0.0,
      crowdScore: (json['crowd_score'] as num?)?.toDouble() ?? 0.0,
      crowdLevel: json['crowd_level'] as String? ?? 'LOW',
      safetyScore: (json['safety_score'] as num?)?.toDouble() ?? 0.0,
      accessibilityScore: (json['accessibility_score'] as num?)?.toDouble() ?? 0.0,
      totalCost: (json['total_cost'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
        'label': label,
        'preference': preference,
        'route': route,
        'route_names': routeNames,
        'distance_m': distanceM,
        'travel_time_min': travelTimeMin,
        'crowd_score': crowdScore,
        'crowd_level': crowdLevel,
        'safety_score': safetyScore,
        'accessibility_score': accessibilityScore,
        'total_cost': totalCost,
      };
}

// SafeCampus AI — Shortest Baseline Model
class ShortestBaseline {
  final List<int> route;
  final List<String> routeNames;
  final double distanceM;
  final double travelTimeMin;
  final double crowdScore;
  final String crowdLevel;
  final double safetyScore;
  final double accessibilityScore;

  const ShortestBaseline({
    required this.route,
    required this.routeNames,
    required this.distanceM,
    required this.travelTimeMin,
    required this.crowdScore,
    required this.crowdLevel,
    required this.safetyScore,
    required this.accessibilityScore,
  });

  factory ShortestBaseline.fromJson(Map<String, dynamic> json) {
    return ShortestBaseline(
      route: (json['route'] as List<dynamic>?)?.map((e) => e as int).toList() ?? [],
      routeNames: (json['route_names'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      distanceM: (json['distance_m'] as num?)?.toDouble() ?? 0.0,
      travelTimeMin: (json['travel_time_min'] as num?)?.toDouble() ?? 0.0,
      crowdScore: (json['crowd_score'] as num?)?.toDouble() ?? 0.0,
      crowdLevel: json['crowd_level'] as String? ?? 'LOW',
      safetyScore: (json['safety_score'] as num?)?.toDouble() ?? 0.0,
      accessibilityScore: (json['accessibility_score'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
        'route': route,
        'route_names': routeNames,
        'distance_m': distanceM,
        'travel_time_min': travelTimeMin,
        'crowd_score': crowdScore,
        'crowd_level': crowdLevel,
        'safety_score': safetyScore,
        'accessibility_score': accessibilityScore,
      };
}

// SafeCampus AI — Tradeoff Metric Model
class TradeoffMetric {
  final double recommended;
  final double shortest;
  final double difference;
  final double percentageDifference;
  final String? recommendedLevel;
  final String? shortestLevel;

  const TradeoffMetric({
    required this.recommended,
    required this.shortest,
    required this.difference,
    required this.percentageDifference,
    this.recommendedLevel,
    this.shortestLevel,
  });

  factory TradeoffMetric.fromJson(Map<String, dynamic> json) {
    return TradeoffMetric(
      recommended: (json['recommended'] as num?)?.toDouble() ?? 0.0,
      shortest: (json['shortest'] as num?)?.toDouble() ?? 0.0,
      difference: (json['difference'] as num?)?.toDouble() ?? 0.0,
      percentageDifference: (json['percentage_difference'] as num?)?.toDouble() ?? 0.0,
      recommendedLevel: json['recommended_level'] as String?,
      shortestLevel: json['shortest_level'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'recommended': recommended,
        'shortest': shortest,
        'difference': difference,
        'percentage_difference': percentageDifference,
        if (recommendedLevel != null) 'recommended_level': recommendedLevel,
        if (shortestLevel != null) 'shortest_level': shortestLevel,
      };
}

// SafeCampus AI — Route Explanation Model
class RouteExplanation {
  final String summary;
  final String whySelected;
  final String distanceTradeoff;
  final String timeTradeoff;
  final String crowdTradeoff;
  final String safetyTradeoff;
  final String accessibilityTradeoff;
  final List<String> reasons;
  final Map<String, dynamic> tradeoffs;
  final ShortestBaseline shortestBaseline;

  const RouteExplanation({
    required this.summary,
    required this.whySelected,
    required this.distanceTradeoff,
    required this.timeTradeoff,
    required this.crowdTradeoff,
    required this.safetyTradeoff,
    required this.accessibilityTradeoff,
    required this.reasons,
    required this.tradeoffs,
    required this.shortestBaseline,
  });

  factory RouteExplanation.fromJson(Map<String, dynamic> json) {
    return RouteExplanation(
      summary: json['summary'] as String? ?? 'Route recommended according to active preferences.',
      whySelected: json['why_selected'] as String? ?? '',
      distanceTradeoff: json['distance_tradeoff'] as String? ?? '',
      timeTradeoff: json['time_tradeoff'] as String? ?? '',
      crowdTradeoff: json['crowd_tradeoff'] as String? ?? '',
      safetyTradeoff: json['safety_tradeoff'] as String? ?? '',
      accessibilityTradeoff: json['accessibility_tradeoff'] as String? ?? '',
      reasons: (json['reasons'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      tradeoffs: json['tradeoffs'] as Map<String, dynamic>? ?? {},
      shortestBaseline: ShortestBaseline.fromJson(
        json['shortest_baseline'] as Map<String, dynamic>? ?? {},
      ),
    );
  }

  Map<String, dynamic> toJson() => {
        'summary': summary,
        'why_selected': whySelected,
        'distance_tradeoff': distanceTradeoff,
        'time_tradeoff': timeTradeoff,
        'crowd_tradeoff': crowdTradeoff,
        'safety_tradeoff': safetyTradeoff,
        'accessibility_tradeoff': accessibilityTradeoff,
        'reasons': reasons,
        'tradeoffs': tradeoffs,
        'shortest_baseline': shortestBaseline.toJson(),
      };
}

// SafeCampus AI — Route Recommendation Model
class RouteRecommendation {
  final int sourceId;
  final int destinationId;
  final String preference;
  final Map<String, double> weights;
  final List<int> route;
  final List<String> routeNames;
  final double distanceM;
  final double travelTimeMin;
  final double crowdScore;
  final String crowdLevel;
  final double safetyScore;
  final double accessibilityScore;
  final double totalCost;
  final double executionTimeMs;
  final String algorithm;
  final bool usedMlCrowd;
  final String? modelName;
  final List<AlternativeRoute> alternatives;
  final RouteExplanation? explanation;

  const RouteRecommendation({
    required this.sourceId,
    required this.destinationId,
    required this.preference,
    required this.weights,
    required this.route,
    required this.routeNames,
    required this.distanceM,
    required this.travelTimeMin,
    required this.crowdScore,
    required this.crowdLevel,
    required this.safetyScore,
    required this.accessibilityScore,
    required this.totalCost,
    required this.executionTimeMs,
    required this.algorithm,
    required this.usedMlCrowd,
    this.modelName,
    this.alternatives = const [],
    this.explanation,
  });

  factory RouteRecommendation.fromJson(Map<String, dynamic> json) {
    final rawWeights = json['weights'] as Map<String, dynamic>? ?? {};
    final weightsMap = rawWeights.map(
      (k, v) => MapEntry(k, (v as num).toDouble()),
    );

    final rawExplanation = json['explanation'] as Map<String, dynamic>?;

    return RouteRecommendation(
      sourceId: json['source_id'] as int? ?? 1,
      destinationId: json['destination_id'] as int? ?? 8,
      preference: json['preference'] as String? ?? 'balanced',
      weights: weightsMap,
      route: (json['route'] as List<dynamic>?)?.map((e) => e as int).toList() ?? [],
      routeNames: (json['route_names'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      distanceM: (json['distance_m'] as num?)?.toDouble() ?? 0.0,
      travelTimeMin: (json['travel_time_min'] as num?)?.toDouble() ?? 0.0,
      crowdScore: (json['crowd_score'] as num?)?.toDouble() ?? 0.0,
      crowdLevel: json['crowd_level'] as String? ?? 'LOW',
      safetyScore: (json['safety_score'] as num?)?.toDouble() ?? 0.0,
      accessibilityScore: (json['accessibility_score'] as num?)?.toDouble() ?? 0.0,
      totalCost: (json['total_cost'] as num?)?.toDouble() ?? 0.0,
      executionTimeMs: (json['execution_time_ms'] as num?)?.toDouble() ?? 0.0,
      algorithm: json['algorithm'] as String? ?? 'personalized_multi_objective_a_star',
      usedMlCrowd: json['used_ml_crowd'] as bool? ?? true,
      modelName: json['model_name'] as String?,
      alternatives: (json['alternatives'] as List<dynamic>?)
              ?.map((e) => AlternativeRoute.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      explanation: rawExplanation != null ? RouteExplanation.fromJson(rawExplanation) : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'source_id': sourceId,
        'destination_id': destinationId,
        'preference': preference,
        'weights': weights,
        'route': route,
        'route_names': routeNames,
        'distance_m': distanceM,
        'travel_time_min': travelTimeMin,
        'crowd_score': crowdScore,
        'crowd_level': crowdLevel,
        'safety_score': safetyScore,
        'accessibility_score': accessibilityScore,
        'total_cost': totalCost,
        'execution_time_ms': executionTimeMs,
        'algorithm': algorithm,
        'used_ml_crowd': usedMlCrowd,
        'model_name': modelName,
        'alternatives': alternatives.map((e) => e.toJson()).toList(),
        if (explanation != null) 'explanation': explanation!.toJson(),
      };
}
