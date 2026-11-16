import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

export default function DepartmentComparisonChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-sm text-slate-400">
        No departmental analytics to compare.
      </div>
    )
  }

  const normalizedData = data.map((d) => ({
    department: d.department || d.department_name || d.name || d.code,
    publications: d.publications ?? d.total_publications ?? 0,
    citations: d.citations ?? d.total_citations ?? 0,
  }))

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={normalizedData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis
            dataKey="department"
            stroke="#64748b"
            fontSize={10}
            interval={0}
            angle={-15}
            textAnchor="end"
          />
          <YAxis stroke="#64748b" fontSize={11} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px', border: 'none' }}
          />
          <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '11px' }} />
          <Bar dataKey="publications" fill="#1d4ed8" radius={[4, 4, 0, 0]} name="Publications" />
          <Bar dataKey="citations" fill="#059669" radius={[4, 4, 0, 0]} name="Citations" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
