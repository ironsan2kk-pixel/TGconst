import client from './client'

export const broadcastsApi = {
  list: async (botUuid) => {
    const response = await client.get(`/bots/${botUuid}/broadcasts`)
    return response.data
  },
  
  get: async (botUuid, id) => {
    const response = await client.get(`/bots/${botUuid}/broadcasts/${id}`)
    return response.data
  },
  
  create: async (botUuid, data) => {
    const response = await client.post(`/bots/${botUuid}/broadcasts`, data)
    return response.data
  },
  
  update: async (botUuid, id, data) => {
    const response = await client.put(`/bots/${botUuid}/broadcasts/${id}`, data)
    return response.data
  },
  
  delete: async (botUuid, id) => {
    const response = await client.delete(`/bots/${botUuid}/broadcasts/${id}`)
    return response.data
  },
  
  start: async (botUuid, id) => {
    const response = await client.post(`/bots/${botUuid}/broadcasts/${id}/start`)
    return response.data
  },
  
  cancel: async (botUuid, id) => {
    const response = await client.post(`/bots/${botUuid}/broadcasts/${id}/cancel`)
    return response.data
  },
  
  stats: async (botUuid) => {
    const response = await client.get(`/bots/${botUuid}/broadcasts/stats`)
    return response.data
  },
}

// Именованные экспорты для удобства
export const getBroadcasts = broadcastsApi.list
export const getBroadcast = broadcastsApi.get
export const createBroadcast = broadcastsApi.create
export const updateBroadcast = broadcastsApi.update
export const deleteBroadcast = broadcastsApi.delete
export const startBroadcast = broadcastsApi.start
export const cancelBroadcast = broadcastsApi.cancel
export const getBroadcastStats = async (botUuid, id) => {
  const response = await client.get(`/bots/${botUuid}/broadcasts/${id}/stats`)
  return response.data
}

export default broadcastsApi
