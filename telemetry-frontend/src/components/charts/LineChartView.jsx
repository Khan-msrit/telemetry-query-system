import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

export default function LineChartView({ data }) {

  return (

    <div>

      <h2>{data.parameter}</h2>

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
          dataKey={data.parameter}
          stroke="#8884d8"
          dot={false}
        />

      </LineChart>

    </div>

  );

}
