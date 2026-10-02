// SafeCampus AI — Flutter Widget & Integration Tests
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:safecampus_ai/core/constants/app_constants.dart';
import 'package:safecampus_ai/main.dart';
import 'package:safecampus_ai/widgets/metric_card.dart';
import 'package:safecampus_ai/widgets/preference_chip.dart';
import 'package:safecampus_ai/widgets/score_badge.dart';

void main() {
  group('App Launch & Splash Screen Tests', () {
    testWidgets('App starts and displays SafeCampus AI branding', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SafeCampusApp(),
        ),
      );

      // Verify splash screen branding
      expect(find.text(AppConstants.appName), findsOneWidget);
      expect(find.text(AppConstants.appTagline), findsOneWidget);
      expect(find.byIcon(Icons.route_rounded), findsOneWidget);

      // Advance past splash delay and navigation timer
      await tester.pump(const Duration(milliseconds: 1500));
      await tester.pump(const Duration(milliseconds: 500));
      await tester.pump(const Duration(milliseconds: 500));
    });
  });

  group('Reusable Widgets Tests', () {
    testWidgets('CrowdBadge displays level and percentage', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: CrowdBadge(level: 'HIGH', score: 0.65),
          ),
        ),
      );

      expect(find.text('Heavy Crowd (65%)'), findsOneWidget);
      expect(find.byIcon(Icons.groups_rounded), findsOneWidget);
    });

    testWidgets('SafetyBadge displays safety percentage', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SafetyBadge(score: 0.88),
          ),
        ),
      );

      expect(find.text('Safety: 88%'), findsOneWidget);
      expect(find.byIcon(Icons.shield_rounded), findsOneWidget);
    });

    testWidgets('MetricCard displays label and value', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: MetricCard(
              icon: Icons.straighten_rounded,
              iconColor: Colors.blue,
              label: 'Distance',
              value: '300 m',
              subtitle: 'Walking path',
            ),
          ),
        ),
      );

      expect(find.text('Distance'), findsOneWidget);
      expect(find.text('300 m'), findsOneWidget);
      expect(find.text('Walking path'), findsOneWidget);
    });

    testWidgets('PreferenceChip responds to selection', (WidgetTester tester) async {
      String? selected;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: PreferenceChip(
              preference: AppConstants.prefSafest,
              isSelected: true,
              onSelected: (val) => selected = val,
            ),
          ),
        ),
      );

      expect(find.text('Safest'), findsOneWidget);
      await tester.tap(find.text('Safest'));
      expect(selected, equals(AppConstants.prefSafest));
    });
  });
}
