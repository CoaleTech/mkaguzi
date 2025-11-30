<template>
  <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <!-- Left Section: Title and Search/Filters -->
      <div class="flex flex-wrap items-center gap-4">
        <h3 class="text-sm font-semibold text-gray-900">Quick Actions</h3>

        <!-- Search and Filter Controls -->
        <div class="flex items-center space-x-2">
          <div class="relative">
            <SearchIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              :value="searchQuery"
              @input="$emit('update:searchQuery', $event.target.value)"
              type="text"
              placeholder="Search assessments..."
              class="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent text-sm w-48"
            />
          </div>

          <Select
            :modelValue="filterStatus"
            @update:modelValue="$emit('update:filterStatus', $event)"
            :options="statusOptionsWithAll"
            class="min-w-36"
          />

          <Select
            :modelValue="filterPeriod"
            @update:modelValue="$emit('update:filterPeriod', $event)"
            :options="periodOptionsWithAll"
            class="min-w-36"
          />

          <Select
            :modelValue="filterYear"
            @update:modelValue="$emit('update:filterYear', $event)"
            :options="yearOptionsWithAll"
            class="min-w-28"
          />
        </div>
      </div>

      <!-- Center Section: Action Buttons -->
      <div class="flex items-center space-x-2">
        <div class="p-1">
          <Button
            variant="solid"
            theme="gray"
            size="sm"
            @click="$emit('bulk-action')"
            :disabled="selectedCount === 0"
          >
            <template #prefix>
              <LayersIcon class="h-3.5 w-3.5" />
            </template>
            Bulk Actions ({{ selectedCount }})
          </Button>
        </div>
        <div class="p-1">
          <Button
            variant="solid"
            theme="gray"
            size="sm"
            @click="$emit('show-analytics')"
          >
            <template #prefix>
              <BarChart3Icon class="h-3.5 w-3.5" />
            </template>
            Risk Analytics
          </Button>
        </div>
        <div class="p-1">
          <Button
            variant="solid"
            theme="gray"
            size="sm"
            @click="$emit('toggle-view')"
          >
            <template #prefix>
              <component :is="viewMode === 'table' ? LayoutGridIcon : TableIcon" class="h-3.5 w-3.5" />
            </template>
            {{ viewMode === 'table' ? 'Card View' : 'Table View' }}
          </Button>
        </div>
      </div>

      <!-- Right Section: Results Count -->
      <div class="flex items-center space-x-2 text-sm text-gray-600">
        <span>Showing {{ filteredCount }} of {{ totalCount }} assessments</span>
        <Button
          v-if="hasActiveFilters"
          variant="ghost"
          size="sm"
          @click="$emit('clear-filters')"
        >
          <XIcon class="h-3.5 w-3.5 mr-1" />
          Clear
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Select } from "frappe-ui"
import {
	BarChart3Icon,
	LayersIcon,
	LayoutGridIcon,
	SearchIcon,
	TableIcon,
	XIcon,
} from "lucide-vue-next"
import { computed } from "vue"

const props = defineProps({
	searchQuery: {
		type: String,
		default: "",
	},
	filterStatus: {
		type: String,
		default: "",
	},
	filterPeriod: {
		type: String,
		default: "",
	},
	filterYear: {
		type: String,
		default: "",
	},
	viewMode: {
		type: String,
		default: "table",
	},
	selectedCount: {
		type: Number,
		default: 0,
	},
	filteredCount: {
		type: Number,
		default: 0,
	},
	totalCount: {
		type: Number,
		default: 0,
	},
})

defineEmits([
	"update:searchQuery",
	"update:filterStatus",
	"update:filterPeriod",
	"update:filterYear",
	"bulk-action",
	"show-analytics",
	"toggle-view",
	"clear-filters",
])

// Options
const periodOptions = [
	{ label: "Annual", value: "Annual" },
	{ label: "Mid-Year", value: "Mid-Year" },
	{ label: "Quarterly", value: "Quarterly" },
	{ label: "Ad-hoc", value: "Ad-hoc" },
]

const statusOptions = [
	{ label: "Planning", value: "Planning" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Review", value: "Review" },
	{ label: "Finalized", value: "Finalized" },
	{ label: "Approved", value: "Approved" },
]

// Generate year options
const currentYear = new Date().getFullYear()
const yearOptions = []
for (let i = currentYear - 2; i <= currentYear + 2; i++) {
	yearOptions.push({ label: i.toString(), value: i.toString() })
}

// Options with "All" as first item
const statusOptionsWithAll = computed(() => [
	{ label: "All Statuses", value: "" },
	...statusOptions,
])

const periodOptionsWithAll = computed(() => [
	{ label: "All Periods", value: "" },
	...periodOptions,
])

const yearOptionsWithAll = computed(() => [
	{ label: "All Years", value: "" },
	...yearOptions,
])

// Check if any filters are active
const hasActiveFilters = computed(() => {
	return (
		props.searchQuery ||
		props.filterStatus ||
		props.filterPeriod ||
		props.filterYear
	)
})
</script>
