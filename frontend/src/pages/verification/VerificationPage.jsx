import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { verificationApi } from '../../api/verification'
import { getPublications } from '../../api/publications'
import Card from '../../components/ui/Card'
import Table from '../../components/ui/Table'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Modal from '../../components/ui/Modal'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import Alert from '../../components/ui/Alert'
import Input from '../../components/ui/Input'
import { useAuthStore } from '../../store/authStore'

export default function VerificationPage() {
  const { user } = useAuthStore()
  const [publications, setPublications] = useState([])
  const [activeTab, setActiveTab] = useState('') // '' (all) | 'verified' | 'partially_verified' | 'requires_review' | 'unverified'
  const [loading, setLoading] = useState(true)

  // Audit Evidence Modal State
  const [selectedPub, setSelectedPub] = useState(null)
  const [verifRecord, setVerifRecord] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [modalLoading, setModalLoading] = useState(false)
  const [scopusCheck, setScopusCheck] = useState(false)
  const [wosCheck, setWosCheck] = useState(false)
  const [auditNotes, setAuditNotes] = useState('')
  const [evidenceUrl, setEvidenceUrl] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [feedback, setFeedback] = useState(null)

  const loadPublications = async () => {
    setLoading(true)
    try {
      const data = await getPublications({
        status_filter: activeTab || undefined,
        limit: 100,
      })
      setPublications(data || [])
    } catch (err) {
      console.error('Failed to load publications for verification:', err)
      setPublications([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPublications()
  }, [activeTab])

  const openAuditModal = async (pub) => {
    setSelectedPub(pub)
    setModalOpen(true)
    setModalLoading(true)
    setFeedback(null)

    try {
      const { data } = await verificationApi.getVerification(pub.id)
      setVerifRecord(data)
      setScopusCheck(Boolean(data?.scopus_verified))
      setWosCheck(Boolean(data?.wos_verified))
      setAuditNotes(data?.verification_evidence?.notes || '')
      setEvidenceUrl(data?.verification_evidence?.evidence_url || '')
    } catch {
      // No verification record yet
      setVerifRecord(null)
      setScopusCheck(false)
      setWosCheck(false)
      setAuditNotes('')
      setEvidenceUrl('')
    } finally {
      setModalLoading(false)
    }
  }

  const handleSubmitAudit = async (e) => {
    e.preventDefault()
    if (!selectedPub) return
    setSubmitting(true)
    setFeedback(null)

    try {
      await verificationApi.submitManualVerification(selectedPub.id, {
        scopus_verified: scopusCheck,
        wos_verified: wosCheck,
        notes: auditNotes || 'Audited by institutional research coordinator.',
        evidence_url: evidenceUrl || undefined,
      })
      setFeedback({
        type: 'success',
        message: 'Verification status updated successfully with manual audit evidence.',
      })
      setModalOpen(false)
      loadPublications()
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to submit verification audit.',
      })
    } finally {
      setSubmitting(false)
    }
  }

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
          {row.doi && (
            <div className="text-[11px] font-mono text-blue-600 mt-0.5">
              DOI: {row.doi}
            </div>
          )}
        </div>
      ),
    },
    {
      header: 'Year',
      accessor: 'publication_year',
      className: 'w-16 font-semibold text-slate-800 text-center',
    },
    {
      header: 'Scopus Verification',
      className: 'w-36 text-center',
      render: (row) =>
        row.verification?.scopus_verified ? (
          <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full inline-flex items-center gap-1">
            ✓ Scopus Indexed
          </span>
        ) : (
          <span className="text-xs text-slate-400">Not Indexed</span>
        ),
    },
    {
      header: 'WoS Verification',
      className: 'w-36 text-center',
      render: (row) =>
        row.verification?.wos_verified ? (
          <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full inline-flex items-center gap-1">
            ✓ WoS Indexed
          </span>
        ) : (
          <span className="text-xs text-slate-400">Not Indexed</span>
        ),
    },
    {
      header: 'Status',
      accessor: 'status',
      className: 'w-36 text-center',
      render: (row) => <Badge status={row.status} />,
    },
    {
      header: 'Evidence & Audit',
      className: 'w-32 text-right',
      render: (row) => (
        <button
          onClick={() => openAuditModal(row)}
          className="px-2.5 py-1 text-xs font-semibold rounded bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 transition-colors cursor-pointer"
        >
          View Evidence →
        </button>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
            Scholarly Verification & Audit Center
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Scopus and Web of Science indexation auditing. Never fabricate claims without official evidence or manual reviewer sign-off.
          </p>
        </div>

        <Link
          to="/agents"
          className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-lg bg-blue-700 text-white hover:bg-blue-800 transition-colors shadow-xs"
        >
          <span>🤖</span> Run Scopus / WoS Verification Agent
        </Link>
      </div>

      {feedback && (
        <Alert
          type={feedback.type}
          message={feedback.message}
          onClose={() => setFeedback(null)}
        />
      )}

      {/* Filter Tabs */}
      <div className="flex border-b border-slate-200 gap-4 text-xs font-semibold overflow-x-auto">
        {[
          { label: 'All Records', value: '' },
          { label: 'Verified (Scopus / WoS)', value: 'verified' },
          { label: 'Partially Verified', value: 'partially_verified' },
          { label: 'Requires Review', value: 'requires_review' },
          { label: 'Unverified', value: 'unverified' },
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => setActiveTab(tab.value)}
            className={`pb-2.5 px-1 border-b-2 whitespace-nowrap cursor-pointer transition-colors ${
              activeTab === tab.value
                ? 'border-blue-700 text-blue-700 font-bold'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Table */}
      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center">
          <Spinner size="lg" />
          <p className="text-xs text-slate-500 mt-2">Loading verification statuses...</p>
        </div>
      ) : publications.length === 0 ? (
        <Card>
          <EmptyState
            icon="🛡️"
            title="No Records Found"
            description="No publications match the selected verification status. Run the Verification Agent to evaluate unverified items."
          />
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <Table columns={columns} data={publications} />
        </Card>
      )}

      {/* Audit & Evidence Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Verification Evidence & Manual Audit"
        maxWidth="max-w-2xl"
      >
        {modalLoading ? (
          <div className="py-12 flex justify-center">
            <Spinner />
          </div>
        ) : selectedPub ? (
          <form onSubmit={handleSubmitAudit} className="space-y-4">
            <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
              <h4 className="text-xs font-bold text-slate-900 leading-snug">
                {selectedPub.title}
              </h4>
              <p className="text-[11px] font-mono text-slate-600 mt-1">
                DOI: {selectedPub.doi || 'None'} • Year: {selectedPub.publication_year}
              </p>
            </div>

            {/* Existing Evidence Display */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Ingested Verification Evidence (Agent / API Payload):
              </label>
              <pre className="bg-slate-900 text-slate-100 p-3 rounded-lg text-[11px] font-mono overflow-x-auto max-h-40">
                {verifRecord?.verification_evidence
                  ? JSON.stringify(verifRecord.verification_evidence, null, 2)
                  : 'No raw API evidence registered yet.'}
              </pre>
            </div>

            {/* Verification Toggles */}
            <div className="grid grid-cols-2 gap-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
              <label className="flex items-center gap-2 text-xs font-semibold text-slate-800 cursor-pointer">
                <input
                  type="checkbox"
                  checked={scopusCheck}
                  onChange={(e) => setScopusCheck(e.target.checked)}
                  className="rounded text-blue-600 w-4 h-4"
                />
                <span>Scopus Verified</span>
              </label>

              <label className="flex items-center gap-2 text-xs font-semibold text-slate-800 cursor-pointer">
                <input
                  type="checkbox"
                  checked={wosCheck}
                  onChange={(e) => setWosCheck(e.target.checked)}
                  className="rounded text-blue-600 w-4 h-4"
                />
                <span>Web of Science Verified</span>
              </label>
            </div>

            {/* Evidence URL */}
            <Input
              label="External Evidence URL (Elsevier / Clarivate Link)"
              type="url"
              value={evidenceUrl}
              onChange={(e) => setEvidenceUrl(e.target.value)}
              placeholder="https://www.scopus.com/record/display.uri?eid=..."
            />

            {/* Notes */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Reviewer Audit Notes *
              </label>
              <textarea
                rows={3}
                value={auditNotes}
                onChange={(e) => setAuditNotes(e.target.value)}
                required
                placeholder="State the verification methodology or citation confirmation details..."
                className="w-full text-xs p-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={() => setModalOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                size="sm"
                className="bg-blue-700 hover:bg-blue-800 font-bold"
                isLoading={submitting}
              >
                Save Manual Verification Audit
              </Button>
            </div>
          </form>
        ) : null}
      </Modal>
    </div>
  )
}
