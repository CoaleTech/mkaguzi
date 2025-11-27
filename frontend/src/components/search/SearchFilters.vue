<template>
  <div class="search-filters">
    <div class="filters-header">
      <h4>Filters</h4>
      <Button
        v-if="Object.keys(activeFilters).length > 0"
        variant="ghost"
        size="sm"
        @click="$emit('filters-cleared')"
      >
        <XIcon class="h-4 w-4 mr-1" />
        Clear All
      </Button>
    </div>

    <!-- Active Filters Display -->
    <div v-if="Object.keys(activeFilters).length > 0" class="active-filters">
      <div class="filter-chips">
        <div
          v-for="(values, field) in activeFilters"
          :key="field"
        >
          <div
            v-for="(filterValue, index) in values"
            :key="index"
            class="filter-chip"
          >
            <span class="filter-field">{{ getFilterLabel(field) }}:</span>
            <span class="filter-value">{{ formatFilterValue(filterValue) }}</span>
            <button
              @click="$emit('filter-removed', field, index)"
              class="remove-filter"
            >
              <XIcon class="h-3 w-3" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Builder -->
    <div class="filter-builder">
      <div class="filter-row">
        <Select
          v-model="newFilter.field"
          :options="filterFieldOptions"
          placeholder="Select field..."
          class="filter-field-select"
        />
        
        <Select
          v-if="newFilter.field"
          v-model="newFilter.operator"
          :options="getOperatorOptions(newFilter.field)"
          placeholder="Operator"
          class="filter-operator-select"
        />
        
        <Input
          v-if="newFilter.field && newFilter.operator"
          v-model="newFilter.value"
          placeholder="Value..."
          class="filter-value-input"
        />
        
        <Button
          v-if="canAddFilter"
          @click="addFilter"
          size="sm"
        >
          <PlusIcon class="h-4 w-4" />
        </Button>
      </div>
    </div>

    <!-- Quick Filters -->
    <div class="quick-filters">
      <h5>Quick Filters</h5>
      <div class="quick-filter-grid">
        <button
          v-for="quickFilter in quickFilters"
          :key="quickFilter.id"
          @click="applyQuickFilter(quickFilter)"
          class="quick-filter-btn"
          :class="{ active: isQuickFilterActive(quickFilter) }"
        >
          <component :is="quickFilter.icon" class="h-4 w-4" />
          <span>{{ quickFilter.label }}</span>
        </button>
      </div>
    </div>

    <!-- Date Range Filters -->
    <div class="date-filters">
      <h5>Date Range</h5>
      <div class="date-range-options">
        <button
          v-for="range in dateRanges"
          :key="range.value"
          @click="applyDateRange(range)"
          class="date-range-btn"
          :class="{ active: activeDateRange === range.value }"
        >
          {{ range.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Input, Select } from "frappe-ui"
import {
	AlertTriangleIcon,
	CheckCircleIcon,
	ClockIcon,
	PlusIcon,
	UserIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, ref } from "vue"

const props = defineProps({
	availableFilters: {
		type: Array,
		default: () => [],
	},
	activeFilters: {
		type: Object,
		default: () => ({}),
	},
})

const emit = defineEmits(["filter-added", "filter-removed", "filters-cleared"])

// State
const newFilter = ref({
	field: "",
	operator: "",
	value: "",
})
const activeDateRange = ref("")

// Quick Filters
const quickFilters = ref([
	{
		id: "high_severity",
		label: "High Severity",
		icon: AlertTriangleIcon,
		filter: { field: "severity", operator: "equals", value: "High" },
	},
	{
		id: "open_status",
		label: "Open Items",
		icon: ClockIcon,
		filter: { field: "status", operator: "equals", value: "Open" },
	},
	{
		id: "completed",
		label: "Completed",
		icon: CheckCircleIcon,
		filter: { field: "status", operator: "equals", value: "Completed" },
	},
])

// Date Ranges
const dateRanges = ref([
	{ label: "Today", value: "today" },
	{ label: "This Week", value: "week" },
	{ label: "This Month", value: "month" },
	{ label: "This Quarter", value: "quarter" },
])

// Computed
const filterFieldOptions = computed(() => [
	{ label: "Select field...", value: "" },
	...props.availableFilters.map((filter) => ({
		label: filter.label,
		value: filter.field,
	})),
])

const canAddFilter = computed(
	() =>
		newFilter.value.field && newFilter.value.operator && newFilter.value.value,
)

// Methods
const getOperatorOptions = (field) => {
	return [
		{ label: "Equals", value: "equals" },
		{ label: "Contains", value: "contains" },
		{ label: "Not Equals", value: "not_equals" },
	]
}

const getFilterLabel = (fieldName) => {
	const config = props.availableFilters.find((f) => f.field === fieldName)
	return config?.label || fieldName
}

const formatFilterValue = (filterValue) => {
	if (typeof filterValue === "object" && filterValue.value) {
		return filterValue.value
	}
	return filterValue
}

const addFilter = () => {
	if (!canAddFilter.value) return

	emit("filter-added", {
		field: newFilter.value.field,
		operator: newFilter.value.operator,
		value: newFilter.value.value,
	})

	// Reset form
	newFilter.value = {
		field: "",
		operator: "",
		value: "",
	}
}

const applyQuickFilter = (quickFilter) => {
	emit("filter-added", quickFilter.filter)
}

const isQuickFilterActive = (quickFilter) => {
	const { field, value } = quickFilter.filter
	const activeValues = props.activeFilters[field]
	if (!activeValues) return false

	return activeValues.some(
		(filterValue) =>
			(typeof filterValue === "object" ? filterValue.value : filterValue) ===
			value,
	)
}

const applyDateRange = (range) => {
	activeDateRange.value = range.value
	emit("filter-added", {
		field: "creation",
		operator: "between",
		value: range.value,
	})
}
</script>

<style scoped>
.search-filters {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters-header h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filter-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--primary-light);
  border: 1px solid var(--primary-color);
  border-radius: 0.75rem;
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

.filter-field {
  font-weight: 500;
  color: var(--primary-color);
}

.filter-value {
  color: var(--text-color);
}

.remove-filter {
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
}

.filter-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.filter-field-select,
.filter-operator-select {
  min-width: 150px;
}

.filter-value-input {
  flex: 1;
  min-width: 200px;
}

.quick-filters h5,
.date-filters h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.75rem 0;
}

.quick-filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.5rem;
}

.quick-filter-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-filter-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.quick-filter-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.date-range-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.date-range-btn {
  padding: 0.375rem 0.75rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.date-range-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.date-range-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}
</style>