import { createContext, useState, useEffect } from 'react'
import authApi from '../api/auth'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setLoading(false)
      return
    }

    try {
      const userData = await authApi.getMe()
      setUser(userData)
      setIsAuthenticated(true)
    } catch (error) {
      localStorage.removeItem('token')
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    const data = await authApi.login(username, password)
    localStorage.setItem('token', data.access_token)
    const userData = await authApi.getMe()
    setUser(userData)
    setIsAuthenticated(true)
    return userData
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{ user, loading, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
