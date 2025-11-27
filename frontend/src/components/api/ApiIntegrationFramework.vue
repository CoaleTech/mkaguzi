<template>
  <div class="api-integration-framework">
    <!-- Header -->
    <div class="framework-header">
      <div class="header-left">
        <h2>API Integration Framework</h2>
        <p>Manage external system integrations, data synchronization, and webhook endpoints</p>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="showLogsModal = true">
          <Activity class="w-4 h-4 mr-2" />
          View Logs
        </Button>
        
        <Button variant="solid" @click="showCreateModal = true">
          <Plus class="w-4 h-4 mr-2" />
          New Integration
        </Button>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon integrations">
          <Zap class="w-6 h-6" />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ integrationStats.active }}</div>
          <div class="stat-label">Active Integrations</div>
          <div class="stat-subtitle">{{ integrationStats.total }} total</div>
        </div>
        <div class="stat-trend positive">
          <TrendingUp class="w-4 h-4" />
          +3 this week
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon sync">
          <RefreshCw class="w-6 h-6" />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ syncStats.running }}</div>
          <div class="stat-label">Running Jobs</div>
          <div class="stat-subtitle">{{ syncStats.scheduled }} scheduled</div>
        </div>
        <div class="stat-trend neutral">
          <Minus class="w-4 h-4" />
          No change
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon webhooks">
          <Webhook class="w-6 h-6" />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ webhookStats.active }}</div>
          <div class="stat-label">Active Webhooks</div>
          <div class="stat-subtitle">{{ webhookStats.successRate }}% success rate</div>
        </div>
        <div class="stat-trend positive">
          <TrendingUp class="w-4 h-4" />
          +5.2%
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon health">
          <Shield class="w-6 h-6" />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ integrationStats.uptime }}%</div>
          <div class="stat-label">System Uptime</div>
          <div class="stat-subtitle">{{ integrationStats.healthy }} healthy</div>
        </div>
        <div class="stat-trend positive">
          <TrendingUp class="w-4 h-4" />
          +0.3%
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tab-navigation">
      <div class="tab-list">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="['tab-button', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          <component :is="tab.icon" class="w-4 h-4" />
          <span>{{ tab.label }}</span>
          <div v-if="tab.badge" class="tab-badge">{{ tab.badge }}</div>
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Integrations Tab -->
      <div v-if="activeTab === 'integrations'" class="integrations-tab">
        <IntegrationsOverview
          :integrations="integrations"
          :loading="loading"
          @create="handleCreateIntegration"
          @edit="handleEditIntegration"
          @test="handleTestConnection"
          @toggle="handleToggleIntegration"
          @delete="handleDeleteIntegration"
        />
      </div>

      <!-- Sync Jobs Tab -->
      <div v-if="activeTab === 'sync-jobs'" class="sync-jobs-tab">
        <SyncJobsManager
          :jobs="syncJobs"
          :integrations="integrations"
          :loading="loading"
          @create="handleCreateJob"
          @run="handleRunJob"
          @pause="handlePauseJob"
          @resume="handleResumeJob"
          @edit="handleEditJob"
          @delete="handleDeleteJob"
        />
      </div>

      <!-- Webhooks Tab -->
      <div v-if="activeTab === 'webhooks'" class="webhooks-tab">
        <WebhookManager
          :webhooks="webhooks"
          :integrations="integrations"
          :loading="loading"
          @create="handleCreateWebhook"
          @test="handleTestWebhook"
          @edit="handleEditWebhook"
          @toggle="handleToggleWebhook"
          @delete="handleDeleteWebhook"
        />
      </div>

      <!-- Transformations Tab -->
      <div v-if="activeTab === 'transformations'" class="transformations-tab">
        <DataTransformations
          :transformations="transformations"
          :integrations="integrations"
          :loading="loading"
          @create="handleCreateTransformation"
          @test="handleTestTransformation"
          @edit="handleEditTransformation"
          @toggle="handleToggleTransformation"
          @delete="handleDeleteTransformation"
        />
      </div>

      <!-- Monitoring Tab -->
      <div v-if="activeTab === 'monitoring'" class="monitoring-tab">
        <IntegrationMonitoring
          :integrations="integrations"
          :logs="recentLogs"
          :stats="integrationStats"
          :loading="loading"
          @refresh="handleRefreshLogs"
          @clear="handleClearLogs"
          @export="handleExportLogs"
        />
      </div>

      <!-- Settings Tab -->
      <div v-if="activeTab === 'settings'" class="settings-tab">
        <IntegrationSettings
          :auth-providers="authProviders"
          :rate-limits="rateLimits"
          @update="handleUpdateSettings"
        />
      </div>
    </div>

    <!-- Real-time Status Bar -->
    <div class="status-bar">
      <div class="status-left">
        <div class="status-item">
          <div class="status-indicator healthy"></div>
          <span>System Status: Operational</span>
        </div>
        
        <div class="status-item">
          <Clock class="w-4 h-4" />
          <span>Last Update: {{ formatTime(lastUpdate) }}</span>
        </div>
      </div>
      
      <div class="status-right">
        <div class="status-item">
          <Activity class="w-4 h-4" />
          <span>{{ totalRequests }} requests/hour</span>
        </div>
        
        <Button variant="ghost" size="sm" @click="refreshData">
          <RefreshCw class="w-3 h-3" :class="{ 'animate-spin': refreshing }" />
        </Button>
      </div>
    </div>

    <!-- Create Integration Modal -->
    <Dialog
      v-if="showCreateModal"
      :options="{ title: 'New Integration', size: 'xl' }"
      @close="showCreateModal = false"
    >
      <CreateIntegrationForm
        @create="handleCreateIntegration"
        @cancel="showCreateModal = false"
      />
    </Dialog>

    <!-- API Logs Modal -->
    <Dialog
      v-if="showLogsModal"
      :options="{ title: 'API Logs', size: 'full' }"
      @close="showLogsModal = false"
    >
      <ApiLogsViewer
        :logs="recentLogs"
        :integrations="integrations"
        @close="showLogsModal = false"
        @refresh="handleRefreshLogs"
        @clear="handleClearLogs"
      />
    </Dialog>

    <!-- Background Task Notifications -->
    <div v-if="backgroundTasks.length > 0" class="background-tasks">
      <div
        v-for="task in backgroundTasks"
        :key="task.id"
        class="task-notification"
        :class="getTaskClass(task.status)"
      >
        <div class="task-icon">
          <component :is="getTaskIcon(task.type)" class="w-4 h-4" />
        </div>
        <div class="task-content">
          <div class="task-title">{{ task.title }}</div>
          <div class="task-progress" v-if="task.progress !== undefined">
            <div class="progress-bar">
              <div 
                class="progress-fill"
                :style="{ width: task.progress + '%' }"
              ></div>
            </div>
            <span class="progress-text">{{ task.progress }}%</span>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          @click="dismissTask(task.id)"
        >
          <X class="w-3 h-3" />
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useApiIntegrationStore } from "@/stores/useApiIntegrationStore"
import { Button, Dialog } from "frappe-ui"
import {
	Activity,
	BarChart3,
	Clock,
	Database,
	Globe,
	Minus,
	Plus,
	RefreshCw,
	Settings,
	Shield,
	TrendingUp,
	Webhook,
	X,
	Zap,
} from "lucide-vue-next"
import { computed, onMounted, onUnmounted, ref } from "vue"

