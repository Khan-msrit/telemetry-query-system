export default function MetricCard({ value }) {

  return (

    <div style={{
      fontSize:"48px",
      fontWeight:"bold",
      padding:"30px",
      border:"1px solid #ddd",
      width:"200px",
      textAlign:"center"
    }}>
      {value}
    </div>

  );

}
