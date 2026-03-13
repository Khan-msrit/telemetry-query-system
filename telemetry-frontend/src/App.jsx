import { useState } from "react";
import axios from "axios";

import MetricCard from "./components/telemetry/MetricCard";
import LineChartView from "./components/charts/LineChartView";
import MultiLineChartView from "./components/charts/MultiLineChartView";

function App() {

  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);

  const sendQuery = async () => {

    try {

      const response = await axios.post(
        "http://localhost:8000/query",
        {
          query: query
        }
      );

      setResult(response.data);

    } catch (error) {

      console.error("Backend error:", error);

    }

  };

  return (

    <div style={{padding:"40px", fontFamily:"Arial"}}>

      <h1>Telemetry Mission Console</h1>

      <div style={{marginTop:"20px"}}>

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

      <div style={{marginTop:"40px"}}>

        {result && result.type === "metric" && (
          <MetricCard value={result.value} />
        )}

        {result && result.type === "line" && (
          <LineChartView data={result} />
        )}

        {result && result.type === "multi_line" && (
          <MultiLineChartView data={result} />
        )}

      </div>

    </div>

  );

}

export default App;
