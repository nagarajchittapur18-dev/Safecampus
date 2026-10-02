# SafeCampus AI — Research Documentation Index

This directory contains the complete academic and technical research documentation for **SafeCampus AI: A Multi-Objective AI-Based Personalized Safe Route Recommendation Framework for Smart Campus Navigation**.

---

## Document Catalog & Structure

| Document | Primary Scope | Core Content Explained |
| :--- | :--- | :--- |
| [`research_problem.md`](research_problem.md) | **Problem & Motivation** | Micro-urban campus challenges, failure of single-objective routing, student safety, and accessibility needs. |
| [`research_questions.md`](research_questions.md) | **Research Questions & Hypotheses** | Primary RQ1, secondary RQ2–RQ6, and testable hypotheses H1–H5 with empirical falsification criteria. |
| [`objectives.md`](objectives.md) | **Objectives & Deliverables** | Primary research objective, specific objectives O1–O10, and project deliverables matrix. |
| [`literature_review_structure.md`](literature_review_structure.md) | **Literature Review Taxonomy** | 5 thematic review domains, database search protocol, Boolean queries, and comparative matrix template. |
| [`candidate_research_gap.md`](candidate_research_gap.md) | **Candidate Research Gaps** | 4 candidate gaps (ML-routing decoupling, fragmented multi-criteria, absence of XAI, proprietary lock-in) with integrity disclaimers. |
| [`proposed_methodology.md`](proposed_methodology.md) | **Methodology & Architecture** | End-to-end architecture, spatial campus graph, ML crowd pipeline, Multi-Objective A*, explanation engine, and Flutter client. |
| [`mathematical_model.md`](mathematical_model.md) | **Mathematical Formulation** | Formal graph definitions, $[0, 1]$ normalization mappings, simplex cost function $\sum w_i = 1$, heuristic admissibility proofs, and Pareto dominance. |
| [`experimental_setup.md`](experimental_setup.md) | **Experimental Protocols & Data** | System specifications, benchmark OD pairs, synthetic crowd dataset ($N=28,800$, seed 42), and protocols for Exp 1–5. |
| [`evaluation_metrics.md`](evaluation_metrics.md) | **Evaluation Metrics** | Mathematical formulations for ML metrics (Accuracy, F1, Latency), routing indices (Distance, Time, Safety, Crowd, Accessibility), and empirical results. |
| [`limitations.md`](limitations.md) | **Scientific Boundaries** | Transparent analysis of synthetic data, graph discretization, static edge ratings, uniform walking speed, and scalarization. |
| [`future_work.md`](future_work.md) | **Future Research Vectors** | Empirical IoT telemetry, non-scalarized Pareto search (NAMOA*), event streaming, personalized walking pace, and human field trials. |

---

## Mapping to Research Requirements

1. **Problem**: Addressed in [`research_problem.md`](research_problem.md).
2. **Motivation**: Addressed in [`research_problem.md`](research_problem.md).
3. **Research Questions**: Formulated in [`research_questions.md`](research_questions.md).
4. **Objectives**: Formulated in [`objectives.md`](objectives.md).
5. **Candidate Research Gap**: Detailed with verification criteria in [`candidate_research_gap.md`](candidate_research_gap.md).
6. **Proposed Methodology**: Architected in [`proposed_methodology.md`](proposed_methodology.md).
7. **Algorithms**: Detailed in [`proposed_methodology.md`](proposed_methodology.md) and [`mathematical_model.md`](mathematical_model.md).
8. **Mathematical Formulation**: Formally proven in [`mathematical_model.md`](mathematical_model.md).
9. **Dataset**: Specified with parameters and distributions in [`experimental_setup.md`](experimental_setup.md).
10. **ML Methodology**: Explained in [`proposed_methodology.md`](proposed_methodology.md) and [`experimental_setup.md`](experimental_setup.md).
11. **Experiments**: Documented across [`experimental_setup.md`](experimental_setup.md) and [`evaluation_metrics.md`](evaluation_metrics.md).
12. **Metrics**: Defined mathematically in [`evaluation_metrics.md`](evaluation_metrics.md).
13. **Limitations**: Critically analyzed in [`limitations.md`](limitations.md).

---

## Reproducibility & Code Links

- **Automated Experiment Runner**: [`run_all_experiments.py`](run_all_experiments.py) executes Experiments 1 through 5 sequentially in ~24 seconds.
- **Empirical CSV Datasets**: Stored under [`results/`](results/).
- **High-Resolution Figures**: Stored under [`figures/`](figures/).
- **Synthesis Report**: [`results/EXPERIMENT_SUMMARY.md`](results/EXPERIMENT_SUMMARY.md).
