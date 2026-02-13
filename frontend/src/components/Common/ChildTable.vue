<template>
  <div class="child-table">
    <!-- Header with title and add button -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-medium text-gray-900">
        {{ title }}
        <span v-if="required" class="text-red-500">*</span>
      </h3>
      <Button variant="solid" theme="gray" size="sm" @click="addRow">
        <PlusIcon class="h-3.5 w-3.5 mr-1" />
        Add {{ modalTitle }}
      </Button>
    </div>

    <!-- Empty state -->
    <div
      v-if="rows.length === 0"
      class="text-center py-6 text-gray-500 border-2 border-dashed border-gray-300 rounded-lg"
    >
      <p>{{ emptyMessage || `No ${modalTitle.toLowerCase()}s added yet` }}</p>
      <p class="text-sm mt-1">Click "Add {{ modalTitle }}" to add a new record</p>
    </div>

    <!-- Data table -->
    <div v-else class="bg-gray-50 rounded-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gray-100">
            <tr>
              <th
                v-for="column in columns"
                :key="column.key"
                class="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase"
                :style="{ width: column.width }"
              >
                {{ column.label }}
              </th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="(row, index) in rows" :key="index" class="hover:bg-gray-50">
              <td
                v-for="column in columns"
                :key="column.key"
                class="px-4 py-2 text-sm text-gray-900"
              >
                <slot :name="`column-${column.key}`" :row="row" :value="row[column.key]">
                  <Badge v-if="column.component === 'Badge'" :theme="getBadgeTheme(row[column.key])">
                    {{ formatCellValue(row[column.key], column) }}
                  </Badge>
                  <span v-else>
                    {{ formatCellValue(row[column.key], column) }}
                  </span>
                </slot>
              </td>
              <td class="px-4 py-2">
                <div class="flex items-center space-x-2">
                  <Button variant="ghost" size="sm" @click="editRow(index, row)">
                    <EditIcon class="h-3.5 w-3.5" />
                  </Button>
                  <Button variant="ghost" size="sm" theme="red" @click="deleteRow(index)">
                    <TrashIcon class="h-3.5 w-3.5" />
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Dialog
      v-model="showModal"
      :options="{
        title: editingIndex !== null ? `Edit ${modalTitle}` : `Add ${modalTitle}`,
        size: modalSize
      }"
    >
      <template #body-content>
        <div class="space-y-4">
          <template v-for="field in visibleFormFields" :key="field.name">
            <!-- Handle raw HTML input elements -->
            <div v-if="typeof field.component === 'string'" class="field-wrapper">
              <label v-if="field.label && field.props?.type !== 'hidden'" class="block text-sm font-medium text-gray-700 mb-2">
                {{ field.label }}
                <span v-if="field.props?.required" class="text-red-500">*</span>
              </label>
              <input
                v-if="field.component === 'input'"
                v-model="formData[field.name]"
                v-bind="field.props"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
                :class="{ 'border-red-500': errors[field.name] }"
                @input="handleFieldChange(field, $event.target.value)"
              />
              <p v-if="errors[field.name]" class="mt-1 text-xs text-red-500">{{ errors[field.name] }}</p>
            </div>
            <!-- Handle Vue component elements -->
            <component
              v-else
              :is="field.component"
              v-model="formData[field.name]"
              v-bind="field.props"
              :label="field.label"
              :required="field.props?.required"
              :error="errors[field.name]"
              @change="(event) => handleFieldChange(field, event)"
            />
          </template>
        </div>
      </template>
      <template #actions>
        <Button variant="ghost" @click="closeModal">
          Cancel
        </Button>
        <Button variant="solid" @click="saveRow" class="bg-green-600 hover:bg-green-700">
          Save {{ modalTitle }}
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Badge, Button, Dialog } from 'frappe-ui'
import { EditIcon, PlusIcon, TrashIcon } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    required: true
  },
  modalTitle: {
    type: String,
    required: true
  },
  columns: {
    type: Array,
    required: true,
    validator: (columns) => {
      return columns.every(col =>
        typeof col === 'object' && 'key' in col && 'label' in col
      )
    }
  },
  formFields: {
    type: Array,
    required: true,
    validator: (fields) => {
      return fields.every(field =>
        typeof field === 'object' &&
        'name' in field &&
        'component' in field
      )
    }
  },
  validate: {
    type: Function,
    default: null
  },
  emptyMessage: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  modalSize: {
    type: String,
    default: 'xl'
  }
})

