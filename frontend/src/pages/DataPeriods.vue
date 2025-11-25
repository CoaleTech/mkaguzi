<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Data Periods</h1>
        <p class="text-gray-600 mt-1">
          Manage fiscal periods, data periods, and period configurations
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export Periods
        </Button>
        <Button @click="createNewPeriod">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Period
        </Button>
      </div>
    </div>

    <!-- Period Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <CalendarIcon class="h-6 w-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Active Periods</p>
            <p class="text-2xl font-bold text-gray-900">{{ activePeriods }}</p>
            <p class="text-xs text-blue-600 mt-1">Current fiscal year</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <CheckCircleIcon class="h-6 w-6 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Closed Periods</p>
            <p class="text-2xl font-bold text-gray-900">{{ closedPeriods }}</p>
            <p class="text-xs text-green-600 mt-1">Ready for audit</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <ClockIcon class="h-6 w-6 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Upcoming Periods</p>
            <p class="text-2xl font-bold text-gray-900">{{ upcomingPeriods }}</p>
            <p class="text-xs text-yellow-600 mt-1">Next 3 months</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 rounded-lg">
            <SettingsIcon class="h-6 w-6 text-purple-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Period Types</p>
            <p class="text-2xl font-bold text-gray-900">{{ periodTypes.length }}</p>
            <p class="text-xs text-purple-600 mt-1">Configured types</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Period Tabs -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="border-b border-gray-200">
        <nav class="flex">
          <button
            @click="activeTab = 'periods'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'periods'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Data Periods
          </button>
          <button
            @click="activeTab = 'fiscal'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'fiscal'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Fiscal Calendar
          </button>
          <button
            @click="activeTab = 'types'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'types'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Period Types
          </button>
          <button
            @click="activeTab = 'settings'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'settings'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Settings
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Data Periods Tab -->
        <div v-if="activeTab === 'periods'">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-medium text-gray-900">Data Periods</h2>
            <div class="flex items-center space-x-3">
              <Select
                v-model="periodFilter"
                :options="periodFilterOptions"
                placeholder="Filter periods"
                class="w-40"
              />
              <Button @click="createNewPeriod">
                <PlusIcon class="h-4 w-4 mr-2" />
                New Period
              </Button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div
              v-for="period in filteredPeriods"
              :key="period.name"
              class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                  <h3 class="text-lg font-medium text-gray-900 mb-1">
                    {{ period.period_name }}
                  </h3>
                  <p class="text-sm text-gray-600 mb-2">
                    {{ period.description || 'Data period configuration' }}
                  </p>
                  <div class="flex items-center space-x-2">
                    <Badge :variant="getPeriodStatusVariant(period.status)">
                      {{ period.status }}
                    </Badge>
                    <Badge :variant="getPeriodTypeVariant(period.period_type)">
                      {{ period.period_type }}
                    </Badge>
                  </div>
                </div>
                <Button variant="ghost" size="sm" @click="editPeriod(period)">
                  <EditIcon class="h-4 w-4" />
                </Button>
              </div>

              <div class="space-y-2 text-sm text-gray-500">
                <div class="flex justify-between">
                  <span>Start Date:</span>
                  <span>{{ formatDate(period.start_date) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>End Date:</span>
                  <span>{{ formatDate(period.end_date) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Fiscal Year:</span>
                  <span>{{ period.fiscal_year }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Company:</span>
                  <span>{{ period.company || 'All' }}</span>
                </div>
              </div>

              <div class="mt-4 flex items-center justify-between">
                <div class="text-xs text-gray-500">
                  Modified: {{ formatDate(period.modified) }}
                </div>
                <div class="flex items-center space-x-2">
                  <Button
                    v-if="period.status === 'Open'"
                    variant="outline"
                    size="sm"
                    @click="closePeriod(period)"
                  >
                    Close
                  </Button>
                  <Button
                    v-if="period.status === 'Closed'"
                    variant="outline"
                    size="sm"
                    @click="reopenPeriod(period)"
                  >
                    Reopen
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Fiscal Calendar Tab -->
        <div v-if="activeTab === 'fiscal'">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-medium text-gray-900">Fiscal Calendar</h2>
            <div class="flex items-center space-x-3">
              <Select
                v-model="fiscalYearFilter"
                :options="fiscalYearOptions"
                placeholder="Select year"
                class="w-32"
              />
              <Button @click="createFiscalYear">
                <PlusIcon class="h-4 w-4 mr-2" />
                New Fiscal Year
              </Button>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Calendar View -->
            <div class="bg-white border border-gray-200 rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Period Calendar</h3>
              <div class="space-y-4">
                <div v-for="month in calendarMonths" :key="month.name" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ month.name }}</p>
                    <p class="text-xs text-gray-500">{{ month.periods }} periods</p>
                  </div>
                  <div class="flex items-center space-x-2">
                    <div :class="['w-3 h-3 rounded-full', month.status === 'complete' ? 'bg-green-500' : month.status === 'partial' ? 'bg-yellow-500' : 'bg-gray-300']"></div>
                    <span class="text-xs text-gray-500">{{ month.status }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Fiscal Year Summary -->
            <div class="bg-white border border-gray-200 rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Fiscal Year Summary</h3>
              <div class="space-y-4">
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600">Total Periods:</span>
                  <span class="text-sm font-medium">{{ fiscalYearSummary.totalPeriods }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600">Open Periods:</span>
                  <span class="text-sm font-medium">{{ fiscalYearSummary.openPeriods }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600">Closed Periods:</span>
                  <span class="text-sm font-medium">{{ fiscalYearSummary.closedPeriods }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600">Companies:</span>
                  <span class="text-sm font-medium">{{ fiscalYearSummary.companies }}</span>
                </div>
              </div>

              <div class="mt-6">
                <h4 class="text-sm font-medium text-gray-900 mb-2">Quick Actions</h4>
                <div class="space-y-2">
                  <Button variant="outline" size="sm" class="w-full justify-start">
                    <FileTextIcon class="h-4 w-4 mr-2" />
                    Generate Period Report
                  </Button>
                  <Button variant="outline" size="sm" class="w-full justify-start">
                    <SettingsIcon class="h-4 w-4 mr-2" />
                    Configure Auto-close
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Period Types Tab -->
        <div v-if="activeTab === 'types'">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-medium text-gray-900">Period Types</h2>
            <Button @click="createNewPeriodType">
              <PlusIcon class="h-4 w-4 mr-2" />
              New Type
            </Button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              v-for="type in periodTypes"
              :key="type.name"
              class="bg-white border border-gray-200 rounded-lg p-6"
            >
              <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                  <h3 class="text-lg font-medium text-gray-900 mb-1">
                    {{ type.period_type_name }}
                  </h3>
                  <p class="text-sm text-gray-600 mb-2">
                    {{ type.description || 'Period type configuration' }}
                  </p>
                  <div class="flex items-center space-x-2">
                    <Badge :variant="type.is_active ? 'success' : 'secondary'">
                      {{ type.is_active ? 'Active' : 'Inactive' }}
                    </Badge>
                    <Badge :variant="type.is_default ? 'info' : 'secondary'">
                      {{ type.is_default ? 'Default' : 'Custom' }}
                    </Badge>
                  </div>
                </div>
                <Button variant="ghost" size="sm" @click="editPeriodType(type)">
                  <EditIcon class="h-4 w-4" />
                </Button>
              </div>

              <div class="space-y-2 text-sm text-gray-500">
                <div class="flex justify-between">
                  <span>Frequency:</span>
                  <span>{{ type.frequency }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Duration (days):</span>
                  <span>{{ type.duration_days }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Auto-close:</span>
                  <span>{{ type.auto_close ? 'Yes' : 'No' }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Carry Forward:</span>
                  <span>{{ type.carry_forward ? 'Yes' : 'No' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Settings Tab -->
        <div v-if="activeTab === 'settings'">
          <div class="space-y-6">
            <h2 class="text-lg font-medium text-gray-900">Period Management Settings</h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- General Settings -->
              <div class="bg-white border border-gray-200 rounded-lg p-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">General Settings</h3>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Default Fiscal Year Start
                    </label>
                    <Input
                      v-model="settings.defaultFiscalStart"
                      type="date"
                      class="w-full"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Auto-close Threshold (days)
                    </label>
                    <Input
                      v-model="settings.autoCloseThreshold"
                      type="number"
                      class="w-full"
                    />
                  </div>
                  <div class="flex items-center">
                    <input
                      id="allowOverlap"
                      v-model="settings.allowPeriodOverlap"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label for="allowOverlap" class="ml-2 block text-sm text-gray-900">
                      Allow period overlap
                    </label>
                  </div>
                </div>
              </div>

              <!-- Notification Settings -->
              <div class="bg-white border border-gray-200 rounded-lg p-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Notifications</h3>
                <div class="space-y-4">
                  <div class="flex items-center">
                    <input
                      id="notifyPeriodClose"
                      v-model="settings.notifyOnPeriodClose"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label for="notifyPeriodClose" class="ml-2 block text-sm text-gray-900">
                      Notify on period close
                    </label>
                  </div>
                  <div class="flex items-center">
                    <input
                      id="notifyPeriodOpen"
                      v-model="settings.notifyOnPeriodOpen"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label for="notifyPeriodOpen" class="ml-2 block text-sm text-gray-900">
                      Notify on period open
                    </label>
                  </div>
                  <div class="flex items-center">
                    <input
                      id="notifyUpcoming"
                      v-model="settings.notifyUpcomingPeriods"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label for="notifyUpcoming" class="ml-2 block text-sm text-gray-900">
                      Notify upcoming periods
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex justify-end">
              <Button @click="saveSettings">
                Save Settings
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useDataStore } from "@/stores/data"
import { Badge, Button, Input, Select } from "frappe-ui"
import {
	CalendarIcon,
	CheckCircleIcon,
	ClockIcon,
	DownloadIcon,
	EditIcon,
	FileTextIcon,
	PlusIcon,
	SettingsIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const dataStore = useDataStore()

// Reactive state
const activeTab = ref("periods")
const periodFilter = ref("")
const fiscalYearFilter = ref("")
const loading = ref(false)

// Mock data for demonstration
const activePeriods = ref(12)
const closedPeriods = ref(24)
const upcomingPeriods = ref(3)

const periods = ref([
	{
		name: "period_1",
		period_name: "Q1 2024",
		description: "First quarter of fiscal year 2024",
		status: "Open",
		period_type: "Quarterly",
		start_date: "2024-01-01",
		end_date: "2024-03-31",
		fiscal_year: "2024",
		company: "Main Company",
		modified: new Date().toISOString(),
	},
	{
		name: "period_2",
		period_name: "Q2 2024",
		description: "Second quarter of fiscal year 2024",
		status: "Open",
		period_type: "Quarterly",
		start_date: "2024-04-01",
		end_date: "2024-06-30",
		fiscal_year: "2024",
		company: "Main Company",
		modified: new Date(Date.now() - 86400000).toISOString(),
	},
	{
		name: "period_3",
		period_name: "Q4 2023",
		description: "Fourth quarter of fiscal year 2023",
		status: "Closed",
		period_type: "Quarterly",
		start_date: "2023-10-01",
		end_date: "2023-12-31",
		fiscal_year: "2023",
		company: "Main Company",
		modified: new Date(Date.now() - 172800000).toISOString(),
	},
])

const periodTypes = ref([
	{
		name: "type_1",
		period_type_name: "Monthly",
		description: "Standard monthly accounting periods",
		is_active: true,
		is_default: false,
		frequency: "Monthly",
		duration_days: 30,
		auto_close: true,
		carry_forward: true,
	},
	{
		name: "type_2",
		period_type_name: "Quarterly",
		description: "Quarterly financial reporting periods",
		is_active: true,
		is_default: true,
		frequency: "Quarterly",
		duration_days: 91,
		auto_close: false,
		carry_forward: true,
	},
	{
		name: "type_3",
		period_type_name: "Annually",
		description: "Annual fiscal year periods",
		is_active: true,
		is_default: false,
		frequency: "Annually",
		duration_days: 365,
		auto_close: false,
		carry_forward: false,
	},
])

const calendarMonths = ref([
	{ name: "January", periods: 1, status: "complete" },
	{ name: "February", periods: 1, status: "complete" },
	{ name: "March", periods: 1, status: "complete" },
	{ name: "April", periods: 1, status: "partial" },
	{ name: "May", periods: 1, status: "pending" },
	{ name: "June", periods: 1, status: "pending" },
	{ name: "July", periods: 0, status: "empty" },
	{ name: "August", periods: 0, status: "empty" },
	{ name: "September", periods: 0, status: "empty" },
	{ name: "October", periods: 0, status: "empty" },
	{ name: "November", periods: 0, status: "empty" },
	{ name: "December", periods: 0, status: "empty" },
])

const fiscalYearSummary = ref({
	totalPeriods: 12,
	openPeriods: 3,
	closedPeriods: 9,
	companies: 2,
})

const settings = ref({
	defaultFiscalStart: "2024-01-01",
	autoCloseThreshold: 30,
	allowPeriodOverlap: false,
	notifyOnPeriodClose: true,
	notifyOnPeriodOpen: false,
	notifyUpcomingPeriods: true,
})

// Computed properties
const periodFilterOptions = [
	{ label: "All Periods", value: "" },
	{ label: "Open", value: "Open" },
	{ label: "Closed", value: "Closed" },
	{ label: "Upcoming", value: "Upcoming" },
]

const fiscalYearOptions = [
	{ label: "2024", value: "2024" },
	{ label: "2023", value: "2023" },
	{ label: "2022", value: "2022" },
]

const filteredPeriods = computed(() => {
	let filtered = periods.value

	if (periodFilter.value) {
		filtered = filtered.filter((period) => period.status === periodFilter.value)
	}

	if (fiscalYearFilter.value) {
		filtered = filtered.filter(
			(period) => period.fiscal_year === fiscalYearFilter.value,
		)
	}

	return filtered
})

// Methods
const fetchData = async () => {
	loading.value = true
	try {
		// Fetch period-related data from store
		await Promise.all([
			// Add data store methods for periods when implemented
		])
	} catch (error) {
		console.error("Error loading period data:", error)
	} finally {
		loading.value = false
	}
}

const getPeriodStatusVariant = (status) => {
	const variants = {
		Open: "success",
		Closed: "secondary",
		Upcoming: "info",
	}
	return variants[status] || "secondary"
}

const getPeriodTypeVariant = (type) => {
	const variants = {
		Monthly: "info",
		Quarterly: "success",
		Annually: "warning",
		Custom: "secondary",
	}
	return variants[type] || "secondary"
}

const formatDate = (date) => {
	if (!date) return "N/A"
	return new Date(date).toLocaleDateString()
}

const createNewPeriod = () => {
	router.push("/data-periods/period/new")
}

const editPeriod = (period) => {
	router.push(`/data-periods/period/${period.name}/edit`)
}

const closePeriod = (period) => {
	period.status = "Closed"
	// Implement close period logic
}

const reopenPeriod = (period) => {
	period.status = "Open"
	// Implement reopen period logic
}

const createFiscalYear = () => {
	router.push("/data-periods/fiscal-year/new")
}

const createNewPeriodType = () => {
	router.push("/data-periods/period-type/new")
}

const editPeriodType = (type) => {
	router.push(`/data-periods/period-type/${type.name}/edit`)
}

const saveSettings = () => {
	// Implement save settings logic
	console.log("Saving settings:", settings.value)
}

// Lifecycle
onMounted(async () => {
	await fetchData()
})
</script>