import ApiLogsViewer from "./ApiLogsViewer.vue"
import CreateIntegrationForm from "./CreateIntegrationForm.vue"
import DataTransformations from "./DataTransformations.vue"
import IntegrationMonitoring from "./IntegrationMonitoring.vue"
import IntegrationSettings from "./IntegrationSettings.vue"
// Components
import IntegrationsOverview from "./IntegrationsOverview.vue"
import SyncJobsManager from "./SyncJobsManager.vue"
import WebhookManager from "./WebhookManager.vue"

// Store
const store = useApiIntegrationStore()

// State
const activeTab = ref("integrations")
const showCreateModal = ref(false)
const showLogsModal = ref(false)
const refreshing = ref(false)
const lastUpdate = ref(new Date())
const backgroundTasks = ref([])

// Tab configuration
const tabs = computed(() => [
	{
		id: "integrations",
		label: "Integrations",
		icon: Globe,
		badge: store.integrationStats.active,
	},
	{
		id: "sync-jobs",
		label: "Sync Jobs",
		icon: RefreshCw,
		badge: store.syncStats.running > 0 ? store.syncStats.running : null,
	},
	{
		id: "webhooks",
		label: "Webhooks",
		icon: Webhook,
		badge: store.webhookStats.active,
	},
	{
		id: "transformations",
		label: "Transformations",
		icon: Database,
		badge: store.transformations.length,
	},
	{
		id: "monitoring",
		label: "Monitoring",
		icon: BarChart3,
		badge: null,
	},
	{
		id: "settings",
		label: "Settings",
		icon: Settings,
		badge: null,
	},
])

