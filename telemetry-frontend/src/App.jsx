import { useState } from "react";
import axios from "axios";

import MetricCard from "./components/telemetry/MetricCard";
import LineChartView from "./components/charts/LineChartView";
import MultiLineChartView from "./components/charts/MultiLineChartView";

function App() {

  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);

  const sendQuery = async () => {

    if (!query.trim()) return;

    const userMessage = {
      role: "user",
      content: query
    };

    setMessages(prev => [...prev, userMessage]);

    try {

      const response = await axios.post(
        "http://localhost:8000/query",
        { query: query }
      );

      const botMessage = {
        role: "bot",
        content: response.data
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {

      const errorMessage = {
        role: "bot",
        content: { error: "Backend error" }
      };

      setMessages(prev => [...prev, errorMessage]);

    }

    setQuery("");

  };

  return (

    <div style={{padding:"40px", fontFamily:"Arial"}}>

      <h1>Telemetry Mission Console</h1>

      <div style={{
        border:"1px solid #ddd",
        padding:"20px",
        height:"500px",
        overflowY:"auto",
        marginBottom:"20px"
      }}>

        {messages.map((msg, index) => (

          <div key={index} style={{marginBottom:"30px"}}>

            {msg.role === "user" && (
              <div>
                <strong>User:</strong> {msg.content}
              </div>
            )}

            {msg.role === "bot" && (

              <div style={{marginTop:"10px"}}>

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

                {msg.content.error && (
                  <div style={{color:"red"}}>{msg.content.error}</div>
                )}

              </div>

            )}

          </div>

        ))}

      </div>

      <div>

        <input
          style={{
            width:"400px",
            padding:"10px",
            fontSize:"16px"
          }}
          value={query}
          onChange={(e)=>setQuery(e.target.value)}
          placeholder="Ask telemetry..."
        />

        <button
          style={{
            marginLeft:"10px",
            padding:"10px",
            fontSize:"16px"
          }}
          onClick={sendQuery}
        >
          Send
        </button>

      </div>

    </div>

  );

}

export default App;
