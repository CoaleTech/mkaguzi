<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Inventory Audit Plans</h1>
        <p class="text-gray-600">Manage audit cycles, scope, and materiality thresholds</p>
      </div>
      <div class="flex gap-2">
        <Button @click="refreshData" :loading="loading" variant="outline" size="sm">
          <RefreshCw class="w-4 h-4" />
        </Button>
        <Button @click="createPlan">
          <Plus class="w-4 h-4 mr-2" />
          New Plan
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filters.status"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @change="loadPlans"
          >
            <option value="">All Statuses</option>
            <option value="Planned">Planned</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="On Hold">On Hold</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Period</label>
          <select
            v-model="filters.audit_period"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @change="loadPlans"
          >
            <option value="">All Periods</option>
            <option v-for="period in store.auditPeriodOptions" :key="period.value" :value="period.value">
              {{ period.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Branch</label>
          <input
            v-model="filters.branch"
            type="text"
            placeholder="Filter by branch"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @input="debouncedLoad"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Warehouse</label>
          <input
            v-model="filters.warehouse"
            type="text"
            placeholder="Filter by warehouse"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @input="debouncedLoad"
          />
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Total Plans</p>
        <p class="text-2xl font-bold">{{ totalCount }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Planned</p>
        <p class="text-2xl font-bold text-blue-600">{{ plans.filter(p => p.status === 'Planned').length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">In Progress</p>
        <p class="text-2xl font-bold text-yellow-600">{{ plans.filter(p => p.status === 'In Progress').length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Completed</p>
        <p class="text-2xl font-bold text-green-600">{{ plans.filter(p => p.status === 'Completed').length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Avg Compliance</p>
        <p class="text-2xl font-bold text-purple-600">{{ avgCompliance }}%</p>
      </div>
    </div>

    <!-- Plans List -->
    <div class="bg-white rounded-lg border shadow-sm">
      <div v-if="plans.length > 0" class="divide-y divide-gray-200">
        <div 
          v-for="plan in plans" 
          :key="plan.name"
          class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
          @click="viewPlan(plan.name)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h4 class="font-medium text-gray-900">{{ plan.plan_title }}</h4>
                <Badge :variant="getStatusVariant(plan.status)">{{ plan.status }}</Badge>
                <Badge v-if="plan.priority === 'High'" variant="red">High Priority</Badge>
              </div>
              <p class="text-sm text-gray-600 mb-2">{{ plan.plan_id }}</p>
              
              <div class="flex items-center gap-6 text-sm text-gray-500">
                <span class="flex items-center gap-1">
                  <Calendar class="w-4 h-4" />
                  {{ plan.audit_period }}
                </span>
                <span class="flex items-center gap-1">
                  <Target class="w-4 h-4" />
                  {{ plan.audit_scope }}
                </span>
                <span v-if="plan.warehouse" class="flex items-center gap-1">
                  <MapPin class="w-4 h-4" />
                  {{ plan.warehouse }}
                </span>
                <span v-if="plan.lead_auditor" class="flex items-center gap-1">
                  <User class="w-4 h-4" />
                  {{ plan.lead_auditor }}
                </span>
              </div>

              <div class="flex items-center gap-6 mt-3 text-sm">
                <span class="text-gray-500">
                  Sessions: <strong>{{ plan.completed_sessions_count || 0 }}/{{ plan.sessions_count || 0 }}</strong>
                </span>
                <span v-if="plan.variance_cases_count" class="text-orange-600">
                  Variance Cases: <strong>{{ plan.variance_cases_count }}</strong>
                </span>
                <span v-if="plan.compliance_score" class="text-purple-600">
                  Compliance: <strong>{{ plan.compliance_score }}%</strong>
                </span>
              </div>
            </div>

            <div class="text-right">
              <p class="text-sm text-gray-500">Due Date</p>
              <p class="font-medium" :class="isDueSoon(plan.due_date) ? 'text-red-600' : 'text-gray-900'">
                {{ formatDate(plan.due_date) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading" class="p-12 text-center text-gray-500">
        <ClipboardList class="w-12 h-12 mx-auto mb-3 text-gray-300" />
        <p>No audit plans found</p>
        <Button variant="outline" size="sm" class="mt-2" @click="createPlan">
          Create First Plan
        </Button>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-4 py-3 border-t flex items-center justify-between">
        <p class="text-sm text-gray-500">
          Showing {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalCount) }} of {{ totalCount }}
        </p>
        <div class="flex gap-2">
          <Button variant="outline" size="sm" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">
            Previous
          </Button>
          <Button variant="outline" size="sm" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">
            Next
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge } from 'frappe-ui'
import { RefreshCw, Plus, Calendar, Target, MapPin, User, ClipboardList } from 'lucide-vue-next'
import { useInventoryAuditStore } from '@/stores/useInventoryAuditStore'

const router = useRouter()
const store = useInventoryAuditStore()

const loading = ref(false)
const filters = ref({
  status: '',
  audit_period: '',
  branch: '',
  warehouse: ''
})

const plans = computed(() => store.plans)
const totalCount = computed(() => store.plansTotalCount)
const currentPage = computed(() => store.plansPage)
const pageSize = computed(() => store.plansPageSize)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

const avgCompliance = computed(() => {
  const plansWithScore = plans.value.filter(p => p.compliance_score)
  if (plansWithScore.length === 0) return 0
  return Math.round(plansWithScore.reduce((sum, p) => sum + p.compliance_score, 0) / plansWithScore.length)
})

onMounted(async () => {
  await loadPlans()
})

async function loadPlans() {
  loading.value = true
  try {
    const filterObj = { ...filters.value }
    Object.keys(filterObj).forEach(key => {
      if (!filterObj[key]) delete filterObj[key]
    })
    await store.loadPlans(filterObj, currentPage.value, pageSize.value)
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  filters.value = { status: '', audit_period: '', branch: '', warehouse: '' }
  await loadPlans()
}

let loadTimeout = null
function debouncedLoad() {
  clearTimeout(loadTimeout)
  loadTimeout = setTimeout(() => loadPlans(), 300)
}

async function changePage(page) {
  await store.loadPlans(filters.value, page, pageSize.value)
}

function createPlan() {
  router.push('/inventory-audit/plans/new')
}

function viewPlan(name) {
  router.push(`/inventory-audit/plans/${name}`)
}

function getStatusVariant(status) {
  const variants = { 'Planned': 'blue', 'In Progress': 'yellow', 'Completed': 'green', 'On Hold': 'gray', 'Cancelled': 'red' }
  return variants[status] || 'gray'
}

function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function isDueSoon(date) {
  if (!date) return false
  const due = new Date(date)
  const now = new Date()
  const diff = (due - now) / (1000 * 60 * 60 * 24)
  return diff <= 7 && diff >= 0
}
</script>
