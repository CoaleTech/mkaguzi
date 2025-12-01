<template>
  <div class="flex flex-col h-full bg-white">
    <!-- Chat Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
          <component :is="getRoomIcon(room.room_type)" class="w-5 h-5 text-blue-600" />
        </div>
        <div>
          <h2 class="text-lg font-semibold text-gray-900">{{ room.room_name }}</h2>
          <p class="text-sm text-gray-500">
            {{ room.participants?.length || 0 }} members
            <span v-if="room.related_document"> • Linked to {{ room.related_document }}</span>
          </p>
        </div>
      </div>

      <div class="flex items-center space-x-2">
        <Button variant="ghost" size="sm" @click="showParticipants = !showParticipants">
          <Users class="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="sm">
          <Settings class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Messages Area -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
      <div v-if="loadingMessages" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="text-sm text-gray-500 mt-2">Loading messages...</p>
      </div>

      <div v-else-if="messages.length === 0" class="text-center py-12">
        <MessageCircle class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No messages yet</h3>
        <p class="text-gray-500">Start the conversation by sending the first message.</p>
      </div>

      <div v-else>
        <div
          v-for="message in messages"
          :key="message.name"
          :class="[
            'flex',
            message.sender === currentUser ? 'justify-end' : 'justify-start'
          ]"
        >
          <div
            :class="[
              'max-w-xs lg:max-w-md px-4 py-2 rounded-lg',
              message.sender === currentUser
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-900'
            ]"
          >
            <div v-if="message.sender !== currentUser" class="text-xs text-gray-500 mb-1">
              {{ getUserDisplayName(message.sender) }}
            </div>
            <div class="text-sm">{{ message.message_content }}</div>
            <div
              :class="[
                'text-xs mt-1',
                message.sender === currentUser ? 'text-blue-200' : 'text-gray-500'
              ]"
            >
              {{ formatMessageTime(message.sent_at) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Input -->
    <div class="p-4 border-t border-gray-200 bg-white">
      <div class="flex space-x-2">
        <input
          type="text"
          v-model="newMessage"
          placeholder="Type a message..."
          class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          @keydown.enter="sendMessage"
        />
        <Button @click="sendMessage" :disabled="!newMessage.trim()">
          <Send class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Participants Sidebar -->
    <div
      v-if="showParticipants"
      class="w-80 border-l border-gray-200 bg-white flex flex-col"
    >
      <div class="p-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">Participants</h3>
      </div>

      <div class="flex-1 overflow-y-auto">
        <div v-if="participants.length === 0" class="p-4 text-center text-gray-500">
          No participants
        </div>
        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="participant in participants"
            :key="participant.user"
            class="p-4 flex items-center space-x-3"
          >
            <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
              <span class="text-sm font-medium text-gray-600">
                {{ getUserInitials(participant.user) }}
              </span>
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">
                {{ getUserDisplayName(participant.user) }}
              </p>
              <p class="text-xs text-gray-500 capitalize">{{ participant.role }}</p>
            </div>
            <div
              v-if="participant.last_seen"
              class="w-2 h-2 bg-green-500 rounded-full"
              title="Online"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	AlertTriangle,
	Building,
	FileText,
	MessageCircle,
	Send,
	Settings,
	Users,
} from "lucide-vue-next"
import { nextTick, onMounted, onUnmounted, ref } from "vue"

// Props
const props = defineProps({
	room: {
		type: Object,
		required: true,
	},
})

// Emits
const emit = defineEmits(["room-updated"])

// Reactive data
const messages = ref([])
const participants = ref([])
const newMessage = ref("")
const loadingMessages = ref(false)
const showParticipants = ref(false)
const currentUser = ref("")
const socket = ref(null)

// Resources
const messagesResource = createResource({
	url: "mkaguzi.issue_chat.api.chat.get_messages",
	onSuccess: (data) => {
		if (data.success) {
			messages.value = data.messages || []
			scrollToBottom()
		}
	},
	onError: (error) => {
		console.error("Failed to load messages:", error)
	},
})

const participantsResource = createResource({
	url: "mkaguzi.issue_chat.api.chat.get_room_participants",
	onSuccess: (data) => {
		if (data.success) {
			participants.value = data.participants || []
		}
	},
	onError: (error) => {
		console.error("Failed to load participants:", error)
	},
})

const sendMessageResource = createResource({
	url: "mkaguzi.issue_chat.doctype.issue_chat_message.issue_chat_message.send_message",
	onSuccess: (data) => {
		if (data.success) {
			newMessage.value = ""
			// Message will be added via WebSocket or we can reload
			loadMessages()
		}
	},
	onError: (error) => {
		console.error("Failed to send message:", error)
	},
})

// Methods
const getRoomIcon = (roomType) => {
	const icons = {
		general: MessageCircle,
		followup: AlertTriangle,
		audit: FileText,
		department: Building,
	}
	return icons[roomType] || MessageCircle
}

const getUserDisplayName = (userName) => {
	// In a real app, you'd fetch user details
	// For now, return the username
	return userName
}

const getUserInitials = (userName) => {
	return userName
		.split(" ")
		.map((n) => n[0])
		.join("")
		.toUpperCase()
		.slice(0, 2)
}

const formatMessageTime = (timestamp) => {
	if (!timestamp) return ""

	const date = new Date(timestamp)
	return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
}

const sendMessage = () => {
	if (!newMessage.value.trim()) return

	sendMessageResource.update({
		params: {
			chat_room: props.room.name,
			message_content: newMessage.value,
		},
	})
	sendMessageResource.fetch()
}

const loadMessages = () => {
	messagesResource.update({
		params: {
			chat_room: props.room.name,
		},
	})
	messagesResource.fetch()
}

const loadParticipants = () => {
	participantsResource.update({
		params: {
			chat_room: props.room.name,
		},
	})
	participantsResource.fetch()
}

const scrollToBottom = () => {
	nextTick(() => {
		const container = document.querySelector(".overflow-y-auto")
		if (container) {
			container.scrollTop = container.scrollHeight
		}
	})
}

const setupWebSocket = () => {
	// Initialize Socket.IO connection for real-time messaging
	try {
		import("socket.io-client").then(({ io }) => {
			socket.value = io("/issue_chat", {
				transports: ["websocket", "polling"],
			})

			socket.value.on("connect", () => {
				console.log("Connected to chat server")
				socket.value.emit("join_room", props.room.name)
			})

			socket.value.on("new_message", (message) => {
				if (message.chat_room === props.room.name) {
					messages.value.push(message)
					scrollToBottom()
				}
			})

			socket.value.on("disconnect", () => {
				console.log("Disconnected from chat server")
			})
		})
	} catch (error) {
		console.warn("Socket.IO not available:", error)
	}
}

const cleanupWebSocket = () => {
	if (socket.value) {
		socket.value.disconnect()
	}
}

// Watchers
watch(
	() => props.room,
	(newRoom) => {
		if (newRoom) {
			loadMessages()
			loadParticipants()
			if (socket.value) {
				socket.value.emit("leave_room", props.room.name)
				socket.value.emit("join_room", newRoom.name)
			}
		}
	},
	{ immediate: true },
)

// Lifecycle
onMounted(async () => {
	// Get current user
	try {
		const userResource = createResource({
			url: "frappe.auth.get_logged_user",
			auto: true,
		})
		await userResource.promise
		currentUser.value = userResource.data
	} catch (error) {
		currentUser.value = "Administrator"
	}

	setupWebSocket()
})

onUnmounted(() => {
	cleanupWebSocket()
})
</script>