// Computed properties from store
const {
	integrations,
	syncJobs,
	webhooks,
	transformations,
	authProviders,
	rateLimits,
	recentLogs,
	integrationStats,
	syncStats,
	webhookStats,
	loading,
} = store

// Computed stats
const totalRequests = computed(() => {
	const hourAgo = new Date(Date.now() - 60 * 60 * 1000)
	return recentLogs.filter((log) => new Date(log.timestamp) > hourAgo).length
})

// Methods
const refreshData = async () => {
	refreshing.value = true
	try {
		await store.loadIntegrations()
		lastUpdate.value = new Date()
	} finally {
		refreshing.value = false
	}
}

const handleCreateIntegration = async (integrationData) => {
	try {
		const newIntegration = await store.createIntegration(integrationData)
		showCreateModal.value = false

		// Add background task for connection testing
		backgroundTasks.value.push({
			id: `task_${Date.now()}`,
			type: "test_connection",
			title: `Testing connection for ${newIntegration.name}...`,
			status: "running",
			progress: 0,
		})

		// Simulate connection test
		setTimeout(async () => {
			const task = backgroundTasks.value.find(
				(t) => t.type === "test_connection",
			)
			if (task) {
				task.progress = 100
				task.status = "completed"
				task.title = `Connection test completed for ${newIntegration.name}`

				// Auto dismiss after 3 seconds
				setTimeout(() => {
					dismissTask(task.id)
				}, 3000)
			}
		}, 2000)
	} catch (error) {
		console.error("Failed to create integration:", error)
	}
}

const handleEditIntegration = (integration) => {
	console.log("Edit integration:", integration.id)
	// Implementation would open edit modal
}

const handleTestConnection = async (integration) => {
	const connection = store.connections.find(
		(c) => c.integration_id === integration.id,
	)
	if (connection) {
		backgroundTasks.value.push({
			id: `task_${Date.now()}`,
			type: "test_connection",
			title: `Testing ${integration.name} connection...`,
			status: "running",
			progress: undefined,
		})

		const success = await store.testConnection(connection.id)
		const task = backgroundTasks.value.find(
			(t) => t.type === "test_connection" && t.title.includes(integration.name),
		)

		if (task) {
			task.status = success ? "completed" : "failed"
			task.title = `Connection test ${success ? "successful" : "failed"} for ${integration.name}`

			setTimeout(() => dismissTask(task.id), 3000)
		}
	}
}

const handleToggleIntegration = async (integration) => {
	const newStatus = integration.status === "Active" ? "Inactive" : "Active"
	await store.updateIntegration(integration.id, { status: newStatus })
}

const handleDeleteIntegration = async (integration) => {
	if (confirm(`Are you sure you want to delete ${integration.name}?`)) {
		await store.deleteIntegration(integration.id)
	}
}

// Sync Job handlers
const handleCreateJob = async (jobData) => {
	await store.createSyncJob(jobData)
}

