<template>
  <div class="inline-child-table w-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
      <div class="flex items-center space-x-2">
        <Badge
          v-if="required && items.length === 0"
          theme="red"
          variant="subtle"
        >
          Required
        </Badge>
        <span class="text-sm text-gray-500">
          {{ items.length }} {{ title.toLowerCase() }}
        </span>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto border border-gray-200 rounded-lg">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-16">
              #
            </th>
            <th
              v-for="column in effectiveColumns"
              :key="column.key"
              class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              :style="{ minWidth: column.width || '140px', width: column.width || 'auto' }"
            >
              <div class="flex items-center">
                <span>{{ column.label }}</span>
                <span v-if="column.required" class="text-red-500 ml-1">*</span>
              </div>
            </th>
            <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="(row, idx) in items"
            :key="row._uid || row.name || idx"
            class="hover:bg-gray-50"
          >
            <!-- Row number -->
            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 text-center align-middle">
              {{ idx + 1 }}
            </td>

            <!-- Dynamic columns -->
            <td
              v-for="column in effectiveColumns"
              :key="column.key"
              class="px-4 py-3 whitespace-nowrap align-middle"
              :class="getCellAlignmentClass(column.fieldType)"
            >
              <!-- Custom slot support -->
              <slot
                :name="`cell-${column.key}`"
                :row="row"
                :column="column"
              >
                <!-- Default rendering -->
                <component
                  v-if="componentFor(column.fieldType)"
                  :is="componentFor(column.fieldType)"
                  v-model="row[column.key]"
                  v-bind="inputProps(column)"
                  :ref="getRefForRow(idx, column.key)"
                />
                <!-- Link field with autocomplete -->
                <div
                  v-if="column.fieldType === 'link'"
                  class="relative"
                >
                  <Input
                    :model-value="getLinkFieldValue(column, row)"
                    :placeholder="column.placeholder || `Select ${column.label}`"
                    size="sm"
                    class="w-full"
                    @update:model-value="updateLinkFieldValue(column, row, $event)"
                    @input="onLinkInput(column, row, $event)"
                    @focus="onLinkFocus(column, row, idx)"
                    @blur="onLinkBlur"
                  />
                  <!-- show display name if set -->
                  <div
                    v-if="column.displayFieldKey && row[column.displayFieldKey] && row[column.displayFieldKey] !== row[column.key]"
                    class="text-xs text-gray-500 mt-1"
                  >
                    {{ row[column.key] }}: {{ row[column.displayFieldKey] }}
                  </div>

                  <!-- Suggestions dropdown -->
                  <div
                    v-if="linkSuggestions.length > 0 && activeLinkField === `${column.key}-${idx}`"
                    class="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm"
                  >
                    <div
                      v-for="suggestion in linkSuggestions"
                      :key="suggestion.value"
                      class="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-gray-100"
                      @mousedown.prevent="selectLinkSuggestion(column, row, suggestion)"
                    >
                      <span class="font-normal ml-3 block truncate">
                        {{ suggestion.label }}
                      </span>
                    </div>
                  </div>
                </div>
                <!-- If no fieldType matched, fallback to text Input -->
                <Input
                  v-if="!componentFor(column.fieldType) && column.fieldType !== 'link'"
                  v-model="row[column.key]"
                  :placeholder="column.placeholder || column.label"
                  size="sm"
                  class="w-full"
                  :ref="getRefForRow(idx, column.key)"
                />
              </slot>
            </td>

            <!-- Actions (remove) -->
            <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-center align-middle">
              <div class="flex items-center justify-center">
                <Button
                  variant="ghost"
                  size="sm"
                  theme="red"
                  @click="removeRow(idx)"
                  :disabled="items.length <= (minRows || 0)"
                >
                  <XIcon class="h-4 w-4" />
                </Button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty state illustration -->
    <div
      v-if="items.length === 0"
      class="text-center py-8 text-gray-500 border-2 border-dashed border-gray-300 rounded-lg mt-4"
    >
      <div class="text-sm">No {{ title.toLowerCase() }} added yet.</div>
      <div class="text-xs mt-1">Click "Add Row" to get started.</div>
    </div>

    <!-- Action buttons -->
    <div class="mt-4 flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <Button variant="solid" size="sm" theme="blue" @click="addRow">
          <PlusIcon class="h-4 w-4 mr-2" />
          Add {{ modalTitle || 'Row' }}
        </Button>
        <Button
          v-if="allowBulkAdd"
          variant="outline"
          size="sm"
          @click="addMultiple"
        >
          Add Multiple
        </Button>
      </div>
      <div class="flex items-center space-x-2">
        <Button
          v-if="allowExport"
          variant="outline"
          size="sm"
          @click="download"
        >
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button
          v-if="allowImport"
          variant="outline"
          size="sm"
          @click="upload"
        >
          <UploadIcon class="h-4 w-4 mr-2" />
          Import
        </Button>
      </div>
    </div>

    <!-- Validation error block -->
    <div v-if="validationErrors.length > 0" class="mt-4">
      <div class="bg-red-50 border border-red-200 rounded-md p-4">
        <div class="flex">
          <AlertTriangleIcon class="h-5 w-5 text-red-400" />
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">
              Validation Errors
            </h3>
            <div class="mt-2 text-sm text-red-700">
              <ul class="list-disc pl-5 space-y-1">
                <li v-for="error in validationErrors" :key="error">
                  {{ error }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Button, Input, Select, Checkbox, Badge } from 'frappe-ui'
