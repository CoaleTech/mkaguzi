<template>
  <div class="flex flex-col h-full chat-container">
    <!-- Clean Frappe-style Chat Header -->
    <div class="chat-header">
      <div class="flex items-center justify-between p-4">
        <div class="flex items-center space-x-3">
          <!-- Simple Room Avatar -->
          <div class="relative">
            <div class="w-10 h-10 rounded-lg bg-chat-secondary border border-chat-border-light flex items-center justify-center">
              <component :is="getRoomIcon(room.room_type)" class="w-5 h-5 text-chat-text-secondary" />
              <!-- Simple AI Badge -->
              <div v-if="room.ai_enabled" class="absolute -top-1 -right-1">
                <div class="w-4 h-4 bg-chat-accent-primary rounded-full flex items-center justify-center">
                  <Bot class="w-2.5 h-2.5 text-white" />
                </div>
              </div>
            </div>
            <!-- Simple Online Status -->
            <div v-if="onlineCount > 0" class="absolute -bottom-1 -right-1">
              <div class="w-3 h-3 bg-chat-accent-success rounded-full border-2 border-chat-primary"></div>
            </div>
          </div>

          <div class="flex-1 min-w-0">
            <!-- Clean Room Title -->
            <div class="flex items-center space-x-2 mb-1">
              <h1 class="text-lg font-semibold text-chat-text-primary truncate">{{ room.room_name }}</h1>

              <!-- Simple Status Indicators -->
              <div class="flex items-center space-x-2">
                <span
                  v-if="room.ai_enabled"
                  class="inline-flex items-center px-2 py-1 text-xs font-medium bg-chat-accent-light text-chat-accent-primary rounded-md"
                >
                  <Bot class="w-3 h-3 mr-1" />
                  AI
                </span>

                <span
                  v-if="room.encryption_level === 'High'"
                  class="inline-flex items-center px-2 py-1 text-xs font-medium bg-chat-accent-success/10 text-chat-accent-success rounded-md"
                >
                  <Shield class="w-3 h-3 mr-1" />
                  Encrypted
                </span>
              </div>
            </div>

            <!-- Clean Room Info -->
            <div class="flex items-center space-x-3 text-sm text-chat-text-secondary">
              <span class="flex items-center space-x-1">
                <component :is="getRoomIcon(room.room_type)" class="w-3 h-3" />
                <span>{{ getRoomTypeLabel(room.room_type) }}</span>
              </span>

              <span class="w-px h-3 bg-chat-border-medium"></span>

              <span v-if="room.participant_count" class="flex items-center space-x-1">
                <Users class="w-3 h-3" />
                <span>{{ room.participant_count }} member{{ room.participant_count !== 1 ? 's' : '' }}</span>
              </span>

              <span class="w-px h-3 bg-chat-border-medium"></span>

              <span v-if="onlineCount > 0" class="flex items-center space-x-1">
                <div class="w-2 h-2 bg-chat-accent-success rounded-full"></div>
                <span>{{ onlineCount }} online</span>
              </span>
            </div>
          </div>

          <!-- Clean Header Actions -->
          <div class="flex items-center space-x-2">
            <!-- Simple AI Toggle -->
            <button
              v-if="room.ai_enabled"
              @click="toggleAIAssistant"
              :class="[
                'p-2 rounded-lg transition-colors chat-hover',
                aiAssistantActive 
                  ? 'bg-chat-accent-primary text-white' 
                  : 'text-chat-text-secondary hover:text-chat-text-primary'
              ]"
            >
              <Bot class="w-4 h-4" />
            </button>

            <!-- Simple Action Buttons -->
            <button
              @click="showSearch = !showSearch"
              :class="[
                'p-2 rounded-lg transition-colors chat-hover',
                showSearch 
                  ? 'bg-chat-secondary text-chat-text-primary' 
                  : 'text-chat-text-secondary hover:text-chat-text-primary'
              ]"
            >
              <Search class="w-4 h-4" />
            </button>

            <button
              @click="showParticipants = !showParticipants"
              :class="[
                'p-2 rounded-lg transition-colors chat-hover relative',
                showParticipants 
                  ? 'bg-chat-secondary text-chat-text-primary' 
                  : 'text-chat-text-secondary hover:text-chat-text-primary'
              ]"
            >
              <Users class="w-4 h-4" />
              <span v-if="room.participant_count > 1" class="absolute -top-1 -right-1 w-4 h-4 bg-chat-accent-primary text-white text-xs rounded-full flex items-center justify-center">
                {{ room.participant_count }}
              </span>
            </button>

            <button
              @click="showRoomSettings = true"
              class="p-2 rounded-lg transition-colors chat-hover text-chat-text-secondary hover:text-chat-text-primary"
            >
              <Settings class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Simple Search Bar -->
      <div v-if="showSearch" class="px-4 pb-4 animate-slide-up">
        <div class="relative">
          <Search class="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-chat-text-muted" />
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search messages..."
            class="w-full pl-9 pr-3 py-2 chat-input rounded-lg text-sm chat-focus"
            @input="searchMessages"
          />
        </div>
      </div>

      <!-- Simple AI Assistant Bar -->
      <div v-if="aiAssistantActive && room.ai_enabled" class="px-4 pb-4 animate-slide-up">
        <div class="p-3 bg-chat-accent-light rounded-lg border border-chat-accent-primary/20">
          <div class="flex items-center space-x-2">
            <Bot class="w-4 h-4 text-chat-accent-primary" />
            <span class="text-sm font-medium text-chat-accent-primary">AI Assistant Active</span>
            <span class="text-xs px-2 py-1 bg-chat-accent-primary text-white rounded">{{ aiModel?.model_name || 'Default' }}</span>
          </div>
          <p class="text-xs text-chat-text-secondary mt-1">
            AI analysis enabled for audit insights and suggestions.
          </p>
        </div>
      </div>
    </div>

    <!-- Main Chat Content Area -->
    <div class="flex-1 flex">
      <!-- Messages Area -->
      <div class="flex-1 flex flex-col">
        <!-- Message List -->
        <OptimizedMessageList
          ref="messageList"
          :messages="messages"
          :loading="loading"
          :typing-users="typingUsers"
          :current-user="{ name: currentUser, email: currentUser }"
          :load-more-threshold="100"
          :estimated-message-height="80"
          :auto-scroll-threshold="150"
          @load-more="loadMoreMessages"
          @message-reply="handleMessageReply"
          @message-edit="handleMessageEdit"
          @message-forward="handleMessageForward"
          @message-delete="handleMessageDelete"
          @scroll="handleScroll"
          class="flex-1"
        />

        <!-- Simple AI Suggestions Panel -->
        <div v-if="aiSuggestions.length > 0 && aiAssistantActive" class="border-t border-chat-border-light p-4 bg-chat-secondary">
          <div class="mb-3 flex items-center space-x-2">
            <Lightbulb class="w-4 h-4 text-chat-accent-warning" />
            <span class="text-sm font-medium text-chat-text-primary">AI Suggestions</span>
          </div>

          <div class="space-y-2">
            <button
              v-for="suggestion in aiSuggestions"
              :key="suggestion.id"
              class="w-full p-3 bg-chat-primary rounded-lg border border-chat-border-light text-left chat-hover transition-colors"
              @click="applySuggestion(suggestion)"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <p class="text-sm text-chat-text-primary">{{ suggestion.text }}</p>
                  <span class="text-xs text-chat-text-muted">{{ suggestion.type }}</span>
                </div>
                <ArrowRight class="w-4 h-4 text-chat-text-muted mt-0.5" />
              </div>
            </button>
          </div>
        </div>

        <!-- Message Input now handled by persistent RichChatInput in ChatPage -->
      </div>

      <!-- Right Sidebar -->
      <div v-if="showParticipants" class="w-80 border-l border-chat-border-light bg-chat-secondary animate-slide-up">
        <ParticipantList
          :room="room"
          :participants="participants"
          @participant-action="handleParticipantAction"
        />
      </div>
    </div>

    <!-- Room Settings Modal -->
    <RoomSettingsModal
      v-if="showRoomSettings"
      :room="room"
      @close="showRoomSettings = false"
      @room-updated="handleRoomUpdated"
    />
  </div>
