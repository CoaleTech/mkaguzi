<template>
  <div class="webhook-manager">
    <!-- Header -->
    <div class="manager-header">
      <div class="header-left">
        <h3>Webhook Management</h3>
        <p>Configure and monitor webhook endpoints and deliveries</p>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="refreshWebhooks">
          <RefreshCw class="w-4 h-4 mr-2" :class="{ 'animate-spin': refreshing }" />
          Refresh
        </Button>
        
        <Button variant="solid" @click="$emit('create')">
          <Plus class="w-4 h-4 mr-2" />
          Create Webhook
        </Button>
      </div>
    </div>

    <!-- Webhook Statistics -->
    <div class="stats-cards">
      <div class="stats-card">
        <div class="stats-content">
          <div class="stats-value">{{ stats.total || 0 }}</div>
          <div class="stats-label">Total Webhooks</div>
        </div>
        <div class="stats-icon">
          <Webhook class="w-6 h-6 text-blue-500" />
        </div>
      </div>
      
      <div class="stats-card">
        <div class="stats-content">
          <div class="stats-value">{{ stats.active || 0 }}</div>
          <div class="stats-label">Active</div>
        </div>
        <div class="stats-icon">
          <CheckCircle class="w-6 h-6 text-green-500" />
        </div>
      </div>
      
      <div class="stats-card">
        <div class="stats-content">
          <div class="stats-value">{{ stats.total_deliveries || 0 }}</div>
          <div class="stats-label">Total Deliveries</div>
        </div>
        <div class="stats-icon">
          <Send class="w-6 h-6 text-purple-500" />
        </div>
      </div>
      
      <div class="stats-card">
        <div class="stats-content">
          <div class="stats-value">{{ stats.success_rate || 0 }}%</div>
          <div class="stats-label">Success Rate</div>
        </div>
        <div class="stats-icon">
          <TrendingUp class="w-6 h-6 text-emerald-500" />
        </div>
      </div>
    </div>

    <!-- Filters and Controls -->
    <div class="filters-section">
      <div class="filters">
        <FormControl
          type="text"
          v-model="searchQuery"
          placeholder="Search webhooks..."
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
        
        <Dropdown :options="eventFilterOptions" @click="handleEventFilter">
          <template #default>
            <Button variant="outline">
              <Zap class="w-4 h-4 mr-2" />
              {{ selectedEvent || 'All Events' }}
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

    <!-- Tab Navigation -->
    <div class="tab-navigation">
      <div class="tab-list">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-button"
          :class="{ 'active': activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <component :is="tab.icon" class="w-4 h-4" />
          {{ tab.label }}
          <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Webhooks Tab -->
      <div v-if="activeTab === 'webhooks'" class="webhooks-tab">
        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <Loader class="w-6 h-6 animate-spin" />
          <p>Loading webhooks...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredWebhooks.length === 0" class="empty-state">
          <Webhook class="w-16 h-16 text-gray-300" />
          <h4>{{ searchQuery ? 'No webhooks found' : 'No webhooks yet' }}</h4>
          <p>
            {{ searchQuery 
              ? 'Try adjusting your search terms or filters.' 
              : 'Create your first webhook to receive real-time notifications.' 
            }}
          </p>
          <Button v-if="!searchQuery" variant="solid" @click="$emit('create')">
            Create Webhook
          </Button>
        </div>

        <!-- Webhooks Grid -->
        <div v-else class="webhooks-grid">
          <div
            v-for="webhook in paginatedWebhooks"
            :key="webhook.id"
            class="webhook-card"
            :class="getWebhookCardClass(webhook)"
          >
            <!-- Card Header -->
            <div class="card-header">
              <div class="webhook-info">
                <div class="webhook-name">
                  <h4>{{ webhook.name }}</h4>
                  <div class="webhook-url">{{ formatUrl(webhook.url) }}</div>
                </div>
                
                <div class="webhook-actions">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="$emit('test', webhook)"
                    :disabled="webhook.status !== 'Active'"
                  >
                    <Zap class="w-3 h-3" />
                  </Button>
                  
                  <Dropdown :options="getWebhookActions(webhook)" @click="handleWebhookAction">
                    <template #default>
                      <Button variant="ghost" size="sm">
                        <MoreVertical class="w-4 h-4" />
                      </Button>
                    </template>
                  </Dropdown>
                </div>
              </div>
              
              <div class="status-row">
                <div class="status-badge" :class="getStatusClass(webhook.status)">
                  <component :is="getStatusIcon(webhook.status)" class="w-3 h-3" />
                  <span>{{ webhook.status }}</span>
                </div>
                
                <div class="webhook-method">{{ webhook.method }}</div>
              </div>
            </div>

            <!-- Card Content -->
            <div class="card-content">
              <div class="webhook-details">
                <div class="detail-row">
                  <Zap class="w-4 h-4" />
                  <div>
                    <span class="detail-label">Events</span>
                    <span class="detail-value">{{ webhook.events.join(', ') }}</span>
                  </div>
                </div>
                
                <div class="detail-row">
                  <Globe class="w-4 h-4" />
                  <div>
                    <span class="detail-label">Integration</span>
                    <span class="detail-value">{{ webhook.integration?.name || 'N/A' }}</span>
                  </div>
                </div>
                
                <div class="detail-row">
                  <Shield class="w-4 h-4" />
                  <div>
                    <span class="detail-label">Authentication</span>
                    <span class="detail-value">{{ webhook.auth_type || 'None' }}</span>
                  </div>
                </div>
              </div>

              <!-- Delivery Stats -->
              <div class="delivery-stats">
                <h5>Delivery Statistics</h5>
                <div class="stats-grid">
                  <div class="stat-item">
                    <span class="stat-value">{{ formatNumber(webhook.total_deliveries) }}</span>
                    <span class="stat-label">Total</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ formatNumber(webhook.successful_deliveries) }}</span>
                    <span class="stat-label">Success</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ formatNumber(webhook.failed_deliveries) }}</span>
                    <span class="stat-label">Failed</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ webhook.success_rate }}%</span>
                    <span class="stat-label">Rate</span>
                  </div>
                </div>
              </div>

              <!-- Last Delivery -->
              <div v-if="webhook.last_delivery" class="last-delivery">
                <div class="delivery-info">
                  <div class="delivery-status" :class="getDeliveryStatusClass(webhook.last_delivery.status)">
                    <component :is="getDeliveryStatusIcon(webhook.last_delivery.status)" class="w-3 h-3" />
                    {{ webhook.last_delivery.status }}
                  </div>
                  <div class="delivery-time">{{ formatRelativeTime(webhook.last_delivery.created_at) }}</div>
                </div>
                <div class="delivery-response">
                  Response: {{ webhook.last_delivery.response_code }} ({{ webhook.last_delivery.response_time }}ms)
                </div>
              </div>
            </div>

            <!-- Card Footer -->
            <div class="card-footer">
              <div class="footer-left">
                <span class="created-date">Created {{ formatRelativeTime(webhook.created_at) }}</span>
              </div>
              
              <div class="footer-actions">
                <Button
                  variant="ghost"
                  size="sm"
                  @click="$emit('edit', webhook)"
                >
                  <Edit class="w-3 h-3 mr-1" />
                  Edit
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  @click="$emit('toggle', webhook)"
                  :class="getToggleButtonClass(webhook.status)"
                >
                  <component :is="getToggleIcon(webhook.status)" class="w-3 h-3 mr-1" />
                  {{ webhook.status === 'Active' ? 'Disable' : 'Enable' }}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Deliveries Tab -->
      <div v-else-if="activeTab === 'deliveries'" class="deliveries-tab">
        <WebhookDeliveriesList 
          :deliveries="deliveries"
          :loading="deliveriesLoading"
          @retry="$emit('retry', $event)"
          @view="$emit('viewDelivery', $event)"
        />
      </div>

      <!-- Events Tab -->
      <div v-else-if="activeTab === 'events'" class="events-tab">
        <EventsConfiguration
          :events="availableEvents"
          @save="$emit('saveEvents', $event)"
        />
      </div>

      <!-- Logs Tab -->
      <div v-else-if="activeTab === 'logs'" class="logs-tab">
        <WebhookLogs
          :logs="logs"
          :loading="logsLoading"
          @export="$emit('exportLogs')"
        />
      </div>
    </div>

    <!-- Pagination (for webhooks tab) -->
    <div v-if="activeTab === 'webhooks' && totalPages > 1" class="pagination">
      <div class="pagination-info">
        Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to 
        {{ Math.min(currentPage * itemsPerPage, filteredWebhooks.length) }} of 
        {{ filteredWebhooks.length }} webhooks
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
	Activity,
	AlertTriangle,
	CheckCircle,
	ChevronDown,
	ChevronLeft,
	ChevronRight,
	Clock,
	Edit,
	FileText,
	Filter,
	Globe,
	Loader,
	MoreVertical,
	Plus,
	Power,
	PowerOff,
	RefreshCw,
	Search,
	Send,
	Settings,
	Shield,
	TrendingUp,
	Webhook,
	XCircle,
	Zap,
} from "lucide-vue-next"
import { computed, ref, watch } from "vue"
import EventsConfiguration from "./EventsConfiguration.vue"
import WebhookDeliveriesList from "./WebhookDeliveriesList.vue"
import WebhookLogs from "./WebhookLogs.vue"

