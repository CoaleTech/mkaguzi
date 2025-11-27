<template>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 mb-6">
    <!-- Active Plans Card -->
    <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl border border-green-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-green-700 uppercase tracking-wide">Active Plans</p>
          <p class="text-3xl font-bold text-green-900 mt-1">{{ stats.active || 0 }}</p>
          <p class="text-xs text-green-600 mt-1">{{ activePercentage }}% of total</p>
        </div>
        <div class="p-3 bg-green-500 rounded-xl shadow-sm">
          <CheckCircle2Icon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Planned Audits Card -->
    <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide">Planned Audits</p>
          <p class="text-3xl font-bold text-blue-900 mt-1">{{ stats.plannedAudits || 0 }}</p>
          <p class="text-xs text-blue-600 mt-1">Across all plans</p>
        </div>
        <div class="p-3 bg-blue-500 rounded-xl shadow-sm">
          <ClipboardListIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Resource Utilization Card -->
    <div class="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl border border-amber-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div class="w-full">
          <p class="text-sm font-semibold text-amber-700 uppercase tracking-wide">Avg Utilization</p>
          <p class="text-3xl font-bold text-amber-900 mt-1">{{ stats.avgUtilization || 0 }}%</p>
          <div class="w-full bg-amber-200 rounded-full h-2 mt-2">
            <div
              class="bg-amber-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${Math.min(stats.avgUtilization || 0, 100)}%` }"
            ></div>
          </div>
        </div>
        <div class="p-3 bg-amber-500 rounded-xl shadow-sm ml-3">
          <UsersIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Upcoming Audits Card -->
    <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-purple-700 uppercase tracking-wide">Upcoming</p>
          <p class="text-3xl font-bold text-purple-900 mt-1">{{ stats.upcoming || 0 }}</p>
          <p class="text-xs text-purple-600 mt-1">Next 30 days</p>
        </div>
        <div class="p-3 bg-purple-500 rounded-xl shadow-sm">
          <CalendarIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Total Days Card -->
    <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border border-gray-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-gray-700 uppercase tracking-wide">Total Days</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.totalDays || 0 }}</p>
          <p class="text-xs text-gray-600 mt-1">Planned across all</p>
        </div>
        <div class="p-3 bg-gray-500 rounded-xl shadow-sm">
          <ClockIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>
  </div>

  <!-- Status Distribution & Budget Summary -->
  <div v-if="showDetails" class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
    <!-- Status Distribution -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h3 class="text-sm font-semibold text-gray-900 mb-4">Plans by Status</h3>
      <div class="space-y-3">
        <div v-for="status in statusDistribution" :key="status.label" class="flex items-center">
          <div class="w-24 text-sm text-gray-600">{{ status.label }}</div>
          <div class="flex-1 mx-3">
            <div class="w-full bg-gray-100 rounded-full h-3">
              <div
                class="h-3 rounded-full transition-all duration-300"
                :class="status.color"
                :style="{ width: `${status.percentage}%` }"
              ></div>
            </div>
          </div>
          <div class="w-12 text-sm font-medium text-gray-900 text-right">{{ status.count }}</div>
        </div>
      </div>
    </div>

    <!-- Quarterly Overview -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h3 class="text-sm font-semibold text-gray-900 mb-4">Quarterly Audit Distribution</h3>
      <div class="grid grid-cols-4 gap-3">
        <div v-for="quarter in quarterlyData" :key="quarter.label" class="text-center p-3 bg-gray-50 rounded-lg">
          <p class="text-lg font-bold" :class="quarter.color">{{ quarter.count }}</p>
          <p class="text-xs text-gray-500">{{ quarter.label }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  CheckCircle2Icon,
  ClipboardListIcon,
  UsersIcon,
  CalendarIcon,
  ClockIcon,
} from 'lucide-vue-next'

// Props
const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      total: 0,
      active: 0,
      draft: 0,
      approved: 0,
      completed: 0,
      plannedAudits: 0,
      avgUtilization: 0,
      upcoming: 0,
      totalDays: 0,
      byQuarter: { q1: 0, q2: 0, q3: 0, q4: 0 },
    }),
  },
  showDetails: {
    type: Boolean,
    default: true,
  },
})

// Computed
const activePercentage = computed(() => {
  if (!props.stats.total) return 0
  return Math.round((props.stats.active / props.stats.total) * 100)
})

const statusDistribution = computed(() => {
  const total = props.stats.total || 1
  return [
    { 
      label: 'Draft', 
      count: props.stats.draft || 0, 
      percentage: ((props.stats.draft || 0) / total) * 100,
      color: 'bg-gray-400'
    },
    { 
      label: 'Approved', 
      count: props.stats.approved || 0, 
      percentage: ((props.stats.approved || 0) / total) * 100,
      color: 'bg-blue-500'
    },
    { 
      label: 'Active', 
      count: props.stats.active || 0, 
      percentage: ((props.stats.active || 0) / total) * 100,
      color: 'bg-green-500'
    },
    { 
      label: 'Completed', 
      count: props.stats.completed || 0, 
      percentage: ((props.stats.completed || 0) / total) * 100,
      color: 'bg-purple-500'
    },
  ]
})

const quarterlyData = computed(() => {
  const q = props.stats.byQuarter || { q1: 0, q2: 0, q3: 0, q4: 0 }
  return [
    { label: 'Q1', count: q.q1, color: 'text-blue-600' },
    { label: 'Q2', count: q.q2, color: 'text-green-600' },
    { label: 'Q3', count: q.q3, color: 'text-amber-600' },
    { label: 'Q4', count: q.q4, color: 'text-purple-600' },
  ]
})
</script>
