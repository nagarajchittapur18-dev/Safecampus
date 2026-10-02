// SafeCampus AI — Route History Screen
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../core/constants/app_constants.dart';
import '../../core/router/app_router.dart';
import '../../models/campus_location.dart';
import '../../models/route_history_item.dart';
import '../../providers/history_provider.dart';
import '../../providers/locations_provider.dart';
import '../../providers/route_provider.dart';
import '../../theme/app_theme.dart';
import '../../widgets/campus_bottom_nav.dart';
import '../../widgets/state_views.dart';

class RouteHistoryScreen extends ConsumerWidget {
  const RouteHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final history = ref.watch(historyProvider);
    final historyNotifier = ref.read(historyProvider.notifier);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Route History'),
        actions: [
          if (history.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_outline_rounded),
              tooltip: 'Clear History',
              onPressed: () => _confirmClearHistory(context, historyNotifier),
            ),
        ],
      ),
      body: history.isEmpty
          ? EmptyStateView(
              icon: Icons.history_rounded,
              title: 'No Route History Yet',
              message: 'Your calculated multi-objective campus routes will appear here for fast replay.',
              action: ElevatedButton(
                onPressed: () => context.go(AppRoutes.home),
                child: const Text('Find a Route'),
              ),
            )
          : ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: history.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final item = history[index];
                return _buildHistoryCard(context, ref, item);
              },
            ),
      bottomNavigationBar: const CampusBottomNav(currentIndex: 3),
    );
  }

  Widget _buildHistoryCard(BuildContext context, WidgetRef ref, RouteHistoryItem item) {
    final dateFormat = DateFormat('MMM dd, hh:mm a');
    final prefLabel = AppConstants.preferenceLabels[item.preference] ?? item.preference;

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.primaryContainer,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  prefLabel.toUpperCase(),
                  style: const TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: AppColors.primary,
                  ),
                ),
              ),
              Text(
                dateFormat.format(item.timestamp),
                style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Origin -> Destination
          Row(
            children: [
              const Icon(Icons.trip_origin_rounded, size: 16, color: AppColors.secondary),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  item.sourceName,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                ),
              ),
            ],
          ),
          Padding(
            padding: const EdgeInsets.only(left: 7.0, top: 2, bottom: 2),
            child: Container(width: 2, height: 12, color: AppColors.border),
          ),
          Row(
            children: [
              const Icon(Icons.location_on_rounded, size: 16, color: AppColors.error),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  item.destinationName,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(height: 1),
          const SizedBox(height: 10),

          // Metrics row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${item.distanceM.toInt()}m • ${item.travelTimeMin.toStringAsFixed(1)} min • Safety ${(item.safetyScore * 100).toInt()}%',
                style: const TextStyle(fontSize: 12, color: AppColors.textSecondary, fontWeight: FontWeight.w500),
              ),
              TextButton.icon(
                onPressed: () => _replayRoute(context, ref, item),
                icon: const Icon(Icons.replay_rounded, size: 16),
                label: const Text('Re-run', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                style: TextButton.styleFrom(visualDensity: VisualDensity.compact),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _replayRoute(BuildContext context, WidgetRef ref, RouteHistoryItem item) {
    final routeNotifier = ref.read(routeProvider.notifier);
    final locations = ref.read(locationsProvider).valueOrNull ?? [];

    CampusLocation? src;
    CampusLocation? dst;

    try {
      src = locations.firstWhere((l) => l.id == item.sourceId);
      dst = locations.firstWhere((l) => l.id == item.destinationId);
    } catch (_) {}

    if (src != null && dst != null) {
      routeNotifier.setSource(src);
      routeNotifier.setDestination(dst);
      routeNotifier.setPreference(item.preference);
      routeNotifier.findBestRoute().then((rec) {
        if (context.mounted && rec != null) {
          context.push(AppRoutes.results);
        }
      });
    } else {
      context.go(AppRoutes.home);
    }
  }

  void _confirmClearHistory(BuildContext context, HistoryNotifier notifier) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Clear Route History?'),
        content: const Text('This will remove all saved route recommendation entries.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              notifier.clearAll();
              Navigator.pop(ctx);
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
            child: const Text('Clear All'),
          ),
        ],
      ),
    );
  }
}
