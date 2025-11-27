<template>
  <div class="grid grid-cols-5 gap-4">
    <!-- Total Checklists -->
    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">Total Checklists</p>
          <p class="text-2xl font-bold text-gray-900">{{ stats.total }}</p>
        </div>
        <div class="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center">
          <ClipboardList class="h-5 w-5 text-blue-600" />
        </div>
      </div>
      <div class="mt-2 flex items-center gap-2 text-xs">
        <span class="text-gray-500">{{ stats.periodsCount }} periods</span>
      </div>
    </div>

    <!-- Total Requirements -->
    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">Total Requirements</p>
          <p class="text-2xl font-bold text-gray-900">{{ stats.totalRequirements }}</p>
        </div>
        <div class="h-10 w-10 rounded-lg bg-indigo-50 flex items-center justify-center">
          <ListChecks class="h-5 w-5 text-indigo-600" />
        </div>
      </div>
      <div class="mt-2 flex items-center gap-2 text-xs">
        <span class="text-gray-500">Across all checklists</span>
      </div>
    </div>

    <!-- Completed -->
    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">Completed</p>
          <p class="text-2xl font-bold text-green-600">{{ stats.completedRequirements }}</p>
        </div>
        <div class="h-10 w-10 rounded-lg bg-green-50 flex items-center justify-center">
          <CheckCircle class="h-5 w-5 text-green-600" />
        </div>
      </div>
      <div class="mt-2">
        <div class="w-full bg-gray-100 rounded-full h-1.5">
          <div
            class="bg-green-500 h-1.5 rounded-full"
            :style="{ width: `${stats.completionRate}%` }"
          />
        </div>
        <span class="text-xs text-gray-500 mt-1">{{ stats.completionRate }}% complete</span>
      </div>
    </div>

    <!-- Overdue -->
    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">Overdue</p>
          <p class="text-2xl font-bold" :class="stats.overdueRequirements > 0 ? 'text-red-600' : 'text-gray-400'">
            {{ stats.overdueRequirements }}
          </p>
        </div>
        <div
          class="h-10 w-10 rounded-lg flex items-center justify-center"
          :class="stats.overdueRequirements > 0 ? 'bg-red-50' : 'bg-gray-50'"
        >
          <AlertTriangle
            class="h-5 w-5"
            :class="stats.overdueRequirements > 0 ? 'text-red-600' : 'text-gray-400'"
          />
        </div>
      </div>
      <div class="mt-2 flex items-center gap-2 text-xs">
        <span :class="stats.overdueRequirements > 0 ? 'text-red-600' : 'text-gray-500'">
          {{ stats.overdueRequirements > 0 ? 'Action required' : 'All on track' }}
        </span>
      </div>
    </div>

    <!-- Active Alerts -->
    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">Active Alerts</p>
          <p class="text-2xl font-bold" :class="stats.totalAlerts > 0 ? 'text-orange-600' : 'text-gray-400'">
            {{ stats.totalAlerts }}
          </p>
        </div>
        <div
          class="h-10 w-10 rounded-lg flex items-center justify-center"
          :class="stats.totalAlerts > 0 ? 'bg-orange-50' : 'bg-gray-50'"
        >
          <Bell
            class="h-5 w-5"
            :class="stats.totalAlerts > 0 ? 'text-orange-600' : 'text-gray-400'"
          />
        </div>
      </div>
      <div class="mt-2 flex items-center gap-2 text-xs">
        <Badge v-if="stats.criticalAlerts > 0" theme="red" size="sm">
          {{ stats.criticalAlerts }} critical
        </Badge>
        <span v-else class="text-gray-500">No critical alerts</span>
      </div>
    </div>
  </div>

  <!-- Period Type Breakdown -->
  <div class="grid grid-cols-3 gap-4 mt-4">
    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between mb-3">
        <h4 class="font-medium text-gray-700">By Period Type</h4>
      </div>
      <div class="space-y-3">
        <div
          v-for="period in periodTypeBreakdown"
          :key="period.type"
          class="flex items-center gap-3"
        >
          <div
            class="h-8 w-8 rounded-lg flex items-center justify-center"
            :class="period.bgClass"
          >
            <Calendar class="h-4 w-4" :class="period.iconClass" />
          </div>
          <div class="flex-1">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700">{{ period.type }}</span>
              <span class="text-sm font-medium text-gray-900">{{ period.count }}</span>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-1.5 mt-1">
              <div
                class="h-1.5 rounded-full"
                :class="period.barClass"
                :style="{ width: `${period.percentage}%` }"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between mb-3">
        <h4 class="font-medium text-gray-700">Status Distribution</h4>
      </div>
      <div class="space-y-2">
        <div
          v-for="status in statusDistribution"
          :key="status.label"
          class="flex items-center justify-between"
        >
          <div class="flex items-center gap-2">
            <div class="h-3 w-3 rounded-full" :class="status.color" />
            <span class="text-sm text-gray-600">{{ status.label }}</span>
          </div>
          <span class="text-sm font-medium text-gray-900">{{ status.count }}</span>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border p-4">
      <div class="flex items-center justify-between mb-3">
        <h4 class="font-medium text-gray-700">Average Completion</h4>
      </div>
      <div class="flex items-center justify-center py-4">
        <div class="relative h-28 w-28">
          <svg class="h-28 w-28 transform -rotate-90">
            <circle
              cx="56"
              cy="56"
              r="48"
              stroke="currentColor"
              stroke-width="12"
              fill="transparent"
              class="text-gray-200"
            />
            <circle
              cx="56"
              cy="56"
              r="48"
              stroke="currentColor"
              stroke-width="12"
              fill="transparent"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="strokeDashoffset"
              stroke-linecap="round"
              :class="getCompletionColorClass(stats.avgCompletion)"
            />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-2xl font-bold text-gray-900">{{ stats.avgCompletion }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Badge } from 'frappe-ui'
