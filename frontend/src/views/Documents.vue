<template>
  <div class="documents-layout">
    <div class="top-nav">
      <el-button @click="$router.push('/chat')" text>返回对话</el-button>
      <h3>文档管理</h3>
      <el-upload
        :show-file-list="false"
        :before-upload="handleUpload"
        accept=".pdf,.doc,.docx,.txt,.csv,.png,.jpg"
      >
        <el-button type="primary">上传文档</el-button>
      </el-upload>
    </div>
    <div class="documents-content">
      <el-table :data="documents" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="content_type" label="类型" width="180" />
        <el-table-column label="大小" width="120">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chunk_count" label="分块数" width="100" />
        <el-table-column label="上传时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { getDocuments, uploadDocument } from '../api/document'
import { ElMessage } from 'element-plus'

const documents = ref([])
let pollTimer = null

const hasProcessing = computed(() =>
  documents.value.some(d => d.status === 'pending' || d.status === 'parsing')
)

function startPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    try {
      documents.value = await getDocuments()
    } catch { /* ignore */ }
    if (!hasProcessing.value) stopPolling()
  }, 3000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

function statusType(status) {
  return { pending: 'warning', parsing: 'info', completed: 'success', failed: 'danger' }[status] || 'info'
}

function statusLabel(status) {
  return { pending: '待解析', parsing: '解析中', completed: '已完成', failed: '失败' }[status] || status
}

async function handleUpload(file) {
  try {
    await uploadDocument(file)
    ElMessage.success('上传成功，正在后台解析...')
    documents.value = await getDocuments()
    startPolling()
  } catch (e) {
    ElMessage.error('上传失败')
  }
  return false
}

onMounted(async () => {
  documents.value = await getDocuments()
  if (hasProcessing.value) startPolling()
})

onUnmounted(() => stopPolling())
</script>

<style scoped>
.documents-layout {
  min-height: 100vh;
  background: #f0f2f5;
}
.top-nav {
  background: #fff;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.top-nav h3 {
  font-size: 18px;
  color: #1a1a2e;
}
.documents-content {
  padding: 24px;
}
</style>
