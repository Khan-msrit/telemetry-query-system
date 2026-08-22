import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Brush } from "recharts";

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div style={{ background: "var(--panel-alt)", border: "1px solid var(--border)", borderRadius: "6px", padding: "8px 12px", fontFamily: "var(--font-mono)", fontSize: "11.5px" }}>
      <div style={{ color: "var(--text-faint)", marginBottom: "4px" }}>{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ color: p.stroke }}>
          {p.dataKey}: {typeof p.value === "number" ? p.value.toFixed(2) : p.value}
        </div>
      ))}
    </div>
  );
}

function ToggleButton({ active, children, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: active ? "var(--accent-cyan-dim)" : "transparent",
        border: `1px solid ${active ? "var(--accent-cyan)" : "var(--border)"}`,
        color: active ? "var(--accent-cyan)" : "var(--text-muted)",
        borderRadius: "5px",
        padding: "4px 10px",
        fontSize: "11px",
        fontFamily: "var(--font-mono)",
        cursor: "pointer",
      }}
    >
      {children}
    </button>
  );
}

export default function LineChartView({ data }) {
  const [view, setView] = useState("chart");
  const param = data.parameter || (data.parameters && data.parameters[0]);

  if (!param) {
    return <div style={{ color: "var(--text-muted)", fontSize: "13px" }}>No parameter found</div>;
  }

  return (
    <div className="grid-texture" style={{ background: "var(--panel)", border: "1px solid var(--border)", borderRadius: "8px", padding: "18px 20px", width: "100%", maxWidth: "760px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
        <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-faint)", letterSpacing: "0.1em", textTransform: "uppercase" }}>
          {param}
        </div>
        <div style={{ display: "flex", gap: "6px" }}>
          <ToggleButton active={view === "chart"} onClick={() => setView("chart")}>Chart</ToggleButton>
          <ToggleButton active={view === "table"} onClick={() => setView("table")}>Table</ToggleButton>
        </div>
      </div>

      {view === "chart" ? (
        <ResponsiveContainer width="100%" height={340}>
          <LineChart data={data.data} margin={{ top: 4, right: 12, bottom: 0, left: -12 }}>
            <CartesianGrid stroke="var(--border-soft)" vertical={false} />
            <XAxis dataKey="time" stroke="var(--text-faint)" tick={{ fill: "var(--text-muted)", fontSize: 10, fontFamily: "var(--font-mono)" }} tickLine={false} axisLine={{ stroke: "var(--border)" }} />
            <YAxis stroke="var(--text-faint)" tick={{ fill: "var(--text-muted)", fontSize: 10, fontFamily: "var(--font-mono)" }} tickLine={false} axisLine={{ stroke: "var(--border)" }} width={50} />
            <Tooltip content={<CustomTooltip />} />
            <Line type="monotone" dataKey={param} stroke="var(--accent-cyan)" strokeWidth={2} dot={false} />
            {data.data.length > 10 && (
              <Brush
                dataKey="time"
                height={22}
                stroke="var(--accent-cyan)"
                fill="var(--panel-alt)"
                travellerWidth={8}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div style={{ maxHeight: "340px", overflowY: "auto" }} className="scroll-fade">
          <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "var(--font-mono)", fontSize: "12px" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", padding: "6px 8px", color: "var(--text-faint)", borderBottom: "1px solid var(--border)", position: "sticky", top: 0, background: "var(--panel)" }}>time</th>
                <th style={{ textAlign: "right", padding: "6px 8px", color: "var(--text-faint)", borderBottom: "1px solid var(--border)", position: "sticky", top: 0, background: "var(--panel)" }}>{param}</th>
              </tr>
            </thead>
            <tbody>
              {data.data.map((row, i) => (
                <tr key={i}>
                  <td style={{ padding: "5px 8px", color: "var(--text-muted)", borderBottom: "1px solid var(--border-soft)" }}>{row.time}</td>
                  <td style={{ padding: "5px 8px", color: "var(--text-primary)", textAlign: "right", borderBottom: "1px solid var(--border-soft)" }}>
                    {typeof row[param] === "number" ? row[param].toFixed(3) : row[param]}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}