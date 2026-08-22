import { useState, useEffect } from "react";

export default function Header() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const timeStr = time.toLocaleTimeString("en-US", { hour12: false });

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "18px 28px",
        borderBottom: "1px solid var(--border)",
        background: "var(--bg)",
      }}
    >
      <div style={{ display: "flex", alignItems: "baseline", gap: "12px" }}>
        <h1
          style={{
            fontFamily: "var(--font-display)",
            fontSize: "18px",
            fontWeight: 600,
            margin: 0,
            letterSpacing: "0.02em",
          }}
        >
          Telemetry Mission Console
        </h1>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "11px",
            color: "var(--text-faint)",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          v1.0
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span className="pulse-dot" />
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              color: "var(--accent-cyan)",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
            }}
          >
            Systems Nominal
          </span>
        </div>

        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "13px",
            color: "var(--text-muted)",
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {timeStr}
        </span>
      </div>
    </header>
  );
}