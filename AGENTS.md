# AGENTS.md, Master Plan for ClinAIQA

## Project overview
**App:** ClinAIQA (Clinical AI Quality Assurance)
**Goal:** A pre-deployment audit harness that takes any healthcare-facing LLM output and returns an evidence-backed pass or fail verdict across grounding, hallucination, regulatory phrasing, and explainability.
**Stack:** Python, FastAPI, PostgreSQL with pgvector, Claude API, SHAP, React, Pytest, GitHub Actions, Docker, AWS (ECS Fargate plus RDS, App Runner fallback), Locust or JMeter.
**Current phase:** Phase 0, foundation.

## How I should think
1. **Understand intent first.** This is a testing and compliance harness, not a generator. If a task drifts toward generating healthcare text rather than auditing it, stop and flag it.
2. **Ask if unsure.** If a requirement is ambiguous, ask before building. Do not invent scope.
3. **Plan before coding.** Propose a short plan, get approval, then implement one slice at a time.
4. **Verify after changes.** Run the relevant tests after each change. Never claim something works without running it.
5. **Explain trade-offs.** When choosing between options (for example ECS versus App Runner), state the trade-off briefly.

## Plan, execute, verify
1. **Plan:** Outline the approach for the current roadmap item, ask for approval.
2. **Execute:** One layer or one slice at a time.
3. **Verify:** Run Pytest and the relevant checks, fix before moving on. Evidence before claims.

## Context files (load only when needed)
- `agent_docs/project_brief.md`, persistent rules and vision, read this first alongside this file.
- `agent_docs/tech_stack.md`, every library, version intent, and setup command.
- `agent_docs/code_patterns.md`, naming, structure, error handling.
- `agent_docs/product_requirements.md`, requirements and success metrics summary.
- `agent_docs/testing.md`, test strategy and the leak-free discipline.
- `agent_docs/synthetic_data_archetypes.md`, the categories of healthy and adversarial synthetic data.
- `docs/PRD-ClinAIQA-MVP.md`, the full PRD.

## Current state
**Last updated:** June 27, 2026
**Working on:** Phase 1, synthetic data and retrieval.
**Recently completed:** Phase 0 complete. Git initialized, folder structure created per code_patterns.md, Docker Compose stack (FastAPI + pgvector/pgvector:pg16), Alembic migration enabling pgvector extension and stub embeddings table, Pydantic-settings-based Claude API client stub (clinaiqa/llm/client.py), pytest.ini with harness marker, placeholder failing test confirmed running, GitHub Actions CI workflow.
**Blocked by:** None.

## Roadmap

The week numbers below are a planning scaffold from the handover, not a fixed commitment. Treat each phase as a deliverable boundary.

### Phase 0: Foundation (start of Week 1)
- [x] Initialize repository, no notebooks, ever.
- [x] Set up Docker Compose for local FastAPI plus PostgreSQL with pgvector.
- [x] Confirm pgvector extension loads and a trivial similarity query runs.
- [x] Stub Claude API client with a settings-based key, never hardcoded.
- [x] Set up Pytest and a placeholder failing test to confirm the loop runs.

### Phase 1: Synthetic data and retrieval (Weeks 1 to 2)
- [ ] Generate healthy synthetic data (correct, grounded healthcare outputs plus their source records). See `agent_docs/synthetic_data_archetypes.md`.
- [ ] Generate adversarial synthetic data (injected hallucinations, wrong drug names, fabricated statistics, missing disclaimers, absolute claims).
- [ ] Split adversarial data into a rubric-tuning set and a held-out reporting set. Record the split with a fixed seed and never mix them. See `agent_docs/testing.md`.
- [ ] Embed reference documents into pgvector.
- [ ] Build the Layer 1 retrieval pipeline: chunk output into claims, retrieve passages, score grounding per sentence.

### Phase 2: Core evaluation harness (Weeks 3 to 4)
- [ ] Define the scoring rubric as input and expected-property pairs.
- [ ] Integrate the Claude API for rubric scoring (Layer 2).
- [ ] Construct the held-out adversarial test set in code, leak-free.
- [ ] Produce the first real precision and recall numbers on the held-out set.
- [ ] Write Pytest cases for the scoring logic, not just the API wrapper.

### Phase 3: Compliance and explainability (Weeks 5 to 6)
- [ ] Build the Layer 3 compliance scanner: rule pack plus LLM-assisted phrase scanning, each flag carries a rule ID and severity.
- [ ] Build the Layer 4 explainability: phrase-level attribution for every flag; SHAP where a learned classifier is involved.
- [ ] Solidify FastAPI endpoints: submit, audit, fetch record, pass-rate history.

### Phase 4: Dashboard (Week 7)
- [ ] React dashboard: verdict view, expandable flags with triggering phrase, pass rate over time, audit record browser.

### Phase 5: The harness around the harness (Week 8)
- [ ] Dockerize the full stack end to end.
- [ ] GitHub Actions workflow that runs Pytest on every push and blocks merge on failure of core evaluation logic.
- [ ] Confirm the gate actually blocks a deliberately broken commit.

### Phase 6: Deploy and load test (Week 9)
- [ ] AWS decision gate: ECS Fargate plus RDS if Docker and CI are stable, App Runner plus RDS if compressing.
- [ ] Deploy. Produce one public working URL.
- [ ] Run the load test (Locust or JMeter), capture throughput and p95 latency under concurrent audits.
- [ ] Write the short load test results page.

### Phase 7: Polish and harvest (Week 10, buffer)
- [ ] README: MedElite origin story, the five layers, honest OSCC relationship, real metrics.
- [ ] Demo recording.
- [ ] Draft resume bullets from the actual measured numbers, never projected.
- [ ] Final pass: confirm no notebooks, no em dashes.

## What NOT to do
- Do NOT generate the healthcare text itself. ClinAIQA audits, it never authors.
- Do NOT use any real patient data. Synthetic only, always.
- Do NOT let the held-out adversarial set leak into rubric tuning. This invalidates the headline metric.
- Do NOT report projected or aspirational precision and recall. Real measured numbers only.
- Do NOT deploy to Render or Railway. AWS is the deliberate goal.
- Do NOT add a notebook to the repository at any point.
- Do NOT use em dashes in code, comments, commit messages, or docs.
- Do NOT hardcode the Claude API key or any secret.
- Do NOT delete files or drop database tables without confirmation.
- Do NOT add features outside the current phase.
- Do NOT claim a step passes without running the check.
