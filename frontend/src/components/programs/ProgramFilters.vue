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
          placeholder="Search programs..."
          class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all"
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

    <!-- Audit Type Filter -->
    <div class="w-36">
      <FormControl
        type="select"
        :modelValue="typeFilter"
        @update:modelValue="$emit('update:typeFilter', $event)"
        :options="typeOptions"
        size="sm"
        placeholder="All Types"
      />
    </div>

    <!-- Template Filter -->
    <div class="w-36">
      <FormControl
        type="select"
        :modelValue="templateFilter"
        @update:modelValue="$emit('update:templateFilter', $event)"
        :options="templateOptions"
        size="sm"
        placeholder="All Programs"
      />
    </div>

    <!-- Status Filter -->
    <div class="w-36">
      <FormControl
        type="select"
        :modelValue="statusFilter"
        @update:modelValue="$emit('update:statusFilter', $event)"
        :options="statusOptions"
        size="sm"
        placeholder="All Status"
      />
    </div>

    <!-- View Toggle -->
    <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
      <button
        @click="$emit('update:viewMode', 'table')"
        :class="[
          'p-2 rounded-md transition-all duration-200',
          viewMode === 'table' 
            ? 'bg-white text-purple-600 shadow-sm' 
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
            ? 'bg-white text-purple-600 shadow-sm' 
            : 'text-gray-500 hover:text-gray-700'
        ]"
        title="Card View"
      >
        <LayoutGridIcon class="h-4 w-4" />
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
      class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium"
    >
      <SearchIcon class="h-3 w-3" />
      "{{ searchQuery }}"
      <button @click="$emit('update:searchQuery', '')" class="hover:text-purple-600">
        <XIcon class="h-3 w-3" />
      </button>
    </span>
    <span 
      v-if="typeFilter"
      class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium"
    >
      Type: {{ typeFilter }}
      <button @click="$emit('update:typeFilter', '')" class="hover:text-blue-600">
        <XIcon class="h-3 w-3" />
      </button>
    </span>
    <span 
      v-if="templateFilter"
      class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium"
    >
      {{ templateFilter === 'templates' ? 'Templates Only' : 'Programs Only' }}
      <button @click="$emit('update:templateFilter', '')" class="hover:text-green-600">
        <XIcon class="h-3 w-3" />
      </button>
    </span>
    <span 
      v-if="statusFilter"
      class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-amber-100 text-amber-800 rounded-full text-xs font-medium"
    >
      Status: {{ statusFilter }}
      <button @click="$emit('update:statusFilter', '')" class="hover:text-amber-600">
        <XIcon class="h-3 w-3" />
      </button>
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FormControl } from 'frappe-ui'
import {
  FilterXIcon,
  LayoutGridIcon,
  ListIcon,
  SearchIcon,
  XIcon,
} from 'lucide-vue-next'

// Props
const props = defineProps({
  searchQuery: {
    type: String,
    default: '',
  },
  typeFilter: {
    type: String,
    default: '',
  },
  templateFilter: {
    type: String,
    default: '',
  },
  statusFilter: {
    type: String,
    default: '',
  },
  viewMode: {
    type: String,
    default: 'table',
  },
})

// Emit
const emit = defineEmits([
  'update:searchQuery',
  'update:typeFilter',
  'update:templateFilter',
  'update:statusFilter',
  'update:viewMode',
])

// Options
const typeOptions = [
  { label: 'All Types', value: '' },
  { label: 'Financial', value: 'Financial' },
  { label: 'Operational', value: 'Operational' },
  { label: 'Compliance', value: 'Compliance' },
  { label: 'IT', value: 'IT' },
  { label: 'Inventory', value: 'Inventory' },
  { label: 'Cash', value: 'Cash' },
  { label: 'Sales', value: 'Sales' },
  { label: 'Procurement', value: 'Procurement' },
]

const templateOptions = [
  { label: 'All Programs', value: '' },
  { label: 'Templates Only', value: 'templates' },
  { label: 'Programs Only', value: 'programs' },
]

const statusOptions = [
  { label: 'All Status', value: '' },
  { label: 'Not Started', value: 'not_started' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
]

// Computed
const hasActiveFilters = computed(() => {
  return props.searchQuery || props.typeFilter || props.templateFilter || props.statusFilter
})

// Methods
const clearFilters = () => {
  emit('update:searchQuery', '')
  emit('update:typeFilter', '')
  emit('update:templateFilter', '')
  emit('update:statusFilter', '')
}
</script>
