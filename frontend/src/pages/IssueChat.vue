<template>
  <div class="h-screen flex bg-gray-50">
    <!-- Sidebar with Chat Rooms -->
    <div class="w-80 bg-white border-r border-gray-200 flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h1 class="text-xl font-semibold text-gray-900">Issue Chat</h1>
          <Button
            variant="outline"
            size="sm"
            @click="showCreateRoomModal = true"
          >
            <Plus class="w-4 h-4 mr-2" />
            New Room
          </Button>
        </div>
      </div>

      <!-- Search -->
      <div class="p-4 border-b border-gray-200">
        <div class="relative">
          <Search class="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search rooms..."
            class="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <!-- Chat Rooms List -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="loading" class="p-4 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-sm text-gray-500 mt-2">Loading chat rooms...</p>
        </div>

        <div v-else-if="chatRooms.length === 0" class="p-8 text-center">
          <MessageCircle class="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">No chat rooms yet</h3>
          <p class="text-gray-500 mb-4">Create your first chat room to start collaborating on audit issues.</p>
          <Button @click="showCreateRoomModal = true">
            <Plus class="w-4 h-4 mr-2" />
            Create Room
          </Button>
        </div>

        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="room in filteredRooms"
            :key="room.name"
            @click="selectRoom(room)"
            :class="[
              'p-4 cursor-pointer hover:bg-gray-50 transition-colors',
              selectedRoom?.name === room.name ? 'bg-blue-50 border-r-2 border-blue-500' : ''
            ]"
          >
            <div class="flex items-start space-x-3">
              <!-- Room Avatar -->
              <div class="relative">
                <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                  <component :is="getRoomIcon(room.room_type)" class="w-5 h-5 text-blue-600" />
                </div>
                <!-- Unread indicator -->
                <div
                  v-if="room.unread_count > 0"
                  class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center"
                >
                  {{ room.unread_count > 99 ? '99+' : room.unread_count }}
                </div>
              </div>

              <!-- Room Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <h3 class="text-sm font-medium text-gray-900 truncate">{{ room.room_name }}</h3>
                  <span v-if="room.last_activity" class="text-xs text-gray-500">
                    {{ formatTime(room.last_activity) }}
                  </span>
                </div>
                <p class="text-sm text-gray-500 truncate mt-1">
                  {{ getLastMessagePreview(room) }}
                </p>
                <div class="flex items-center space-x-2 mt-1">
                  <span class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">
                    {{ getRoomTypeLabel(room.room_type) }}
                  </span>
                  <span v-if="room.related_document" class="text-xs text-blue-600">
                    Linked to {{ room.related_document.split(' ').pop() }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col">
      <div v-if="!selectedRoom" class="flex-1 flex items-center justify-center bg-gray-50">
        <div class="text-center">
          <MessageCircle class="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 class="text-2xl font-semibold text-gray-900 mb-2">Select a chat room</h2>
          <p class="text-gray-500">Choose a room from the sidebar to start chatting about audit issues.</p>
        </div>
      </div>

      <IssueChatRoom
        v-else
        :room="selectedRoom"
        @room-updated="handleRoomUpdated"
        class="flex-1"
      />
    </div>

    <!-- Create Room Modal -->
    <Dialog v-model="showCreateRoomModal" :options="{ title: 'Create Chat Room' }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Room Name</label>
            <input
              type="text"
              v-model="newRoom.name"
              placeholder="Enter room name..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Room Type</label>
            <select
              v-model="newRoom.type"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="general">General Discussion</option>
              <option value="followup">Follow-up Discussion</option>
              <option value="audit">Audit Team</option>
              <option value="department">Department</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
            <textarea
              v-model="newRoom.description"
              placeholder="Describe the purpose of this chat room..."
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Add Participants</label>
            <input
              type="text"
              v-model="participantSearch"
              placeholder="Search users..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              @input="searchUsers"
            />
            <div v-if="userSearchResults.length > 0" class="mt-2 max-h-32 overflow-y-auto border border-gray-200 rounded-lg">
              <div
                v-for="user in userSearchResults"
                :key="user.name"
                @click="addParticipant(user)"
                class="p-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
              >
                {{ user.full_name || user.name }}
              </div>
            </div>
            <div v-if="newRoom.participants.length > 0" class="mt-2 flex flex-wrap gap-2">
              <span
                v-for="participant in newRoom.participants"
                :key="participant"
                class="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
              >
                {{ participant }}
                <X class="w-3 h-3 ml-1 cursor-pointer" @click="removeParticipant(participant)" />
              </span>
            </div>
          </div>
        </div>
      </template>

      <template #actions>
        <Button variant="outline" @click="showCreateRoomModal = false">Cancel</Button>
        <Button @click="createRoom" :disabled="!newRoom.name.trim()">Create Room</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import IssueChatRoom from "@/components/issue_chat/IssueChatRoom.vue"
import { Button, Dialog } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	AlertTriangle,
	Building,
	FileText,
	MessageCircle,
	Plus,
	Search,
	Users,
	X,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

// Reactive data
const chatRooms = ref([])
const selectedRoom = ref(null)
const searchQuery = ref("")
const loading = ref(false)
const showCreateRoomModal = ref(false)
const newRoom = ref({
	name: "",
	type: "general",
	description: "",
	participants: [],
})
const participantSearch = ref("")
const userSearchResults = ref([])

// Computed
const filteredRooms = computed(() => {
	if (!searchQuery.value) return chatRooms.value

	const query = searchQuery.value.toLowerCase()
	return chatRooms.value.filter(
		(room) =>
			room.room_name.toLowerCase().includes(query) ||
			room.description?.toLowerCase().includes(query),
	)
})

// Resources
const chatRoomsResource = createResource({
	url: "mkaguzi.issue_chat.api.chat.get_chat_rooms",
	auto: true,
	onSuccess: (data) => {
		chatRooms.value = data.chat_rooms || []
	},
	onError: (error) => {
		console.error("Failed to load chat rooms:", error)
	},
})

const createRoomResource = createResource({
	url: "mkaguzi.issue_chat.api.chat.create_chat_room",
	onSuccess: (data) => {
		if (data.success) {
			chatRoomsResource.reload()
			showCreateRoomModal.value = false
			resetNewRoom()
		}
	},
	onError: (error) => {
		console.error("Failed to create room:", error)
	},
})

const searchUsersResource = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "User",
		fields: ["name", "full_name", "email"],
		filters: { enabled: 1 },
	},
	onSuccess: (data) => {
		userSearchResults.value = data || []
	},
})

