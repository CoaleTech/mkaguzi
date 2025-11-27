<template>
  <div class="search-history">
    <div class="history-header">
      <h5>Recent Searches</h5>
      <Button
        v-if="searchHistory.length"
        variant="ghost"
        size="sm"
        @click="$emit('clear-history')"
      >
        Clear All
      </Button>
    </div>
    
    <div v-if="searchHistory.length" class="history-list">
      <div
        v-for="search in searchHistory"
        :key="search.timestamp"
        class="history-item"
        @click="$emit('load-search', search)"
      >
        <div class="search-query">{{ search.query }}</div>
        <div class="search-timestamp">
          {{ formatTimestamp(search.timestamp) }}
        </div>
      </div>
    </div>
    
    <div v-else class="empty-state">
      <ClockIcon class="h-12 w-12 text-gray-300" />
      <h5>No Search History</h5>
      <p>Your recent searches will appear here</p>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import { ClockIcon } from "lucide-vue-next"

const props = defineProps({
	searchHistory: {
		type: Array,
		default: () => [],
	},
})

const emit = defineEmits(["load-search", "clear-history"])

const formatTimestamp = (timestamp) => {
	const date = new Date(timestamp)
	const now = new Date()
	const diffMs = now - date
	const diffMins = Math.floor(diffMs / 60000)
	const diffHours = Math.floor(diffMs / 3600000)
	const diffDays = Math.floor(diffMs / 86400000)

	if (diffMins < 1) return "Just now"
	if (diffMins < 60) return `${diffMins}m ago`
	if (diffHours < 24) return `${diffHours}h ago`
	if (diffDays < 7) return `${diffDays}d ago`

	return date.toLocaleDateString()
}
</script>

<style scoped>
.search-history {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-header h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.search-query {
  font-weight: 500;
  color: var(--text-color);
}

.search-timestamp {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
  color: var(--text-muted);
}

.empty-state h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}
</style>