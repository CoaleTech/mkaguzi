<template>
  <span v-html="highlightedText" class="highlighted-text"></span>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
	text: {
		type: String,
		default: "",
	},
	searchQuery: {
		type: String,
		default: "",
	},
	maxLength: {
		type: Number,
		default: null,
	},
})

// Computed
const highlightedText = computed(() => {
	let text = props.text || ""

	// Truncate if maxLength is specified
	if (props.maxLength && text.length > props.maxLength) {
		text = text.substring(0, props.maxLength) + "..."
	}

	// If no search query, return plain text
	if (!props.searchQuery) {
		return escapeHtml(text)
	}

	// Escape HTML and highlight search terms
	const escapedText = escapeHtml(text)
	const searchTerms = props.searchQuery
		.split(" ")
		.filter((term) => term.length > 0)

	let highlightedResult = escapedText

	searchTerms.forEach((term) => {
		const regex = new RegExp(`(${escapeRegex(term)})`, "gi")
		highlightedResult = highlightedResult.replace(
			regex,
			'<mark class="search-highlight">$1</mark>',
		)
	})

	return highlightedResult
})

// Methods
const escapeHtml = (text) => {
	const div = document.createElement("div")
	div.textContent = text
	return div.innerHTML
}

const escapeRegex = (string) => {
	return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}
</script>

<style scoped>
.highlighted-text :deep(.search-highlight) {
  background: #fef08a;
  color: #854d0e;
  padding: 0 0.125rem;
  border-radius: 0.125rem;
  font-weight: 600;
}
</style>