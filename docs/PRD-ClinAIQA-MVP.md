# PRD, ClinAIQA MVP

**Document owner:** Ateeq Ur Rahman
**Status:** Draft for build kickoff
**Last updated:** June 27, 2026
**Target build window:** 8 to 10 weeks

---

## 1. Product overview

**Name:** ClinAIQA (Clinical AI Quality Assurance)

**One line:** ClinAIQA is a pre-deployment audit harness that takes any healthcare-facing LLM output and returns an evidence-backed pass or fail verdict, covering grounding, hallucination, regulatory phrasing, and explainability.

**What it is not:** It is not a chatbot, not a document generator, and not another RAG demo. It is the testing and compliance layer that sits in front of those systems and answers one question with measured evidence: is this output safe to ship.

**Primary goal:** Produce one publicly deployed, Dockerized, AWS-hosted system with a real, honestly measured precision and recall figure against a documented held-out adversarial test set, finishable inside the build window, that reads as a production-equivalent system rather than a notebook demo.

**Secondary goal:** Close all seven named resume skill gaps (CI/CD as a deploy gate, Docker, LLM evaluation harness design, vector retrieval, AWS deployment, SHAP explainability, LLM-aware load testing) inside one coherent project.

---

## 2. Target users

**Primary persona, the platform engineer at a small healthcare AI team.**
Builds or maintains a system that turns structured clinical or facility data into narrative text (discharge summaries, patient communications, facility or compliance reports). Ships fast, has no dedicated QA function, and has no in-house tooling to systematically catch hallucinations, ungrounded claims, or risky regulatory phrasing before output reaches a patient or a regulator. Needs a verdict plus an audit trail, not a vague score.

**Secondary persona, the compliance or clinical reviewer.**
Not an engineer. Receives the audit record and needs to understand why a given output was flagged, which specific phrase triggered it, and whether it is safe to release. Reads the explainability output, not the code.

**Jobs to be done:**
- When I generate patient-facing text from an LLM, I want to verify it is grounded in the source record, so that I do not ship a fabricated clinical fact.
- When I review flagged output, I want to see the exact phrase that triggered the flag, so that I can make a release decision quickly.
- When I change my generation prompt or model, I want to re-run the same audit suite, so that I can prove the new version did not regress on safety.

---

## 3. Problem statement

Healthcare organizations are deploying LLMs to generate patient-facing communications, clinical summaries, and structured facility and compliance reports. These outputs carry real liability when they hallucinate clinical facts, drift from source data, omit required disclaimers, or use language that creates regulatory exposure (absolute claims such as "this will cure," HIPAA-adjacent phrasing, missing disclaimers). Most teams building these systems have no in-house tooling to catch these failures before deployment.

ClinAIQA is the tool that should have been checking the author's own MedElite facility report generator output. It takes any healthcare-facing LLM text and runs it through automated grounding checks, hallucination detection, regulatory phrase scanning, and explainability, then returns a pass or fail audit record with attribution.

---

## 4. User journey

1. A platform engineer pastes or POSTs a piece of LLM-generated healthcare text plus its source record into ClinAIQA.
2. ClinAIQA chunks the output into claims, retrieves supporting passages from the reference corpus stored in pgvector, and scores grounding per sentence.
3. The hallucination harness scores each claim against the rubric and flags fabricated facts, wrong drug names, and unsupported statistics.
4. The compliance scanner flags missing disclaimers and disallowed absolute claims.
5. The explainability layer attaches, for each flag, the specific input phrase that drove it.
6. ClinAIQA returns a structured audit record with an overall pass or fail verdict and a per-check breakdown.
7. A compliance reviewer opens the dashboard, reads the flagged phrases and attribution, and makes a release decision.
8. When the engineer changes the upstream prompt or model, they re-run the same suite and compare pass rate over time.

---

## 5. The five layers (MVP feature set, MoSCoW)

### Must have

**Layer 1, Retrieval-grounded fact checking.**
Reference documents (CMS facility data, clinical guideline excerpts, synthetic patient records) are embedded and stored in PostgreSQL with pgvector. Submitted output is chunked into claims; each claim is matched against retrieved reference passages. Output: a grounding score per sentence, with any claim lacking a supporting match flagged as ungrounded.
- Success criteria: every sentence in a submitted output receives a grounding score and a supporting passage reference or an ungrounded flag.

