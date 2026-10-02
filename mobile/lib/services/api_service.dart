// SafeCampus AI — API Service
// Handles all HTTP communication with the FastAPI backend.
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/constants/app_constants.dart';
import '../models/campus_location.dart';
import '../models/crowd_prediction.dart';
import '../models/route_recommendation.dart';
import '../models/user_model.dart';

import '../core/constants/fallback_campus_data.dart';

// ---------------------------------------------------------------------------
// Riverpod Provider
// ---------------------------------------------------------------------------
final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});

// ---------------------------------------------------------------------------
// Service Implementation
// ---------------------------------------------------------------------------
class ApiService {
  late final Dio _dio;
  String? _authToken;

  ApiService() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.apiBaseUrl,
        connectTimeout: const Duration(seconds: 12),
        receiveTimeout: const Duration(seconds: 25),
        headers: {'Content-Type': 'application/json'},
      ),
    );

    if (kDebugMode) {
      _dio.interceptors.add(
        LogInterceptor(
          requestBody: true,
          responseBody: false,
          logPrint: (obj) => debugPrint('[API] $obj'),
        ),
      );
    }
  }

  void setAuthToken(String? token) {
    _authToken = token;
  }

  Map<String, String> get _authHeaders {
    if (_authToken != null && _authToken!.isNotEmpty) {
      return {'Authorization': 'Bearer $_authToken'};
    }
    return {};
  }

  // -------------------------------------------------------------------------
  // 1. Health
  // -------------------------------------------------------------------------
  Future<bool> checkHealth() async {
    try {
      final res = await _dio.get('/health');
      return res.statusCode == 200 && res.data['status'] == 'ok';
    } catch (e) {
      debugPrint('[API] Health check failed: $e');
      return false;
    }
  }

  // -------------------------------------------------------------------------
  // 2. Locations
  // -------------------------------------------------------------------------
  Future<List<CampusLocation>> getLocations() async {
    try {
      final response = await _dio.get('/locations');
      final data = response.data;
      final rawList = data is Map ? (data['locations'] as List? ?? []) : (data as List);
      return rawList.map((e) => CampusLocation.fromJson(e as Map<String, dynamic>)).toList();
    } catch (e) {
      debugPrint('[API] Error fetching locations from server, falling back to local campus graph: $e');
      return FallbackCampusData.locations;
    }
  }

  Future<CampusLocation> getLocation(int locationId) async {
    try {
      final response = await _dio.get('/locations/$locationId');
      return CampusLocation.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      debugPrint('[API] Error fetching location $locationId: $e');
      rethrow;
    }
  }

  // -------------------------------------------------------------------------
  // 3. Route Recommendation (Multi-Objective A* with ML Crowd)
  // -------------------------------------------------------------------------
  Future<RouteRecommendation> recommendRoute({
    required int sourceId,
    required int destinationId,
    String preference = 'balanced',
    Map<String, double>? weights,
    int? hour,
    int? dayOfWeek,
    int eventFlag = 0,
    int? classActivity,
    int examFlag = 0,
    int holidayFlag = 0,
    bool useMlCrowd = true,
  }) async {
    try {
      final payload = {
        'source_id': sourceId,
        'destination_id': destinationId,
        'preference': preference,
        'weights': weights,
        'hour': hour,
        'day_of_week': dayOfWeek,
        'event_flag': eventFlag,
        'class_activity': classActivity,
        'exam_flag': examFlag,
        'holiday_flag': holidayFlag,
        'use_ml_crowd': useMlCrowd,
      };

      final response = await _dio.post(
        '/routes/recommend',
        data: payload,
      );

      return RouteRecommendation.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      debugPrint('[API] Error in route recommendation: $e');
      rethrow;
    }
  }

  // -------------------------------------------------------------------------
  // 4. Dijkstra Shortest Route (for Pareto Trade-Off Comparison)
  // -------------------------------------------------------------------------
  Future<Map<String, dynamic>> getDijkstraRoute({
    required int sourceId,
    required int destinationId,
  }) async {
    try {
      final response = await _dio.post(
        '/routes/dijkstra',
        data: {'source_id': sourceId, 'destination_id': destinationId},
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      debugPrint('[API] Error fetching Dijkstra route: $e');
      rethrow;
    }
  }

  // -------------------------------------------------------------------------
  // 5. Crowd Prediction for Location
  // -------------------------------------------------------------------------
  Future<CrowdPrediction> getCrowdPrediction(
    int locationId, {
    int? hour,
    int? dayOfWeek,
    int eventFlag = 0,
    int? classActivity,
    int examFlag = 0,
    int holidayFlag = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        if (hour != null) 'hour': hour,
        if (dayOfWeek != null) 'day_of_week': dayOfWeek,
        'event_flag': eventFlag,
        if (classActivity != null) 'class_activity': classActivity,
        'exam_flag': examFlag,
        'holiday_flag': holidayFlag,
      };

      final response = await _dio.get(
        '/crowd/prediction/$locationId',
        queryParameters: queryParams,
      );

      return CrowdPrediction.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      debugPrint('[API] Error fetching crowd prediction for $locationId: $e');
      rethrow;
    }
  }

  // -------------------------------------------------------------------------
  // 6. Authentication
  // -------------------------------------------------------------------------
  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    String role = 'student',
    String? accessibilityNeed,
  }) async {
    try {
      final response = await _dio.post(
        '/auth/register',
        data: {
          'username': username,
          'email': email,
          'password': password,
          'role': role,
          'accessibility_need': accessibilityNeed,
        },
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      debugPrint('[API] Register error: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _dio.post(
        '/auth/login',
        data: {'email': email, 'password': password},
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      debugPrint('[API] Login error: $e');
      rethrow;
    }
  }

  Future<UserModel> getCurrentUser() async {
    try {
      final response = await _dio.get(
        '/auth/me',
        options: Options(headers: _authHeaders),
      );
      return UserModel.fromJson(response.data as Map<String, dynamic>, token: _authToken);
    } catch (e) {
      debugPrint('[API] GetCurrentUser error: $e');
      return UserModel.guest();
    }
  }
}
