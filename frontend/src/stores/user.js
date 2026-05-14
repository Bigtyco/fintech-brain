import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, getMe } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const data = await loginApi(username, password)
    token.value = data.access_token
    refreshToken.value = data.refresh_token
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    await fetchUser()
  }

  async function register(username, email, password) {
    await registerApi(username, email, password)
  }

  async function fetchUser() {
    try {
      user.value = await getMe()
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { token, refreshToken, user, isLoggedIn, login, register, fetchUser, logout }
})
