import { useAuthStore } from '../store/authStore'
import { login as apiLogin, logout as apiLogout } from '../api/auth'

export function useAuth() {
  const user = useAuthStore((s) => s.user)
  const token = useAuthStore((s) => s.token)
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const setAuth = useAuthStore((s) => s.setAuth)
  const logoutStore = useAuthStore((s) => s.logout)
  const hasRole = useAuthStore((s) => s.hasRole)
  const isAdmin = useAuthStore((s) => s.isAdmin)

  const login = async (credentials) => {
    const data = await apiLogin(credentials)
    setAuth(data.user, data.access_token, data.refresh_token)
    return data
  }

  const logout = async () => {
    try {
      await apiLogout()
    } catch {
      // Ignore server errors on logout
    } finally {
      logoutStore()
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    hasRole,
    isAdmin,
  }
}
