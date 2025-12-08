/**
 * useCollaboration composable
 * Provides real-time collaboration features for AI context sessions
 */

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { createResource, call } from 'frappe-ui'

export function useCollaboration(options = {}) {
  const {
    sessionId: initialSessionId = '',
    pageType = '',
    documentId = '',
    autoConnect = true,
    pollInterval = 5000
  } = options

  // State
  const sessionId = ref(initialSessionId)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const participants = ref([])
  const events = ref([])
  const error = ref(null)
  let pollTimer = null

  // Computed
  const participantCount = computed(() => participants.value.length)
  const isActive = computed(() => isConnected.value && sessionId.value)
  const otherParticipants = computed(() => {
    return participants.value.filter(p => !p.is_current_user)
  })

  // API Resources
  const subscribeResource = createResource({
    url: 'mkaguzi.api.ai_specialist.join_collaborative_session'
  })

  const publishResource = createResource({
    url: 'mkaguzi.api.ai_specialist.broadcast_session_update'
  })

  const getParticipantsResource = createResource({
    url: 'mkaguzi.api.ai_specialist.get_session_participants'
  })

  // Methods
  const connect = async (newSessionId = null) => {
    if (newSessionId) {
      sessionId.value = newSessionId
    }

    if (!sessionId.value) {
      error.value = 'No session ID provided'
      return false
    }

    isConnecting.value = true
    error.value = null

    try {
      const result = await subscribeResource.fetch({
        session_id: sessionId.value,
        page_type: pageType,
        document_id: documentId
      })

      if (result.success) {
        isConnected.value = true
        await refreshParticipants()
        startPolling()
        return true
      } else {
        error.value = result.error || 'Failed to connect'
        return false
      }
    } catch (err) {
      error.value = err.message || 'Connection error'
      return false
    } finally {
      isConnecting.value = false
    }
  }

  const disconnect = () => {
    stopPolling()
    isConnected.value = false
    participants.value = []
    events.value = []
  }

  const refreshParticipants = async () => {
    if (!sessionId.value) return

    try {
      const result = await getParticipantsResource.fetch({
        session_id: sessionId.value
      })

      if (result.success) {
        const oldUsers = participants.value.map(p => p.user)
        participants.value = result.participants || []

        // Detect new participants
        const newUsers = participants.value.filter(p => !oldUsers.includes(p.user))
        newUsers.forEach(user => {
          events.value.unshift({
            type: 'joined',
            user: user.user,
            timestamp: new Date().toISOString()
          })
        })

        // Detect left participants
        const leftUsers = oldUsers.filter(
          user => !participants.value.find(p => p.user === user)
        )
        leftUsers.forEach(user => {
          events.value.unshift({
            type: 'left',
            user,
            timestamp: new Date().toISOString()
          })
        })

        // Keep only recent events
        events.value = events.value.slice(0, 50)
      }
    } catch (err) {
      console.error('Failed to refresh participants:', err)
    }
  }

  const publishEvent = async (eventType, eventData = {}) => {
    if (!sessionId.value || !isConnected.value) {
      return false
    }

    try {
      const result = await publishResource.fetch({
        session_id: sessionId.value,
        event_type: eventType,
        event_data: eventData
      })

      if (result.success) {
        events.value.unshift({
          type: eventType,
          user: 'You',
          data: eventData,
          timestamp: new Date().toISOString()
        })
        return true
      }
      return false
    } catch (err) {
      console.error('Failed to publish event:', err)
      return false
    }
  }

  const notifyTyping = () => publishEvent('typing', { typing: true })
  const notifyViewing = () => publishEvent('viewing', { page_type: pageType, document_id: documentId })
  const shareView = () => publishEvent('view_shared', { url: window.location.href })
  const sendMessage = (message) => publishEvent('message', { message })

  // Polling
  const startPolling = () => {
    if (pollTimer) return
    pollTimer = setInterval(refreshParticipants, pollInterval)
  }

  const stopPolling = () => {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  // Lifecycle
  onMounted(() => {
    if (autoConnect && sessionId.value) {
      connect()
    }
  })

  onUnmounted(() => {
    disconnect()
  })

  // Watch for session ID changes
  watch(() => initialSessionId, (newId) => {
    if (newId && newId !== sessionId.value) {
      disconnect()
      sessionId.value = newId
      if (autoConnect) {
        connect()
      }
    }
  })

  return {
    // State
    sessionId,
    isConnected,
    isConnecting,
    participants,
    events,
    error,

    // Computed
    participantCount,
    isActive,
    otherParticipants,

    // Methods
    connect,
    disconnect,
    refreshParticipants,
    publishEvent,
    notifyTyping,
    notifyViewing,
    shareView,
    sendMessage
  }
}

export default useCollaboration
