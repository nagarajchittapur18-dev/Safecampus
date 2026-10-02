# Mathematical Formulation of Personalized Multi-Objective A\*

## 1. Graph Theoretical Foundation

Let the academic campus pedestrian network be formally represented as an attributed directed multigraph:

$$\mathcal{G} = (V, E)$$

where:
- $V = \{v_1, v_2, \dots, v_{|V|}\}$ represents the finite set of campus landmark nodes, pathway junctions, transit hubs, and building entrances ($|V| = 26$).
- $E \subseteq V \times V$ represents the set of directed, walkable pedestrian corridors ($|E| = 42$). Each directed edge $e = (u, v) \in E$ denotes an unobstructed walking connection from origin node $u$ to destination node $v$.

---

## 2. Edge Attribute Functions

Every directed edge $e \in E$ is associated with a tuple of physical and environmental attributes:

1. **Physical Geodesic Distance ($D$)**:
   $$D: E \to \mathbb{R}^+, \quad D(e) = \text{Haversine}(\text{coord}(u), \text{coord}(v))$$
   where coordinates $\text{coord}(u) = (\phi_u, \lambda_u)$ represent the latitude and longitude on the WGS84 ellipsoid.

2. **Base Travel Duration ($T$)**:
   $$T: E \to \mathbb{R}^+, \quad T(e) = \frac{D(e)}{v_{\text{walk}}}$$
   where $v_{\text{walk}} = 1.33 \text{ m/s}$ ($80 \text{ m/min}$) denotes the standard pedestrian walking velocity.

3. **Dynamic Crowd Density Cost ($C$)**:
   $$C: E \times \mathcal{T} \to [0, 1]$$
   where $\mathcal{T}$ represents the temporal context (hour, day, calendar event). Given node-level ML predictions $C_{\text{pred}}(u), C_{\text{pred}}(v) \in [0, 1]$, the edge crowd cost is defined as:
   $$C(e) = \frac{1}{2}\left(C_{\text{pred}}(u) + C_{\text{pred}}(v)\right)$$
   If dynamic ML inference is unavailable, the edge falls back to its static historical expectation $C_{\text{static}}(e)$.

4. **Environmental Safety Score ($S$)**:
   $$S: E \to [0, 1]$$
   synthesized from nocturnal lighting ($L(e) \in [0, 1]$), surveillance coverage ($\text{CCTV}(e) \in \{0, 1\}$), and security patrol frequency ($\text{Patrol}(e) \in [0, 1]$):
   $$S(e) = \alpha_1 L(e) + \alpha_2 \text{CCTV}(e) + \alpha_3 \text{Patrol}(e), \quad \sum_{j=1}^3 \alpha_j = 1.0$$

5. **Universal Accessibility Score ($A$)**:
   $$A: E \to [0, 1]$$
   reflecting pavement smoothness, presence of handrails, and ramp continuity.

---

## 3. Dimensionless Normalization Mappings

Because the raw attributes possess divergent physical dimensions (meters, minutes, dimensionless ratios), each component is transformed into a normalized penalty function bounded strictly within the closed unit interval $[0, 1]$:

$$\bar{D}(e) = \min\left(1.0, \frac{D(e)}{D_{\max}}\right)$$
$$\bar{T}(e) = \min\left(1.0, \frac{T(e)}{T_{\max}}\right)$$
$$\bar{C}(e) = \min\left(1.0, \max\left(0.0, C(e)\right)\right)$$
$$\bar{S}_{\text{cost}}(e) = 1.0 - S(e)$$
$$\bar{A}_{\text{cost}}(e) = \begin{cases} 1.0, & \text{if } \text{has\_stairs}(e) \land \neg \text{has\_ramp}(e) \\ 1.0 - A(e), & \text{otherwise} \end{cases}$$

