import { useState } from "react";
import AuditForm from "./components/AuditForm.jsx";
import AuditBrowser from "./components/AuditBrowser.jsx";
import PassRateChart from "./components/PassRateChart.jsx";

const TABS = [
  { id: "submit", label: "Submit Audit" },
  { id: "browse", label: "Audit Records" },
  { id: "passrate", label: "Pass Rate" },
];

export default function App() {
  const [tab, setTab] = useState("submit");

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <h1>ClinAIQA</h1>
          <p className="header-sub">Clinical AI Quality Assurance</p>
        </div>
      </header>

      <nav className="tab-nav">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`tab-btn ${tab === t.id ? "tab-btn-active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main className="app-main">
        {tab === "submit" && <AuditForm />}
        {tab === "browse" && <AuditBrowser />}
        {tab === "passrate" && <PassRateChart />}
      </main>
    </div>
  );
}
