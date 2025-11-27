<template>
  <div class="data-transformations">
    <!-- Header -->
    <div class="transformations-header">
      <div class="header-left">
        <h3>Data Transformations</h3>
        <p>Configure data transformation pipelines for API integrations</p>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="refreshTransformations">
          <RefreshCw class="w-4 h-4 mr-2" :class="{ 'animate-spin': refreshing }" />
          Refresh
        </Button>
        
        <Button variant="solid" @click="$emit('create')">
          <Plus class="w-4 h-4 mr-2" />
          Create Transformation
        </Button>
      </div>
    </div>

    <!-- Transformation Stats -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-value">{{ stats.total || 0 }}</div>
          <div class="stat-label">Total Transformations</div>
        </div>
        <div class="stat-icon">
          <Shuffle class="w-6 h-6 text-blue-500" />
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-value">{{ stats.active || 0 }}</div>
          <div class="stat-label">Active</div>
        </div>
        <div class="stat-icon">
          <CheckCircle class="w-6 h-6 text-green-500" />
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-value">{{ stats.executions || 0 }}</div>
          <div class="stat-label">Executions</div>
        </div>
        <div class="stat-icon">
          <Play class="w-6 h-6 text-purple-500" />
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-value">{{ stats.success_rate || 0 }}%</div>
          <div class="stat-label">Success Rate</div>
        </div>
        <div class="stat-icon">
          <TrendingUp class="w-6 h-6 text-emerald-500" />
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filters">
        <FormControl
          type="text"
          v-model="searchQuery"
          placeholder="Search transformations..."
          class="search-input"
        >
          <template #prefix>
            <Search class="w-4 h-4" />
          </template>
        </FormControl>
        
        <Dropdown :options="statusFilterOptions" @click="handleStatusFilter">
          <template #default>
            <Button variant="outline">
              <Filter class="w-4 h-4 mr-2" />
              {{ selectedStatus || 'All Status' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
        
        <Dropdown :options="typeFilterOptions" @click="handleTypeFilter">
          <template #default>
            <Button variant="outline">
              <Shuffle class="w-4 h-4 mr-2" />
              {{ selectedType || 'All Types' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
        
        <Dropdown :options="integrationFilterOptions" @click="handleIntegrationFilter">
          <template #default>
            <Button variant="outline">
              <Globe class="w-4 h-4 mr-2" />
              {{ selectedIntegration || 'All Integrations' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <Loader class="w-6 h-6 animate-spin" />
      <p>Loading transformations...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredTransformations.length === 0" class="empty-state">
      <Shuffle class="w-16 h-16 text-gray-300" />
      <h4>{{ searchQuery ? 'No transformations found' : 'No transformations yet' }}</h4>
      <p>
        {{ searchQuery 
          ? 'Try adjusting your search terms or filters.' 
          : 'Create your first data transformation pipeline.' 
        }}
      </p>
      <Button v-if="!searchQuery" variant="solid" @click="$emit('create')">
        Create Transformation
      </Button>
    </div>

    <!-- Transformations List -->
    <div v-else class="transformations-container">
      <div class="transformations-list">
        <div
          v-for="transformation in paginatedTransformations"
          :key="transformation.id"
          class="transformation-item"
          :class="getTransformationClass(transformation)"
        >
          <!-- Transformation Header -->
          <div class="transformation-header">
            <div class="transformation-info">
              <div class="transformation-title">
                <h4>{{ transformation.name }}</h4>
                <div class="transformation-meta">
                  <span class="transformation-type">{{ transformation.type }}</span>
                  <span class="transformation-integration">{{ transformation.integration.name }}</span>
                </div>
              </div>
              
              <div class="transformation-status">
                <div class="status-badge" :class="getStatusClass(transformation.status)">
                  <component :is="getStatusIcon(transformation.status)" class="w-3 h-3" />
                  <span>{{ transformation.status }}</span>
                </div>
              </div>
            </div>
            
            <div class="transformation-actions">
              <Button
                variant="ghost"
                size="sm"
                @click="$emit('test', transformation)"
                :disabled="transformation.status !== 'Active'"
              >
                <Zap class="w-3 h-3" />
              </Button>
              
              <Dropdown :options="getTransformationActions(transformation)" @click="handleTransformationAction">
                <template #default>
                  <Button variant="ghost" size="sm">
                    <MoreVertical class="w-4 h-4" />
                  </Button>
                </template>
              </Dropdown>
            </div>
          </div>

          <!-- Transformation Description -->
          <div class="transformation-description">
            <p>{{ transformation.description }}</p>
          </div>

          <!-- Pipeline Visualization -->
          <div class="pipeline-section">
            <h5>Transformation Pipeline</h5>
            <div class="pipeline-flow">
              <div
                v-for="(step, index) in transformation.pipeline_steps"
                :key="step.id"
                class="pipeline-step"
                :class="getStepClass(step)"
              >
                <div class="step-content">
                  <div class="step-header">
                    <div class="step-icon">
                      <component :is="getStepIcon(step.type)" class="w-4 h-4" />
                    </div>
                    <div class="step-info">
                      <div class="step-name">{{ step.name }}</div>
                      <div class="step-type">{{ step.type }}</div>
                    </div>
                    <div class="step-status">
                      <component :is="getStepStatusIcon(step.status)" class="w-3 h-3" />
                    </div>
                  </div>
                  
                  <div v-if="step.description" class="step-description">
                    {{ step.description }}
                  </div>
                  
                  <!-- Step Configuration Preview -->
                  <div v-if="step.config && Object.keys(step.config).length > 0" class="step-config">
                    <div class="config-preview">
                      <div
                        v-for="(value, key) in step.config"
                        :key="key"
                        class="config-item"
                      >
                        <span class="config-key">{{ key }}:</span>
                        <span class="config-value">{{ formatConfigValue(value) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Arrow connector (not for last step) -->
                <div v-if="index < transformation.pipeline_steps.length - 1" class="pipeline-connector">
                  <ArrowRight class="w-4 h-4" />
                </div>
              </div>
            </div>
          </div>

          <!-- Execution Stats -->
          <div class="execution-stats">
            <div class="stats-header">
              <h5>Execution Statistics</h5>
              <span class="stats-period">Last 30 days</span>
            </div>
            
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-number">{{ formatNumber(transformation.stats.total_executions) }}</span>
                <span class="stat-label">Total Executions</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ formatNumber(transformation.stats.successful_executions) }}</span>
                <span class="stat-label">Successful</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ formatNumber(transformation.stats.failed_executions) }}</span>
                <span class="stat-label">Failed</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ transformation.stats.avg_execution_time }}ms</span>
                <span class="stat-label">Avg Time</span>
              </div>
            </div>
          </div>

          <!-- Recent Executions -->
          <div v-if="transformation.recent_executions?.length" class="recent-executions">
            <div class="executions-header">
              <h5>Recent Executions</h5>
              <Button
                variant="ghost"
                size="sm"
                @click="$emit('viewExecutions', transformation)"
              >
                <Eye class="w-3 h-3 mr-1" />
                View All
              </Button>
            </div>
            
            <div class="executions-list">
              <div
                v-for="execution in transformation.recent_executions.slice(0, 3)"
                :key="execution.id"
                class="execution-item"
              >
                <div class="execution-status">
                  <component 
                    :is="getExecutionStatusIcon(execution.status)" 
                    class="w-3 h-3"
                    :class="getExecutionStatusClass(execution.status)"
                  />
                </div>
                
                <div class="execution-info">
                  <div class="execution-time">{{ formatTime(execution.created_at) }}</div>
                  <div class="execution-duration">{{ execution.duration }}ms</div>
                </div>
                
                <div class="execution-records">
                  {{ execution.records_processed }} records
                </div>
                
                <div v-if="execution.error" class="execution-error">
                  <AlertCircle class="w-3 h-3" />
                  <span>{{ execution.error }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Transformation Footer -->
          <div class="transformation-footer">
            <div class="footer-left">
              <div class="creation-info">
                <span>Created {{ formatRelativeTime(transformation.created_at) }}</span>
                <span>by {{ transformation.created_by }}</span>
              </div>
              <div v-if="transformation.last_execution" class="last-execution">
                Last run: {{ formatRelativeTime(transformation.last_execution) }}
              </div>
            </div>
            
            <div class="footer-actions">
              <Button
                variant="ghost"
                size="sm"
                @click="$emit('edit', transformation)"
              >
                <Edit class="w-3 h-3 mr-1" />
                Edit
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                @click="$emit('run', transformation)"
                :disabled="transformation.status !== 'Active'"
              >
                <Play class="w-3 h-3 mr-1" />
                Run Now
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                @click="$emit('toggle', transformation)"
                :class="getToggleButtonClass(transformation.status)"
              >
                <component :is="getToggleIcon(transformation.status)" class="w-3 h-3 mr-1" />
                {{ transformation.status === 'Active' ? 'Disable' : 'Enable' }}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <div class="pagination-info">
        Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to 
        {{ Math.min(currentPage * itemsPerPage, filteredTransformations.length) }} of 
        {{ filteredTransformations.length }} transformations
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
  </div>
</template>

<script setup>
import { Button, Dropdown, FormControl } from "frappe-ui"
import {
	AlertCircle,
	ArrowRight,
	CheckCircle,
	ChevronDown,
	ChevronLeft,
	ChevronRight,
	Clock,
	Code,
	Database,
	Edit,
	Eye,
	FileText,
	Filter,
	Filter as FilterIcon,
	Globe,
	Loader,
	Map,
	MoreVertical,
	Play,
	Plus,
	Power,
	PowerOff,
	RefreshCw,
	Search,
	Settings,
	Shuffle,
	TrendingUp,
	XCircle,
	Zap,
} from "lucide-vue-next"
import { computed, ref, watch } from "vue"

const props = defineProps({
	transformations: {
		type: Array,
		default: () => [],
	},
	integrations: {
		type: Array,
		default: () => [],
	},
	stats: {
		type: Object,
		default: () => ({}),
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits([
	"create",
	"edit",
	"run",
	"test",
	"toggle",
	"delete",
	"viewExecutions",
	"viewLogs",
])

// Local state
const searchQuery = ref("")
const selectedStatus = ref("")
const selectedType = ref("")
const selectedIntegration = ref("")
const currentPage = ref(1)
const itemsPerPage = ref(5)
const refreshing = ref(false)

// Filter options
const statusFilterOptions = [
	{ label: "All Status", value: "" },
	{ label: "Active", value: "Active" },
	{ label: "Inactive", value: "Inactive" },
	{ label: "Error", value: "Error" },
]

const typeFilterOptions = [
	{ label: "All Types", value: "" },
	{ label: "Data Mapping", value: "Data Mapping" },
	{ label: "Field Transformation", value: "Field Transformation" },
	{ label: "Validation", value: "Validation" },
	{ label: "Filtering", value: "Filtering" },
	{ label: "Aggregation", value: "Aggregation" },
	{ label: "Custom Script", value: "Custom Script" },
]

const integrationFilterOptions = computed(() => [
	{ label: "All Integrations", value: "" },
	...props.integrations.map((integration) => ({
		label: integration.name,
		value: integration.id,
	})),
])

// Computed properties
const filteredTransformations = computed(() => {
	let filtered = [...props.transformations]

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		filtered = filtered.filter(
			(transformation) =>
				transformation.name.toLowerCase().includes(query) ||
				transformation.description.toLowerCase().includes(query) ||
				transformation.type.toLowerCase().includes(query),
		)
	}

	// Status filter
	if (selectedStatus.value) {
		filtered = filtered.filter(
			(transformation) => transformation.status === selectedStatus.value,
		)
	}

	// Type filter
	if (selectedType.value) {
		filtered = filtered.filter(
			(transformation) => transformation.type === selectedType.value,
		)
	}

	// Integration filter
	if (selectedIntegration.value) {
		filtered = filtered.filter(
			(transformation) =>
				transformation.integration?.id === selectedIntegration.value,
		)
	}

	// Sort by name
	filtered.sort((a, b) => a.name.localeCompare(b.name))

	return filtered
})

const totalPages = computed(() =>
	Math.ceil(filteredTransformations.value.length / itemsPerPage.value),
)

const paginatedTransformations = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	return filteredTransformations.value.slice(start, start + itemsPerPage.value)
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
const refreshTransformations = async () => {
	refreshing.value = true
	try {
		await new Promise((resolve) => setTimeout(resolve, 1000))
	} finally {
		refreshing.value = false
	}
}

const handleStatusFilter = (option) => {
	selectedStatus.value = option.value
	currentPage.value = 1
}

const handleTypeFilter = (option) => {
	selectedType.value = option.value
	currentPage.value = 1
}

const handleIntegrationFilter = (option) => {
	selectedIntegration.value = option.value
	currentPage.value = 1
}

const getTransformationClass = (transformation) => {
	return {
		"transformation-inactive": transformation.status === "Inactive",
		"transformation-error": transformation.status === "Error",
	}
}

const getStatusClass = (status) => {
	return {
		"status-active": status === "Active",
		"status-inactive": status === "Inactive",
		"status-error": status === "Error",
	}
}

const getStatusIcon = (status) => {
	const icons = {
		Active: CheckCircle,
		Inactive: XCircle,
		Error: AlertCircle,
	}
	return icons[status] || XCircle
}

const getStepClass = (step) => {
	return {
		"step-completed": step.status === "Completed",
		"step-failed": step.status === "Failed",
		"step-running": step.status === "Running",
	}
}

const getStepIcon = (type) => {
	const icons = {
		"Data Mapping": Map,
		"Field Transformation": Shuffle,
		Validation: CheckCircle,
		Filtering: FilterIcon,
		Aggregation: Database,
		"Custom Script": Code,
	}
	return icons[type] || Settings
}

const getStepStatusIcon = (status) => {
	const icons = {
		Active: CheckCircle,
		Completed: CheckCircle,
		Failed: XCircle,
		Running: Clock,
		Inactive: XCircle,
	}
	return icons[status] || Clock
}

const getExecutionStatusIcon = (status) => {
	const icons = {
		Success: CheckCircle,
		Failed: XCircle,
		Running: Clock,
	}
	return icons[status] || Clock
}

const getExecutionStatusClass = (status) => {
	return {
		"text-green-500": status === "Success",
		"text-red-500": status === "Failed",
		"text-blue-500": status === "Running",
	}
}

const getToggleButtonClass = (status) => {
	return {
		"toggle-disable": status === "Active",
		"toggle-enable": status === "Inactive",
	}
}

const getToggleIcon = (status) => {
	return status === "Active" ? PowerOff : Power
}

const formatConfigValue = (value) => {
	if (typeof value === "object") {
		return JSON.stringify(value)
	}
	if (typeof value === "string" && value.length > 50) {
		return value.substring(0, 50) + "..."
	}
	return value
}

const formatNumber = (num) => {
	if (!num) return "0"
	if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
	if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
	return num.toString()
}

const formatTime = (dateString) => {
	if (!dateString) return "-"
	return new Date(dateString).toLocaleTimeString()
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

const getTransformationActions = (transformation) => [
	{
		label: "View Details",
		value: "view",
		action: () => console.log("View", transformation.id),
	},
	{
		label: "Test Transformation",
		value: "test",
		action: () => emit("test", transformation),
	},
	{
		label: "Edit Configuration",
		value: "edit",
		action: () => emit("edit", transformation),
	},
	{
		label: "View Executions",
		value: "executions",
		action: () => emit("viewExecutions", transformation),
	},
	{
		label: "View Logs",
		value: "logs",
		action: () => emit("viewLogs", transformation),
	},
	{
		label: "Duplicate",
		value: "duplicate",
		action: () => console.log("Duplicate", transformation.id),
	},
	{
		label: transformation.status === "Active" ? "Disable" : "Enable",
		value: "toggle",
		action: () => emit("toggle", transformation),
	},
	{
		label: "Delete",
		value: "delete",
		action: () => emit("delete", transformation),
		dangerous: true,
	},
]

const handleTransformationAction = (action) => {
	if (action.action) {
		action.action()
	}
}

// Watchers
watch([searchQuery, selectedStatus, selectedType, selectedIntegration], () => {
	currentPage.value = 1
})
</script>

<style scoped>
.data-transformations {
  padding: 0;
}

.transformations-header {
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

/* Stats Overview */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-weight: 500;
}

.stat-icon {
  opacity: 0.1;
}

.filters-section {
  margin-bottom: 1.5rem;
}

.filters {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  min-width: 300px;
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

/* Transformations List */
.transformations-container {
  margin-bottom: 2rem;
}

.transformations-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.transformation-item {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  transition: all 0.2s;
}

.transformation-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.transformation-item.transformation-inactive {
  opacity: 0.7;
  background: #f9fafb;
}

.transformation-item.transformation-error {
  border-left: 4px solid #ef4444;
}

.transformation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.transformation-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex: 1;
  margin-right: 1rem;
}

.transformation-title h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.transformation-meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.transformation-type,
.transformation-integration {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 500;
}

.transformation-type {
  background: var(--primary-light);
  color: var(--primary-color);
}

.transformation-integration {
  background: var(--background-color);
  color: var(--text-muted);
}

.transformation-status {
  margin-left: auto;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.status-active {
  background: #dcfce7;
  color: #166534;
}

.status-badge.status-inactive {
  background: #f3f4f6;
  color: #374151;
}

.status-badge.status-error {
  background: #fee2e2;
  color: #991b1b;
}

.transformation-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.transformation-description {
  margin-bottom: 1.5rem;
}

.transformation-description p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
}

/* Pipeline Section */
.pipeline-section {
  margin-bottom: 1.5rem;
}

.pipeline-section h5 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.pipeline-flow {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  overflow-x: auto;
  padding: 1rem 0;
}

.pipeline-step {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
  min-width: 200px;
  flex-shrink: 0;
  transition: all 0.2s;
}

.pipeline-step:hover {
  border-color: var(--primary-color);
  background: white;
}

.pipeline-step.step-completed {
  border-color: #10b981;
  background: #f0fdf4;
}

.pipeline-step.step-failed {
  border-color: #ef4444;
  background: #fef2f2;
}

.pipeline-step.step-running {
  border-color: #3b82f6;
  background: #eff6ff;
}

.step-content {
  width: 100%;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.step-icon {
  flex-shrink: 0;
  color: var(--text-muted);
}

.step-info {
  flex: 1;
  min-width: 0;
}

.step-name {
  font-weight: 500;
  color: var(--text-color);
  font-size: 0.875rem;
}

.step-type {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.step-status {
  flex-shrink: 0;
}

.step-description {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.step-config {
  margin-top: 0.5rem;
}

.config-preview {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.config-item {
  font-size: 0.75rem;
  font-family: monospace;
}

.config-key {
  color: var(--text-muted);
  margin-right: 0.25rem;
}

.config-value {
  color: var(--text-color);
  font-weight: 500;
}

.pipeline-connector {
  flex-shrink: 0;
  color: var(--text-muted);
  margin: 0 0.5rem;
}

/* Execution Stats */
.execution-stats {
  background: var(--background-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stats-header h5 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.stats-period {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Recent Executions */
.recent-executions {
  margin-bottom: 1.5rem;
}

.executions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.executions-header h5 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.executions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.execution-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--background-color);
  border-radius: 0.375rem;
}

.execution-status {
  flex-shrink: 0;
}

.execution-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.execution-time {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-color);
}

.execution-duration {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.execution-records {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-left: auto;
}

.execution-error {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #dc2626;
  margin-left: auto;
}

/* Transformation Footer */
.transformation-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  gap: 1rem;
}

.footer-left {
  flex: 1;
  min-width: 0;
}

.creation-info,
.last-execution {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.footer-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.toggle-disable {
  color: #dc2626;
}

.toggle-enable {
  color: #059669;
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
  .transformations-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .filters {
    flex-wrap: wrap;
  }
  
  .stats-overview {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .pipeline-flow {
    flex-direction: column;
    align-items: stretch;
  }
  
  .pipeline-connector {
    transform: rotate(90deg);
    align-self: center;
    margin: 0.5rem 0;
  }
  
  .pipeline-step {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .search-input {
    min-width: auto;
  }
  
  .transformation-info {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
    margin-right: 0;
  }
  
  .transformation-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .execution-item {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .execution-records,
  .execution-error {
    margin-left: 0;
  }
  
  .transformation-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .footer-actions {
    justify-content: stretch;
  }
  
  .footer-actions .button {
    flex: 1;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .transformation-item {
    padding: 1rem;
  }
  
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .pipeline-step {
    padding: 0.75rem;
  }
  
  .execution-stats {
    padding: 1rem;
  }
}
</style>