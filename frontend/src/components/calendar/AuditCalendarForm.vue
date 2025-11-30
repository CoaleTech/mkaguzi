<template>
  <div class="space-y-6">
    <!-- Basic Information -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <FormControl
        v-model="form.calendar_id"
        label="Calendar ID"
        placeholder="Enter calendar ID"
        :required="true"
      />
      <Select
        v-model="form.audit_universe"
        :options="universeOptions"
        label="Audit Universe"
        placeholder="Select universe"
        :required="true"
      />
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Select
        v-model="form.audit_type"
        :options="auditTypeOptions"
        label="Audit Type"
        placeholder="Select type"
        :required="true"
      />
      <Select
        v-model="form.status"
        :options="statusOptions"
        label="Status"
        placeholder="Select status"
      />
      <Select
        v-model="form.annual_audit_plan"
        :options="planOptions"
        label="Annual Audit Plan"
        placeholder="Select plan"
      />
    </div>

    <!-- Dates and Resources -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <FormControl
        v-model="form.planned_start_date"
        type="date"
        label="Planned Start Date"
        :required="true"
      />
      <FormControl
        v-model="form.planned_end_date"
        type="date"
        label="Planned End Date"
        :required="true"
      />
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <FormControl
        v-model="form.lead_auditor"
        label="Lead Auditor"
        placeholder="Select lead auditor"
        :required="true"
      />
      <FormControl
        v-model="form.estimated_days"
        type="number"
        label="Estimated Days"
        placeholder="0"
      />
      <FormControl
        v-model="form.progress_percentage"
        type="number"
        label="Progress %"
        placeholder="0"
        min="0"
        max="100"
      />
    </div>

    <!-- Objectives and Scope -->
    <div class="space-y-4">
      <FormControl
        v-model="form.objectives"
        type="textarea"
        label="Objectives"
        placeholder="Enter audit objectives"
        rows="3"
      />
      <FormControl
        v-model="form.scope"
        type="textarea"
        label="Scope"
        placeholder="Define audit scope"
        rows="3"
      />
      <FormControl
        v-model="form.key_risks"
        type="textarea"
        label="Key Risks"
        placeholder="Identify key risks"
        rows="3"
      />
    </div>
  </div>
</template>

<script setup>
import { FormControl, Select } from "frappe-ui"

// Props
defineProps({
	form: {
		type: Object,
		required: true,
	},
	universeOptions: {
		type: Array,
		required: true,
	},
	auditTypeOptions: {
		type: Array,
		required: true,
	},
	statusOptions: {
		type: Array,
		required: true,
	},
	planOptions: {
		type: Array,
		required: true,
	},
})
</script>