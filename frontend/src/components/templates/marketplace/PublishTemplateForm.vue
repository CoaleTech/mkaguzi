<template>
  <div class="publish-template-form">
    <Form @submit="handleSubmit" class="space-y-6">
      <!-- Step 1: Select Template -->
      <div v-if="currentStep === 1">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Select Template to Publish</h3>

        <FormControl
          label="Local Template"
          v-model="form.template_name"
          type="select"
          :options="localTemplateOptions"
          required
          placeholder="Choose a template from your registry"
          :error="errors.template_name"
        />

        <div v-if="selectedTemplate" class="mt-4 p-4 bg-gray-50 rounded-lg">
          <h4 class="font-medium text-gray-900">{{ selectedTemplate.template_name }}</h4>
          <p class="text-sm text-gray-600">{{ selectedTemplate.template_type }} • {{ selectedTemplate.category }}</p>
          <p class="text-sm text-gray-500 mt-1">{{ selectedTemplate.description }}</p>
        </div>
      </div>

      <!-- Step 2: Marketplace Details -->
      <div v-if="currentStep === 2">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Marketplace Details</h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormControl
            label="Display Name"
            v-model="form.marketplace_name"
            type="text"
            required
            placeholder="Name shown in marketplace"
            :error="errors.marketplace_name"
          />

          <FormControl
            label="Version"
            v-model="form.version"
            type="text"
            required
            placeholder="e.g., 1.0.0"
            :error="errors.version"
          />
        </div>

        <FormControl
          label="Description"
          v-model="form.description"
          type="textarea"
          required
          placeholder="Detailed description of your template"
          :error="errors.description"
        />

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormControl
            label="Tags"
            v-model="form.tags"
            type="text"
            placeholder="Comma-separated tags"
            :error="errors.tags"
          />

          <FormControl
            label="Category"
            v-model="form.category"
            type="select"
            :options="categoryOptions"
            :error="errors.category"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormControl
            label="License Type"
            v-model="form.license_type"
            type="select"
            :options="licenseOptions"
            :error="errors.license_type"
          />

          <FormControl
            label="Price (USD)"
            v-model="form.price"
            type="number"
            min="0"
            step="0.01"
            placeholder="0 for free"
            :error="errors.price"
          />
        </div>

        <FormControl
          label="Compatibility"
          v-model="form.compatibility"
          type="text"
          placeholder="e.g., ERPNext v14+, Mkaguzi v1.0+"
          :error="errors.compatibility"
        />

        <FormControl
          label="Required Modules"
          v-model="form.required_modules"
          type="text"
          placeholder="Comma-separated module names"
          :error="errors.required_modules"
        />
      </div>

      <!-- Step 3: Preview and Publish -->
      <div v-if="currentStep === 3">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Preview and Publish</h3>

        <div class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="font-medium text-gray-900 mb-3">Template Preview</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p class="text-sm text-gray-600"><strong>Name:</strong> {{ form.marketplace_name }}</p>
              <p class="text-sm text-gray-600"><strong>Type:</strong> {{ selectedTemplate?.template_type }}</p>
              <p class="text-sm text-gray-600"><strong>Version:</strong> {{ form.version }}</p>
              <p class="text-sm text-gray-600"><strong>License:</strong> {{ form.license_type }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600"><strong>Price:</strong> ${{ form.price || 0 }}</p>
              <p class="text-sm text-gray-600"><strong>Category:</strong> {{ form.category }}</p>
              <p class="text-sm text-gray-600"><strong>Tags:</strong> {{ form.tags }}</p>
            </div>
          </div>
          <div class="mt-4">
            <p class="text-sm text-gray-600"><strong>Description:</strong></p>
            <p class="text-sm text-gray-700 mt-1">{{ form.description }}</p>
          </div>
        </div>

        <div class="space-y-4">
          <div class="flex items-center">
            <input
              id="is_public"
              v-model="form.is_public"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="is_public" class="ml-2 block text-sm text-gray-900">
              Make this template public in the marketplace
            </label>
          </div>

          <div class="flex items-center">
            <input
              id="publish_now"
              v-model="form.publish_now"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="publish_now" class="ml-2 block text-sm text-gray-900">
              Publish immediately (or save as draft)
            </label>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="flex items-center justify-between pt-6 border-t border-gray-200">
        <Button
          @click="previousStep"
          :disabled="currentStep === 1"
          variant="outline"
        >
          Previous
        </Button>

        <div class="flex items-center space-x-2">
          <div class="flex space-x-1">
            <div
              v-for="step in 3"
              :key="step"
              :class="[
                'w-2 h-2 rounded-full',
                step <= currentStep ? 'bg-blue-600' : 'bg-gray-300'
              ]"
            ></div>
          </div>
          <span class="text-sm text-gray-500 ml-2">Step {{ currentStep }} of 3</span>
        </div>

        <Button
          v-if="currentStep < 3"
          @click="nextStep"
          variant="solid"
        >
          Next
        </Button>

        <Button
          v-else
          type="submit"
          variant="solid"
          :loading="publishing"
        >
          {{ form.publish_now ? 'Publish Template' : 'Save as Draft' }}
        </Button>
      </div>
    </Form>
  </div>
