<template>
  <div class="w-72 bg-white border-l border-gray-200 flex flex-col h-full">
    <div class="p-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-gray-900">Participants</h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Online/Offline Toggle -->
    <div class="flex border-b border-gray-100">
      <button 
        @click="activeFilter = 'all'"
        :class="['flex-1 py-2 text-xs font-medium', activeFilter === 'all' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500']"
      >
        All ({{ participants.length }})
      </button>
      <button 
        @click="activeFilter = 'online'"
        :class="['flex-1 py-2 text-xs font-medium', activeFilter === 'online' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500']"
      >
        Online ({{ onlineCount }})
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-4 space-y-3">
      <div 
        v-for="participant in filteredParticipants"
        :key="participant.user"
        class="flex items-center space-x-3 group"
      >
        <div class="relative">
          <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
            <span class="text-xs font-medium text-gray-600">
              {{ getInitials(participant.user) }}
            </span>
          </div>
          <!-- Online indicator -->
          <div 
            v-if="isOnline(participant.user)"
            class="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-white"
          ></div>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">
            {{ participant.user_name || participant.user }}
          </p>
          <div class="flex items-center space-x-2">
            <p class="text-xs text-gray-500 capitalize">{{ participant.role || 'member' }}</p>
            <span 
              v-if="isTyping(participant.user)" 
              class="text-xs text-blue-500 animate-pulse"
            >
              typing...
            </span>
          </div>
        </div>
        
        <!-- Actions (on hover) -->
        <div class="opacity-0 group-hover:opacity-100 transition-opacity">
          <Dropdown :options="getParticipantActions(participant)">
            <button class="p-1 hover:bg-gray-100 rounded">
              <MoreVertical class="w-4 h-4 text-gray-400" />
            </button>
          </Dropdown>
        </div>
      </div>

      <div v-if="filteredParticipants.length === 0" class="text-center py-8 text-sm text-gray-500">
        No {{ activeFilter === 'online' ? 'online ' : '' }}participants
      </div>
    </div>

    <!-- Add Participant -->
    <div class="p-4 border-t border-gray-200">
      <Button 
        variant="outline" 
        class="w-full" 
        size="sm"
        @click="$emit('add-participant')"
      >
        <UserPlus class="w-4 h-4 mr-2" />
        Add Participant
      </Button>
    </div>
  </div>
</template>

<script setup>
import { Button, Dropdown } from "frappe-ui"
import {
	Crown,
	MessageCircle,
	MoreVertical,
	UserMinus,
	UserPlus,
	X,
} from "lucide-vue-next"
import { computed, ref } from "vue"

const props = defineProps({
	participants: { type: Array, default: () => [] },
	onlineUsers: { type: Array, default: () => [] },
	typingUsers: { type: Array, default: () => [] },
	currentUser: { type: String, default: "" },
	isAdmin: { type: Boolean, default: false },
})

const emit = defineEmits([
	"close",
	"add-participant",
	"remove-participant",
	"make-admin",
	"direct-message",
])

const activeFilter = ref("all")

const onlineCount = computed(
	() =>
		props.participants.filter((p) => props.onlineUsers.includes(p.user)).length,
)

const filteredParticipants = computed(() => {
	if (activeFilter.value === "online") {
		return props.participants.filter((p) => props.onlineUsers.includes(p.user))
	}
	return props.participants
})

const isOnline = (user) => props.onlineUsers.includes(user)
const isTyping = (user) => props.typingUsers.includes(user)

const getInitials = (name) => {
	if (!name) return "?"
	return name
		.split(/[@\s]/)
		.map((n) => n[0])
		.join("")
		.toUpperCase()
		.slice(0, 2)
}

const getParticipantActions = (participant) => {
	const actions = [
		{
			label: "Send Message",
			icon: MessageCircle,
			onClick: () => emit("direct-message", participant),
		},
	]

	if (props.isAdmin && participant.user !== props.currentUser) {
		actions.push({
			label: participant.role === "Admin" ? "Remove Admin" : "Make Admin",
			icon: Crown,
			onClick: () => emit("make-admin", participant),
		})
		actions.push({
			label: "Remove from Room",
			icon: UserMinus,
			onClick: () => emit("remove-participant", participant),
		})
	}

	return actions
}
</script>
