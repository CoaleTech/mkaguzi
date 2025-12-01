<template>
  <div class="flex h-full bg-gray-50">
    <!-- Sidebar -->
    <ChatSidebar
      :rooms="filteredRooms"
      :users="users"
      :selected-room="selectedRoom"
      :active-tab="activeTab"
      :search-query="searchQuery"
      :loading="roomsLoading"
      :users-loading="usersLoading"
      :is-ai-enabled="isAiEnabledForRoom"
      :selected-model="aiSettings?.selected_model"
      :typing-users="roomTypingUsers"
      :online-users="onlineUsers"
      @select-room="selectRoom"
      @start-dm="startDirectMessage"
      @create-room="showCreateRoomModal = true"
      @update:activeTab="activeTab = $event"
      @update:searchQuery="searchQuery = $event"
    />

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col bg-white">
      <template v-if="selectedRoom">
        <!-- Header -->
        <ChatHeader
          :room="selectedRoom"
          :is-ai-enabled="isAiEnabledForRoom"
          :online-count="onlineUsers.length"
          :typing-users="typingUsers"
          @open-settings="showSettingsPanel = true"
          @show-participants="showParticipantsPanel = !showParticipantsPanel"
        />

        <!-- Messages Area -->
        <div class="flex-1 flex overflow-hidden">
          <div class="flex-1 flex flex-col">
            <ChatMessageList
              :messages="messages"
              :current-user="currentUser"
              :loading="messagesLoading"
              :has-more="hasMoreMessages"
              :typing-users="typingUsers"
              :is-ai-enabled="isAiEnabledForRoom"
              @load-more="loadMoreMessages"
              @reply="handleReply"
              @edit="handleEdit"
              @delete="handleDelete"
            />

            <!-- Input -->
            <ChatMessageInput
              :replying-to="replyingTo"
              :is-ai-enabled="isAiEnabledForRoom"
              :loading="sendingMessage"
              @send="sendMessage"
              @cancel-reply="replyingTo = null"
              @typing="handleTyping"
            />
          </div>

          <!-- Participants Panel (Collapsible) -->
          <transition name="slide">
            <ChatParticipants
              v-if="showParticipantsPanel"
              :participants="participants"
              :online-users="onlineUsers"
              :typing-users="typingUsers.map(u => u.user)"
              :current-user="currentUser"
              :is-admin="isRoomAdmin"
              @close="showParticipantsPanel = false"
              @add-participant="showAddParticipantModal = true"
              @remove-participant="removeParticipant"
              @make-admin="toggleParticipantAdmin"
              @direct-message="startDirectMessage"
            />
          </transition>
        </div>
      </template>

      <!-- Empty State -->
      <div v-else class="flex-1 flex items-center justify-center text-gray-500">
        <div class="text-center">
          <MessageSquare class="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">No room selected</h3>
          <p class="text-sm">Select a room from the sidebar or create a new one</p>
        </div>
      </div>
    </div>

    <!-- Create Room Modal -->
    <Dialog v-model="showCreateRoomModal" :options="{ title: 'Create Chat Room' }">
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            v-model="newRoom.room_name"
            label="Room Name"
            placeholder="Enter room name"
            required
          />
          <FormControl
            v-model="newRoom.description"
            label="Description"
            type="textarea"
            placeholder="Optional description"
          />
          <div class="flex items-center space-x-3">
            <Checkbox v-model="newRoom.is_ai_enabled" />
            <span class="text-sm text-gray-700">Enable AI Assistant</span>
          </div>
          <FormControl
            v-model="newRoom.engagement"
            label="Link to Engagement"
            type="link"
            :options="{ doctype: 'Audit Engagement' }"
          />
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showCreateRoomModal = false">Cancel</Button>
        <Button variant="solid" @click="createRoom" :loading="creatingRoom">Create Room</Button>
      </template>
    </Dialog>

    <!-- Add Participant Modal -->
    <Dialog v-model="showAddParticipantModal" :options="{ title: 'Add Participant' }">
      <template #body-content>
        <FormControl
          v-model="newParticipant.user"
          label="User"
          type="link"
          :options="{ doctype: 'User' }"
          required
        />
        <FormControl
          v-model="newParticipant.role"
          label="Role"
          type="select"
          :options="['Member', 'Admin']"
          class="mt-4"
        />
      </template>
      <template #actions>
        <Button variant="outline" @click="showAddParticipantModal = false">Cancel</Button>
        <Button variant="solid" @click="addParticipant" :loading="addingParticipant">Add</Button>
      </template>
    </Dialog>

    <!-- Edit Message Modal -->
    <Dialog v-model="showEditModal" :options="{ title: 'Edit Message' }">
      <template #body-content>
        <FormControl
          v-model="editingMessage.content"
          type="textarea"
          rows="4"
        />
      </template>
      <template #actions>
        <Button variant="outline" @click="showEditModal = false">Cancel</Button>
        <Button variant="solid" @click="saveEditedMessage" :loading="savingEdit">Save</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Button, Checkbox, Dialog, FormControl, call } from "frappe-ui"
