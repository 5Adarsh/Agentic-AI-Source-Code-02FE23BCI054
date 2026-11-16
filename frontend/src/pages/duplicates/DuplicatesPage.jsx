import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { duplicatesApi } from '../../api/duplicates'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import Alert from '../../components/ui/Alert'
import { useAuthStore } from '../../store/authStore'

export default function DuplicatesPage() {
  const { user } = useAuthStore()
  const [candidates, setCandidates] = useState([])
  const [activeTab, setActiveTab] = useState('pending') // 'pending' | 'confirmed_duplicate' | 'not_duplicate'
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(null)
  const [feedback, setFeedback] = useState(null)

  const loadCandidates = async () => {
    setLoading(true)
    try {
      const { data } = await duplicatesApi.getDuplicates({
        status_filter: activeTab,
        limit: 50,
      })
      setCandidates(data || [])
    } catch (err) {
      console.error('Failed to load duplicate candidates:', err)
      setCandidates([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCandidates()
  }, [activeTab])

  const handleResolve = async (candidateId, action) => {
    setActionLoading(candidateId)
    setFeedback(null)
    try {
      await duplicatesApi.resolveDuplicate(candidateId, { action })
      setFeedback({
        type: 'success',
        message: action === 'approve'
          ? 'Duplicate confirmed. Publication records have been merged in the repository.'
          : 'Record pair marked as distinct publication entities.',
      })
      // Reload candidate list
      loadCandidates()
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to resolve duplicate candidate.',
      })
    } finally {
      setActionLoading(null)
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Title & Explanation */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
            Duplicate Detection & Merge Center
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Autonomous duplicate identification powered by DOI matching, fuzzy title similarity, and author overlap analysis.
          </p>
        </div>

        <Link
          to="/agents"
          className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-lg bg-blue-700 text-white hover:bg-blue-800 transition-colors shadow-xs"
        >
          <span>🤖</span> Run Duplicate Detection Agent
        </Link>
      </div>

      {feedback && (
        <Alert
          type={feedback.type}
          message={feedback.message}
          onClose={() => setFeedback(null)}
        />
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-200 gap-6 text-sm font-semibold">
        <button
          onClick={() => setActiveTab('pending')}
          className={`pb-3 relative transition-colors cursor-pointer ${
            activeTab === 'pending'
              ? 'text-blue-700 border-b-2 border-blue-700'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          Pending Review Candidates
        </button>
        <button
          onClick={() => setActiveTab('confirmed_duplicate')}
          className={`pb-3 relative transition-colors cursor-pointer ${
            activeTab === 'confirmed_duplicate'
              ? 'text-blue-700 border-b-2 border-blue-700'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          Merged History
        </button>
        <button
          onClick={() => setActiveTab('not_duplicate')}
          className={`pb-3 relative transition-colors cursor-pointer ${
            activeTab === 'not_duplicate'
              ? 'text-blue-700 border-b-2 border-blue-700'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          Dismissed / Not Duplicates
        </button>
      </div>

      {/* Candidates List */}
      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center">
          <Spinner size="lg" />
          <p className="text-xs text-slate-500 mt-2">Checking duplicate candidates database...</p>
        </div>
      ) : candidates.length === 0 ? (
        <Card>
          <EmptyState
            icon="✨"
            title={
              activeTab === 'pending'
                ? 'No Pending Duplicate Candidates'
                : activeTab === 'confirmed_duplicate'
                ? 'No Merge History'
                : 'No Dismissed Duplicates'
            }
            description={
              activeTab === 'pending'
                ? 'All harvested publications are unique and verified. If new publications are imported, the Duplicate Detection Agent will evaluate them.'
                : 'No records match this status.'
            }
          />
        </Card>
      ) : (
        <div className="space-y-6">
          {candidates.map((cand) => {
            const pubA = cand.publication_a
            const pubB = cand.publication_b
            const similarityPercent = Math.round(cand.similarity_score * 100)

            return (
              <div
                key={cand.id}
                className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden"
              >
                {/* Comparison Header */}
                <div className="bg-slate-50 px-6 py-3 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-600 bg-white px-2 py-0.5 rounded border border-slate-200">
                      Match Type: <strong className="text-slate-900">{cand.match_type?.replace('_', ' ')}</strong>
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-semibold text-slate-600">Similarity Confidence:</span>
                      <div className="w-28 bg-slate-200 rounded-full h-2.5 overflow-hidden">
                        <div
                          className={`h-2.5 rounded-full ${
                            similarityPercent >= 90
                              ? 'bg-red-600'
                              : similarityPercent >= 75
                              ? 'bg-amber-500'
                              : 'bg-blue-600'
                          }`}
                          style={{ width: `${similarityPercent}%` }}
                        ></div>
                      </div>
                      <span className="text-xs font-bold text-slate-900 font-mono">
                        {similarityPercent}%
                      </span>
                    </div>
                  </div>

                  <div className="text-xs text-slate-400">
                    Flagged: {new Date(cand.created_at).toLocaleDateString()}
                  </div>
                </div>

                {/* Side-by-Side Comparison Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200 p-6 gap-6">
                  {/* Record A: Existing / Canonical Candidate */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-extrabold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        Record A (Primary Candidate)
                      </span>
                      {pubA && <Badge status={pubA.status} />}
                    </div>

                    {pubA ? (
                      <>
                        <h3 className="font-bold text-slate-900 text-sm leading-snug">
                          {pubA.title}
                        </h3>
                        <div className="text-xs space-y-1 text-slate-600">
                          <div>
                            <strong className="text-slate-700">DOI:</strong>{' '}
                            {pubA.doi ? (
                              <span className="font-mono text-blue-600">{pubA.doi}</span>
                            ) : (
                              <span className="italic text-slate-400">None</span>
                            )}
                          </div>
                          <div>
                            <strong className="text-slate-700">Publication Year:</strong>{' '}
                            <span>{pubA.publication_year}</span>
                          </div>
                          <div>
                            <strong className="text-slate-700">Citations:</strong>{' '}
                            <span className="font-mono font-bold text-slate-800">
                              {pubA.total_citations}
                            </span>
                          </div>
                          <div>
                            <strong className="text-slate-700">Authors:</strong>{' '}
                            <span>
                              {pubA.authors?.map((a) => a.author_name).join(', ') || 'Unknown'}
                            </span>
                          </div>
                        </div>
                        <div className="pt-2">
                          <Link
                            to={`/publications/${pubA.id}`}
                            className="text-xs text-blue-600 hover:underline font-semibold"
                          >
                            Inspect Full Record A →
                          </Link>
                        </div>
                      </>
                    ) : (
                      <p className="text-xs text-slate-400">Publication ID: {cand.publication_a_id}</p>
                    )}
                  </div>

                  {/* Record B: Suspected Duplicate */}
                  <div className="space-y-3 pt-4 md:pt-0">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-extrabold uppercase tracking-wider text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                        Record B (Duplicate Candidate)
                      </span>
                      {pubB && <Badge status={pubB.status} />}
                    </div>

                    {pubB ? (
                      <>
                        <h3 className="font-bold text-slate-900 text-sm leading-snug">
                          {pubB.title}
                        </h3>
                        <div className="text-xs space-y-1 text-slate-600">
                          <div>
                            <strong className="text-slate-700">DOI:</strong>{' '}
                            {pubB.doi ? (
                              <span className="font-mono text-blue-600">{pubB.doi}</span>
                            ) : (
                              <span className="italic text-slate-400">None</span>
                            )}
                          </div>
                          <div>
                            <strong className="text-slate-700">Publication Year:</strong>{' '}
                            <span>{pubB.publication_year}</span>
                          </div>
                          <div>
                            <strong className="text-slate-700">Citations:</strong>{' '}
                            <span className="font-mono font-bold text-slate-800">
                              {pubB.total_citations}
                            </span>
                          </div>
                          <div>
                            <strong className="text-slate-700">Authors:</strong>{' '}
                            <span>
                              {pubB.authors?.map((a) => a.author_name).join(', ') || 'Unknown'}
                            </span>
                          </div>
                        </div>
                        <div className="pt-2">
                          <Link
                            to={`/publications/${pubB.id}`}
                            className="text-xs text-blue-600 hover:underline font-semibold"
                          >
                            Inspect Full Record B →
                          </Link>
                        </div>
                      </>
                    ) : (
                      <p className="text-xs text-slate-400">Publication ID: {cand.publication_b_id}</p>
                    )}
                  </div>
                </div>

                {/* Action Bar for Pending Review */}
                {activeTab === 'pending' && (
                  <div className="bg-slate-50/70 px-6 py-3 border-t border-slate-200 flex items-center justify-between">
                    <p className="text-xs text-slate-500">
                      Merging marks Record B as duplicate and consolidates citations under Record A.
                    </p>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        isLoading={actionLoading === cand.id}
                        onClick={() => handleResolve(cand.id, 'reject')}
                      >
                        ✗ Dismiss (Distinct Records)
                      </Button>
                      <Button
                        size="sm"
                        className="bg-red-600 hover:bg-red-700 text-white font-bold"
                        isLoading={actionLoading === cand.id}
                        onClick={() => handleResolve(cand.id, 'approve')}
                      >
                        ✓ Approve Merge
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