import {
  PlusIcon,
  XIcon,
  DownloadIcon,
  UploadIcon,
  AlertTriangleIcon
} from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: 'Items'
  },
  modalTitle: {
    type: String,
    default: 'Item'
  },
  doctype: {
    type: String,
    default: null
  },
  columns: {
    type: Array,
    default: () => []
  },
  validate: {
    type: Function,
    default: null
  },
  required: {
    type: Boolean,
    default: false
  },
  minRows: {
    type: Number,
    default: 0
  },
  maxRows: {
    type: Number,
    default: null
  },
  autoAddRow: {
    type: Boolean,
    default: false
  },
  allowBulkAdd: {
    type: Boolean,
    default: false
  },
  allowExport: {
    type: Boolean,
    default: false
  },
  allowImport: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'add-row', 'remove-row', 'validate'])

const linkSuggestions = ref([])
const activeLinkField = ref(null)
const validationErrors = ref([])

// reactive alias for v-model
const items = computed({
  get: () => props.modelValue || [],
  set: (val) => {
    emit('update:modelValue', val)
    runValidation(val)
  }
})

const doctypeSchema = ref(null)

// Determine effective columns
const effectiveColumns = computed(() => {
  if (props.columns && props.columns.length > 0) {
    return props.columns
  }
  if (doctypeSchema.value && doctypeSchema.value.fields) {
    return generateColumnsFromDoctype(doctypeSchema.value)
  }
  return []
})

// Mapping of fieldTypes → components
function componentFor(fieldType) {
  switch (fieldType) {
    case 'text':
    case 'data':
    case 'small_text':
    case 'long_text':
      return Input
    case 'int':
    case 'float':
    case 'currency':
      return Input
    case 'date':
    case 'datetime':
      return Input
    case 'select':
      return Select
    case 'check':
      return Checkbox
    case 'link':
      // link is handled specially in template
      return null
    default:
      return Input // fallback to text input
  }
}

// Returns props to bind to the component
function inputProps(column) {
  const p = {}
  const fieldType = column.fieldType.toLowerCase()

  // Handle numeric types
  if (['int', 'float', 'currency'].includes(fieldType)) {
    p.type = 'number'
    if (column.min !== undefined) p.min = column.min
    if (column.step !== undefined) p.step = column.step
    if (fieldType === 'float' || fieldType === 'currency') {
      p.step = p.step || '0.01'
    }
  }
  // Handle date types
  else if (fieldType === 'date') {
    p.type = 'date'
  }
  else if (fieldType === 'datetime') {
    p.type = 'datetime-local'
  }
  // Handle email field (Data with Email option)
  else if (fieldType === 'data' && column.options === 'Email') {
    p.type = 'email'
  }
  // Handle phone field (Data field that might be used for phone)
  else if (fieldType === 'data' && (column.key?.toLowerCase().includes('phone') || column.label?.toLowerCase().includes('phone'))) {
    p.type = 'tel'
  }
  // Handle select options
  if (fieldType === 'select' && column.options) {
    p.options = column.options
  }

  p.placeholder = column.placeholder || column.label
  p.size = 'sm'
  p.class = 'w-full'
  return p
}

