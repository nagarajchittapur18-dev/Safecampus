// SafeCampus AI — Profile & Accessibility Settings Screen
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/constants/app_constants.dart';
import '../../core/router/app_router.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';
import '../../widgets/campus_bottom_nav.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  bool _isTestingBackend = false;
  String? _backendHealthStatus;

  Future<void> _pingBackend() async {
    setState(() {
      _isTestingBackend = true;
      _backendHealthStatus = null;
    });

    final api = ref.read(apiServiceProvider);
    final ok = await api.checkHealth();

    if (!mounted) return;

    setState(() {
      _isTestingBackend = false;
      _backendHealthStatus = ok ? 'Connected • Fast & Operational (HTTP 200 OK)' : 'Failed to reach backend';
    });
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authProvider);
    final authNotifier = ref.read(authProvider.notifier);
    final isGuest = user.id == 0;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Profile & Settings'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. User Profile Header Card
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.border),
              ),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 30,
                    backgroundColor: AppColors.primaryContainer,
                    child: Icon(
                      isGuest ? Icons.person_outline_rounded : Icons.person_rounded,
                      size: 36,
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          user.username,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          user.email.isNotEmpty ? user.email : 'Campus Visitor',
                          style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                        ),
                        const SizedBox(height: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.surfaceVariant,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            user.role.toUpperCase(),
                            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.primary),
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (isGuest)
                    OutlinedButton(
                      onPressed: () => context.push(AppRoutes.login),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      child: const Text('Log In'),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // 2. Mobility & Accessibility Preferences
            Text(
              'Mobility & Accessibility Preferences',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              'Enforces physical accessibility constraints on all generated routes.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 10),

            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.border),
              ),
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text('Prefer Wheelchair Ramps', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                    subtitle: const Text('Prioritizes routes that have certified incline ramps', style: TextStyle(fontSize: 12)),
                    value: user.preferRamps,
                    activeColor: AppColors.secondary,
                    onChanged: (val) => authNotifier.updateMobilityPreferences(preferRamps: val),
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('Avoid Staircases', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                    subtitle: const Text('Eliminates steep outdoor stairs from recommended paths', style: TextStyle(fontSize: 12)),
                    value: user.avoidStairs,
                    activeColor: AppColors.secondary,
                    onChanged: (val) => authNotifier.updateMobilityPreferences(avoidStairs: val),
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('High Contrast Map View', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                    subtitle: const Text('Enhances route visibility for visually impaired users', style: TextStyle(fontSize: 12)),
                    value: user.highContrastMap,
                    activeColor: AppColors.secondary,
                    onChanged: (val) => authNotifier.updateMobilityPreferences(highContrastMap: val),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // 3. Backend & AI Framework Diagnostics
            Text(
              'Backend & Framework Diagnostics',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),

            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.border),
              ),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('API Base URL', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                      Text(
                        AppConstants.apiBaseUrl,
                        style: const TextStyle(fontFamily: 'monospace', fontSize: 11, color: AppColors.textSecondary),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: _isTestingBackend ? null : _pingBackend,
                      icon: _isTestingBackend
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.network_check_rounded, size: 18),
                      label: const Text('Test FastAPI Server Connection'),
                    ),
                  ),
                  if (_backendHealthStatus != null) ...[
                    const SizedBox(height: 10),
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: _backendHealthStatus!.contains('Connected')
                            ? AppColors.secondaryContainer.withOpacity(0.5)
                            : AppColors.error.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            _backendHealthStatus!.contains('Connected') ? Icons.check_circle_rounded : Icons.error_rounded,
                            size: 16,
                            color: _backendHealthStatus!.contains('Connected') ? AppColors.success : AppColors.error,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              _backendHealthStatus!,
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: _backendHealthStatus!.contains('Connected') ? AppColors.success : AppColors.error,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 24),

            // 4. Academic Citation & Info
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant,
                borderRadius: BorderRadius.circular(14),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'SafeCampus AI — Academic Framework',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                  SizedBox(height: 4),
                  Text(
                    AppConstants.academicCitation,
                    style: TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: AppColors.textSecondary),
                  ),
                  SizedBox(height: 6),
                  Text(
                    'Zero-cost open source research implementation using OpenStreetMap and Gradient Boosting ML.',
                    style: TextStyle(fontSize: 10, color: AppColors.textMuted),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // 5. Logout Button (if authenticated)
            if (!isGuest)
              SizedBox(
                width: double.infinity,
                child: TextButton.icon(
                  onPressed: () {
                    authNotifier.logout();
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Logged out.')),
                    );
                  },
                  icon: const Icon(Icons.logout_rounded, color: AppColors.error, size: 18),
                  label: const Text('Log Out', style: TextStyle(color: AppColors.error, fontWeight: FontWeight.bold)),
                ),
              ),
            const SizedBox(height: 20),
          ],
        ),
      ),
      bottomNavigationBar: const CampusBottomNav(currentIndex: 4),
    );
  }
}
