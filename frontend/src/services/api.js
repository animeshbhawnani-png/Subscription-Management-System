import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// Attach access token to every request automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// On 401 → clear tokens (refresh flow can be added later)
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    }
    return Promise.reject(err)
  }
)

export default api

