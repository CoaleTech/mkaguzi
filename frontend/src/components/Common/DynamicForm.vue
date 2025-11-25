<template>
  <div class="space-y-6">
    <!-- Form Header -->
    <div v-if="title || description" class="border-b border-gray-200 pb-4">
      <h3 v-if="title" class="text-lg font-medium text-gray-900">
        {{ title }}
      </h3>
      <p v-if="description" class="text-sm text-gray-500 mt-1">
        {{ description }}
      </p>
    </div>

    <!-- Form Fields -->
    <div class="space-y-6">
      <div
        v-for="(field, index) in visibleFields"
        :key="field.name || index"
        class="space-y-2"
      >
        <!-- Field Label -->
        <label
          v-if="field.label"
          :for="field.name"
          class="block text-sm font-medium text-gray-700"
          :class="{ 'text-red-600': hasFieldError(field.name) }"
        >
          {{ field.label }}
          <span v-if="field.required" class="text-red-500">*</span>
        </label>

        <!-- Field Description -->
        <p v-if="field.description" class="text-sm text-gray-500">
          {{ field.description }}
        </p>

        <!-- Field Input -->
        <div class="relative">
          <!-- Text Input -->
          <Input
            v-if="field.type === 'text' || field.type === 'email' || field.type === 'url' || field.type === 'password'"
            :id="field.name"
            v-model="formData[field.name]"
            :type="field.type"
            :placeholder="field.placeholder"
            :disabled="field.disabled || loading"
            :maxlength="field.maxlength"
            :class="fieldInputClasses(field)"
            @input="onFieldChange(field.name)"
            @blur="onFieldBlur(field.name)"
          />

          <!-- Textarea -->
          <Textarea
            v-else-if="field.type === 'textarea'"
            :id="field.name"
            v-model="formData[field.name]"
            :placeholder="field.placeholder"
            :disabled="field.disabled || loading"
            :maxlength="field.maxlength"
            :rows="field.rows || 3"
            :class="fieldInputClasses(field)"
            @input="onFieldChange(field.name)"
            @blur="onFieldBlur(field.name)"
          />

          <!-- Number Input -->
          <Input
            v-else-if="field.type === 'number'"
            :id="field.name"
            v-model.number="formData[field.name]"
            type="number"
            :placeholder="field.placeholder"
            :disabled="field.disabled || loading"
            :min="field.min"
            :max="field.max"
            :step="field.step"
            :class="fieldInputClasses(field)"
            @input="onFieldChange(field.name)"
            @blur="onFieldBlur(field.name)"
          />

          <!-- Select -->
          <Select
            v-else-if="field.type === 'select'"
            :id="field.name"
            v-model="formData[field.name]"
            :options="getSelectOptions(field)"
            :placeholder="field.placeholder"
            :disabled="field.disabled || loading"
            :multiple="field.multiple"
            :class="fieldInputClasses(field)"
            @change="onFieldChange(field.name)"
          />

          <!-- Checkbox -->
          <div v-else-if="field.type === 'checkbox'" class="space-y-2">
            <Checkbox
              v-for="option in field.options"
              :key="option.value"
              :id="`${field.name}-${option.value}`"
              v-model="formData[field.name]"
              :value="option.value"
              :disabled="field.disabled || loading"
              :class="fieldInputClasses(field)"
              @change="onFieldChange(field.name)"
            >
              {{ option.label }}
            </Checkbox>
          </div>

          <!-- Radio -->
          <div v-else-if="field.type === 'radio'" class="space-y-2">
            <div
              v-for="option in field.options"
              :key="option.value"
              class="flex items-center"
            >
              <input
                :id="`${field.name}-${option.value}`"
                v-model="formData[field.name]"
                :value="option.value"
                type="radio"
                :name="field.name"
                :disabled="field.disabled || loading"
                :class="fieldInputClasses(field)"
                @change="onFieldChange(field.name)"
              />
              <label
                :for="`${field.name}-${option.value}`"
                class="ml-2 text-sm text-gray-700"
              >
                {{ option.label }}
              </label>
            </div>
          </div>

          <!-- Date Input -->
          <Input
            v-else-if="field.type === 'date'"
            :id="field.name"
            v-model="formData[field.name]"
            type="date"
            :placeholder="field.placeholder"
            :disabled="field.disabled || loading"
            :min="field.min"
            :max="field.max"
            :class="fieldInputClasses(field)"
            @input="onFieldChange(field.name)"
            @blur="onFieldBlur(field.name)"
          />

          <!-- File Input -->
          <div v-else-if="field.type === 'file'" class="space-y-2">
            <input
              :id="field.name"
              ref="fileInput"
              type="file"
              :multiple="field.multiple"
              :accept="field.accept"
              :disabled="field.disabled || loading"
              class="hidden"
              @change="onFileChange(field.name, $event)"
            />
            <div class="flex items-center space-x-2">
              <Button
                variant="outline"
                @click="$refs.fileInput[index].click()"
                :disabled="field.disabled || loading"
              >
                <UploadIcon class="h-4 w-4 mr-2" />
                Choose File{{ field.multiple ? 's' : '' }}
              </Button>
              <span v-if="formData[field.name]" class="text-sm text-gray-600">
                {{ getFileName(formData[field.name]) }}
              </span>
            </div>
          </div>

          <!-- Custom Field -->
          <slot
            v-else
            :name="`field-${field.name}`"
            :field="field"
            :value="formData[field.name]"
            :on-change="(value) => onFieldChange(field.name, value)"
            :error="getFieldError(field.name)"
          />
        </div>

        <!-- Field Error -->
        <div v-if="hasFieldError(field.name)" class="text-sm text-red-600">
          {{ getFieldError(field.name) }}
        </div>

        <!-- Field Help -->
        <div v-if="field.help" class="text-sm text-gray-500">
          {{ field.help }}
        </div>
      </div>
    </div>

    <!-- Form Actions -->
    <div v-if="showActions" class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
      <Button
        v-if="showCancel"
        variant="outline"
        @click="onCancel"
        :disabled="loading"
      >
        {{ cancelText }}
      </Button>
      <Button
        v-if="showReset"
        variant="outline"
        color="red"
        @click="onReset"
        :disabled="loading"
      >
        {{ resetText }}
      </Button>
      <Button
        @click="onSubmit"
        :disabled="!isValid || loading"
        :loading="loading"
      >
        {{ submitText }}
      </Button>
    </div>
  </div>