// Get cell alignment class based on field type
function getCellAlignmentClass(fieldType) {
  const type = fieldType.toLowerCase()
  switch (type) {
    case 'int':
    case 'float':
    case 'currency':
      return 'text-right'
    case 'check':
      return 'text-center'
    case 'date':
    case 'datetime':
    case 'select':
    case 'link':
    case 'text':
    case 'data':
    case 'small_text':
    case 'long_text':
    case 'email':
    default:
      return 'text-left'
  }
}

// Fetch DocType schema if doctype prop provided
async function fetchSchema() {
  if (!props.doctype || typeof frappe === 'undefined') return
  try {
    const res = await frappe.call({
      method: 'frappe.client.get',
      args: {
        doctype: 'DocType',
        name: props.doctype
      }
    })
    if (res.message) {
      doctypeSchema.value = res.message
    }
  } catch (err) {
    console.error('Error fetching schema for doctype', props.doctype, err)
  }
}

function generateColumnsFromDoctype(schema) {
  return schema.fields
    .filter((f) => {
      // Include fields that are in list view or name/title fields
      const isInList = f.in_list_view || ['name', 'title'].includes(f.fieldname)
      // Exclude read-only display fields that are just for showing linked field names
      const isDisplayField = f.read_only && f.fieldname.endsWith('_name') && schema.fields.some(field =>
        field.fieldtype.toLowerCase() === 'link' && `${field.fieldname}_name` === f.fieldname
      )
      return isInList && !isDisplayField
    })
    .map((f) => {
      const fieldtype = f.fieldtype.toLowerCase()
      const col = {
        key: f.fieldname,
        label: f.label,
        fieldType: fieldtype,
        required: !!f.reqd,
        width: getColumnWidth(f.fieldtype),
        placeholder: `Enter ${f.label}`,
        options: f.options
      }

      // Handle select options
      if (fieldtype === 'select' && f.options) {
        col.options = f.options.split('\n').map((opt) => ({
          value: opt.trim(),
          label: opt.trim()
        }))
      }

      // Handle link fields
      if (fieldtype === 'link') {
        col.doctype = f.options
        // Check if there's a corresponding display field (e.g., team_member -> team_member_name)
        const displayFieldName = `${f.fieldname}_name`
        const hasDisplayField = schema.fields.some(field => field.fieldname === displayFieldName)
        if (hasDisplayField) {
          col.displayFieldKey = displayFieldName
        }
        // optional fetchMap might be passed via props.columns override
      }

      // Handle special data types
      if (fieldtype === 'data' && f.options === 'Email') {
        col.fieldType = 'email'
      }

      return col
    })
}

function getColumnWidth(fieldtype) {
  const type = fieldtype.toLowerCase()
  switch (type) {
    case 'int':
    case 'float':
    case 'currency':
      return '120px'
    case 'check':
      return '80px'
    case 'date':
    case 'datetime':
      return '130px'
    case 'select':
      return '160px'
    case 'link':
      return '180px'
    case 'small_text':
    case 'long_text':
      return '200px'
    case 'email':
      return '200px'
    case 'data':
    case 'text':
    default:
      return '160px'
  }
}

// --- Row / Data Management ---

function getDefaultForFieldType(type) {
  const fieldType = type.toLowerCase()
  switch (fieldType) {
    case 'int':
    case 'float':
    case 'currency':
      return 0
    case 'check':
      return false
    case 'date':
    case 'datetime':
      return ''
    case 'select':
      return ''
    case 'link':
      return ''
    case 'email':
    case 'data':
    case 'text':
    case 'small_text':
    case 'long_text':
    default:
      return ''
  }
}

function addRow() {
  if (props.maxRows != null && items.value.length >= props.maxRows) {
    return
  }
  const newRow = {}
  effectiveColumns.value.forEach((col) => {
    if (col && col.key) {
      newRow[col.key] =
        col.default !== undefined
          ? col.default
          : getDefaultForFieldType(col.fieldType)
      // compute computed fields too
      if (typeof col.compute === 'function') {
        newRow[col.key] = col.compute(newRow)
      }
    }
  })
  items.value = [...items.value, newRow]
  emit('add-row', newRow)

  // autofocus first field of new row
  nextTick(() => {
    if (effectiveColumns.value.length > 0) {
      const refName = `input-${items.value.length - 1}-${effectiveColumns.value[0].key}`
      const el = refsMap[refName]
      if (el && el.focus) {
        el.focus()
      }
    }
  })
}

