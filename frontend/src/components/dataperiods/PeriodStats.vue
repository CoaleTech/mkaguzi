<template>
  <div class="space-y-4">
    <!-- Stats Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
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
      <!-- Period Type Distribution -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">By Period Type</h3>
        <div class="space-y-3">
          <div
            v-for="type in periodTypeDistribution"
            :key="type.name"
            class="flex items-center gap-3 cursor-pointer hover:bg-gray-50 p-1 rounded"
            @click="$emit('filter', 'period_type', type.name)"
          >
            <div class="w-3 h-3 rounded-full" :class="type.dotColor"></div>
            <div class="flex-1 text-sm text-gray-600">{{ type.name }}</div>
            <div class="text-sm font-medium text-gray-700">{{ type.count }}</div>
          </div>
        </div>
      </div>

      <!-- Data Quality Overview -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Data Quality Overview</h3>
        <div class="flex items-center justify-center">
          <div class="relative h-32 w-32">
            <svg viewBox="0 0 36 36" class="transform -rotate-90">
              <circle
                cx="18" cy="18" r="15.9"
                fill="none"
                stroke="#E5E7EB"
                stroke-width="3"
              />
              <circle
                cx="18" cy="18" r="15.9"
                fill="none"
                :stroke="avgQualityColor"
                stroke-width="3"
                :stroke-dasharray="`${avgDataQuality} ${100 - avgDataQuality}`"
                stroke-linecap="round"
              />
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <div class="text-2xl font-bold text-gray-900">{{ avgDataQuality }}%</div>
              <div class="text-xs text-gray-500">Avg Quality</div>
            </div>
          </div>
        </div>
        <div class="flex justify-center gap-4 mt-4 text-xs">
          <div class="flex items-center gap-1">
            <div class="w-2 h-2 rounded-full bg-green-500"></div>
            <span class="text-gray-500">Complete: {{ avgCompleteness }}%</span>
          </div>
        </div>
      </div>

      <!-- Reconciliation Status -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Reconciliation Status</h3>
        <div class="space-y-3">
          <div
            v-for="status in reconciliationDistribution"
            :key="status.name"
            class="flex items-center gap-3 cursor-pointer hover:bg-gray-50 p-1 rounded"
            @click="$emit('filter', 'reconciliation_status', status.name)"
          >
            <component :is="status.icon" class="h-4 w-4" :class="status.iconColor" />
            <div class="flex-1 text-sm text-gray-600">{{ status.name }}</div>
            <Badge :theme="status.theme">{{ status.count }}</Badge>
          </div>
        </div>
      </div>
    </div>

    <!-- Timeline View -->
    <div class="bg-white rounded-xl border p-4">
      <h3 class="text-sm font-medium text-gray-700 mb-4">Period Timeline</h3>
      <div class="flex items-center gap-2 overflow-x-auto pb-2">
        <div
          v-for="period in sortedPeriods"
          :key="period.name"
          class="flex-shrink-0 p-3 rounded-lg border cursor-pointer hover:shadow-sm transition-shadow min-w-[180px]"
          :class="getStatusBgClass(period.status)"
          @click="$emit('select', period)"
        >
          <div class="flex items-center justify-between mb-2">
            <Badge :theme="getStatusTheme(period.status)">{{ period.status }}</Badge>
            <span class="text-xs text-gray-500">{{ period.period_type }}</span>
          </div>
          <div class="text-sm font-medium text-gray-800">{{ period.period_name }}</div>
          <div class="text-xs text-gray-500 mt-1">
            {{ formatDate(period.start_date) }} - {{ formatDate(period.end_date) }}
          </div>
          <div class="mt-2 flex items-center gap-2">
            <div class="flex-1 bg-gray-200 rounded-full h-1.5">
              <div
                class="h-1.5 rounded-full bg-blue-500"
                :style="{ width: `${period.data_completeness_score || 0}%` }"
              ></div>
            </div>
            <span class="text-xs text-gray-500">{{ period.data_completeness_score || 0 }}%</span>
          </div>
        </div>
        <div v-if="!sortedPeriods.length" class="text-sm text-gray-500 py-4">
          No periods defined
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge } from "frappe-ui"
import {
	AlertTriangle,
	Archive,
	Calendar,
	CalendarCheck,
	CheckCircle,
	Clock,
	Lock,
	Unlock,
	XCircle,
} from "lucide-vue-next"
import { computed } from "vue"

const props = defineProps({
	periods: { type: Array, default: () => [] },
	activeFilter: { type: String, default: "" },
})

defineEmits(["filter", "select"])

