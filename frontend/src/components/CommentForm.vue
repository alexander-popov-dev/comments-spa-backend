<script setup>
import {useAuthStore} from "@/stores/auth.js";
import {ref} from "vue";
import useCommentsStore from "@/stores/comments.js";

const emit = defineEmits(['close'])
const authStore = useAuthStore()
const commentStore = useCommentsStore()
const errors = ref({})
const textareaRef = ref(null)
const file = ref(null)
const form = ref({
  username: '',
  email: '',
  homepage: '',
  comment: '',
})

async function sendComment() {
  const payload = new FormData()
  payload.append('comment', form.value.comment)

  try {
    if (authStore.user) {
      payload.append('email', localStorage.getItem("email"))
      payload.append('username', localStorage.getItem("username"))
    }
    if (file.value) {
      const field = file.value.type === 'text/plain' ? 'text_file' : 'image_file'
      payload.append(field, file.value)
    }
    await commentStore.createComment(payload)
    emit('close')
    await commentStore.fetchComments()
  } catch (e) {
    errors.value = e.response?.data || {}
  }
}

function wrapTag(tag) {
  const el = textareaRef.value
  const start = el.selectionStart
  const end = el.selectionEnd
  const selected = form.value.comment.substring(start, end)
  const before = form.value.comment.substring(0, start)
  const after = form.value.comment.substring(end)

  form.value.comment = `${before}<${tag}>${selected}</${tag}>${after}`
}

function onFileChange(e) {
  file.value = e.target.files[0]
}


</script>

<template>
  <div class="overlay" @click.self="emit('close')">
    <div class="modal">
      <div class="header">
        <h4>Create commet</h4>
        <button class="btn btn-modal" @click="emit('close')">X</button>
      </div>
      <template v-if="!authStore.user">
        <p v-if="errors.email" class="error">{{ errors.email[0] }}</p>
        <input v-model="form.email" type="email" placeholder="Email" required/>
        <p v-if="errors.username" class="error">{{ errors.username[0] }}</p>
        <input v-model="form.username" placeholder="User Name" required/>
        <input v-model="form.homepage" placeholder="Home page"/>
      </template>
      <div class="tag-btns">
        <button type="button" @click="wrapTag('i')"><i>I</i></button>
        <button type="button" @click="wrapTag('strong')"><strong>B</strong></button>
        <button type="button" @click="wrapTag('code')">{ }</button>
        <button type="button" @click="wrapTag('a')">URL</button>
      </div>
      <p v-if="errors.comment" class="error">{{ errors.comment[0] }}</p>
      <textarea ref="textareaRef" v-model="form.comment" placeholder="Your comment..."/>
      <input type="file" accept=".jpg,.gif,.png,.txt" @change="onFileChange"/>
      <div class="actions">
        <button class="btn btn-modal" type="submit">Preview</button>
        <button class="btn btn-modal" @click="sendComment">Publicate</button>
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
}

.tag-btns {
  display: flex;
  gap: 10px;
  margin-bottom: 5px;
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