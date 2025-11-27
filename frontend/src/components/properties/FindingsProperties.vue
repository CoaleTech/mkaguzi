<template>
  <div class="findings-properties">
    <div class="property-group">
      <label class="property-label">Section Title</label>
      <Input
        :value="section.config?.title || ''"
        placeholder="Enter section title"
        @input="updateConfig('title', $event.target.value)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Finding Types</label>
      <div class="checkbox-list">
        <div v-for="type in findingTypeOptions" :key="type.value" class="checkbox-group">
          <input
            type="checkbox"
            :checked="(section.config?.finding_types || []).includes(type.value)"
            @change="toggleFindingType(type.value, $event.target.checked)"
          />
          <label class="checkbox-label">{{ type.label }}</label>
        </div>
      </div>
    </div>

    <div class="property-group">
      <label class="property-label">Status Filter</label>
      <Select
        :value="section.config?.status_filter || ''"
        :options="statusOptions"
        placeholder="All statuses"
        @change="updateConfig('status_filter', $event)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Severity Filter</label>
      <Select
        :value="section.config?.severity_filter || ''"
        :options="severityOptions"
        placeholder="All severities"
        @change="updateConfig('severity_filter', $event)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Group By</label>
      <Select
        :value="section.config?.group_by || 'finding_type'"
        :options="groupByOptions"
        @change="updateConfig('group_by', $event)"
      />
    </div>

    <div class="property-group">
      <div class="checkbox-group">
        <input
          type="checkbox"
          :checked="section.config?.show_descriptions || true"
          @change="updateConfig('show_descriptions', $event.target.checked)"
        />
        <label class="checkbox-label">Show descriptions</label>
      </div>
    </div>

    <div class="property-group">
      <div class="checkbox-group">
        <input
          type="checkbox"
          :checked="section.config?.show_due_dates || true"
          @change="updateConfig('show_due_dates', $event.target.checked)"
        />
        <label class="checkbox-label">Show due dates</label>
      </div>
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

const findingTypeOptions = [
	{ label: "Control Deficiency", value: "Control Deficiency" },
	{ label: "Compliance Issue", value: "Compliance Issue" },
	{ label: "Process Improvement", value: "Process Improvement" },
	{ label: "Risk Assessment", value: "Risk Assessment" },
	{ label: "Data Quality", value: "Data Quality" },
	{ label: "Security Concern", value: "Security Concern" },
]

const statusOptions = [
	{ label: "All Statuses", value: "" },
	{ label: "Open", value: "Open" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Resolved", value: "Resolved" },
	{ label: "Closed", value: "Closed" },
]

const severityOptions = [
	{ label: "All Severities", value: "" },
	{ label: "Critical", value: "Critical" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

const groupByOptions = [
	{ label: "Finding Type", value: "finding_type" },
	{ label: "Severity", value: "severity" },
	{ label: "Status", value: "status" },
	{ label: "Department", value: "department" },
	{ label: "None", value: "none" },
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

const toggleFindingType = (type, checked) => {
	const currentTypes = props.section.config?.finding_types || []
	let newTypes

	if (checked) {
		newTypes = [...currentTypes, type]
	} else {
		newTypes = currentTypes.filter((t) => t !== type)
	}

	updateConfig("finding_types", newTypes)
}
</script>

<style scoped>
.findings-properties {
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

.checkbox-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--background-color);
  border-radius: 0.25rem;
  max-height: 150px;
  overflow-y: auto;
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
</style>