// SafeCampus AI — Preference Chip Selector
import 'package:flutter/material.dart';
import '../core/constants/app_constants.dart';
import '../theme/app_theme.dart';

class PreferenceChip extends StatelessWidget {
  final String preference;
  final bool isSelected;
  final ValueChanged<String> onSelected;

  const PreferenceChip({
    super.key,
    required this.preference,
    required this.isSelected,
    required this.onSelected,
  });

  IconData get _icon {
    switch (preference) {
      case AppConstants.prefSafest:
        return Icons.shield_rounded;
      case AppConstants.prefFastest:
        return Icons.bolt_rounded;
      case AppConstants.prefShortest:
        return Icons.straighten_rounded;
      case AppConstants.prefLeastCrowded:
        return Icons.people_outline_rounded;
      case AppConstants.prefAccessible:
        return Icons.accessible_rounded;
      case AppConstants.prefBalanced:
      default:
        return Icons.balance_rounded;
    }
  }

  Color get _color {
    switch (preference) {
      case AppConstants.prefSafest:
        return AppColors.success;
      case AppConstants.prefFastest:
        return AppColors.warning;
      case AppConstants.prefShortest:
        return AppColors.primary;
      case AppConstants.prefLeastCrowded:
        return AppColors.secondary;
      case AppConstants.prefAccessible:
        return AppColors.accent;
      case AppConstants.prefBalanced:
      default:
        return AppColors.primary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final label = AppConstants.preferenceLabels[preference] ?? preference;

    return Padding(
      padding: const EdgeInsets.only(right: 8.0),
      child: FilterChip(
        avatar: Icon(
          _icon,
          size: 16,
          color: isSelected ? Colors.white : _color,
        ),
        label: Text(label),
        selected: isSelected,
        onSelected: (_) => onSelected(preference),
        selectedColor: _color,
        backgroundColor: Colors.white,
        checkmarkColor: Colors.white,
        showCheckmark: false,
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(
            color: isSelected ? _color : AppColors.border,
            width: isSelected ? 1.5 : 1.0,
          ),
        ),
        labelStyle: TextStyle(
          color: isSelected ? Colors.white : AppColors.textPrimary,
          fontSize: 13,
          fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
        ),
      ),
    );
  }
}
