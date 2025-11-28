<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Inventory Audit Dashboard</h1>
        <p class="text-gray-600">Overview of stock take audits, variance analysis, and compliance metrics</p>
      </div>
      <div class="flex gap-2">
        <Button @click="refreshData" :loading="loading" variant="outline" size="sm">
          <RefreshCw class="w-4 h-4" />
        </Button>
        <Button @click="navigateToPlans">
          <Plus class="w-4 h-4 mr-2" />
          New Audit Plan
        </Button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <!-- Plans Stats -->
      <div class="bg-white rounded-lg border p-4 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">Audit Plans</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.plans?.total || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <ClipboardList class="w-6 h-6 text-blue-600" />
          </div>
        </div>
        <div class="mt-2 flex items-center gap-4 text-sm">
          <span class="text-green-600">{{ stats.plans?.active || 0 }} active</span>
          <span class="text-gray-500">{{ stats.plans?.completed || 0 }} completed</span>
        </div>
      </div>

      <!-- Sessions Stats -->
      <div class="bg-white rounded-lg border p-4 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">Stock Take Sessions</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.sessions?.total || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <Package class="w-6 h-6 text-green-600" />
          </div>
        </div>
        <div class="mt-2 flex items-center gap-4 text-sm">
          <span class="text-yellow-600">{{ stats.sessions?.in_progress || 0 }} in progress</span>
        </div>
      </div>

      <!-- Variance Cases Stats -->
      <div class="bg-white rounded-lg border p-4 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">Variance Cases</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.variance_cases?.total || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
            <AlertTriangle class="w-6 h-6 text-orange-600" />
          </div>
        </div>
        <div class="mt-2 flex items-center gap-4 text-sm">
          <span class="text-orange-600">{{ stats.variance_cases?.open || 0 }} open</span>
          <span class="text-red-600">{{ stats.variance_cases?.sla_breached || 0 }} SLA breached</span>
        </div>
      </div>

      <!-- Compliance Score -->
      <div class="bg-white rounded-lg border p-4 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">Avg Compliance Score</p>
            <p class="text-2xl font-bold text-gray-900">{{ Math.round(stats.avg_compliance_score || 0) }}%</p>
          </div>
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <TrendingUp class="w-6 h-6 text-purple-600" />
          </div>
        </div>
        <div class="mt-2">
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div 
              class="h-2 rounded-full transition-all duration-300"
              :class="getScoreColor(stats.avg_compliance_score)"
              :style="{ width: `${stats.avg_compliance_score || 0}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Issues Stats Row -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <!-- Open Issues -->
      <div class="bg-white rounded-lg border p-4 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-900">Stock Take Issues</h3>
          <Button variant="ghost" size="sm" @click="navigateToIssues">View All</Button>
        </div>
        <div class="flex items-center gap-8">
          <div class="text-center">
            <p class="text-3xl font-bold text-yellow-600">{{ stats.issues?.open || 0 }}</p>
            <p class="text-sm text-gray-500">Open Issues</p>
          </div>
          <div class="text-center">
            <p class="text-3xl font-bold text-gray-600">{{ stats.issues?.total || 0 }}</p>
            <p class="text-sm text-gray-500">Total Issues</p>
          </div>
        </div>
      </div>

      <!-- Inventory Items -->
      <div class="bg-white rounded-lg border p-4 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-900">Inventory Items</h3>
          <Button variant="ghost" size="sm" @click="navigateToItems">View All</Button>
        </div>
        <div class="flex items-center gap-8">
          <div class="text-center">
            <p class="text-3xl font-bold text-blue-600">{{ stats.items?.active || 0 }}</p>
            <p class="text-sm text-gray-500">Active Items</p>
          </div>
          <div class="text-center">
            <p class="text-3xl font-bold text-gray-600">{{ stats.items?.total || 0 }}</p>
            <p class="text-sm text-gray-500">Total Items</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent Audit Plans -->
      <div class="bg-white rounded-lg border shadow-sm">
        <div class="px-4 py-3 border-b flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">Recent Audit Plans</h3>
          <Button variant="ghost" size="sm" @click="navigateToPlans">View All</Button>
        </div>
        <div v-if="recentPlans.length > 0" class="divide-y">
          <div 
            v-for="plan in recentPlans" 
            :key="plan.name"
            class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
            @click="viewPlan(plan.name)"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-gray-900">{{ plan.plan_title }}</span>
              <Badge :variant="getStatusVariant(plan.status)">{{ plan.status }}</Badge>
            </div>
            <div class="flex items-center gap-4 text-sm text-gray-500">
              <span class="flex items-center gap-1">
                <Calendar class="w-4 h-4" />
                {{ plan.audit_period }}
              </span>
              <span class="flex items-center gap-1">
                <MapPin class="w-4 h-4" />
                {{ plan.warehouse || plan.branch || 'All' }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="p-8 text-center text-gray-500">
          <ClipboardList class="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>No audit plans yet</p>
          <Button variant="outline" size="sm" class="mt-2" @click="navigateToPlans">
            Create First Plan
          </Button>
        </div>
      </div>

      <!-- Recent Stock Take Sessions -->
      <div class="bg-white rounded-lg border shadow-sm">
        <div class="px-4 py-3 border-b flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">Recent Stock Take Sessions</h3>
          <Button variant="ghost" size="sm" @click="navigateToSessions">View All</Button>
        </div>
        <div v-if="recentSessions.length > 0" class="divide-y">
          <div 
            v-for="session in recentSessions" 
            :key="session.name"
            class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
            @click="viewSession(session.name)"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-gray-900">{{ session.session_title }}</span>
              <Badge :variant="getStatusVariant(session.status)">{{ session.status }}</Badge>
            </div>
            <div class="flex items-center gap-4 text-sm text-gray-500">
              <span class="flex items-center gap-1">
                <Package class="w-4 h-4" />
                {{ session.total_items_counted || 0 }} items
              </span>
              <span v-if="session.items_with_variance" class="flex items-center gap-1 text-orange-600">
                <AlertTriangle class="w-4 h-4" />
                {{ session.items_with_variance }} variances
              </span>
            </div>
            <div class="mt-2 flex items-center gap-2">
              <span v-if="session.team_signoff" class="text-xs text-green-600">✓ Team</span>
              <span v-else class="text-xs text-gray-400">○ Team</span>
              <span v-if="session.supervisor_signoff" class="text-xs text-green-600">✓ Supervisor</span>
              <span v-else class="text-xs text-gray-400">○ Supervisor</span>
              <span v-if="session.auditor_signoff" class="text-xs text-green-600">✓ Auditor</span>
              <span v-else class="text-xs text-gray-400">○ Auditor</span>
            </div>
          </div>
        </div>
        <div v-else class="p-8 text-center text-gray-500">
          <Package class="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>No stock take sessions yet</p>
          <Button variant="outline" size="sm" class="mt-2" @click="navigateToSessions">
            Start Session
          </Button>
        </div>
      </div>

      <!-- Open Variance Cases -->
      <div class="bg-white rounded-lg border shadow-sm">
        <div class="px-4 py-3 border-b flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">Open Variance Cases</h3>
          <Button variant="ghost" size="sm" @click="navigateToVarianceCases">View All</Button>
        </div>
        <div v-if="openVarianceCases.length > 0" class="divide-y">
          <div 
            v-for="vc in openVarianceCases" 
            :key="vc.name"
            class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
            @click="viewVarianceCase(vc.name)"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-gray-900">{{ vc.item_code }}</span>
              <div class="flex items-center gap-2">
                <Badge v-if="vc.is_sla_breached" variant="red">SLA Breached</Badge>
                <Badge :variant="getPriorityVariant(vc.priority)">{{ vc.priority }}</Badge>
              </div>
            </div>
            <div class="flex items-center gap-4 text-sm text-gray-500">
              <span class="flex items-center gap-1">
                <Hash class="w-4 h-4" />
                {{ formatNumber(vc.variance_quantity) }} units
              </span>
              <span class="flex items-center gap-1">
                <DollarSign class="w-4 h-4" />
                {{ formatCurrency(vc.variance_value) }}
              </span>
              <span v-if="vc.root_cause" class="flex items-center gap-1">
                <Target class="w-4 h-4" />
                {{ vc.root_cause }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="p-8 text-center text-gray-500">
          <CheckCircle class="w-12 h-12 mx-auto mb-3 text-green-300" />
          <p>No open variance cases</p>
        </div>
      </div>

      <!-- Compliance Scorecards -->
      <div class="bg-white rounded-lg border shadow-sm">
        <div class="px-4 py-3 border-b flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">Compliance Scorecards</h3>
          <Button variant="ghost" size="sm" @click="navigateToScorecards">View All</Button>
        </div>
        <div v-if="scorecards.length > 0" class="divide-y">
          <div 
            v-for="sc in scorecards.slice(0, 5)" 
            :key="sc.name"
            class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
            @click="viewScorecard(sc.name)"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-gray-900">{{ sc.audit_plan_title }}</span>
              <div class="flex items-center gap-2">
                <span class="text-lg font-bold" :class="getGradeTextColor(sc.grade)">{{ sc.grade }}</span>
                <span class="text-gray-500">{{ Math.round(sc.overall_compliance_score || 0) }}%</span>
              </div>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="h-2 rounded-full transition-all duration-300"
                :class="getScoreColor(sc.overall_compliance_score)"
                :style="{ width: `${sc.overall_compliance_score || 0}%` }"
              ></div>
            </div>
          </div>
        </div>
        <div v-else class="p-8 text-center text-gray-500">
          <BarChart2 class="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>No scorecards available</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge } from 'frappe-ui'
import { 
  RefreshCw, Plus, ClipboardList, Package, AlertTriangle, TrendingUp,
  Calendar, MapPin, Hash, DollarSign, Target, CheckCircle, BarChart2
} from 'lucide-vue-next'
import { useInventoryAuditStore } from '@/stores/useInventoryAuditStore'

const router = useRouter()
const store = useInventoryAuditStore()

const loading = ref(false)

const stats = computed(() => store.dashboardStats)
const recentPlans = computed(() => store.plans.slice(0, 5))
const recentSessions = computed(() => store.sessions.slice(0, 5))
const openVarianceCases = computed(() => store.getOpenVarianceCases.slice(0, 5))
const scorecards = computed(() => store.scorecards)

onMounted(async () => {
  await refreshData()
})

async function refreshData() {
  loading.value = true
  try {
    await store.loadAllData()
  } finally {
    loading.value = false
  }
}

function getStatusVariant(status) {
  const variants = {
    'Planned': 'blue',
    'In Progress': 'yellow',
    'Completed': 'green',
    'On Hold': 'gray',
    'Cancelled': 'red',
    'New': 'blue',
    'Under Investigation': 'yellow',
    'Resolution Proposed': 'orange',
    'Resolved': 'green',
    'Closed': 'gray'
  }
  return variants[status] || 'gray'
}

function getPriorityVariant(priority) {
  const variants = {
    'Critical': 'red',
    'High': 'orange',
    'Medium': 'yellow',
    'Low': 'blue'
  }
  return variants[priority] || 'gray'
}

function getScoreColor(score) {
  if (score >= 90) return 'bg-green-500'
  if (score >= 70) return 'bg-yellow-500'
  if (score >= 50) return 'bg-orange-500'
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

function formatNumber(num) {
  return new Intl.NumberFormat().format(num || 0)
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount || 0)
}

// Navigation
function navigateToPlans() {
  router.push('/inventory-audit/plans')
}

function navigateToSessions() {
  router.push('/inventory-audit/sessions')
}

function navigateToVarianceCases() {
  router.push('/inventory-audit/variance-cases')
}

function navigateToScorecards() {
  router.push('/inventory-audit/scorecards')
}

function navigateToIssues() {
  router.push('/inventory-audit/issues')
}

function navigateToItems() {
  router.push('/inventory-audit/items')
}

function viewPlan(name) {
  router.push(`/inventory-audit/plans/${name}`)
}

function viewSession(name) {
  router.push(`/inventory-audit/sessions/${name}`)
}

function viewVarianceCase(name) {
  router.push(`/inventory-audit/variance-cases/${name}`)
}

function viewScorecard(name) {
  router.push(`/inventory-audit/scorecards/${name}`)
}
</script>
