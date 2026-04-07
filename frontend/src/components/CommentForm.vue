<script setup>
import {useAuthStore} from "@/stores/auth.js";
import {ref, computed, onMounted, watch} from "vue";
import useCommentsStore from "@/stores/comments.js";
import api from "@/api/index.js";
import CommentItem from "@/components/CommentItem.vue";

const props = defineProps({
  mode: {type: String, default: 'create'}, // 'create' | 'edit' | 'reply'
  comment: {type: Object, default: null},
})

const emit = defineEmits(['close'])
const authStore = useAuthStore()
const { updateComment, createReply, createComment } = useCommentsStore()
const errors = ref({})
const textareaRef = ref(null)
const file = ref(null)
const filePreviewUrl = ref(null)
const fileInputRef = ref(null)
const captcha = ref({key: '', image_url: ''})
const showPreview = ref(false)
const previewHtml = ref('')

const title = computed(() => {
  if (props.mode === 'edit') return 'Edit comment'
  if (props.mode === 'reply') return 'Reply'
  return 'Create comment'
})

const previewComment = computed(() => ({
  username: authStore.user?.username || form.value.username,
  email: authStore.user?.email || form.value.email,
  comment: previewHtml.value,
  created_at: new Date().toISOString(),
  replies_count: 0,
  image_file: filePreviewUrl.value || null,
  text_file: file.value?.type === 'text/plain' ? file.value.name : null,
}))

const form = ref({
  username: '',
  email: '',
  homepage: '',
  comment: '',
  captcha_value: '',
})

const draftKey = `comment-draft-${props.mode}-${props.comment?.id || 'new'}`

async function fetchCaptcha() {
  try {
    const res = await api.get('/api/v1/captcha/')
    captcha.value = res.data
  } catch {
    // silently ignore — user will see empty captcha
  }
}

onMounted(async () => {
  if (props.mode === 'edit' && props.comment) {
    form.value.comment = props.comment.comment
  }
  const draft = sessionStorage.getItem(draftKey)
  if (draft) {
    const parsed = JSON.parse(draft)
    form.value = {...form.value, ...parsed}
  }
  if (!authStore.user && props.mode !== 'edit') {
    await fetchCaptcha()
  }
})

watch(form, (val) => {
  sessionStorage.setItem(draftKey, JSON.stringify(val))
}, {deep: true})

function buildPayload() {
  const payload = new FormData()
  payload.append('comment', form.value.comment)
  if (authStore.user) {
    payload.append('email', authStore.user.email)
    payload.append('username', authStore.user.username)
  } else {
    payload.append('email', form.value.email)
    payload.append('username', form.value.username)
    if (form.value.homepage) payload.append('homepage', form.value.homepage)
    payload.append('captcha_key', captcha.value.key)
    payload.append('captcha_value', form.value.captcha_value)
  }
  if (file.value) {
    const field = file.value.type === 'text/plain' ? 'text_file' : 'image_file'
    payload.append(field, file.value, file.value.name)
  }
  return payload
}

async function submit() {
  errors.value = {}
  try {
    if (props.mode === 'edit') {
      await updateComment(props.comment.id, {comment: form.value.comment})
    } else if (props.mode === 'reply') {
      await createReply(props.comment.id, buildPayload())
    } else {
      await createComment(buildPayload())
    }
    sessionStorage.removeItem(draftKey)
    emit('close')
  } catch (e) {
    errors.value = e.response?.data || {}
    if (!authStore.user && props.mode !== 'edit') {
      form.value.captcha_value = ''
      await fetchCaptcha()
    }
  }
}

function wrapTag(tag) {
  const el = textareaRef.value
  const start = el.selectionStart
  const end = el.selectionEnd
  const selected = form.value.comment.substring(start, end)
  const before = form.value.comment.substring(0, start)
  const after = form.value.comment.substring(end)

  if (tag === 'a') {
    const href = prompt('Enter URL:')
    if (!href) return
    form.value.comment = `${before}<a href="${href}">${selected || href}</a>${after}`
  } else {
    form.value.comment = `${before}<${tag}>${selected}</${tag}>${after}`
  }
}

