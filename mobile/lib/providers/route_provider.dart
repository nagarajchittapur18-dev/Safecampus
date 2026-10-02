// SafeCampus AI — Route Recommendation State & Provider
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/constants/app_constants.dart';
import '../models/campus_location.dart';
import '../models/route_history_item.dart';
import '../models/route_recommendation.dart';
import '../services/api_service.dart';
import 'history_provider.dart';
import 'locations_provider.dart';

class RouteState {
  final CampusLocation? source;
  final CampusLocation? destination;
  final String preference;
  final Map<String, double>? customWeights;
  final int? simulationHour;
  final int? simulationDay;
  final int eventFlag;
  final int? classActivity;
  final int examFlag;
  final int holidayFlag;
  final bool useMlCrowd;
  final AsyncValue<RouteRecommendation?> recommendation;
  final Map<String, dynamic>? dijkstraBaseline;
  final int navigationIndex;
  final int selectedRouteIndex; // 0: recommended, 1+: alternatives

  const RouteState({
    this.source,
    this.destination,
    this.preference = AppConstants.prefBalanced,
    this.customWeights,
    this.simulationHour,
    this.simulationDay,
    this.eventFlag = 0,
    this.classActivity,
    this.examFlag = 0,
    this.holidayFlag = 0,
    this.useMlCrowd = true,
    this.recommendation = const AsyncData(null),
    this.dijkstraBaseline,
    this.navigationIndex = 0,
    this.selectedRouteIndex = 0,
  });

  List<int> get activeRouteIds {
    final rec = recommendation.valueOrNull;
    if (rec == null) return [];
    if (selectedRouteIndex == 0 || selectedRouteIndex > rec.alternatives.length) {
      return rec.route;
    }
    return rec.alternatives[selectedRouteIndex - 1].route;
  }

  List<String> get activeRouteNames {
    final rec = recommendation.valueOrNull;
    if (rec == null) return [];
    if (selectedRouteIndex == 0 || selectedRouteIndex > rec.alternatives.length) {
      return rec.routeNames;
    }
    return rec.alternatives[selectedRouteIndex - 1].routeNames;
  }

  RouteState copyWith({
    CampusLocation? source,
    CampusLocation? destination,
    String? preference,
    Map<String, double>? customWeights,
    int? simulationHour,
    int? simulationDay,
    int? eventFlag,
    int? classActivity,
    int? examFlag,
    int? holidayFlag,
    bool? useMlCrowd,
    AsyncValue<RouteRecommendation?>? recommendation,
    Map<String, dynamic>? dijkstraBaseline,
    int? navigationIndex,
    int? selectedRouteIndex,
    bool clearCustomWeights = false,
  }) {
    return RouteState(
      source: source ?? this.source,
      destination: destination ?? this.destination,
      preference: preference ?? this.preference,
      customWeights: clearCustomWeights ? null : (customWeights ?? this.customWeights),
      simulationHour: simulationHour ?? this.simulationHour,
      simulationDay: simulationDay ?? this.simulationDay,
      eventFlag: eventFlag ?? this.eventFlag,
      classActivity: classActivity ?? this.classActivity,
      examFlag: examFlag ?? this.examFlag,
      holidayFlag: holidayFlag ?? this.holidayFlag,
      useMlCrowd: useMlCrowd ?? this.useMlCrowd,
      recommendation: recommendation ?? this.recommendation,
      dijkstraBaseline: dijkstraBaseline ?? this.dijkstraBaseline,
      navigationIndex: navigationIndex ?? this.navigationIndex,
      selectedRouteIndex: selectedRouteIndex ?? this.selectedRouteIndex,
    );
  }
}

class RouteNotifier extends StateNotifier<RouteState> {
  final Ref _ref;

  RouteNotifier(this._ref) : super(const RouteState()) {
    _initializeDefaults();
  }

  void selectRouteIndex(int index) {
    state = state.copyWith(selectedRouteIndex: index, navigationIndex: 0);
  }


