// SafeCampus AI — Destination & Origin Search Screen
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/campus_location.dart';
import '../../providers/locations_provider.dart';
import '../../providers/route_provider.dart';
import '../../providers/user_location_provider.dart';
import '../../theme/app_theme.dart';
import '../../widgets/state_views.dart';

class DestinationSearchScreen extends ConsumerStatefulWidget {
  final bool isOrigin;

  const DestinationSearchScreen({
    super.key,
    this.isOrigin = false,
  });

  @override
  ConsumerState<DestinationSearchScreen> createState() => _DestinationSearchScreenState();
}

class _DestinationSearchScreenState extends ConsumerState<DestinationSearchScreen> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    // Reset search query
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(locationSearchQueryProvider.notifier).state = '';
      ref.read(locationCategoryFilterProvider.notifier).state = 'all';
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final filteredAsync = ref.watch(filteredLocationsProvider);
    final currentCategory = ref.watch(locationCategoryFilterProvider);
    final routeNotifier = ref.read(routeProvider.notifier);

    final title = widget.isOrigin ? 'Select Starting Point' : 'Select Campus Destination';

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(title),
        elevation: 0,
      ),
      body: Column(
        children: [
          // 1. Search Bar Container
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            color: Colors.white,
            child: TextField(
              controller: _searchController,
              autofocus: true,
              decoration: InputDecoration(
                hintText: 'Search 20 campus facilities, labs, gates...',
                prefixIcon: const Icon(Icons.search_rounded, color: AppColors.primary),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear_rounded),
                        onPressed: () {
                          _searchController.clear();
                          ref.read(locationSearchQueryProvider.notifier).state = '';
                        },
                      )
                    : null,
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              ),
              onChanged: (val) {
                ref.read(locationSearchQueryProvider.notifier).state = val;
                setState(() {});
              },
            ),
          ),

          // 2. Category Filter Chips
          Container(
            color: Colors.white,
            padding: const EdgeInsets.only(left: 16, right: 16, bottom: 12),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildCategoryChip('All', 'all', currentCategory),
                  _buildCategoryChip('Academic', 'academic', currentCategory),
                  _buildCategoryChip('Amenities', 'amenities', currentCategory),
                  _buildCategoryChip('Gates', 'gate', currentCategory),
                  _buildCategoryChip('Junctions', 'junction', currentCategory),
                ],
              ),
            ),
          ),
          const Divider(height: 1),

          // 3. Search Results List
          Expanded(
            child: filteredAsync.when(
              data: (locations) {
                if (locations.isEmpty) {
                  return const EmptyStateView(
                    icon: Icons.search_off_rounded,
                    title: 'No Locations Found',
                    message: 'Try changing your search terms or selecting a different category filter.',
                  );
                }

                return ListView(
                  padding: const EdgeInsets.all(12),
                  children: [
                    if (widget.isOrigin)
                      Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        decoration: BoxDecoration(
                          color: AppColors.secondary.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppColors.secondary.withOpacity(0.3)),
                        ),
                        child: Material(
                          color: Colors.transparent,
                          borderRadius: BorderRadius.circular(12),
                          child: ListTile(
                            leading: const CircleAvatar(
                              backgroundColor: AppColors.secondary,
                              child: Icon(Icons.my_location_rounded, color: Colors.white, size: 20),
                            ),
                            title: const Text('Use Current Location', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                            subtitle: const Text('Detect GPS & snap to nearest campus facility', style: TextStyle(fontSize: 11)),
                            trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 13),
                            onTap: () async {
                              final outcome = await ref.read(userLocationProvider.notifier).detectLocationAndSnapSource(autoSetSource: true);
                              if (context.mounted) {
                                if (outcome.success) {
                                  Navigator.pop(context);
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(content: Text(outcome.message)),
                                  );
                                } else {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text(outcome.message),
                                      duration: const Duration(seconds: 4),
                                    ),
                                  );
                                }
                              }
                            },
                          ),
                        ),
                      ),
                    ...locations.map((loc) => Padding(
                          padding: const EdgeInsets.only(bottom: 6),
                          child: _buildLocationItem(context, loc, routeNotifier),
                        )),
                  ],
                );
              },
              loading: () => const LoadingStateView(message: 'Loading campus map nodes...'),
              error: (err, _) => ErrorStateView(
                message: 'Failed to retrieve locations: $err',
                onRetry: () => ref.refresh(locationsProvider),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryChip(String label, String value, String current) {
    final isSelected = current == value;
    return Padding(
      padding: const EdgeInsets.only(right: 6.0),
      child: FilterChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (_) {
          ref.read(locationCategoryFilterProvider.notifier).state = value;
        },
        selectedColor: AppColors.primary,
        backgroundColor: AppColors.surfaceVariant,
        checkmarkColor: Colors.white,
        showCheckmark: false,
        labelStyle: TextStyle(
          color: isSelected ? Colors.white : AppColors.textPrimary,
          fontSize: 12,
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
        ),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
    );
  }

  Widget _buildLocationItem(
    BuildContext context,
    CampusLocation loc,
    RouteNotifier routeNotifier,
  ) {
    return Card(
      elevation: 0,
      color: Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: AppColors.border),
      ),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: widget.isOrigin
                ? AppColors.secondary.withOpacity(0.12)
                : AppColors.error.withOpacity(0.12),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            widget.isOrigin ? Icons.trip_origin_rounded : Icons.location_on_rounded,
            color: widget.isOrigin ? AppColors.secondary : AppColors.error,
            size: 22,
          ),
        ),
        title: Text(
          loc.name,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
        ),
        subtitle: Text(
          loc.description ?? 'Campus location (ID: ${loc.id})',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: AppColors.surfaceVariant,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            loc.locationType.toUpperCase(),
            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppColors.textSecondary),
          ),
        ),
        onTap: () {
          if (widget.isOrigin) {
            routeNotifier.setSource(loc);
          } else {
            routeNotifier.setDestination(loc);
          }
          Navigator.of(context).pop();
        },
      ),
    );
  }
}
