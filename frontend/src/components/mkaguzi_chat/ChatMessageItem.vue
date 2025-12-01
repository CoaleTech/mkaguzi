<template>
  <div :class="['flex', messageAlignment]">
    <!-- AI Message -->
    <div v-if="message.is_ai_generated" class="max-w-2xl group">
      <div class="flex items-start space-x-3">
        <div class="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
          <Bot class="w-4 h-4 text-purple-600" />
        </div>
        <div class="flex-1">
          <div class="bg-purple-50 border border-purple-100 rounded-lg px-4 py-3 relative">
            <!-- Message Actions (on hover) -->
            <div class="absolute -top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <div class="flex items-center space-x-1 bg-white rounded-lg shadow-sm border px-1">
                <button 
                  @click="copyContent" 
                  class="p-1 hover:bg-gray-100 rounded"
                  title="Copy"
                >
                  <Copy class="w-3.5 h-3.5 text-gray-500" />
                </button>
              </div>
            </div>

            <div class="flex items-center space-x-2 mb-2">
              <span class="text-xs font-medium text-purple-600">AI Assistant</span>
              <span v-if="message.ai_model_used" class="text-xs text-purple-400">
                {{ getModelDisplayName(message.ai_model_used) }}
              </span>
            </div>
            
            <!-- Rich content rendering -->
            <div class="text-sm text-gray-800 prose prose-sm max-w-none" v-html="renderedContent"></div>
            
            <!-- Context Sources -->
            <div v-if="contextSources.length > 0" class="mt-3 pt-3 border-t border-purple-200">
              <p class="text-xs text-purple-600 mb-2 flex items-center">
                <FileText class="w-3 h-3 mr-1" />
                Sources:
              </p>
              <div class="flex flex-wrap gap-1">
                <span 
                  v-for="source in contextSources"
                  :key="source"
                  class="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded cursor-pointer hover:bg-purple-200"
                  @click="$emit('view-source', source)"
                >
                  {{ source }}
                </span>
              </div>
            </div>
          </div>
          <span class="text-xs text-gray-400 mt-1 block">
            {{ formatTime(message.creation) }}
          </span>
        </div>
      </div>
    </div>

    <!-- User Message -->
    <div v-else class="max-w-md group" :class="isOwnMessage ? 'order-2' : ''">
      <div class="relative">
        <!-- Message Actions (on hover) -->
        <div 
          :class="[
            'absolute -top-2 opacity-0 group-hover:opacity-100 transition-opacity z-10',
            isOwnMessage ? 'left-2' : 'right-2'
          ]"
        >
          <div class="flex items-center space-x-1 bg-white rounded-lg shadow-sm border px-1">
            <button 
              @click="copyContent" 
              class="p-1 hover:bg-gray-100 rounded"
              title="Copy"
            >
              <Copy class="w-3.5 h-3.5 text-gray-500" />
            </button>
            <button 
              v-if="isOwnMessage && !message.is_ai_generated"
              @click="$emit('edit', message)" 
              class="p-1 hover:bg-gray-100 rounded"
              title="Edit"
            >
              <Pencil class="w-3.5 h-3.5 text-gray-500" />
            </button>
            <button 
              @click="$emit('reply', message)" 
              class="p-1 hover:bg-gray-100 rounded"
              title="Reply"
            >
              <Reply class="w-3.5 h-3.5 text-gray-500" />
            </button>
            <button 
              v-if="isOwnMessage"
              @click="$emit('delete', message)" 
              class="p-1 hover:bg-red-100 rounded"
              title="Delete"
            >
              <Trash2 class="w-3.5 h-3.5 text-red-500" />
            </button>
          </div>
        </div>

        <div :class="['rounded-lg px-4 py-2', messageClass]">
          <!-- Sender name for other users -->
          <div v-if="showSender && !isOwnMessage" class="text-xs opacity-75 mb-1">
            {{ message.sender_name || message.sender }}
          </div>
          
          <!-- Reply preview -->
          <div 
            v-if="message.reply_to" 
            class="text-xs opacity-75 mb-2 pl-2 border-l-2 border-current"
          >
            <span class="font-medium">{{ message.reply_to_sender }}</span>
            <p class="truncate">{{ message.reply_to_content }}</p>
          </div>
          
          <!-- Message content -->
          <div class="text-sm whitespace-pre-wrap" v-html="renderedContent"></div>
          
          <!-- Edited indicator -->
          <span v-if="message.is_edited" class="text-xs opacity-50 ml-1">(edited)</span>
        </div>
        
        <div :class="['text-xs mt-1', isOwnMessage ? 'text-right text-gray-400' : 'text-gray-400']">
          {{ formatTime(message.creation) }}
          <Check v-if="isOwnMessage && message.delivered" class="w-3 h-3 inline ml-1" />
          <CheckCheck v-if="isOwnMessage && message.read" class="w-3 h-3 inline ml-1 text-blue-500" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
	Bot,
	Check,
	CheckCheck,
	Copy,
	FileText,
	Pencil,
	Reply,
	Trash2,
} from "lucide-vue-next"
import { computed } from "vue"

