# SafeCampus AI — API Documentation

Base URL: `http://localhost:8000/api`

Interactive docs: `http://localhost:8000/docs`

---

## Phase 1 Endpoints

### GET /health

Health check.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "message": "SafeCampus AI backend is running."
}
```

---

## Phase 2 Endpoints (Planned)

### POST /auth/register
Register a new user.

**Request:**
```json
{
  "username": "student1",
  "email": "student1@campus.edu",
  "password": "securepassword"
}
```

### POST /auth/login
Login and receive JWT token.

### GET /locations
Get all campus locations (nodes).

### GET /locations/{id}
Get a specific location.

### POST /routes/recommend
Get route recommendation.

**Request:**
```json
{
  "source_id": 1,
  "destination_id": 8,
  "preference": "safest"
}
```

**Response:**
```json
{
  "recommended_route": [1, 3, 5, 8],
  "distance_m": 520,
  "travel_time_min": 6.2,
  "crowd_level": "LOW",
  "safety_score": 0.91,
  "accessibility_score": 1.0,
  "total_cost": 0.31,
  "preference": "safest",
  "explanation": [
    "Route selected: predicted crowd is LOW.",
    "Safety score 0.91 is 18% above campus average.",
    "Route is fully wheelchair accessible."
  ],
  "comparison": {
    "vs_shortest": {
      "extra_distance_m": 80,
      "extra_time_min": 1.0,
      "crowd_reduction_pct": 42,
      "safety_improvement_pct": 18
    }
  },
  "alternatives": [...]
}
```

### GET /routes/history
Get current user's route history.

### GET /crowd/current
Get current crowd levels for all locations.

### GET /crowd/prediction/{location_id}
Get predicted crowd for a specific location.

### GET /events
List campus events.

### POST /events
Create a campus event (admin only).