</template>

<script setup>
// MessageInput removed - now using persistent RichChatInput in ChatPage
import MessageList from "@/components/chat/MessageList.vue"
import ParticipantList from "@/components/chat/ParticipantList.vue"
import RoomSettingsModal from "@/components/chat/RoomSettingsModal.vue"
import { useTheme } from "@/composables/useTheme"
import { call, createResource } from "frappe-ui"
import { Badge, Button } from "frappe-ui"
import {
	AlertTriangle,
	ArrowRight,
	Bot,
	Building,
	FileText,
	Lightbulb,
	Lock,
	MessageCircle,
	Search,
	Settings,
	Shield,
	Users,
} from "lucide-vue-next"
import { computed, onMounted, onUnmounted, ref, watch } from "vue"

// Props
const props = defineProps({
	room: {
		type: Object,
		required: true,
	},
})

// Emits
const emit = defineEmits(["room-updated"])

// Theme
const { currentTheme, isLoaded } = useTheme()

// Message cache for performance
const messageCache = new Map()
const CACHE_SIZE = 1000

// Add message to cache
const addToCache = (message) => {
	if (messageCache.size >= CACHE_SIZE) {
		// Remove oldest entries (simple FIFO)
		const firstKey = messageCache.keys().next().value
		messageCache.delete(firstKey)
	}
	messageCache.set(message.name || message.id, message)
}

