import { NavLink } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: '📊', desc: 'KPIs & Research Overview' },
  { name: 'Faculty Management', path: '/faculty', icon: '👨‍🏫', desc: 'Profiles & Identifiers' },
  { name: 'Publications', path: '/publications', icon: '📚', desc: 'Catalog & CSV Ingest' },
  { name: 'Duplicate Management', path: '/duplicates', icon: '🔍', desc: 'Fuzzy Matching & Merges' },
  { name: 'Verification Center', path: '/verification', icon: '🛡️', desc: 'Scopus / WoS Auditing' },
  { name: 'Citation Analytics', path: '/analytics', icon: '📈', desc: 'h-index & Impact Metrics' },
  { name: 'AI Agent Monitoring', path: '/agents', icon: '🤖', desc: '7-Agent Pipeline' },
  { name: 'NIRF / NAAC Reporting', path: '/reports', icon: '📋', desc: 'Compliance & Exports' },
  { name: 'Settings & Integrations', path: '/settings', icon: '⚙️', desc: 'API Keys & System Controls', roles: ['admin', 'research_coordinator'] },
]

export default function Sidebar() {
  const { user } = useAuthStore()

  return (
    <aside className="w-72 bg-[#0B1528] text-slate-100 flex flex-col min-h-screen border-r border-slate-800 shrink-0">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 bg-[#08101E]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-600 to-red-800 flex items-center justify-center text-white font-bold text-lg shadow-md border border-red-500/30">
            🏛️
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h1 className="font-extrabold text-sm tracking-wide text-white uppercase">KLE Tech</h1>
              <span className="text-[10px] bg-red-600/30 text-red-300 border border-red-500/40 px-1.5 py-0.2 rounded font-semibold uppercase">RIAP</span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Research Intelligence Portal</p>
          </div>
        </div>
      </div>

      {/* Nav List */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 pt-2 pb-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
          Core Worklets
        </div>
        {navItems.map((item) => {
          if (item.roles && (!user || !item.roles.includes(user.role))) {
            return null
          }
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150 ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-600/20 border-l-4 border-red-500'
                    : 'text-slate-300 hover:bg-slate-800/70 hover:text-white'
                }`
              }
            >
              <span className="text-lg opacity-90 group-hover:scale-110 transition-transform">{item.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="truncate font-medium">{item.name}</div>
                <div className="text-[11px] text-slate-400 truncate opacity-80">{item.desc}</div>
              </div>
            </NavLink>
          )
        })}
      </nav>

      {/* Institutional Footer */}
      <div className="p-4 border-t border-slate-800/80 bg-[#08101E] text-xs text-slate-400">
        <div className="flex items-center justify-between text-[11px] mb-1">
          <span className="text-slate-300 font-semibold">Project 14 Architecture</span>
          <span className="text-emerald-400 font-mono text-[10px]">● Online</span>
        </div>
        <p className="text-[11px] text-slate-400">7 Multi-Agent Worklets Compendium</p>
      </div>
    </aside>
  )
}
