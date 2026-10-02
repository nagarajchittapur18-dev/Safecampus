# Research Problem

## Title
**A Multi-Objective AI-Based Personalized Safe Route Recommendation Framework for Smart Campus Navigation**

---

## 1. Context and Problem Statement

University and institutional campuses represent intricate, micro-urban ecosystems characterized by diverse pedestrian infrastructures—including academic complexes, research laboratories, residential halls, dining commons, athletic grounds, and arterial pathways. Navigating these spaces presents complex challenges that distinguish campus mobility from general urban vehicular or pedestrian transport:

1. **Complex Spatial Topologies**: Campuses frequently feature pedestrian-only zones, multi-level structures, elevation variations, staircases, and restricted-access courtyards that are absent or poorly indexed in global mapping platforms.
2. **Temporal Congestion and Dynamic Crowd Surges**: Pedestrian flow fluctuates dramatically according to university class timetables, examination schedules, public lectures, athletic meets, and dining hours. Pathways adjacent to lecture halls experience sudden surges of congestion that cause substantial delays and physical discomfort.
3. **Safety Disparities Across Space and Time**: Pathways vary widely in infrastructure safety attributes, including nocturnal illumination, surveillance coverage (CCTV monitoring), emergency call box proximity, and security patrol frequency. Route selection after dusk is a major concern for student safety and well-being.
4. **Accessibility Hurdles for Differently-Abled Users**: Differently-abled students, wheelchair users, and individuals with temporary physical limitations encounter insurmountable physical barriers such as steep gradients, unramped staircases, and irregular pavement. Conventional navigation tools routinely direct users toward paths with stairs.
5. **Divergent User Preferences**: No single objective metric (e.g., shortest physical distance) satisfies every pedestrian. A late student may prioritize travel velocity, a student walking alone at midnight prioritizes well-lit corridors, a wheelchair user requires strict universal accessibility, and an introverted or immunocompromised individual seeks minimal crowd exposure.

### Limitations of Existing Solutions
Mainstream consumer navigation systems (such as Google Maps, Apple Maps, and OpenStreetMap routers) are engineered primarily for vehicular transit or macro-scale urban walking. Consequently, they exhibit key systemic shortcomings when applied to smart campuses:
- **Single-Objective Optimization**: Standard engines almost exclusively compute shortest-distance or shortest-estimated-time paths using classical single-objective algorithms (e.g., Dijkstra or unweighted A*).
- **Static Graph Topologies**: Navigation graphs treat edge traversal costs as fixed geometric quantities, ignoring dynamic crowd conditions and safety annotations.
- **Lack of Preference Personalization**: Users cannot tune the path-finding objective function to weigh safety, accessibility, and crowd avoidance alongside physical distance.
- **Opaque Routing Decisions**: Recommended routes lack explanatory transparency, offering no justification of the trade-offs incurred (e.g., why a route that is 20 meters longer is recommended because it avoids high crowd density and dark corridors).

---

## 2. Research Motivation

The overarching motivation of SafeCampus AI is to transform campus mobility from a passive, distance-centric paradigm into an **intelligent, adaptive, multi-criteria recommendation system**. 

By synthesizing machine learning for micro-spatial crowd prediction with a formal multi-objective graph optimization engine, the framework seeks to:
- **Protect Student and Staff Safety**: Guide pedestrians toward well-lit, monitored corridors without imposing unreasonable distance detours.
- **Promote Universal Accessibility**: Ensure wheelchair users and mobility-impaired individuals are guaranteed obstacle-free paths with zero stairs and continuous ramps.
- **Alleviate Campus Pathway Congestion**: Distribute pedestrian flow smoothly across alternative campus corridors by proactively anticipating crowd peaks.
- **Foster Algorithmic Transparency**: Provide human-interpretable explanations of multi-objective route trade-offs, fostering user trust and agency.

---

## 3. Candidate Research Gap

> [!IMPORTANT]
> **Academic Integrity & Literature Validation Disclaimer**  
> The research gaps articulated herein are formulated as **candidate gaps** derived from initial exploratory analysis and structural systems comparison. In accordance with rigorous scientific methodology, these gaps must be systematically validated against contemporary literature (IEEE Xplore, ACM Digital Library, Springer, Elsevier) and must not be asserted as established facts prior to formal systematic literature indexing.

Preliminary exploration identifies the following core candidate research gaps:
1. **Decoupled Prediction and Optimization**: Existing works explore crowd counting or building occupancy forecasting in smart campuses, but rarely feed these predictive ML inferences into dynamic edge traversal weights within a multi-objective path-finding algorithm in real-time.
2. **Unified Multi-Criteria Pedestrian Cost Formulation**: Literature on pedestrian routing typically treats accessibility, personal safety, and crowd density as isolated concerns. A unified, mathematically constrained multi-objective framework that normalizes these heterogeneous factors on a simplex ($\sum w_i = 1$) remains underexplored in campus environments.
3. **Contrastive Multi-Objective Explanations**: While Explainable AI (XAI) has advanced in recommender systems, its application to spatial route selection—specifically explaining multi-criteria trade-offs relative to the Pareto-optimal shortest baseline—remains nascent.

---

## 4. Scope and Boundary Conditions

To ensure empirical reproducibility and scientific tractability, the scope of this research is defined as follows:
- **Spatial Scope**: Pedestrian outdoor network of an academic campus, modeled as an attributed directed graph $G = (V, E)$ comprising 26 key landmarks/junctions and 42 interconnected pathways.
- **Temporal Scope**: Dynamic crowd density modeled over hourly intervals, class transition periods, examination weeks, and special event schedules.
- **Data Provenance**:
  - *Campus Network Topology*: Modeled directly from physical campus coordinates, path lengths, lighting infrastructure, CCTV positioning, and accessibility survey data.
  - *Crowd Training Dataset*: Formulated via a controlled, reproducible synthetic spatial-temporal simulation ($N = 28,800$ records, seed 42) clearly labeled as synthetic data, establishing baseline ML feasibility without fabricating real-world sensor deployments.
- **Algorithmic Scope**: Exact graph search algorithms (Dijkstra, A*, and Personalized Multi-Objective A*) utilizing an admissible and consistent heuristic under scalarized multi-attribute utility theory.
