<template>
  <div class="compliance-requirement-form">
    <div class="form-sections">
      <!-- Basic Information -->
      <div class="form-section">
        <h3 class="section-title">Basic Information</h3>
        <div class="form-grid">
          <FormControl
            label="Requirement ID"
            v-model="formData.requirement_id"
            type="text"
            required
          />
          <FormControl
            label="Requirement Name"
            v-model="formData.requirement_name"
            type="text"
            required
          />
          <FormControl
            label="Regulatory Body"
            v-model="formData.regulatory_body"
            type="select"
            :options="regulatoryBodyOptions"
            required
          />
          <FormControl
            label="Category"
            v-model="formData.compliance_category"
            type="select"
            :options="categoryOptions"
            required
          />
        </div>
      </div>

      <!-- Details & Responsibility -->
      <div class="form-section">
        <h3 class="section-title">Details & Responsibility</h3>
        <div class="form-grid">
          <FormControl
            label="Description"
            v-model="formData.description"
            type="textarea"
            rows="3"
            required
          />
          <FormControl
            label="Frequency"
            v-model="formData.frequency"
            type="select"
            :options="frequencyOptions"
            required
          />
          <FormControl
            label="Responsible Person"
            v-model="formData.responsible_person"
            type="link"
            doctype="User"
          />
          <FormControl
            label="Responsible Department"
            v-model="formData.responsible_department"
            type="link"
            doctype="Department"
          />
        </div>
        <div class="form-row">
          <FormControl
            label="Is Active"
            v-model="formData.is_active"
            type="checkbox"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FormControl } from "frappe-ui"

const props = defineProps({
	formData: {
		type: Object,
		required: true,
		default: () => ({
			requirement_id: "",
			requirement_name: "",
			regulatory_body: "",
			compliance_category: "",
			description: "",
			frequency: "",
			responsible_person: "",
			responsible_department: "",
			is_active: true,
		}),
	},
})

// Options
const regulatoryBodyOptions = [
	{ label: "KRA", value: "KRA" },
	{ label: "NSSF", value: "NSSF" },
	{ label: "NHIF", value: "NHIF" },
	{ label: "NEMA", value: "NEMA" },
	{ label: "County Government", value: "County Government" },
	{ label: "KEBS", value: "KEBS" },
	{ label: "Central Bank of Kenya", value: "Central Bank of Kenya" },
	{ label: "CMA", value: "CMA" },
	{ label: "IRA", value: "IRA" },
	{ label: "Other", value: "Other" },
]

const categoryOptions = [
	{ label: "Tax", value: "Tax" },
	{ label: "Social Security", value: "Social Security" },
	{ label: "Environmental", value: "Environmental" },
	{ label: "Licensing", value: "Licensing" },
	{ label: "Health & Safety", value: "Health & Safety" },
	{ label: "Industry-Specific", value: "Industry-Specific" },
	{ label: "Employment", value: "Employment" },
	{ label: "Data Protection", value: "Data Protection" },
]

const frequencyOptions = [
	{ label: "Daily", value: "Daily" },
	{ label: "Weekly", value: "Weekly" },
	{ label: "Monthly", value: "Monthly" },
	{ label: "Quarterly", value: "Quarterly" },
	{ label: "Semi-Annual", value: "Semi-Annual" },
	{ label: "Annual", value: "Annual" },
	{ label: "One-time", value: "One-time" },
	{ label: "Event-Based", value: "Event-Based" },
]
</script>

<style scoped>
.compliance-requirement-form {
  padding: 1rem 0;
}

.form-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  border: 1px solid var(--border-color-2);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color-2);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-row {
  margin-top: 1rem;
}

.form-grid .form-control,
.form-row .form-control {
  margin-bottom: 0;
}

/* Responsive design */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-section {
    padding: 1rem;
  }
}
</style>