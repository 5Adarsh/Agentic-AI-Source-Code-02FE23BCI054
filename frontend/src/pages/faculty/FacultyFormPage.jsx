import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createFaculty, getFacultyById, updateFaculty } from '../../api/faculty'
import Card from '../../components/ui/Card'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import Alert from '../../components/ui/Alert'

export default function FacultyFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEditing = Boolean(id)

  const [form, setForm] = useState({
    faculty_id: '',
    full_name: '',
    email: '',
    designation: 'Assistant Professor',
    orcid: '',
    google_scholar_id: '',
    scopus_author_id: '',
    wos_researcher_id: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (isEditing) {
      async function load() {
        try {
          const data = await getFacultyById(id)
          if (data) setForm(data)
        } catch (err) {
          setError('Failed to load faculty record.')
        }
      }
      load()
    }
  }, [id, isEditing])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      if (isEditing) {
        await updateFaculty(id, form)
      } else {
        await createFaculty(form)
      }
      navigate('/faculty')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save faculty profile.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900">
          {isEditing ? 'Edit Faculty Profile' : 'Register Faculty Profile'}
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Faculty identifiers will be reconciled by the Faculty Profile Agent
        </p>
      </div>

      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Full Name *"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              required
            />
            <Input
              label="Institutional Faculty ID *"
              value={form.faculty_id}
              onChange={(e) => setForm({ ...form, faculty_id: e.target.value })}
              required
            />
            <Input
              label="Institutional Email *"
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
            <Input
              label="Designation"
              value={form.designation}
              onChange={(e) => setForm({ ...form, designation: e.target.value })}
            />
          </div>

          <div className="border-t border-slate-100 pt-4 mt-4">
            <h4 className="text-xs font-semibold uppercase text-slate-500 mb-3 tracking-wider">
              Scholarly Profile Identifiers
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="ORCID (e.g. 0000-0002-1825-0097)"
                value={form.orcid || ''}
                onChange={(e) => setForm({ ...form, orcid: e.target.value })}
                placeholder="0000-0000-0000-0000"
              />
              <Input
                label="Google Scholar Profile ID"
                value={form.google_scholar_id || ''}
                onChange={(e) => setForm({ ...form, google_scholar_id: e.target.value })}
                placeholder="Scholar user ID"
              />
              <Input
                label="Scopus Author ID"
                value={form.scopus_author_id || ''}
                onChange={(e) => setForm({ ...form, scopus_author_id: e.target.value })}
                placeholder="Scopus numeric author ID"
              />
              <Input
                label="Web of Science Researcher ID"
                value={form.wos_researcher_id || ''}
                onChange={(e) => setForm({ ...form, wos_researcher_id: e.target.value })}
                placeholder="Clarivate ResearcherID"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="secondary" onClick={() => navigate('/faculty')}>
              Cancel
            </Button>
            <Button type="submit" isLoading={loading}>
              {isEditing ? 'Save Changes' : 'Create Profile'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
