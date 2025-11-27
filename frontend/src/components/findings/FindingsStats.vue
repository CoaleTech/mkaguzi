<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <!-- Total Findings -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-gray-500">Total Findings</p>
          <p class="text-2xl font-bold text-gray-900 mt-1">{{ stats.total }}</p>
        </div>
        <div class="p-3 bg-blue-50 rounded-lg">
          <DocumentMagnifyingGlassIcon class="h-6 w-6 text-blue-600" />
        </div>
      </div>
      <div class="mt-3 flex items-center text-sm">
        <span class="text-gray-500">{{ stats.thisMonth }} this month</span>
      </div>
    </div>

    <!-- Open Findings -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-gray-500">Open Findings</p>
          <p class="text-2xl font-bold text-red-600 mt-1">{{ stats.open }}</p>
        </div>
        <div class="p-3 bg-red-50 rounded-lg">
          <ExclamationTriangleIcon class="h-6 w-6 text-red-600" />
        </div>
      </div>
      <div class="mt-3 flex items-center text-sm">
        <span class="text-red-600 font-medium">{{ stats.overdue }} overdue</span>
      </div>
    </div>

    <!-- In Progress -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-gray-500">In Progress</p>
          <p class="text-2xl font-bold text-yellow-600 mt-1">{{ stats.inProgress }}</p>
        </div>
        <div class="p-3 bg-yellow-50 rounded-lg">
          <ClockIcon class="h-6 w-6 text-yellow-600" />
        </div>
      </div>
      <div class="mt-3 flex items-center text-sm">
        <span class="text-gray-500">{{ stats.pendingVerification }} pending verification</span>
      </div>
    </div>

    <!-- Closed Findings -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-gray-500">Closed Findings</p>
          <p class="text-2xl font-bold text-green-600 mt-1">{{ stats.closed }}</p>
        </div>
        <div class="p-3 bg-green-50 rounded-lg">
          <CheckCircleIcon class="h-6 w-6 text-green-600" />
        </div>
      </div>
      <div class="mt-3 flex items-center text-sm">
        <span class="text-green-600 font-medium">{{ stats.closureRate }}%</span>
        <span class="text-gray-500 ml-1">closure rate</span>
      </div>
    </div>

    <!-- Risk Distribution (expanded row) -->
    <div class="col-span-1 md:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-medium text-gray-900">Risk Distribution</h3>
        <Badge variant="subtle" theme="gray">Open Findings</Badge>
      </div>
      <div class="grid grid-cols-4 gap-3">
        <div class="text-center p-3 bg-red-50 rounded-lg">
          <p class="text-xl font-bold text-red-700">{{ stats.bySeverity.critical }}</p>
          <p class="text-xs text-red-600 mt-1">Critical</p>
        </div>
        <div class="text-center p-3 bg-orange-50 rounded-lg">
          <p class="text-xl font-bold text-orange-700">{{ stats.bySeverity.high }}</p>
          <p class="text-xs text-orange-600 mt-1">High</p>
        </div>
        <div class="text-center p-3 bg-yellow-50 rounded-lg">
          <p class="text-xl font-bold text-yellow-700">{{ stats.bySeverity.medium }}</p>
          <p class="text-xs text-yellow-600 mt-1">Medium</p>
        </div>
        <div class="text-center p-3 bg-green-50 rounded-lg">
          <p class="text-xl font-bold text-green-700">{{ stats.bySeverity.low }}</p>
          <p class="text-xs text-green-600 mt-1">Low</p>
        </div>
      </div>
    </div>

    <!-- Aging Analysis -->
    <div class="col-span-1 md:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-medium text-gray-900">Finding Aging</h3>
        <Badge variant="subtle" theme="gray">Open Findings</Badge>
      </div>
      <div class="space-y-3">
        <div class="flex items-center">
          <span class="w-24 text-sm text-gray-600">0-30 days</span>
          <div class="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
            <div
              class="h-full bg-green-500 rounded-full"
              :style="{ width: `${getAgingPercentage(stats.aging.days0to30)}%` }"
            ></div>
          </div>
          <span class="w-12 text-right text-sm font-medium text-gray-900">{{ stats.aging.days0to30 }}</span>
        </div>
        <div class="flex items-center">
          <span class="w-24 text-sm text-gray-600">31-60 days</span>
          <div class="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
            <div
              class="h-full bg-yellow-500 rounded-full"
              :style="{ width: `${getAgingPercentage(stats.aging.days31to60)}%` }"
            ></div>
          </div>
          <span class="w-12 text-right text-sm font-medium text-gray-900">{{ stats.aging.days31to60 }}</span>
        </div>
        <div class="flex items-center">
          <span class="w-24 text-sm text-gray-600">61-90 days</span>
          <div class="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
            <div
              class="h-full bg-orange-500 rounded-full"
              :style="{ width: `${getAgingPercentage(stats.aging.days61to90)}%` }"
            ></div>
          </div>
          <span class="w-12 text-right text-sm font-medium text-gray-900">{{ stats.aging.days61to90 }}</span>
        </div>
        <div class="flex items-center">
          <span class="w-24 text-sm text-gray-600">90+ days</span>
          <div class="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
            <div
              class="h-full bg-red-500 rounded-full"
              :style="{ width: `${getAgingPercentage(stats.aging.days90plus)}%` }"
            ></div>
          </div>
          <span class="w-12 text-right text-sm font-medium text-gray-900">{{ stats.aging.days90plus }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Badge } from 'frappe-ui'
import {
  SearchIcon as DocumentMagnifyingGlassIcon,
  AlertTriangleIcon as ExclamationTriangleIcon,
  ClockIcon,
  CheckCircle2Icon as CheckCircleIcon,
} from 'lucide-vue-next'

// Props
const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      total: 0,
      thisMonth: 0,
      open: 0,
      overdue: 0,
      inProgress: 0,
      pendingVerification: 0,
      closed: 0,
      closureRate: 0,
      bySeverity: {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
      },
      aging: {
        days0to30: 0,
        days31to60: 0,
        days61to90: 0,
        days90plus: 0,
      },
    }),
  },
})

// Computed
const totalAging = computed(() => {
  const aging = props.stats.aging || {}
  return (aging.days0to30 || 0) + (aging.days31to60 || 0) + (aging.days61to90 || 0) + (aging.days90plus || 0)
})

// Methods
const getAgingPercentage = (count) => {
  if (totalAging.value === 0) return 0
  return Math.round((count / totalAging.value) * 100)
}
</script>
