import api from './api'

export default {
  // Auth
  auth: {
    login: (data) => api.post('/auth/login', data),
    register: (data) => api.post('/auth/register', data),
    logout: () => api.post('/auth/logout'),
    getMe: () => api.get('/auth/me')
  },

  // Users
  users: {
    getMe: () => api.get('/users/me'),
    updateMe: (data) => api.patch('/users/me', data),
    deleteMe: () => api.delete('/users/me')
  },

  // API Keys
  apiKeys: {
    getAll: () => api.get('/users/me/api-keys'),
    create: (data) => api.post('/users/me/api-keys', data),
    getById: (id) => api.get(`/users/me/api-keys/${id}`),
    update: (id, data) => api.patch(`/users/me/api-keys/${id}`, data),
    delete: (id) => api.delete(`/users/me/api-keys/${id}`)
  },

  // Topics
  topics: {
    getAll: (params) => api.get('/topics', { params }),
    create: (data) => api.post('/topics', data),
    getById: (id) => api.get(`/topics/${id}`),
    update: (id, data) => api.patch(`/topics/${id}`, data),
    delete: (id) => api.delete(`/topics/${id}`),
    search: (query, params) => api.get('/topics/search', { params: { query, ...params } })
  },

  // Characters
  characters: {
    getTemplates: (params) => api.get('/characters/templates', { params }),
    getTemplateById: (id) => api.get(`/characters/templates/${id}`),
    getRandomTemplates: (count) => api.get('/characters/templates/random', { params: { count } }),
    getMine: (params) => api.get('/characters', { params }),
    getById: (id) => api.get(`/characters/${id}`),
    create: (data) => api.post('/characters', data),
    update: (id, data) => api.patch(`/characters/${id}`, data),
    delete: (id) => api.delete(`/characters/${id}`),
    search: (query, params) => api.get('/characters/search', { params: { query, ...params } }),
    recommend: (topic, count = 5) => api.post('/characters/recommend', topic, { params: { count } })
  },

  // Discussions
  discussions: {
    getAll: (params) => api.get('/discussions', { params }),
    create: (data) => api.post('/discussions', data),
    getById: (id) => api.get(`/discussions/${id}`),
    delete: (id) => api.delete(`/discussions/${id}`),
    start: (id, provider) => api.post(`/discussions/${id}/start`, null, { params: { provider } }),
    pause: (id) => api.post(`/discussions/${id}/pause`),
    resume: (id) => api.post(`/discussions/${id}/resume`),
    stop: (id) => api.post(`/discussions/${id}/stop`),
    injectQuestion: (id, question) => api.post(`/discussions/${id}/inject-question`, { question }),
    getMessages: (id, params) => api.get(`/discussions/${id}/messages`, { params })
  },

  // Reports
  reports: {
    getById: (id) => api.get(`/reports/${id}`),
    getByDiscussionId: (id) => api.get(`/reports/discussions/${id}`),
    regenerate: (id) => api.post(`/reports/discussions/${id}/regenerate`)
  }
}
