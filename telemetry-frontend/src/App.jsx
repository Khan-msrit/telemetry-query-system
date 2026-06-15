import { useState, useEffect } from "react";
import axios from "axios";

import MetricCard from "./components/telemetry/MetricCard";
import LineChartView from "./components/charts/LineChartView";
import MultiLineChartView from "./components/charts/MultiLineChartView";

function App() {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

  // 🔥 1. DEBOUNCE EFFECT: Delays updating debouncedQuery until typing pauses for 300ms
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // 🔥 2. AUTOCOMPLETE EFFECT: Fires API call only when debouncedQuery changes
  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setSuggestions([]);
      return;
    }

    const fetchSuggestions = async () => {
      try {
        const res = await axios.get(
          `http://localhost:8000/autocomplete?q=${debouncedQuery}`
        );
        setSuggestions(res.data);
      } catch {
        setSuggestions([]);
      }
    };

    fetchSuggestions();
  }, [debouncedQuery]);

  const sendQuery = async (customQuery = null) => {
    const finalQuery = customQuery || query;

    if (!finalQuery.trim()) return;

    const userMessage = {
      role: "user",
      content: finalQuery
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await axios.post(
        "http://localhost:8000/query",
        { query: finalQuery }
      );

      const botMessage = {
        role: "bot",
        content: response.data
      };

      setMessages(prev => [...prev, botMessage]);
    } catch {
      const errorMessage = {
        role: "bot",
        content: { type: "error", message: "Backend error" }
      };

      setMessages(prev => [...prev, errorMessage]);
    }

    setQuery("");
    setSuggestions([]);
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>Telemetry Mission Console</h1>

      {/* CHAT AREA */}
      <div style={{
        border: "1px solid #ddd",
        padding: "20px",
        height: "500px",
        overflowY: "auto",
        marginBottom: "20px"
      }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ marginBottom: "30px" }}>
            {/* USER */}
            {msg.role === "user" && (
              <div>
                <strong>User:</strong> {msg.content}
              </div>
            )}

            {/* SYSTEM */}
            {msg.role === "bot" && (
              <div style={{ marginTop: "10px" }}>
                <strong>System:</strong>

                {msg.content.type === "metric" && (
                  <MetricCard value={msg.content.value} />
                )}

                {msg.content.type === "line" && (
                  <LineChartView data={msg.content} />
                )}

                {msg.content.type === "multi_line" && (
                  <MultiLineChartView data={msg.content} />
                )}

                {msg.content.type === "error" && (
                  <div style={{ color: "red" }}>
                    {msg.content.message}

                    {msg.content.suggestions &&
                      msg.content.suggestions.map((s, i) => (
                        <button
                          key={i}
                          onClick={() => sendQuery(`show ${s}`)}
                          style={{ margin: "5px" }}
                        >
                          {s}
                        </button>
                      ))
                    }
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* INPUT + AUTOCOMPLETE */}
      <div style={{ position: "relative" }}>
        <input
          style={{
            width: "400px",
            padding: "10px",
            fontSize: "16px"
          }}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendQuery();
            }
          }}
          placeholder="Ask telemetry..."
        />

        <button
          style={{
            marginLeft: "10px",
            padding: "10px",
            fontSize: "16px"
          }}
          onClick={() => sendQuery()}
        >
          Send
        </button>

        {/* 🔥 AUTOCOMPLETE DROPDOWN */}
        {suggestions.length > 0 && (
          <div style={{
            position: "absolute",
            top: "45px",
            width: "400px",
            border: "1px solid #ccc",
            background: "#fff",
            color:"#000",
            zIndex: 100
          }}>
            {suggestions.map((s, i) => (
              <div
                key={i}
                style={{
                  padding:"8px",
                  cursor:"pointer",
                  color:"#000",           // 🔥 ensure visible
                  background:"#fff"
                }}
                onMouseEnter={(e) => e.target.style.background = "#eee"}
                onMouseLeave={(e) => e.target.style.background = "#fff"}
                onClick={() => {
                  setQuery(`show ${s}`);
                  setSuggestions([]);
                }}
              >
                {s}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
