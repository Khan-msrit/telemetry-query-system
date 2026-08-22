import { useState, useEffect } from "react";
import "./App.css";

import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import { fetchAutocomplete, sendNlQuery } from "./services/api";

function App() {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    if (debouncedQuery.length < 2) { setSuggestions([]); return; }
    let cancelled = false;
    fetchAutocomplete(debouncedQuery)
      .then((data) => { if (!cancelled) setSuggestions(data); })
      .catch(() => { if (!cancelled) setSuggestions([]); });
    return () => { cancelled = true; };
  }, [debouncedQuery]);

  const sendQuery = async (customQuery = null) => {
    const finalQuery = customQuery || query;
    if (!finalQuery.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: finalQuery }]);
    setHistory((prev) => [...prev, finalQuery]);
    setQuery("");
    setSuggestions([]);

    try {
      const data = await sendNlQuery(finalQuery);
      setMessages((prev) => [...prev, { role: "bot", content: data }]);
    } catch {
      setMessages((prev) => [...prev, { role: "bot", content: { type: "error", message: "Backend error — check the API server." } }]);
    }
  };

  return (
    <div className="console-shell">
      <Sidebar history={history} onSelectQuery={(q) => sendQuery(q)} />
      <div style={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
        <Header />
        <ChatPanel
          messages={messages}
          query={query}
          setQuery={setQuery}
          onSend={sendQuery}
          suggestions={suggestions}
          onSelectSuggestion={(s) => { setQuery(""); setSuggestions([]); sendQuery(`show ${s}`); }}
        />
      </div>
    </div>
  );
}

export default App;