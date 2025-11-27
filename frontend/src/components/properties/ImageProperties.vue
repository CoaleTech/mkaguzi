<template>
  <div class="image-properties">
    <div class="property-group">
      <label class="property-label">Image Source</label>
      <Input
        :value="section.config?.src || ''"
        placeholder="Enter image URL or upload"
        @input="updateConfig('src', $event.target.value)"
      />
      <div class="upload-section">
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          @change="handleFileUpload"
          class="file-input"
        />
        <Button variant="outline" size="sm" @click="$refs.fileInput?.click()">
          <UploadIcon class="h-4 w-4 mr-1" />
          Upload Image
        </Button>
      </div>
    </div>

    <div class="property-group">
      <label class="property-label">Alt Text</label>
      <Input
        :value="section.config?.alt || ''"
        placeholder="Describe the image"
        @input="updateConfig('alt', $event.target.value)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Caption</label>
      <Input
        :value="section.config?.caption || ''"
        placeholder="Image caption (optional)"
        @input="updateConfig('caption', $event.target.value)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Alignment</label>
      <Select
        :value="section.config?.alignment || 'center'"
        :options="alignmentOptions"
        @change="updateConfig('alignment', $event)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Image Size</label>
      <div class="size-inputs">
        <div class="size-input-group">
          <label class="size-label">Width</label>
          <Input
            :value="section.config?.styling?.width || ''"
            placeholder="auto"
            @input="updateStyling('width', $event.target.value)"
          />
        </div>
        <div class="size-input-group">
          <label class="size-label">Max Width</label>
          <Input
            :value="section.config?.styling?.maxWidth || ''"
            placeholder="100%"
            @input="updateStyling('maxWidth', $event.target.value)"
          />
        </div>
      </div>
    </div>

    <div class="property-group">
      <label class="property-label">Border Radius</label>
      <Input
        :value="section.config?.styling?.borderRadius || ''"
        placeholder="0.25rem"
        @input="updateStyling('borderRadius', $event.target.value)"
      />
    </div>

    <div class="property-group">
      <div class="checkbox-group">
        <input
          type="checkbox"
          :checked="section.config?.styling?.shadow || false"
          @change="updateStyling('shadow', $event.target.checked)"
        />
        <label class="checkbox-label">Add shadow</label>
      </div>
    </div>

    <div v-if="section.config?.src" class="image-preview">
      <label class="property-label">Preview</label>
      <img
        :src="section.config.src"
        :alt="section.config.alt || 'Preview'"
        class="preview-image"
        @error="handleImageError"
      />
    </div>
  </div>
</template>

<script setup>
import { Button, Input, Select } from "frappe-ui"
import { UploadIcon } from "lucide-vue-next"
import { ref } from "vue"

const props = defineProps({
	section: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update"])
const fileInput = ref(null)

const alignmentOptions = [
	{ label: "Left", value: "left" },
	{ label: "Center", value: "center" },
	{ label: "Right", value: "right" },
]

const updateConfig = (key, value) => {
	const updatedSection = {
		...props.section,
		config: {
			...props.section.config,
			[key]: value,
		},
	}
	emit("update", updatedSection)
}

const updateStyling = (key, value) => {
	const updatedSection = {
		...props.section,
		config: {
			...props.section.config,
			styling: {
				...props.section.config?.styling,
				[key]: value,
			},
		},
	}
	emit("update", updatedSection)
}

const handleFileUpload = (event) => {
	const file = event.target.files[0]
	if (file) {
		const reader = new FileReader()
		reader.onload = (e) => {
			updateConfig("src", e.target?.result)
			if (!props.section.config?.alt) {
				updateConfig("alt", file.name.replace(/\.[^/.]+$/, ""))
			}
		}
		reader.readAsDataURL(file)
	}
}

const handleImageError = (event) => {
	console.error("Failed to load image:", event.target.src)
}
</script>

<style scoped>
.image-properties {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.property-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.property-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-input {
  display: none;
}

.size-inputs {
  display: flex;
  gap: 0.5rem;
}

.size-input-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.size-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-label {
  font-size: 0.875rem;
  color: var(--text-color);
}

.image-preview {
  margin-top: 1rem;
}

.preview-image {
  max-width: 100%;
  height: auto;
  border: 1px solid var(--border-color);
  border-radius: 0.25rem;
}
</style>