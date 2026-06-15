import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

export default function LineChartView({ data }) {

  // 🔥 FIX: support BOTH formats
  const param =
    data.parameter ||
    (data.parameters && data.parameters[0]);

  if (!param) {
    return <div>No parameter found</div>;
  }

  return (

    <div>

      <h2>{param}</h2>

      <LineChart
        width={900}
        height={400}
        data={data.data}
      >

        <CartesianGrid stroke="#ccc"/>

        <XAxis dataKey="time"/>

        <YAxis/>

        <Tooltip/>

        <Line
          type="monotone"
          dataKey={param}
          stroke="#8884d8"
          dot={false}
        />

      </LineChart>

    </div>

  );

}
