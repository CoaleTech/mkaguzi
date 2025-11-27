<template>
  <div class="create-requirement-form">
    <form @submit.prevent="handleSubmit">
      <!-- Basic Information -->
      <div class="form-section">
        <h4>Basic Information</h4>
        
        <div class="form-grid">
          <FormControl
            type="text"
            v-model="formData.title"
            :invalid="errors.title"
            label="Requirement Title"
            required
          >
            <template #description>
              Enter a clear, descriptive title for the compliance requirement
            </template>
          </FormControl>
          
          <FormControl
            type="select"
            v-model="formData.framework_id"
            :options="frameworkOptions"
            :invalid="errors.framework_id"
            label="Compliance Framework"
            required
          />
        </div>
        
        <div class="form-grid">
          <FormControl
            type="text"
            v-model="formData.section"
            :invalid="errors.section"
            label="Section/Control ID"
            required
          >
            <template #description>
              e.g., SOX.302.4, GDPR.Art.32, ISO.A.12.6.1
            </template>
          </FormControl>
          
          <FormControl
            type="select"
            v-model="formData.category"
            :options="categoryOptions"
            :invalid="errors.category"
            label="Category"
            required
          />
        </div>
        
        <FormControl
          type="textarea"
          v-model="formData.description"
          :invalid="errors.description"
          label="Description"
          required
          :rows="4"
        >
          <template #description>
            Detailed description of the compliance requirement and what needs to be achieved
          </template>
        </FormControl>
      </div>

      <!-- Risk Assessment -->
      <div class="form-section">
        <h4>Risk Assessment</h4>
        
        <div class="form-grid">
          <FormControl
            type="select"
            v-model="formData.risk_level"
            :options="riskLevelOptions"
            :invalid="errors.risk_level"
            label="Risk Level"
            required
          />
          
          <FormControl
            type="select"
            v-model="formData.priority"
            :options="priorityOptions"
            :invalid="errors.priority"
            label="Priority"
            required
          />
        </div>
        
        <FormControl
          type="textarea"
          v-model="formData.risk_description"
          label="Risk Description"
          :rows="3"
        >
          <template #description>
            Describe the potential risks associated with non-compliance
          </template>
        </FormControl>
      </div>

      <!-- Control Requirements -->
      <div class="form-section">
        <h4>Control Requirements</h4>
        
        <div class="form-grid">
          <FormControl
            type="select"
            v-model="formData.control_type"
            :options="controlTypeOptions"
            :invalid="errors.control_type"
            label="Control Type"
            required
          />
          
          <FormControl
            type="select"
            v-model="formData.control_frequency"
            :options="frequencyOptions"
            :invalid="errors.control_frequency"
            label="Control Frequency"
            required
          />
        </div>
        
        <div class="control-activities">
          <label class="form-label">Control Activities</label>
          <p class="form-description">Add specific control activities that need to be performed</p>
          
          <div class="activities-list">
            <div
              v-for="(activity, index) in formData.control_activities"
              :key="index"
              class="activity-item"
            >
              <FormControl
                type="text"
                v-model="activity.description"
                placeholder="Control activity description"
                required
              />
              
              <FormControl
                type="select"
                v-model="activity.frequency"
                :options="activityFrequencyOptions"
                placeholder="Frequency"
                required
              />
              
              <Button
                variant="ghost"
                size="sm"
                @click="removeActivity(index)"
                :disabled="formData.control_activities.length === 1"
              >
                <Trash2 class="w-4 h-4" />
              </Button>
            </div>
          </div>
          
          <Button
            type="button"
            variant="outline"
            size="sm"
            @click="addActivity"
          >
            <Plus class="w-4 h-4 mr-2" />
            Add Activity
          </Button>
        </div>
      </div>

      <!-- Assignment & Timeline -->
      <div class="form-section">
        <h4>Assignment & Timeline</h4>
        
        <div class="form-grid">
          <FormControl
            type="text"
            v-model="formData.assigned_to"
            :invalid="errors.assigned_to"
            label="Assigned To"
            required
          >
            <template #description>
              Person responsible for ensuring compliance
            </template>
          </FormControl>
          
          <FormControl
            type="text"
            v-model="formData.reviewer"
            :invalid="errors.reviewer"
            label="Reviewer"
          >
            <template #description>
              Person responsible for reviewing compliance
            </template>
          </FormControl>
        </div>
        
        <div class="form-grid">
          <FormControl
            type="date"
            v-model="formData.effective_date"
            :invalid="errors.effective_date"
            label="Effective Date"
            required
          />
          
          <FormControl
            type="date"
            v-model="formData.next_review_date"
            :invalid="errors.next_review_date"
            label="Next Review Date"
            required
          />
        </div>
        
        <FormControl
          type="select"
          v-model="formData.review_frequency"
          :options="reviewFrequencyOptions"
          :invalid="errors.review_frequency"
          label="Review Frequency"
          required
        />
      </div>

      <!-- Evidence Requirements -->
      <div class="form-section">
        <h4>Evidence Requirements</h4>
        
        <div class="evidence-types">
          <label class="form-label">Required Evidence Types</label>
          <p class="form-description">Select the types of evidence required to demonstrate compliance</p>
          
          <div class="checkbox-grid">
            <div
              v-for="evidenceType in evidenceTypeOptions"
              :key="evidenceType.value"
              class="checkbox-item"
            >
              <FormControl
                type="checkbox"
                :model-value="formData.evidence_requirements.includes(evidenceType.value)"
                @update:modelValue="toggleEvidenceType(evidenceType.value, $event)"
                :label="evidenceType.label"
              />
            </div>
          </div>
        </div>
        
        <FormControl
          type="textarea"
          v-model="formData.evidence_description"
          label="Evidence Description"
          :rows="3"
        >
          <template #description>
            Describe specific evidence requirements and acceptance criteria
          </template>
        </FormControl>
      </div>

      <!-- Testing & Validation -->
      <div class="form-section">
        <h4>Testing & Validation</h4>
        
        <div class="form-grid">
          <FormControl
            type="select"
            v-model="formData.testing_approach"
            :options="testingApproachOptions"
            :invalid="errors.testing_approach"
            label="Testing Approach"
            required
          />
          
          <FormControl
            type="number"
            v-model="formData.sample_size"
            label="Sample Size"
            min="1"
          >
            <template #description>
              Number of samples required for testing (if applicable)
            </template>
          </FormControl>
        </div>
        
        <FormControl
          type="textarea"
          v-model="formData.testing_procedures"
          label="Testing Procedures"
          :rows="4"
        >
          <template #description>
            Detailed testing procedures and validation steps
          </template>
        </FormControl>
      </div>

      <!-- Remediation -->
      <div class="form-section">
        <h4>Remediation Planning</h4>
        
        <FormControl
          type="textarea"
          v-model="formData.remediation_guidelines"
          label="Remediation Guidelines"
          :rows="3"
        >
          <template #description>
            Guidelines for addressing non-compliance issues
          </template>
        </FormControl>
        
        <div class="form-grid">
          <FormControl
            type="number"
            v-model="formData.remediation_timeline"
            label="Remediation Timeline (days)"
            min="1"
          >
            <template #description>
              Standard timeframe for addressing non-compliance
            </template>
          </FormControl>
          
          <FormControl
            type="text"
            v-model="formData.escalation_contact"
            label="Escalation Contact"
          >
            <template #description>
              Person to contact for escalation of issues
            </template>
          </FormControl>
        </div>
      </div>

      <!-- Additional Settings -->
      <div class="form-section">
        <h4>Additional Settings</h4>
        
        <div class="form-checkboxes">
          <FormControl
            type="checkbox"
            v-model="formData.automated_monitoring"
            label="Enable Automated Monitoring"
          >
            <template #description>
              Automatically monitor compliance status where possible
            </template>
          </FormControl>
          
          <FormControl
            type="checkbox"
            v-model="formData.continuous_monitoring"
            label="Continuous Monitoring"
          >
            <template #description>
              Monitor compliance on an ongoing basis
            </template>
          </FormControl>
          
          <FormControl
            type="checkbox"
            v-model="formData.exception_reporting"
            label="Exception Reporting"
          >
            <template #description>
              Generate reports for compliance exceptions
            </template>
          </FormControl>
        </div>
        
        <FormControl
          type="textarea"
          v-model="formData.notes"
          label="Additional Notes"
          :rows="3"
        >
          <template #description>
            Any additional information or special considerations
          </template>
        </FormControl>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <Button
          type="button"
          variant="outline"
          @click="$emit('cancel')"
        >
          Cancel
        </Button>
        
        <Button
          type="button"
          variant="ghost"
          @click="saveAsDraft"
          :loading="saving"
        >
          Save as Draft
        </Button>
        
        <Button
          type="submit"
          variant="solid"
          :loading="saving"
          :disabled="!isFormValid"
        >
          Create Requirement
        </Button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { Button, FormControl } from "frappe-ui"
