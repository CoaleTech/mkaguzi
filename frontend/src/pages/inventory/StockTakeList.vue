<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Stock Take Management</h1>
          <p class="text-gray-600 mt-1">Comprehensive physical verification of stock items across all warehouses</p>
        </div>
        <div class="flex gap-3">
          <Button 
            variant="solid" 
            size="sm" 
            @click="showImportModal = true"
            class="bg-blue-600 hover:bg-blue-700 shadow-sm"
          >
            <div class="flex items-center gap-2">
              <Upload class="w-4 h-4" />
              <span>Import CSV</span>
            </div>
          </Button>
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
            @click="createStockTake"
            class="bg-green-600 hover:bg-green-700 shadow-sm"
          >
            <div class="flex items-center gap-2">
              <Plus class="w-4 h-4" />
              <span>New Stock Take</span>
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
        <p class="text-sm text-gray-600 mt-1">Filter stock takes by type, status, warehouse, and date range</p>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-6 gap-6">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Stock Take Type</label>
            <select
              v-model="filters.stock_take_type"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors"
              @change="loadStockTakes"
            >
              <option value="">All Types</option>
              <option value="Sales Return">Sales Return</option>
              <option value="Daily Stock Take">Daily Stock Take</option>
              <option value="Weekly Stock Take">Weekly Stock Take</option>
              <option value="Monthly Stock Take">Monthly Stock Take</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Status</label>
            <select
              v-model="filters.status"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors"
              @change="loadStockTakes"
            >
              <option value="">All Statuses</option>
              <option value="Draft">Draft</option>
              <option value="Physical Count Submitted">Physical Count Submitted</option>
              <option value="Analyst Reviewed">Analyst Reviewed</option>
              <option value="HOD Approved">HOD Approved</option>
              <option value="Under Investigation">Under Investigation</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Warehouse</label>
            <select
              v-model="filters.warehouse"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors"
              @change="loadStockTakes"
            >
              <option value="">All Warehouses</option>
              <option v-for="wh in warehouses" :key="wh.name" :value="wh.name">
                {{ wh.warehouse_code }} - {{ wh.warehouse_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Date From</label>
            <input
              v-model="filters.date_from"
              type="date"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors"
              @change="loadStockTakes"
            />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">Date To</label>
            <input
              v-model="filters.date_to"
              type="date"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors"
              @change="loadStockTakes"
            />
          </div>
          <div class="flex items-end">
            <label class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
              <input type="checkbox" v-model="overdueOnly" @change="loadStockTakes" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
              <div>
                <span class="text-sm font-medium text-gray-700">Overdue Only</span>
                <p class="text-xs text-gray-500">Show only overdue stock takes</p>
              </div>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-6 gap-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Stock Takes</p>
            <p class="text-3xl font-bold text-gray-900 mt-1">{{ totalCount }}</p>
          </div>
          <div class="bg-blue-100 p-3 rounded-full">
            <ClipboardList class="w-6 h-6 text-blue-600" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Pending Count</p>
            <p class="text-3xl font-bold text-yellow-600 mt-1">{{ pendingCount }}</p>
          </div>
          <div class="bg-yellow-100 p-3 rounded-full">
            <AlertTriangle class="w-6 h-6 text-yellow-600" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">With Discrepancy</p>
            <p class="text-3xl font-bold text-red-600 mt-1">{{ discrepancyCount }}</p>
          </div>
          <div class="bg-red-100 p-3 rounded-full">
            <AlertTriangle class="w-6 h-6 text-red-600" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Under Investigation</p>
            <p class="text-3xl font-bold text-orange-600 mt-1">{{ investigationCount }}</p>
          </div>
          <div class="bg-orange-100 p-3 rounded-full">
            <AlertTriangle class="w-6 h-6 text-orange-600" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Resolved</p>
            <p class="text-3xl font-bold text-green-600 mt-1">{{ resolvedCount }}</p>
          </div>
          <div class="bg-green-100 p-3 rounded-full">
            <CheckCircleIcon class="w-6 h-6 text-green-600" />
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Variance</p>
            <p class="text-3xl font-bold text-red-600 mt-1">{{ formatCurrency(totalVariance) }}</p>
          </div>
          <div class="bg-red-100 p-3 rounded-full">
            <AlertTriangle class="w-6 h-6 text-red-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Stock Takes List -->
    <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h3 class="text-lg font-semibold text-gray-900">Stock Take Records</h3>
        <p class="text-sm text-gray-600 mt-1">Click on any record to view details and manage the stock take process</p>
      </div>
      
      <div v-if="loading" class="p-12 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="text-gray-500 mt-4 text-lg">Loading stock takes...</p>
      </div>

      <div v-else-if="stockTakes.length > 0" class="divide-y divide-gray-200">
        <div 
          v-for="stockTake in stockTakes" 
          :key="stockTake.name"
          class="p-6 hover:bg-blue-50 cursor-pointer transition-all duration-200 hover:shadow-sm border-l-4 hover:border-l-blue-500"
          @click="viewStockTake(stockTake.name)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h4 class="font-medium text-gray-900">{{ stockTake.name }}</h4>
                <Badge :variant="getTypeVariant(stockTake.stock_take_type)">{{ stockTake.stock_take_type }}</Badge>
                <Badge :variant="getStatusVariant(stockTake.status)">{{ stockTake.status }}</Badge>
                <Badge v-if="isOverdue(stockTake)" variant="red">
                  <AlertTriangle class="w-3 h-3 mr-1" />
                  Overdue
                </Badge>
              </div>
              
              <div class="flex items-center gap-6 text-sm text-gray-500">
                <span class="flex items-center gap-1">
                  <Warehouse class="w-4 h-4" />
                  {{ stockTake.warehouse }}
                </span>
                <span v-if="stockTake.branch" class="flex items-center gap-1">
                  <MapPin class="w-4 h-4" />
                  {{ stockTake.branch }}
                </span>
                <span class="flex items-center gap-1">
                  <Calendar class="w-4 h-4" />
                  {{ formatDate(stockTake.audit_date) }}
                </span>
              </div>

              <!-- Items Summary -->
              <div class="flex items-center gap-6 mt-3 text-sm">
                <span class="text-gray-700">
                  Total Items: <strong>{{ stockTake.total_items || 0 }}</strong>
                </span>
                <span class="text-yellow-600">
                  Pending: <strong>{{ stockTake.items_pending || 0 }}</strong>
                </span>
                <span class="text-green-600">
                  Match: <strong>{{ stockTake.items_verified_match || 0 }}</strong>
                </span>
                <span class="text-red-600">
                  Discrepancy: <strong>{{ stockTake.items_verified_discrepancy || 0 }}</strong>
                </span>
                <span class="text-blue-600">
                  Resolved: <strong>{{ stockTake.items_resolved || 0 }}</strong>
                </span>
              </div>

              <!-- Workflow Status -->
              <div class="flex items-center gap-2 mt-3">
                <span class="text-xs px-2 py-1 rounded-full" 
                      :class="stockTake.analyst_verified ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                  {{ stockTake.analyst_verified ? '✓' : '○' }} Analyst
                </span>
                <span class="text-xs px-2 py-1 rounded-full" 
                      :class="stockTake.taker_verified ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                  {{ stockTake.taker_verified ? '✓' : '○' }} Stock Taker
                </span>
                <span class="text-xs px-2 py-1 rounded-full" 
                      :class="stockTake.manager_confirmed ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                  {{ stockTake.manager_confirmed ? '✓' : '○' }} Manager
                </span>
                <span class="text-xs px-2 py-1 rounded-full" 
                      :class="stockTake.hod_approved ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                  {{ stockTake.hod_approved ? '✓' : '○' }} HOD
                </span>
              </div>
            </div>

            <div class="text-right">
              <p class="text-sm text-gray-500">Variance Value</p>
              <p class="text-xl font-bold" :class="(stockTake.total_variance_value || 0) > 0 ? 'text-red-600' : 'text-green-600'">
                {{ formatCurrency(stockTake.total_variance_value || 0) }}
              </p>
              <p class="text-xs text-gray-400 mt-1">
                Deadline: {{ formatDate(stockTake.resolution_deadline) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="p-16 text-center">
        <div class="bg-gray-100 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
          <ClipboardList class="w-12 h-12 text-gray-400" />
        </div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No Stock Takes Found</h3>
        <p class="text-gray-600 mb-8 max-w-md mx-auto">Get started by importing stock data from CSV or creating a new stock take record to begin the physical verification process.</p>
        <div class="flex gap-4 justify-center">
          <Button 
            variant="solid" 
            size="sm" 
            @click="showImportModal = true"
            class="bg-blue-600 hover:bg-blue-700 shadow-sm px-6 py-3"
          >
            <div class="flex items-center gap-2">
              <Upload class="w-5 h-5" />
              <span>Import CSV</span>
            </div>
          </Button>
          <Button 
            variant="solid" 
            size="sm" 
            @click="createStockTake"
            class="bg-green-600 hover:bg-green-700 shadow-sm px-6 py-3"
          >
            <div class="flex items-center gap-2">
              <Plus class="w-5 h-5" />
              <span>New Stock Take</span>
            </div>
          </Button>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
        <p class="text-sm text-gray-700 font-medium">
          Showing <span class="font-semibold">{{ (currentPage - 1) * pageSize + 1 }}</span> - 
          <span class="font-semibold">{{ Math.min(currentPage * pageSize, totalCount) }}</span> of 
          <span class="font-semibold">{{ totalCount }}</span> stock takes
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

    <!-- Import Modal -->
    <Dialog v-model="showImportModal" :options="{ title: 'Import Stock Take from CSV' }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Stock Take Type <span class="text-red-500">*</span>
            </label>
            <select
              v-model="importForm.stock_take_type"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="Daily Stock Take">Daily Stock Take</option>
              <option value="Weekly Stock Take">Weekly Stock Take</option>
              <option value="Monthly Stock Take">Monthly Stock Take</option>
              <option value="Sales Return">Sales Return</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Warehouse <span class="text-red-500">*</span>
            </label>
            <select
              v-model="importForm.warehouse"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="">Select Warehouse</option>
              <option v-for="wh in warehouses" :key="wh.name" :value="wh.name">
                {{ wh.warehouse_code }} - {{ wh.warehouse_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Stock Take Date</label>
            <input
              v-model="importForm.audit_date"
              type="date"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Upload CSV File</label>
            <input 
              type="file" 
              accept=".csv"
              @change="onFileSelected"
              class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>
          <div class="text-sm text-gray-500 bg-gray-50 p-3 rounded">
            <p class="font-medium mb-1">Expected CSV columns:</p>
            <p>Item Code, Description, System Qty, Value, Warehouse, Date</p>
          </div>
          <div v-if="importPreview.length > 0" class="border rounded p-3">
            <p class="text-sm font-medium mb-2">Preview ({{ importPreview.length }} items):</p>
            <div class="max-h-40 overflow-y-auto text-xs">
              <div v-for="(item, idx) in importPreview.slice(0, 5)" :key="idx" class="py-1 border-b">
                {{ item['Item Code'] }} - {{ item['Description'] }} (Qty: {{ item['System Qty'] || item['Return Qty'] }})
              </div>
              <div v-if="importPreview.length > 5" class="py-1 text-gray-500">
                ... and {{ importPreview.length - 5 }} more items
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button 
          variant="solid" 
          size="sm" 
          @click="showImportModal = false"
          class="bg-gray-600 hover:bg-gray-700"
        >
          <span>Cancel</span>
        </Button>
        <Button 
          variant="solid" 
          size="sm" 
          @click="confirmImport" 
          :disabled="!importForm.warehouse || importPreview.length === 0"
          :loading="importing"
          class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400"
        >
          <span>Import {{ importPreview.length }} Items</span>
        </Button>
      </template>
    </Dialog>
    </div>
  </div>
</template>

<script setup>
import { useInventoryAuditStore } from "@/stores/useInventoryAuditStore"
import { Badge, Button, Dialog } from "frappe-ui"
import { call } from "frappe-ui"
import {
	AlertTriangle,
	Calendar,
	CheckCircleIcon,
	ClipboardList,
	MapPin,
	Plus,
	RefreshCw,
	Upload,
	Warehouse,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const store = useInventoryAuditStore()

const loading = ref(false)
const importing = ref(false)
const overdueOnly = ref(false)
const showImportModal = ref(false)
const stockTakes = ref([])
const warehouses = ref([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const filters = ref({
	stock_take_type: "",
	status: "",
	warehouse: "",
	date_from: "",
	date_to: "",
})

const importForm = ref({
	stock_take_type: "Daily Stock Take",
	warehouse: "",
	audit_date: new Date().toISOString().split("T")[0],
})
const importPreview = ref([])
const csvContent = ref("")

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

const pendingCount = computed(
	() =>
		stockTakes.value.filter((a) =>
			["Draft", "Physical Count Submitted"].includes(a.status),
		).length,
)

const discrepancyCount = computed(
	() =>
		stockTakes.value.filter((a) => (a.items_verified_discrepancy || 0) > 0)
			.length,
)

const investigationCount = computed(
	() =>
		stockTakes.value.filter((a) => a.status === "Under Investigation").length,
)

const resolvedCount = computed(
	() => stockTakes.value.filter((a) => a.status === "HOD Approved").length,
)

const totalVariance = computed(() =>
	stockTakes.value.reduce(
		(sum, a) => sum + Math.abs(a.total_variance_value || 0),
		0,
	),
)

onMounted(async () => {
	await Promise.all([loadStockTakes(), loadWarehouses()])
})

async function loadWarehouses() {
	try {
		const result = await call("frappe.client.get_list", {
			doctype: "Warehouse Master",
			filters: { is_active: 1 },
			fields: ["name", "warehouse_code", "warehouse_name"],
			limit_page_length: 0,
		})
		warehouses.value = result
	} catch (error) {
		console.error("Error loading warehouses:", error)
	}
}

async function loadStockTakes() {
	loading.value = true
	try {
		const filterObj = {}

		if (filters.value.stock_take_type) {
			filterObj.stock_take_type = filters.value.stock_take_type
		}
		if (filters.value.status) {
			filterObj.status = filters.value.status
		}
		if (filters.value.warehouse) {
			filterObj.warehouse = filters.value.warehouse
		}
		if (filters.value.date_from) {
			filterObj.audit_date = [">=", filters.value.date_from]
		}
		if (filters.value.date_to) {
			if (filterObj.audit_date) {
				filterObj.audit_date = [
					"between",
					[filters.value.date_from, filters.value.date_to],
				]
			} else {
				filterObj.audit_date = ["<=", filters.value.date_to]
			}
		}
		if (overdueOnly.value) {
			filterObj.resolution_deadline = [
				"<",
				new Date().toISOString().split("T")[0],
			]
			filterObj.status = ["not in", ["Resolved", "Closed"]]
		}

		await store.loadStockTakeAudits(
			filterObj,
			currentPage.value,
			pageSize.value,
		)
		stockTakes.value = store.returnAudits
		totalCount.value = store.returnAuditsTotalCount
	} catch (error) {
		console.error("Error loading stock takes:", error)
	} finally {
		loading.value = false
	}
}

async function refreshData() {
	filters.value = {
		stock_take_type: "",
		status: "",
		warehouse: "",
		date_from: "",
		date_to: "",
	}
	overdueOnly.value = false
	currentPage.value = 1
	await loadStockTakes()
}

async function changePage(page) {
	currentPage.value = page
	await loadStockTakes()
}

function createStockTake() {
	router.push("/inventory-audit/stock-take/new")
}

function viewStockTake(name) {
	router.push(`/inventory-audit/stock-take/${name}`)
}

function isOverdue(stockTake) {
	if (!stockTake.resolution_deadline) return false
	if (["HOD Approved", "Under Investigation"].includes(stockTake.status))
		return false
	return new Date(stockTake.resolution_deadline) < new Date()
}

function getTypeVariant(type) {
	const variants = {
		"Sales Return": "orange",
		"Daily Stock Take": "blue",
		"Weekly Stock Take": "purple",
		"Monthly Stock Take": "green",
	}
	return variants[type] || "gray"
}

function getStatusVariant(status) {
	const variants = {
		Draft: "subtle",
		"Physical Count Submitted": "yellow",
		"Analyst Reviewed": "blue",
		"HOD Approved": "green",
		"Under Investigation": "red",
	}
	return variants[status] || "gray"
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
	return new Intl.NumberFormat("en-US", {
		style: "currency",
		currency: "KES",
		minimumFractionDigits: 0,
	}).format(amount || 0)
}

function onFileSelected(event) {
	const file = event.target.files[0]
	if (!file) return

	const reader = new FileReader()
	reader.onload = (e) => {
		csvContent.value = e.target.result
		parseCSV(csvContent.value)
	}
	reader.readAsText(file)
}

function parseCSV(content) {
	const lines = content.split("\n").filter((line) => line.trim())
	if (lines.length < 2) return

	const headers = lines[0].split(",").map((h) => h.trim().replace(/"/g, ""))
	importPreview.value = lines.slice(1).map((line) => {
		const values = line.split(",").map((v) => v.trim().replace(/"/g, ""))
		const row = {}
		headers.forEach((h, i) => {
			row[h] = values[i] || ""
		})
		return row
	})
}

async function confirmImport() {
	if (!importForm.value.warehouse) {
		alert("Please select a warehouse")
		return
	}

	importing.value = true
	try {
		const result = await call(
			"mkaguzi.inventory_audit.doctype.stock_take_audit.stock_take_audit.import_stock_take_from_csv",
			{
				file_content: csvContent.value,
				warehouse: importForm.value.warehouse,
				stock_take_type: importForm.value.stock_take_type,
				audit_date: importForm.value.audit_date,
			},
		)

		alert(`Successfully created ${result.audits.length} stock take(s)`)
		showImportModal.value = false
		importPreview.value = []
		csvContent.value = ""
		await loadStockTakes()
	} catch (error) {
		console.error("Import error:", error)
		alert("Import failed: " + error.message)
	} finally {
		importing.value = false
	}
}
</script>