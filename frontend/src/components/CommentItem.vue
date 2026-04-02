<script setup>
import {ref} from 'vue'
import useCommentsStore from '@/stores/comments'
import CommentItem from '@/components/CommentItem.vue'

defineProps({
  comment: Object,
})

const store = useCommentsStore()
const replies = ref([])
const showReplies = ref(false)

async function toggleReplies(commentId) {
  if (!showReplies.value && replies.value.length === 0) {
    replies.value = await store.fetchReplies(commentId)
  }
  showReplies.value = !showReplies.value
}
</script>

<template>
  <div>
    <div class="comment-item">
      <div class="comment-header">
        <span>{{ comment.username }}</span>
        <span>{{ comment.email }}</span>
      </div>
      <div class="comment-content" v-html="comment.comment"></div>
      <div class="comment-footer">
        <span>{{ comment.created_at }}</span>
        <button v-if="comment.replies_count > 0" @click="toggleReplies(comment.id)">
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
        />
      </div>
    </Transition>
  </div>
</template>


<style scoped>
.comment-item {
  background: var(--accent-bg);
  border-radius: 10px;
  margin-bottom: 30px;
  transition: margin 0.9s ease;

  .comment-header {
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: var(--text);
    margin-bottom: 10px;
    padding: 5px 10px;
    border-bottom: 1px solid var(--border);

    span:first-child {
      font-weight: 600;
      color: var(--text);
    }
  }

  .comment-content {
    padding: 5px 10px;
    font-size: 15px;
    color: var(--text-h);
  }

  .comment-footer {
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: var(--text);
    margin-top: 10px;
    padding: 5px 10px;
    border-top: 1px solid var(--border);

    button {
      font-size: 12px;
      color: var(--text-h);
    }
  }
}

&:hover {
  text-decoration: underline;
}

.comment-reply {
  margin-top: 12px;
  padding-left: 16px;
  border-left: 2px solid var(--border);
}

.comment-item {
  background: var(--surface);
  border: 1px solid var(--border);
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

</style>