// Get message from cache
const getFromCache = (messageId) => {
	return messageCache.get(messageId)
}

// Clear cache for room change
const clearCache = () => {
	messageCache.clear()
}

// Resources
const messagesResource = createResource({
	url: "mkaguzi.chat_system.api.chat_api.get_room_messages",
	params: {
		room_id: props.room.name,
		limit: 50,
	},
	auto: true,
	onSuccess: (data) => {
		messages.value = data?.messages || []
		participants.value = data?.participants || []
		onlineCount.value = data?.online_count || 0
	},
	onError: (error) => {
		console.warn("Failed to load messages:", error)
		messages.value = []
	},
})

const aiModelResource = createResource({
	url: "mkaguzi.chat_system.doctype.chat_ai_model_registry.chat_ai_model_registry.get_room_ai_model",
	params: {
		room: props.room.name,
	},
	auto: props.room.ai_enabled,
	onSuccess: (data) => {
		aiModel.value = data
		if (data) {
			aiAssistantActive.value = true
		}
	},
	onError: (error) => {
		console.warn("Failed to load AI model:", error)
		aiModel.value = null
	},
})

// Methods
const handleSendMessage = async (messageData) => {
	try {
		loading.value = true

		const response = await call(
			"mkaguzi.chat_system.doctype.chat_message.chat_message.send_message",
			{
				room: props.room.name,
				content: messageData.content,
				message_type: messageData.type || "Text",
				attachments: messageData.attachments,
				reply_to: messageData.replyTo,
			},
		)

		if (response.message) {
			// Message will be added via WebSocket
			// messages.value.push(response.message)

			// Check if this is a direct message with AI Assistant
			const hasAIAssistant = participants.value.some(
				(p) => p.user === "AI Assistant",
			)

			if (hasAIAssistant && props.room.room_type === "Direct") {
				// Generate AI response for direct messages with AI Assistant
				setTimeout(() => {
					generateAIResponse(messageData.content)
				}, 1000) // Small delay to simulate thinking
			} else if (aiAssistantActive.value && props.room.ai_enabled) {
				// Get AI suggestions for group chats with AI enabled
				requestAISuggestions(messageData.content)
			}
		}
	} catch (error) {
		console.error("Failed to send message:", error)
		// Show error message to user
		console.error("Failed to send message. Please try again.")
	} finally {
		loading.value = false
	}
}

const handleMessageReply = (message) => {
	// Handle reply - this would be handled by the MessageInput component
	console.log('Reply to message:', message)
}

const handleMessageEdit = (message) => {
	// Handle message editing
	console.log('Edit message:', message)
}

const handleMessageForward = (message) => {
	// Handle message forwarding
	console.log('Forward message:', message)
}

const handleMessageDelete = async (message) => {
	try {
		await deleteMessage(message.name || message.id)
	} catch (error) {
		console.error('Failed to delete message:', error)
	}
}

const handleScroll = (scrollInfo) => {
	// Handle scroll events for analytics or additional features
	console.log('Scroll info:', scrollInfo)
}

const deleteMessage = async (messageId) => {
	try {
		await call(
			"mkaguzi.chat_system.doctype.chat_message.chat_message.delete_message",
			{ message_id: messageId },
		)

		// Remove message from local state
		messages.value = messages.value.filter((m) => m.name !== messageId)
	} catch (error) {
		console.error("Failed to delete message:", error)
	}
}

const reactToMessage = async (messageId, emoji) => {
	try {
		await call(
			"mkaguzi.chat_system.doctype.chat_message.chat_message.add_reaction",
			{
				message_id: messageId,
				emoji: emoji,
			},
		)
	} catch (error) {
		console.error("Failed to add reaction:", error)
	}
}

const handleParticipantAction = async (action, participant) => {
	switch (action) {
		case "remove":
			await removeParticipant(participant.user)
			break
		case "make_admin":
			await updateParticipantRole(participant.user, "Admin")
			break
		case "remove_admin":
			await updateParticipantRole(participant.user, "Member")
			break
		default:
			console.warn("Unknown participant action:", action)
	}
}

