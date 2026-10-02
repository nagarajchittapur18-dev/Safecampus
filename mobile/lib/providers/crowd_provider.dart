// SafeCampus AI — Crowd Heatmap Provider
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/crowd_prediction.dart';
import '../services/api_service.dart';
import 'locations_provider.dart';

final selectedHeatmapHourProvider = StateProvider<int>((ref) {
  return DateTime.now().hour;
});

final crowdHeatmapProvider = FutureProvider<Map<int, CrowdPrediction>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  final locationsAsync = await ref.watch(locationsProvider.future);
  final hour = ref.watch(selectedHeatmapHourProvider);

  final predictions = <int, CrowdPrediction>{};

  // Fetch predictions for all active locations
  final futures = locationsAsync.map((loc) async {
    try {
      final pred = await apiService.getCrowdPrediction(loc.id, hour: hour);
      return MapEntry(loc.id, pred);
    } catch (_) {
      return null;
    }
  });

  final results = await Future.wait(futures);
  for (final res in results) {
    if (res != null) {
      predictions[res.key] = res.value;
    }
  }

  return predictions;
});
