<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Anomaly Alerts</h1>
        <p class="text-gray-600 mt-1">Monitor and investigate detected anomalies</p>
      </div>
      <Button variant="outline" @click="refreshAlerts">
        <RefreshCwIcon class="h-4 w-4 mr-2" />
        Refresh
      </Button>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Total Alerts</p>
        <p class="text-2xl font-bold text-gray-900">{{ store.anomalyAlerts.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Open</p>
        <p class="text-2xl font-bold text-red-600">{{ store.openAlerts.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Critical</p>
        <p class="text-2xl font-bold text-red-700">{{ store.criticalAlerts.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Investigating</p>
        <p class="text-2xl font-bold text-yellow-600">{{ investigatingCount }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Resolved</p>
        <p class="text-2xl font-bold text-green-600">{{ resolvedCount }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="flex flex-wrap items-center gap-3">
        <FormControl type="text" v-model="search" placeholder="Search alerts..." class="w-52" />
        <FormControl
          type="select"
          v-model="filterSeverity"
          :options="[{ label: 'All Severities', value: '' }, { label: 'Critical', value: 'Critical' }, { label: 'High', value: 'High' }, { label: 'Medium', value: 'Medium' }, { label: 'Low', value: 'Low' }]"
          class="w-36"
        />
        <FormControl
          type="select"
          v-model="filterStatus"
          :options="[{ label: 'All Statuses', value: '' }, { label: 'Open', value: 'Open' }, { label: 'Investigating', value: 'Investigating' }, { label: 'Resolved', value: 'Resolved' }, { label: 'Closed', value: 'Closed' }, { label: 'False Positive', value: 'False Positive' }]"
          class="w-40"
        />
        <FormControl
          type="select"
          v-model="filterType"
          :options="alertTypeOptions"
          class="w-44"
        />
        <Button variant="outline" size="sm" @click="resetFilters">Clear</Button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <!-- Alert List -->
    <div v-else-if="filteredAlerts.length > 0" class="space-y-3">
      <div
        v-for="alert in paginatedAlerts"
        :key="alert.name"
        class="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow cursor-pointer"
        @click="showAlertDetail(alert)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-2">
              <Badge :variant="getSeverityVariant(alert.severity)">{{ alert.severity }}</Badge>
              <Badge :variant="getStatusVariant(alert.status)">{{ alert.status }}</Badge>
              <Badge variant="secondary">{{ alert.alert_type }}</Badge>
            </div>
            <p class="text-gray-900 font-medium">{{ alert.alert_description }}</p>
            <div class="flex items-center space-x-4 mt-2 text-sm text-gray-500">
              <span>{{ formatDateTime(alert.detected_date) }}</span>
              <span v-if="alert.source_doctype">Source: {{ alert.source_doctype }}</span>
              <span v-if="alert.assigned_to">Assigned: {{ alert.assigned_to }}</span>
              <span v-if="alert.confidence_score">Confidence: {{ Math.round(alert.confidence_score * 100) }}%</span>
            </div>
          </div>
          <ChevronRightIcon class="h-5 w-5 text-gray-400 flex-shrink-0" />
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="filteredAlerts.length > pageSize" class="flex items-center justify-between">
        <span class="text-sm text-gray-600">
          Showing {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, filteredAlerts.length) }} of {{ filteredAlerts.length }}
        </span>
        <div class="flex items-center space-x-2">
          <Button variant="outline" size="sm" :disabled="currentPage <= 1" @click="currentPage--">Previous</Button>
          <Button variant="outline" size="sm" :disabled="currentPage >= totalPages" @click="currentPage++">Next</Button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="bg-white rounded-lg border border-gray-200 p-12 text-center">
      <AlertTriangleIcon class="h-12 w-12 text-gray-300 mx-auto mb-3" />
      <p class="text-gray-600">No anomaly alerts found.</p>
    </div>

    <!-- Detail Dialog -->
    <Dialog v-model="showDetail" :options="{ title: 'Alert Details', size: 'xl' }">
      <template #body-content>
        <div v-if="selectedAlert" class="space-y-4">
          <div class="flex items-center space-x-3">
            <Badge :variant="getSeverityVariant(selectedAlert.severity)">{{ selectedAlert.severity }}</Badge>
            <Badge :variant="getStatusVariant(selectedAlert.status)">{{ selectedAlert.status }}</Badge>
            <Badge variant="secondary">{{ selectedAlert.alert_type }}</Badge>
          </div>

          <p class="text-gray-900">{{ selectedAlert.alert_description }}</p>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600">Alert ID</p>
              <p class="font-medium">{{ selectedAlert.alert_id }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Detected</p>
              <p class="font-medium">{{ formatDateTime(selectedAlert.detected_date) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Detection Method</p>
              <p class="font-medium">{{ selectedAlert.detection_method || '-' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Confidence Score</p>
              <p class="font-medium">{{ selectedAlert.confidence_score ? Math.round(selectedAlert.confidence_score * 100) + '%' : '-' }}</p>
            </div>
            <div v-if="selectedAlert.source_doctype">
              <p class="text-sm text-gray-600">Source</p>
              <p class="font-medium">{{ selectedAlert.source_doctype }}: {{ selectedAlert.source_document }}</p>
            </div>
            <div v-if="selectedAlert.threshold_breached">
              <p class="text-sm text-gray-600">Threshold Breached</p>
              <p class="font-medium">{{ selectedAlert.threshold_breached }}</p>
            </div>
          </div>

          <div v-if="selectedAlert.anomaly_details" class="mt-4">
            <p class="text-sm text-gray-600 mb-1">Anomaly Details</p>
            <pre class="bg-gray-50 rounded p-3 text-sm overflow-x-auto max-h-48">{{ formatJSON(selectedAlert.anomaly_details) }}</pre>
          </div>

          <div v-if="selectedAlert.preventive_actions" class="mt-4">
            <p class="text-sm text-gray-600 mb-1">Preventive Actions</p>
            <p class="text-sm text-gray-700">{{ selectedAlert.preventive_actions }}</p>
          </div>

          <!-- Status Actions -->
          <div class="flex items-center space-x-3 pt-4 border-t border-gray-200">
            <Button v-if="selectedAlert.status === 'Open'" @click="updateStatus('Investigating')" variant="outline">
              Mark Investigating
            </Button>
            <Button v-if="selectedAlert.status === 'Investigating'" @click="updateStatus('Resolved')">
              Mark Resolved
            </Button>
            <Button v-if="selectedAlert.status !== 'Closed' && selectedAlert.status !== 'False Positive'" variant="outline" @click="updateStatus('False Positive')">
              Mark False Positive
            </Button>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { useRiskMonitoringStore } from "@/stores/riskMonitoring"
import { Badge, Button, Dialog, FormControl, Spinner } from "frappe-ui"
import {
	AlertTriangleIcon,
	ChevronRightIcon,
	RefreshCwIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

const store = useRiskMonitoringStore()
const search = ref("")
const filterSeverity = ref("")
const filterStatus = ref("")
const filterType = ref("")
const currentPage = ref(1)
const pageSize = 20
const showDetail = ref(false)
const selectedAlert = ref(null)

const alertTypeOptions = [
	{ label: "All Types", value: "" },
	{ label: "Financial Anomaly", value: "Financial Anomaly" },
	{ label: "Timing Anomaly", value: "Timing Anomaly" },
	{ label: "Access Anomaly", value: "Access Anomaly" },
	{ label: "Volume Anomaly", value: "Volume Anomaly" },
	{ label: "Pattern Anomaly", value: "Pattern Anomaly" },
	{ label: "Predictive Alert", value: "Predictive Alert" },
]

const investigatingCount = computed(() => store.anomalyAlerts.filter((a) => a.status === "Investigating").length)
const resolvedCount = computed(() => store.anomalyAlerts.filter((a) => a.status === "Resolved").length)

const filteredAlerts = computed(() => {
	let result = store.anomalyAlerts
	if (search.value) {
		const q = search.value.toLowerCase()
		result = result.filter((a) => a.alert_description?.toLowerCase().includes(q) || a.alert_id?.toLowerCase().includes(q))
	}
	if (filterSeverity.value) result = result.filter((a) => a.severity === filterSeverity.value)
	if (filterStatus.value) result = result.filter((a) => a.status === filterStatus.value)
	if (filterType.value) result = result.filter((a) => a.alert_type === filterType.value)
	return result
})

const totalPages = computed(() => Math.ceil(filteredAlerts.value.length / pageSize))
const paginatedAlerts = computed(() => {
	const start = (currentPage.value - 1) * pageSize
	return filteredAlerts.value.slice(start, start + pageSize)
})

const getSeverityVariant = (s) => ({ Critical: "danger", High: "warning", Medium: "info", Low: "secondary" })[s] || "secondary"
const getStatusVariant = (s) => ({ Open: "danger", Investigating: "warning", Resolved: "success", Closed: "secondary", "False Positive": "subtle" })[s] || "secondary"

const formatDateTime = (dt) => dt ? new Date(dt).toLocaleString() : "-"
const formatJSON = (data) => {
	try { return JSON.stringify(JSON.parse(data), null, 2) } catch { return data }
}

const resetFilters = () => {
	search.value = ""
	filterSeverity.value = ""
	filterStatus.value = ""
	filterType.value = ""
	currentPage.value = 1
}

const showAlertDetail = async (alert) => {
	selectedAlert.value = alert
	const detail = await store.fetchAlertDetail(alert.name)
	if (detail) selectedAlert.value = detail
	showDetail.value = true
}

const updateStatus = async (status) => {
	if (!selectedAlert.value) return
	try {
		await store.updateAlertStatus(selectedAlert.value.name, status)
		selectedAlert.value.status = status
	} catch (err) {
		console.error("Status update failed:", err)
	}
}

const refreshAlerts = () => store.fetchAnomalyAlerts()

onMounted(() => {
	store.fetchAnomalyAlerts()
})
</script>