// Stats cards
const statsCards = computed(() => {
	const periods = props.periods
	const total = periods.length
	const open = periods.filter((p) => p.status === "Open").length
	const locked = periods.filter((p) => p.status === "Locked").length
	const closed = periods.filter((p) => p.status === "Closed").length
	const archived = periods.filter((p) => p.status === "Archived").length

	return [
		{
			label: "Total Periods",
			value: total,
			icon: Calendar,
			bgColor: "bg-blue-100",
			iconColor: "text-blue-600",
			filterKey: null,
			filterValue: null,
		},
		{
			label: "Open",
			value: open,
			icon: Unlock,
			bgColor: "bg-green-100",
			iconColor: "text-green-600",
			filterKey: "status",
			filterValue: "Open",
			active: props.activeFilter === "Open",
		},
		{
			label: "Locked",
			value: locked,
			icon: Lock,
			bgColor: "bg-yellow-100",
			iconColor: "text-yellow-600",
			filterKey: "status",
			filterValue: "Locked",
			active: props.activeFilter === "Locked",
		},
		{
			label: "Closed",
			value: closed,
			icon: CalendarCheck,
			bgColor: "bg-gray-100",
			iconColor: "text-gray-600",
			filterKey: "status",
			filterValue: "Closed",
			active: props.activeFilter === "Closed",
		},
		{
			label: "Archived",
			value: archived,
			icon: Archive,
			bgColor: "bg-purple-100",
			iconColor: "text-purple-600",
			filterKey: "status",
			filterValue: "Archived",
			active: props.activeFilter === "Archived",
		},
	]
})

// Period type distribution
const periodTypeDistribution = computed(() => {
	const periods = props.periods
	const types = ["Month", "Quarter", "Half-Year", "Year", "Custom"]
	const colors = {
		Month: "bg-blue-500",
		Quarter: "bg-green-500",
		"Half-Year": "bg-purple-500",
		Year: "bg-orange-500",
		Custom: "bg-gray-500",
	}

	return types
		.map((name) => ({
			name,
			count: periods.filter((p) => p.period_type === name).length,
			dotColor: colors[name] || "bg-gray-400",
		}))
		.filter((t) => t.count > 0)
})

// Data quality averages
const avgDataQuality = computed(() => {
	const periods = props.periods.filter((p) => p.data_quality_score)
	if (!periods.length) return 0
	return Math.round(
		periods.reduce((sum, p) => sum + p.data_quality_score, 0) / periods.length,
	)
})

const avgCompleteness = computed(() => {
	const periods = props.periods.filter((p) => p.data_completeness_score)
	if (!periods.length) return 0
	return Math.round(
		periods.reduce((sum, p) => sum + p.data_completeness_score, 0) /
			periods.length,
	)
})

const avgQualityColor = computed(() => {
	const score = avgDataQuality.value
	if (score >= 80) return "#22C55E"
	if (score >= 60) return "#F59E0B"
	return "#EF4444"
})

// Reconciliation distribution
const reconciliationDistribution = computed(() => {
	const periods = props.periods

	return [
		{
			name: "Completed",
			count: periods.filter((p) => p.reconciliation_status === "Completed")
				.length,
			icon: CheckCircle,
			iconColor: "text-green-600",
			theme: "green",
		},
		{
			name: "In Progress",
			count: periods.filter((p) => p.reconciliation_status === "In Progress")
				.length,
			icon: Clock,
			iconColor: "text-blue-600",
			theme: "blue",
		},
		{
			name: "Not Started",
			count: periods.filter((p) => p.reconciliation_status === "Not Started")
				.length,
			icon: AlertTriangle,
			iconColor: "text-yellow-600",
			theme: "orange",
		},
		{
			name: "Issues Found",
			count: periods.filter((p) => p.reconciliation_status === "Issues Found")
				.length,
			icon: XCircle,
			iconColor: "text-red-600",
			theme: "red",
		},
	].filter((s) => s.count > 0)
})

// Sorted periods for timeline
const sortedPeriods = computed(() => {
	return [...props.periods]
		.sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
		.slice(0, 8)
})

// Helper functions
function formatDate(date) {
	if (!date) return ""
	return new Date(date).toLocaleDateString("en-US", {
		month: "short",
		year: "numeric",
	})
}

function getStatusTheme(status) {
	const themes = {
		Open: "green",
		Locked: "orange",
		Closed: "gray",
		Archived: "blue",
	}
	return themes[status] || "gray"
}

function getStatusBgClass(status) {
	const classes = {
		Open: "bg-green-50 border-green-200",
		Locked: "bg-yellow-50 border-yellow-200",
		Closed: "bg-gray-50 border-gray-200",
		Archived: "bg-purple-50 border-purple-200",
	}
	return classes[status] || "bg-gray-50 border-gray-200"
}
</script>