const props = defineProps({
	webhooks: {
		type: Array,
		default: () => [],
	},
	deliveries: {
		type: Array,
		default: () => [],
	},
	logs: {
		type: Array,
		default: () => [],
	},
	availableEvents: {
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
	deliveriesLoading: {
		type: Boolean,
		default: false,
	},
	logsLoading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits([
	"create",
	"edit",
	"test",
	"toggle",
	"delete",
	"retry",
	"viewDelivery",
	"saveEvents",
	"exportLogs",
])

// Local state
const activeTab = ref("webhooks")
const searchQuery = ref("")
const selectedStatus = ref("")
const selectedEvent = ref("")
const selectedIntegration = ref("")
const currentPage = ref(1)
const itemsPerPage = ref(9)
const refreshing = ref(false)

// Tab configuration
const tabs = computed(() => [
	{
		id: "webhooks",
		label: "Webhooks",
		icon: Webhook,
		count: props.webhooks.length,
	},
	{
		id: "deliveries",
		label: "Deliveries",
		icon: Send,
		count: props.deliveries.length,
	},
	{
		id: "events",
		label: "Events",
		icon: Activity,
	},
	{
		id: "logs",
		label: "Logs",
		icon: FileText,
	},
])

// Filter options
const statusFilterOptions = [
	{ label: "All Status", value: "" },
	{ label: "Active", value: "Active" },
	{ label: "Inactive", value: "Inactive" },
	{ label: "Error", value: "Error" },
]

const eventFilterOptions = [
	{ label: "All Events", value: "" },
	{ label: "sync.completed", value: "sync.completed" },
	{ label: "sync.failed", value: "sync.failed" },
	{ label: "data.created", value: "data.created" },
	{ label: "data.updated", value: "data.updated" },
	{ label: "data.deleted", value: "data.deleted" },
	{ label: "integration.connected", value: "integration.connected" },
	{ label: "integration.disconnected", value: "integration.disconnected" },
]

const integrationFilterOptions = computed(() => [
	{ label: "All Integrations", value: "" },
	...props.integrations.map((integration) => ({
		label: integration.name,
		value: integration.id,
	})),
])

// Computed properties
const filteredWebhooks = computed(() => {
	let filtered = [...props.webhooks]

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		filtered = filtered.filter(
			(webhook) =>
				webhook.name.toLowerCase().includes(query) ||
				webhook.url.toLowerCase().includes(query) ||
				webhook.events.some((event) => event.toLowerCase().includes(query)),
		)
	}

	// Status filter
	if (selectedStatus.value) {
		filtered = filtered.filter(
			(webhook) => webhook.status === selectedStatus.value,
		)
	}

	// Event filter
	if (selectedEvent.value) {
		filtered = filtered.filter((webhook) =>
			webhook.events.includes(selectedEvent.value),
		)
	}

	// Integration filter
	if (selectedIntegration.value) {
		filtered = filtered.filter(
			(webhook) => webhook.integration?.id === selectedIntegration.value,
		)
	}

	// Sort by name
	filtered.sort((a, b) => a.name.localeCompare(b.name))

	return filtered
})

const totalPages = computed(() =>
	Math.ceil(filteredWebhooks.value.length / itemsPerPage.value),
)

const paginatedWebhooks = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	return filteredWebhooks.value.slice(start, start + itemsPerPage.value)
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
const refreshWebhooks = async () => {
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

const handleEventFilter = (option) => {
	selectedEvent.value = option.value
	currentPage.value = 1
}

const handleIntegrationFilter = (option) => {
	selectedIntegration.value = option.value
	currentPage.value = 1
}

const getWebhookCardClass = (webhook) => {
	return {
		"card-inactive": webhook.status === "Inactive",
		"card-error": webhook.status === "Error",
		"card-high-success": webhook.success_rate >= 95,
		"card-medium-success":
			webhook.success_rate >= 80 && webhook.success_rate < 95,
		"card-low-success": webhook.success_rate < 80,
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
		Error: AlertTriangle,
	}
	return icons[status] || XCircle
}

const getDeliveryStatusClass = (status) => {
	return {
		"delivery-success": status === "Success",
		"delivery-failed": status === "Failed",
		"delivery-pending": status === "Pending",
	}
}

const getDeliveryStatusIcon = (status) => {
	const icons = {
		Success: CheckCircle,
		Failed: XCircle,
		Pending: Clock,
	}
	return icons[status] || Clock
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
		return `${urlObj.hostname}${urlObj.pathname}`
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
	if (!num) return "0"
	if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
	if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
	return num.toString()
}

const getWebhookActions = (webhook) => [
	{
		label: "View Deliveries",
		value: "deliveries",
		action: () => {
			activeTab.value = "deliveries"
			// Filter deliveries by webhook
		},
	},
	{
		label: "Test Webhook",
		value: "test",
		action: () => emit("test", webhook),
	},
	{
		label: "Edit Configuration",
		value: "edit",
		action: () => emit("edit", webhook),
	},
	{
		label: "View Logs",
		value: "logs",
		action: () => {
			activeTab.value = "logs"
			// Filter logs by webhook
		},
	},
	{
		label: "Duplicate",
		value: "duplicate",
		action: () => console.log("Duplicate", webhook.id),
	},
	{
		label: webhook.status === "Active" ? "Disable" : "Enable",
		value: "toggle",
		action: () => emit("toggle", webhook),
	},
	{
		label: "Delete",
		value: "delete",
		action: () => emit("delete", webhook),
		dangerous: true,
	},
]

const handleWebhookAction = (action) => {
	if (action.action) {
		action.action()
	}
}

// Watchers
watch([searchQuery, selectedStatus, selectedEvent, selectedIntegration], () => {
	currentPage.value = 1
})

watch(activeTab, () => {
	// Reset filters when switching tabs
	searchQuery.value = ""
	selectedStatus.value = ""
	selectedEvent.value = ""
	selectedIntegration.value = ""
	currentPage.value = 1
})
</script>

<style scoped>
.webhook-manager {
  padding: 0;
}

.manager-header {
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

/* Stats Cards */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stats-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-content {
  flex: 1;
}

.stats-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stats-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-weight: 500;
}

.stats-icon {
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

/* Tab Navigation */
.tab-navigation {
  margin-bottom: 1.5rem;
}

.tab-list {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  color: var(--text-muted);
  font-weight: 500;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-button:hover {
  color: var(--text-color);
}

.tab-button.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.tab-count {
  background: var(--background-color);
  color: var(--text-muted);
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 600;
}

.tab-button.active .tab-count {
  background: var(--primary-light);
  color: var(--primary-color);
}

.tab-content {
  min-height: 400px;
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

/* Webhooks Grid */
.webhooks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.webhook-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  transition: all 0.2s;
}

.webhook-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.webhook-card.card-inactive {
  opacity: 0.7;
  background: #f9fafb;
}

.webhook-card.card-error {
  border-left: 4px solid #ef4444;
}

.webhook-card.card-high-success {
  border-left: 4px solid #10b981;
}

.webhook-card.card-medium-success {
  border-left: 4px solid #f59e0b;
}

.webhook-card.card-low-success {
  border-left: 4px solid #ef4444;
}

.card-header {
  margin-bottom: 1rem;
}

.webhook-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.webhook-name h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.webhook-url {
  font-size: 0.875rem;
  color: var(--text-muted);
  word-break: break-all;
}

.webhook-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.webhook-method {
  background: var(--primary-light);
  color: var(--primary-color);
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.card-content {
  margin-bottom: 1.5rem;
}

.webhook-details {
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

.delivery-stats {
  background: var(--background-color);
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.delivery-stats h5 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.75rem 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.last-delivery {
  background: var(--background-color);
  border-radius: 0.375rem;
  padding: 0.75rem;
  margin-bottom: 1rem;
}

.delivery-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.delivery-status {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.delivery-status.delivery-success {
  color: #166534;
}

.delivery-status.delivery-failed {
  color: #991b1b;
}

.delivery-status.delivery-pending {
  color: #92400e;
}

.delivery-time {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.delivery-response {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: monospace;
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

.created-date {
  font-size: 0.75rem;
  color: var(--text-muted);
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
  .webhooks-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
  
  .manager-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .filters {
    flex-wrap: wrap;
  }
  
  .stats-cards {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}

@media (max-width: 768px) {
  .search-input {
    min-width: auto;
  }
  
  .webhooks-grid {
    grid-template-columns: 1fr;
  }
  
  .webhook-info {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .status-row {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 0.5rem;
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
  
  .tab-list {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .tab-button {
    flex-shrink: 0;
    padding: 0.75rem 1rem;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .webhook-card {
    padding: 1rem;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .stats-card {
    padding: 1rem;
  }
  
  .stats-value {
    font-size: 1.5rem;
  }
  
  .delivery-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>