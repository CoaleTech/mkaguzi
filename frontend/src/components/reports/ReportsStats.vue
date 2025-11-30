<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
    <!-- Audit Reports Card -->
    <div class="bg-white p-4 rounded-lg border shadow-sm">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Audit Reports</p>
          <p class="text-2xl font-bold">{{ activeAuditReports.length }}</p>
        </div>
        <FileText class="w-8 h-8 text-blue-500" />
      </div>
    </div>

    <!-- Board Reports Card -->
    <div class="bg-white p-4 rounded-lg border shadow-sm">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Board Reports</p>
          <p class="text-2xl font-bold">{{ activeBoardReports.length }}</p>
        </div>
        <Users class="w-8 h-8 text-green-500" />
      </div>
    </div>

    <!-- Active Dashboards Card -->
    <div class="bg-white p-4 rounded-lg border shadow-sm">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Active Dashboards</p>
          <p class="text-2xl font-bold">{{ activeDashboards.length }}</p>
        </div>
        <BarChart3 class="w-8 h-8 text-purple-500" />
      </div>
    </div>

    <!-- Avg Compliance Score Card -->
    <div class="bg-white p-4 rounded-lg border shadow-sm">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Avg Compliance Score</p>
          <p class="text-2xl font-bold" :class="getScoreColor(complianceScore)">
            {{ Math.round(complianceScore) }}%
          </p>
        </div>
        <TrendingUp class="w-8 h-8 text-orange-500" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { BarChart3, FileText, TrendingUp, Users } from "lucide-vue-next"
import { computed } from "vue"

// Props
const props = defineProps({
	activeAuditReports: {
		type: Array,
		default: () => [],
	},
	activeBoardReports: {
		type: Array,
		default: () => [],
	},
	activeDashboards: {
		type: Array,
		default: () => [],
	},
	complianceScore: {
		type: Number,
		default: 0,
	},
})

// Computed properties
const getScoreColor = (score) => {
	if (score >= 80) return "text-green-600"
	if (score >= 60) return "text-yellow-600"
	return "text-red-600"
}
</script>