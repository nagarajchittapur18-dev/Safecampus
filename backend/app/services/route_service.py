"""
SafeCampus AI — Route Service
==============================
Orchestration layer between routers and raw algorithms.

RouteService
  .find_dijkstra(source_id, destination_id) → DijkstraResponse
  .find_a_star(source_id, destination_id)   → AStarResponse
  .recommend_route(...)                     → RecommendRouteResponse
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from app.algorithms.a_star import AStarResult, a_star
from app.algorithms.dijkstra import (
    DijkstraResult,
    NodeNotFoundError,
    NoPathError,
    dijkstra,
)
from app.algorithms.multi_objective_a_star import (
    MultiObjectiveResult,
    WeightVector,
    multi_objective_a_star,
)
from app.schemas.route import (
    AStarResponse,
    AlternativeRoute,
    DijkstraResponse,
    RecommendRouteResponse,
)
from app.services.crowd_service import get_crowd_service
from app.services.explanation_service import get_explanation_engine
from app.services.graph_service import get_graph

logger = logging.getLogger(__name__)


class RouteService:
    """
    Stateless service class for route computation.
    All methods are synchronous (algorithms are CPU-bound, not I/O-bound).
    """

    # ------------------------------------------------------------------
    # Dijkstra
    # ------------------------------------------------------------------

    def find_dijkstra(
        self,
        source_id: int,
        destination_id: int,
    ) -> DijkstraResponse:
        """
        Find the shortest-distance path using Dijkstra's algorithm.
        """
        graph = get_graph()

        result: DijkstraResult = dijkstra(
            graph=graph,
            source_id=source_id,
            destination_id=destination_id,
        )

        route_names = [
            graph.get_node(nid).name  # type: ignore[union-attr]
            for nid in result.path
        ]

        return DijkstraResponse(
            source_id=result.source_id,
            destination_id=result.destination_id,
            route=result.path,
            route_names=route_names,
            distance_m=result.distance_m,
            travel_time_min=result.travel_time_min,
            algorithm="dijkstra",
        )

    # ------------------------------------------------------------------
    # A*
    # ------------------------------------------------------------------

    def find_a_star(
        self,
        source_id: int,
        destination_id: int,
    ) -> AStarResponse:
        """
        Find the shortest-distance path using A* search with Haversine heuristic.
        """
        graph = get_graph()

        result: AStarResult = a_star(
            graph=graph,
            source_id=source_id,
            destination_id=destination_id,
        )

        route_names = [
            graph.get_node(nid).name  # type: ignore[union-attr]
            for nid in result.path
        ]

        return AStarResponse(
            source_id=result.source_id,
            destination_id=result.destination_id,
            route=result.path,
            route_names=route_names,
            distance_m=result.distance_m,
            travel_time_min=result.travel_time_min,
            execution_time_ms=result.execution_time_ms,
            algorithm="a_star",
        )

    # ------------------------------------------------------------------
    # Personalized Multi-Objective Recommendation (Phase 5 & 7)
    # ------------------------------------------------------------------

    def recommend_route(
        self,
        source_id: int,
        destination_id: int,
        preference: str = "balanced",
        custom_weights: Optional[Dict[str, float]] = None,
        hour: Optional[int] = None,
        day_of_week: Optional[int] = None,
        event_flag: int = 0,
        class_activity: Optional[int] = None,
        exam_flag: int = 0,
        holiday_flag: int = 0,
        use_ml_crowd: bool = True,
    ) -> RecommendRouteResponse:
        """
        Compute a personalized multi-objective safe route using Multi-Objective A*.
        Connects dynamic ML crowd predictions into the routing cost function.
        Falls back seamlessly to static graph baselines if ML is unavailable.
        """
        graph = get_graph()

        # 1. Parse / validate weights
        if custom_weights is not None:
            weights = WeightVector(
                wD=float(custom_weights["wD"]),
                wT=float(custom_weights["wT"]),
                wC=float(custom_weights["wC"]),
                wS=float(custom_weights["wS"]),
                wA=float(custom_weights["wA"]),
            )
        else:
            weights = WeightVector.from_preference(preference)

        # 2. Predict crowd for relevant campus locations
        node_crowd_scores: Optional[Dict[int, float]] = None
        model_name: Optional[str] = None

        if use_ml_crowd:
            try:
                crowd_service = get_crowd_service()
                scores: Dict[int, float] = {}
                for node in graph.all_nodes():
                    pred = crowd_service.predict(
                        location_id=node.id,
                        hour=hour,
                        day_of_week=day_of_week,
                        event_flag=event_flag,
                        class_activity=class_activity,
                        exam_flag=exam_flag,
                        holiday_flag=holiday_flag,
                    )
                    scores[node.id] = pred.predicted_crowd_score
                node_crowd_scores = scores
                model_name = crowd_service.model_name
            except Exception as exc:
                logger.warning(
                    "ML crowd prediction unavailable, falling back to static graph baselines: %s",
                    exc,
                )
                node_crowd_scores = None
                model_name = None

        # 3. Execute Personalized Multi-Objective A* search
        result: MultiObjectiveResult = multi_objective_a_star(
            graph=graph,
            source_id=source_id,
            destination_id=destination_id,
            weights=weights,
            preference=preference,
            node_crowd_scores=node_crowd_scores,
            model_name=model_name,
        )

        route_names = [
            graph.get_node(nid).name  # type: ignore[union-attr]
            for nid in result.path
        ]

        # 4. Generate candidate alternative routes
        alternatives: List[AlternativeRoute] = []
        candidate_presets = [
            ("shortest", "Shortest Path"),
            ("safest", "Safest Route"),
            ("least_crowded", "Least Crowded"),
            ("fastest", "Fastest Route"),
            ("accessible", "Maximum Accessibility"),
        ]

        seen_paths = {tuple(result.path)}
        for alt_pref, alt_label in candidate_presets:
            if alt_pref == preference and custom_weights is None:
                continue
            if len(alternatives) >= 2:
                break
            try:
                alt_weights = WeightVector.from_preference(alt_pref)
                alt_res = multi_objective_a_star(
                    graph=graph,
                    source_id=source_id,
                    destination_id=destination_id,
                    weights=alt_weights,
                    preference=alt_pref,
                    node_crowd_scores=node_crowd_scores,
                    model_name=model_name,
                )
                if tuple(alt_res.path) not in seen_paths:
                    seen_paths.add(tuple(alt_res.path))
                    alt_names = [
                        graph.get_node(nid).name  # type: ignore[union-attr]
                        for nid in alt_res.path
                    ]
                    alternatives.append(
                        AlternativeRoute(
                            label=alt_label,
                            preference=alt_pref,
                            route=alt_res.path,
                            route_names=alt_names,
                            distance_m=alt_res.distance_m,
                            travel_time_min=alt_res.travel_time_min,
                            crowd_score=alt_res.crowd_score,
                            crowd_level=alt_res.crowd_level,
                            safety_score=alt_res.safety_score,
                            accessibility_score=alt_res.accessibility_score,
                            total_cost=alt_res.total_cost,
                        )
                    )
            except Exception as exc:
                logger.debug("Alternative route candidate calculation failed: %s", exc)
                continue

        # 5. Generate dynamic route explanation
        explanation = None
        try:
            explanation_engine = get_explanation_engine()
            explanation = explanation_engine.generate_explanation(
                graph=graph,
                recommended=result,
                source_id=source_id,
                destination_id=destination_id,
                node_crowd_scores=node_crowd_scores,
            )
        except Exception as exc:
            logger.warning("Failed to generate route explanation: %s", exc)
            explanation = None

        return RecommendRouteResponse(
            source_id=result.source_id,
            destination_id=result.destination_id,
            preference=result.preference,
            weights=result.weights,
            route=result.path,
            recommended_route=result.path,
            route_names=route_names,
            distance_m=result.distance_m,
            travel_time_min=result.travel_time_min,
            crowd_score=result.crowd_score,
            crowd_level=result.crowd_level,
            safety_score=result.safety_score,
            accessibility_score=result.accessibility_score,
            total_cost=result.total_cost,
            execution_time_ms=result.execution_time_ms,
            algorithm="personalized_multi_objective_a_star",
            used_ml_crowd=result.used_ml_crowd,
            model_name=result.model_name,
            alternatives=alternatives,
            explanation=explanation,
        )