function removeRow(index) {
  if (items.value.length <= props.minRows) return
  const removed = items.value[index]
  items.value = items.value.filter((_, i) => i !== index)
  emit('remove-row', removed)
}

// Map of refs to inputs to implement autofocus
const refsMap = {}
function getRefForRow(idx, key) {
  const refName = `input-${idx}-${key}`
  refsMap[refName] = null
  return refName
}

// Computed property for link field display value
function getLinkFieldValue(column, row) {
  if (column.displayFieldKey && row[column.displayFieldKey]) {
    return row[column.displayFieldKey]
  }
  return row[column.key] || ''
}

// Update link field value
function updateLinkFieldValue(column, row, value) {
  // If we have a display field, update it, otherwise update the main field
  if (column.displayFieldKey) {
    row[column.displayFieldKey] = value
  } else {
    row[column.key] = value
  }
}

// Watch for items changes to re-compute computed fields & validate
watch(
  items,
  (newVal) => {
    newVal.forEach((row) => {
      effectiveColumns.value.forEach((col) => {
        if (col && typeof col.compute === 'function') {
          row[col.key] = col.compute(row)
        }
      })
    })
    runValidation(newVal)
  },
  { deep: true }
)

function runValidation(rows) {
  validationErrors.value = []
  rows.forEach((row, idx) => {
    effectiveColumns.value.forEach((col) => {
      if (!col || !col.key) return
      // required check
      if (col.required && (row[col.key] === '' || row[col.key] == null)) {
        validationErrors.value.push(
          `Row ${idx + 1} - ${col.label}: Required`
        )
      }
      // custom validator
      if (typeof col.validator === 'function') {
        const msg = col.validator(row[col.key], row, rows)
        if (msg) {
          validationErrors.value.push(`Row ${idx + 1} - ${col.label}: ${msg}`)
        }
      }
    })
    // row-level validate function
    if (props.validate) {
      const res = props.validate(row, rows, idx)
      if (res) {
        Object.entries(res).forEach(([fld, message]) => {
          const col = effectiveColumns.value.find((c) => c && c.key === fld)
          const label = col ? col.label : fld
          validationErrors.value.push(
            `Row ${idx + 1} - ${label}: ${message}`
          )
        })
      }
    }
  })
  emit('validate', validationErrors.value.length === 0)
}

// --- Link field auto-complete logic ---

async function onLinkInput(column, row, ev) {
  const val = ev.target.value
  if (!column.doctype || typeof frappe === 'undefined') return
  if (val.length < 2) {
    linkSuggestions.value = []
    return
  }
  try {
    const resp = await frappe.call({
      method: 'frappe.client.get_list',
      args: {
        doctype: column.doctype,
        filters: { name: ['like', `%${val}%`] },
        fields: ['name', 'title', ...((column.fetchMap && Object.values(column.fetchMap)) || [])],
        limit: 10
      }
    })
    linkSuggestions.value = resp.message.map((d) => ({
      value: d.name,
      label: d.title || d.name,
      data: d
    }))
  } catch (err) {
    console.error('Link suggestions error', err)
    linkSuggestions.value = []
  }
}

function onLinkFocus(column, row, idx) {
  activeLinkField.value = `${column.key}-${idx}`
}

function onLinkBlur() {
  setTimeout(() => {
    activeLinkField.value = null
    linkSuggestions.value = []
  }, 200)
}

function selectLinkSuggestion(column, row, suggestion) {
  // Set the main link field to the ID
  row[column.key] = suggestion.value
  // Set the display field to the name/title
  if (column.displayFieldKey) {
    row[column.displayFieldKey] = suggestion.label
  }
  // Handle additional field mapping if configured
  if (column.fetchMap) {
    for (const [targetKey, sourceField] of Object.entries(column.fetchMap)) {
      row[targetKey] = suggestion.data[sourceField]
    }
  }
  linkSuggestions.value = []
  activeLinkField.value = null
}

// --- Placeholder stubs ---
function addMultiple() {
  console.log('bulk-add not implemented yet')
}
function download() {
  console.log('export not implemented yet')
}
function upload() {
  console.log('import not implemented yet')
}

// --- Initialization ---
if (props.autoAddRow && items.value.length === 0) {
  addRow()
}

watch(
  () => props.doctype,
  () => {
    if (props.doctype) {
      fetchSchema()
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.inline-child-table {
  width: 100%;
}
</style>
