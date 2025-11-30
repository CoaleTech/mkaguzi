<template>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 mb-6">
    <!-- Total Entities Card -->
    <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide">Total Entities</p>
          <p class="text-3xl font-bold text-blue-900 mt-1">{{ stats.total || 0 }}</p>
          <p class="text-xs text-blue-600 mt-1">Auditable universe</p>
        </div>
        <div class="p-3 bg-blue-500 rounded-xl shadow-sm">
          <BuildingIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Critical Risk Card -->
    <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-xl border border-red-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-red-700 uppercase tracking-wide">Critical Risk</p>
          <p class="text-3xl font-bold text-red-900 mt-1">{{ stats.criticalRisk || 0 }}</p>
          <p class="text-xs text-red-600 mt-1">High priority</p>
        </div>
        <div class="p-3 bg-red-500 rounded-xl shadow-sm">
          <AlertTriangleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- High Risk Card -->
    <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl border border-orange-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-orange-700 uppercase tracking-wide">High Risk</p>
          <p class="text-3xl font-bold text-orange-900 mt-1">{{ stats.highRisk || 0 }}</p>
          <p class="text-xs text-orange-600 mt-1">Medium priority</p>
        </div>
        <div class="p-3 bg-orange-500 rounded-xl shadow-sm">
          <AlertCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Due This Quarter Card -->
    <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-purple-700 uppercase tracking-wide">Due This Quarter</p>
          <p class="text-3xl font-bold text-purple-900 mt-1">{{ stats.dueThisQuarter || 0 }}</p>
          <p class="text-xs text-purple-600 mt-1">Upcoming audits</p>
        </div>
        <div class="p-3 bg-purple-500 rounded-xl shadow-sm">
          <CalendarIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Active Entities Card -->
    <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl border border-green-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-green-700 uppercase tracking-wide">Active</p>
          <p class="text-3xl font-bold text-green-900 mt-1">{{ stats.active || 0 }}</p>
          <p class="text-xs text-green-600 mt-1">In scope entities</p>
        </div>
        <div class="p-3 bg-green-500 rounded-xl shadow-sm">
          <CheckCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>
  </div>

  <!-- Distribution Charts -->
  <div v-if="showDetails" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
    <!-- Risk Distribution -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h3 class="text-sm font-semibold text-gray-900 mb-4">Risk Distribution</h3>
      <div class="space-y-3">
        <div v-for="risk in riskDistribution" :key="risk.label" class="flex items-center">
          <div class="w-20 text-sm text-gray-600">{{ risk.label }}</div>
          <div class="flex-1 mx-3">
            <div class="w-full bg-gray-100 rounded-full h-3">
              <div
                class="h-3 rounded-full transition-all duration-300"
                :class="risk.color"
                :style="{ width: `${risk.percentage}%` }"
              ></div>
            </div>
          </div>
          <div class="w-10 text-sm font-medium text-gray-900 text-right">{{ risk.count }}</div>
        </div>
      </div>
    </div>

    <!-- Entity Type Distribution -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h3 class="text-sm font-semibold text-gray-900 mb-4">Entity Types</h3>
      <div class="grid grid-cols-2 gap-3">
        <div v-for="type in typeDistribution" :key="type.label" class="text-center p-3 bg-gray-50 rounded-lg">
          <p class="text-lg font-bold text-blue-600">{{ type.count }}</p>
          <p class="text-xs text-gray-500 truncate">{{ type.label }}</p>
        </div>
      </div>
    </div>

    <!-- Control Environment -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h3 class="text-sm font-semibold text-gray-900 mb-4">Control Environment</h3>
      <div class="space-y-3">
        <div v-for="control in controlDistribution" :key="control.label" class="flex items-center justify-between">
          <span class="text-sm text-gray-600">{{ control.label }}</span>
          <div class="flex items-center gap-2">
            <div class="w-16 bg-gray-100 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all duration-300"
                :class="control.color"
                :style="{ width: `${control.percentage}%` }"
              ></div>
            </div>
            <span class="text-sm font-medium text-gray-900 w-8 text-right">{{ control.count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Audit Schedule Summary -->
  <div v-if="showDetails" class="bg-white rounded-xl border border-gray-200 p-5 mb-6">
    <h3 class="text-sm font-semibold text-gray-900 mb-4">Audit Schedule Summary</h3>
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div class="text-center p-4 bg-red-50 rounded-lg">
        <p class="text-2xl font-bold text-red-600">{{ stats.overdue || 0 }}</p>
        <p class="text-xs text-red-700">Overdue</p>
      </div>
      <div class="text-center p-4 bg-amber-50 rounded-lg">
        <p class="text-2xl font-bold text-amber-600">{{ stats.dueThisMonth || 0 }}</p>
        <p class="text-xs text-amber-700">Due This Month</p>
      </div>
      <div class="text-center p-4 bg-purple-50 rounded-lg">
        <p class="text-2xl font-bold text-purple-600">{{ stats.dueThisQuarter || 0 }}</p>
        <p class="text-xs text-purple-700">Due This Quarter</p>
      </div>
      <div class="text-center p-4 bg-blue-50 rounded-lg">
        <p class="text-2xl font-bold text-blue-600">{{ stats.mandatory || 0 }}</p>
        <p class="text-xs text-blue-700">Mandatory</p>
      </div>
      <div class="text-center p-4 bg-gray-50 rounded-lg">
        <p class="text-2xl font-bold text-gray-600">{{ stats.inactive || 0 }}</p>
        <p class="text-xs text-gray-700">Inactive</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
	AlertCircleIcon,
	AlertTriangleIcon,
	BuildingIcon,
	CalendarIcon,
	CheckCircleIcon,
} from "lucide-vue-next"
import { computed } from "vue"

// Props
const props = defineProps({
	stats: {
		type: Object,
		default: () => ({
			total: 0,
			criticalRisk: 0,
			highRisk: 0,
			mediumRisk: 0,
			lowRisk: 0,
			active: 0,
			inactive: 0,
			dueThisQuarter: 0,
			dueThisMonth: 0,
			overdue: 0,
			mandatory: 0,
			byType: {},
			byControlEnvironment: {},
		}),
	},
	showDetails: {
		type: Boolean,
		default: true,
	},
})

// Computed
const riskDistribution = computed(() => {
	const total = props.stats.total || 1
	return [
		{
			label: "Critical",
			count: props.stats.criticalRisk || 0,
			percentage: ((props.stats.criticalRisk || 0) / total) * 100,
			color: "bg-red-500",
		},
		{
			label: "High",
			count: props.stats.highRisk || 0,
			percentage: ((props.stats.highRisk || 0) / total) * 100,
			color: "bg-orange-500",
		},
		{
			label: "Medium",
			count: props.stats.mediumRisk || 0,
			percentage: ((props.stats.mediumRisk || 0) / total) * 100,
			color: "bg-amber-500",
		},
		{
			label: "Low",
			count: props.stats.lowRisk || 0,
			percentage: ((props.stats.lowRisk || 0) / total) * 100,
			color: "bg-green-500",
		},
	]
})

const typeDistribution = computed(() => {
	const types = props.stats.byType || {}
	return Object.entries(types).map(([label, count]) => ({
		label,
		count,
	}))
})

const controlDistribution = computed(() => {
	const controls = props.stats.byControlEnvironment || {}
	const total =
		Object.values(controls).reduce((sum, count) => sum + count, 0) || 1

	const colors = {
		Strong: "bg-green-500",
		Adequate: "bg-blue-500",
		Weak: "bg-orange-500",
		"Not Assessed": "bg-gray-400",
	}

	return Object.entries(controls).map(([label, count]) => ({
		label,
		count,
		percentage: (count / total) * 100,
		color: colors[label] || "bg-gray-400",
	}))
})
</script>
