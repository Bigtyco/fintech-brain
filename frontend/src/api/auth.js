import request from './request'

export function register(username, email, password) {
  return request.post('/auth/register', { username, email, password })
}

export function login(username, password) {
  return request.post('/auth/login', { username, password })
}

export function getMe() {
  return request.get('/auth/me')
}

export function refreshToken() {
  return request.post('/auth/refresh')
}

export function logout() {
  return request.post('/auth/logout')
}
