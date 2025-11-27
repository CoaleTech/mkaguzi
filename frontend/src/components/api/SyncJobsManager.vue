<template>
  <div class="sync-jobs-manager">
    <!-- Header -->
    <div class="manager-header">
      <div class="header-left">
        <h3>Sync Jobs</h3>
        <p>Monitor and manage data synchronization jobs</p>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="refreshJobs">
          <RefreshCw class="w-4 h-4 mr-2" :class="{ 'animate-spin': refreshing }" />
          Refresh
        </Button>
        
        <Button variant="solid" @click="$emit('create')">
          <Play class="w-4 h-4 mr-2" />
          Start Sync Job
        </Button>
      </div>
    </div>

    <!-- Filters and Controls -->
    <div class="filters-section">
      <div class="filters">
        <FormControl
          type="text"
          v-model="searchQuery"
          placeholder="Search sync jobs..."
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
        
        <Dropdown :options="integrationFilterOptions" @click="handleIntegrationFilter">
          <template #default>
            <Button variant="outline">
              <Globe class="w-4 h-4 mr-2" />
              {{ selectedIntegration || 'All Integrations' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
        
        <Dropdown :options="sortOptions" @click="handleSort">
          <template #default>
            <Button variant="outline">
              <ArrowUpDown class="w-4 h-4 mr-2" />
              {{ sortBy || 'Sort by Created' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
      </div>
      
      <div v-if="selectedJobs.length > 0" class="bulk-actions">
        <span class="selection-count">{{ selectedJobs.length }} selected</span>
        
        <div class="bulk-buttons">
          <Button variant="outline" size="sm" @click="bulkCancel">
            <X class="w-3 h-3 mr-1" />
            Cancel
          </Button>
          
          <Button variant="outline" size="sm" @click="bulkRetry">
            <RotateCcw class="w-3 h-3 mr-1" />
            Retry
          </Button>
          
          <Button variant="outline" size="sm" @click="bulkDelete">
            <Trash class="w-3 h-3 mr-1" />
            Delete
          </Button>
        </div>
      </div>
    </div>

    <!-- Jobs Summary Cards -->
    <div class="summary-cards">
      <div class="summary-card">
        <div class="summary-content">
          <div class="summary-value">{{ stats.total || 0 }}</div>
          <div class="summary-label">Total Jobs</div>
        </div>
        <div class="summary-icon">
          <List class="w-6 h-6 text-blue-500" />
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-content">
          <div class="summary-value">{{ stats.running || 0 }}</div>
          <div class="summary-label">Running</div>
        </div>
        <div class="summary-icon">
          <Play class="w-6 h-6 text-green-500" />
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-content">
          <div class="summary-value">{{ stats.completed || 0 }}</div>
          <div class="summary-label">Completed</div>
        </div>
        <div class="summary-icon">
          <CheckCircle class="w-6 h-6 text-emerald-500" />
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-content">
          <div class="summary-value">{{ stats.failed || 0 }}</div>
          <div class="summary-label">Failed</div>
        </div>
        <div class="summary-icon">
          <XCircle class="w-6 h-6 text-red-500" />
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <Loader class="w-6 h-6 animate-spin" />
      <p>Loading sync jobs...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredJobs.length === 0" class="empty-state">
      <Sync class="w-16 h-16 text-gray-300" />
      <h4>{{ searchQuery ? 'No sync jobs found' : 'No sync jobs yet' }}</h4>
      <p>
        {{ searchQuery 
          ? 'Try adjusting your search terms or filters.' 
          : 'Start your first data synchronization job.' 
        }}
      </p>
      <Button v-if="!searchQuery" variant="solid" @click="$emit('create')">
        Start Sync Job
      </Button>
    </div>

    <!-- Jobs Table -->
    <div v-else class="jobs-table-container">
      <div class="jobs-table">
        <div class="table-header">
          <div class="header-cell select-cell">
            <Checkbox
              :checked="allSelected"
              :indeterminate="someSelected"
              @change="toggleSelectAll"
            />
          </div>
          <div class="header-cell">Job Name</div>
          <div class="header-cell">Integration</div>
          <div class="header-cell">Status</div>
          <div class="header-cell">Progress</div>
          <div class="header-cell">Duration</div>
          <div class="header-cell">Records</div>
          <div class="header-cell">Actions</div>
        </div>
        
        <div class="table-body">
          <div
            v-for="job in paginatedJobs"
            :key="job.id"
            class="table-row"
            :class="getJobRowClass(job)"
          >
            <div class="table-cell select-cell">
              <Checkbox
                :checked="selectedJobs.includes(job.id)"
                @change="toggleJobSelection(job.id)"
              />
            </div>
            
            <div class="table-cell job-info">
              <div class="job-name">{{ job.name }}</div>
              <div class="job-type">{{ job.type }}</div>
              <div v-if="job.error_message" class="job-error">
                <AlertCircle class="w-3 h-3" />
                {{ job.error_message }}
              </div>
            </div>
            
            <div class="table-cell">
              <div class="integration-info">
                <div class="integration-name">{{ job.integration.name }}</div>
                <div class="integration-type">{{ job.integration.type }}</div>
              </div>
            </div>
            
            <div class="table-cell">
              <div class="status-badge" :class="getStatusClass(job.status)">
                <component :is="getStatusIcon(job.status)" class="w-3 h-3" />
                <span>{{ job.status }}</span>
              </div>
            </div>
            
            <div class="table-cell">
              <div class="progress-container">
                <div class="progress-bar">
                  <div 
                    class="progress-fill"
                    :class="getProgressClass(job.status)"
                    :style="{ width: `${job.progress_percentage || 0}%` }"
                  ></div>
                </div>
                <div class="progress-text">{{ job.progress_percentage || 0 }}%</div>
              </div>
            </div>
            
            <div class="table-cell">
              <div class="duration-info">
                <div class="duration-time">{{ formatDuration(job.duration) }}</div>
                <div class="duration-times">
                  <span>Started: {{ formatTime(job.started_at) }}</span>
                  <span v-if="job.completed_at">Ended: {{ formatTime(job.completed_at) }}</span>
                </div>
              </div>
            </div>
            
            <div class="table-cell">
              <div class="records-stats">
                <div class="records-count">
                  {{ formatNumber(job.records_processed) }} / {{ formatNumber(job.total_records) }}
                </div>
                <div class="records-breakdown">
                  <span v-if="job.records_success" class="success">
                    ✓ {{ formatNumber(job.records_success) }}
                  </span>
                  <span v-if="job.records_failed" class="failed">
                    ✗ {{ formatNumber(job.records_failed) }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="table-cell actions-cell">
              <div class="job-actions">
                <Button
                  v-if="job.status === 'Running'"
                  variant="ghost"
                  size="sm"
                  @click="$emit('pause', job)"
                >
                  <Pause class="w-3 h-3" />
                </Button>
                
                <Button
                  v-if="job.status === 'Paused'"
                  variant="ghost"
                  size="sm"
                  @click="$emit('resume', job)"
                >
                  <Play class="w-3 h-3" />
                </Button>
                
                <Button
                  v-if="['Running', 'Queued', 'Paused'].includes(job.status)"
                  variant="ghost"
                  size="sm"
                  @click="$emit('cancel', job)"
                >
                  <X class="w-3 h-3" />
                </Button>
                
                <Button
                  v-if="['Failed', 'Cancelled'].includes(job.status)"
                  variant="ghost"
                  size="sm"
                  @click="$emit('retry', job)"
                >
                  <RotateCcw class="w-3 h-3" />
                </Button>
                
                <Dropdown :options="getJobActions(job)" @click="handleJobAction">
                  <template #default>
                    <Button variant="ghost" size="sm">
                      <MoreVertical class="w-3 h-3" />
                    </Button>
                  </template>
                </Dropdown>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <div class="pagination-info">
        Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to 
        {{ Math.min(currentPage * itemsPerPage, filteredJobs.length) }} of 
        {{ filteredJobs.length }} sync jobs
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
import { Button, Checkbox, Dropdown, FormControl } from "frappe-ui"
import {
	AlertCircle,
	ArrowUpDown,
	CheckCircle,
	ChevronDown,
	ChevronLeft,
	ChevronRight,
	Clock,
	Download,
	Eye,
	Filter,
	Globe,
	List,
	Loader,
	MoreVertical,
	Pause,
	Play,
	RefreshCw,
	RotateCcw,
	Search,
	Sync,
	Trash,
	X,
	XCircle,
} from "lucide-vue-next"
import { computed, ref, watch } from "vue"

const props = defineProps({
	jobs: {
		type: Array,
		default: () => [],
	},
	integrations: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
	stats: {
		type: Object,
		default: () => ({}),
	},
})

const emit = defineEmits([
	"create",
	"pause",
	"resume",
	"cancel",
	"retry",
	"delete",
	"view",
	"download",
])

// Local state
const searchQuery = ref("")
const selectedStatus = ref("")
const selectedIntegration = ref("")
const sortBy = ref("")
const sortOrder = ref("desc")
const currentPage = ref(1)
const itemsPerPage = ref(10)
const refreshing = ref(false)
const selectedJobs = ref([])

// Filter and sort options
const statusFilterOptions = [
	{ label: "All Status", value: "" },
	{ label: "Queued", value: "Queued" },
	{ label: "Running", value: "Running" },
	{ label: "Paused", value: "Paused" },
	{ label: "Completed", value: "Completed" },
	{ label: "Failed", value: "Failed" },
	{ label: "Cancelled", value: "Cancelled" },
]

const integrationFilterOptions = computed(() => [
	{ label: "All Integrations", value: "" },
	...props.integrations.map((integration) => ({
		label: integration.name,
		value: integration.id,
	})),
])

const sortOptions = [
	{ label: "Sort by Created", value: "created_at" },
	{ label: "Sort by Started", value: "started_at" },
	{ label: "Sort by Status", value: "status" },
	{ label: "Sort by Duration", value: "duration" },
	{ label: "Sort by Progress", value: "progress_percentage" },
]

// Computed properties
const filteredJobs = computed(() => {
	let filtered = [...props.jobs]

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		filtered = filtered.filter(
			(job) =>
				job.name.toLowerCase().includes(query) ||
				job.type.toLowerCase().includes(query) ||
				job.integration.name.toLowerCase().includes(query),
		)
	}

	// Status filter
	if (selectedStatus.value) {
		filtered = filtered.filter((job) => job.status === selectedStatus.value)
	}

	// Integration filter
	if (selectedIntegration.value) {
		filtered = filtered.filter(
			(job) => job.integration.id === selectedIntegration.value,
		)
	}

	// Sort
	const sortKey = sortBy.value || "created_at"
	filtered.sort((a, b) => {
		let aValue = a[sortKey]
		let bValue = b[sortKey]

		if (sortKey === "duration") {
			aValue = a.duration || 0
			bValue = b.duration || 0
		}

		if (sortKey.includes("_at")) {
			aValue = new Date(aValue)
			bValue = new Date(bValue)
		}

		if (sortOrder.value === "asc") {
			return aValue < bValue ? -1 : aValue > bValue ? 1 : 0
		} else {
			return aValue > bValue ? -1 : aValue < bValue ? 1 : 0
		}
	})

	return filtered
})

const totalPages = computed(() =>
	Math.ceil(filteredJobs.value.length / itemsPerPage.value),
)

const paginatedJobs = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	return filteredJobs.value.slice(start, start + itemsPerPage.value)
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

const allSelected = computed(
	() =>
		paginatedJobs.value.length > 0 &&
		paginatedJobs.value.every((job) => selectedJobs.value.includes(job.id)),
)

const someSelected = computed(
	() => selectedJobs.value.length > 0 && !allSelected.value,
)

// Methods
const refreshJobs = async () => {
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

const handleIntegrationFilter = (option) => {
	selectedIntegration.value = option.value
	currentPage.value = 1
}

const handleSort = (option) => {
	if (sortBy.value === option.value) {
		sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc"
	} else {
		sortBy.value = option.value
		sortOrder.value = "desc"
	}
	currentPage.value = 1
}

const toggleSelectAll = () => {
	if (allSelected.value) {
		selectedJobs.value = selectedJobs.value.filter(
			(id) => !paginatedJobs.value.find((job) => job.id === id),
		)
	} else {
		const pageJobIds = paginatedJobs.value.map((job) => job.id)
		selectedJobs.value = [...new Set([...selectedJobs.value, ...pageJobIds])]
	}
}

const toggleJobSelection = (jobId) => {
	const index = selectedJobs.value.indexOf(jobId)
	if (index > -1) {
		selectedJobs.value.splice(index, 1)
	} else {
		selectedJobs.value.push(jobId)
	}
}

const bulkCancel = () => {
	console.log("Bulk cancel:", selectedJobs.value)
	selectedJobs.value = []
}

const bulkRetry = () => {
	console.log("Bulk retry:", selectedJobs.value)
	selectedJobs.value = []
}

const bulkDelete = () => {
	console.log("Bulk delete:", selectedJobs.value)
	selectedJobs.value = []
}

const getJobRowClass = (job) => {
	return {
		"row-running": job.status === "Running",
		"row-completed": job.status === "Completed",
		"row-failed": job.status === "Failed",
		"row-cancelled": job.status === "Cancelled",
	}
}

const getStatusClass = (status) => {
	return {
		"status-queued": status === "Queued",
		"status-running": status === "Running",
		"status-paused": status === "Paused",
		"status-completed": status === "Completed",
		"status-failed": status === "Failed",
		"status-cancelled": status === "Cancelled",
	}
}

const getStatusIcon = (status) => {
	const icons = {
		Queued: Clock,
		Running: Play,
		Paused: Pause,
		Completed: CheckCircle,
		Failed: XCircle,
		Cancelled: X,
	}
	return icons[status] || Clock
}

const getProgressClass = (status) => {
	return {
		"progress-running": status === "Running",
		"progress-completed": status === "Completed",
		"progress-failed": status === "Failed",
		"progress-paused": status === "Paused",
	}
}

const formatDuration = (duration) => {
	if (!duration) return "-"

	const hours = Math.floor(duration / 3600)
	const minutes = Math.floor((duration % 3600) / 60)
	const seconds = duration % 60

	if (hours > 0) {
		return `${hours}h ${minutes}m`
	} else if (minutes > 0) {
		return `${minutes}m ${seconds}s`
	} else {
		return `${seconds}s`
	}
}

const formatTime = (dateString) => {
	if (!dateString) return "-"
	return new Date(dateString).toLocaleTimeString()
}

const formatNumber = (num) => {
	if (!num) return "0"
	if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
	if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
	return num.toString()
}

const getJobActions = (job) => [
	{
		label: "View Details",
		value: "view",
		action: () => emit("view", job),
	},
	{
		label: "View Logs",
		value: "logs",
		action: () => console.log("View logs", job.id),
	},
	{
		label: "Download Report",
		value: "download",
		action: () => emit("download", job),
	},
	{
		label: "Duplicate",
		value: "duplicate",
		action: () => console.log("Duplicate", job.id),
	},
	...(job.status === "Completed" || job.status === "Failed"
		? [
				{
					label: "Delete",
					value: "delete",
					action: () => emit("delete", job),
					dangerous: true,
				},
			]
		: []),
]

const handleJobAction = (action) => {
	if (action.action) {
		action.action()
	}
}

// Watchers
watch([searchQuery, selectedStatus, selectedIntegration], () => {
	currentPage.value = 1
	selectedJobs.value = []
})
</script>

<style scoped>
.sync-jobs-manager {
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

.filters-section {
  margin-bottom: 1.5rem;
}

.filters {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.search-input {
  min-width: 300px;
}

.bulk-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--primary-light);
  border-radius: 0.5rem;
}

.selection-count {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--primary-color);
}

.bulk-buttons {
  display: flex;
  gap: 0.5rem;
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.summary-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-content {
  flex: 1;
}

.summary-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.summary-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-weight: 500;
}

.summary-icon {
  opacity: 0.1;
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

/* Jobs Table */
.jobs-table-container {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.jobs-table {
  width: 100%;
}

.table-header {
  display: grid;
  grid-template-columns: 40px 1fr 150px 120px 150px 100px 120px 80px;
  gap: 1rem;
  padding: 1rem;
  background: var(--background-color);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
}

.table-body {
  max-height: 600px;
  overflow-y: auto;
}

.table-row {
  display: grid;
  grid-template-columns: 40px 1fr 150px 120px 150px 100px 120px 80px;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.2s;
}

.table-row:hover {
  background: var(--background-color);
}

.table-row.row-running {
  background: #f0f9ff;
  border-left: 3px solid #3b82f6;
}

.table-row.row-completed {
  background: #f0fdf4;
  border-left: 3px solid #10b981;
}

.table-row.row-failed {
  background: #fef2f2;
  border-left: 3px solid #ef4444;
}

.table-row.row-cancelled {
  background: #f9fafb;
  border-left: 3px solid #6b7280;
}

.table-cell {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  min-height: 40px;
}

.select-cell {
  justify-content: center;
}

.job-info {
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
}

.job-name {
  font-weight: 600;
  color: var(--text-color);
}

.job-type {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.job-error {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #dc2626;
  font-weight: 500;
}

.integration-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.integration-name {
  font-weight: 500;
  color: var(--text-color);
}

.integration-type {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
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

.status-badge.status-queued {
  background: #f3f4f6;
  color: #374151;
}

.status-badge.status-running {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.status-paused {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.status-completed {
  background: #dcfce7;
  color: #166534;
}

.status-badge.status-failed {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.status-cancelled {
  background: #f3f4f6;
  color: #6b7280;
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 100%;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-fill.progress-running {
  background: #3b82f6;
}

.progress-fill.progress-completed {
  background: #10b981;
}

.progress-fill.progress-failed {
  background: #ef4444;
}

.progress-fill.progress-paused {
  background: #f59e0b;
}

.progress-text {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
}

.duration-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.duration-time {
  font-weight: 600;
  color: var(--text-color);
}

.duration-times {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.duration-times span {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.records-stats {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.records-count {
  font-weight: 600;
  color: var(--text-color);
}

.records-breakdown {
  display: flex;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.records-breakdown .success {
  color: #166534;
}

.records-breakdown .failed {
  color: #991b1b;
}

.actions-cell {
  justify-content: flex-end;
}

.job-actions {
  display: flex;
  gap: 0.25rem;
  align-items: center;
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
@media (max-width: 1200px) {
  .table-header,
  .table-row {
    grid-template-columns: 40px 1fr 120px 100px 120px 80px 100px 60px;
    gap: 0.5rem;
  }
  
  .summary-cards {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}

@media (max-width: 1024px) {
  .manager-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .filters {
    flex-wrap: wrap;
  }
  
  .search-input {
    min-width: auto;
  }
  
  .jobs-table-container {
    overflow-x: auto;
  }
  
  .jobs-table {
    min-width: 800px;
  }
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .bulk-actions {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .bulk-buttons {
    justify-content: center;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
  
  .summary-card {
    padding: 1rem;
  }
  
  .summary-value {
    font-size: 1.5rem;
  }
}
</style>