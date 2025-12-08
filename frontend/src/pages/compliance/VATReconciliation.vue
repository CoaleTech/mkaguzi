<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">VAT Reconciliation</h1>
          <p class="text-gray-600 mt-1">Reconcile VAT data between System, iTax, and TIMs device records</p>
        </div>
        <div class="flex gap-3">
          <AskAIButton
            contextType="vat-reconciliation-list"
            pageComponent="VATReconciliation"
            :contextData="getVATReconciliationListContext()"
            variant="solid"
            size="sm"
            theme="purple"
          />
          <Button 
            variant="solid" 
            size="sm" 
            @click="refreshData" 
            :loading="loading"
            class="bg-gray-600 hover:bg-gray-700 shadow-sm"
          >
            <div class="flex items-center gap-2">
              <RefreshCw class="w-4 h-4" />
              <span v-if="!loading">Refresh</span>
            </div>
          </Button>
          <Button 
            variant="solid" 
            size="sm" 
            @click="createNewReconciliation"
            class="bg-green-600 hover:bg-green-700 shadow-sm"
          >
            <div class="flex items-center gap-2">
              <Plus class="w-4 h-4" />
              <span>New Reconciliation</span>
            </div>
          </Button>
        </div>
      </div>
    </div>

    <div class="p-6 space-y-6">
      <!-- Filters -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">Filters & Search</h3>
          <p class="text-sm text-gray-600 mt-1">Filter reconciliations by month, year, type, and status</p>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-5 gap-6">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Month</label>
              <select
                v-model="filters.month"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors"
                @change="loadReconciliations"
              >
                <option value="">All Months</option>
                <option v-for="month in months" :key="month.value" :value="month.value">
                  {{ month.label }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Fiscal Year</label>
              <select
                v-model="filters.fiscal_year"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors"
                @change="loadReconciliations"
              >
                <option value="">All Years</option>
                <option v-for="year in fiscalYears" :key="year" :value="year">
                  {{ year }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Reconciliation Type</label>
              <select
                v-model="filters.reconciliation_type"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors"
                @change="loadReconciliations"
              >
                <option value="">All Types</option>
                <option value="System vs iTax">System vs iTax</option>
                <option value="System vs TIMs">System vs TIMs</option>
                <option value="iTax vs TIMs">iTax vs TIMs</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Status</label>
              <select
                v-model="filters.status"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors"
                @change="loadReconciliations"
              >
                <option value="">All Statuses</option>
                <option value="Draft">Draft</option>
                <option value="Files Uploaded">Files Uploaded</option>
                <option value="Validated">Validated</option>
                <option value="Processing">Processing</option>
                <option value="Completed">Completed</option>
                <option value="Failed">Failed</option>
              </select>
            </div>
            <div class="flex items-end">
              <Button 
                variant="solid" 
                size="sm"
                @click="clearFilters"
                class="bg-gray-200 hover:bg-gray-300 text-gray-700 shadow-sm"
              >
                <div class="flex items-center gap-2">
                  <X class="w-4 h-4" />
                  <span>Clear Filters</span>
                </div>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-6 gap-6">
        <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Total Reconciliations</p>
              <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.total }}</p>
            </div>
            <div class="bg-blue-100 p-3 rounded-full">
              <FileText class="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Pending Review</p>
              <p class="text-3xl font-bold text-yellow-600 mt-1">{{ stats.pending }}</p>
            </div>
            <div class="bg-yellow-100 p-3 rounded-full">
              <Clock class="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">With Discrepancies</p>
              <p class="text-3xl font-bold text-red-600 mt-1">{{ stats.discrepancies }}</p>
            </div>
            <div class="bg-red-100 p-3 rounded-full">
              <AlertTriangle class="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Approved</p>
              <p class="text-3xl font-bold text-green-600 mt-1">{{ stats.approved }}</p>
            </div>
            <div class="bg-green-100 p-3 rounded-full">
              <CheckCircle class="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Match Rate</p>
              <p class="text-3xl font-bold text-blue-600 mt-1">{{ stats.matchRate }}%</p>
            </div>
            <div class="bg-blue-100 p-3 rounded-full">
              <TrendingUp class="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Total Variance</p>
              <p class="text-3xl font-bold text-red-600 mt-1">{{ formatCurrency(stats.totalVariance) }}</p>
            </div>
            <div class="bg-red-100 p-3 rounded-full">
              <DollarSign class="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      <!-- Reconciliations List -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h3 class="text-lg font-semibold text-gray-900">VAT Reconciliation Records</h3>
          <p class="text-sm text-gray-600 mt-1">Click on any record to view details, upload files, or run reconciliation</p>
        </div>
        
        <div v-if="loading" class="p-12 text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-gray-500 mt-4 text-lg">Loading reconciliations...</p>
        </div>

        <div v-else-if="reconciliations.length > 0" class="divide-y divide-gray-200">
          <div 
            v-for="recon in reconciliations" 
            :key="recon.name"
            class="p-6 hover:bg-blue-50 cursor-pointer transition-all duration-200 hover:shadow-sm border-l-4 hover:border-l-blue-500"
            @click="viewReconciliation(recon.name)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h4 class="font-medium text-gray-900">{{ recon.name }}</h4>
                  <Badge :variant="getTypeVariant(recon.reconciliation_type)">
                    {{ formatReconciliationType(recon.reconciliation_type) }}
                  </Badge>
                  <Badge :variant="getStatusVariant(recon.status)">{{ recon.status }}</Badge>
                </div>
                
                <div class="flex items-center gap-6 text-sm text-gray-500">
                  <span class="flex items-center gap-1">
                    <Calendar class="w-4 h-4" />
                    {{ recon.reconciliation_month }} {{ recon.fiscal_year }}
                  </span>
                  <span class="flex items-center gap-1">
                    <Clock class="w-4 h-4" />
                    Created: {{ formatDate(recon.creation) }}
                  </span>
                </div>

                <!-- Data Summary -->
                <div class="flex items-center gap-6 mt-3 text-sm">
                  <span class="text-gray-700">
                    Source A: <strong>{{ recon.total_source_a_records || 0 }}</strong>
                  </span>
                  <span class="text-gray-700">
                    Source B: <strong>{{ recon.total_source_b_records || 0 }}</strong>
                  </span>
                  <span class="text-green-600">
                    Matched: <strong>{{ recon.total_matched || 0 }}</strong>
                  </span>
                  <span class="text-yellow-600">
                    Missing in B: <strong>{{ recon.total_unmatched_source_a || 0 }}</strong>
                  </span>
                  <span class="text-orange-600">
                    Missing in A: <strong>{{ recon.total_unmatched_source_b || 0 }}</strong>
                  </span>
                  <span class="text-red-600">
                    Amount Mismatch: <strong>{{ recon.total_amount_discrepancies || 0 }}</strong>
                  </span>
                </div>

                <!-- File Status -->
                <div class="flex items-center gap-2 mt-3">
                  <span class="text-xs px-2 py-1 rounded-full" 
                        :class="recon.system_data_file ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                    {{ recon.system_data_file ? '✓' : '○' }} System Data
                  </span>
                  <span class="text-xs px-2 py-1 rounded-full" 
                        :class="recon.itax_data_file ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                    {{ recon.itax_data_file ? '✓' : '○' }} iTax Data
                  </span>
                  <span class="text-xs px-2 py-1 rounded-full" 
                        :class="recon.tims_data_file ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                    {{ recon.tims_data_file ? '✓' : '○' }} TIMs Data
                  </span>
                  <span v-if="recon.completed_at" class="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700">
                    Completed: {{ formatDate(recon.completed_at) }}
                  </span>
                </div>
              </div>

              <div class="text-right">
                <p class="text-sm text-gray-500">Total Variance</p>
                <p class="text-xl font-bold" :class="(recon.total_variance_amount || 0) > 0 ? 'text-red-600' : 'text-green-600'">
                  {{ formatCurrency(recon.total_variance_amount || 0) }}
                </p>
                <p class="text-xs text-gray-400 mt-1">
                  Match Rate: {{ (recon.match_percentage || 0).toFixed(1) }}%
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="p-16 text-center">
          <div class="bg-gray-100 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
            <FileText class="w-12 h-12 text-gray-400" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">No Reconciliations Found</h3>
          <p class="text-gray-600 mb-8 max-w-md mx-auto">Get started by creating a new VAT reconciliation to compare data between System, iTax, and TIMs device records.</p>
          <Button 
            variant="solid" 
            size="sm" 
            @click="createNewReconciliation"
            class="bg-green-600 hover:bg-green-700 shadow-sm px-6 py-3"
          >
            <div class="flex items-center gap-2">
              <Plus class="w-5 h-5" />
              <span>Create New Reconciliation</span>
            </div>
          </Button>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
          <p class="text-sm text-gray-700 font-medium">
            Showing <span class="font-semibold">{{ (currentPage - 1) * pageSize + 1 }}</span> - 
            <span class="font-semibold">{{ Math.min(currentPage * pageSize, totalCount) }}</span> of 
            <span class="font-semibold">{{ totalCount }}</span> reconciliations
          </p>
          <div class="flex gap-3">
            <Button 
              variant="solid" 
              size="sm" 
              :disabled="currentPage === 1" 
              @click="changePage(currentPage - 1)"
              class="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed shadow-sm px-4 py-2"
            >
              <span>Previous</span>
            </Button>
            <Button 
              variant="solid" 
              size="sm" 
              :disabled="currentPage === totalPages" 
              @click="changePage(currentPage + 1)"
              class="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed shadow-sm px-4 py-2"
            >
              <span>Next</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useVATReconciliationStore } from "@/stores/useVATReconciliationStore"
