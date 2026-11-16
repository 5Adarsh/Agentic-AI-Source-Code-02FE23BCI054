import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts'

export default function HIndexGaugeChart({ value = 0, max = 50, label = 'h-index' }) {
  const chartData = [{ name: label, value: value || 0 }]

  return (
    <div className="h-48 flex flex-col items-center justify-center relative">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          cx="50%"
          cy="50%"
          innerRadius="70%"
          outerRadius="90%"
          barSize={12}
          data={chartData}
          startAngle={180}
          endAngle={0}
        >
          <PolarAngleAxis type="number" domain={[0, max]} angleAxisId={0} tick={false} />
          <RadialBar background dataKey="value" cornerRadius={6} fill="#6366f1" />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1 text-center">
        <span className="text-3xl font-extrabold text-slate-800">{value || 0}</span>
        <p className="text-xs text-slate-400 font-medium">{label}</p>
      </div>
    </div>
  )
}