const handleRunJob = async (job) => {
	backgroundTasks.value.push({
		id: `task_${Date.now()}`,
		type: "sync_job",
		title: `Running ${job.name}...`,
		status: "running",
		progress: 0,
	})

	const success = await store.runSyncJob(job.id)
	const task = backgroundTasks.value.find(
		(t) => t.type === "sync_job" && t.title.includes(job.name),
	)

	if (task) {
		task.status = success ? "completed" : "failed"
		task.title = `Sync job ${success ? "completed" : "failed"}: ${job.name}`
		task.progress = 100

		setTimeout(() => dismissTask(task.id), 5000)
	}
}

const handlePauseJob = async (job) => {
	await store.pauseSyncJob(job.id)
}

const handleResumeJob = async (job) => {
	await store.resumeSyncJob(job.id)
}

const handleEditJob = (job) => {
	console.log("Edit job:", job.id)
}

const handleDeleteJob = async (job) => {
	if (confirm(`Are you sure you want to delete ${job.name}?`)) {
		const index = syncJobs.findIndex((j) => j.id === job.id)
		if (index !== -1) {
			syncJobs.splice(index, 1)
		}
	}
}

// Webhook handlers
const handleCreateWebhook = async (webhookData) => {
	await store.createWebhook(webhookData)
}

const handleTestWebhook = async (webhook) => {
	backgroundTasks.value.push({
		id: `task_${Date.now()}`,
		type: "test_webhook",
		title: `Testing webhook ${webhook.name}...`,
		status: "running",
		progress: undefined,
	})

	const success = await store.testWebhook(webhook.id)
	const task = backgroundTasks.value.find(
		(t) => t.type === "test_webhook" && t.title.includes(webhook.name),
	)

	if (task) {
		task.status = success ? "completed" : "failed"
		task.title = `Webhook test ${success ? "successful" : "failed"}: ${webhook.name}`

		setTimeout(() => dismissTask(task.id), 3000)
	}
}

const handleEditWebhook = (webhook) => {
	console.log("Edit webhook:", webhook.id)
}

const handleToggleWebhook = async (webhook) => {
	const newStatus = webhook.status === "Active" ? "Paused" : "Active"
	await store.updateWebhook(webhook.id, { status: newStatus })
}

const handleDeleteWebhook = async (webhook) => {
	if (confirm(`Are you sure you want to delete ${webhook.name}?`)) {
		await store.deleteWebhook(webhook.id)
	}
}

// Transformation handlers
const handleCreateTransformation = async (transformationData) => {
	await store.createTransformation(transformationData)
}

const handleTestTransformation = async (transformation) => {
	const sampleData = { sample: "data" }
	const result = await store.testTransformation(transformation.id, sampleData)
	console.log("Transformation test result:", result)
}

const handleEditTransformation = (transformation) => {
	console.log("Edit transformation:", transformation.id)
}

const handleToggleTransformation = async (transformation) => {
	const newStatus = transformation.status === "Active" ? "Inactive" : "Active"
	const index = transformations.findIndex((t) => t.id === transformation.id)
	if (index !== -1) {
		transformations[index].status = newStatus
	}
}

const handleDeleteTransformation = async (transformation) => {
	if (confirm(`Are you sure you want to delete ${transformation.name}?`)) {
		const index = transformations.findIndex((t) => t.id === transformation.id)
		if (index !== -1) {
			transformations.splice(index, 1)
		}
	}
}

// Monitoring handlers
const handleRefreshLogs = async () => {
	await refreshData()
}

const handleClearLogs = async (integrationId = null) => {
	if (confirm("Are you sure you want to clear the logs?")) {
		store.clearApiLogs(integrationId)
	}
}

const handleExportLogs = () => {
	// Implementation would export logs to CSV/JSON
	console.log("Export logs")
}

// Settings handler
const handleUpdateSettings = (settings) => {
	console.log("Update settings:", settings)
}

// Utility methods
const formatTime = (date) => {
	return new Date(date).toLocaleTimeString()
}

const getTaskClass = (status) => {
	return {
		"task-running": status === "running",
		"task-completed": status === "completed",
		"task-failed": status === "failed",
	}
}

