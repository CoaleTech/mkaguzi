<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Reports & Analytics</h1>
        <p class="text-gray-600">Comprehensive reporting and dashboard analytics</p>
      </div>
      <div class="flex gap-2">
        <Button @click="showCreateReportDialog = true" class="flex items-center gap-2">
          <Plus class="w-4 h-4" />
          Create Report
        </Button>
        <Button @click="showCreateDashboardDialog = true" variant="outline" class="flex items-center gap-2">
          <BarChart3 class="w-4 h-4" />
          Create Dashboard
        </Button>
      </div>
    </div>

    <!-- Summary Cards -->
    <ReportsStats
      :active-audit-reports="activeAuditReports"
      :active-board-reports="activeBoardReports"
      :active-dashboards="activeDashboards"
      :compliance-score="dashboardKPIs.complianceScore"
    />

    <!-- Report Categories -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Audit Reports Section -->
      <div class="bg-white rounded-lg border shadow-sm">
        <div class="p-4 border-b">
          <div class="flex justify-between items-center">
            <h2 class="text-lg font-semibold">Audit Reports</h2>
            <Button @click="createAuditReport" :loading="generating" variant="outline" size="sm">
              New Audit Report
            </Button>
          </div>
        </div>
        <div class="p-4">
          <div class="space-y-3">
            <div v-for="report in activeAuditReports.slice(0, 5)" :key="report.name" class="flex items-center justify-between p-3 border rounded">
              <div>
                <h4 class="font-medium">{{ report.report_title }}</h4>
                <p class="text-sm text-gray-600">{{ report.report_type }} • {{ formatDate(report.report_date) }}</p>
              </div>
              <div class="flex items-center gap-2">
                <Badge :variant="getReportStatusVariant(report.report_status)">
                  {{ report.report_status }}
                </Badge>
                <Button @click="viewAuditReport(report)" variant="ghost" size="sm">
                  <Eye class="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div v-if="activeAuditReports.length === 0" class="text-center py-4 text-gray-500">
              <FileText class="w-8 h-8 mx-auto mb-2 text-gray-300" />
              <p>No audit reports found</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Board Reports Section -->
      <div class="bg-white rounded-lg border shadow-sm">
        <div class="p-4 border-b">
          <div class="flex justify-between items-center">
            <h2 class="text-lg font-semibold">Board Reports</h2>
            <Button @click="createBoardReport" :loading="generating" variant="outline" size="sm">
              New Board Report
            </Button>
          </div>
        </div>
        <div class="p-4">
          <div class="space-y-3">
            <div v-for="report in activeBoardReports.slice(0, 5)" :key="report.name" class="flex items-center justify-between p-3 border rounded">
              <div>
                <h4 class="font-medium">{{ report.report_title }}</h4>
                <p class="text-sm text-gray-600">{{ report.reporting_period }} • {{ report.report_type }}</p>
              </div>
              <div class="flex items-center gap-2">
                <Badge :variant="getReportStatusVariant(report.report_status)">
                  {{ report.report_status }}
                </Badge>
                <Button @click="viewBoardReport(report)" variant="ghost" size="sm">
                  <Eye class="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div v-if="activeBoardReports.length === 0" class="text-center py-4 text-gray-500">
              <Users class="w-8 h-8 mx-auto mb-2 text-gray-300" />
              <p>No board reports found</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Management Dashboards Section -->
    <div class="bg-white rounded-lg border shadow-sm mb-6">
      <div class="p-4 border-b">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold">Management Dashboards</h2>
          <div class="flex gap-2">
            <Button @click="createDefaultDashboards" :loading="generating" variant="outline" size="sm">
              Create Defaults
            </Button>
            <Button @click="refreshAllDashboards" :loading="loading" variant="outline" size="sm">
              <RefreshCw class="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
      <div class="p-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="dashboard in activeDashboards" :key="dashboard.name" class="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <BarChart3 class="w-5 h-5 text-purple-500" />
                <h4 class="font-medium">{{ dashboard.dashboard_title }}</h4>
                <Badge v-if="dashboard.is_default" variant="success" size="sm">Default</Badge>
              </div>
              <Button @click="viewDashboard(dashboard)" variant="ghost" size="sm">
                <Eye class="w-4 h-4" />
              </Button>
            </div>
            <div class="space-y-2 text-sm">
              <p class="text-gray-600">{{ dashboard.dashboard_type }}</p>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <span class="text-gray-500">Engagements:</span>
                  <span class="font-medium">{{ dashboard.total_engagements || 0 }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Findings:</span>
                  <span class="font-medium">{{ dashboard.total_findings || 0 }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Compliance:</span>
                  <span class="font-medium">{{ Math.round(dashboard.compliance_score || 0) }}%</span>
                </div>
                <div>
                  <span class="text-gray-500">Updated:</span>
                  <span class="font-medium text-xs">{{ formatDate(dashboard.last_updated) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="activeDashboards.length === 0" class="col-span-full text-center py-8 text-gray-500">
            <BarChart3 class="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p class="text-lg font-medium mb-2">No dashboards found</p>
            <p class="mb-4">Create default dashboards to get started with analytics</p>
            <Button @click="createDefaultDashboards" :loading="generating">
              Create Default Dashboards
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Report Templates Section -->
    <div class="bg-white rounded-lg border shadow-sm">
      <div class="p-4 border-b">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold">Report Templates</h2>
          <Button @click="refreshTemplates" :loading="loading" variant="outline" size="sm">
            <RefreshCw class="w-4 h-4" />
          </Button>
        </div>
      </div>
      <div class="p-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="template in reportTemplates.filter(t => t.is_active)" :key="template.name" class="border rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <h4 class="font-medium">{{ template.template_name }}</h4>
              <Badge v-if="template.is_default" variant="success" size="sm">Default</Badge>
            </div>
            <p class="text-sm text-gray-600 mb-2">{{ template.template_type }}</p>
            <p class="text-xs text-gray-500">{{ template.description }}</p>
          </div>
          <div v-if="reportTemplates.filter(t => t.is_active).length === 0" class="col-span-full text-center py-8 text-gray-500">
            <FileText class="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No active report templates found</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Report Dialog -->
    <Dialog v-model="showCreateReportDialog" :options="{ title: 'Create New Report' }">
      <template #body-content>
        <div class="space-y-4">
          <FormControl label="Report Type" v-model="newReport.type" type="select" :options="reportTypeOptions" required />
          <FormControl v-if="newReport.type === 'audit'" label="Audit Engagement" v-model="newReport.engagement" type="link" doctype="Audit Engagement" required />
          <FormControl v-if="newReport.type === 'board'" label="Reporting Period" v-model="newReport.period" type="select" :options="periodOptions" required />
          <FormControl label="Report Title" v-model="newReport.title" type="text" placeholder="Enter report title" required />
          <FormControl label="Description" v-model="newReport.description" type="textarea" placeholder="Optional description" />
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showCreateReportDialog = false">Cancel</Button>
        <Button @click="createReport" :loading="generating">Create Report</Button>
      </template>
    </Dialog>

    <!-- Create Dashboard Dialog -->
    <Dialog v-model="showCreateDashboardDialog" :options="{ title: 'Create New Dashboard' }">
      <template #body-content>
        <div class="space-y-4">
          <FormControl label="Dashboard Type" v-model="newDashboard.type" type="select" :options="dashboardTypeOptions" required />
          <FormControl label="Dashboard Title" v-model="newDashboard.title" type="text" placeholder="Enter dashboard title" required />
          <FormControl label="Description" v-model="newDashboard.description" type="textarea" placeholder="Optional description" />
          <FormControl label="Time Period" v-model="newDashboard.timePeriod" type="select" :options="timePeriodOptions" required />
          <div class="flex items-center gap-2">
            <input type="checkbox" v-model="newDashboard.isDefault" class="rounded" />
            <label class="text-sm">Set as default dashboard</label>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showCreateDashboardDialog = false">Cancel</Button>
        <Button @click="createDashboard" :loading="generating">Create Dashboard</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import ReportsStats from "@/components/reports/ReportsStats.vue"
import { Badge, Button, Dialog, FormControl } from "frappe-ui"
import {
	BarChart3,
	Eye,
	FileText,
	Plus,
	RefreshCw,
	TrendingUp,
	Users,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useReportsStore } from "../stores/reports"

// Store
const reportsStore = useReportsStore()

// Reactive data
const showCreateReportDialog = ref(false)
const showCreateDashboardDialog = ref(false)
const generating = ref(false)
const newReport = ref({
	type: "audit",
	engagement: "",
	period: "",
	title: "",
	description: "",
})
const newDashboard = ref({
	type: "Management Overview",
	title: "",
	description: "",
	timePeriod: "Current Month",
	isDefault: false,
})

// Computed
const activeAuditReports = computed(() => reportsStore.activeAuditReports)
const activeBoardReports = computed(() => reportsStore.activeBoardReports)
const activeDashboards = computed(() => reportsStore.activeDashboards)
const dashboardKPIs = computed(() => reportsStore.dashboardKPIs)
const reportTemplates = computed(() => reportsStore.reportTemplates)
const loading = computed(() => reportsStore.loading)

// Options
const reportTypeOptions = [
	{ label: "Audit Report", value: "audit" },
	{ label: "Board Report", value: "board" },
]

const periodOptions = [
	{ label: "Q1", value: "Q1" },
	{ label: "Q2", value: "Q2" },
	{ label: "Q3", value: "Q3" },
	{ label: "Q4", value: "Q4" },
	{ label: "Annual", value: "Annual" },
]

const dashboardTypeOptions = [
	{ label: "Management Overview", value: "Management Overview" },
	{ label: "Compliance Dashboard", value: "Compliance Dashboard" },
	{ label: "Risk Dashboard", value: "Risk Dashboard" },
	{ label: "Operational Dashboard", value: "Operational Dashboard" },
	{ label: "Executive Summary", value: "Executive Summary" },
]

const timePeriodOptions = [
	{ label: "Current Month", value: "Current Month" },
	{ label: "Last Month", value: "Last Month" },
	{ label: "Current Quarter", value: "Current Quarter" },
	{ label: "Last Quarter", value: "Last Quarter" },
	{ label: "Current Year", value: "Current Year" },
	{ label: "Last Year", value: "Last Year" },
]

// Methods
const createAuditReport = async () => {
	try {
		generating.value = true
		// This would typically open a dialog or navigate to audit report creation
		console.log("Create audit report")
	} catch (error) {
		console.error("Error creating audit report:", error)
	} finally {
		generating.value = false
	}
}

const createBoardReport = async () => {
	try {
		generating.value = true
		// This would typically open a dialog or navigate to board report creation
		console.log("Create board report")
	} catch (error) {
		console.error("Error creating board report:", error)
	} finally {
		generating.value = false
	}
}

const createReport = async () => {
	try {
		generating.value = true

		if (newReport.value.type === "audit") {
			await reportsStore.createAuditReport({
				engagement_reference: newReport.value.engagement,
				report_title: newReport.value.title,
				report_type: "Full Audit Report",
				report_status: "Draft",
			})
		} else if (newReport.value.type === "board") {
			await reportsStore.createBoardReport({
				report_title: newReport.value.title,
				reporting_period: newReport.value.period,
				report_type: "Board Report",
				report_status: "Draft",
				is_active: 1,
			})
		}

		showCreateReportDialog.value = false
		newReport.value = {
			type: "audit",
			engagement: "",
			period: "",
			title: "",
			description: "",
		}
	} catch (error) {
		console.error("Error creating report:", error)
	} finally {
		generating.value = false
	}
}

const createDashboard = async () => {
	try {
		generating.value = true

		await reportsStore.createManagementDashboard({
			dashboard_title: newDashboard.value.title,
			dashboard_type: newDashboard.value.type,
			description: newDashboard.value.description,
			time_period: newDashboard.value.timePeriod,
			is_default: newDashboard.value.isDefault,
			is_active: 1,
			kpi_section: 1,
			compliance_section: 1,
			chart_configuration: 1,
		})

		showCreateDashboardDialog.value = false
		newDashboard.value = {
			type: "Management Overview",
			title: "",
			description: "",
			timePeriod: "Current Month",
			isDefault: false,
		}
	} catch (error) {
		console.error("Error creating dashboard:", error)
	} finally {
		generating.value = false
	}
}

const createDefaultDashboards = async () => {
	try {
		generating.value = true
		await reportsStore.createDefaultDashboards()
	} catch (error) {
		console.error("Error creating default dashboards:", error)
	} finally {
		generating.value = false
	}
}

const refreshAllDashboards = async () => {
	try {
		// Refresh all dashboards
		for (const dashboard of activeDashboards.value) {
			await reportsStore.refreshDashboard(dashboard.name)
		}
	} catch (error) {
		console.error("Error refreshing dashboards:", error)
	}
}

const refreshTemplates = async () => {
	await reportsStore.fetchReportTemplates()
}

const viewAuditReport = (report) => {
	// Navigate to audit report detail view
	console.log("View audit report:", report)
}

const viewBoardReport = (report) => {
	// Navigate to board report detail view
	console.log("View board report:", report)
}

const viewDashboard = (dashboard) => {
	// Navigate to dashboard view
	console.log("View dashboard:", dashboard)
}

const getScoreColor = (score) => {
	if (score >= 80) return "text-green-600"
	if (score >= 60) return "text-yellow-600"
	return "text-red-600"
}

const getReportStatusVariant = (status) => {
	const variants = {
		Draft: "secondary",
		"Under Review": "warning",
		Approved: "success",
		Finalized: "success",
		Issued: "success",
		Presented: "success",
		Archived: "secondary",
	}
	return variants[status] || "secondary"
}

const formatDate = (dateString) => {
	if (!dateString) return ""
	return new Date(dateString).toLocaleDateString()
}

// Lifecycle
onMounted(async () => {
	await reportsStore.fetchAuditReports()
	await reportsStore.fetchBoardReports()
	await reportsStore.fetchManagementDashboards()
	await reportsStore.fetchDataAnalyticsDashboards()
	await reportsStore.fetchReportTemplates()
})
</script>