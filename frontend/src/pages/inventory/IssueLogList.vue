<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Stock Take Issue Log</h1>
        <p class="text-gray-600">Track and resolve operational issues during audits</p>
      </div>
      <div class="flex gap-2">
        <Button @click="refreshData" :loading="loading" variant="outline" size="sm">
          <RefreshCw class="w-4 h-4" />
        </Button>
        <Button @click="createIssue">
          <Plus class="w-4 h-4 mr-2" />
          Log Issue
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
            @change="loadIssues"
          >
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="In Progress">In Progress</option>
            <option value="Resolved">Resolved</option>
            <option value="Closed">Closed</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
          <select
            v-model="filters.priority"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @change="loadIssues"
          >
            <option value="">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Issue Type</label>
          <select
            v-model="filters.issue_type"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @change="loadIssues"
          >
            <option value="">All Types</option>
            <option v-for="type in store.issueTypeOptions" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Assigned To</label>
          <input
            v-model="filters.assigned_to"
            type="text"
            placeholder="Filter by assignee"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @input="debouncedLoad"
          />
        </div>
        <div class="flex items-end">
          <label class="flex items-center gap-2">
            <input type="checkbox" v-model="showSlaBreached" @change="loadIssues" class="rounded border-gray-300" />
            <span class="text-sm text-gray-700">SLA Breached Only</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Total Issues</p>
        <p class="text-2xl font-bold">{{ totalCount }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Open</p>
        <p class="text-2xl font-bold text-yellow-600">{{ issues.filter(i => i.status === 'Open').length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">In Progress</p>
        <p class="text-2xl font-bold text-blue-600">{{ issues.filter(i => i.status === 'In Progress').length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">SLA Breached</p>
        <p class="text-2xl font-bold text-red-600">{{ issues.filter(i => i.is_sla_breached).length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Resolved</p>
        <p class="text-2xl font-bold text-green-600">{{ issues.filter(i => i.status === 'Resolved').length }}</p>
      </div>
    </div>

    <!-- Issues List -->
    <div class="bg-white rounded-lg border shadow-sm">
      <div v-if="issues.length > 0" class="divide-y divide-gray-200">
        <div 
          v-for="issue in issues" 
          :key="issue.name"
          class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
          @click="viewIssue(issue.name)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h4 class="font-medium text-gray-900">{{ issue.issue_title }}</h4>
                <Badge :variant="getStatusVariant(issue.status)">{{ issue.status }}</Badge>
                <Badge :variant="getPriorityVariant(issue.priority)">{{ issue.priority }}</Badge>
                <Badge v-if="issue.is_sla_breached" variant="red">
                  <AlertTriangle class="w-3 h-3 mr-1" />
                  SLA Breached
                </Badge>
              </div>
              <p class="text-sm text-gray-600 mb-2">{{ issue.issue_id }}</p>
              
              <div class="flex items-center gap-6 text-sm text-gray-500">
                <span class="flex items-center gap-1">
                  <Tag class="w-4 h-4" />
                  {{ issue.issue_type }}
                </span>
                <span v-if="issue.warehouse" class="flex items-center gap-1">
                  <MapPin class="w-4 h-4" />
                  {{ issue.warehouse }}
                </span>
                <span v-if="issue.item_code" class="flex items-center gap-1">
                  <Package class="w-4 h-4" />
                  {{ issue.item_code }}
                </span>
              </div>

              <!-- Assignment & Reporter -->
              <div class="flex items-center gap-6 mt-3 text-sm">
                <span v-if="issue.assigned_to" class="flex items-center gap-1 text-gray-700">
                  <User class="w-4 h-4" />
                  Assigned: <strong>{{ issue.assigned_to }}</strong>
                </span>
                <span v-if="issue.reported_by" class="flex items-center gap-1 text-gray-500">
                  Reported by: {{ issue.reported_by }}
                </span>
                <span class="flex items-center gap-1 text-gray-500">
                  <Calendar class="w-4 h-4" />
                  {{ formatDate(issue.reported_date) }}
                </span>
              </div>
            </div>

            <div class="text-right">
              <p class="text-sm text-gray-500">SLA Due</p>
              <p class="font-medium" :class="getSLAColor(issue)">
                {{ formatDate(issue.sla_due_date) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading" class="p-12 text-center text-gray-500">
        <CheckCircle class="w-12 h-12 mx-auto mb-3 text-green-300" />
        <p>No issues logged</p>
        <Button variant="outline" size="sm" class="mt-2" @click="createIssue">
          Log First Issue
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
import { RefreshCw, Plus, Tag, MapPin, Package, User, Calendar, AlertTriangle, CheckCircle } from 'lucide-vue-next'
import { useInventoryAuditStore } from '@/stores/useInventoryAuditStore'

const router = useRouter()
const store = useInventoryAuditStore()

const loading = ref(false)
const showSlaBreached = ref(false)
const filters = ref({
  status: '',
  priority: '',
  issue_type: '',
  assigned_to: ''
})

const issues = computed(() => store.issues)
const totalCount = computed(() => store.issuesTotalCount)
const currentPage = computed(() => store.issuesPage)
const pageSize = computed(() => store.issuesPageSize)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

onMounted(async () => {
  await loadIssues()
})

async function loadIssues() {
  loading.value = true
  try {
    const filterObj = { ...filters.value }
    Object.keys(filterObj).forEach(key => {
      if (!filterObj[key]) delete filterObj[key]
    })
    await store.loadIssues(filterObj, currentPage.value, pageSize.value)
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  filters.value = { status: '', priority: '', issue_type: '', assigned_to: '' }
  showSlaBreached.value = false
  await loadIssues()
}

let loadTimeout = null
function debouncedLoad() {
  clearTimeout(loadTimeout)
  loadTimeout = setTimeout(() => loadIssues(), 300)
}

async function changePage(page) {
  await store.loadIssues(filters.value, page, pageSize.value)
}

function createIssue() {
  router.push('/inventory-audit/issues/new')
}

function viewIssue(name) {
  router.push(`/inventory-audit/issues/${name}`)
}

function getStatusVariant(status) {
  const variants = { 'Open': 'yellow', 'In Progress': 'blue', 'Resolved': 'green', 'Closed': 'gray' }
  return variants[status] || 'gray'
}

function getPriorityVariant(priority) {
  const variants = { 'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'blue' }
  return variants[priority] || 'gray'
}

function getSLAColor(issue) {
  if (issue.is_sla_breached) return 'text-red-600'
  return 'text-gray-900'
}

function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>
