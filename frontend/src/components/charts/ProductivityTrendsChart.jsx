import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

export default function ProductivityTrendsChart({ publications = [], citations = [] }) {
  if (!publications.length && !citations.length) {
    return (
      <div className="h-64 flex items-center justify-center text-sm text-slate-400">
        No productivity trend data available.
      </div>
    )
  }

  // Merge by year
  const yearsSet = new Set([
    ...publications.map((p) => p.year),
    ...citations.map((c) => c.year),
  ])
  const sortedYears = Array.from(yearsSet).sort((a, b) => a - b)

  const pubMap = Object.fromEntries(publications.map((p) => [p.year, p.count ?? p.publications ?? 0]))
  const citeMap = Object.fromEntries(citations.map((c) => [c.year, c.citations ?? 0]))

  const data = sortedYears.map((yr) => ({
    year: yr,
    publications: pubMap[yr] || 0,
    citations: citeMap[yr] || 0,
  }))

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="year" stroke="#94a3b8" fontSize={12} />
          <YAxis yAxisId="left" stroke="#2563eb" fontSize={11} label={{ value: 'Pubs', angle: -90, position: 'insideLeft', fontSize: 10 }} />
          <YAxis yAxisId="right" orientation="right" stroke="#dc2626" fontSize={11} label={{ value: 'Citations', angle: 90, position: 'insideRight', fontSize: 10 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px', border: 'none' }}
          />
          <Legend wrapperStyle={{ fontSize: '11px' }} />
          <Bar yAxisId="left" dataKey="publications" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Publications" barSize={24} />
          <Line yAxisId="right" type="monotone" dataKey="citations" stroke="#dc2626" strokeWidth={2.5} dot={{ r: 4 }} name="Citations" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
