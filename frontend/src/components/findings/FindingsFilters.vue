<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
    <div class="flex flex-wrap items-center gap-4">
      <!-- Search -->
      <div class="flex-1 min-w-[200px]">
        <div class="relative">
          <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            v-model="localFilters.search"
            type="text"
            placeholder="Search findings..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @input="emitFilters"
          />
        </div>
      </div>

      <!-- Status Filter -->
      <div class="w-40">
        <FormControl
          v-model="localFilters.status"
          type="select"
          :options="statusOptions"
          placeholder="Status"
          @change="emitFilters"
        />
      </div>

      <!-- Category Filter -->
      <div class="w-44">
        <FormControl
          v-model="localFilters.category"
          type="select"
          :options="categoryOptions"
          placeholder="Category"
          @change="emitFilters"
        />
      </div>

      <!-- Risk Rating Filter -->
      <div class="w-36">
        <FormControl
          v-model="localFilters.riskRating"
          type="select"
          :options="riskRatingOptions"
          placeholder="Risk Rating"
          @change="emitFilters"
        />
      </div>

      <!-- Engagement Filter -->
      <div class="w-48">
        <FormControl
          v-model="localFilters.engagement"
          type="autocomplete"
          :options="engagementOptions"
          placeholder="Engagement"
          @change="emitFilters"
        />
      </div>

      <!-- Date Range -->
      <div class="flex items-center gap-2">
        <FormControl
          v-model="localFilters.dateFrom"
          type="date"
          placeholder="From"
          class="w-36"
          @change="emitFilters"
        />
        <span class="text-gray-400">to</span>
        <FormControl
          v-model="localFilters.dateTo"
          type="date"
          placeholder="To"
          class="w-36"
          @change="emitFilters"
        />
      </div>

      <!-- Clear Filters -->
      <Button
        v-if="hasActiveFilters"
        variant="subtle"
        @click="clearFilters"
      >
        <XMarkIcon class="h-4 w-4 mr-1" />
        Clear
      </Button>

      <!-- Advanced Filters Toggle -->
      <Button
        variant="subtle"
        @click="showAdvanced = !showAdvanced"
      >
        <AdjustmentsHorizontalIcon class="h-4 w-4 mr-1" />
        {{ showAdvanced ? 'Less' : 'More' }}
      </Button>
    </div>

    <!-- Advanced Filters -->
    <div v-if="showAdvanced" class="mt-4 pt-4 border-t border-gray-200">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Responsible Person -->
        <div class="w-48">
          <FormControl
            v-model="localFilters.responsiblePerson"
            type="autocomplete"
            :options="userOptions"
            placeholder="Responsible Person"
            @change="emitFilters"
          />
        </div>

        <!-- Follow-up Required -->
        <div class="w-40">
          <FormControl
            v-model="localFilters.followUpRequired"
            type="select"
            :options="followUpOptions"
            placeholder="Follow-up"
            @change="emitFilters"
          />
        </div>

        <!-- Overdue Only -->
        <label class="inline-flex items-center">
          <input
            type="checkbox"
            v-model="localFilters.overdueOnly"
            class="form-checkbox h-4 w-4 text-blue-600 rounded"
            @change="emitFilters"
          />
          <span class="ml-2 text-sm text-gray-700">Overdue Only</span>
        </label>

        <!-- Repeat Findings Only -->
        <label class="inline-flex items-center">
          <input
            type="checkbox"
            v-model="localFilters.repeatFindingsOnly"
            class="form-checkbox h-4 w-4 text-yellow-600 rounded"
            @change="emitFilters"
          />
          <span class="ml-2 text-sm text-gray-700">Repeat Findings</span>
        </label>

        <!-- Include in Report -->
        <label class="inline-flex items-center">
          <input
            type="checkbox"
            v-model="localFilters.includeInReport"
            class="form-checkbox h-4 w-4 text-green-600 rounded"
            @change="emitFilters"
          />
          <span class="ml-2 text-sm text-gray-700">Include in Report</span>
        </label>
      </div>
    </div>

    <!-- Active Filters Pills -->
    <div v-if="activeFilterPills.length > 0" class="mt-3 flex flex-wrap gap-2">
      <Badge
        v-for="pill in activeFilterPills"
        :key="pill.key"
        variant="subtle"
        theme="gray"
        class="cursor-pointer"
        @click="removeFilter(pill.key)"
      >
        {{ pill.label }}: {{ pill.value }}
        <XMarkIcon class="h-3 w-3 ml-1" />
      </Badge>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { Button, FormControl, Badge } from 'frappe-ui'
