import { useRef, useEffect } from "react";
import MetricCard from "./telemetry/MetricCard";
import LineChartView from "./charts/LineChartView";
import MultiLineChartView from "./charts/MultiLineChartView";
import StatusCard from "./telemetry/StatusCard";
import StatusHistoryTable from "./telemetry/StatusHistoryTable";

export default function ChatPanel({
  messages,
  query,
  setQuery,
  onSend,
  suggestions,
  onSelectSuggestion,
  isLoading,
}) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>
      <div
        ref={scrollRef}
        className="scroll-fade"
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "28px",
          display: "flex",
          flexDirection: "column",
          gap: "22px",
        }}
      >
        {messages.length === 0 && (
          <div style={{ margin: "auto", textAlign: "center", color: "var(--text-faint)", maxWidth: "360px" }}>
            <div style={{ fontFamily: "var(--font-display)", fontSize: "15px", color: "var(--text-muted)", marginBottom: "6px" }}>
              No queries yet
            </div>
            <div style={{ fontSize: "12.5px", lineHeight: 1.6 }}>
              Ask about a telemetry parameter in plain language, or pick a quick-start query from the sidebar.
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index}>
            {msg.role === "user" && (
              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <div
                  style={{
                    background: "var(--accent-cyan-dim)",
                    border: "1px solid rgba(94, 234, 212, 0.25)",
                    borderRadius: "8px",
                    padding: "9px 14px",
                    maxWidth: "70%",
                    fontSize: "13.5px",
                    color: "var(--text-primary)",
                  }}
                >
                  {msg.content}
                </div>
              </div>
            )}

            {msg.role === "bot" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "10px",
                    color: "var(--text-faint)",
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                  }}
                >
                  System
                </div>

                {msg.content.type === "metric" && (
                  <MetricCard value={msg.content.value} label={msg.content.parameter} />
                )}

                {msg.content.type === "line" && <LineChartView data={msg.content} />}
                {msg.content.type === "multi_line" && <MultiLineChartView data={msg.content} />}
                {msg.content.type === "status" && (<StatusCard value={msg.content.value} label={msg.content.parameter} time={msg.content.time} />)}
                {msg.content.type === "status_history" && (<StatusHistoryTable parameter={msg.content.parameter} data={msg.content.data} />)}

                {msg.content.type === "error" && (
                  <div
                    style={{
                      border: "1px solid rgba(240, 85, 76, 0.3)",
                      background: "var(--accent-red-dim)",
                      borderRadius: "8px",
                      padding: "14px 16px",
                      maxWidth: "480px",
                    }}
                  >
                    <div style={{ color: "var(--accent-red)", fontSize: "13px", marginBottom: "10px" }}>
                      {msg.content.message}
                    </div>

                    {msg.content.suggestions && (
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                        {msg.content.suggestions.map((s, i) => (
                          <button
                            key={i}
                            onClick={() => onSend(s)}
                            style={{
                              background: "var(--panel-alt)",
                              border: "1px solid var(--border)",
                              borderRadius: "5px",
                              padding: "5px 10px",
                              color: "var(--text-primary)",
                              fontSize: "11.5px",
                              cursor: "pointer",
                            }}
                          >
                            {s}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
                {isLoading && (
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                color: "var(--text-faint)",
                letterSpacing: "0.08em",
                textTransform: "uppercase",
              }}
            >
              System
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                background: "var(--panel)",
                border: "1px solid var(--border)",
                borderRadius: "8px",
                padding: "10px 16px",
                width: "fit-content",
              }}
            >
              <span className="pulse-dot" />
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "12px",
                  color: "var(--text-muted)",
                }}
              >
                Processing query...
              </span>
            </div>
          </div>
        )}
      </div>

      <div
        style={{
          borderTop: "1px solid var(--border)",
          padding: "18px 28px 24px",
          position: "relative",
          background: "var(--bg)",
        }}
      >
        {suggestions.length > 0 && (
          <div
            style={{
              position: "absolute",
              bottom: "72px",
              left: "28px",
              right: "28px",
              maxWidth: "600px",
              background: "var(--panel-alt)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              overflow: "hidden",
              boxShadow: "0 8px 24px rgba(0,0,0,0.4)",
            }}
          >
            {suggestions.map((s, i) => (
              <div
                key={i}
                onClick={() => onSelectSuggestion(s)}
                style={{
                  padding: "10px 14px",
                  fontSize: "12.5px",
                  fontFamily: "var(--font-mono)",
                  color: "var(--text-primary)",
                  cursor: "pointer",
                  borderBottom: i < suggestions.length - 1 ? "1px solid var(--border)" : "none",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "var(--accent-cyan-dim)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
              >
                {s}
              </div>
            ))}
          </div>
        )}

        <div style={{ display: "flex", gap: "10px", maxWidth: "600px" }}>
                    <input
            style={{
              flex: 1,
              background: "var(--panel)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              padding: "12px 16px",
              fontSize: "13.5px",
              color: "var(--text-primary)",
              opacity: isLoading ? 0.5 : 1,
            }}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") onSend(); }}
            placeholder="Ask telemetry — e.g. max battery voltage"
            disabled={isLoading}
          />
          <button
            onClick={() => onSend()}
            disabled={isLoading}
            style={{
              background: "var(--accent-cyan)",
              border: "none",
              borderRadius: "8px",
              padding: "0 22px",
              fontSize: "13px",
              fontWeight: 600,
              color: "#04191a",
              cursor: isLoading ? "default" : "pointer",
              opacity: isLoading ? 0.6 : 1,
            }}
          >
            {isLoading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}