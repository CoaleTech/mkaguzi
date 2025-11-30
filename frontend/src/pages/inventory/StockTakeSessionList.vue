<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Stock Take Sessions</h1>
        <p class="text-gray-600">Manage physical count sessions and count teams</p>
      </div>
      <div class="flex gap-2">
        <Button @click="refreshData" :loading="loading" variant="outline" size="sm">
          <RefreshCw class="w-4 h-4" />
        </Button>
        <Button @click="createSession">
          <Plus class="w-4 h-4 mr-2" />
          New Session
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
            @change="loadSessions"
          >
            <option value="">All Statuses</option>
            <option value="Planned">Planned</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Count Type</label>
          <select
            v-model="filters.count_type"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @change="loadSessions"
          >
            <option value="">All Types</option>
            <option v-for="type in store.countTypeOptions" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Audit Plan</label>
          <input
            v-model="filters.audit_plan"
            type="text"
            placeholder="Filter by plan"
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
        <p class="text-sm text-gray-500">Total Sessions</p>
        <p class="text-2xl font-bold">{{ totalCount }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">In Progress</p>
        <p class="text-2xl font-bold text-yellow-600">{{ sessions.filter(s => s.status === 'In Progress').length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Pending Signoff</p>
        <p class="text-2xl font-bold text-orange-600">{{ pendingSignoffCount }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Total Items Counted</p>
        <p class="text-2xl font-bold text-blue-600">{{ totalItemsCounted }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Items w/ Variance</p>
        <p class="text-2xl font-bold text-red-600">{{ totalVariances }}</p>
      </div>
    </div>

    <!-- Sessions List -->
    <div class="bg-white rounded-lg border shadow-sm">
      <div v-if="sessions.length > 0" class="divide-y divide-gray-200">
        <div 
          v-for="session in sessions" 
          :key="session.name"
          class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
          @click="viewSession(session.name)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h4 class="font-medium text-gray-900">{{ session.session_title }}</h4>
                <Badge :variant="getStatusVariant(session.status)">{{ session.status }}</Badge>
                <Badge variant="gray">{{ session.count_type }}</Badge>
              </div>
              <p class="text-sm text-gray-600 mb-2">{{ session.session_id }}</p>
              
              <div class="flex items-center gap-6 text-sm text-gray-500">
                <span v-if="session.warehouse" class="flex items-center gap-1">
                  <MapPin class="w-4 h-4" />
                  {{ session.warehouse }}
                </span>
                <span v-if="session.start_datetime" class="flex items-center gap-1">
                  <Clock class="w-4 h-4" />
                  {{ formatDateTime(session.start_datetime) }}
                </span>
              </div>

              <!-- Count Summary -->
              <div class="flex items-center gap-6 mt-3 text-sm">
                <span class="text-gray-500">
                  Items: <strong>{{ session.total_items_counted || 0 }}</strong>
                </span>
                <span v-if="session.items_with_variance" class="text-orange-600">
                  Variances: <strong>{{ session.items_with_variance }}</strong>
                </span>
                <span v-if="session.total_variance_value" class="text-red-600">
                  Value: <strong>{{ formatCurrency(session.total_variance_value) }}</strong>
                </span>
                <span v-if="session.materiality_breaches" class="text-red-700 font-medium">
                  <AlertTriangle class="w-4 h-4 inline" />
                  {{ session.materiality_breaches }} material
                </span>
              </div>

              <!-- Signoff Status -->
              <div class="flex items-center gap-4 mt-3">
                <span class="text-xs px-2 py-1 rounded-full" 
                      :class="session.team_signoff ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                  {{ session.team_signoff ? '✓' : '○' }} Team
                </span>
                <span class="text-xs px-2 py-1 rounded-full" 
                      :class="session.supervisor_signoff ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                  {{ session.supervisor_signoff ? '✓' : '○' }} Supervisor
                </span>
                <span class="text-xs px-2 py-1 rounded-full" 
                      :class="session.auditor_signoff ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                  {{ session.auditor_signoff ? '✓' : '○' }} Auditor
                </span>
              </div>
            </div>

            <div class="text-right">
              <p v-if="session.session_compliance_score" class="text-lg font-bold" :class="getScoreColor(session.session_compliance_score)">
                {{ session.session_compliance_score }}%
              </p>
              <p v-if="session.variance_rate" class="text-sm text-gray-500">
                Variance: {{ session.variance_rate }}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading" class="p-12 text-center text-gray-500">
        <Package class="w-12 h-12 mx-auto mb-3 text-gray-300" />
        <p>No stock take sessions found</p>
        <Button variant="outline" size="sm" class="mt-2" @click="createSession">
          Start First Session
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
import { useInventoryAuditStore } from "@/stores/useInventoryAuditStore"
import { Badge, Button } from "frappe-ui"
import {
	AlertTriangle,
	Clock,
	MapPin,
	Package,
	Plus,
	RefreshCw,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const store = useInventoryAuditStore()

const loading = ref(false)
const filters = ref({
	status: "",
	count_type: "",
	audit_plan: "",
	warehouse: "",
})

const sessions = computed(() => store.sessions)
const totalCount = computed(() => store.sessionsTotalCount)
const currentPage = computed(() => store.sessionsPage)
const pageSize = computed(() => store.sessionsPageSize)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

const pendingSignoffCount = computed(() => {
	return sessions.value.filter(
		(s) =>
			s.status === "Completed" &&
			(!s.team_signoff || !s.supervisor_signoff || !s.auditor_signoff),
	).length
})

const totalItemsCounted = computed(() => {
	return sessions.value.reduce(
		(sum, s) => sum + (s.total_items_counted || 0),
		0,
	)
})

const totalVariances = computed(() => {
	return sessions.value.reduce(
		(sum, s) => sum + (s.items_with_variance || 0),
		0,
	)
})

onMounted(async () => {
	await loadSessions()
})

async function loadSessions() {
	loading.value = true
	try {
		const filterObj = { ...filters.value }
		Object.keys(filterObj).forEach((key) => {
			if (!filterObj[key]) delete filterObj[key]
		})
		await store.loadSessions(filterObj, currentPage.value, pageSize.value)
	} finally {
		loading.value = false
	}
}

async function refreshData() {
	filters.value = { status: "", count_type: "", audit_plan: "", warehouse: "" }
	await loadSessions()
}

let loadTimeout = null
function debouncedLoad() {
	clearTimeout(loadTimeout)
	loadTimeout = setTimeout(() => loadSessions(), 300)
}

async function changePage(page) {
	await store.loadSessions(filters.value, page, pageSize.value)
}

function createSession() {
	router.push("/inventory-audit/sessions/new")
}

function viewSession(name) {
	router.push(`/inventory-audit/sessions/${name}`)
}

function getStatusVariant(status) {
	const variants = {
		Planned: "blue",
		"In Progress": "yellow",
		Completed: "green",
		Cancelled: "red",
	}
	return variants[status] || "gray"
}

function getScoreColor(score) {
	if (score >= 90) return "text-green-600"
	if (score >= 70) return "text-yellow-600"
	return "text-red-600"
}

function formatDateTime(date) {
	if (!date) return "-"
	return new Date(date).toLocaleString("en-US", {
		month: "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	})
}

function formatCurrency(amount) {
	return new Intl.NumberFormat("en-US", {
		style: "currency",
		currency: "KES",
		minimumFractionDigits: 0,
	}).format(amount || 0)
}
</script>
