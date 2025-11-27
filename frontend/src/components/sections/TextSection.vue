<template>
  <div class="text-section" :class="alignmentClass">
    <div
      v-if="preview"
      class="text-preview"
      :style="textStyle"
      v-html="formattedContent"
    ></div>
    <div
      v-else
      class="text-content"
      :style="textStyle"
      v-html="formattedContent"
    ></div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
	section: {
		type: Object,
		required: true,
	},
	preview: {
		type: Boolean,
		default: true,
	},
})

const alignmentClass = computed(() => {
	const alignment = props.section.config?.alignment || "left"
	return `text-${alignment}`
})

const textStyle = computed(() => {
	const styling = props.section.config?.styling || {}
	return {
		fontSize: styling.fontSize || "1rem",
		lineHeight: styling.lineHeight || "1.5",
		color: styling.color || "#374151",
		fontWeight: styling.fontWeight || "400",
		margin: styling.margin || "1rem 0",
	}
})

const formattedContent = computed(() => {
	const content =
		props.section.config?.content || "Enter your text content here..."

	// Basic markdown-like formatting
	return content
		.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
		.replace(/\*(.*?)\*/g, "<em>$1</em>")
		.replace(/\n/g, "<br>")
})
</script>

<style scoped>
.text-section {
  margin: 1rem 0;
}

.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-justify { text-align: justify; }

.text-preview,
.text-content {
  word-wrap: break-word;
}

.text-preview {
  min-height: 2rem;
  padding: 0.5rem;
  border: 1px dashed #d1d5db;
  border-radius: 0.25rem;
  background: #f9fafb;
}
</style>