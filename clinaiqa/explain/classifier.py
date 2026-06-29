"""
Layer 4 SHAP-backed flag classifier.

A small interpretable classifier over per-layer feature scores (grounding
similarity, Layer 2 confidences, Layer 3 compliance hits). It predicts whether
an output should be flagged and, via SHAP, attributes that prediction to the
individual layer features. This closes the named SHAP explainability gap without
authoring any healthcare text. The model is trained on the tuning split only
(see train_classifier.py); the held-out set never informs it.

scikit-learn is required for the model. shap is an optional import, so the
harness suite runs where shap is not installed; the SHAP explanation raises a
clear error only if invoked without it.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

try:
    import shap
except ModuleNotFoundError:  # optional; explanation is gated on it being present
    shap = None  # type: ignore[assignment]

from clinaiqa.eval.runner import EvalResult

FEATURE_NAMES: list[str] = [
    "min_grounding_similarity",
    "ungrounded_sentence_count",
    "max_layer2_confidence",
    "layer2_violation_count",
    "layer3_flag_count",
    "layer3_max_severity",
]

_SEVERITY_SCORE = {"low": 1.0, "medium": 2.0, "high": 3.0}


@dataclass
class FeatureContribution:
    feature_name: str
    value: float
    shap_value: float


def extract_features(eval_result: EvalResult) -> list[float]:
    """Reduce an EvalResult to the fixed-order feature vector in FEATURE_NAMES."""
    report = eval_result.grounding_report
    sentences = report.sentences if report is not None else []

    similarities = [s.cosine_similarity for s in sentences] or [1.0]
    min_similarity = min(similarities)
    ungrounded_count = sum(1 for s in sentences if not s.grounded)

    confidences = [v.confidence for v in eval_result.property_verdicts] or [0.0]
    max_layer2_confidence = max(confidences)
    layer2_violations = sum(1 for v in eval_result.property_verdicts if v.violated)

    layer3_flags = [f for f in eval_result.flags if f.source == "layer3"]
    layer3_count = len(layer3_flags)
    layer3_max_severity = max(
        (_SEVERITY_SCORE.get(f.severity or "", 0.0) for f in layer3_flags),
        default=0.0,
    )

    return [
        float(min_similarity),
        float(ungrounded_count),
        float(max_layer2_confidence),
        float(layer2_violations),
        float(layer3_count),
        float(layer3_max_severity),
    ]


class FlagClassifier:
    """Logistic-regression flag predictor with SHAP attribution."""

    def __init__(self) -> None:
        self._model: LogisticRegression | None = None
        self._background: np.ndarray | None = None

    def fit(self, X: list[list[float]], y: list[int]) -> "FlagClassifier":
        features = np.asarray(X, dtype=float)
        self._model = LogisticRegression(max_iter=1000).fit(features, y)
        self._background = features
        return self

    def predict_proba(self, X: list[list[float]]) -> list[float]:
        if self._model is None:
            raise RuntimeError("FlagClassifier is not fitted. Call fit() first.")
        proba = self._model.predict_proba(np.asarray(X, dtype=float))
        return [float(p) for p in proba[:, 1]]

    def save(self, path: str | Path) -> None:
        """Persist coefficients and a background sample as JSON (diff-friendly)."""
        if self._model is None or self._background is None:
            raise RuntimeError("FlagClassifier is not fitted. Call fit() first.")
        payload = {
            "feature_names": FEATURE_NAMES,
            "coef": self._model.coef_.tolist(),
            "intercept": self._model.intercept_.tolist(),
            "classes": self._model.classes_.tolist(),
            "background": self._background.tolist(),
        }
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "FlagClassifier":
        """Reconstruct a fitted classifier from a saved JSON file."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        model = LogisticRegression()
        model.coef_ = np.asarray(data["coef"], dtype=float)
        model.intercept_ = np.asarray(data["intercept"], dtype=float)
        model.classes_ = np.asarray(data["classes"])
        model.n_features_in_ = len(data["feature_names"])
        clf = cls()
        clf._model = model
        clf._background = np.asarray(data["background"], dtype=float)
        return clf

    def explain(self, features: list[float]) -> list[FeatureContribution]:
        """Return per-feature SHAP contributions for a single instance."""
        if self._model is None or self._background is None:
            raise RuntimeError("FlagClassifier is not fitted. Call fit() first.")
        if shap is None:
            raise RuntimeError(
                "The 'shap' package is not installed. Run 'pip install -r requirements.txt'."
            )

        explainer = shap.LinearExplainer(self._model, self._background)
        instance = np.asarray([features], dtype=float)
        shap_values = np.asarray(explainer.shap_values(instance)).reshape(-1)

        return [
            FeatureContribution(
                feature_name=name,
                value=float(features[i]),
                shap_value=float(shap_values[i]),
            )
            for i, name in enumerate(FEATURE_NAMES)
        ]
