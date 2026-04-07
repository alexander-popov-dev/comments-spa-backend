import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '@/api/index.js'

const useCommentsStore = defineStore('comments', () => {
    const comments = ref([])
    const loading = ref(false)
    const totalCount = ref(0)
    const currentPage = ref(1)
    const orderField = ref('created_at')
    const orderDir = ref('desc')
    const newReplyEvent = ref(null)

    let socket = null
    let reconnectTimer = null

    function connectWS() {
        const wsUrl = import.meta.env.VITE_WS_URL ||
            `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/comments/`

        socket = new WebSocket(wsUrl)

        socket.onmessage = (event) => {
            const { action, comment, id } = JSON.parse(event.data)
            if (action === 'created') {
                if (!comment.parent_comment && currentPage.value === 1 && orderField.value === 'created_at' && orderDir.value === 'desc') {
                    comments.value.unshift(comment)
                    totalCount.value += 1
                } else if (comment.parent_comment) {
                    const idx = comments.value.findIndex(c => c.id === comment.parent_comment)
                    if (idx !== -1) comments.value[idx] = {...comments.value[idx], replies_count: comments.value[idx].replies_count + 1}
                    newReplyEvent.value = {parentId: comment.parent_comment, reply: comment}
                }
            } else if (action === 'updated') {
                const idx = comments.value.findIndex(c => c.id === comment.id)
                if (idx !== -1) comments.value[idx] = comment
            } else if (action === 'deleted') {
                const idx = comments.value.findIndex(c => c.id === id)
                if (idx !== -1) {
                    comments.value.splice(idx, 1)
                    totalCount.value -= 1
                }
            }
        }

        socket.onclose = () => {
            reconnectTimer = setTimeout(connectWS, 3000)
        }

        socket.onerror = () => {
            socket.close()
        }
    }

    function disconnectWS() {
        clearTimeout(reconnectTimer)
        socket?.close()
        socket = null
    }

    async function fetchComments(page = 1) {
        loading.value = true
        try {
            const ordering = (orderDir.value === 'desc' ? '-' : '') + orderField.value
            const response = await api.get('/api/v1/comment/', {params: {page, ordering}})
            comments.value = response.data.results
            totalCount.value = response.data.count
            currentPage.value = page
        } finally {
            loading.value = false
        }
    }

    function setOrdering(field, dir) {
        orderField.value = field
        orderDir.value = dir
        fetchComments(1)
    }

    async function fetchReplies(commentId) {
        const response = await api.get(`/api/v1/comment/${commentId}/`)
        return response.data.replies
    }

    async function createComment(data) {
        await api.post(`/api/v1/comment/`, data)
    }

    async function deleteComment(id) {
        await api.delete(`/api/v1/comment/${id}/`)
    }

    async function updateComment(id, data) {
        await api.patch(`/api/v1/comment/${id}/`, data)
    }

    async function createReply(parentId, data) {
        await api.post(`/api/v1/comment/${parentId}/reply/`, data)
    }

    return {
        comments,
        loading,
        totalCount,
        currentPage,
        orderField,
        orderDir,
        newReplyEvent,
        fetchComments,
        fetchReplies,
        setOrdering,
        createComment,
        deleteComment,
        updateComment,
        createReply,
        connectWS,
        disconnectWS,
    }
})

export default useCommentsStore
