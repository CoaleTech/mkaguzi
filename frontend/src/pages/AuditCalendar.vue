<template>
  <div class="space-y-6">
    <!-- Page Header with Enhanced Actions -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-blue-100 rounded-lg">
            <CalendarIcon class="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Audit Calendar</h1>
            <p class="text-gray-600 mt-1">
              Schedule and manage audit engagements and timelines
            </p>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <!-- Action Buttons -->
        <div class="flex items-center space-x-2">
          <div class="p-1">
            <Button
              variant="solid"
              theme="gray"
              size="sm"
              @click="exportCalendar"
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
              @click="showTemplateModal = true"
            >
              <template #prefix>
                <FileTextIcon class="h-3.5 w-3.5" />
              </template>
              Templates
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
              theme="blue"
              size="sm"
              @click="showCreateModal = true"
            >
              <template #prefix>
                <PlusIcon class="h-3.5 w-3.5" />
              </template>
              Schedule Audit
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Stats Dashboard -->
    <CalendarStats
      :stats="calendarStats"
    />

    <!-- Quick Actions Bar -->
    <CalendarFilters
      :filters="filters"
      :status-options="statusOptions"
      :audit-type-options="auditTypeOptions"
      :universe-options="universeOptions"
      :selected-count="selectedAudits.length"
      :filtered-count="filteredAudits.length"
      :total-count="auditCalendar.length"
      :view-mode="viewMode"
      @update:filters="updateFilters"
      @bulk-actions="showBulkModal = true"
      @capacity-planning="showCapacityModal = true"
      @toggle-view="toggleViewMode"
    />    <!-- Main Content Area -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <!-- Calendar View -->
      <div v-if="viewMode === 'calendar'" class="p-6">
        <!-- Calendar Header -->
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center space-x-4">
            <Button
              variant="outline"
              size="sm"
              @click="previousMonth"
            >
              <ChevronLeftIcon class="h-4 w-4" />
            </Button>
            <h3 class="text-xl font-semibold text-gray-900">
              {{ format(currentMonth, 'MMMM yyyy') }}
            </h3>
            <Button
              variant="outline"
              size="sm"
              @click="nextMonth"
            >
              <ChevronRightIcon class="h-4 w-4" />
            </Button>
          </div>
          <Button
            variant="outline"
            size="sm"
            @click="currentMonth = new Date()"
          >
            Today
          </Button>
        </div>

        <!-- Calendar Grid -->
        <div class="grid grid-cols-7 gap-1 mb-4">
          <div
            v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']"
            :key="day"
            class="p-3 text-center text-sm font-medium text-gray-500 bg-gray-50 rounded-lg"
          >
            {{ day }}
          </div>
        </div>

        <div class="grid grid-cols-7 gap-1">
          <div
            v-for="day in calendarDays"
            :key="day.date"
            class="min-h-32 p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
            :class="{
              'bg-blue-50 border-blue-200': isToday(day.date),
              'bg-gray-100': !isSameMonth(day.date, currentMonth)
            }"
            @click="selectDate(day.date)"
          >
            <div class="flex justify-between items-start mb-2">
              <span
                class="text-sm font-medium"
                :class="{
                  'text-blue-600': isToday(day.date),
                  'text-gray-400': !isSameMonth(day.date, currentMonth),
                  'text-gray-900': isSameMonth(day.date, currentMonth) && !isToday(day.date)
                }"
              >
                {{ format(day.date, 'd') }}
              </span>
              <div v-if="day.audits.length > 0" class="text-xs text-gray-500">
                {{ day.audits.length }}
              </div>
            </div>

            <div class="space-y-1">
              <div
                v-for="audit in day.audits.slice(0, 3)"
                :key="audit.name"
                class="text-xs p-1 rounded truncate"
                :class="getAuditStatusClass(audit.status)"
                @click.stop="editAudit(audit)"
              >
                {{ audit.calendar_id || audit.name }}
              </div>
              <div
                v-if="day.audits.length > 3"
                class="text-xs text-gray-500 text-center"
              >
                +{{ day.audits.length - 3 }} more
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="overflow-hidden">
        <!-- Table Header -->
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <Checkbox
                :modelValue="selectAll"
                @update:modelValue="toggleSelectAll"
              />
              <span class="text-sm font-medium text-gray-700">
                {{ selectedAudits.length }} of {{ filteredAudits.length }} selected
              </span>
            </div>
            <div class="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                @click="sortBy = sortBy === 'start_date' ? 'end_date' : 'start_date'"
              >
                <ArrowUpDownIcon class="h-4 w-4 mr-2" />
                Sort by {{ sortBy === 'start_date' ? 'End Date' : 'Start Date' }}
              </Button>
            </div>
          </div>
        </div>

        <!-- Table Content -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <Checkbox
                    :modelValue="selectAll"
                    @update:modelValue="toggleSelectAll"
                  />
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Calendar ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Universe
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Start Date
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  End Date
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Progress
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="audit in paginatedAudits"
                :key="audit.name"
                class="hover:bg-gray-50 transition-colors"
                :class="{ 'bg-blue-50': selectedAudits.includes(audit.name) }"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <Checkbox
                    :modelValue="selectedAudits.includes(audit.name)"
                    @update:modelValue="toggleAuditSelection(audit.name)"
                  />
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                      <div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                        <FileTextIcon class="h-5 w-5 text-gray-600" />
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">
                        {{ audit.calendar_id || audit.name }}
                      </div>
                      <div class="text-sm text-gray-500">
                        {{ audit.objectives?.substring(0, 50) }}...
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <Badge :theme="getAuditTypeTheme(audit.audit_type)">
                    {{ audit.audit_type }}
                  </Badge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ getUniverseName(audit.audit_universe) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDate(audit.planned_start_date) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDate(audit.planned_end_date) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        :style="{ width: `${audit.progress_percentage || 0}%` }"
                      ></div>
                    </div>
                    <span class="text-sm text-gray-600">{{ audit.progress_percentage || 0 }}%</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <Badge :theme="getStatusTheme(audit.status)">
                    {{ audit.status }}
                  </Badge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="viewCalendarItem(audit)"
                    >
                      <EyeIcon class="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="editCalendarItem(audit)"
                    >
                      <EditIcon class="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="deleteAudit(audit)"
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
              Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredAudits.length) }} of {{ filteredAudits.length }} results
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
    </div>

    <!-- Empty State -->
    <div
      v-if="filteredAudits.length === 0"
      class="text-center py-12 bg-white rounded-xl border border-gray-200"
    >
      <CalendarIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">No audits scheduled</h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ filters.searchQuery || filters.statusFilter || filters.typeFilter || filters.universeFilter ? 'No audits match your current filters.' : 'Get started by scheduling your first audit.' }}
      </p>
      <div class="mt-6">
        <Button
          @click="showCreateModal = true"
          class="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          Schedule Audit
        </Button>
      </div>
    </div>

    <!-- Create/Edit Calendar Modal -->
    <Dialog
      v-model="showCreateModal"
      :title="editingItem ? 'Edit Audit Schedule' : 'Schedule New Audit'"
      size="4xl"
    >
      <template #body>
        <AuditCalendarForm
          :form="calendarForm"
          :universe-options="universeOptions"
          :audit-type-options="auditTypeOptions"
          :status-options="statusOptions"
          :plan-options="planOptions"
        />
      </template>

      <template #footer>
        <div class="flex justify-end space-x-3">
          <Button
            variant="outline"
            @click="showCreateModal = false"
          >
            Cancel
          </Button>
          <Button
            @click="saveCalendarItem"
            :loading="saving"
            class="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {{ editingItem ? 'Update' : 'Schedule' }} Audit
          </Button>
        </div>
      </template>
    </Dialog>

    <!-- Templates Modal -->
    <Dialog
      v-model="showTemplateModal"
      title="Audit Calendar Templates"
      size="3xl"
    >
      <template #body>
        <div class="space-y-4">
          <p class="text-gray-600">
            Choose from pre-built audit calendar templates to quickly schedule your audits.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="template in calendarTemplates"
              :key="template.id"
              class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
              @click="applyTemplate(template)"
            >
              <div class="flex items-start space-x-3">
                <div class="p-2 bg-blue-100 rounded-lg">
                  <FileTextIcon class="h-5 w-5 text-blue-600" />
                </div>
                <div class="flex-1">
                  <h4 class="font-medium text-gray-900">{{ template.name }}</h4>
                  <p class="text-sm text-gray-600 mt-1">{{ template.description }}</p>
                  <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <span>{{ template.audits }} audits</span>
                    <span>{{ template.duration }} months</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end">
          <Button
            variant="outline"
            @click="showTemplateModal = false"
          >
            Cancel
          </Button>
        </div>
      </template>
    </Dialog>

    <!-- Bulk Actions Modal -->
    <Dialog
      v-model="showBulkModal"
      title="Bulk Actions"
      size="2xl"
    >
      <template #body>
        <div class="space-y-6">
          <div class="bg-blue-50 rounded-lg p-4">
            <div class="flex items-center space-x-2">
              <LayersIcon class="h-5 w-5 text-blue-600" />
              <span class="font-medium text-blue-900">
                {{ selectedAudits.length }} audits selected
              </span>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Update Status
              </label>
              <Select
                v-model="bulkStatusUpdate"
                :options="statusOptions"
                placeholder="Select new status"
              />
              <Button
                variant="solid"
                theme="blue"
                size="sm"
                class="mt-2"
                @click="applyBulkStatusUpdate"
                :loading="bulkUpdating"
              >
                Apply Status Update
              </Button>
            </div>

            <div class="border-t pt-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Bulk Delete
              </label>
              <p class="text-sm text-gray-600 mb-3">
                This action cannot be undone. All selected audits will be permanently deleted.
              </p>
              <Button
                variant="solid"
                theme="red"
                size="sm"
                @click="confirmBulkDelete"
              >
                Delete Selected Audits
              </Button>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end">
          <Button
            variant="outline"
            @click="showBulkModal = false"
          >
            Close
          </Button>
        </div>
      </template>
    </Dialog>

    <!-- Capacity Planning Modal -->
    <Dialog
      v-model="showCapacityModal"
      title="Capacity Planning"
      size="4xl"
    >
      <template #body>
        <div class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-blue-50 rounded-lg p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-blue-700">Total Capacity</p>
                  <p class="text-2xl font-bold text-blue-900">{{ totalCapacity }}</p>
                </div>
                <UserIcon class="h-8 w-8 text-blue-600" />
              </div>
            </div>

            <div class="bg-green-50 rounded-lg p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-green-700">Available</p>
                  <p class="text-2xl font-bold text-green-900">{{ availableCapacity }}</p>
                </div>
                <CheckCircleIcon class="h-8 w-8 text-green-600" />
              </div>
            </div>

            <div class="bg-yellow-50 rounded-lg p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-yellow-700">Utilization</p>
                  <p class="text-2xl font-bold text-yellow-900">{{ utilizationRate }}%</p>
                </div>
                <BarChartIcon class="h-8 w-8 text-yellow-600" />
              </div>
            </div>
          </div>

          <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div class="px-4 py-3 border-b border-gray-200 bg-gray-50">
              <h4 class="font-medium text-gray-900">Auditor Workload</h4>
            </div>
            <div class="p-4">
              <div class="space-y-4">
                <div
                  v-for="auditor in auditorWorkload"
                  :key="auditor.name"
                  class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <UserIcon class="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                      <p class="font-medium text-gray-900">{{ auditor.name }}</p>
                      <p class="text-sm text-gray-600">{{ auditor.audits }} active audits</p>
                    </div>
                  </div>
                  <div class="text-right">
                    <div class="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        :style="{ width: `${auditor.utilization}%` }"
                      ></div>
                    </div>
                    <p class="text-xs text-gray-600 mt-1">{{ auditor.utilization }}% utilized</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end">
          <Button
            variant="outline"
            @click="showCapacityModal = false"
          >
            Close
          </Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import AuditCalendarForm from "@/components/calendar/AuditCalendarForm.vue"