const removeParticipant = async (userId) => {
	try {
		await call(
			"mkaguzi.chat_system.doctype.chat_participant.chat_participant.remove_participant",
			{
				room: props.room.name,
				user_id: userId,
			},
		)

		// Update local participants
		participants.value = participants.value.filter((p) => p.user !== userId)
	} catch (error) {
		console.error("Failed to remove participant:", error)
	}
}

const updateParticipantRole = async (userId, role) => {
	try {
		await call(
			"mkaguzi.chat_system.doctype.chat_participant.chat_participant.update_participant_role",
			{
				room: props.room.name,
				user_id: userId,
				role: role,
			},
		)

		// Update local participant
		const participant = participants.value.find((p) => p.user === userId)
		if (participant) {
			participant.role = role
		}
	} catch (error) {
		console.error("Failed to update participant role:", error)
	}
}

const loadMoreMessages = async () => {
	if (loading.value || !messages.value.length) return

	try {
		loading.value = true
		const oldestMessage = messages.value[0]

		// Use optimized API endpoint
		const response = await call(
			"mkaguzi.chat_system.api.chat_api.get_room_messages",
			{
				room_id: props.room.name,
				limit: 50,
				before_timestamp: oldestMessage?.timestamp || oldestMessage?.creation,
			},
		)

		if (response.message?.messages?.length > 0) {
			// Prepend older messages to maintain chronological order
			messages.value = [...response.message.messages, ...messages.value]
		}
	} catch (error) {
		console.error("Failed to load more messages:", error)
	} finally {
		loading.value = false
	}
}

const searchMessages = async () => {
	if (!searchQuery.value.trim()) {
		messagesResource.reload()
		return
	}

	try {
		const response = await call(
			"mkaguzi.chat_system.doctype.chat_message.chat_message.search_messages",
			{
				room: props.room.name,
				query: searchQuery.value,
			},
		)

		messages.value = response.message || []
	} catch (error) {
		console.error("Failed to search messages:", error)
	}
}

const toggleAIAssistant = () => {
	aiAssistantActive.value = !aiAssistantActive.value

	if (!aiAssistantActive.value) {
		aiSuggestions.value = []
	}
}

const requestAISuggestions = async (lastMessage) => {
	if (!props.room.ai_enabled || !aiAssistantActive.value) return

	try {
		const response = await call("mkaguzi.chat_system.api.get_ai_suggestions", {
			room: props.room.name,
			message: lastMessage,
			context: messages.value.slice(-5), // Last 5 messages for context
		})

		aiSuggestions.value = response.message?.suggestions || []
	} catch (error) {
		console.error("Failed to get AI suggestions:", error)
	}
}

const applySuggestion = (suggestion) => {
	// This would be handled by the MessageInput component
	// For now, we'll just clear the suggestion
	aiSuggestions.value = aiSuggestions.value.filter(
		(s) => s.id !== suggestion.id,
	)
}

const generateAIResponse = async (userMessage) => {
	try {
		// Show typing indicator for AI Assistant
		handleTypingStartAI()

		const response = await call(
			"mkaguzi.chat_system.api.generate_ai_response",
			{
				room: props.room.name,
				user_message: userMessage,
				context: messages.value.slice(-10), // Last 10 messages for context
			},
		)

		// Stop typing indicator
		handleTypingStopAI()

		if (response.message) {
			// AI response will be added via WebSocket
			// For immediate feedback, we could add it locally
			// messages.value.push(response.message)
		}
	} catch (error) {
		console.error("Failed to generate AI response:", error)
		handleTypingStopAI()

		// Send a fallback response
		sendFallbackAIResponse()
	}
}

const handleTypingStartAI = () => {
	// Emit typing indicator for AI Assistant
	// Note: Realtime typing indicators disabled for now
	console.log("AI Assistant typing started")
}

const handleTypingStopAI = () => {
	// Stop typing indicator for AI Assistant
	// Note: Realtime typing indicators disabled for now
	console.log("AI Assistant typing stopped")
}

const sendFallbackAIResponse = async () => {
	try {
		await call(
			"mkaguzi.chat_system.doctype.chat_message.chat_message.send_ai_message",
			{
				room: props.room.name,
				content:
					"I'm sorry, I'm currently unable to process your request. Please try again later or contact support if the issue persists.",
				message_type: "Text",
				is_ai_generated: true,
			},
		)
	} catch (error) {
		console.error("Failed to send fallback AI response:", error)
	}
}

const handleTypingStart = () => {
	// Emit typing indicator to other users
	// Note: Realtime typing indicators disabled for now
	console.log("Typing started for user:", currentUser.value)
}

