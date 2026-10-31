import api from './api'

export const subscriptionService = {
  // Quotations
  getQuotations: (params) => api.get('/quotations/', { params }),
  getQuotation: (id) => api.get(`/quotations/${id}/`),
  createQuotation: (data) => api.post('/quotations/', data),
  updateQuotation: (id, data) => api.put(`/quotations/${id}/`, data),
  acceptQuotation: (id) => api.post(`/quotations/${id}/accept/`),
  rejectQuotation: (id) => api.post(`/quotations/${id}/reject/`),
  convertQuotation: (id, data) => api.post(`/quotations/${id}/convert/`, data),

  // Subscriptions
  getSubscriptions: (params) => api.get('/subscriptions/', { params }),
  getSubscription: (id) => api.get(`/subscriptions/${id}/`),
  pauseSubscription: (id) => api.post(`/subscriptions/${id}/pause/`),
  resumeSubscription: (id) => api.post(`/subscriptions/${id}/resume/`),
  renewSubscription: (id) => api.post(`/subscriptions/${id}/renew/`),
  closeSubscription: (id) => api.post(`/subscriptions/${id}/close/`),

  // Helpers
  getCustomers: () => api.get('/customers/'),
  getCatalog: () => api.get('/catalog/'),
}

export default subscriptionService
