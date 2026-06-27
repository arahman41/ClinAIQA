# synthetic_data_archetypes.md

All ClinAIQA data is synthetic. No real patient data, ever. This file defines the categories of synthetic data to generate in Phase 1. Each adversarial archetype is a known failure mode that a real healthcare LLM output could exhibit, and is what the harness must learn to catch.

## Two top-level buckets

### 1. Healthy examples (the negatives, should pass)
Correct, grounded healthcare outputs paired with their source record. Used to confirm the harness does not over-flag clean output (this is what gives precision its meaning). Each healthy example is:
- A source record (synthetic facility data, a synthetic clinical guideline excerpt, or a synthetic patient record).
- An output text that is fully grounded in that record, names medications and figures correctly, includes required disclaimers, and avoids absolute claims.

### 2. Adversarial examples (the positives, should be flagged)
Outputs that contain one or more injected defects. Each example records which defect was injected and where, so precision and recall can be computed against ground truth.

## Adversarial archetypes

**A. Fabricated clinical fact.**
A claim with no support in the source record (a diagnosis, a procedure, a vital sign that was never recorded). Targets Layer 1 grounding and Layer 2 hallucination detection.

**B. Wrong medication name.**
A drug name that does not match the source record, including look-alike or sound-alike substitutions (for example a real drug swapped for a similarly spelled one). Targets Layer 2 exact-match property checking.

**C. Fabricated statistic.**
A specific number (a success rate, a survival percentage, a count) that is not in the source or is contradicted by it. Targets Layer 1 and Layer 2.

**D. Specific diagnosis without disclaimer.**
A definitive diagnostic statement where policy requires a disclaimer ("consult your physician," "this is not a diagnosis"). Targets Layer 3 compliance.

**E. Missing required disclaimer.**
Output that omits a disclaimer the rule pack requires for its content type. Targets Layer 3.

**F. Disallowed absolute claim.**
Language asserting certainty that is not clinically appropriate, for example "this will cure," "guaranteed," "no side effects." Targets Layer 3.

**G. HIPAA-adjacent phrasing issue.**
Phrasing that exposes or implies identifiable information inappropriately, or otherwise creates regulatory exposure. Targets Layer 3. Keep these synthetic and clearly artificial.

**H. Subtle drift (hard negative).**
Output that is mostly grounded but contains one small unsupported embellishment. These are the hardest to catch and the most interview-credible when the harness catches them. Include a meaningful share of these so recall is honestly tested, not inflated by only easy cases.

## Generation guidance
- Generate healthy examples first, then derive adversarial ones by injecting a single, recorded defect into a copy of a healthy example where possible, so the only difference is the defect. This makes ground truth unambiguous.
- Record, per adversarial example: archetype, the exact span of the injected defect, and the expected flag type. This span is the ground truth for the Layer 4 attribution check too.
- Vary content types (facility report, patient summary, medication instruction) so the rule packs are exercised across contexts.
- Generation can use the Claude API, but every generated example must be reviewed or validated against its recorded defect so the ground truth is trustworthy. A wrong ground-truth label silently corrupts the precision and recall metric.

## Split assignment
After generation, assign every adversarial example to either the rubric-tuning set or the held-out reporting set, once, with a fixed recorded seed. See `testing.md` for the leak-free discipline. The split is sacred: held-out examples never inform tuning.
