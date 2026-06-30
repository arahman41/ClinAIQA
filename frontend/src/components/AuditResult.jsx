import FlagCard from "./FlagCard.jsx";

function formatTs(iso) {
  if (!iso) return "Unknown";
  const d = new Date(iso);
  return isNaN(d.getTime()) ? "Invalid date" : d.toLocaleString();
}

export default function AuditResult({ audit }) {
  const pass = audit.verdict === "pass";
  const ts = formatTs(audit.created_at);
  const flags = audit.flags ?? [];

  return (
    <div className="audit-result">
      <div className="result-header">
        <span className={`verdict-badge ${pass ? "verdict-pass" : "verdict-fail"}`}>
          {pass ? "PASS" : "FAIL"}
        </span>
        <span className="result-meta">
          #{audit.id} &middot; {audit.doc_type} &middot; {ts}
        </span>
      </div>

      {flags.length === 0 ? (
        <p className="no-flags">No flags raised.</p>
      ) : (
        <div className="flag-list">
          <p className="flag-count">
            {flags.length} flag{flags.length !== 1 ? "s" : ""}
          </p>
          {flags.map((f, i) => (
            <FlagCard key={`${f.flag_type}-${f.phrase}-${i}`} flag={f} />
          ))}
        </div>
      )}
    </div>
  );
}
