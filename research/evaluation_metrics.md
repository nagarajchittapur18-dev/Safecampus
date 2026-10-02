# Evaluation Metrics and Mathematical Definitions

This document details the mathematical definitions, equations, and evaluation criteria employed to assess the predictive machine learning models and multi-objective routing algorithms in SafeCampus AI.

---

## 1. Machine Learning Classification Metrics

For a multi-class classification problem with $K = 4$ discrete crowd classes ($\text{LOW}, \text{MEDIUM}, \text{HIGH}, \text{VERY\_HIGH}$), let:
- $TP_k$: True Positives for class $k$
- $FP_k$: False Positives for class $k$
- $FN_k$: False Negatives for class $k$
- $TN_k$: True Negatives for class $k$
- $N$: Total number of test samples ($N = 5,760$)
- $N_k$: Support (number of true instances) for class $k$

### 1. Overall Accuracy
The fraction of correctly classified instances across all classes:
$$\text{Accuracy} = \frac{\sum_{k=1}^K TP_k}{N}$$

### 2. Macro-Averaged Precision
The arithmetic mean of class-specific precisions, giving equal weight to each crowd class regardless of class imbalance:
$$\text{Precision}_k = \frac{TP_k}{TP_k + FP_k}$$
$$\text{Precision}_{\text{macro}} = \frac{1}{K} \sum_{k=1}^K \text{Precision}_k$$

### 3. Macro-Averaged Recall
The arithmetic mean of class-specific recall rates, measuring the model's sensitivity in identifying crowd surges:
$$\text{Recall}_k = \frac{TP_k}{TP_k + FN_k}$$
$$\text{Recall}_{\text{macro}} = \frac{1}{K} \sum_{k=1}^K \text{Recall}_k$$

### 4. Macro-Averaged F1-Score
The harmonic mean of macro-precision and macro-recall:
$$\text{F1}_k = \frac{2 \cdot \text{Precision}_k \cdot \text{Recall}_k}{\text{Precision}_k + \text{Recall}_k}$$
$$\text{F1}_{\text{macro}} = \frac{1}{K} \sum_{k=1}^K \text{F1}_k$$

### 5. Multi-Class Confusion Matrix
A $K \times K$ contingency matrix $M$ where element $M_{i, j}$ represents the count of instances whose ground-truth class is $i$ and predicted class is $j$:
$$M_{i, j} = \sum_{m=1}^N \mathbb{I}(y_m = i \land \hat{y}_m = j)$$
where $\mathbb{I}(\cdot)$ is the indicator function.

### 6. Computational Efficiency Metrics
- **Training Time ($t_{\text{train}}$)**: Total wall-clock time in milliseconds to fit the model on $N_{\text{train}} = 23,040$ samples.
- **Inference Latency ($\tau_{\text{infer}}$)**: Mean execution time in microseconds per single sample inference:
  $$\tau_{\text{infer}} = \frac{t_{\text{eval}}}{N_{\text{test}}} \times 10^6 \quad (\mu\text{s/sample})$$

---

## 2. Multi-Objective Routing Performance Metrics

Let a recommended route $P$ consisting of $|P|$ directed edges $e_1, e_2, \dots, e_{|P|}$ be evaluated under the following spatial and environmental indices:

### 1. Physical Route Distance ($D(P)$)
The cumulative geographic length along the path in meters:
$$D(P) = \sum_{e \in P} D(e) \quad (\text{meters})$$

### 2. Total Transit Duration ($T(P)$)
The cumulative pedestrian transit time in minutes:
$$T(P) = \sum_{e \in P} T(e) = \sum_{e \in P} \frac{D(e)}{80.0} \quad (\text{minutes})$$

### 3. Path-Averaged Crowd Exposure Index ($\bar{C}(P)$)
The mean normalized crowd density encountered along the path:
$$\bar{C}(P) = \frac{1}{|P|} \sum_{e \in P} C(e) \in [0, 1]$$
- $\bar{C} < 0.28$: `LOW` density corridor.
- $0.28 \le \bar{C} < 0.52$: `MEDIUM` density corridor.
- $0.52 \le \bar{C} < 0.74$: `HIGH` density corridor.
- $\bar{C} \ge 0.74$: `VERY_HIGH` density corridor.

### 4. Path-Averaged Safety Index ($\bar{S}(P)$)
The mean environmental safety score along the path:
$$\bar{S}(P) = \frac{1}{|P|} \sum_{e \in P} S(e) \in [0, 1]$$
where higher scores reflect well-lit, CCTV-monitored, security-patrolled corridors.

