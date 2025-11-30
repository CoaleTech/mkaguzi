<template>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
    <!-- Total Scheduled Card -->
    <div class="bg-blue-50 rounded-xl border border-blue-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide">Total Scheduled</p>
          <p class="text-3xl font-bold text-blue-900 mt-1">{{ stats.totalScheduled }}</p>
          <p class="text-xs text-blue-600 mt-1">{{ ((stats.totalScheduled / Math.max(stats.totalCapacity, 1)) * 100).toFixed(0) }}% of capacity</p>
        </div>
        <div class="p-3 bg-blue-500 rounded-xl shadow-sm">
          <CalendarIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- In Progress Card -->
    <div class="bg-yellow-50 rounded-xl border border-yellow-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-yellow-700 uppercase tracking-wide">In Progress</p>
          <p class="text-3xl font-bold text-yellow-900 mt-1">{{ stats.inProgress }}</p>
          <p class="text-xs text-yellow-600 mt-1">Active audits</p>
        </div>
        <div class="p-3 bg-yellow-500 rounded-xl shadow-sm">
          <PlayIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Upcoming Card -->
    <div class="bg-green-50 rounded-xl border border-green-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-green-700 uppercase tracking-wide">Upcoming</p>
          <p class="text-3xl font-bold text-green-900 mt-1">{{ stats.upcoming }}</p>
          <p class="text-xs text-green-600 mt-1">Next 30 days</p>
        </div>
        <div class="p-3 bg-green-500 rounded-xl shadow-sm">
          <ClockIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Average Progress Card -->
    <div class="bg-purple-50 rounded-xl border border-purple-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-purple-700 uppercase tracking-wide">Avg. Progress</p>
          <p class="text-3xl font-bold text-purple-900 mt-1">{{ stats.averageProgress }}%</p>
          <div class="w-full bg-purple-200 rounded-full h-2 mt-2">
            <div
              class="bg-purple-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${Math.min(stats.averageProgress, 100)}%` }"
            ></div>
          </div>
        </div>
        <div class="p-3 bg-purple-500 rounded-xl shadow-sm">
          <BarChartIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Overdue Card -->
    <div class="bg-red-50 rounded-xl border border-red-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-red-700 uppercase tracking-wide">Overdue</p>
          <p class="text-3xl font-bold text-red-900 mt-1">{{ stats.overdue }}</p>
          <p class="text-xs text-red-600 mt-1">Need attention</p>
        </div>
        <div class="p-3 bg-red-500 rounded-xl shadow-sm">
          <AlertTriangleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
	AlertTriangleIcon,
	BarChartIcon,
	CalendarIcon,
	ClockIcon,
	PlayIcon,
} from "lucide-vue-next"

// Props
defineProps({
	stats: {
		type: Object,
		required: true,
		validator: (stats) => {
			return (
				typeof stats === "object" &&
				typeof stats.totalScheduled === "number" &&
				typeof stats.inProgress === "number" &&
				typeof stats.upcoming === "number" &&
				typeof stats.averageProgress === "number" &&
				typeof stats.overdue === "number" &&
				typeof stats.totalCapacity === "number"
			)
		},
	},
})
</script>