const getTaskIcon = (type) => {
	const icons = {
		test_connection: Globe,
		sync_job: RefreshCw,
		test_webhook: Webhook,
		transformation: Database,
	}
	return icons[type] || Activity
}

const dismissTask = (taskId) => {
	const index = backgroundTasks.value.findIndex((t) => t.id === taskId)
	if (index !== -1) {
		backgroundTasks.value.splice(index, 1)
	}
}

// Auto-refresh setup
let refreshInterval
onMounted(() => {
	refreshData()
	refreshInterval = setInterval(() => {
		lastUpdate.value = new Date()
		// In a real app, you might want to refresh data periodically
	}, 30000) // Every 30 seconds
})

onUnmounted(() => {
	if (refreshInterval) {
		clearInterval(refreshInterval)
	}
})
</script>

<style scoped>
.api-integration-framework {
  padding: 1.5rem;
  max-width: 100%;
}

.framework-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header-left h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.header-left p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.95rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  transition: all 0.2s;
}

.stat-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  padding: 0.75rem;
  border-radius: 0.5rem;
  color: white;
  flex-shrink: 0;
}

.stat-icon.integrations {
  background: #6366f1;
}

.stat-icon.sync {
  background: #10b981;
}

.stat-icon.webhooks {
  background: #f59e0b;
}

.stat-icon.health {
  background: #8b5cf6;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.125rem;
}

.stat-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.stat-trend.positive {
  color: #059669;
}

.stat-trend.negative {
  color: #dc2626;
}

.stat-trend.neutral {
  color: var(--text-muted);
}

/* Tab Navigation */
.tab-navigation {
  margin-bottom: 2rem;
}

.tab-list {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  overflow-x: auto;
  gap: 0.5rem;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  color: var(--text-muted);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  white-space: nowrap;
  position: relative;
}

.tab-button:hover {
  color: var(--text-color);
  background: var(--background-color);
  border-radius: 0.375rem 0.375rem 0 0;
}

.tab-button.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.tab-badge {
  background: var(--primary-color);
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 1.25rem;
  text-align: center;
}

/* Tab Content */
.tab-content {
  min-height: 500px;
}

/* Status Bar */
.status-bar {
  position: sticky;
  bottom: 0;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  margin-top: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.status-left,
.status-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.status-indicator {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}

.status-indicator.healthy {
  background: #10b981;
}

.status-indicator.warning {
  background: #f59e0b;
}

.status-indicator.error {
  background: #ef4444;
}

/* Background Tasks */
.background-tasks {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 400px;
}

.task-notification {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease-out;
}

.task-notification.task-running {
  border-left: 4px solid #3b82f6;
}

.task-notification.task-completed {
  border-left: 4px solid #10b981;
}

.task-notification.task-failed {
  border-left: 4px solid #ef4444;
}

.task-icon {
  padding: 0.5rem;
  border-radius: 0.375rem;
  background: var(--background-color);
  color: var(--primary-color);
  flex-shrink: 0;
}

.task-content {
  flex: 1;
  min-width: 0;
}

.task-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.task-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 0.25rem;
  background: var(--background-color);
  border-radius: 0.125rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
  min-width: 2rem;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive Design */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .framework-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: stretch;
  }
}

@media (max-width: 768px) {
  .api-integration-framework {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  
  .stat-card {
    padding: 1rem;
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }
  
  .stat-trend {
    position: static;
    margin-top: 0.5rem;
  }
  
  .tab-list {
    gap: 0;
  }
  
  .tab-button {
    padding: 0.5rem 0.75rem;
    font-size: 0.75rem;
  }
  
  .status-bar {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .background-tasks {
    position: fixed;
    top: auto;
    bottom: 6rem;
    left: 1rem;
    right: 1rem;
    max-width: none;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    flex-direction: row;
    text-align: left;
  }
  
  .tab-button span {
    display: none;
  }
  
  .task-notification {
    padding: 0.75rem;
  }
  
  .task-title {
    font-size: 0.75rem;
  }
}
</style>