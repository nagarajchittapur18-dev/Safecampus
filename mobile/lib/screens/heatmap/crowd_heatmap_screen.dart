// SafeCampus AI — Crowd Heatmap & Prediction Screen
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/router/app_router.dart';
import '../../providers/crowd_provider.dart';
import '../../providers/locations_provider.dart';
import '../../providers/route_provider.dart';
import '../../theme/app_theme.dart';
import '../../widgets/campus_bottom_nav.dart';
import '../../widgets/score_badge.dart';
import '../../widgets/state_views.dart';

class CrowdHeatmapScreen extends ConsumerWidget {
  const CrowdHeatmapScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedHour = ref.watch(selectedHeatmapHourProvider);
    final crowdMapAsync = ref.watch(crowdHeatmapProvider);
    final locationsAsync = ref.watch(locationsProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Campus Crowd AI'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Refresh Predictions',
            onPressed: () => ref.refresh(crowdHeatmapProvider),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Time-of-Day Simulation Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Time-of-Day Prediction Slider',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.primaryContainer,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          '${selectedHour.toString().padLeft(2, '0')}:00',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: AppColors.primary,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Slider(
                    value: selectedHour.toDouble(),
                    min: 0,
                    max: 23,
                    divisions: 23,
                    activeColor: AppColors.primary,
                    label: '${selectedHour.toString().padLeft(2, '0')}:00',
                    onChanged: (val) {
                      ref.read(selectedHeatmapHourProvider.notifier).state = val.round();
                    },
                  ),
                  const SizedBox(height: 8),

                  // Quick Rush Hour Buttons
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        _buildQuickHourChip(ref, 'Morning (09:00)', 9, selectedHour),
                        _buildQuickHourChip(ref, 'Lunch Rush (13:00)', 13, selectedHour),
                        _buildQuickHourChip(ref, 'Evening Rush (17:00)', 17, selectedHour),
                        _buildQuickHourChip(ref, 'Night (21:00)', 21, selectedHour),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // 2. Machine Learning Model Banner
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.secondaryContainer.withOpacity(0.5),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.secondary.withOpacity(0.3)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.psychology_rounded, color: AppColors.secondary, size: 22),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Model: Gradient Boosting Classifier • Dynamic Node Density',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.secondaryDark),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // 3. Facility Density Breakdown List
            Text(
              'Location Density Predictions',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),

            crowdMapAsync.when(
              data: (crowdMap) {
                return locationsAsync.when(
                  data: (locations) {
                    return ListView.separated(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: locations.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final loc = locations[index];
                        final pred = crowdMap[loc.id];
                        final level = pred?.predictedCrowdLevel ?? 'LOW';
                        final score = pred?.predictedCrowdScore ?? 0.2;

                        return Container(
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: AppColors.border),
                          ),
                          child: ListTile(
                            leading: Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: _getCrowdColor(level).withOpacity(0.12),
                                shape: BoxShape.circle,
                              ),
                              child: Icon(Icons.people_alt_rounded, color: _getCrowdColor(level), size: 20),
                            ),
                            title: Text(
                              loc.name,
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                            ),
                            subtitle: Text(
                              'Type: ${loc.locationType.toUpperCase()} • Confidence: ${((pred?.confidence ?? 0.85) * 100).toInt()}%',
                              style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                            ),
                            trailing: CrowdBadge(level: level, score: score),
                            onTap: () {
                              ref.read(routeProvider.notifier).setDestination(loc);
                              context.go(AppRoutes.home);
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Set ${loc.name} as Destination on Home')),
                              );
                            },
                          ),
                        );
                      },
                    );
                  },
                  loading: () => const LoadingStateView(message: 'Loading locations...'),
                  error: (e, _) => Text('Error: $e'),
                );
              },
              loading: () => const LoadingStateView(message: 'Running ML crowd inference for 20 facilities...'),
              error: (err, _) => ErrorStateView(
                message: 'Crowd model error: $err',
                onRetry: () => ref.refresh(crowdHeatmapProvider),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: const CampusBottomNav(currentIndex: 2),
    );
  }

  Widget _buildQuickHourChip(WidgetRef ref, String label, int hour, int current) {
    final isSelected = current == hour;
    return Padding(
      padding: const EdgeInsets.only(right: 6.0),
      child: ActionChip(
        label: Text(label),
        onPressed: () {
          ref.read(selectedHeatmapHourProvider.notifier).state = hour;
        },
        backgroundColor: isSelected ? AppColors.primary : AppColors.surfaceVariant,
        labelStyle: TextStyle(
          color: isSelected ? Colors.white : AppColors.textPrimary,
          fontSize: 11,
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
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
}