  void _initializeDefaults() {
    // Attempt to set default source (Main Gate: id 1) and destination (Canteen: id 8)
    _ref.listen<AsyncValue<List<CampusLocation>>>(locationsProvider, (prev, next) {
      if (next.hasValue && next.value != null && next.value!.isNotEmpty) {
        final locs = next.value!;
        final defaultSource = locs.firstWhere((l) => l.id == 1, orElse: () => locs.first);
        final defaultDest = locs.firstWhere((l) => l.id == 8, orElse: () => locs.last);
        if (state.source == null) {
          state = state.copyWith(source: defaultSource, destination: defaultDest);
        }
      }
    });
  }

  void setSource(CampusLocation loc) {
    state = state.copyWith(source: loc);
  }

  void setDestination(CampusLocation loc) {
    state = state.copyWith(destination: loc);
  }

  void swapLocations() {
    final temp = state.source;
    state = state.copyWith(
      source: state.destination,
      destination: temp,
    );
  }

  void setPreference(String pref) {
    state = state.copyWith(
      preference: pref,
      clearCustomWeights: true,
    );
  }

  void setCustomWeights(Map<String, double> weights) {
    state = state.copyWith(customWeights: weights);
  }

  void setSimulationHour(int? hour) {
    state = state.copyWith(simulationHour: hour);
  }

  void setEventFlag(int flag) {
    state = state.copyWith(eventFlag: flag);
  }

  void setClassActivity(int? flag) {
    state = state.copyWith(classActivity: flag);
  }

  void setExamFlag(int flag) {
    state = state.copyWith(examFlag: flag);
  }

  void setUseMlCrowd(bool use) {
    state = state.copyWith(useMlCrowd: use);
  }

  void setNavigationIndex(int index) {
    state = state.copyWith(navigationIndex: index);
  }

  void nextNavigationStep() {
    final route = state.recommendation.valueOrNull?.route ?? [];
    if (state.navigationIndex < route.length - 1) {
      state = state.copyWith(navigationIndex: state.navigationIndex + 1);
    }
  }

  void previousNavigationStep() {
    if (state.navigationIndex > 0) {
      state = state.copyWith(navigationIndex: state.navigationIndex - 1);
    }
  }

  // -------------------------------------------------------------------------
  // Core Method: Find Best Route (calls FastAPI backend)
  // -------------------------------------------------------------------------
  Future<RouteRecommendation?> findBestRoute() async {
    if (state.source == null || state.destination == null) {
      state = state.copyWith(
        recommendation: const AsyncError('Please select both a start and destination location.', StackTrace.empty),
      );
      return null;
    }

    state = state.copyWith(
      recommendation: const AsyncLoading(),
      navigationIndex: 0,
      selectedRouteIndex: 0,
    );

    final apiService = _ref.read(apiServiceProvider);

    try {
      // 1. Compute Personalized Multi-Objective A* recommended route
      final rec = await apiService.recommendRoute(
        sourceId: state.source!.id,
        destinationId: state.destination!.id,
        preference: state.preference,
        weights: state.customWeights,
        hour: state.simulationHour,
        dayOfWeek: state.simulationDay,
        eventFlag: state.eventFlag,
        classActivity: state.classActivity,
        examFlag: state.examFlag,
        holidayFlag: state.holidayFlag,
        useMlCrowd: state.useMlCrowd,
      );

      // 2. Compute Dijkstra baseline for Pareto trade-off explanation
      Map<String, dynamic>? dijkstra;
      try {
        dijkstra = await apiService.getDijkstraRoute(
          sourceId: state.source!.id,
          destinationId: state.destination!.id,
        );
      } catch (_) {
        // Fallback gracefully if dijkstra endpoint fails
      }

      state = state.copyWith(
        recommendation: AsyncData(rec),
        dijkstraBaseline: dijkstra,
      );

      // 3. Save to route history
      final historyItem = RouteHistoryItem.fromRecommendation(
        rec: rec,
        sourceName: state.source!.name,
        destinationName: state.destination!.name,
      );
      _ref.read(historyProvider.notifier).addItem(historyItem);

      return rec;
    } catch (e, st) {
      state = state.copyWith(
        recommendation: AsyncError(
          'Failed to calculate route: ${e.toString().replaceAll('Exception:', '').trim()}',
          st,
        ),
      );
      return null;
    }
  }
}

final routeProvider = StateNotifierProvider<RouteNotifier, RouteState>((ref) {
  return RouteNotifier(ref);
});
