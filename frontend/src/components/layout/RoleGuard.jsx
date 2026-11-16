import { useAuthStore } from '../../store/authStore'

export default function RoleGuard({ roles = [], children, fallback = null }) {
  const { user } = useAuthStore()

  if (!user || (roles.length > 0 && !roles.includes(user.role))) {
    return fallback
  }

  return children
}
