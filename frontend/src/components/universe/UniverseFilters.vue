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
            placeholder="Search entities..."
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm w-64 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @input="emitFilters"
          />
        </div>

        <!-- Entity Type Filter -->
        <FormControl
          type="select"
          v-model="filters.entityType"
          :options="entityTypeOptions"
          placeholder="All Types"
          class="w-40"
          @change="emitFilters"
        />

        <!-- Risk Rating Filter -->
        <FormControl
          type="select"
          v-model="filters.riskRating"
          :options="riskRatingOptions"
          placeholder="All Risk Levels"
          class="w-40"
          @change="emitFilters"
        />

        <!-- Department Filter -->
        <div class="w-44">
          <LinkField
            v-model="filters.department"
            doctype="Department"
            placeholder="Department"
            @change="emitFilters"
          />
        </div>

        <!-- Status Filter -->
        <FormControl
          type="select"
          v-model="filters.status"
          :options="statusOptions"
          placeholder="All Status"
          class="w-32"
          @change="emitFilters"
        />

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
          theme="gray"
          size="sm"
          @click="$emit('create')"
        >
          <PlusIcon class="h-4 w-4 mr-1" />
          Add Entity
        </Button>
      </div>
    </div>

    <!-- Active Filters Tags -->
    <div v-if="hasActiveFilters" class="flex flex-wrap gap-2 mt-3 pt-3 border-t border-gray-100">
      <Badge
        v-if="filters.entityType"
        variant="outline"
        class="cursor-pointer"
        @click="filters.entityType = ''; emitFilters()"
      >
        Type: {{ filters.entityType }}
        <XIcon class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="filters.riskRating"
        variant="outline"
        class="cursor-pointer"
        @click="filters.riskRating = ''; emitFilters()"
      >
        Risk: {{ filters.riskRating }}
        <XIcon class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="filters.department"
        variant="outline"
        class="cursor-pointer"
        @click="filters.department = ''; emitFilters()"
      >
        Dept: {{ filters.department }}
        <XIcon class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="filters.status"
        variant="outline"
        class="cursor-pointer"
        @click="filters.status = ''; emitFilters()"
      >
        Status: {{ filters.status === 'active' ? 'Active' : 'Inactive' }}
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
  entityType: '',
  riskRating: '',
  department: '',
  status: '',
})

// Options
const entityTypeOptions = [
  { label: 'All Types', value: '' },
  { label: 'Process', value: 'Process' },
  { label: 'Function', value: 'Function' },
  { label: 'Department', value: 'Department' },
  { label: 'Location', value: 'Location' },
  { label: 'System', value: 'System' },
  { label: 'Compliance Area', value: 'Compliance Area' },
]

const riskRatingOptions = [
  { label: 'All Risk Levels', value: '' },
  { label: 'Critical', value: 'Critical' },
  { label: 'High', value: 'High' },
  { label: 'Medium', value: 'Medium' },
  { label: 'Low', value: 'Low' },
]

const statusOptions = [
  { label: 'All Status', value: '' },
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
]

// Computed
const hasActiveFilters = computed(() => {
  return filters.search || filters.entityType || filters.riskRating || filters.department || filters.status
})

// Methods
const emitFilters = () => {
  emit('update:modelValue', { ...filters })
}

const clearFilters = () => {
  filters.search = ''
  filters.entityType = ''
  filters.riskRating = ''
  filters.department = ''
  filters.status = ''
  emitFilters()
}

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    Object.assign(filters, newValue)
  }
}, { deep: true, immediate: true })
</script>