**Layer 2, Hallucination and clinical claim detection (the centerpiece).**
A structured evaluation suite built on input and expected-property pairs, not subjective grading without ground truth. Examples of properties: a summary must not state a specific diagnosis without a disclaimer; medication names must match the source record exactly. The Claude API scores each output against the rubric. A held-out set of known-bad synthetic examples (injected hallucinations, wrong drug names, fabricated statistics) is built, and the harness precision and recall at catching them is measured and reported.
- Success criteria: a documented held-out adversarial set exists, and the harness reports a real measured precision and recall on it. This is the single most interview-credible artifact in the project.

**Layer 3, Regulatory and compliance phrase scanning.**
Rule-based plus LLM-assisted scanning for HIPAA-relevant phrasing, missing required disclaimers, and disallowed absolute claims. Structurally echoes the BSA and FinCEN style compliance record from the shelved FraudSense scope, applied here to healthcare language.
- Success criteria: a defined ruleset produces a list of compliance flags with severity and rule ID per output.

**Layer 5 (build dependency, treated as must have for credibility), the harness around the harness.**
A Pytest suite covering the scoring logic itself, wired into a GitHub Actions workflow that runs on every push and blocks merge on regression of core evaluation logic. The full stack (FastAPI, PostgreSQL, pgvector) is Dockerized. Deployed on AWS. A load test measures throughput and latency under concurrent evaluation requests, written up as a short results page.
- Success criteria: green CI gate that genuinely blocks merge on test failure; one public AWS URL; one load test results writeup with real numbers.

### Should have

**Layer 4, Explainability.**
SHAP values or comparable attribution showing which input tokens or phrases drove each flag, so the audit output is usable by a human reviewer. Marked should have because the rule-based and retrieval flags already carry natural phrase-level attribution; SHAP adds depth and closes the named explainability skill gap, but the project still demonstrates attribution without it if the timeline compresses.
- Success criteria: each flag links to the specific driving phrase; where a learned classifier is used, SHAP attributions are surfaced.

**React dashboard.**
Pass rate over time, attribution visualization, audit record browser.

