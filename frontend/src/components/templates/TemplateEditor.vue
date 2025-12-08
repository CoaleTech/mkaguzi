<template>
  <div class="template-editor">
    <Form @submit="handleSubmit" class="space-y-6">
      <!-- Basic Information -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FormControl
          label="Template Name"
          v-model="form.template_name"
          type="text"
          required
          placeholder="Enter template name"
          :error="errors.template_name"
        />

        <FormControl
          label="Template Type"
          v-model="form.template_type"
          type="select"
          required
          :options="templateTypeOptions"
          :error="errors.template_type"
        />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FormControl
          label="Category"
          v-model="form.category"
          type="select"
          :options="categoryOptions"
          :error="errors.category"
        />

        <FormControl
          label="Template Engine"
          v-model="form.template_engine"
          type="select"
          required
          :options="engineOptions"
          :error="errors.template_engine"
        />
      </div>

      <FormControl
        label="Description"
        v-model="form.description"
        type="textarea"
        placeholder="Describe what this template is used for"
        :error="errors.description"
      />

      <!-- Template Content -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Template Content
          <span class="text-red-500">*</span>
        </label>
        <div class="border border-gray-300 rounded-lg overflow-hidden">
          <div class="bg-gray-50 px-4 py-2 border-b border-gray-300 flex items-center justify-between">
            <span class="text-sm font-medium text-gray-700">
              {{ getEngineDisplayName(form.template_engine) }} Template
            </span>
            <div class="flex items-center space-x-2">
              <Button
                @click="formatContent"
                variant="ghost"
                size="sm"
                :disabled="!canFormat"
              >
                <Code class="w-4 h-4 mr-1" />
                Format
              </Button>
              <Button
                @click="validateContent"
                variant="ghost"
                size="sm"
              >
                <CheckCircle class="w-4 h-4 mr-1" />
                Validate
              </Button>
            </div>
          </div>
          <Textarea
            v-model="form.template_content"
            :placeholder="getContentPlaceholder()"
            class="min-h-96 font-mono text-sm"
            :error="errors.template_content"
          />
        </div>
        <p v-if="errors.template_content" class="mt-1 text-sm text-red-600">
          {{ errors.template_content }}
        </p>
      </div>

      <!-- Configuration -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Template Configuration (JSON)
        </label>
        <Textarea
          v-model="form.template_config"
          placeholder='{"variables": [], "styles": {}, "options": {}}'
          class="min-h-32 font-mono text-sm"
          :error="errors.template_config"
        />
        <p class="mt-1 text-sm text-gray-500">
          JSON configuration for template variables, styles, and options
        </p>
      </div>

      <!-- Settings -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="flex items-center">
          <input
            id="is_active"
            v-model="form.is_active"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="is_active" class="ml-2 block text-sm text-gray-900">
            Active
          </label>
        </div>

        <div class="flex items-center">
          <input
            id="is_default"
            v-model="form.is_default"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="is_default" class="ml-2 block text-sm text-gray-900">
            Default Template
          </label>
        </div>

        <div class="flex items-center">
          <input
            id="allow_preview"
            v-model="form.allow_preview"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="allow_preview" class="ml-2 block text-sm text-gray-900">
            Allow Preview
          </label>
        </div>
      </div>

      <!-- Tags -->
      <FormControl
        label="Tags"
        v-model="form.tags"
        type="text"
        placeholder="Comma-separated tags (e.g., audit, report, compliance)"
        :error="errors.tags"
      />

      <!-- Actions -->
      <div class="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200">
        <Button @click="$emit('cancel')" variant="outline">
          Cancel
        </Button>
        <Button
          type="submit"
          variant="solid"
          :loading="saving"
        >
          {{ isEditing ? 'Update Template' : 'Create Template' }}
        </Button>
      </div>
    </Form>
  </div>
</template>

<script setup>
import { CheckCircle, Code } from "lucide-vue-next"
import { computed, ref, watch } from "vue"

// Props
const props = defineProps({
	template: {
		type: Object,
		default: () => ({}),
	},
	isEditing: {
		type: Boolean,
		default: false,
	},
})

// Emits
const emit = defineEmits(["save", "cancel"])

// Reactive data
const form = ref({
	template_name: "",
	template_type: "Report",
	category: "",
	description: "",
	template_content: "",
	template_config: "{}",
	template_engine: "Jinja2",
	is_active: true,
	is_default: false,
	allow_preview: true,
	tags: "",
})

const errors = ref({})
const saving = ref(false)

// Options
const templateTypeOptions = [
	{ label: "Report", value: "Report" },
	{ label: "Component", value: "Component" },
	{ label: "Page", value: "Page" },
	{ label: "Email", value: "Email" },
	{ label: "Base", value: "Base" },
	{ label: "Utility", value: "Utility" },
]

const categoryOptions = [
	{ label: "Audit Report", value: "Audit Report" },
	{ label: "Compliance", value: "Compliance" },
	{ label: "Risk Assessment", value: "Risk Assessment" },
	{ label: "Dashboard", value: "Dashboard" },
	{ label: "Form", value: "Form" },
	{ label: "Email Notification", value: "Email Notification" },
	{ label: "Print Template", value: "Print Template" },
	{ label: "API Response", value: "API Response" },
]

