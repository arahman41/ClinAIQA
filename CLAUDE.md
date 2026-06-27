# CLAUDE.md, Claude Code Configuration for ClinAIQA

## Project context
**App:** ClinAIQA, a pre-deployment audit harness for healthcare-facing LLM output.
**Stack:** Python, FastAPI, PostgreSQL with pgvector, Claude API, SHAP, React, Pytest, GitHub Actions, Docker, AWS.
**Stage:** MVP development.

## Directives
1. **Master plan first.** Read `AGENTS.md` for the current phase and the active task before doing anything.
2. **Brief first.** Read `agent_docs/project_brief.md` for the non-negotiable rules.
3. **Documentation on demand.** Pull specifics from `agent_docs/` and `docs/PRD-ClinAIQA-MVP.md` rather than guessing.
4. **Plan first.** Propose a short plan for the current task and wait for approval before writing code.
5. **Incremental.** One layer or one slice at a time. Test after each.
6. **Evidence before claims.** Never say something is fixed, passing, or done without running the check and seeing the output. Follow the verification-before-completion discipline.
7. **Concise.** Be brief. Ask clarifying questions when a requirement is ambiguous.

## Hard rules (these override convenience)
- ClinAIQA audits healthcare LLM output; it never generates it.
- Synthetic data only. No real patient data, ever.
- The held-out adversarial test set must never be used to tune or build the detection rubric. Keep the split fixed and seeded. See `agent_docs/testing.md`.
- Report only real measured precision and recall from the held-out set. Never projected.
- No notebooks in the repository.
- No em dashes in code, comments, commit messages, or any generated text. Use commas, periods, parentheses, or "to" for ranges.
- No secrets in code. The Claude API key and database credentials come from environment or settings, never hardcoded.
- Deploy to AWS only. Not Render, not Railway.

## Continuity hints (avoid empty-chat resets)
- If you are starting a fresh session, read `AGENTS.md` Current State and Roadmap to find where the build is, then read `agent_docs/project_brief.md`. Do not re-derive scope from scratch.
- When you finish a task, update the Current State block in `AGENTS.md` (Working On, Recently Completed, Blocked By) so the next session resumes cleanly.
- The PRD is the source of truth for scope. If something is not in the PRD, confirm before building it.

## Commands
These are the intended commands; create the scripts and Makefile or compose entries that back them during Phase 0.
- `docker compose up` , start FastAPI plus PostgreSQL with pgvector locally.
- `pytest` , run the harness test suite.
- `pytest -m harness` , run only the core evaluation-logic tests (the ones the CI gate protects).
- `python -m clinaiqa.eval.report_metrics` , compute precision and recall on the held-out set.
- `locust -f loadtest/locustfile.py` , run the load test.
- `npm run dev` (in the frontend directory) , start the React dashboard.

## When in doubt
Ask. The biggest risks to this project are silent scope creep (building a generator), a leaked test set (invalid metric), and a deployment that quietly falls back off AWS. Flag any of these the moment you sense them.
