import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  getDashboardMetrics,
  getPublicationsByYear,
  getCitationTrends,
  getDepartmentComparison,
} from '../../api/analytics'
import api from '../../api/axios'
import StatCard from '../../components/ui/StatCard'
import Card from '../../components/ui/Card'
import EmptyState from '../../components/ui/EmptyState'
import Spinner from '../../components/ui/Spinner'
import Alert from '../../components/ui/Alert'
import CitationTrendChart from '../../components/charts/CitationTrendChart'
import PublicationsByYearChart from '../../components/charts/PublicationsByYearChart'
import DepartmentComparisonChart from '../../components/charts/DepartmentComparisonChart'
import VerificationDistributionChart from '../../components/charts/VerificationDistributionChart'
import ProductivityTrendsChart from '../../components/charts/ProductivityTrendsChart'
import AgentPipelineView from '../../components/agents/AgentPipelineView'
import { useAuthStore } from '../../store/authStore'

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [metrics, setMetrics] = useState(null)
  const [pubYears, setPubYears] = useState([])
  const [citeTrends, setCiteTrends] = useState([])
  const [deptComp, setDeptComp] = useState([])
  const [verifDist, setVerifDist] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [m, py, ct, dc, vd] = await Promise.all([
        getDashboardMetrics().catch(() => null),
        getPublicationsByYear().catch(() => []),
        getCitationTrends().catch(() => []),
        getDepartmentComparison().catch(() => []),
        api.get('/analytics/verification-distribution').then((r) => r.data).catch(() => []),
      ])
      setMetrics(m)
      setPubYears(py || [])
      setCiteTrends(ct || [])
      setDeptComp(dc || [])
      setVerifDist(vd || [])
    } catch (err) {
      setError(err.message || 'Failed to load dashboard metrics.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  if (loading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center gap-3">
        <Spinner size="lg" />
        <p className="text-xs text-slate-500 font-medium animate-pulse">
          Aggregating institutional publications, citations, and verification statuses...
        </p>
      </div>
    )
  }

  const hasData = metrics && (metrics.total_publications > 0 || metrics.total_faculty > 0)

  return (
    <div className="space-y-6">
      {/* Institutional Header Banner */}
      <div className="bg-gradient-to-r from-[#0B1528] via-[#0E2042] to-[#122A56] rounded-xl p-6 text-white shadow-md border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-widest bg-red-600/30 text-red-300 border border-red-500/40 px-2 py-0.5 rounded font-bold">
                Institutional Analytics
              </span>
              <span className="text-xs text-slate-300">KLE Technological University</span>
            </div>
            <h1 className="text-2xl font-extrabold tracking-tight mt-1 text-white">
              Research Intelligence & Publication Analytics Portal
            </h1>
            <p className="text-xs text-slate-300 max-w-2xl mt-1">
              Multi-Agent publication reconciliation, Crossref/OpenAlex/Scopus/WoS indexing verification, duplicate resolution, and NIRF/NAAC academic compliance reporting.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <Link
              to="/publications/import"
              className="inline-flex items-center px-3.5 py-2 text-xs font-bold rounded-lg bg-red-600 text-white hover:bg-red-700 shadow-md shadow-red-600/20 transition-all cursor-pointer"
            >
              📥 Import Scholar CSV
            </Link>
            <Link
              to="/agents"
              className="inline-flex items-center px-3.5 py-2 text-xs font-semibold rounded-lg bg-white/10 hover:bg-white/20 text-white border border-white/20 transition-all cursor-pointer"
            >
              🤖 Trigger 7-Agent Pipeline
            </Link>
          </div>
        </div>
      </div>

      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

      {/* 7-Agent Coordination Pipeline Progress */}
      <AgentPipelineView />

      {/* 8 Core Institutional KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Faculty Members"
          value={metrics?.total_faculty ?? 0}
          icon="👨‍🏫"
          description="Registered researchers across schools"
        />
        <StatCard
          label="Total Publications"
          value={metrics?.total_publications ?? 0}
          icon="📚"
          description="Indexed scholarly works catalog"
        />
        <StatCard
          label="Total Citations"
          value={metrics?.total_citations ?? 0}
          icon="📈"
          description="Cumulative scholarly citations"
        />
        <StatCard
          label="Avg Citations / Pub"
          value={metrics?.avg_citations_per_pub ?? 0}
          icon="⚡"
          description="Institutional research impact factor"
        />
        <div className="relative group">
          <StatCard
            label="Institutional h-index"
            value={metrics?.h_index ?? 0}
            icon="🎯"
            description="h papers with ≥ h citations"
          />
          <div className="absolute top-2 right-2 text-slate-400 hover:text-slate-600 cursor-help text-xs" title="Hirsch index (h-index): The maximum value h such that the institution has published at least h papers that have each been cited at least h times. Computed deterministically via Python.">
            ℹ️
          </div>
        </div>
        <StatCard
          label="Verified Publications"
          value={metrics?.verified_publications ?? 0}
          icon="✅"
          description="Validated in Scopus or WoS"
          color="emerald"
        />
        <StatCard
          label="Requires Review"
          value={metrics?.requires_review_publications ?? 0}
          icon="⚠️"
          description="Unverified or conflicting metadata"
          color="amber"
        />
        <StatCard
          label="Duplicate Candidates"
          value={metrics?.duplicate_candidates ?? 0}
          icon="🔍"
          description="Fuzzy matching pending merge approval"
          color="red"
        />
      </div>

      {/* Charts Grid or Genuine Empty State */}
      {!hasData ? (
        <Card>
          <EmptyState
            title="Institutional Research Database is Empty"
            description="No faculty publication records have been imported yet. Use the Scholar CSV Ingest or configure API connectors to harvest scholarly profiles."
            actionLabel="Import Scholar CSV"
            onAction={() => (window.location.href = '/publications/import')}
          />
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Row 1: Publications by Year & Citations by Year */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card title="Publications by Year" subtitle="Annual publication volume indexed in portal">
              <PublicationsByYearChart data={pubYears} />
            </Card>

            <Card title="Citations by Year" subtitle="Yearly citation trends and growth impact">
              <CitationTrendChart data={citeTrends} />
            </Card>
          </div>

          {/* Row 2: Department-wise comparison & Verification distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card title="Department-wise Research Comparison" subtitle="Publications vs Citations across Schools & Departments">
                <DepartmentComparisonChart data={deptComp} />
              </Card>
            </div>

            <div className="lg:col-span-1">
              <Card title="Verification Distribution" subtitle="Scopus / Web of Science Indexing Status">
                <VerificationDistributionChart data={verifDist} />
              </Card>
            </div>
          </div>

          {/* Row 3: Research Productivity Trends (Dual-Axis) */}
          <Card title="Institutional Research Productivity Trends" subtitle="Correlation of annual publication output with received citations">
            <ProductivityTrendsChart publications={pubYears} citations={citeTrends} />
          </Card>
        </div>
      )}
    </div>
  )
}
