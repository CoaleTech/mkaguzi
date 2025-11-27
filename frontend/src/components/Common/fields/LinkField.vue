<template>
  <div class="link-field">
    <Autocomplete
      v-model="selectedValue"
      :label="label"
      :placeholder="placeholder"
      :options="options"
      :loading="isSearching"
      @update:model-value="handleSelect"
      @update:query="handleSearch"
    >
      <template #target="{ open, close, togglePopover, isOpen }">
        <div class="w-full space-y-1.5">
          <label v-if="label" class="block text-xs font-medium text-gray-700">
            {{ label }}
            <span v-if="required" class="text-red-500">*</span>
          </label>
          <button
            type="button"
            class="flex h-9 w-full items-center justify-between gap-2 rounded border px-3 py-2 text-sm transition-colors"
            :class="[
              isOpen
                ? 'border-green-500 ring-2 ring-green-500 ring-opacity-20'
                : 'border-gray-300 hover:border-gray-400',
              disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
            ]"
            :disabled="disabled"
            @click="togglePopover"
          >
            <span v-if="displayLabel" class="truncate text-gray-900">
              {{ displayLabel }}
            </span>
            <span v-else class="text-gray-500">
              {{ placeholder || `Select ${label || 'option'}` }}
            </span>
            <svg
              class="h-4 w-4 text-gray-500 transition-transform"
              :class="{ 'rotate-180': isOpen }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </template>
    </Autocomplete>
    <p v-if="error" class="mt-1 text-xs text-red-500">{{ error }}</p>
  </div>
</template>

<script setup>
import { Autocomplete } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { useLinkField } from '@/composables/useLinkField'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  doctype: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  filters: {
    type: Object,
    default: () => ({})
  },
  fetchFields: {
    type: Array,
    default: () => []
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const { searchResults, isSearching, search, getValue } = useLinkField(
  props.doctype,
  props.filters
)

const selectedValue = ref(props.modelValue)
const displayLabel = ref('')

// Computed options for Autocomplete
const options = computed(() => {
  return searchResults.value.map(item => ({
    label: item.label,
    value: item.value
  }))
})

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
  selectedValue.value = newValue
  if (newValue) {
    // Fetch display label if needed
    fetchDisplayLabel(newValue)
  } else {
    displayLabel.value = ''
  }
}, { immediate: true })

/**
 * Fetch display label for the selected value
 */
const fetchDisplayLabel = async (value) => {
  if (!value) {
    displayLabel.value = ''
    return
  }

  // If we have fetchFields, use them to get a proper label
  if (props.fetchFields.length > 0) {
    const data = await getValue(value, props.fetchFields)
    if (data) {
      // Use the first field as display label
      displayLabel.value = data[props.fetchFields[0]] || value
    } else {
      displayLabel.value = value
    }
  } else {
    // Just use the value as label
    displayLabel.value = value
  }
}

/**
 * Handle search input
 */
const handleSearch = (query) => {
  if (query && query.length > 0) {
    search(query)
  }
}

/**
 * Handle selection from autocomplete
 */
const handleSelect = async (selected) => {
  if (!selected) {
    selectedValue.value = ''
    displayLabel.value = ''
    emit('update:modelValue', '')
    emit('change', { value: '', relatedData: null })
    return
  }

  const value = typeof selected === 'object' ? selected.value : selected
  selectedValue.value = value
  emit('update:modelValue', value)

  // Fetch related fields if specified
  let relatedData = null
  if (props.fetchFields.length > 0) {
    relatedData = await getValue(value, props.fetchFields)
    if (relatedData) {
      // Set display label from fetched data
      displayLabel.value = relatedData[props.fetchFields[0]] || value
    }
  } else {
    displayLabel.value = typeof selected === 'object' ? selected.label : value
  }

  // Emit change event with related data for auto-population
  emit('change', { value, relatedData })
}
</script>

<style scoped>
.link-field {
  width: 100%;
}
</style>
