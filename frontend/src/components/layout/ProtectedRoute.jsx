import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

export default function ProtectedRoute() {
  const { isAuthenticated, token } = useAuthStore()
  const location = useLocation()

  if (!isAuthenticated && !token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}
