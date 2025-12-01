<template>
  <div class="bg-white border-b border-gray-200 p-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div :class="['w-10 h-10 rounded-lg flex items-center justify-center', roomIconClass]">
          <component :is="roomIcon" class="w-5 h-5" />
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h2 class="text-lg font-semibold text-gray-900">{{ room.room_name }}</h2>
            <Badge v-if="room.is_ai_enabled" variant="subtle" theme="purple">
              <Bot class="w-3 h-3 mr-1" />
              AI
            </Badge>
          </div>
          <p class="text-sm text-gray-500">
            {{ room.participant_count || 0 }} members
            <span v-if="room.linked_engagement" class="ml-2">
              • Linked to <span class="text-blue-600">{{ room.linked_engagement }}</span>
            </span>
          </p>
        </div>
      </div>

      <div class="flex items-center space-x-2">
        <!-- Online count -->
        <div v-if="onlineCount > 0" class="flex items-center text-sm text-gray-500">
          <div class="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
          {{ onlineCount }} online
        </div>

        <!-- Typing indicator -->
        <div v-if="typingUsers.length > 0" class="text-sm text-blue-500 animate-pulse">
          {{ typingUsers.map(u => u.full_name || u.user).join(', ') }} typing...
        </div>

        <!-- Index Button for Engagement Rooms -->
        <Button 
          v-if="room.linked_engagement"
          variant="ghost"
          size="sm"
          @click="$emit('index-documents')"
          :loading="indexing"
          title="Index engagement documents for AI"
        >
          <Database class="w-4 h-4" />
        </Button>
        
        <!-- Participants Toggle -->
        <Button variant="ghost" size="sm" @click="$emit('show-participants')">
          <Users class="w-4 h-4" />
        </Button>
        
        <!-- Room Settings -->
        <Button variant="ghost" size="sm" @click="$emit('open-settings')">
          <Settings class="w-4 h-4" />
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button } from "frappe-ui"
import {
	Bot,
	Building,
	Database,
	FileText,
	MessageCircle,
	Settings,
	User,
	Users,
} from "lucide-vue-next"
import { computed } from "vue"

const props = defineProps({
	room: { type: Object, required: true },
	isAiEnabled: { type: Boolean, default: false },
	onlineCount: { type: Number, default: 0 },
	typingUsers: { type: Array, default: () => [] },
	indexing: { type: Boolean, default: false },
})

defineEmits([
	"toggle-ai",
	"open-settings",
	"show-participants",
	"index-documents",
])

const roomIcon = computed(() => {
	const icons = {
		Engagement: FileText,
		Group: Users,
		Direct: MessageCircle,
		Private: User,
		Department: Building,
	}
	return icons[props.room.room_type] || MessageCircle
})

const roomIconClass = computed(() => {
	const classes = {
		Engagement: "bg-blue-100 text-blue-600",
		Group: "bg-green-100 text-green-600",
		Direct: "bg-purple-100 text-purple-600",
		Private: "bg-purple-100 text-purple-600",
	}
	return classes[props.room.room_type] || "bg-gray-100 text-gray-600"
})
</script>
