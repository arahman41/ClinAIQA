# tech_stack.md

This file lists every component, why it is here, and how it maps to a named resume skill gap. Versions are intent, not pins; pin exact versions during Phase 0 and record them here.

## Backend
- **Python 3.11 or higher.** Primary language. Python appears in roughly 71 percent of AI engineering postings.
- **FastAPI.** Async API framework. Endpoints: submit output for audit, run audit, fetch audit record, fetch pass-rate history. Author already has FastAPI experience from InternTrack and MedElite.
- **Pydantic.** Request and response schemas, settings management (API keys and DB URL come from settings, never hardcoded).
- **uvicorn.** ASGI server.

## Database and vector store (closes the vector DB gap)
- **PostgreSQL 15 or higher.**
- **pgvector extension.** Embedding storage and cosine or inner-product similarity search. Deliberately one product rather than a separate vector database, extending the author's existing PostgreSQL fluency. The resume previously claimed RAG architecture without a shipped retrieval store; this closes that.
- **SQLAlchemy** plus **Alembic** for models and migrations.

## LLM
- **Claude API.** Rubric-based scoring (Layer 2) and compliance reasoning (Layer 3). Use a model-family choice appropriate to cost and latency; Sonnet-class for scoring throughput is the sensible default, escalate to Opus-class only where reasoning depth measurably helps. Wrap all calls behind one client module with retry and structured-output parsing.

## Embeddings
- An embedding model for the reference corpus and submitted claims. Decide in Phase 1 between a hosted embedding API and a local sentence-transformer. Constraint: whatever is chosen must run inside the Docker image for reproducible local and deployed behavior.

## Explainability (closes the SHAP gap)
- **SHAP.** Attribution for any learned classifier component, surfacing which input phrases drove a flag. Where flags are rule-based or retrieval-based, attribution is the matched phrase or missing-rule reference directly.

## Frontend
- **React.** Dashboard: verdict view, expandable flags with triggering phrase, pass rate over time line chart, audit record browser. Chosen over CLI-first or a GitHub-Action package for build speed inside the MVP window. Follow the interface-design skill for the audit-tool aesthetic.

## Testing (closes nothing on its own but underpins the SDET story)
- **Pytest.** Covers the scoring logic itself, not just the LLM API wrappers. Marker `harness` tags the core evaluation-logic tests the CI gate protects. See `testing.md`.

## CI/CD (closes the GitHub Actions deploy-gate gap)
- **GitHub Actions.** Runs Pytest on every push. Configured as a real deploy-blocking gate: merge is blocked when `pytest -m harness` fails. This is distinct from simply using git to push code, which the author already does fluently.

## Containerization (closes the Docker gap)
- **Docker** and **Docker Compose.** The full stack (FastAPI plus PostgreSQL with pgvector) runs identically locally and in deployment. One image for the API service.

## Deployment (closes the AWS gap)
- **AWS.** Target: ECS on Fargate behind an Application Load Balancer, with RDS for PostgreSQL 15 or higher running pgvector. Fallback: AWS App Runner pointed at the same image, still with RDS. Decision gate at start of Week 9. Render and Railway are excluded by design. Watch cost: smallest viable Fargate task and db.t-class RDS, stop when idle.

## Load testing (closes the LLM-aware load testing gap)
- **Locust** (preferred for Python-native scripting) or **JMeter** (author has production JMeter experience from Hashedin). Measures throughput and p95 latency under concurrent audit requests, accounting for the LLM call latency that conventional load tests do not. Output: a short results page with real numbers.

## Repository hygiene
- No notebooks, ever.
- `.env` for local secrets, never committed; `.env.example` documents the variables.
- No em dashes in any file.
