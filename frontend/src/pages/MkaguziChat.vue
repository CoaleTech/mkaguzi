<template>
  <div class="chat-page-container">
    <ChatContainer
      :initial-room-name="initialRoomName"
      :engagement-filter="engagementFilter"
      @room-changed="onRoomChanged"
    />
  </div>
</template>

<script setup>
import { ChatContainer } from "@/components/mkaguzi_chat"
import { computed, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"

const route = useRoute()
const router = useRouter()

// Get initial room from route params or path
const initialRoomName = computed(
	() => route.params.roomId || route.query.room || null,
)
const engagementFilter = computed(() => route.query.engagement || null)

// Handle room changes - update URL
const onRoomChanged = (room) => {
	if (room?.name) {
		// Use path-based routing for cleaner URLs
		router.replace({
			name: "MkaguziChatRoom",
			params: { roomId: room.name },
			query: route.query.engagement
				? { engagement: route.query.engagement }
				: undefined,
		})
	}
}

onMounted(() => {
	document.title = "Chat - Mkaguzi"
})
</script>

<style scoped>
.chat-page-container {
  /* Fill the parent container - fullHeight mode removes padding */
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Handle flex container properly */
:deep(.chat-container) {
  height: 100%;
  flex: 1;
}
</style>
