import { useState, useEffect } from 'react'
import {
  getReports,
  generateReport,
  downloadPdfReport,
  downloadExcelReport,
} from '../../api/reports'
import { getDepartmentComparison, getDashboardMetrics } from '../../api/analytics'
import Card from '../../components/ui/Card'
import Table from '../../components/ui/Table'
import Button from '../../components/ui/Button'
import Select from '../../components/ui/Select'
import Input from '../../components/ui/Input'
import Badge from '../../components/ui/Badge'
import Alert from '../../components/ui/Alert'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'

export default function ReportsPage() {
  const [reports, setReports] = useState([])
  const [reportType, setReportType] = useState('nirf')
  const [academicYear, setAcademicYear] = useState('2023-2024')
  const [title, setTitle] = useState('NIRF Parameter 3 Research Metric Submission')
  const [generating, setGenerating] = useState(false)
  const [downloadingId, setDownloadingId] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [deptStats, setDeptStats] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)

  const loadData = async () => {
    try {
      const [reps, m, ds] = await Promise.all([
        getReports().catch(() => []),
        getDashboardMetrics().catch(() => null),
        getDepartmentComparison().catch(() => []),
      ])
      setReports(reps || [])
      setMetrics(m)
      setDeptStats(ds || [])
    } catch (err) {
      console.error('Failed to load reports:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleTypeChange = (newType) => {
    setReportType(newType)
    if (newType === 'nirf') {
      setTitle(`NIRF Parameter 3 (RP) Research Publication Submission (${academicYear})`)
    } else if (newType === 'naac') {
      setTitle(`NAAC Criterion 3.4 Research Publications & Awards (${academicYear})`)
    } else {
      setTitle(`Institutional Academic Research Audit Report (${academicYear})`)
    }
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    setGenerating(true)
    setError(null)
    setMessage(null)

    try {
      await generateReport({
        report_type: reportType,
        academic_year: academicYear,
        title: title || `${reportType.toUpperCase()} Research Report (${academicYear})`,
      })
      setMessage(`Report '${title}' compiled successfully by Dashboard Agent. Ready for PDF and Excel export.`)
      await loadData()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate accreditation report.')
    } finally {
      setGenerating(false)
    }
  }

  const handleDownload = async (reportId, format, reportTitle) => {
    setDownloadingId(`${reportId}-${format}`)
    try {
      const safeTitle = (reportTitle || 'report').replace(/[^a-zA-Z0-9_-]/g, '_')
      if (format === 'pdf') {
        await downloadPdfReport(reportId, `${safeTitle}.pdf`)
      } else {
        await downloadExcelReport(reportId, `${safeTitle}.xlsx`)
      }
    } catch (err) {
      setError(`Failed to download ${format.toUpperCase()} export: ${err.message}`)
    } finally {
      setDownloadingId(null)
    }
  }

  const reportColumns = [
    {
      header: 'Report Title',
      accessor: 'title',
      className: 'min-w-[280px]',
      render: (r) => (
        <div>
          <span className="font-bold text-slate-900 block leading-snug">{r.title}</span>
          <span className="text-[11px] text-slate-500">
            Generated: {new Date(r.created_at).toLocaleDateString()}
          </span>
        </div>
      ),
    },
    {
      header: 'Framework',
      accessor: 'report_type',
      className: 'w-28 text-center',
      render: (r) => (
        <span className="uppercase text-[11px] font-extrabold px-2 py-0.5 rounded bg-blue-50 text-blue-800 border border-blue-200">
          {r.report_type}
        </span>
      ),
    },
    {
      header: 'Academic Year',
      accessor: 'academic_year',
      className: 'w-28 text-center font-semibold text-slate-700',
    },
    {
      header: 'Status',
      accessor: 'status',
      className: 'w-28 text-center',
      render: (r) => <Badge status={r.status} />,
    },
    {
      header: 'Official Exports',
      className: 'w-48 text-right',
      render: (r) => (
        <div className="flex items-center justify-end gap-1.5">
          <button
            onClick={() => handleDownload(r.id, 'pdf', r.title)}
            disabled={downloadingId === `${r.id}-pdf`}
            className="px-2.5 py-1 text-xs font-semibold rounded bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 transition-colors disabled:opacity-50 cursor-pointer"
          >
            {downloadingId === `${r.id}-pdf` ? 'Downloading...' : '📄 PDF'}
          </button>
          <button
            onClick={() => handleDownload(r.id, 'excel', r.title)}
            disabled={downloadingId === `${r.id}-excel`}
            className="px-2.5 py-1 text-xs font-semibold rounded bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 transition-colors disabled:opacity-50 cursor-pointer"
          >
            {downloadingId === `${r.id}-excel` ? 'Downloading...' : '📊 Excel'}
          </button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
          Accreditation & Institutional Reports (NIRF / NAAC)
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Compile certified National Institutional Ranking Framework (NIRF Parameter 3 - RP) and NAAC Criterion 3.4 submissions directly from verified publications.
        </p>
      </div>

      {message && <Alert type="success" message={message} onClose={() => setMessage(null)} />}
      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

      {/* Compliance Verification Breakdown Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-[#122A56] rounded-xl p-5 text-white shadow-md border border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-red-400 mb-3">
          NIRF & NAAC Audit Verification Integrity
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/10 p-3 rounded-lg border border-white/10">
            <span className="text-[11px] text-slate-300 block">Total Catalog Publications</span>
            <span className="text-2xl font-extrabold text-white font-mono">{metrics?.total_publications ?? 0}</span>
          </div>
          <div className="bg-white/10 p-3 rounded-lg border border-white/10">
            <span className="text-[11px] text-emerald-300 block">✓ Scopus / WoS Verified (Eligible)</span>
            <span className="text-2xl font-extrabold text-emerald-400 font-mono">{metrics?.verified_publications ?? 0}</span>
          </div>
          <div className="bg-white/10 p-3 rounded-lg border border-white/10">
            <span className="text-[11px] text-amber-300 block">⚠️ Unverified / Under Review (Excluded)</span>
            <span className="text-2xl font-extrabold text-amber-400 font-mono">{metrics?.requires_review_publications ?? 0}</span>
          </div>
          <div className="bg-white/10 p-3 rounded-lg border border-white/10">
            <span className="text-[11px] text-blue-300 block">Total Verified Citations</span>
            <span className="text-2xl font-extrabold text-blue-400 font-mono">{metrics?.total_citations ?? 0}</span>
          </div>
        </div>
      </div>

      {/* Report Generator Form */}
      <Card
        title="Generate Institutional Research Report"
        subtitle="Configure evaluation period, framework, and certified export parameters"
      >
        <form onSubmit={handleGenerate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Select
              label="Accreditation Framework *"
              value={reportType}
              onChange={(e) => handleTypeChange(e.target.value)}
              options={[
                { label: 'NIRF (Research and Professional Practice)', value: 'nirf' },
                { label: 'NAAC (Criterion 3 - Research & Citations)', value: 'naac' },
                { label: 'Institutional Research Audit', value: 'institutional' },
              ]}
            />

            <Select
              label="Evaluation Academic Year *"
              value={academicYear}
              onChange={(e) => {
                setAcademicYear(e.target.value)
                handleTypeChange(reportType)
              }}
              options={[
                { label: '2024-2025 (Current Cycle)', value: '2024-2025' },
                { label: '2023-2024', value: '2023-2024' },
                { label: '2022-2023', value: '2022-2023' },
                { label: '2021-2022', value: '2021-2022' },
                { label: '5-Year Cumulative Audit', value: '2020-2025' },
              ]}
            />

            <Input
              label="Submission Document Title *"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="pt-2 flex items-center justify-between">
            <p className="text-xs text-slate-500">
              Only records with verified indexing proofs will be included in the primary accreditation tally.
            </p>
            <Button
              type="submit"
              isLoading={generating}
              className="bg-blue-700 hover:bg-blue-800 text-white font-bold px-5"
            >
              Compile & Sign Report
            </Button>
          </div>
        </form>
      </Card>

      {/* Department Summary Table Preview */}
      {deptStats.length > 0 && (
        <Card
          title="Departmental Research Metric Summary"
          subtitle="Real-time aggregation compiled for institutional documentation"
        >
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">School / Department</th>
                  <th className="py-2.5 px-3 text-center">Faculty Count</th>
                  <th className="py-2.5 px-3 text-center">Total Publications</th>
                  <th className="py-2.5 px-3 text-center">Total Citations</th>
                  <th className="py-2.5 px-3 text-right">Avg Citations/Pub</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {deptStats.map((d, idx) => {
                  const avg = d.publications ? (d.citations / d.publications).toFixed(2) : '0.00'
                  return (
                    <tr key={idx} className="hover:bg-slate-50/70">
                      <td className="py-2 px-3 font-semibold text-slate-900">{d.department}</td>
                      <td className="py-2 px-3 text-center font-mono text-slate-700">{d.faculty_count}</td>
                      <td className="py-2 px-3 text-center font-mono font-bold text-slate-900">{d.publications}</td>
                      <td className="py-2 px-3 text-center font-mono font-bold text-blue-700">{d.citations}</td>
                      <td className="py-2 px-3 text-right font-mono text-slate-800">{avg}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Generated Reports Archive */}
      <Card
        title="Compiled Reports Archive & Download"
        subtitle="Certified PDF and structured Excel exports signed by Dashboard Agent"
      >
        {loading ? (
          <div className="py-12 flex justify-center">
            <Spinner />
          </div>
        ) : reports.length === 0 ? (
          <EmptyState
            icon="📋"
            title="No Reports Generated Yet"
            description="Use the configuration panel above to compile your first certified NIRF or NAAC institutional report."
          />
        ) : (
          <Table columns={reportColumns} data={reports} />
        )}
      </Card>
    </div>
  )
}
