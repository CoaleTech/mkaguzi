<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Data Quality</h1>
        <p class="text-gray-600 mt-1">
          Monitor data quality metrics and manage data validation rules
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export Report
        </Button>
        <Button @click="createNewRule">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Rule
        </Button>
      </div>
    </div>

    <!-- Quality Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <CheckCircleIcon class="h-6 w-6 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Overall Quality Score</p>
            <p class="text-2xl font-bold text-gray-900">{{ overallQualityScore }}%</p>
            <p class="text-xs text-green-600 mt-1">↑ 2.1% from last month</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <DatabaseIcon class="h-6 w-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Records Validated</p>
            <p class="text-2xl font-bold text-gray-900">{{ totalRecordsValidated }}</p>
            <p class="text-xs text-blue-600 mt-1">Last 30 days</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-red-100 rounded-lg">
            <AlertTriangleIcon class="h-6 w-6 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Active Alerts</p>
            <p class="text-2xl font-bold text-gray-900">{{ activeAlerts }}</p>
            <p class="text-xs text-red-600 mt-1">{{ criticalAlerts }} critical</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-gray-100 rounded-lg">
            <ShieldIcon class="h-6 w-6 text-gray-900" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Validation Rules</p>
            <p class="text-2xl font-bold text-gray-900">{{ validationRules.length }}</p>
            <p class="text-xs text-gray-900 mt-1">{{ activeRules }} active</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Quality Tabs -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="border-b border-gray-200">
        <nav class="flex">
          <button
            @click="activeTab = 'dashboard'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'dashboard'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Quality Dashboard
          </button>
          <button
            @click="activeTab = 'rules'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'rules'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Validation Rules
          </button>
          <button
            @click="activeTab = 'alerts'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'alerts'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Alerts & Issues
          </button>
          <button
            @click="activeTab = 'reports'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'reports'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Quality Reports
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Quality Dashboard Tab -->
        <div v-if="activeTab === 'dashboard'">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Quality Score Chart -->
            <div class="bg-white border border-gray-200 rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Quality Score Trend</h3>
              <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                <div class="text-center">
                  <BarChart3Icon class="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <p class="text-gray-500">Quality score chart will be displayed here</p>
                </div>
              </div>
            </div>

            <!-- Data Quality Metrics -->
            <div class="bg-white border border-gray-200 rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Data Quality Metrics</h3>
              <div class="space-y-4">
                <div v-for="metric in qualityMetrics" :key="metric.name" class="flex items-center justify-between">
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">{{ metric.label }}</p>
                    <p class="text-xs text-gray-500">{{ metric.description }}</p>
                  </div>
                  <div class="text-right">
                    <p class="text-lg font-bold text-gray-900">{{ metric.value }}%</p>
                    <p :class="['text-xs', metric.trend > 0 ? 'text-green-600' : 'text-red-600']">
                      {{ metric.trend > 0 ? '↑' : '↓' }} {{ Math.abs(metric.trend) }}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Quality Checks -->
          <div class="mt-6 bg-white border border-gray-200 rounded-lg p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Quality Checks</h3>
            <div class="space-y-4">
              <div v-for="check in recentQualityChecks" :key="check.id" class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-3">
                  <div :class="['w-3 h-3 rounded-full', getCheckStatusColor(check.status)]"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ check.rule_name }}</p>
                    <p class="text-xs text-gray-500">{{ check.doctype }} • {{ check.records_checked }} records</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-sm font-medium text-gray-900">{{ check.issues_found }} issues</p>
                  <p class="text-xs text-gray-500">{{ formatDate(check.checked_at) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Validation Rules Tab -->
        <div v-if="activeTab === 'rules'">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-medium text-gray-900">Validation Rules</h2>
            <Button @click="createNewRule">
              <PlusIcon class="h-4 w-4 mr-2" />
              New Rule
            </Button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              v-for="rule in validationRules"
              :key="rule.name"
              class="bg-white border border-gray-200 rounded-lg p-6"
            >
              <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                  <h3 class="text-lg font-medium text-gray-900 mb-1">
                    {{ rule.rule_name }}
                  </h3>
                  <p class="text-sm text-gray-600 mb-2">
                    {{ rule.description || 'Validation rule' }}
                  </p>
                  <div class="flex items-center space-x-2">
                    <Badge :variant="rule.is_active ? 'success' : 'secondary'">
                      {{ rule.is_active ? 'Active' : 'Inactive' }}
                    </Badge>
                    <Badge :variant="getRuleTypeVariant(rule.rule_type)">
                      {{ rule.rule_type }}
                    </Badge>
                  </div>
                </div>
                <Button variant="ghost" size="sm" @click="editRule(rule)">
                  <EditIcon class="h-4 w-4" />
                </Button>
              </div>

              <div class="space-y-2 text-sm text-gray-500">
                <div class="flex justify-between">
                  <span>DocType:</span>
                  <span>{{ rule.target_doctype }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Field:</span>
                  <span>{{ rule.target_field || 'All fields' }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Severity:</span>
                  <span>{{ rule.severity_level }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Last Run:</span>
                  <span>{{ rule.last_run ? formatDate(rule.last_run) : 'Never' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Alerts & Issues Tab -->
        <div v-if="activeTab === 'alerts'">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-medium text-gray-900">Alerts & Data Quality Issues</h2>
              <div class="flex items-center space-x-3">
                <Select
                  v-model="alertFilter"
                  :options="alertFilterOptions"
                  placeholder="Filter alerts"
                  class="w-40"
                />
                <Button variant="outline" @click="clearResolvedAlerts">
                  Clear Resolved
                </Button>
              </div>
            </div>

            <div class="space-y-4">
              <div
                v-for="alert in filteredAlerts"
                :key="alert.name"
                class="bg-white border border-gray-200 rounded-lg p-6"
              >
                <div class="flex items-start justify-between mb-4">
                  <div class="flex-1">
                    <div class="flex items-center space-x-2 mb-2">
                      <Badge :variant="getAlertSeverityVariant(alert.severity)">
                        {{ alert.severity }}
                      </Badge>
                      <Badge :variant="getAlertStatusVariant(alert.status)">
                        {{ alert.status }}
                      </Badge>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 mb-1">
                      {{ alert.alert_title }}
                    </h3>
                    <p class="text-sm text-gray-600 mb-2">
                      {{ alert.alert_description }}
                    </p>
                    <div class="text-sm text-gray-500">
                      Rule: {{ alert.rule_name }} • DocType: {{ alert.target_doctype }}
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <Button variant="ghost" size="sm" @click="viewAlertDetails(alert)">
                      View Details
                    </Button>
                    <Button
                      v-if="alert.status !== 'Resolved'"
                      variant="ghost"
                      size="sm"
                      @click="resolveAlert(alert)"
                    >
                      Resolve
                    </Button>
                  </div>
                </div>

                <div class="flex items-center justify-between text-sm text-gray-500">
                  <span>Created: {{ formatDate(alert.creation) }}</span>
                  <span>Affected Records: {{ alert.affected_records || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quality Reports Tab -->
        <div v-if="activeTab === 'reports'">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-medium text-gray-900">Quality Reports</h2>
              <Button @click="generateReport">
                <FileTextIcon class="h-4 w-4 mr-2" />
                Generate Report
              </Button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div
                v-for="report in qualityReports"
                :key="report.id"
                class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
                @click="viewReport(report)"
              >
                <div class="flex items-start justify-between mb-4">
                  <div class="flex-1">
                    <h3 class="text-lg font-medium text-gray-900 mb-1">
                      {{ report.report_name }}
                    </h3>
                    <p class="text-sm text-gray-600 mb-2">
                      {{ report.description }}
                    </p>
                    <Badge :variant="getReportStatusVariant(report.status)">
                      {{ report.status }}
                    </Badge>
                  </div>
                  <Button variant="ghost" size="sm" @click.stop="downloadReport(report)">
                    <DownloadIcon class="h-4 w-4" />
                  </Button>
                </div>

                <div class="text-sm text-gray-500">
                  Generated: {{ formatDate(report.generated_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useDataStore } from "@/stores/data"
import { Badge, Button, Select } from "frappe-ui"
import {
	AlertTriangleIcon,
	BarChart3Icon,
	CheckCircleIcon,
	DatabaseIcon,
	DownloadIcon,
	EditIcon,
	FileTextIcon,
	PlusIcon,
	ShieldIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const dataStore = useDataStore()

// Reactive state
const activeTab = ref("dashboard")
const alertFilter = ref("")
const loading = ref(false)

// Mock data for demonstration
const overallQualityScore = ref(87)
const totalRecordsValidated = ref(15420)
const activeAlerts = ref(12)
const criticalAlerts = ref(3)
const activeRules = ref(8)

const qualityMetrics = ref([
	{
		name: "completeness",
		label: "Data Completeness",
		description: "Percentage of required fields filled",
		value: 92,
		trend: 1.5,
	},
	{
		name: "accuracy",
		label: "Data Accuracy",
		description: "Percentage of accurate data entries",
		value: 89,
		trend: -0.8,
	},
	{
		name: "consistency",
		label: "Data Consistency",
		description: "Percentage of consistent data across records",
		value: 94,
		trend: 2.1,
	},
	{
		name: "timeliness",
		label: "Data Timeliness",
		description: "Percentage of data updated within timeframe",
		value: 78,
		trend: 3.2,
	},
])

const recentQualityChecks = ref([
	{
		id: 1,
		rule_name: "Required Field Validation",
		doctype: "Audit Engagement",
		records_checked: 150,
		issues_found: 5,
		status: "completed",
		checked_at: new Date().toISOString(),
	},
	{
		id: 2,
		rule_name: "Date Format Validation",
		doctype: "Finding",
		records_checked: 89,
		issues_found: 12,
		status: "completed",
		checked_at: new Date(Date.now() - 3600000).toISOString(),
	},
	{
		id: 3,
		rule_name: "Numeric Range Validation",
		doctype: "Working Paper",
		records_checked: 234,
		issues_found: 0,
		status: "completed",
		checked_at: new Date(Date.now() - 7200000).toISOString(),
	},
])

const validationRules = ref([
	{
		name: "rule_1",
		rule_name: "Required Field Check",
		description: "Ensures all required fields are filled",
		is_active: true,
		rule_type: "Required Field",
		target_doctype: "Audit Engagement",
		target_field: null,
		severity_level: "High",
		last_run: new Date().toISOString(),
	},
	{
		name: "rule_2",
		rule_name: "Date Format Validation",
		description: "Validates date fields are in correct format",
		is_active: true,
		rule_type: "Format Check",
		target_doctype: "Finding",
		target_field: "finding_date",
		severity_level: "Medium",
		last_run: new Date(Date.now() - 3600000).toISOString(),
	},
])

const alerts = ref([
	{
		name: "alert_1",
		alert_title: "Missing Required Fields",
		alert_description: "12 audit engagements have missing required fields",
		severity: "High",
		status: "Open",
		rule_name: "Required Field Check",
		target_doctype: "Audit Engagement",
		affected_records: 12,
		creation: new Date().toISOString(),
	},
	{
		name: "alert_2",
		alert_title: "Invalid Date Formats",
		alert_description: "8 findings have invalid date formats",
		severity: "Medium",
		status: "Open",
		rule_name: "Date Format Validation",
		target_doctype: "Finding",
		affected_records: 8,
		creation: new Date(Date.now() - 3600000).toISOString(),
	},
])

const qualityReports = ref([
	{
		id: 1,
		report_name: "Monthly Data Quality Report",
		description: "Comprehensive quality assessment for the current month",
		status: "Generated",
		generated_at: new Date().toISOString(),
	},
	{
		id: 2,
		report_name: "Critical Issues Summary",
		description: "Summary of all critical data quality issues",
		status: "Generated",
		generated_at: new Date(Date.now() - 86400000).toISOString(),
	},
])

// Computed properties
const alertFilterOptions = [
	{ label: "All Alerts", value: "" },
	{ label: "Open", value: "Open" },
	{ label: "Resolved", value: "Resolved" },
	{ label: "Critical", value: "Critical" },
]

const filteredAlerts = computed(() => {
	let filtered = alerts.value

	if (alertFilter.value === "Open") {
		filtered = filtered.filter((alert) => alert.status === "Open")
	} else if (alertFilter.value === "Resolved") {
		filtered = filtered.filter((alert) => alert.status === "Resolved")
	} else if (alertFilter.value === "Critical") {
		filtered = filtered.filter((alert) => alert.severity === "High")
	}

	return filtered
})

// Methods
const fetchData = async () => {
	loading.value = true
	try {
		await dataStore.fetchDataQualityMetrics()
	} catch (error) {
		console.error("Error loading data quality metrics:", error)
	} finally {
		loading.value = false
	}
}

const getCheckStatusColor = (status) => {
	const colors = {
		completed: "bg-green-500",
		failed: "bg-red-500",
		running: "bg-yellow-500",
	}
	return colors[status] || "bg-gray-500"
}

const getRuleTypeVariant = (type) => {
	const variants = {
		"Required Field": "warning",
		"Format Check": "info",
		"Range Check": "success",
		"Duplicate Check": "secondary",
		"Reference Check": "info",
	}
	return variants[type] || "secondary"
}

const getAlertSeverityVariant = (severity) => {
	const variants = {
		High: "danger",
		Medium: "warning",
		Low: "info",
	}
	return variants[severity] || "secondary"
}

const getAlertStatusVariant = (status) => {
	const variants = {
		Open: "warning",
		Resolved: "success",
		Dismissed: "secondary",
	}
	return variants[status] || "secondary"
}

const getReportStatusVariant = (status) => {
	const variants = {
		Generated: "success",
		Generating: "warning",
		Failed: "danger",
	}
	return variants[status] || "secondary"
}

const formatDate = (date) => {
	if (!date) return "N/A"
	return new Date(date).toLocaleString()
}

const createNewRule = () => {
	router.push("/data-quality/rule/new")
}

const editRule = (rule) => {
	router.push(`/data-quality/rule/${rule.name}/edit`)
}

const viewAlertDetails = (alert) => {
	router.push(`/data-quality/alert/${alert.name}`)
}

const resolveAlert = (alert) => {
	// Implement resolve alert logic
	alert.status = "Resolved"
}

const clearResolvedAlerts = () => {
	alerts.value = alerts.value.filter((alert) => alert.status !== "Resolved")
}

const generateReport = () => {
	router.push("/data-quality/report/generate")
}

const viewReport = (report) => {
	router.push(`/data-quality/report/${report.id}`)
}

const downloadReport = (report) => {
	// Implement download logic
	console.log("Downloading report:", report.report_name)
}

// Lifecycle
onMounted(async () => {
	await fetchData()
})
</script>