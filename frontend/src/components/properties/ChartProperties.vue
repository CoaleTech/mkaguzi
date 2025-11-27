<template>
  <div class="chart-properties">
    <div class="property-group">
      <label class="property-label">Chart Type</label>
      <Select
        :value="section.config?.chart_type || 'bar'"
        :options="chartTypeOptions"
        @change="updateConfig('chart_type', $event)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Chart Title</label>
      <Input
        :value="section.config?.title || ''"
        placeholder="Enter chart title"
        @input="updateConfig('title', $event.target.value)"
      />
    </div>

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
      <label class="property-label">X-Axis Field</label>
      <Select
        :value="section.config?.x_field || ''"
        :options="fieldOptions"
        placeholder="Select X-axis field"
        @change="updateConfig('x_field', $event)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Y-Axis Field</label>
      <Select
        :value="section.config?.y_field || ''"
        :options="fieldOptions"
        placeholder="Select Y-axis field"
        @change="updateConfig('y_field', $event)"
      />
    </div>

    <div class="property-group">
      <label class="property-label">Chart Size</label>
      <div class="size-inputs">
        <div class="size-input-group">
          <label class="size-label">Width</label>
          <Input
            :value="section.config?.styling?.width || ''"
            placeholder="100%"
            @input="updateStyling('width', $event.target.value)"
          />
        </div>
        <div class="size-input-group">
          <label class="size-label">Height</label>
          <Input
            :value="section.config?.styling?.height || ''"
            placeholder="400"
            @input="updateStyling('height', $event.target.value)"
          />
        </div>
      </div>
    </div>

    <div class="property-group">
      <label class="property-label">Chart Colors</label>
      <div class="color-palette">
        <div
          v-for="(color, index) in chartColors"
          :key="index"
          class="color-input-group"
        >
          <Input
            type="color"
            :value="color"
            @input="updateColor(index, $event.target.value)"
          />
          <Button variant="ghost" size="sm" @click="removeColor(index)" v-if="chartColors.length > 1">
            <XIcon class="h-4 w-4" />
          </Button>
        </div>
        <Button variant="outline" size="sm" @click="addColor">
          <PlusIcon class="h-4 w-4 mr-1" />
          Add Color
        </Button>
      </div>
    </div>

    <div v-if="section.config?.chart_type !== 'pie' && section.config?.chart_type !== 'donut'" class="property-group">
      <label class="property-label">Axis Titles</label>
      <div class="axis-inputs">
        <Input
          :value="section.config?.x_axis_title || ''"
          placeholder="X-axis title"
          @input="updateConfig('x_axis_title', $event.target.value)"
        />
        <Input
          :value="section.config?.y_axis_title || ''"
          placeholder="Y-axis title"
          @input="updateConfig('y_axis_title', $event.target.value)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Input, Select } from "frappe-ui"
import { PlusIcon, XIcon } from "lucide-vue-next"
import { computed } from "vue"

const props = defineProps({
	section: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update"])

const chartTypeOptions = [
	{ label: "Bar Chart", value: "bar" },
	{ label: "Line Chart", value: "line" },
	{ label: "Pie Chart", value: "pie" },
	{ label: "Donut Chart", value: "donut" },
	{ label: "Area Chart", value: "area" },
]

const dataSourceOptions = [
	{ label: "Audit Findings", value: "audit_findings" },
	{ label: "Test Results", value: "test_results" },
	{ label: "Compliance Items", value: "compliance_items" },
	{ label: "Risk Assessments", value: "risk_assessments" },
]

const fieldOptions = [
	{ label: "Date", value: "date" },
	{ label: "Type", value: "type" },
	{ label: "Status", value: "status" },
	{ label: "Severity", value: "severity" },
	{ label: "Count", value: "count" },
	{ label: "Amount", value: "amount" },
	{ label: "Score", value: "score" },
]

const chartColors = computed(() => {
	return (
		props.section.config?.styling?.colors || [
			"#3b82f6",
			"#10b981",
			"#f59e0b",
			"#ef4444",
		]
	)
})

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

const updateColor = (index, color) => {
	const colors = [...chartColors.value]
	colors[index] = color
	updateStyling("colors", colors)
}

const addColor = () => {
	const colors = [...chartColors.value, "#6366f1"]
	updateStyling("colors", colors)
}

const removeColor = (index) => {
	const colors = [...chartColors.value]
	colors.splice(index, 1)
	updateStyling("colors", colors)
}
</script>

<style scoped>
.chart-properties {
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

.size-inputs,
.axis-inputs {
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

.color-palette {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.color-input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.color-input-group input[type="color"] {
  width: 40px;
  height: 32px;
  border-radius: 0.25rem;
  border: 1px solid var(--border-color);
  cursor: pointer;
}
</style>