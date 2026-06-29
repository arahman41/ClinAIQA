"""
Train the Layer 4 flag classifier on the TUNING split only (leak-free).

Run: python -m clinaiqa.explain.train_classifier

This makes live Claude API calls and queries the database, so it is a manual
step (like report_metrics), not a Pytest test. It loads the tuning adversarial
examples and the healthy examples, runs the full harness to extract per-layer
features, fits the classifier, and persists coefficients to
flag_classifier.json for the API to load.

The held-out split is NEVER loaded here. A Pytest leak guard enforces that this
module does not import the held-out loader.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clinaiqa.data.schemas import DocType
from clinaiqa.eval.db_loader import load_healthy_from_db, load_tuning_from_db
from clinaiqa.eval.runner import EvalRunner
from clinaiqa.explain.classifier import FlagClassifier, extract_features
from clinaiqa.settings import settings

MODEL_PATH = Path(__file__).parent / "flag_classifier.json"


def main() -> None:
    url = settings.database_url_sync
    if not url:
        print("ERROR: DATABASE_URL_SYNC is not set.", file=sys.stderr)
        sys.exit(1)

    engine = create_engine(url)
    runner = EvalRunner()
    features: list[list[float]] = []
    labels: list[int] = []

    with Session(engine) as session:
        tuning = load_tuning_from_db(session)
        healthy = load_healthy_from_db(session)
        print(f"Training set: {len(tuning)} tuning adversarial, {len(healthy)} healthy.")

        print("Extracting features from adversarial (positive) examples...")
        for ex in tuning:
            source_record = json.dumps(ex.healthy_example.source_record)
            doc_type = DocType(ex.healthy_example.doc_type)
            try:
                result = runner.evaluate(ex.output_text, source_record, doc_type=doc_type)
            except Exception as exc:  # a failed eval should not abort training
                print(f"  [WARN] tuning example {ex.id} eval failed: {exc}. Skipping.")
                continue
            features.append(extract_features(result))
            labels.append(1)

        print("Extracting features from healthy (negative) examples...")
        for ex in healthy:
            source_record = json.dumps(ex.source_record)
            doc_type = DocType(ex.doc_type)
            try:
                result = runner.evaluate(ex.output_text, source_record, doc_type=doc_type)
            except Exception as exc:
                print(f"  [WARN] healthy example {ex.id} eval failed: {exc}. Skipping.")
                continue
            features.append(extract_features(result))
            labels.append(0)

    if len(set(labels)) < 2:
        print("ERROR: need both positive and negative examples to train.", file=sys.stderr)
        sys.exit(1)

    classifier = FlagClassifier().fit(features, labels)
    classifier.save(MODEL_PATH)
    print(f"Trained on {len(labels)} examples. Saved classifier to {MODEL_PATH}.")


if __name__ == "__main__":
    main()