where:
- $D_{\max} = \max_{e \in E} D(e)$ represents the maximum single edge length in the campus network graph.
- $T_{\max} = \frac{D_{\max}}{v_{\text{walk}}}$ represents the corresponding maximum single edge travel duration.
- For accessibility, an unramped staircase incurs a maximal impedance penalty of $1.0$, rendering it non-viable for mobility-constrained routing.

---

## 4. Multi-Objective Simplex Formulation

Let $\mathbf{w} = (w_D, w_T, w_C, w_S, w_A)^T$ define the user's personal preference weight vector. To preserve scale invariance and prevent metric dominance, the weight vector is constrained to the 4-dimensional probability simplex $\Delta^4$:

$$\Delta^4 = \left\{ \mathbf{w} \in \mathbb{R}^5 \;\middle|\; \sum_{i \in \{D, T, C, S, A\}} w_i = 1.0 \quad \text{and} \quad w_i \ge 0 \; \forall i \right\}$$

### Edge Traversal Cost Function
The total multi-objective traversal cost for an edge $e \in E$ under weight vector $\mathbf{w}$ is formulated as the convex linear scalarization:

$$Cost(e; \mathbf{w}) = w_D \bar{D}(e) + w_T \bar{T}(e) + w_C \bar{C}(e) + w_S \bar{S}_{\text{cost}}(e) + w_A \bar{A}_{\text{cost}}(e)$$

**Proposition 1 (Bounded Cost)**:  
*For any edge $e \in E$ and any valid weight vector $\mathbf{w} \in \Delta^4$, the edge cost satisfies:*
$$0.0 \le Cost(e; \mathbf{w}) \le 1.0$$

*Proof*:  
Since $\bar{D}(e), \bar{T}(e), \bar{C}(e), \bar{S}_{\text{cost}}(e), \bar{A}_{\text{cost}}(e) \in [0, 1]$ and $w_i \ge 0$, we have:
$$Cost(e; \mathbf{w}) = \sum_{i} w_i f_i(e) \le \sum_{i} w_i \cdot 1.0 = \sum_{i} w_i = 1.0$$
Similarly, $Cost(e; \mathbf{w}) \ge \sum_i w_i \cdot 0.0 = 0.0$. $\quad \blacksquare$

---

## 5. Path Cost and Optimization Formulation

Let a pedestrian path $P$ from origin $s \in V$ to destination $d \in V$ be defined as an ordered sequence of edges:
$$P = \langle e_1, e_2, \dots, e_k \rangle, \quad e_j = (u_{j-1}, u_j) \in E, \quad u_0 = s, \; u_k = d$$

Let $\mathcal{P}_{s, d}$ denote the set of all simple directed paths connecting $s$ to $d$. The cumulative path cost is additive:

$$Cost(P; \mathbf{w}) = \sum_{e \in P} Cost(e; \mathbf{w})$$

The optimal personalized route $P^*$ is the minimizer:

$$P^* = \arg\min_{P \in \mathcal{P}_{s, d}} Cost(P; \mathbf{w})$$

---

## 6. Admissible Heuristic and Proof of Optimality

To accelerate A\* search without sacrificing exact optimality, we formulate a normalized geographic heuristic function $h: V \to \mathbb{R}^+$:

$$h(u; d) = w_D \cdot \frac{\text{Haversine}(\text{coord}(u), \text{coord}(d))}{D_{\max}}$$

### Theorem 1 (Admissibility)
*The heuristic function $h(u; d)$ is strictly admissible, meaning it never overestimates the true remaining minimal multi-objective cost to the destination:*
$$h(u; d) \le Cost^*(u, d; \mathbf{w}), \quad \forall u \in V$$

