// SafeCampus AI — Turn-by-Turn Navigation Screen (Simulated Guidance)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/route_provider.dart';
import '../../theme/app_theme.dart';

class NavigationScreen extends ConsumerWidget {
  const NavigationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final routeState = ref.watch(routeProvider);
    final routeNotifier = ref.read(routeProvider.notifier);
    final rec = routeState.recommendation.valueOrNull;

    if (rec == null || rec.routeNames.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: const Text('Navigation')),
        body: const Center(child: Text('No active route to navigate.')),
      );
    }

    final currentIndex = routeState.navigationIndex;
    final totalSteps = rec.routeNames.length;
    final isArrived = currentIndex >= totalSteps - 1;
    final currentNodeName = rec.routeNames[currentIndex];
    final nextNodeName = !isArrived ? rec.routeNames[currentIndex + 1] : null;

    final stepProgress = (currentIndex + 1) / totalSteps;

    // Remaining distance calculation estimate
    final remainingPct = (totalSteps - 1 - currentIndex) / (totalSteps - 1 > 0 ? totalSteps - 1 : 1);
    final remainingDist = (rec.distanceM * remainingPct).toInt();
    final remainingTime = (rec.travelTimeMin * remainingPct).toStringAsFixed(1);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Live Campus Guidance'),
        leading: IconButton(
          icon: const Icon(Icons.close_rounded),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // 1. Top Turn Banner
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
              decoration: const BoxDecoration(
                color: AppColors.primary,
                boxShadow: [
                  BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, 4)),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Icon(
                          isArrived ? Icons.flag_rounded : Icons.straight_rounded,
                          size: 36,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              isArrived ? 'You have reached your destination!' : 'Head towards',
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.85),
                                fontSize: 13,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              isArrived ? currentNodeName : nextNodeName!,
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 20,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: stepProgress,
                      backgroundColor: Colors.white.withOpacity(0.2),
                      valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF00E676)),
                      minHeight: 6,
                    ),
                  ),
                ],
              ),
            ),

            // 2. Middle Body: Waypoint Timeline & Safety Advisory
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Status Badge Card
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppColors.border),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildStatColumn('REMAINING DIST', '$remainingDist m', Icons.straighten_rounded),
                          Container(width: 1, height: 36, color: AppColors.border),
                          _buildStatColumn('EST. TIME', '$remainingTime min', Icons.schedule_rounded),
                          Container(width: 1, height: 36, color: AppColors.border),
                          _buildStatColumn('STEP', '${currentIndex + 1}/$totalSteps', Icons.pin_drop_rounded),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Active Safety & Advisory
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppColors.secondaryContainer.withOpacity(0.6),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppColors.secondary.withOpacity(0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.verified_user_rounded, color: AppColors.secondary, size: 28),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Safe Route Recommendation Active',
                                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppColors.secondaryDark),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  'Current segment safety score is ${(rec.safetyScore * 100).toInt()}%. Well-lit with CCTV coverage.',
                                  style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Next Waypoints preview
                    Text(
                      'Upcoming Steps',
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 10),

                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: totalSteps,
                      itemBuilder: (context, i) {
                        final isPassed = i < currentIndex;
                        final isCurrent = i == currentIndex;

                        return ListTile(
                          contentPadding: EdgeInsets.zero,
                          leading: CircleAvatar(
                            radius: 12,
                            backgroundColor: isPassed
                                ? AppColors.success
                                : (isCurrent ? AppColors.primary : AppColors.border),
                            child: isPassed
                                ? const Icon(Icons.check, size: 14, color: Colors.white)
                                : Text(
                                    '${i + 1}',
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                      color: isCurrent ? Colors.white : AppColors.textSecondary,
                                    ),
                                  ),
                          ),
                          title: Text(
                            rec.routeNames[i],
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                              color: isPassed ? AppColors.textMuted : AppColors.textPrimary,
                            ),
                          ),
                          subtitle: isCurrent
                              ? const Text('Current Location', style: TextStyle(color: AppColors.primary, fontSize: 11, fontWeight: FontWeight.bold))
                              : null,
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),

            // 3. Navigation Controls (Simulate advancement)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              decoration: const BoxDecoration(
                color: Colors.white,
                border: Border(top: BorderSide(color: AppColors.border)),
              ),
              child: Row(
                children: [
                  OutlinedButton.icon(
                    onPressed: currentIndex > 0 ? () => routeNotifier.previousNavigationStep() : null,
                    icon: const Icon(Icons.arrow_back_rounded, size: 16),
                    label: const Text('Back'),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: isArrived
                          ? () => Navigator.of(context).pop()
                          : () => routeNotifier.nextNavigationStep(),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: isArrived ? AppColors.success : AppColors.primary,
                      ),
                      icon: Icon(isArrived ? Icons.check_circle_rounded : Icons.arrow_forward_rounded),
                      label: Text(
                        isArrived ? 'Finish Navigation' : 'Next Step (${currentIndex + 2}/$totalSteps)',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatColumn(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 18, color: AppColors.textSecondary),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        const SizedBox(height: 2),
        Text(label, style: const TextStyle(fontSize: 9, color: AppColors.textMuted, fontWeight: FontWeight.bold)),
      ],
    );
  }
}
