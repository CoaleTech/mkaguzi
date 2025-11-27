<template>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-6 gap-4">
    <!-- Total Engagements Card -->
    <div class="bg-green-50 rounded-xl border border-green-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-green-700 uppercase tracking-wide">Total Engagements</p>
          <p class="text-3xl font-bold text-green-900 mt-1">{{ totalEngagements }}</p>
          <p class="text-xs text-green-600 mt-1">Active projects</p>
        </div>
        <div class="p-3 bg-green-500 rounded-xl shadow-sm">
          <BriefcaseIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- In Progress Card -->
    <div class="bg-blue-50 rounded-xl border border-blue-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide">In Progress</p>
          <p class="text-3xl font-bold text-blue-900 mt-1">{{ inProgressCount }}</p>
          <p class="text-xs text-blue-600 mt-1">{{ ((inProgressCount / Math.max(totalEngagements, 1)) * 100).toFixed(0) }}% of total</p>
        </div>
        <div class="p-3 bg-blue-500 rounded-xl shadow-sm">
          <PlayCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Reporting Card -->
    <div class="bg-purple-50 rounded-xl border border-purple-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-purple-700 uppercase tracking-wide">Reporting</p>
          <p class="text-3xl font-bold text-purple-900 mt-1">{{ reportingCount }}</p>
          <p class="text-xs text-purple-600 mt-1">Final reports</p>
        </div>
        <div class="p-3 bg-purple-500 rounded-xl shadow-sm">
          <FileTextIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Average Progress Card -->
    <div class="bg-yellow-50 rounded-xl border border-yellow-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-yellow-700 uppercase tracking-wide">Avg. Progress</p>
          <p class="text-3xl font-bold text-yellow-900 mt-1">{{ averageProgress }}%</p>
          <div class="w-full bg-yellow-200 rounded-full h-2 mt-2">
            <div
              class="bg-yellow-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${averageProgress}%` }"
            ></div>
          </div>
        </div>
        <div class="p-3 bg-yellow-500 rounded-xl shadow-sm">
          <BarChartIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Quality Review Card -->
    <div class="bg-indigo-50 rounded-xl border border-indigo-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-indigo-700 uppercase tracking-wide">Quality Review</p>
          <p class="text-3xl font-bold text-indigo-900 mt-1">{{ qualityReviewCount }}</p>
          <p class="text-xs text-indigo-600 mt-1">Under review</p>
        </div>
        <div class="p-3 bg-indigo-500 rounded-xl shadow-sm">
          <CheckCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Completed Card -->
    <div class="bg-emerald-50 rounded-xl border border-emerald-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-emerald-700 uppercase tracking-wide">Completed</p>
          <p class="text-3xl font-bold text-emerald-900 mt-1">{{ completedCount }}</p>
          <p class="text-xs text-emerald-600 mt-1">{{ ((completedCount / Math.max(totalEngagements, 1)) * 100).toFixed(0) }}% completion rate</p>
        </div>
        <div class="p-3 bg-emerald-500 rounded-xl shadow-sm">
          <CheckCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  BarChartIcon,
  BriefcaseIcon,
  CheckCircleIcon,
  FileTextIcon,
  PlayCircleIcon,
} from "lucide-vue-next"
import { computed } from "vue"

// Props
const props = defineProps({
  engagements: {
    type: Array,
    default: () => [],
  },
})

// Computed properties
const totalEngagements = computed(() => props.engagements.length)

const inProgressCount = computed(() =>
  props.engagements.filter((engagement) => engagement.status === "In Progress").length
)

const reportingCount = computed(() =>
  props.engagements.filter((engagement) => engagement.status === "Reporting").length
)

const qualityReviewCount = computed(() =>
  props.engagements.filter((engagement) => engagement.status === "Quality Review").length
)

const completedCount = computed(() =>
  props.engagements.filter((engagement) => engagement.status === "Completed").length
)

const averageProgress = computed(() => {
  if (props.engagements.length === 0) return 0
  const totalProgress = props.engagements.reduce(
    (sum, engagement) => sum + (engagement.progress_percentage || 0),
    0
  )
  return Math.round(totalProgress / props.engagements.length)
})
</script>