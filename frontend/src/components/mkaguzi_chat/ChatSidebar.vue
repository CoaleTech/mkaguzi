<template>
  <div class="w-80 bg-white border-r border-gray-200 flex flex-col h-full">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <MessageCircle class="w-6 h-6 text-blue-600" />
          <h1 class="text-xl font-semibold text-gray-900">Mkaguzi Chat</h1>
        </div>
        <Button variant="ghost" size="sm" @click="$emit('create-room')">
          <Plus class="w-5 h-5" />
        </Button>
      </div>

      <!-- AI Status Indicator -->
      <div v-if="isAiEnabled" class="mt-3 flex items-center space-x-2 text-sm">
        <div class="flex items-center space-x-1 text-green-600">
          <Bot class="w-4 h-4" />
          <span>AI Enabled</span>
        </div>
        <span class="text-gray-400">•</span>
        <span class="text-gray-500 text-xs truncate">{{ modelDisplayName }}</span>
      </div>
    </div>

    <!-- Room Type Tabs -->
    <div class="flex border-b border-gray-200">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="$emit('update:activeTab', tab.key)"
        :class="[
          'flex-1 py-2 text-sm font-medium transition-colors',
          activeTab === tab.key 
            ? 'text-blue-600 border-b-2 border-blue-600' 
            : 'text-gray-500 hover:text-gray-700'
        ]"
      >
        <div class="flex items-center justify-center space-x-1">
          <component :is="tab.icon" class="w-4 h-4" />
          <span>{{ tab.label }}</span>
          <Badge v-if="getCount(tab.key)" variant="subtle" size="sm">
            {{ getCount(tab.key) }}
          </Badge>
        </div>
      </button>
    </div>

    <!-- Search -->
    <div class="p-3 border-b border-gray-100">
      <div class="relative">
        <Search class="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          :value="searchQuery"
          @input="$emit('update:searchQuery', $event.target.value)"
          :placeholder="activeTab === 'dm' ? 'Search users...' : 'Search rooms...'"
          class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-y-auto">
      <!-- DM Tab: Show Users -->
      <template v-if="activeTab === 'dm'">
        <div v-if="usersLoading" class="p-4 text-center">
          <Loader2 class="w-6 h-6 animate-spin text-blue-600 mx-auto" />
          <p class="text-sm text-gray-500 mt-2">Loading users...</p>
        </div>

        <div v-else-if="filteredUsers.length === 0 && !searchQuery" class="p-8 text-center">
          <Users class="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 class="text-sm font-medium text-gray-900 mb-1">No users found</h3>
          <p class="text-xs text-gray-500">Try adjusting your search</p>
        </div>

        <div v-else class="divide-y divide-gray-100">
          <!-- Existing DM Rooms -->
          <div v-if="dmRooms.length > 0" class="p-3 bg-gray-50">
            <h4 class="text-xs font-medium text-gray-700 uppercase tracking-wide mb-2">Recent Conversations</h4>
            <div v-for="room in dmRooms" :key="room.name" @click="$emit('select-room', room)" class="p-2 rounded-lg hover:bg-white cursor-pointer mb-1">
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center text-white font-medium text-sm">
                  {{ getDMInitials(room) }}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">{{ getDMDisplayName(room) }}</p>
                  <p class="text-xs text-gray-500">Direct message</p>
                </div>
              </div>
            </div>
          </div>

          <!-- All Users -->
          <div class="p-3">
            <h4 class="text-xs font-medium text-gray-700 uppercase tracking-wide mb-2">Start New Conversation</h4>
            <div v-for="user in filteredUsers" :key="user.email" @click="$emit('start-dm', user)" class="p-2 rounded-lg hover:bg-gray-50 cursor-pointer mb-1">
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-medium text-sm">
                  {{ getUserInitials(user) }}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900">{{ user.full_name || user.email }}</p>
                  <p class="text-xs text-gray-500">{{ user.email }}</p>
                </div>
                <div v-if="isUserOnline(user.email)" class="w-2 h-2 bg-green-500 rounded-full"></div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Other Tabs: Show Rooms -->
      <template v-else>
        <div v-if="loading" class="p-4 text-center">
          <Loader2 class="w-6 h-6 animate-spin text-blue-600 mx-auto" />
          <p class="text-sm text-gray-500 mt-2">Loading rooms...</p>
        </div>

        <div v-else-if="rooms.length === 0" class="p-8 text-center">
          <MessageCircle class="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 class="text-sm font-medium text-gray-900 mb-1">
            {{ activeTab === 'dm' ? 'No direct messages' : 'No chat rooms' }}
          </h3>
          <p class="text-xs text-gray-500 mb-4">
            {{ activeTab === 'dm' ? 'Click on a participant to start a DM' : 'Create a new chat room to get started' }}
          </p>
          <Button v-if="activeTab !== 'dm'" size="sm" @click="$emit('create-room')">
            <Plus class="w-4 h-4 mr-1" />
            New Room
          </Button>
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div
            v-for="room in rooms"
            :key="room.name"
            @click="$emit('select-room', room)"
            :class="[
              'p-3 cursor-pointer transition-colors',
              selectedRoom?.name === room.name 
                ? 'bg-blue-50 border-l-3 border-blue-500' 
                : 'hover:bg-gray-50'
            ]"
          >
            <div class="flex items-start space-x-3">
              <!-- Room Icon / DM Avatar -->
              <div class="relative flex-shrink-0">
                <!-- DM Avatar -->
                <template v-if="room.is_dm">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center text-white font-medium text-sm">
                    {{ getDMInitials(room) }}
                  </div>
                  <!-- Online status indicator -->
                  <div v-if="isUserOnline(getDMOtherUser(room))" class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                </template>
                <!-- Regular room icon -->
                <template v-else>
                  <div :class="['w-10 h-10 rounded-lg flex items-center justify-center', getRoomIconClass(room.room_type)]">
                    <component :is="getRoomIcon(room.room_type)" class="w-5 h-5" />
                  </div>
                  <div v-if="room.is_ai_enabled" class="absolute -top-1 -right-1">
                    <div class="w-4 h-4 bg-purple-500 rounded-full flex items-center justify-center">
                      <Bot class="w-2.5 h-2.5 text-white" />
                    </div>
                  </div>
                </template>
              </div>

              <!-- Room Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <h3 class="text-sm font-medium text-gray-900 truncate">
                    {{ room.is_dm ? getDMDisplayName(room) : room.room_name }}
                  </h3>
                  <span v-if="room.last_message_time" class="text-xs text-gray-400">
                    {{ formatTime(room.last_message_time) }}
                  </span>
                </div>
                <p v-if="room.linked_engagement && !room.is_dm" class="text-xs text-blue-600 mt-0.5 truncate">
                  <FileText class="w-3 h-3 inline mr-1" />
                  {{ room.engagement_title || room.linked_engagement }}
                </p>
                <div class="flex items-center space-x-2 mt-0.5">
                  <p class="text-xs text-gray-500">
                    {{ room.is_dm ? 'Direct message' : `${room.participant_count || 0} members` }}
                  </p>
                  <!-- Typing indicator -->
                  <span v-if="typingInRoom(room.name)" class="text-xs text-blue-500 animate-pulse">
                    typing...
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- Settings Link -->
    <div class="p-3 border-t border-gray-200">
      <router-link 
        to="/settings/configuration?tab=ai"
        class="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
      >
        <Settings class="w-4 h-4" />
        <span>AI Chat Settings</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button } from "frappe-ui"
