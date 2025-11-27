<template>
  <div class="table-properties">
    <div class="property-group">
      <label class="property-label">Data Source</label>
      <Select
        :value="section.config?.data_source || ''"
        :options="dataSourceOptions"
        placeholder="Select data source"
        @change="updateConfig('data_source', $event)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Table Title</label>
      <Input
        :value="section.config?.title || ''"
        placeholder="Enter table title"
        @input="updateConfig('title', $event.target.value)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Columns</label>
      <div class="columns-list">
        <div
          v-for="(column, index) in section.config?.columns || []"
          :key="index"
          class="column-item"
        >
          <Input
            :value="column.label"
            placeholder="Column label"
            @input="updateColumn(index, 'label', $event.target.value)"
          />
          <Select
            :value="column.type || 'text'"
            :options="columnTypeOptions"
            @change="updateColumn(index, 'type', $event)"
          />
          <Button variant="ghost" size="sm" @click="removeColumn(index)">
            <XIcon class="h-4 w-4" />
          </Button>
        </div>
        <Button variant="outline" size="sm" @click="addColumn">
          <PlusIcon class="h-4 w-4 mr-1" />
          Add Column
        </Button>
      </div>
    </div>

    <div class="property-group">
      <div class="checkbox-group">
        <input
          type="checkbox"
          :checked="section.config?.pagination || false"
          @change="updateConfig('pagination', $event.target.checked)"
        />
        <label class="checkbox-label">Enable pagination</label>
      </div>
    </div>

    <div class="property-group">
      <label class="property-label">Table Style</label>
      <div class="style-options">
        <div class="checkbox-group">
          <input
            type="checkbox"
            :checked="section.config?.styling?.striped || false"
            @change="updateStyling('striped', $event.target.checked)"
          />
          <label class="checkbox-label">Striped rows</label>
        </div>
        <div class="checkbox-group">
          <input
            type="checkbox"
            :checked="section.config?.styling?.bordered || false"
            @change="updateStyling('bordered', $event.target.checked)"
          />
          <label class="checkbox-label">Bordered</label>
        </div>
        <div class="checkbox-group">
          <input
            type="checkbox"
            :checked="section.config?.styling?.hover || false"
            @change="updateStyling('hover', $event.target.checked)"
          />
          <label class="checkbox-label">Hover effect</label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Input, Select } from "frappe-ui"
import { PlusIcon, XIcon } from "lucide-vue-next"

const props = defineProps({
	section: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update"])

const dataSourceOptions = [
	{ label: "Audit Findings", value: "audit_findings" },
	{ label: "Test Results", value: "test_results" },
	{ label: "Compliance Items", value: "compliance_items" },
	{ label: "Risk Assessments", value: "risk_assessments" },
	{ label: "Custom Query", value: "custom_query" },
]

const columnTypeOptions = [
	{ label: "Text", value: "text" },
	{ label: "Number", value: "number" },
	{ label: "Currency", value: "currency" },
	{ label: "Date", value: "date" },
	{ label: "DateTime", value: "datetime" },
	{ label: "Boolean", value: "boolean" },
	{ label: "Percent", value: "percent" },
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

const updateColumn = (index, key, value) => {
	const columns = [...(props.section.config?.columns || [])]
	columns[index] = { ...columns[index], [key]: value }
	updateConfig("columns", columns)
}

const addColumn = () => {
	const columns = [...(props.section.config?.columns || [])]
	columns.push({
		label: `Column ${columns.length + 1}`,
		key: `col_${columns.length + 1}`,
		type: "text",
		width: "auto",
		align: "left",
	})
	updateConfig("columns", columns)
}

const removeColumn = (index) => {
	const columns = [...(props.section.config?.columns || [])]
	columns.splice(index, 1)
	updateConfig("columns", columns)
}
</script>

<style scoped>
.table-properties {
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

.columns-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.column-item {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.column-item input {
  flex: 1;
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

.style-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--background-color);
  border-radius: 0.25rem;
}
</style>