import { MessageSquare } from "lucide-vue-next"
import { computed, onMounted, provide, ref, watch } from "vue"

import {
	ChatHeader,
	ChatMessageInput,
	ChatMessageList,
	ChatParticipants,
	ChatSidebar,
	ChatTypingIndicator,
} from "./index"

import { useChatRealtime } from "../../composables/useChatRealtime"
import { useMkaguziChat } from "../../composables/useMkaguziChat"

const props = defineProps({
	initialRoomName: { type: String, default: null },
	engagementFilter: { type: String, default: null },
})

const emit = defineEmits(["room-changed"])

// Core chat composable
const {
	rooms,
	selectedRoom,
	messages,
	participants,
	users,
	aiSettings,
	roomsLoading,
	messagesLoading,
	usersLoading,
	hasMoreMessages,
	sendingMessage,
	currentUser,
	fetchRooms,
	fetchUsers,
	selectRoom,
	sendMessage: sendChatMessage,
	loadMoreMessages,
	deleteMessage: deleteChatMessage,
	editMessage: editChatMessage,
	addReaction,
	removeReaction,
	getOrCreateDM,
	isAiEnabled,
	loadSettings,
} = useMkaguziChat()

// Real-time composable
const roomName = computed(() => selectedRoom.value?.name)
const currentUserRef = computed(() => currentUser.value)
const {
	isConnected,
	typingUsers,
	onlineUsers,
	sendTyping,
	emitMessageCreated,
	emitMessageUpdated,
	emitMessageDeleted,
	on: onRealtimeEvent,
	joinRoom,
	leaveRoom,
} = useChatRealtime(roomName, currentUserRef)

// UI State
const showParticipantsPanel = ref(false)
const showCreateRoomModal = ref(false)
const showAddParticipantModal = ref(false)
const showEditModal = ref(false)
const showSettingsPanel = ref(false)
const replyingTo = ref(null)
const activeTab = ref("all")
const searchQuery = ref("")

// Form State
const newRoom = ref({
	room_name: "",
	description: "",
	is_ai_enabled: true,
	engagement: null,
})
const newParticipant = ref({
	user: "",
	role: "Member",
})
const editingMessage = ref({
	name: "",
	content: "",
})

// Loading states
const creatingRoom = ref(false)
const addingParticipant = ref(false)
const savingEdit = ref(false)

// Computed
const engagements = computed(() => {
	// Get unique engagements from rooms
	const engMap = new Map()
	rooms.value.forEach((room) => {
		if (room.engagement) {
			engMap.set(room.engagement, room.engagement_name || room.engagement)
		}
	})
	return Array.from(engMap, ([value, label]) => ({ value, label }))
})

const isRoomAdmin = computed(() => {
	if (!selectedRoom.value || !currentUser.value) return false
	const participant = participants.value.find(
		(p) => p.user === currentUser.value,
	)
	return (
		participant?.role === "Admin" ||
		selectedRoom.value.created_by === currentUser.value
	)
})

// Combined AI enabled check (global + room level)
const isAiEnabledForRoom = computed(() => {
	return isAiEnabled.value && selectedRoom.value?.is_ai_enabled !== false
})

