import { useRef, useState } from "react";
import { submitAudit } from "../api.js";
import AuditResult from "./AuditResult.jsx";

const AUDIT_TIMEOUT_MS = 120_000;

const DOC_TYPES = [
  { value: "patient_record", label: "Patient Record" },
  { value: "clinical_guideline", label: "Clinical Guideline" },
  { value: "cms_facility", label: "CMS Facility" },
];

const PLACEHOLDER_OUTPUT = `Patient John Doe, 45, presents with uncontrolled hypertension. Current medication: Lisinopril 10mg daily. Blood pressure today: 160/95 mmHg. This will completely cure your condition with continued use. Note: This is not medical advice.`;

const PLACEHOLDER_SOURCE = JSON.stringify(
  {
    patient_id: "P-001",
    name: "John Doe",
    age: 45,
    diagnosis: "hypertension",
    medications: [{ name: "Lisinopril", dose: "10mg", frequency: "daily" }],
  },
  null,
  2
);

export default function AuditForm() {
  const [outputText, setOutputText] = useState("");
  const [sourceRecord, setSourceRecord] = useState("");
  const [docType, setDocType] = useState("patient_record");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const abortRef = useRef(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setResult(null);

    let parsed;
    try {
      parsed = JSON.parse(sourceRecord);
    } catch {
      setError("Source record must be valid JSON.");
      return;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), AUDIT_TIMEOUT_MS);
    abortRef.current = controller;

    setLoading(true);
    try {
      const audit = await submitAudit(
        { output_text: outputText, source_record: parsed, doc_type: docType },
        controller.signal,
      );
      setResult(audit);
    } catch (err) {
      if (err.name === "AbortError") {
        setError("Audit timed out. The request took longer than 2 minutes.");
      } else {
        setError(err.message);
      }
    } finally {
      clearTimeout(timeoutId);
      abortRef.current = null;
      setLoading(false);
    }
  }

  function loadExample() {
    abortRef.current?.abort();
    setOutputText(PLACEHOLDER_OUTPUT);
    setSourceRecord(PLACEHOLDER_SOURCE);
    setDocType("patient_record");
    setResult(null);
    setError(null);
    setLoading(false);
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="audit-form">
        <div className="form-group">
          <label htmlFor="doc-type">Document type</label>
          <select
            id="doc-type"
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
          >
            {DOC_TYPES.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="output-text">LLM output text</label>
          <textarea
            id="output-text"
            rows={8}
            value={outputText}
            onChange={(e) => setOutputText(e.target.value)}
            placeholder="Paste the LLM-generated healthcare text to audit..."
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="source-record">Source record (JSON)</label>
          <textarea
            id="source-record"
            rows={8}
            value={sourceRecord}
            onChange={(e) => setSourceRecord(e.target.value)}
            placeholder='{"patient_id": "...", ...}'
            required
          />
        </div>

        {error && <p className="form-error">{error}</p>}

        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={loadExample}>
            Load example
          </button>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Running audit..." : "Run audit"}
          </button>
        </div>
      </form>

      {result && <AuditResult audit={result} />}
    </div>
  );
}
