<template>
  <div class="risk-filters">
    <div class="filters-header">
      <h4>Filter Risks</h4>
      <div class="filter-actions">
        <Button
          variant="ghost"
          size="sm"
          @click="clearAllFilters"
          :disabled="!hasActiveFilters"
        >
          <XIcon class="h-4 w-4 mr-1" />
          Clear All
        </Button>
        <Button
          variant="outline"
          size="sm"
          @click="showAdvancedFilters = !showAdvancedFilters"
        >
          <FilterIcon class="h-4 w-4 mr-1" />
          {{ showAdvancedFilters ? 'Hide' : 'Show' }} Advanced
        </Button>
      </div>
    </div>

    <!-- Quick Filters -->
    <div class="quick-filters">
      <div class="filter-group">
        <label>Risk Level</label>
        <div class="filter-buttons">
          <Button
            v-for="level in riskLevels"
            :key="level.value"
            :variant="filters.riskLevel === level.value ? 'solid' : 'outline'"
            size="sm"
            @click="toggleFilter('riskLevel', level.value)"
            :style="{ '--button-color': level.color }"
          >
            {{ level.label }}
          </Button>
        </div>
      </div>

      <div class="filter-group">
        <label>Category</label>
        <div class="filter-buttons">
          <Button
            v-for="category in categories"
            :key="category.id"
            :variant="filters.category === category.id ? 'solid' : 'outline'"
            size="sm"
            @click="toggleFilter('category', category.id)"
          >
            <component :is="getCategoryIcon(category.icon)" class="h-4 w-4 mr-1" />
            {{ category.label }}
          </Button>
        </div>
      </div>

      <div class="filter-group">
        <label>Status</label>
        <div class="filter-buttons">
          <Button
            v-for="status in riskStatuses"
            :key="status.value"
            :variant="filters.status === status.value ? 'solid' : 'outline'"
            size="sm"
            @click="toggleFilter('status', status.value)"
          >
            <component :is="status.icon" class="h-4 w-4 mr-1" />
            {{ status.label }}
          </Button>
        </div>
      </div>
    </div>

    <!-- Advanced Filters -->
    <div v-if="showAdvancedFilters" class="advanced-filters">
      <div class="filter-row">
        <div class="filter-field">
          <FormControl
            type="select"
            label="Risk Owner"
            v-model="filters.owner"
            :options="ownerOptions"
            placeholder="Select owner..."
          />
        </div>
        <div class="filter-field">
          <FormControl
            type="select"
            label="Likelihood"
            v-model="filters.likelihood"
            :options="likelihoodOptions"
            placeholder="Select likelihood..."
          />
        </div>
        <div class="filter-field">
          <FormControl
            type="select"
            label="Impact"
            v-model="filters.impact"
            :options="impactOptions"
            placeholder="Select impact..."
          />
        </div>
      </div>

      <div class="filter-row">
        <div class="filter-field">
          <label>Date Range</label>
          <div class="date-range">
            <FormControl
              type="date"
              v-model="filters.dateFrom"
              placeholder="From date"
            />
            <FormControl
              type="date"
              v-model="filters.dateTo"
              placeholder="To date"
            />
          </div>
        </div>
        <div class="filter-field">
          <FormControl
            type="text"
            label="Search Keywords"
            v-model="filters.search"
            placeholder="Search in title, description..."
          >
            <template #prefix>
              <SearchIcon class="h-4 w-4" />
            </template>
          </FormControl>
        </div>
      </div>
    </div>

    <!-- Active Filters Display -->
    <div v-if="activeFilters.length > 0" class="active-filters">
      <div class="active-filters-label">Active Filters:</div>
      <div class="filter-chips">
        <div
          v-for="filter in activeFilters"
          :key="filter.key"
          class="filter-chip"
        >
          <span>{{ filter.label }}: {{ filter.value }}</span>
          <button @click="removeFilter(filter.key)">
            <XIcon class="h-3 w-3" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, FormControl } from "frappe-ui"
import {
	AlertCircleIcon,
	AlertTriangleIcon,
	CheckCircleIcon,
	ClockIcon,
	DollarSignIcon,
	FilterIcon,
	MonitorIcon,
	SearchIcon,
	SettingsIcon,
	ShieldIcon,
	TargetIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, ref, watch } from "vue"

