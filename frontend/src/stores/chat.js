import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sendMessage, getConversations, getConversationDetail } from '../api/chat'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const loading = ref(false)

  async function fetchConversations() {
    conversations.value = await getConversations()
  }

  async function fetchConversation(id) {
    currentConversation.value = await getConversationDetail(id)
    messages.value = currentConversation.value.messages || []
  }

  async function send(content) {
    loading.value = true
    try {
      messages.value.push({ role: 'user', content, created_at: new Date().toISOString() })
      const data = await sendMessage(content, currentConversation.value?.id)
      currentConversation.value = { ...currentConversation.value, id: data.conversation_id }
      messages.value.push({
        role: 'assistant',
        content: data.message,
        intent: data.intent,
        created_at: new Date().toISOString(),
      })
      return data
    } catch (error) {
      console.error('Send message failed:', error)
      messages.value.push({
        role: 'assistant',
        content: '抱歉，请求失败，请稍后重试。',
        intent: 'chat',
        created_at: new Date().toISOString(),
      })
    } finally {
      loading.value = false
    }
  }

  function clearChat() {
    currentConversation.value = null
    messages.value = []
  }

  return { conversations, currentConversation, messages, loading, fetchConversations, fetchConversation, send, clearChat }
})