### 5. Path-Averaged Accessibility Compliance Index ($\bar{A}(P)$)
The mean universal accessibility score along the path:
$$\bar{A}(P) = \frac{1}{|P|} \sum_{e \in P} A(e) \in [0, 1]$$
subject to the staircase penalty rule:
$$\text{If } \exists e \in P \text{ s.t. } (\text{has\_stairs}(e) \land \neg \text{has\_ramp}(e)) \implies \bar{A}_{\text{cost}}(e) = 1.0$$

### 6. Cumulative Multi-Objective Cost ($Cost(P; \mathbf{w})$)
The scalarized objective function minimized by the A\* search:
$$Cost(P; \mathbf{w}) = \sum_{e \in P} \left( w_D \bar{D}(e) + w_T \bar{T}(e) + w_C \bar{C}(e) + w_S \bar{S}_{\text{cost}}(e) + w_A \bar{A}_{\text{cost}}(e) \right)$$

### 7. Algorithmic Execution Latency ($t_{\text{exec}}$)
The wall-clock computation time required to execute the graph search, measured in milliseconds using Python’s monotonic high-resolution timer (`time.perf_counter()`):
$$t_{\text{exec}} = (t_{\text{end}} - t_{\text{start}}) \times 1000.0 \quad (\text{ms})$$

---

## 3. Comparative Trade-off Metrics

To measure the marginal gain or penalty incurred by choosing a personalized route $P^*$ over the physical shortest path baseline $P_{\text{shortest}}$, the system computes relative trade-off percentages:

$$\Delta D = \frac{D(P^*) - D(P_{\text{shortest}})}{D(P_{\text{shortest}})} \times 100\% \quad (\text{Distance Detour})$$
$$\Delta T = \frac{T(P^*) - T(P_{\text{shortest}})}{T(P_{\text{shortest}})} \times 100\% \quad (\text{Time Detour})$$
$$\Delta C = \frac{\bar{C}(P^*) - \bar{C}(P_{\text{shortest}})}{\bar{C}(P_{\text{shortest}})} \times 100\% \quad (\text{Crowd Reduction})$$
$$\Delta S = \frac{\bar{S}(P^*) - \bar{S}(P_{\text{shortest}})}{\bar{S}(P_{\text{shortest}})} \times 100\% \quad (\text{Safety Enhancement})$$
$$\Delta A = \frac{\bar{A}(P^*) - \bar{A}(P_{\text{shortest}})}{\bar{A}(P_{\text{shortest}})} \times 100\% \quad (\text{Accessibility Enhancement})$$

---

## 4. Empirical Baseline Reference Summary

The following empirical results were recorded across Experiments 1 through 5:

### Supervised Classification Benchmarks (Test Set $N = 5,760$)
| Architecture | Accuracy | Macro Precision | Macro Recall | Macro F1 | Inference Latency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Logistic Regression | 74.48% | 0.5367 | 0.5471 | 0.5418 | $0.43 \;\mu\text{s}$ |
| Decision Tree | 91.30% | 0.8122 | 0.8110 | 0.8116 | $0.54 \;\mu\text{s}$ |
| Random Forest | 92.57% | 0.8263 | 0.8247 | 0.8254 | $13.91 \;\mu\text{s}$ |
| **Gradient Boosting** | **93.28%** | **0.8369** | **0.8363** | **0.8366** | $4.88 \;\mu\text{s}$ |

### Routing Algorithm Performance Across 12 Benchmark OD Pairs
| Metric | Dijkstra Baseline | A\* Baseline | Multi-Objective A\* (`balanced`) | Relative Gain / Detour |
| :--- | :---: | :---: | :---: | :---: |
| **Physical Distance** | 352.1 m | 352.1 m | 355.8 m | +1.06% (+3.7 m) |
| **Travel Duration** | 4.40 min | 4.40 min | 4.45 min | +1.06% (+0.05 min) |
| **Crowd Exposure** | 0.449 | 0.449 | 0.387 | **-13.8%** |
| **Safety Score** | 0.831 | 0.831 | 0.865 | **+4.1%** |
| **Accessibility Score**| 0.824 | 0.824 | 0.854 | **+3.6%** |
| **Execution Latency** | 0.014 ms | 0.025 ms | 0.072 ms | All $< 0.1 \text{ ms}$ |
