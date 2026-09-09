export default function StatusHistoryTable({ parameter, data }) {
  return (
    <div
      className="grid-texture"
      style={{ background: "var(--panel)", border: "1px solid var(--border)", borderRadius: "8px", padding: "18px 20px", width: "100%", maxWidth: "480px" }}
    >
      <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-faint)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "12px" }}>
        {parameter} — status history
      </div>
      <div style={{ maxHeight: "280px", overflowY: "auto" }} className="scroll-fade">
        <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "var(--font-mono)", fontSize: "12px" }}>
          <thead>
            <tr>
              <th style={{ textAlign: "left", padding: "6px 8px", color: "var(--text-faint)", borderBottom: "1px solid var(--border)" }}>time</th>
              <th style={{ textAlign: "right", padding: "6px 8px", color: "var(--text-faint)", borderBottom: "1px solid var(--border)" }}>value</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                <td style={{ padding: "5px 8px", color: "var(--text-muted)", borderBottom: "1px solid var(--border-soft)" }}>{row.time}</td>
                <td style={{ padding: "5px 8px", color: "var(--accent-amber)", textAlign: "right", borderBottom: "1px solid var(--border-soft)" }}>{row.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}