<template>
  <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-6">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <!-- Left: Filters -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- Search -->
        <div class="relative">
          <SearchIcon class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            v-model="filters.search"
            type="text"
            placeholder="Search action plans..."
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm w-64 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            @input="emitFilters"
          />
        </div>

        <!-- Status Filter -->
        <FormControl
          type="select"
          v-model="filters.status"
          :options="statusOptions"
          placeholder="All Status"
          class="w-36"
          @change="emitFilters"
        />

        <!-- Priority Filter -->
        <FormControl
          type="select"
          v-model="filters.priority"
          :options="priorityOptions"
          placeholder="All Priority"
          class="w-36"
          @change="emitFilters"
        />

        <!-- Due Date Range -->
        <FormControl
          type="select"
          v-model="filters.dueRange"
          :options="dueRangeOptions"
          placeholder="Due Date"
          class="w-40"
          @change="emitFilters"
        />

        <!-- Responsible Person -->
        <div class="w-44">
          <LinkField
            v-model="filters.responsiblePerson"
            doctype="User"
            placeholder="Responsible Person"
            @change="emitFilters"
          />
        </div>

        <!-- Clear Filters -->
        <Button
          v-if="hasActiveFilters"
          variant="ghost"
          size="sm"
          @click="clearFilters"
        >
          <XIcon class="h-4 w-4 mr-1" />
          Clear
        </Button>
      </div>

      <!-- Right: Actions -->
      <div class="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          @click="$emit('refresh')"
        >
          <RefreshCwIcon class="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="sm"
          @click="$emit('export')"
        >
          <DownloadIcon class="h-4 w-4 mr-1" />
          Export
        </Button>
        <Button
          variant="solid"
          theme="orange"
          size="sm"
          @click="$emit('create')"
        >
          <PlusIcon class="h-4 w-4 mr-1" />
          New Action Plan
        </Button>
      </div>
    </div>

    <!-- Active Filters Tags -->
    <div v-if="hasActiveFilters" class="flex flex-wrap gap-2 mt-3 pt-3 border-t border-gray-100">
      <Badge
        v-if="filters.status"
        variant="outline"
        class="cursor-pointer"
        @click="filters.status = ''; emitFilters()"
      >
        Status: {{ filters.status }}
        <XIcon class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="filters.priority"
        variant="outline"
        class="cursor-pointer"
        @click="filters.priority = ''; emitFilters()"
      >
        Priority: {{ filters.priority }}
        <XIcon class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="filters.dueRange"
        variant="outline"
        class="cursor-pointer"
        @click="filters.dueRange = ''; emitFilters()"
      >
        Due: {{ getDueRangeLabel(filters.dueRange) }}
        <XIcon class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="filters.responsiblePerson"
        variant="outline"
        class="cursor-pointer"
        @click="filters.responsiblePerson = ''; emitFilters()"
      >
        Responsible: {{ filters.responsiblePerson }}
        <XIcon class="h-3 w-3 ml-1" />
      </Badge>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { Badge, Button, FormControl } from 'frappe-ui'
import {
  DownloadIcon,
  PlusIcon,
  RefreshCwIcon,
  SearchIcon,
  XIcon,
} from 'lucide-vue-next'
import LinkField from '@/components/Common/fields/LinkField.vue'

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({}),
  },
})

// Emits
const emit = defineEmits(['update:modelValue', 'refresh', 'export', 'create'])

// State
const filters = reactive({
  search: '',
  status: '',
  priority: '',
  dueRange: '',
  responsiblePerson: '',
})

// Options
const statusOptions = [
  { label: 'All Status', value: '' },
  { label: 'Draft', value: 'Draft' },
  { label: 'Approved', value: 'Approved' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'On Hold', value: 'On Hold' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Cancelled', value: 'Cancelled' },
]

const priorityOptions = [
  { label: 'All Priority', value: '' },
  { label: 'Critical', value: 'Critical' },
  { label: 'High', value: 'High' },
  { label: 'Medium', value: 'Medium' },
  { label: 'Low', value: 'Low' },
]

const dueRangeOptions = [
  { label: 'All Due Dates', value: '' },
  { label: 'Overdue', value: 'overdue' },
  { label: 'Due Today', value: 'today' },
  { label: 'Due This Week', value: 'this_week' },
  { label: 'Due This Month', value: 'this_month' },
  { label: 'Due Later', value: 'later' },
]

// Computed
const hasActiveFilters = computed(() => {
  return filters.search || filters.status || filters.priority || filters.dueRange || filters.responsiblePerson
})

// Methods
const getDueRangeLabel = (value) => {
  const option = dueRangeOptions.find(o => o.value === value)
  return option ? option.label : value
}

const emitFilters = () => {
  emit('update:modelValue', { ...filters })
}

const clearFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.priority = ''
  filters.dueRange = ''
  filters.responsiblePerson = ''
  emitFilters()
}

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    Object.assign(filters, newValue)
  }
}, { deep: true, immediate: true })
</script>