import {
  SearchIcon as MagnifyingGlassIcon,
  XIcon as XMarkIcon,
  SlidersHorizontalIcon as AdjustmentsHorizontalIcon,
} from 'lucide-vue-next'

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({}),
  },
  engagementOptions: {
    type: Array,
    default: () => [],
  },
  userOptions: {
    type: Array,
    default: () => [],
  },
})

// Emits
const emit = defineEmits(['update:modelValue', 'filter-change'])

// Local state
const showAdvanced = ref(false)
const localFilters = reactive({
  search: '',
  status: '',
  category: '',
  riskRating: '',
  engagement: '',
  dateFrom: '',
  dateTo: '',
  responsiblePerson: '',
  followUpRequired: '',
  overdueOnly: false,
  repeatFindingsOnly: false,
  includeInReport: false,
})

// Options
const statusOptions = [
  { label: 'All Statuses', value: '' },
  { label: 'Open', value: 'Open' },
  { label: 'Action in Progress', value: 'Action in Progress' },
  { label: 'Pending Verification', value: 'Pending Verification' },
  { label: 'Closed', value: 'Closed' },
  { label: 'Accepted as Risk', value: 'Accepted as Risk' },
  { label: 'Management Override', value: 'Management Override' },
]

const categoryOptions = [
  { label: 'All Categories', value: '' },
  { label: 'Control Weakness', value: 'Control Weakness' },
  { label: 'Process Inefficiency', value: 'Process Inefficiency' },
  { label: 'Compliance Gap', value: 'Compliance Gap' },
  { label: 'Policy Violation', value: 'Policy Violation' },
  { label: 'Documentation Issue', value: 'Documentation Issue' },
  { label: 'Fraud Indicator', value: 'Fraud Indicator' },
  { label: 'IT/System Issue', value: 'IT/System Issue' },
  { label: 'Operational Risk', value: 'Operational Risk' },
]

const riskRatingOptions = [
  { label: 'All Ratings', value: '' },
  { label: 'Critical', value: 'Critical' },
  { label: 'High', value: 'High' },
  { label: 'Medium', value: 'Medium' },
  { label: 'Low', value: 'Low' },
]

const followUpOptions = [
  { label: 'All', value: '' },
  { label: 'Required', value: '1' },
  { label: 'Not Required', value: '0' },
]

// Computed
const hasActiveFilters = computed(() => {
  return Object.entries(localFilters).some(([key, value]) => {
    if (typeof value === 'boolean') return value
    return value !== ''
  })
})

const activeFilterPills = computed(() => {
  const pills = []
  
  if (localFilters.status) {
    pills.push({ key: 'status', label: 'Status', value: localFilters.status })
  }
  if (localFilters.category) {
    pills.push({ key: 'category', label: 'Category', value: localFilters.category })
  }
  if (localFilters.riskRating) {
    pills.push({ key: 'riskRating', label: 'Risk', value: localFilters.riskRating })
  }
  if (localFilters.engagement) {
    pills.push({ key: 'engagement', label: 'Engagement', value: localFilters.engagement })
  }
  if (localFilters.overdueOnly) {
    pills.push({ key: 'overdueOnly', label: 'Filter', value: 'Overdue' })
  }
  if (localFilters.repeatFindingsOnly) {
    pills.push({ key: 'repeatFindingsOnly', label: 'Filter', value: 'Repeat' })
  }
  
  return pills
})

// Methods
const emitFilters = () => {
  emit('update:modelValue', { ...localFilters })
  emit('filter-change', { ...localFilters })
}

const clearFilters = () => {
  Object.keys(localFilters).forEach(key => {
    if (typeof localFilters[key] === 'boolean') {
      localFilters[key] = false
    } else {
      localFilters[key] = ''
    }
  })
  emitFilters()
}

const removeFilter = (key) => {
  if (typeof localFilters[key] === 'boolean') {
    localFilters[key] = false
  } else {
    localFilters[key] = ''
  }
  emitFilters()
}

// Watch for prop changes
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    Object.assign(localFilters, newVal)
  }
}, { immediate: true, deep: true })
</script>
