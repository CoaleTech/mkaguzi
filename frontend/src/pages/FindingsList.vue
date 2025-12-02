<template>
  <div class="space-y-6">
    <!-- Page Header with Enhanced Actions -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-red-100 rounded-lg">
            <AlertCircleIcon class="h-6 w-6 text-red-600" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Audit Findings</h1>
            <p class="text-gray-600 mt-1">
              Review and manage audit findings and observations
            </p>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <!-- Action Buttons -->
        <div class="p-1">
          <Button
            variant="solid"
            theme="gray"
            size="sm"
            @click="exportFindings"
            :loading="exporting"
          >
            <template #prefix>
              <DownloadIcon class="h-3.5 w-3.5" />
            </template>
            Export
          </Button>
        </div>

        <div class="p-1">
          <Button
            variant="solid"
            theme="gray"
            size="sm"
            @click="refreshData"
            :loading="loading"
          >
            <template #prefix>
              <RefreshCwIcon class="h-3.5 w-3.5" />
            </template>
            Refresh
          </Button>
        </div>

        <div class="p-1">
          <Button
            variant="solid"
            theme="red"
            size="sm"
            @click="createNewFinding"
          >
            <template #prefix>
              <PlusIcon class="h-3.5 w-3.5" />
            </template>
            New Finding
          </Button>
        </div>
      </div>
    </div>

    <!-- Stats Dashboard -->
    <FindingsStats :stats="findingsStats" />

    <!-- Quick Actions Bar -->
    <div class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <!-- Left Section: Search and Filters -->
        <div class="flex flex-col sm:flex-row gap-4 flex-1">
          <!-- Search Input -->
          <div class="relative flex-1 max-w-md">
            <SearchIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              v-model="filters.search"
              type="text"
              placeholder="Search findings..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />
          </div>

          <!-- Filters -->
          <div class="flex flex-wrap gap-2">
            <select
              v-model="filters.status"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-sm"
            >
              <option value="">All Status</option>
              <option value="Open">Open</option>
              <option value="Action in Progress">Action in Progress</option>
              <option value="Pending Verification">Pending Verification</option>
              <option value="Closed">Closed</option>
              <option value="Accepted as Risk">Accepted as Risk</option>
              <option value="Management Override">Management Override</option>
            </select>

            <select
              v-model="filters.riskRating"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-sm"
            >
              <option value="">All Risk Ratings</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>

            <select
              v-model="filters.category"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-sm"
            >
              <option value="">All Categories</option>
              <option value="Control Weakness">Control Weakness</option>
              <option value="Process Inefficiency">Process Inefficiency</option>
              <option value="Compliance Gap">Compliance Gap</option>
              <option value="Policy Violation">Policy Violation</option>
              <option value="Documentation Issue">Documentation Issue</option>
              <option value="Fraud Indicator">Fraud Indicator</option>
              <option value="IT/System Issue">IT/System Issue</option>
              <option value="Operational Risk">Operational Risk</option>
            </select>

            <select
              v-model="filters.engagement"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-sm"
            >
              <option value="">All Engagements</option>
              <option v-for="engagement in engagementOptions" :key="engagement.value" :value="engagement.value">
                {{ engagement.label }}
              </option>
            </select>

            <!-- Overdue Toggle -->
            <label class="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 cursor-pointer">
              <input
                type="checkbox"
                v-model="filters.overdueOnly"
                class="form-checkbox h-4 w-4 text-red-600 rounded"
              />
              <span class="ml-2 text-sm text-gray-700">Overdue Only</span>
            </label>
          </div>
        </div>

        <!-- Right Section: View Toggle and Actions -->
        <div class="flex items-center gap-3">
          <!-- View Mode Toggle -->
          <div class="flex items-center bg-gray-100 rounded-lg p-1">
            <button
              @click="viewMode = 'table'"
              :class="[
                'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                viewMode === 'table'
                  ? 'bg-white text-red-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              ]"
            >
              <TableIcon class="h-4 w-4 inline mr-1" />
              Table
            </button>
            <button
              @click="viewMode = 'cards'"
              :class="[
                'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                viewMode === 'cards'
                  ? 'bg-white text-red-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              ]"
            >
              <GridIcon class="h-4 w-4 inline mr-1" />
              Cards
            </button>
          </div>

          <!-- Bulk Actions -->
          <Button
            @click="showBulkActionsModal = true"
            variant="outline"
            class="flex items-center gap-2"
            :disabled="selectedFindings.length === 0"
          >
            <LayersIcon class="h-4 w-4" />
            Bulk Actions
          </Button>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <!-- Header Controls -->
      <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <Checkbox
              :modelValue="selectAll"
              @update:modelValue="toggleSelectAll"
            />
            <span class="text-sm font-medium text-gray-700">
              {{ selectedFindings.length }} of {{ filteredFindings.length }} selected
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              @click="toggleSortOrder"
            >
              <ArrowUpDownIcon class="h-4 w-4 mr-2" />
              Sort by {{ sortBy === 'creation' ? 'Due Date' : 'Created' }}
            </Button>
          </div>
        </div>
      </div>

      <!-- Card View -->
      <div v-if="viewMode === 'cards'" class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          <div
            v-for="finding in paginatedFindings"
            :key="finding.name"
            class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
            :class="{ 'ring-2 ring-red-500': selectedFindings.includes(finding.name) }"
            @click="viewFinding(finding)"
          >
            <!-- Card Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">
                  {{ finding.finding_title || 'Untitled Finding' }}
                </h3>
                <p class="text-sm text-gray-600 mb-2">{{ finding.finding_id }}</p>
                <div class="flex items-center space-x-2 flex-wrap gap-1">
                  <Badge :theme="getSeverityTheme(finding.risk_rating)">
                    {{ finding.risk_rating || 'Medium' }}
                  </Badge>
                  <Badge :theme="getStatusTheme(finding.finding_status)">
                    {{ finding.finding_status || 'Open' }}
                  </Badge>
                  <Badge v-if="finding.repeat_finding" theme="yellow">
                    Repeat
                  </Badge>
                </div>
              </div>
              <Checkbox
                :modelValue="selectedFindings.includes(finding.name)"
                @update:modelValue="toggleFindingSelection(finding.name)"
                @click.stop
              />
            </div>

            <!-- Card Content -->
            <div class="space-y-3">
              <!-- Category & Engagement -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-gray-500 uppercase tracking-wide">Category</p>
                  <p class="text-sm font-medium text-gray-900">{{ finding.finding_category || 'N/A' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-500 uppercase tracking-wide">Engagement</p>
                  <p class="text-sm font-medium text-gray-900 truncate">{{ finding.engagement_reference || 'N/A' }}</p>
                </div>
              </div>

              <!-- Responsible & Due Date -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-gray-500 uppercase tracking-wide">Responsible</p>
                  <p class="text-sm font-medium text-gray-900">{{ finding.responsible_person || 'Unassigned' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-500 uppercase tracking-wide">Due Date</p>
                  <div class="flex items-center">
                    <span 
                      :class="[
                        'text-sm font-medium',
                        isOverdue(finding.target_completion_date) && finding.finding_status !== 'Closed' 
                          ? 'text-red-600' 
                          : 'text-gray-900'
                      ]"
                    >
                      {{ formatDate(finding.target_completion_date) }}
                    </span>
                    <AlertCircleIcon
                      v-if="isOverdue(finding.target_completion_date) && finding.finding_status !== 'Closed'"
                      class="h-4 w-4 text-red-500 ml-1"
                    />
                  </div>
                </div>
              </div>

              <!-- Condition Preview -->
              <div v-if="finding.condition">
                <p class="text-xs text-gray-500 uppercase tracking-wide">Condition</p>
                <p class="text-sm text-gray-700 line-clamp-2">{{ finding.condition }}</p>
              </div>
            </div>

            <!-- Card Actions -->
            <div class="flex items-center justify-end space-x-2 mt-4 pt-4 border-t border-gray-200">
              <Button
                variant="ghost"
                size="sm"
                @click.stop="viewFinding(finding)"
              >
                <EyeIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click.stop="editFinding(finding)"
              >
                <EditIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click.stop="deleteFinding(finding)"
                theme="red"
              >
                <TrashIcon class="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-if="viewMode === 'table'" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-10">
                <Checkbox
                  :modelValue="selectAll"
                  @update:modelValue="toggleSelectAll"
                />
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Finding ID
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Risk Rating
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Engagement
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Responsible
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Due Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="finding in paginatedFindings"
              :key="finding.name"
              class="hover:bg-gray-50 transition-colors cursor-pointer"
              :class="{ 'bg-red-50': selectedFindings.includes(finding.name) }"
              @click="viewFinding(finding)"
            >
              <td class="px-6 py-4 whitespace-nowrap" @click.stop>
                <Checkbox
                  :modelValue="selectedFindings.includes(finding.name)"
                  @update:modelValue="toggleFindingSelection(finding.name)"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div 
                      class="h-10 w-10 rounded-full flex items-center justify-center"
                      :class="getSeverityBgClass(finding.risk_rating)"
                    >
                      <AlertCircleIcon class="h-5 w-5" :class="getSeverityIconClass(finding.risk_rating)" />
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-blue-600 hover:underline">
                      {{ finding.finding_id }}
                    </div>
                    <div v-if="finding.repeat_finding" class="text-xs text-yellow-600">
                      Repeat Finding
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900 max-w-xs truncate">
                  {{ finding.finding_title || 'Untitled' }}
                </div>
                <div class="text-sm text-gray-500 max-w-xs truncate">
                  {{ finding.finding_category || 'No category' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge :theme="getSeverityTheme(finding.risk_rating)">
                  {{ finding.risk_rating || 'Medium' }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge :theme="getStatusTheme(finding.finding_status)">
                  {{ finding.finding_status || 'Open' }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ finding.engagement_reference || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ finding.responsible_person || 'Unassigned' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span 
                    :class="[
                      'text-sm',
                      isOverdue(finding.target_completion_date) && finding.finding_status !== 'Closed' 
                        ? 'text-red-600 font-medium' 
                        : 'text-gray-600'
                    ]"
                  >
                    {{ formatDate(finding.target_completion_date) }}
                  </span>
                  <AlertCircleIcon
                    v-if="isOverdue(finding.target_completion_date) && finding.finding_status !== 'Closed'"
                    class="h-4 w-4 text-red-500 ml-1"
                  />
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium" @click.stop>
                <div class="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="viewFinding(finding)"
                  >
                    <EyeIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="editFinding(finding)"
                  >
                    <EditIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="deleteFinding(finding)"
                    theme="red"
                  >
                    <TrashIcon class="h-4 w-4" />
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-6 py-4 border-t border-gray-200 bg-gray-50">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700">
            Showing {{ paginationStart }} to {{ paginationEnd }} of {{ filteredFindings.length }} results
          </div>
          <div class="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              :disabled="currentPage === 1"
              @click="currentPage--"
            >
              <ChevronLeftIcon class="h-4 w-4" />
              Previous
            </Button>
            <span class="text-sm text-gray-700">
              Page {{ currentPage }} of {{ totalPages }}
            </span>
            <Button
              variant="outline"
              size="sm"
              :disabled="currentPage === totalPages"
              @click="currentPage++"
            >
              Next
              <ChevronRightIcon class="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-if="filteredFindings.length === 0 && !loading"
      class="text-center py-12 bg-white rounded-xl border border-gray-200"
    >
      <AlertCircleIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">No findings found</h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ hasActiveFilters ? 'No findings match your current filters.' : 'Get started by creating your first audit finding.' }}
      </p>
      <div class="mt-6">
        <Button
          @click="createNewFinding"
          class="bg-red-600 hover:bg-red-700 text-white"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          Create Finding
        </Button>
      </div>
    </div>

    <!-- Bulk Actions Modal -->
    <Dialog v-model="showBulkActionsModal" :options="{ title: 'Bulk Actions' }">
      <template #body-content>
        <div class="space-y-4">
          <p class="text-sm text-gray-600">
            Apply bulk action to {{ selectedFindings.length }} selected findings:
          </p>
          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Update Status
              </label>
              <select 
                v-model="bulkStatusUpdate" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                <option value="">Select Status...</option>
                <option value="Open">Open</option>
                <option value="Action in Progress">Action in Progress</option>
                <option value="Pending Verification">Pending Verification</option>
                <option value="Closed">Closed</option>
                <option value="Accepted as Risk">Accepted as Risk</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Assign Responsible Person
              </label>
              <select 
                v-model="bulkResponsibleUpdate" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                <option value="">Select Person...</option>
                <option v-for="user in userOptions" :key="user.value" :value="user.value">
                  {{ user.label }}
                </option>
              </select>
            </div>
            <div class="flex items-center space-x-2 pt-2">
              <Checkbox v-model="bulkDeleteConfirm" />
              <span class="text-sm text-red-600">
                Delete selected findings (this action cannot be undone)
              </span>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="ghost" @click="showBulkActionsModal = false">
          Cancel
        </Button>
        <Button variant="solid" @click="applyBulkActions" :disabled="!bulkStatusUpdate && !bulkResponsibleUpdate && !bulkDeleteConfirm">
          Apply Changes
        </Button>
      </template>
    </Dialog>

    <!-- Finding Form Dialog -->
    <AuditFindingForm
      v-model="showFormDialog"
      :finding="selectedFinding"
      @saved="handleFindingSaved"
      @close="handleFormClose"
    />
  </div>
</template>

<script setup>
import AuditFindingForm from "@/components/findings/AuditFindingForm.vue"
import FindingsStats from "@/components/findings/FindingsStats.vue"
import { useAuditStore } from "@/stores/audit"
import { Badge, Button, Checkbox, Dialog } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	AlertCircleIcon,
	ArrowUpDownIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	GridIcon,
	LayersIcon,
	PlusIcon,
	RefreshCwIcon,
	SearchIcon,
	TableIcon,
	TrashIcon,
} from "lucide-vue-next"
import { computed, onMounted, reactive, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const auditStore = useAuditStore()

// Reactive state
const loading = ref(false)
const exporting = ref(false)
const showFormDialog = ref(false)
const selectedFinding = ref(null)
const viewMode = ref("table")
const sortBy = ref("creation")
const sortOrder = ref("desc")
const currentPage = ref(1)
const itemsPerPage = ref(10)

// Selection state
const selectedFindings = ref([])

// Modal state
const showBulkActionsModal = ref(false)
const bulkStatusUpdate = ref("")
const bulkResponsibleUpdate = ref("")
const bulkDeleteConfirm = ref(false)

// Filters
const filters = reactive({
	search: "",
	status: "",
	category: "",
	riskRating: "",
	engagement: "",
	dateFrom: "",
	dateTo: "",
	responsiblePerson: "",
	followUpRequired: "",
	overdueOnly: false,
	repeatFindingsOnly: false,
	includeInReport: false,
})

// Options for filters
const engagementOptions = ref([])
const userOptions = ref([])

// Computed properties
const findings = computed(() => auditStore.findings)

// Check if any filters are active
const hasActiveFilters = computed(() => {
	return filters.search || filters.status || filters.category || 
		   filters.riskRating || filters.engagement || filters.overdueOnly ||
		   filters.repeatFindingsOnly
})

// Filtered findings based on active filters
const filteredFindings = computed(() => {
	let result = [...findings.value]

	// Search filter
	if (filters.search) {
		const search = filters.search.toLowerCase()
		result = result.filter(
			(f) =>
				f.finding_id?.toLowerCase().includes(search) ||
				f.finding_title?.toLowerCase().includes(search) ||
				f.condition?.toLowerCase().includes(search),
		)
	}

	// Status filter
	if (filters.status) {
		result = result.filter((f) => f.finding_status === filters.status)
	}

	// Category filter
	if (filters.category) {
		result = result.filter((f) => f.finding_category === filters.category)
	}

	// Risk rating filter
	if (filters.riskRating) {
		result = result.filter((f) => f.risk_rating === filters.riskRating)
	}

	// Engagement filter
	if (filters.engagement) {
		result = result.filter((f) => f.engagement_reference === filters.engagement)
	}

	// Overdue filter
	if (filters.overdueOnly) {
		result = result.filter(
			(f) =>
				isOverdue(f.target_completion_date) && f.finding_status !== "Closed",
		)
	}

	// Repeat findings filter
	if (filters.repeatFindingsOnly) {
		result = result.filter((f) => f.repeat_finding)
	}

	// Sort results
	result.sort((a, b) => {
		const aVal = a[sortBy.value] || ""
		const bVal = b[sortBy.value] || ""
		const comparison = aVal > bVal ? 1 : aVal < bVal ? -1 : 0
		return sortOrder.value === "desc" ? -comparison : comparison
	})

	return result
})

// Pagination computed properties
const totalPages = computed(() =>
	Math.max(1, Math.ceil(filteredFindings.value.length / itemsPerPage.value))
)

const paginatedFindings = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	const end = start + itemsPerPage.value
	return filteredFindings.value.slice(start, end)
})

const paginationStart = computed(() => {
	if (filteredFindings.value.length === 0) return 0
	return (currentPage.value - 1) * itemsPerPage.value + 1
})

const paginationEnd = computed(() => {
	return Math.min(currentPage.value * itemsPerPage.value, filteredFindings.value.length)
})

// Selection computed properties
const selectAll = computed({
	get: () =>
		filteredFindings.value.length > 0 &&
		selectedFindings.value.length === filteredFindings.value.length,
	set: (value) => {
		if (value) {
			selectedFindings.value = filteredFindings.value.map((f) => f.name)
		} else {
			selectedFindings.value = []
		}
	},
})

// Stats calculation
const findingsStats = computed(() => {
	const all = findings.value
	const today = new Date()
	const thisMonth = new Date(today.getFullYear(), today.getMonth(), 1)

	const open = all.filter((f) => f.finding_status === "Open")
	const inProgress = all.filter(
		(f) => f.finding_status === "Action in Progress",
	)
	const pendingVerification = all.filter(
		(f) => f.finding_status === "Pending Verification",
	)
	const closed = all.filter((f) => f.finding_status === "Closed")

	// Overdue calculation
	const overdue = all.filter(
		(f) => f.finding_status !== "Closed" && isOverdue(f.target_completion_date),
	)

	// This month
	const createdThisMonth = all.filter((f) => new Date(f.creation) >= thisMonth)

	// By severity
	const bySeverity = {
		critical: open.filter((f) => f.risk_rating === "Critical").length,
		high: open.filter((f) => f.risk_rating === "High").length,
		medium: open.filter((f) => f.risk_rating === "Medium").length,
		low: open.filter((f) => f.risk_rating === "Low").length,
	}

	// Aging calculation for open findings
	const aging = calculateAging(all.filter((f) => f.finding_status !== "Closed"))

	return {
		total: all.length,
		thisMonth: createdThisMonth.length,
		open: open.length,
		overdue: overdue.length,
		inProgress: inProgress.length,
		pendingVerification: pendingVerification.length,
		closed: closed.length,
		closureRate:
			all.length > 0 ? Math.round((closed.length / all.length) * 100) : 0,
		bySeverity,
		aging,
	}
})

// Helper functions
const calculateAging = (openFindings) => {
	const today = new Date()
	const aging = { days0to30: 0, days31to60: 0, days61to90: 0, days90plus: 0 }

	openFindings.forEach((f) => {
		const created = new Date(f.creation)
		const days = Math.floor((today - created) / (1000 * 60 * 60 * 24))

		if (days <= 30) aging.days0to30++
		else if (days <= 60) aging.days31to60++
		else if (days <= 90) aging.days61to90++
		else aging.days90plus++
	})

	return aging
}

const isOverdue = (dateStr) => {
	if (!dateStr) return false
	return new Date(dateStr) < new Date()
}

const formatDate = (dateStr) => {
	if (!dateStr) return "-"
	return new Date(dateStr).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	})
}

// Theme functions
const getSeverityTheme = (severity) => {
	const themes = {
		Critical: "red",
		High: "orange",
		Medium: "yellow",
		Low: "green",
	}
	return themes[severity] || "gray"
}

const getSeverityBgClass = (severity) => {
	const classes = {
		Critical: "bg-red-100",
		High: "bg-orange-100",
		Medium: "bg-yellow-100",
		Low: "bg-green-100",
	}
	return classes[severity] || "bg-gray-100"
}

const getSeverityIconClass = (severity) => {
	const classes = {
		Critical: "text-red-600",
		High: "text-orange-600",
		Medium: "text-yellow-600",
		Low: "text-green-600",
	}
	return classes[severity] || "text-gray-600"
}

const getStatusTheme = (status) => {
	const themes = {
		Open: "red",
		"Action in Progress": "yellow",
		"Pending Verification": "blue",
		Closed: "green",
		"Accepted as Risk": "gray",
		"Management Override": "gray",
	}
	return themes[status] || "gray"
}

// Data fetching
const fetchFindings = async () => {
	loading.value = true
	try {
		const response = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Audit Finding",
				fields: [
					"name",
					"finding_id",
					"finding_title",
					"finding_status",
					"finding_category",
					"risk_rating",
					"engagement_reference",
					"responsible_person",
					"responsible_department",
					"target_completion_date",
					"creation",
					"modified",
					"condition",
					"effect",
					"recommendation",
					"repeat_finding",
					"follow_up_required",
				],
				limit_page_length: 1000,
				order_by: "creation desc",
			},
		}).fetch()

		auditStore.setFindings(response || [])
	} catch (error) {
		console.error("Error loading findings:", error)
		auditStore.setFindings([])
	} finally {
		loading.value = false
	}
}

