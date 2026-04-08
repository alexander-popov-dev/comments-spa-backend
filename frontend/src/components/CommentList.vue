<script setup>
import {computed, onMounted, onUnmounted, ref} from 'vue'
import useCommentsStore from '@/stores/comments'
import CommentItem from '@/components/CommentItem.vue'
import {vAutoAnimate} from '@formkit/auto-animate/vue'
import CommentForm from "@/components/CommentForm.vue";

const store = useCommentsStore()
const totalPages = computed(() => Math.ceil(store.totalCount / 25) || 1)
const currentPage = computed(() => store.currentPage)
const showForm = ref(false)

const ORDER_FIELDS = [
  {value: 'username', label: 'User Name'},
  {value: 'email', label: 'E-mail'},
  {value: 'created_at', label: 'Date'},
]

onMounted(() => {
  store.fetchComments()
  store.connectWS()
})

onUnmounted(() => {
  store.disconnectWS()
})

function changePage(page) {
  store.fetchComments(page)
}

function onFieldChange(e) {
  store.setOrdering(e.target.value, store.orderDir)
}

function toggleDir() {
  store.setOrdering(store.orderField, store.orderDir === 'desc' ? 'asc' : 'desc')
}

function createComment() {
  showForm.value = true
}

</script>

<template>
  <div>
    <!-- Header -->
    <div class="header">
      <button class="btn btn-modal" @click="createComment">Add</button>
      <div class="filters">
        <span class="filters-label">Sort by:</span>
        <select class="filters-select" :value="store.orderField" @change="onFieldChange">
          <option class="filters-item" v-for="f in ORDER_FIELDS" :key="f.value" :value="f.value">{{ f.label }}</option>
        </select>
        <button class="filters-dir" @click="toggleDir" :title="store.orderDir === 'desc' ? 'Descending' : 'Ascending'">
          {{ store.orderDir === 'desc' ? '↓' : '↑' }}
        </button>
      </div>
    </div>

    <!-- List comments -->
    <div v-auto-animate class="comments">
      <CommentItem
          v-for="comment in store.comments"
          :key="comment.id"
          :comment="comment"
          @refresh="store.fetchComments(store.currentPage)"
      />
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button class="btn btn-modal" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">←</button>
      <span class="pagination-text">{{ currentPage }} / {{ totalPages }}</span>
      <button class="btn btn-modal" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">→</button>
    </div>
  </div>

  <CommentForm v-if="showForm" @close="showForm = false"/>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filters-label {
  font-size: 13px;
  color: var(--text);
}

.filters-select {
  font-size: 13px;
  padding: 4px 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 5px;
  color: var(--text);
  cursor: pointer;
}

.filters-dir {
  font-size: 16px;
  width: 30px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 5px;
  color: var(--text);
  transition: background 0.15s;
}

.filters-dir:hover {
  background: var(--bg);
}

.pagination {
  max-width: 20%;
  display: flex;
  margin: 30px auto;
}

.pagination-text {
  margin: auto;
  font-size: 13px;
}

.btn-modal {
  padding: 0 10px;
}
</style>