// Filtered rooms based on tab and search
const filteredRooms = computed(() => {
	let filtered = rooms.value

	// Filter by tab
	if (activeTab.value === "dm") {
		filtered = filtered.filter((r) => r.is_dm) // Only true DMs
	} else if (activeTab.value === "engagement") {
		filtered = filtered.filter((r) => r.room_type === "Engagement")
	} else if (activeTab.value === "group") {
		filtered = filtered.filter((r) => r.room_type === "Group")
	}

	// Filter by search query
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		filtered = filtered.filter(
			(r) =>
				r.room_name?.toLowerCase().includes(query) ||
				r.linked_engagement?.toLowerCase().includes(query),
		)
	}

	return filtered
})

// Transform typingUsers for sidebar (by room)
const roomTypingUsers = computed(() => {
	const result = {}
	// typingUsers is an array of users typing in the current room
	if (selectedRoom.value && typingUsers.value.length > 0) {
		result[selectedRoom.value.name] = typingUsers.value
	}
	return result
})

// Provide to child components
provide("currentUser", currentUser)
provide("isConnected", isConnected)

// Methods
const handleTyping = () => {
	sendTyping(true)
}

const handleReply = (message) => {
	replyingTo.value = message
}

const handleEdit = (message) => {
	editingMessage.value = {
		name: message.name,
		content: message.content,
	}
	showEditModal.value = true
}

const handleDelete = async (message) => {
	if (!confirm("Are you sure you want to delete this message?")) return

	try {
		await deleteChatMessage(message.name)
		emitMessageDeleted(message.name)
		window.frappe?.show_alert("Message deleted", 5, "green")
	} catch (error) {
		toast({ title: "Failed to delete message", variant: "error" })
	}
}

const handleAddReaction = async ({ message, emoji }) => {
	try {
		await addReaction(message.name, emoji)
	} catch (error) {
		console.error("Failed to add reaction:", error)
	}
}

const sendMessage = async ({ content, isAiPrompt }) => {
	if (!content.trim()) return

	// Stop typing indicator
	sendTyping(false)

	try {
		const message = await sendChatMessage(
			content,
			replyingTo.value?.name,
			isAiPrompt,
		)

		// Clear reply
		replyingTo.value = null

		// Emit real-time event
		emitMessageCreated(message)
	} catch (error) {
		window.frappe?.show_alert("Failed to send message", 5, "red")
	}
}

const saveEditedMessage = async () => {
	if (!editingMessage.value.content.trim()) return

	savingEdit.value = true
	try {
		const updated = await editChatMessage(
			editingMessage.value.name,
			editingMessage.value.content,
		)
		emitMessageUpdated(updated)
		showEditModal.value = false
		window.frappe?.show_alert("Message updated", 5, "green")
	} catch (error) {
		window.frappe?.show_alert("Failed to update message", 5, "red")
	} finally {
		savingEdit.value = false
	}
}

const createRoom = async () => {
	if (!newRoom.value.room_name.trim()) {
		window.frappe?.show_alert("Room name is required", 5, "red")
		return
	}

	creatingRoom.value = true
	try {
		const room = await call(
			"mkaguzi.mkaguzi.api.chat.create_room",
			newRoom.value,
		)

		await fetchRooms()
		selectRoom(room.message)
		showCreateRoomModal.value = false

		// Reset form
		newRoom.value = {
			room_name: "",
			description: "",
			is_ai_enabled: true,
			engagement: null,
		}

		window.frappe?.show_alert("Room created successfully", 5, "green")
	} catch (error) {
		window.frappe?.show_alert(
			error.message || "Failed to create room",
			5,
			"red",
		)
	} finally {
		creatingRoom.value = false
	}
}

const addParticipant = async () => {
	if (!newParticipant.value.user) {
		window.frappe?.show_alert("User is required", 5, "red")
		return
	}

	addingParticipant.value = true
	try {
		await call("mkaguzi.mkaguzi.api.chat.add_participant", {
			room_name: selectedRoom.value.name,
			user: newParticipant.value.user,
			role: newParticipant.value.role,
		})

		// Refresh participants
		await selectRoom(selectedRoom.value)
		showAddParticipantModal.value = false

		// Reset form
		newParticipant.value = { user: "", role: "Member" }

		window.frappe?.show_alert("Participant added", 5, "green")
	} catch (error) {
		window.frappe?.show_alert(
			error.message || "Failed to add participant",
			5,
			"red",
		)
	} finally {
		addingParticipant.value = false
	}
}

