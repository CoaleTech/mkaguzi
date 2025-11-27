<template>
  <div class="integrations-overview">
    <!-- Header -->
    <div class="overview-header">
      <div class="header-left">
        <h3>API Integrations</h3>
        <p>Manage external system connections and configurations</p>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="refreshIntegrations">
          <RefreshCw class="w-4 h-4 mr-2" :class="{ 'animate-spin': refreshing }" />
          Refresh
        </Button>
        
        <Button variant="solid" @click="$emit('create')">
          <Plus class="w-4 h-4 mr-2" />
          Add Integration
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filters">
        <FormControl
          type="text"
          v-model="searchQuery"
          placeholder="Search integrations..."
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
              <Database class="w-4 h-4 mr-2" />
              {{ selectedType || 'All Types' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
        
        <Dropdown :options="healthFilterOptions" @click="handleHealthFilter">
          <template #default>
            <Button variant="outline">
              <Shield class="w-4 h-4 mr-2" />
              {{ selectedHealth || 'All Health' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <Loader class="w-6 h-6 animate-spin" />
      <p>Loading integrations...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredIntegrations.length === 0" class="empty-state">
      <Globe class="w-16 h-16 text-gray-300" />
      <h4>{{ searchQuery ? 'No integrations found' : 'No integrations yet' }}</h4>
      <p>
        {{ searchQuery 
          ? 'Try adjusting your search terms or filters.' 
          : 'Create your first API integration to connect external systems.' 
        }}
      </p>
      <Button v-if="!searchQuery" variant="solid" @click="$emit('create')">
        Add Integration
      </Button>
    </div>

    <!-- Integrations Grid -->
    <div v-else class="integrations-grid">
      <div
        v-for="integration in paginatedIntegrations"
        :key="integration.id"
        class="integration-card"
        :class="getIntegrationCardClass(integration)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="integration-info">
            <div class="integration-name">
              <h4>{{ integration.name }}</h4>
              <div class="integration-meta">
                <span class="integration-type">{{ integration.type }}</span>
                <span class="integration-version">v{{ integration.version }}</span>
              </div>
            </div>
            
            <div class="integration-actions">
              <Dropdown :options="getIntegrationActions(integration)" @click="handleAction">
                <template #default>
                  <Button variant="ghost" size="sm">
                    <MoreVertical class="w-4 h-4" />
                  </Button>
                </template>
              </Dropdown>
            </div>
          </div>
          
          <div class="status-indicators">
            <div 
              class="status-badge"
              :class="getStatusClass(integration.status)"
            >
              <component :is="getStatusIcon(integration.status)" class="w-3 h-3" />
              <span>{{ integration.status }}</span>
            </div>
            
            <div 
              class="health-indicator"
              :class="getHealthClass(integration.health_status)"
            >
              <component :is="getHealthIcon(integration.health_status)" class="w-3 h-3" />
              <span>{{ integration.health_status }}</span>
            </div>
          </div>
        </div>

        <!-- Card Content -->
        <div class="card-content">
          <p class="integration-description">{{ integration.description }}</p>
          
          <div class="integration-details">
            <div class="detail-row">
              <Globe class="w-4 h-4" />
              <div>
                <span class="detail-label">Base URL</span>
                <span class="detail-value">{{ formatUrl(integration.base_url) }}</span>
              </div>
            </div>
            
            <div class="detail-row">
              <Key class="w-4 h-4" />
              <div>
                <span class="detail-label">Authentication</span>
                <span class="detail-value">{{ integration.auth_type }}</span>
              </div>
            </div>
            
            <div class="detail-row">
              <Clock class="w-4 h-4" />
              <div>
                <span class="detail-label">Last Sync</span>
                <span class="detail-value">{{ formatRelativeTime(integration.last_sync) }}</span>
              </div>
            </div>
            
            <div class="detail-row">
              <Gauge class="w-4 h-4" />
              <div>
                <span class="detail-label">Rate Limit</span>
                <span class="detail-value">{{ integration.rate_limit }}/{{ integration.rate_period }}</span>
              </div>
            </div>
          </div>

          <!-- Integration Metrics -->
          <div class="metrics-section">
            <div class="metrics-header">
              <h5>Performance Metrics</h5>
              <span class="uptime-badge" :class="getUptimeClass(integration.metadata.uptime_percentage)">
                {{ integration.metadata.uptime_percentage }}% uptime
              </span>
            </div>
            
            <div class="metrics-grid">
              <div class="metric-item">
                <span class="metric-value">{{ formatNumber(integration.metadata.total_requests) }}</span>
                <span class="metric-label">Total Requests</span>
              </div>
              
              <div class="metric-item">
                <span class="metric-value">{{ formatNumber(integration.metadata.successful_requests) }}</span>
                <span class="metric-label">Successful</span>
              </div>
              
              <div class="metric-item">
                <span class="metric-value">{{ formatNumber(integration.metadata.failed_requests) }}</span>
                <span class="metric-label">Failed</span>
              </div>
              
              <div class="metric-item">
                <span class="metric-value">{{ integration.metadata.avg_response_time }}ms</span>
                <span class="metric-label">Avg Response</span>
              </div>
            </div>
          </div>

          <!-- Tags -->
          <div v-if="integration.tags?.length" class="tags-section">
            <div
              v-for="tag in integration.tags"
              :key="tag"
              class="tag"
            >
              {{ tag }}
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-left">
            <div class="sync-info">
              <div v-if="integration.next_sync" class="sync-item">
                <Calendar class="w-3 h-3" />
                <span>Next sync: {{ formatRelativeTime(integration.next_sync) }}</span>
              </div>
              
              <div v-if="integration.metadata.last_error" class="error-item">
                <AlertCircle class="w-3 h-3" />
                <span>{{ integration.metadata.last_error }}</span>
              </div>
            </div>
          </div>
          
          <div class="footer-actions">
            <Button
              variant="ghost"
              size="sm"
              @click="$emit('test', integration)"
              :disabled="integration.status !== 'Active'"
            >
              <Zap class="w-3 h-3 mr-1" />
              Test
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              @click="$emit('edit', integration)"
            >
              <Edit class="w-3 h-3 mr-1" />
              Edit
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              @click="$emit('toggle', integration)"
              :class="getToggleButtonClass(integration.status)"
            >
              <component :is="getToggleIcon(integration.status)" class="w-3 h-3 mr-1" />
              {{ integration.status === 'Active' ? 'Disable' : 'Enable' }}
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <div class="pagination-info">
        Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to 
        {{ Math.min(currentPage * itemsPerPage, filteredIntegrations.length) }} of 
        {{ filteredIntegrations.length }} integrations
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
	Calendar,
	CheckCircle,
	ChevronDown,
	ChevronLeft,
	ChevronRight,
	Clock,
	Database,
	Edit,
	Filter,
	Gauge,
	Globe,
	Key,
	Loader,
	MoreVertical,
	Plus,
	Power,
	PowerOff,
	RefreshCw,
	Search,
	Shield,
	Wifi,
	WifiOff,
	XCircle,
	Zap,
} from "lucide-vue-next"
import { computed, ref, watch } from "vue"

const props = defineProps({
	integrations: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["create", "edit", "test", "toggle", "delete"])

// Local state
const searchQuery = ref("")
const selectedStatus = ref("")
const selectedType = ref("")
const selectedHealth = ref("")
const currentPage = ref(1)
const itemsPerPage = ref(9)
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
	{ label: "REST", value: "REST" },
	{ label: "GraphQL", value: "GraphQL" },
	{ label: "SOAP", value: "SOAP" },
	{ label: "WebSocket", value: "WebSocket" },
]

const healthFilterOptions = [
	{ label: "All Health", value: "" },
	{ label: "Healthy", value: "Healthy" },
	{ label: "Warning", value: "Warning" },
	{ label: "Error", value: "Error" },
	{ label: "Disconnected", value: "Disconnected" },
]

// Computed
const filteredIntegrations = computed(() => {
	let filtered = [...props.integrations]

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		filtered = filtered.filter(
			(integration) =>
				integration.name.toLowerCase().includes(query) ||
				integration.description.toLowerCase().includes(query) ||
				integration.type.toLowerCase().includes(query) ||
				integration.tags?.some((tag) => tag.toLowerCase().includes(query)),
		)
	}

	// Status filter
	if (selectedStatus.value) {
		filtered = filtered.filter(
			(integration) => integration.status === selectedStatus.value,
		)
	}

	// Type filter
	if (selectedType.value) {
		filtered = filtered.filter(
			(integration) => integration.type === selectedType.value,
		)
	}

	// Health filter
	if (selectedHealth.value) {
		filtered = filtered.filter(
			(integration) => integration.health_status === selectedHealth.value,
		)
	}

	// Sort by name
	filtered.sort((a, b) => a.name.localeCompare(b.name))

	return filtered
})

const totalPages = computed(() =>
	Math.ceil(filteredIntegrations.value.length / itemsPerPage.value),
)

const paginatedIntegrations = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	return filteredIntegrations.value.slice(start, start + itemsPerPage.value)
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
const refreshIntegrations = async () => {
	refreshing.value = true
	try {
		// Simulate refresh
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

const handleHealthFilter = (option) => {
	selectedHealth.value = option.value
	currentPage.value = 1
}

const getIntegrationCardClass = (integration) => {
	return {
		"card-inactive": integration.status === "Inactive",
		"card-error": integration.health_status === "Error",
		"card-warning": integration.health_status === "Warning",
		"card-disconnected": integration.health_status === "Disconnected",
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
		Error: XCircle,
	}
	return icons[status] || XCircle
}

const getHealthClass = (health) => {
	return {
		"health-healthy": health === "Healthy",
		"health-warning": health === "Warning",
		"health-error": health === "Error",
		"health-disconnected": health === "Disconnected",
	}
}

const getHealthIcon = (health) => {
	const icons = {
		Healthy: CheckCircle,
		Warning: AlertCircle,
		Error: XCircle,
		Disconnected: WifiOff,
	}
	return icons[health] || AlertCircle
}

const getUptimeClass = (uptime) => {
	if (uptime >= 99) return "uptime-excellent"
	if (uptime >= 95) return "uptime-good"
	if (uptime >= 90) return "uptime-warning"
	return "uptime-poor"
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

const formatUrl = (url) => {
	try {
		const urlObj = new URL(url)
		return urlObj.hostname
	} catch {
		return url
	}
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

const formatNumber = (num) => {
	if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
	if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
	return num.toString()
}

const getIntegrationActions = (integration) => [
	{
		label: "View Details",
		value: "view",
		action: () => console.log("View", integration.id),
	},
	{
		label: "Test Connection",
		value: "test",
		action: () => emit("test", integration),
	},
	{
		label: "Edit Configuration",
		value: "edit",
		action: () => emit("edit", integration),
	},
	{
		label: "View Logs",
		value: "logs",
		action: () => console.log("View logs", integration.id),
	},
	{
		label: "Duplicate",
		value: "duplicate",
		action: () => console.log("Duplicate", integration.id),
	},
	{
		label: integration.status === "Active" ? "Disable" : "Enable",
		value: "toggle",
		action: () => emit("toggle", integration),
	},
	{
		label: "Delete",
		value: "delete",
		action: () => emit("delete", integration),
		dangerous: true,
	},
]

const handleAction = (action) => {
	if (action.action) {
		action.action()
	}
}

// Watchers
watch([searchQuery, selectedStatus, selectedType, selectedHealth], () => {
	currentPage.value = 1
})
</script>

<style scoped>
.integrations-overview {
  padding: 0;
}

.overview-header {
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

/* Integrations Grid */
.integrations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.integration-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  transition: all 0.2s;
}

.integration-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.integration-card.card-inactive {
  opacity: 0.7;
  background: #f9fafb;
}

.integration-card.card-error {
  border-left: 4px solid #ef4444;
}

.integration-card.card-warning {
  border-left: 4px solid #f59e0b;
}

.integration-card.card-disconnected {
  border-left: 4px solid #6b7280;
}

.card-header {
  margin-bottom: 1rem;
}

.integration-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.integration-name h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.integration-meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.integration-type,
.integration-version {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 500;
}

.integration-type {
  background: var(--primary-light);
  color: var(--primary-color);
}

.integration-version {
  background: var(--background-color);
  color: var(--text-muted);
}

.status-indicators {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.status-badge,
.health-indicator {
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

.health-indicator.health-healthy {
  background: #dcfce7;
  color: #166534;
}

.health-indicator.health-warning {
  background: #fef3c7;
  color: #92400e;
}

.health-indicator.health-error {
  background: #fee2e2;
  color: #991b1b;
}

.health-indicator.health-disconnected {
  background: #f3f4f6;
  color: #6b7280;
}

.card-content {
  margin-bottom: 1.5rem;
}

.integration-description {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin: 0 0 1rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.integration-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.detail-row > svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.detail-row > div {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.detail-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.125rem;
}

.detail-value {
  font-size: 0.875rem;
  color: var(--text-color);
  font-weight: 500;
  word-break: break-all;
}

/* Metrics Section */
.metrics-section {
  background: var(--background-color);
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.metrics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.metrics-header h5 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.uptime-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.uptime-badge.uptime-excellent {
  background: #dcfce7;
  color: #166534;
}

.uptime-badge.uptime-good {
  background: #fef3c7;
  color: #92400e;
}

.uptime-badge.uptime-warning {
  background: #fed7aa;
  color: #c2410c;
}

.uptime-badge.uptime-poor {
  background: #fee2e2;
  color: #991b1b;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.metric-item {
  text-align: center;
}

.metric-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
  margin-bottom: 0.25rem;
}

.metric-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Tags Section */
.tags-section {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tag {
  padding: 0.25rem 0.75rem;
  background: var(--background-color);
  color: var(--text-muted);
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.card-footer {
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

.sync-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sync-item,
.error-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.error-item {
  color: #dc2626;
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
  .integrations-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
  
  .overview-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .filters {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .search-input {
    min-width: auto;
  }
  
  .integrations-grid {
    grid-template-columns: 1fr;
  }
  
  .integration-info {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .status-indicators {
    justify-content: flex-start;
  }
  
  .card-footer {
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
  .integration-card {
    padding: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .integration-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>