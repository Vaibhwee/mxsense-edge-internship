import axios from 'axios'

const apiBaseURL = import.meta.env.VITE_API_BASE_URL;
export const api = axios.create({
  baseURL: `${apiBaseURL.replace(/\/$/, '')}/api`,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

