# product_requirements.md

A condensed reference for build sessions. The full PRD is `docs/PRD-ClinAIQA-MVP.md`; that is the source of truth. This file is the quick lookup.

## One line
ClinAIQA takes any healthcare-facing LLM output and returns an evidence-backed pass or fail verdict across grounding, hallucination, regulatory phrasing, and explainability.

## Primary user story
As a platform engineer on a small healthcare AI team, I want to verify that LLM-generated patient-facing text is grounded, hallucination-free, and compliant before it ships, so that I do not expose patients or my organization to a fabricated clinical fact or a regulatory violation.

## Supporting user stories
- As a compliance reviewer, I want to see the exact phrase that triggered each flag, so that I can make a release decision quickly.
- As an engineer, I want to re-run the same audit suite after changing my prompt or model, so that I can prove I did not regress on safety.

## Must-have features
1. Layer 1, retrieval-grounded fact checking (pgvector), grounding score per sentence.
2. Layer 2, hallucination and clinical claim detection, rubric-based, with a documented held-out adversarial set and real measured precision and recall. The centerpiece.
3. Layer 3, regulatory and compliance phrase scanning, rule pack plus LLM-assisted, each flag with rule ID and severity.
4. Layer 5, the harness around the harness: Pytest over scoring logic, GitHub Actions deploy gate, Docker, AWS deployment, load test.

## Should-have
- Layer 4, explainability, phrase-level attribution for every flag, SHAP where a learned classifier is used.
- React dashboard, pass rate over time, attribution view, audit record browser.

## Could-have
- Batch submission, configurable rule packs, PDF export of audit record.

## Will-not-have (MVP)
- LLM generation of healthcare text (audit only).
- Auth beyond a simple API key.
- Any real patient data.
- Model fine-tuning.
- Notebooks in the repository.

## Success metrics
- Real measured hallucination precision and recall on the held-out set (the headline).
- 100 percent of sentences receive a grounding score.
- CI gate genuinely blocks merge on core-logic regression.
- One public working AWS URL.
- Load test with real throughput and p95 latency numbers.
- Pytest covers scoring logic, not just API wrappers.

## Hard constraints
- Synthetic data only.
- Leak-free held-out set.
- Real numbers only, never projected.
- AWS deployment, not Render or Railway.
- No notebooks.
- No em dashes.
- No hardcoded secrets.

## Honest related-work framing
OSCC: credibility transfer plus the leak-free methodology transfer, no shared code. FraudSense (shelved): compliance record format as a structural template for Layer 3 only.