import CalendarFilters from "@/components/calendar/CalendarFilters.vue"
import CalendarStats from "@/components/calendar/CalendarStats.vue"
import { useAuditStore } from "@/stores/audit"
import {
	addMonths,
	eachDayOfInterval,
	endOfMonth,
	endOfWeek,
	format,
	isSameDay,
	isSameMonth,
	isToday as isTodayDate,
	startOfMonth,
	startOfWeek,
	subMonths,
} from "date-fns"
import { Badge, Button, Checkbox, Dialog, FormControl, Select } from "frappe-ui"
import {
	AlertTriangleIcon,
	ArrowUpDownIcon,
	BarChart3Icon,
	BarChartIcon,
	CalendarIcon,
	CheckCircleIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	ClockIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	FileTextIcon,
	LayersIcon,
	PlayIcon,
	PlusIcon,
	RefreshCwIcon,
	TableIcon,
	TrashIcon,
	UserIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const auditStore = useAuditStore()

// Reactive state
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const editingItem = ref(null)
const viewMode = ref("calendar") // Changed default to calendar view
const currentMonth = ref(new Date())
const selectedDate = ref(null)

// New reactive variables for enhanced functionality
const searchQuery = ref("")
const statusFilter = ref("")
const typeFilter = ref("")
const universeFilter = ref("")
const selectedAudits = ref([])
const sortBy = ref("start_date")
const currentPage = ref(1)
const itemsPerPage = ref(10)
const showBulkModal = ref(false)
const showCapacityModal = ref(false)
const showTemplateModal = ref(false)
const exporting = ref(false)

// Filters object for CalendarFilters component
const filters = ref({
	searchQuery: "",
	statusFilter: "",
	typeFilter: "",
	universeFilter: "",
})

// Form data
const calendarForm = ref({
	calendar_id: "",
	annual_audit_plan: "",
	audit_universe: "",
	audit_type: "",
	status: "Planned",
	planned_start_date: "",
	planned_end_date: "",
	lead_auditor: "",
	estimated_days: 0,
	progress_percentage: 0,
	objectives: "",
	scope: "",
	key_risks: "",
})

// Options
const auditTypeOptions = [
	{ label: "Financial", value: "Financial" },
	{ label: "Operational", value: "Operational" },
	{ label: "Compliance", value: "Compliance" },
	{ label: "IT", value: "IT" },
	{ label: "Integrated", value: "Integrated" },
	{ label: "Special Investigation", value: "Special Investigation" },
	{ label: "Follow-up", value: "Follow-up" },
]

const statusOptions = [
	{ label: "Planned", value: "Planned" },
	{ label: "Scheduled", value: "Scheduled" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "On Hold", value: "On Hold" },
	{ label: "Completed", value: "Completed" },
	{ label: "Cancelled", value: "Cancelled" },
	{ label: "Rescheduled", value: "Rescheduled" },
]

// Computed properties
const auditCalendar = computed(() => auditStore.auditCalendar)
const inProgressAudits = computed(() =>
	auditStore.auditCalendar.filter((item) => item.status === "In Progress"),
)
const upcomingAudits = computed(() => auditStore.upcomingAudits)

const averageProgress = computed(() => {
	if (auditStore.auditCalendar.length === 0) return 0
	const total = auditStore.auditCalendar.reduce(
		(sum, item) => sum + (item.progress_percentage || 0),
		0,
	)
	return Math.round(total / auditStore.auditCalendar.length)
})

const universeOptions = computed(() => {
	return auditStore.auditUniverse.map((universe) => ({
		label: `${universe.universe_id} - ${universe.auditable_entity}`,
		value: universe.name,
	}))
})

const planOptions = computed(() => {
	return auditStore.activeAnnualPlans.map((plan) => ({
		label: `${plan.plan_id} (${plan.plan_year})`,
		value: plan.name,
	}))
})

// New computed properties for enhanced functionality
const filteredAudits = computed(() => {
	let filtered = [...auditCalendar.value]

	// Apply search filter
	if (filters.value.searchQuery) {
		const query = filters.value.searchQuery.toLowerCase()
		filtered = filtered.filter(
			(audit) =>
				audit.calendar_id?.toLowerCase().includes(query) ||
				audit.audit_type?.toLowerCase().includes(query) ||
				getUniverseName(audit.audit_universe)?.toLowerCase().includes(query) ||
				audit.status?.toLowerCase().includes(query),
		)
	}

	// Apply status filter
	if (filters.value.statusFilter) {
		filtered = filtered.filter(
			(audit) => audit.status === filters.value.statusFilter,
		)
	}

	// Apply type filter
	if (filters.value.typeFilter) {
		filtered = filtered.filter(
			(audit) => audit.audit_type === filters.value.typeFilter,
		)
	}

	// Apply universe filter
	if (filters.value.universeFilter) {
		filtered = filtered.filter(
			(audit) => audit.audit_universe === filters.value.universeFilter,
		)
	}

	// Apply sorting
	filtered.sort((a, b) => {
		const aDate = new Date(a.planned_start_date || a.planned_end_date)
		const bDate = new Date(b.planned_start_date || b.planned_end_date)
		return sortBy.value === "start_date" ? aDate - bDate : bDate - aDate
	})

	return filtered
})

const selectAll = computed({
	get: () =>
		filteredAudits.value.length > 0 &&
		selectedAudits.value.length === filteredAudits.value.length,
	set: (value) => {
		if (value) {
			selectedAudits.value = filteredAudits.value.map((audit) => audit.name)
		} else {
			selectedAudits.value = []
		}
	},
})

const paginatedAudits = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage.value
	const end = start + itemsPerPage.value
	return filteredAudits.value.slice(start, end)
})