</template>

<script setup>
import { call } from "frappe-ui"
import { computed, onMounted, ref, watch } from "vue"

// Props
const props = defineProps({})

// Emits
const emit = defineEmits(["published", "cancel"])

// Reactive data
const currentStep = ref(1)
const publishing = ref(false)
const localTemplates = ref([])
const selectedTemplate = ref(null)

const form = ref({
	template_name: "",
	marketplace_name: "",
	version: "1.0.0",
	description: "",
	tags: "",
	category: "",
	license_type: "MIT",
	price: 0,
	compatibility: "ERPNext v14+, Mkaguzi v1.0+",
	required_modules: "",
	is_public: true,
	publish_now: false,
})

const errors = ref({})

// Options
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

const licenseOptions = [
	{ label: "MIT", value: "MIT" },
	{ label: "GPL", value: "GPL" },
	{ label: "BSD", value: "BSD" },
	{ label: "Apache", value: "Apache" },
	{ label: "Proprietary", value: "Proprietary" },
	{ label: "Free", value: "Free" },
]

// Computed
const localTemplateOptions = computed(() => {
	return localTemplates.value.map((template) => ({
		label: `${template.template_name} (${template.template_type})`,
		value: template.name,
	}))
})

// Methods
const loadLocalTemplates = async () => {
	try {
		const response = await call(
			"mkaguzi.mkaguzi.core.doctype.template_registry.template_registry.get_templates_by_category",
		)
		localTemplates.value = response || []
	} catch (error) {
		console.error("Error loading local templates:", error)
		localTemplates.value = []
	}
}

const validateStep = (step) => {
	errors.value = {}

	if (step === 1) {
		if (!form.value.template_name) {
			errors.value.template_name = "Please select a template"
			return false
		}
	} else if (step === 2) {
		if (!form.value.marketplace_name.trim()) {
			errors.value.marketplace_name = "Display name is required"
		}
		if (!form.value.version.trim()) {
			errors.value.version = "Version is required"
		}
		if (!form.value.description.trim()) {
			errors.value.description = "Description is required"
		}
	}

	return Object.keys(errors.value).length === 0
}

const nextStep = () => {
	if (validateStep(currentStep.value)) {
		if (currentStep.value === 1) {
			// Load selected template details
			selectedTemplate.value = localTemplates.value.find(
				(t) => t.name === form.value.template_name,
			)
			// Pre-fill marketplace name if not set
			if (!form.value.marketplace_name) {
				form.value.marketplace_name =
					selectedTemplate.value?.template_name || ""
			}
			if (!form.value.description) {
				form.value.description = selectedTemplate.value?.description || ""
			}
			if (!form.value.category) {
				form.value.category = selectedTemplate.value?.category || ""
			}
		}
		currentStep.value++
	}
}

const previousStep = () => {
	if (currentStep.value > 1) {
		currentStep.value--
	}
}

const handleSubmit = async () => {
	if (!validateStep(currentStep.value)) {
		return
	}

	publishing.value = true
	try {
		const marketplaceData = {
			template_name: form.value.marketplace_name,
			version: form.value.version,
			author: frappe.session?.user || "Anonymous",
			description: form.value.description,
			tags: form.value.tags,
			category: form.value.category,
			license_type: form.value.license_type,
			price: form.value.price,
			compatibility: form.value.compatibility,
			required_modules: form.value.required_modules,
			is_public: form.value.is_public,
			is_featured: false, // Featured status requires admin approval
			publish_now: form.value.publish_now,
		}

		await call(
			"mkaguzi.mkaguzi.core.doctype.template_marketplace.template_marketplace.publish_to_marketplace",
			{
				template_name: form.value.template_name,
				marketplace_data: marketplaceData,
			},
		)

		emit("published")
	} catch (error) {
		console.error("Error publishing template:", error)
		alert(`Failed to publish template: ${error.message}`)
	} finally {
		publishing.value = false
	}
}

// Watchers
watch(
	() => form.value.template_name,
	(newValue) => {
		if (newValue) {
			selectedTemplate.value = localTemplates.value.find(
				(t) => t.name === newValue,
			)
		} else {
			selectedTemplate.value = null
		}
	},
)

// Lifecycle
onMounted(() => {
	loadLocalTemplates()
})
</script>

<style scoped>
/* Custom styles for publish form */
</style>