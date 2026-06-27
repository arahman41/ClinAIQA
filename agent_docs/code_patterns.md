# code_patterns.md

## Project structure (target)
```
clinaiqa/
├── docs/
│   └── PRD-ClinAIQA-MVP.md
├── agent_docs/
├── AGENTS.md
├── CLAUDE.md
├── clinaiqa/                  # Python package, the harness
│   ├── api/                   # FastAPI routers and schemas
│   ├── retrieval/             # Layer 1, chunking, embedding, pgvector search, grounding score
│   ├── eval/                  # Layer 2, rubric, Claude scoring, metrics; report_metrics entrypoint
│   ├── compliance/            # Layer 3, rule packs, phrase scanning
│   ├── explain/               # Layer 4, attribution and SHAP
│   ├── llm/                   # Claude API client, retry, structured-output parsing
│   ├── data/                  # synthetic data generation and the seeded split
│   ├── db/                    # SQLAlchemy models, Alembic migrations
│   └── settings.py            # Pydantic settings, reads env, no hardcoded secrets
├── tests/                     # Pytest, mirrors the package; harness-marked tests for the CI gate
├── frontend/                  # React dashboard
├── loadtest/                  # Locust or JMeter scripts
├── docker-compose.yml
├── Dockerfile
├── .github/workflows/ci.yml
├── .env.example
└── README.md
```
No notebooks anywhere in this tree, at any phase.

## Naming
- Python: `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_SNAKE` for constants.
- Make the held-out loader name unmistakable, for example `load_heldout_for_final_report()`, so misuse is visible in review.
- Test files mirror the module path: `clinaiqa/eval/metrics.py` is tested by `tests/eval/test_metrics.py`.

## Error handling
- LLM calls go through one client in `clinaiqa/llm/`. Centralize retry with backoff, timeout, and structured-output parsing there. Never scatter raw API calls across modules.
- Parse Claude responses defensively. If the model is asked for JSON, strip any code fences and parse safely; on parse failure, raise a typed error, do not silently return a wrong score.
- A scoring failure must never default to a silent pass. If the harness cannot score a claim, that claim is flagged for human review, not waved through. Failing safe means failing toward flagging.

## Config and secrets
- All config through `clinaiqa/settings.py` (Pydantic settings reading environment variables).
- The Claude API key and the database URL come from the environment. `.env` is local only and gitignored. `.env.example` lists every variable with a placeholder.
- Never log secrets. Never put secrets, patient-like data, or full source records into URLs or query strings.

## Determinism
- Anything that affects the reported metric (the data split, any sampling) uses a fixed, recorded seed.
- Unit tests of scoring logic mock the LLM so they are deterministic.

## Commit and PR conventions
- No em dashes in commit messages or comments.
- Commit messages describe what changed and what was verified.
- A PR description states what was run to verify the change (for example "pytest -m harness green, 0 failures").

## Frontend
- React function components and hooks. Keep the dashboard's verdict the most prominent element. Flags are expandable to reveal the triggering phrase and the supporting or contradicting passage. Follow the interface-design skill for the audit-tool look.
