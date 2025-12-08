<template>
  <div class="collaborative-session-panel bg-white border rounded-lg shadow-sm">
    <div class="flex items-center justify-between p-3 border-b">
      <h3 class="text-sm font-medium flex items-center gap-2">
        <Users class="w-4 h-4 text-blue-500" />
        Collaboration
        <span 
          v-if="isConnected"
          class="w-2 h-2 bg-green-500 rounded-full animate-pulse"
        ></span>
      </h3>
      <div class="flex items-center gap-1">
        <Button variant="ghost" size="sm" @click="toggleExpanded">
          <ChevronDown 
            class="w-4 h-4 transition-transform" 
            :class="{ 'rotate-180': isExpanded }"
          />
        </Button>
        <Button variant="ghost" size="sm" @click="$emit('close')">
          <X class="w-4 h-4" />
        </Button>
      </div>
    </div>
    
    <div v-show="isExpanded" class="p-3 space-y-3">
      <!-- Connection status -->
      <div 
        :class="[
          'flex items-center gap-2 p-2 rounded-lg text-sm',
          isConnected ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'
        ]"
      >
        <Wifi class="w-4 h-4" :class="{ 'animate-pulse': !isConnected }" />
        {{ isConnected ? 'Connected' : 'Connecting...' }}
      </div>
      
      <!-- Participants -->
      <div>
        <div class="text-xs font-medium text-gray-500 mb-2">
          Active Participants ({{ participants.length }})
        </div>
        <div class="flex flex-wrap gap-2">
          <div
            v-for="participant in participants"
            :key="participant.user"
            class="flex items-center gap-2 p-2 bg-gray-50 rounded-lg"
          >
            <div 
              class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-medium"
              :style="{ backgroundColor: getAvatarColor(participant.user) }"
            >
              {{ getInitials(participant.user) }}
            </div>
            <div>
              <div class="text-sm font-medium">{{ participant.user }}</div>
              <div class="text-xs text-gray-400">
                {{ formatLastSeen(participant.last_seen) }}
              </div>
            </div>
            <div 
              v-if="participant.is_typing"
              class="flex gap-1"
            >
              <span class="w-1 h-1 bg-blue-500 rounded-full animate-bounce"></span>
              <span class="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
              <span class="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent events -->
      <div v-if="events.length > 0">
        <div class="text-xs font-medium text-gray-500 mb-2">
          Recent Activity
        </div>
        <div class="space-y-1 max-h-32 overflow-y-auto">
          <div
            v-for="(event, index) in events"
            :key="index"
            class="text-xs p-2 bg-gray-50 rounded flex items-center gap-2"
          >
            <component 
              :is="getEventIcon(event.type)" 
              class="w-3 h-3 text-gray-400"
            />
            <span class="text-gray-600">
              <strong>{{ event.user }}</strong>
              {{ getEventText(event) }}
            </span>
            <span class="text-gray-400 ml-auto">
              {{ formatTime(event.timestamp) }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Quick actions -->
      <div class="pt-2 border-t">
        <div class="text-xs font-medium text-gray-500 mb-2">Quick Actions</div>
        <div class="flex gap-2">
          <Button 
            variant="subtle" 
            size="sm"
            @click="notifyTyping"
          >
            <Edit3 class="w-3 h-3 mr-1" />
            Typing...
          </Button>
          <Button 
            variant="subtle" 
            size="sm"
            @click="shareCurrentView"
          >
            <Share2 class="w-3 h-3 mr-1" />
            Share View
          </Button>
        </div>
      </div>
      
      <!-- Invite link -->
      <div class="pt-2 border-t">
        <div class="text-xs font-medium text-gray-500 mb-2">Invite Others</div>
        <div class="flex gap-2">
          <Input
            v-model="inviteLink"
            readonly
            class="flex-1 text-xs"
          />
          <Button variant="ghost" size="sm" @click="copyInviteLink">
            <Copy class="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Button, Input } from 'frappe-ui'
import { 
  Users, X, ChevronDown, Wifi, Edit3, Share2, Copy, 
  MessageSquare, Eye, LogIn, LogOut 
} from 'lucide-vue-next'
import { createResource, call } from 'frappe-ui'

const props = defineProps({
  sessionId: {
    type: String,
    required: true
  },
  pageType: {
    type: String,
    required: true
  },
  documentId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'participantJoined', 'participantLeft', 'eventReceived'])

const isExpanded = ref(true)
const isConnected = ref(false)
const participants = ref([])
const events = ref([])
const inviteLink = ref('')
let pollInterval = null

// Avatar colors for participants
const avatarColors = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
]

