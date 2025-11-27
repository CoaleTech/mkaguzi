<template>
  <div class="board-reports-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <Presentation class="title-icon" />
          Board Reports
        </h1>
        <p class="page-description">
          Executive-level reporting and strategic insights for board of directors
        </p>
      </div>
      <div class="header-actions">
        <Button variant="outline" @click="exportBoardReport">
          <Download />
          Export Report
        </Button>
        <Button variant="outline" @click="scheduleReport">
          <Calendar />
          Schedule Report
        </Button>
        <Button @click="createNewReport">
          <Plus />
          New Board Report
        </Button>
      </div>
    </div>

    <!-- Executive Summary Dashboard -->
    <!-- Executive Dashboard -->
    <BoardStats :board-metrics="boardMetrics" />

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Recent Board Reports -->
      <div class="reports-section">
        <div class="section-header">
          <h2>Recent Board Reports</h2>
          <Button variant="outline" size="sm" @click="viewAllReports">
            View All
          </Button>
        </div>

        <div class="reports-list">
          <div
            v-for="report in recentBoardReports"
            :key="report.name"
            class="report-card"
            @click="viewReport(report)"
          >
            <div class="report-header">
              <div class="report-title">
                <h4>{{ report.report_title }}</h4>
                <Badge :variant="getReportStatusVariant(report.report_status)">
                  {{ report.report_status }}
                </Badge>
              </div>
              <div class="report-meta">
                <span class="period">{{ report.reporting_period }}</span>
                <span class="date">{{ formatDate(report.report_date) }}</span>
              </div>
            </div>
            <div class="report-summary">
              <div class="summary-item">
                <span class="label">Key Findings:</span>
                <span class="value">{{ report.key_findings_count || 0 }}</span>
              </div>
              <div class="summary-item">
                <span class="label">Recommendations:</span>
                <span class="value">{{ report.recommendations_count || 0 }}</span>
              </div>
              <div class="summary-item">
                <span class="label">Risk Areas:</span>
                <span class="value">{{ report.risk_areas_count || 0 }}</span>
              </div>
            </div>
          </div>

          <div v-if="recentBoardReports.length === 0" class="empty-state">
            <Presentation class="empty-icon" />
            <h3>No Board Reports</h3>
            <p>Create your first board report to get started</p>
            <Button @click="createNewReport">
              <Plus />
              Create First Report
            </Button>
          </div>
        </div>
      </div>

      <!-- Key Risk Indicators -->
      <div class="risk-indicators-section">
        <div class="section-header">
          <h2>Key Risk Indicators</h2>
          <Button variant="outline" size="sm" @click="viewRiskDashboard">
            View Details
          </Button>
        </div>

        <div class="risk-indicators">
          <div
            v-for="indicator in keyRiskIndicators"
            :key="indicator.id"
            class="risk-indicator-card"
            :class="getRiskIndicatorClass(indicator.level)"
          >
            <div class="indicator-header">
              <div class="indicator-title">
                <h4>{{ indicator.title }}</h4>
                <Badge :variant="getRiskLevelVariant(indicator.level)">
                  {{ indicator.level }}
                </Badge>
              </div>
              <div class="indicator-value">
                {{ indicator.value }}
              </div>
            </div>
            <div class="indicator-description">
              {{ indicator.description }}
            </div>
            <div class="indicator-trend">
              <span :class="getTrendClass(indicator.trend)">
                {{ indicator.trend > 0 ? '↗' : indicator.trend < 0 ? '↘' : '→' }}
                {{ Math.abs(indicator.trend) }}% vs last period
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Audit Findings Overview -->
      <div class="findings-overview-section">
        <div class="section-header">
          <h2>Audit Findings Overview</h2>
          <Button variant="outline" size="sm" @click="viewFindings">
            View All Findings
          </Button>
        </div>

        <div class="findings-chart">
          <div class="chart-placeholder">
            <BarChart3 class="chart-icon" />
            <p>Findings by Risk Level</p>
          </div>
        </div>

        <div class="findings-summary">
          <div class="finding-category">
            <div class="category-header">
              <AlertTriangle class="category-icon high-risk" />
              <span>High Risk</span>
            </div>
            <div class="category-count">{{ findingsSummary.highRisk }}</div>
          </div>
          <div class="finding-category">
            <div class="category-header">
              <AlertCircle class="category-icon medium-risk" />
              <span>Medium Risk</span>
            </div>
            <div class="category-count">{{ findingsSummary.mediumRisk }}</div>
          </div>
          <div class="finding-category">
            <div class="category-header">
              <Info class="category-icon low-risk" />
              <span>Low Risk</span>
            </div>
            <div class="category-count">{{ findingsSummary.lowRisk }}</div>
          </div>
        </div>
      </div>

      <!-- Compliance Status -->
      <div class="compliance-section">
        <div class="section-header">
          <h2>Compliance Status</h2>
          <Button variant="outline" size="sm" @click="viewCompliance">
            View Details
          </Button>
        </div>

        <div class="compliance-overview">
          <div class="compliance-score">
            <div class="score-circle" :class="getComplianceScoreClass(boardMetrics.complianceScore)">
              <span class="score-value">{{ Math.round(boardMetrics.complianceScore) }}%</span>
              <span class="score-label">Overall</span>
            </div>
          </div>

          <div class="compliance-breakdown">
            <div class="compliance-item">
              <span class="item-label">Regulatory</span>
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: complianceBreakdown.regulatory + '%' }"
                  :class="getProgressClass(complianceBreakdown.regulatory)"
                ></div>
              </div>
              <span class="item-value">{{ complianceBreakdown.regulatory }}%</span>
            </div>
            <div class="compliance-item">
              <span class="item-label">Internal Policies</span>
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: complianceBreakdown.policies + '%' }"
                  :class="getProgressClass(complianceBreakdown.policies)"
                ></div>
              </div>
              <span class="item-value">{{ complianceBreakdown.policies }}%</span>
            </div>
            <div class="compliance-item">
              <span class="item-label">Industry Standards</span>
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: complianceBreakdown.standards + '%' }"
                  :class="getProgressClass(complianceBreakdown.standards)"
                ></div>
              </div>
              <span class="item-value">{{ complianceBreakdown.standards }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Strategic Recommendations -->
      <div class="recommendations-section">
        <div class="section-header">
          <h2>Strategic Recommendations</h2>
          <Button variant="outline" size="sm" @click="viewRecommendations">
            View All
          </Button>
        </div>

        <div class="recommendations-list">
          <div
            v-for="recommendation in strategicRecommendations"
            :key="recommendation.id"
            class="recommendation-card"
            :class="getRecommendationPriorityClass(recommendation.priority)"
          >
            <div class="recommendation-header">
              <div class="priority-indicator" :class="recommendation.priority.toLowerCase()"></div>
              <h4>{{ recommendation.title }}</h4>
              <Badge :variant="getPriorityVariant(recommendation.priority)">
                {{ recommendation.priority }}
              </Badge>
            </div>
            <p class="recommendation-description">{{ recommendation.description }}</p>
            <div class="recommendation-meta">
              <span class="category">{{ recommendation.category }}</span>
              <span class="timeline">{{ recommendation.timeline }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Board Meetings -->
      <div class="meetings-section">
        <div class="section-header">
          <h2>Upcoming Board Meetings</h2>
          <Button variant="outline" size="sm" @click="scheduleMeeting">
            Schedule Meeting
          </Button>
        </div>

        <div class="meetings-list">
          <div
            v-for="meeting in upcomingMeetings"
            :key="meeting.id"
            class="meeting-card"
          >
            <div class="meeting-date">
              <div class="date">{{ formatDate(meeting.date, 'dd') }}</div>
              <div class="month">{{ formatDate(meeting.date, 'MMM') }}</div>
            </div>
            <div class="meeting-details">
              <h4>{{ meeting.title }}</h4>
              <p class="meeting-time">{{ meeting.time }}</p>
              <p class="meeting-location">{{ meeting.location }}</p>
              <div class="meeting-agenda">
                <span class="agenda-label">Key Topics:</span>
                <span class="agenda-items">{{ meeting.agenda.join(', ') }}</span>
              </div>
            </div>
            <div class="meeting-actions">
              <Button variant="outline" size="sm" @click="prepareMaterials(meeting)">
                Prepare Materials
              </Button>
            </div>
          </div>

          <div v-if="upcomingMeetings.length === 0" class="empty-state">
            <Calendar class="empty-icon" />
            <h3>No Upcoming Meetings</h3>
            <p>Schedule your next board meeting</p>
            <Button @click="scheduleMeeting">
              <Calendar />
              Schedule Meeting
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Board Report Dialog -->
    <Dialog v-model="showCreateReportDialog" :options="{ title: 'Create New Board Report' }">
      <template #body-content>
        <BoardReportForm v-model:form-data="newReport" />
      </template>
      <template #actions>
        <Button variant="outline" @click="showCreateReportDialog = false">Cancel</Button>
        <Button @click="createReport" :loading="creating">Create Report</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Badge, Button, Dialog, FormControl } from "frappe-ui"
import {
	AlertCircle,
	AlertTriangle,
	BarChart3,
	Calendar,
	Download,
	Eye,
	Info,
	Plus,
	Presentation,
	ShieldCheck,
	Target,
	TrendingDown,
	TrendingUp,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useReportsStore } from "../stores/reports"
import BoardStats from "../components/board/BoardStats.vue"
import BoardReportForm from "../components/board/BoardReportForm.vue"

// Store
const reportsStore = useReportsStore()

// Reactive data
const showCreateReportDialog = ref(false)
const creating = ref(false)
const newReport = ref({
	title: "",
	period: "",
	type: "Comprehensive",
	presentationDate: "",
	focusAreas: "",
	notes: "",
})

// Computed properties
const recentBoardReports = computed(() => {
	return reportsStore.activeBoardReports.slice(0, 5)
})

// Mock data for demonstration (in real app, this would come from stores/APIs)
const boardMetrics = ref({
	auditCoverage: 87,
	auditCoverageTrend: 5.2,
	openFindings: 23,
	findingsTrend: -8,
	complianceScore: 92,
	complianceTrend: 3.1,
	overallRisk: "Medium",
})

const keyRiskIndicators = ref([
	{
		id: 1,
		title: "Financial Reporting Risk",
		level: "Medium",
		value: "78%",
		description: "Risk of material misstatement in financial statements",
		trend: 2.3,
	},
	{
		id: 2,
		title: "Cybersecurity Risk",
		level: "High",
		value: "85%",
		description: "Exposure to cyber threats and data breaches",
		trend: 12.5,
	},
	{
		id: 3,
		title: "Regulatory Compliance",
		level: "Low",
		value: "45%",
		description: "Compliance with new regulatory requirements",
		trend: -5.1,
	},
	{
		id: 4,
		title: "Operational Risk",
		level: "Medium",
		value: "62%",
		description: "Risk of operational disruptions",
		trend: 1.8,
	},
])

const findingsSummary = ref({
	highRisk: 5,
	mediumRisk: 12,
	lowRisk: 8,
})

const complianceBreakdown = ref({
	regulatory: 94,
	policies: 89,
	standards: 91,
})

const strategicRecommendations = ref([
	{
		id: 1,
		title: "Enhance Cybersecurity Framework",
		description:
			"Implement advanced threat detection and response capabilities",
		priority: "High",
		category: "Technology",
		timeline: "Q1 2026",
	},
	{
		id: 2,
		title: "Strengthen Internal Controls",
		description: "Review and update financial controls framework",
		priority: "High",
		category: "Finance",
		timeline: "Q2 2026",
	},
	{
		id: 3,
		title: "Risk Management Training",
		description: "Develop comprehensive risk management training program",
		priority: "Medium",
		category: "Human Resources",
		timeline: "Q3 2026",
	},
])

const upcomingMeetings = ref([
	{
		id: 1,
		title: "Q4 2025 Board Meeting",
		date: "2025-12-15",
		time: "10:00 AM - 4:00 PM",
		location: "Board Room A",
		agenda: [
			"Financial Results Review",
			"Risk Management Update",
			"Strategic Planning",
		],
	},
	{
		id: 2,
		title: "Annual Strategy Session",
		date: "2026-01-20",
		time: "9:00 AM - 5:00 PM",
		location: "Executive Conference Room",
		agenda: [
			"2026 Strategic Objectives",
			"Budget Planning",
			"Performance Targets",
		],
	},
])

// Methods
const createNewReport = () => {
	showCreateReportDialog.value = true
}

const createReport = async () => {
	try {
		creating.value = true
		await reportsStore.createBoardReport({
			report_title: newReport.value.title,
			reporting_period: newReport.value.period,
			report_type: newReport.value.type,
			presentation_date: newReport.value.presentationDate,
			focus_areas: newReport.value.focusAreas,
			additional_notes: newReport.value.notes,
			report_status: "Draft",
			is_active: 1,
		})

		showCreateReportDialog.value = false
		newReport.value = {
			title: "",
			period: "",
			type: "Comprehensive",
			presentationDate: "",
			focusAreas: "",
			notes: "",
		}
	} catch (error) {
		console.error("Error creating board report:", error)
	} finally {
		creating.value = false
	}
}

const viewReport = (report) => {
	router.push(`/reports/board-reports/${report.name}`)
}

const viewAllReports = () => {
	router.push('/reports/board-reports')
}

const exportBoardReport = () => {
	// TODO: Implement export functionality
	console.log("Export board report")
}

const scheduleReport = () => {
	// TODO: Implement schedule functionality
	console.log("Schedule report")
}

const viewRiskDashboard = () => {
	router.push('/audit-planning/risk-assessment')
}

const viewFindings = () => {
	router.push('/findings/list')
}

const viewCompliance = () => {
	router.push('/compliance/requirements')
}

const viewRecommendations = () => {
	router.push('/findings/corrective-actions')
}

const scheduleMeeting = () => {
	// TODO: Implement meeting scheduling
	console.log("Schedule meeting")
}

const prepareMaterials = (meeting) => {
	// TODO: Implement material preparation
	console.log("Prepare materials for:", meeting)
}

// Utility methods
const getReportStatusVariant = (status) => {
	const variants = {
		Draft: "secondary",
		"Under Review": "warning",
		Approved: "success",
		Finalized: "success",
		Presented: "success",
	}
	return variants[status] || "secondary"
}

const getRiskIndicatorClass = (level) => {
	return `risk-${level.toLowerCase()}`
}

const getRiskLevelVariant = (level) => {
	const variants = {
		Low: "success",
		Medium: "warning",
		High: "danger",
		Critical: "danger",
	}
	return variants[level] || "warning"
}

const getComplianceScoreClass = (score) => {
	if (score >= 90) return "excellent"
	if (score >= 80) return "good"
	if (score >= 70) return "fair"
	return "poor"
}

const getProgressClass = (value) => {
	if (value >= 90) return "excellent"
	if (value >= 80) return "good"
	if (value >= 70) return "fair"
	return "poor"
}

const getRecommendationPriorityClass = (priority) => {
	return `priority-${priority.toLowerCase()}`
}

const getPriorityVariant = (priority) => {
	const variants = {
		High: "danger",
		Medium: "warning",
		Low: "success",
	}
	return variants[priority] || "warning"
}

const getTrendClass = (trend) => {
	if (trend > 0) return "positive"
	if (trend < 0) return "negative"
	return "neutral"
}

const formatDate = (dateString, format = "medium") => {
	if (!dateString) return ""
	const date = new Date(dateString)

	if (format === "dd") {
		return date.getDate().toString().padStart(2, "0")
	}
	if (format === "MMM") {
		return date.toLocaleDateString("en-US", { month: "short" })
	}
	if (format === "short") {
		return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
	}
	if (format === "long") {
		return date.toLocaleDateString("en-US", {
			year: "numeric",
			month: "long",
			day: "numeric"
		})
	}

	// Default medium format
	return date.toLocaleDateString("en-US", {
		year: "numeric",
		month: "short",
		day: "numeric"
	})
}

// Lifecycle
onMounted(async () => {
	await reportsStore.fetchBoardReports()
})
</script>

<style scoped>
.board-reports-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.header-content h1 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.title-icon {
  color: var(--primary-color);
}

.page-description {
  color: var(--text-muted);
  margin: 0.5rem 0 0 0;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.reports-section,
.risk-indicators-section,
.findings-overview-section,
.compliance-section,
.recommendations-section,
.meetings-section {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.report-card {
  border: 1px solid var(--border-color-2);
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.report-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.report-title h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.report-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.period {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--primary-color);
}

.date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.summary-item {
  text-align: center;
}

.summary-item .label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.summary-item .value {
  display: block;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: var(--text-muted);
  margin: 0 0 1.5rem 0;
}

.risk-indicators {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.risk-indicator-card {
  border: 1px solid var(--border-color-2);
  border-radius: 0.5rem;
  padding: 1rem;
}

.risk-indicator-card.risk-low {
  border-left: 4px solid #10b981;
}

.risk-indicator-card.risk-medium {
  border-left: 4px solid #f59e0b;
}

.risk-indicator-card.risk-high {
  border-left: 4px solid #ef4444;
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.indicator-title h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.indicator-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
}

.indicator-description {
  color: var(--text-color);
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.indicator-trend {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.indicator-trend .positive {
  color: #10b981;
}

.indicator-trend .negative {
  color: #ef4444;
}

.indicator-trend .neutral {
  color: #6b7280;
}

.findings-chart {
  margin-bottom: 1.5rem;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  background: var(--background-color);
  border: 1px solid var(--border-color-2);
  border-radius: 0.5rem;
}

.chart-icon {
  font-size: 2rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.chart-placeholder p {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.findings-summary {
  display: flex;
  gap: 1.5rem;
}

.finding-category {
  flex: 1;
  text-align: center;
}

.category-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.category-icon {
  font-size: 1.25rem;
}

.category-icon.high-risk {
  color: #ef4444;
}

.category-icon.medium-risk {
  color: #f59e0b;
}

.category-icon.low-risk {
  color: #10b981;
}

.category-header span {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
}

.category-count {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
}

.compliance-overview {
  display: flex;
  gap: 2rem;
}

.compliance-score {
  flex: 1;
  display: flex;
  justify-content: center;
}

.score-circle {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 8px solid;
}

.score-circle.excellent {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.score-circle.good {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.score-circle.fair {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.score-circle.poor {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.score-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
}

.score-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.compliance-breakdown {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.compliance-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.item-label {
  min-width: 120px;
  font-size: 0.875rem;
  color: var(--text-color);
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--background-color);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.excellent {
  background: #10b981;
}

.progress-fill.good {
  background: #3b82f6;
}

.progress-fill.fair {
  background: #f59e0b;
}

.progress-fill.poor {
  background: #ef4444;
}

.item-value {
  min-width: 40px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  text-align: right;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recommendation-card {
  border: 1px solid var(--border-color-2);
  border-radius: 0.5rem;
  padding: 1rem;
}

.recommendation-card.priority-high {
  border-left: 4px solid #ef4444;
}

.recommendation-card.priority-medium {
  border-left: 4px solid #f59e0b;
}

.recommendation-card.priority-low {
  border-left: 4px solid #10b981;
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.priority-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.priority-indicator.high {
  background: #ef4444;
}

.priority-indicator.medium {
  background: #f59e0b;
}

.priority-indicator.low {
  background: #10b981;
}

.recommendation-header h4 {
  flex: 1;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.recommendation-description {
  color: var(--text-color);
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.recommendation-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category {
  font-size: 0.75rem;
  color: var(--primary-color);
  font-weight: 500;
}

.timeline {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.meetings-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.meeting-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid var(--border-color-2);
  border-radius: 0.5rem;
  padding: 1rem;
}

.meeting-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.date {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-color);
}

.month {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 500;
}

.meeting-details {
  flex: 1;
}

.meeting-details h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.meeting-time,
.meeting-location {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0.125rem 0;
}

.meeting-agenda {
  margin-top: 0.5rem;
}

.agenda-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
}

.agenda-items {
  font-size: 0.75rem;
  color: var(--text-color);
  margin-left: 0.5rem;
}

.meeting-actions {
  flex-shrink: 0;
}

/* Responsive design */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
  }

  .header-actions {
    width: 100%;
    justify-content: stretch;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .compliance-overview {
    flex-direction: column;
    gap: 1.5rem;
  }

  .meeting-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .meeting-date {
    align-self: flex-start;
  }

  .meeting-actions {
    width: 100%;
  }

  .meeting-actions .button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .board-reports-page {
    padding: 1rem;
  }

  .metric-card {
    padding: 1rem;
  }

  .metric-value {
    font-size: 1.5rem;
  }

  .report-summary {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .findings-summary {
    flex-direction: column;
    gap: 1rem;
  }

  .compliance-breakdown {
    gap: 0.75rem;
  }

  .compliance-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .item-label {
    min-width: auto;
  }

  .progress-bar {
    width: 100%;
  }
}
</style>