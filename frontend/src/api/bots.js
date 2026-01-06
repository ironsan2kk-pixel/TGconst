import client from './client'

export const botsApi = {
  list: async () => {
    const response = await client.get('/bots')
    return response.data
  },
  
  get: async (uuid) => {
    const response = await client.get(`/bots/${uuid}`)
    return response.data
  },
  
  create: async (data) => {
    const response = await client.post('/bots', data)
    return response.data
  },
  
  update: async (uuid, data) => {
    const response = await client.put(`/bots/${uuid}`, data)
    return response.data
  },
  
  delete: async (uuid) => {
    const response = await client.delete(`/bots/${uuid}`)
    return response.data
  },
  
  start: async (uuid) => {
    const response = await client.post(`/bots/${uuid}/start`)
    return response.data
  },
  
  stop: async (uuid) => {
    const response = await client.post(`/bots/${uuid}/stop`)
    return response.data
  },
  
  restart: async (uuid) => {
    const response = await client.post(`/bots/${uuid}/restart`)
    return response.data
  },
  
  status: async (uuid) => {
    const response = await client.get(`/bots/${uuid}/status`)
    return response.data
  },
}

export default botsApi
