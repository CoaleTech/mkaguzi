<template>
  <div class="compliance-reports">
    <!-- Header -->
    <div class="reports-header">
      <div class="header-left">
        <h3>Compliance Reports</h3>
        <p>Generate and manage compliance reports</p>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="showSchedulerModal = true">
          <Calendar class="w-4 h-4 mr-2" />
          Schedule Report
        </Button>
        
        <Button variant="solid" @click="showGeneratorModal = true">
          <FileText class="w-4 h-4 mr-2" />
          Generate Report
        </Button>
      </div>
    </div>

    <!-- Report Statistics -->
    <div class="report-stats">
      <div class="stat-card">
        <div class="stat-icon total">
          <FileText class="w-5 h-5" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalReports }}</div>
          <div class="stat-label">Total Reports</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon generated">
          <CheckCircle class="w-5 h-5" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ generatedThisMonth }}</div>
          <div class="stat-label">This Month</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon scheduled">
          <Clock class="w-5 h-5" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ scheduledReports }}</div>
          <div class="stat-label">Scheduled</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon shared">
          <Share2 class="w-5 h-5" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ sharedReports }}</div>
          <div class="stat-label">Shared</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filters">
        <FormControl
          type="text"
          v-model="searchQuery"
          placeholder="Search reports..."
          class="search-input"
        >
          <template #prefix>
            <Search class="w-4 h-4" />
          </template>
        </FormControl>
        
        <Dropdown :options="typeFilterOptions" @click="handleTypeFilter">
          <template #default>
            <Button variant="outline">
              <Filter class="w-4 h-4 mr-2" />
              {{ selectedType || 'All Types' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
        
        <Dropdown :options="statusFilterOptions" @click="handleStatusFilter">
          <template #default>
            <Button variant="outline">
              <component :is="getStatusIcon(selectedStatus)" class="w-4 h-4 mr-2" />
              {{ selectedStatus || 'All Status' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
        
        <Dropdown :options="frameworkFilterOptions" @click="handleFrameworkFilter">
          <template #default>
            <Button variant="outline">
              <Building class="w-4 h-4 mr-2" />
              {{ selectedFramework ? selectedFramework.name : 'All Frameworks' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
      </div>
      
      <div class="date-range">
        <FormControl
          type="date"
          v-model="dateRange.start"
          placeholder="Start date"
          size="sm"
        />
        <span class="date-separator">to</span>
        <FormControl
          type="date"
          v-model="dateRange.end"
          placeholder="End date"
          size="sm"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <Loader class="w-6 h-6 animate-spin" />
      <p>Loading reports...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredReports.length === 0" class="empty-state">
      <FileText class="w-16 h-16 text-gray-300" />
      <h4>{{ searchQuery ? 'No reports found' : 'No reports yet' }}</h4>
      <p>
        {{ searchQuery 
          ? 'Try adjusting your search terms or filters.' 
          : 'Generate your first compliance report to get started.' 
        }}
      </p>
      <Button v-if="!searchQuery" variant="solid" @click="showGeneratorModal = true">
        Generate Report
      </Button>
    </div>

    <!-- Reports Grid -->
    <div v-else class="reports-grid">
      <div
        v-for="report in paginatedReports"
        :key="report.id"
        class="report-card"
        :class="getReportCardClass(report)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="report-type">
            <component :is="getReportTypeIcon(report.type)" class="w-4 h-4" />
            <span>{{ report.type }}</span>
          </div>
          
          <Dropdown :options="getReportActions(report)" @click="handleAction">
            <template #default>
              <Button variant="ghost" size="sm">
                <MoreVertical class="w-4 h-4" />
              </Button>
            </template>
          </Dropdown>
        </div>

        <!-- Card Content -->
        <div class="card-content">
          <h4 class="report-title">{{ report.title }}</h4>
          <p class="report-description">{{ report.description }}</p>
          
          <div class="report-details">
            <div class="detail-row">
              <Building class="w-3 h-3" />
              <span>{{ getFrameworkName(report.framework_id) }}</span>
            </div>
            
            <div class="detail-row">
              <Calendar class="w-3 h-3" />
              <span>{{ formatDate(report.generated_date) }}</span>
            </div>
            
            <div class="detail-row">
              <User class="w-3 h-3" />
              <span>{{ report.generated_by }}</span>
            </div>
            
            <div v-if="report.scheduled" class="detail-row">
              <Clock class="w-3 h-3" />
              <span>{{ report.schedule_frequency }}</span>
            </div>
          </div>
          
          <!-- Report Metrics -->
          <div v-if="report.metrics" class="report-metrics">
            <div class="metric-item">
              <span class="metric-label">Compliance Score</span>
              <div class="metric-value">
                <div class="score-bar">
                  <div 
                    class="score-fill"
                    :style="{ width: report.metrics.compliance_score + '%' }"
                    :class="getScoreClass(report.metrics.compliance_score)"
                  ></div>
                </div>
                <span class="score-text">{{ report.metrics.compliance_score }}%</span>
              </div>
            </div>
            
            <div class="metrics-grid">
              <div class="metric-small">
                <span class="metric-number">{{ report.metrics.total_requirements }}</span>
                <span class="metric-text">Requirements</span>
              </div>
              
              <div class="metric-small">
                <span class="metric-number">{{ report.metrics.compliant }}</span>
                <span class="metric-text">Compliant</span>
              </div>
              
              <div class="metric-small">
                <span class="metric-number">{{ report.metrics.non_compliant }}</span>
                <span class="metric-text">Issues</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="status-section">
            <div 
              class="status-badge"
              :class="getStatusClass(report.status)"
            >
              <component :is="getStatusIcon(report.status)" class="w-3 h-3" />
              <span>{{ report.status }}</span>
            </div>
            
            <div v-if="report.file_size" class="file-info">
              <span class="file-size">{{ formatFileSize(report.file_size) }}</span>
              <span class="file-format">{{ report.format?.toUpperCase() }}</span>
            </div>
          </div>
          
          <div class="card-actions">
            <Button
              variant="ghost"
              size="sm"
              @click="downloadReport(report)"
              :disabled="report.status !== 'Completed'"
            >
              <Download class="w-3 h-3 mr-1" />
              Download
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              @click="shareReport(report)"
              :disabled="report.status !== 'Completed'"
            >
              <Share2 class="w-3 h-3 mr-1" />
              Share
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              @click="viewReport(report)"
              :disabled="report.status !== 'Completed'"
            >
              <Eye class="w-3 h-3 mr-1" />
              View
            </Button>
          </div>
        </div>

        <!-- Progress Bar for Generating Reports -->
        <div v-if="report.status === 'Generating'" class="progress-section">
          <div class="progress-header">
            <span>Generating...</span>
            <span>{{ report.progress }}%</span>
          </div>
          <div class="progress-bar">
            <div 
              class="progress-fill"
              :style="{ width: report.progress + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <div class="pagination-info">
        Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to 
        {{ Math.min(currentPage * itemsPerPage, filteredReports.length) }} of 
        {{ filteredReports.length }} reports
      </div>
      
      <div class="pagination-controls">
        <Button
          variant="outline"
          size="sm"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <ChevronLeft class="w-3 h-3" />
        </Button>
        
        <div class="page-numbers">
          <Button
            v-for="page in visiblePages"
            :key="page"
            variant="ghost"
            size="sm"
            :class="{ 'active': page === currentPage }"
            @click="currentPage = page"
          >
            {{ page }}
          </Button>
        </div>
        
        <Button
          variant="outline"
          size="sm"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          <ChevronRight class="w-3 h-3" />
        </Button>
      </div>
    </div>

    <!-- Report Generator Modal -->
    <Dialog
      v-if="showGeneratorModal"
      :options="{ title: 'Generate Compliance Report', size: 'xl' }"
      @close="showGeneratorModal = false"
    >
      <ReportGenerator
        :frameworks="frameworks"
        :templates="reportTemplates"
        @generate="handleGenerateReport"
        @cancel="showGeneratorModal = false"
      />
    </Dialog>

    <!-- Report Scheduler Modal -->
    <Dialog
      v-if="showSchedulerModal"
      :options="{ title: 'Schedule Report', size: 'lg' }"
      @close="showSchedulerModal = false"
    >
      <ReportScheduler
        :frameworks="frameworks"
        :templates="reportTemplates"
        @schedule="handleScheduleReport"
        @cancel="showSchedulerModal = false"
      />
    </Dialog>

    <!-- Share Report Modal -->
    <Dialog
      v-if="shareModalReport"
      :options="{ title: 'Share Report', size: 'md' }"
      @close="shareModalReport = null"
    >
      <ShareReportForm
        :report="shareModalReport"
        @share="handleShareReport"
        @cancel="shareModalReport = null"
      />
    </Dialog>

    <!-- Report Viewer Modal -->
    <Dialog
      v-if="viewModalReport"
      :options="{ title: 'Report Preview', size: 'full' }"
      @close="viewModalReport = null"
    >
      <ReportViewer
        :report="viewModalReport"
        @close="viewModalReport = null"
      />
    </Dialog>
  </div>
</template>

<script setup>
import { Button, Dialog, Dropdown, FormControl } from "frappe-ui"
import {
	AlertCircle,
	BarChart3,
	Building,
	Calendar,
	CheckCircle,
	ChevronDown,
	ChevronLeft,
	ChevronRight,
	Clock,
	Download,
	Eye,
	FileText,
	Filter,
	Loader,
	MoreVertical,
	PieChart,
	Search,
	Share2,
	TrendingUp,
	User,
	XCircle,
} from "lucide-vue-next"
import { computed, ref, watch } from "vue"

// Components
import ReportGenerator from "./ReportGenerator.vue"
import ReportScheduler from "./ReportScheduler.vue"
import ReportViewer from "./ReportViewer.vue"
import ShareReportForm from "./ShareReportForm.vue"

const props = defineProps({
	reports: {
		type: Array,
		default: () => [],
	},
	frameworks: {
		type: Array,
		default: () => [],
	},
	reportTemplates: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["generate", "schedule", "download", "share", "view"])

// Local state
const searchQuery = ref("")
const selectedType = ref("")
const selectedStatus = ref("")
const selectedFramework = ref(null)
const dateRange = ref({
	start: "",
	end: "",
})
const currentPage = ref(1)
const itemsPerPage = ref(12)
const showGeneratorModal = ref(false)
const showSchedulerModal = ref(false)
const shareModalReport = ref(null)
const viewModalReport = ref(null)

// Filter options
const typeFilterOptions = [
	{ label: "All Types", value: "" },
	{ label: "Compliance Summary", value: "Compliance Summary" },
	{ label: "Gap Analysis", value: "Gap Analysis" },
	{ label: "Risk Assessment", value: "Risk Assessment" },
	{ label: "Audit Report", value: "Audit Report" },
	{ label: "Management Report", value: "Management Report" },
	{ label: "Exception Report", value: "Exception Report" },
	{ label: "Trend Analysis", value: "Trend Analysis" },
	{ label: "Remediation Plan", value: "Remediation Plan" },
]

const statusFilterOptions = [
	{ label: "All Status", value: "" },
	{ label: "Completed", value: "Completed" },
	{ label: "Generating", value: "Generating" },
	{ label: "Failed", value: "Failed" },
	{ label: "Scheduled", value: "Scheduled" },
]

const frameworkFilterOptions = computed(() => {
	return [
		{ label: "All Frameworks", value: null },
		...props.frameworks.map((framework) => ({
			label: framework.name,
			value: framework,
		})),
	]
})

// Computed - Statistics
const totalReports = computed(() => props.reports.length)

const generatedThisMonth = computed(() => {
	const now = new Date()
	const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
	return props.reports.filter(
		(report) =>
			new Date(report.generated_date) >= startOfMonth &&
			report.status === "Completed",
	).length
})

const scheduledReports = computed(
	() =>
		props.reports.filter(
			(report) => report.scheduled && report.status === "Scheduled",
		).length,
)

const sharedReports = computed(
	() => props.reports.filter((report) => report.shared_count > 0).length,
)

// Computed - Filtered Data
const filteredReports = computed(() => {
	let filtered = [...props.reports]

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		filtered = filtered.filter(
			(report) =>
				report.title?.toLowerCase().includes(query) ||
				report.description?.toLowerCase().includes(query) ||
				report.type?.toLowerCase().includes(query) ||
				report.generated_by?.toLowerCase().includes(query),
		)
	}

	// Type filter
	if (selectedType.value) {
		filtered = filtered.filter((report) => report.type === selectedType.value)
	}

	// Status filter
	if (selectedStatus.value) {
		filtered = filtered.filter(
			(report) => report.status === selectedStatus.value,
		)
	}

	// Framework filter
	if (selectedFramework.value) {
		filtered = filtered.filter(
			(report) => report.framework_id === selectedFramework.value.id,
		)
	}

	// Date range filter
	if (dateRange.value.start) {
		filtered = filtered.filter(
			(report) =>
				new Date(report.generated_date) >= new Date(dateRange.value.start),
		)
	}

	if (dateRange.value.end) {
		filtered = filtered.filter(
			(report) =>
				new Date(report.generated_date) <= new Date(dateRange.value.end),
		)
	}

	// Sort by most recent
	filtered.sort(
		(a, b) => new Date(b.generated_date) - new Date(a.generated_date),
	)

	return filtered
})

const totalPages = computed(() =>
	Math.ceil(filteredReports.value.length / itemsPerPage.value),
)

const paginatedReports = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	return filteredReports.value.slice(start, start + itemsPerPage.value)
})

const visiblePages = computed(() => {
	const pages = []
	const total = totalPages.value
	const current = currentPage.value

	if (total <= 7) {
		for (let i = 1; i <= total; i++) {
			pages.push(i)
		}
	} else {
		if (current <= 4) {
			for (let i = 1; i <= 5; i++) pages.push(i)
			pages.push("...", total)
		} else if (current >= total - 3) {
			pages.push(1, "...")
			for (let i = total - 4; i <= total; i++) pages.push(i)
		} else {
			pages.push(1, "...")
			for (let i = current - 1; i <= current + 1; i++) pages.push(i)
			pages.push("...", total)
		}
	}

	return pages.filter(
		(p) => p !== "..." || pages.indexOf(p) === pages.lastIndexOf(p),
	)
})

// Methods
const handleTypeFilter = (option) => {
	selectedType.value = option.value
	currentPage.value = 1
}

const handleStatusFilter = (option) => {
	selectedStatus.value = option.value
	currentPage.value = 1
}

const handleFrameworkFilter = (option) => {
	selectedFramework.value = option.value
	currentPage.value = 1
}

const getFrameworkName = (frameworkId) => {
	const framework = props.frameworks.find((f) => f.id === frameworkId)
	return framework ? framework.name : "Multiple Frameworks"
}

const getReportTypeIcon = (type) => {
	const icons = {
		"Compliance Summary": BarChart3,
		"Gap Analysis": AlertCircle,
		"Risk Assessment": XCircle,
		"Audit Report": CheckCircle,
		"Management Report": TrendingUp,
		"Exception Report": AlertCircle,
		"Trend Analysis": TrendingUp,
		"Remediation Plan": FileText,
	}
	return icons[type] || FileText
}

const getStatusIcon = (status) => {
	const icons = {
		Completed: CheckCircle,
		Generating: Clock,
		Failed: XCircle,
		Scheduled: Calendar,
	}
	return icons[status] || AlertCircle
}

const getStatusClass = (status) => {
	return {
		"status-completed": status === "Completed",
		"status-generating": status === "Generating",
		"status-failed": status === "Failed",
		"status-scheduled": status === "Scheduled",
	}
}

const getReportCardClass = (report) => {
	return {
		"card-failed": report.status === "Failed",
		"card-generating": report.status === "Generating",
		"card-scheduled": report.scheduled,
	}
}

const getScoreClass = (score) => {
	if (score >= 80) return "score-good"
	if (score >= 60) return "score-medium"
	return "score-poor"
}

const formatDate = (dateString) => {
	return new Date(dateString).toLocaleDateString()
}

const formatFileSize = (bytes) => {
	if (bytes === 0) return "0 Bytes"
	const k = 1024
	const sizes = ["Bytes", "KB", "MB", "GB"]
	const i = Math.floor(Math.log(bytes) / Math.log(k))
	return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}

const getReportActions = (report) => [
	{
		label: "View Details",
		value: "details",
		action: () => console.log("View details", report.id),
	},
	{
		label: "Download",
		value: "download",
		action: () => downloadReport(report),
		disabled: report.status !== "Completed",
	},
	{
		label: "Share",
		value: "share",
		action: () => shareReport(report),
		disabled: report.status !== "Completed",
	},
	{
		label: "Duplicate",
		value: "duplicate",
		action: () => console.log("Duplicate", report.id),
	},
	{
		label: "Delete",
		value: "delete",
		action: () => console.log("Delete", report.id),
	},
]

const handleAction = (action) => {
	if (action.action && !action.disabled) {
		action.action()
	}
}

const downloadReport = (report) => {
	emit("download", report)
}

const shareReport = (report) => {
	shareModalReport.value = report
}

const viewReport = (report) => {
	viewModalReport.value = report
}

const handleGenerateReport = (reportData) => {
	emit("generate", reportData)
	showGeneratorModal.value = false
}

const handleScheduleReport = (scheduleData) => {
	emit("schedule", scheduleData)
	showSchedulerModal.value = false
}

const handleShareReport = (shareData) => {
	emit("share", { report: shareModalReport.value, ...shareData })
	shareModalReport.value = null
}

// Watchers
watch(
	[searchQuery, selectedType, selectedStatus, selectedFramework, dateRange],
	() => {
		currentPage.value = 1
	},
	{ deep: true },
)
</script>

<style scoped>
.compliance-reports {
  padding: 1.5rem;
}

.reports-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header-left h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.header-left p {
  color: var(--text-muted);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Report Statistics */
.report-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
}

.stat-icon {
  padding: 0.75rem;
  border-radius: 0.5rem;
  color: white;
}

.stat-icon.total {
  background: #6366f1;
}

.stat-icon.generated {
  background: #10b981;
}

.stat-icon.scheduled {
  background: #f59e0b;
}

.stat-icon.shared {
  background: #404040;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

/* Filters */
.filters-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.search-input {
  min-width: 300px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-separator {
  color: var(--text-muted);
  font-size: 0.875rem;
}

/* Loading and Empty States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  gap: 1.5rem;
}

.empty-state h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.empty-state p {
  color: var(--text-muted);
  margin: 0;
  max-width: 400px;
}

/* Reports Grid */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.report-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  transition: all 0.2s;
  position: relative;
}

.report-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.report-card.card-failed {
  border-left: 4px solid #ef4444;
}

.report-card.card-generating {
  border-left: 4px solid #3b82f6;
}

.report-card.card-scheduled {
  border-left: 4px solid #f59e0b;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.report-type {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: var(--background-color);
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-color);
}

.card-content {
  margin-bottom: 1.5rem;
}

.report-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.report-description {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin: 0 0 1rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.report-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Report Metrics */
.report-metrics {
  padding: 1rem;
  background: var(--background-color);
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.metric-item {
  margin-bottom: 1rem;
}

.metric-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  display: block;
  margin-bottom: 0.5rem;
}

.metric-value {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.score-bar {
  flex: 1;
  height: 0.5rem;
  background: #e5e7eb;
  border-radius: 0.25rem;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  transition: width 0.3s;
  border-radius: 0.25rem;
}

.score-fill.score-good {
  background: #10b981;
}

.score-fill.score-medium {
  background: #f59e0b;
}

.score-fill.score-poor {
  background: #ef4444;
}

.score-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  min-width: 2.5rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.metric-small {
  text-align: center;
}

.metric-number {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
}

.metric-text {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.status-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.status-completed {
  background: #dcfce7;
  color: #166534;
}

.status-badge.status-generating {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-badge.status-failed {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.status-scheduled {
  background: #fef3c7;
  color: #92400e;
}

.file-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.file-size {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.file-format {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-color);
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

/* Progress Section */
.progress-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.progress-bar {
  height: 0.5rem;
  background: var(--background-color);
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
}

.pagination-info {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.pagination-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.page-numbers .button.active {
  background: var(--primary-color);
  color: white;
}

/* Responsive */
@media (max-width: 1024px) {
  .reports-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
  
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .compliance-reports {
    padding: 1rem;
  }
  
  .reports-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .search-input {
    min-width: auto;
  }
  
  .reports-grid {
    grid-template-columns: 1fr;
  }
  
  .report-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .date-range {
    flex-direction: column;
    align-items: stretch;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .report-card {
    padding: 1rem;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .card-actions {
    justify-content: stretch;
  }
  
  .card-actions .button {
    flex: 1;
  }
  
  .report-stats {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>