*Proof*:  
Let $P^* = \langle e_1, e_2, \dots, e_m \rangle$ be the optimal path from node $u$ to destination $d$.
By definition of the multi-objective edge cost:
$$Cost(e; \mathbf{w}) \ge w_D \bar{D}(e) = w_D \frac{D(e)}{D_{\max}}$$
Summing over all edges along $P^*$:
$$Cost^*(u, d; \mathbf{w}) = \sum_{j=1}^m Cost(e_j; \mathbf{w}) \ge \sum_{j=1}^m w_D \frac{D(e_j)}{D_{\max}} = \frac{w_D}{D_{\max}} \sum_{j=1}^m D(e_j)$$
By the triangle inequality of the Haversine spherical geodesic metric:
$$\sum_{j=1}^m D(e_j) \ge \text{Haversine}(\text{coord}(u), \text{coord}(d))$$
Substituting this inequality yields:
$$Cost^*(u, d; \mathbf{w}) \ge \frac{w_D}{D_{\max}} \text{Haversine}(\text{coord}(u), \text{coord}(d)) = h(u; d)$$
Hence, $h(u; d) \le Cost^*(u, d; \mathbf{w})$, establishing admissibility. $\quad \blacksquare$

### Theorem 2 (Consistency / Monotonicity)
*The heuristic function $h(u; d)$ is consistent (monotonic), satisfying:*
$$h(u; d) \le Cost(e; \mathbf{w}) + h(v; d), \quad \forall e = (u, v) \in E$$

*Proof*:  
By the triangle inequality on the sphere:
$$\text{Haversine}(u, d) \le \text{Haversine}(u, v) + \text{Haversine}(v, d) = D(e) + \text{Haversine}(v, d)$$
Multiplying by the non-negative scalar $\frac{w_D}{D_{\max}}$:
$$h(u; d) \le w_D \frac{D(e)}{D_{\max}} + h(v; d) = w_D \bar{D}(e) + h(v; d)$$
Since $Cost(e; \mathbf{w}) = w_D \bar{D}(e) + \sum_{i \neq D} w_i f_i(e)$ and all non-distance cost components are non-negative ($f_i(e) \ge 0, w_i \ge 0$):
$$w_D \bar{D}(e) \le Cost(e; \mathbf{w})$$
Therefore:
$$h(u; d) \le Cost(e; \mathbf{w}) + h(v; d)$$
This establishes monotonicity, guaranteeing that A\* with this heuristic expands each node at most once and yields the globally optimal cost path $P^*$. $\quad \blacksquare$

---

## 7. Preference Presets

The framework defines six standardized weight vectors tailored to distinct user personas:

| Preset Name | Distance ($w_D$) | Travel Time ($w_T$) | Crowd Avoidance ($w_C$) | Safety Priority ($w_S$) | Accessibility ($w_A$) | Simplex Sum ($\sum w_i$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`shortest`** | **0.70** | 0.10 | 0.05 | 0.10 | 0.05 | 1.000 |
| **`fastest`** | 0.10 | **0.70** | 0.05 | 0.10 | 0.05 | 1.000 |
| **`safest`** | 0.10 | 0.05 | 0.05 | **0.70** | 0.10 | 1.000 |
| **`least_crowded`** | 0.10 | 0.05 | **0.70** | 0.10 | 0.05 | 1.000 |
| **`accessible`** | 0.10 | 0.05 | 0.05 | 0.10 | **0.70** | 1.000 |
| **`balanced`** | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 | 1.000 |

---

## 8. Multi-Criteria Pareto Optimality

In a multi-objective space, a path $P_1$ is said to **Pareto-dominate** another path $P_2$ ($P_1 \succ P_2$) if and only if:
$$\forall k \in \{D, T, C, S_{\text{cost}}, A_{\text{cost}}\}, \quad f_k(P_1) \le f_k(P_2)$$
$$\exists k \in \{D, T, C, S_{\text{cost}}, A_{\text{cost}}\}, \quad f_k(P_1) < f_k(P_2)$$

A path $P^* \in \mathcal{P}_{s, d}$ is **Pareto-optimal** if there exists no path $P' \in \mathcal{P}_{s, d}$ such that $P' \succ P^*$.

By applying the weighted sum scalarization with strictly positive weights ($w_i > 0$), the optimal solution $P^*$ obtained by Personalized Multi-Objective A\* is guaranteed to belong to the Pareto-optimal set (nondominated frontier) of the campus graph.
