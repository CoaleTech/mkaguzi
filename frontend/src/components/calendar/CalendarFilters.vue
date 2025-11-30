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
              v-model="localFilters.searchQuery"
              type="text"
              class="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm w-48"
              placeholder="Search audits..."
              @input="handleFilterChange"
            />
          </div>

          <Select
            v-model="localFilters.statusFilter"
            :options="[
              { label: 'All Status', value: '' },
              ...statusOptions
            ]"
            class="min-w-36"
            @change="handleFilterChange"
          />

          <Select
            v-model="localFilters.typeFilter"
            :options="[
              { label: 'All Types', value: '' },
              ...auditTypeOptions
            ]"
            class="min-w-32"
            @change="handleFilterChange"
          />

          <Select
            v-model="localFilters.universeFilter"
            :options="[
              { label: 'All Universes', value: '' },
              ...universeOptions
            ]"
            class="min-w-40"
            @change="handleFilterChange"
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
            @click="$emit('bulk-actions')"
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
            @click="$emit('capacity-planning')"
          >
            <template #prefix>
              <BarChart3Icon class="h-3.5 w-3.5" />
            </template>
            Capacity Planning
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
              <component :is="viewMode === 'calendar' ? 'TableIcon' : 'CalendarIcon'" class="h-3.5 w-3.5" />
            </template>
            {{ viewMode === 'calendar' ? 'List View' : 'Calendar View' }}
          </Button>
        </div>
      </div>

      <!-- Right Section: Results Count -->
      <div class="flex items-center space-x-2 text-sm text-gray-600">
        <span>Showing {{ filteredCount }} of {{ totalCount }} audits</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Select } from "frappe-ui"
import {
	BarChart3Icon,
	CalendarIcon,
	LayersIcon,
	SearchIcon,
	TableIcon,
} from "lucide-vue-next"
import { ref, watch } from "vue"

// Props
const props = defineProps({
	filters: {
		type: Object,
		required: true,
		validator: (filters) => {
			return (
				typeof filters === "object" &&
				typeof filters.searchQuery === "string" &&
				typeof filters.statusFilter === "string" &&
				typeof filters.typeFilter === "string" &&
				typeof filters.universeFilter === "string"
			)
		},
	},
	statusOptions: {
		type: Array,
		required: true,
	},
	auditTypeOptions: {
		type: Array,
		required: true,
	},
	universeOptions: {
		type: Array,
		required: true,
	},
	selectedCount: {
		type: Number,
		default: 0,
	},
	filteredCount: {
		type: Number,
		required: true,
	},
	totalCount: {
		type: Number,
		required: true,
	},
	viewMode: {
		type: String,
		required: true,
		validator: (value) => ["calendar", "list"].includes(value),
	},
})

// Emits
const emit = defineEmits([
	"update:filters",
	"bulk-actions",
	"capacity-planning",
	"toggle-view",
])

// Reactive local filters
const localFilters = ref({
	searchQuery: "",
	statusFilter: "",
	typeFilter: "",
	universeFilter: "",
})

// Watch for prop changes to sync local filters
watch(
	() => props.filters,
	(newFilters) => {
		localFilters.value = { ...newFilters }
	},
	{ immediate: true, deep: true },
)

// Methods
const handleFilterChange = () => {
	emit("update:filters", { ...localFilters.value })
}
</script>