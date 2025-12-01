<template>
  <div class="flex items-center space-x-2 text-sm text-gray-500">
    <div class="flex -space-x-1">
      <div 
        v-for="user in displayUsers" 
        :key="user"
        class="w-6 h-6 rounded-full bg-blue-100 border-2 border-white flex items-center justify-center"
        :title="user"
      >
        <span class="text-xs font-medium text-blue-600">{{ getInitials(user) }}</span>
      </div>
    </div>
    <span class="animate-pulse">
      {{ typingText }}
    </span>
    <span class="flex space-x-1">
      <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
      <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
      <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
    </span>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
	users: { type: Array, default: () => [] }, // Can be array of strings or {user, full_name} objects
})

// Normalize users to get display names
const normalizedUsers = computed(() => {
	return props.users.map((u) => {
		if (typeof u === "string") return u
		return u.full_name || u.user || "Someone"
	})
})

const displayUsers = computed(() => normalizedUsers.value.slice(0, 3))

const typingText = computed(() => {
	const users = normalizedUsers.value
	const count = users.length
	if (count === 0) return ""
	if (count === 1) return `${users[0]} is typing`
	if (count === 2) return `${users[0]} and ${users[1]} are typing`
	return `${users[0]} and ${count - 1} others are typing`
})

const getInitials = (name) => {
	if (!name) return "?"
	return name
		.split(/[@\s]/)
		.map((n) => n[0])
		.join("")
		.toUpperCase()
		.slice(0, 2)
}
</script>
