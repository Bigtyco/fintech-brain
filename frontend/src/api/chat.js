import request from './request'

export function sendMessage(message, conversation_id) {
  return request.post('/chat', { message, conversation_id })
}

export function getConversations() {
  return request.get('/chat/conversations')
}

export function getConversationDetail(id) {
  return request.get(`/chat/conversations/${id}`)
}
