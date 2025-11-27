<template>
  <div class="saved-searches">
    <div v-if="savedSearches.length" class="searches-list">
      <div
        v-for="search in savedSearches"
        :key="search.name"
        class="search-item"
      >
        <div class="search-info">
          <h5>{{ search.name }}</h5>
          <p>{{ search.query }}</p>
          <div class="search-meta">
            <span>{{ formatDate(search.creation) }}</span>
            <span v-if="Object.keys(search.filters || {}).length" class="filter-count">
              {{ Object.keys(search.filters).length }} filters
            </span>
          </div>
        </div>
        <div class="search-actions">
          <Button
            variant="outline"
            size="sm"
            @click="$emit('load-search', search.name)"
          >
            <PlayIcon class="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            @click="$emit('delete-search', search.name)"
          >
            <TrashIcon class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">
      <BookmarkIcon class="h-12 w-12 text-gray-300" />
      <h5>No Saved Searches</h5>
      <p>Save your frequent searches for quick access</p>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import { BookmarkIcon, PlayIcon, TrashIcon } from "lucide-vue-next"

const props = defineProps({
	savedSearches: {
		type: Array,
		default: () => [],
	},
})

const emit = defineEmits(["load-search", "delete-search"])

const formatDate = (dateString) => {
	return new Date(dateString).toLocaleDateString()
}
</script>

<style scoped>
.searches-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
}

.search-info h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.search-info p {
  color: var(--text-muted);
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
}

.search-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.filter-count {
  background: var(--background-color);
  padding: 0.125rem 0.5rem;
  border-radius: 0.75rem;
}

.search-actions {
  display: flex;
  gap: 0.5rem;
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