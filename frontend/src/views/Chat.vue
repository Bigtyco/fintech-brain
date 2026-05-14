<template>
  <div class="chat-layout">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>投研助手</h3>
        <el-button type="primary" :icon="Plus" circle size="small" @click="newChat" />
      </div>
      <div class="conversation-list">
        <div
          v-for="conv in chatStore.conversations"
          :key="conv.id"
          class="conv-item"
          :class="{ active: chatStore.currentConversation?.id === conv.id }"
          @click="selectConversation(conv.id)"
        >
          <el-icon><ChatDotRound /></el-icon>
          <span>{{ conv.title }}</span>
        </div>
      </div>
      <div class="sidebar-footer">
        <el-button @click="goTo('/dashboard')" text>风控看板</el-button>
        <el-button @click="goTo('/documents')" text>文档管理</el-button>
        <el-button @click="goTo('/knowledge')" text>知识图谱</el-button>
        <el-button @click="handleLogout" text type="danger">退出</el-button>
      </div>
    </div>

    <!-- 聊天区 -->
    <div class="chat-main">
      <div class="messages" ref="messagesRef">
        <div v-if="chatStore.messages.length === 0" class="empty-state">
          <el-icon :size="64" color="#c0c4cc"><ChatDotRound /></el-icon>
          <p>开始您的投研对话</p>
          <p class="hint">可以问我任何金融投研或风控相关的问题</p>
        </div>
        <div v-for="(msg, i) in chatStore.messages" :key="i" class="message" :class="msg.role">
          <div class="avatar">
            <el-icon v-if="msg.role === 'user'" :size="20"><User /></el-icon>
            <el-icon v-else :size="20"><Monitor /></el-icon>
          </div>
          <div class="bubble">
            <div class="content" v-html="renderMarkdown(msg.content)"></div>
            <span v-if="msg.intent" class="intent-tag">{{ intentLabel(msg.intent) }}</span>
          </div>
        </div>
        <div v-if="chatStore.loading" class="message assistant">
          <div class="avatar"><el-icon :size="20"><Monitor /></el-icon></div>
          <div class="bubble"><span class="typing">思考中...</span></div>
        </div>
      </div>
      <div class="input-area">
        <el-input
          v-model="input"
          placeholder="输入您的问题..."
          :rows="1"
          resize="none"
          @keydown.enter.exact.prevent="handleSend"
          :disabled="chatStore.loading"
        />
        <el-button type="primary" :icon="Promotion" @click="handleSend" :loading="chatStore.loading" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '../stores/chat'
import { useUserStore } from '../stores/user'
import { Plus, ChatDotRound, User, Monitor, Promotion } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'

const router = useRouter()
const chatStore = useChatStore()
const userStore = useUserStore()
const input = ref('')
const messagesRef = ref()
const md = new MarkdownIt()

function renderMarkdown(text) {
  return md.render(text || '')
}

function intentLabel(intent) {
  return { research: '投研分析', risk: '风控评估', chat: '通用对话' }[intent] || intent
}

function goTo(path) {
  router.push(path)
}

function newChat() {
  chatStore.clearChat()
}

async function selectConversation(id) {
  await chatStore.fetchConversation(id)
}

async function handleSend() {
  if (!input.value.trim() || chatStore.loading) return
  const msg = input.value.trim()
  input.value = ''
  await chatStore.send(msg)
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  chatStore.fetchConversations()
})
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
}
.sidebar {
  width: 260px;
  background: #1a1a2e;
  color: #fff;
  display: flex;
  flex-direction: column;
}
.sidebar-header {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.sidebar-header h3 {
  font-size: 16px;
}
.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.conv-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  margin-bottom: 4px;
}
.conv-item:hover, .conv-item.active {
  background: rgba(255,255,255,0.1);
}
.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.sidebar-footer .el-button {
  color: rgba(255,255,255,0.7);
  font-size: 12px;
}
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}
.empty-state .hint {
  font-size: 14px;
  margin-top: 8px;
}
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
.message.user {
  flex-direction: row-reverse;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.message.user .avatar {
  background: #409eff;
  color: #fff;
}
.message.assistant .avatar {
  background: #67c23a;
  color: #fff;
}
.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 14px;
}
.message.user .bubble {
  background: #409eff;
  color: #fff;
}
.message.assistant .bubble {
  background: #fff;
  color: #333;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.content :deep(p) {
  margin: 0 0 8px;
}
.content :deep(p:last-child) {
  margin: 0;
}
.intent-tag {
  display: inline-block;
  margin-top: 8px;
  padding: 2px 8px;
  background: rgba(64,158,255,0.1);
  color: #409eff;
  border-radius: 4px;
  font-size: 12px;
}
.typing {
  color: #909399;
}
.input-area {
  padding: 16px 20px;
  background: #fff;
  display: flex;
  gap: 12px;
  border-top: 1px solid #e4e7ed;
}
.input-area .el-input {
  flex: 1;
}
</style>
