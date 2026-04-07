<script setup>
import {ref} from 'vue'

const menuOpen = ref(false)
import {useAuthStore} from '@/stores/auth'
import {useRouter} from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

async function logout() {
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="header">
    <a class="logo" href="/">CommentSPA</a>

    <nav class="menu" :class="{ open: menuOpen }">

      <template v-if="auth.user">
        <a>{{ auth.user?.username }}</a>
        <a @click="logout">Sign Out</a>
      </template>

      <template v-else>
        <a href="/register">Sign Up</a>
        <a href="/login">Sign In</a>
      </template>

    </nav>

    <button class="burger" @click="menuOpen = !menuOpen">
      <span></span>
      <span></span>
      <span></span>
    </button>

  </div>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 25px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  margin-bottom: 30px;
  position: relative;
}

.logo {
  font-weight: 700;
  font-size: 18px;
  color: var(--text-h);
  text-decoration: none;
}

.menu {
  display: flex;
  gap: 20px;
}

a {
  color: var(--text);
  text-decoration: none;
  font-size: 14px;
}

a:hover {
  color: var(--accent);
}

.burger {
  display: none;
  flex-direction: column;
  gap: 5px;
  padding: 4px;
}

span {
  display: block;
  width: 22px;
  height: 2px;
  background: var(--text-h);
  border-radius: 2px;
  transition: 0.3s;
}

@media (max-width: 768px) {
  .burger {
    display: flex;
  }

  .menu {
    display: none;
    position: absolute;
    top: 56px;
    left: 0;
    right: 0;
    flex-direction: column;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 16px 24px;
    gap: 16px;
  }

  .menu.open {
    display: flex;
  }
}
</style>