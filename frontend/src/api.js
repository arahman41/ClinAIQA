export async function submitAudit({ output_text, source_record, doc_type }, signal) {
  const res = await fetch("/audit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ output_text, source_record, doc_type }),
    signal,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Audit failed (${res.status}): ${detail}`);
  }
  return res.json();
}

export async function fetchAudit(id) {
  const res = await fetch(`/audit/${id}`);
  if (!res.ok) throw new Error(`Fetch audit failed (${res.status})`);
  return res.json();
}

export async function fetchPassRate() {
  const res = await fetch("/audits/pass-rate");
  if (!res.ok) throw new Error(`Fetch pass-rate failed (${res.status})`);
  return res.json();
}
