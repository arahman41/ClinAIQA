# testing.md

Testing is not a side concern in ClinAIQA; the product is a testing harness, so the test strategy is part of the product story. There are two distinct test layers, and they must not be confused.

## Layer A: tests of ClinAIQA's own code (Pytest)
Standard software tests that prove the harness logic works.
- **Scope:** the scoring logic itself, not just the LLM API wrappers. Chunking, claim extraction, grounding-score computation, rule-pack matching, severity assignment, audit-record assembly, the precision and recall computation.
- **Mock the LLM where the test is about logic.** Tests of scoring math, parsing, and aggregation use recorded or stubbed Claude responses so they are deterministic, fast, and free. Do not call the live API in unit tests.
- **Marker:** tag core evaluation-logic tests with `@pytest.mark.harness`. These are the tests the CI gate protects. A regression here blocks merge.
- **Run:** `pytest` for all, `pytest -m harness` for the gate set.

## Layer B: the harness's own evaluation against the adversarial set
This is the product metric, not a software test. It measures how well ClinAIQA catches bad healthcare output.

### The leak-free discipline (the single most important rule in this project)
The synthetic adversarial examples are split once, with a fixed seed, into two sets that never mix:
1. **Rubric-tuning set.** Used to design, tune, and iterate the detection rubric and rule packs. Look at these as much as needed.
2. **Held-out reporting set.** Used exactly once at the end to measure and report precision and recall. Never inspected during rubric design. Never used to choose thresholds. Never used to pick examples for prompts.

If a held-out example influences any tuning decision, the held-out metric is no longer valid and the number is worthless. This is the same leak-free cross-validation discipline the author applied in the OSCC survival analysis work. State it that way in the README.

Enforcement ideas to build in Phase 2:
- Store the split assignment in the database or a versioned file with the seed recorded.
- Load the held-out set only through a function named to make its purpose obvious, for example `load_heldout_for_final_report()`, and do not call it anywhere in tuning code.
- Add a Pytest check that fails if tuning modules import the held-out loader.

### Metrics computed
- **Precision:** of the outputs ClinAIQA flagged as hallucinated, what fraction were truly bad.
- **Recall:** of the truly bad outputs in the held-out set, what fraction ClinAIQA caught.
- Report both, with the held-out set size N. Headline framing: "catches X percent of injected hallucinations in a held-out adversarial set of N outputs."
- Compute via `python -m clinaiqa.eval.report_metrics`, run once, at the end, on the held-out set.

## Verification loop (every change)
1. Make the change.
2. Run `pytest -m harness`. If red, fix before moving on.
3. Run the broader `pytest` if the change touched anything beyond core logic.
4. Only then claim the task done, citing the command output. Follow the verification-before-completion discipline: evidence before assertions.

## CI gate
- GitHub Actions runs `pytest -m harness` on every push.
- Merge is blocked on failure. This is a real gate, not a passive status check.
- Confirm the gate works by pushing a deliberately broken commit once and watching it block, then reverting.

## What not to test against the live LLM
- Do not run the full adversarial set against the live Claude API inside CI on every push; that is slow and costly. The held-out metric run is a deliberate, manual, end-of-build step. CI protects the deterministic logic, not the paid API.
