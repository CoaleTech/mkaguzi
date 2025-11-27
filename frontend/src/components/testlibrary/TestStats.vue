<template>
  <div class="space-y-4">
    <!-- Stats Cards Row -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <div
        v-for="stat in statsCards"
        :key="stat.label"
        class="bg-white rounded-xl border p-4 hover:shadow-md transition-shadow cursor-pointer"
        :class="stat.active ? 'ring-2 ring-blue-500' : ''"
        @click="$emit('filter', stat.filterKey, stat.filterValue)"
      >
        <div class="flex items-center gap-3">
          <div
            class="p-2 rounded-lg"
            :class="stat.bgColor"
          >
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
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Category Distribution -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Tests by Category</h3>
        <div class="space-y-3">
          <div
            v-for="category in categoryDistribution"
            :key="category.name"
            class="flex items-center gap-3"
          >
            <div class="w-32 text-sm text-gray-600 truncate">{{ category.name }}</div>
            <div class="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
              <div
                class="h-full rounded-full transition-all"
                :class="category.color"
                :style="{ width: `${category.percentage}%` }"
              ></div>
            </div>
            <div class="w-16 text-right text-sm font-medium text-gray-700">
              {{ category.count }} <span class="text-gray-400 text-xs">({{ category.percentage }}%)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Test Type Distribution -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Tests by Type</h3>
        <div class="grid grid-cols-2 gap-4">
          <div
            v-for="type in typeDistribution"
            :key="type.name"
            class="p-4 rounded-lg border text-center hover:shadow-sm transition-shadow cursor-pointer"
            :class="type.bgColor"
            @click="$emit('filter', 'test_type', type.name)"
          >
            <component :is="type.icon" class="h-8 w-8 mx-auto mb-2" :class="type.iconColor" />
            <div class="text-2xl font-bold" :class="type.textColor">{{ type.count }}</div>
            <div class="text-sm text-gray-600">{{ type.name }}</div>
            <div class="text-xs text-gray-400 mt-1">{{ type.percentage }}% of total</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Stats Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Success Rate Overview -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Average Success Rate</h3>
        <div class="flex items-center justify-center">
          <div class="relative h-32 w-32">
            <svg class="transform -rotate-90" viewBox="0 0 36 36">
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="#E5E7EB"
                stroke-width="3"
              />
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                :stroke="successRateColor"
                stroke-width="3"
                :stroke-dasharray="`${averageSuccessRate}, 100`"
                stroke-linecap="round"
              />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">{{ averageSuccessRate }}%</div>
                <div class="text-xs text-gray-500">Success</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Logic Type Distribution -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Test Logic Types</h3>
        <div class="space-y-3">
          <div
            v-for="logic in logicTypeDistribution"
            :key="logic.name"
            class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
            @click="$emit('filter', 'test_logic_type', logic.name)"
          >
            <div class="flex items-center gap-2">
              <component :is="logic.icon" class="h-5 w-5" :class="logic.iconColor" />
              <span class="text-sm text-gray-700">{{ logic.name }}</span>
            </div>
            <Badge :theme="logic.theme">{{ logic.count }}</Badge>
          </div>
        </div>
      </div>

      <!-- Usage Stats -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Usage Statistics</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Total Executions</span>
            <span class="text-lg font-semibold text-gray-900">{{ formatNumber(totalExecutions) }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Most Used Test</span>
            <span class="text-sm font-medium text-blue-600 truncate max-w-[150px]">{{ mostUsedTest }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Avg. Executions/Test</span>
            <span class="text-lg font-semibold text-gray-900">{{ avgExecutionsPerTest }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Under Review</span>
            <Badge theme="orange">{{ underReviewCount }}</Badge>
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
  FlaskConical,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Layers,
  Target,
  BarChart3,
  Shield,
  Database,
  FileCode,
  Cog,
} from 'lucide-vue-next'

const props = defineProps({
  tests: { type: Array, default: () => [] },
  activeFilter: { type: String, default: '' },
})

defineEmits(['filter'])

// Stats cards computation
const statsCards = computed(() => {
  const tests = props.tests
  const total = tests.length
  const active = tests.filter((t) => t.status === 'Active').length
  const inactive = tests.filter((t) => t.status === 'Inactive').length
  const underReview = tests.filter((t) => t.status === 'Under Review').length
  const substantive = tests.filter((t) => t.test_type === 'Substantive').length
  const controls = tests.filter((t) => t.test_type === 'Controls').length

  return [
    {
      label: 'Total Tests',
      value: total,
      icon: FlaskConical,
      bgColor: 'bg-blue-100',
      iconColor: 'text-blue-600',
      filterKey: null,
      filterValue: null,
    },
    {
      label: 'Active',
      value: active,
      icon: CheckCircle,
      bgColor: 'bg-green-100',
      iconColor: 'text-green-600',
      filterKey: 'status',
      filterValue: 'Active',
      active: props.activeFilter === 'Active',
    },
    {
      label: 'Inactive',
      value: inactive,
      icon: XCircle,
      bgColor: 'bg-gray-100',
      iconColor: 'text-gray-600',
      filterKey: 'status',
      filterValue: 'Inactive',
      active: props.activeFilter === 'Inactive',
    },
    {
      label: 'Under Review',
      value: underReview,
      icon: AlertTriangle,
      bgColor: 'bg-orange-100',
      iconColor: 'text-orange-600',
      filterKey: 'status',
      filterValue: 'Under Review',
      active: props.activeFilter === 'Under Review',
    },
    {
      label: 'Substantive',
      value: substantive,
      icon: Target,
      bgColor: 'bg-purple-100',
      iconColor: 'text-purple-600',
      filterKey: 'test_type',
      filterValue: 'Substantive',
      active: props.activeFilter === 'Substantive',
    },
    {
      label: 'Controls',
      value: controls,
      icon: Shield,
      bgColor: 'bg-indigo-100',
      iconColor: 'text-indigo-600',
      filterKey: 'test_type',
      filterValue: 'Controls',
      active: props.activeFilter === 'Controls',
    },
  ]
})

// Category distribution
const categoryDistribution = computed(() => {
  const tests = props.tests
  const categories = {}

  tests.forEach((test) => {
    const cat = test.test_category || 'Uncategorized'
    categories[cat] = (categories[cat] || 0) + 1
  })

  const total = tests.length || 1
  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-purple-500',
    'bg-orange-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-teal-500',
    'bg-red-500',
    'bg-yellow-500',
    'bg-cyan-500',
  ]

  return Object.entries(categories)
    .map(([name, count], index) => ({
      name,
      count,
      percentage: Math.round((count / total) * 100),
      color: colors[index % colors.length],
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6)
})

// Type distribution
const typeDistribution = computed(() => {
  const tests = props.tests
  const total = tests.length || 1

  return [
    {
      name: 'Substantive',
      count: tests.filter((t) => t.test_type === 'Substantive').length,
      icon: Target,
      bgColor: 'bg-purple-50 border-purple-200',
      iconColor: 'text-purple-600',
      textColor: 'text-purple-700',
      percentage: Math.round((tests.filter((t) => t.test_type === 'Substantive').length / total) * 100),
    },
    {
      name: 'Controls',
      count: tests.filter((t) => t.test_type === 'Controls').length,
      icon: Shield,
      bgColor: 'bg-indigo-50 border-indigo-200',
      iconColor: 'text-indigo-600',
      textColor: 'text-indigo-700',
      percentage: Math.round((tests.filter((t) => t.test_type === 'Controls').length / total) * 100),
    },
    {
      name: 'Analytical',
      count: tests.filter((t) => t.test_type === 'Analytical').length,
      icon: BarChart3,
      bgColor: 'bg-blue-50 border-blue-200',
      iconColor: 'text-blue-600',
      textColor: 'text-blue-700',
      percentage: Math.round((tests.filter((t) => t.test_type === 'Analytical').length / total) * 100),
    },
    {
      name: 'Compliance',
      count: tests.filter((t) => t.test_type === 'Compliance').length,
      icon: Layers,
      bgColor: 'bg-green-50 border-green-200',
      iconColor: 'text-green-600',
      textColor: 'text-green-700',
      percentage: Math.round((tests.filter((t) => t.test_type === 'Compliance').length / total) * 100),
    },
  ]
})

// Logic type distribution
const logicTypeDistribution = computed(() => {
  const tests = props.tests

  return [
    {
      name: 'SQL Query',
      count: tests.filter((t) => t.test_logic_type === 'SQL Query').length,
      icon: Database,
      iconColor: 'text-blue-600',
      theme: 'blue',
    },
    {
      name: 'Python Script',
      count: tests.filter((t) => t.test_logic_type === 'Python Script').length,
      icon: FileCode,
      iconColor: 'text-yellow-600',
      theme: 'orange',
    },
    {
      name: 'Built-in Function',
      count: tests.filter((t) => t.test_logic_type === 'Built-in Function').length,
      icon: Cog,
      iconColor: 'text-gray-600',
      theme: 'gray',
    },
  ]
})

// Average success rate
const averageSuccessRate = computed(() => {
  const tests = props.tests.filter((t) => t.success_rate !== undefined && t.success_rate !== null)
  if (!tests.length) return 0
  const sum = tests.reduce((acc, t) => acc + (t.success_rate || 0), 0)
  return Math.round(sum / tests.length)
})

const successRateColor = computed(() => {
  const rate = averageSuccessRate.value
  if (rate >= 80) return '#22C55E' // green-500
  if (rate >= 60) return '#F59E0B' // amber-500
  return '#EF4444' // red-500
})

// Usage stats
const totalExecutions = computed(() => {
  return props.tests.reduce((acc, t) => acc + (t.usage_count || 0), 0)
})

const mostUsedTest = computed(() => {
  if (!props.tests.length) return 'N/A'
  const sorted = [...props.tests].sort((a, b) => (b.usage_count || 0) - (a.usage_count || 0))
  return sorted[0]?.test_name || 'N/A'
})

const avgExecutionsPerTest = computed(() => {
  if (!props.tests.length) return 0
  return Math.round(totalExecutions.value / props.tests.length)
})

const underReviewCount = computed(() => {
  return props.tests.filter((t) => t.status === 'Under Review').length
})

function formatNumber(num) {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}
</script>
