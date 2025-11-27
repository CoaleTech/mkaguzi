<template>
  <div class="workflow-instances">
    <!-- Header -->
    <div class="instances-header">
      <div class="header-left">
        <h3>Workflow Instances</h3>
        <p>Monitor running workflows and execution history</p>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="refreshInstances">
          <RefreshCw class="w-4 h-4 mr-2" />
          Refresh
        </Button>
        
        <Dropdown :options="filterOptions" @click="handleFilterChange">
          <template #default>
            <Button variant="outline">
              <Filter class="w-4 h-4 mr-2" />
              {{ currentFilter.label }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
      </div>
    </div>

    <!-- Status Overview -->
    <div class="status-overview">
      <div class="status-card running">
        <div class="status-icon">
          <Play class="w-5 h-5" />
        </div>
        <div class="status-content">
          <div class="status-value">{{ runningInstances.length }}</div>
          <div class="status-label">Running</div>
        </div>
      </div>
      
      <div class="status-card completed">
        <div class="status-icon">
          <CheckCircle class="w-5 h-5" />
        </div>
        <div class="status-content">
          <div class="status-value">{{ completedInstances.length }}</div>
          <div class="status-label">Completed</div>
        </div>
      </div>
      
      <div class="status-card failed">
        <div class="status-icon">
          <XCircle class="w-5 h-5" />
        </div>
        <div class="status-content">
          <div class="status-value">{{ failedInstances.length }}</div>
          <div class="status-label">Failed</div>
        </div>
      </div>
      
      <div class="status-card queued">
        <div class="status-icon">
          <Clock class="w-5 h-5" />
        </div>
        <div class="status-content">
          <div class="status-value">{{ queuedInstances.length }}</div>
          <div class="status-label">Queued</div>
        </div>
      </div>
    </div>

    <!-- Running Instances -->
    <div v-if="runningInstances.length > 0" class="section">
      <h4>Currently Running</h4>
      
      <div class="running-instances">
        <div
          v-for="instance in runningInstances"
          :key="instance.id"
          class="instance-card running-card"
        >
          <div class="instance-header">
            <div class="instance-info">
              <h5>{{ instance.workflow_name }}</h5>
              <div class="instance-meta">
                <span class="instance-id">{{ instance.id }}</span>
                <span class="start-time">Started {{ formatRelativeTime(instance.started_at) }}</span>
              </div>
            </div>
            
            <div class="instance-actions">
              <Button
                variant="ghost"
                size="sm"
                @click="viewInstanceDetails(instance)"
              >
                <Eye class="w-3 h-3" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                @click="cancelInstance(instance.id)"
                class="text-red-600"
              >
                <Square class="w-3 h-3" />
              </Button>
            </div>
          </div>
          
          <div class="progress-section">
            <div class="progress-info">
              <span>Step {{ getCurrentStepIndex(instance) }} of {{ getTotalSteps(instance) }}</span>
              <span class="progress-percentage">{{ instance.progress }}%</span>
            </div>
            
            <div class="progress-bar">
              <div 
                class="progress-fill"
                :style="{ width: `${instance.progress}%` }"
              ></div>
            </div>
            
            <div v-if="instance.current_step" class="current-step">
              <Zap class="w-3 h-3" />
              <span>{{ getCurrentStepName(instance) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Execution History -->
    <div class="section">
      <div class="section-header">
        <h4>Execution History</h4>
        
        <div class="history-filters">
          <FormControl
            type="text"
            v-model="searchQuery"
            placeholder="Search executions..."
            class="search-input"
          >
            <template #prefix>
              <Search class="w-4 h-4" />
            </template>
          </FormControl>
          
          <FormControl
            type="select"
            v-model="statusFilter"
            :options="statusFilterOptions"
            placeholder="All Status"
            class="status-filter"
          />
        </div>
      </div>
      
      <!-- History Table -->
      <div class="history-table">
        <table>
          <thead>
            <tr>
              <th>Workflow</th>
              <th>Status</th>
              <th>Started</th>
              <th>Duration</th>
              <th>Steps</th>
              <th>Output</th>
              <th>Actions</th>
            </tr>
          </thead>
          
          <tbody>
            <tr
              v-for="execution in filteredHistory"
              :key="execution.id"
              class="execution-row"
              :class="{ 'failed': execution.status === 'Failed' }"
            >
              <td class="workflow-column">
                <div class="workflow-info">
                  <h6>{{ execution.workflow_name }}</h6>
                  <span class="execution-id">{{ execution.id }}</span>
                </div>
              </td>
              
              <td class="status-column">
                <div 
                  class="status-badge"
                  :class="getStatusClass(execution.status)"
                >
                  <component :is="getStatusIcon(execution.status)" class="w-3 h-3" />
                  {{ execution.status }}
                </div>
              </td>
              
              <td class="time-column">
                <div class="time-info">
                  <div class="absolute-time">{{ formatDateTime(execution.executed_at) }}</div>
                  <div class="relative-time">{{ formatRelativeTime(execution.executed_at) }}</div>
                </div>
              </td>
              
              <td class="duration-column">
                {{ formatDuration(execution.duration) }}
              </td>
              
              <td class="steps-column">
                <div class="steps-progress">
                  <span class="steps-count">{{ execution.steps_completed }}/{{ execution.steps_total }}</span>
                  <div class="mini-progress">
                    <div 
                      class="mini-progress-fill"
                      :class="{ 'failed': execution.status === 'Failed' }"
                      :style="{ width: `${(execution.steps_completed / execution.steps_total) * 100}%` }"
                    ></div>
                  </div>
                </div>
              </td>
              
              <td class="output-column">
                <div class="output-preview">
                  <span v-if="execution.output" :title="execution.output">
                    {{ truncateText(execution.output, 40) }}
                  </span>
                  <span v-else-if="execution.error" class="error-text" :title="execution.error">
                    {{ truncateText(execution.error, 40) }}
                  </span>
                  <span v-else class="no-output">No output</span>
                </div>
              </td>
              
              <td class="actions-column">
                <div class="row-actions">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="viewExecutionDetails(execution)"
                    title="View details"
                  >
                    <Eye class="w-3 h-3" />
                  </Button>
                  
                  <Button
                    v-if="execution.status === 'Failed'"
                    variant="ghost"
                    size="sm"
                    @click="retryExecution(execution)"
                    title="Retry execution"
                  >
                    <RotateCcw class="w-3 h-3" />
                  </Button>
                  
                  <Dropdown :options="getExecutionActions(execution)" @click="handleExecutionAction">
                    <template #default>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal class="w-3 h-3" />
                      </Button>
                    </template>
                  </Dropdown>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <Button
          variant="outline"
          size="sm"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <ChevronLeft class="w-3 h-3" />
          Previous
        </Button>
        
        <div class="page-info">
          Page {{ currentPage }} of {{ totalPages }}
        </div>
        
        <Button
          variant="outline"
          size="sm"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          Next
          <ChevronRight class="w-3 h-3" />
        </Button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="instances.length === 0 && history.length === 0" class="empty-state">
      <Activity class="w-16 h-16 text-gray-300" />
      <h3>No Workflow Executions</h3>
      <p>Workflow instances and execution history will appear here once workflows start running.</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner">
        <Loader class="w-6 h-6 animate-spin" />
        <p>Loading workflow instances...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Dropdown, FormControl } from "frappe-ui"
import {
	Activity,
	CheckCircle,
	ChevronDown,
	ChevronLeft,
	ChevronRight,
	Clock,
	Eye,
	Filter,
	Loader,
	MoreHorizontal,
	Play,
	RefreshCw,
	RotateCcw,
	Search,
	Square,
	XCircle,
	Zap,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"

const props = defineProps({
	instances: {
		type: Array,
		default: () => [],
	},
	history: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits([
	"refresh",
	"view-details",
	"cancel-instance",
	"retry-execution",
])

// Local state
const searchQuery = ref("")
const statusFilter = ref("")
const currentFilter = ref({ label: "All Instances", value: "all" })
const currentPage = ref(1)
const itemsPerPage = ref(10)

// Filter options
const filterOptions = [
	{ label: "All Instances", value: "all" },
	{ label: "Running Only", value: "running" },
	{ label: "Recent Completed", value: "recent" },
	{ label: "Failed Only", value: "failed" },
]

const statusFilterOptions = [
	{ label: "All Status", value: "" },
	{ label: "Success", value: "Success" },
	{ label: "Failed", value: "Failed" },
	{ label: "Cancelled", value: "Cancelled" },
]

// Computed
const runningInstances = computed(() => {
	return props.instances.filter((instance) => instance.status === "Running")
})

const completedInstances = computed(() => {
	return props.history.filter((execution) => execution.status === "Success")
})

const failedInstances = computed(() => {
	return props.history.filter((execution) => execution.status === "Failed")
})

const queuedInstances = computed(() => {
	return props.instances.filter((instance) => instance.status === "Queued")
})

const filteredHistory = computed(() => {
	let filtered = [...props.history]

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		filtered = filtered.filter(
			(execution) =>
				execution.workflow_name.toLowerCase().includes(query) ||
				execution.id.toLowerCase().includes(query) ||
				execution.output?.toLowerCase().includes(query),
		)
	}

	// Status filter
	if (statusFilter.value) {
		filtered = filtered.filter(
			(execution) => execution.status === statusFilter.value,
		)
	}

	// Apply main filter
	if (currentFilter.value.value === "running") {
		// Show only currently running (from instances)
		filtered = runningInstances.value.map((instance) => ({
			...instance,
			workflow_name: instance.workflow_name,
			status: instance.status,
			executed_at: instance.started_at,
			duration: null,
			steps_completed: Math.floor((instance.progress || 0) / 10),
			steps_total: 10,
			output: `Currently at step: ${instance.current_step || "Unknown"}`,
		}))
	} else if (currentFilter.value.value === "recent") {
		// Show only recent completed (last 24 hours)
		const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
		filtered = filtered.filter(
			(execution) =>
				execution.status === "Success" &&
				new Date(execution.executed_at) > oneDayAgo,
		)
	} else if (currentFilter.value.value === "failed") {
		filtered = filtered.filter((execution) => execution.status === "Failed")
	}

	// Sort by execution date (newest first)
	filtered.sort((a, b) => new Date(b.executed_at) - new Date(a.executed_at))

	return filtered
})

const totalPages = computed(() =>
	Math.ceil(filteredHistory.value.length / itemsPerPage.value),
)

const paginatedHistory = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	return filteredHistory.value.slice(start, start + itemsPerPage.value)
})

// Methods
const refreshInstances = () => {
	emit("refresh")
}

const handleFilterChange = (option) => {
	currentFilter.value = option
	currentPage.value = 1
}

const viewInstanceDetails = (instance) => {
	emit("view-details", instance)
}

const viewExecutionDetails = (execution) => {
	emit("view-details", execution)
}

const cancelInstance = (instanceId) => {
	if (confirm("Are you sure you want to cancel this running workflow?")) {
		emit("cancel-instance", instanceId)
	}
}

const retryExecution = (execution) => {
	emit("retry-execution", execution)
}

const handleExecutionAction = (action) => {
	// Handle dropdown actions
	console.log("Execution action:", action)
}

const getCurrentStepIndex = (instance) => {
	// Calculate current step index based on progress
	return Math.floor((instance.progress || 0) / 10) + 1
}

const getTotalSteps = (instance) => {
	// This should come from the workflow definition
	return 10 // Placeholder
}

const getCurrentStepName = (instance) => {
	// Get the name of the current step
	return instance.current_step || "Unknown Step"
}

const getStatusClass = (status) => {
	return {
		success: status === "Success",
		failed: status === "Failed",
		cancelled: status === "Cancelled",
		running: status === "Running",
		queued: status === "Queued",
	}
}

const getStatusIcon = (status) => {
	const icons = {
		Success: CheckCircle,
		Failed: XCircle,
		Cancelled: Square,
		Running: Play,
		Queued: Clock,
	}
	return icons[status] || Clock
}

const getExecutionActions = (execution) => {
	const actions = [
		{
			label: "View Logs",
			value: "logs",
			action: () => console.log("View logs for", execution.id),
		},
		{
			label: "Copy ID",
			value: "copy-id",
			action: () => navigator.clipboard?.writeText(execution.id),
		},
	]

	if (execution.status === "Failed") {
		actions.unshift({
			label: "Retry",
			value: "retry",
			action: () => retryExecution(execution),
		})
	}

	return actions
}

const formatDateTime = (dateString) => {
	if (!dateString) return "-"
	return new Date(dateString).toLocaleString()
}

const formatRelativeTime = (dateString) => {
	if (!dateString) return "-"

	const now = new Date()
	const date = new Date(dateString)
	const diffMs = now - date

	const seconds = Math.floor(diffMs / 1000)
	const minutes = Math.floor(seconds / 60)
	const hours = Math.floor(minutes / 60)
	const days = Math.floor(hours / 24)

	if (seconds < 60) return `${seconds}s ago`
	if (minutes < 60) return `${minutes}m ago`
	if (hours < 24) return `${hours}h ago`
	return `${days}d ago`
}

const formatDuration = (duration) => {
	if (!duration) return "-"

	const seconds = Math.floor(duration / 1000)
	const minutes = Math.floor(seconds / 60)

	if (minutes > 0) {
		return `${minutes}m ${seconds % 60}s`
	}
	return `${seconds}s`
}

const truncateText = (text, maxLength) => {
	if (!text) return ""
	return text.length > maxLength ? text.substring(0, maxLength) + "..." : text
}

// Watchers
watch([searchQuery, statusFilter], () => {
	currentPage.value = 1
})
</script>

<style scoped>
.workflow-instances {
  padding: 1.5rem;
}

.instances-header {
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

.status-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.status-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  color: white;
}

.status-card.running .status-icon {
  background: #3b82f6;
}

.status-card.completed .status-icon {
  background: #22c55e;
}

.status-card.failed .status-icon {
  background: #ef4444;
}

.status-card.queued .status-icon {
  background: #f59e0b;
}

.status-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.status-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-weight: 500;
}

.section {
  margin-bottom: 2rem;
}

.section h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.history-filters {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.search-input {
  min-width: 250px;
}

.status-filter {
  min-width: 150px;
}

.running-instances {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.instance-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.running-card {
  border-left: 4px solid #3b82f6;
  background: #eff6ff;
}

.instance-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.instance-info h5 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.instance-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.instance-actions {
  display: flex;
  gap: 0.5rem;
}

.progress-section {
  margin-top: 1rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color);
}

.progress-bar {
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.current-step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.history-table {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
}

.history-table table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  text-align: left;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.history-table th {
  background: var(--background-color);
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.875rem;
}

.execution-row {
  transition: background-color 0.2s;
}

.execution-row:hover {
  background: var(--background-color);
}

.execution-row.failed {
  background: #fef2f2;
}

.workflow-info h6 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
}

.execution-id {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: monospace;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  width: fit-content;
}

.status-badge.success {
  background: #dcfce7;
  color: #166534;
}

.status-badge.failed {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.cancelled {
  background: #f3f4f6;
  color: #374151;
}

.status-badge.running {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.queued {
  background: #fef3c7;
  color: #92400e;
}

.time-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.absolute-time {
  font-size: 0.875rem;
  color: var(--text-color);
}

.relative-time {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.steps-progress {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.steps-count {
  font-size: 0.875rem;
  color: var(--text-color);
}

.mini-progress {
  width: 60px;
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
}

.mini-progress-fill {
  height: 100%;
  background: #22c55e;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.mini-progress-fill.failed {
  background: #ef4444;
}

.output-preview {
  max-width: 200px;
}

.output-preview span {
  font-size: 0.875rem;
  color: var(--text-color);
  cursor: help;
}

.error-text {
  color: #991b1b !important;
}

.no-output {
  color: var(--text-muted) !important;
  font-style: italic;
}

.row-actions {
  display: flex;
  gap: 0.25rem;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
}

.page-info {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 1rem 0 0.5rem 0;
}

.empty-state p {
  color: var(--text-muted);
  margin: 0;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 4rem;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-spinner p {
  color: var(--text-muted);
  margin: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .status-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .history-filters {
    justify-content: space-between;
  }
}

@media (max-width: 768px) {
  .workflow-instances {
    padding: 1rem;
  }
  
  .instances-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .status-overview {
    grid-template-columns: 1fr;
  }
  
  .history-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input,
  .status-filter {
    min-width: auto;
  }
  
  .history-table {
    overflow-x: auto;
  }
  
  .history-table th,
  .history-table td {
    padding: 0.75rem 0.5rem;
    white-space: nowrap;
  }
  
  .output-preview {
    max-width: 150px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .instance-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .instance-meta {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .instance-actions {
    justify-content: flex-end;
  }
  
  .status-card {
    padding: 1rem;
  }
  
  .status-icon {
    width: 2.5rem;
    height: 2.5rem;
  }
}
</style>