const removeParticipant = async (participant) => {
	if (
		!confirm(
			`Remove ${participant.user_name || participant.user} from this room?`,
		)
	)
		return

	try {
		await call("mkaguzi.mkaguzi.api.chat.remove_participant", {
			room_name: selectedRoom.value.name,
			user: participant.user,
		})

		await selectRoom(selectedRoom.value)
		window.frappe?.show_alert("Participant removed", 5, "green")
	} catch (error) {
		window.frappe?.show_alert(
			error.message || "Failed to remove participant",
			5,
			"red",
		)
	}
}

const toggleParticipantAdmin = async (participant) => {
	const newRole = participant.role === "Admin" ? "Member" : "Admin"

	try {
		await call("mkaguzi.mkaguzi.api.chat.update_participant_role", {
			room_name: selectedRoom.value.name,
			user: participant.user,
			role: newRole,
		})

		await selectRoom(selectedRoom.value)
		window.frappe?.show_alert(
			`${participant.user_name || participant.user} is now ${newRole}`,
			5,
			"green",
		)
	} catch (error) {
		window.frappe?.show_alert(
			error.message || "Failed to update role",
			5,
			"red",
		)
	}
}

const startDirectMessage = async (user) => {
	const targetUser = user.email || user.user || user
	if (!targetUser || targetUser === currentUser.value) {
		return
	}

	try {
		// Get or create DM room (this already refreshes rooms)
		const dmRoom = await getOrCreateDM(targetUser)
		if (dmRoom) {
			// No need to refresh rooms again - getOrCreateDM already did this
			await selectRoom(dmRoom)

			window.frappe?.show_alert(
				`Direct message with ${user.full_name || user.user_name || targetUser}`,
				5,
				"green",
			)
		}
	} catch (error) {
		console.error("Failed to start DM:", error)
		const errorMessage =
			error?.message ||
			(typeof error === "string" ? error : "Failed to start direct message")
		window.frappe?.show_alert(errorMessage, 5, "red")
	}
}

// Real-time event handlers
onRealtimeEvent("messageCreated", (data) => {
	// Check if message is for current room
	console.log("messageCreated callback called with data:", data)
	if (selectedRoom.value && data.room === selectedRoom.value.name) {
		console.log("Message is for current room, adding to messages")
		// Check if message already exists (avoid duplicates)
		const exists = messages.value.some((m) => m.name === data.message?.name)
		if (!exists && data.message) {
			console.log("Adding message to messages array:", data.message)
			messages.value.push(data.message)
		} else {
			console.log("Message already exists or no message data")
		}
	} else {
		console.log(
			"Message not for current room:",
			data.room,
			"current room:",
			selectedRoom.value?.name,
		)
	}
})

onRealtimeEvent("messageUpdated", (data) => {
	if (selectedRoom.value && data.room === selectedRoom.value.name) {
		const idx = messages.value.findIndex((m) => m.name === data.message?.name)
		if (idx !== -1 && data.message) {
			messages.value[idx] = { ...messages.value[idx], ...data.message }
		}
	}
})

onRealtimeEvent("messageDeleted", (data) => {
	if (selectedRoom.value && data.room === selectedRoom.value.name) {
		messages.value = messages.value.filter((m) => m.name !== data.message_name)
	}
})

// Watch for room changes
watch(selectedRoom, async (newRoom, oldRoom) => {
	if (newRoom) {
		// Leave previous room
		if (oldRoom) {
			await leaveRoom()
		}

		// Join new room for real-time updates
		await joinRoom()

		emit("room-changed", newRoom)
	}
})

// Initial load
onMounted(async () => {
	await fetchRooms()
	await fetchUsers() // Load users for DM functionality
	await loadSettings() // Load AI settings

	// Select initial room if provided
	if (props.initialRoomName) {
		const room = rooms.value.find((r) => r.name === props.initialRoomName)
		if (room) {
			selectRoom(room)
		}
	}
})
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
