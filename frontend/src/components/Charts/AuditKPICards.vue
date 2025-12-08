<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <!-- Total Findings -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-gray-600">Total Findings</p>
          <p class="text-3xl font-bold text-gray-900">{{ totalFindings }}</p>
          <p class="text-sm text-gray-500 mt-1">
            <span :class="findingsChange >= 0 ? 'text-red-600' : 'text-green-600'">
              {{ findingsChange >= 0 ? '+' : '' }}{{ findingsChange }}% from last month
            </span>
          </p>
        </div>
        <div class="p-3 bg-blue-100 rounded-full">
          <FileTextIcon class="h-6 w-6 text-blue-600" />
        </div>
      </div>
    </div>

    <!-- Open Findings -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-gray-600">Open Findings</p>
          <p class="text-3xl font-bold text-gray-900">{{ openFindings }}</p>
          <p class="text-sm text-gray-500 mt-1">
            {{ ((openFindings / totalFindings) * 100).toFixed(1) }}% of total
          </p>
        </div>
        <div class="p-3 bg-yellow-100 rounded-full">
          <AlertTriangleIcon class="h-6 w-6 text-yellow-600" />
        </div>
      </div>
    </div>

    <!-- Critical Findings -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-gray-600">Critical Findings</p>
          <p class="text-3xl font-bold text-gray-900">{{ criticalFindings }}</p>
          <p class="text-sm text-gray-500 mt-1">
            Requires immediate attention
          </p>
        </div>
        <div class="p-3 bg-red-100 rounded-full">
          <AlertCircleIcon class="h-6 w-6 text-red-600" />
        </div>
      </div>
    </div>

    <!-- Completed Actions -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-gray-600">Completed Actions</p>
          <p class="text-3xl font-bold text-gray-900">{{ completedActions }}</p>
          <p class="text-sm text-gray-500 mt-1">
            {{ actionCompletionRate.toFixed(1) }}% completion rate
          </p>
        </div>
        <div class="p-3 bg-green-100 rounded-full">
          <CheckCircleIcon class="h-6 w-6 text-green-600" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
	AlertCircleIcon,
	AlertTriangleIcon,
	CheckCircleIcon,
	FileTextIcon,
} from "lucide-vue-next"
import { computed } from "vue"

// Props
const props = defineProps({
	findings: {
		type: Array,
		default: () => [],
	},
	correctiveActions: {
		type: Array,
		default: () => [],
	},
	previousFindings: {
		type: Array,
		default: () => [],
	},
})

// Computed
const totalFindings = computed(() => props.findings.length)

const openFindings = computed(
	() => props.findings.filter((f) => f.status === "Open" || !f.status).length,
)

const criticalFindings = computed(
	() => props.findings.filter((f) => f.risk_level === "Critical").length,
)

const completedActions = computed(
	() => props.correctiveActions.filter((a) => a.status === "Completed").length,
)

const actionCompletionRate = computed(() => {
	const total = props.correctiveActions.length
	return total > 0 ? (completedActions.value / total) * 100 : 0
})

const findingsChange = computed(() => {
	const current = totalFindings.value
	const previous = props.previousFindings.length
	if (previous === 0) return 0
	return ((current - previous) / previous) * 100
})
</script>