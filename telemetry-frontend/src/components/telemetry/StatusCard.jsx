export default function StatusCard({ value, label, time }) {
  return (
    <div
      className="grid-texture"
      style={{
        background: "var(--panel)",
        border: "1px solid var(--border)",
        borderRadius: "8px",
        padding: "22px 26px",
        width: "260px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-faint)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "10px" }}>
        {label || "Status"}
      </div>
      <div style={{ fontFamily: "var(--font-mono)", fontSize: "30px", fontWeight: 600, color: "var(--accent-amber)", lineHeight: 1.1, wordBreak: "break-word" }}>
        {String(value)}
      </div>
      {time && (
        <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-faint)", marginTop: "12px" }}>
          as of {time}
        </div>
      )}
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: "3px", background: "var(--accent-amber)", opacity: 0.7 }} />
    </div>
  );
}