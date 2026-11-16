import { useState, useEffect } from 'react'
import { systemApi } from '../../api/system'
import { usersApi } from '../../api/users'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import Modal from '../../components/ui/Modal'
import Alert from '../../components/ui/Alert'
import Spinner from '../../components/ui/Spinner'
import { useAuthStore } from '../../store/authStore'

export default function SettingsPage() {
  const { user } = useAuthStore()
  const [config, setConfig] = useState(null)
  const [usersList, setUsersList] = useState([])
  const [loading, setLoading] = useState(true)
  const [seedLoading, setSeedLoading] = useState(false)
  const [clearLoading, setClearLoading] = useState(false)
  const [feedback, setFeedback] = useState(null)

  // Add User Modal
  const [userModalOpen, setUserModalOpen] = useState(false)
  const [newEmail, setNewEmail] = useState('')
  const [newName, setNewName] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [newRole, setNewRole] = useState('faculty_member')
  const [userCreating, setUserCreating] = useState(false)

  const loadSettingsData = async () => {
    try {
      const [cfgRes, usrRes] = await Promise.all([
        systemApi.getConfigStatus().then((r) => r.data).catch(() => null),
        usersApi.getUsers().then((r) => r.data).catch(() => []),
      ])
      setConfig(cfgRes)
      setUsersList(usrRes || [])
    } catch (err) {
      console.error('Failed to load settings:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSettingsData()
  }, [])

  const handleSeedDemo = async () => {
    setSeedLoading(true)
    setFeedback(null)
    try {
      const { data } = await systemApi.seedDemo()
      setFeedback({
        type: 'success',
        message: data.message || 'Realistic institutional demo data seeded successfully.',
      })
      await loadSettingsData()
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to seed demo data.',
      })
    } finally {
      setSeedLoading(false)
    }
  }

  const handleClearDemo = async () => {
    if (!window.confirm('Are you sure you want to remove all DEMO publications and restore a pristine empty state?')) {
      return
    }
    setClearLoading(true)
    setFeedback(null)
    try {
      const { data } = await systemApi.clearDemo()
      setFeedback({
        type: 'success',
        message: data.message || 'Cleared all demo records.',
      })
      await loadSettingsData()
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to clear demo data.',
      })
    } finally {
      setClearLoading(false)
    }
  }

  const handleCreateUser = async (e) => {
    e.preventDefault()
    setUserCreating(true)
    setFeedback(null)
    try {
      await usersApi.createUser({
        email: newEmail,
        full_name: newName,
        password: newPassword,
        role: newRole,
      })
      setFeedback({
        type: 'success',
        message: `User account created successfully for ${newEmail}.`,
      })
      setUserModalOpen(false)
      setNewEmail('')
      setNewName('')
      setNewPassword('')
      await loadSettingsData()
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to create user account.',
      })
    } finally {
      setUserCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="py-24 flex justify-center">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
          System Administration & Settings
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Scholarly API connectivity status, LLM agent providers, role-based access control, and institutional data controls.
        </p>
      </div>

      {feedback && (
        <Alert
          type={feedback.type}
          message={feedback.message}
          onClose={() => setFeedback(null)}
        />
      )}

      {/* Section 1: Scholarly APIs & Integrations Connectivity */}
      <Card
        title="Scholarly APIs & External Connectors"
        subtitle="Verification against official publisher APIs and bibliographic databases"
      >
        <div className="divide-y divide-slate-100">
          {config?.integrations?.map((item, idx) => (
            <div key={idx} className="py-3.5 flex items-center justify-between">
              <div>
                <p className="text-sm font-bold text-slate-800">{item.service}</p>
                <p className="text-xs text-slate-500 mt-0.5 font-mono">{item.details}</p>
              </div>
              <span
                className={`text-xs font-bold px-2.5 py-0.5 rounded-full inline-flex items-center gap-1.5 ${
                  item.configured
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {item.configured ? '● Active' : '○ Standby / Unconfigured'}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Section 2: LLM Orchestration Provider Configuration */}
      <Card
        title="LLM Agent Configuration"
        subtitle="LangGraph multi-agent orchestration reasoning model"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="text-[11px] text-slate-500 font-semibold uppercase block">Active Provider</span>
            <span className="text-base font-bold text-slate-900 capitalize font-mono">
              {config?.llm_provider || 'Gemini'}
            </span>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="text-[11px] text-slate-500 font-semibold uppercase block">Database Engine</span>
            <span className="text-base font-bold text-slate-900 font-mono">
              {config?.database_url_type || 'PostgreSQL'}
            </span>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
            <span className="text-[11px] text-slate-500 font-semibold uppercase block">Environment</span>
            <span className="text-base font-bold text-slate-900 font-mono">
              {config?.environment || 'Development'}
            </span>
          </div>
        </div>
      </Card>

      {/* Section 3: User & Role-Based Access Management */}
      <Card
        title="User & Role-Based Access Control"
        subtitle="Manage access scopes across Administrator, Research Coordinator, and Faculty Member roles"
      >
        <div className="flex justify-between items-center mb-4">
          <p className="text-xs text-slate-500">
            Total Authorized Accounts: <strong className="text-slate-800">{usersList.length}</strong>
          </p>
          <Button
            size="sm"
            onClick={() => setUserModalOpen(true)}
            className="bg-blue-700 hover:bg-blue-800 text-xs font-bold"
          >
            + Create New User
          </Button>
        </div>

        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Full Name</th>
                <th className="py-2.5 px-3">Institutional Email</th>
                <th className="py-2.5 px-3 text-center">System Role</th>
                <th className="py-2.5 px-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {usersList.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/70">
                  <td className="py-2.5 px-3 font-semibold text-slate-900">{u.full_name}</td>
                  <td className="py-2.5 px-3 font-mono text-slate-600">{u.email}</td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 border border-slate-200 px-2 py-0.5 rounded">
                      {u.role?.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${u.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                      {u.is_active ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Section 4: Institutional Demo Controls */}
      <Card
        title="Institutional Demonstration & Testing Data Controls"
        subtitle="Seed realistic academic data modeled after KLE Technological University or restore genuine empty state"
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-600 leading-relaxed">
            By default, the platform initiates in a <strong>genuine empty state</strong> until real data is imported.
            For presentation or architectural review, you can trigger the backend seed mechanism to populate realistic departments, faculty records, publications, and verification trails.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Button
              onClick={handleSeedDemo}
              isLoading={seedLoading}
              className="bg-red-600 hover:bg-red-700 text-white font-bold text-xs"
            >
              🌱 Seed Institutional Demo Data (KLE Tech)
            </Button>

            <Button
              variant="secondary"
              onClick={handleClearDemo}
              isLoading={clearLoading}
              className="text-xs font-semibold hover:border-red-300 hover:text-red-700"
            >
              🗑️ Clear All Demo Records (Restore Empty State)
            </Button>
          </div>
        </div>
      </Card>

      {/* Create User Modal */}
      <Modal
        isOpen={userModalOpen}
        onClose={() => setUserModalOpen(false)}
        title="Register New User Account"
        maxWidth="max-w-md"
      >
        <form onSubmit={handleCreateUser} className="space-y-4">
          <Input
            label="Full Name *"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Dr. Rajeshwari Hegde"
            required
          />

          <Input
            label="Institutional Email *"
            type="email"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            placeholder="r.hegde@kletech.ac.in"
            required
          />

          <Input
            label="Initial Password *"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="••••••••"
            required
          />

          <Select
            label="Authorization Role *"
            value={newRole}
            onChange={(e) => setNewRole(e.target.value)}
            options={[
              { label: 'Faculty Member', value: 'faculty_member' },
              { label: 'Research Coordinator', value: 'research_coordinator' },
              { label: 'Administrator', value: 'admin' },
            ]}
          />

          <div className="pt-3 flex justify-end gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => setUserModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              size="sm"
              className="bg-blue-700 hover:bg-blue-800 font-bold"
              isLoading={userCreating}
            >
              Create Account
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