const totalPages = computed(() =>
	Math.ceil(filteredAudits.value.length / itemsPerPage.value),
)

// Enhanced stats computed properties
const totalScheduled = computed(() => auditCalendar.value.length)

const inProgressCount = computed(
	() =>
		auditCalendar.value.filter((item) => item.status === "In Progress").length,
)

const upcomingCount = computed(() => {
	const now = new Date()
	const thirtyDaysFromNow = new Date()
	thirtyDaysFromNow.setDate(now.getDate() + 30)

	return auditCalendar.value.filter((item) => {
		if (!item.planned_start_date) return false
		const startDate = new Date(item.planned_start_date)
		return startDate >= now && startDate <= thirtyDaysFromNow
	}).length
})

const overdueCount = computed(() => {
	const now = new Date()
	return auditCalendar.value.filter((item) => {
		if (!item.planned_end_date || item.status === "Completed") return false
		const endDate = new Date(item.planned_end_date)
		return endDate < now
	}).length
})

// Calendar stats for CalendarStats component
const calendarStats = computed(() => ({
	totalScheduled: auditCalendar.value.length,
	inProgress: inProgressCount.value,
	upcoming: upcomingCount.value,
	averageProgress: averageProgress.value,
	overdue: overdueCount.value,
	totalCapacity: 15, // Mock data - would come from auditor records
}))

