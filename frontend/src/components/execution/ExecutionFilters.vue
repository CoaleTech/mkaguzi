<template>
  <div class="bg-white rounded-xl border p-4">
    <div class="flex flex-wrap items-center gap-4">
      <!-- Search -->
      <div class="flex-1 min-w-[200px] max-w-md">
        <FormControl
          v-model="localFilters.search"
          type="text"
          placeholder="Search by name, ID, or test..."
          :debounce="300"
          @update:modelValue="emitFilters"
        >
          <template #prefix>
            <Search class="h-4 w-4 text-gray-400" />
          </template>
        </FormControl>
      </div>

      <!-- Test Library Filter -->
      <div class="w-48">
        <LinkField
          v-model="localFilters.testLibrary"
          doctype="Audit Test Library"
          placeholder="All Tests"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Execution Type Filter -->
      <div class="w-36">
        <Select
          v-model="localFilters.executionType"
          :options="executionTypeOptions"
          placeholder="All Types"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Priority Filter -->
      <div class="w-32">
        <Select
          v-model="localFilters.priority"
          :options="priorityOptions"
          placeholder="Priority"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Status Filter -->
      <div class="w-36">
        <Select
          v-model="localFilters.status"
          :options="statusOptions"
          placeholder="All Status"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Date Range Filter -->
      <div class="w-40">
        <FormControl
          v-model="localFilters.dateFrom"
          type="date"
          placeholder="From date"
          @update:modelValue="emitFilters"
        />
      </div>
      <div class="w-40">
        <FormControl
          v-model="localFilters.dateTo"
          type="date"
          placeholder="To date"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2 ml-auto">
        <Button
          v-if="hasActiveFilters"
          variant="outline"
          @click="clearFilters"
        >
          <template #prefix><X class="h-4 w-4" /></template>
          Clear
        </Button>
        <Button variant="outline" @click="$emit('refresh')">
          <template #prefix><RefreshCw class="h-4 w-4" /></template>
          Refresh
        </Button>
        <Button variant="solid" @click="$emit('create')">
          <template #prefix><Play class="h-4 w-4" /></template>
          New Execution
        </Button>
      </div>
    </div>

    <!-- Active Filter Tags -->
    <div v-if="hasActiveFilters" class="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t">
      <span class="text-xs text-gray-500">Active filters:</span>
      <Badge
        v-if="localFilters.search"
        theme="blue"
        class="cursor-pointer"
        @click="removeFilter('search')"
      >
        Search: "{{ localFilters.search }}"
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.testLibrary"
        theme="purple"
        class="cursor-pointer"
        @click="removeFilter('testLibrary')"
      >
        Test: {{ localFilters.testLibrary }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.executionType"
        theme="indigo"
        class="cursor-pointer"
        @click="removeFilter('executionType')"
      >
        Type: {{ localFilters.executionType }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.priority"
        theme="orange"
        class="cursor-pointer"
        @click="removeFilter('priority')"
      >
        Priority: {{ localFilters.priority }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.status"
        theme="green"
        class="cursor-pointer"
        @click="removeFilter('status')"
      >
        Status: {{ localFilters.status }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.dateFrom || localFilters.dateTo"
        theme="gray"
        class="cursor-pointer"
        @click="removeFilter('dateRange')"
      >
        Date: {{ localFilters.dateFrom || '*' }} - {{ localFilters.dateTo || '*' }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, watch } from 'vue'
import { FormControl, Select, Button, Badge } from 'frappe-ui'
import LinkField from '@/components/Common/fields/LinkField.vue'
import { Search, X, RefreshCw, Play } from 'lucide-vue-next'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:filters', 'refresh', 'create'])

const localFilters = reactive({
  search: '',
  testLibrary: '',
  executionType: '',
  priority: '',
  status: '',
  dateFrom: '',
  dateTo: '',
})

// Watch for external filter changes
watch(
  () => props.filters,
  (newFilters) => {
    if (newFilters) {
      Object.assign(localFilters, newFilters)
    }
  },
  { immediate: true, deep: true }
)

const executionTypeOptions = [
  { label: 'All Types', value: '' },
  { label: 'Manual', value: 'Manual' },
  { label: 'Scheduled', value: 'Scheduled' },
  { label: 'Batch', value: 'Batch' },
  { label: 'API', value: 'API' },
]

const priorityOptions = [
  { label: 'All Priorities', value: '' },
  { label: 'Low', value: 'Low' },
  { label: 'Medium', value: 'Medium' },
  { label: 'High', value: 'High' },
  { label: 'Critical', value: 'Critical' },
]

const statusOptions = [
  { label: 'All Status', value: '' },
  { label: 'Pending', value: 'Pending' },
  { label: 'Queued', value: 'Queued' },
  { label: 'Running', value: 'Running' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Failed', value: 'Failed' },
  { label: 'Cancelled', value: 'Cancelled' },
  { label: 'Paused', value: 'Paused' },
]

const hasActiveFilters = computed(() => {
  return Object.values(localFilters).some((v) => v !== '')
})

function emitFilters() {
  emit('update:filters', { ...localFilters })
}

function removeFilter(key) {
  if (key === 'dateRange') {
    localFilters.dateFrom = ''
    localFilters.dateTo = ''
  } else {
    localFilters[key] = ''
  }
  emitFilters()
}

function clearFilters() {
  Object.keys(localFilters).forEach((key) => {
    localFilters[key] = ''
  })
  emitFilters()
}
</script>
