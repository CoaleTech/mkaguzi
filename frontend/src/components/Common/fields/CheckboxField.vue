<template>
  <div class="checkbox-field">
    <label class="flex items-center space-x-2 cursor-pointer">
      <Checkbox
        :model-value="modelValue"
        :disabled="disabled"
        @update:model-value="handleChange"
      />
      <span class="text-sm text-gray-700">
        {{ label }}
        <span v-if="required" class="text-red-500">*</span>
      </span>
    </label>
    <p v-if="error" class="mt-1 text-xs text-red-500">{{ error }}</p>
  </div>
</template>

<script setup>
import { Checkbox } from 'frappe-ui'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  label: {
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
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const handleChange = (value) => {
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<style scoped>
.checkbox-field {
  width: 100%;
}
</style>
