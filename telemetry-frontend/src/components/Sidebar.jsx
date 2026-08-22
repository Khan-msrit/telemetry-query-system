const QUICK_QUERIES = [
  "avg battery voltage",
  "show battery voltage trend",
  "max battery voltage",
];

export default function Sidebar({ history, onSelectQuery }) {
  return (
    <aside
      style={{
        background: "var(--panel)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        height: "100%",
        overflow: "hidden",
      }}
    >
      <div style={{ padding: "20px 20px 16px" }}>
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            color: "var(--text-faint)",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            marginBottom: "10px",
          }}
        >
          Quick Start
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
          {QUICK_QUERIES.map((q) => (
            <button
              key={q}
              onClick={() => onSelectQuery(q)}
              style={{
                textAlign: "left",
                background: "var(--panel-alt)",
                border: "1px solid var(--border)",
                borderRadius: "6px",
                padding: "9px 12px",
                color: "var(--text-primary)",
                fontSize: "12.5px",
                cursor: "pointer",
                transition: "border-color 0.15s, color 0.15s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "var(--accent-cyan)";
                e.currentTarget.style.color = "var(--accent-cyan)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "var(--border)";
                e.currentTarget.style.color = "var(--text-primary)";
              }}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      <div style={{ height: "1px", background: "var(--border)" }} />

      <div style={{ padding: "16px 20px", flex: 1, overflowY: "auto" }} className="scroll-fade">
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            color: "var(--text-faint)",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            marginBottom: "10px",
          }}
        >
          Query Log
        </div>

        {history.length === 0 && (
          <div style={{ fontSize: "12px", color: "var(--text-faint)", fontStyle: "italic" }}>
            No queries yet.
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          {history
            .slice()
            .reverse()
            .map((q, i) => (
              <button
                key={i}
                onClick={() => onSelectQuery(q)}
                style={{
                  textAlign: "left",
                  background: "transparent",
                  border: "none",
                  borderLeft: "2px solid var(--border)",
                  padding: "6px 10px",
                  color: "var(--text-muted)",
                  fontFamily: "var(--font-mono)",
                  fontSize: "11.5px",
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderLeftColor = "var(--accent-cyan)";
                  e.currentTarget.style.color = "var(--text-primary)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderLeftColor = "var(--border)";
                  e.currentTarget.style.color = "var(--text-muted)";
                }}
                title={q}
              >
                {q}
              </button>
            ))}
        </div>
      </div>
    </aside>
  );
}