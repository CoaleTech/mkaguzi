<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
    <!-- Total Dashboards Card -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-blue-100 rounded-lg">
          <BarChart3Icon class="h-6 w-6 text-blue-600" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-600">Total Dashboards</p>
          <p class="text-2xl font-bold text-gray-900">{{ totalDashboards }}</p>
        </div>
      </div>
    </div>

    <!-- Active Dashboards Card -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-green-100 rounded-lg">
          <CheckCircleIcon class="h-6 w-6 text-green-600" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-600">Active Dashboards</p>
          <p class="text-2xl font-bold text-gray-900">{{ activeDashboards }}</p>
        </div>
      </div>
    </div>

    <!-- Total Charts Card -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-gray-100 rounded-lg">
          <PieChartIcon class="h-6 w-6 text-gray-600" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-600">Total Charts</p>
          <p class="text-2xl font-bold text-gray-900">{{ totalCharts }}</p>
        </div>
      </div>
    </div>

    <!-- Data Sources Card -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-orange-100 rounded-lg">
          <DatabaseIcon class="h-6 w-6 text-orange-600" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-600">Data Sources</p>
          <p class="text-2xl font-bold text-gray-900">{{ totalDataSources }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  BarChart3Icon,
  CheckCircleIcon,
  DatabaseIcon,
  PieChartIcon,
} from "lucide-vue-next"
import { computed } from "vue"

// Props
const props = defineProps({
  dashboards: {
    type: Array,
    default: () => [],
  },
  dashboardCharts: {
    type: Array,
    default: () => [],
  },
  dashboardDataSources: {
    type: Array,
    default: () => [],
  },
})

// Computed properties
const totalDashboards = computed(() => props.dashboards.length)

const activeDashboards = computed(() =>
  props.dashboards.filter(dashboard => dashboard.is_active).length
)

const totalCharts = computed(() => props.dashboardCharts.length)

const totalDataSources = computed(() => props.dashboardDataSources.length)
</script>