// Calendar computed properties
const calendarDays = computed(() => {
	const monthStart = startOfMonth(currentMonth.value)
	const monthEnd = endOfMonth(currentMonth.value)
	const calendarStart = startOfWeek(monthStart)
	const calendarEnd = endOfWeek(monthEnd)

	const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd })

	return days.map((date) => ({
		date,
		isCurrentMonth: isSameMonth(date, currentMonth.value),
		isToday: isTodayDate(date),
		audits: getEventsForDate(date),
	}))
})

// Methods
const refreshData = async () => {
	loading.value = true
	try {
		await Promise.all([
			auditStore.fetchAuditCalendar(),
			auditStore.fetchAuditUniverse(),
			auditStore.fetchAnnualPlans(),
		])
	} finally {
		loading.value = false
	}
}

// Methods for component interactions
const updateFilters = (newFilters) => {
	filters.value = { ...newFilters }
	searchQuery.value = newFilters.searchQuery
	statusFilter.value = newFilters.statusFilter
	typeFilter.value = newFilters.typeFilter
	universeFilter.value = newFilters.universeFilter
}

const toggleViewMode = () => {
	viewMode.value = viewMode.value === "calendar" ? "list" : "calendar"
}

const getUniverseName = (universeId) => {
	const universe = auditStore.auditUniverse.find((u) => u.name === universeId)
	return universe ? universe.auditable_entity : universeId
}

