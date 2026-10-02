# Research Objectives and Deliverables

## 1. Primary Research Objective

To architect, mathematically formulate, empirically benchmark, and deploy a comprehensive **Personalized Multi-Objective AI Route Recommendation and Explanation Framework** designed for smart campus navigation, unifying machine learning crowd prediction, physical safety indexing, universal accessibility compliance, and contrastive explainability.

---

## 2. Specific Research Objectives (SRO)

- **O1: Topological Campus Graph Engineering**  
  Model the academic campus environment as an attributed directed multigraph $G = (V, E)$ featuring 26 heterogeneous nodes (academic blocks, administrative complexes, libraries, hostels, dining halls, gates, and pathway junctions) and 42 interconnected pathways annotated with Haversine distances, base walking times, nocturnal illumination ratings, CCTV surveillance coverage, physical stair presence, and wheelchair ramp availability.

- **O2: Single-Objective Baseline Routing Implementation**  
  Implement exact single-objective routing baselines:
  - Dijkstra’s shortest-path algorithm for optimal physical distance path-finding.
  - Standard A\* search utilizing an admissible spherical Haversine heuristic.

- **O3: Personalized Multi-Objective A\* Formulation**  
  Design and implement the core research routing algorithm—**Personalized Multi-Objective A\***—combining distance, travel time, crowd exposure, physical safety, and accessibility into a unified scalarized cost function constrained to a four-dimensional simplex ($\sum w_i = 1.0$), guided by an admissible and monotonic normalized Euclidean heuristic.

- **O4: Synthetic Crowd Dataset Generation**  
  Synthesize a transparent, reproducible temporal-spatial dataset ($N = 28,800$ records, 120 days, seed 42) capturing diurnal cycles, hourly distribution patterns, academic lecture dismissals, exam periods, and weekend shifts across 10 campus locations, fully labeled as synthetic to maintain research integrity.

- **O5: Machine Learning Model Development & Benchmarking**  
  Train, validate, and compare four supervised classification architectures—Logistic Regression, Decision Tree, Random Forest, and Gradient Boosting—optimizing Macro F1-score, precision, recall, and inference latency, saving the optimal serialized model via `joblib`.

- **O6: Dynamic ML-Routing Integration & Robust Fallback**  
  Integrate the trained predictive model into the path-finding pipeline, dynamically converting predicted crowd levels into normalized edge traversal costs while retaining graceful degradation to static baseline scores if the ML subsystem is unavailable.

- **O7: Contrastive Explanation Engine**  
  Develop an explainability engine that quantitatively benchmarks the recommended personalized route against the shortest physical path baseline, calculating exact percentage deltas in distance, transit duration, crowd exposure, safety, and accessibility to synthesize clear natural language rationales.

- **O8: Comprehensive Experimental Evaluation**  
  Execute five reproducible research experiments:
  1. *Experiment 1*: ML crowd model classification benchmark.
  2. *Experiment 2*: Routing algorithm efficiency and quality comparison (Dijkstra vs. A\* vs. Multi-Objective A\*).
  3. *Experiment 3*: Route personalization presets across identical origin-destination pairs.
  4. *Experiment 4*: Cumulative ablation study isolating factor contributions.
  5. *Experiment 5*: Parametric weight sensitivity analysis.

- **O9: Zero-Cost Open-Source Client-Server Implementation**  
  Build a fully asynchronous FastAPI backend service alongside an accessible, responsive Flutter mobile client utilizing OpenStreetMap tiles, device GPS location detection, and offline campus fallback.

- **O10: Automated Testing and Reproducibility Validation**  
  Establish an exhaustive automated test suite covering all units, algorithms, endpoints, and mobile views, verifying 100% test pass rates across both backend and client software layers.

---

## 3. Project Deliverables Matrix

| Deliverable ID | Description | Phase / Milestone | Status |
| :--- | :--- | :--- | :---: |
| **D1: Backend Architecture** | Asynchronous FastAPI core with error handlers, CORS, and Pydantic schemas | Phase 1 | ✅ Completed |
| **D2: Campus Graph Model** | Node and Edge JSON definitions with graph loader, validation, and Haversine math | Phase 2 | ✅ Completed |
| **D3: Dijkstra Baseline** | Dijkstra routing algorithm with distance and time measurement | Phase 3 | ✅ Completed |
| **D4: A\* Baseline** | Standard A\* algorithm with admissible Haversine heuristic | Phase 4 | ✅ Completed |
| **D5: Multi-Objective A\*** | Core personalized A\* algorithm with 5-weight vector, simplex validation, and presets | Phase 5 | ✅ Completed |
| **D6: Crowd ML Pipeline** | Synthetic dataset generator, preprocessing, training, evaluation, and serialized model | Phase 6 | ✅ Completed |
| **D7: ML-Routing Integration** | Dynamic edge crowd cost injection and real-time route recommendation endpoint | Phase 7 | ✅ Completed |
| **D8: Flutter Mobile App** | 14 production UI screens with Provider state management and API service layer | Phase 8 | ✅ Completed |
| **D9: OpenStreetMap Integration**| Zero-cost OpenStreetMap tile rendering, custom markers, route polylines, and zoom/pan | Phase 9 | ✅ Completed |
| **D10: Current Location & GPS** | Geolocator permission handling, GPS position detection, and nearest graph node snapping | Phase 10 | ✅ Completed |
| **D11: Explanation Engine** | Dynamic trade-off calculation engine and dedicated Route Explanation screen | Phase 11 | ✅ Completed |
| **D12: Research Experiments** | Reproducible scripts for Experiments 1–5, CSV outputs, and publication-ready plots | Research Phase | ✅ Completed |
| **D13: Research Documentation** | Complete theoretical, mathematical, empirical, and architectural documentation | Research Phase | ✅ Completed |

---

## 4. Verification & Testing Coverage

- **Automated Experiment Test Suite**: `backend/tests/test_experiments.py` (**5 / 5 passed**)
- **Backend Core Test Suite**: `backend/tests/` (**205 / 205 passed**)
- **Flutter Client Test Suite**: `mobile/test/` (**39 / 39 passed**)
- **Combined Automated Verification**: **244 / 244 passed (100%)**
