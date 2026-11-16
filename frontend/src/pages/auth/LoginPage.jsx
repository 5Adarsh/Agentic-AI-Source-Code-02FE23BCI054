import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { authApi } from '../../api/auth'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Alert from '../../components/ui/Alert'

export default function LoginPage() {
  const [email, setEmail] = useState('admin@university.edu')
  const [password, setPassword] = useState('Admin@123456')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const response = await authApi.login({ email, password })
      useAuthStore.getState().setTokens(response.access_token, response.refresh_token)
      
      // Fetch authenticated user profile
      let userProfile
      try {
        userProfile = await authApi.getCurrentUser()
      } catch {
        userProfile = {
          email,
          role: 'admin',
          full_name: email.split('@')[0],
        }
      }

      setAuth(userProfile, response.access_token, response.refresh_token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.')
    } finally {
      setLoading(false)
    }
  }

  const fillCredentials = (userEmail, userPass) => {
    setEmail(userEmail)
    setPassword(userPass)
  }

  return (
    <div className="min-h-screen bg-[#070F1E] flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background Decorative Grid */}
      <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-40"></div>
      
      {/* Subtle Red/Blue Ambient Glow */}
      <div className="absolute top-1/4 -left-20 w-96 h-96 bg-red-600/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-blue-600/15 rounded-full blur-3xl pointer-events-none"></div>

      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 border border-slate-200 relative z-10">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-red-600 to-red-800 text-white flex items-center justify-center text-2xl shadow-lg shadow-red-600/20 border-2 border-red-500/40">
            🏛️
          </div>
          <h2 className="text-xl font-extrabold text-slate-900 mt-3 tracking-tight">
            KLE Technological University
          </h2>
          <p className="text-xs font-semibold text-red-600 uppercase tracking-wider mt-0.5">
            Research Intelligence & Publication Analytics Portal
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Agentic AI Worklets Compendium (Project 14)
          </p>
        </div>

        {error && (
          <div className="mb-4">
            <Alert type="error" message={error} onClose={() => setError(null)} />
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Institutional Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin@university.edu"
            required
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />

          <div className="pt-2">
            <Button type="submit" className="w-full bg-blue-700 hover:bg-blue-800 text-white font-semibold py-2.5 shadow-md" isLoading={loading}>
              Sign In to Portal
            </Button>
          </div>
        </form>

        {/* Demo Fast-Fill Buttons */}
        <div className="mt-6 pt-5 border-t border-slate-100">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2.5 text-center">
            Institutional Demo Accounts
          </p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => fillCredentials('admin@university.edu', 'Admin@123456')}
              className="px-2.5 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-left transition-colors cursor-pointer"
            >
              <div className="font-bold text-slate-800">Administrator</div>
              <div className="text-[10px] text-slate-500 truncate">admin@university.edu</div>
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('vc@kletech.ac.in', 'Faculty@123456')}
              className="px-2.5 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-left transition-colors cursor-pointer"
            >
              <div className="font-bold text-slate-800">Faculty (VC)</div>
              <div className="text-[10px] text-slate-500 truncate">vc@kletech.ac.in</div>
            </button>
          </div>
        </div>

        <div className="mt-5 text-center text-[11px] text-slate-400">
          Role-Based Access Control • Administrator, Research Coordinator, Faculty
        </div>
      </div>
    </div>
  )
}
