import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 300000,  // 5分钟，LLM 调用需要较长时间
  withCredentials: true,  // 携带 httpOnly cookies
})

let isRefreshing = false
let pendingQueue = []

function processQueue(error) {
  pendingQueue.forEach(({ resolve, reject }) => {
    error ? reject(error) : resolve()
  })
  pendingQueue = []
}

request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push({ resolve, reject })
        }).then(() => request(originalRequest))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        await axios.post('/api/auth/refresh', {}, { withCredentials: true })
        processQueue(null)
        return request(originalRequest)
      } catch {
        processQueue(error)
        router.push('/login')
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }

    if (error.response?.status !== 401) {
      ElMessage.error(error.response?.data?.detail || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request
