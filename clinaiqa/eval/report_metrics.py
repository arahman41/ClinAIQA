"""
Compute and print precision and recall on the held-out adversarial test set.

Run: python -m clinaiqa.eval.report_metrics

This script makes live Claude API calls and queries the production database.
It is NOT a Pytest test; it is the final measurement step. Run it exactly once,
manually, at the end of the build to get the headline number.

The held-out set is loaded here and ONLY here. Do not import
load_heldout_from_db_for_final_report from any other module (a Pytest leak guard
enforces this).
"""
from __future__ import annotations

import json
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clinaiqa.data.schemas import DocType
from clinaiqa.eval.db_loader import (
    load_healthy_from_db,
    load_heldout_from_db_for_final_report,
)
from clinaiqa.eval.metrics import compute_metrics
from clinaiqa.eval.runner import EvalResult, EvalRunner
from clinaiqa.settings import settings


def _evaluate_one(
    runner: EvalRunner,
    output_text: str,
    source_record: str,
    doc_type: DocType,
    label: str,
) -> EvalResult:
    """Evaluate one example, counting any failure as flagged (fail toward flagging)."""
    try:
        return runner.evaluate(output_text, source_record, doc_type=doc_type)
    except Exception as exc:
        print(f"  [WARN] {label} scoring failed: {exc}. Counting as flagged.")
        return EvalResult(output_text=output_text, flagged=True)


def main() -> None:
    url = settings.database_url_sync
    if not url:
        print("ERROR: DATABASE_URL_SYNC is not set.", file=sys.stderr)
        sys.exit(1)

    engine = create_engine(url)

    # One session kept open for the whole run so lazy relationships (the parent
    # healthy_example and its source_record) resolve while we iterate.
    with Session(engine) as session:
        print("ClinAIQA: loading held-out adversarial examples from database...")
        heldout = load_heldout_from_db_for_final_report(session)
        healthy = load_healthy_from_db(session)

        print(f"  Held-out adversarial examples: {len(heldout)}")
        print(f"  Healthy (negative) examples  : {len(healthy)}")

        if not heldout and not healthy:
            print("ERROR: No examples found. Run 'make seed' first.")
            sys.exit(1)

        runner = EvalRunner()
        results: list[EvalResult] = []
        ground_truths: list[bool] = []

        print("Running evaluation on adversarial examples (live Claude API calls)...")
        for i, ex in enumerate(heldout, 1):
            source_record = json.dumps(ex.healthy_example.source_record)
            doc_type = DocType(ex.healthy_example.doc_type)
            results.append(
                _evaluate_one(
                    runner, ex.output_text, source_record, doc_type, f"adversarial example {ex.id}"
                )
            )
            ground_truths.append(True)
            if i % 5 == 0:
                print(f"  Processed {i}/{len(heldout)} adversarial examples")

        print("Running evaluation on healthy examples...")
        for i, ex in enumerate(healthy, 1):
            source_record = json.dumps(ex.source_record)
            doc_type = DocType(ex.doc_type)
            results.append(
                _evaluate_one(
                    runner, ex.output_text, source_record, doc_type, f"healthy example {ex.id}"
                )
            )
            ground_truths.append(False)
            if i % 5 == 0:
                print(f"  Processed {i}/{len(healthy)} healthy examples")

    report = compute_metrics(results, ground_truths)
    print("\n" + "=" * 50)
    print(report)
    print(
        f"Headline: ClinAIQA catches {report.recall * 100:.1f} percent of injected hallucinations "
        f"in a held-out adversarial set of {len(heldout)} outputs "
        f"(precision {report.precision * 100:.1f} percent, N={report.n_total})."
    )


if __name__ == "__main__":
    main()
