<template>
  <div class="compliance-assessments">
    <!-- Header -->
    <div class="assessments-header">
      <div class="header-left">
        <h3>Compliance Assessments</h3>
        <p>Conduct and manage compliance assessments</p>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="showBulkAssessModal = true">
          <CheckSquare class="w-4 h-4 mr-2" />
          Bulk Assessment
        </Button>
        
        <Button variant="solid" @click="showCreateModal = true">
          <Plus class="w-4 h-4 mr-2" />
          New Assessment
        </Button>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="quick-stats">
      <div class="stat-card">
        <div class="stat-icon pending">
          <Clock class="w-5 h-5" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ pendingCount }}</div>
          <div class="stat-label">Pending</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon in-progress">
          <PlayCircle class="w-5 h-5" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ inProgressCount }}</div>
          <div class="stat-label">In Progress</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon completed">
          <CheckCircle class="w-5 h-5" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ completedCount }}</div>
          <div class="stat-label">Completed</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon overdue">
          <AlertTriangle class="w-5 h-5" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ overdueCount }}</div>
          <div class="stat-label">Overdue</div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filters-section">
      <div class="filters">
        <FormControl
          type="text"
          v-model="searchQuery"
          placeholder="Search assessments..."
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
        
        <Dropdown :options="assessorFilterOptions" @click="handleAssessorFilter">
          <template #default>
            <Button variant="outline">
              <User class="w-4 h-4 mr-2" />
              {{ selectedAssessor || 'All Assessors' }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
      </div>
      
      <div class="view-controls">
        <Button
          variant="ghost"
          size="sm"
          :class="{ 'active': viewMode === 'cards' }"
          @click="viewMode = 'cards'"
        >
          <Grid3X3 class="w-4 h-4" />
        </Button>
        
        <Button
          variant="ghost"
          size="sm"
          :class="{ 'active': viewMode === 'table' }"
          @click="viewMode = 'table'"
        >
          <List class="w-4 h-4" />
        </Button>
        
        <Button
          variant="ghost"
          size="sm"
          :class="{ 'active': viewMode === 'kanban' }"
          @click="viewMode = 'kanban'"
        >
          <Columns class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <Loader class="w-6 h-6 animate-spin" />
      <p>Loading assessments...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredAssessments.length === 0" class="empty-state">
      <CheckSquare class="w-16 h-16 text-gray-300" />
      <h4>{{ searchQuery ? 'No assessments found' : 'No assessments yet' }}</h4>
      <p>
        {{ searchQuery 
          ? 'Try adjusting your search terms or filters.' 
          : 'Create your first compliance assessment to get started.' 
        }}
      </p>
      <Button v-if="!searchQuery" variant="solid" @click="showCreateModal = true">
        New Assessment
      </Button>
    </div>

    <!-- Cards View -->
    <div v-else-if="viewMode === 'cards'" class="cards-view">
      <div
        v-for="assessment in paginatedAssessments"
        :key="assessment.id"
        class="assessment-card"
        :class="getAssessmentCardClass(assessment)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="assessment-info">
            <h4 class="assessment-title">{{ assessment.requirement_title }}</h4>
            <div class="assessment-meta">
              <span class="assessment-id">#{{ assessment.id }}</span>
              <span class="framework-badge" :style="{ backgroundColor: getFrameworkColor(assessment.framework_id) + '20', color: getFrameworkColor(assessment.framework_id) }">
                {{ getFrameworkName(assessment.framework_id) }}
              </span>
            </div>
          </div>
          
          <Dropdown :options="getAssessmentActions(assessment)" @click="handleAction">
            <template #default>
              <Button variant="ghost" size="sm">
                <MoreVertical class="w-4 h-4" />
              </Button>
            </template>
          </Dropdown>
        </div>

        <!-- Card Content -->
        <div class="card-content">
          <div class="assessment-details">
            <div class="detail-item">
              <Calendar class="w-4 h-4" />
              <div>
                <span class="detail-label">Assessment Date</span>
                <span class="detail-value">{{ formatDate(assessment.assessment_date) }}</span>
              </div>
            </div>
            
            <div class="detail-item">
              <User class="w-4 h-4" />
              <div>
                <span class="detail-label">Assessor</span>
                <span class="detail-value">{{ assessment.assessor }}</span>
              </div>
            </div>
            
            <div class="detail-item">
              <Clock class="w-4 h-4" />
              <div>
                <span class="detail-label">Due Date</span>
                <span class="detail-value" :class="getDateUrgencyClass(assessment.due_date)">
                  {{ formatDate(assessment.due_date) }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- Progress Bar -->
          <div v-if="assessment.status === 'In Progress'" class="progress-section">
            <div class="progress-header">
              <span>Progress</span>
              <span>{{ assessment.completion_percentage }}%</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill"
                :style="{ width: assessment.completion_percentage + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="status-section">
            <div 
              class="status-badge"
              :class="getStatusClass(assessment.status)"
            >
              <component :is="getStatusIcon(assessment.status)" class="w-3 h-3" />
              <span>{{ assessment.status }}</span>
            </div>
            
            <div v-if="assessment.compliance_result" class="compliance-result">
              <div 
                class="result-badge"
                :class="getComplianceResultClass(assessment.compliance_result)"
              >
                {{ assessment.compliance_result }}
              </div>
            </div>
          </div>
          
          <div class="card-actions">
            <Button
              variant="ghost"
              size="sm"
              @click="continueAssessment(assessment)"
              v-if="assessment.status === 'In Progress'"
            >
              <Edit class="w-3 h-3 mr-1" />
              Continue
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              @click="startAssessment(assessment)"
              v-else-if="assessment.status === 'Pending'"
            >
              <Play class="w-3 h-3 mr-1" />
              Start
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              @click="reviewAssessment(assessment)"
              v-else-if="assessment.status === 'Completed'"
            >
              <Eye class="w-3 h-3 mr-1" />
              Review
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Table View -->
    <div v-else-if="viewMode === 'table'" class="table-view">
      <div class="table-container">
        <table class="assessments-table">
          <thead>
            <tr>
              <th @click="sortBy('id')" class="sortable">
                ID
                <ChevronUp v-if="sortField === 'id' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'id' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('requirement_title')" class="sortable">
                Requirement
                <ChevronUp v-if="sortField === 'requirement_title' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'requirement_title' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('framework_id')" class="sortable">
                Framework
                <ChevronUp v-if="sortField === 'framework_id' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'framework_id' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('status')" class="sortable">
                Status
                <ChevronUp v-if="sortField === 'status' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'status' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('assessor')" class="sortable">
                Assessor
                <ChevronUp v-if="sortField === 'assessor' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'assessor' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th @click="sortBy('due_date')" class="sortable">
                Due Date
                <ChevronUp v-if="sortField === 'due_date' && sortDirection === 'asc'" class="w-3 h-3" />
                <ChevronDown v-else-if="sortField === 'due_date' && sortDirection === 'desc'" class="w-3 h-3" />
              </th>
              <th>Result</th>
              <th>Actions</th>
            </tr>
          </thead>
          
          <tbody>
            <tr
              v-for="assessment in paginatedAssessments"
              :key="assessment.id"
              class="assessment-row"
              :class="getAssessmentRowClass(assessment)"
            >
              <td class="id-column">
                <span class="assessment-id">#{{ assessment.id }}</span>
              </td>
              
              <td class="requirement-column">
                <div class="requirement-info">
                  <h5>{{ assessment.requirement_title }}</h5>
                  <p>{{ truncateText(assessment.requirement_section, 40) }}</p>
                </div>
              </td>
              
              <td class="framework-column">
                <span 
                  class="framework-name"
                  :style="{ color: getFrameworkColor(assessment.framework_id) }"
                >
                  {{ getFrameworkName(assessment.framework_id) }}
                </span>
              </td>
              
              <td class="status-column">
                <div 
                  class="status-badge"
                  :class="getStatusClass(assessment.status)"
                >
                  <component :is="getStatusIcon(assessment.status)" class="w-3 h-3" />
                  <span>{{ assessment.status }}</span>
                </div>
                
                <div v-if="assessment.status === 'In Progress'" class="progress-mini">
                  {{ assessment.completion_percentage }}%
                </div>
              </td>
              
              <td class="assessor-column">
                <div class="assessor-info">
                  <User class="w-3 h-3" />
                  <span>{{ assessment.assessor }}</span>
                </div>
              </td>
              
              <td class="due-date-column">
                <div 
                  class="due-date"
                  :class="getDateUrgencyClass(assessment.due_date)"
                >
                  {{ formatDate(assessment.due_date) }}
                  <div class="date-relative">{{ getRelativeDate(assessment.due_date) }}</div>
                </div>
              </td>
              
              <td class="result-column">
                <div 
                  v-if="assessment.compliance_result"
                  class="result-badge"
                  :class="getComplianceResultClass(assessment.compliance_result)"
                >
                  {{ assessment.compliance_result }}
                </div>
                <span v-else class="no-result">-</span>
              </td>
              
              <td class="actions-column">
                <div class="row-actions">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="continueAssessment(assessment)"
                    v-if="assessment.status === 'In Progress'"
                  >
                    <Edit class="w-3 h-3" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="startAssessment(assessment)"
                    v-else-if="assessment.status === 'Pending'"
                  >
                    <Play class="w-3 h-3" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="reviewAssessment(assessment)"
                    v-else-if="assessment.status === 'Completed'"
                  >
                    <Eye class="w-3 h-3" />
                  </Button>
                  
                  <Dropdown :options="getAssessmentActions(assessment)" @click="handleAction">
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

    <!-- Kanban View -->
    <div v-else-if="viewMode === 'kanban'" class="kanban-view">
      <div class="kanban-board">
        <div
          v-for="status in kanbanColumns"
          :key="status.id"
          class="kanban-column"
        >
          <div class="column-header">
            <div class="column-title">
              <component :is="status.icon" class="w-4 h-4" />
              <span>{{ status.title }}</span>
              <div class="column-count">{{ getAssessmentsByStatus(status.id).length }}</div>
            </div>
          </div>
          
          <div class="column-content">
            <div
              v-for="assessment in getAssessmentsByStatus(status.id)"
              :key="assessment.id"
              class="kanban-card"
              :class="getAssessmentCardClass(assessment)"
            >
              <div class="card-header-mini">
                <span class="assessment-id">#{{ assessment.id }}</span>
                <span class="framework-mini" :style="{ color: getFrameworkColor(assessment.framework_id) }">
                  {{ getFrameworkAbbr(assessment.framework_id) }}
                </span>
              </div>
              
              <h5 class="card-title">{{ assessment.requirement_title }}</h5>
              
              <div class="card-meta">
                <div class="meta-item">
                  <User class="w-3 h-3" />
                  <span>{{ assessment.assessor }}</span>
                </div>
                
                <div class="meta-item">
                  <Calendar class="w-3 h-3" />
                  <span>{{ formatShortDate(assessment.due_date) }}</span>
                </div>
              </div>
              
              <div v-if="assessment.status === 'In Progress'" class="progress-mini-bar">
                <div 
                  class="progress-fill"
                  :style="{ width: assessment.completion_percentage + '%' }"
                ></div>
              </div>
              
              <div v-if="assessment.compliance_result" class="result-mini">
                <div 
                  class="result-indicator"
                  :class="getComplianceResultClass(assessment.compliance_result)"
                >
                  {{ assessment.compliance_result }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1 && viewMode !== 'kanban'" class="pagination">
      <div class="pagination-info">
        Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to 
        {{ Math.min(currentPage * itemsPerPage, filteredAssessments.length) }} of 
        {{ filteredAssessments.length }} assessments
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

    <!-- Create Assessment Modal -->
    <Dialog
      v-if="showCreateModal"
      :options="{ title: 'New Assessment', size: 'xl' }"
      @close="showCreateModal = false"
    >
      <CreateAssessmentForm
        :frameworks="frameworks"
        :requirements="requirements"
        @create="handleCreateAssessment"
        @cancel="showCreateModal = false"
      />
    </Dialog>

    <!-- Bulk Assessment Modal -->
    <Dialog
      v-if="showBulkAssessModal"
      :options="{ title: 'Bulk Assessment', size: 'lg' }"
      @close="showBulkAssessModal = false"
    >
      <BulkAssessmentForm
        :assessments="selectedAssessments"
        @update="handleBulkUpdate"
        @cancel="showBulkAssessModal = false"
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
	Clock,
	Columns,
	Edit,
	Eye,
	Filter,
	Grid3X3,
	List,
	Loader,
	MoreHorizontal,
	MoreVertical,
	Play,
	PlayCircle,
	Plus,
	Search,
	User,
	XCircle,
} from "lucide-vue-next"
import { computed, ref, watch } from "vue"

import BulkAssessmentForm from "./BulkAssessmentForm.vue"
// Components
import CreateAssessmentForm from "./CreateAssessmentForm.vue"

const props = defineProps({
	assessments: {
		type: Array,
		default: () => [],
	},
	frameworks: {
		type: Array,
		default: () => [],
	},
	requirements: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["create", "update", "start", "continue", "review"])

// Local state
const searchQuery = ref("")
const selectedFramework = ref(null)
const selectedStatus = ref("")
const selectedAssessor = ref("")
const viewMode = ref("cards")
const sortField = ref("due_date")
const sortDirection = ref("asc")
const currentPage = ref(1)
const itemsPerPage = ref(12)
const showCreateModal = ref(false)
const showBulkAssessModal = ref(false)
const selectedAssessments = ref([])

// Kanban columns
const kanbanColumns = [
	{ id: "Pending", title: "Pending", icon: Clock },
	{ id: "In Progress", title: "In Progress", icon: PlayCircle },
	{ id: "Completed", title: "Completed", icon: CheckCircle },
	{ id: "Overdue", title: "Overdue", icon: AlertTriangle },
]

// Computed - Quick Stats
const pendingCount = computed(
	() => props.assessments.filter((a) => a.status === "Pending").length,
)
const inProgressCount = computed(
	() => props.assessments.filter((a) => a.status === "In Progress").length,
)
const completedCount = computed(
	() => props.assessments.filter((a) => a.status === "Completed").length,
)
const overdueCount = computed(
	() =>
		props.assessments.filter(
			(a) => isOverdue(a.due_date) && a.status !== "Completed",
		).length,
)

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
	{ label: "Pending", value: "Pending" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Completed", value: "Completed" },
	{ label: "Overdue", value: "Overdue" },
]

const assessorFilterOptions = computed(() => {
	const assessors = [
		...new Set(props.assessments.map((a) => a.assessor).filter(Boolean)),
	]
	return [
		{ label: "All Assessors", value: "" },
		...assessors.map((assessor) => ({
			label: assessor,
			value: assessor,
		})),
	]
})

// Computed - Filtered and Sorted Data
const filteredAssessments = computed(() => {
	let filtered = [...props.assessments]

	// Search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase()
		filtered = filtered.filter(
			(assessment) =>
				assessment.requirement_title?.toLowerCase().includes(query) ||
				assessment.requirement_section?.toLowerCase().includes(query) ||
				assessment.assessor?.toLowerCase().includes(query) ||
				assessment.id?.toString().includes(query),
		)
	}

	// Framework filter
	if (selectedFramework.value) {
		filtered = filtered.filter(
			(assessment) => assessment.framework_id === selectedFramework.value.id,
		)
	}

	// Status filter
	if (selectedStatus.value) {
		if (selectedStatus.value === "Overdue") {
			filtered = filtered.filter(
				(assessment) =>
					isOverdue(assessment.due_date) && assessment.status !== "Completed",
			)
		} else {
			filtered = filtered.filter(
				(assessment) => assessment.status === selectedStatus.value,
			)
		}
	}

	// Assessor filter
	if (selectedAssessor.value) {
		filtered = filtered.filter(
			(assessment) => assessment.assessor === selectedAssessor.value,
		)
	}

	// Sort
	filtered.sort((a, b) => {
		let aVal = a[sortField.value]
		let bVal = b[sortField.value]

		if (
			sortField.value === "due_date" ||
			sortField.value === "assessment_date"
		) {
			aVal = new Date(aVal || 0)
			bVal = new Date(bVal || 0)
		} else if (sortField.value === "framework_id") {
			aVal = getFrameworkName(aVal)
			bVal = getFrameworkName(bVal)
		} else if (typeof aVal === "string") {
			aVal = aVal.toLowerCase()
			bVal = bVal?.toLowerCase() || ""
		}

		const result = aVal > bVal ? 1 : aVal < bVal ? -1 : 0
		return sortDirection.value === "desc" ? -result : result
	})

	return filtered
})

const totalPages = computed(() =>
	Math.ceil(filteredAssessments.value.length / itemsPerPage.value),
)

const paginatedAssessments = computed(() => {
	if (viewMode.value === "kanban") return filteredAssessments.value
	const start = (currentPage.value - 1) * itemsPerPage.value
	return filteredAssessments.value.slice(start, start + itemsPerPage.value)
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

const handleAssessorFilter = (option) => {
	selectedAssessor.value = option.value
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

const getFrameworkAbbr = (frameworkId) => {
	const framework = props.frameworks.find((f) => f.id === frameworkId)
	return framework
		? framework.abbreviation || framework.name.substring(0, 3)
		: "UNK"
}

const getFrameworkColor = (frameworkId) => {
	const framework = props.frameworks.find((f) => f.id === frameworkId)
	return framework ? framework.color : "#6b7280"
}

const getStatusIcon = (status) => {
	const icons = {
		Pending: Clock,
		"In Progress": PlayCircle,
		Completed: CheckCircle,
		Overdue: AlertTriangle,
	}
	return icons[status] || AlertCircle
}

const getStatusClass = (status) => {
	return {
		"status-pending": status === "Pending",
		"status-in-progress": status === "In Progress",
		"status-completed": status === "Completed",
		"status-overdue": status === "Overdue",
	}
}

const getComplianceResultClass = (result) => {
	return {
		"result-compliant": result === "Compliant",
		"result-partial": result === "Partially Compliant",
		"result-non-compliant": result === "Non-Compliant",
		"result-not-applicable": result === "Not Applicable",
	}
}

const getAssessmentCardClass = (assessment) => {
	return {
		"card-overdue":
			isOverdue(assessment.due_date) && assessment.status !== "Completed",
		"card-high-priority": assessment.priority === "High",
		"card-completed": assessment.status === "Completed",
	}
}

const getAssessmentRowClass = (assessment) => {
	return {
		"row-overdue":
			isOverdue(assessment.due_date) && assessment.status !== "Completed",
		"row-high-priority": assessment.priority === "High",
		"row-completed": assessment.status === "Completed",
	}
}

const getDateUrgencyClass = (date) => {
	const days = getDaysUntil(date)
	return {
		"date-overdue": days < 0,
		"date-urgent": days >= 0 && days <= 3,
		"date-warning": days > 3 && days <= 7,
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

const formatShortDate = (dateString) => {
	return new Date(dateString).toLocaleDateString(undefined, {
		month: "short",
		day: "numeric",
	})
}

const getRelativeDate = (dateString) => {
	const days = getDaysUntil(dateString)
	if (days < 0) return `${Math.abs(days)}d overdue`
	if (days === 0) return "Today"
	if (days === 1) return "Tomorrow"
	return `${days}d`
}

const truncateText = (text, maxLength) => {
	return text?.length > maxLength
		? text.substring(0, maxLength) + "..."
		: text || ""
}

const getAssessmentsByStatus = (status) => {
	if (status === "Overdue") {
		return filteredAssessments.value.filter(
			(assessment) =>
				isOverdue(assessment.due_date) && assessment.status !== "Completed",
		)
	}
	return filteredAssessments.value.filter(
		(assessment) => assessment.status === status,
	)
}

const getAssessmentActions = (assessment) => [
	{
		label: "View Details",
		value: "view",
		action: () => console.log("View", assessment.id),
	},
	{
		label: "Edit",
		value: "edit",
		action: () => console.log("Edit", assessment.id),
	},
	{
		label: "Duplicate",
		value: "duplicate",
		action: () => console.log("Duplicate", assessment.id),
	},
	{
		label: "Reassign",
		value: "reassign",
		action: () => console.log("Reassign", assessment.id),
	},
	{
		label: "Delete",
		value: "delete",
		action: () => console.log("Delete", assessment.id),
	},
]

const handleAction = (action) => {
	if (action.action) {
		action.action()
	}
}

const startAssessment = (assessment) => {
	emit("start", assessment)
}

const continueAssessment = (assessment) => {
	emit("continue", assessment)
}

const reviewAssessment = (assessment) => {
	emit("review", assessment)
}

const handleCreateAssessment = (assessmentData) => {
	emit("create", assessmentData)
	showCreateModal.value = false
}

const handleBulkUpdate = (updates) => {
	emit("update", updates)
	showBulkAssessModal.value = false
}

// Watchers
watch(
	[searchQuery, selectedFramework, selectedStatus, selectedAssessor],
	() => {
		currentPage.value = 1
	},
)
</script>

<style scoped>
.compliance-assessments {
  padding: 1.5rem;
}

.assessments-header {
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

/* Quick Stats */
.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
}

.stat-icon {
  padding: 0.75rem;
  border-radius: 0.5rem;
  color: white;
}

.stat-icon.pending {
  background: #eab308;
}

.stat-icon.in-progress {
  background: #3b82f6;
}

.stat-icon.completed {
  background: #10b981;
}

.stat-icon.overdue {
  background: #ef4444;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

/* Filters and Search */
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

/* Cards View */
.cards-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.assessment-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  transition: all 0.2s;
}

.assessment-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.assessment-card.card-overdue {
  border-left: 4px solid #ef4444;
}

.assessment-card.card-high-priority {
  border-left: 4px solid #f59e0b;
}

.assessment-card.card-completed {
  background: #f0fdf4;
  border-color: #22c55e;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.assessment-info {
  flex: 1;
}

.assessment-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.assessment-meta {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.assessment-id {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: monospace;
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

.assessment-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.detail-item > div {
  display: flex;
  flex-direction: column;
  min-width: 0;
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
}

.progress-section {
  margin-top: 1rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.progress-bar {
  height: 0.5rem;
  background: var(--background-color);
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.status-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.status-in-progress {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-badge.status-completed {
  background: #dcfce7;
  color: #166534;
}

.status-badge.status-overdue {
  background: #fee2e2;
  color: #991b1b;
}

.result-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.result-badge.result-compliant {
  background: #dcfce7;
  color: #166534;
}

.result-badge.result-partial {
  background: #fef3c7;
  color: #92400e;
}

.result-badge.result-non-compliant {
  background: #fee2e2;
  color: #991b1b;
}

.result-badge.result-not-applicable {
  background: #f3f4f6;
  color: #374151;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

/* Table View */
.table-view {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 2rem;
}

.table-container {
  overflow-x: auto;
}

.assessments-table {
  width: 100%;
  border-collapse: collapse;
}

.assessments-table th,
.assessments-table td {
  text-align: left;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.assessments-table th {
  background: var(--background-color);
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.875rem;
}

.assessments-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.assessments-table th.sortable:hover {
  background: var(--border-color);
}

.assessment-row {
  transition: background-color 0.2s;
}

.assessment-row:hover {
  background: var(--background-color);
}

.assessment-row.row-overdue {
  background: #fef2f2;
}

.assessment-row.row-high-priority {
  background: #fefbf2;
}

.assessment-row.row-completed {
  background: #f0fdf4;
}

.requirement-info h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
}

.requirement-info p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.75rem;
}

.framework-name {
  font-weight: 600;
  font-size: 0.875rem;
}

.assessor-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color);
}

.due-date {
  font-size: 0.875rem;
  color: var(--text-color);
}

.date-relative {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.125rem;
}

.due-date.date-overdue {
  color: #991b1b;
}

.due-date.date-urgent {
  color: #f59e0b;
}

.due-date.date-warning {
  color: #eab308;
}

.progress-mini {
  font-size: 0.75rem;
  color: var(--primary-color);
  margin-top: 0.125rem;
}

.no-result {
  color: var(--text-muted);
  font-style: italic;
}

.row-actions {
  display: flex;
  gap: 0.25rem;
}

/* Kanban View */
.kanban-view {
  margin-bottom: 2rem;
}

.kanban-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.kanban-column {
  background: var(--background-color);
  border-radius: 0.5rem;
  overflow: hidden;
}

.column-header {
  padding: 1rem;
  background: white;
  border-bottom: 1px solid var(--border-color);
}

.column-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.column-count {
  background: var(--primary-light);
  color: var(--primary-color);
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  margin-left: auto;
}

.column-content {
  padding: 1rem;
  max-height: 70vh;
  overflow-y: auto;
}

.kanban-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.kanban-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.kanban-card:last-child {
  margin-bottom: 0;
}

.card-header-mini {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.framework-mini {
  font-size: 0.75rem;
  font-weight: 600;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.75rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.progress-mini-bar {
  height: 0.25rem;
  background: var(--background-color);
  border-radius: 0.125rem;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.result-mini {
  margin-top: 0.75rem;
}

.result-indicator {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
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
  .cards-view {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
  
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters {
    flex-wrap: wrap;
  }
  
  .quick-stats {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
}

@media (max-width: 768px) {
  .compliance-assessments {
    padding: 1rem;
  }
  
  .assessments-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .search-input {
    min-width: auto;
  }
  
  .cards-view {
    grid-template-columns: 1fr;
  }
  
  .kanban-board {
    grid-template-columns: 1fr;
  }
  
  .quick-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .assessment-card {
    padding: 1rem;
  }
  
  .assessment-details {
    gap: 0.5rem;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .card-actions {
    justify-content: stretch;
  }
  
  .card-actions .button {
    flex: 1;
  }
  
  .quick-stats {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 1rem;
  }
}
</style>