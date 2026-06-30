import { useEffect, useRef, useState } from "react";
import { fetchAudit, fetchPassRate } from "../api.js";
import AuditResult from "./AuditResult.jsx";

export default function AuditBrowser() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState(null);
  const [selected, setSelected] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState(null);
  const latestIdRef = useRef(null);

  useEffect(() => {
    fetchPassRate()
      .then((data) => setHistory((data.history ?? []).slice().reverse()))
      .catch((err) => setListError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleSelect(id) {
    if (selected?.id === id && !detailLoading) {
      setSelected(null);
      return;
    }
    latestIdRef.current = id;
    setDetailLoading(true);
    setDetailError(null);
    try {
      const audit = await fetchAudit(id);
      if (latestIdRef.current === id) {
        setSelected(audit);
      }
    } catch (err) {
      if (latestIdRef.current === id) {
        setDetailError(err.message);
      }
    } finally {
      if (latestIdRef.current === id) {
        setDetailLoading(false);
      }
    }
  }

  if (loading) return <p className="status-msg">Loading audit records...</p>;
  if (listError) return <p className="error-msg">{listError}</p>;
  if (history.length === 0)
    return <p className="status-msg">No audit records yet. Run an audit first.</p>;

  return (
    <div className="browser-layout">
      <div className="browser-list">
        <p className="browser-count">{history.length} records</p>
        {history.map((row) => {
          const pass = row.verdict === "pass";
          const active = selected?.id === row.id;
          return (
            <button
              key={row.id}
              className={`browser-row ${active ? "browser-row-active" : ""}`}
              onClick={() => handleSelect(row.id)}
            >
              <span className={`verdict-dot ${pass ? "dot-pass" : "dot-fail"}`} />
              <span className="browser-id">#{row.id}</span>
              <span className="browser-verdict">
                {row.verdict?.toUpperCase() ?? ""}
              </span>
              <span className="browser-ts">
                {new Date(row.created_at).toLocaleString()}
              </span>
            </button>
          );
        })}
      </div>

      <div className="browser-detail">
        {detailLoading && <p className="status-msg">Loading...</p>}
        {!detailLoading && detailError && (
          <p className="error-msg">{detailError}</p>
        )}
        {!detailLoading && !detailError && selected && (
          <AuditResult audit={selected} />
        )}
        {!detailLoading && !detailError && !selected && (
          <p className="status-msg">Select a record to view details.</p>
        )}
      </div>
    </div>
  );
}
