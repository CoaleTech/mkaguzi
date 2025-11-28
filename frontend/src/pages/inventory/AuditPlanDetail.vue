<template>
  <div class="p-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <Spinner class="w-8 h-8" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <AlertCircle class="w-12 h-12 mx-auto mb-4 text-red-400" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">Error Loading Plan</h3>
      <p class="text-gray-500 mb-4">{{ error }}</p>
      <Button @click="loadPlan">Try Again</Button>
    </div>

    <!-- Plan Content -->
    <template v-else-if="plan">
      <!-- Header -->
      <div class="flex items-start justify-between mb-6">
        <div class="flex items-center gap-4">
          <Button variant="ghost" @click="goBack">
            <ArrowLeft class="w-5 h-5" />
          </Button>
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-2xl font-bold text-gray-900">{{ plan.plan_title }}</h1>
              <Badge :variant="getStatusVariant(plan.status)">{{ plan.status }}</Badge>
            </div>
            <p class="text-gray-500 mt-1">{{ plan.name }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <Button variant="outline" @click="exportPlan">
            <Download class="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" @click="editPlan">
            <Edit class="w-4 h-4 mr-2" />
            Edit
          </Button>
          <Button 
            v-if="plan.status === 'Planned'" 
            variant="solid"
            @click="startPlan"
          >
            <Play class="w-4 h-4 mr-2" />
            Start Audit
          </Button>
        </div>
      </div>

      <!-- Main Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Column (2/3) -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Overview Card -->
          <div class="bg-white rounded-lg border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Overview</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">Audit Period</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ plan.audit_period }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">Audit Scope</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ plan.audit_scope }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">Branch</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ plan.branch || '-' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">Warehouse</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ plan.warehouse || '-' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">Lead Auditor</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ plan.lead_auditor_name || plan.lead_auditor || '-' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">Sampling Strategy</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ plan.sampling_strategy || '-' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">Audit Year</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ plan.audit_year || '-' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">SLA Days</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ plan.sla_days || '-' }} days</p>
              </div>
            </div>
          </div>

          <!-- Materiality Thresholds -->
          <div class="bg-white rounded-lg border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Materiality Thresholds</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-xs text-gray-500 uppercase tracking-wide">Type</p>
                <p class="text-lg font-semibold text-gray-900 mt-1">{{ plan.materiality_type || '-' }}</p>
              </div>
              <div class="bg-blue-50 rounded-lg p-4">
                <p class="text-xs text-blue-600 uppercase tracking-wide">Quantity Threshold</p>
                <p class="text-lg font-semibold text-blue-700 mt-1">{{ plan.materiality_threshold_qty || 0 }}</p>
              </div>
              <div class="bg-green-50 rounded-lg p-4">
                <p class="text-xs text-green-600 uppercase tracking-wide">Amount Threshold</p>
                <p class="text-lg font-semibold text-green-700 mt-1">{{ formatCurrency(plan.materiality_threshold_amount) }}</p>
              </div>
              <div class="bg-yellow-50 rounded-lg p-4">
                <p class="text-xs text-yellow-600 uppercase tracking-wide">Percent Threshold</p>
                <p class="text-lg font-semibold text-yellow-700 mt-1">{{ plan.materiality_threshold_percent || 0 }}%</p>
              </div>
            </div>
          </div>

          <!-- Timeline -->
          <div class="bg-white rounded-lg border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">Planned Start</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ formatDate(plan.planned_start_date) }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">Planned End</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ formatDate(plan.planned_end_date) }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">Actual Start</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ formatDate(plan.actual_start_date) || '-' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase tracking-wide">Actual End</p>
                <p class="text-sm font-medium text-gray-900 mt-1">{{ formatDate(plan.actual_end_date) || '-' }}</p>
              </div>
            </div>
            
            <!-- SLA Status -->
            <div class="mt-4 pt-4 border-t">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs text-gray-500 uppercase tracking-wide">SLA Due Date</p>
                  <p class="text-sm font-medium" :class="plan.is_overdue ? 'text-red-600' : 'text-gray-900'">
                    {{ formatDate(plan.sla_due_date) }}
                  </p>
                </div>
                <Badge v-if="plan.is_overdue" variant="red">
                  <AlertTriangle class="w-3 h-3 mr-1" />
                  Overdue
                </Badge>
                <Badge v-else-if="plan.sla_due_date" variant="green">On Track</Badge>
              </div>
            </div>
          </div>

          <!-- Team Members -->
          <div class="bg-white rounded-lg border p-6">
            <TeamMemberTable
              v-model="plan.team_members"
              title="Audit Team"
              readonly
            />
          </div>

          <!-- Stock Take Sessions -->
          <div class="bg-white rounded-lg border p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Stock Take Sessions</h3>
              <Button size="sm" variant="outline" @click="createSession">
                <Plus class="w-4 h-4 mr-1" />
                New Session
              </Button>
            </div>
            
            <div v-if="sessions.length === 0" class="text-center py-8 text-gray-500">
              <ClipboardList class="w-10 h-10 mx-auto mb-2 text-gray-300" />
              <p>No sessions created yet</p>
            </div>
            
            <div v-else class="space-y-3">
              <div 
                v-for="session in sessions" 
                :key="session.name"
                class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                @click="viewSession(session.name)"
              >
                <div class="flex items-center gap-4">
                  <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Package class="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">{{ session.session_title }}</p>
                    <p class="text-sm text-gray-500">{{ session.count_type }} • {{ session.total_items_counted || 0 }} items</p>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <div class="text-right">
                    <p v-if="session.items_with_variance" class="text-sm text-orange-600">
                      {{ session.items_with_variance }} variances
                    </p>
                    <p class="text-xs text-gray-500">{{ formatDate(session.start_datetime) }}</p>
                  </div>
                  <Badge :variant="getStatusVariant(session.status)">{{ session.status }}</Badge>
                  <ChevronRight class="w-5 h-5 text-gray-400" />
                </div>
              </div>
            </div>
          </div>

          <!-- Notes -->
          <div v-if="plan.notes" class="bg-white rounded-lg border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Notes</h3>
            <div class="prose prose-sm max-w-none" v-html="plan.notes"></div>
          </div>
        </div>

        <!-- Right Column (1/3) - Sidebar -->
        <div class="space-y-6">
          <!-- Quick Stats -->
          <div class="bg-white rounded-lg border p-6">
            <h4 class="text-sm font-medium text-gray-700 mb-4">Progress</h4>
            <div class="space-y-4">
              <div>
                <div class="flex items-center justify-between text-sm mb-1">
                  <span class="text-gray-500">Sessions Completed</span>
                  <span class="font-medium">{{ completedSessionsCount }}/{{ sessions.length }}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    class="bg-blue-500 h-2 rounded-full transition-all"
                    :style="{ width: `${sessionsProgress}%` }"
                  ></div>
                </div>
              </div>
              
              <div class="pt-4 border-t space-y-3">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-500">Total Items Counted</span>
                  <span class="text-sm font-medium">{{ totalItemsCounted }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-500">Variance Cases</span>
                  <span class="text-sm font-medium text-orange-600">{{ varianceCasesCount }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-500">Open Issues</span>
                  <span class="text-sm font-medium text-yellow-600">{{ openIssuesCount }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Compliance Score -->
          <div v-if="scorecard" class="bg-white rounded-lg border p-6">
            <h4 class="text-sm font-medium text-gray-700 mb-4">Compliance Score</h4>
            <div class="text-center">
              <div class="inline-flex items-center justify-center w-24 h-24 rounded-full border-4" :class="getScoreBorderClass(scorecard.overall_score)">
                <div>
                  <p class="text-2xl font-bold" :class="getScoreTextClass(scorecard.overall_score)">
                    {{ Math.round(scorecard.overall_score || 0) }}%
                  </p>
                  <p class="text-lg font-bold" :class="getGradeClass(scorecard.grade)">{{ scorecard.grade }}</p>
                </div>
              </div>
              <div class="mt-4 space-y-2 text-sm">
                <div class="flex items-center justify-between">
                  <span class="text-gray-500">Completion Rate</span>
                  <span class="font-medium">{{ scorecard.completion_rate || 0 }}%</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-gray-500">Accuracy Score</span>
                  <span class="font-medium">{{ scorecard.accuracy_score || 0 }}%</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-gray-500">Timeliness</span>
                  <span class="font-medium">{{ scorecard.timeliness_score || 0 }}%</span>
                </div>
              </div>
              <Button size="sm" variant="ghost" class="mt-4" @click="viewScorecard">
                View Full Scorecard
              </Button>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg border p-6">
            <h4 class="text-sm font-medium text-gray-700 mb-4">Quick Actions</h4>
            <div class="space-y-2">
              <Button variant="outline" class="w-full justify-start" @click="createSession">
                <Plus class="w-4 h-4 mr-2" />
                Add Session
              </Button>
              <Button variant="outline" class="w-full justify-start" @click="viewVarianceCases">
                <AlertTriangle class="w-4 h-4 mr-2" />
                View Variance Cases
              </Button>
              <Button variant="outline" class="w-full justify-start" @click="viewIssues">
                <FileWarning class="w-4 h-4 mr-2" />
                View Issues
              </Button>
              <Button variant="outline" class="w-full justify-start" @click="recalculateScorecard">
                <RefreshCw class="w-4 h-4 mr-2" />
                Recalculate Score
              </Button>
            </div>
          </div>

          <!-- Activity Timeline -->
          <div class="bg-white rounded-lg border p-6">
            <h4 class="text-sm font-medium text-gray-700 mb-4">Recent Activity</h4>
            <div class="space-y-4">
              <div class="flex gap-3">
                <div class="w-2 h-2 mt-2 rounded-full bg-blue-500"></div>
                <div>
                  <p class="text-sm text-gray-900">Plan created</p>
                  <p class="text-xs text-gray-500">{{ formatDateTime(plan.creation) }}</p>
                </div>
              </div>
              <div v-if="plan.actual_start_date" class="flex gap-3">
                <div class="w-2 h-2 mt-2 rounded-full bg-green-500"></div>
                <div>
                  <p class="text-sm text-gray-900">Audit started</p>
                  <p class="text-xs text-gray-500">{{ formatDate(plan.actual_start_date) }}</p>
                </div>
              </div>
              <div class="flex gap-3">
                <div class="w-2 h-2 mt-2 rounded-full bg-gray-300"></div>
                <div>
                  <p class="text-sm text-gray-900">Last modified</p>
                  <p class="text-xs text-gray-500">{{ formatDateTime(plan.modified) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Badge, Spinner } from 'frappe-ui'
import { call } from 'frappe-ui'
import {
  ArrowLeft, Edit, Download, Play, Plus, Package, ChevronRight,
  AlertCircle, AlertTriangle, ClipboardList, FileWarning, RefreshCw
} from 'lucide-vue-next'
import { TeamMemberTable } from '@/components/inventory-audit'
import { useInventoryAuditStore } from '@/stores/useInventoryAuditStore'

const route = useRoute()
const router = useRouter()
const store = useInventoryAuditStore()

const loading = ref(true)
const error = ref(null)
const plan = ref(null)
const sessions = ref([])
const scorecard = ref(null)
const varianceCasesCount = ref(0)
const openIssuesCount = ref(0)

const planId = computed(() => route.params.id)

onMounted(() => {
  loadPlan()
})

async function loadPlan() {
  loading.value = true
  error.value = null
  
  try {
    // Load plan details
    plan.value = await call('frappe.client.get', {
      doctype: 'Inventory Audit Plan',
      name: planId.value
    })
    
    // Load related sessions
    const sessionsResult = await call('frappe.client.get_list', {
      doctype: 'Stock Take Session',
      filters: { audit_plan: planId.value },
      fields: ['name', 'session_title', 'status', 'count_type', 'start_datetime', 'total_items_counted', 'items_with_variance'],
      order_by: 'creation desc'
    })
    sessions.value = sessionsResult || []
    
    // Load scorecard
    const scorecardResult = await call('frappe.client.get_list', {
      doctype: 'Audit Compliance Scorecard',
      filters: { audit_plan: planId.value },
      fields: ['name', 'overall_score', 'grade', 'completion_rate', 'accuracy_score', 'timeliness_score'],
      limit_page_length: 1
    })
    scorecard.value = scorecardResult?.[0] || null
    
    // Get variance cases count
    varianceCasesCount.value = await call('frappe.client.get_count', {
      doctype: 'Variance Reconciliation Case',
      filters: { audit_plan: planId.value }
    })
    
    // Get open issues count
    openIssuesCount.value = await call('frappe.client.get_count', {
      doctype: 'Stock Take Issue Log',
      filters: { 
        audit_plan: planId.value,
        status: ['in', ['Open', 'In Progress']]
      }
    })
    
  } catch (e) {
    console.error('Error loading plan:', e)
    error.value = e.message || 'Failed to load plan'
  } finally {
    loading.value = false
  }
}

// Computed
const completedSessionsCount = computed(() => {
  return sessions.value.filter(s => s.status === 'Completed').length
})

const sessionsProgress = computed(() => {
  if (sessions.value.length === 0) return 0
  return (completedSessionsCount.value / sessions.value.length) * 100
})

const totalItemsCounted = computed(() => {
  return sessions.value.reduce((sum, s) => sum + (s.total_items_counted || 0), 0)
})

// Navigation
function goBack() {
  router.push('/inventory-audit/plans')
}

function editPlan() {
  router.push(`/inventory-audit/plans/${planId.value}/edit`)
}

function createSession() {
  router.push(`/inventory-audit/sessions/new?plan=${planId.value}`)
}

function viewSession(sessionId) {
  router.push(`/inventory-audit/sessions/${sessionId}`)
}

function viewVarianceCases() {
  router.push(`/inventory-audit/variance-cases?plan=${planId.value}`)
}

function viewIssues() {
  router.push(`/inventory-audit/issues?plan=${planId.value}`)
}

function viewScorecard() {
  if (scorecard.value) {
    router.push(`/inventory-audit/scorecards/${scorecard.value.name}`)
  }
}

// Actions
async function startPlan() {
  try {
    await call('frappe.client.set_value', {
      doctype: 'Inventory Audit Plan',
      name: planId.value,
      fieldname: {
        status: 'In Progress',
        actual_start_date: new Date().toISOString().split('T')[0]
      }
    })
    await loadPlan()
  } catch (e) {
    console.error('Error starting plan:', e)
  }
}

async function recalculateScorecard() {
  try {
    await store.recalculateScorecard(planId.value)
    await loadPlan()
  } catch (e) {
    console.error('Error recalculating scorecard:', e)
  }
}

function exportPlan() {
  // TODO: Implement export
  console.log('Export plan')
}

// Helpers
function getStatusVariant(status) {
  const variants = {
    'Planned': 'blue',
    'In Progress': 'yellow',
    'Completed': 'green',
    'Closed': 'gray',
    'Cancelled': 'red',
    'Draft': 'gray',
    'Counting Complete': 'blue',
    'Pending Review': 'yellow',
    'Reviewed': 'green'
  }
  return variants[status] || 'gray'
}

function getScoreBorderClass(score) {
  if (score >= 90) return 'border-green-500'
  if (score >= 70) return 'border-yellow-500'
  if (score >= 50) return 'border-orange-500'
  return 'border-red-500'
}

function getScoreTextClass(score) {
  if (score >= 90) return 'text-green-600'
  if (score >= 70) return 'text-yellow-600'
  if (score >= 50) return 'text-orange-600'
  return 'text-red-600'
}

function getGradeClass(grade) {
  const classes = {
    'A': 'text-green-600',
    'B': 'text-blue-600',
    'C': 'text-yellow-600',
    'D': 'text-orange-600',
    'F': 'text-red-600'
  }
  return classes[grade] || 'text-gray-600'
}

function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function formatDateTime(datetime) {
  if (!datetime) return '-'
  return new Date(datetime).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatCurrency(amount) {
  if (!amount) return 'KES 0'
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 0
  }).format(amount)
}
</script>