import {
	Bot,
	Building,
	FileText,
	Loader2,
	MessageCircle,
	Plus,
	Search,
	Settings,
	User,
	Users,
} from "lucide-vue-next"
import { computed, inject } from "vue"

const props = defineProps({
	rooms: { type: Array, default: () => [] },
	users: { type: Array, default: () => [] },
	selectedRoom: { type: Object, default: null },
	activeTab: { type: String, default: "all" },
	searchQuery: { type: String, default: "" },
	loading: { type: Boolean, default: false },
	usersLoading: { type: Boolean, default: false },
	isAiEnabled: { type: Boolean, default: false },
	selectedModel: { type: String, default: "" },
	typingUsers: { type: Object, default: () => ({}) }, // { roomName: [users] }
	onlineUsers: { type: Array, default: () => [] },
})

defineEmits([
	"create-room",
	"select-room",
	"start-dm",
	"update:activeTab",
	"update:searchQuery",
])

// Get current user from context
const currentUser = inject("currentUser", { value: "" })

const tabs = [
	{ key: "all", label: "All", icon: MessageCircle },
	{ key: "dm", label: "DMs", icon: User },
	{ key: "engagement", label: "Engagements", icon: FileText },
	{ key: "group", label: "Groups", icon: Users },
]

const modelDisplayName = computed(() => {
	const names = {
		"meta-llama/llama-3.1-8b-instruct:free": "Llama 3.1",
		"google/gemma-2-9b-it:free": "Gemma 2",
		"qwen/qwen-2.5-7b-instruct:free": "Qwen 2.5",
	}
	return (
		names[props.selectedModel] ||
		props.selectedModel?.split("/").pop()?.split(":")[0] ||
		"AI"
	)
})

