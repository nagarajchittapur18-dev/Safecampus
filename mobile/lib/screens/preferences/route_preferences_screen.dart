// SafeCampus AI — Route Preferences & Weight Configuration Screen
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/constants/app_constants.dart';
import '../../providers/route_provider.dart';
import '../../theme/app_theme.dart';

class RoutePreferencesScreen extends ConsumerStatefulWidget {
  const RoutePreferencesScreen({super.key});

  @override
  ConsumerState<RoutePreferencesScreen> createState() => _RoutePreferencesScreenState();
}

class _RoutePreferencesScreenState extends ConsumerState<RoutePreferencesScreen> {
  // Custom weights local state
  late double _wD;
  late double _wT;
  late double _wC;
  late double _wS;
  late double _wA;
  bool _useCustomWeights = false;

  // Temporal simulator local state
  int _simulationHour = DateTime.now().hour;
  bool _hasEvent = false;
  bool _classInSession = true;
  bool _examPeriod = false;
  bool _useMlCrowd = true;

  @override
  void initState() {
    super.initState();
    final routeState = ref.read(routeProvider);

    final weights = routeState.customWeights;
    if (weights != null) {
      _useCustomWeights = true;
      _wD = weights['wD'] ?? 0.2;
      _wT = weights['wT'] ?? 0.2;
      _wC = weights['wC'] ?? 0.2;
      _wS = weights['wS'] ?? 0.2;
      _wA = weights['wA'] ?? 0.2;
    } else {
      _useCustomWeights = false;
      _wD = 0.2;
      _wT = 0.2;
      _wC = 0.2;
      _wS = 0.2;
      _wA = 0.2;
    }

    _simulationHour = routeState.simulationHour ?? DateTime.now().hour;
    _hasEvent = routeState.eventFlag == 1;
    _classInSession = routeState.classActivity != 0;
    _examPeriod = routeState.examFlag == 1;
    _useMlCrowd = routeState.useMlCrowd;
  }

  double get _totalWeight => _wD + _wT + _wC + _wS + _wA;

  void _normalizeWeights() {
    final sum = _totalWeight;
    if (sum > 0) {
      setState(() {
        _wD = double.parse((_wD / sum).toStringAsFixed(2));
        _wT = double.parse((_wT / sum).toStringAsFixed(2));
        _wC = double.parse((_wC / sum).toStringAsFixed(2));
        _wS = double.parse((_wS / sum).toStringAsFixed(2));
        _wA = double.parse((1.0 - (_wD + _wT + _wC + _wS)).toStringAsFixed(2));
      });
    }
  }

