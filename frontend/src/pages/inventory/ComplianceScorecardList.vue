<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Compliance Scorecards</h1>
        <p class="text-gray-600">Track audit compliance metrics and performance grades</p>
      </div>
      <div class="flex gap-2">
        <Button @click="refreshData" :loading="loading" variant="outline" size="sm">
          <RefreshCw class="w-4 h-4" />
        </Button>
        <Button @click="recalculateAll" :loading="recalculating" variant="outline" size="sm">
          <Calculator class="w-4 h-4 mr-2" />
          Recalculate All
        </Button>
        <Button @click="newScorecard" variant="solid" size="sm">
          <Plus class="w-4 h-4 mr-2" />
          New Scorecard
        </Button>
      </div>
    </div>

    <!-- Overview Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Total Scorecards</p>
        <p class="text-2xl font-bold">{{ scorecards.length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Average Score</p>
        <p class="text-2xl font-bold" :class="getScoreTextColor(avgScore)">{{ avgScore }}%</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Grade Distribution</p>
        <div class="flex items-center gap-2 mt-1">
          <span v-for="(count, grade) in gradeDistribution" :key="grade" 
                class="text-sm px-2 py-1 rounded-full" 
                :class="getGradeBadgeColor(grade)">
            {{ grade }}: {{ count }}
          </span>
        </div>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Last Updated</p>
        <p class="text-lg font-medium">{{ lastUpdated }}</p>
      </div>
    </div>

    <!-- Scorecards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="sc in scorecards" 
        :key="sc.name"
        class="bg-white rounded-lg border shadow-sm overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
        @click="viewScorecard(sc.name)"
      >
        <!-- Header -->
        <div class="px-4 py-3 border-b bg-gray-50 flex items-center justify-between">
          <div>
            <h4 class="font-medium text-gray-900">{{ sc.audit_plan_title }}</h4>
            <p class="text-sm text-gray-500">{{ sc.scorecard_id }}</p>
          </div>
          <div class="text-right">
            <p class="text-3xl font-bold" :class="getGradeTextColor(sc.grade)">{{ sc.grade }}</p>
          </div>
        </div>

        <!-- Main Score -->
        <div class="p-4">
          <div class="text-center mb-4">
            <p class="text-sm text-gray-500">Overall Compliance Score</p>
            <p class="text-4xl font-bold" :class="getScoreTextColor(sc.overall_compliance_score)">
              {{ Math.round(sc.overall_compliance_score || 0) }}%
            </p>
            <div class="w-full bg-gray-200 rounded-full h-3 mt-2">
              <div 
                class="h-full rounded-full transition-all duration-500"
                :class="getScoreBarColor(sc.overall_compliance_score)"
                :style="{ width: `${sc.overall_compliance_score || 0}%` }"
              ></div>
            </div>
          </div>

          <!-- Metric Breakdown -->
          <div class="space-y-3">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Completion Rate</span>
              <span class="font-medium">{{ Math.round(sc.completion_rate || 0) }}%</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Accuracy Score</span>
              <span class="font-medium">{{ Math.round(sc.accuracy_score || 0) }}%</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Timeliness Score</span>
              <span class="font-medium">{{ Math.round(sc.timeliness_score || 0) }}%</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">SLA Compliance</span>
              <span class="font-medium">{{ Math.round(sc.sla_compliance_rate || 0) }}%</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Issue Resolution</span>
              <span class="font-medium">{{ Math.round(sc.issue_resolution_rate || 0) }}%</span>
            </div>
          </div>

          <!-- Summary Stats -->
          <div class="mt-4 pt-4 border-t grid grid-cols-3 gap-2 text-center text-sm">
            <div>
              <p class="text-gray-500">Sessions</p>
              <p class="font-medium">{{ sc.completed_sessions || 0 }}/{{ sc.total_sessions || 0 }}</p>
            </div>
            <div>
              <p class="text-gray-500">Cases</p>
              <p class="font-medium">{{ sc.resolved_variance_cases || 0 }}/{{ sc.total_variance_cases || 0 }}</p>
            </div>
            <div>
              <p class="text-gray-500">Issues</p>
              <p class="font-medium">{{ sc.resolved_issues || 0 }}/{{ sc.total_issues || 0 }}</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-4 py-2 bg-gray-50 border-t flex items-center justify-between text-sm text-gray-500">
          <span>Last calculated: {{ formatDate(sc.calculation_date) }}</span>
          <Button variant="ghost" size="sm" @click.stop="recalculateScorecard(sc.audit_plan)">
            <RefreshCw class="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="scorecards.length === 0 && !loading" class="bg-white rounded-lg border p-12 text-center text-gray-500">
      <BarChart2 class="w-12 h-12 mx-auto mb-3 text-gray-300" />
      <p>No scorecards available</p>
      <p class="text-sm mt-1">Scorecards are created automatically when audit plans are set up</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge } from 'frappe-ui'
import { RefreshCw, Calculator, BarChart2, Plus } from 'lucide-vue-next'
import { useInventoryAuditStore } from '@/stores/useInventoryAuditStore'

const router = useRouter()
const store = useInventoryAuditStore()

const loading = ref(false)
const recalculating = ref(false)

const scorecards = computed(() => store.scorecards)

const avgScore = computed(() => {
  if (scorecards.value.length === 0) return 0
  return Math.round(
    scorecards.value.reduce((sum, sc) => sum + (sc.overall_compliance_score || 0), 0) / scorecards.value.length
  )
})

const gradeDistribution = computed(() => {
  return scorecards.value.reduce((acc, sc) => {
    const grade = sc.grade || 'N/A'
    acc[grade] = (acc[grade] || 0) + 1
    return acc
  }, {})
})

const lastUpdated = computed(() => {
  if (scorecards.value.length === 0) return '-'
  const latest = scorecards.value.reduce((latest, sc) => {
    const date = new Date(sc.calculation_date || 0)
    return date > latest ? date : latest
  }, new Date(0))
  return formatDate(latest.toISOString())
})

const metricDetails = [
  { key: 'completion_rate', label: 'Completion Rate', weight: 20 },
  { key: 'accuracy_score', label: 'Accuracy Score', weight: 25 },
  { key: 'timeliness_score', label: 'Timeliness Score', weight: 15 },
  { key: 'sla_compliance_rate', label: 'SLA Compliance', weight: 20 },
  { key: 'issue_resolution_rate', label: 'Issue Resolution', weight: 20 }
]

onMounted(async () => {
  await refreshData()
})

async function refreshData() {
  loading.value = true
  try {
    await store.loadScorecards()
  } finally {
    loading.value = false
  }
}

async function recalculateAll() {
  recalculating.value = true
  try {
    for (const sc of scorecards.value) {
      await store.recalculateScorecard(sc.audit_plan)
    }
  } finally {
    recalculating.value = false
  }
}

async function recalculateScorecard(planId) {
  await store.recalculateScorecard(planId)
}

async function viewScorecard(name) {
  router.push({ name: 'ComplianceScorecardDetail', params: { id: name } })
}

function newScorecard() {
  router.push({ name: 'NewComplianceScorecard' })
}

function getScoreTextColor(score) {
  if (score >= 90) return 'text-green-600'
  if (score >= 70) return 'text-blue-600'
  if (score >= 50) return 'text-yellow-600'
  return 'text-red-600'
}

function getScoreBarColor(score) {
  if (score >= 90) return 'bg-green-500'
  if (score >= 70) return 'bg-blue-500'
  if (score >= 50) return 'bg-yellow-500'
  return 'bg-red-500'
}

function getGradeTextColor(grade) {
  const colors = {
    'A': 'text-green-600',
    'B': 'text-blue-600',
    'C': 'text-yellow-600',
    'D': 'text-orange-600',
    'F': 'text-red-600'
  }
  return colors[grade] || 'text-gray-600'
}

function getGradeBadgeColor(grade) {
  const colors = {
    'A': 'bg-green-100 text-green-700',
    'B': 'bg-blue-100 text-blue-700',
    'C': 'bg-yellow-100 text-yellow-700',
    'D': 'bg-orange-100 text-orange-700',
    'F': 'bg-red-100 text-red-700'
  }
  return colors[grade] || 'bg-gray-100 text-gray-700'
}

function getGradeVariant(grade) {
  const variants = { 'A': 'green', 'B': 'blue', 'C': 'yellow', 'D': 'orange', 'F': 'red' }
  return variants[grade] || 'gray'
}

function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-US', { 
    month: 'short', day: 'numeric', year: 'numeric' 
  })
}
</script>
