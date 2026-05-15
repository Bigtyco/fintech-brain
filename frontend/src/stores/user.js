import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, getMe, logout as logoutApi } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const isLoggedIn = computed(() => !!user.value)

  async function login(username, password) {
    await loginApi(username, password)
    await fetchUser()
  }

  async function register(username, email, password) {
    await registerApi(username, email, password)
  }

  async function fetchUser() {
    try {
      user.value = await getMe()
    } catch {
      user.value = null
    }
  }

  async function logout() {
    try {
      await logoutApi()
    } finally {
      user.value = null
      window.location.href = '/login'
    }
  }

  return { user, isLoggedIn, login, register, fetchUser, logout }
})
