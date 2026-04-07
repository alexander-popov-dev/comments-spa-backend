<script setup>
import {ref} from 'vue'
import {useAuthStore} from '@/stores/auth'
import {useRouter} from 'vue-router'

const store = useAuthStore()
const router = useRouter()

const email = ref('')
const username = ref('')
const homepage = ref('')
const password = ref('')
const password2 = ref('')
const error = ref('')


async function submit() {
  try {
    await store.register({
      email: email.value,
      username: username.value,
      homepage: homepage.value,
      password: password.value,
      password2: password2.value,
    })
    router.push('/')
  } catch (e) {
    const data = e.response?.data
    if (data && typeof data === 'object') {
      error.value = Object.values(data).flat().join('\n')
    } else {
      error.value = 'Something went wrong'
    }
  }
}

</script>

<template>
  <main class="container">
    <form @submit.prevent="submit">
      <div class="form-container">
        <h4 style="margin-bottom: 20px">Create account</h4>
        <p v-if="error" class="error" style="white-space: pre-line">{{ error }}</p>
        <input v-model="email" type="email" placeholder="Email" required/>
        <input v-model="username" placeholder="Username" required/>
        <input v-model="homepage" placeholder="Homepage"/>
        <input v-model="password" type="password" placeholder="Password" required/>
        <input v-model="password2" type="password" placeholder="Confirm password" required/>
        <button class="btn" type="submit">Sign Up</button>
      </div>
    </form>
  </main>
</template>

