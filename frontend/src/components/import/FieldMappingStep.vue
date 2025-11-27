<template>
  <div class="field-mapping-step">
    <div class="mapping-header">
      <h3 class="step-title">Map Your Data Fields</h3>
      <p class="step-description">
        Connect your file columns to the appropriate fields in the system
      </p>
    </div>

    <div class="mapping-content">
      <!-- Source Preview -->
      <div class="source-section">
        <h4 class="section-title">Your File Columns</h4>
        <div class="source-preview">
          <div class="preview-table-container">
            <table class="preview-table">
              <thead>
                <tr>
                  <th v-for="(header, index) in filePreview.headers" :key="index">
                    {{ header }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, rowIndex) in filePreview.rows.slice(0, 3)" :key="rowIndex">
                  <td v-for="(cell, cellIndex) in row" :key="cellIndex">
                    {{ cell || '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Field Mappings -->
      <div class="mapping-section">
        <div class="mapping-controls">
          <Button 
            variant="outline" 
            size="sm" 
            @click="autoMapFields"
            :disabled="!canAutoMap"
          >
            <ZapIcon class="h-4 w-4 mr-1" />
            Auto Map
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            @click="clearAllMappings"
          >
            <XIcon class="h-4 w-4 mr-1" />
            Clear All
          </Button>
        </div>

        <div class="field-mappings">
          <!-- Required Fields -->
          <div class="field-group">
            <h5 class="group-title required">
              <span>Required Fields</span>
              <span class="field-count">{{ requiredFields.length }}</span>
            </h5>
            
            <div class="mapping-list">
              <div 
                v-for="field in requiredFields" 
                :key="field.field"
                class="mapping-item"
                :class="{ 'mapped': fieldMappings[field.field], 'error': hasValidationError(field.field) }"
              >
                <div class="field-info">
                  <label class="field-label">
                    {{ field.label }}
                    <span class="required-indicator">*</span>
                  </label>
                  <span class="field-type">{{ field.type }}</span>
                </div>
                
                <div class="mapping-control">
                  <Select
                    :value="fieldMappings[field.field] || ''"
                    :options="sourceFieldOptions"
                    placeholder="Select column..."
                    @change="updateMapping(field.field, $event)"
                  />
                  
                  <div v-if="fieldMappings[field.field]" class="mapping-preview">
                    {{ getFieldPreview(fieldMappings[field.field]) }}
                  </div>
                </div>
                
                <div v-if="hasValidationError(field.field)" class="field-error">
                  <AlertTriangleIcon class="h-4 w-4" />
                  <span>{{ getValidationError(field.field) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Optional Fields -->
          <div class="field-group">
            <h5 class="group-title optional">
              <span>Optional Fields</span>
              <span class="field-count">{{ optionalFields.length }}</span>
              <Button
                variant="ghost"
                size="sm"
                @click="showOptionalFields = !showOptionalFields"
              >
                <ChevronDownIcon 
                  class="h-4 w-4 transition-transform"
                  :class="{ 'rotate-180': showOptionalFields }"
                />
              </Button>
            </h5>
            
            <div v-show="showOptionalFields" class="mapping-list">
              <div 
                v-for="field in optionalFields" 
                :key="field.field"
                class="mapping-item"
                :class="{ 'mapped': fieldMappings[field.field] }"
              >
                <div class="field-info">
                  <label class="field-label">{{ field.label }}</label>
                  <span class="field-type">{{ field.type }}</span>
                </div>
                
                <div class="mapping-control">
                  <Select
                    :value="fieldMappings[field.field] || ''"
                    :options="sourceFieldOptions"
                    placeholder="Select column (optional)..."
                    @change="updateMapping(field.field, $event)"
                  />
                  
                  <div v-if="fieldMappings[field.field]" class="mapping-preview">
                    {{ getFieldPreview(fieldMappings[field.field]) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Mapping Summary -->
      <div class="mapping-summary">
        <div class="summary-stats">
          <div class="stat-item">
            <span class="stat-label">Required Fields Mapped</span>
            <span class="stat-value" :class="{ 'complete': requiredMappedCount === requiredFields.length }">
              {{ requiredMappedCount }}/{{ requiredFields.length }}
            </span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Optional Fields Mapped</span>
            <span class="stat-value">{{ optionalMappedCount }}/{{ optionalFields.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Unmapped Columns</span>
            <span class="stat-value" :class="{ 'warning': unmappedColumns.length > 0 }">
              {{ unmappedColumns.length }}
            </span>
          </div>
        </div>

        <!-- Unmapped Columns Warning -->
        <div v-if="unmappedColumns.length > 0" class="unmapped-warning">
          <AlertTriangleIcon class="h-4 w-4 text-amber-500" />
          <div class="warning-content">
            <h6>Unmapped Columns</h6>
            <p>The following columns will be ignored during import:</p>
            <div class="unmapped-list">
              <span 
                v-for="column in unmappedColumns" 
                :key="column" 
                class="unmapped-column"
              >
                {{ column }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Select } from "frappe-ui"
import {
	AlertTriangleIcon,
	ChevronDownIcon,
	XIcon,
	ZapIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"

const props = defineProps({
	importData: {
		type: Object,
		required: true,
	},
	filePreview: {
		type: Object,
		required: true,
	},
	availableFields: {
		type: Array,
		required: true,
	},
	fieldMappings: {
		type: Object,
		default: () => ({}),
	},
})

const emit = defineEmits(["mappings-updated"])

// State
const showOptionalFields = ref(false)
const localMappings = ref({ ...props.fieldMappings })
const validationErrors = ref({})

// Computed
const requiredFields = computed(() =>
	props.availableFields.filter((field) =>
		props.importData.template?.required_fields?.some(
			(rf) => rf.field === field.field,
		),
	),
)

const optionalFields = computed(() =>
	props.availableFields.filter((field) =>
		props.importData.template?.optional_fields?.some(
			(of) => of.field === field.field,
		),
	),
)

const sourceFieldOptions = computed(() => [
	{ label: "- Select Column -", value: "" },
	...props.filePreview.headers.map((header) => ({
		label: header,
		value: header,
	})),
])

const requiredMappedCount = computed(
	() =>
		requiredFields.value.filter((field) => localMappings.value[field.field])
			.length,
)

const optionalMappedCount = computed(
	() =>
		optionalFields.value.filter((field) => localMappings.value[field.field])
			.length,
)

const unmappedColumns = computed(() =>
	props.filePreview.headers.filter(
		(header) => !Object.values(localMappings.value).includes(header),
	),
)

const canAutoMap = computed(
	() =>
		props.filePreview.headers.length > 0 && props.availableFields.length > 0,
)

// Methods
const updateMapping = (fieldName, columnName) => {
	if (columnName === "") {
		delete localMappings.value[fieldName]
	} else {
		// Remove any existing mapping for this column
		Object.keys(localMappings.value).forEach((key) => {
			if (localMappings.value[key] === columnName) {
				delete localMappings.value[key]
			}
		})

		localMappings.value[fieldName] = columnName
	}

	// Clear validation error for this field
	delete validationErrors.value[fieldName]

	emitMappingsUpdate()
}

const autoMapFields = () => {
	const newMappings = {}

	// Auto-map based on field name similarity
	props.availableFields.forEach((field) => {
		const suggestion = findFieldSuggestion(field)
		if (suggestion && !Object.values(newMappings).includes(suggestion)) {
			newMappings[field.field] = suggestion
		}
	})

	localMappings.value = { ...localMappings.value, ...newMappings }
	emitMappingsUpdate()
}

const findFieldSuggestion = (field) => {
	const fieldName = field.label.toLowerCase()
	const fieldKey = field.field.toLowerCase()

	// Direct match
	let match = props.filePreview.headers.find(
		(header) =>
			header.toLowerCase() === fieldName || header.toLowerCase() === fieldKey,
	)

	if (match) return match

	// Partial match
	match = props.filePreview.headers.find((header) => {
		const headerLower = header.toLowerCase()
		return (
			fieldName.includes(headerLower) ||
			headerLower.includes(fieldName) ||
			fieldKey.includes(headerLower) ||
			headerLower.includes(fieldKey)
		)
	})

	if (match) return match

	// Pattern-based matching
	const patterns = {
		title: ["title", "name", "subject"],
		type: ["type", "category", "kind"],
		status: ["status", "state", "condition"],
		date: ["date", "time", "when"],
		description: ["description", "details", "note", "comment"],
		severity: ["severity", "priority", "level", "importance"],
		owner: ["owner", "assignee", "responsible", "user"],
	}

	for (const [key, keywordList] of Object.entries(patterns)) {
		if (fieldKey.includes(key) || fieldName.includes(key)) {
			match = props.filePreview.headers.find((header) => {
				const headerLower = header.toLowerCase()
				return keywordList.some(
					(keyword) =>
						headerLower.includes(keyword) || keyword.includes(headerLower),
				)
			})
			if (match) return match
		}
	}

	return null
}

const clearAllMappings = () => {
	localMappings.value = {}
	validationErrors.value = {}
	emitMappingsUpdate()
}

const getFieldPreview = (columnName) => {
	const columnIndex = props.filePreview.headers.indexOf(columnName)
	if (columnIndex === -1 || !props.filePreview.rows.length) return "No preview"

	const sampleValues = props.filePreview.rows
		.slice(0, 3)
		.map((row) => row[columnIndex])
		.filter((val) => val && val.trim())

	return sampleValues.length > 0 ? sampleValues.join(", ") : "No data"
}

const hasValidationError = (fieldName) => {
	return validationErrors.value[fieldName]
}

const getValidationError = (fieldName) => {
	return validationErrors.value[fieldName]
}

const validateMappings = () => {
	const errors = {}

	// Check required fields
	requiredFields.value.forEach((field) => {
		if (!localMappings.value[field.field]) {
			errors[field.field] = "This field is required"
		}
	})

	validationErrors.value = errors
	return Object.keys(errors).length === 0
}

const emitMappingsUpdate = () => {
	emit("mappings-updated", { ...localMappings.value })
}

// Watchers
watch(
	() => props.fieldMappings,
	(newMappings) => {
		localMappings.value = { ...newMappings }
	},
	{ deep: true },
)

// Initialize
onMounted(() => {
	// Auto-expand optional fields if any are already mapped
	if (optionalMappedCount.value > 0) {
		showOptionalFields.value = true
	}
})
</script>

<style scoped>
.field-mapping-step {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.mapping-header {
  margin-bottom: 1rem;
}

.step-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.step-description {
  color: var(--text-muted);
  margin: 0;
}

.mapping-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.section-title {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.source-preview {
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.preview-table-container {
  overflow-x: auto;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table th,
.preview-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.preview-table th {
  background: var(--background-color);
  font-weight: 600;
  color: var(--text-color);
}

.preview-table td {
  color: var(--text-muted);
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mapping-controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.field-group {
  margin-bottom: 2rem;
}

.group-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.group-title.required {
  color: var(--error-color);
}

.field-count {
  background: var(--background-color);
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.mapping-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.mapping-item {
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
  transition: all 0.2s;
}

.mapping-item.mapped {
  border-color: var(--success-color);
  background: var(--success-light);
}

.mapping-item.error {
  border-color: var(--error-color);
  background: var(--error-light);
}

.field-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.field-label {
  font-weight: 500;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.required-indicator {
  color: var(--error-color);
  font-weight: bold;
}

.field-type {
  font-size: 0.75rem;
  color: var(--text-muted);
  background: var(--background-color);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.mapping-control {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mapping-preview {
  font-size: 0.875rem;
  color: var(--text-muted);
  background: var(--background-color);
  padding: 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid var(--border-color);
}

.field-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--error-color);
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.mapping-summary {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.stat-value {
  font-weight: 600;
  color: var(--text-color);
}

.stat-value.complete {
  color: var(--success-color);
}

.stat-value.warning {
  color: var(--warning-color);
}

.unmapped-warning {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 0.375rem;
}

.warning-content h6 {
  font-weight: 600;
  color: #d97706;
  margin: 0 0 0.5rem 0;
}

.warning-content p {
  color: #92400e;
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
}

.unmapped-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.unmapped-column {
  background: #fbbf24;
  color: #92400e;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

@media (max-width: 768px) {
  .mapping-content {
    grid-template-columns: 1fr;
  }
  
  .summary-stats {
    grid-template-columns: 1fr;
  }
  
  .field-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .unmapped-warning {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>