const fetchOptions = async () => {
	// Fetch engagement options
	try {
		const engagements = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Audit Engagement",
				fields: ["name", "engagement_title"],
				limit_page_length: 500,
			},
		}).fetch()
		engagementOptions.value = (engagements || []).map((e) => ({
			label: e.engagement_title || e.name,
			value: e.name,
		}))
	} catch (error) {
		console.error("Error loading engagements:", error)
	}

	// Fetch user options
	try {
		const users = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "User",
				fields: ["name", "full_name"],
				filters: { enabled: 1 },
				limit_page_length: 500,
			},
		}).fetch()
		userOptions.value = (users || []).map((u) => ({
			label: u.full_name || u.name,
			value: u.name,
		}))
	} catch (error) {
		console.error("Error loading users:", error)
	}
}

// Selection methods
const toggleSelectAll = (value) => {
	if (value) {
		selectedFindings.value = filteredFindings.value.map((f) => f.name)
	} else {
		selectedFindings.value = []
	}
}

const toggleFindingSelection = (findingName) => {
	const index = selectedFindings.value.indexOf(findingName)
	if (index > -1) {
		selectedFindings.value.splice(index, 1)
	} else {
		selectedFindings.value.push(findingName)
	}
}

// Sort methods
const toggleSortOrder = () => {
	if (sortBy.value === "creation") {
		sortBy.value = "target_completion_date"
	} else {
		sortBy.value = "creation"
	}
}

