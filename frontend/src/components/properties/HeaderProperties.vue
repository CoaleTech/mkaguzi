<template>
  <div class="header-properties">
    <div class="property-group">
      <label class="property-label">Heading Level</label>
      <Select
        :value="section.config?.level || 1"
        :options="levelOptions"
        @change="updateConfig('level', $event)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Heading Text</label>
      <Input
        :value="section.config?.text || ''"
        placeholder="Enter heading text"
        @input="updateConfig('text', $event.target.value)"
      />
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
        placeholder="e.g., 2rem, 24px"
        @input="updateStyling('fontSize', $event.target.value)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Text Color</label>
      <Input
        type="color"
        :value="section.config?.styling?.color || '#000000'"
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

const levelOptions = [
	{ label: "H1 - Main Title", value: 1 },
	{ label: "H2 - Section Title", value: 2 },
	{ label: "H3 - Subsection", value: 3 },
	{ label: "H4 - Sub-subsection", value: 4 },
	{ label: "H5 - Minor Heading", value: 5 },
	{ label: "H6 - Smallest Heading", value: 6 },
]

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
</script>

<style scoped>
.header-properties {
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
</style>