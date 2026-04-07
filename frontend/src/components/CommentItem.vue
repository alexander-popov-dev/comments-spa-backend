<script setup>
import {computed, ref, watch} from 'vue'
import useCommentsStore from '@/stores/comments'
import CommentItem from '@/components/CommentItem.vue'
import CommentForm from '@/components/CommentForm.vue'
import {useAuthStore} from "@/stores/auth.js";

const emit = defineEmits(['refresh'])
const commentsStore = useCommentsStore()
const authStore = useAuthStore()
const replies = ref([])
const showReplies = ref(false)
const showForm = ref(false)
const formMode = ref('reply')
const props = defineProps({comment: Object})
const isOwner = computed(() => authStore.user?.username === props.comment.username)

async function toggleReplies(commentId) {
  if (!showReplies.value && replies.value.length === 0) {
    replies.value = await commentsStore.fetchReplies(commentId)
  }
  showReplies.value = !showReplies.value
}

async function deleteComment() {
  if (!confirm('Are you sure you want to delete this comment?')) return
  await commentsStore.deleteComment(props.comment.id)
  await commentsStore.fetchComments()
  emit('refresh')
}

function editComment() {
  formMode.value = 'edit'
  showForm.value = true
}

function replyComment() {
  formMode.value = 'reply'
  showForm.value = true
}

async function refreshReplies() {
  if (showReplies.value) {
    replies.value = await commentsStore.fetchReplies(props.comment.id)
  }
}

async function onFormClose() {
  showForm.value = false
  if (formMode.value === 'reply') {
    commentsStore.incrementRepliesCount(props.comment.id)
    replies.value = await commentsStore.fetchReplies(props.comment.id)
    showReplies.value = true
  }
  emit('refresh')
}

const lightboxUrl = ref(null)
const imageError = ref(false)

const apiUrl = import.meta.env.VITE_API_URL || ''
function getFileName(path) {
  return path.split('/').pop().split('?')[0]
}

const textContent = ref(null)
const textLoading = ref(false)
const showTextLightbox = ref(false)

async function viewTextFile() {
  showTextLightbox.value = true
  if (textContent.value !== null) return
  textLoading.value = true
  try {
    const raw = props.comment.text_file
    const pathname = raw.startsWith('http') ? new URL(raw).pathname : raw
    const res = await fetch(pathname)
    textContent.value = await res.text()
  } catch (e) {
    textContent.value = `Error: ${e.message}`
  } finally {
    textLoading.value = false
  }
}

function fileUrl(path) {
  if (!path) return null
  if (path.startsWith('blob:') || path.startsWith('data:')) return path
  if (path.startsWith('http')) {
    const url = new URL(path)
    return `${apiUrl}${url.pathname}`
  }
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${apiUrl}${normalized}`
}

function openLightbox() {
  lightboxUrl.value = fileUrl(props.comment.image_file)
}

</script>

<template>
  <div>
    <div class="comment-item">
      <div class="comment-header">
        <span>{{ comment.username }}</span>
        <span>{{ comment.email }}</span>
        <div class="btn-header">
          <button v-if="isOwner" @click="editComment">Edit</button>
          <button v-if="isOwner" @click="deleteComment">Delete</button>
          <button v-if="!isOwner" @click="replyComment">Reply</button>
        </div>
      </div>
      <div class="comment-content">
        <div v-html="comment.comment"></div>
      <div class="comment-file">
        <img
            v-if="comment.image_file && !imageError"
            :src="fileUrl(comment.image_file)"
            alt="attachment"
            @click="openLightbox"
            @error="imageError = true"
        />
        <div v-if="imageError" class="no-image">No image</div>
      </div>
      <div v-if="comment.text_file" class="comment-file">
        <a class="file-link" @click.prevent="viewTextFile">{{ comment.text_file_name || getFileName(comment.text_file) }}</a>
      </div>
      </div>
      <div class="comment-footer">
        <span>{{ new Date(comment.created_at).toLocaleString() }}</span>
        <button v-if="comment.replies_count > 0" @click="toggleReplies(comment.id)" class="btn-header">
          Show {{ comment.replies_count }} answer/s
        </button>
      </div>
    </div>
    <Transition name="slide">
      <div class="comment-reply" v-if="showReplies">
        <CommentItem
            v-for="reply in replies"
            :key="reply.id"
            :comment="reply"
            @refresh="refreshReplies"
        />
      </div>
    </Transition>
    <CommentForm
        v-if="showForm"
        :mode="formMode"
        :comment="comment"
        @close="onFormClose"
    />
    <Transition name="fade">
      <div v-if="lightboxUrl" class="lightbox" @click="lightboxUrl = null">
        <img :src="lightboxUrl" alt="attachment" />
      </div>
    </Transition>
    <Transition name="fade">
      <div v-if="showTextLightbox" class="lightbox" @click="showTextLightbox = false">
        <pre class="text-lightbox" @click.stop>{{ textLoading ? 'Loading...' : textContent }}</pre>
      </div>
    </Transition>
  </div>
</template>


<style scoped>
button {
  font-size: 12px;
  color: var(--text-h);
}

.comment-item {
  border-radius: 10px;
  margin-bottom: 30px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.comment-header {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text);
  margin-bottom: 10px;
  padding: 5px 10px;
  border-bottom: 1px solid var(--border);
}

.btn-header {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

span:first-child {
  font-weight: 600;
  color: var(--text);
}

.comment-content {
  padding: 5px 10px;
  font-size: 15px;
  color: var(--text-h);
  word-break: break-word;
}

.comment-footer {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text);
  margin-top: 10px;
  padding: 5px 10px;
  border-top: 1px solid var(--border);
}

.no-image {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: var(--bg);
  border: 1px dashed var(--border);
  border-radius: 5px;
  color: var(--text);
  font-size: 12px;
  margin-top: 8px;
}

.comment-file img {
  max-width: 320px;
  max-height: 240px;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 10px;
}

.file-link {
  font-size: 13px;
  color: var(--accent);
  margin-top: 10px;
  display: block;
  cursor: pointer;
}

.text-lightbox {
  background: var(--surface);
  border-radius: 8px;
  padding: 20px;
  max-width: 700px;
  width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--text);
}


.comment-reply {
  margin-top: 12px;
  padding-left: 16px;
  border-left: 2px solid var(--border);
}

.slide-enter-active,
.slide-leave-active {
  transition: opacity 0.4s, transform 0.5s;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  cursor: zoom-out;
}

.lightbox img {
  max-width: 90vw;
  max-height: 90vh;
  border-radius: 8px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

</style>