// Action methods
const refreshData = async () => {
	await fetchFindings()
}

const createNewFinding = () => {
	selectedFinding.value = null
	showFormDialog.value = true
}

const viewFinding = (finding) => {
	router.push(`/findings/${finding.name}`)
}

const editFinding = (finding) => {
	selectedFinding.value = finding
	showFormDialog.value = true
}

const deleteFinding = async (finding) => {
	if (confirm("Are you sure you want to delete this finding?")) {
		try {
			await createResource({
				url: "frappe.client.delete",
				params: {
					doctype: "Audit Finding",
					name: finding.name,
				},
			}).fetch()
			await fetchFindings()
		} catch (error) {
			console.error("Error deleting finding:", error)
		}
	}
}

const exportFindings = async () => {
	exporting.value = true
	try {
		// TODO: Implement export logic
		console.log("Exporting findings...")
	} finally {
		exporting.value = false
	}
}

// Bulk actions
const applyBulkActions = async () => {
	if (bulkDeleteConfirm.value) {
		if (confirm(`Are you sure you want to delete ${selectedFindings.value.length} findings?`)) {
			for (const name of selectedFindings.value) {
				try {
					await createResource({
						url: "frappe.client.delete",
						params: {
							doctype: "Audit Finding",
							name: name,
						},
					}).fetch()
				} catch (error) {
					console.error(`Error deleting finding ${name}:`, error)
				}
			}
		}
	} else {
		// Update status or responsible person
		for (const name of selectedFindings.value) {
			const updateData = {}
			if (bulkStatusUpdate.value) {
				updateData.finding_status = bulkStatusUpdate.value
			}
			if (bulkResponsibleUpdate.value) {
				updateData.responsible_person = bulkResponsibleUpdate.value
			}
			
			if (Object.keys(updateData).length > 0) {
				try {
					await createResource({
						url: "frappe.client.set_value",
						params: {
							doctype: "Audit Finding",
							name: name,
							fieldname: updateData,
						},
					}).fetch()
				} catch (error) {
					console.error(`Error updating finding ${name}:`, error)
				}
			}
		}
	}
	
	// Reset and refresh
	showBulkActionsModal.value = false
	bulkStatusUpdate.value = ""
	bulkResponsibleUpdate.value = ""
	bulkDeleteConfirm.value = false
	selectedFindings.value = []
	await fetchFindings()
}

const handleFindingSaved = async () => {
	await fetchFindings()
	showFormDialog.value = false
	selectedFinding.value = null
}

const handleFormClose = () => {
	selectedFinding.value = null
}

// Lifecycle
onMounted(async () => {
	await Promise.all([fetchFindings(), fetchOptions()])
})
</script>