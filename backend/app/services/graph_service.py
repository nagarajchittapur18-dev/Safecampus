"""
SafeCampus AI — Graph Loader (Service)
=======================================
Reads campus_nodes.json and campus_edges.json from the /data directory,
constructs a CampusGraph, and validates it.

The loaded graph is cached as a module-level singleton so it is built
once at startup and reused across all API requests.

To replace the campus data: edit data/campus_nodes.json and campus_edges.json
— no source code changes required.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from app.algorithms.graph import CampusGraph
from app.algorithms.models import Edge, Node

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default data paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_NODES_PATH = _REPO_ROOT / "data" / "campus_nodes.json"
_DEFAULT_EDGES_PATH = _REPO_ROOT / "data" / "campus_edges.json"

# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_graph: Optional[CampusGraph] = None


def get_graph() -> CampusGraph:
    """
    Return the loaded campus graph.

    If the graph has not been loaded yet, it is loaded on first call.
    """
    global _graph
    if _graph is None:
        _graph = load_graph()
    return _graph


def reset_graph() -> None:
    """
    Reset the singleton (used in tests to reload with custom data).
    """
    global _graph
    _graph = None


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_graph(
    nodes_path: Optional[Path] = None,
    edges_path: Optional[Path] = None,
    bidirectional: bool = True,
) -> CampusGraph:
    """
    Build a CampusGraph from JSON files.

    Parameters
    ----------
    nodes_path   : Path to campus_nodes.json (defaults to data/campus_nodes.json)
    edges_path   : Path to campus_edges.json (defaults to data/campus_edges.json)
    bidirectional: If True (default) each edge is inserted in both directions.

    Returns
    -------
    CampusGraph  : Fully populated and validated graph.
    """
    nodes_path = Path(nodes_path) if nodes_path else _DEFAULT_NODES_PATH
    edges_path = Path(edges_path) if edges_path else _DEFAULT_EDGES_PATH

    logger.info("Loading campus graph from %s and %s", nodes_path, edges_path)

    graph = CampusGraph()

    # ---- Load nodes ----
    nodes_raw = _read_json(nodes_path)
    for raw in nodes_raw:
        node = _parse_node(raw)
        graph.add_node(node)
    logger.info("Loaded %d nodes", graph.node_count())

    # ---- Load edges ----
    edges_raw = _read_json(edges_path)
    for raw in edges_raw:
        edge = _parse_edge(raw)
        graph.add_edge(edge, bidirectional=bidirectional)
    logger.info(
        "Loaded %d edges (%s)",
        graph.edge_count(),
        "bidirectional" if bidirectional else "directed",
    )

    # ---- Validate ----
    errors = graph.validate()
    if errors:
        msg = "Campus graph validation failed:\n" + "\n".join(f"  • {e}" for e in errors)
        logger.error(msg)
        raise ValueError(msg)

    logger.info("Campus graph loaded and validated: %r", graph)
    return graph


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _read_json(path: Path) -> list:
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array in {path}, got {type(data).__name__}")
    return data


def _parse_node(raw: dict) -> Node:
    """Parse one dict from campus_nodes.json into a Node."""
    required = {"id", "name", "latitude", "longitude", "type"}
    missing = required - raw.keys()
    if missing:
        raise ValueError(f"Node record missing fields: {missing}  →  {raw}")

    return Node(
        id=int(raw["id"]),
        name=str(raw["name"]),
        latitude=float(raw["latitude"]),
        longitude=float(raw["longitude"]),
        node_type=str(raw["type"]),
        description=str(raw.get("description", "")),
    )


def _parse_edge(raw: dict) -> Edge:
    """Parse one dict from campus_edges.json into an Edge."""
    required = {"id", "source", "destination", "distance", "base_time",
                "safety_score", "accessibility_score", "stairs", "ramp_available"}
    missing = required - raw.keys()
    if missing:
        raise ValueError(f"Edge record missing fields: {missing}  →  {raw}")

    return Edge(
        id=int(raw["id"]),
        source=int(raw["source"]),
        destination=int(raw["destination"]),
        distance=float(raw["distance"]),
        base_time=float(raw["base_time"]),
        safety_score=float(raw["safety_score"]),
        accessibility_score=float(raw["accessibility_score"]),
        stairs=bool(raw["stairs"]),
        ramp_available=bool(raw["ramp_available"]),
        crowd_score=float(raw.get("crowd_score", 0.5)),
        note=str(raw.get("note", "")),
    )
