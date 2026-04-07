import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/api/index.js'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(
        localStorage.getItem('username')
            ? {username: localStorage.getItem('username'), email: localStorage.getItem('email')}
            : null
    )
    const accessToken = ref(localStorage.getItem('access') || null)
    const refreshToken = ref(localStorage.getItem('refresh') || null)


    async function register(data) {
        const response = await api.post('/api/auth/register/', data)
        await updateLocalStorage(response)
        user.value = { username: response.data.username, email: response.data.email }
    }

    async function login(data) {
        const response = await api.post(`/api/auth/login/`, data)
        await updateLocalStorage(response)
        user.value = { username: response.data.username, email: response.data.email }
    }

    async function logout() {
        try {
            await api.post('/api/auth/logout/', {refresh: refreshToken.value})
        } finally {
            accessToken.value = null
            refreshToken.value = null
            user.value = null
            localStorage.removeItem('access')
            localStorage.removeItem('refresh')
            localStorage.removeItem('username')
            localStorage.removeItem('email')
        }
    }


    async function updateLocalStorage(response) {
        accessToken.value = response.data.access
        refreshToken.value = response.data.refresh
        localStorage.setItem('access', response.data.access)
        localStorage.setItem('refresh', response.data.refresh)
        localStorage.setItem('username', response.data.username)
        localStorage.setItem('email', response.data.email)
    }

    return {user, register, login, logout}

})
