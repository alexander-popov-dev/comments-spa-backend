import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
})


api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const original = error.config
        const data = error.response?.data
        const isExpired = data?.messages?.[0]?.token_class === 'AccessToken'

        if (error.response?.status === 401 && isExpired && !original._retry) {
            original._retry = true
            try {
                const refresh = localStorage.getItem('refresh')
                const response = await api.post('/api/auth/refresh/', {refresh})
                localStorage.setItem('access', response.data.access)
                original.headers.Authorization = `Bearer ${response.data.access}`
                return api(original)
            } catch {
                localStorage.removeItem('access')
                localStorage.removeItem('refresh')
                localStorage.removeItem('username')
                localStorage.removeItem('email')
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export default api

