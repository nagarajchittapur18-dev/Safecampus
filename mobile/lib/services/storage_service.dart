// SafeCampus AI — Local Storage Service
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/route_history_item.dart';
import '../models/user_model.dart';

final storageServiceProvider = Provider<StorageService>((ref) {
  return StorageService();
});

class StorageService {
  static const String _keyOnboardingSeen = 'onboarding_seen';
  static const String _keyUser = 'user_profile';
  static const String _keyHistory = 'route_history';

  Future<bool> isOnboardingSeen() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_keyOnboardingSeen) ?? false;
  }

  Future<void> setOnboardingSeen(bool seen) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyOnboardingSeen, seen);
  }

  Future<UserModel?> getSavedUser() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final str = prefs.getString(_keyUser);
      if (str == null) return null;
      return UserModel.fromJson(jsonDecode(str) as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<void> saveUser(UserModel user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyUser, jsonEncode(user.toJson()));
  }

  Future<void> clearUser() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyUser);
  }

  Future<List<RouteHistoryItem>> getHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final list = prefs.getStringList(_keyHistory) ?? [];
      return list
          .map((item) => RouteHistoryItem.fromJson(jsonDecode(item) as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<void> saveHistoryItem(RouteHistoryItem item) async {
    final prefs = await SharedPreferences.getInstance();
    final current = await getHistory();
    // Prepend new item, keep last 20
    final updated = [item, ...current.where((e) => e.id != item.id)].take(20).toList();
    final strList = updated.map((e) => jsonEncode(e.toJson())).toList();
    await prefs.setStringList(_keyHistory, strList);
  }

  Future<void> clearHistory() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyHistory);
  }
}