const props = defineProps({
	filters: {
		type: Object,
		default: () => ({}),
	},
	categories: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["update:filters", "apply-filters", "clear-filters"])

// Local state
const showAdvancedFilters = ref(false)

// Filter options
const riskLevels = [
	{ label: "Critical", value: "Critical", color: "#ef4444" },
	{ label: "High", value: "High", color: "#f97316" },
	{ label: "Medium", value: "Medium", color: "#eab308" },
	{ label: "Low", value: "Low", color: "#22c55e" },
]

const riskStatuses = [
	{ label: "Open", value: "Open", icon: AlertCircleIcon },
	{ label: "In Progress", value: "In Progress", icon: ClockIcon },
	{ label: "Under Review", value: "Under Review", icon: SearchIcon },
	{ label: "Closed", value: "Closed", icon: CheckCircleIcon },
]

const ownerOptions = [
	{ label: "John Doe", value: "john.doe@company.com" },
	{ label: "Jane Smith", value: "jane.smith@company.com" },
	{ label: "Mike Johnson", value: "mike.johnson@company.com" },
]

const likelihoodOptions = [
	{ label: "1 - Rare", value: 1 },
	{ label: "2 - Unlikely", value: 2 },
	{ label: "3 - Possible", value: 3 },
	{ label: "4 - Likely", value: 4 },
	{ label: "5 - Almost Certain", value: 5 },
]

const impactOptions = [
	{ label: "1 - Insignificant", value: 1 },
	{ label: "2 - Minor", value: 2 },
	{ label: "3 - Moderate", value: 3 },
	{ label: "4 - Major", value: 4 },
	{ label: "5 - Catastrophic", value: 5 },
]

// Category icons mapping
const categoryIcons = {
	Settings: SettingsIcon,
	DollarSign: DollarSignIcon,
	Shield: ShieldIcon,
	Target: TargetIcon,
	AlertTriangle: AlertTriangleIcon,
	Monitor: MonitorIcon,
}

// Computed
const hasActiveFilters = computed(() => {
	return Object.values(props.filters).some(
		(value) => value !== null && value !== undefined && value !== "",
	)
})

const activeFilters = computed(() => {
	const filters = []

	if (props.filters.riskLevel) {
		filters.push({
			key: "riskLevel",
			label: "Risk Level",
			value: props.filters.riskLevel,
		})
	}

	if (props.filters.category) {
		const category = props.categories.find(
			(c) => c.id === props.filters.category,
		)
		filters.push({
			key: "category",
			label: "Category",
			value: category?.label || props.filters.category,
		})
	}

	if (props.filters.status) {
		filters.push({
			key: "status",
			label: "Status",
			value: props.filters.status,
		})
	}

	if (props.filters.owner) {
		const owner = ownerOptions.find((o) => o.value === props.filters.owner)
		filters.push({
			key: "owner",
			label: "Owner",
			value: owner?.label || props.filters.owner,
		})
	}

	if (props.filters.search) {
		filters.push({
			key: "search",
			label: "Search",
			value: props.filters.search,
		})
	}

	return filters
})

// Methods
const getCategoryIcon = (iconName) => {
	return categoryIcons[iconName] || AlertTriangleIcon
}

const toggleFilter = (key, value) => {
	const newFilters = { ...props.filters }

	if (newFilters[key] === value) {
		newFilters[key] = null
	} else {
		newFilters[key] = value
	}

	emit("update:filters", newFilters)
	emit("apply-filters", newFilters)
}

const removeFilter = (key) => {
	const newFilters = { ...props.filters }
	newFilters[key] = null

	emit("update:filters", newFilters)
	emit("apply-filters", newFilters)
}

const clearAllFilters = () => {
	const clearedFilters = {
		riskLevel: null,
		category: null,
		status: null,
		owner: null,
		likelihood: null,
		impact: null,
		dateFrom: null,
		dateTo: null,
		search: null,
	}

	emit("update:filters", clearedFilters)
	emit("clear-filters")
}

// Watch for filter changes
watch(
	() => props.filters,
	(newFilters) => {
		emit("apply-filters", newFilters)
	},
	{ deep: true },
)
</script>

<style scoped>
.risk-filters {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
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

.filter-actions {
  display: flex;
  gap: 0.5rem;
}

.quick-filters {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.advanced-filters {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 0.375rem;
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-field label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
}

.date-range {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.active-filters {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.active-filters-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
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
  padding: 0.25rem 0.5rem;
  background: var(--primary-light);
  border: 1px solid var(--primary-color);
  border-radius: 1rem;
  font-size: 0.75rem;
  color: var(--primary-color);
}

.filter-chip button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1rem;
  height: 1rem;
  background: transparent;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  color: var(--primary-color);
  transition: all 0.2s;
}

.filter-chip button:hover {
  background: var(--primary-color);
  color: white;
}

@media (max-width: 768px) {
  .filters-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .filter-row {
    grid-template-columns: 1fr;
  }
  
  .date-range {
    grid-template-columns: 1fr;
  }
}
</style>