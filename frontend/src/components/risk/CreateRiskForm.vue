<template>
  <div class="create-risk-form">
    <form @submit.prevent="handleSubmit">
      <!-- Basic Information -->
      <div class="form-section">
        <h4>Basic Information</h4>
        <div class="form-grid">
          <div class="form-field">
            <FormControl
              type="text"
              label="Risk Title"
              v-model="formData.title"
              placeholder="Enter risk title..."
              :error="errors.title"
              required
            />
          </div>
          
          <div class="form-field">
            <FormControl
              type="select"
              label="Category"
              v-model="formData.category"
              :options="categoryOptions"
              placeholder="Select category..."
              :error="errors.category"
              required
            />
          </div>
        </div>
        
        <div class="form-field">
          <FormControl
            type="textarea"
            label="Risk Description"
            v-model="formData.description"
            placeholder="Describe the risk in detail..."
            :error="errors.description"
            rows="4"
            required
          />
        </div>
      </div>

      <!-- Risk Assessment -->
      <div class="form-section">
        <h4>Risk Assessment</h4>
        <div class="assessment-grid">
          <!-- Likelihood -->
          <div class="assessment-field">
            <label>Likelihood</label>
            <p class="field-description">Probability that the risk will occur</p>
            <div class="likelihood-options">
              <div
                v-for="level in likelihoodLevels"
                :key="level.id"
                class="assessment-option"
                :class="{ active: formData.likelihood === level.id }"
                @click="formData.likelihood = level.id"
              >
                <div class="option-number">{{ level.id }}</div>
                <div class="option-content">
                  <div class="option-label">{{ level.label }}</div>
                  <div class="option-description">{{ level.description }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Impact -->
          <div class="assessment-field">
            <label>Impact</label>
            <p class="field-description">Severity of consequences if the risk occurs</p>
            <div class="impact-options">
              <div
                v-for="level in impactLevels"
                :key="level.id"
                class="assessment-option"
                :class="{ active: formData.impact === level.id }"
                @click="formData.impact = level.id"
              >
                <div class="option-number">{{ level.id }}</div>
                <div class="option-content">
                  <div class="option-label">{{ level.label }}</div>
                  <div class="option-description">{{ level.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Risk Level Indicator -->
        <div v-if="formData.likelihood && formData.impact" class="risk-level-indicator">
          <div class="indicator-header">
            <h5>Calculated Risk Level</h5>
            <div class="risk-score">Score: {{ formData.likelihood * formData.impact }}</div>
          </div>
          <div class="indicator-content">
            <div
              class="level-badge"
              :style="{ backgroundColor: calculatedRiskLevel.color }"
            >
              {{ calculatedRiskLevel.level }}
            </div>
            <p>{{ getRiskLevelDescription(calculatedRiskLevel.level) }}</p>
          </div>
        </div>
      </div>

      <!-- Additional Details -->
      <div class="form-section">
        <h4>Additional Details</h4>
        <div class="form-grid">
          <div class="form-field">
            <FormControl
              type="select"
              label="Risk Owner"
              v-model="formData.risk_owner"
              :options="ownerOptions"
              placeholder="Assign risk owner..."
            />
          </div>
          
          <div class="form-field">
            <FormControl
              type="select"
              label="Status"
              v-model="formData.status"
              :options="statusOptions"
              placeholder="Select status..."
            />
          </div>
        </div>
        
        <div class="form-grid">
          <div class="form-field">
            <FormControl
              type="date"
              label="Review Date"
              v-model="formData.review_date"
              placeholder="Select review date..."
            />
          </div>
          
          <div class="form-field">
            <FormControl
              type="select"
              label="Priority"
              v-model="formData.priority"
              :options="priorityOptions"
              placeholder="Select priority..."
            />
          </div>
        </div>
      </div>

      <!-- Risk Context -->
      <div class="form-section">
        <h4>Risk Context</h4>
        <div class="form-field">
          <FormControl
            type="textarea"
            label="Root Cause"
            v-model="formData.root_cause"
            placeholder="Identify the root cause of this risk..."
            rows="3"
          />
        </div>
        
        <div class="form-field">
          <FormControl
            type="textarea"
            label="Potential Consequences"
            v-model="formData.consequences"
            placeholder="Describe potential consequences if this risk materializes..."
            rows="3"
          />
        </div>
        
        <div class="form-field">
          <FormControl
            type="textarea"
            label="Existing Controls"
            v-model="formData.existing_controls"
            placeholder="List any existing controls or mitigation measures..."
            rows="3"
          />
        </div>
      </div>

      <!-- Tags and References -->
      <div class="form-section">
        <h4>Tags & References</h4>
        <div class="form-grid">
          <div class="form-field">
            <FormControl
              type="text"
              label="Tags"
              v-model="formData.tags"
              placeholder="Enter tags separated by commas..."
            />
          </div>
          
          <div class="form-field">
            <FormControl
              type="text"
              label="Reference ID"
              v-model="formData.reference_id"
              placeholder="External reference or ID..."
            />
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <Button
          type="button"
          variant="outline"
          @click="$emit('cancel')"
          :disabled="isSubmitting"
        >
          Cancel
        </Button>
        
        <div class="action-buttons">
          <Button
            type="button"
            variant="outline"
            @click="saveAsDraft"
            :loading="isSubmitting && submitType === 'draft'"
          >
            Save as Draft
          </Button>
          
          <Button
            type="submit"
            variant="solid"
            :loading="isSubmitting && submitType === 'submit'"
          >
            Create Risk
          </Button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { Button, FormControl } from "frappe-ui"
import { computed, onMounted, ref } from "vue"

const props = defineProps({
	categories: {
		type: Array,
		default: () => [],
	},
	likelihoodLevels: {
		type: Array,
		default: () => [],
	},
	impactLevels: {
		type: Array,
		default: () => [],
	},
	initialData: {
		type: Object,
		default: () => ({}),
	},
})

const emit = defineEmits(["submit", "cancel", "save-draft"])

// Form data
const formData = ref({
	title: "",
	description: "",
	category: "",
	likelihood: null,
	impact: null,
	risk_owner: "",
	status: "Open",
	review_date: "",
	priority: "Medium",
	root_cause: "",
	consequences: "",
	existing_controls: "",
	tags: "",
	reference_id: "",
	...props.initialData,
})

// Form state
const isSubmitting = ref(false)
const submitType = ref("")
const errors = ref({})

// Options
const categoryOptions = computed(() => {
	return props.categories.map((cat) => ({
		label: cat.label,
		value: cat.id,
	}))
})

const ownerOptions = [
	{ label: "John Doe", value: "john.doe@company.com" },
	{ label: "Jane Smith", value: "jane.smith@company.com" },
	{ label: "Mike Johnson", value: "mike.johnson@company.com" },
	{ label: "Sarah Wilson", value: "sarah.wilson@company.com" },
]

const statusOptions = [
	{ label: "Open", value: "Open" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Under Review", value: "Under Review" },
	{ label: "Closed", value: "Closed" },
]

const priorityOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Medium", value: "Medium" },
	{ label: "High", value: "High" },
	{ label: "Critical", value: "Critical" },
]

// Computed
const calculatedRiskLevel = computed(() => {
	if (!formData.value.likelihood || !formData.value.impact) {
		return { level: "Unknown", color: "#6b7280" }
	}

	const score = formData.value.likelihood * formData.value.impact
	if (score <= 5) return { level: "Low", color: "#22c55e" }
	if (score <= 12) return { level: "Medium", color: "#eab308" }
	if (score <= 20) return { level: "High", color: "#f97316" }
	return { level: "Critical", color: "#ef4444" }
})

// Methods
const getRiskLevelDescription = (level) => {
	const descriptions = {
		Low: "Low priority risk that requires monitoring but minimal immediate action.",
		Medium:
			"Moderate risk that requires attention and planned mitigation measures.",
		High: "High priority risk that requires immediate attention and active management.",
		Critical:
			"Critical risk that requires immediate action and executive attention.",
	}
	return descriptions[level] || ""
}

const validateForm = () => {
	const newErrors = {}

	if (!formData.value.title?.trim()) {
		newErrors.title = "Risk title is required"
	}

	if (!formData.value.category) {
		newErrors.category = "Category is required"
	}

	if (!formData.value.description?.trim()) {
		newErrors.description = "Risk description is required"
	}

	if (!formData.value.likelihood) {
		newErrors.likelihood = "Likelihood assessment is required"
	}

	if (!formData.value.impact) {
		newErrors.impact = "Impact assessment is required"
	}

	errors.value = newErrors
	return Object.keys(newErrors).length === 0
}

const handleSubmit = async () => {
	if (!validateForm()) return

	isSubmitting.value = true
	submitType.value = "submit"

	try {
		await emit("submit", {
			...formData.value,
			risk_level: calculatedRiskLevel.value.level,
			risk_score: formData.value.likelihood * formData.value.impact,
		})
	} catch (error) {
		console.error("Error creating risk:", error)
	} finally {
		isSubmitting.value = false
		submitType.value = ""
	}
}

const saveAsDraft = async () => {
	isSubmitting.value = true
	submitType.value = "draft"

	try {
		await emit("save-draft", {
			...formData.value,
			status: "Draft",
			risk_level: calculatedRiskLevel.value.level,
			risk_score: formData.value.likelihood * formData.value.impact,
		})
	} catch (error) {
		console.error("Error saving draft:", error)
	} finally {
		isSubmitting.value = false
		submitType.value = ""
	}
}

// Lifecycle
onMounted(() => {
	// Set default values if provided in initial data
	if (props.initialData.likelihood && props.initialData.impact) {
		formData.value.likelihood = props.initialData.likelihood
		formData.value.impact = props.initialData.impact
	}
})
</script>

<style scoped>
.create-risk-form {
  max-width: 800px;
  margin: 0 auto;
}

.form-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
}

.form-section h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.assessment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.assessment-field label {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.field-description {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0 0 1rem 0;
}

.likelihood-options,
.impact-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.assessment-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.assessment-option:hover {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.assessment-option.active {
  border-color: var(--primary-color);
  background: var(--primary-light);
  box-shadow: 0 0 0 1px var(--primary-color);
}

.option-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  font-weight: 700;
  flex-shrink: 0;
}

.assessment-option.active .option-number {
  background: var(--primary-color);
}

.option-content {
  flex: 1;
}

.option-label {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.option-description {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.risk-level-indicator {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: var(--background-color);
  border-radius: 0.375rem;
  border: 1px solid var(--border-color);
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.indicator-header h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.risk-score {
  font-weight: 600;
  color: var(--primary-color);
}

.indicator-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.level-badge {
  padding: 0.5rem 1rem;
  color: white;
  border-radius: 0.375rem;
  font-weight: 600;
  font-size: 0.875rem;
}

.indicator-content p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: var(--background-color);
  border-top: 1px solid var(--border-color);
  margin-top: 2rem;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

@media (max-width: 768px) {
  .form-grid,
  .assessment-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .action-buttons {
    justify-content: stretch;
  }
  
  .indicator-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .indicator-content {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>