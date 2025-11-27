<template>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-6 gap-4">
    <!-- Total Working Papers Card -->
    <div class="bg-purple-50 rounded-xl border border-purple-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-purple-700 uppercase tracking-wide">Total Papers</p>
          <p class="text-3xl font-bold text-purple-900 mt-1">{{ totalWorkingPapers }}</p>
          <p class="text-xs text-purple-600 mt-1">Active documentation</p>
        </div>
        <div class="p-3 bg-purple-500 rounded-xl shadow-sm">
          <FileTextIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Review Complete Card -->
    <div class="bg-green-50 rounded-xl border border-green-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-green-700 uppercase tracking-wide">Review Complete</p>
          <p class="text-3xl font-bold text-green-900 mt-1">{{ reviewCompleteCount }}</p>
          <p class="text-xs text-green-600 mt-1">{{ ((reviewCompleteCount / Math.max(totalWorkingPapers, 1)) * 100).toFixed(0) }}% of total</p>
        </div>
        <div class="p-3 bg-green-500 rounded-xl shadow-sm">
          <CheckCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Under Review Card -->
    <div class="bg-yellow-50 rounded-xl border border-yellow-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-yellow-700 uppercase tracking-wide">Under Review</p>
          <p class="text-3xl font-bold text-yellow-900 mt-1">{{ underReviewCount }}</p>
          <p class="text-xs text-yellow-600 mt-1">Pending approval</p>
        </div>
        <div class="p-3 bg-yellow-500 rounded-xl shadow-sm">
          <ClockIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Revision Required Card -->
    <div class="bg-red-50 rounded-xl border border-red-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-red-700 uppercase tracking-wide">Revision Required</p>
          <p class="text-3xl font-bold text-red-900 mt-1">{{ revisionRequiredCount }}</p>
          <p class="text-xs text-red-600 mt-1">Needs updates</p>
        </div>
        <div class="p-3 bg-red-500 rounded-xl shadow-sm">
          <AlertTriangleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Average Review Time Card -->
    <div class="bg-blue-50 rounded-xl border border-blue-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide">Avg. Review Time</p>
          <p class="text-3xl font-bold text-blue-900 mt-1">{{ averageReviewTime }} days</p>
          <div class="w-full bg-blue-200 rounded-full h-2 mt-2">
            <div
              class="bg-blue-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${Math.min((averageReviewTime / 14) * 100, 100)}%` }"
            ></div>
          </div>
        </div>
        <div class="p-3 bg-blue-500 rounded-xl shadow-sm">
          <BarChartIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Quality Score Card -->
    <div class="bg-indigo-50 rounded-xl border border-indigo-200 p-6 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-indigo-700 uppercase tracking-wide">Quality Score</p>
          <p class="text-3xl font-bold text-indigo-900 mt-1">{{ averageQualityScore }}%</p>
          <p class="text-xs text-indigo-600 mt-1">Scored papers</p>
        </div>
        <div class="p-3 bg-indigo-500 rounded-xl shadow-sm">
          <BarChart3Icon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  AlertTriangleIcon,
  BarChart3Icon,
  BarChartIcon,
  CheckCircleIcon,
  ClockIcon,
  FileTextIcon,
} from "lucide-vue-next"
import { computed } from "vue"

// Props
const props = defineProps({
  workingPapers: {
    type: Array,
    default: () => [],
  },
})

// Computed properties
const totalWorkingPapers = computed(() => props.workingPapers.length)

const reviewCompleteCount = computed(
  () =>
    props.workingPapers.filter(
      (paper) => paper.review_status === "Review Complete",
    ).length,
)

const underReviewCount = computed(
  () =>
    props.workingPapers.filter(
      (paper) => paper.review_status === "Under Review",
    ).length,
)

const revisionRequiredCount = computed(
  () =>
    props.workingPapers.filter(
      (paper) => paper.review_status === "Revision Required",
    ).length,
)

const averageReviewTime = computed(() => {
  const reviewedPapers = props.workingPapers.filter(
    (paper) => paper.review_date && paper.preparation_date,
  )
  if (reviewedPapers.length === 0) return 0

  const totalDays = reviewedPapers.reduce((sum, paper) => {
    const prepDate = new Date(paper.preparation_date)
    const reviewDate = new Date(paper.review_date)
    const diffTime = Math.abs(reviewDate - prepDate)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return sum + diffDays
  }, 0)

  return Math.round(totalDays / reviewedPapers.length)
})

const averageQualityScore = computed(() => {
  const scoredPapers = props.workingPapers.filter(
    (paper) => paper.quality_score,
  )
  if (scoredPapers.length === 0) return 0

  const totalScore = scoredPapers.reduce(
    (sum, paper) => sum + (paper.quality_score || 0),
    0,
  )
  return Math.round(totalScore / scoredPapers.length)
})
</script>