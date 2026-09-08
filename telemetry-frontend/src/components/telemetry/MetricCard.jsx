export default function MetricCard({ value, label }) {
  const formatValue = (v) => {
    if (typeof v !== "number") return v;
    if (v !== 0 && Math.abs(v) < 0.001) {
      // Very small values: show real precision instead of rounding to 0
      return v.toPrecision(4);
    }
    return v.toLocaleString(undefined, { maximumFractionDigits: 4 });
  };
  const display = formatValue(value);

  return (
    <div
      className="grid-texture"
      style={{
        background: "var(--panel)",
        border: "1px solid var(--border)",
        borderRadius: "8px",
        padding: "22px 26px",
        width: "220px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-faint)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "10px" }}>
        {label || "Reading"}
      </div>
      <div style={{ fontFamily: "var(--font-mono)", fontSize: "40px", fontWeight: 600, color: "var(--accent-cyan)", lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>
        {display}
      </div>
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: "3px", background: "var(--accent-cyan)", opacity: 0.7 }} />
    </div>
  );
}