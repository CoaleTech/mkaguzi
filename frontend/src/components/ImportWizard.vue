<template>
  <div class="import-wizard">
    <!-- Header -->
    <div class="wizard-header">
      <div class="title-section">
        <h2 class="wizard-title">Data Import Wizard</h2>
        <p class="wizard-description">Import your audit data with field mapping and validation</p>
      </div>
      
      <!-- Progress Indicator -->
      <div class="progress-indicator">
        <div 
          v-for="(step, index) in steps" 
          :key="step.id"
          class="progress-step"
          :class="{
            'active': currentStep === index + 1,
            'completed': currentStep > index + 1,
            'disabled': currentStep < index + 1
          }"
        >
          <div class="step-circle">
            <CheckIcon v-if="currentStep > index + 1" class="h-4 w-4" />
            <span v-else>{{ index + 1 }}</span>
          </div>
          <span class="step-label">{{ step.label }}</span>
        </div>
      </div>
    </div>

    <!-- Step Content -->
    <div class="wizard-content">
      <!-- Step 1: File Upload & Template Selection -->
      <div v-if="currentStep === 1" class="step-content">
        <ImportFileUpload
          :templates="availableTemplates"
          :loading="loading.create"
          @file-uploaded="handleFileUploaded"
          @template-selected="handleTemplateSelected"
          @template-downloaded="handleTemplateDownloaded"
        />
      </div>

      <!-- Step 2: Field Mapping -->
      <div v-if="currentStep === 2" class="step-content">
        <FieldMappingStep
          v-if="activeImport && filePreview"
          :import-data="activeImport"
          :file-preview="filePreview"
          :available-fields="availableFields"
          :field-mappings="fieldMappings"
          @mappings-updated="handleMappingsUpdated"
        />
      </div>

      <!-- Step 3: Data Validation -->
      <div v-if="currentStep === 3" class="step-content">
        <DataValidationStep
          v-if="activeImport && validationResults"
          :import-data="activeImport"
          :validation-results="validationResults"
          :loading="loading.validate"
          @validation-fixed="handleValidationFixed"
          @re-validate="handleReValidate"
        />
      </div>

      <!-- Step 4: Import Preview & Execution -->
      <div v-if="currentStep === 4" class="step-content">
        <ImportPreviewStep
          v-if="activeImport"
          :import-data="activeImport"
          :processing="loading.process"
          :import-progress="importProgress"
          @start-import="handleStartImport"
          @cancel-import="handleCancelImport"
        />
      </div>

      <!-- Step 5: Completion & Results -->
      <div v-if="currentStep === 5" class="step-content">
        <ImportResultsStep
          v-if="activeImport"
          :import-data="activeImport"
          :import-results="importResults"
          @start-new-import="handleStartNewImport"
          @view-imported-data="handleViewImportedData"
        />
      </div>
    </div>

    <!-- Navigation -->
    <div class="wizard-navigation">
      <div class="nav-buttons">
        <Button
          v-if="currentStep > 1 && currentStep < 5"
          variant="outline"
          @click="previousStep"
          :disabled="loading.create || loading.process"
        >
          <ChevronLeftIcon class="h-4 w-4 mr-1" />
          Previous
        </Button>
        
        <div class="spacer"></div>
        
        <Button
          v-if="currentStep < 4"
          @click="nextStep"
          :disabled="!canProceedToNext || loading.create || loading.validate"
        >
          Next
          <ChevronRightIcon class="h-4 w-4 ml-1" />
        </Button>
        
        <Button
          v-if="currentStep === 4"
          variant="solid"
          @click="handleStartImport"
          :disabled="!canStartImport || loading.process"
        >
          <PlayIcon class="h-4 w-4 mr-1" />
          Start Import
        </Button>
      </div>
      
      <!-- Step Info -->
      <div class="step-info">
        <span class="step-counter">Step {{ currentStep }} of {{ steps.length }}</span>
        <span class="step-title">{{ steps[currentStep - 1]?.label }}</span>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-display">
      <div class="error-content">
        <AlertTriangleIcon class="h-5 w-5 text-red-500" />
        <div class="error-text">
          <h4>Import Error</h4>
          <p>{{ error }}</p>
        </div>
        <Button variant="ghost" size="sm" @click="clearError">
          <XIcon class="h-4 w-4" />
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import {
	AlertTriangleIcon,
	CheckIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	PlayIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"
import { useImportStore } from "../stores/useImportStore"
import DataValidationStep from "./import/DataValidationStep.vue"
import FieldMappingStep from "./import/FieldMappingStep.vue"
import ImportFileUpload from "./import/ImportFileUpload.vue"
import ImportPreviewStep from "./import/ImportPreviewStep.vue"
import ImportResultsStep from "./import/ImportResultsStep.vue"

const importStore = useImportStore()

// State
const currentStep = ref(1)
const selectedTemplate = ref(null)
const filePreview = ref(null)
const fieldMappings = ref({})
const validationResults = ref(null)
const importProgress = ref(null)
const importResults = ref(null)

// Steps configuration
const steps = [
	{ id: "upload", label: "File Upload" },
	{ id: "mapping", label: "Field Mapping" },
	{ id: "validation", label: "Data Validation" },
	{ id: "import", label: "Import Data" },
	{ id: "results", label: "Results" },
]

// Computed
const { activeImport, loading, error, availableTemplates } = importStore

const availableFields = computed(() => {
	if (!selectedTemplate.value) return []
	return [
		...selectedTemplate.value.required_fields,
		...selectedTemplate.value.optional_fields,
	]
})

const canProceedToNext = computed(() => {
	switch (currentStep.value) {
		case 1:
			return activeImport.value && filePreview.value
		case 2:
			return Object.keys(fieldMappings.value).length > 0
		case 3:
			return validationResults.value && validationResults.value.is_valid
		default:
			return true
	}
})

const canStartImport = computed(() => {
	return (
		activeImport.value &&
		validationResults.value &&
		validationResults.value.is_valid
	)
})

// Methods
const nextStep = () => {
	if (canProceedToNext.value && currentStep.value < steps.length) {
		currentStep.value++

		// Auto-trigger actions for certain steps
		if (
			currentStep.value === 3 &&
			Object.keys(fieldMappings.value).length > 0
		) {
			handleReValidate()
		}
	}
}

const previousStep = () => {
	if (currentStep.value > 1) {
		currentStep.value--
	}
}

const handleFileUploaded = async (uploadData) => {
	try {
		filePreview.value = uploadData.preview

		// Auto-advance to field mapping if we have a template
		if (selectedTemplate.value) {
			currentStep.value = 2
		}
	} catch (err) {
		console.error("File upload error:", err)
	}
}

const handleTemplateSelected = (template) => {
	selectedTemplate.value = template
}

const handleTemplateDownloaded = (templateId) => {
	// Template download handled by store
	console.log("Template downloaded:", templateId)
}

const handleMappingsUpdated = (mappings) => {
	fieldMappings.value = mappings
}

const handleReValidate = async () => {
	if (!activeImport.value || !Object.keys(fieldMappings.value).length) return

	try {
		const results = await importStore.validateImportData(
			activeImport.value.name,
			fieldMappings.value,
		)
		validationResults.value = results
	} catch (err) {
		console.error("Validation error:", err)
	}
}

const handleValidationFixed = (fixedData) => {
	// Handle validation fixes
	validationResults.value = {
		...validationResults.value,
		...fixedData,
	}
}

const handleStartImport = async () => {
	if (!activeImport.value) return

	try {
		importProgress.value = { progress: 0, status: "Starting..." }

		const results = await importStore.processImport(activeImport.value.name, {
			field_mappings: fieldMappings.value,
		})

		importResults.value = results
		currentStep.value = 5
	} catch (err) {
		console.error("Import processing error:", err)
	}
}

const handleCancelImport = async () => {
	if (!activeImport.value) return

	try {
		await importStore.cancelImport(activeImport.value.name)
		handleStartNewImport()
	} catch (err) {
		console.error("Cancel import error:", err)
	}
}

const handleStartNewImport = () => {
	// Reset wizard state
	currentStep.value = 1
	selectedTemplate.value = null
	filePreview.value = null
	fieldMappings.value = {}
	validationResults.value = null
	importProgress.value = null
	importResults.value = null
	importStore.activeImport = null
}

const handleViewImportedData = () => {
	// Navigate to imported data view
	if (importResults.value?.doctype) {
		// This would typically navigate to a list view
		console.log("View imported data:", importResults.value.doctype)
	}
}

const clearError = () => {
	importStore.error = null
}

// Watch for import progress updates
watch(
	() => activeImport.value?.progress,
	(newProgress) => {
		if (newProgress) {
			importProgress.value = newProgress
		}
	},
	{ deep: true },
)

// Initialize store on mount
onMounted(async () => {
	await importStore.initialize()
})
</script>

<style scoped>
.import-wizard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.wizard-header {
  margin-bottom: 2rem;
}

.title-section {
  margin-bottom: 1.5rem;
}

.wizard-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.wizard-description {
  color: var(--text-muted);
  margin: 0;
}

.progress-indicator {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: center;
  padding: 1.5rem 0;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  background: var(--background-color);
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.progress-step.active,
.progress-step.completed {
  opacity: 1;
}

.step-circle {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.2s;
}

.progress-step.active .step-circle {
  border-color: var(--primary-color);
  background: var(--primary-color);
  color: white;
}

.progress-step.completed .step-circle {
  border-color: var(--success-color);
  background: var(--success-color);
  color: white;
}

.step-label {
  font-size: 0.875rem;
  font-weight: 500;
  text-align: center;
}

.wizard-content {
  min-height: 500px;
  margin-bottom: 2rem;
}

.step-content {
  padding: 1rem 0;
}

.wizard-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.nav-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.spacer {
  flex: 1;
}

.step-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.step-counter {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.step-title {
  font-weight: 500;
  color: var(--text-color);
}

.error-display {
  margin-top: 1rem;
  padding: 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
}

.error-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.error-text h4 {
  font-weight: 600;
  color: #dc2626;
  margin: 0 0 0.25rem 0;
}

.error-text p {
  color: #7f1d1d;
  margin: 0;
}

@media (max-width: 768px) {
  .import-wizard {
    padding: 1rem;
  }
  
  .progress-indicator {
    gap: 0.5rem;
  }
  
  .progress-step {
    gap: 0.25rem;
  }
  
  .step-circle {
    width: 2rem;
    height: 2rem;
  }
  
  .step-label {
    font-size: 0.75rem;
  }
  
  .wizard-navigation {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .step-info {
    align-items: center;
  }
}
</style>