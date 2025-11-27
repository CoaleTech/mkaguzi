<template>
  <div class="space-y-4">
    <!-- Stats Cards Row -->
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
      <div
        v-for="stat in statsCards"
        :key="stat.label"
        class="bg-white rounded-xl border p-4 hover:shadow-md transition-shadow cursor-pointer"
        :class="stat.active ? 'ring-2 ring-blue-500' : ''"
        @click="$emit('filter', stat.filterKey, stat.filterValue)"
      >
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-lg" :class="stat.bgColor">
            <component :is="stat.icon" class="h-5 w-5" :class="stat.iconColor" />
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ stat.value }}</div>
            <div class="text-xs text-gray-500">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Status Distribution -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Status Distribution</h3>
        <div class="space-y-3">
          <div
            v-for="status in statusDistribution"
            :key="status.name"
            class="flex items-center gap-3 cursor-pointer hover:bg-gray-50 p-1 rounded"
            @click="$emit('filter', 'status', status.name)"
          >
            <div class="w-3 h-3 rounded-full" :class="status.dotColor"></div>
            <div class="flex-1 text-sm text-gray-600">{{ status.name }}</div>
            <div class="text-sm font-medium text-gray-700">{{ status.count }}</div>
            <div class="w-20 bg-gray-100 rounded-full h-2">
              <div
                class="h-2 rounded-full"
                :class="status.barColor"
                :style="{ width: `${status.percentage}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pass/Fail Rate -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Test Results Summary</h3>
        <div class="flex items-center justify-center">
          <div class="relative h-40 w-40">
            <svg viewBox="0 0 36 36" class="transform -rotate-90">
              <!-- Background circle -->
              <circle
                cx="18" cy="18" r="15.9"
                fill="none"
                stroke="#E5E7EB"
                stroke-width="3"
              />
              <!-- Pass segment -->
              <circle
                cx="18" cy="18" r="15.9"
                fill="none"
                stroke="#22C55E"
                stroke-width="3"
                :stroke-dasharray="`${passRate} ${100 - passRate}`"
                stroke-linecap="round"
              />
              <!-- Fail segment -->
              <circle
                cx="18" cy="18" r="15.9"
                fill="none"
                stroke="#EF4444"
                stroke-width="3"
                :stroke-dasharray="`${failRate} ${100 - failRate}`"
                :stroke-dashoffset="`${-passRate}`"
                stroke-linecap="round"
              />
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <div class="text-2xl font-bold text-gray-900">{{ totalTests }}</div>
              <div class="text-xs text-gray-500">Total Tests</div>
            </div>
          </div>
        </div>
        <div class="flex justify-center gap-6 mt-4">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-green-500"></div>
            <span class="text-sm text-gray-600">Pass: {{ passedTests }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-red-500"></div>
            <span class="text-sm text-gray-600">Fail: {{ failedTests }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span class="text-sm text-gray-600">Warn: {{ warningTests }}</span>
          </div>
        </div>
      </div>

      <!-- Performance Overview -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Performance Overview</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Clock class="h-4 w-4 text-gray-400" />
              <span class="text-sm text-gray-600">Avg Duration</span>
            </div>
            <span class="text-sm font-semibold text-gray-900">{{ avgDuration }}</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Zap class="h-4 w-4 text-gray-400" />
              <span class="text-sm text-gray-600">Throughput</span>
            </div>
            <span class="text-sm font-semibold text-gray-900">{{ avgThroughput }} rec/s</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <AlertTriangle class="h-4 w-4 text-gray-400" />
              <span class="text-sm text-gray-600">Total Exceptions</span>
            </div>
            <span class="text-sm font-semibold text-red-600">{{ totalExceptions }}</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Database class="h-4 w-4 text-gray-400" />
              <span class="text-sm text-gray-600">Records Processed</span>
            </div>
            <span class="text-sm font-semibold text-gray-900">{{ formatNumber(totalRecords) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Executions Timeline -->
    <div class="bg-white rounded-xl border p-4">
      <h3 class="text-sm font-medium text-gray-700 mb-4">Recent Executions</h3>
      <div class="flex items-center gap-2 overflow-x-auto pb-2">
        <div
          v-for="exec in recentExecutions"
          :key="exec.name"
          class="flex-shrink-0 p-3 rounded-lg border cursor-pointer hover:shadow-sm transition-shadow min-w-[200px]"
          :class="getStatusBgClass(exec.status)"
          @click="$emit('select', exec)"
        >
          <div class="flex items-center justify-between mb-2">
            <Badge :theme="getStatusTheme(exec.status)">{{ exec.status }}</Badge>
            <span class="text-xs text-gray-500">{{ formatTime(exec.creation) }}</span>
          </div>
          <div class="text-sm font-medium text-gray-800 truncate">{{ exec.execution_name }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ exec.test_library_reference }}</div>
        </div>
        <div v-if="!recentExecutions.length" class="text-sm text-gray-500 py-4">
          No recent executions
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Badge } from 'frappe-ui'
import {
  Play,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Pause,
  Clock,
  Loader,
  Ban,
  Zap,
  Database,
} from 'lucide-vue-next'

const props = defineProps({
  executions: { type: Array, default: () => [] },
  activeFilter: { type: String, default: '' },
})

defineEmits(['filter', 'select'])

// Stats cards
const statsCards = computed(() => {
  const execs = props.executions
  const total = execs.length
  const pending = execs.filter((e) => e.status === 'Pending').length
  const running = execs.filter((e) => e.status === 'Running').length
  const completed = execs.filter((e) => e.status === 'Completed').length
  const failed = execs.filter((e) => e.status === 'Failed').length
  const queued = execs.filter((e) => e.status === 'Queued').length
  const paused = execs.filter((e) => e.status === 'Paused').length

  return [
    { label: 'Total', value: total, icon: Play, bgColor: 'bg-blue-100', iconColor: 'text-blue-600', filterKey: null, filterValue: null },
    { label: 'Pending', value: pending, icon: Clock, bgColor: 'bg-gray-100', iconColor: 'text-gray-600', filterKey: 'status', filterValue: 'Pending', active: props.activeFilter === 'Pending' },
    { label: 'Queued', value: queued, icon: Loader, bgColor: 'bg-indigo-100', iconColor: 'text-indigo-600', filterKey: 'status', filterValue: 'Queued', active: props.activeFilter === 'Queued' },
    { label: 'Running', value: running, icon: Play, bgColor: 'bg-blue-100', iconColor: 'text-blue-600', filterKey: 'status', filterValue: 'Running', active: props.activeFilter === 'Running' },
    { label: 'Completed', value: completed, icon: CheckCircle, bgColor: 'bg-green-100', iconColor: 'text-green-600', filterKey: 'status', filterValue: 'Completed', active: props.activeFilter === 'Completed' },
    { label: 'Failed', value: failed, icon: XCircle, bgColor: 'bg-red-100', iconColor: 'text-red-600', filterKey: 'status', filterValue: 'Failed', active: props.activeFilter === 'Failed' },
    { label: 'Paused', value: paused, icon: Pause, bgColor: 'bg-yellow-100', iconColor: 'text-yellow-600', filterKey: 'status', filterValue: 'Paused', active: props.activeFilter === 'Paused' },
  ]
})

// Status distribution
const statusDistribution = computed(() => {
  const execs = props.executions
  const total = execs.length || 1
  const statuses = ['Pending', 'Queued', 'Running', 'Completed', 'Failed', 'Cancelled', 'Paused']
  const colors = {
    Pending: { dot: 'bg-gray-400', bar: 'bg-gray-400' },
    Queued: { dot: 'bg-indigo-400', bar: 'bg-indigo-400' },
    Running: { dot: 'bg-blue-500', bar: 'bg-blue-500' },
    Completed: { dot: 'bg-green-500', bar: 'bg-green-500' },
    Failed: { dot: 'bg-red-500', bar: 'bg-red-500' },
    Cancelled: { dot: 'bg-gray-500', bar: 'bg-gray-500' },
    Paused: { dot: 'bg-yellow-500', bar: 'bg-yellow-500' },
  }

  return statuses.map((name) => ({
    name,
    count: execs.filter((e) => e.status === name).length,
    percentage: Math.round((execs.filter((e) => e.status === name).length / total) * 100),
    dotColor: colors[name]?.dot || 'bg-gray-400',
    barColor: colors[name]?.bar || 'bg-gray-400',
  })).filter((s) => s.count > 0)
})

// Test results aggregation
const totalTests = computed(() => {
  return props.executions.reduce((sum, e) => sum + (e.total_tests || 0), 0)
})

const passedTests = computed(() => {
  return props.executions.reduce((sum, e) => sum + (e.passed_tests || 0), 0)
})

const failedTests = computed(() => {
  return props.executions.reduce((sum, e) => sum + (e.failed_tests || 0), 0)
})

const warningTests = computed(() => {
  return props.executions.reduce((sum, e) => sum + (e.warning_tests || 0), 0)
})

const passRate = computed(() => {
  if (!totalTests.value) return 0
  return Math.round((passedTests.value / totalTests.value) * 100)
})

const failRate = computed(() => {
  if (!totalTests.value) return 0
  return Math.round((failedTests.value / totalTests.value) * 100)
})

// Performance metrics
const avgDuration = computed(() => {
  const completed = props.executions.filter((e) => e.execution_time_ms)
  if (!completed.length) return '0ms'
  const avg = completed.reduce((sum, e) => sum + e.execution_time_ms, 0) / completed.length
  if (avg < 1000) return `${Math.round(avg)}ms`
  if (avg < 60000) return `${(avg / 1000).toFixed(1)}s`
  return `${(avg / 60000).toFixed(1)}m`
})

const avgThroughput = computed(() => {
  const completed = props.executions.filter((e) => e.records_per_second)
  if (!completed.length) return 0
  return Math.round(completed.reduce((sum, e) => sum + e.records_per_second, 0) / completed.length)
})

const totalExceptions = computed(() => {
  return props.executions.reduce((sum, e) => sum + (e.exceptions_found || 0), 0)
})

const totalRecords = computed(() => {
  return props.executions.reduce((sum, e) => sum + (e.total_records_processed || 0), 0)
})

// Recent executions
const recentExecutions = computed(() => {
  return [...props.executions]
    .sort((a, b) => new Date(b.creation) - new Date(a.creation))
    .slice(0, 5)
})

// Helper functions
function formatNumber(num) {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

function formatTime(datetime) {
  if (!datetime) return ''
  return new Date(datetime).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function getStatusTheme(status) {
  const themes = {
    Pending: 'gray',
    Queued: 'blue',
    Running: 'blue',
    Completed: 'green',
    Failed: 'red',
    Cancelled: 'gray',
    Paused: 'orange',
  }
  return themes[status] || 'gray'
}

function getStatusBgClass(status) {
  const classes = {
    Pending: 'bg-gray-50 border-gray-200',
    Queued: 'bg-indigo-50 border-indigo-200',
    Running: 'bg-blue-50 border-blue-200',
    Completed: 'bg-green-50 border-green-200',
    Failed: 'bg-red-50 border-red-200',
    Cancelled: 'bg-gray-50 border-gray-200',
    Paused: 'bg-yellow-50 border-yellow-200',
  }
  return classes[status] || 'bg-gray-50 border-gray-200'
}
</script>
