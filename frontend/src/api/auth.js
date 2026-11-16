import api from './axios'

/**
 * Login with email/password — returns { access_token, refresh_token, expires_in, token_type }
 */
export const login = async (credentials) => {
  const payload = {
    email: credentials.email || credentials.username,
    password: credentials.password,
  }
  const { data } = await api.post('/auth/login', payload)
  return data
}

/**
 * Refresh access token using refresh token
 */
export const refreshToken = async (token) => {
  const { data } = await api.post('/auth/refresh', { refresh_token: token })
  return data
}

/**
 * Logout — invalidates server-side session
 */
export const logout = async () => {
  await api.post('/auth/logout')
}

/**
 * Get current user profile
 */
export const getCurrentUser = async () => {
  const { data } = await api.get('/auth/me')
  return data
}

export const authApi = {
  login,
  refreshToken,
  logout,
  getCurrentUser,
}