</template>

<script setup>
import { Button, Checkbox, Input, Select, Textarea } from "frappe-ui"
import { UploadIcon } from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"

// Props
const props = defineProps({
	fields: {
		type: Array,
		required: true,
	},
	modelValue: {
		type: Object,
		default: () => ({}),
	},
	title: {
		type: String,
		default: "",
	},
	description: {
		type: String,
		default: "",
	},
	loading: {
		type: Boolean,
		default: false,
	},
	showActions: {
		type: Boolean,
		default: true,
	},
	showCancel: {
		type: Boolean,
		default: false,
	},
	showReset: {
		type: Boolean,
		default: false,
	},
	submitText: {
		type: String,
		default: "Submit",
	},
	cancelText: {
		type: String,
		default: "Cancel",
	},
	resetText: {
		type: String,
		default: "Reset",
	},
	validationRules: {
		type: Object,
		default: () => ({}),
	},
})

// Emits
const emit = defineEmits([
	"update:modelValue",
	"submit",
	"cancel",
	"reset",
	"field-change",
	"field-blur",
])

// Reactive state
const formData = ref({ ...props.modelValue })
const errors = ref({})
const touched = ref({})

// Computed properties
const visibleFields = computed(() => {
	return props.fields.filter((field) => {
		if (field.condition) {
			return evaluateCondition(field.condition)
		}
		return true
	})
})

const isValid = computed(() => {
	return visibleFields.value.every((field) => !hasFieldError(field.name))
})

// Methods
const fieldInputClasses = (field) => {
	const baseClasses = "w-full"
	const errorClasses = hasFieldError(field.name)
		? "border-red-300 focus:border-red-500"
		: ""
	return `${baseClasses} ${errorClasses}`
}