import { Plus, Trash2 } from "lucide-vue-next"
import { computed, ref, watch } from "vue"

const props = defineProps({
	frameworks: {
		type: Array,
		default: () => [],
	},
})

const emit = defineEmits(["create", "cancel"])

// Form state
const formData = ref({
	title: "",
	framework_id: "",
	section: "",
	category: "",
	description: "",
	risk_level: "",
	priority: "Medium",
	risk_description: "",
	control_type: "",
	control_frequency: "",
	control_activities: [{ description: "", frequency: "Monthly" }],
	assigned_to: "",
	reviewer: "",
	effective_date: "",
	next_review_date: "",
	review_frequency: "Quarterly",
	evidence_requirements: [],
	evidence_description: "",
	testing_approach: "",
	sample_size: null,
	testing_procedures: "",
	remediation_guidelines: "",
	remediation_timeline: 30,
	escalation_contact: "",
	automated_monitoring: false,
	continuous_monitoring: false,
	exception_reporting: true,
	notes: "",
})

const errors = ref({})
const saving = ref(false)

// Options
const frameworkOptions = computed(() =>
	props.frameworks.map((framework) => ({
		label: framework.name,
		value: framework.id,
	})),
)

const categoryOptions = [
	{ label: "Access Control", value: "access_control" },
	{ label: "Data Protection", value: "data_protection" },
	{ label: "Financial Reporting", value: "financial_reporting" },
	{ label: "IT Security", value: "it_security" },
	{ label: "Operational Control", value: "operational_control" },
	{ label: "Risk Management", value: "risk_management" },
	{ label: "Governance", value: "governance" },
	{ label: "Audit Trail", value: "audit_trail" },
	{ label: "Change Management", value: "change_management" },
	{ label: "Business Continuity", value: "business_continuity" },
]