const engineOptions = [
	{ label: "Jinja2", value: "Jinja2" },
	{ label: "Vue", value: "Vue" },
	{ label: "Handlebars", value: "Handlebars" },
	{ label: "Plain Text", value: "Plain Text" },
]

// Computed
const canFormat = computed(() => {
	return ["Jinja2", "Vue", "Handlebars"].includes(form.value.template_engine)
})

// Methods
const initializeForm = () => {
	if (props.isEditing && props.template) {
		form.value = {
			template_name: props.template.template_name || "",
			template_type: props.template.template_type || "Report",
			category: props.template.category || "",
			description: props.template.description || "",
			template_content: props.template.template_content || "",
			template_config: props.template.template_config || "{}",
			template_engine: props.template.template_engine || "Jinja2",
			is_active: props.template.is_active !== false,
			is_default: props.template.is_default || false,
			allow_preview: props.template.allow_preview !== false,
			tags: props.template.tags || "",
		}
	} else {
		form.value = {
			template_name: "",
			template_type: "Report",
			category: "",
			description: "",
			template_content: "",
			template_config: "{}",
			template_engine: "Jinja2",
			is_active: true,
			is_default: false,
			allow_preview: true,
			tags: "",
		}
	}
	errors.value = {}
}

const getEngineDisplayName = (engine) => {
	const names = {
		Jinja2: "Jinja2",
		Vue: "Vue.js",
		Handlebars: "Handlebars",
		"Plain Text": "Plain Text",
	}
	return names[engine] || engine
}

const getContentPlaceholder = () => {
	const placeholders = {
		Jinja2: "{{ variable_name }} or {% for item in items %}...{% endfor %}",
		Vue: "<template>...</template> or {{ variable }}",
		Handlebars: "{{variable}} or {{#each items}}...{{/each}}",
		"Plain Text": "Plain text content...",
	}
	return placeholders[form.value.template_engine] || "Enter template content..."
}

const validateForm = () => {
	errors.value = {}

	if (!form.value.template_name.trim()) {
		errors.value.template_name = "Template name is required"
	}

	if (!form.value.template_type) {
		errors.value.template_type = "Template type is required"
	}

	if (!form.value.template_content.trim()) {
		errors.value.template_content = "Template content is required"
	}

	if (!form.value.template_engine) {
		errors.value.template_engine = "Template engine is required"
	}

	// Validate JSON config
	try {
		JSON.parse(form.value.template_config)
	} catch (e) {
		errors.value.template_config = "Invalid JSON format"
	}

	return Object.keys(errors.value).length === 0
}

const formatContent = () => {
	// Basic formatting for different engines
	let content = form.value.template_content

	switch (form.value.template_engine) {
		case "Jinja2":
			// Basic Jinja2 formatting
			content = content.replace(/\{\{\s*/g, "{{ ").replace(/\s*\}\}/g, " }}")
			content = content.replace(/\{\%\s*/g, "{% ").replace(/\s*\%\}/g, " %}")
			break
		case "Vue":
			// Basic Vue formatting
			content = content.replace(/\{\{\s*/g, "{{ ").replace(/\s*\}\}/g, " }}")
			break
		case "Handlebars":
			// Basic Handlebars formatting
			content = content.replace(/\{\{\s*/g, "{{ ").replace(/\s*\}\}/g, " }}")
			break
	}

	form.value.template_content = content
}

const validateContent = async () => {
	try {
		// Basic syntax validation
		switch (form.value.template_engine) {
			case "Jinja2":
				// Check for basic Jinja2 syntax
				if (
					form.value.template_content.includes("{%") &&
					!form.value.template_content.includes("%}")
				) {
					throw new Error("Unclosed Jinja2 block")
				}
				if (
					form.value.template_content.includes("{{") &&
					!form.value.template_content.includes("}}")
				) {
					throw new Error("Unclosed Jinja2 variable")
				}
				break
			case "Vue":
				// Basic Vue validation
				if (
					form.value.template_content.includes("<template>") &&
					!form.value.template_content.includes("</template>")
				) {
					throw new Error("Unclosed template tag")
				}
				break
			case "Handlebars":
				// Basic Handlebars validation
				if (
					form.value.template_content.includes("{{#") &&
					!form.value.template_content.includes("{{/")
				) {
					throw new Error("Unclosed Handlebars block")
				}
				break
		}

		// Show success message
		alert("Template validation passed!")
	} catch (error) {
		alert(`Validation error: ${error.message}`)
	}
}

const handleSubmit = async () => {
	if (!validateForm()) {
		return
	}

	saving.value = true
	try {
		const templateData = {
			...form.value,
			name: props.isEditing ? props.template.name : undefined,
			template_id: props.isEditing
				? props.template.template_id
				: generateTemplateId(),
			tags: form.value.tags
				? form.value.tags
						.split(",")
						.map((tag) => tag.trim())
						.filter((tag) => tag)
				: [],
		}

		await emit("save", templateData)
	} catch (error) {
		console.error("Error saving template:", error)
	} finally {
		saving.value = false
	}
}

const generateTemplateId = () => {
	return `template_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// Watchers
watch(() => props.template, initializeForm, { immediate: true })
watch(() => props.isEditing, initializeForm)
</script>

<style scoped>
/* Custom styles for template editor */
</style>