const viewCalendarItem = (item) => {
	router.push(`/audit-planning/calendar/${item.name}`)
}

const editCalendarItem = (item) => {
	editingItem.value = item
	// Load item data into form
	calendarForm.value = { ...item }
	showCreateModal.value = true
}

const updateStatus = async (item, newStatus) => {
	try {
		await auditStore.updateAuditCalendarEntry(item.name, { status: newStatus })
		await refreshData()
	} catch (error) {
		console.error("Error updating status:", error)
	}
}

const saveCalendarItem = async () => {
	saving.value = true
	try {
		if (editingItem.value) {
			await auditStore.updateAuditCalendarEntry(
				editingItem.value.name,
				calendarForm.value,
			)
		} else {
			await auditStore.createAuditCalendarEntry(calendarForm.value)
		}

		showCreateModal.value = false
		resetForm()
		await refreshData()
	} catch (error) {
		console.error("Error saving calendar item:", error)
	} finally {
		saving.value = false
	}
}

const resetForm = () => {
	calendarForm.value = {
		calendar_id: "",
		annual_audit_plan: "",
		audit_universe: "",
		audit_type: "",
		status: "Planned",
		planned_start_date: "",
		planned_end_date: "",
		lead_auditor: "",
		estimated_days: 0,
		progress_percentage: 0,
		objectives: "",
		scope: "",
		key_risks: "",
	}
	editingItem.value = null
}

