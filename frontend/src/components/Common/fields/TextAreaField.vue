<template>
  <div class="textarea-field">
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <textarea
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :rows="rows"
      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent resize-vertical"
      :class="{
        'bg-gray-100 cursor-not-allowed': disabled,
        'border-red-500': error
      }"
      @input="handleChange"
    ></textarea>
    <p v-if="error" class="mt-1 text-xs text-red-500">{{ error }}</p>
  </div>
</template>

<script setup>
const props = defineProps({
	modelValue: {
		type: String,
		default: "",
	},
	label: {
		type: String,
		default: "",
	},
	placeholder: {
		type: String,
		default: "",
	},
	rows: {
		type: Number,
		default: 3,
	},
	required: {
		type: Boolean,
		default: false,
	},
	disabled: {
		type: Boolean,
		default: false,
	},
	error: {
		type: String,
		default: "",
	},
})

const emit = defineEmits(["update:modelValue", "change"])

const handleChange = (event) => {
	const value = event.target.value
	emit("update:modelValue", value)
	emit("change", value)
}
</script>

<style scoped>
.textarea-field {
  width: 100%;
}
</style>