import {
  ClipboardList,
  ListChecks,
  CheckCircle,
  AlertTriangle,
  Bell,
  Calendar,
} from 'lucide-vue-next'

const props = defineProps({
  checklists: {
    type: Array,
    default: () => [],
  },
})

const circumference = 2 * Math.PI * 48

const stats = computed(() => {
  const total = props.checklists.length

  // Aggregate all items across checklists
  const allItems = props.checklists.flatMap((c) => c.checklist_items || [])
  const totalRequirements = allItems.length
  const completedRequirements = allItems.filter((i) =>
    ['Completed', 'Filed'].includes(i.status)
  ).length
  const overdueRequirements = allItems.filter((i) => i.status === 'Overdue').length

  const completionRate =
    totalRequirements > 0
      ? Math.round((completedRequirements / totalRequirements) * 100)
      : 0

  // Alerts
  const allAlerts = props.checklists.flatMap((c) => c.alerts || [])
  const totalAlerts = allAlerts.length
  const criticalAlerts = allAlerts.filter((a) => a.severity === 'Critical').length

  // Average completion percentage
  const completionPercentages = props.checklists
    .filter((c) => c.completion_percent !== null && c.completion_percent !== undefined)
    .map((c) => c.completion_percent || 0)
  const avgCompletion =
    completionPercentages.length > 0
      ? Math.round(
          completionPercentages.reduce((sum, p) => sum + p, 0) / completionPercentages.length
        )
      : 0

  // Unique periods
  const periodsCount = new Set(props.checklists.map((c) => c.compliance_period)).size

  return {
    total,
    totalRequirements,
    completedRequirements,
    overdueRequirements,
    completionRate,
    totalAlerts,
    criticalAlerts,
    avgCompletion,
    periodsCount,
  }
})

const strokeDashoffset = computed(() => {
  const progress = stats.value.avgCompletion / 100
  return circumference * (1 - progress)
})

const periodTypeBreakdown = computed(() => {
  const total = props.checklists.length || 1
  const types = ['Monthly', 'Quarterly', 'Annual']

  const colors = {
    Monthly: { bgClass: 'bg-blue-50', iconClass: 'text-blue-600', barClass: 'bg-blue-500' },
    Quarterly: { bgClass: 'bg-purple-50', iconClass: 'text-purple-600', barClass: 'bg-purple-500' },
    Annual: { bgClass: 'bg-green-50', iconClass: 'text-green-600', barClass: 'bg-green-500' },
  }

  return types.map((type) => {
    const count = props.checklists.filter((c) => c.period_type === type).length
    return {
      type,
      count,
      percentage: Math.round((count / total) * 100),
      ...colors[type],
    }
  })
})

const statusDistribution = computed(() => {
  const allItems = props.checklists.flatMap((c) => c.checklist_items || [])
  const statuses = [
    { label: 'Not Started', color: 'bg-gray-400' },
    { label: 'In Progress', color: 'bg-blue-500' },
    { label: 'Completed', color: 'bg-green-500' },
    { label: 'Filed', color: 'bg-purple-500' },
    { label: 'Overdue', color: 'bg-red-500' },
    { label: 'Not Applicable', color: 'bg-gray-300' },
  ]

  return statuses.map((s) => ({
    ...s,
    count: allItems.filter((i) => i.status === s.label).length,
  }))
})

function getCompletionColorClass(percent) {
  if (percent >= 90) return 'text-green-500'
  if (percent >= 70) return 'text-blue-500'
  if (percent >= 50) return 'text-orange-500'
  return 'text-red-500'
}
</script>
