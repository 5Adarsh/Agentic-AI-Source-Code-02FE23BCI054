import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const COLORS = {
  verified: '#10b981', // green
  partially_verified: '#3b82f6', // blue
  requires_review: '#f59e0b', // amber
  unverified: '#94a3b8', // slate
  duplicate: '#ef4444', // red
}

const LABELS = {
  verified: 'Verified (Scopus/WoS)',
  partially_verified: 'Partially Verified',
  requires_review: 'Requires Review',
  unverified: 'Unverified',
  duplicate: 'Duplicate',
}

export default function VerificationDistributionChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-sm text-slate-400">
        No verification records available.
      </div>
    )
  }

  const chartData = data.map((item) => ({
    name: LABELS[item.status] || item.status,
    value: item.count,
    color: COLORS[item.status] || '#64748b',
  }))

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={85}
            paddingAngle={3}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px', border: 'none' }}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="circle"
            wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
