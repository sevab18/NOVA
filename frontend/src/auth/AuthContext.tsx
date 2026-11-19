import {
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'

import { api, TOKEN_STORAGE_KEY } from '../api/client'
import type { LoginPayload, RegisterPayload, User } from '../types'
import { AuthContext } from './context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(
    () => sessionStorage.getItem(TOKEN_STORAGE_KEY) !== null,
  )

  useEffect(() => {
    const token = sessionStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token) return

    let active = true
    api
      .me(token)
      .then((profile) => {
        if (active) setUser(profile)
      })
      .catch(() => {
        sessionStorage.removeItem(TOKEN_STORAGE_KEY)
        if (active) setUser(null)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  const login = async (payload: LoginPayload) => {
    const token = await api.login(payload)
    sessionStorage.setItem(TOKEN_STORAGE_KEY, token.access_token)

    try {
      const profile = await api.me(token.access_token)
      setUser(profile)
    } catch (error) {
      sessionStorage.removeItem(TOKEN_STORAGE_KEY)
      throw error
    }
  }

  const register = async (payload: RegisterPayload) => {
    await api.register(payload)
    await login({ email: payload.email, password: payload.password })
  }

  const logout = () => {
    sessionStorage.removeItem(TOKEN_STORAGE_KEY)
    setUser(null)
  }

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
