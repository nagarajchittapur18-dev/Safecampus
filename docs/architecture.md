# SafeCampus AI — Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Flutter Mobile App                    │
│  Dart + Flutter 3.x + Riverpod + go_router + flutter_map│
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP REST (Dio)
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│  Python 3.10 + FastAPI + Uvicorn                        │
│                                                         │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   Routers  │  │   Services   │  │  Algorithms    │  │
│  │  /health   │  │ GraphService │  │  Dijkstra      │  │
│  │  /auth     │  │ RouteService │  │  A*            │  │
│  │  /routes   │  │ CrowdService │  │  MultiObj A*   │  │
│  │  /locations│  │ SafetyService│  │                │  │
│  └────────────┘  └──────────────┘  └────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │            SQLite Database (campus.db)           │   │
│  │  users | locations | routes | events | crowd    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │            ML Inference (Phase 2)               │   │
│  │  scikit-learn + joblib — crowd_model.pkl        │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Flutter App
- User interface and experience
- Location permission handling
- Map rendering (flutter_map + OpenStreetMap tiles)
- Route preference selection
- Displaying recommendations and explanations

### FastAPI Backend
- REST API serving the mobile app
- Campus graph management
- Route algorithm execution
- ML model inference (Phase 2)
- Authentication (Phase 2)
- Event management

### SQLite Database
- Persistent storage for users, routes, events, crowd records
- Managed via SQLAlchemy async ORM

### ML Pipeline (Phase 2)
- Crowd level classification
- Trained offline, loaded at startup
- No retraining on API requests

### Graph Algorithms
- Dijkstra: baseline shortest path
- A*: heuristic-guided shortest path  
- Multi-Objective A*: personalized weighted cost

## Data Flow — Route Recommendation

```
User selects source, destination, preference
        │
Flutter sends POST /api/routes/recommend
        │
RouteService.recommend()
        │
   ┌────┴────────────────────────┐
   │  Load campus graph          │
   │  Get ML crowd predictions   │ ← Phase 2
   │  Run Multi-Objective A*     │
   │  Compute metrics            │
   │  Generate explanation       │
   └────────────────────────────┘
        │
Return RouteResponse JSON
        │
Flutter renders route on map + explanation card
```

## Zero-Cost Guarantee

- Maps: OpenStreetMap (free)
- Backend: Local FastAPI (free)
- Database: SQLite (free)
- ML: scikit-learn local inference (free)
- No external paid APIs
