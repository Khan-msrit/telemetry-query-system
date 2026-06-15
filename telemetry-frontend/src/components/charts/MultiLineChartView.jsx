import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

export default function MultiLineChartView({ data }) {

  // 🔥 FIX: normalize all values
  const cleanData = data.data.map(d => {
    const obj = { time: d.time };

    data.parameters.forEach(p => {
      obj[p] = Number(d[p]) || 0;
    });

    return obj;
  });

  return (
    <div>

      <h2>Telemetry Comparison</h2>

      <LineChart width={900} height={400} data={cleanData}>

        <CartesianGrid stroke="#ccc"/>

        <XAxis dataKey="time"/>

        <YAxis/>

        <Tooltip/>

        {data.parameters.map((param, index) => (

          <Line
            key={param}
            type="monotone"
            dataKey={param}
            stroke={["#8884d8","#82ca9d","#ff7300","#ff0000"][index % 4]}
            dot={false}
          />

        ))}

      </LineChart>

    </div>
  );
}
