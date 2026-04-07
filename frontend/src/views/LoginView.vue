<script setup>
import {ref} from 'vue'
import {useAuthStore} from '@/stores/auth'
import {useRouter} from 'vue-router'

const store = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')


async function submit() {
  try {
    await store.login({email: email.value, password: password.value})
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Something went wrong'
  }
}

</script>

<template>
  <main class="container">
    <form @submit.prevent="submit">
      <div class="form-container">
        <h4 style="margin-bottom: 20px" >Welcome back</h4>
        <p v-if="error" class="error">{{ error }}</p>
        <input v-model="email" type="email" placeholder="Email" required/>
        <input v-model="password" type="password" placeholder="Password" required/>
        <button class="btn" type="submit">Sign In</button>
      </div>
    </form>
  </main>
</template>

