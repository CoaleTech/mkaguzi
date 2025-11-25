<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit Calendar</h1>
        <p class="text-gray-600 mt-1">
          Schedule and manage audit engagements and timelines
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button
          variant="outline"
          @click="refreshData"
          :loading="loading"
        >
          <RefreshCwIcon class="h-4 w-4 mr-2" />
          Refresh
        </Button>
        <Button
          @click="showCreateModal = true"
          class="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          Schedule Audit
        </Button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Scheduled</p>
            <p class="text-3xl font-bold text-gray-900">{{ auditCalendar.length }}</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-full">
            <CalendarIcon class="h-6 w-6 text-blue-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">In Progress</p>
            <p class="text-3xl font-bold text-gray-900">{{ inProgressAudits.length }}</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-full">
            <PlayIcon class="h-6 w-6 text-yellow-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Upcoming</p>
            <p class="text-3xl font-bold text-gray-900">{{ upcomingAudits.length }}</p>
          </div>
          <div class="p-3 bg-green-100 rounded-full">
            <ClockIcon class="h-6 w-6 text-green-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Avg. Progress</p>
            <p class="text-3xl font-bold text-gray-900">{{ averageProgress }}%</p>
          </div>
          <div class="p-3 bg-purple-100 rounded-full">
            <BarChartIcon class="h-6 w-6 text-purple-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar View Toggle -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Audit Schedule</h3>
        <div class="flex items-center space-x-2">
          <Button
            :variant="viewMode === 'list' ? 'solid' : 'outline'"
            size="sm"
            @click="viewMode = 'list'"
          >
            <ListIcon class="h-4 w-4 mr-2" />
            List View
          </Button>
          <Button
            :variant="viewMode === 'calendar' ? 'solid' : 'outline'"
            size="sm"
            @click="viewMode = 'calendar'"
          >
            <CalendarIcon class="h-4 w-4 mr-2" />
            Calendar View
          </Button>
        </div>
      </div>

      <!-- List View -->
      <div v-if="viewMode === 'list'" class="mt-6">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Calendar ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Audit Universe
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Start Date
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Progress
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="item in auditCalendar"
                :key="item.name"
                class="hover:bg-gray-50"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ item.calendar_id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ getUniverseName(item.audit_universe) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ item.audit_type }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <Badge
                    :variant="getStatusVariant(item.status)"
                    size="sm"
                  >
                    {{ item.status }}
                  </Badge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(item.planned_start_date) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        class="bg-blue-600 h-2 rounded-full"
                        :style="{ width: `${item.progress_percentage || 0}%` }"
                      ></div>
                    </div>
                    <span class="text-sm text-gray-500">{{ item.progress_percentage || 0 }}%</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="viewCalendarItem(item)"
                    >
                      <EyeIcon class="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="editCalendarItem(item)"
                    >
                      <EditIcon class="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="updateStatus(item, 'In Progress')"
                      v-if="item.status === 'Planned'"
                    >
                      <PlayIcon class="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      @click="updateStatus(item, 'Completed')"
                      v-if="item.status === 'In Progress'"
                    >
                      <CheckCircleIcon class="h-4 w-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Calendar View -->
      <div v-if="viewMode === 'calendar'" class="mt-6">
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
              {{ formatMonthYear(currentMonth) }}
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
            @click="goToToday"
          >
            Today
          </Button>
        </div>

        <!-- Calendar Grid -->
        <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <!-- Days of Week Header -->
          <div class="grid grid-cols-7 bg-gray-50 border-b border-gray-200">
            <div
              v-for="day in daysOfWeek"
              :key="day"
              class="px-4 py-3 text-center text-sm font-medium text-gray-500 border-r border-gray-200 last:border-r-0"
            >
              {{ day }}
            </div>
          </div>

          <!-- Calendar Days -->
          <div class="grid grid-cols-7">
            <!-- Empty cells for days before the first day of the month -->
            <div
              v-for="emptyDay in calendarDays[0].emptyDays"
              :key="`empty-${emptyDay}`"
              class="min-h-[120px] bg-gray-50 border-r border-b border-gray-200 last:border-r-0"
            ></div>

            <!-- Calendar day cells -->
            <div
              v-for="day in calendarDays"
              :key="day.date"
              class="min-h-[120px] border-r border-b border-gray-200 last:border-r-0 p-2 hover:bg-gray-50 cursor-pointer transition-colors"
              :class="{
                'bg-blue-50': isToday(day.date),
                'bg-gray-100': !isCurrentMonth(day.date)
              }"
              @click="selectDate(day.date)"
            >
              <div class="flex items-center justify-between mb-1">
                <span
                  class="text-sm font-medium"
                  :class="{
                    'text-blue-600': isToday(day.date),
                    'text-gray-400': !isCurrentMonth(day.date),
                    'text-gray-900': isCurrentMonth(day.date) && !isToday(day.date)
                  }"
                >
                  {{ formatDay(day.date) }}
                </span>
                <div v-if="getEventsForDate(day.date).length > 0" class="flex space-x-1">
                  <div
                    v-for="event in getEventsForDate(day.date).slice(0, 3)"
                    :key="event.name"
                    class="w-2 h-2 rounded-full"
                    :class="getEventColor(event.status)"
                  ></div>
                  <span
                    v-if="getEventsForDate(day.date).length > 3"
                    class="text-xs text-gray-500"
                  >
                    +{{ getEventsForDate(day.date).length - 3 }}
                  </span>
                </div>
              </div>

              <!-- Events for this day -->
              <div class="space-y-1">
                <div
                  v-for="event in getEventsForDate(day.date).slice(0, 2)"
                  :key="event.name"
                  class="text-xs p-1 rounded truncate"
                  :class="getEventBackground(event.status)"
                  @click.stop="viewCalendarItem(event)"
                >
                  <div class="font-medium truncate">{{ event.calendar_id }}</div>
                  <div class="text-gray-600 truncate">{{ event.audit_type }}</div>
                </div>
                <div
                  v-if="getEventsForDate(day.date).length > 2"
                  class="text-xs text-gray-500 text-center py-1"
                >
                  +{{ getEventsForDate(day.date).length - 2 }} more
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Selected Date Details -->
        <div v-if="selectedDate" class="mt-6 bg-white border border-gray-200 rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h4 class="text-lg font-medium text-gray-900">
              Events for {{ formatFullDate(selectedDate) }}
            </h4>
            <Button
              variant="outline"
              size="sm"
              @click="selectedDate = null"
            >
              <XIcon class="h-4 w-4" />
            </Button>
          </div>

          <div v-if="getEventsForDate(selectedDate).length === 0" class="text-center py-8 text-gray-500">
            <CalendarIcon class="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No audit events scheduled for this date</p>
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="event in getEventsForDate(selectedDate)"
              :key="event.name"
              class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <h5 class="text-sm font-medium text-gray-900">{{ event.calendar_id }}</h5>
                    <Badge
                      :variant="getStatusVariant(event.status)"
                      size="sm"
                    >
                      {{ event.status }}
                    </Badge>
                  </div>
                  <div class="grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div>
                      <span class="font-medium">Universe:</span> {{ getUniverseName(event.audit_universe) }}
                    </div>
                    <div>
                      <span class="font-medium">Type:</span> {{ event.audit_type }}
                    </div>
                    <div>
                      <span class="font-medium">Lead Auditor:</span> {{ event.lead_auditor || 'Unassigned' }}
                    </div>
                    <div>
                      <span class="font-medium">Progress:</span> {{ event.progress_percentage || 0 }}%
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-2 ml-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="viewCalendarItem(event)"
                  >
                    <EyeIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="editCalendarItem(event)"
                  >
                    <EditIcon class="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Calendar Modal -->
    <Dialog
      v-model="showCreateModal"
      :title="editingItem ? 'Edit Audit Schedule' : 'Schedule New Audit'"
      size="4xl"
    >
      <template #body>
        <div class="space-y-6">
          <!-- Basic Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormControl
              v-model="calendarForm.calendar_id"
              label="Calendar ID"
              placeholder="Enter calendar ID"
              :required="true"
            />
            <Select
              v-model="calendarForm.audit_universe"
              :options="universeOptions"
              label="Audit Universe"
              placeholder="Select universe"
              :required="true"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Select
              v-model="calendarForm.audit_type"
              :options="auditTypeOptions"
              label="Audit Type"
              placeholder="Select type"
              :required="true"
            />
            <Select
              v-model="calendarForm.status"
              :options="statusOptions"
              label="Status"
              placeholder="Select status"
            />
            <Select
              v-model="calendarForm.annual_audit_plan"
              :options="planOptions"
              label="Annual Audit Plan"
              placeholder="Select plan"
            />
          </div>

          <!-- Dates and Resources -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormControl
              v-model="calendarForm.planned_start_date"
              type="date"
              label="Planned Start Date"
              :required="true"
            />
            <FormControl
              v-model="calendarForm.planned_end_date"
              type="date"
              label="Planned End Date"
              :required="true"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <FormControl
              v-model="calendarForm.lead_auditor"
              label="Lead Auditor"
              placeholder="Select lead auditor"
              :required="true"
            />
            <FormControl
              v-model="calendarForm.estimated_days"
              type="number"
              label="Estimated Days"
              placeholder="0"
            />
            <FormControl
              v-model="calendarForm.progress_percentage"
              type="number"
              label="Progress %"
              placeholder="0"
              min="0"
              max="100"
            />
          </div>

          <!-- Objectives and Scope -->
          <div class="space-y-4">
            <FormControl
              v-model="calendarForm.objectives"
              type="textarea"
              label="Objectives"
              placeholder="Enter audit objectives"
              rows="3"
            />
            <FormControl
              v-model="calendarForm.scope"
              type="textarea"
              label="Scope"
              placeholder="Define audit scope"
              rows="3"
            />
            <FormControl
              v-model="calendarForm.key_risks"
              type="textarea"
              label="Key Risks"
              placeholder="Identify key risks"
              rows="3"
            />
          </div>
        </div>
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
  </div>
</template>

<script setup>
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
import { Badge, Button, Dialog, FormControl, Select } from "frappe-ui"
import {
	BarChartIcon,
	CalendarIcon,
	CheckCircleIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	ClockIcon,
	EditIcon,
	EyeIcon,
	ListIcon,
	PlayIcon,
	PlusIcon,
	RefreshCwIcon,
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

// Calendar computed properties
const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

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
		events: getEventsForDate(date),
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

// Lifecycle
onMounted(async () => {
	await refreshData()
})
</script>