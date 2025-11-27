<template>
  <div class="workflow-list">
    <!-- Filters and Actions Bar -->
    <div class="list-header">
      <div class="filters">
        <FormControl
          type="text"
          v-model="searchQuery"
          placeholder="Search workflows..."
        >
          <template #prefix>
            <Search class="w-4 h-4" />
          </template>
        </FormControl>
        
        <Dropdown :options="categoryOptions" @click="handleCategoryFilter">
          <template #default>
            <Button variant="outline">
              <Filter class="w-4 h-4 mr-2" />
              {{ selectedCategory || 'All Categories' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
        
        <Dropdown :options="statusOptions" @click="handleStatusFilter">
          <template #default>
            <Button variant="outline">
              <div 
                class="status-indicator"
                :class="{ 'active': selectedStatus === 'active', 'inactive': selectedStatus === 'inactive' }"
              ></div>
              {{ selectedStatus ? (selectedStatus === 'active' ? 'Active Only' : 'Inactive Only') : 'All Status' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
      </div>
      
      <div class="actions">
        <div v-if="selected.length > 0" class="bulk-actions">
          <span class="selection-count">{{ selected.length }} selected</span>
          
          <Dropdown :options="bulkActionOptions" @click="handleBulkAction">
            <template #default>
              <Button variant="outline" size="sm">
                Actions
                <ChevronDown class="w-4 h-4 ml-2" />
              </Button>
            </template>
          </Dropdown>
          
          <Button variant="outline" size="sm" @click="clearSelection">
            Clear
          </Button>
        </div>
        
        <div class="view-controls">
          <Button
            variant="ghost"
            size="sm"
            :class="{ 'active': viewMode === 'grid' }"
            @click="viewMode = 'grid'"
          >
            <Grid3X3 class="w-4 h-4" />
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            :class="{ 'active': viewMode === 'list' }"
            @click="viewMode = 'list'"
          >
            <List class="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-grid" v-if="viewMode === 'grid'">
        <div v-for="i in 6" :key="i" class="workflow-card skeleton">
          <div class="skeleton-header"></div>
          <div class="skeleton-content"></div>
          <div class="skeleton-footer"></div>
        </div>
      </div>
      
      <div v-else class="loading-table">
        <div v-for="i in 8" :key="i" class="table-row skeleton">
          <div class="skeleton-cell"></div>
          <div class="skeleton-cell"></div>
          <div class="skeleton-cell"></div>
          <div class="skeleton-cell"></div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredWorkflows.length === 0" class="empty-state">
      <Workflow class="w-16 h-16 text-gray-300" />
      <h3>{{ searchQuery ? 'No workflows found' : 'No workflows created yet' }}</h3>
      <p>
        {{ searchQuery 
          ? 'Try adjusting your search terms or filters.' 
          : 'Create your first automated workflow to get started.' 
        }}
      </p>
      <Button v-if="!searchQuery" variant="solid" @click="$emit('create-workflow')">
        Create Workflow
      </Button>
    </div>

    <!-- Grid View -->
    <div v-else-if="viewMode === 'grid'" class="grid-view">
      <div
        v-for="workflow in paginatedWorkflows"
        :key="workflow.id"
        class="workflow-card"
        :class="{ 'selected': isSelected(workflow.id) }"
        @click="handleCardClick(workflow)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="header-left">
            <input
              type="checkbox"
              :checked="isSelected(workflow.id)"
              @click.stop="toggleSelection(workflow.id)"
              @change="handleSelectionChange"
            />
            
            <div class="workflow-status">
              <div 
                class="status-dot" 
                :class="{ 'active': workflow.is_active, 'inactive': !workflow.is_active }"
              ></div>
              <span class="status-text">
                {{ workflow.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
          
          <div class="header-actions">
            <Dropdown :options="getCardActions(workflow)" @click="handleCardAction">
              <template #default>
                <Button variant="ghost" size="sm">
                  <MoreVertical class="w-4 h-4" />
                </Button>
              </template>
            </Dropdown>
          </div>
        </div>

        <!-- Card Content -->
        <div class="card-content">
          <h4 class="workflow-title">{{ workflow.name }}</h4>
          <p class="workflow-description">{{ workflow.description }}</p>
          
          <div class="workflow-meta">
            <div class="meta-item">
              <Tag class="w-3 h-3" />
              <span>{{ getCategoryLabel(workflow.category) }}</span>
            </div>
            
            <div class="meta-item">
              <Clock class="w-3 h-3" />
              <span>{{ formatRelativeTime(workflow.last_run) }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="execution-stats">
            <div class="stat">
              <span class="stat-value">{{ workflow.execution_count || 0 }}</span>
              <span class="stat-label">Runs</span>
            </div>
            
            <div class="stat">
              <span class="stat-value">{{ getSuccessRate(workflow) }}%</span>
              <span class="stat-label">Success</span>
            </div>
            
            <div class="stat">
              <span 
                class="stat-badge"
                :class="getStatusClass(workflow.last_status)"
              >
                {{ workflow.last_status || 'Never run' }}
              </span>
            </div>
          </div>
          
          <div class="card-actions">
            <Button
              variant="ghost"
              size="sm"
              :disabled="!workflow.is_active"
              @click.stop="$emit('execute', workflow)"
            >
              <Play class="w-3 h-3" />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              @click.stop="$emit('edit', workflow)"
            >
              <Edit class="w-3 h-3" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="list-view">
      <div class="table-container">
        <table class="workflows-table">
          <thead>
            <tr>
              <th class="checkbox-column">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  :indeterminate="isPartiallySelected"
                  @change="toggleSelectAll"
                />
              </th>
              <th @click="sortBy('name')" class="sortable">
                Name
                <ChevronUp v-if="sortField === 'name' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'name' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('category')" class="sortable">
                Category
                <ChevronUp v-if="sortField === 'category' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'category' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th>Status</th>
              <th @click="sortBy('last_run')" class="sortable">
                Last Run
                <ChevronUp v-if="sortField === 'last_run' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'last_run' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('execution_count')" class="sortable">
                Executions
                <ChevronUp v-if="sortField === 'execution_count' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'execution_count' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th>Success Rate</th>
              <th>Actions</th>
            </tr>
          </thead>
          
          <tbody>
            <tr
              v-for="workflow in paginatedWorkflows"
              :key="workflow.id"
              class="workflow-row"
              :class="{ 'selected': isSelected(workflow.id) }"
              @click="handleRowClick(workflow)"
            >
              <td class="checkbox-column" @click.stop>
                <input
                  type="checkbox"
                  :checked="isSelected(workflow.id)"
                  @change="toggleSelection(workflow.id)"
                />
              </td>
              
              <td class="name-column">
                <div class="workflow-info">
                  <h5>{{ workflow.name }}</h5>
                  <p>{{ workflow.description }}</p>
                </div>
              </td>
              
              <td>
                <div class="category-badge">
                  <Tag class="w-3 h-3" />
                  {{ getCategoryLabel(workflow.category) }}
                </div>
              </td>
              
              <td>
                <div class="status-badge" :class="{ 'active': workflow.is_active }">
                  <div class="status-dot"></div>
                  {{ workflow.is_active ? 'Active' : 'Inactive' }}
                </div>
              </td>
              
              <td>
                <div class="last-run">
                  {{ formatDateTime(workflow.last_run) }}
                </div>
              </td>
              
              <td>
                <div class="execution-count">
                  {{ workflow.execution_count || 0 }}
                </div>
              </td>
              
              <td>
                <div class="success-rate">
                  {{ getSuccessRate(workflow) }}%
                </div>
              </td>
              
              <td class="actions-column" @click.stop>
                <div class="row-actions">
                  <Button
                    variant="ghost"
                    size="sm"
                    :disabled="!workflow.is_active"
                    @click="$emit('execute', workflow)"
                    title="Execute workflow"
                  >
                    <Play class="w-3 h-3" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="$emit('edit', workflow)"
                    title="Edit workflow"
                  >
                    <Edit class="w-3 h-3" />
                  </Button>
                  
                  <Dropdown :options="getRowActions(workflow)" @click="handleRowAction">
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
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <div class="pagination-info">
        Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to 
        {{ Math.min(currentPage * itemsPerPage, filteredWorkflows.length) }} of 
        {{ filteredWorkflows.length }} workflows
      </div>
      
      <div class="pagination-controls">
        <Button
          variant="outline"
          size="sm"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <ChevronLeft class="w-3 h-3" />
          Previous
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
          Next
          <ChevronRight class="w-3 h-3" />
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Dropdown, FormControl } from "frappe-ui"
import {
	ChevronDown,
	ChevronLeft,
	ChevronRight,
	ChevronUp,
	Clock,
	Copy,
	Edit,
	Filter,
	Grid3X3,
	List,
	MoreHorizontal,
	MoreVertical,
	Play,
	Power,
	PowerOff,
	Search,
	Tag,
	Trash2,
	Workflow,
} from "lucide-vue-next"
import { computed, ref, watch } from "vue"

const props = defineProps({
	workflows: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
	selected: {
		type: Array,
		default: () => [],
	},
})

const emit = defineEmits([
	"select",
	"execute",
	"edit",
	"duplicate",
	"toggle-status",
	"delete",
	"bulk-action",
	"create-workflow",
])

// Local state
const searchQuery = ref("")
const selectedCategory = ref("")
const selectedStatus = ref("")
const viewMode = ref("grid")
const sortField = ref("name")
const sortDirection = ref("asc")
const currentPage = ref(1)
const itemsPerPage = ref(12)

// Filter options
const categoryOptions = [
	{ label: "All Categories", value: "" },
	{ label: "Compliance", value: "compliance" },
	{ label: "Risk Management", value: "risk_management" },
	{ label: "Reporting", value: "reporting" },
	{ label: "Data Processing", value: "data_processing" },
	{ label: "Notifications", value: "notifications" },
]

const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Active Only", value: "active" },
	{ label: "Inactive Only", value: "inactive" },
]

const bulkActionOptions = [
	{
		label: "Activate",
		value: "activate",
		icon: Power,
	},
	{
		label: "Deactivate",
		value: "deactivate",
		icon: PowerOff,
	},
	{
		label: "Delete",
		value: "delete",
		icon: Trash2,
	},
]

// Computed
const filteredWorkflows = computed(() => {
	let filtered = props.workflows

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		filtered = filtered.filter(
			(workflow) =>
				workflow.name.toLowerCase().includes(query) ||
				workflow.description?.toLowerCase().includes(query),
		)
	}

	// Category filter
	if (selectedCategory.value) {
		filtered = filtered.filter(
			(workflow) => workflow.category === selectedCategory.value,
		)
	}

	// Status filter
	if (selectedStatus.value) {
		filtered = filtered.filter((workflow) =>
			selectedStatus.value === "active"
				? workflow.is_active
				: !workflow.is_active,
		)
	}

	// Sort
	filtered.sort((a, b) => {
		let aVal = a[sortField.value]
		let bVal = b[sortField.value]

		if (sortField.value === "last_run") {
			aVal = aVal ? new Date(aVal) : new Date(0)
			bVal = bVal ? new Date(bVal) : new Date(0)
		}

		if (typeof aVal === "string") {
			aVal = aVal.toLowerCase()
			bVal = bVal?.toLowerCase() || ""
		}

		const result = aVal > bVal ? 1 : aVal < bVal ? -1 : 0
		return sortDirection.value === "desc" ? -result : result
	})

	return filtered
})

const totalPages = computed(() =>
	Math.ceil(filteredWorkflows.value.length / itemsPerPage.value),
)

const paginatedWorkflows = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	return filteredWorkflows.value.slice(start, start + itemsPerPage.value)
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

const isAllSelected = computed(() => {
	return (
		paginatedWorkflows.value.length > 0 &&
		paginatedWorkflows.value.every((w) => props.selected.includes(w.id))
	)
})

const isPartiallySelected = computed(() => {
	return props.selected.length > 0 && !isAllSelected.value
})

// Methods
const isSelected = (workflowId) => {
	return props.selected.includes(workflowId)
}

const toggleSelection = (workflowId) => {
	const selected = [...props.selected]
	const index = selected.indexOf(workflowId)

	if (index > -1) {
		selected.splice(index, 1)
	} else {
		selected.push(workflowId)
	}

	emit("bulk-action", "select", selected)
}

const toggleSelectAll = () => {
	if (isAllSelected.value) {
		emit("bulk-action", "select", [])
	} else {
		const allIds = paginatedWorkflows.value.map((w) => w.id)
		emit("bulk-action", "select", [...new Set([...props.selected, ...allIds])])
	}
}

const clearSelection = () => {
	emit("bulk-action", "select", [])
}

const handleSelectionChange = () => {
	// Handled by individual toggleSelection calls
}

const handleCategoryFilter = (option) => {
	selectedCategory.value = option.value
	currentPage.value = 1
}

const handleStatusFilter = (option) => {
	selectedStatus.value = option.value
	currentPage.value = 1
}

const handleBulkAction = (option) => {
	emit("bulk-action", option.value, props.selected)
}

const sortBy = (field) => {
	if (sortField.value === field) {
		sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc"
	} else {
		sortField.value = field
		sortDirection.value = "asc"
	}
}

const handleCardClick = (workflow) => {
	emit("select", workflow)
}

const handleRowClick = (workflow) => {
	emit("select", workflow)
}

const handleCardAction = (action) => {
	// Actions handled by individual buttons or dropdowns
}

const handleRowAction = (action) => {
	// Actions handled by individual buttons or dropdowns
}

const getCardActions = (workflow) => [
	{
		label: "Execute",
		value: "execute",
		icon: Play,
		disabled: !workflow.is_active,
		action: () => emit("execute", workflow),
	},
	{
		label: "Edit",
		value: "edit",
		icon: Edit,
		action: () => emit("edit", workflow),
	},
	{
		label: "Duplicate",
		value: "duplicate",
		icon: Copy,
		action: () => emit("duplicate", workflow),
	},
	{
		label: workflow.is_active ? "Deactivate" : "Activate",
		value: "toggle-status",
		icon: workflow.is_active ? PowerOff : Power,
		action: () => emit("toggle-status", workflow),
	},
	{
		label: "Delete",
		value: "delete",
		icon: Trash2,
		action: () => emit("delete", workflow),
	},
]

const getRowActions = (workflow) => [
	{
		label: "Duplicate",
		value: "duplicate",
		icon: Copy,
		action: () => emit("duplicate", workflow),
	},
	{
		label: workflow.is_active ? "Deactivate" : "Activate",
		value: "toggle-status",
		icon: workflow.is_active ? PowerOff : Power,
		action: () => emit("toggle-status", workflow),
	},
	{
		label: "Delete",
		value: "delete",
		icon: Trash2,
		action: () => emit("delete", workflow),
	},
]

const getCategoryLabel = (category) => {
	const option = categoryOptions.find((opt) => opt.value === category)
	return option ? option.label : category
}

const getSuccessRate = (workflow) => {
	if (!workflow.execution_count) return 0
	return Math.round(
		((workflow.success_count || 0) / workflow.execution_count) * 100,
	)
}

const getStatusClass = (status) => {
	return {
		success: status === "Success",
		error: status === "Failed",
		warning: status === "Cancelled",
		info: !status,
	}
}

const formatDateTime = (dateString) => {
	if (!dateString) return "Never"
	return new Date(dateString).toLocaleString()
}

const formatRelativeTime = (dateString) => {
	if (!dateString) return "Never run"

	const now = new Date()
	const date = new Date(dateString)
	const diffMs = now - date

	const minutes = Math.floor(diffMs / (1000 * 60))
	const hours = Math.floor(diffMs / (1000 * 60 * 60))
	const days = Math.floor(diffMs / (1000 * 60 * 60 * 24))

	if (minutes < 60) return `${minutes}m ago`
	if (hours < 24) return `${hours}h ago`
	return `${days}d ago`
}

// Watchers
watch([searchQuery, selectedCategory, selectedStatus], () => {
	currentPage.value = 1
})
</script>

<style scoped>
.workflow-list {
  padding: 1.5rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.filters .form-control {
  min-width: 250px;
}

.actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.bulk-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.selection-count {
  font-size: 0.875rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.view-controls {
  display: flex;
  gap: 0.25rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  padding: 0.25rem;
}

.view-controls .button.active {
  background: var(--primary-color);
  color: white;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.status-indicator.active {
  background: #22c55e;
}

.status-indicator.inactive {
  background: #6b7280;
}

/* Loading States */
.loading-state {
  padding: 2rem;
}

.loading-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.workflow-card.skeleton {
  background: var(--background-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
}

.skeleton-header,
.skeleton-content,
.skeleton-footer {
  background: var(--border-color);
  border-radius: 0.25rem;
  animation: pulse 2s infinite;
}

.skeleton-header {
  height: 20px;
  margin-bottom: 1rem;
}

.skeleton-content {
  height: 60px;
  margin-bottom: 1rem;
}

.skeleton-footer {
  height: 30px;
}

.loading-table {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.table-row.skeleton {
  display: flex;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border-radius: 0.375rem;
  background: var(--background-color);
}

.skeleton-cell {
  background: var(--border-color);
  border-radius: 0.25rem;
  height: 16px;
  animation: pulse 2s infinite;
}

.skeleton-cell:nth-child(1) { flex: 2; }
.skeleton-cell:nth-child(2) { flex: 1; }
.skeleton-cell:nth-child(3) { flex: 1; }
.skeleton-cell:nth-child(4) { flex: 0.5; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 1rem 0 0.5rem 0;
}

.empty-state p {
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

/* Grid View */
.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  padding: 0.5rem;
}

.workflow-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.workflow-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.workflow-card.selected {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 1px var(--primary-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.header-left {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.workflow-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.active {
  background: #22c55e;
}

.status-dot.inactive {
  background: #6b7280;
}

.status-text {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.card-content {
  margin-bottom: 1.5rem;
}

.workflow-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.workflow-description {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin: 0 0 1rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.workflow-meta {
  display: flex;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
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

.execution-stats {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.stat {
  text-align: center;
}

.stat-value {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.875rem;
  display: block;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.stat-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 500;
}

.stat-badge.success {
  background: #dcfce7;
  color: #166534;
}

.stat-badge.error {
  background: #fee2e2;
  color: #991b1b;
}

.stat-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.stat-badge.info {
  background: var(--background-color);
  color: var(--text-muted);
}

.card-actions {
  display: flex;
  gap: 0.25rem;
}

/* List View */
.list-view {
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
}

.workflows-table {
  width: 100%;
  border-collapse: collapse;
}

.workflows-table th,
.workflows-table td {
  text-align: left;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
}

.workflows-table th {
  background: var(--background-color);
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.875rem;
}

.workflows-table th.sortable {
  cursor: pointer;
  user-select: none;
  position: relative;
}

.workflows-table th.sortable:hover {
  background: var(--border-color);
}

.workflows-table th svg {
  display: inline-block;
  margin-left: 0.5rem;
}

.checkbox-column {
  width: 40px;
}

.name-column {
  min-width: 200px;
}

.actions-column {
  width: 120px;
}

.workflow-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.workflow-row:hover {
  background: var(--background-color);
}

.workflow-row.selected {
  background: var(--primary-light);
}

.workflow-info h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
}

.workflow-info p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.category-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.status-badge.active {
  color: #166534;
}

.status-badge .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #6b7280;
}

.status-badge.active .status-dot {
  background: #22c55e;
}

.last-run,
.execution-count,
.success-rate {
  font-size: 0.875rem;
  color: var(--text-color);
}

.row-actions {
  display: flex;
  gap: 0.25rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
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
  .grid-view {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .workflow-list {
    padding: 1rem;
  }
  
  .list-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .filters {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .filters .form-control {
    min-width: auto;
  }
  
  .actions {
    justify-content: space-between;
  }
  
  .bulk-actions {
    flex-wrap: wrap;
  }
  
  .grid-view {
    grid-template-columns: 1fr;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
  
  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .workflow-card {
    padding: 1rem;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .execution-stats {
    gap: 0.75rem;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
</style>