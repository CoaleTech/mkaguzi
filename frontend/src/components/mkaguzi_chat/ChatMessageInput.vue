<template>
  <div class="bg-white border-t border-gray-200 p-4">
    <!-- Reply Preview -->
    <div 
      v-if="replyingTo" 
      class="mb-3 p-2 bg-gray-50 rounded-lg border-l-4 border-blue-500 flex items-center justify-between"
    >
      <div class="flex-1 min-w-0">
        <p class="text-xs text-blue-600 font-medium">Replying to {{ replyingTo.sender_name || replyingTo.sender }}</p>
        <p class="text-sm text-gray-600 truncate">{{ replyingTo.content }}</p>
      </div>
      <button @click="$emit('cancel-reply')" class="p-1 hover:bg-gray-200 rounded">
        <X class="w-4 h-4 text-gray-500" />
      </button>
    </div>

    <!-- Edit Preview -->
    <div 
      v-if="editingMessage" 
      class="mb-3 p-2 bg-yellow-50 rounded-lg border-l-4 border-yellow-500 flex items-center justify-between"
    >
      <div class="flex-1 min-w-0">
        <p class="text-xs text-yellow-600 font-medium">Editing message</p>
        <p class="text-sm text-gray-600 truncate">{{ editingMessage.content }}</p>
      </div>
      <button @click="$emit('cancel-edit')" class="p-1 hover:bg-yellow-100 rounded">
        <X class="w-4 h-4 text-gray-500" />
      </button>
    </div>

    <!-- Tiptap Editor -->
    <div class="flex items-end space-x-3">
      <div class="flex-1 relative">
        <!-- Formatting Toolbar -->
        <div 
          v-if="editor && showToolbar" 
          class="absolute bottom-full left-0 mb-2 flex items-center space-x-1 bg-white border rounded-lg shadow-lg p-1 z-10"
        >
          <button
            @click="editor.chain().focus().toggleBold().run()"
            :class="['p-1.5 rounded hover:bg-gray-100', { 'bg-gray-200': editor.isActive('bold') }]"
            title="Bold (Ctrl+B)"
          >
            <Bold class="w-4 h-4" />
          </button>
          <button
            @click="editor.chain().focus().toggleItalic().run()"
            :class="['p-1.5 rounded hover:bg-gray-100', { 'bg-gray-200': editor.isActive('italic') }]"
            title="Italic (Ctrl+I)"
          >
            <Italic class="w-4 h-4" />
          </button>
          <button
            @click="editor.chain().focus().toggleStrike().run()"
            :class="['p-1.5 rounded hover:bg-gray-100', { 'bg-gray-200': editor.isActive('strike') }]"
            title="Strikethrough"
          >
            <Strikethrough class="w-4 h-4" />
          </button>
          <button
            @click="editor.chain().focus().toggleCode().run()"
            :class="['p-1.5 rounded hover:bg-gray-100', { 'bg-gray-200': editor.isActive('code') }]"
            title="Code"
          >
            <Code class="w-4 h-4" />
          </button>
          <div class="w-px h-5 bg-gray-300 mx-1"></div>
          <button
            @click="editor.chain().focus().toggleBulletList().run()"
            :class="['p-1.5 rounded hover:bg-gray-100', { 'bg-gray-200': editor.isActive('bulletList') }]"
            title="Bullet List"
          >
            <List class="w-4 h-4" />
          </button>
          <button
            @click="editor.chain().focus().toggleOrderedList().run()"
            :class="['p-1.5 rounded hover:bg-gray-100', { 'bg-gray-200': editor.isActive('orderedList') }]"
            title="Numbered List"
          >
            <ListOrdered class="w-4 h-4" />
          </button>
        </div>

        <!-- Editor Container -->
        <div 
          class="border border-gray-200 rounded-lg focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent overflow-hidden"
        >
          <EditorContent 
            :editor="editor" 
            class="prose prose-sm max-w-none px-4 py-3 min-h-[44px] max-h-[200px] overflow-y-auto focus:outline-none"
          />
        </div>

        <!-- Character count -->
        <div v-if="characterCount > 0" class="absolute bottom-1 right-2 text-xs text-gray-400">
          {{ characterCount }}/{{ maxLength }}
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center space-x-2">
        <!-- Toolbar Toggle -->
        <Button 
          variant="ghost" 
          size="sm" 
          @click="showToolbar = !showToolbar"
          :class="{ 'bg-gray-100': showToolbar }"
          title="Formatting"
        >
          <Type class="w-4 h-4" />
        </Button>

        <!-- Emoji Picker -->
        <Button variant="ghost" size="sm" @click="showEmojiPicker = !showEmojiPicker" title="Emoji">
          <Smile class="w-4 h-4" />
        </Button>

        <!-- AI Ask Button -->
        <Button 
          v-if="isAiEnabled"
          variant="outline"
          size="sm"
          @click="handleAskAi"
          :disabled="!hasContent || aiThinking"
          title="Ask AI Assistant"
          class="flex items-center"
        >
          <Bot class="w-4 h-4 mr-1" />
          Ask AI
        </Button>

        <!-- Send Button -->
        <Button 
          @click="handleSend"
          :disabled="!hasContent || props.loading"
          size="sm"
          variant="solid"
        >
          <Send class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Keyboard Shortcuts Hint -->
    <div class="mt-2 text-xs text-gray-400 flex items-center space-x-4">
      <span><kbd class="px-1 bg-gray-100 rounded">Enter</kbd> to send</span>
      <span><kbd class="px-1 bg-gray-100 rounded">Shift+Enter</kbd> for new line</span>
      <span v-if="showToolbar"><kbd class="px-1 bg-gray-100 rounded">Ctrl+B</kbd> bold</span>
    </div>

    <!-- Simple Emoji Picker -->
    <div 
      v-if="showEmojiPicker" 
      class="absolute bottom-full mb-2 right-4 bg-white border rounded-lg shadow-lg p-3 z-20"
    >
      <div class="grid grid-cols-8 gap-1">
        <button 
          v-for="emoji in commonEmojis" 
          :key="emoji" 
          @click="insertEmoji(emoji)"
          class="p-2 hover:bg-gray-100 rounded text-lg"
        >
          {{ emoji }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import Placeholder from "@tiptap/extension-placeholder"
import StarterKit from "@tiptap/starter-kit"
import { EditorContent, useEditor } from "@tiptap/vue-3"
import { Button } from "frappe-ui"
import {
	Bold,
	Bot,
	Code,
	Italic,
	List,
	ListOrdered,
	Send,
	Smile,
	Strikethrough,
	Type,
	X,
} from "lucide-vue-next"
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"

const props = defineProps({
	isAiEnabled: { type: Boolean, default: false },
	aiThinking: { type: Boolean, default: false },
	loading: { type: Boolean, default: false },
	replyingTo: { type: Object, default: null },
	editingMessage: { type: Object, default: null },
	placeholder: { type: String, default: "Type a message..." },
	maxLength: { type: Number, default: 4000 },
})

const emit = defineEmits([
	"send",
	"ask-ai",
	"cancel-reply",
	"cancel-edit",
	"typing",
	"toggle-ai",
])

const showToolbar = ref(false)
const showEmojiPicker = ref(false)
const typingTimeout = null

const commonEmojis = [
	"😊",
	"👍",
	"❤️",
	"🎉",
	"🔥",
	"✅",
	"⭐",
	"💡",
	"👀",
	"🤔",
	"👏",
	"💪",
	"🙏",
	"📌",
	"⚠️",
	"✨",
]

// Initialize Tiptap editor
const editor = useEditor({
	extensions: [
		StarterKit.configure({
			heading: false,
			codeBlock: false,
		}),
		Placeholder.configure({
			placeholder: () =>
				props.editingMessage
					? "Edit your message..."
					: props.isAiEnabled
						? "Type a message or ask AI..."
						: props.placeholder,
		}),
	],
	editorProps: {
		attributes: {
			class: "focus:outline-none",
		},
		handleKeyDown: (view, event) => {
			// Enter to send (without shift)
			if (event.key === "Enter" && !event.shiftKey) {
				event.preventDefault()
				handleSend()
				return true
			}
			return false
		},
	},
	onUpdate: ({ editor }) => {
		// Emit typing events
		if (editor.getText().length > 0) {
			emit("typing")
		}
	},
})

const hasContent = computed(() => {
	return editor.value?.getText().trim().length > 0
})

const characterCount = computed(() => {
	return editor.value?.getText().length || 0
})

const handleSend = () => {
	if (!hasContent.value || props.loading) return

	const content = editor.value.getHTML()
	const plainText = editor.value.getText().trim()

	emit("send", {
		content: plainText, // For now, send plain text; could send HTML for rich display
		html: content,
		replyTo: props.replyingTo?.name,
		editId: props.editingMessage?.name,
		isAiPrompt: false,
	})

	editor.value.commands.clearContent()
}

const handleAskAi = () => {
	if (!hasContent.value || props.aiThinking) return

	const content = editor.value.getText().trim()
	emit("send", { content, isAiPrompt: true })
	editor.value.commands.clearContent()
}

const insertEmoji = (emoji) => {
	editor.value.commands.insertContent(emoji)
	showEmojiPicker.value = false
	editor.value.commands.focus()
}

// Set content when editing
watch(
	() => props.editingMessage,
	(msg) => {
		if (msg && editor.value) {
			editor.value.commands.setContent(msg.content)
			editor.value.commands.focus("end")
		}
	},
	{ immediate: true },
)

// Focus editor on mount
onMounted(() => {
	setTimeout(() => editor.value?.commands.focus(), 100)
})

onBeforeUnmount(() => {
	clearTimeout(typingTimeout)
	editor.value?.destroy()
})

// Expose editor for parent access
defineExpose({ editor, focus: () => editor.value?.commands.focus() })
</script>

<style>
/* Tiptap editor styles */
.ProseMirror {
  outline: none;
}

.ProseMirror p {
  margin: 0;
}

.ProseMirror p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  float: left;
  color: #9ca3af;
  pointer-events: none;
  height: 0;
}

.ProseMirror ul,
.ProseMirror ol {
  padding-left: 1.5rem;
  margin: 0.5rem 0;
}

.ProseMirror code {
  background-color: #f3f4f6;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.ProseMirror strong {
  font-weight: 600;
}

.ProseMirror em {
  font-style: italic;
}

.ProseMirror s {
  text-decoration: line-through;
}
</style>
