<template>
  <div class="board-report-form">
    <div class="form-sections">
      <!-- Basic Information -->
      <div class="form-section">
        <h3 class="section-title">Basic Information</h3>
        <div class="form-grid">
          <FormControl
            label="Report Title"
            v-model="formData.title"
            type="text"
            placeholder="e.g., Q4 2025 Board Report"
            required
          />
          <FormControl
            label="Reporting Period"
            v-model="formData.period"
            type="select"
            :options="periodOptions"
            required
          />
          <FormControl
            label="Report Type"
            v-model="formData.type"
            type="select"
            :options="reportTypeOptions"
            required
          />
          <FormControl
            label="Presentation Date"
            v-model="formData.presentationDate"
            type="date"
          />
        </div>
      </div>

      <!-- Content & Focus -->
      <div class="form-section">
        <h3 class="section-title">Content & Focus</h3>
        <div class="form-grid">
          <FormControl
            label="Key Focus Areas"
            v-model="formData.focusAreas"
            type="textarea"
            placeholder="Enter key areas to focus on in this report"
            rows="3"
          />
          <FormControl
            label="Additional Notes"
            v-model="formData.notes"
            type="textarea"
            placeholder="Any additional context or notes"
            rows="3"
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
      title: "",
      period: "",
      type: "Comprehensive",
      presentationDate: "",
      focusAreas: "",
      notes: "",
    })
  }
})

// Options
const periodOptions = [
  { label: "Q1 2025", value: "Q1 2025" },
  { label: "Q2 2025", value: "Q2 2025" },
  { label: "Q3 2025", value: "Q3 2025" },
  { label: "Q4 2025", value: "Q4 2025" },
  { label: "Annual 2025", value: "Annual 2025" },
  { label: "Q1 2026", value: "Q1 2026" },
]

const reportTypeOptions = [
  { label: "Comprehensive", value: "Comprehensive" },
  { label: "Financial Focus", value: "Financial Focus" },
  { label: "Risk & Compliance", value: "Risk & Compliance" },
  { label: "Operational Review", value: "Operational Review" },
]
</script>

<style scoped>
.board-report-form {
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

.form-grid .form-control {
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