const riskLevelOptions = [
	{ label: "Critical", value: "Critical" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

const priorityOptions = [
	{ label: "Urgent", value: "Urgent" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

const controlTypeOptions = [
	{ label: "Preventive", value: "preventive" },
	{ label: "Detective", value: "detective" },
	{ label: "Corrective", value: "corrective" },
	{ label: "Compensating", value: "compensating" },
]

const frequencyOptions = [
	{ label: "Continuous", value: "continuous" },
	{ label: "Daily", value: "daily" },
	{ label: "Weekly", value: "weekly" },
	{ label: "Monthly", value: "monthly" },
	{ label: "Quarterly", value: "quarterly" },
	{ label: "Semi-Annually", value: "semi_annually" },
	{ label: "Annually", value: "annually" },
]

const activityFrequencyOptions = [
	{ label: "Daily", value: "daily" },
	{ label: "Weekly", value: "weekly" },
	{ label: "Monthly", value: "monthly" },
	{ label: "Quarterly", value: "quarterly" },
	{ label: "Annually", value: "annually" },
]

const reviewFrequencyOptions = [
	{ label: "Monthly", value: "monthly" },
	{ label: "Quarterly", value: "quarterly" },
	{ label: "Semi-Annually", value: "semi_annually" },
	{ label: "Annually", value: "annually" },
]

const evidenceTypeOptions = [
	{ label: "Documentation", value: "documentation" },
	{ label: "Screenshots", value: "screenshots" },
	{ label: "System Reports", value: "system_reports" },
	{ label: "Audit Logs", value: "audit_logs" },
	{ label: "Policies & Procedures", value: "policies_procedures" },
	{ label: "Training Records", value: "training_records" },
	{ label: "Certifications", value: "certifications" },
	{ label: "Test Results", value: "test_results" },
	{ label: "Meeting Minutes", value: "meeting_minutes" },
	{ label: "External Confirmations", value: "external_confirmations" },
]

const testingApproachOptions = [
	{ label: "Manual Testing", value: "manual" },
	{ label: "Automated Testing", value: "automated" },
	{ label: "Sample-Based", value: "sample_based" },
	{ label: "Full Population", value: "full_population" },
	{ label: "Risk-Based", value: "risk_based" },
	{ label: "Walkthrough", value: "walkthrough" },
]

// Computed
const isFormValid = computed(() => {
	const required = [
		"title",
		"framework_id",
		"section",
		"category",
		"description",
		"risk_level",
		"control_type",
		"control_frequency",
		"assigned_to",
		"effective_date",
		"next_review_date",
		"review_frequency",
		"testing_approach",
	]
	return (
		required.every((field) => formData.value[field]) &&
		formData.value.control_activities.every(
			(activity) => activity.description && activity.frequency,
		)
	)
})

// Methods
const validateForm = () => {
	const newErrors = {}

	if (!formData.value.title?.trim()) {
		newErrors.title = "Title is required"
	}

	if (!formData.value.framework_id) {
		newErrors.framework_id = "Framework is required"
	}

	if (!formData.value.section?.trim()) {
		newErrors.section = "Section/Control ID is required"
	}

	if (!formData.value.category) {
		newErrors.category = "Category is required"
	}

	if (!formData.value.description?.trim()) {
		newErrors.description = "Description is required"
	}

	if (!formData.value.risk_level) {
		newErrors.risk_level = "Risk level is required"
	}

	if (!formData.value.control_type) {
		newErrors.control_type = "Control type is required"
	}

	if (!formData.value.control_frequency) {
		newErrors.control_frequency = "Control frequency is required"
	}

	if (!formData.value.assigned_to?.trim()) {
		newErrors.assigned_to = "Assigned to is required"
	}

	if (!formData.value.effective_date) {
		newErrors.effective_date = "Effective date is required"
	}

	if (!formData.value.next_review_date) {
		newErrors.next_review_date = "Next review date is required"
	} else if (
		new Date(formData.value.next_review_date) <=
		new Date(formData.value.effective_date)
	) {
		newErrors.next_review_date = "Next review date must be after effective date"
	}

	if (!formData.value.review_frequency) {
		newErrors.review_frequency = "Review frequency is required"
	}

	if (!formData.value.testing_approach) {
		newErrors.testing_approach = "Testing approach is required"
	}

	// Validate control activities
	if (
		formData.value.control_activities.some(
			(activity) => !activity.description?.trim() || !activity.frequency,
		)
	) {
		newErrors.control_activities =
			"All control activities must have description and frequency"
	}

	errors.value = newErrors
	return Object.keys(newErrors).length === 0
}

const addActivity = () => {
	formData.value.control_activities.push({
		description: "",
		frequency: "Monthly",
	})
}

const removeActivity = (index) => {
	if (formData.value.control_activities.length > 1) {
		formData.value.control_activities.splice(index, 1)
	}
}

const toggleEvidenceType = (type, checked) => {
	if (checked) {
		if (!formData.value.evidence_requirements.includes(type)) {
			formData.value.evidence_requirements.push(type)
		}
	} else {
		const index = formData.value.evidence_requirements.indexOf(type)
		if (index > -1) {
			formData.value.evidence_requirements.splice(index, 1)
		}
	}
}

const handleSubmit = async () => {
	if (!validateForm()) {
		return
	}

	saving.value = true

	try {
		const requirementData = {
			...formData.value,
			compliance_status: "Not Assessed",
			created: new Date().toISOString(),
			modified: new Date().toISOString(),
			status: "Active",
		}

		emit("create", requirementData)
	} finally {
		saving.value = false
	}
}

const saveAsDraft = async () => {
	saving.value = true

	try {
		const requirementData = {
			...formData.value,
			compliance_status: "Not Assessed",
			status: "Draft",
			created: new Date().toISOString(),
			modified: new Date().toISOString(),
		}

		emit("create", requirementData)
	} finally {
		saving.value = false
	}
}

// Auto-calculate next review date based on frequency
watch(
	[() => formData.value.effective_date, () => formData.value.review_frequency],
	([effectiveDate, frequency]) => {
		if (effectiveDate && frequency) {
			const date = new Date(effectiveDate)

			switch (frequency) {
				case "monthly":
					date.setMonth(date.getMonth() + 1)
					break
				case "quarterly":
					date.setMonth(date.getMonth() + 3)
					break
				case "semi_annually":
					date.setMonth(date.getMonth() + 6)
					break
				case "annually":
					date.setFullYear(date.getFullYear() + 1)
					break
			}

			formData.value.next_review_date = date.toISOString().split("T")[0]
		}
	},
)
</script>

<style scoped>
.create-requirement-form {
  max-width: 800px;
  margin: 0 auto;
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border-color);
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1.5rem 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-grid:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.form-description {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0 0 1rem 0;
}

/* Control Activities */
.control-activities {
  margin-bottom: 1.5rem;
}

.activities-list {
  margin-bottom: 1rem;
}

.activity-item {
  display: grid;
  grid-template-columns: 1fr 200px auto;
  gap: 1rem;
  align-items: end;
  margin-bottom: 1rem;
}

/* Evidence Types */
.evidence-types {
  margin-bottom: 1.5rem;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.checkbox-item {
  display: flex;
  align-items: center;
}

/* Form Checkboxes */
.form-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

/* Responsive */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .activity-item {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .checkbox-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
}

@media (max-width: 480px) {
  .create-requirement-form {
    padding: 0;
  }
  
  .form-section {
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
  }
  
  .form-actions {
    gap: 0.75rem;
  }
}
</style>