import client from './client'

export const channelsApi = {
  list: async (botUuid) => {
    const response = await client.get(`/bots/${botUuid}/channels`)
    return response.data
  },
  
  get: async (botUuid, id) => {
    const response = await client.get(`/bots/${botUuid}/channels/${id}`)
    return response.data
  },
  
  create: async (botUuid, data) => {
    const response = await client.post(`/bots/${botUuid}/channels`, data)
    return response.data
  },
  
  update: async (botUuid, id, data) => {
    const response = await client.put(`/bots/${botUuid}/channels/${id}`, data)
    return response.data
  },
  
  delete: async (botUuid, id) => {
    const response = await client.delete(`/bots/${botUuid}/channels/${id}`)
    return response.data
  },
}

export default channelsApi
