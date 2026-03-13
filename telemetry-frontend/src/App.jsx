import { useState } from "react";
import axios from "axios";

function App() {

  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);

  const sendQuery = async () => {

    const response = await axios.post("http://localhost:8000/query", {
      query: query
    });

    setResult(response.data);

  };

  return (

    <div style={{padding:"40px", fontFamily:"Arial"}}>

      <h1>Telemetry Mission Console</h1>

      <input
        style={{width:"400px", padding:"10px"}}
        value={query}
        onChange={(e)=>setQuery(e.target.value)}
        placeholder="Ask telemetry..."
      />

      <button
        style={{marginLeft:"10px", padding:"10px"}}
        onClick={sendQuery}
      >
        Send
      </button>

      <pre style={{marginTop:"30px"}}>
        {JSON.stringify(result, null, 2)}
      </pre>

    </div>
  );

}

export default App;
