# Future Research Directions

Building upon the empirical and architectural foundations established in SafeCampus AI, this document outlines high-priority research vectors for subsequent phases of investigation.

---

## 1. Physical IoT Sensor Integration and Real-World Crowd Telemetry

### Objective
Transition the crowd prediction pipeline from synthetic simulation to empirical campus IoT sensor streams while maintaining strict data privacy:
- **Anonymized Wi-Fi Probe Analytics**: Ingest real-time access point association counts across campus Wi-Fi infrastructure (e.g., Cisco/Aruba enterprise networks), leveraging device counts per building as continuous ground truth.
- **Privacy-Preserving Optical Edge Counters**: Deploy low-power edge microcontrollers (e.g., Raspberry Pi with Hailo/Edge TPU) running lightweight people-counting models (e.g., YOLO-nano) at building entry portals, streaming only aggregate numerical headcounts without transmitting video feeds or PII.
- **Bluetooth Low Energy (BLE) Beacons**: Deploy battery-operated BLE beacons along major pathway corridors to enable continuous micro-spatial positioning and crowd density estimation.

---

## 2. Non-Scalarized True Pareto Frontier Generation

### Objective
Advance beyond linear scalarized A\* search to explore the complete non-convex Pareto frontier:
- **Multiobjective A\* (NAMOA\* / BOA\*)**: Implement exact multiobjective label-setting algorithms capable of returning the complete set of Pareto-optimal non-dominated paths $\mathcal{P}_{\text{Pareto}}$ for a given origin-destination query.
- **Evolutionary Multi-Objective Optimization (NSGA-II)**: Adapt genetic path-planning heuristics for large-scale campus graphs where exact multi-objective search becomes computationally intractable.
- **Interactive Multi-Route Selection**: Rather than presenting a single pre-calculated route, render the top 3 non-dominated paths on the mobile canvas (e.g., *Path A: 350m / 4.4 min / moderate crowd* vs. *Path B: 370m / 4.6 min / zero crowd / 100% lit*), empowering users to visually inspect and select their preferred trade-off.

---

## 3. Dynamic Graph Streaming and Incident Management

### Objective
Transform the static campus graph into a real-time reactive spatial network:
- **Event-Driven Architecture**: Ingest real-time campus alerts via an MQTT / Kafka event bus to dynamically mutate edge weights during active incidents (e.g., pathway maintenance, waterlogging, fallen trees, or security alarms).
- **Crowdsourced Hazard Verification**: Implement a student reporting interface allowing pedestrians to flag hazards (e.g., broken streetlights, aggressive stray animals, unramped temporary barriers) coupled with a consensus/reputation algorithm to prevent spam and verify reports.

---

## 4. Personalized Mobility & Heterogeneous Velocity Profiles

### Objective
Refine travel time estimation by moving beyond the uniform $1.33 \text{ m/s}$ walking velocity:
- **User-Specific Velocity Profiling**: Allow users to optionally record their comfortable walking pace or select a mobility profile (e.g., brisk walker, leisurely walker, motorized wheelchair, manual wheelchair, crutches).
- **Physical Incline and Rolling Resistance Modeling**: Incorporate 3D digital elevation models (DEM) to compute slope gradients, dynamically penalizing uphill wheelchair transit and adjusting travel times according to physical grade.

---

## 5. Human-Centered Evaluation and Field Trials

### Objective
Validate the system’s real-world impact through an institutional review board (IRB) approved user study:
- **Field Trial Design**: Conduct a multi-week deployment with a diverse cohort of campus participants ($N \ge 100$), including undergraduate students, late-night research scholars, security personnel, and differently-abled individuals.
- **Evaluation Dimensions**:
  - *Route Compliance Rate*: Measure the percentage of recommended paths actually followed by participants.
  - *Perceived Safety & Comfort*: Quantify subjective safety before and after route completion via standardized psychometric surveys (e.g., Likert-scale comfort ratings).
  - *Cognitive Load (NASA-TLX)*: Measure the mental effort required to interpret the route explanation views versus traditional map displays.

---

## 6. Generative Explainable AI (XAI) and Dialogue Interfaces

### Objective
Enhance explanation transparency and conversational interaction:
- **Dialogue Agent Integration**: Integrate an on-device or edge-hosted lightweight Large Language Model (e.g., Gemma 2B) to allow users to ask conversational follow-up questions (e.g., *"Why did you avoid Central Avenue?"* $\to$ *"Central Avenue has a predicted crowd density of 85% due to class dismissal at the adjacent lecture hall"*).
- **Counterfactual Reasoning**: Develop formal counterfactual explanation modules demonstrating what minimum environmental change would be required to make the shortest path viable (e.g., *"If Central Avenue crowd drops below 40%, it becomes the recommended path"*).

---

## 7. Cross-Institutional Transferability

### Objective
Assess the generalizability of the SafeCampus AI architecture across alternative closed-campus environments:
- **Hospital and Medical Campuses**: Navigation across medical centers where patient mobility, sterile zones, and emergency corridors impose strict routing constraints.
- **Airport Terminals and Transit Hubs**: Managing passenger flow between check-in, security gates, and boarding lounges under flight schedule surge dynamics.
- **Industrial Parks and Corporate Facilities**: Safety-critical routing in large manufacturing plants requiring active avoidance of heavy machinery transit zones.