const getCount = (tabKey) => {
	if (tabKey === "all") return props.rooms.length
	if (tabKey === "dm")
		return props.rooms.filter((r) => r.is_dm || r.room_type === "Private")
			.length
	if (tabKey === "engagement")
		return props.rooms.filter((r) => r.room_type === "Engagement").length
	if (tabKey === "group")
		return props.rooms.filter((r) => r.room_type === "Group").length
	return 0
}

const getRoomIcon = (roomType) => {
	const icons = {
		Engagement: FileText,
		Group: Users,
		Direct: MessageCircle,
		Private: User,
		Department: Building,
	}
	return icons[roomType] || MessageCircle
}

const getRoomIconClass = (roomType) => {
	const classes = {
		Engagement: "bg-blue-100 text-blue-600",
		Group: "bg-green-100 text-green-600",
		Direct: "bg-purple-100 text-purple-600",
		Private: "bg-purple-100 text-purple-600",
	}
	return classes[roomType] || "bg-gray-100 text-gray-600"
}

const formatTime = (timestamp) => {
	if (!timestamp) return ""
	const date = new Date(timestamp)
	const now = new Date()
	const diff = now - date
	if (diff < 60000) return "now"
	if (diff < 3600000) return `${Math.floor(diff / 60000)}m`
	if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`
	return date.toLocaleDateString([], { month: "short", day: "numeric" })
}

const typingInRoom = (roomName) => {
	return props.typingUsers[roomName]?.length > 0
}

// DM-specific helpers
const getDMOtherUser = (room) => {
	if (!room.participants || !currentUser.value) return ""
	const other = room.participants.find((p) => p.user !== currentUser.value)
	return other?.user || ""
}

const getDMDisplayName = (room) => {
	// Use display_name if available (from backend), fallback to participant lookup
	if (room.display_name) return room.display_name

	if (!room.participants) return room.room_name
	const other = room.participants.find((p) => p.user !== currentUser.value)
	return other?.user_name || other?.user || room.room_name
}

const getDMInitials = (room) => {
	const name = getDMDisplayName(room)
	return (
		name
			.split(" ")
			.map((n) => n[0])
			.join("")
			.toUpperCase()
			.slice(0, 2) || "?"
	)
}

const isUserOnline = (user) => {
	return props.onlineUsers.includes(user)
}

// DM-specific computed properties
const dmRooms = computed(() => {
	return props.rooms.filter((r) => r.is_dm || r.room_type === "Private")
})

const filteredUsers = computed(() => {
	let filtered = props.users

	// Filter by search query
	if (props.searchQuery) {
		const query = props.searchQuery.toLowerCase()
		filtered = filtered.filter(
			(u) =>
				u.full_name?.toLowerCase().includes(query) ||
				u.email?.toLowerCase().includes(query),
		)
	}

	return filtered
})

// User helper functions
const getUserInitials = (user) => {
	const name = user.full_name || user.email
	return (
		name
			.split(" ")
			.map((n) => n[0])
			.join("")
			.toUpperCase()
			.slice(0, 2) || "?"
	)
}
</script>

<style scoped>
.border-l-3 { border-left-width: 3px; }
</style>