onMounted(() => {
  generateInviteLink()
  startPolling()
  subscribeToSession()
})

onUnmounted(() => {
  stopPolling()
})

const generateInviteLink = () => {
  const baseUrl = window.location.origin
  inviteLink.value = `${baseUrl}/collaboration/${props.sessionId}`
}

// Subscribe to collaboration session
const subscribeResource = createResource({
  url: 'mkaguzi.api.ai_specialist.join_collaborative_session',
  makeParams: () => ({
    session_id: props.sessionId,
    page_type: props.pageType,
    document_id: props.documentId
  }),
  onSuccess: (data) => {
    if (data.success) {
      isConnected.value = true
    }
  }
})

// Get participants
const getParticipantsResource = createResource({
  url: 'mkaguzi.api.ai_specialist.get_session_participants',
  makeParams: () => ({
    session_id: props.sessionId
  }),
  onSuccess: (data) => {
    if (data.success) {
      const oldParticipants = participants.value.map(p => p.user)
      participants.value = data.participants || []
      
      // Emit events for new/left participants
      const newParticipants = data.participants.filter(p => !oldParticipants.includes(p.user))
      newParticipants.forEach(p => emit('participantJoined', p))
    }
  }
})

// Publish event
const publishEventResource = createResource({
  url: 'mkaguzi.api.ai_specialist.broadcast_session_update'
})

const subscribeToSession = async () => {
  await subscribeResource.fetch()
  await getParticipantsResource.fetch()
}

const startPolling = () => {
  pollInterval = setInterval(() => {
    getParticipantsResource.fetch()
  }, 5000) // Poll every 5 seconds
}

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
}

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const notifyTyping = async () => {
  await publishEventResource.fetch({
    session_id: props.sessionId,
    event_type: 'typing',
    event_data: { typing: true }
  })
}

const shareCurrentView = async () => {
  await publishEventResource.fetch({
    session_id: props.sessionId,
    event_type: 'view_shared',
    event_data: {
      page_type: props.pageType,
      document_id: props.documentId,
      url: window.location.href
    }
  })
  
  // Add to local events
  events.value.unshift({
    type: 'view_shared',
    user: 'You',
    timestamp: new Date().toISOString()
  })
}

const copyInviteLink = async () => {
  try {
    await navigator.clipboard.writeText(inviteLink.value)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const getAvatarColor = (user) => {
  const index = user.charCodeAt(0) % avatarColors.length
  return avatarColors[index]
}

const getInitials = (user) => {
  return user.substring(0, 2).toUpperCase()
}

const formatLastSeen = (lastSeen) => {
  if (!lastSeen) return 'Just now'
  const diff = Date.now() - new Date(lastSeen).getTime()
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  return `${Math.floor(diff / 3600000)}h ago`
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const getEventIcon = (type) => {
  const icons = {
    'typing': Edit3,
    'view_shared': Share2,
    'message': MessageSquare,
    'joined': LogIn,
    'left': LogOut
  }
  return icons[type] || Eye
}

const getEventText = (event) => {
  const texts = {
    'typing': 'is typing...',
    'view_shared': 'shared their view',
    'message': 'sent a message',
    'joined': 'joined the session',
    'left': 'left the session'
  }
  return texts[event.type] || event.type
}
</script>

<style scoped>
.collaborative-session-panel {
  min-width: 280px;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
</style>
