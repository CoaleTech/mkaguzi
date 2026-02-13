<template>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
    <!-- Total Assessments Card -->
    <div class="bg-blue-50 rounded-xl border border-blue-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide">Total Assessments</p>
          <p class="text-3xl font-bold text-blue-900 mt-1">{{ stats.total }}</p>
          <p class="text-xs text-blue-600 mt-1">Active assessments</p>
        </div>
        <div class="p-3 bg-blue-500 rounded-xl shadow-sm">
          <FileTextIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Critical Risks Card -->
    <div class="bg-red-50 rounded-xl border border-red-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-red-700 uppercase tracking-wide">Critical Risks</p>
          <p class="text-3xl font-bold text-red-900 mt-1">{{ stats.criticalRisks }}</p>
          <p class="text-xs text-red-600 mt-1">High priority items</p>
        </div>
        <div class="p-3 bg-red-500 rounded-xl shadow-sm">
          <AlertTriangleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- High Risks Card -->
    <div class="bg-orange-50 rounded-xl border border-orange-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-orange-700 uppercase tracking-wide">High Risks</p>
          <p class="text-3xl font-bold text-orange-900 mt-1">{{ stats.highRisks }}</p>
          <p class="text-xs text-orange-600 mt-1">Medium priority items</p>
        </div>
        <div class="p-3 bg-orange-500 rounded-xl shadow-sm">
          <AlertCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Approved Assessments Card -->
    <div class="bg-green-50 rounded-xl border border-green-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-green-700 uppercase tracking-wide">Approved</p>
          <p class="text-3xl font-bold text-green-900 mt-1">{{ stats.approved }}</p>
          <p class="text-xs text-green-600 mt-1">Completed assessments</p>
        </div>
        <div class="p-3 bg-green-500 rounded-xl shadow-sm">
          <CheckCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Average Risk Score Card -->
    <div class="bg-gray-50 rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-gray-700 uppercase tracking-wide">Avg Risk Score</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.averageRiskScore }}</p>
          <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div
              class="bg-gray-900 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${Math.min(stats.averageRiskScore, 25) * 4}%` }"
            ></div>
          </div>
        </div>
        <div class="p-3 bg-gray-900 rounded-xl shadow-sm">
          <BarChart3Icon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  AlertCircleIcon,
  AlertTriangleIcon,
  BarChart3Icon,
  CheckCircleIcon,
  FileTextIcon,
} from "lucide-vue-next"

defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({
      total: 0,
      criticalRisks: 0,
      highRisks: 0,
      approved: 0,
      averageRiskScore: 0,
    }),
  },
})
</script>
