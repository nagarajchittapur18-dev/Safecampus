# Scientific and Practical Limitations

A foundational requirement of rigorous academic research is the transparent identification of methodological, computational, and empirical limitations. This document articulates the explicit boundaries and constraints of the SafeCampus AI framework.

---

## 1. Data Provenance and Synthetic Crowd Simulation

### Limitation
The machine learning crowd prediction pipeline was developed, trained, and benchmarked on a high-fidelity **synthetic temporal-spatial simulation** ($N = 28,800$ records, seed 42) rather than physical IoT sensor streams.

### Scientific Implications
- While the synthetic data accurately models diurnal academic timetables, class dismissal surges, examination weeks, and weekend quiet periods, it does not capture spontaneous, unmodeled human behavioral phenomena—such as sudden impromptu student gatherings, unannounced flash protests, or localized weather-induced stampedes.
- The high classification accuracy ($93.28\%$) achieved by the Gradient Boosting model reflects performance on structured synthetic probability distributions; deployment in a live campus environment with physical sensor noise may result in a distribution shift and lower real-world accuracy.
- **Academic Standard**: The results of Experiment 1 must be interpreted as a proof-of-concept demonstrating algorithmic feasibility rather than an empirical claim of real-world crowd dynamics.

---

## 2. Topological Graph Discretization

### Limitation
The campus walking environment is modeled as a discrete, attributed directed multigraph $G = (V, E)$ consisting of 26 nodes and 42 pathway edges.

### Scientific Implications
- Real-world campus pedestrians frequently traverse unpaved desire paths, lawns, open plazas, and parking lots that are not captured in the 1D graph skeleton.
- Obstacles within corridors (e.g., temporary construction scaffolding, parked maintenance vehicles, fallen tree branches) are not dynamically detected unless manually updated in the graph configuration files.
- Elevation changes and vertical indoor staircases across multi-story buildings are represented as discrete edge attributes rather than full 3D spatial geometry.

---

## 3. Static Safety and Environmental Attributes

### Limitation
Physical safety attributes (nocturnal lighting ratings, CCTV surveillance presence, and security patrol frequency) and accessibility metrics are currently modeled as static edge attributes derived from physical audits.

### Scientific Implications
- Environmental conditions change dynamically: a burned-out streetlamp immediately degrades corridor safety, heavy rainfall creates slippery surfaces that compromise accessibility, and security patrol routes change shift schedules.
- The framework currently lacks a real-time crowdsourcing or IoT telemetry feedback loop to dynamically update edge safety and accessibility scores during operational runtime.

---

## 4. Uniform Pedestrian Walking Velocity

### Limitation
Travel time calculations assume a constant, uniform walking velocity of $v_{\text{walk}} = 1.33 \text{ m/s}$ ($80 \text{ m/min}$) across all pedestrians and pathways.

### Scientific Implications
- Walking speeds vary significantly across demographic cohorts, age groups, physical fitness levels, and carrying loads (e.g., heavy backpacks).
- Differently-abled pedestrians using manual or motorized wheelchairs experience different velocities on inclines and ramps compared to able-bodied pedestrians on flat surfaces.
- Ambient environmental factors (inclement weather, heatwaves, extreme rain) slow walking speeds, which is currently unmodeled in the deterministic transit time equation.

---

## 5. Linear Scalarization of the Multi-Objective Frontier

### Limitation
The Personalized Multi-Objective A\* solver employs a convex linear weighted-sum scalarization:
$$Cost(e) = \sum_{i} w_i f_i(e), \quad \sum_{i} w_i = 1.0$$

### Scientific Implications
- While linear scalarization permits sub-millisecond execution ($< 0.1 \text{ ms}$) and guarantees that the solution belongs to the Pareto-optimal set, it is theoretically incapable of finding non-convex portions of the Pareto front in multi-criteria space.
- The user must choose an *a priori* preference preset or manual weight vector, rather than inspecting a set of multiple Pareto-optimal alternative paths generated *a posteriori*.

---

## 6. Offline Map Tile Caching Constraints

### Limitation
The mobile client leverages OpenStreetMap (OSM) raster tiles rendered via `flutter_map`.

### Scientific Implications
- While manual campus landmark selection, routing computation, and text explanations function entirely offline, interactive map visualization relies on cached tiles.
- If a user opens the mobile application in a cellular dead zone without prior map tile caching, the visual map background will display blank grid tiles, although the underlying routing engine, node coordinate snapping, and textual instructions remain fully operational.

---

## 7. Template-Based Explanation Generation

### Limitation
The Route Explanation Engine synthesizes natural language justifications using rule-based templates grounded in exact mathematical percentage differentials relative to the shortest path baseline.

### Scientific Implications
- The explanations do not employ generative large language models (LLMs) or continuous feature attribution frameworks (such as Graph LIME or Graph SHAP).
- While this ensures zero hallucination, strict factual accuracy, and instantaneous execution, the syntactic variability and conversational flexibility of the generated explanations are constrained by the underlying template grammar.
