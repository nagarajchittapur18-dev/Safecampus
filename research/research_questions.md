# Research Questions and Hypotheses

## 1. Primary Research Question

**RQ1 (System Efficacy)**:  
*Can a personalized multi-objective route recommendation system—integrating machine learning crowd prediction with physical safety scoring and universal accessibility constraints—provide quantitatively superior, context-tailored campus navigation outcomes compared to classical single-objective shortest-path algorithms (Dijkstra, A\*) on a pedestrian campus network?*

---

## 2. Secondary Research Questions

### Machine Learning and Predictive Intelligence
- **RQ2 (Predictive Accuracy)**:  
  *How accurately can supervised machine learning models predict discrete campus crowd density levels ($C \in \{\text{LOW}, \text{MEDIUM}, \text{HIGH}, \text{VERY\_HIGH}\}$) utilizing temporal attributes, academic calendar cycles, location typologies, and historical moving averages?*
- **RQ3 (Model Selection and Deployment Efficiency)**:  
  *Which classification architecture among Logistic Regression, Decision Tree, Random Forest, and Gradient Boosting provides the optimal trade-off between Macro F1-score and inference latency ($\mu\text{s/sample}$) for sub-millisecond route optimization pipelines?*

### Multi-Objective Path Optimization
- **RQ4 (Personalization and Pareto Trade-offs)**:  
  *How do user-configured objective weight vectors $\mathbf{w} = (w_D, w_T, w_C, w_S, w_A)$ across preference presets (`shortest`, `fastest`, `safest`, `least_crowded`, `accessible`, `balanced`) alter the Pareto frontier between physical travel distance, transit time, crowd exposure, physical safety, and universal accessibility?*
- **RQ5 (Factor Contribution / Cumulative Ablation)**:  
  *What is the marginal impact on path geometry and route quality metrics when routing objectives are cumulatively introduced into the cost function—from single-objective distance minimization ($w_D = 1.0$) up to the full five-factor multi-objective formulation ($\sum w_i = 1.0$)?*
- **RQ6 (Parametric Weight Sensitivity)**:  
  *How sensitive are route selection decisions, physical path lengths, and safety/accessibility indices to systematic parametric variations of individual objective weights over the continuum $w_i \in [0.10, 0.90]$ under simplex conservation?*

---

## 3. Formulated Research Hypotheses

The following hypotheses were formulated *a priori* to guide the empirical investigation. Each hypothesis defines clear, quantifiable criteria for empirical confirmation or refutation based on experimental data:

### Hypothesis H1 (Safety Maximization Trade-off)
> **Statement**: Under the `safest` preference preset ($w_S = 0.70$), the multi-objective algorithm will identify paths with a safety index significantly higher than the baseline shortest path ($\ge 5\%$ relative gain), while incurring a distance detour of less than $10\%$.
>
> **Evaluation Metric**: Path safety score $\bar{S}(P) \in [0, 1]$ and relative distance detour $\Delta D = \frac{D(P_{\text{safest}}) - D(P_{\text{shortest}})}{D(P_{\text{shortest}})} \times 100\%$.

### Hypothesis H2 (Crowd Avoidance Trade-off)
> **Statement**: Under the `least_crowded` preference preset ($w_C = 0.70$), the algorithm will direct pedestrians toward lower-density corridors, reducing average path crowd exposure by at least $15\%$ relative to the physical shortest path, with an execution latency remaining under $5.0$ milliseconds.
>
> **Evaluation Metric**: Crowd score $\bar{C}(P) \in [0, 1]$ and algorithmic execution time in milliseconds.

### Hypothesis H3 (Strict Accessibility Compliance)
> **Statement**: Under the `accessible` preference preset ($w_A = 0.70$), the algorithm will strictly penalize non-ramped staircases ($A_{\text{cost}} = 1.0$), ensuring $100\%$ avoidance of impassable obstacles and selecting exclusively ramped and paved corridors.
>
> **Evaluation Metric**: Number of unramped stair segments in the recommended path ($N_{\text{stairs}} = 0$) and path accessibility score $\bar{A}(P)$.

### Hypothesis H4 (Nonlinear Ensemble Superiority in Crowd Classification)
> **Statement**: Tree-based ensemble models (Random Forest, Gradient Boosting) will outperform linear baselines (Logistic Regression) by at least $15\%$ in Macro F1-score due to complex nonlinear interactions between academic schedule flags and location typologies.
>
> **Evaluation Metric**: Multi-class Macro F1-score on a stratified 20% test partition ($N_{\text{test}} = 5,760$).

### Hypothesis H5 (Parametric Monotonicity in Weight Sensitivity)
> **Statement**: As an individual objective weight $w_i$ monotonically increases from $0.10$ to $0.90$ with remaining weights uniformly distributed, the corresponding path performance attribute $f_i(P)$ will respond monotonically, proving algorithmic stability without chaotic route oscillations.
>
> **Evaluation Metric**: Monotonic response curve of distance, travel time, crowd score, safety score, and accessibility score as a function of $w_i$.

---

> [!NOTE]
> All hypotheses are tested systematically in Experiments 1 through 5 using reproducible empirical procedures with seed 42. Empirical verification status is documented in [`experimental_setup.md`](file:///c:/Users/Nagaraj/Desktop/Safecampus-AI/research/experimental_setup.md) and [`evaluation_metrics.md`](file:///c:/Users/Nagaraj/Desktop/Safecampus-AI/research/evaluation_metrics.md).
