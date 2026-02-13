<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Import Data</h1>
        <p class="text-gray-600 mt-1">
          Manage CSV imports and data import configurations
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Download Template
        </Button>
        <Button @click="createNewImportType">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Import Type
        </Button>
      </div>
    </div>

    <!-- Import Tabs -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="border-b border-gray-200">
        <nav class="flex">
          <button
            @click="activeTab = 'imports'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'imports'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Import Types
          </button>
          <button
            @click="activeTab = 'history'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'history'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Import History
          </button>
          <button
            @click="activeTab = 'bc-explorer'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'bc-explorer'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            BC Data Explorer
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Mode-specific content -->
        <div v-if="currentMode === 'new-import-type'" class="text-center py-12">
          <div class="max-w-md mx-auto">
            <PlusIcon class="h-16 w-16 text-blue-500 mx-auto mb-4" />
            <h2 class="text-2xl font-bold text-gray-900 mb-2">Create New Import Type</h2>
            <p class="text-gray-600 mb-6">
              This feature is under development. Please use the Import Types tab to create new import configurations.
            </p>
            <Button @click="goToImportData">
              <ArrowLeftIcon class="h-4 w-4 mr-2" />
              Back to Import Data
            </Button>
          </div>
        </div>

        <div v-else-if="currentMode === 'edit-import-type'" class="text-center py-12">
          <div class="max-w-md mx-auto">
            <EditIcon class="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 class="text-2xl font-bold text-gray-900 mb-2">Edit Import Type</h2>
            <p class="text-gray-600 mb-6">
              Editing import type: {{ importTypeId }}. This feature is under development.
            </p>
            <Button @click="goToImportData">
              <ArrowLeftIcon class="h-4 w-4 mr-2" />
              Back to Import Data
            </Button>
          </div>
        </div>

        <div v-else-if="currentMode === 'run-import'" class="text-center py-12">
          <div class="max-w-md mx-auto">
            <PlayIcon class="h-16 w-16 text-gray-900 mx-auto mb-4" />
            <h2 class="text-2xl font-bold text-gray-900 mb-2">Run Import</h2>
            <p class="text-gray-600 mb-6">
              Running import for type: {{ importTypeId }}. This feature is under development.
            </p>
            <Button @click="goToImportData">
              <ArrowLeftIcon class="h-4 w-4 mr-2" />
              Back to Import Data
            </Button>
          </div>
        </div>

        <div v-else-if="currentMode === 'view-history'" class="text-center py-12">
          <div class="max-w-md mx-auto">
            <HistoryIcon class="h-16 w-16 text-orange-500 mx-auto mb-4" />
            <h2 class="text-2xl font-bold text-gray-900 mb-2">Import History Details</h2>
            <p class="text-gray-600 mb-6">
              Viewing history for: {{ historyId }}. This feature is under development.
            </p>
            <Button @click="goToImportData">
              <ArrowLeftIcon class="h-4 w-4 mr-2" />
              Back to Import Data
            </Button>
          </div>
        </div>

        <div v-else-if="currentMode === 'new-mapping'" class="text-center py-12">
          <div class="max-w-md mx-auto">
            <MapIcon class="h-16 w-16 text-indigo-500 mx-auto mb-4" />
            <h2 class="text-2xl font-bold text-gray-900 mb-2">Create New Field Mapping</h2>
            <p class="text-gray-600 mb-6">
              This feature is under development. Please use the Field Mappings tab to create new mappings.
            </p>
            <Button @click="goToImportData">
              <ArrowLeftIcon class="h-4 w-4 mr-2" />
              Back to Import Data
            </Button>
          </div>
        </div>

        <div v-else-if="currentMode === 'edit-mapping'" class="text-center py-12">
          <div class="max-w-md mx-auto">
            <EditIcon class="h-16 w-16 text-teal-500 mx-auto mb-4" />
            <h2 class="text-2xl font-bold text-gray-900 mb-2">Edit Field Mapping</h2>
            <p class="text-gray-600 mb-6">
              Editing mapping: {{ mappingId }}. This feature is under development.
            </p>
            <Button @click="goToImportData">
              <ArrowLeftIcon class="h-4 w-4 mr-2" />
              Back to Import Data
            </Button>
          </div>
        </div>

        <!-- Regular tabs content -->
        <template v-else>
          <!-- Import Types Tab -->
          <div v-if="activeTab === 'imports'">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <!-- Create New Import Type Card -->
              <div
                class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-400 hover:bg-blue-50 cursor-pointer transition-colors"
                @click="createNewImportType"
              >
                <div class="flex flex-col items-center justify-center h-full">
                  <PlusIcon class="h-12 w-12 text-gray-400 mb-4" />
                  <h3 class="text-lg font-medium text-gray-900 mb-2">Create New Import Type</h3>
                  <p class="text-sm text-gray-600 text-center">
                    Define a new CSV import configuration
                  </p>
                </div>
              </div>

              <!-- Import Type Cards -->
              <div
                v-for="importType in dataStore.csvImportTypes"
                :key="importType.name"
                class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
              >
                <div class="flex items-start justify-between mb-4">
                  <div class="flex-1">
                    <h3 class="text-lg font-medium text-gray-900 mb-1">
                      {{ importType.import_type_name }}
                    </h3>
                    <p class="text-sm text-gray-600 mb-2">
                      {{ importType.description || 'No description' }}
                    </p>
                    <div class="flex items-center space-x-2">
                      <Badge :variant="importType.is_active ? 'success' : 'secondary'">
                        {{ importType.is_active ? 'Active' : 'Inactive' }}
                      </Badge>
                      <Badge :variant="getImportTypeVariant(importType.import_type)">
                        {{ importType.import_type }}
                      </Badge>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <Button variant="ghost" size="sm" @click.stop="editImportType(importType)">
                      <EditIcon class="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" @click.stop="runImport(importType)">
                      <PlayIcon class="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div class="space-y-2 text-sm text-gray-500">
                  <div class="flex justify-between">
                    <span>Target DocType:</span>
                    <span>{{ importType.target_doctype }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>Delimiter:</span>
                    <span>{{ importType.delimiter || ',' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>Has Header:</span>
                    <span>{{ importType.has_header ? 'Yes' : 'No' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Import History Tab -->
          <div v-if="activeTab === 'history'">
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-medium text-gray-900">Import History</h2>
                <div class="flex items-center space-x-3">
                  <Input
                    v-model="searchQuery"
                    placeholder="Search imports..."
                    class="w-64"
                  />
                  <Select
                    v-model="statusFilter"
                    :options="statusOptions"
                    placeholder="Filter by status"
                    class="w-40"
                  />
                </div>
              </div>

              <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Import Type
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Records
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Started
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Duration
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="history in filteredImportHistory" :key="history.name">
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm font-medium text-gray-900">
                          {{ history.import_type_name }}
                        </div>
                        <div class="text-sm text-gray-500">
                          {{ history.file_name }}
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <Badge :variant="getStatusVariant(history.status)">
                          {{ history.status }}
                        </Badge>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {{ history.records_processed }} / {{ history.total_records }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {{ formatDate(history.started_at) }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {{ history.duration || 'N/A' }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <Button variant="ghost" size="sm" @click="viewImportDetails(history)">
                          View Details
                        </Button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Field Mappings Tab -->
          <div v-if="activeTab === 'mappings'">
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-medium text-gray-900">Field Mappings</h2>
                <Button @click="createNewMapping">
                  <PlusIcon class="h-4 w-4 mr-2" />
                  New Mapping
                </Button>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div
                  v-for="mapping in dataStore.csvImportFieldMappings"
                  :key="mapping.name"
                  class="bg-white border border-gray-200 rounded-lg p-6"
                >
                  <div class="flex items-start justify-between mb-4">
                    <div class="flex-1">
                      <h3 class="text-lg font-medium text-gray-900 mb-1">
                        {{ mapping.import_type_name }}
                      </h3>
                      <p class="text-sm text-gray-600 mb-2">
                        {{ mapping.description || 'Field mapping configuration' }}
                      </p>
                      <div class="flex items-center space-x-2">
                        <Badge :variant="mapping.is_active ? 'success' : 'secondary'">
                          {{ mapping.is_active ? 'Active' : 'Inactive' }}
                        </Badge>
                        <Badge :variant="mapping.is_required ? 'warning' : 'secondary'">
                          {{ mapping.is_required ? 'Required' : 'Optional' }}
                        </Badge>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm" @click="editMapping(mapping)">
                      <EditIcon class="h-4 w-4" />
                    </Button>
                  </div>

                  <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                      <span class="text-gray-500">CSV Column:</span>
                      <span class="font-medium">{{ mapping.csv_column_name }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-500">Target Field:</span>
                      <span class="font-medium">{{ mapping.target_field_name }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-500">Data Type:</span>
                      <span class="font-medium">{{ mapping.data_type }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-500">Default Value:</span>
                      <span class="font-medium">{{ mapping.default_value || 'None' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- BC Data Explorer Tab -->
          <div v-if="activeTab === 'bc-explorer'">
            <div class="space-y-6">
              <!-- BC Data Sources Overview -->
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="bg-white border border-gray-200 rounded-lg p-6">
                  <div class="flex items-center">
                    <div class="p-2 bg-blue-100 rounded-lg">
                      <DatabaseIcon class="h-6 w-6 text-blue-600" />
                    </div>
                    <div class="ml-4">
                      <p class="text-sm font-medium text-gray-600">GL Entries</p>
                      <p class="text-2xl font-bold text-gray-900">{{ bcStats.glEntries }}</p>
                    </div>
                  </div>
                </div>

                <div class="bg-white border border-gray-200 rounded-lg p-6">
                  <div class="flex items-center">
                    <div class="p-2 bg-green-100 rounded-lg">
                      <UsersIcon class="h-6 w-6 text-green-600" />
                    </div>
                    <div class="ml-4">
                      <p class="text-sm font-medium text-gray-600">Customers</p>
                      <p class="text-2xl font-bold text-gray-900">{{ bcStats.customers }}</p>
                    </div>
                  </div>
                </div>

                <div class="bg-white border border-gray-200 rounded-lg p-6">
                  <div class="flex items-center">
                    <div class="p-2 bg-gray-100 rounded-lg">
                      <PackageIcon class="h-6 w-6 text-gray-900" />
                    </div>
                    <div class="ml-4">
                      <p class="text-sm font-medium text-gray-600">Items</p>
                      <p class="text-2xl font-bold text-gray-900">{{ bcStats.items }}</p>
                    </div>
                  </div>
                </div>

                <div class="bg-white border border-gray-200 rounded-lg p-6">
                  <div class="flex items-center">
                    <div class="p-2 bg-orange-100 rounded-lg">
                      <ReceiptIcon class="h-6 w-6 text-orange-600" />
                    </div>
                    <div class="ml-4">
                      <p class="text-sm font-medium text-gray-600">Sales Invoices</p>
                      <p class="text-2xl font-bold text-gray-900">{{ bcStats.salesInvoices }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <FileTextIcon class="h-6 w-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Import Types</p>
            <p class="text-2xl font-bold text-gray-900">{{ dataStore.csvImportTypes.length }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <CheckCircleIcon class="h-6 w-6 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Successful Imports</p>
            <p class="text-2xl font-bold text-gray-900">{{ successfulImports }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-red-100 rounded-lg">
            <AlertCircleIcon class="h-6 w-6 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Failed Imports</p>
            <p class="text-2xl font-bold text-gray-900">{{ failedImports }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-gray-100 rounded-lg">
            <MapIcon class="h-6 w-6 text-gray-900" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Field Mappings</p>
            <p class="text-2xl font-bold text-gray-900">{{ dataStore.csvImportFieldMappings.length }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useDataStore } from "@/stores/data"
import {
	BarElement,
	CategoryScale,
	Chart as ChartJS,
	Legend,
	LineElement,
	LinearScale,
	PointElement,
	Title,
	Tooltip,
} from "chart.js"
import { Badge, Button, Input, Select } from "frappe-ui"
import {
	AlertCircleIcon,
	ArrowLeftIcon,
	BarChart3Icon,
	CheckCircleIcon,
	ChevronDownIcon,
	ChevronLeftIcon,
	ChevronUpIcon,
	DatabaseIcon,
	DownloadIcon,
	EditIcon,
	FileTextIcon,
	FilterIcon,
	HistoryIcon,
	MapIcon,
	PackageIcon,
	PlayIcon,
	PlusIcon,
	ReceiptIcon,
	RefreshCwIcon,
	TrendingUpIcon,
	UsersIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"
import { Bar, Line } from "vue-chartjs"
import { useRouter } from "vue-router"

const props = defineProps({
	defaultTab: {
		type: String,
		default: "imports",
	},
	mode: {
		type: String,
		default: null,
	},
	importTypeId: {
		type: String,
		default: null,
	},
	historyId: {
		type: String,
		default: null,
	},
	mappingId: {
		type: String,
		default: null,
	},
})

// Register Chart.js components
ChartJS.register(
	CategoryScale,
	LinearScale,
	BarElement,
	LineElement,
	PointElement,
	Title,
	Tooltip,
	Legend,
)

const router = useRouter()
const dataStore = useDataStore()

// Reactive state
const activeTab = ref(props.defaultTab)
const searchQuery = ref("")
const statusFilter = ref("")
const loading = ref(false)

// Chart refs
const distributionChart = ref(null)
const trendsChart = ref(null)

// BC Explorer state
const selectedDataType = ref("")
const filters = ref({
	dateFrom: "",
	dateTo: "",
	search: "",
})
const sortField = ref("")
const sortOrder = ref("asc")
const currentPage = ref(1)
const pageSize = ref(25)
const bcData = ref([])
const bcStats = ref({
	glEntries: 0,
	customers: 0,
	items: 0,
	salesInvoices: 0,
})

// Computed properties
const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Success", value: "Success" },
	{ label: "Failed", value: "Failed" },
	{ label: "Processing", value: "Processing" },
	{ label: "Cancelled", value: "Cancelled" },
]

const filteredImportHistory = computed(() => {
	let history = dataStore.csvImportHistory

	// Apply search filter
	if (searchQuery.value) {
		const search = searchQuery.value.toLowerCase()
		history = history.filter(
			(item) =>
				item.import_type_name?.toLowerCase().includes(search) ||
				item.file_name?.toLowerCase().includes(search) ||
				item.status?.toLowerCase().includes(search),
		)
	}

	// Apply status filter
	if (statusFilter.value) {
		history = history.filter((item) => item.status === statusFilter.value)
	}

	return history
})

const successfulImports = computed(() => {
	return dataStore.csvImportHistory.filter((item) => item.status === "Success")
		.length
})

const failedImports = computed(() => {
	return dataStore.csvImportHistory.filter((item) => item.status === "Failed")
		.length
})

// BC Explorer computed properties
const dataTypeOptions = [
	{ label: "GL Entries", value: "gl_entries" },
	{ label: "Customers", value: "customers" },
	{ label: "Items", value: "items" },
	{ label: "Sales Invoices", value: "sales_invoices" },
	{ label: "Purchase Invoices", value: "purchase_invoices" },
	{ label: "Vendor Ledger", value: "vendor_ledger" },
]

const tableColumns = computed(() => {
	const columnsMap = {
		gl_entries: [
			{ key: "posting_date", label: "Posting Date", type: "date" },
			{ key: "document_no", label: "Document No", type: "string" },
			{ key: "account_no", label: "Account No", type: "string" },
			{ key: "description", label: "Description", type: "string" },
			{ key: "debit_amount", label: "Debit", type: "currency" },
			{ key: "credit_amount", label: "Credit", type: "currency" },
		],
		customers: [
			{ key: "no", label: "Customer No", type: "string" },
			{ key: "name", label: "Name", type: "string" },
			{ key: "address", label: "Address", type: "string" },
			{ key: "phone_no", label: "Phone", type: "string" },
			{ key: "email", label: "Email", type: "string" },
		],
		items: [
			{ key: "no", label: "Item No", type: "string" },
			{ key: "description", label: "Description", type: "string" },
			{ key: "unit_cost", label: "Unit Cost", type: "currency" },
			{ key: "unit_price", label: "Unit Price", type: "currency" },
			{ key: "inventory", label: "Inventory", type: "number" },
		],
		sales_invoices: [
			{ key: "no", label: "Invoice No", type: "string" },
			{ key: "posting_date", label: "Posting Date", type: "date" },
			{ key: "sell_to_customer_no", label: "Customer No", type: "string" },
			{ key: "sell_to_customer_name", label: "Customer Name", type: "string" },
			{ key: "amount", label: "Amount", type: "currency" },
			{ key: "status", label: "Status", type: "string" },
		],
	}
	return columnsMap[selectedDataType.value] || []
})

const filteredData = computed(() => {
	let data = [...bcData.value]

	// Apply search filter
	if (filters.value.search) {
		const search = filters.value.search.toLowerCase()
		data = data.filter((row) =>
			Object.values(row).some((value) =>
				String(value).toLowerCase().includes(search),
			),
		)
	}

	// Apply date filters
	if (filters.value.dateFrom) {
		data = data.filter((row) => {
			const date = new Date(row.posting_date || row.created_at)
			return date >= new Date(filters.value.dateFrom)
		})
	}
	if (filters.value.dateTo) {
		data = data.filter((row) => {
			const date = new Date(row.posting_date || row.created_at)
			return date <= new Date(filters.value.dateTo)
		})
	}

	// Apply sorting
	if (sortField.value) {
		data.sort((a, b) => {
			const aVal = a[sortField.value]
			const bVal = b[sortField.value]
			let result = 0
			if (aVal < bVal) result = -1
			if (aVal > bVal) result = 1
			return sortOrder.value === "desc" ? -result : result
		})
	}

	return data
})

const paginatedData = computed(() => {
	const start = (currentPage.value - 1) * pageSize.value
	const end = start + pageSize.value
	return filteredData.value.slice(start, end)
})

const totalPages = computed(() => {
	return Math.ceil(filteredData.value.length / pageSize.value)
})

// Mode handling
const currentMode = computed(() => {
	if (props.mode === "new-import-type") {
		return "new-import-type"
	}
	if (props.mode === "edit-import-type" && props.importTypeId) {
		return "edit-import-type"
	}
	if (props.mode === "run-import" && props.importTypeId) {
		return "run-import"
	}
	if (props.mode === "view-history" && props.historyId) {
		return "view-history"
	}
	if (props.mode === "new-mapping") {
		return "new-mapping"
	}
	if (props.mode === "edit-mapping" && props.mappingId) {
		return "edit-mapping"
	}
	return null
})

// Methods
	const fetchData = async () => {
		loading.value = true
		try {
			await Promise.all([
				dataStore.fetchCsvImportTypes(), // This now also fetches field mappings
				dataStore.fetchCsvImportHistory(),
			])
		} catch (error) {
			console.error("Error loading import data:", error)
		} finally {
			loading.value = false
		}
	}

const getImportTypeVariant = (type) => {
	const variants = {
		"Audit Data": "info",
		"Financial Data": "success",
		"Customer Data": "warning",
		"Inventory Data": "secondary",
		"Transaction Data": "info",
	}
	return variants[type] || "secondary"
}

const getStatusVariant = (status) => {
	const variants = {
		Success: "success",
		Failed: "danger",
		Processing: "warning",
		Cancelled: "secondary",
	}
	return variants[status] || "secondary"
}

const formatDate = (date) => {
	if (!date) return "N/A"
	return new Date(date).toLocaleString()
}

const createNewImportType = () => {
	router.push("/import-data/import-type/new")
}

const editImportType = (importType) => {
	router.push(`/import-data/import-type/${importType.name}/edit`)
}

const runImport = (importType) => {
	router.push(`/import-data/import-type/${importType.name}/run`)
}

const viewImportDetails = (history) => {
	router.push(`/import-data/history/${history.name}`)
}

const createNewMapping = () => {
	router.push("/import-data/mapping/new")
}

const editMapping = (mapping) => {
	router.push(`/import-data/mapping/${mapping.name}/edit`)
}

// BC Explorer methods
const refreshBCData = async () => {
	if (!selectedDataType.value) return

	loading.value = true
	try {
		// This would typically fetch data from the backend
		// For now, we'll simulate with mock data
		await loadMockBCData()
	} catch (error) {
		console.error("Error loading BC data:", error)
	} finally {
		loading.value = false
	}
}

const loadMockBCData = async () => {
	// Mock data for demonstration
	const mockData = {
		gl_entries: [
			{
				id: 1,
				posting_date: "2024-01-15",
				document_no: "INV001",
				account_no: "4000",
				description: "Sales Revenue",
				debit_amount: 0,
				credit_amount: 15000,
			},
			{
				id: 2,
				posting_date: "2024-01-15",
				document_no: "INV001",
				account_no: "1200",
				description: "Accounts Receivable",
				debit_amount: 15000,
				credit_amount: 0,
			},
		],
		customers: [
			{
				id: 1,
				no: "CUST001",
				name: "ABC Company Ltd",
				address: "123 Main St, Nairobi",
				phone_no: "+254700000000",
				email: "info@abc.com",
			},
		],
		items: [
			{
				id: 1,
				no: "ITEM001",
				description: "Office Chair",
				unit_cost: 5000,
				unit_price: 7500,
				inventory: 25,
			},
		],
		sales_invoices: [
			{
				id: 1,
				no: "SI001",
				posting_date: "2024-01-15",
				sell_to_customer_no: "CUST001",
				sell_to_customer_name: "ABC Company Ltd",
				amount: 15000,
				status: "Posted",
			},
		],
	}

	bcData.value = mockData[selectedDataType.value] || []

	// Update stats
	bcStats.value = {
		glEntries: mockData.gl_entries.length,
		customers: mockData.customers.length,
		items: mockData.items.length,
		salesInvoices: mockData.sales_invoices.length,
	}

	// Create charts after data is loaded
	setTimeout(() => {
		createDistributionChart()
		createTrendsChart()
	}, 100)
}

const applyFilters = () => {
	currentPage.value = 1
	// Filters are reactive, so the computed properties will update automatically
}

const sortBy = (field) => {
	if (sortField.value === field) {
		sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc"
	} else {
		sortField.value = field
		sortOrder.value = "asc"
	}
}

const formatCellValue = (value, type) => {
	if (!value) return "-"

	switch (type) {
		case "currency":
			return new Intl.NumberFormat("en-KE", {
				style: "currency",
				currency: "KES",
			}).format(value)
		case "date":
			return new Date(value).toLocaleDateString()
		case "number":
			return new Intl.NumberFormat().format(value)
		default:
			return String(value)
	}
}

const viewRecordDetails = (row) => {
	// Navigate to record details
	console.log("View record details:", row)
}

const goToImportData = () => {
	router.push("/data-management/import-wizard")
}

// Chart methods
const createDistributionChart = () => {
	if (!distributionChart.value) return

	const ctx = distributionChart.value.getContext("2d")
	const data = {
		labels: ["GL Entries", "Customers", "Items", "Sales Invoices"],
		datasets: [
			{
				label: "Record Count",
				data: [
					bcStats.value.glEntries,
					bcStats.value.customers,
					bcStats.value.items,
					bcStats.value.salesInvoices,
				],
				backgroundColor: [
					"rgba(59, 130, 246, 0.8)",
					"rgba(16, 185, 129, 0.8)",
					"rgba(139, 69, 19, 0.8)",
					"rgba(245, 158, 11, 0.8)",
				],
				borderColor: [
					"rgb(59, 130, 246)",
					"rgb(16, 185, 129)",
					"rgb(139, 69, 19)",
					"rgb(245, 158, 11)",
				],
				borderWidth: 1,
			},
		],
	}

	const config = {
		type: "bar",
		data: data,
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				legend: {
					position: "top",
				},
				title: {
					display: true,
					text: "Business Central Data Distribution",
				},
			},
		},
	}

	new ChartJS(ctx, config)
}

const createTrendsChart = () => {
	if (!trendsChart.value) return

	const ctx = trendsChart.value.getContext("2d")
	const data = {
		labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
		datasets: [
			{
				label: "GL Entries",
				data: [120, 150, 180, 200, 170, 190],
				borderColor: "rgb(59, 130, 246)",
				backgroundColor: "rgba(59, 130, 246, 0.5)",
			},
			{
				label: "Sales Invoices",
				data: [80, 90, 110, 130, 120, 140],
				borderColor: "rgb(16, 185, 129)",
				backgroundColor: "rgba(16, 185, 129, 0.5)",
			},
		],
	}

	const config = {
		type: "line",
		data: data,
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				legend: {
					position: "top",
				},
				title: {
					display: true,
					text: "Monthly Trends",
				},
			},
		},
	}

	new ChartJS(ctx, config)
}

// Lifecycle
onMounted(async () => {
	await fetchData()
})

// Watch for prop changes to update activeTab
watch(
	() => props.defaultTab,
	(newTab) => {
		activeTab.value = newTab
	},
)
</script>