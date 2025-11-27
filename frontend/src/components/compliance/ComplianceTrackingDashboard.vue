<template>
  <div class="compliance-tracking-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <h2>Compliance Dashboard</h2>
        <p>Monitor regulatory compliance across all frameworks and requirements</p>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="refreshData">
          <RefreshCw class="w-4 h-4 mr-2" />
          Refresh
        </Button>
        
        <Button variant="outline" @click="showReportGenerator = true">
          <FileText class="w-4 h-4 mr-2" />
          Generate Report
        </Button>
        
        <Dropdown :options="viewOptions" @click="handleViewChange">
          <template #default>
            <Button variant="solid">
              <component :is="currentViewIcon" class="w-4 h-4 mr-2" />
              {{ currentViewLabel }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
      </div>
    </div>

    <!-- Alerts Bar -->
    <div v-if="unreadAlerts.length > 0" class="alerts-bar">
      <div
        v-for="alert in unreadAlerts.slice(0, 3)"
        :key="alert.id"
        class="alert-item"
        :class="getAlertClass(alert.severity)"
      >
        <component :is="getAlertIcon(alert.type)" class="w-4 h-4" />
        <span class="alert-message">{{ alert.message }}</span>
        <div class="alert-actions">
          <Button variant="ghost" size="sm" @click="markAlertRead(alert.id)">
            <Check class="w-3 h-3" />
          </Button>
          <Button variant="ghost" size="sm" @click="dismissAlert(alert.id)">
            <X class="w-3 h-3" />
          </Button>
        </div>
      </div>
      
      <div v-if="unreadAlerts.length > 3" class="more-alerts">
        <Button variant="ghost" size="sm" @click="showAllAlerts = true">
          +{{ unreadAlerts.length - 3 }} more alerts
        </Button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="dashboard-content">
      <!-- Overview Dashboard -->
      <div v-if="currentView === 'dashboard'" class="overview-dashboard">
        <!-- Key Metrics -->
        <div class="metrics-grid">
          <div class="metric-card overall-score">
            <div class="metric-header">
              <h4>Overall Compliance Score</h4>
              <TrendingUp class="w-5 h-5" />
            </div>
            <div class="metric-content">
              <div class="score-display">
                <div class="score-value">{{ complianceStore.statistics.overallComplianceScore }}%</div>
                <div class="score-change positive">+2.3% from last month</div>
              </div>
              <div class="score-progress">
                <div 
                  class="progress-fill"
                  :style="{ width: `${complianceStore.statistics.overallComplianceScore}%` }"
                ></div>
              </div>
            </div>
          </div>
          
          <div class="metric-card compliant">
            <div class="metric-header">
              <h4>Compliant Requirements</h4>
              <Shield class="w-5 h-5" />
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ complianceStore.statistics.compliantRequirements }}</div>
              <div class="metric-total">of {{ complianceStore.statistics.totalRequirements }}</div>
            </div>
          </div>
          
          <div class="metric-card non-compliant">
            <div class="metric-header">
              <h4>Critical Issues</h4>
              <AlertTriangle class="w-5 h-5" />
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ complianceStore.statistics.criticalIssuesCount }}</div>
              <div class="metric-label">Require immediate attention</div>
            </div>
          </div>
          
          <div class="metric-card deadlines">
            <div class="metric-header">
              <h4>Upcoming Deadlines</h4>
              <Clock class="w-5 h-5" />
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ complianceStore.statistics.upcomingDeadlinesCount }}</div>
              <div class="metric-label">Next 30 days</div>
            </div>
          </div>
        </div>

        <!-- Framework Compliance Overview -->
        <div class="section">
          <h3>Framework Compliance Status</h3>
          <div class="frameworks-grid">
            <div
              v-for="framework in complianceStore.frameworks"
              :key="framework.id"
              class="framework-card"
              @click="selectFramework(framework)"
            >
              <div class="framework-header">
                <div class="framework-info">
                  <h5>{{ framework.name }}</h5>
                  <p>{{ framework.jurisdiction }} • {{ framework.category }}</p>
                </div>
                <div 
                  class="framework-score"
                  :style="{ color: framework.color }"
                >
                  {{ getFrameworkScore(framework.id) }}%
                </div>
              </div>
              
              <div class="framework-progress">
                <div 
                  class="progress-bar"
                  :style="{ backgroundColor: framework.color + '20' }"
                >
                  <div 
                    class="progress-fill"
                    :style="{ 
                      width: `${getFrameworkScore(framework.id)}%`,
                      backgroundColor: framework.color 
                    }"
                  ></div>
                </div>
              </div>
              
              <div class="framework-stats">
                <div class="stat-item">
                  <span class="stat-value">{{ getFrameworkRequirementsCount(framework.id) }}</span>
                  <span class="stat-label">Requirements</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">{{ getFrameworkIssuesCount(framework.id) }}</span>
                  <span class="stat-label">Issues</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="section">
          <div class="section-header">
            <h3>Recent Activity</h3>
            <Button variant="ghost" @click="setCurrentView('assessments')">
              View All
              <ArrowRight class="w-4 h-4 ml-2" />
            </Button>
          </div>
          
          <div class="activity-list">
            <div
              v-for="assessment in recentAssessments"
              :key="assessment.id"
              class="activity-item"
            >
              <div class="activity-icon">
                <component :is="getAssessmentIcon(assessment.score)" class="w-4 h-4" />
              </div>
              <div class="activity-content">
                <h6>{{ getRequirementTitle(assessment.requirement_id) }}</h6>
                <p>Assessment completed by {{ assessment.assessor }}</p>
                <div class="activity-meta">
                  <span class="activity-date">{{ formatRelativeTime(assessment.assessment_date) }}</span>
                  <span 
                    class="activity-score"
                    :class="getScoreClass(assessment.score)"
                  >
                    Score: {{ assessment.score }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Deadlines -->
        <div class="section">
          <div class="section-header">
            <h3>Upcoming Deadlines</h3>
            <Button variant="ghost" @click="setCurrentView('requirements')">
              View All
              <ArrowRight class="w-4 h-4 ml-2" />
            </Button>
          </div>
          
          <div class="deadlines-list">
            <div
              v-for="requirement in upcomingDeadlines.slice(0, 5)"
              :key="requirement.id"
              class="deadline-item"
              :class="getDeadlineUrgency(requirement.next_review_date)"
            >
              <div class="deadline-content">
                <h6>{{ requirement.title }}</h6>
                <p>{{ getFrameworkName(requirement.framework_id) }} • {{ requirement.section }}</p>
              </div>
              <div class="deadline-info">
                <div class="deadline-date">{{ formatDate(requirement.next_review_date) }}</div>
                <div class="deadline-days">{{ getDaysUntilDeadline(requirement.next_review_date) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Requirements View -->
      <div v-else-if="currentView === 'requirements'" class="requirements-view">
        <ComplianceRequirements
          :requirements="complianceStore.getFilteredRequirements"
          :frameworks="complianceStore.frameworks"
          :loading="complianceStore.isLoading"
          @create="handleCreateRequirement"
          @edit="handleEditRequirement"
          @assess="handleAssessRequirement"
          @remediate="handleCreateRemediation"
        />
      </div>

      <!-- Assessments View -->
      <div v-else-if="currentView === 'assessments'" class="assessments-view">
        <ComplianceAssessments
          :assessments="complianceStore.assessments"
          :requirements="complianceStore.requirements"
          :loading="complianceStore.isLoading"
          @create="handleCreateAssessment"
          @view="handleViewAssessment"
        />
      </div>

      <!-- Reports View -->
      <div v-else-if="currentView === 'reports'" class="reports-view">
        <ComplianceReports
          :reports="complianceStore.reports"
          :frameworks="complianceStore.frameworks"
          :loading="complianceStore.isLoading"
          @generate="handleGenerateReport"
          @download="handleDownloadReport"
        />
      </div>
    </div>

    <!-- Report Generator Modal -->
    <Dialog
      v-if="showReportGenerator"
      :options="{ title: 'Generate Compliance Report', size: 'lg' }"
      @close="showReportGenerator = false"
    >
      <ReportGenerator
        :frameworks="complianceStore.frameworks"
        :requirements="complianceStore.requirements"
        @generate="handleGenerateReport"
        @cancel="showReportGenerator = false"
      />
    </Dialog>

    <!-- All Alerts Modal -->
    <Dialog
      v-if="showAllAlerts"
      :options="{ title: 'All Alerts', size: 'md' }"
      @close="showAllAlerts = false"
    >
      <AlertsList
        :alerts="complianceStore.alerts"
        @mark-read="markAlertRead"
        @dismiss="dismissAlert"
      />
    </Dialog>

    <!-- Loading State -->
    <div v-if="complianceStore.isLoading" class="loading-overlay">
      <div class="loading-content">
        <Loader class="w-8 h-8 animate-spin" />
        <p>Loading compliance data...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="complianceStore.error" class="error-state">
      <div class="error-content">
        <AlertTriangle class="w-8 h-8 text-red-500" />
        <h4>Error Loading Compliance Data</h4>
        <p>{{ complianceStore.error }}</p>
        <Button @click="retryLoad" variant="solid">
          Retry
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Dialog, Dropdown } from "frappe-ui"
import {
	AlertCircle,
	AlertTriangle,
	ArrowRight,
	BarChart3,
	Calendar,
	Check,
	CheckCircle,
	ChevronDown,
	Clock,
	FileCheck,
	FileText,
	Loader,
	RefreshCw,
	Settings,
	Shield,
	TrendingUp,
	X,
	XCircle,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

import { useComplianceStore } from "../../stores/useComplianceStore"

import AlertsList from "./AlertsList.vue"
import ComplianceAssessments from "./ComplianceAssessments.vue"
import ComplianceReports from "./ComplianceReports.vue"
// Components (to be created)
import ComplianceRequirements from "./ComplianceRequirements.vue"
import ReportGenerator from "./ReportGenerator.vue"

// Store
const complianceStore = useComplianceStore()

// Local state
const showReportGenerator = ref(false)
const showAllAlerts = ref(false)

// View management
const currentView = computed(() => complianceStore.currentView)

const viewOptions = [
	{
		label: "Dashboard",
		value: "dashboard",
		icon: BarChart3,
	},
	{
		label: "Requirements",
		value: "requirements",
		icon: FileCheck,
	},
	{
		label: "Assessments",
		value: "assessments",
		icon: CheckCircle,
	},
	{
		label: "Reports",
		value: "reports",
		icon: FileText,
	},
]

const currentViewIcon = computed(() => {
	const view = viewOptions.find((v) => v.value === currentView.value)
	return view ? view.icon : BarChart3
})

const currentViewLabel = computed(() => {
	const view = viewOptions.find((v) => v.value === currentView.value)
	return view ? view.label : "Dashboard"
})

// Computed
const unreadAlerts = computed(() => {
	return complianceStore.alerts.filter((alert) => !alert.is_read)
})

const recentAssessments = computed(() => {
	return complianceStore.getRecentAssessments
})

const upcomingDeadlines = computed(() => {
	return complianceStore.getUpcomingDeadlines
})

// Methods
const refreshData = async () => {
	await complianceStore.loadComplianceData()
}

const handleViewChange = (option) => {
	complianceStore.setCurrentView(option.value)
}

const selectFramework = (framework) => {
	complianceStore.setFrameworkFilters([framework.id])
	complianceStore.setCurrentView("requirements")
}

const getFrameworkScore = (frameworkId) => {
	const scores = complianceStore.getComplianceScoreByFramework
	return scores[frameworkId] || 0
}

const getFrameworkRequirementsCount = (frameworkId) => {
	return complianceStore.getRequirementsByFramework(frameworkId).length
}

const getFrameworkIssuesCount = (frameworkId) => {
	return complianceStore
		.getRequirementsByFramework(frameworkId)
		.filter((req) => req.compliance_status === "Non-Compliant").length
}

const getFrameworkName = (frameworkId) => {
	const framework = complianceStore.getFrameworkById(frameworkId)
	return framework ? framework.name : "Unknown Framework"
}

const getRequirementTitle = (requirementId) => {
	const requirement = complianceStore.requirements.find(
		(req) => req.id === requirementId,
	)
	return requirement ? requirement.title : "Unknown Requirement"
}

const getAlertClass = (severity) => {
	return {
		"alert-high": severity === "High",
		"alert-medium": severity === "Medium",
		"alert-low": severity === "Low",
	}
}

const getAlertIcon = (type) => {
	const icons = {
		"Deadline Warning": Clock,
		"Compliance Issue": AlertTriangle,
		"Remediation Update": CheckCircle,
	}
	return icons[type] || AlertCircle
}

const getAssessmentIcon = (score) => {
	if (score >= 90) return CheckCircle
	if (score >= 70) return AlertCircle
	return XCircle
}

const getScoreClass = (score) => {
	return {
		"score-excellent": score >= 90,
		"score-good": score >= 70 && score < 90,
		"score-poor": score < 70,
	}
}

const getDeadlineUrgency = (deadlineDate) => {
	const days = getDaysUntilDeadlineNumber(deadlineDate)
	return {
		"deadline-overdue": days < 0,
		"deadline-urgent": days >= 0 && days <= 7,
		"deadline-warning": days > 7 && days <= 14,
	}
}

const getDaysUntilDeadline = (deadlineDate) => {
	const days = getDaysUntilDeadlineNumber(deadlineDate)
	if (days < 0) return "Overdue"
	if (days === 0) return "Today"
	if (days === 1) return "Tomorrow"
	return `${days} days`
}

const getDaysUntilDeadlineNumber = (deadlineDate) => {
	const today = new Date()
	const deadline = new Date(deadlineDate)
	const diffTime = deadline - today
	return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

const formatDate = (dateString) => {
	return new Date(dateString).toLocaleDateString()
}

const formatRelativeTime = (dateString) => {
	const now = new Date()
	const date = new Date(dateString)
	const diffMs = now - date

	const hours = Math.floor(diffMs / (1000 * 60 * 60))
	const days = Math.floor(diffMs / (1000 * 60 * 60 * 24))

	if (hours < 24) return `${hours}h ago`
	return `${days}d ago`
}

const markAlertRead = (alertId) => {
	complianceStore.markAlertAsRead(alertId)
}

const dismissAlert = (alertId) => {
	complianceStore.dismissAlert(alertId)
}

const setCurrentView = (view) => {
	complianceStore.setCurrentView(view)
}

// Event handlers
const handleCreateRequirement = (requirementData) => {
	// Handle requirement creation
	console.log("Create requirement:", requirementData)
}

const handleEditRequirement = (requirement) => {
	// Handle requirement editing
	console.log("Edit requirement:", requirement)
}

const handleAssessRequirement = (requirement) => {
	// Handle requirement assessment
	console.log("Assess requirement:", requirement)
}

const handleCreateRemediation = (requirement) => {
	// Handle remediation plan creation
	console.log("Create remediation:", requirement)
}

const handleCreateAssessment = (assessmentData) => {
	// Handle assessment creation
	console.log("Create assessment:", assessmentData)
}

const handleViewAssessment = (assessment) => {
	// Handle assessment viewing
	console.log("View assessment:", assessment)
}

const handleGenerateReport = (reportData) => {
	// Handle report generation
	console.log("Generate report:", reportData)
	showReportGenerator.value = false
}

const handleDownloadReport = (report) => {
	// Handle report download
	console.log("Download report:", report)
}

const retryLoad = async () => {
	complianceStore.clearError()
	await complianceStore.loadComplianceData()
}

// Lifecycle
onMounted(async () => {
	await complianceStore.loadComplianceData()
})
</script>

<style scoped>
.compliance-tracking-dashboard {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.header-content h2 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.header-content p {
  color: var(--text-muted);
  font-size: 1.125rem;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.alerts-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid;
  min-width: 0;
}

.alert-item.alert-high {
  background: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

.alert-item.alert-medium {
  background: #fefbf2;
  border-color: #fed7aa;
  color: #92400e;
}

.alert-item.alert-low {
  background: #f0f9ff;
  border-color: #bae6fd;
  color: #1e40af;
}

.alert-message {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alert-actions {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.more-alerts {
  flex-shrink: 0;
}

.dashboard-content {
  min-height: 600px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.metric-header h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.overall-score .metric-header {
  color: var(--primary-color);
}

.compliant .metric-header {
  color: #22c55e;
}

.non-compliant .metric-header {
  color: #ef4444;
}

.deadlines .metric-header {
  color: #f59e0b;
}

.metric-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.score-display {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.score-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.score-change {
  font-size: 0.875rem;
  font-weight: 500;
}

.score-change.positive {
  color: #22c55e;
}

.score-progress {
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
}

.metric-total {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.metric-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.section {
  margin-bottom: 2rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1.5rem 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.frameworks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.framework-card {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.framework-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.framework-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.framework-info h5 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.framework-info p {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0;
}

.framework-score {
  font-size: 1.5rem;
  font-weight: 700;
}

.framework-progress {
  margin-bottom: 1rem;
}

.progress-bar {
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
}

.framework-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 0.5rem;
}

.activity-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: var(--primary-light);
  color: var(--primary-color);
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-content h6 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.activity-content p {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0 0 0.5rem 0;
}

.activity-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.activity-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.activity-score {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.score-excellent {
  background: #dcfce7;
  color: #166534;
}

.score-good {
  background: #fef3c7;
  color: #92400e;
}

.score-poor {
  background: #fee2e2;
  color: #991b1b;
}

.deadlines-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.deadline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 0.5rem;
  border-left: 4px solid transparent;
}

.deadline-item.deadline-overdue {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.deadline-item.deadline-urgent {
  border-left-color: #f59e0b;
  background: #fefbf2;
}

.deadline-item.deadline-warning {
  border-left-color: #eab308;
  background: #fefce8;
}

.deadline-content h6 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.deadline-content p {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0;
}

.deadline-info {
  text-align: right;
}

.deadline-date {
  font-size: 0.875rem;
  color: var(--text-color);
  font-weight: 500;
}

.deadline-days {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.requirements-view,
.assessments-view,
.reports-view {
  background: white;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
  min-height: 500px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.loading-content p {
  color: var(--text-muted);
  margin: 0;
}

.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.error-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  max-width: 400px;
}

.error-content h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.error-content p {
  color: var(--text-muted);
  margin: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .alerts-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .alert-item {
    min-width: auto;
  }
  
  .alert-message {
    white-space: normal;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .compliance-tracking-dashboard {
    padding: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .frameworks-grid {
    grid-template-columns: 1fr;
  }
  
  .section {
    padding: 1rem;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .deadline-item {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .deadline-info {
    text-align: left;
  }
  
  .framework-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .framework-stats {
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .score-value {
    font-size: 2rem;
  }
  
  .metric-value {
    font-size: 1.5rem;
  }
  
  .framework-score {
    font-size: 1.25rem;
  }
  
  .activity-item {
    padding: 0.75rem;
  }
  
  .activity-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>