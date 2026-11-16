import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6 text-center">
      <span className="text-6xl mb-4">🔍</span>
      <h1 className="text-3xl font-bold text-slate-900">404 - Page Not Found</h1>
      <p className="text-sm text-slate-500 mt-2 max-w-md">
        The research portal resource you requested could not be located.
      </p>
      <Link
        to="/dashboard"
        className="mt-6 px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors shadow-sm"
      >
        Return to Dashboard
      </Link>
    </div>
  )
}
