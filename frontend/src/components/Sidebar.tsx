import { Link, NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  Briefcase,
  Kanban,
  Sparkles,
  LogOut,
  User,
  X,
} from 'lucide-react'
import { useAuth } from '../auth/AuthContext'

const nav = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/cvs', label: 'CV Library', icon: FileText },
  { to: '/jobs', label: 'Job Tracker', icon: Briefcase },
  { to: '/applications', label: 'Applications', icon: Kanban },
  { to: '/ai', label: 'AI Tools', icon: Sparkles },
  { to: '/profile', label: 'Profile', icon: User },
]

export function Sidebar({ onClose }: { onClose?: () => void }) {
  const { logout, user } = useAuth()

  return (
    <aside className="flex h-screen w-56 flex-col bg-slate-900 text-slate-100">
      <div className="flex items-center justify-between px-5 py-6">
        <div className="min-w-0">
          <span className="text-lg font-bold tracking-tight text-white">JobAssist</span>
          <Link to="/profile" className="block mt-1 truncate text-xs text-slate-400 hover:text-slate-200 transition-colors">
            {user?.email}
          </Link>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-2 rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white md:hidden"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onClose}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-brand-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-3 py-4">
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </aside>
  )
}
