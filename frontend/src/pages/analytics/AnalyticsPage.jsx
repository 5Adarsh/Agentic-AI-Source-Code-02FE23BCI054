import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  getCitationTrends,
  getPublicationsByYear,
  getDepartmentComparison,
  getPublicationTypeDistribution,
  getHIndexData,
  getDashboardMetrics,
} from '../../api/analytics'
import Card from '../../components/ui/Card'
import StatCard from '../../components/ui/StatCard'
import Table from '../../components/ui/Table'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import CitationTrendChart from '../../components/charts/CitationTrendChart'
import DepartmentComparisonChart from '../../components/charts/DepartmentComparisonChart'
import PublicationTypeChart from '../../components/charts/PublicationTypeChart'
import ProductivityTrendsChart from '../../components/charts/ProductivityTrendsChart'

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true)
  const [metrics, setMetrics] = useState(null)
  const [citationTrends, setCitationTrends] = useState([])
  const [pubsByYear, setPubsByYear] = useState([])
  const [deptComparison, setDeptComparison] = useState([])
  const [pubTypes, setPubTypes] = useState([])
  const [hIndexData, setHIndexData] = useState(null)

  useEffect(() => {
    async function loadAll() {
      try {
        const [dash, trends, yearly, depts, types, hData] = await Promise.all([
          getDashboardMetrics().catch(() => null),
          getCitationTrends().catch(() => []),
          getPublicationsByYear().catch(() => []),
          getDepartmentComparison().catch(() => []),
          getPublicationTypeDistribution().catch(() => []),
          getHIndexData().catch(() => null),
        ])
        setMetrics(dash)
        setCitationTrends(trends || [])
        setPubsByYear(yearly || [])
        setDeptComparison(depts || [])
        setPubTypes(types || [])
        setHIndexData(hData)
      } finally {
        setLoading(false)
      }
    }
    loadAll()
  }, [])

  if (loading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center">
        <Spinner size="lg" />
        <p className="text-xs text-slate-500 mt-2">Computing scholarly impact and citation analytics...</p>
      </div>
    )
  }

  const hasData =
    (metrics && metrics.total_publications > 0) ||
    citationTrends.length > 0 ||
    deptComparison.length > 0

  const facultyColumns = [
    {
      header: 'Faculty Member',
      accessor: 'faculty_name',
      render: (row) => (
        <div>
          <Link
            to={`/faculty/${row.faculty_id}`}
            className="font-bold text-slate-900 hover:text-blue-700 hover:underline"
          >
            {row.faculty_name}
          </Link>
          <div className="text-[11px] text-slate-500">{row.department}</div>
        </div>
      ),
    },
    {
      header: 'Publications',
      accessor: 'publications_count',
      className: 'w-24 text-center font-semibold text-slate-800',
    },
    {
      header: 'Total Citations',
      accessor: 'total_citations',
      className: 'w-28 text-center font-bold text-slate-900 font-mono',
    },
    {
      header: 'h-index',
      accessor: 'h_index',
      className: 'w-24 text-center font-bold text-blue-700 font-mono text-sm',
    },
    {
      header: 'i10-index',
      accessor: 'i10_index',
      className: 'w-24 text-center font-bold text-amber-700 font-mono text-sm',
    },
    {
      header: 'Action',
      className: 'w-24 text-right',
      render: (row) => (
        <Link
          to={`/faculty/${row.faculty_id}`}
          className="text-xs font-semibold text-blue-600 hover:underline"
        >
          View Profile →
        </Link>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
          Citation Impact & Bibliometric Analytics
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Deterministic citation trajectories, Hirsch index (h-index), and departmental research volume computations
        </p>
      </div>

      {/* Metric Tooltip Explainers Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="relative group">
          <StatCard
            label="Total Citations"
            value={metrics?.total_citations ?? 0}
            icon="📈"
            description="Verified scholarly citations count"
          />
          <div
            className="absolute top-2.5 right-2.5 text-slate-400 hover:text-slate-600 cursor-help text-xs"
            title="Total Citations: The aggregate number of times the institution's scholarly papers have been cited by other academic works across Google Scholar, Crossref, Scopus and Web of Science."
          >
            ℹ️
          </div>
        </div>

        <div className="relative group">
          <StatCard
            label="Institutional h-index"
            value={hIndexData?.institutional_h_index ?? metrics?.h_index ?? 0}
            icon="🎯"
            description="Max h papers cited ≥ h times"
          />
          <div
            className="absolute top-2.5 right-2.5 text-slate-400 hover:text-slate-600 cursor-help text-xs"
            title="Hirsch Index (h-index): An institution has an h-index of h if h of its papers have at least h citations each, and the other papers have fewer than h citations each. Computed deterministically in Python."
          >
            ℹ️
          </div>
        </div>

        <div className="relative group">
          <StatCard
            label="Institutional i10-Index"
            value={hIndexData?.institutional_i10_index ?? metrics?.i10_index ?? 0}
            icon="⭐"
            description="Publications with ≥ 10 citations"
          />
          <div
            className="absolute top-2.5 right-2.5 text-slate-400 hover:text-slate-600 cursor-help text-xs"
            title="i10-Index: The number of publications that have at least 10 citations. A robust measure of sustained research impact introduced by Google Scholar."
          >
            ℹ️
          </div>
        </div>

        <div className="relative group">
          <StatCard
            label="Avg Citations / Pub"
            value={metrics?.avg_citations_per_pub ?? 0}
            icon="⚡"
            description="Institutional research impact factor"
          />
          <div
            className="absolute top-2.5 right-2.5 text-slate-400 hover:text-slate-600 cursor-help text-xs"
            title="Average Citations per Publication: The mean number of citations received per published work. Used heavily in NIRF and NAAC criteria for research quality."
          >
            ℹ️
          </div>
        </div>
      </div>

      {!hasData ? (
        <Card>
          <EmptyState
            icon="📈"
            title="No Citation Records Computed"
            description="Analytics are computed dynamically from actual publication records. Import records to calculate real h-index and citation trajectories."
            actionLabel="Import Scholar CSV"
            onAction={() => (window.location.href = '/publications/import')}
          />
        </Card>
      ) : (
        <>
          {/* Charts Row 1: Citation Trajectory & Productivity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card
              title="Citation Trajectory & Growth"
              subtitle="Annual citations received by university researchers"
            >
              <CitationTrendChart data={citationTrends} />
            </Card>

            <Card
              title="Annual Output & Impact Correlation"
              subtitle="Dual-axis visualization: Publications volume vs Citations received"
            >
              <ProductivityTrendsChart publications={pubsByYear} citations={citationTrends} />
            </Card>
          </div>

          {/* Charts Row 2: Department Comparison & Publication Types */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card
                title="Departmental Research Comparison"
                subtitle="Comparative research output and citation volume across Schools"
              >
                <DepartmentComparisonChart data={deptComparison} />
              </Card>
            </div>

            <div className="lg:col-span-1">
              <Card
                title="Publication Types Distribution"
                subtitle="Journals vs Conferences vs Books & Chapters"
              >
                <PublicationTypeChart data={pubTypes} />
              </Card>
            </div>
          </div>

          {/* Faculty-wise Citation Comparison Table */}
          {hIndexData?.faculty_breakdown?.length ? (
            <Card
              title="Faculty-wise Research Impact & Hirsch Metrics"
              subtitle="Individual h-index and i10-index calculations computed deterministically by the Citation Analytics Agent"
            >
              <Table columns={facultyColumns} data={hIndexData.faculty_breakdown} />
            </Card>
          ) : null}
        </>
      )}
    </div>
  )
}
