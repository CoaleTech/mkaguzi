<template>
  <div class="text-properties">
    <div class="property-group">
      <label class="property-label">Content</label>
      <textarea
        :value="section.config?.content || ''"
        placeholder="Enter text content..."
        class="content-textarea"
        rows="4"
        @input="updateConfig('content', $event.target.value)"
      ></textarea>
      <p class="property-hint">Use **bold** and *italic* for formatting</p>
    </div>

    <div class="property-group">
      <label class="property-label">Alignment</label>
      <Select
        :value="section.config?.alignment || 'left'"
        :options="alignmentOptions"
        @change="updateConfig('alignment', $event)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Font Size</label>
      <Input
        :value="section.config?.styling?.fontSize || ''"
        placeholder="e.g., 1rem, 16px"
        @input="updateStyling('fontSize', $event.target.value)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Line Height</label>
      <Input
        :value="section.config?.styling?.lineHeight || ''"
        placeholder="e.g., 1.5, 24px"
        @input="updateStyling('lineHeight', $event.target.value)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Text Color</label>
      <Input
        type="color"
        :value="section.config?.styling?.color || '#374151'"
        @input="updateStyling('color', $event.target.value)"
      />
    </div>
  </div>
</template>

<script setup>
import { Input, Select } from "frappe-ui"

const props = defineProps({
	section: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update"])

const alignmentOptions = [
	{ label: "Left", value: "left" },
	{ label: "Center", value: "center" },
	{ label: "Right", value: "right" },
	{ label: "Justify", value: "justify" },
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
</script>

<style scoped>
.text-properties {
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

.content-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  resize: vertical;
  font-family: inherit;
  font-size: 0.875rem;
}

.property-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0;
}
</style>