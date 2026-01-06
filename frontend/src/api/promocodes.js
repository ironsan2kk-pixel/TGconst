import client from './client'

export const promocodesApi = {
  list: async (botUuid) => {
    const response = await client.get(`/bots/${botUuid}/promocodes`)
    return response.data
  },
  
  get: async (botUuid, id) => {
    const response = await client.get(`/bots/${botUuid}/promocodes/${id}`)
    return response.data
  },
  
  create: async (botUuid, data) => {
    const response = await client.post(`/bots/${botUuid}/promocodes`, data)
    return response.data
  },
  
  update: async (botUuid, id, data) => {
    const response = await client.put(`/bots/${botUuid}/promocodes/${id}`, data)
    return response.data
  },
  
  delete: async (botUuid, id) => {
    const response = await client.delete(`/bots/${botUuid}/promocodes/${id}`)
    return response.data
  },
  
  validate: async (botUuid, code) => {
    const response = await client.post(`/bots/${botUuid}/promocodes/validate`, { code })
    return response.data
  },
}

export default promocodesApi
