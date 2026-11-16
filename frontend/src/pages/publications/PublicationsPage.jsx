import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { getPublications } from '../../api/publications'
import Card from '../../components/ui/Card'
import Table from '../../components/ui/Table'
import Badge from '../../components/ui/Badge'
import EmptyState from '../../components/ui/EmptyState'
import Spinner from '../../components/ui/Spinner'
import SearchInput from '../../components/ui/SearchInput'
import Select from '../../components/ui/Select'
import Button from '../../components/ui/Button'
import Pagination from '../../components/ui/Pagination'

export default function PublicationsPage() {
  const [publications, setPublications] = useState([])
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [yearFilter, setYearFilter] = useState('')
  const [sortField, setSortField] = useState('year_desc')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [loading, setLoading] = useState(true)

  const loadData = async () => {
    setLoading(true)
    try {
      const data = await getPublications({
        status_filter: statusFilter || undefined,
        pub_type: typeFilter || undefined,
        year: yearFilter ? parseInt(yearFilter, 10) : undefined,
        limit: 100,
      })
      setPublications(data || [])
    } catch (err) {
      console.error('Failed to load publications:', err)
      setPublications([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [statusFilter, typeFilter, yearFilter])

  // Filter and sort
  const filteredAndSorted = useMemo(() => {
    let result = [...publications]

    // Search query (title, doi, authors)
    if (search.trim()) {
      const q = search.toLowerCase()
      result = result.filter(
        (p) =>
          p.title?.toLowerCase().includes(q) ||
          p.doi?.toLowerCase().includes(q) ||
          p.authors?.some((a) => a.author_name?.toLowerCase().includes(q))
      )
    }

    // Sorting
    result.sort((a, b) => {
      if (sortField === 'year_desc') return (b.publication_year || 0) - (a.publication_year || 0)
      if (sortField === 'year_asc') return (a.publication_year || 0) - (b.publication_year || 0)
      if (sortField === 'citations_desc') return (b.total_citations || 0) - (a.total_citations || 0)
      if (sortField === 'citations_asc') return (a.total_citations || 0) - (b.total_citations || 0)
      if (sortField === 'title_asc') return (a.title || '').localeCompare(b.title || '')
      return 0
    })

    return result
  }, [publications, search, sortField])

  // Pagination slice
  const totalPages = Math.ceil(filteredAndSorted.length / pageSize) || 1
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize
    return filteredAndSorted.slice(start, start + pageSize)
  }, [filteredAndSorted, currentPage, pageSize])

  // CSV Export utility
  const exportToCSV = () => {
    if (!filteredAndSorted.length) return
    const headers = [
      'Title',
      'DOI',
      'Year',
      'Type',
      'Citations',
      'Authors',
      'Scopus Verified',
      'WoS Verified',
      'Status',
    ]

    const rows = filteredAndSorted.map((p) => [
      `"${(p.title || '').replace(/"/g, '""')}"`,
      `"${p.doi || ''}"`,
      p.publication_year || '',
      p.publication_type || '',
      p.total_citations ?? 0,
      `"${p.authors?.map((a) => a.author_name).join('; ') || ''}"`,
      p.verification?.scopus_verified ? 'Yes' : 'No',
      p.verification?.wos_verified ? 'Yes' : 'No',
      p.status || '',
    ])

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `KLE_Publications_Export_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // Extract available years for filter dropdown
  const availableYears = useMemo(() => {
    const years = Array.from(new Set(publications.map((p) => p.publication_year).filter(Boolean)))
    return years.sort((a, b) => b - a)
  }, [publications])

  const columns = [
    {
      header: 'Publication Title & DOI',
      accessor: 'title',
      className: 'min-w-[280px]',
      render: (row) => (
        <div>
          <Link
            to={`/publications/${row.id}`}
            className="font-bold text-slate-900 hover:text-blue-700 leading-snug line-clamp-2"
          >
            {row.title}
          </Link>
          <div className="flex items-center gap-2 mt-1">
            {row.doi ? (
              <a
                href={`https://doi.org/${row.doi}`}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] font-mono text-blue-600 hover:underline flex items-center gap-0.5"
              >
                <span>DOI:</span> {row.doi}
              </a>
            ) : (
              <span className="text-[11px] font-mono text-slate-400">No DOI</span>
            )}
          </div>
        </div>
      ),
    },
    {
      header: 'Authors & Faculty',
      accessor: 'authors',
      className: 'min-w-[180px]',
      render: (row) => {
        const authors = row.authors || []
        if (!authors.length) return <span className="text-xs text-slate-400 italic">Unknown</span>
        return (
          <div className="text-xs text-slate-700">
            <span className="font-medium text-slate-900">{authors[0]?.author_name}</span>
            {authors.length > 1 && (
              <span className="text-slate-500"> +{authors.length - 1} more</span>
            )}
          </div>
        )
      },
    },
    {
      header: 'Year',
      accessor: 'publication_year',
      className: 'w-16 font-semibold text-slate-800 text-center',
      render: (row) => row.publication_year || '—',
    },
    {
      header: 'Type',
      accessor: 'publication_type',
      className: 'w-24 capitalize text-xs text-slate-600',
      render: (row) => (
        <span className="px-2 py-0.5 bg-slate-100 rounded text-[11px] font-medium border border-slate-200">
          {row.publication_type?.replace('_', ' ') || 'Journal'}
        </span>
      ),
    },
    {
      header: 'Citations',
      accessor: 'total_citations',
      className: 'w-20 font-bold text-slate-900 text-right',
      render: (row) => <span className="font-mono">{row.total_citations ?? 0}</span>,
    },
    {
      header: 'Sources',
      accessor: 'sources',
      className: 'w-28 text-center',
      render: (row) => {
        const hasScholar = row.sources?.some((s) => s.source_name === 'google_scholar')
        return (
          <div className="flex items-center justify-center gap-1">
            {hasScholar ? (
              <span
                className="text-[10px] font-bold px-1.5 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 rounded"
                title="Google Scholar harvest record linked"
              >
                Scholar
              </span>
            ) : (
              <span className="text-[10px] text-slate-400">—</span>
            )}
          </div>
        )
      },
    },
    {
      header: 'Scopus',
      accessor: 'scopus',
      className: 'w-20 text-center',
      render: (row) =>
        row.verification?.scopus_verified ? (
          <span className="inline-flex items-center text-xs font-bold text-emerald-600 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded">
            ✓ Yes
          </span>
        ) : (
          <span className="inline-flex items-center text-xs text-slate-400">✗ No</span>
        ),
    },
    {
      header: 'WoS',
      accessor: 'wos',
      className: 'w-20 text-center',
      render: (row) =>
        row.verification?.wos_verified ? (
          <span className="inline-flex items-center text-xs font-bold text-emerald-600 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded">
            ✓ Yes
          </span>
        ) : (
          <span className="inline-flex items-center text-xs text-slate-400">✗ No</span>
        ),
    },
    {
      header: 'Verification Status',
      accessor: 'status',
      className: 'w-36 text-center',
      render: (row) => <Badge status={row.status} />,
    },
    {
      header: 'Actions',
      className: 'w-24 text-right',
      render: (row) => (
        <Link
          to={`/publications/${row.id}`}
          className="text-xs font-semibold text-blue-700 hover:text-blue-900 hover:underline"
        >
          View & Audit
        </Link>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header with Title and Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
            University Publications Registry
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Institutional research catalog reconciled across Scholar, Crossref, OpenAlex, Scopus & Web of Science
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={exportToCSV}
            disabled={!filteredAndSorted.length}
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-50 transition-colors shadow-xs cursor-pointer"
          >
            <span>📊</span> Export CSV
          </button>
          <Link
            to="/publications/import"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-lg bg-red-600 text-white hover:bg-red-700 shadow-sm shadow-red-600/20 transition-colors cursor-pointer"
          >
            <span>📥</span> Import Scholar CSV
          </Link>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card className="p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          <div className="lg:col-span-2">
            <SearchInput
              value={search}
              onChange={setSearch}
              placeholder="Search title, DOI, or author name..."
            />
          </div>

          <Select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setCurrentPage(1)
            }}
            options={[
              { label: 'All Verification Statuses', value: '' },
              { label: 'Verified (Scopus / WoS)', value: 'verified' },
              { label: 'Partially Verified', value: 'partially_verified' },
              { label: 'Unverified', value: 'unverified' },
              { label: 'Requires Review', value: 'requires_review' },
              { label: 'Duplicate Records', value: 'duplicate' },
            ]}
          />

          <Select
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value)
              setCurrentPage(1)
            }}
            options={[
              { label: 'All Publication Types', value: '' },
              { label: 'Journal', value: 'journal' },
              { label: 'Conference Paper', value: 'conference' },
              { label: 'Book', value: 'book' },
              { label: 'Book Chapter', value: 'book_chapter' },
              { label: 'Patent', value: 'patent' },
              { label: 'Thesis', value: 'thesis' },
            ]}
          />

          <Select
            value={sortField}
            onChange={(e) => setSortField(e.target.value)}
            options={[
              { label: 'Sort: Year (Newest First)', value: 'year_desc' },
              { label: 'Sort: Year (Oldest First)', value: 'year_asc' },
              { label: 'Sort: Citations (Highest)', value: 'citations_desc' },
              { label: 'Sort: Citations (Lowest)', value: 'citations_asc' },
              { label: 'Sort: Title (A-Z)', value: 'title_asc' },
            ]}
          />
        </div>

        {/* Filter Summary & Count */}
        <div className="flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100 mt-3">
          <span>
            Showing <strong className="text-slate-800">{paginatedData.length}</strong> of{' '}
            <strong className="text-slate-800">{filteredAndSorted.length}</strong> matching publications
          </span>
          {(search || statusFilter || typeFilter || yearFilter) && (
            <button
              onClick={() => {
                setSearch('')
                setStatusFilter('')
                setTypeFilter('')
                setYearFilter('')
              }}
              className="text-blue-600 hover:underline font-medium cursor-pointer"
            >
              Reset Filters
            </button>
          )}
        </div>
      </Card>

      {/* Main Table or Empty State */}
      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center">
          <Spinner size="lg" />
          <p className="text-xs text-slate-500 mt-2">Loading publications from database...</p>
        </div>
      ) : filteredAndSorted.length === 0 ? (
        <Card>
          <EmptyState
            icon="📚"
            title="No Publications Found"
            description={
              search || statusFilter || typeFilter
                ? 'No publications match your filter criteria. Try adjusting the search filters.'
                : 'The publications catalog is currently empty. Upload a Google Scholar CSV to harvest publication records.'
            }
            actionLabel="Import Scholar CSV"
            onAction={() => (window.location.href = '/publications/import')}
          />
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <Table columns={columns} data={paginatedData} />

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="p-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs text-slate-500">
                Page {currentPage} of {totalPages}
              </span>
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
              />
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
