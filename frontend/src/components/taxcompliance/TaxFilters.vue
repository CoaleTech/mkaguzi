<template>
  <div class="bg-white rounded-xl border p-4">
    <div class="flex flex-wrap items-center gap-4">
      <!-- Search -->
      <div class="flex-1 min-w-[200px] max-w-md">
        <FormControl
          v-model="localFilters.search"
          type="text"
          placeholder="Search by tracker ID..."
          :debounce="300"
          @update:modelValue="emitFilters"
        >
          <template #prefix>
            <Search class="h-4 w-4 text-gray-400" />
          </template>
        </FormControl>
      </div>

      <!-- Tax Period Filter -->
      <div class="w-44">
        <LinkField
          v-model="localFilters.taxPeriod"
          doctype="Data Period"
          placeholder="All Periods"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Tax Type Filter -->
      <div class="w-36">
        <Select
          v-model="localFilters.taxType"
          :options="taxTypeOptions"
          placeholder="Tax Type"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Filing Status Filter -->
      <div class="w-36">
        <Select
          v-model="localFilters.filingStatus"
          :options="filingStatusOptions"
          placeholder="Filing Status"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Compliance Score Range -->
      <div class="w-40">
        <Select
          v-model="localFilters.scoreRange"
          :options="scoreRangeOptions"
          placeholder="Score Range"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Has Issues Filter -->
      <div class="w-32">
        <Select
          v-model="localFilters.hasIssues"
          :options="hasIssuesOptions"
          placeholder="Issues"
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
          New Tracker
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
        v-if="localFilters.taxPeriod"
        theme="purple"
        class="cursor-pointer"
        @click="removeFilter('taxPeriod')"
      >
        Period: {{ localFilters.taxPeriod }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.taxType"
        theme="green"
        class="cursor-pointer"
        @click="removeFilter('taxType')"
      >
        Type: {{ localFilters.taxType }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.filingStatus"
        theme="indigo"
        class="cursor-pointer"
        @click="removeFilter('filingStatus')"
      >
        Status: {{ localFilters.filingStatus }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.scoreRange"
        theme="orange"
        class="cursor-pointer"
        @click="removeFilter('scoreRange')"
      >
        Score: {{ localFilters.scoreRange }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.hasIssues"
        theme="red"
        class="cursor-pointer"
        @click="removeFilter('hasIssues')"
      >
        {{ localFilters.hasIssues === 'yes' ? 'Has Issues' : 'No Issues' }}
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
  taxPeriod: '',
  taxType: '',
  filingStatus: '',
  scoreRange: '',
  hasIssues: '',
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

const taxTypeOptions = [
  { label: 'All Tax Types', value: '' },
  { label: 'VAT', value: 'VAT' },
  { label: 'PAYE', value: 'PAYE' },
  { label: 'Withholding Tax', value: 'WHT' },
  { label: 'NSSF', value: 'NSSF' },
  { label: 'NHIF', value: 'NHIF' },
]

const filingStatusOptions = [
  { label: 'All Status', value: '' },
  { label: 'All Filed', value: 'filed' },
  { label: 'Pending Filing', value: 'pending' },
  { label: 'Overdue', value: 'overdue' },
]

const scoreRangeOptions = [
  { label: 'All Scores', value: '' },
  { label: 'Excellent (90-100%)', value: '90-100' },
  { label: 'Good (70-89%)', value: '70-89' },
  { label: 'Fair (50-69%)', value: '50-69' },
  { label: 'Poor (0-49%)', value: '0-49' },
]

const hasIssuesOptions = [
  { label: 'All', value: '' },
  { label: 'Has Issues', value: 'yes' },
  { label: 'No Issues', value: 'no' },
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
