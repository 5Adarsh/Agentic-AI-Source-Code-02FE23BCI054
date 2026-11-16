import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

export default function Topbar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 sticky top-0 z-20 shadow-xs">
      <div className="flex items-center gap-3 text-sm">
        <span className="font-bold text-slate-900 tracking-tight text-base">
          KLE Technological University
        </span>
        <span className="text-slate-300">|</span>
        <span className="text-slate-600 text-xs font-medium">Research Intelligence & Publication Analytics Portal</span>
        <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] px-2 py-0.5 rounded-full font-semibold flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          Connected
        </span>
      </div>

      <div className="flex items-center gap-4">
        {user && (
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-xs font-bold text-slate-800">{user.full_name || user.email}</p>
              <div className="flex items-center justify-end gap-1.5 mt-0.5">
                <span className="text-[10px] uppercase tracking-wider bg-slate-100 text-slate-600 border border-slate-200 font-semibold px-1.5 py-0.5 rounded">
                  {user.role?.replace('_', ' ')}
                </span>
              </div>
            </div>
            <div className="w-9 h-9 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold shadow-xs border-2 border-red-500">
              {(user.full_name || user.email || 'U')[0].toUpperCase()}
            </div>
          </div>
        )}

        <button
          onClick={handleLogout}
          className="text-xs font-semibold text-slate-600 hover:text-red-700 px-3 py-1.5 border border-slate-300 rounded-lg hover:border-red-300 hover:bg-red-50/50 transition-colors cursor-pointer"
        >
          Sign Out
        </button>
      </div>
    </header>
  )
}
