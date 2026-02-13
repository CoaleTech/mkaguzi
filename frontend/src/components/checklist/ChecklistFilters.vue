<template>
  <div class="bg-white rounded-xl border p-4">
    <div class="flex flex-wrap items-center gap-4">
      <!-- Search -->
      <div class="flex-1 min-w-[200px] max-w-md">
        <FormControl
          v-model="localFilters.search"
          type="text"
          placeholder="Search by checklist ID..."
          :debounce="300"
          @update:modelValue="emitFilters"
        >
          <template #prefix>
            <Search class="h-4 w-4 text-gray-400" />
          </template>
        </FormControl>
      </div>

      <!-- Period Type Filter -->
      <div class="w-32">
        <Select
          v-model="localFilters.periodType"
          :options="periodTypeOptions"
          placeholder="Period Type"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Compliance Period Filter -->
      <div class="w-44">
        <LinkField
          v-model="localFilters.compliancePeriod"
          doctype="Data Period"
          placeholder="All Periods"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Fiscal Year Filter -->
      <div class="w-36">
        <LinkField
          v-model="localFilters.fiscalYear"
          doctype="Fiscal Year"
          placeholder="Fiscal Year"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Completion Status Filter -->
      <div class="w-36">
        <Select
          v-model="localFilters.completionStatus"
          :options="completionStatusOptions"
          placeholder="Completion"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Has Overdue Filter -->
      <div class="w-32">
        <Select
          v-model="localFilters.hasOverdue"
          :options="hasOverdueOptions"
          placeholder="Overdue"
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
          <template #prefix><Plus class="h-4 w-4" /></template>
          New Checklist
        </Button>
      </div>
    </div>

    <!-- Active Filter Tags -->
    <div v-if="hasActiveFilters" class="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t">
      <span class="text-xs text-gray-500">Active filters:</span>
      <Badge
        v-if="localFilters.search"
        theme="gray"
        class="cursor-pointer"
        @click="removeFilter('search')"
      >
        Search: "{{ localFilters.search }}"
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.periodType"
        theme="gray"
        class="cursor-pointer"
        @click="removeFilter('periodType')"
      >
        Type: {{ localFilters.periodType }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.compliancePeriod"
        theme="gray"
        class="cursor-pointer"
        @click="removeFilter('compliancePeriod')"
      >
        Period: {{ localFilters.compliancePeriod }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.fiscalYear"
        theme="indigo"
        class="cursor-pointer"
        @click="removeFilter('fiscalYear')"
      >
        FY: {{ localFilters.fiscalYear }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.completionStatus"
        theme="gray"
        class="cursor-pointer"
        @click="removeFilter('completionStatus')"
      >
        {{ localFilters.completionStatus }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.hasOverdue"
        theme="gray"
        class="cursor-pointer"
        @click="removeFilter('hasOverdue')"
      >
        {{ localFilters.hasOverdue === 'yes' ? 'Has Overdue' : 'No Overdue' }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, watch } from 'vue'
import { FormControl, Select, Button, Badge } from 'frappe-ui'
import LinkField from '@/components/Common/fields/LinkField.vue'
import { Search, X, RefreshCw, Plus } from 'lucide-vue-next'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:filters', 'refresh', 'create'])

const localFilters = reactive({
  search: '',
  periodType: '',
  compliancePeriod: '',
  fiscalYear: '',
  completionStatus: '',
  hasOverdue: '',
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

const periodTypeOptions = [
  { label: 'All Types', value: '' },
  { label: 'Monthly', value: 'Monthly' },
  { label: 'Quarterly', value: 'Quarterly' },
  { label: 'Annual', value: 'Annual' },
]

const completionStatusOptions = [
  { label: 'All', value: '' },
  { label: 'Complete (100%)', value: 'complete' },
  { label: 'Almost Done (75-99%)', value: 'almost' },
  { label: 'In Progress (25-74%)', value: 'progress' },
  { label: 'Just Started (1-24%)', value: 'started' },
  { label: 'Not Started (0%)', value: 'notstarted' },
]

const hasOverdueOptions = [
  { label: 'All', value: '' },
  { label: 'Has Overdue', value: 'yes' },
  { label: 'No Overdue', value: 'no' },
]

const hasActiveFilters = computed(() => {
  return Object.values(localFilters).some((v) => v !== '')
})

function emitFilters() {
  emit('update:filters', { ...localFilters })
}

function removeFilter(key) {
  localFilters[key] = ''
  emitFilters()
}

function clearFilters() {
  Object.keys(localFilters).forEach((key) => {
    localFilters[key] = ''
  })
  emitFilters()
}
</script>