const handleTypingStop = () => {
	// Note: Realtime typing indicators disabled for now
	console.log("Typing stopped for user:", currentUser.value)
}

const handleRoomUpdated = (updatedData) => {
	emit("room-updated", updatedData)
}

// Helper methods
const getRoomIcon = (roomType) => {
	const icons = {
		Direct: Users,
		Group: Users,
		"Audit Room": FileText,
		Department: Building,
		"Finding Room": AlertTriangle,
	}
	return icons[roomType] || MessageCircle
}

const getRoomTypeColor = (roomType) => {
	const colors = {
		Direct: "bg-blue-100 text-blue-600",
		Group: "bg-green-100 text-green-600",
		"Audit Room": "bg-purple-100 text-purple-600",
		Department: "bg-orange-100 text-orange-600",
		"Finding Room": "bg-red-100 text-red-600",
	}
	return colors[roomType] || "bg-gray-100 text-gray-600"
}

const getRoomTypeLabel = (roomType) => {
	const labels = {
		Direct: "Direct Message",
		Group: "Group Chat",
		"Audit Room": "Audit Room",
		Department: "Department Chat",
		"Finding Room": "Finding Discussion",
	}
	return labels[roomType] || roomType
}

// WebSocket event handlers - Optimized for performance
const setupRealtimeHandlers = () => {
	try {
		// Import WebSocket service dynamically to avoid issues
		import('@/services/WebSocketService').then((module) => {
			const webSocketService = module.default

			// Connect to WebSocket
			webSocketService.connect(currentUser.value, null)

			// Handle new messages
			webSocketService.on('message', (data) => {
				if (data.room === props.room.name) {
					// Add to cache
					addToCache(data)
					// Add to messages if not already present
					const existingIndex = messages.value.findIndex(m => m.name === data.id || m.id === data.id)
					if (existingIndex === -1) {
						messages.value.push(data)
					}
				}
			})

			// Handle message updates
			webSocketService.on('messageStatus', (data) => {
				const message = messages.value.find(m => m.name === data.id || m.id === data.id)
				if (message) {
					message.read_by = data.read_by || message.read_by
					message.delivered_to = data.delivered_to || message.delivered_to
				}
			})

			// Handle typing indicators
			webSocketService.on('typing', (data) => {
				if (data.room === props.room.name && data.user !== currentUser.value) {
					if (data.isTyping) {
						if (!typingUsers.value.includes(data.user)) {
							typingUsers.value.push(data.user)
						}
					} else {
						typingUsers.value = typingUsers.value.filter(u => u !== data.user)
					}
				}
			})

			// Join room for real-time updates
			webSocketService.joinRoom(props.room.name)
		}).catch(error => {
			console.warn('WebSocket service not available:', error)
		})
	} catch (error) {
		console.warn('Failed to setup realtime handlers:', error)
	}
}

const cleanupRealtimeHandlers = () => {
	console.log("Realtime handlers cleanup (disabled for now)")
	// TODO: Implement proper realtime cleanup
}

// Watchers
watch(
	() => props.room,
	(newRoom, oldRoom) => {
		if (newRoom?.name !== oldRoom?.name) {
			// Clear cache for new room
			clearCache()
			// Reset state
			messages.value = []
			typingUsers.value = []
			// Reload messages
			messagesResource.reload()
			if (newRoom.ai_enabled) {
				aiModelResource.reload()
			}
		}
	},
	{ immediate: true },
)

watch(searchQuery, (newQuery) => {
	if (!newQuery.trim()) {
		messagesResource.reload()
	}
})

// Lifecycle
onMounted(async () => {
	// Initialize current user from session
	try {
		const sessionResource = createResource({
			url: "frappe.auth.get_logged_user",
			auto: true,
		})
		await sessionResource.promise
		currentUser.value = sessionResource.data
	} catch (error) {
		console.warn("Could not get current user, using default")
		currentUser.value = "Administrator"
	}

	setupRealtimeHandlers()
})

onUnmounted(() => {
	cleanupRealtimeHandlers()
})

// Expose methods for parent components (like ChatPage)
defineExpose({
	handleSendMessage
})
</script>

<style scoped>
/* Import the theme styles */
@import '@/styles/chat-theme.css';

/* Component-specific styles that complement the theme */
.chat-container {
  /* Inherits theme colors from CSS custom properties */
}

/* Ensure smooth transitions for theme changes */
* {
  transition-property: background-color, border-color, color;
  transition-duration: 200ms;
  transition-timing-function: ease;
}
</style>