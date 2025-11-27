<template>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 mb-6">
    <!-- Total Actions Card -->
    <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl border border-orange-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-orange-700 uppercase tracking-wide">Total Plans</p>
          <p class="text-3xl font-bold text-orange-900 mt-1">{{ stats.total || 0 }}</p>
          <p class="text-xs text-orange-600 mt-1">All action plans</p>
        </div>
        <div class="p-3 bg-orange-500 rounded-xl shadow-sm">
          <ClipboardListIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- In Progress Card -->
    <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide">In Progress</p>
          <p class="text-3xl font-bold text-blue-900 mt-1">{{ stats.inProgress || 0 }}</p>
          <p class="text-xs text-blue-600 mt-1">Currently active</p>
        </div>
        <div class="p-3 bg-blue-500 rounded-xl shadow-sm">
          <PlayCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Completed Card -->
    <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl border border-green-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-green-700 uppercase tracking-wide">Completed</p>
          <p class="text-3xl font-bold text-green-900 mt-1">{{ stats.completed || 0 }}</p>
          <p class="text-xs text-green-600 mt-1">Successfully closed</p>
        </div>
        <div class="p-3 bg-green-500 rounded-xl shadow-sm">
          <CheckCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Overdue Card -->
    <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-xl border border-red-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-red-700 uppercase tracking-wide">Overdue</p>
          <p class="text-3xl font-bold text-red-900 mt-1">{{ stats.overdue || 0 }}</p>
          <p class="text-xs text-red-600 mt-1">Past due date</p>
        </div>
        <div class="p-3 bg-red-500 rounded-xl shadow-sm">
          <AlertCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Avg Completion Card -->
    <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div class="w-full">
          <p class="text-sm font-semibold text-purple-700 uppercase tracking-wide">Avg Progress</p>
          <p class="text-3xl font-bold text-purple-900 mt-1">{{ stats.avgProgress || 0 }}%</p>
          <div class="w-full bg-purple-200 rounded-full h-2 mt-2">
            <div
              class="bg-purple-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${Math.min(stats.avgProgress || 0, 100)}%` }"
            ></div>
          </div>
        </div>
        <div class="p-3 bg-purple-500 rounded-xl shadow-sm ml-3">
          <PercentIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>
  </div>

  <!-- Distribution Charts -->
  <div v-if="showDetails" class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
    <!-- Status Distribution -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h3 class="text-sm font-semibold text-gray-900 mb-4">Status Distribution</h3>
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

    <!-- Priority Distribution -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h3 class="text-sm font-semibold text-gray-900 mb-4">Priority Distribution</h3>
      <div class="grid grid-cols-2 gap-3">
        <div v-for="priority in priorityDistribution" :key="priority.label" class="text-center p-3 bg-gray-50 rounded-lg">
          <p class="text-lg font-bold" :class="priority.color">{{ priority.count }}</p>
          <p class="text-xs text-gray-500">{{ priority.label }}</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Due Date Summary -->
  <div v-if="showDetails" class="bg-white rounded-xl border border-gray-200 p-5 mb-6">
    <h3 class="text-sm font-semibold text-gray-900 mb-4">Due Date Summary</h3>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="text-center p-4 bg-red-50 rounded-lg">
        <p class="text-2xl font-bold text-red-600">{{ stats.overdue || 0 }}</p>
        <p class="text-xs text-red-700">Overdue</p>
      </div>
      <div class="text-center p-4 bg-amber-50 rounded-lg">
        <p class="text-2xl font-bold text-amber-600">{{ stats.dueThisWeek || 0 }}</p>
        <p class="text-xs text-amber-700">Due This Week</p>
      </div>
      <div class="text-center p-4 bg-blue-50 rounded-lg">
        <p class="text-2xl font-bold text-blue-600">{{ stats.dueThisMonth || 0 }}</p>
        <p class="text-xs text-blue-700">Due This Month</p>
      </div>
      <div class="text-center p-4 bg-green-50 rounded-lg">
        <p class="text-2xl font-bold text-green-600">{{ stats.dueLater || 0 }}</p>
        <p class="text-xs text-green-700">Due Later</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  AlertCircleIcon,
  CheckCircleIcon,
  ClipboardListIcon,
  PercentIcon,
  PlayCircleIcon,
} from 'lucide-vue-next'

// Props
const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      total: 0,
      inProgress: 0,
      completed: 0,
      overdue: 0,
      avgProgress: 0,
      dueThisWeek: 0,
      dueThisMonth: 0,
      dueLater: 0,
      byStatus: {},
      byPriority: {},
    }),
  },
  showDetails: {
    type: Boolean,
    default: true,
  },
})

// Computed
const statusDistribution = computed(() => {
  const statuses = props.stats.byStatus || {}
  const total = Object.values(statuses).reduce((sum, count) => sum + count, 0) || 1
  
  const colors = {
    'Draft': 'bg-gray-400',
    'Approved': 'bg-blue-500',
    'In Progress': 'bg-amber-500',
    'On Hold': 'bg-purple-500',
    'Completed': 'bg-green-500',
    'Cancelled': 'bg-red-500',
  }

  return Object.entries(statuses).map(([label, count]) => ({
    label,
    count,
    percentage: (count / total) * 100,
    color: colors[label] || 'bg-gray-400',
  }))
})

const priorityDistribution = computed(() => {
  const priorities = props.stats.byPriority || {}
  return [
    { label: 'Critical', count: priorities['Critical'] || 0, color: 'text-red-600' },
    { label: 'High', count: priorities['High'] || 0, color: 'text-orange-600' },
    { label: 'Medium', count: priorities['Medium'] || 0, color: 'text-amber-600' },
    { label: 'Low', count: priorities['Low'] || 0, color: 'text-green-600' },
  ]
})
</script>
