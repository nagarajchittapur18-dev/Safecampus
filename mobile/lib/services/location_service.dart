// SafeCampus AI — Location Service (Phase 10: Current Location & Nearest Node Snapping)
// Strictly privacy-preserving: precise coordinates are transient and never persisted.
// Does not require GPS for the application to function.

import 'dart:math' as math;
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';

import '../models/campus_location.dart';

enum LocationServiceStatus {
  initial,
  loading,
  ready,
  permissionDenied,
  permissionDeniedForever,
  serviceDisabled,
  error,
}

class UserLocationResult {
  final double latitude;
  final double longitude;
  final double accuracy;
  final CampusLocation nearestNode;
  final double distanceToNodeM;

  const UserLocationResult({
    required this.latitude,
    required this.longitude,
    required this.accuracy,
    required this.nearestNode,
    required this.distanceToNodeM,
  });
}

final locationServiceProvider = Provider<LocationService>((ref) {
  return LocationService();
});

class LocationService {
  /// Calculate great-circle distance between two geographic coordinates in metres.
  static double calculateDistanceMeters(
    double lat1,
    double lon1,
    double lat2,
    double lon2,
  ) {
    const earthRadiusM = 6371000.0;
    final dLat = _degToRad(lat2 - lat1);
    final dLon = _degToRad(lon2 - lon1);

    final a = math.sin(dLat / 2) * math.sin(dLat / 2) +
        math.cos(_degToRad(lat1)) *
            math.cos(_degToRad(lat2)) *
            math.sin(dLon / 2) *
            math.sin(dLon / 2);
    final c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));
    return earthRadiusM * c;
  }

  static double _degToRad(double deg) => deg * (math.pi / 180.0);

  /// Find the nearest campus graph node to the given coordinates.
  static CampusLocation findNearestNode(
    double lat,
    double lon,
    List<CampusLocation> locations,
  ) {
    if (locations.isEmpty) {
      throw StateError('Cannot find nearest node from empty campus locations list');
    }

    CampusLocation nearest = locations.first;
    double minDistance = calculateDistanceMeters(lat, lon, nearest.latitude, nearest.longitude);

    for (int i = 1; i < locations.length; i++) {
      final loc = locations[i];
      final dist = calculateDistanceMeters(lat, lon, loc.latitude, loc.longitude);
      if (dist < minDistance) {
        minDistance = dist;
        nearest = loc;
      }
    }
    return nearest;
  }

  /// Request permission, detect GPS position, and snap to nearest campus node.
  Future<({LocationServiceStatus status, UserLocationResult? result, String message})>
      getCurrentLocationAndNearestNode(List<CampusLocation> campusLocations) async {
    try {
      // 1. Check if location services (GPS) are enabled on the device
      final isEnabled = await Geolocator.isLocationServiceEnabled();
      if (!isEnabled) {
        return (
          status: LocationServiceStatus.serviceDisabled,
          result: null,
          message: 'Location services (GPS) are disabled on your device. Please choose a starting point manually.',
        );
      }

      // 2. Check and request location permission
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          return (
            status: LocationServiceStatus.permissionDenied,
            result: null,
            message: 'Location permission was denied. You can select your starting campus location manually.',
          );
        }
      }

      if (permission == LocationPermission.deniedForever) {
        return (
          status: LocationServiceStatus.permissionDeniedForever,
          result: null,
          message: 'Location permission is permanently denied. You can select your starting campus location manually.',
        );
      }

      // 3. Acquire current position with high accuracy and a strict timeout
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: Duration(seconds: 8),
        ),
      );

      // 4. Find nearest campus graph node
      final nearest = findNearestNode(position.latitude, position.longitude, campusLocations);
      final dist = calculateDistanceMeters(
        position.latitude,
        position.longitude,
        nearest.latitude,
        nearest.longitude,
      );

      // Privacy Guarantee: Precise coordinates are solely kept in transient memory
      // for real-time map rendering. They are never sent to external servers or logged.
      final result = UserLocationResult(
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
        nearestNode: nearest,
        distanceToNodeM: dist,
      );

      return (
        status: LocationServiceStatus.ready,
        result: result,
        message: 'Located near ${nearest.name} (${dist.toInt()}m away)',
      );
    } catch (e) {
      debugPrint('[LocationService] Error acquiring position: $e');
      return (
        status: LocationServiceStatus.error,
        result: null,
        message: 'Could not detect GPS location: ${e.toString().replaceAll('Exception:', '').trim()}. Manual selection is available.',
      );
    }
  }
}
