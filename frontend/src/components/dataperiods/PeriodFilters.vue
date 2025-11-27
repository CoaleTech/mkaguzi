<template>
  <div class="bg-white rounded-xl border p-4">
    <div class="flex flex-wrap items-center gap-4">
      <!-- Search -->
      <div class="flex-1 min-w-[200px] max-w-md">
        <FormControl
          v-model="localFilters.search"
          type="text"
          placeholder="Search by period name or ID..."
          :debounce="300"
          @update:modelValue="emitFilters"
        >
          <template #prefix>
            <Search class="h-4 w-4 text-gray-400" />
          </template>
        </FormControl>
      </div>

      <!-- Period Type Filter -->
      <div class="w-36">
        <Select
          v-model="localFilters.periodType"
          :options="periodTypeOptions"
          placeholder="All Types"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Fiscal Year Filter -->
      <div class="w-40">
        <LinkField
          v-model="localFilters.fiscalYear"
          doctype="Fiscal Year"
          placeholder="All Years"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Status Filter -->
      <div class="w-32">
        <Select
          v-model="localFilters.status"
          :options="statusOptions"
          placeholder="All Status"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Reconciliation Filter -->
      <div class="w-40">
        <Select
          v-model="localFilters.reconciliation"
          :options="reconciliationOptions"
          placeholder="All Reconciliation"
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
          New Period
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
        v-if="localFilters.periodType"
        theme="purple"
        class="cursor-pointer"
        @click="removeFilter('periodType')"
      >
        Type: {{ localFilters.periodType }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.fiscalYear"
        theme="indigo"
        class="cursor-pointer"
        @click="removeFilter('fiscalYear')"
      >
        Year: {{ localFilters.fiscalYear }}
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
        v-if="localFilters.reconciliation"
        theme="orange"
        class="cursor-pointer"
        @click="removeFilter('reconciliation')"
      >
        Reconciliation: {{ localFilters.reconciliation }}
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
  fiscalYear: '',
  status: '',
  reconciliation: '',
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
  { label: 'Month', value: 'Month' },
  { label: 'Quarter', value: 'Quarter' },
  { label: 'Half-Year', value: 'Half-Year' },
  { label: 'Year', value: 'Year' },
  { label: 'Custom', value: 'Custom' },
]

const statusOptions = [
  { label: 'All Status', value: '' },
  { label: 'Open', value: 'Open' },
  { label: 'Locked', value: 'Locked' },
  { label: 'Closed', value: 'Closed' },
  { label: 'Archived', value: 'Archived' },
]

const reconciliationOptions = [
  { label: 'All', value: '' },
  { label: 'Not Started', value: 'Not Started' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Issues Found', value: 'Issues Found' },
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
