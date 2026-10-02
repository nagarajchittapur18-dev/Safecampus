// SafeCampus AI — Campus Location Model
class CampusLocation {
  final int id;
  final String name;
  final double latitude;
  final double longitude;
  final String locationType;
  final String? description;
  final bool isActive;

  const CampusLocation({
    required this.id,
    required this.name,
    required this.latitude,
    required this.longitude,
    required this.locationType,
    this.description,
    this.isActive = true,
  });

  factory CampusLocation.fromJson(Map<String, dynamic> json) {
    return CampusLocation(
      id: json['id'] as int,
      name: json['name'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      locationType: (json['location_type'] ?? json['type'] ?? 'landmark') as String,
      description: json['description'] as String?,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'latitude': latitude,
        'longitude': longitude,
        'location_type': locationType,
        'description': description,
        'is_active': isActive,
      };

  @override
  String toString() => '$name (ID: $id, Type: $locationType)';
}