const hasFieldError = (fieldName) => {
	return errors.value[fieldName] && touched.value[fieldName]
}

const getFieldError = (fieldName) => {
	return errors.value[fieldName]
}

const getSelectOptions = (field) => {
	if (!field.options) return []

	return field.options.map((option) => ({
		label: option.label || option,
		value: option.value || option,
	}))
}

const getFileName = (file) => {
	if (!file) return ""
	if (Array.isArray(file)) {
		return `${file.length} file${file.length > 1 ? "s" : ""} selected`
	}
	return file.name
}

const onFieldChange = (fieldName, value) => {
	const fieldValue = value !== undefined ? value : formData.value[fieldName]

	// Update form data
	formData.value[fieldName] = fieldValue

	// Emit update
	emit("update:modelValue", { ...formData.value })

	// Validate field
	validateField(fieldName)

	// Emit field change
	emit("field-change", {
		field: fieldName,
		value: fieldValue,
	})
}

const onFieldBlur = (fieldName) => {
	touched.value[fieldName] = true
	validateField(fieldName)

	emit("field-blur", {
		field: fieldName,
		value: formData.value[fieldName],
	})
}

const onFileChange = (fieldName, event) => {
	const files = Array.from(event.target.files)
	const value = event.target.multiple ? files : files[0]
	onFieldChange(fieldName, value)
}

const validateField = (fieldName) => {
	const field = props.fields.find((f) => f.name === fieldName)
	if (!field) return

	const value = formData.value[fieldName]
	const rules = props.validationRules[fieldName] || field.validation || []

	let error = null

	// Required validation
	if (
		field.required &&
		(value === null || value === undefined || value === "")
	) {
		error = `${field.label || fieldName} is required`
	}

	// Custom validation rules
	if (!error && rules.length > 0) {
		for (const rule of rules) {
			if (typeof rule === "function") {
				const result = rule(value, formData.value)
				if (result !== true) {
					error = result
					break
				}
			} else if (rule.type === "email" && value) {
				const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
				if (!emailRegex.test(value)) {
					error = "Please enter a valid email address"
				}
			} else if (
				rule.type === "minLength" &&
				value &&
				value.length < rule.value
			) {
				error = `Must be at least ${rule.value} characters`
			} else if (
				rule.type === "maxLength" &&
				value &&
				value.length > rule.value
			) {
				error = `Must be no more than ${rule.value} characters`
			} else if (rule.type === "pattern" && value && !rule.value.test(value)) {
				error = rule.message || "Invalid format"
			}
		}
	}

	errors.value[fieldName] = error
}

const evaluateCondition = (condition) => {
	// Simple condition evaluation
	// Supports: { field: 'fieldName', operator: 'equals', value: 'expectedValue' }
	const { field, operator, value } = condition
	const fieldValue = formData.value[field]

	switch (operator) {
		case "equals":
			return fieldValue === value
		case "notEquals":
			return fieldValue !== value
		case "contains":
			return Array.isArray(fieldValue) ? fieldValue.includes(value) : false
		case "notContains":
			return Array.isArray(fieldValue) ? !fieldValue.includes(value) : true
		default:
			return true
	}
}

const onSubmit = () => {
	// Mark all fields as touched
	visibleFields.value.forEach((field) => {
		touched.value[field.name] = true
		validateField(field.name)
	})

	if (isValid.value) {
		emit("submit", { ...formData.value })
	}
}

const onCancel = () => {
	emit("cancel")
}

const onReset = () => {
	formData.value = {}
	errors.value = {}
	touched.value = {}
	emit("reset")
}

// Watch for external model value changes
watch(
	() => props.modelValue,
	(newValue) => {
		formData.value = { ...newValue }
	},
	{ deep: true },
)

// Initialize form data and validation
onMounted(() => {
	formData.value = { ...props.modelValue }

	// Initialize touched state
	props.fields.forEach((field) => {
		touched.value[field.name] = false
	})
})
</script>