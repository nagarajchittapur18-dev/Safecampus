// SafeCampus AI — Campus Map Screen (OpenStreetMap via flutter_map)
// Zero-cost open data mapping with offline schematic resilience, multi-route visualization,
// distinct source/destination markers, interactive node inspection, and academic integrity disclaimers.

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';

import '../../core/constants/app_constants.dart';
import '../../core/constants/fallback_campus_data.dart';
import '../../core/router/app_router.dart';
import '../../models/campus_location.dart';
import '../../models/route_recommendation.dart';
import '../../providers/crowd_provider.dart';
import '../../providers/locations_provider.dart';
import '../../providers/route_provider.dart';
import '../../providers/user_location_provider.dart';
import '../../services/location_service.dart';
import '../../theme/app_theme.dart';
import '../../widgets/campus_bottom_nav.dart';
import '../../widgets/score_badge.dart';

class CampusMapScreen extends ConsumerStatefulWidget {
  const CampusMapScreen({super.key});

  @override
  ConsumerState<CampusMapScreen> createState() => _CampusMapScreenState();
}

class _CampusMapScreenState extends ConsumerState<CampusMapScreen> {
  final MapController _mapController = MapController();
  bool _showCrowdOverlay = false;
  bool _offlineSchematicMode = false;

  @override
  Widget build(BuildContext context) {
    final locationsAsync = ref.watch(locationsProvider);
    final routeState = ref.watch(routeProvider);
    final crowdDataAsync = ref.watch(crowdHeatmapProvider);
    final rec = routeState.recommendation.valueOrNull;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Campus Map'),
        actions: [
          // 1. Toggle Offline Schematic Grid View
          IconButton(
            icon: Icon(
              _offlineSchematicMode ? Icons.grid_view_rounded : Icons.map_outlined,
              color: _offlineSchematicMode ? AppColors.accent : AppColors.textPrimary,
            ),
            tooltip: _offlineSchematicMode ? 'Switch to OSM Street Map' : 'Switch to Schematic Grid (Offline Mode)',
            onPressed: () {
              setState(() => _offlineSchematicMode = !_offlineSchematicMode);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(_offlineSchematicMode
                      ? 'Offline Schematic Campus Grid view active'
                      : 'OpenStreetMap satellite/street tile view active'),
                  duration: const Duration(seconds: 2),
                ),
              );
            },
          ),

