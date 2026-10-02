// SafeCampus AI — Route History Provider
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/route_history_item.dart';
import '../services/storage_service.dart';

class HistoryNotifier extends StateNotifier<List<RouteHistoryItem>> {
  final StorageService _storage;

  HistoryNotifier(this._storage) : super([]) {
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    final list = await _storage.getHistory();
    if (mounted) {
      state = list;
    }
  }

  Future<void> addItem(RouteHistoryItem item) async {
    await _storage.saveHistoryItem(item);
    if (mounted) {
      state = [item, ...state.where((e) => e.id != item.id)].take(20).toList();
    }
  }

  Future<void> clearAll() async {
    await _storage.clearHistory();
    state = [];
  }
}

final historyProvider = StateNotifierProvider<HistoryNotifier, List<RouteHistoryItem>>((ref) {
  final storage = ref.watch(storageServiceProvider);
  return HistoryNotifier(storage);
});
