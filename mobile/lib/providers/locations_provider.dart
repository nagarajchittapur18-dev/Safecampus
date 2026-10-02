// SafeCampus AI — Locations Provider
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/campus_location.dart';
import '../services/api_service.dart';

// Async provider for all campus locations from FastAPI
final locationsProvider = FutureProvider<List<CampusLocation>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getLocations();
});

// Search query state
final locationSearchQueryProvider = StateProvider<String>((ref) => '');

// Filter category state (all, building, gate, canteen, library, outdoor, junction)
final locationCategoryFilterProvider = StateProvider<String>((ref) => 'all');

// Filtered locations provider
final filteredLocationsProvider = Provider<AsyncValue<List<CampusLocation>>>((ref) {
  final locationsAsync = ref.watch(locationsProvider);
  final query = ref.watch(locationSearchQueryProvider).trim().toLowerCase();
  final category = ref.watch(locationCategoryFilterProvider).toLowerCase();

  return locationsAsync.whenData((locations) {
    return locations.where((loc) {
      final matchesQuery = query.isEmpty ||
          loc.name.toLowerCase().contains(query) ||
          (loc.description?.toLowerCase().contains(query) ?? false) ||
          loc.locationType.toLowerCase().contains(query);

      final matchesCategory = category == 'all' ||
          loc.locationType.toLowerCase() == category ||
          (category == 'academic' && (loc.locationType == 'building' || loc.locationType == 'lab' || loc.locationType == 'library')) ||
          (category == 'amenities' && (loc.locationType == 'canteen' || loc.locationType == 'sports' || loc.locationType == 'hostel'));

      return matchesQuery && matchesCategory;
    }).toList();
  });
});

// Location by ID lookup helper
final locationByIdProvider = Provider.family<CampusLocation?, int>((ref, id) {
  final locations = ref.watch(locationsProvider).valueOrNull;
  if (locations == null) return null;
  try {
    return locations.firstWhere((loc) => loc.id == id);
  } catch (_) {
    return null;
  }
});
