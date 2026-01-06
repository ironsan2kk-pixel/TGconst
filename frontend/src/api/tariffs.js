import client from './client'

export const tariffsApi = {
  list: async (botUuid, channelId) => {
    const response = await client.get(`/bots/${botUuid}/channels/${channelId}/tariffs`)
    return response.data
  },
  
  get: async (botUuid, id) => {
    const response = await client.get(`/bots/${botUuid}/tariffs/${id}`)
    return response.data
  },
  
  create: async (botUuid, channelId, data) => {
    const response = await client.post(`/bots/${botUuid}/channels/${channelId}/tariffs`, data)
    return response.data
  },
  
  update: async (botUuid, id, data) => {
    const response = await client.put(`/bots/${botUuid}/tariffs/${id}`, data)
    return response.data
  },
  
  delete: async (botUuid, id) => {
    const response = await client.delete(`/bots/${botUuid}/tariffs/${id}`)
    return response.data
  },
}

export default tariffsApi
