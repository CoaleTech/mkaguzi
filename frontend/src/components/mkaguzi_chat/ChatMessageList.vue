<template>
  <div 
    ref="containerRef"
    class="flex-1 overflow-y-auto p-4 space-y-4"
    @scroll="handleScroll"
  >
    <!-- Load More Button -->
    <div v-if="hasMore && !loading" class="text-center">
      <Button variant="ghost" size="sm" @click="$emit('load-more')">
        <ArrowUp class="w-4 h-4 mr-1" />
        Load older messages
      </Button>
    </div>

    <!-- Loading Indicator -->
    <div v-if="loading" class="text-center py-4">
      <Loader2 class="w-6 h-6 animate-spin text-blue-600 mx-auto" />
      <p class="text-sm text-gray-500 mt-2">Loading messages...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="messages.length === 0" class="text-center py-12">
      <MessageCircle class="w-12 h-12 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No messages yet</h3>
      <p class="text-gray-500 text-sm">
        Start the conversation{{ isAiEnabled ? ' or ask the AI assistant' : '' }}
      </p>
    </div>

    <!-- Messages -->
    <template v-else>
      <ChatMessageItem
        v-for="(message, index) in messages"
        :key="message.name || index"
        :message="message"
        :current-user="currentUser"
        :show-sender="shouldShowSender(message, index)"
        @edit="$emit('edit', message)"
        @delete="$emit('delete', message)"
        @reply="$emit('reply', message)"
      />

      <!-- Typing Indicator -->
      <ChatTypingIndicator 
        v-if="typingUsers.length > 0" 
        :users="typingUsers" 
      />

      <!-- AI Thinking Indicator -->
      <div v-if="aiThinking" class="flex justify-start">
        <div class="flex items-start space-x-3">
          <div class="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
            <Bot class="w-4 h-4 text-purple-600 animate-pulse" />
          </div>
          <div class="bg-purple-50 border border-purple-100 rounded-lg px-4 py-3">
            <div class="flex items-center space-x-2">
              <Loader2 class="w-4 h-4 animate-spin text-purple-600" />
              <span class="text-sm text-purple-600">AI is thinking...</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Scroll anchor -->
    <div ref="scrollAnchor"></div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import { ArrowUp, Bot, Loader2, MessageCircle } from "lucide-vue-next"
import { nextTick, onMounted, ref, watch } from "vue"
import ChatMessageItem from "./ChatMessageItem.vue"
import ChatTypingIndicator from "./ChatTypingIndicator.vue"

const props = defineProps({
	messages: { type: Array, default: () => [] },
	currentUser: { type: String, default: "" },
	loading: { type: Boolean, default: false },
	hasMore: { type: Boolean, default: false },
	isAiEnabled: { type: Boolean, default: false },
	aiThinking: { type: Boolean, default: false },
	typingUsers: { type: Array, default: () => [] },
})

const emit = defineEmits([
	"load-more",
	"edit",
	"delete",
	"reply",
	"add-reaction",
	"scroll",
])

const containerRef = ref(null)
const scrollAnchor = ref(null)
const isNearBottom = ref(true)

const shouldShowSender = (message, index) => {
	if (index === 0) return true
	const prevMessage = props.messages[index - 1]
	return (
		prevMessage.sender !== message.sender ||
		prevMessage.is_ai_generated !== message.is_ai_generated
	)
}

const scrollToBottom = (smooth = true) => {
	nextTick(() => {
		if (scrollAnchor.value) {
			scrollAnchor.value.scrollIntoView({
				behavior: smooth ? "smooth" : "auto",
			})
		}
	})
}

const handleScroll = () => {
	if (!containerRef.value) return
	const { scrollTop, scrollHeight, clientHeight } = containerRef.value
	isNearBottom.value = scrollHeight - scrollTop - clientHeight < 100
	emit("scroll", {
		scrollTop,
		scrollHeight,
		clientHeight,
		isNearBottom: isNearBottom.value,
	})
}

// Auto-scroll when new messages arrive (if near bottom)
watch(
	() => props.messages.length,
	(newLen, oldLen) => {
		if (newLen > oldLen && isNearBottom.value) {
			scrollToBottom()
		}
	},
)

// Scroll to bottom on AI thinking
watch(
	() => props.aiThinking,
	(thinking) => {
		if (thinking && isNearBottom.value) {
			scrollToBottom()
		}
	},
)

onMounted(() => {
	scrollToBottom(false)
})

defineExpose({ scrollToBottom })
</script>
