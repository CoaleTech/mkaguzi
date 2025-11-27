<template>
  <div class="image-section" :class="alignmentClass">
    <div v-if="preview && !section.config?.src" class="image-preview">
      <div class="preview-placeholder">
        <ImageIcon class="preview-icon" />
        <h5>Image Section</h5>
        <p>Upload an image or provide a URL</p>
      </div>
    </div>

    <div v-else-if="section.config?.src" class="image-container">
      <img
        :src="section.config.src"
        :alt="section.config.alt || 'Report image'"
        :style="imageStyle"
        class="report-image"
        @error="handleImageError"
      />
      <p v-if="section.config.caption" class="image-caption">
        {{ section.config.caption }}
      </p>
    </div>

    <div v-else class="empty-image">
      <ImageIcon class="empty-icon" />
      <p>No image configured</p>
    </div>
  </div>
</template>

<script setup>
import { ImageIcon } from "lucide-vue-next"
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

const imageStyle = computed(() => {
	const styling = props.section.config?.styling || {}
	return {
		width: styling.width || "auto",
		maxWidth: styling.maxWidth || "100%",
		height: styling.height || "auto",
		borderRadius: styling.borderRadius || "0.25rem",
		border: styling.border || "none",
		boxShadow: styling.shadow ? "0 4px 6px rgba(0, 0, 0, 0.1)" : "none",
	}
})

const handleImageError = (event) => {
	event.target.style.display = "none"
	// Could show error placeholder here
}
</script>

<style scoped>
.image-section {
  margin: 1.5rem 0;
}

.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

.image-preview {
  padding: 2rem;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  background: #f9fafb;
  text-align: center;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
}

.preview-icon {
  width: 3rem;
  height: 3rem;
}

.preview-placeholder h5 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.preview-placeholder p {
  font-size: 0.875rem;
  margin: 0;
}

.image-container {
  display: inline-block;
}

.report-image {
  display: block;
  max-width: 100%;
  height: auto;
}

.image-caption {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0.5rem 0 0 0;
  font-style: italic;
}

.empty-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: #6b7280;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  background: #f9fafb;
}

.empty-icon {
  width: 2rem;
  height: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}
</style>