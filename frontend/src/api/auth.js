import client from './client'

export const authApi = {
  login: async (username, password) => {
    const response = await client.post('/auth/login', { username, password })
    return response.data
  },
  
  getMe: async () => {
    const response = await client.get('/auth/me')
    return response.data
  },
}

export default authApi
