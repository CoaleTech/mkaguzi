<template>
  <div class="integration-monitoring">
    <!-- Header -->
    <div class="monitoring-header">
      <div class="header-left">
        <h3>Integration Monitoring</h3>
        <p>Real-time monitoring and analytics for API integrations</p>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="refreshData">
          <RefreshCw class="w-4 h-4 mr-2" :class="{ 'animate-spin': refreshing }" />
          Refresh
        </Button>
        
        <Button variant="outline" @click="$emit('export')">
          <Download class="w-4 h-4 mr-2" />
          Export
        </Button>
        
        <Dropdown :options="timeRangeOptions" @click="handleTimeRangeChange">
          <template #default>
            <Button variant="outline">
              <Calendar class="w-4 h-4 mr-2" />
              {{ selectedTimeRange.label }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
      </div>
    </div>

    <!-- System Health Overview -->
    <div class="health-overview">
      <div class="health-card">
        <div class="health-content">
          <div class="health-status" :class="getOverallHealthClass(systemHealth.overall)">
            <component :is="getHealthIcon(systemHealth.overall)" class="w-6 h-6" />
            <span>{{ systemHealth.overall }}</span>
          </div>
          <div class="health-label">System Health</div>
        </div>
        <div class="health-details">
          <div class="detail-item">
            <span class="detail-label">Uptime</span>
            <span class="detail-value">{{ systemHealth.uptime }}%</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Active Integrations</span>
            <span class="detail-value">{{ systemHealth.active_integrations }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Avg Response</span>
            <span class="detail-value">{{ systemHealth.avg_response_time }}ms</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Metrics Dashboard -->
    <div class="metrics-dashboard">
      <!-- Performance Metrics -->
      <div class="metrics-section">
        <div class="section-header">
          <h4>Performance Metrics</h4>
          <div class="time-selector">
            <Button
              v-for="period in timePeriods"
              :key="period.value"
              variant="ghost"
              size="sm"
              :class="{ 'active': selectedPeriod === period.value }"
              @click="selectedPeriod = period.value"
            >
              {{ period.label }}
            </Button>
          </div>
        </div>
        
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-header">
              <div class="metric-icon">
                <Activity class="w-5 h-5 text-blue-500" />
              </div>
              <div class="metric-title">API Requests</div>
            </div>
            <div class="metric-value">{{ formatNumber(metrics.total_requests) }}</div>
            <div class="metric-trend" :class="getTrendClass(metrics.requests_trend)">
              <component :is="getTrendIcon(metrics.requests_trend)" class="w-3 h-3" />
              {{ Math.abs(metrics.requests_trend) }}% vs last period
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-header">
              <div class="metric-icon">
                <CheckCircle class="w-5 h-5 text-green-500" />
              </div>
              <div class="metric-title">Success Rate</div>
            </div>
            <div class="metric-value">{{ metrics.success_rate }}%</div>
            <div class="metric-trend" :class="getTrendClass(metrics.success_trend)">
              <component :is="getTrendIcon(metrics.success_trend)" class="w-3 h-3" />
              {{ Math.abs(metrics.success_trend) }}% vs last period
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-header">
              <div class="metric-icon">
                <Clock class="w-5 h-5 text-orange-500" />
              </div>
              <div class="metric-title">Avg Response Time</div>
            </div>
            <div class="metric-value">{{ metrics.avg_response_time }}ms</div>
            <div class="metric-trend" :class="getTrendClass(-metrics.response_time_trend)">
              <component :is="getTrendIcon(-metrics.response_time_trend)" class="w-3 h-3" />
              {{ Math.abs(metrics.response_time_trend) }}ms vs last period
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-header">
              <div class="metric-icon">
                <XCircle class="w-5 h-5 text-red-500" />
              </div>
              <div class="metric-title">Error Rate</div>
            </div>
            <div class="metric-value">{{ metrics.error_rate }}%</div>
            <div class="metric-trend" :class="getTrendClass(-metrics.error_trend)">
              <component :is="getTrendIcon(-metrics.error_trend)" class="w-3 h-3" />
              {{ Math.abs(metrics.error_trend) }}% vs last period
            </div>
          </div>
        </div>
      </div>

      <!-- Integration Status -->
      <div class="status-section">
        <div class="section-header">
          <h4>Integration Status</h4>
          <div class="status-filters">
            <Button
              v-for="filter in statusFilters"
              :key="filter.value"
              variant="ghost"
              size="sm"
              :class="{ 'active': selectedStatusFilter === filter.value }"
              @click="selectedStatusFilter = filter.value"
            >
              <component :is="filter.icon" class="w-3 h-3 mr-1" />
              {{ filter.label }}
            </Button>
          </div>
        </div>
        
        <div class="integrations-status">
          <div
            v-for="integration in filteredIntegrationStatus"
            :key="integration.id"
            class="integration-status-item"
          >
            <div class="status-info">
              <div class="status-header">
                <div class="integration-name">{{ integration.name }}</div>
                <div class="status-indicator" :class="getStatusClass(integration.status)">
                  <component :is="getStatusIcon(integration.status)" class="w-3 h-3" />
                  <span>{{ integration.status }}</span>
                </div>
              </div>
              
              <div class="status-metrics">
                <div class="metric-item">
                  <span class="metric-label">Uptime</span>
                  <span class="metric-value" :class="getUptimeClass(integration.uptime)">
                    {{ integration.uptime }}%
                  </span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Requests</span>
                  <span class="metric-value">{{ formatNumber(integration.requests) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Avg Response</span>
                  <span class="metric-value">{{ integration.avg_response_time }}ms</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Last Check</span>
                  <span class="metric-value">{{ formatRelativeTime(integration.last_check) }}</span>
                </div>
              </div>
              
              <div v-if="integration.last_error" class="status-error">
                <AlertCircle class="w-3 h-3" />
                <span>{{ integration.last_error }}</span>
              </div>
            </div>
            
            <div class="status-actions">
              <Button
                variant="ghost"
                size="sm"
                @click="$emit('testIntegration', integration)"
              >
                <Zap class="w-3 h-3" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                @click="$emit('viewLogs', integration)"
              >
                <FileText class="w-3 h-3" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                @click="$emit('viewDetails', integration)"
              >
                <Eye class="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Events -->
      <div class="events-section">
        <div class="section-header">
          <h4>Recent Events</h4>
          <div class="event-filters">
            <Button
              v-for="eventType in eventTypes"
              :key="eventType.value"
              variant="ghost"
              size="sm"
              :class="{ 'active': selectedEventType === eventType.value }"
              @click="selectedEventType = eventType.value"
            >
              <component :is="eventType.icon" class="w-3 h-3 mr-1" />
              {{ eventType.label }}
            </Button>
          </div>
        </div>
        
        <div class="events-list">
          <div
            v-for="event in filteredEvents"
            :key="event.id"
            class="event-item"
            :class="getEventClass(event.type)"
          >
            <div class="event-icon">
              <component :is="getEventIcon(event.type)" class="w-4 h-4" />
            </div>
            
            <div class="event-content">
              <div class="event-message">{{ event.message }}</div>
              <div class="event-details">
                <span class="event-integration">{{ event.integration_name }}</span>
                <span class="event-time">{{ formatRelativeTime(event.timestamp) }}</span>
              </div>
            </div>
            
            <div v-if="event.severity" class="event-severity" :class="getSeverityClass(event.severity)">
              {{ event.severity }}
            </div>
          </div>
        </div>
        
        <div v-if="filteredEvents.length === 0" class="empty-events">
          <Calendar class="w-8 h-8 text-gray-300" />
          <p>No events found for the selected criteria.</p>
        </div>
      </div>

      <!-- Alerts -->
      <div v-if="activeAlerts.length > 0" class="alerts-section">
        <div class="section-header">
          <h4>Active Alerts</h4>
          <Button
            variant="ghost"
            size="sm"
            @click="$emit('dismissAll')"
          >
            Dismiss All
          </Button>
        </div>
        
        <div class="alerts-list">
          <div
            v-for="alert in activeAlerts"
            :key="alert.id"
            class="alert-item"
            :class="getAlertClass(alert.severity)"
          >
            <div class="alert-icon">
              <component :is="getAlertIcon(alert.severity)" class="w-4 h-4" />
            </div>
            
            <div class="alert-content">
              <div class="alert-title">{{ alert.title }}</div>
              <div class="alert-message">{{ alert.message }}</div>
              <div class="alert-details">
                <span class="alert-integration">{{ alert.integration_name }}</span>
                <span class="alert-time">{{ formatRelativeTime(alert.created_at) }}</span>
              </div>
            </div>
            
            <div class="alert-actions">
              <Button
                variant="ghost"
                size="sm"
                @click="$emit('dismissAlert', alert)"
              >
                <X class="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Dropdown } from "frappe-ui"
import {
	Activity,
	AlertCircle,
	AlertTriangle,
	Calendar,
	CheckCircle,
	ChevronDown,
	Clock,
	Database,
	Download,
	Eye,
	FileText,
	Globe,
	Minus,
	RefreshCw,
	Shield,
	Sync,
	TrendingDown,
	TrendingUp,
	Webhook,
	X,
	XCircle,
	Zap,
} from "lucide-vue-next"
import { computed, ref } from "vue"

const props = defineProps({
	systemHealth: {
		type: Object,
		default: () => ({}),
	},
	metrics: {
		type: Object,
		default: () => ({}),
	},
	integrationStatus: {
		type: Array,
		default: () => [],
	},
	events: {
		type: Array,
		default: () => [],
	},
	activeAlerts: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits([
	"export",
	"testIntegration",
	"viewLogs",
	"viewDetails",
	"dismissAlert",
	"dismissAll",
])

// Local state
const refreshing = ref(false)
const selectedPeriod = ref("1h")
const selectedStatusFilter = ref("all")
const selectedEventType = ref("all")

// Time range options
const timeRangeOptions = [
	{ label: "Last 1 Hour", value: "1h" },
	{ label: "Last 6 Hours", value: "6h" },
	{ label: "Last 24 Hours", value: "24h" },
	{ label: "Last 7 Days", value: "7d" },
	{ label: "Last 30 Days", value: "30d" },
]

const selectedTimeRange = ref(timeRangeOptions[2]) // Default to 24h

const timePeriods = [
	{ label: "1H", value: "1h" },
	{ label: "6H", value: "6h" },
	{ label: "24H", value: "24h" },
	{ label: "7D", value: "7d" },
]

const statusFilters = [
	{ label: "All", value: "all", icon: Globe },
	{ label: "Healthy", value: "healthy", icon: CheckCircle },
	{ label: "Warning", value: "warning", icon: AlertTriangle },
	{ label: "Error", value: "error", icon: XCircle },
]

const eventTypes = [
	{ label: "All", value: "all", icon: Activity },
	{ label: "Success", value: "success", icon: CheckCircle },
	{ label: "Error", value: "error", icon: XCircle },
	{ label: "Warning", value: "warning", icon: AlertTriangle },
	{ label: "Sync", value: "sync", icon: Sync },
]

// Computed properties
const filteredIntegrationStatus = computed(() => {
	if (selectedStatusFilter.value === "all") {
		return props.integrationStatus
	}

	const statusMap = {
		healthy: "Healthy",
		warning: "Warning",
		error: "Error",
	}

	return props.integrationStatus.filter(
		(integration) =>
			integration.status === statusMap[selectedStatusFilter.value],
	)
})

const filteredEvents = computed(() => {
	let filtered = [...props.events]

	if (selectedEventType.value !== "all") {
		filtered = filtered.filter(
			(event) => event.type === selectedEventType.value,
		)
	}

	// Sort by timestamp (newest first)
	filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))

	// Limit to recent events
	return filtered.slice(0, 20)
})

// Methods
const refreshData = async () => {
	refreshing.value = true
	try {
		await new Promise((resolve) => setTimeout(resolve, 1000))
	} finally {
		refreshing.value = false
	}
}

const handleTimeRangeChange = (option) => {
	selectedTimeRange.value = option
}

const getOverallHealthClass = (health) => {
	return {
		"health-healthy": health === "Healthy",
		"health-warning": health === "Warning",
		"health-error": health === "Error" || health === "Critical",
	}
}

const getHealthIcon = (health) => {
	const icons = {
		Healthy: CheckCircle,
		Warning: AlertTriangle,
		Error: XCircle,
		Critical: XCircle,
	}
	return icons[health] || AlertCircle
}

const getTrendClass = (trend) => {
	if (trend > 0) return "trend-up"
	if (trend < 0) return "trend-down"
	return "trend-neutral"
}

const getTrendIcon = (trend) => {
	if (trend > 0) return TrendingUp
	if (trend < 0) return TrendingDown
	return Minus
}

const getStatusClass = (status) => {
	return {
		"status-healthy": status === "Healthy",
		"status-warning": status === "Warning",
		"status-error": status === "Error",
		"status-disconnected": status === "Disconnected",
	}
}

const getStatusIcon = (status) => {
	const icons = {
		Healthy: CheckCircle,
		Warning: AlertTriangle,
		Error: XCircle,
		Disconnected: XCircle,
	}
	return icons[status] || XCircle
}

const getUptimeClass = (uptime) => {
	if (uptime >= 99) return "uptime-excellent"
	if (uptime >= 95) return "uptime-good"
	if (uptime >= 90) return "uptime-warning"
	return "uptime-poor"
}

const getEventClass = (type) => {
	return {
		"event-success": type === "success",
		"event-error": type === "error",
		"event-warning": type === "warning",
		"event-sync": type === "sync",
	}
}

const getEventIcon = (type) => {
	const icons = {
		success: CheckCircle,
		error: XCircle,
		warning: AlertTriangle,
		sync: Sync,
		webhook: Webhook,
		connection: Globe,
	}
	return icons[type] || Activity
}

const getSeverityClass = (severity) => {
	return {
		"severity-low": severity === "Low",
		"severity-medium": severity === "Medium",
		"severity-high": severity === "High",
		"severity-critical": severity === "Critical",
	}
}

const getAlertClass = (severity) => {
	return {
		"alert-low": severity === "Low",
		"alert-medium": severity === "Medium",
		"alert-high": severity === "High",
		"alert-critical": severity === "Critical",
	}
}

const getAlertIcon = (severity) => {
	const icons = {
		Low: AlertCircle,
		Medium: AlertTriangle,
		High: XCircle,
		Critical: XCircle,
	}
	return icons[severity] || AlertCircle
}

const formatNumber = (num) => {
	if (!num) return "0"
	if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
	if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
	return num.toString()
}

const formatRelativeTime = (dateString) => {
	if (!dateString) return "Never"

	const date = new Date(dateString)
	const now = new Date()
	const diffMs = now - date
	const diffMins = Math.floor(diffMs / (1000 * 60))
	const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
	const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

	if (diffMins < 1) return "Just now"
	if (diffMins < 60) return `${diffMins}m ago`
	if (diffHours < 24) return `${diffHours}h ago`
	return `${diffDays}d ago`
}
</script>

<style scoped>
.integration-monitoring {
  padding: 0;
}

.monitoring-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.header-left h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.header-left p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Health Overview */
.health-overview {
  margin-bottom: 2rem;
}

.health-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.health-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.health-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.health-status.health-healthy {
  color: #059669;
}

.health-status.health-warning {
  color: #d97706;
}

.health-status.health-error {
  color: #dc2626;
}

.health-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-weight: 500;
}

.health-details {
  display: flex;
  gap: 2rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
}

/* Metrics Dashboard */
.metrics-dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.metrics-section,
.status-section,
.events-section,
.alerts-section {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.time-selector,
.status-filters,
.event-filters {
  display: flex;
  gap: 0.25rem;
}

.time-selector .button.active,
.status-filters .button.active,
.event-filters .button.active {
  background: var(--primary-color);
  color: white;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.metric-card {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.25rem;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.metric-icon {
  flex-shrink: 0;
}

.metric-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-muted);
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.metric-trend.trend-up {
  color: #059669;
}

.metric-trend.trend-down {
  color: #dc2626;
}

.metric-trend.trend-neutral {
  color: var(--text-muted);
}

/* Integration Status */
.integrations-status {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.integration-status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.status-info {
  flex: 1;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.integration-name {
  font-weight: 600;
  color: var(--text-color);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-indicator.status-healthy {
  background: #dcfce7;
  color: #166534;
}

.status-indicator.status-warning {
  background: #fef3c7;
  color: #92400e;
}

.status-indicator.status-error {
  background: #fee2e2;
  color: #991b1b;
}

.status-indicator.status-disconnected {
  background: #f3f4f6;
  color: #6b7280;
}

.status-metrics {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 0.5rem;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.metric-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.metric-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
}

.metric-value.uptime-excellent {
  color: #059669;
}

.metric-value.uptime-good {
  color: #d97706;
}

.metric-value.uptime-warning {
  color: #ea580c;
}

.metric-value.uptime-poor {
  color: #dc2626;
}

.status-error {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #dc2626;
  margin-top: 0.5rem;
}

.status-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* Events */
.events-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 400px;
  overflow-y: auto;
}

.event-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 0.5rem;
  border-left: 3px solid transparent;
}

.event-item.event-success {
  border-left-color: #10b981;
  background: #f0fdf4;
}

.event-item.event-error {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.event-item.event-warning {
  border-left-color: #f59e0b;
  background: #fffbeb;
}

.event-item.event-sync {
  border-left-color: #3b82f6;
  background: #eff6ff;
}

.event-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.event-content {
  flex: 1;
  min-width: 0;
}

.event-message {
  font-size: 0.875rem;
  color: var(--text-color);
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

.event-details {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.event-severity {
  flex-shrink: 0;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.event-severity.severity-low {
  background: #f3f4f6;
  color: #6b7280;
}

.event-severity.severity-medium {
  background: #fef3c7;
  color: #92400e;
}

.event-severity.severity-high {
  background: #fed7aa;
  color: #c2410c;
}

.event-severity.severity-critical {
  background: #fee2e2;
  color: #991b1b;
}

.empty-events {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
  text-align: center;
}

.empty-events p {
  color: var(--text-muted);
  margin: 0;
}

/* Alerts */
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.alert-item.alert-low {
  background: #f9fafb;
  border-color: #d1d5db;
}

.alert-item.alert-medium {
  background: #fffbeb;
  border-color: #fbbf24;
}

.alert-item.alert-high {
  background: #fef2f2;
  border-color: #f87171;
}

.alert-item.alert-critical {
  background: #fef2f2;
  border-color: #dc2626;
}

.alert-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-title {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.alert-message {
  font-size: 0.875rem;
  color: var(--text-color);
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.alert-details {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.alert-actions {
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .monitoring-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .health-card {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .health-details {
    justify-content: space-around;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .status-metrics {
    flex-wrap: wrap;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .time-selector,
  .status-filters,
  .event-filters {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .integration-status-item {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .status-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .status-actions {
    align-self: center;
  }
  
  .health-details {
    flex-direction: column;
    gap: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .metrics-section,
  .status-section,
  .events-section,
  .alerts-section {
    padding: 1rem;
  }
  
  .health-card {
    padding: 1rem;
  }
  
  .metric-card {
    padding: 1rem;
  }
  
  .metric-value {
    font-size: 1.5rem;
  }
  
  .status-metrics {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
  
  .event-details,
  .alert-details {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>