const getStatusVariant = (status) => {
	const variants = {
		Planned: "secondary",
		Scheduled: "primary",
		"In Progress": "warning",
		"On Hold": "danger",
		Completed: "success",
		Cancelled: "danger",
		Rescheduled: "warning",
	}
	return variants[status] || "secondary"
}

const formatDate = (dateString) => {
	if (!dateString) return ""
	return new Date(dateString).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	})
}

// Calendar methods
const formatMonthYear = (date) => {
	return format(date, "MMMM yyyy")
}

const formatDay = (date) => {
	return format(date, "d")
}

const formatFullDate = (date) => {
	return format(date, "EEEE, MMMM d, yyyy")
}

const isToday = (date) => {
	return isTodayDate(date)
}

const isCurrentMonth = (date) => {
	return isSameMonth(date, currentMonth.value)
}

const previousMonth = () => {
	currentMonth.value = subMonths(currentMonth.value, 1)
	selectedDate.value = null
}

const nextMonth = () => {
	currentMonth.value = addMonths(currentMonth.value, 1)
	selectedDate.value = null
}

const goToToday = () => {
	currentMonth.value = new Date()
	selectedDate.value = null
}

const selectDate = (date) => {
	selectedDate.value =
		selectedDate.value && isSameDay(selectedDate.value, date) ? null : date
}

const getEventsForDate = (date) => {
	return auditCalendar.value.filter((event) => {
		if (!event.planned_start_date) return false
		const eventDate = new Date(event.planned_start_date)
		return isSameDay(eventDate, date)
	})
}

const getEventColor = (status) => {
	const colors = {
		Planned: "bg-gray-400",
		Scheduled: "bg-blue-400",
		"In Progress": "bg-yellow-400",
		"On Hold": "bg-red-400",
		Completed: "bg-green-400",
		Cancelled: "bg-gray-600",
		Rescheduled: "bg-orange-400",
	}
	return colors[status] || "bg-gray-400"
}

const getEventBackground = (status) => {
	const backgrounds = {
		Planned: "bg-gray-100 text-gray-800",
		Scheduled: "bg-blue-100 text-blue-800",
		"In Progress": "bg-yellow-100 text-yellow-800",
		"On Hold": "bg-red-100 text-red-800",
		Completed: "bg-green-100 text-green-800",
		Cancelled: "bg-gray-200 text-gray-600",
		Rescheduled: "bg-orange-100 text-orange-800",
	}
	return backgrounds[status] || "bg-gray-100 text-gray-800"
}

// New methods for enhanced functionality
const toggleSelectAll = (value) => {
	if (value) {
		selectedAudits.value = filteredAudits.value.map((audit) => audit.name)
	} else {
		selectedAudits.value = []
	}
}

const toggleAuditSelection = (auditName) => {
	const index = selectedAudits.value.indexOf(auditName)
	if (index > -1) {
		selectedAudits.value.splice(index, 1)
	} else {
		selectedAudits.value.push(auditName)
	}
}

const getAuditStatusClass = (status) => {
	const classes = {
		Planned: "bg-gray-100 text-gray-800",
		Scheduled: "bg-blue-100 text-blue-800",
		"In Progress": "bg-yellow-100 text-yellow-800",
		"On Hold": "bg-red-100 text-red-800",
		Completed: "bg-green-100 text-green-800",
		Cancelled: "bg-gray-200 text-gray-600",
		Rescheduled: "bg-orange-100 text-orange-800",
	}
	return classes[status] || "bg-gray-100 text-gray-800"
}

