# project_brief.md

## Vision
ClinAIQA proves a specific, scarce skill: building evaluation and compliance tooling for healthcare-facing LLM output. The market gap it targets (AI governance and compliance) is flagged as a 52 percent talent shortage area for 2026, and almost no entry-level portfolio project addresses it. The deliverable that matters most is a working eval harness with a real, honestly measured precision and recall against a documented adversarial test set. Everything else supports that one credible artifact.

## Origin story (use in README and interviews)
ClinAIQA is the tool that should have been checking the author's own MedElite facility report generator, a FastAPI service that turned structured CMS data into narrative PDF and Word reports. That firsthand experience of shipping a healthcare text generator with no safety net is the honest reason this project exists.

## Non-negotiable rules
1. **Audit, never author.** ClinAIQA evaluates healthcare LLM output. It does not generate healthcare text. If a task drifts toward generation, stop and flag it.
2. **Synthetic data only.** No real patient data at any point.
3. **Leak-free test set.** The held-out adversarial set never touches rubric tuning. This is the single discipline that makes the headline metric valid. It is the same leak-free discipline used in the author's OSCC survival analysis work.
4. **Real numbers only.** Precision and recall are measured on the held-out set and reported as measured. Never projected, never aspirational.
5. **AWS deployment.** One public working AWS URL is mandatory. Not Render, not Railway.
6. **Production-equivalent.** No notebooks in the repository. This must read as a real system.
7. **No em dashes.** Anywhere. Code, comments, commit messages, docs.
8. **No secrets in code.** Keys and credentials come from environment or settings.

## Quality gates
- A change to core evaluation logic does not merge unless `pytest -m harness` passes in CI.
- A claim of "done" or "passing" is backed by command output, not assertion.
- Every PR description states what was verified and how.

## Honest framing of related work
- **OSCC pipeline:** credibility transfer (rigorous clinical-data work) plus one real methodology transfer (leak-free evaluation). No shared code. Do not invent a deeper integration.
- **FraudSense (shelved):** the compliance record format is a structural template for Layer 3. Reference it for shape, do not resurrect the project.

## Key commands
See `CLAUDE.md` Commands. Back them with real scripts during Phase 0.

## Candidate-facing reminder
Resume bullets are drafted at the end of the build from the actual measured numbers (Phase 7), never before. The point of this project is that the numbers are honest.