          // 2. Toggle Crowd Density Overlay
          IconButton(
            icon: Icon(
              _showCrowdOverlay ? Icons.people_rounded : Icons.people_outline_rounded,
              color: _showCrowdOverlay ? AppColors.warning : AppColors.textPrimary,
            ),
            tooltip: 'Toggle Crowd Density Heatmap Pins',
            onPressed: () {
              setState(() => _showCrowdOverlay = !_showCrowdOverlay);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(_showCrowdOverlay
                      ? 'AI Predicted crowd density pins enabled'
                      : 'Default campus facility pins active'),
                  duration: const Duration(seconds: 1),
                ),
              );
            },
          ),

          // 3. Search / Manual Campus Location Directory
          IconButton(
            icon: const Icon(Icons.list_alt_rounded, color: AppColors.textPrimary),
            tooltip: 'Campus Location Directory (Manual Picker)',
            onPressed: () => _showLocationDirectory(context, locationsAsync.valueOrNull ?? FallbackCampusData.locations),
          ),

          // 4. Details action when route is computed
          if (rec != null)
            IconButton(
              icon: const Icon(Icons.insights_rounded, color: AppColors.primary),
              tooltip: 'Route Details & Explanation',
              onPressed: () => context.push(AppRoutes.results),
            ),
        ],
      ),
      body: locationsAsync.when(
        data: (locations) => _buildMapContent(context, locations, routeState, rec, crowdDataAsync.valueOrNull ?? {}),
        loading: () => const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 12),
              Text('Loading campus facility map...', style: TextStyle(color: AppColors.textSecondary)),
            ],
          ),
        ),
        error: (_, __) => _buildMapContent(
          context,
          FallbackCampusData.locations,
          routeState,
          rec,
          crowdDataAsync.valueOrNull ?? {},
        ),
      ),
      bottomNavigationBar: const CampusBottomNav(currentIndex: 1),
    );
  }

  Widget _buildMapContent(
    BuildContext context,
    List<CampusLocation> locations,
    RouteState routeState,
    RouteRecommendation? rec,
    Map<int, dynamic> crowdMap,
  ) {
    final locMap = {for (var l in locations) l.id: l};
    final userLocationState = ref.watch(userLocationProvider);
    final userLocation = userLocationState.result;

    // Calculate Route Points
    final activeRoutePoints = <LatLng>[];
    for (final nid in routeState.activeRouteIds) {
      final loc = locMap[nid];
      if (loc != null) {
        activeRoutePoints.add(LatLng(loc.latitude, loc.longitude));
      }
    }

    // Build Polylines (Recommended + Alternatives + Walkway Edges)
    final polylines = <Polyline>[];

    // If user location is detected, draw connection line to nearest node
    if (userLocation != null) {
      polylines.add(
        Polyline(
          points: [
            LatLng(userLocation.latitude, userLocation.longitude),
            LatLng(userLocation.nearestNode.latitude, userLocation.nearestNode.longitude),
          ],
          strokeWidth: 2.5,
          color: Colors.blueAccent.withOpacity(0.65),
        ),
      );
    }

    // If in schematic mode or offline, draw campus graph walkway edges
    if (_offlineSchematicMode) {
      for (final edge in FallbackCampusData.edges) {
        final u = locMap[edge[0]];
        final v = locMap[edge[1]];
        if (u != null && v != null) {
          polylines.add(
            Polyline(
              points: [LatLng(u.latitude, u.longitude), LatLng(v.latitude, v.longitude)],
              strokeWidth: 2.0,
              color: Colors.blueGrey.withOpacity(0.35),
            ),
          );
        }
      }
    }

    // Draw Candidate Alternative Routes if available
    if (rec != null && rec.alternatives.isNotEmpty) {
      for (int i = 0; i < rec.alternatives.length; i++) {
        final alt = rec.alternatives[i];
        final altPoints = <LatLng>[];
        for (final nid in alt.route) {
          final loc = locMap[nid];
          if (loc != null) altPoints.add(LatLng(loc.latitude, loc.longitude));
        }

        final isSelected = routeState.selectedRouteIndex == (i + 1);
        final altColor = i == 0 ? const Color(0xFFE65100) : const Color(0xFF00897B);

        polylines.add(
          Polyline(
            points: altPoints,
            strokeWidth: isSelected ? 5.5 : 3.5,
            color: isSelected ? altColor : altColor.withOpacity(0.55),
          ),
        );
      }
    }

    // Draw Primary Recommended Route
    if (rec != null && rec.route.isNotEmpty) {
      final recPoints = <LatLng>[];
      for (final nid in rec.route) {
        final loc = locMap[nid];
        if (loc != null) recPoints.add(LatLng(loc.latitude, loc.longitude));
      }

      final isSelected = routeState.selectedRouteIndex == 0;

      // Glow border shadow
      if (isSelected) {
        polylines.add(
          Polyline(
            points: recPoints,
            strokeWidth: 8.5,
            color: AppColors.primaryDark.withOpacity(0.35),
          ),
        );
      }

      // Foreground recommended polyline
      polylines.add(
        Polyline(
          points: recPoints,
          strokeWidth: isSelected ? 5.5 : 3.5,
          color: isSelected ? AppColors.primary : AppColors.primary.withOpacity(0.55),
        ),
      );
    }

    return Stack(
      children: [
        // 1. OpenStreetMap Tile Layer or Schematic Background
        FlutterMap(
          mapController: _mapController,
          options: const MapOptions(
            initialCenter: LatLng(AppConstants.campusCenterLat, AppConstants.campusCenterLon),
            initialZoom: AppConstants.defaultZoom,
            minZoom: 14.5,
            maxZoom: 19.5,
          ),
          children: [
            if (!_offlineSchematicMode)
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.safecampus.ai',
                fallbackUrl: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                errorTileCallback: (tile, error, stackTrace) {
                  debugPrint('[Map] Tile load error, displaying offline campus fallback: $error');
                },
              ),

            // Polyline layer (walkways + routes)
            PolylineLayer(polylines: polylines),

            // Markers layer
            MarkerLayer(
              markers: [
                if (userLocation != null)
                  Marker(
                    point: LatLng(userLocation.latitude, userLocation.longitude),
                    width: 54,
                    height: 54,
                    child: GestureDetector(
                      onTap: () => _showUserLocationDetails(context, userLocation),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          Container(
                            width: 50,
                            height: 50,
                            decoration: BoxDecoration(
                              color: Colors.blueAccent.withOpacity(0.2),
                              shape: BoxShape.circle,
                            ),
                          ),
                          Container(
                            width: 24,
                            height: 24,
                            decoration: const BoxDecoration(
                              color: Colors.white,
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(color: Colors.black26, blurRadius: 4, offset: Offset(0, 2)),
                              ],
                            ),
                          ),
                          Container(
                            width: 14,
                            height: 14,
                            decoration: const BoxDecoration(
                              color: Colors.blueAccent,
                              shape: BoxShape.circle,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ...locations.map((loc) {
                final isOrigin = routeState.source?.id == loc.id;
                final isDest = routeState.destination?.id == loc.id;
                final isInActiveRoute = routeState.activeRouteIds.contains(loc.id);
                final crowdPred = crowdMap[loc.id];

                Color markerColor;
                if (isOrigin) {
                  markerColor = AppColors.secondary;
                } else if (isDest) {
                  markerColor = AppColors.error;
                } else if (_showCrowdOverlay && crowdPred != null) {
                  markerColor = _getCrowdColor(crowdPred.predictedCrowdLevel);
                } else if (isInActiveRoute) {
                  markerColor = AppColors.primary;
                } else {
                  markerColor = _getNodeColor(loc.locationType);
                }

                final size = isOrigin || isDest ? 46.0 : (isInActiveRoute ? 38.0 : 34.0);

                return Marker(
                  point: LatLng(loc.latitude, loc.longitude),
                  width: size + 20,
                  height: size + 22,
                  child: GestureDetector(
                    onTap: () => _showLocationDetails(context, loc, crowdPred),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // Label badge for Start / Destination
                        if (isOrigin || isDest)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                            margin: const EdgeInsets.only(bottom: 2),
                            decoration: BoxDecoration(
                              color: isOrigin ? AppColors.secondary : AppColors.error,
                              borderRadius: BorderRadius.circular(6),
                              boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 3)],
                            ),
                            child: Text(
                              isOrigin ? 'START' : 'DEST',
                              style: const TextStyle(color: Colors.white, fontSize: 8.5, fontWeight: FontWeight.bold),
                            ),
                          ),

                        // Circle Pin
                        Container(
                          width: size,
                          height: size,
                          decoration: BoxDecoration(
                            color: markerColor,
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: Colors.white,
                              width: isOrigin || isDest ? 3.0 : 2.0,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: (isOrigin
                                        ? AppColors.secondary
                                        : (isDest ? AppColors.error : Colors.black))
                                    .withOpacity(0.35),
                                blurRadius: isOrigin || isDest ? 8 : 4,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: Icon(
                            isOrigin
                                ? Icons.play_arrow_rounded
                                : (isDest ? Icons.flag_rounded : _getNodeIcon(loc.locationType)),
                            color: Colors.white,
                            size: size * 0.55,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }),
            ],
          ),
          ],
        ),

        // 2. Offline Mode Banner indicator
        if (_offlineSchematicMode)
          Positioned(
            top: 10,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.blueGrey.shade900.withOpacity(0.85),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Row(
                children: [
                  Icon(Icons.offline_bolt_rounded, color: Colors.amber, size: 16),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Schematic Grid View (Offline Compatible • No Tile Dependency)',
                      style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
          ),

        // 3. Active Route Card & Alternative Route Switcher
        if (rec != null)
          Positioned(
            top: _offlineSchematicMode ? 46 : 12,
            left: 14,
            right: 14,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Active Route Summary Card
                Card(
                  elevation: 4,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: _getRouteBadgeColor(routeState.selectedRouteIndex).withOpacity(0.15),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Icon(
                            Icons.route_rounded,
                            color: _getRouteBadgeColor(routeState.selectedRouteIndex),
                            size: 22,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                _getActiveRouteTitle(routeState, rec),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                _getActiveRouteSubtitle(routeState, rec),
                                style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                              ),
                            ],
                          ),
                        ),
                        TextButton(
                          onPressed: () => context.push(AppRoutes.results),
                          child: const Text('Details'),
                        ),
                      ],
                    ),
                  ),
                ),

                // Alternative Routes Selector Pills
                if (rec.alternatives.isNotEmpty)
                  Container(
                    height: 38,
                    margin: const EdgeInsets.only(top: 6),
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: [
                        // Recommended Option Pill
                        _buildRouteSelectorPill(
                          index: 0,
                          label: '★ Recommended (${rec.preference.toUpperCase()})',
                          sub: '${rec.distanceM.toInt()}m',
                          isSelected: routeState.selectedRouteIndex == 0,
                          color: AppColors.primary,
                        ),
                        // Alternatives Pills
                        for (int i = 0; i < rec.alternatives.length; i++)
                          _buildRouteSelectorPill(
                            index: i + 1,
                            label: rec.alternatives[i].label,
                            sub: '${rec.alternatives[i].distanceM.toInt()}m',
                            isSelected: routeState.selectedRouteIndex == (i + 1),
                            color: i == 0 ? const Color(0xFFE65100) : const Color(0xFF00897B),
                          ),
                      ],
                    ),
                  ),
              ],
            ),
          ),

        // 4. Map Action Controls (Recenter, Zoom In, Zoom Out, Fit Route, Directions)
        Positioned(
          bottom: 24,
          right: 14,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Zoom In FAB
              FloatingActionButton.small(
                heroTag: 'zoom_in_fab',
                backgroundColor: Colors.white,
                foregroundColor: AppColors.textPrimary,
                onPressed: () {
                  _mapController.move(
                    _mapController.camera.center,
                    _mapController.camera.zoom + 0.5,
                  );
                },
                child: const Icon(Icons.add_rounded),
              ),
              const SizedBox(height: 8),

              // Zoom Out FAB
              FloatingActionButton.small(
                heroTag: 'zoom_out_fab',
                backgroundColor: Colors.white,
                foregroundColor: AppColors.textPrimary,
                onPressed: () {
                  _mapController.move(
                    _mapController.camera.center,
                    _mapController.camera.zoom - 0.5,
                  );
                },
                child: const Icon(Icons.remove_rounded),
              ),
              const SizedBox(height: 8),

              // Fit Route Bounds FAB (if route active)
              if (activeRoutePoints.isNotEmpty) ...[
                FloatingActionButton.small(
                  heroTag: 'fit_bounds_fab',
                  backgroundColor: Colors.white,
                  foregroundColor: AppColors.primary,
                  tooltip: 'Fit Route in View',
                  onPressed: () => _fitRouteBounds(activeRoutePoints),
                  child: const Icon(Icons.zoom_out_map_rounded),
                ),
                const SizedBox(height: 8),
              ],

              // Current Location GPS FAB (Phase 10)
              FloatingActionButton.small(
                heroTag: 'gps_fab',
                backgroundColor: userLocationState.isUsingGpsSource ? AppColors.secondary : Colors.white,
                foregroundColor: userLocationState.isUsingGpsSource ? Colors.white : AppColors.primary,
                tooltip: 'Current Location (Snap Nearest Campus Node)',
                onPressed: () async {
                  final outcome = await ref.read(userLocationProvider.notifier).detectLocationAndSnapSource(autoSetSource: true);
                  if (context.mounted) {
                    if (outcome.success && outcome.nearestNode != null) {
                      _mapController.move(
                        LatLng(outcome.nearestNode!.latitude, outcome.nearestNode!.longitude),
                        18.0,
                      );
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(outcome.message)),
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(outcome.message),
                          duration: const Duration(seconds: 4),
                          action: SnackBarAction(
                            label: 'Manual',
                            onPressed: () => _showLocationDirectory(context, locations),
                          ),
                        ),
                      );
                    }
                  }
                },
                child: userLocationState.isLoading
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : Icon(userLocationState.isUsingGpsSource ? Icons.gps_fixed_rounded : Icons.my_location_rounded),
              ),
              const SizedBox(height: 8),

              // Recenter Campus Center FAB
              FloatingActionButton.small(
                heroTag: 'center_fab',
                backgroundColor: Colors.white,
                foregroundColor: AppColors.primary,
                tooltip: 'Recenter Campus',
                onPressed: () {
                  _mapController.move(
                    const LatLng(AppConstants.campusCenterLat, AppConstants.campusCenterLon),
                    AppConstants.defaultZoom,
                  );
                },
                child: const Icon(Icons.domain_rounded),
              ),
              const SizedBox(height: 12),

              // Plan Route / Switch to Home
              FloatingActionButton.extended(
                heroTag: 'plan_route_fab',
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                icon: const Icon(Icons.directions_rounded),
                label: const Text('Find Route'),
                onPressed: () => context.go(AppRoutes.home),
              ),
            ],
          ),
        ),

        // User Location Snapping Banner (Phase 10)
        if (userLocation != null)
          Positioned(
            bottom: 34,
            left: 14,
            right: 14,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.blueAccent.withOpacity(0.35)),
                boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 6)],
              ),
              child: Row(
                children: [
                  const Icon(Icons.gps_fixed_rounded, color: Colors.blueAccent, size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'GPS: Near ${userLocation.nearestNode.name} (~${userLocation.distanceToNodeM.toInt()}m away)',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                    ),
                  ),
                  if (routeState.source?.id != userLocation.nearestNode.id)
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.secondary,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        minimumSize: const Size(60, 28),
                      ),
                      onPressed: () {
                        ref.read(routeProvider.notifier).setSource(userLocation.nearestNode);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Origin set to ${userLocation.nearestNode.name}')),
                        );
                      },
                      child: const Text('Set Start', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                    )
                  else
                    const Text('Origin Active', style: TextStyle(fontSize: 11, color: AppColors.secondary, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
          ),

        // 5. OpenStreetMap & Simulated AI Research Attribution Disclaimer (Zero-Cost Guarantee)
        Positioned(
          bottom: 4,
          left: 14,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.85),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: Colors.black12),
            ),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.public_rounded, size: 10, color: AppColors.textSecondary),
                SizedBox(width: 4),
                Text(
                  '© OpenStreetMap (Zero-Cost) • AI Simulated Crowd Data',
                  style: TextStyle(fontSize: 9, color: AppColors.textSecondary, fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRouteSelectorPill({
    required int index,
    required String label,
    required String sub,
    required bool isSelected,
    required Color color,
  }) {
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: FilterChip(
        selected: isSelected,
        showCheckmark: false,
        avatar: Icon(
          Icons.route_rounded,
          size: 14,
          color: isSelected ? Colors.white : color,
        ),
        label: Text(
          '$label • $sub',
          style: TextStyle(
            fontSize: 11,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
            color: isSelected ? Colors.white : AppColors.textPrimary,
          ),
        ),
        selectedColor: color,
        backgroundColor: Colors.white,
        elevation: isSelected ? 3 : 1,
        onSelected: (_) {
          ref.read(routeProvider.notifier).selectRouteIndex(index);
        },
      ),
    );
  }

  void _fitRouteBounds(List<LatLng> points) {
    if (points.isEmpty) return;
    double minLat = points.first.latitude;
    double maxLat = points.first.latitude;
    double minLon = points.first.longitude;
    double maxLon = points.first.longitude;

    for (final p in points) {
      if (p.latitude < minLat) minLat = p.latitude;
      if (p.latitude > maxLat) maxLat = p.latitude;
      if (p.longitude < minLon) minLon = p.longitude;
      if (p.longitude > maxLon) maxLon = p.longitude;
    }

    final bounds = LatLngBounds(LatLng(minLat, minLon), LatLng(maxLat, maxLon));
    _mapController.fitCamera(
      CameraFit.bounds(
        bounds: bounds,
        padding: const EdgeInsets.all(50.0),
      ),
    );
  }

  String _getActiveRouteTitle(RouteState state, RouteRecommendation rec) {
    if (state.selectedRouteIndex == 0 || state.selectedRouteIndex > rec.alternatives.length) {
      return '${rec.routeNames.first} → ${rec.routeNames.last}';
    }
    final alt = rec.alternatives[state.selectedRouteIndex - 1];
    return '${alt.label}: ${alt.routeNames.first} → ${alt.routeNames.last}';
  }

  String _getActiveRouteSubtitle(RouteState state, RouteRecommendation rec) {
    if (state.selectedRouteIndex == 0 || state.selectedRouteIndex > rec.alternatives.length) {
      return '${rec.distanceM.toInt()}m • ${rec.travelTimeMin.toStringAsFixed(1)} min • ${rec.crowdLevel} Crowd';
    }
    final alt = rec.alternatives[state.selectedRouteIndex - 1];
    return '${alt.distanceM.toInt()}m • ${alt.travelTimeMin.toStringAsFixed(1)} min • Safety ${(alt.safetyScore * 100).toInt()}%';
  }

  Color _getRouteBadgeColor(int index) {
    if (index == 0) return AppColors.primary;
    if (index == 1) return const Color(0xFFE65100);
    return const Color(0xFF00897B);
  }

  void _showLocationDetails(BuildContext context, CampusLocation loc, dynamic crowdPred) {
    final routeNotifier = ref.read(routeProvider.notifier);
    final routeState = ref.read(routeProvider);

    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: _getNodeColor(loc.locationType).withOpacity(0.15),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(_getNodeIcon(loc.locationType), color: _getNodeColor(loc.locationType)),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          loc.name,
                          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        Text(
                          'Category: ${loc.locationType.toUpperCase()} (Node #${loc.id})',
                          style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              if (loc.description != null) ...[
                Text(
                  loc.description!,
                  style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                ),
                const SizedBox(height: 12),
              ],
              if (crowdPred != null) ...[
                Row(
                  children: [
                    CrowdBadge(level: crowdPred.predictedCrowdLevel, score: crowdPred.predictedCrowdScore),
                    const SizedBox(width: 8),
                    const Text(
                      '(AI Predicted / Simulated)',
                      style: TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: AppColors.textSecondary),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
              ],
              // Accessibility notice
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.accessible_rounded, size: 16, color: AppColors.primary),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Accessible corridors & ramp-compatible pathways connected.',
                        style: TextStyle(fontSize: 11, color: AppColors.textSecondary),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        routeNotifier.setSource(loc);
                        Navigator.pop(ctx);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Origin set to: ${loc.name}')),
                        );
                      },
                      icon: const Icon(Icons.trip_origin_rounded, size: 16),
                      label: const Text('Set as Start'),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        routeNotifier.setDestination(loc);
                        Navigator.pop(ctx);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Destination set to: ${loc.name}')),
                        );
                      },
                      icon: const Icon(Icons.location_on_rounded, size: 16),
                      label: const Text('Set as Dest'),
                    ),
                  ),
                ],
              ),
              if (routeState.source != null && loc.id != routeState.source!.id) ...[
                const SizedBox(height: 10),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.secondary,
                      foregroundColor: Colors.white,
                    ),
                    onPressed: () async {
                      routeNotifier.setDestination(loc);
                      Navigator.pop(ctx);
                      await routeNotifier.findBestRoute();
                    },
                    icon: const Icon(Icons.directions_rounded),
                    label: Text('Plan Route to ${loc.name}'),
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }

  void _showLocationDirectory(BuildContext context, List<CampusLocation> locations) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return DraggableScrollableSheet(
          initialChildSize: 0.65,
          minChildSize: 0.4,
          maxChildSize: 0.9,
          expand: false,
          builder: (_, scrollController) {
            return Column(
              children: [
                Container(
                  margin: const EdgeInsets.symmetric(vertical: 8),
                  height: 4,
                  width: 40,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Campus Directory (${locations.length} Locations)',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close_rounded),
                        onPressed: () => Navigator.pop(ctx),
                      ),
                    ],
                  ),
                ),
                const Divider(height: 1),
                Expanded(
                  child: ListView.separated(
                    controller: scrollController,
                    itemCount: locations.length,
                    separatorBuilder: (_, __) => const Divider(height: 1, indent: 64),
                    itemBuilder: (_, index) {
                      final loc = locations[index];
                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor: _getNodeColor(loc.locationType).withOpacity(0.15),
                          child: Icon(_getNodeIcon(loc.locationType), color: _getNodeColor(loc.locationType), size: 20),
                        ),
                        title: Text(loc.name, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                        subtitle: Text(
                          '${loc.locationType.toUpperCase()} • ${loc.description ?? ""}',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 11),
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.trip_origin_rounded, size: 20, color: AppColors.secondary),
                              tooltip: 'Set as Start',
                              onPressed: () {
                                ref.read(routeProvider.notifier).setSource(loc);
                                Navigator.pop(ctx);
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text('Origin set to: ${loc.name}')),
                                );
                              },
                            ),
                            IconButton(
                              icon: const Icon(Icons.location_on_rounded, size: 20, color: AppColors.error),
                              tooltip: 'Set as Destination',
                              onPressed: () {
                                ref.read(routeProvider.notifier).setDestination(loc);
                                Navigator.pop(ctx);
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text('Destination set to: ${loc.name}')),
                                );
                              },
                            ),
                          ],
                        ),
                        onTap: () {
                          Navigator.pop(ctx);
                          _mapController.move(LatLng(loc.latitude, loc.longitude), 18.5);
                          _showLocationDetails(context, loc, null);
                        },
                      );
                    },
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Color _getNodeColor(String type) {
    switch (type.toLowerCase()) {
      case 'gate':
        return const Color(0xFF1E88E5);
      case 'canteen':
        return const Color(0xFFFB8C00);
      case 'library':
        return const Color(0xFF00897B);
      case 'building':
        return const Color(0xFF5E35B1);
      case 'hostel':
        return const Color(0xFF8E24AA);
      case 'sports':
        return const Color(0xFF43A047);
      case 'medical':
        return const Color(0xFFE53935);
      case 'parking':
        return const Color(0xFF3949AB);
      case 'auditorium':
        return const Color(0xFFF4511E);
      default:
        return const Color(0xFF546E7A);
    }
  }

  IconData _getNodeIcon(String type) {
    switch (type.toLowerCase()) {
      case 'gate':
        return Icons.meeting_room_rounded;
      case 'canteen':
        return Icons.restaurant_rounded;
      case 'library':
        return Icons.local_library_rounded;
      case 'building':
        return Icons.business_rounded;
      case 'hostel':
        return Icons.bed_rounded;
      case 'sports':
        return Icons.sports_soccer_rounded;
      case 'medical':
        return Icons.local_hospital_rounded;
      case 'parking':
        return Icons.local_parking_rounded;
      case 'auditorium':
        return Icons.theater_comedy_rounded;
      default:
        return Icons.place_rounded;
    }
  }

  Color _getCrowdColor(String level) {
    switch (level.toUpperCase()) {
      case 'LOW':
        return AppColors.crowdLow;
      case 'MEDIUM':
        return AppColors.crowdMedium;
      case 'HIGH':
        return AppColors.crowdHigh;
      default:
        return AppColors.crowdVeryHigh;
    }
  }

  void _showUserLocationDetails(BuildContext context, UserLocationResult userLoc) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(Icons.my_location_rounded, color: Colors.blueAccent),
                  ),
                  const SizedBox(width: 14),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Your Current Position', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        Text('On-device GPS detection • Transient (Not Stored)', style: TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              Text(
                'Nearest Campus Facility: ${userLoc.nearestNode.name}',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              ),
              const SizedBox(height: 4),
              Text(
                'Distance: ~${userLoc.distanceToNodeM.toInt()} metres (${userLoc.accuracy.toStringAsFixed(1)}m GPS accuracy)',
                style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
              ),
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.secondary,
                        foregroundColor: Colors.white,
                      ),
                      onPressed: () {
                        ref.read(routeProvider.notifier).setSource(userLoc.nearestNode);
                        Navigator.pop(ctx);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Origin snapped to nearest node: ${userLoc.nearestNode.name}')),
                        );
                      },
                      icon: const Icon(Icons.trip_origin_rounded, size: 16),
                      label: const Text('Use as Start'),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        ref.read(userLocationProvider.notifier).clearGps();
                        Navigator.pop(ctx);
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Cleared GPS location. Manual selection active.')),
                        );
                      },
                      icon: const Icon(Icons.clear_rounded, size: 16),
                      label: const Text('Clear GPS'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