import { Badge, Button } from "frappe-ui"
import AskAIButton from "@/components/AskAIButton.vue"
import {
	AlertTriangle,
	Calendar,
	CheckCircle,
	Clock,
	DollarSign,
	FileText,
	Plus,
	RefreshCw,
	TrendingUp,
	X,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const store = useVATReconciliationStore()

const loading = ref(false)
const reconciliations = ref([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const filters = ref({
	month: "",
	fiscal_year: "",
	reconciliation_type: "",
	status: "",
})

const months = [
	{ value: "January", label: "January" },
	{ value: "February", label: "February" },
	{ value: "March", label: "March" },
	{ value: "April", label: "April" },
	{ value: "May", label: "May" },
	{ value: "June", label: "June" },
	{ value: "July", label: "July" },
	{ value: "August", label: "August" },
	{ value: "September", label: "September" },
	{ value: "October", label: "October" },
	{ value: "November", label: "November" },
	{ value: "December", label: "December" },
]

// Generate fiscal years (current year and 5 previous years)
const fiscalYears = computed(() => {
	const currentYear = new Date().getFullYear()
	return Array.from({ length: 6 }, (_, i) => `FY ${currentYear - i}`)
})

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

const stats = computed(() => {
	const all = reconciliations.value
	const total = totalCount.value || all.length
	const pending = all.filter((r) =>
		["Draft", "Data Uploaded", "In Progress"].includes(r.status),
	).length
	const approved = all.filter((r) => r.status === "Approved").length
	const discrepancies = all.filter(
		(r) => (r.total_amount_discrepancies || 0) > 0,
	).length

	// Calculate average match rate
	const withMatchRate = all.filter(
		(r) => r.match_percentage !== null && r.match_percentage !== undefined,
	)
	const avgMatchRate =
		withMatchRate.length > 0
			? Math.round(
					withMatchRate.reduce((sum, r) => sum + (r.match_percentage || 0), 0) /
						withMatchRate.length,
				)
			: 0

	const totalVariance = all.reduce(
		(sum, r) => sum + (r.total_variance_amount || 0),
		0,
	)

	return {
		total,
		pending,
		approved,
		discrepancies,
		matchRate: avgMatchRate,
		totalVariance,
	}
})

onMounted(async () => {
	await loadReconciliations()
})

async function loadReconciliations() {
	loading.value = true
	try {
		const filterObj = {}

		if (filters.value.month) {
			filterObj.reconciliation_month = filters.value.month
		}
		if (filters.value.fiscal_year) {
			filterObj.fiscal_year = filters.value.fiscal_year
		}
		if (filters.value.reconciliation_type) {
			filterObj.reconciliation_type = filters.value.reconciliation_type
		}
		if (filters.value.status) {
			filterObj.status = filters.value.status
		}

		await store.fetchReconciliations(
			filterObj,
			currentPage.value,
			pageSize.value,
		)
		reconciliations.value = store.reconciliations
		totalCount.value = store.totalCount
	} catch (error) {
		console.error("Error loading reconciliations:", error)
	} finally {
		loading.value = false
	}
}

async function refreshData() {
	currentPage.value = 1
	await loadReconciliations()
}

function clearFilters() {
	filters.value = {
		month: "",
		fiscal_year: "",
		reconciliation_type: "",
		status: "",
	}
	currentPage.value = 1
	loadReconciliations()
}

async function changePage(page) {
	currentPage.value = page
	await loadReconciliations()
}

function createNewReconciliation() {
	router.push("/compliance/vat-reconciliation/new")
}

function viewReconciliation(name) {
	router.push(`/compliance/vat-reconciliation/${name}`)
}

function getTypeVariant(type) {
	const variants = {
		system_vs_itax: "blue",
		system_vs_tims: "purple",
		itax_vs_tims: "orange",
	}
	return variants[type] || "gray"
}

function getStatusVariant(status) {
	const variants = {
		Draft: "subtle",
		"Data Uploaded": "yellow",
		Reconciled: "blue",
		Reviewed: "purple",
		Approved: "green",
	}
	return variants[status] || "gray"
}

function getVATReconciliationListContext() {
	return {
		total_reconciliations: stats.value.total,
		pending_reconciliations: stats.value.pending,
		approved_reconciliations: stats.value.approved,
		reconciliations_with_discrepancies: stats.value.discrepancies,
		average_match_rate: stats.value.matchRate,
		total_variance_amount: stats.value.totalVariance,
		current_filters: filters.value,
		reconciliation_summary: reconciliations.value.map(r => ({
			name: r.name,
			status: r.status,
			reconciliation_month: r.reconciliation_month,
			fiscal_year: r.fiscal_year,
			match_percentage: r.match_percentage,
			total_variance_amount: r.total_variance_amount,
			total_matched: r.total_matched,
			total_unmatched_source_a: r.total_unmatched_source_a,
			total_unmatched_source_b: r.total_unmatched_source_b,
			total_amount_discrepancies: r.total_amount_discrepancies
		}))
	}
}

function formatReconciliationType(type) {
	const labels = {
		system_vs_itax: "System vs iTax",
		system_vs_tims: "System vs TIMs",
		itax_vs_tims: "iTax vs TIMs",
	}
	return labels[type] || type
}

function formatDate(date) {
	if (!date) return "-"
	return new Date(date).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	})
}

function formatCurrency(amount) {
	return new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
		minimumFractionDigits: 2,
	}).format(amount || 0)
}
</script>
