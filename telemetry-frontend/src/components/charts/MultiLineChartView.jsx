import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

export default function MultiLineChartView({ data }) {

  return (

    <div>

      <h2>Telemetry Comparison</h2>

      <LineChart
        width={900}
        height={400}
        data={data.data}
      >

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
