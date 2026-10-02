// SafeCampus AI — Home Screen
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/constants/app_constants.dart';
import '../../core/router/app_router.dart';
import '../../models/campus_location.dart';
import '../../providers/auth_provider.dart';
import '../../providers/locations_provider.dart';
import '../../providers/route_provider.dart';
import '../../providers/user_location_provider.dart';
import '../../theme/app_theme.dart';
import '../../widgets/campus_bottom_nav.dart';
import '../../widgets/location_selector_card.dart';
import '../../widgets/preference_chip.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider);
    final routeState = ref.watch(routeProvider);
    final routeNotifier = ref.read(routeProvider.notifier);
    final locationsAsync = ref.watch(locationsProvider);
    final isLoadingRoute = routeState.recommendation.isLoading;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppColors.primaryContainer,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.route_rounded, color: AppColors.primary, size: 20),
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  AppConstants.appName,
                  style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
                ),
                Text(
                  'Hello, ${user.username.split(' ').first}',
                  style: const TextStyle(fontSize: 11, color: AppColors.textSecondary, fontWeight: FontWeight.normal),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.tune_rounded, color: AppColors.primary),
            tooltip: 'Route Preferences & Weights',
            onPressed: () => context.push(AppRoutes.preferences),
          ),
          IconButton(
            icon: const Icon(Icons.account_circle_outlined, color: AppColors.textPrimary),
            onPressed: () => context.go(AppRoutes.profile),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 1. Campus Safety & AI Status Banner
              _buildCampusStatusBanner(context),
              const SizedBox(height: 16),

              // 2. Origin & Destination Selector Card
              Text(
                'Plan Your Journey',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.2,
                    ),
              ),
              const SizedBox(height: 8),
              LocationSelectorCard(
                origin: routeState.source,
                destination: routeState.destination,
                onSelectOrigin: () => context.push('${AppRoutes.search}?isOrigin=true'),
                onSelectDestination: () => context.push('${AppRoutes.search}?isOrigin=false'),
                onSwap: () => routeNotifier.swapLocations(),
              ),
              const SizedBox(height: 8),
              _buildGpsLocationAction(context, ref),
              const SizedBox(height: 16),

              // 3. Route Preferences Pills
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Optimization Goal',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  TextButton.icon(
                    onPressed: () => context.push(AppRoutes.preferences),
                    icon: const Icon(Icons.tune_rounded, size: 14),
                    label: const Text('Custom Weights', style: TextStyle(fontSize: 12)),
                    style: TextButton.styleFrom(visualDensity: VisualDensity.compact),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: AppConstants.preferences.map((pref) {
                    return PreferenceChip(
                      preference: pref,
                      isSelected: routeState.preference == pref && routeState.customWeights == null,
                      onSelected: (val) => routeNotifier.setPreference(val),
                    );
                  }).toList(),
                ),
              ),
              const SizedBox(height: 20),

              // 4. Primary CTA: Find Best Route Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: isLoadingRoute
                      ? null
                      : () async {
                          final result = await routeNotifier.findBestRoute();
                          if (context.mounted) {
                            if (result != null) {
                              context.push(AppRoutes.results);
                            } else if (routeState.recommendation.hasError) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(routeState.recommendation.error.toString()),
                                  backgroundColor: AppColors.error,
                                ),
                              );
                            }
                          }
                        },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: isLoadingRoute
                      ? const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2.5,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            ),
                            SizedBox(width: 12),
                            Text('Evaluating Multi-Objective Paths...'),
                          ],
                        )
                      : const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.directions_rounded, size: 22),
                            SizedBox(width: 10),
                            Text(
                              'Find Best Safe Route',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                ),
              ),
              const SizedBox(height: 24),

              // 5. Popular Campus Destinations Quick Pick
              Text(
                'Popular Destinations',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 10),
              locationsAsync.when(
                data: (locations) => _buildPopularDestinations(context, locations, routeNotifier),
                loading: () => const Center(child: Padding(padding: EdgeInsets.all(8), child: CircularProgressIndicator())),
                error: (_, __) => const SizedBox.shrink(),
              ),
              const SizedBox(height: 24),

              // 6. Navigation Hub Quick Cards (Map, Crowd Heatmap, History)
              Text(
                'Explore Campus',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildFeatureCard(
                      context,
                      title: 'Campus Map',
                      subtitle: 'Interactive OSM with 20 facility nodes',
                      icon: Icons.map_rounded,
                      color: AppColors.primary,
                      onTap: () => context.go(AppRoutes.map),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildFeatureCard(
                      context,
                      title: 'Crowd AI',
                      subtitle: 'Real-time Gradient Boosting predictions',
                      icon: Icons.analytics_rounded,
                      color: AppColors.secondary,
                      onTap: () => context.go(AppRoutes.crowd),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
      bottomNavigationBar: const CampusBottomNav(currentIndex: 0),
    );
  }

  Widget _buildCampusStatusBanner(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.primary,
            AppColors.primary.withBlue(180),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.18),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.security_rounded, color: Colors.white, size: 26),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: Color(0xFF00E676),
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 6),
                    const Text(
                      'AI Routing & Safety Engine Active',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  'Multi-objective optimization with dynamic crowd inference',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.85),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPopularDestinations(
    BuildContext context,
    List<CampusLocation> locations,
    RouteNotifier routeNotifier,
  ) {
    // Select popular nodes: Canteen (8), Library (4), CSE Block (6), Auditorium (10)
    final popular = locations.where((l) => [8, 4, 6, 10, 16].contains(l.id)).toList();

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: popular.map((loc) {
          return Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: ActionChip(
              avatar: const Icon(Icons.place_rounded, size: 16, color: AppColors.primary),
              label: Text(loc.name),
              onPressed: () {
                routeNotifier.setDestination(loc);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Destination set to: ${loc.name}'),
                    duration: const Duration(seconds: 1),
                  ),
                );
              },
              backgroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: const BorderSide(color: AppColors.border),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildFeatureCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: color.withOpacity(0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 24),
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGpsLocationAction(BuildContext context, WidgetRef ref) {
    final locationState = ref.watch(userLocationProvider);
    final locationNotifier = ref.read(userLocationProvider.notifier);

    if (locationState.isLoading) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: AppColors.border),
        ),
        child: const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            SizedBox(width: 10),
            Text(
              'Detecting current GPS location & nearest node...',
              style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
            ),
          ],
        ),
      );
    }

    if (locationState.isUsingGpsSource && locationState.result != null) {
      final res = locationState.result!;
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: AppColors.secondary.withOpacity(0.08),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: AppColors.secondary.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            const Icon(Icons.gps_fixed_rounded, color: AppColors.secondary, size: 16),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                'GPS Origin: Near ${res.nearestNode.name} (~${res.distanceToNodeM.toInt()}m)',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
              ),
            ),
            TextButton(
              onPressed: () {
                locationNotifier.clearGps();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Switched to manual origin selection')),
                );
              },
              child: const Text('Manual Mode', style: TextStyle(fontSize: 11)),
            ),
          ],
        ),
      );
    }

    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          side: const BorderSide(color: AppColors.border),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          backgroundColor: Colors.white,
        ),
        onPressed: () async {
          final outcome = await locationNotifier.detectLocationAndSnapSource(autoSetSource: true);
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(outcome.message),
                duration: Duration(seconds: outcome.success ? 2 : 4),
                action: outcome.success
                    ? null
                    : SnackBarAction(
                        label: 'Pick Manually',
                        onPressed: () => context.push('${AppRoutes.search}?isOrigin=true'),
                      ),
              ),
            );
          }
        },
        icon: const Icon(Icons.my_location_rounded, size: 16, color: AppColors.primary),
        label: const Text(
          'Use Current Location (Snap to Nearest Campus Node)',
          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
        ),
      ),
    );
  }
}

