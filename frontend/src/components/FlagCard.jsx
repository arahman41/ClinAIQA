import { useState } from "react";

const SEVERITY_CLASS = {
  critical: "severity-critical",
  high: "severity-high",
  medium: "severity-medium",
  low: "severity-low",
};

const SOURCE_LABEL = {
  layer1: "Layer 1 - Grounding",
  layer2: "Layer 2 - Hallucination",
  layer3: "Layer 3 - Compliance",
  layer4: "Layer 4 - Explainability",
};

export default function FlagCard({ flag }) {
  const [open, setOpen] = useState(false);
  const sev = flag.severity ?? "info";
  const severityClass = SEVERITY_CLASS[sev] ?? "severity-low";
  const sourceLabel = SOURCE_LABEL[flag.source] ?? flag.source;

  return (
    <div className="flag-card">
      <button className="flag-header" onClick={() => setOpen((o) => !o)}>
        <span className="flag-toggle">{open ? "▼" : "▶"}</span>
        <span className={`severity-badge ${severityClass}`}>
          {sev}
        </span>
        <span className="flag-type">{flag.flag_type}</span>
        {flag.rule_id && <span className="rule-id">{flag.rule_id}</span>}
        <span className="flag-source">{sourceLabel}</span>
      </button>

      {open && (
        <div className="flag-body">
          <div className="flag-phrase-row">
            <span className="label">Triggering phrase</span>
            <blockquote className="flag-phrase">{flag.phrase}</blockquote>
          </div>

          {flag.reasoning && (
            <div className="flag-detail-row">
              <span className="label">Reasoning</span>
              <p className="flag-reasoning">{flag.reasoning}</p>
            </div>
          )}

          {flag.reference_passage && (
            <div className="flag-detail-row">
              <span className="label">Reference passage</span>
              <blockquote className="flag-reference">
                {flag.reference_passage}
              </blockquote>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
