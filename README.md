# SafeCampus AI

> **A Multi-Objective AI-Based Personalized Safe Route Recommendation Framework
> for Smart Campus Navigation**

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)](https://fastapi.tiangolo.com)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-blue)](https://flutter.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Problem

University campuses have complex, dynamic environments where existing navigation
tools optimize only for distance or time. This project proposes a framework that
simultaneously considers **predicted crowd density**, **safety**, **accessibility**,
**distance**, and **travel time** to recommend personalized routes.

## Research Gap (Candidate)

See [`research/candidate_research_gap.md`](research/candidate_research_gap.md) for
the candidate research gaps requiring literature validation.

## Architecture

```
Flutter Mobile App (Dart)
        │  HTTP/REST
        ▼
FastAPI Backend (Python)
        │
   ┌────┴────┐
   │ SQLite  │  SQLAlchemy (async)
   └─────────┘
        │
   ML Services (scikit-learn)   ←── Phase 2
   Graph Algorithms             ←── Phase 2
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Mobile | Flutter 3.x + Dart |
| Backend | Python 3.10 + FastAPI |
| Database | SQLite + SQLAlchemy (async) |
| ML | scikit-learn, pandas, numpy, joblib |
| Maps | flutter_map (OpenStreetMap) |
| State Mgmt | Riverpod |
| Routing | go_router |

## Project Structure

```
SafeCampusAI/
├── mobile/                  # Flutter mobile app
│   ├── lib/
│   │   ├── core/            # Router, constants
│   │   ├── models/          # Data models
│   │   ├── services/        # API service (Dio)
│   │   ├── screens/         # UI screens
│   │   ├── widgets/         # Reusable widgets
│   │   └── theme/           # App theme & colors
│   └── test/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py          # App entry point
│   │   ├── database.py      # SQLite + SQLAlchemy
│   │   ├── models/          # ORM models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── algorithms/      # Graph algorithms (Phase 2)
│   │   └── utils/           # Helpers
│   └── tests/
├── ml/                      # ML pipeline (Phase 2)
│   ├── data/
│   ├── models/
│   └── results/
├── data/                    # Campus graph JSON (Phase 2)
├── research/                # Research documentation
└── docs/                    # Technical documentation
```

---

## Setup Instructions

### Backend

#### 1. Create virtual environment
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 2. Install dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Verify
Open: http://localhost:8000/api/health

Expected:
```json
{"status": "ok", "version": "0.1.0", "message": "SafeCampus AI backend is running."}
```

API Docs: http://localhost:8000/docs

#### 5. Run tests
```bash
pytest tests/ -v
```

---

### Flutter Mobile App

#### Prerequisites
- Flutter SDK ≥ 3.3.0 (https://flutter.dev/docs/get-started/install)
- Android Studio or VS Code with Flutter plugin

#### 1. Install dependencies
```bash
cd mobile
flutter pub get
```

#### 2. Run the app
```bash
# Android emulator (backend at 10.0.2.2:8000)
flutter run

# Chrome / web (backend at localhost:8000)
flutter run -d chrome
```

#### 3. Run tests
```bash
flutter test
```

---

## API Endpoints (Phase 1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/docs` | Swagger UI |

## Phase Roadmap

| Phase | Contents | Status |
|-------|----------|--------|
| Phase 1 | Project scaffold, FastAPI health endpoint, Flutter scaffold | ✅ Done |
| Phase 2 | Campus graph, Dijkstra, A*, Multi-Objective A*, Crowd ML | 🔲 Next |
| Phase 3 | Full Flutter UI — map, heatmap, route results | 🔲 Planned |
| Phase 4 | Research experiments, evaluation, paper draft | 🔲 Planned |

---

## Research Ethics

- All datasets are clearly labeled as synthetic unless stated otherwise.
- Research gaps are candidates pending literature validation.
- No results are fabricated — experiments are marked NOT RUN until executed.
- No paid external APIs are used.

---

## Dataset

> **Phase 2** — The ML dataset (`ml/data/crowd_data.csv`) is synthetic,
> generated with a fixed random seed for reproducibility.
> It does not represent real campus measurements.

---

## License

MIT License — see [LICENSE](LICENSE).

---

## Authors

SafeCampus AI Research Project