const props = defineProps({
	message: { type: Object, required: true },
	currentUser: { type: String, default: "" },
	showSender: { type: Boolean, default: true },
})

const emit = defineEmits(["edit", "delete", "reply", "view-source"])

const isOwnMessage = computed(() => props.message.sender === props.currentUser)

const messageAlignment = computed(() => {
	if (props.message.is_ai_generated) return "justify-start"
	return isOwnMessage.value ? "justify-end" : "justify-start"
})

const messageClass = computed(() => {
	if (props.message.is_ai_generated)
		return "bg-purple-50 border border-purple-100"
	return isOwnMessage.value
		? "bg-blue-600 text-white"
		: "bg-gray-100 text-gray-900"
})

const renderedContent = computed(() => {
	let content = props.message.content || ""

	// Convert markdown-like formatting
	// Bold: **text** or __text__
	content = content.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
	content = content.replace(/__(.*?)__/g, "<strong>$1</strong>")

	// Italic: *text* or _text_
	content = content.replace(/\*(.*?)\*/g, "<em>$1</em>")
	content = content.replace(/_(.*?)_/g, "<em>$1</em>")

	// Code: `code`
	content = content.replace(
		/`(.*?)`/g,
		'<code class="px-1 py-0.5 bg-gray-200 rounded text-sm">$1</code>',
	)

	// Links: [text](url)
	content = content.replace(
		/\[([^\]]+)\]\(([^)]+)\)/g,
		'<a href="$2" target="_blank" class="text-blue-600 underline">$1</a>',
	)

	// Line breaks
	content = content.replace(/\n/g, "<br>")

	return content
})

const contextSources = computed(() => {
	if (!props.message.context_sources) return []
	if (typeof props.message.context_sources === "string") {
		try {
			return JSON.parse(props.message.context_sources)
		} catch {
			return [props.message.context_sources]
		}
	}
	return props.message.context_sources
})

const getModelDisplayName = (model) => {
	const names = {
		"meta-llama/llama-3.1-8b-instruct:free": "Llama 3.1",
		"google/gemma-2-9b-it:free": "Gemma 2",
		"qwen/qwen-2.5-7b-instruct:free": "Qwen 2.5",
	}
	return names[model] || model?.split("/").pop()?.split(":")[0] || "AI"
}

const formatTime = (timestamp) => {
	if (!timestamp) return ""
	return new Date(timestamp).toLocaleTimeString([], {
		hour: "2-digit",
		minute: "2-digit",
	})
}

const copyContent = () => {
	navigator.clipboard.writeText(props.message.content)
}
</script>

<style scoped>
.prose :deep(code) {
  @apply px-1 py-0.5 bg-gray-200 rounded text-sm font-mono;
}
.prose :deep(a) {
  @apply text-blue-600 underline;
}
</style>
