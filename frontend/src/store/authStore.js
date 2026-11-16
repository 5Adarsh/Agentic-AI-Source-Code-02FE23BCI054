import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,

      /**
       * Set user and tokens after a successful login
       */
      setAuth: (user, accessToken, refreshToken) => {
        set({
          user,
          token: accessToken,
          refreshToken,
          isAuthenticated: true,
        })
      },

      /**
       * Update tokens (after refresh)
       */
      setTokens: (accessToken, refreshToken) => {
        set({ token: accessToken, refreshToken })
      },

      /**
       * Update user profile
       */
      setUser: (user) => {
        set({ user })
      },

      /**
       * Clear everything — logout
       */
      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },

      /**
       * Check if the current user has a given role
       */
      hasRole: (role) => {
        const { user } = get()
        if (!user) return false
        if (Array.isArray(role)) return role.includes(user.role)
        return user.role === role
      },

      /**
       * Check if user is admin
       */
      isAdmin: () => get().hasRole('admin'),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
)
