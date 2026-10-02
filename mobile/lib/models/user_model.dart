// SafeCampus AI — User Profile Model
class UserModel {
  final int id;
  final String username;
  final String email;
  final String role; // student, faculty, visitor, admin
  final String? accessibilityNeed;
  final String? token;
  final bool preferRamps;
  final bool avoidStairs;
  final bool highContrastMap;

  const UserModel({
    required this.id,
    required this.username,
    required this.email,
    this.role = 'student',
    this.accessibilityNeed,
    this.token,
    this.preferRamps = false,
    this.avoidStairs = false,
    this.highContrastMap = false,
  });

  factory UserModel.guest() {
    return const UserModel(
      id: 0,
      username: 'Campus Guest',
      email: 'guest@safecampus.edu',
      role: 'visitor',
    );
  }

  factory UserModel.fromJson(Map<String, dynamic> json, {String? token}) {
    return UserModel(
      id: json['id'] as int? ?? 0,
      username: json['username'] as String? ?? 'User',
      email: json['email'] as String? ?? '',
      role: json['role'] as String? ?? 'student',
      accessibilityNeed: json['accessibility_need'] as String?,
      token: token ?? json['access_token'] as String?,
      preferRamps: json['prefer_ramps'] as bool? ?? false,
      avoidStairs: json['avoid_stairs'] as bool? ?? false,
      highContrastMap: json['high_contrast_map'] as bool? ?? false,
    );
  }

  UserModel copyWith({
    int? id,
    String? username,
    String? email,
    String? role,
    String? accessibilityNeed,
    String? token,
    bool? preferRamps,
    bool? avoidStairs,
    bool? highContrastMap,
  }) {
    return UserModel(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      role: role ?? this.role,
      accessibilityNeed: accessibilityNeed ?? this.accessibilityNeed,
      token: token ?? this.token,
      preferRamps: preferRamps ?? this.preferRamps,
      avoidStairs: avoidStairs ?? this.avoidStairs,
      highContrastMap: highContrastMap ?? this.highContrastMap,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'username': username,
        'email': email,
        'role': role,
        'accessibility_need': accessibilityNeed,
        'token': token,
        'prefer_ramps': preferRamps,
        'avoid_stairs': avoidStairs,
        'high_contrast_map': highContrastMap,
      };
}
