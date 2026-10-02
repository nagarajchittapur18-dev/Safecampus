// SafeCampus AI — User Location Provider (Riverpod State)
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/constants/fallback_campus_data.dart';
import '../models/campus_location.dart';
import '../services/location_service.dart';
import 'locations_provider.dart';
import 'route_provider.dart';

class UserLocationState {
  final LocationServiceStatus status;
  final UserLocationResult? result;
  final String? message;
  final bool isUsingGpsSource;

  const UserLocationState({
    this.status = LocationServiceStatus.initial,
    this.result,
    this.message,
    this.isUsingGpsSource = false,
  });

  bool get hasLocation => result != null;
  bool get isLoading => status == LocationServiceStatus.loading;

  UserLocationState copyWith({
    LocationServiceStatus? status,
    UserLocationResult? result,
    String? message,
    bool? isUsingGpsSource,
    bool clearResult = false,
  }) {
    return UserLocationState(
      status: status ?? this.status,
      result: clearResult ? null : (result ?? this.result),
      message: message ?? this.message,
      isUsingGpsSource: isUsingGpsSource ?? this.isUsingGpsSource,
    );
  }
}

class UserLocationNotifier extends StateNotifier<UserLocationState> {
  final Ref _ref;

  UserLocationNotifier(this._ref) : super(const UserLocationState());

  /// Detect current position, locate nearest campus node, and optionally set as route origin.
  Future<({bool success, String message, CampusLocation? nearestNode})> detectLocationAndSnapSource({
    bool autoSetSource = true,
  }) async {
    state = state.copyWith(status: LocationServiceStatus.loading, message: 'Detecting GPS location...');

    final locations = _ref.read(locationsProvider).valueOrNull ?? FallbackCampusData.locations;
    final locationService = _ref.read(locationServiceProvider);

    final outcome = await locationService.getCurrentLocationAndNearestNode(locations);

    if (outcome.status == LocationServiceStatus.ready && outcome.result != null) {
      final res = outcome.result!;
      state = state.copyWith(
        status: LocationServiceStatus.ready,
        result: res,
        message: outcome.message,
        isUsingGpsSource: autoSetSource,
      );

      if (autoSetSource) {
        _ref.read(routeProvider.notifier).setSource(res.nearestNode);
      }

      return (
        success: true,
        message: outcome.message,
        nearestNode: res.nearestNode,
      );
    } else {
      state = state.copyWith(
        status: outcome.status,
        clearResult: true,
        message: outcome.message,
        isUsingGpsSource: false,
      );

      return (
        success: false,
        message: outcome.message,
        nearestNode: null,
      );
    }
  }

  /// Reset GPS detection and return to purely manual selection.
  void clearGps() {
    state = state.copyWith(
      status: LocationServiceStatus.initial,
      clearResult: true,
      message: null,
      isUsingGpsSource: false,
    );
  }

  /// Inform state that a manual location selection occurred.
  void notifyManualSelection() {
    if (state.isUsingGpsSource) {
      state = state.copyWith(isUsingGpsSource: false);
    }
  }
}

final userLocationProvider = StateNotifierProvider<UserLocationNotifier, UserLocationState>((ref) {
  return UserLocationNotifier(ref);
});
