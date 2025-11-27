<template>
  <div class="compliance-requirements">
    <!-- Header -->
    <div class="requirements-header">
      <div class="header-left">
        <h3>Compliance Requirements</h3>
        <p>Manage and track regulatory compliance requirements</p>
      </div>
      
      <div class="header-actions">
        <Button variant="solid" @click="showCreateModal = true">
          <Plus class="w-4 h-4 mr-2" />
          Add Requirement
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filters">
        <FormControl
          type="text"
          v-model="searchQuery"
          placeholder="Search requirements..."
          class="search-input"
        >
          <template #prefix>
            <Search class="w-4 h-4" />
          </template>
        </FormControl>
        
        <Dropdown :options="frameworkFilterOptions" @click="handleFrameworkFilter">
          <template #default>
            <Button variant="outline">
              <Filter class="w-4 h-4 mr-2" />
              {{ selectedFramework ? selectedFramework.name : 'All Frameworks' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
        
        <Dropdown :options="statusFilterOptions" @click="handleStatusFilter">
          <template #default>
            <Button variant="outline">
              <component :is="getStatusIcon(selectedStatus)" class="w-4 h-4 mr-2" />
              {{ selectedStatus || 'All Status' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
        
        <Dropdown :options="riskFilterOptions" @click="handleRiskFilter">
          <template #default>
            <Button variant="outline">
              <AlertTriangle class="w-4 h-4 mr-2" />
              {{ selectedRisk || 'All Risk Levels' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
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

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <Loader class="w-6 h-6 animate-spin" />
      <p>Loading requirements...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredRequirements.length === 0" class="empty-state">
      <FileCheck class="w-16 h-16 text-gray-300" />
      <h4>{{ searchQuery ? 'No requirements found' : 'No requirements yet' }}</h4>
      <p>
        {{ searchQuery 
          ? 'Try adjusting your search terms or filters.' 
          : 'Add your first compliance requirement to get started.' 
        }}
      </p>
      <Button v-if="!searchQuery" variant="solid" @click="showCreateModal = true">
        Add Requirement
      </Button>
    </div>

    <!-- Grid View -->
    <div v-else-if="viewMode === 'grid'" class="grid-view">
      <div
        v-for="requirement in paginatedRequirements"
        :key="requirement.id"
        class="requirement-card"
        :class="getRequirementCardClass(requirement)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="framework-badge" :style="{ backgroundColor: getFrameworkColor(requirement.framework_id) + '20', color: getFrameworkColor(requirement.framework_id) }">
            {{ getFrameworkName(requirement.framework_id) }}
          </div>
          
          <div class="card-actions">
            <Dropdown :options="getRequirementActions(requirement)" @click="handleAction">
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
          <div class="requirement-header">
            <h4 class="requirement-title">{{ requirement.title }}</h4>
            <span class="requirement-section">{{ requirement.section }}</span>
          </div>
          
          <p class="requirement-description">{{ requirement.description }}</p>
          
          <div class="requirement-meta">
            <div class="meta-item">
              <User class="w-3 h-3" />
              <span>{{ requirement.assigned_to }}</span>
            </div>
            
            <div class="meta-item">
              <Calendar class="w-3 h-3" />
              <span>Due {{ formatDate(requirement.next_review_date) }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="compliance-status">
            <div 
              class="status-indicator"
              :class="getStatusClass(requirement.compliance_status)"
            >
              <component :is="getStatusIcon(requirement.compliance_status)" class="w-3 h-3" />
              <span>{{ requirement.compliance_status }}</span>
            </div>
            
            <div class="compliance-score" v-if="requirement.compliance_score">
              {{ requirement.compliance_score }}%
            </div>
          </div>
          
          <div class="risk-level">
            <div 
              class="risk-badge"
              :class="getRiskClass(requirement.risk_level)"
            >
              {{ requirement.risk_level }}
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="card-quick-actions">
          <Button variant="ghost" size="sm" @click="$emit('assess', requirement)">
            <CheckSquare class="w-3 h-3 mr-1" />
            Assess
          </Button>
          
          <Button variant="ghost" size="sm" @click="$emit('edit', requirement)">
            <Edit class="w-3 h-3 mr-1" />
            Edit
          </Button>
          
          <Button 
            v-if="requirement.compliance_status === 'Non-Compliant'"
            variant="ghost" 
            size="sm" 
            @click="$emit('remediate', requirement)"
          >
            <Settings class="w-3 h-3 mr-1" />
            Remediate
          </Button>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="list-view">
      <div class="table-container">
        <table class="requirements-table">
          <thead>
            <tr>
              <th @click="sortBy('title')" class="sortable">
                Requirement
                <ChevronUp v-if="sortField === 'title' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'title' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('framework_id')" class="sortable">
                Framework
                <ChevronUp v-if="sortField === 'framework_id' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'framework_id' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('compliance_status')" class="sortable">
                Status
                <ChevronUp v-if="sortField === 'compliance_status' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'compliance_status' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('risk_level')" class="sortable">
                Risk Level
                <ChevronUp v-if="sortField === 'risk_level' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'risk_level' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('assigned_to')" class="sortable">
                Assigned To
                <ChevronUp v-if="sortField === 'assigned_to' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'assigned_to' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('next_review_date')" class="sortable">
                Next Review
                <ChevronUp v-if="sortField === 'next_review_date' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'next_review_date' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          
          <tbody>
            <tr
              v-for="requirement in paginatedRequirements"
              :key="requirement.id"
              class="requirement-row"
              :class="getRequirementRowClass(requirement)"
            >
              <td class="requirement-column">
                <div class="requirement-info">
                  <h5>{{ requirement.title }}</h5>
                  <p>{{ requirement.section }} • {{ truncateText(requirement.description, 60) }}</p>
                  <div v-if="requirement.compliance_score" class="score-badge">
                    {{ requirement.compliance_score }}%
                  </div>
                </div>
              </td>
              
              <td class="framework-column">
                <div class="framework-info">
                  <span 
                    class="framework-name"
                    :style="{ color: getFrameworkColor(requirement.framework_id) }"
                  >
                    {{ getFrameworkName(requirement.framework_id) }}
                  </span>
                </div>
              </td>
              
              <td class="status-column">
                <div 
                  class="status-badge"
                  :class="getStatusClass(requirement.compliance_status)"
                >
                  <component :is="getStatusIcon(requirement.compliance_status)" class="w-3 h-3" />
                  <span>{{ requirement.compliance_status }}</span>
                </div>
              </td>
              
              <td class="risk-column">
                <div 
                  class="risk-badge"
                  :class="getRiskClass(requirement.risk_level)"
                >
                  {{ requirement.risk_level }}
                </div>
              </td>
              
              <td class="assignee-column">
                <div class="assignee-info">
                  <User class="w-3 h-3" />
                  <span>{{ requirement.assigned_to }}</span>
                </div>
              </td>
              
              <td class="review-column">
                <div 
                  class="review-date"
                  :class="getDateUrgencyClass(requirement.next_review_date)"
                >
                  {{ formatDate(requirement.next_review_date) }}
                  <div class="date-relative">{{ getRelativeDate(requirement.next_review_date) }}</div>
                </div>
              </td>
              
              <td class="actions-column">
                <div class="row-actions">
                  <Button variant="ghost" size="sm" @click="$emit('assess', requirement)">
                    <CheckSquare class="w-3 h-3" />
                  </Button>
                  
                  <Button variant="ghost" size="sm" @click="$emit('edit', requirement)">
                    <Edit class="w-3 h-3" />
                  </Button>
                  
                  <Dropdown :options="getRequirementActions(requirement)" @click="handleAction">
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
        {{ Math.min(currentPage * itemsPerPage, filteredRequirements.length) }} of 
        {{ filteredRequirements.length }} requirements
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

    <!-- Create Requirement Modal -->
    <Dialog
      v-if="showCreateModal"
      :options="{ title: 'Add Compliance Requirement', size: 'xl' }"
      @close="showCreateModal = false"
    >
      <CreateRequirementForm
        :frameworks="frameworks"
        @create="handleCreateRequirement"
        @cancel="showCreateModal = false"
      />
    </Dialog>
  </div>
</template>

<script setup>
import { Button, Dialog, Dropdown, FormControl } from "frappe-ui"
import {
	AlertCircle,
	AlertTriangle,
	Calendar,
	CheckCircle,
	CheckSquare,
	ChevronDown,
	ChevronLeft,
	ChevronRight,
	ChevronUp,
	Edit,
	FileCheck,
	Filter,
	Grid3X3,
	List,
	Loader,
	MoreHorizontal,
	MoreVertical,
	Plus,
	Search,
	Settings,
	User,
	XCircle,
} from "lucide-vue-next"
import { computed, ref, watch } from "vue"

// Components
import CreateRequirementForm from "./CreateRequirementForm.vue"

const props = defineProps({
	requirements: {
		type: Array,
		default: () => [],
	},
	frameworks: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["create", "edit", "assess", "remediate"])

// Local state
const searchQuery = ref("")
const selectedFramework = ref(null)
const selectedStatus = ref("")
const selectedRisk = ref("")
const viewMode = ref("grid")
const sortField = ref("title")
const sortDirection = ref("asc")
const currentPage = ref(1)
const itemsPerPage = ref(12)
const showCreateModal = ref(false)

// Filter options
const frameworkFilterOptions = computed(() => {
	return [
		{ label: "All Frameworks", value: null },
		...props.frameworks.map((framework) => ({
			label: framework.name,
			value: framework,
		})),
	]
})

const statusFilterOptions = [
	{ label: "All Status", value: "" },
	{ label: "Compliant", value: "Compliant" },
	{ label: "Partially Compliant", value: "Partially Compliant" },
	{ label: "Non-Compliant", value: "Non-Compliant" },
	{ label: "Not Assessed", value: "Not Assessed" },
]

const riskFilterOptions = [
	{ label: "All Risk Levels", value: "" },
	{ label: "Critical", value: "Critical" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

// Computed
const filteredRequirements = computed(() => {
	let filtered = [...props.requirements]

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		filtered = filtered.filter(
			(req) =>
				req.title.toLowerCase().includes(query) ||
				req.description.toLowerCase().includes(query) ||
				req.section.toLowerCase().includes(query),
		)
	}

	// Framework filter
	if (selectedFramework.value) {
		filtered = filtered.filter(
			(req) => req.framework_id === selectedFramework.value.id,
		)
	}

	// Status filter
	if (selectedStatus.value) {
		filtered = filtered.filter(
			(req) => req.compliance_status === selectedStatus.value,
		)
	}

	// Risk filter
	if (selectedRisk.value) {
		filtered = filtered.filter((req) => req.risk_level === selectedRisk.value)
	}

	// Sort
	filtered.sort((a, b) => {
		let aVal = a[sortField.value]
		let bVal = b[sortField.value]

		if (sortField.value === "next_review_date") {
			aVal = new Date(aVal)
			bVal = new Date(bVal)
		} else if (sortField.value === "framework_id") {
			aVal = getFrameworkName(aVal)
			bVal = getFrameworkName(bVal)
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
	Math.ceil(filteredRequirements.value.length / itemsPerPage.value),
)

const paginatedRequirements = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	return filteredRequirements.value.slice(start, start + itemsPerPage.value)
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
const handleFrameworkFilter = (option) => {
	selectedFramework.value = option.value
	currentPage.value = 1
}

const handleStatusFilter = (option) => {
	selectedStatus.value = option.value
	currentPage.value = 1
}

const handleRiskFilter = (option) => {
	selectedRisk.value = option.value
	currentPage.value = 1
}

const sortBy = (field) => {
	if (sortField.value === field) {
		sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc"
	} else {
		sortField.value = field
		sortDirection.value = "asc"
	}
}

const getFrameworkName = (frameworkId) => {
	const framework = props.frameworks.find((f) => f.id === frameworkId)
	return framework ? framework.name : "Unknown"
}

const getFrameworkColor = (frameworkId) => {
	const framework = props.frameworks.find((f) => f.id === frameworkId)
	return framework ? framework.color : "#6b7280"
}

const getStatusIcon = (status) => {
	const icons = {
		Compliant: CheckCircle,
		"Partially Compliant": AlertCircle,
		"Non-Compliant": XCircle,
		"Not Assessed": AlertCircle,
	}
	return icons[status] || AlertCircle
}

const getStatusClass = (status) => {
	return {
		"status-compliant": status === "Compliant",
		"status-partial": status === "Partially Compliant",
		"status-non-compliant": status === "Non-Compliant",
		"status-not-assessed": status === "Not Assessed",
	}
}

const getRiskClass = (riskLevel) => {
	return {
		"risk-critical": riskLevel === "Critical",
		"risk-high": riskLevel === "High",
		"risk-medium": riskLevel === "Medium",
		"risk-low": riskLevel === "Low",
	}
}

const getRequirementCardClass = (requirement) => {
	return {
		"card-overdue": isOverdue(requirement.next_review_date),
		"card-non-compliant": requirement.compliance_status === "Non-Compliant",
	}
}

const getRequirementRowClass = (requirement) => {
	return {
		"row-overdue": isOverdue(requirement.next_review_date),
		"row-non-compliant": requirement.compliance_status === "Non-Compliant",
	}
}

const getDateUrgencyClass = (date) => {
	const days = getDaysUntil(date)
	return {
		"date-overdue": days < 0,
		"date-urgent": days >= 0 && days <= 7,
		"date-warning": days > 7 && days <= 14,
	}
}

const isOverdue = (date) => {
	return new Date(date) < new Date()
}

const getDaysUntil = (date) => {
	const today = new Date()
	const target = new Date(date)
	return Math.ceil((target - today) / (1000 * 60 * 60 * 24))
}

const formatDate = (dateString) => {
	return new Date(dateString).toLocaleDateString()
}

const getRelativeDate = (dateString) => {
	const days = getDaysUntil(dateString)
	if (days < 0) return `${Math.abs(days)} days overdue`
	if (days === 0) return "Today"
	if (days === 1) return "Tomorrow"
	return `${days} days`
}

const truncateText = (text, maxLength) => {
	return text.length > maxLength ? text.substring(0, maxLength) + "..." : text
}

const getRequirementActions = (requirement) => [
	{
		label: "View Details",
		value: "view",
		action: () => console.log("View", requirement.id),
	},
	{
		label: "Assess",
		value: "assess",
		action: () => emit("assess", requirement),
	},
	{
		label: "Edit",
		value: "edit",
		action: () => emit("edit", requirement),
	},
	{
		label: "Duplicate",
		value: "duplicate",
		action: () => console.log("Duplicate", requirement.id),
	},
	{
		label: "Delete",
		value: "delete",
		action: () => console.log("Delete", requirement.id),
	},
]

const handleAction = (action) => {
	if (action.action) {
		action.action()
	}
}

const handleCreateRequirement = (requirementData) => {
	emit("create", requirementData)
	showCreateModal.value = false
}

// Watchers
watch([searchQuery, selectedFramework, selectedStatus, selectedRisk], () => {
	currentPage.value = 1
})
</script>

<style scoped>
.compliance-requirements {
  padding: 1.5rem;
}

.requirements-header {
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

.filters-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.search-input {
  min-width: 300px;
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

/* Loading and Empty States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-state {
  gap: 1rem;
}

.empty-state {
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

/* Grid View */
.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.requirement-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  transition: all 0.2s;
}

.requirement-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.requirement-card.card-overdue {
  border-left: 4px solid #ef4444;
}

.requirement-card.card-non-compliant {
  border-left: 4px solid #f59e0b;
  background: #fefbf2;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.framework-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.card-content {
  margin-bottom: 1.5rem;
}

.requirement-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.requirement-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
  flex: 1;
}

.requirement-section {
  font-size: 0.75rem;
  color: var(--text-muted);
  background: var(--background-color);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  margin-left: 0.75rem;
}

.requirement-description {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin: 0 0 1rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.requirement-meta {
  display: flex;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  margin-bottom: 1rem;
}

.compliance-status {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-indicator.status-compliant {
  background: #dcfce7;
  color: #166534;
}

.status-indicator.status-partial {
  background: #fef3c7;
  color: #92400e;
}

.status-indicator.status-non-compliant {
  background: #fee2e2;
  color: #991b1b;
}

.status-indicator.status-not-assessed {
  background: #f3f4f6;
  color: #374151;
}

.compliance-score {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
}

.risk-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.risk-badge.risk-critical {
  background: #7c2d12;
  color: white;
}

.risk-badge.risk-high {
  background: #fee2e2;
  color: #991b1b;
}

.risk-badge.risk-medium {
  background: #fef3c7;
  color: #92400e;
}

.risk-badge.risk-low {
  background: #dcfce7;
  color: #166534;
}

.card-quick-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* List View */
.list-view {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 2rem;
}

.table-container {
  overflow-x: auto;
}

.requirements-table {
  width: 100%;
  border-collapse: collapse;
}

.requirements-table th,
.requirements-table td {
  text-align: left;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.requirements-table th {
  background: var(--background-color);
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.875rem;
}

.requirements-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.requirements-table th.sortable:hover {
  background: var(--border-color);
}

.requirement-row {
  transition: background-color 0.2s;
}

.requirement-row:hover {
  background: var(--background-color);
}

.requirement-row.row-overdue {
  background: #fef2f2;
}

.requirement-row.row-non-compliant {
  background: #fefbf2;
}

.requirement-info h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
}

.requirement-info p {
  color: var(--text-muted);
  margin: 0 0 0.5rem 0;
  font-size: 0.75rem;
}

.score-badge {
  display: inline-block;
  background: var(--primary-light);
  color: var(--primary-color);
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.framework-name {
  font-weight: 600;
  font-size: 0.875rem;
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

.assignee-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color);
}

.review-date {
  font-size: 0.875rem;
  color: var(--text-color);
}

.date-relative {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.125rem;
}

.review-date.date-overdue {
  color: #991b1b;
}

.review-date.date-urgent {
  color: #f59e0b;
}

.review-date.date-warning {
  color: #eab308;
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
  .grid-view {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
  
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .compliance-requirements {
    padding: 1rem;
  }
  
  .requirements-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .search-input {
    min-width: auto;
  }
  
  .grid-view {
    grid-template-columns: 1fr;
  }
  
  .requirement-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .requirement-section {
    margin-left: 0;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .requirement-card {
    padding: 1rem;
  }
  
  .requirement-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .card-quick-actions {
    justify-content: stretch;
  }
  
  .card-quick-actions .button {
    flex: 1;
  }
}
</style>