<template>
  <div class="flex flex-wrap items-center gap-3 mb-6">
    <!-- Search Input -->
    <div class="flex-1 min-w-[250px] max-w-md">
      <div class="relative">
        <SearchIcon class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          :value="searchQuery"
          @input="$emit('update:searchQuery', $event.target.value)"
          placeholder="Search plans..."
          class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
        />
        <button
          v-if="searchQuery"
          @click="$emit('update:searchQuery', '')"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        >
          <XIcon class="h-4 w-4" />
        </button>
      </div>
    </div>

    <!-- Status Filter -->
    <div class="w-40">
      <FormControl
        type="select"
        :modelValue="statusFilter"
        @update:modelValue="$emit('update:statusFilter', $event)"
        :options="statusOptions"
        size="sm"
        placeholder="All Status"
      />
    </div>

    <!-- Year Filter -->
    <div class="w-32">
      <FormControl
        type="select"
        :modelValue="yearFilter"
        @update:modelValue="$emit('update:yearFilter', $event)"
        :options="yearOptions"
        size="sm"
        placeholder="All Years"
      />
    </div>

    <!-- Period Filter -->
    <div class="w-40">
      <FormControl
        type="select"
        :modelValue="periodFilter"
        @update:modelValue="$emit('update:periodFilter', $event)"
        :options="periodOptions"
        size="sm"
        placeholder="All Periods"
      />
    </div>

    <!-- View Toggle -->
    <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
      <button
        @click="$emit('update:viewMode', 'table')"
        :class="[
          'p-2 rounded-md transition-all duration-200',
          viewMode === 'table' 
            ? 'bg-white text-blue-600 shadow-sm' 
            : 'text-gray-500 hover:text-gray-700'
        ]"
        title="Table View"
      >
        <ListIcon class="h-4 w-4" />
      </button>
      <button
        @click="$emit('update:viewMode', 'cards')"
        :class="[
          'p-2 rounded-md transition-all duration-200',
          viewMode === 'cards' 
            ? 'bg-white text-blue-600 shadow-sm' 
            : 'text-gray-500 hover:text-gray-700'
        ]"
        title="Card View"
      >
        <LayoutGridIcon class="h-4 w-4" />
      </button>
      <button
        @click="$emit('update:viewMode', 'timeline')"
        :class="[
          'p-2 rounded-md transition-all duration-200',
          viewMode === 'timeline' 
            ? 'bg-white text-blue-600 shadow-sm' 
            : 'text-gray-500 hover:text-gray-700'
        ]"
        title="Timeline View"
      >
        <CalendarDaysIcon class="h-4 w-4" />
      </button>
    </div>

    <!-- Clear Filters -->
    <button
      v-if="hasActiveFilters"
      @click="clearFilters"
      class="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-all"
    >
      <FilterXIcon class="h-4 w-4" />
      <span>Clear</span>
    </button>
  </div>

  <!-- Active Filters Tags -->
  <div v-if="hasActiveFilters" class="flex flex-wrap gap-2 mb-4">
    <span 
      v-if="searchQuery"
      class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium"
    >
      <SearchIcon class="h-3 w-3" />
      "{{ searchQuery }}"
      <button @click="$emit('update:searchQuery', '')" class="hover:text-blue-600">
        <XIcon class="h-3 w-3" />
      </button>
    </span>
    <span 
      v-if="statusFilter"
      class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium"
    >
      Status: {{ statusFilter }}
      <button @click="$emit('update:statusFilter', '')" class="hover:text-green-600">
        <XIcon class="h-3 w-3" />
      </button>
    </span>
    <span 
      v-if="yearFilter"
      class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-amber-100 text-amber-800 rounded-full text-xs font-medium"
    >
      Year: {{ yearFilter }}
      <button @click="$emit('update:yearFilter', '')" class="hover:text-amber-600">
        <XIcon class="h-3 w-3" />
      </button>
    </span>
    <span 
      v-if="periodFilter"
      class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium"
    >
      Period: {{ periodFilter }}
      <button @click="$emit('update:periodFilter', '')" class="hover:text-purple-600">
        <XIcon class="h-3 w-3" />
      </button>
    </span>
  </div>
</template>

<script setup>
import { FormControl } from "frappe-ui"
import {
	CalendarDaysIcon,
	FilterXIcon,
	LayoutGridIcon,
	ListIcon,
	SearchIcon,
	XIcon,
} from "lucide-vue-next"
import { computed } from "vue"

// Props
const props = defineProps({
	searchQuery: {
		type: String,
		default: "",
	},
	statusFilter: {
		type: String,
		default: "",
	},
	yearFilter: {
		type: [String, Number],
		default: "",
	},
	periodFilter: {
		type: String,
		default: "",
	},
	viewMode: {
		type: String,
		default: "table",
	},
})

// Emit
const emit = defineEmits([
	"update:searchQuery",
	"update:statusFilter",
	"update:yearFilter",
	"update:periodFilter",
	"update:viewMode",
])

// Options
const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Draft", value: "Draft" },
	{ label: "Pending Approval", value: "Pending Approval" },
	{ label: "Approved", value: "Approved" },
	{ label: "Active", value: "Active" },
	{ label: "Completed", value: "Completed" },
	{ label: "Cancelled", value: "Cancelled" },
]

const periodOptions = [
	{ label: "All Periods", value: "" },
	{ label: "Annual", value: "Annual" },
	{ label: "Q1", value: "Q1" },
	{ label: "Q2", value: "Q2" },
	{ label: "Q3", value: "Q3" },
	{ label: "Q4", value: "Q4" },
	{ label: "H1", value: "H1" },
	{ label: "H2", value: "H2" },
]

// Generate year options (current year +/- 3 years)
const currentYear = new Date().getFullYear()
const yearOptions = computed(() => {
	const years = [{ label: "All Years", value: "" }]
	for (let i = currentYear + 2; i >= currentYear - 3; i--) {
		years.push({ label: String(i), value: i })
	}
	return years
})

// Computed
const hasActiveFilters = computed(() => {
	return (
		props.searchQuery ||
		props.statusFilter ||
		props.yearFilter ||
		props.periodFilter
	)
})

// Methods
const clearFilters = () => {
	emit("update:searchQuery", "")
	emit("update:statusFilter", "")
	emit("update:yearFilter", "")
	emit("update:periodFilter", "")
}
</script>
