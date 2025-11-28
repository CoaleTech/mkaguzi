<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Variance Reconciliation Cases</h1>
        <p class="text-gray-600">Investigate and resolve inventory discrepancies</p>
      </div>
      <div class="flex gap-2">
        <Button @click="refreshData" :loading="loading" variant="outline" size="sm">
          <RefreshCw class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filters.status"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @change="loadCases"
          >
            <option value="">All Statuses</option>
            <option value="New">New</option>
            <option value="Under Investigation">Under Investigation</option>
            <option value="Resolution Proposed">Resolution Proposed</option>
            <option value="Resolved">Resolved</option>
            <option value="Closed">Closed</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
          <select
            v-model="filters.priority"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @change="loadCases"
          >
            <option value="">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Root Cause</label>
          <select
            v-model="filters.root_cause"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @change="loadCases"
          >
            <option value="">All Causes</option>
            <option v-for="cause in store.rootCauseOptions" :key="cause.value" :value="cause.value">
              {{ cause.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Investigator</label>
          <input
            v-model="filters.investigator"
            type="text"
            placeholder="Filter by investigator"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @input="debouncedLoad"
          />
        </div>
        <div class="flex items-end">
          <label class="flex items-center gap-2">
            <input type="checkbox" v-model="showSlaBreached" @change="loadCases" class="rounded border-gray-300" />
            <span class="text-sm text-gray-700">SLA Breached Only</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Total Cases</p>
        <p class="text-2xl font-bold">{{ totalCount }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">New</p>
        <p class="text-2xl font-bold text-blue-600">{{ cases.filter(c => c.status === 'New').length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Under Investigation</p>
        <p class="text-2xl font-bold text-yellow-600">{{ cases.filter(c => c.status === 'Under Investigation').length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">SLA Breached</p>
        <p class="text-2xl font-bold text-red-600">{{ cases.filter(c => c.is_sla_breached).length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Total Variance Value</p>
        <p class="text-2xl font-bold text-orange-600">{{ formatCurrency(totalVarianceValue) }}</p>
      </div>
    </div>

    <!-- Cases List -->
    <div class="bg-white rounded-lg border shadow-sm">
      <div v-if="cases.length > 0" class="divide-y divide-gray-200">
        <div 
          v-for="vc in cases" 
          :key="vc.name"
          class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
          @click="viewCase(vc.name)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h4 class="font-medium text-gray-900">{{ vc.case_title || vc.item_code }}</h4>
                <Badge :variant="getStatusVariant(vc.status)">{{ vc.status }}</Badge>
                <Badge :variant="getPriorityVariant(vc.priority)">{{ vc.priority }}</Badge>
                <Badge v-if="vc.is_sla_breached" variant="red">
                  <AlertTriangle class="w-3 h-3 mr-1" />
                  SLA Breached
                </Badge>
              </div>
              <p class="text-sm text-gray-600 mb-2">{{ vc.case_id }}</p>
              
              <div class="flex items-center gap-6 text-sm text-gray-500">
                <span class="flex items-center gap-1">
                  <Package class="w-4 h-4" />
                  {{ vc.item_code }}
                </span>
                <span v-if="vc.item_description" class="line-clamp-1">{{ vc.item_description }}</span>
              </div>

              <!-- Variance Details -->
              <div class="flex items-center gap-6 mt-3 text-sm">
                <span class="text-gray-700">
                  Qty Variance: <strong :class="vc.variance_quantity > 0 ? 'text-green-600' : 'text-red-600'">
                    {{ vc.variance_quantity > 0 ? '+' : '' }}{{ vc.variance_quantity }}
                  </strong>
                </span>
                <span class="text-gray-700">
                  Value: <strong :class="vc.variance_value > 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatCurrency(vc.variance_value) }}
                  </strong>
                </span>
                <span class="text-gray-700">
                  Variance %: <strong>{{ Math.abs(vc.variance_percent || 0).toFixed(1) }}%</strong>
                </span>
              </div>

              <!-- Root Cause & Investigator -->
              <div class="flex items-center gap-6 mt-3 text-sm">
                <span v-if="vc.root_cause" class="flex items-center gap-1 text-purple-600">
                  <Target class="w-4 h-4" />
                  {{ vc.root_cause }}
                </span>
                <span v-if="vc.investigator" class="flex items-center gap-1 text-gray-500">
                  <User class="w-4 h-4" />
                  {{ vc.investigator }}
                </span>
              </div>
            </div>

            <div class="text-right">
              <p class="text-sm text-gray-500">SLA Due</p>
              <p class="font-medium" :class="getSLAColor(vc)">
                {{ formatDate(vc.sla_due_date) }}
              </p>
              <p v-if="vc.sla_days_remaining !== undefined" class="text-xs text-gray-500">
                {{ vc.sla_days_remaining >= 0 ? `${vc.sla_days_remaining} days left` : `${Math.abs(vc.sla_days_remaining)} days overdue` }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading" class="p-12 text-center text-gray-500">
        <CheckCircle class="w-12 h-12 mx-auto mb-3 text-green-300" />
        <p>No variance cases found</p>
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
import { RefreshCw, Package, Target, User, AlertTriangle, CheckCircle } from 'lucide-vue-next'
import { useInventoryAuditStore } from '@/stores/useInventoryAuditStore'

const router = useRouter()
const store = useInventoryAuditStore()

const loading = ref(false)
const showSlaBreached = ref(false)
const filters = ref({
  status: '',
  priority: '',
  root_cause: '',
  investigator: ''
})

const cases = computed(() => store.varianceCases)
const totalCount = computed(() => store.varianceCasesTotalCount)
const currentPage = computed(() => store.varianceCasesPage)
const pageSize = computed(() => store.varianceCasesPageSize)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

const totalVarianceValue = computed(() => {
  return cases.value.reduce((sum, c) => sum + Math.abs(c.variance_value || 0), 0)
})

onMounted(async () => {
  await loadCases()
})

async function loadCases() {
  loading.value = true
  try {
    const filterObj = { ...filters.value }
    Object.keys(filterObj).forEach(key => {
      if (!filterObj[key]) delete filterObj[key]
    })
    await store.loadVarianceCases(filterObj, currentPage.value, pageSize.value)
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  filters.value = { status: '', priority: '', root_cause: '', investigator: '' }
  showSlaBreached.value = false
  await loadCases()
}

let loadTimeout = null
function debouncedLoad() {
  clearTimeout(loadTimeout)
  loadTimeout = setTimeout(() => loadCases(), 300)
}

async function changePage(page) {
  await store.loadVarianceCases(filters.value, page, pageSize.value)
}

function viewCase(name) {
  router.push(`/inventory-audit/variance-cases/${name}`)
}

function getStatusVariant(status) {
  const variants = { 
    'New': 'blue', 
    'Under Investigation': 'yellow', 
    'Resolution Proposed': 'orange',
    'Resolved': 'green', 
    'Closed': 'gray',
    'No Variance': 'gray'
  }
  return variants[status] || 'gray'
}

function getPriorityVariant(priority) {
  const variants = { 'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'blue' }
  return variants[priority] || 'gray'
}

function getSLAColor(vc) {
  if (vc.is_sla_breached) return 'text-red-600'
  if (vc.sla_days_remaining !== undefined && vc.sla_days_remaining <= 2) return 'text-orange-600'
  return 'text-gray-900'
}

function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency', currency: 'KES', minimumFractionDigits: 0
  }).format(amount || 0)
}
</script>
