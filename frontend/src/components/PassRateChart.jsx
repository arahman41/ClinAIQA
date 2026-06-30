import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { fetchPassRate } from "../api.js";

function buildChartData(history) {
  let passed = 0;
  return history.map((row, i) => {
    if (row.verdict === "pass") passed++;
    return {
      index: i + 1,
      passRate: Math.round((passed / (i + 1)) * 100),
      verdict: row.verdict,
      id: row.id,
    };
  });
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <p>Audit #{d.id}</p>
      <p>
        Cumulative pass rate: <strong>{d.passRate}%</strong>
      </p>
      <p>This audit: {d.verdict?.toUpperCase() ?? "unknown"}</p>
    </div>
  );
}

export default function PassRateChart() {
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPassRate()
      .then((res) => {
        setSummary(res);
        setData(buildChartData(res.history ?? []));
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="status-msg">Loading pass-rate data...</p>;
  if (error) return <p className="error-msg">{error}</p>;
  if (!data.length)
    return <p className="status-msg">No audits yet. Run an audit first.</p>;

  const pct = Math.round((summary.pass_rate ?? 0) * 100);

  return (
    <div className="chart-section">
      <div className="chart-summary">
        <div className="stat-box">
          <span className="stat-value">{pct}%</span>
          <span className="stat-label">overall pass rate</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{summary.passed}</span>
          <span className="stat-label">passed</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{summary.total - summary.passed}</span>
          <span className="stat-label">failed</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{summary.total}</span>
          <span className="stat-label">total audits</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="index"
            label={{ value: "Audit #", position: "insideBottomRight", offset: -8 }}
            tick={{ fontSize: 12 }}
          />
          <YAxis
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={80} stroke="#aaa" strokeDasharray="4 4" />
          <Line
            type="monotone"
            dataKey="passRate"
            stroke="#1a56b0"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="chart-note">Dashed line at 80%. Cumulative pass rate over audit sequence.</p>
    </div>
  );
}
