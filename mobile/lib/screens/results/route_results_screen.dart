// SafeCampus AI — Route Results Screen
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/constants/app_constants.dart';
import '../../core/router/app_router.dart';
import '../../providers/route_provider.dart';
import '../../services/explanation_engine.dart';
import '../../theme/app_theme.dart';
import '../../widgets/metric_card.dart';
import '../../widgets/state_views.dart';

class RouteResultsScreen extends ConsumerWidget {
  const RouteResultsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final routeState = ref.watch(routeProvider);
    final rec = routeState.recommendation.valueOrNull;

    if (rec == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Route Results')),
        body: EmptyStateView(
          icon: Icons.alt_route_rounded,
          title: 'No Route Recommended Yet',
          message: 'Please choose starting and destination campus locations on the Home screen.',
          action: ElevatedButton(
            onPressed: () => context.go(AppRoutes.home),
            child: const Text('Go to Home'),
          ),
        ),
      );
    }

    final prefLabel = AppConstants.preferenceLabels[rec.preference] ?? rec.preference;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Recommended Route'),
        actions: [
          IconButton(
            icon: const Icon(Icons.map_rounded, color: AppColors.primary),
            tooltip: 'View on Campus Map',
            onPressed: () => context.go(AppRoutes.map),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Route Summary Banner
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.border),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.03),
                    blurRadius: 10,
                    offset: const Offset(0, 3),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.primaryContainer,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          'PREFERENCE: ${prefLabel.toUpperCase()}',
                          style: const TextStyle(
                            color: AppColors.primary,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      if (rec.usedMlCrowd)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppColors.secondaryContainer,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.auto_awesome_rounded, size: 12, color: AppColors.secondaryDark),
                              SizedBox(width: 4),
                              Text(
                                'AI Dynamic Crowd',
                                style: TextStyle(
                                  color: AppColors.secondaryDark,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      const Icon(Icons.trip_origin_rounded, color: AppColors.secondary, size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          rec.routeNames.first,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                      ),
                    ],
                  ),
                  Padding(
                    padding: const EdgeInsets.only(left: 8.0, top: 4, bottom: 4),
                    child: Container(width: 2, height: 16, color: AppColors.border),
                  ),
                  Row(
                    children: [
                      const Icon(Icons.location_on_rounded, color: AppColors.error, size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          rec.routeNames.last,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // 1b. Dynamic AI Recommendation Summary Banner
            Builder(
              builder: (context) {
                final exp = RouteExplanationEngine.generate(
                  recommendation: rec,
                  dijkstraBaseline: routeState.dijkstraBaseline,
                );
                return InkWell(
                  onTap: () => context.push(AppRoutes.explanation),
                  borderRadius: BorderRadius.circular(14),
                  child: Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: AppColors.primaryContainer.withOpacity(0.45),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppColors.primary.withOpacity(0.25)),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.auto_awesome_rounded, color: AppColors.primary, size: 20),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                exp.summary,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 13,
                                  color: AppColors.primaryDark,
                                  height: 1.3,
                                ),
                              ),
                              const SizedBox(height: 4),
                              const Row(
                                children: [
                                  Text(
                                    'View dynamic trade-offs & Pareto proof',
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: AppColors.primary,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  SizedBox(width: 4),
                                  Icon(Icons.arrow_forward_rounded, size: 12, color: AppColors.primary),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
            const SizedBox(height: 16),

            // 2. Metrics Grid
            Text(
              'Multi-Objective Evaluation',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: MetricCard(
                    icon: Icons.straighten_rounded,
                    iconColor: AppColors.primary,
                    label: 'Distance',
                    value: '${rec.distanceM.toInt()} m',
                    subtitle: 'Walking distance',
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: MetricCard(
                    icon: Icons.timer_outlined,
                    iconColor: AppColors.warning,
                    label: 'Travel Time',
                    value: '${rec.travelTimeMin.toStringAsFixed(1)} min',
                    subtitle: 'Estimated walk',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: MetricCard(
                    icon: Icons.shield_rounded,
                    iconColor: AppColors.success,
                    label: 'Safety Score',
                    value: '${(rec.safetyScore * 100).toInt()}%',
                    subtitle: 'Well-lit & secure',
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: MetricCard(
                    icon: Icons.groups_rounded,
                    iconColor: _getCrowdMetricColor(rec.crowdLevel),
                    label: 'Crowd Density',
                    value: rec.crowdLevel,
                    subtitle: 'Exposure: ${(rec.crowdScore * 100).toInt()}%',
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: MetricCard(
                    icon: Icons.accessible_rounded,
                    iconColor: AppColors.accent,
                    label: 'Access',
                    value: '${(rec.accessibilityScore * 100).toInt()}%',
                    subtitle: 'Ramp-friendly',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // 3. Technical Research Footprint
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Optimization Cost: ${rec.totalCost.toStringAsFixed(4)}',
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.textSecondary),
                  ),
                  Text(
                    'Search Time: ${rec.executionTimeMs.toStringAsFixed(2)} ms',
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // 4. Primary Actions (Start Navigation, Explanation)
            Row(
              children: [
                Expanded(
                  flex: 3,
                  child: SizedBox(
                    height: 50,
                    child: ElevatedButton.icon(
                      onPressed: () => context.push(AppRoutes.navigation),
                      icon: const Icon(Icons.navigation_rounded),
                      label: const Text('Start Navigation', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  flex: 2,
                  child: SizedBox(
                    height: 50,
                    child: OutlinedButton.icon(
                      onPressed: () => context.push(AppRoutes.explanation),
                      icon: const Icon(Icons.insights_rounded, size: 18),
                      label: const Text('Why This?'),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Alternative Candidate Routes
            if (rec.alternatives.isNotEmpty) ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Alternative Candidate Routes (${rec.alternatives.length})',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  TextButton.icon(
                    onPressed: () => context.go(AppRoutes.map),
                    icon: const Icon(Icons.map_rounded, size: 16),
                    label: const Text('View on Map', style: TextStyle(fontSize: 12)),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              ...rec.alternatives.asMap().entries.map((entry) {
                final idx = entry.key + 1;
                final alt = entry.value;
                final isSelected = routeState.selectedRouteIndex == idx;
                return Container(
                  margin: const EdgeInsets.only(bottom: 10),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: isSelected ? AppColors.primary : AppColors.border,
                      width: isSelected ? 2 : 1,
                    ),
                  ),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 18,
                        backgroundColor: (idx == 1 ? const Color(0xFFE65100) : const Color(0xFF00897B)).withOpacity(0.15),
                        child: Icon(
                          Icons.alt_route_rounded,
                          color: idx == 1 ? const Color(0xFFE65100) : const Color(0xFF00897B),
                          size: 18,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              alt.label,
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              '${alt.distanceM.toInt()}m • ${alt.travelTimeMin.toStringAsFixed(1)} min • Safety ${(alt.safetyScore * 100).toInt()}% • ${alt.crowdLevel} Crowd',
                              style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                            ),
                          ],
                        ),
                      ),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: isSelected ? AppColors.primary : AppColors.surfaceVariant,
                          foregroundColor: isSelected ? Colors.white : AppColors.textPrimary,
                          elevation: isSelected ? 2 : 0,
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          minimumSize: const Size(60, 32),
                        ),
                        onPressed: () {
                          ref.read(routeProvider.notifier).selectRouteIndex(isSelected ? 0 : idx);
                        },
                        child: Text(isSelected ? 'Selected' : 'Select', style: const TextStyle(fontSize: 11)),
                      ),
                    ],
                  ),
                );
              }),
              const SizedBox(height: 16),
            ],

            // 5. Turn-by-Turn Waypoints Sequence
            Text(
              'Waypoint Sequence (${rec.routeNames.length} Nodes)',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.border),
              ),
              child: ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: rec.routeNames.length,
                separatorBuilder: (_, __) => const Divider(height: 1, indent: 48),
                itemBuilder: (context, index) {
                  final isFirst = index == 0;
                  final isLast = index == rec.routeNames.length - 1;
                  final name = rec.routeNames[index];
                  final nodeId = rec.route[index];

                  return ListTile(
                    leading: CircleAvatar(
                      radius: 14,
                      backgroundColor: isFirst
                          ? AppColors.secondary
                          : (isLast ? AppColors.error : AppColors.primaryContainer),
                      child: Text(
                        '${index + 1}',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: isFirst || isLast ? Colors.white : AppColors.primary,
                        ),
                      ),
                    ),
                    title: Text(
                      name,
                      style: TextStyle(
                        fontWeight: isFirst || isLast ? FontWeight.bold : FontWeight.w500,
                        fontSize: 14,
                      ),
                    ),
                    subtitle: Text('Campus Node #$nodeId', style: const TextStyle(fontSize: 11)),
                    trailing: isFirst
                        ? const Text('START', style: TextStyle(color: AppColors.secondary, fontWeight: FontWeight.bold, fontSize: 11))
                        : (isLast
                            ? const Text('DEST', style: TextStyle(color: AppColors.error, fontWeight: FontWeight.bold, fontSize: 11))
                            : const Icon(Icons.arrow_forward_ios_rounded, size: 12, color: AppColors.textMuted)),
                  );
                },
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Color _getCrowdMetricColor(String level) {
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
