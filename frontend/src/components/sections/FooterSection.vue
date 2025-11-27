<template>
  <div class="footer-section" :class="alignmentClass">
    <div
      class="footer-content"
      :style="footerStyle"
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
	const alignment = props.section.config?.alignment || "center"
	return `text-${alignment}`
})

const footerStyle = computed(() => {
	const styling = props.section.config?.styling || {}
	return {
		fontSize: styling.fontSize || "0.875rem",
		color: styling.color || "#6b7280",
		fontWeight: styling.fontWeight || "400",
		borderTop: styling.borderTop || "1px solid #e5e7eb",
		paddingTop: styling.paddingTop || "1rem",
		marginTop: styling.marginTop || "2rem",
	}
})

const formattedContent = computed(() => {
	const content =
		props.section.config?.content || "© 2025 Internal Audit Department"

	// Replace common variables
	const currentYear = new Date().getFullYear()
	const currentDate = new Date().toLocaleDateString()

	return content
		.replace(/\{\{year\}\}/g, currentYear)
		.replace(/\{\{date\}\}/g, currentDate)
		.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
		.replace(/\*(.*?)\*/g, "<em>$1</em>")
})
</script>

<style scoped>
.footer-section {
  margin: 2rem 0 0 0;
}

.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

.footer-content {
  word-wrap: break-word;
  line-height: 1.4;
}

@media print {
  .footer-section {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
  }
}
</style>