  void _applySettings() {
    final notifier = ref.read(routeProvider.notifier);

    if (_useCustomWeights) {
      _normalizeWeights();
      notifier.setCustomWeights({
        'wD': _wD,
        'wT': _wT,
        'wC': _wC,
        'wS': _wS,
        'wA': _wA,
      });
    }

    notifier.setSimulationHour(_simulationHour);
    notifier.setEventFlag(_hasEvent ? 1 : 0);
    notifier.setClassActivity(_classInSession ? 1 : 0);
    notifier.setExamFlag(_examPeriod ? 1 : 0);
    notifier.setUseMlCrowd(_useMlCrowd);

    Navigator.of(context).pop();

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Preferences applied successfully!'),
        backgroundColor: AppColors.success,
        duration: Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final routeState = ref.watch(routeProvider);
    final routeNotifier = ref.read(routeProvider.notifier);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Route Preferences'),
        actions: [
          TextButton(
            onPressed: _applySettings,
            child: const Text('Save', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Presets Header
            Text(
              'Optimization Presets',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              'Select a preset to automatically apply mathematically verified objective weights.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 12),

            // Preset Cards
            ...AppConstants.preferences.map((pref) {
              final isSelected = !_useCustomWeights && routeState.preference == pref;
              return _buildPresetTile(
                pref: pref,
                isSelected: isSelected,
                onTap: () {
                  setState(() => _useCustomWeights = false);
                  routeNotifier.setPreference(pref);
                },
              );
            }),
            const SizedBox(height: 24),

            // 2. Custom Weights Section
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: _useCustomWeights ? AppColors.primary : AppColors.border),
              ),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.tune_rounded,
                            color: _useCustomWeights ? AppColors.primary : AppColors.textSecondary,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          const Text(
                            'Custom Weights (wD, wT, wC, wS, wA)',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                          ),
                        ],
                      ),
                      Switch(
                        value: _useCustomWeights,
                        activeColor: AppColors.primary,
                        onChanged: (val) {
                          setState(() => _useCustomWeights = val);
                        },
                      ),
                    ],
                  ),
                  if (_useCustomWeights) ...[
                    const Divider(height: 20),
                    _buildWeightSlider('Distance (wD)', _wD, (v) => setState(() => _wD = v)),
                    _buildWeightSlider('Travel Time (wT)', _wT, (v) => setState(() => _wT = v)),
                    _buildWeightSlider('Crowd Avoidance (wC)', _wC, (v) => setState(() => _wC = v)),
                    _buildWeightSlider('Safety Level (wS)', _wS, (v) => setState(() => _wS = v)),
                    _buildWeightSlider('Accessibility (wA)', _wA, (v) => setState(() => _wA = v)),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Sum of Weights: ${_totalWeight.toStringAsFixed(2)} / 1.00',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: (_totalWeight - 1.0).abs() < 0.05 ? AppColors.success : AppColors.error,
                          ),
                        ),
                        TextButton.icon(
                          onPressed: _normalizeWeights,
                          icon: const Icon(Icons.auto_fix_high_rounded, size: 14),
                          label: const Text('Auto-Normalize', style: TextStyle(fontSize: 12)),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 24),

            // 3. Temporal Context Simulator
            Text(
              'Temporal & Campus Simulator',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              'Simulate how ML crowd prediction responds to time-of-day rush hours and active events.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 12),

            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.border),
              ),
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Simulated Hour of Day', style: TextStyle(fontWeight: FontWeight.w600)),
                      Text(
                        '${_simulationHour.toString().padLeft(2, '0')}:00',
                        style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary),
                      ),
                    ],
                  ),
                  Slider(
                    value: _simulationHour.toDouble(),
                    min: 0,
                    max: 23,
                    divisions: 23,
                    activeColor: AppColors.primary,
                    label: '${_simulationHour.toString().padLeft(2, '0')}:00',
                    onChanged: (val) => setState(() => _simulationHour = val.round()),
                  ),
                  const Divider(height: 16),
                  SwitchListTile(
                    title: const Text('Classes in Session', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                    subtitle: const Text('Increases corridor and academic building traffic', style: TextStyle(fontSize: 11)),
                    value: _classInSession,
                    activeColor: AppColors.primary,
                    contentPadding: EdgeInsets.zero,
                    onChanged: (v) => setState(() => _classInSession = v),
                  ),
                  SwitchListTile(
                    title: const Text('Major Campus Event', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                    subtitle: const Text('Triggers high crowd spikes at Auditorium & Stadium', style: TextStyle(fontSize: 11)),
                    value: _hasEvent,
                    activeColor: AppColors.primary,
                    contentPadding: EdgeInsets.zero,
                    onChanged: (v) => setState(() => _hasEvent = v),
                  ),
                  SwitchListTile(
                    title: const Text('Exam Period', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                    subtitle: const Text('Increases library traffic while reducing athletic field crowds', style: TextStyle(fontSize: 11)),
                    value: _examPeriod,
                    activeColor: AppColors.primary,
                    contentPadding: EdgeInsets.zero,
                    onChanged: (v) => setState(() => _examPeriod = v),
                  ),
                  const Divider(height: 16),
                  SwitchListTile(
                    title: const Text('Use ML Crowd Prediction', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
                    subtitle: const Text('Enable trained Gradient Boosting model inference', style: TextStyle(fontSize: 11)),
                    value: _useMlCrowd,
                    activeColor: AppColors.secondary,
                    contentPadding: EdgeInsets.zero,
                    onChanged: (v) => setState(() => _useMlCrowd = v),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 28),

            // Save CTA
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: _applySettings,
                child: const Text('Apply Preferences', style: TextStyle(fontSize: 16)),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildPresetTile({
    required String pref,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    final label = AppConstants.preferenceLabels[pref] ?? pref;
    final desc = AppConstants.preferenceDescriptions[pref] ?? '';

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isSelected ? AppColors.primary : AppColors.border,
          width: isSelected ? 2.0 : 1.0,
        ),
      ),
      child: ListTile(
        title: Text(label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        subtitle: Text(desc, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        leading: Radio<bool>(
          value: true,
          groupValue: isSelected,
          activeColor: AppColors.primary,
          onChanged: (_) => onTap(),
        ),
        onTap: onTap,
      ),
    );
  }

  Widget _buildWeightSlider(String label, double value, ValueChanged<double> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          SizedBox(
            width: 140,
            child: Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500)),
          ),
          Expanded(
            child: Slider(
              value: value,
              min: 0.0,
              max: 1.0,
              divisions: 20,
              activeColor: AppColors.primary,
              onChanged: onChanged,
            ),
          ),
          SizedBox(
            width: 36,
            child: Text(
              value.toStringAsFixed(2),
              textAlign: TextAlign.right,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }
}