### Could have
- Batch submission (audit a folder of outputs in one run).
- Configurable rule packs (swap the healthcare ruleset for a different domain).
- Exportable audit record as PDF (reuses the author's existing ReportLab experience).

### Will not have (explicitly out of scope for MVP)
- No LLM generation of the healthcare text itself; ClinAIQA only audits, it does not author.
- No authentication beyond a simple API key gate; this is a demo, not a multi-tenant SaaS.
- No real patient data of any kind; synthetic only, always.
- No fine-tuning of any model.
- No notebooks in the final repository.

---

## 6. Success metrics

| Metric | Target | Notes |
|---|---|---|
| Hallucination detection precision (held-out set) | Report real measured value | Honest number only, never projected |
| Hallucination detection recall (held-out set) | Report real measured value | The headline resume artifact |
| Grounding coverage | 100% of sentences scored | Every sentence gets a score or ungrounded flag |
| CI gate | Blocks merge on core logic regression | Must be a real gate, not a passive status check |
| Public deployment | One working AWS URL | Mandatory |
| Load test | Throughput and p95 latency under concurrency | Real measured numbers, short writeup |
| Pytest coverage of scoring logic | Scoring logic covered, not just API wrappers | Tests the harness, not the LLM |

Resume framing example, to be filled from real numbers at the end, never before: "Built an LLM evaluation harness that catches X percent of injected hallucinations in a held-out adversarial test set of N healthcare outputs."

---

## 7. Relationship to the OSCC Survival Prediction Pipeline

This is a credibility relationship, not a code relationship. The PRD states it explicitly so that future build sessions do not invent a deeper integration that does not exist.

OSCC is Cox proportional hazards survival modeling on TCGA RNA-seq data. ClinAIQA is LLM text evaluation. These are structurally different ML paradigms with no shared code or architecture. A sharp interviewer would spot a forced connection and it would weaken credibility.

Two things carry over honestly and should appear in the README and interview narrative:

1. **Credibility transfer.** OSCC already demonstrates the author can work rigorously with high-stakes clinical data (leak-free cross-validation, defensible AUC reporting, real TCGA data). That is genuine prior evidence of clinical-data competence.
2. **Methodological reuse.** The leak-free cross-validation discipline from OSCC applies directly to ClinAIQA's held-out adversarial test set. Synthetic hallucination examples must not leak between the set used to build and tune the detection rubric and the set used to report final precision and recall, or the reported metric is invalid. Stated plainly: the same leak-free evaluation discipline from the survival analysis work keeps the adversarial test set honest.

---

## 8. Design direction

Clean, clinical, evidence-first. The dashboard should read like an audit tool, not a consumer app. Verdict (pass or fail) is the most prominent element. Each flag is expandable to show the triggering phrase and the supporting or contradicting reference passage. Pass-rate-over-time is a single line chart. No decorative animation. Default stack is React, chosen over a CLI-first or GitHub-Action-package approach for build speed inside the MVP timeline.

---

## 9. Technical considerations

See `agent_docs/tech_stack.md` for the full stack. Summary:

- Backend: Python, FastAPI.
- Database and vector store: PostgreSQL with pgvector (one product, extends existing PostgreSQL fluency, no new database introduced).
- LLM: Claude API for rubric scoring and compliance reasoning.
- Explainability: SHAP or comparable.
- Frontend: React.
- Testing: Pytest over the harness internal logic.
- CI/CD: GitHub Actions as a deploy-blocking gate.
- Containerization: Docker for the full stack.
- Deployment: AWS. See decision below.
- Load testing: Locust or JMeter.

**AWS deployment decision (resolving the open question from the handover).**
Recommended target: **ECS on Fargate** for the Dockerized FastAPI service, fronted by an Application Load Balancer, with **RDS for PostgreSQL 15 or higher** running the pgvector extension. Rationale: ECS Fargate gives the most credible "deployed a containerized service on AWS" signal, demonstrates container orchestration, and avoids managing EC2 hosts. RDS PostgreSQL supports pgvector, so the vector store and relational store stay unified.

Fallback if the timeline compresses in Week 9: **AWS App Runner** pointed at the same container image, still paired with RDS PostgreSQL. App Runner is faster to stand up and still counts as a real AWS container deployment. Decision gate is set for the start of Week 9; pick ECS if Docker and CI are stable by then, App Runner if not. Either way, RDS PostgreSQL with pgvector is the database. Cost should be watched: use the smallest viable Fargate task and a db.t-class RDS instance, and tear down or stop when not demoing.

---

## 10. Constraints

- Timeline: 8 to 10 weeks, planning scaffold not a fixed commitment. Week-by-week deliverables in the AGENTS.md roadmap.
- Solo developer.
- Budget: minimize AWS spend; smallest viable instances; stop resources when idle.
- No real patient data ever; synthetic only.
- No em dashes anywhere in documents, code comments, or commit messages.
- No notebooks in the final repository.
- The held-out adversarial test set must never leak into rubric tuning.
- Final precision and recall must be real measured numbers from the held-out set, never projected.
- One public working AWS URL is mandatory.
- AWS is a deliberate goal; Render and Railway are excluded since they were used on prior projects.

---

## 11. Definition of done

- [ ] Five layers implemented at the MoSCoW level defined in Section 5 (Layer 4 should-have may compress to phrase-level attribution if timeline forces it).
- [ ] Documented held-out adversarial test set, built leak-free.
- [ ] Real measured precision and recall reported in the README.
- [ ] Pytest suite covers the scoring logic, not just API wrappers.
- [ ] GitHub Actions gate genuinely blocks merge on core logic regression.
- [ ] Full stack Dockerized and running identically locally and deployed.
- [ ] One public AWS URL live.
- [ ] Load test executed with a short results writeup (throughput, p95 latency).
- [ ] README frames the MedElite origin story and the OSCC credibility and methodology transfer honestly.
- [ ] No notebooks in the repository.
- [ ] No em dashes anywhere.
- [ ] Resume bullets drafted from actual measured numbers.
