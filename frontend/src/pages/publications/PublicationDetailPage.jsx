import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getPublicationById } from '../../api/publications'
import { verificationApi } from '../../api/verification'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'

export default function PublicationDetailPage() {
  const { id } = useParams()
  const [pub, setPub] = useState(null)
  const [verification, setVerification] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [pubData, verifData] = await Promise.all([
          getPublicationById(id),
          verificationApi.getVerification(id).then((r) => r.data).catch(() => null),
        ])
        setPub(pubData)
        setVerification(verifData)
      } catch (err) {
        console.error('Failed to load publication:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) return <Spinner size="lg" className="py-24" />

  if (!pub) {
    return (
      <EmptyState
        title="Publication Not Found"
        description="The requested publication record does not exist or has been removed."
        actionLabel="Back to Publications"
        onAction={() => (window.location.href = '/publications')}
      />
    )
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top Navigation & Status */}
      <div className="flex items-center justify-between">
        <Link
          to="/publications"
          className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 flex items-center gap-1.5 transition-colors"
        >
          <span>←</span> Back to Publications Registry
        </Link>
        <div className="flex items-center gap-2">
          <Badge status={pub.status} />
          <Link
            to="/verification"
            className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-700 hover:bg-blue-100 transition-colors"
          >
            🛡️ Open in Verification Center
          </Link>
        </div>
      </div>

      {/* Main Publication Header */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs">
        <div className="flex items-center gap-2 text-xs text-slate-500 mb-2">
          <span className="font-bold uppercase tracking-wider text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
            {pub.publication_type?.replace('_', ' ') || 'Journal'}
          </span>
          <span>•</span>
          <span>Year: <strong className="text-slate-800">{pub.publication_year || 'Unknown'}</strong></span>
        </div>

        <h1 className="text-xl md:text-2xl font-bold text-slate-900 leading-snug">
          {pub.title}
        </h1>

        {pub.doi && (
          <div className="mt-3 flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500">Digital Object Identifier:</span>
            <a
              href={`https://doi.org/${pub.doi}`}
              target="_blank"
              rel="noreferrer"
              className="text-xs font-mono text-blue-600 hover:underline bg-blue-50 px-2 py-0.5 rounded border border-blue-100"
            >
              https://doi.org/{pub.doi} ↗
            </a>
          </div>
        )}
      </div>

      {/* Metric Highlights */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card title="Citations Count" className="text-center">
          <p className="text-3xl font-extrabold text-slate-900 font-mono mt-1">{pub.total_citations ?? 0}</p>
          <p className="text-[11px] text-slate-400 mt-1">Cross-database citations</p>
        </Card>
        <Card title="Scopus Verified" className="text-center">
          <p className={`text-xl font-bold mt-1 ${verification?.scopus_verified ? 'text-emerald-600' : 'text-slate-400'}`}>
            {verification?.scopus_verified ? '✓ Verified' : '✗ Unverified'}
          </p>
          <p className="text-[11px] text-slate-400 mt-1 font-mono">
            {verification?.scopus_eid || 'No Scopus EID'}
          </p>
        </Card>
        <Card title="Web of Science" className="text-center">
          <p className={`text-xl font-bold mt-1 ${verification?.wos_verified ? 'text-emerald-600' : 'text-slate-400'}`}>
            {verification?.wos_verified ? '✓ Verified' : '✗ Unverified'}
          </p>
          <p className="text-[11px] text-slate-400 mt-1 font-mono">
            {verification?.wos_uid || 'No WoS UID'}
          </p>
        </Card>
        <Card title="OpenAlex / Crossref" className="text-center">
          <p className={`text-xl font-bold mt-1 ${verification?.crossref_verified ? 'text-emerald-600' : 'text-slate-400'}`}>
            {verification?.crossref_verified ? '✓ Resolved' : '✗ Unresolved'}
          </p>
          <p className="text-[11px] text-slate-400 mt-1">Bibliographic metadata</p>
        </Card>
      </div>

      {/* Abstract */}
      <Card title="Abstract Text" subtitle="Reconciled abstract from bibliographic index">
        <p className="text-sm text-slate-700 leading-relaxed">
          {pub.abstract || 'No abstract text was provided in the harvest source record.'}
        </p>
      </Card>

      {/* Authors & Co-authors */}
      <Card title="Authors & Contributors" subtitle="Affiliated institutional and external authors">
        {pub.authors?.length ? (
          <div className="divide-y divide-slate-100">
            {pub.authors.map((author, idx) => (
              <div key={author.id || idx} className="py-2.5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-slate-100 text-slate-600 font-bold text-xs flex items-center justify-center">
                    {author.author_order || idx + 1}
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{author.author_name}</p>
                    {author.is_corresponding && (
                      <span className="text-[10px] text-red-600 font-semibold uppercase">Corresponding Author</span>
                    )}
                  </div>
                </div>
                {author.faculty_id ? (
                  <Link
                    to={`/faculty/${author.faculty_id}`}
                    className="text-xs text-blue-600 hover:underline font-medium"
                  >
                    View Faculty Profile →
                  </Link>
                ) : (
                  <span className="text-xs text-slate-400">External Contributor</span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">No author records associated.</p>
        )}
      </Card>

      {/* Harvest Sources & Provenance */}
      <Card title="Harvest Provenance & Sources" subtitle="Where this publication record was ingested from">
        {pub.sources?.length ? (
          <div className="space-y-3">
            {pub.sources.map((src) => (
              <div
                key={src.id}
                className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase text-slate-800 bg-white px-2 py-0.5 rounded border border-slate-200">
                      {src.source_name?.replace('_', ' ')}
                    </span>
                    {src.is_primary && (
                      <span className="text-[10px] bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded font-semibold">
                        Primary Source
                      </span>
                    )}
                  </div>
                  {src.source_url && (
                    <a
                      href={src.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-blue-600 hover:underline block mt-1 truncate max-w-lg"
                    >
                      {src.source_url} ↗
                    </a>
                  )}
                </div>
                <div className="text-right text-[11px] text-slate-400">
                  Retrieved: {src.retrieved_at ? new Date(src.retrieved_at).toLocaleString() : 'N/A'}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">No provenance sources recorded.</p>
        )}
      </Card>
    </div>
  )
}
