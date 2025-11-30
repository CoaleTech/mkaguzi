<template>
  <div class="text-field">
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <input
      :type="inputType"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :min="min"
      :max="max"
      :step="step"
      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
      :class="{
        'bg-gray-100 cursor-not-allowed': disabled,
        'border-red-500': error
      }"
      @input="handleChange"
    />
    <p v-if="description" class="mt-1 text-xs text-gray-500">{{ description }}</p>
    <p v-if="error" class="mt-1 text-xs text-red-500">{{ error }}</p>
  </div>
</template>

<script setup>
const props = defineProps({
	modelValue: {
		type: [String, Number],
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
	description: {
		type: String,
		default: "",
	},
	inputType: {
		type: String,
		default: "text",
	},
	min: {
		type: [String, Number],
		default: null,
	},
	max: {
		type: [String, Number],
		default: null,
	},
	step: {
		type: [String, Number],
		default: null,
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
	const value =
		props.inputType === "number"
			? Number(event.target.value)
			: event.target.value
	emit("update:modelValue", value)
	emit("change", value)
}
</script>

<style scoped>
.text-field {
  width: 100%;
}
</style>