const emit = defineEmits(['update:modelValue', 'row-change'])

const rows = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// Filter out hidden fields from form display
const visibleFormFields = computed(() => {
  return props.formFields.filter(field => field.props?.type !== 'hidden')
})

const showModal = ref(false)
const editingIndex = ref(null)
const formData = ref({})
const errors = ref({})

/**
 * Initialize form data with default values from field configuration
 */
const initializeFormData = () => {
  const data = {}
  props.formFields.forEach(field => {
    data[field.name] = field.defaultValue !== undefined ? field.defaultValue : ''
  })
  return data
}

/**
 * Add new row - open modal with empty form
 */
const addRow = () => {
  editingIndex.value = null
  formData.value = initializeFormData()
  errors.value = {}
  showModal.value = true
}

/**
 * Edit existing row - open modal with row data
 */
const editRow = (index, row) => {
  editingIndex.value = index
  formData.value = { ...row }
  errors.value = {}
  showModal.value = true
}

/**
 * Save row (create or update)
 */
const saveRow = () => {
  // Validate if validator is provided
  if (props.validate) {
    const validationErrors = props.validate(formData.value)
    if (validationErrors) {
      errors.value = validationErrors
      return
    }
  }

  // Clear errors
  errors.value = {}

  // Update or add row
  const updatedRows = [...rows.value]
  if (editingIndex.value !== null) {
    // Update existing
    updatedRows[editingIndex.value] = { ...formData.value }
  } else {
    // Add new
    updatedRows.push({ ...formData.value })
  }

  rows.value = updatedRows
  emit('row-change', formData.value)
  showModal.value = false
}

/**
 * Delete row with confirmation
 */
const deleteRow = (index) => {
  if (confirm(`Are you sure you want to delete this ${props.modalTitle.toLowerCase()}?`)) {
    const updatedRows = [...rows.value]
    updatedRows.splice(index, 1)
    rows.value = updatedRows
  }
}

/**
 * Close modal without saving
 */
const closeModal = () => {
  showModal.value = false
  errors.value = {}
}

/**
 * Handle field change events (for auto-population)
 */
const handleFieldChange = (field, event) => {
  // Handle auto-population for Link fields
  if (field.autoPopulate && event && event.relatedData) {
    Object.entries(field.autoPopulate).forEach(([sourceField, targetField]) => {
      if (event.relatedData[sourceField] !== undefined) {
        formData.value[targetField] = event.relatedData[sourceField]
      }
    })
  }
}

/**
 * Format cell value based on column configuration
 */
const formatCellValue = (value, column) => {
  if (value === null || value === undefined || value === '') {
    return '-'
  }

  if (column.format) {
    return column.format(value)
  }

  if (column.type === 'currency') {
    return `$${parseFloat(value).toFixed(2)}`
  }

  if (column.type === 'percent') {
    return `${parseFloat(value).toFixed(1)}%`
  }

  if (column.type === 'number') {
    return parseFloat(value).toFixed(2)
  }

  if (column.type === 'boolean') {
    return value ? 'Yes' : 'No'
  }

  return value
}

/**
 * Get badge theme based on value
 */
const getBadgeTheme = (value) => {
  const lowerValue = String(value).toLowerCase()

  if (lowerValue.includes('completed') || lowerValue.includes('active')) {
    return 'green'
  }
  if (lowerValue.includes('pending') || lowerValue.includes('assigned')) {
    return 'blue'
  }
  if (lowerValue.includes('removed') || lowerValue.includes('rejected')) {
    return 'red'
  }
  return 'gray'
}
</script>

<style scoped>
.child-table {
  width: 100%;
}
</style>
