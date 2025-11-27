<template>
  <div class="bg-white rounded-xl border p-4">
    <div class="flex flex-wrap items-center gap-4">
      <!-- Search -->
      <div class="flex-1 min-w-[200px] max-w-md">
        <FormControl
          v-model="localFilters.search"
          type="text"
          placeholder="Search by tracker ID or finding..."
          :debounce="300"
          @update:modelValue="emitFilters"
        >
          <template #prefix>
            <Search class="h-4 w-4 text-gray-400" />
          </template>
        </FormControl>
      </div>

      <!-- Finding Link Filter -->
      <div class="w-44">
        <LinkField
          v-model="localFilters.auditFinding"
          doctype="Audit Finding"
          placeholder="All Findings"
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

      <!-- Follow-up Type Filter -->
      <div class="w-48">
        <Select
          v-model="localFilters.followUpType"
          :options="followUpTypeOptions"
          placeholder="All Types"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Frequency Filter -->
      <div class="w-32">
        <Select
          v-model="localFilters.frequency"
          :options="frequencyOptions"
          placeholder="Frequency"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Current Status Filter -->
      <div class="w-40">
        <Select
          v-model="localFilters.currentStatus"
          :options="currentStatusOptions"
          placeholder="Current Status"
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
        v-if="localFilters.auditFinding"
        theme="purple"
        class="cursor-pointer"
        @click="removeFilter('auditFinding')"
      >
        Finding: {{ localFilters.auditFinding }}
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
        v-if="localFilters.followUpType"
        theme="indigo"
        class="cursor-pointer"
        @click="removeFilter('followUpType')"
      >
        Type: {{ localFilters.followUpType }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.frequency"
        theme="orange"
        class="cursor-pointer"
        @click="removeFilter('frequency')"
      >
        Frequency: {{ localFilters.frequency }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.currentStatus"
        theme="gray"
        class="cursor-pointer"
        @click="removeFilter('currentStatus')"
      >
        Progress: {{ localFilters.currentStatus }}
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
  auditFinding: '',
  status: '',
  followUpType: '',
  frequency: '',
  currentStatus: '',
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

const statusOptions = [
  { label: 'All Status', value: '' },
  { label: 'Active', value: 'Active' },
  { label: 'Completed', value: 'Completed' },
  { label: 'On Hold', value: 'On Hold' },
  { label: 'Cancelled', value: 'Cancelled' },
]

const followUpTypeOptions = [
  { label: 'All Types', value: '' },
  { label: 'Corrective Action Monitoring', value: 'Corrective Action Monitoring' },
  { label: 'Preventive Measure Verification', value: 'Preventive Measure Verification' },
  { label: 'Process Improvement Tracking', value: 'Process Improvement Tracking' },
  { label: 'Risk Mitigation Assessment', value: 'Risk Mitigation Assessment' },
  { label: 'Compliance Verification', value: 'Compliance Verification' },
]

const frequencyOptions = [
  { label: 'All Frequencies', value: '' },
  { label: 'Monthly', value: 'Monthly' },
  { label: 'Quarterly', value: 'Quarterly' },
  { label: 'Semi-Annual', value: 'Semi-Annual' },
  { label: 'Annual', value: 'Annual' },
  { label: 'One-time', value: 'One-time' },
  { label: 'As Needed', value: 'As Needed' },
]

const currentStatusOptions = [
  { label: 'All Progress', value: '' },
  { label: 'On Track', value: 'On Track' },
  { label: 'Behind Schedule', value: 'Behind Schedule' },
  { label: 'At Risk', value: 'At Risk' },
  { label: 'Off Track', value: 'Off Track' },
  { label: 'Completed Successfully', value: 'Completed Successfully' },
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
