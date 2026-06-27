# ClinAIQA

**Clinical AI Quality Assurance.** A pre-deployment audit harness for healthcare-facing LLM output.

ClinAIQA takes any LLM-generated healthcare text and returns an evidence-backed pass or fail verdict covering grounding, hallucination detection, regulatory phrase compliance, and phrase-level explainability.

> Status: Phase 0 (foundation). See `AGENTS.md` for the full roadmap.

## Origin

ClinAIQA is the tool that should have been checking the author's own MedElite facility report generator, a FastAPI service that turned structured CMS data into narrative PDF and Word reports. That firsthand experience of shipping healthcare text with no safety net is the honest reason this project exists.

## Commands

```bash
docker compose up          # start FastAPI + PostgreSQL with pgvector locally
pytest                     # run the harness test suite
pytest -m harness          # run only the core evaluation-logic tests (CI gate)
python -m clinaiqa.eval.report_metrics  # precision and recall on held-out set
locust -f loadtest/locustfile.py        # load test
cd frontend && npm run dev              # React dashboard
```

## The five layers

| Layer | Description |
|-------|-------------|
| 1 | Retrieval-grounded fact checking (pgvector cosine similarity) |
| 2 | Hallucination and clinical claim detection (rubric-based, Claude API) |
| 3 | Regulatory and compliance phrase scanning (rule pack + LLM-assisted) |
| 4 | Explainability: phrase-level attribution, SHAP where a classifier is used |
| 5 | The harness around the harness: Pytest gate, GitHub Actions CI, Docker, AWS |

## Metrics

Precision and recall against the held-out adversarial test set are reported here at the end of the build from real measured numbers. Placeholder until then.

## Stack

Python 3.12, FastAPI, PostgreSQL 16 + pgvector, Claude API, SHAP, React, Pytest, GitHub Actions, Docker, AWS ECS Fargate + RDS.

## Constraints

- Synthetic data only. No real patient data, ever.
- The held-out adversarial set is never used to tune or build the detection rubric.
- All reported metrics are real measured values from the held-out set, never projected.
- Deployed on AWS. Not Render, not Railway.
