<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit GL Entries</h1>
        <p class="text-gray-600 mt-1">Flagged general ledger entries for review</p>
      </div>
      <Button variant="outline" @click="refreshEntries">
        <RefreshCwIcon class="h-4 w-4 mr-2" />
        Refresh
      </Button>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Total Entries</p>
        <p class="text-2xl font-bold text-gray-900">{{ entries.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Pending Review</p>
        <p class="text-2xl font-bold text-orange-600">{{ pendingCount }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Reviewed</p>
        <p class="text-2xl font-bold text-blue-600">{{ reviewedCount }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Acknowledged</p>
        <p class="text-2xl font-bold text-green-600">{{ acknowledgedCount }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="flex flex-wrap items-center gap-3">
        <FormControl type="text" v-model="search" placeholder="Search..." class="w-48" />
        <FormControl
          type="select"
          v-model="filterAnomalyType"
          :options="anomalyTypeOptions"
          class="w-48"
        />
        <FormControl
          type="select"
          v-model="filterStatus"
          :options="[{ label: 'All Statuses', value: '' }, { label: 'Pending', value: 'Pending' }, { label: 'Reviewed', value: 'Reviewed' }, { label: 'Acknowledged', value: 'Acknowledged' }]"
          class="w-36"
        />
        <FormControl type="date" v-model="filterFromDate" placeholder="From Date" class="w-40" />
        <FormControl type="date" v-model="filterToDate" placeholder="To Date" class="w-40" />
        <Button variant="outline" size="sm" @click="resetFilters">Clear</Button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <!-- Table -->
    <div v-else-if="filteredEntries.length > 0" class="bg-white rounded-lg border border-gray-200 overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-200 bg-gray-50">
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Name</th>
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Account</th>
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Posting Date</th>
            <th class="text-right text-xs font-medium text-gray-500 uppercase px-4 py-3">Debit</th>
            <th class="text-right text-xs font-medium text-gray-500 uppercase px-4 py-3">Credit</th>
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Risk Score</th>
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Anomaly</th>
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in paginatedEntries"
            :key="entry.name"
            class="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
            @click="showEntryDetail(entry)"
          >
            <td class="px-4 py-3 text-sm font-medium text-blue-600">{{ entry.name }}</td>
            <td class="px-4 py-3 text-sm text-gray-900">{{ entry.account }}</td>
            <td class="px-4 py-3 text-sm text-gray-600">{{ formatDate(entry.posting_date) }}</td>
            <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatCurrency(entry.debit_amount) }}</td>
            <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatCurrency(entry.credit_amount) }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center space-x-2">
                <div class="w-16 bg-gray-200 rounded-full h-2">
                  <div :class="['h-2 rounded-full', getRiskScoreColor(entry.risk_score)]" :style="{ width: entry.risk_score + '%' }"></div>
                </div>
                <span class="text-sm">{{ entry.risk_score }}%</span>
              </div>
            </td>
            <td class="px-4 py-3">
              <Badge v-if="entry.anomaly_type" variant="warning">{{ entry.anomaly_type }}</Badge>
              <span v-else class="text-sm text-gray-400">-</span>
            </td>
            <td class="px-4 py-3">
              <Badge :variant="getStatusVariant(entry.status)">{{ entry.status }}</Badge>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="filteredEntries.length > pageSize" class="flex items-center justify-between px-4 py-3 border-t border-gray-200">
        <span class="text-sm text-gray-600">
          {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, filteredEntries.length) }} of {{ filteredEntries.length }}
        </span>
        <div class="flex space-x-2">
          <Button variant="outline" size="sm" :disabled="currentPage <= 1" @click="currentPage--">Previous</Button>
          <Button variant="outline" size="sm" :disabled="currentPage >= totalPages" @click="currentPage++">Next</Button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="bg-white rounded-lg border border-gray-200 p-12 text-center">
      <BookOpenIcon class="h-12 w-12 text-gray-300 mx-auto mb-3" />
      <p class="text-gray-600">No flagged GL entries found.</p>
    </div>

    <!-- Detail Dialog -->
    <Dialog v-model="showDetail" :options="{ title: selectedEntry?.name || 'GL Entry Details', size: 'xl' }">
      <template #body-content>
        <div v-if="entryDetail" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600">GL Entry</p>
              <p class="font-medium">{{ entryDetail.gl_entry_link }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Account</p>
              <p class="font-medium">{{ entryDetail.account }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Posting Date</p>
              <p class="font-medium">{{ formatDate(entryDetail.posting_date) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Risk Score</p>
              <p class="font-medium" :class="entryDetail.risk_score >= 80 ? 'text-red-600' : entryDetail.risk_score >= 50 ? 'text-orange-600' : 'text-green-600'">
                {{ entryDetail.risk_score }}%
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Debit</p>
              <p class="font-medium">{{ formatCurrency(entryDetail.debit_amount) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Credit</p>
              <p class="font-medium">{{ formatCurrency(entryDetail.credit_amount) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Anomaly Type</p>
              <Badge v-if="entryDetail.anomaly_type" variant="warning">{{ entryDetail.anomaly_type }}</Badge>
              <span v-else>-</span>
            </div>
            <div>
              <p class="text-sm text-gray-600">Analyzed By</p>
              <p class="font-medium">{{ entryDetail.analyzed_by || '-' }}</p>
            </div>
          </div>
          <div v-if="entryDetail.findings">
            <p class="text-sm text-gray-600 mb-1">Analysis Findings</p>
            <p class="text-sm text-gray-700">{{ entryDetail.findings }}</p>
          </div>
          <div v-if="entryDetail.audit_remarks">
            <p class="text-sm text-gray-600 mb-1">Audit Remarks</p>
            <p class="text-sm text-gray-700">{{ entryDetail.audit_remarks }}</p>
          </div>
          <div v-if="entryDetail.voucher_type || entryDetail.party" class="grid grid-cols-2 gap-4 pt-3 border-t border-gray-200">
            <div v-if="entryDetail.voucher_type">
              <p class="text-sm text-gray-600">Voucher</p>
              <p class="font-medium">{{ entryDetail.voucher_type }}: {{ entryDetail.voucher_no }}</p>
            </div>
            <div v-if="entryDetail.party">
              <p class="text-sm text-gray-600">Party</p>
              <p class="font-medium">{{ entryDetail.party }}</p>
            </div>
            <div v-if="entryDetail.cost_center">
              <p class="text-sm text-gray-600">Cost Center</p>
              <p class="font-medium">{{ entryDetail.cost_center }}</p>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Badge, Button, Dialog, FormControl, Spinner } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	BookOpenIcon,
	RefreshCwIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

const loading = ref(false)
const entries = ref([])
const showDetail = ref(false)
const selectedEntry = ref(null)
const entryDetail = ref(null)
const search = ref("")
const filterAnomalyType = ref("")
const filterStatus = ref("")
const filterFromDate = ref("")
const filterToDate = ref("")
const currentPage = ref(1)
const pageSize = 25

const anomalyTypeOptions = [
	{ label: "All Types", value: "" },
	{ label: "Unusual Amount", value: "Unusual Amount" },
	{ label: "Round Figure Anomaly", value: "Round Figure Anomaly" },
	{ label: "Duplicate Entry", value: "Duplicate Entry" },
	{ label: "Timing Anomaly", value: "Timing Anomaly" },
	{ label: "Unusual Account Combination", value: "Unusual Account Combination" },
	{ label: "Missing Documentation", value: "Missing Documentation" },
	{ label: "Violation of Policy", value: "Violation of Policy" },
	{ label: "Other", value: "Other" },
]

const pendingCount = computed(() => entries.value.filter((e) => e.status === "Pending").length)
const reviewedCount = computed(() => entries.value.filter((e) => e.status === "Reviewed").length)
const acknowledgedCount = computed(() => entries.value.filter((e) => e.status === "Acknowledged").length)

const filteredEntries = computed(() => {
	let result = entries.value
	if (search.value) {
		const q = search.value.toLowerCase()
		result = result.filter((e) => e.account?.toLowerCase().includes(q) || e.name?.toLowerCase().includes(q) || e.findings?.toLowerCase().includes(q))
	}
	if (filterAnomalyType.value) result = result.filter((e) => e.anomaly_type === filterAnomalyType.value)
	if (filterStatus.value) result = result.filter((e) => e.status === filterStatus.value)
	if (filterFromDate.value) result = result.filter((e) => e.posting_date >= filterFromDate.value)
	if (filterToDate.value) result = result.filter((e) => e.posting_date <= filterToDate.value)
	return result
})

const totalPages = computed(() => Math.ceil(filteredEntries.value.length / pageSize))
const paginatedEntries = computed(() => {
	const start = (currentPage.value - 1) * pageSize
	return filteredEntries.value.slice(start, start + pageSize)
})

const getStatusVariant = (s) => ({ Pending: "warning", Reviewed: "info", Acknowledged: "success" })[s] || "secondary"
const getRiskScoreColor = (score) => {
	if (score >= 80) return "bg-red-500"
	if (score >= 50) return "bg-orange-500"
	return "bg-green-500"
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : "-"
const formatCurrency = (val) => {
	if (val == null || val === 0) return "-"
	return new Intl.NumberFormat(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val)
}

const resetFilters = () => {
	search.value = ""
	filterAnomalyType.value = ""
	filterStatus.value = ""
	filterFromDate.value = ""
	filterToDate.value = ""
	currentPage.value = 1
}

const fetchEntries = async () => {
	loading.value = true
	try {
		const res = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Audit GL Entry",
				fields: [
					"name", "gl_entry_link", "posting_date", "account",
					"debit_amount", "credit_amount", "risk_score",
					"anomaly_type", "status", "findings", "analyzed_by",
					"analysis_date", "docstatus",
				],
				order_by: "risk_score desc",
				limit_page_length: 500,
			},
		}).fetch()
		entries.value = res || []
	} catch (err) {
		console.error("Failed to fetch GL entries:", err)
	} finally {
		loading.value = false
	}
}

const showEntryDetail = async (entry) => {
	selectedEntry.value = entry
	entryDetail.value = null
	showDetail.value = true
	try {
		entryDetail.value = await createResource({
			url: "frappe.client.get",
			params: { doctype: "Audit GL Entry", name: entry.name },
		}).fetch()
	} catch (err) {
		console.error("Failed to load detail:", err)
	}
}

const refreshEntries = () => fetchEntries()

onMounted(() => {
	fetchEntries()
})
</script>