const getAuditTypeTheme = (type) => {
	const themes = {
		Financial: "blue",
		Operational: "green",
		Compliance: "purple",
		IT: "orange",
		Integrated: "red",
		"Special Investigation": "gray",
		"Follow-up": "yellow",
	}
	return themes[type] || "gray"
}

const getStatusTheme = (status) => {
	const themes = {
		Planned: "gray",
		Scheduled: "blue",
		"In Progress": "yellow",
		"On Hold": "red",
		Completed: "green",
		Cancelled: "gray",
		Rescheduled: "orange",
	}
	return themes[status] || "gray"
}

const editAudit = (audit) => {
	editingItem.value = audit
	calendarForm.value = { ...audit }
	showCreateModal.value = true
}

const viewAudit = (audit) => {
	router.push(`/audit-planning/calendar/${audit.name}`)
}

const deleteAudit = async (audit) => {
	if (
		confirm(`Are you sure you want to delete audit "${audit.calendar_id}"?`)
	) {
		try {
			await auditStore.deleteAuditCalendarEntry(audit.name)
			await refreshData()
		} catch (error) {
			console.error("Error deleting audit:", error)
		}
	}
}

const exportCalendar = async () => {
	exporting.value = true
	try {
		// Implement export functionality
		console.log("Exporting calendar data...")
		// This would typically call an API to export the data
	} finally {
		exporting.value = false
	}
}

// New reactive variables for modals
const bulkStatusUpdate = ref("")
const bulkUpdating = ref(false)

// Calendar templates data
const calendarTemplates = [
	{
		id: "annual-financial",
		name: "Annual Financial Audit",
		description: "Complete financial audit cycle with quarterly reviews",
		audits: 5,
		duration: 12,
	},
	{
		id: "compliance-check",
		name: "Compliance Review",
		description: "Regulatory compliance and internal controls assessment",
		audits: 8,
		duration: 6,
	},
	{
		id: "operational-efficiency",
		name: "Operational Efficiency",
		description: "Process optimization and efficiency improvement audits",
		audits: 6,
		duration: 9,
	},
	{
		id: "it-security",
		name: "IT Security Audit",
		description: "Information security and data protection assessments",
		audits: 4,
		duration: 8,
	},
]

// Capacity planning computed properties
const totalCapacity = computed(() => 15) // Mock data - would come from auditor records
const availableCapacity = computed(
	() => totalCapacity.value - inProgressCount.value,
)
const utilizationRate = computed(() => {
	if (totalCapacity.value === 0) return 0
	return Math.round((inProgressCount.value / totalCapacity.value) * 100)
})

const auditorWorkload = computed(() => [
	{ name: "John Smith", audits: 3, utilization: 75 },
	{ name: "Sarah Johnson", audits: 2, utilization: 50 },
	{ name: "Mike Davis", audits: 4, utilization: 90 },
	{ name: "Lisa Brown", audits: 1, utilization: 25 },
])

// Modal methods
const applyTemplate = (template) => {
	console.log("Applying template:", template)
	// Implement template application logic
	showTemplateModal.value = false
}

const applyBulkStatusUpdate = async () => {
	if (!bulkStatusUpdate.value || selectedAudits.value.length === 0) return

	bulkUpdating.value = true
	try {
		for (const auditName of selectedAudits.value) {
			await auditStore.updateAuditCalendarEntry(auditName, {
				status: bulkStatusUpdate.value,
			})
		}
		selectedAudits.value = []
		bulkStatusUpdate.value = ""
		showBulkModal.value = false
		await refreshData()
	} catch (error) {
		console.error("Error applying bulk status update:", error)
	} finally {
		bulkUpdating.value = false
	}
}

const confirmBulkDelete = async () => {
	if (selectedAudits.value.length === 0) return

	if (
		confirm(
			`Are you sure you want to delete ${selectedAudits.value.length} selected audits? This action cannot be undone.`,
		)
	) {
		try {
			for (const auditName of selectedAudits.value) {
				await auditStore.deleteAuditCalendarEntry(auditName)
			}
			selectedAudits.value = []
			showBulkModal.value = false
			await refreshData()
		} catch (error) {
			console.error("Error deleting audits:", error)
		}
	}
}

// Lifecycle
onMounted(async () => {
	await refreshData()
})
</script>