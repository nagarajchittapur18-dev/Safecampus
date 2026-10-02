// SafeCampus AI — Score & Status Badges
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class CrowdBadge extends StatelessWidget {
  final String level;
  final double? score;

  const CrowdBadge({
    super.key,
    required this.level,
    this.score,
  });

  @override
  Widget build(BuildContext context) {
    Color color;
    IconData icon;
    String displayLabel;

    switch (level.toUpperCase()) {
      case 'LOW':
        color = AppColors.crowdLow;
        icon = Icons.people_outline_rounded;
        displayLabel = 'Low Crowd';
        break;
      case 'MEDIUM':
        color = AppColors.crowdMedium;
        icon = Icons.people_alt_rounded;
        displayLabel = 'Moderate';
        break;
      case 'HIGH':
        color = AppColors.crowdHigh;
        icon = Icons.groups_rounded;
        displayLabel = 'Heavy Crowd';
        break;
      case 'VERY_HIGH':
      default:
        color = AppColors.crowdVeryHigh;
        icon = Icons.warning_amber_rounded;
        displayLabel = 'Very Crowded';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 5),
          Text(
            score != null ? '$displayLabel (${(score! * 100).toInt()}%)' : displayLabel,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

class SafetyBadge extends StatelessWidget {
  final double score;

  const SafetyBadge({super.key, required this.score});

  @override
  Widget build(BuildContext context) {
    final pct = (score * 100).toInt();
    final color = score >= 0.75
        ? AppColors.success
        : (score >= 0.5 ? AppColors.warning : AppColors.error);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.shield_rounded, size: 14, color: color),
          const SizedBox(width: 5),
          Text(
            'Safety: $pct%',
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

class AccessibilityBadge extends StatelessWidget {
  final double score;

  const AccessibilityBadge({super.key, required this.score});

  @override
  Widget build(BuildContext context) {
    final pct = (score * 100).toInt();
    final color = score >= 0.7 ? AppColors.primary : AppColors.warning;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.accessible_rounded, size: 14, color: color),
          const SizedBox(width: 5),
          Text(
            'Access: $pct%',
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}
