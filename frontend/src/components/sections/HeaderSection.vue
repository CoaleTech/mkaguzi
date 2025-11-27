<template>
  <div class="header-section" :class="alignmentClass">
    <component
      :is="headingTag"
      :style="headingStyle"
      class="section-heading"
    >
      {{ section.config?.text || section.title || 'Header Text' }}
    </component>
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

const headingTag = computed(() => {
	const level = props.section.config?.level || 1
	return `h${Math.min(Math.max(level, 1), 6)}`
})

const alignmentClass = computed(() => {
	const alignment = props.section.config?.alignment || "left"
	return `text-${alignment}`
})

const headingStyle = computed(() => {
	const styling = props.section.config?.styling || {}
	return {
		color: styling.color || "#000",
		fontSize:
			styling.fontSize ||
			`${2.5 - (props.section.config?.level || 1) * 0.25}rem`,
		fontWeight: styling.fontWeight || "600",
		margin: styling.margin || "0 0 1rem 0",
		lineHeight: styling.lineHeight || "1.2",
	}
})
</script>

<style scoped>
.header-section {
  margin: 1rem 0;
}

.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

.section-heading {
  word-wrap: break-word;
}
</style>