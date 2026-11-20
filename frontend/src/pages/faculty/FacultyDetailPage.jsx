import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getFacultyById, getFacultyPublications } from '../../api/faculty'
import Card from '../../components/ui/Card'
import Table from '../../components/ui/Table'
import Badge from '../../components/ui/Badge'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import StatCard from '../../components/ui/StatCard'

export default function FacultyDetailPage() {
  const { id } = useParams()
  const [faculty, setFaculty] = useState(null)
  const [publications, setPublications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const facData = await getFacultyById(id)
        setFaculty(facData)
        try {
          const pubsData = await getFacultyPublications(id)
          setPublications(pubsData || [])
        } catch (e) {
          console.warn('Could not load faculty publications:', e)
          setPublications([])
        }
      } catch (err) {
        console.error('Error loading faculty profile:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) return <Spinner size="lg" className="py-24" />

  if (!faculty) {
    return (
      <EmptyState
        title="Faculty Profile Not Found"
        description="The requested faculty record does not exist or has been removed."
      />
    )
  }

  // Calculate individual metrics deterministically
  const totalPubs = publications.length
  const totalCites = publications.reduce((acc, p) => acc + (p.total_citations || 0), 0)
  
  // h-index
  const sortedCites = publications.map((p) => p.total_citations || 0).sort((a, b) => b - a)
  let hIndex = 0
  for (let i = 0; i < sortedCites.length; i++) {
    if (sortedCites[i] >= i + 1) {
      hIndex = i + 1
    } else {
      break
    }
  }

  // i10-index
  const i10Index = sortedCites.filter((c) => c >= 10).length

  const columns = [
    {
      header: 'Publication Title',
      accessor: 'title',
      render: (p) => (
        <div>
          <Link to={`/publications/${p.id}`} className="font-semibold text-blue-700 hover:underline">
            {p.title}
          </Link>
          {p.doi && (
            <div className="text-[11px] font-mono text-slate-500 mt-0.5">
              DOI: <a href={`https://doi.org/${p.doi}`} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{p.doi}</a>
            </div>
          )}
        </div>
      ),
    },
    { header: 'Year', accessor: 'publication_year', className: 'w-20' },
    {
      header: 'Type',
      accessor: 'publication_type',
      className: 'w-28 capitalize',
    },
    {
      header: 'Citations',
      accessor: 'total_citations',
      className: 'w-24 font-bold text-slate-800 text-right',
    },
    {
      header: 'Status',
      accessor: 'status',
      className: 'w-36 text-center',
      render: (p) => <Badge status={p.status} />,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Faculty Profile Banner */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-slate-900 text-white flex items-center justify-center font-extrabold text-2xl border-2 border-red-500">
            {faculty.full_name?.[0]?.toUpperCase() || 'F'}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900">{faculty.full_name}</h1>
              <span className={`text-[11px] px-2 py-0.5 rounded-full font-semibold ${faculty.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'}`}>
                {faculty.is_active ? 'Active Faculty' : 'Inactive'}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              <span className="font-medium text-slate-700">{faculty.designation}</span> • Institutional ID: <span className="font-mono text-slate-700">{faculty.faculty_id}</span> • {faculty.email}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Link
            to={`/faculty/${id}/edit`}
            className="px-3.5 py-1.5 text-xs font-semibold rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors"
          >
            Edit Profile
          </Link>
          <Link
            to="/publications/import"
            className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-blue-700 text-white hover:bg-blue-800 transition-colors shadow-xs"
          >
            Import Publications
          </Link>
        </div>
      </div>

      {/* Individual Research Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Publications" value={totalPubs} icon="📚" description="Reconciled scholarly works" />
        <StatCard label="Citations" value={totalCites} icon="📈" description="Cumulative citations count" />
        <StatCard label="Faculty h-index" value={hIndex} icon="🎯" description="Hirsch impact metric" />
        <StatCard label="i10-Index" value={i10Index} icon="⭐" description="Papers with ≥ 10 citations" />
      </div>

      {/* Scholarly Profile Identifiers */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="ORCID ID" className="border-t-4 border-t-emerald-600">
          {faculty.orcid ? (
            <div className="space-y-1 mt-1">
              <a
                href={faculty.orcid.startsWith('http') ? faculty.orcid : `https://orcid.org/${faculty.orcid.trim()}`}
                target="_blank"
                rel="noreferrer"
                className="font-mono text-xs text-emerald-600 font-bold hover:underline flex items-center gap-1.5"
              >
                <span>🔗</span> {faculty.orcid.replace(/^https?:\/\/orcid\.org\//, '')}
              </a>
              <span className="inline-block text-[10px] text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded font-medium">
                ✓ Verified ORCID Registry
              </span>
            </div>
          ) : (
            <p className="text-xs text-slate-400 mt-1 italic">Not linked</p>
          )}
        </Card>

        <Card title="Google Scholar" className="border-t-4 border-t-blue-600">
          {faculty.google_scholar_id || faculty.full_name ? (
            <div className="space-y-1 mt-1">
              <a
                href={
                  faculty.google_scholar_id && faculty.google_scholar_id.length === 12
                    ? `https://scholar.google.com/citations?user=${faculty.google_scholar_id}`
                    : `https://scholar.google.com/scholar?q=author:%22${encodeURIComponent(faculty.full_name.replace(/^(Dr\.|Prof\.)\s*/, '').trim())}%22+KLE`
                }
                target="_blank"
                rel="noreferrer"
                className="font-mono text-xs text-blue-600 font-bold hover:underline flex items-center gap-1.5"
              >
                <span>🔗</span> {faculty.google_scholar_id || 'Scholar Search'}
              </a>
              <span className="inline-block text-[10px] text-blue-800 bg-blue-50 px-2 py-0.5 rounded font-medium">
                Indexed Publications
              </span>
            </div>
          ) : (
            <p className="text-xs text-slate-400 mt-1 italic">Not linked</p>
          )}
        </Card>

        <Card title="Scopus Author ID" className="border-t-4 border-t-amber-600">
          {faculty.scopus_author_id ? (
            <span className="font-mono text-xs text-amber-700 font-bold block mt-1">
              {faculty.scopus_author_id}
            </span>
          ) : (
            <p className="text-xs text-slate-400 mt-1 italic">Not linked</p>
          )}
        </Card>

        <Card title="Web of Science ID" className="border-t-4 border-t-purple-600">
          {faculty.wos_researcher_id ? (
            <span className="font-mono text-xs text-purple-700 font-bold block mt-1">
              {faculty.wos_researcher_id}
            </span>
          ) : (
            <p className="text-xs text-slate-400 mt-1 italic">Not linked</p>
          )}
        </Card>
      </div>

      {/* Publications Table */}
      <Card
        title={`Scholarly Publications (${publications.length})`}
        subtitle="Catalog reconciled and verified across Crossref, OpenAlex, Scopus & Web of Science"
      >
        {publications.length === 0 ? (
          <EmptyState
            icon="📚"
            title="No Publications Associated"
            description="No publications are currently linked to this faculty profile. Upload a Scholar CSV or run the Scholar Harvest Agent."
            actionLabel="Import Scholar CSV"
            onAction={() => (window.location.href = '/publications/import')}
          />
        ) : (
          <Table columns={columns} data={publications} />
        )}
      </Card>
    </div>
  )
}