// Methods
const selectRoom = (room) => {
	selectedRoom.value = room
	// Mark messages as read when room is selected
	markRoomAsRead(room.name)
}

const getRoomIcon = (roomType) => {
	const icons = {
		general: MessageCircle,
		followup: AlertTriangle,
		audit: FileText,
		department: Building,
	}
	return icons[roomType] || MessageCircle
}

const getRoomTypeLabel = (roomType) => {
	const labels = {
		general: "General",
		followup: "Follow-up",
		audit: "Audit",
		department: "Department",
	}
	return labels[roomType] || roomType
}

const getLastMessagePreview = (room) => {
	// This would come from the API response
	// For now, return a placeholder
	return room.description || "No messages yet"
}

const formatTime = (timestamp) => {
	if (!timestamp) return ""

	const date = new Date(timestamp)
	const now = new Date()
	const diff = now - date

	if (diff < 60000) return "now" // less than 1 minute
	if (diff < 3600000) return `${Math.floor(diff / 60000)}m` // minutes
	if (diff < 86400000) return `${Math.floor(diff / 3600000)}h` // hours
	if (diff < 604800000) return `${Math.floor(diff / 86400000)}d` // days

	return date.toLocaleDateString()
}

const createRoom = () => {
	if (!newRoom.value.name.trim()) return

	createRoomResource.update({
		params: {
			room_name: newRoom.value.name,
			room_type: newRoom.value.type,
			description: newRoom.value.description,
			participants: newRoom.value.participants,
		},
	})
	createRoomResource.fetch()
}

const resetNewRoom = () => {
	newRoom.value = {
		name: "",
		type: "general",
		description: "",
		participants: [],
	}
	participantSearch.value = ""
	userSearchResults.value = []
}

const searchUsers = () => {
	if (participantSearch.value.length < 2) {
		userSearchResults.value = []
		return
	}

	searchUsersResource.update({
		params: {
			doctype: "User",
			fields: ["name", "full_name", "email"],
			filters: {
				enabled: 1,
				full_name: ["like", `%${participantSearch.value}%`],
			},
			limit: 10,
		},
	})
	searchUsersResource.fetch()
}

const addParticipant = (user) => {
	if (!newRoom.value.participants.includes(user.name)) {
		newRoom.value.participants.push(user.name)
	}
	participantSearch.value = ""
	userSearchResults.value = []
}

const removeParticipant = (userName) => {
	newRoom.value.participants = newRoom.value.participants.filter(
		(p) => p !== userName,
	)
}

const markRoomAsRead = async (roomName) => {
	try {
		await createResource({
			url: "mkaguzi.issue_chat.doctype.issue_chat_read_receipt.issue_chat_read_receipt.mark_message_read",
			params: { room: roomName },
		}).fetch()
	} catch (error) {
		console.error("Failed to mark room as read:", error)
	}
}

const handleRoomUpdated = (updatedRoom) => {
	// Update the room in the list
	const index = chatRooms.value.findIndex((r) => r.name === updatedRoom.name)
	if (index !== -1) {
		chatRooms.value[index] = { ...chatRooms.value[index], ...updatedRoom }
	}
}

// Lifecycle
onMounted(() => {
	chatRoomsResource.fetch()
})
</script>