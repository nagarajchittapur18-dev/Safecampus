// SafeCampus AI — Auth & Profile Provider
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/user_model.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

class AuthNotifier extends StateNotifier<UserModel> {
  final ApiService _api;
  final StorageService _storage;

  AuthNotifier(this._api, this._storage) : super(UserModel.guest()) {
    _loadUser();
  }

  Future<void> _loadUser() async {
    final saved = await _storage.getSavedUser();
    if (mounted && saved != null) {
      state = saved;
      _api.setAuthToken(saved.token);
    }
  }

  Future<bool> login(String email, String password) async {
    try {
      final res = await _api.login(email: email, password: password);
      final token = res['access_token'] as String?;
      final userData = res['user'] as Map<String, dynamic>;
      final user = UserModel.fromJson(userData, token: token);
      state = user;
      _api.setAuthToken(token);
      await _storage.saveUser(user);
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> register({
    required String username,
    required String email,
    required String password,
    String role = 'student',
    String? accessibilityNeed,
  }) async {
    try {
      final res = await _api.register(
        username: username,
        email: email,
        password: password,
        role: role,
        accessibilityNeed: accessibilityNeed,
      );
      final token = res['access_token'] as String?;
      final userData = res['user'] as Map<String, dynamic>;
      final user = UserModel.fromJson(userData, token: token);
      state = user;
      _api.setAuthToken(token);
      await _storage.saveUser(user);
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<void> logout() async {
    await _storage.clearUser();
    _api.setAuthToken(null);
    state = UserModel.guest();
  }

  void updateMobilityPreferences({
    bool? preferRamps,
    bool? avoidStairs,
    bool? highContrastMap,
  }) {
    final updated = state.copyWith(
      preferRamps: preferRamps ?? state.preferRamps,
      avoidStairs: avoidStairs ?? state.avoidStairs,
      highContrastMap: highContrastMap ?? state.highContrastMap,
    );
    state = updated;
    _storage.saveUser(updated);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, UserModel>((ref) {
  final api = ref.watch(apiServiceProvider);
  final storage = ref.watch(storageServiceProvider);
  return AuthNotifier(api, storage);
});
