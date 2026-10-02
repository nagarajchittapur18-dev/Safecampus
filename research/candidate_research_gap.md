# Candidate Research Gaps

> [!IMPORTANT]
> **Academic Integrity & Literature Validation Disclaimer**  
> The research gaps documented in this section represent **candidate research gaps** formulated during the architectural and experimental development of SafeCampus AI. They stem from a critical analysis of current smart campus prototypes, commercial navigation tools, and general pedestrian routing research.
>
> In strict compliance with scholarly research ethics:
> 1. These gaps are **hypotheses** requiring confirmation through a formal, systematic literature review using the protocols detailed in [`literature_review_structure.md`](file:///c:/Users/Nagaraj/Desktop/Safecampus-AI/research/literature_review_structure.md).
> 2. They must **not** be presented in research publications as verified historical consensus until indexed against comprehensive bibliographic databases.

---

## 1. Candidate Gap 1: Decoupling of Predictive Micro-Spatial Crowd Inference from Graph Optimization

### Observation
Recent advances in smart campus IoT literature have extensively investigated crowd estimation, Wi-Fi probe tracking, and indoor room occupancy forecasting. Concurrently, a vast body of literature focuses on graph-based pedestrian route planning.

### The Candidate Gap
However, there appears to be a distinct **architectural decoupling** between predictive crowd modeling and real-time path-finding:
- Most predictive crowd models serve purely descriptive dashboards or administrative occupancy monitors without exposing API endpoints consumed by routing engines.
- Conversely, pedestrian navigation algorithms that incorporate dynamic congestion typically rely on live, instantaneous sensor readings rather than anticipatory, calendar-aware machine learning predictions.
- The direct injection of supervised ML classification inferences ($C \in \{\text{LOW}, \text{MEDIUM}, \text{HIGH}, \text{VERY\_HIGH}\}$) into edge-cost functions of an A\* heuristic search remains underexplored in campus micro-geographies.

### Verification Criterion
A systematic review must search for peer-reviewed papers that execute an end-to-end pipeline: `Temporal Features → Supervised ML Inference → Dynamic Edge Weighting → Heuristic Graph Search`. If fewer than 5 papers directly implement this workflow in a campus setting, this candidate gap will be considered confirmed.

---

## 2. Candidate Gap 2: Fragmented Multi-Criteria Pedestrian Cost Formulation

### Observation
Pedestrian routing literature has investigated several non-distance attributes:
- *Safe routing* works focus primarily on night-time crime avoidance, streetlighting, or CCTV coverage.
- *Accessible routing* works focus primarily on wheelchair slope constraints, curb cuts, and elevator access.
- *Comfort routing* works focus on shade, greenery, or noise reduction.

### The Candidate Gap
Existing systems rarely unify these divergent objectives into a **single, mathematically coherent, simplex-constrained utility framework**:
- Most algorithms treat constraints as binary filters (e.g., pruning all edges with stairs) or optimize bi-criteria pairs (distance vs. safety, or distance vs. accessibility).
- There is a noticeable lack of a five-dimensional, normalized formulation ($Cost(e) = w_D D + w_T T + w_C C + w_S S + w_A A$ subject to $\sum w_i = 1$) where users can dynamically modulate their personal profile across multiple valid presets (`shortest`, `fastest`, `safest`, `least_crowded`, `accessible`, `balanced`).

### Verification Criterion
Review literature to identify whether existing multi-objective campus routing systems integrate at least five simultaneous, normalized criteria on a strict probability simplex with proven heuristic admissibility.

---

## 3. Candidate Gap 3: Absence of Contrastive, Multi-Attribute Explanations in Navigation Systems

### Observation
Explainable Artificial Intelligence (XAI) has grown substantially across healthcare, finance, and algorithmic recommender systems. However, spatial navigation engines (both commercial tools and academic prototypes) remain largely "black boxes."

### The Candidate Gap
Navigation systems output turn-by-turn guidance or highlighted route polylines without offering **contrastive, multi-attribute justifications**:
- Users are not informed *why* a detour was recommended over the physical shortest path.
- Quantitative trade-offs (e.g., "This route is 12 meters longer (+3.0%) but avoids high crowd density and increases safety by 18.2%") are absent from consumer interfaces.
- The generation of dynamic, empirical explanations derived directly from multi-objective cost differentials relative to a shortest-path baseline remains rare in pedestrian wayfinding systems.

### Verification Criterion
Survey existing pedestrian and campus wayfinding literature to determine whether contrastive, feature-by-feature trade-off explanations against an optimal shortest-path baseline are implemented and evaluated for user trust.

---

## 4. Candidate Gap 4: Proprietary API Dependency vs. Zero-Cost Open Campus Mobility Stacks

### Observation
Many smart campus mobile applications depend upon commercial mapping stacks (e.g., Google Maps Platform, Mapbox, Apple MapKit).

### The Candidate Gap
This reliance creates significant functional and economic barriers for educational institutions:
- Commercial routing APIs incur recurring per-request licensing costs that limit large-scale student deployment.
- Commercial cartographic graphs do not permit custom modification of micro-campus pedestrian paths, interior pathways, temporary construction bypasses, or building entrances.
- A fully reproducible, zero-cost architecture unifying custom topological graphs, OpenStreetMap tile rendering, client-side GPS snapping, and an open FastAPI/Python backend represents a critical practical contribution for open science.

---

## 5. Summary of Candidate Gaps and Research Alignment

| Candidate Gap ID | Core Research Dimension | Corresponding Project Component | Evaluation Method |
| :--- | :--- | :--- | :--- |
| **Gap 1** | Dynamic ML Crowd Integration | Gradient Boosting $\to$ Multi-Objective A\* | Experiment 1 & Experiment 2 |
| **Gap 2** | Simplex-Constrained 5-Factor Formulation | Personalized Multi-Objective Cost Engine | Experiment 3, 4, & 5 |
| **Gap 3** | Contrastive Explainability Engine | Dynamic Trade-off Calculation Engine | Phase 11 Explanation Module |
| **Gap 4** | Zero-Cost Open Architecture | OpenStreetMap + FastAPI + Flutter Stack | Full-Stack Client-Server Deployment |