function clearFile() {
  file.value = null
  filePreviewUrl.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

function onFileChange(e) {
  const selected = e.target.files[0]
  if (!selected) return

  if (selected.size > 10 * 1024 * 1024) {
    errors.value.file = 'File size must not exceed 10 MB.'
    e.target.value = ''
    file.value = null
    filePreviewUrl.value = null
    return
  }

  errors.value.file = null
  file.value = selected
  if (file.value.type !== 'text/plain') {
    filePreviewUrl.value = URL.createObjectURL(file.value)
  } else {
    filePreviewUrl.value = null
  }
}

async function preview() {
  try {
    const response = await api.post('/api/v1/comment/preview/', {comment: form.value.comment})
    previewHtml.value = response.data.comment
    showPreview.value = true
  } catch (e) {
    errors.value = e.response?.data || {}
  }
}
</script>

<template>
  <div class="overlay">
    <div :class="['modal', { 'modal-preview': showPreview }]">
      <div class="header">
        <h4>{{ title }}</h4>
        <button class="btn btn-modal" @click="emit('close')">X</button>
      </div>
      <template v-if="!authStore.user && mode !== 'edit' && !showPreview">
        <p v-if="errors.email" class="error">{{ errors.email[0] }}</p>
        <input v-model="form.email" type="email" placeholder="Email" required/>
        <p v-if="errors.username" class="error">{{ errors.username[0] }}</p>
        <input v-model="form.username" placeholder="User Name" pattern="[a-zA-Z0-9]+" title="Only letters and digits" required/>
        <input v-model="form.homepage" type="url" placeholder="Home page"/>
        <div class="captcha-wrap">
          <img v-if="captcha.image_url" :src="captcha.image_url" alt="captcha" @click="fetchCaptcha" title="Click to refresh"/>
          <p v-if="errors.captcha" class="error">{{ errors.captcha[0] }}</p>
          <input v-model="form.captcha_value" placeholder="Enter captcha" autocomplete="off"/>
        </div>
      </template>
      <div v-if="!showPreview">
        <div class="tag-btns">
          <button type="button" @click="wrapTag('i')"><i>I</i></button>
          <button type="button" @click="wrapTag('strong')"><strong>B</strong></button>
          <button type="button" @click="wrapTag('code')">{ }</button>
          <button type="button" @click="wrapTag('a')">URL</button>
        </div>
        <p v-if="errors.comment" class="error">{{ errors.comment[0] }}</p>
        <textarea ref="textareaRef" v-model="form.comment" placeholder="Your comment..."/>
        <template v-if="mode !== 'edit'">
          <div v-if="file" class="file-selected">
            <img v-if="filePreviewUrl" :src="filePreviewUrl" alt="preview" style="max-width: 320px; max-height: 240px;"/>
            <p v-else>{{ file.name }} ({{ (file.size / 1024).toFixed(1) }} KB)</p>
            <button type="button" class="file-remove" @click="clearFile">✕ Remove</button>
          </div>
          <p v-if="errors.file" class="error">{{ errors.file }}</p>
          <input v-show="!file" type="file" accept=".jpg,.gif,.png,.txt" @change="onFileChange" ref="fileInputRef"/>
        </template>
      </div>
      <CommentItem v-if="showPreview" :comment="previewComment"/>
      <div class="actions">
        <button class="btn btn-modal" @click="showPreview ? showPreview = false : preview()">
          {{ showPreview ? 'Edit' : 'Preview' }}
        </button>
        <button class="btn btn-modal" @click="submit">
          {{ mode === 'edit' ? 'Save' : 'Publish' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: var(--surface);
  border-radius: 10px;
  padding: 20px;
  width: 480px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-preview {
  width: 860px;
  word-break: break-word;
}

.header {
  display: flex;
  margin-bottom: 20px;
  justify-content: space-between;
  align-items: center;
}

.btn-modal {
  padding: 0 10px;
}

.actions {
  justify-content: right;
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.tag-btns {
  display: flex;
  gap: 10px;
  margin-bottom: 5px;
}

.file-selected {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: 8px;
}

.file-remove {
  font-size: 12px;
  color: var(--accent);
  width: fit-content;
}

.captcha-wrap {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: 5px;
}

.captcha-wrap img {
  height: 50px;
  width: 180px;
  cursor: pointer;
  border-radius: 5px;
}

textarea {
  resize: none;
  margin-bottom: 5px;
  padding: 5px;
  width: 100%;
  height: 100px;
  background: var(--bg);
  border-radius: 5px;
  color: var(--text);
}
</style>
