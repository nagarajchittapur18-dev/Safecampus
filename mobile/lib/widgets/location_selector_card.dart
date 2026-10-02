// SafeCampus AI — Origin / Destination Selector Card
import 'package:flutter/material.dart';
import '../models/campus_location.dart';
import '../theme/app_theme.dart';

class LocationSelectorCard extends StatelessWidget {
  final CampusLocation? origin;
  final CampusLocation? destination;
  final VoidCallback onSelectOrigin;
  final VoidCallback onSelectDestination;
  final VoidCallback onSwap;

  const LocationSelectorCard({
    super.key,
    required this.origin,
    required this.destination,
    required this.onSelectOrigin,
    required this.onSelectDestination,
    required this.onSwap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.border),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            // Left: Connecting line with origin and dest indicators
            Column(
              children: [
                const Icon(Icons.radio_button_checked_rounded, color: AppColors.secondary, size: 20),
                Container(
                  width: 2,
                  height: 28,
                  color: AppColors.border,
                  margin: const EdgeInsets.symmetric(vertical: 4),
                ),
                const Icon(Icons.location_on_rounded, color: AppColors.error, size: 20),
              ],
            ),
            const SizedBox(width: 14),

            // Middle: Origin & Destination clickable rows
            Expanded(
              child: Column(
                children: [
                  // From
                  InkWell(
                    onTap: onSelectOrigin,
                    borderRadius: BorderRadius.circular(8),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'STARTING POINT',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.secondaryDark,
                                  letterSpacing: 0.5,
                                ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            origin?.name ?? 'Select origin location',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                  color: origin != null ? AppColors.textPrimary : AppColors.textMuted,
                                  fontWeight: FontWeight.w600,
                                ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const Divider(height: 12, color: AppColors.divider),

                  // To
                  InkWell(
                    onTap: onSelectDestination,
                    borderRadius: BorderRadius.circular(8),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'DESTINATION',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.error,
                                  letterSpacing: 0.5,
                                ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            destination?.name ?? 'Select campus destination',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                  color: destination != null ? AppColors.textPrimary : AppColors.textMuted,
                                  fontWeight: FontWeight.w600,
                                ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Right: Swap button
            IconButton(
              icon: Container(
                padding: const EdgeInsets.all(8),
                decoration: const BoxDecoration(
                  color: AppColors.surfaceVariant,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.swap_vert_rounded, color: AppColors.primary, size: 20),
              ),
              onPressed: onSwap,
              tooltip: 'Swap locations',
            ),
          ],
        ),
      ),
    );
  }
}
