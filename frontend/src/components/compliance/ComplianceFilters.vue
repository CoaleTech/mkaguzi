<template>
  <div class="compliance-filters">
    <div class="filters-grid">
      <FormControl
        label="Regulatory Body"
        v-model="filters.regulatory_body"
        type="select"
        :options="regulatoryBodyOptions"
        placeholder="All Bodies"
      />
      <FormControl
        label="Category"
        v-model="filters.compliance_category"
        type="select"
        :options="categoryOptions"
        placeholder="All Categories"
      />
      <FormControl
        label="Status"
        v-model="filters.is_active"
        type="select"
        :options="statusOptions"
        placeholder="All Status"
      />
      <div class="filter-actions">
        <Button @click="clearFilters" variant="outline">Clear Filters</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, FormControl } from "frappe-ui"

const props = defineProps({
  filters: {
    type: Object,
    required: true,
    default: () => ({
      regulatory_body: "",
      compliance_category: "",
      is_active: "",
    })
  }
})

const emit = defineEmits(['clear-filters'])

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

const statusOptions = [
  { label: "All", value: "" },
  { label: "Active", value: "true" },
  { label: "Inactive", value: "false" },
]

// Methods
const clearFilters = () => {
  emit('clear-filters')
}
</script>

<style scoped>
.compliance-filters {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  gap: 1rem;
  align-items: end;
}

.filter-actions {
  display: flex;
  align-items: flex-end;
}

/* Responsive design */
@media (max-width: 1024px) {
  .filters-grid {
    grid-template-columns: 1fr 1fr;
  }

  .filter-actions {
    grid-column: span 2;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .filters-grid {
    grid-template-columns: 1fr;
  }

  .filter-actions {
    grid-column: span 1;
  }

  .compliance-filters {
    padding: 1rem;
  }
}
</style>