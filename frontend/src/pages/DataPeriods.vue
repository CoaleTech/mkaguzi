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
        <Button variant="outline" @click="exportPeriods">
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
    <PeriodStats :stats="stats" />

    <!-- Filters -->
    <PeriodFilters
      v-model:searchQuery="searchQuery"
      v-model:selectedStatus="selectedStatus"
      v-model:selectedPeriodType="selectedPeriodType"
      v-model:selectedFiscalYear="selectedFiscalYear"
      v-model:selectedReconciliationStatus="selectedReconciliationStatus"
    />

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

    <!-- Data Period Form Dialog -->
    <DataPeriodForm
      v-model:show="showFormDialog"
      :period-data="selectedPeriod"
      :is-edit-mode="isEditMode"
      @saved="handlePeriodSaved"
    />
  </div>
</template>

<script setup>
import DataPeriodForm from "@/components/dataperiods/DataPeriodForm.vue"
import PeriodFilters from "@/components/dataperiods/PeriodFilters.vue"
import PeriodStats from "@/components/dataperiods/PeriodStats.vue"
import { useDataPeriodsStore } from "@/stores/dataPeriods"
import { Badge, Button, Input, Select, createResource } from "frappe-ui"
import {
	DownloadIcon,
	EditIcon,
	FileTextIcon,
	PlusIcon,
	SettingsIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

const dataPeriodsStore = useDataPeriodsStore()

// Reactive state
const activeTab = ref("periods")
const periodFilter = ref("")
const fiscalYearFilter = ref("")
const showFormDialog = ref(false)
const isEditMode = ref(false)
const selectedPeriod = ref(null)

// Additional state variables for new functions
const creatingFiscalYear = ref(false)
const creatingPeriodType = ref(false)
const savingSettings = ref(false)
const exporting = ref(false)

// Additional reactive state
const periodSettings = ref({})
const currentFilters = ref({})
const dataPeriods = ref([])
const error = ref(null)

// Utility functions
const showSuccessMessage = (message) => {
	// Using frappe-ui toast or similar
	console.log("Success:", message)
	// You can implement proper toast notification here
}

const showErrorMessage = (message) => {
	console.log("Error:", message)
	// You can implement proper error notification here
}

const generateCSVFromData = (data, columns) => {
	if (!data || !data.length) return ""
	
	const headers = columns.join(",")
	const rows = data.map(row => 
		columns.map(col => `"${row[col] || ''}"`).join(",")
	).join("\n")
	
	return `${headers}\n${rows}`
}

const downloadCSV = (content, filename) => {
	const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
	const link = document.createElement('a')
	const url = URL.createObjectURL(blob)
	link.setAttribute('href', url)
	link.setAttribute('download', filename)
	link.style.visibility = 'hidden'
	document.body.appendChild(link)
	link.click()
	document.body.removeChild(link)
}

// API functions
const loadDataPeriods = async () => {
	loading.value = true
	error.value = null
	try {
		const result = await createResource({
			url: "mkaguzi.api.data_period.get_data_periods",
			params: currentFilters.value
		}).fetch()
		dataPeriods.value = result || []
	} catch (err) {
		error.value = err.message
		showErrorMessage("Failed to load data periods")
	} finally {
		loading.value = false
	}
}

const loadPeriodTypes = async () => {
	try {
		const result = await createResource({
			url: "mkaguzi.api.data_period.get_period_types"
		}).fetch()
		periodTypes.value = result || []
	} catch (err) {
		showErrorMessage("Failed to load period types")
	}
}

// Store bindings
const loading = computed(() => dataPeriodsStore.loading)
const filteredPeriods = computed(() => dataPeriodsStore.filteredPeriods)
const stats = computed(() => dataPeriodsStore.stats)

const searchQuery = computed({
	get: () => dataPeriodsStore.searchQuery,
	set: (value) => (dataPeriodsStore.searchQuery = value),
})

const selectedStatus = computed({
	get: () => dataPeriodsStore.filters.status,
	set: (value) => (dataPeriodsStore.filters.status = value),
})

const selectedPeriodType = computed({
	get: () => dataPeriodsStore.filters.periodType,
	set: (value) => (dataPeriodsStore.filters.periodType = value),
})

const selectedFiscalYear = computed({
	get: () => dataPeriodsStore.filters.fiscalYear,
	set: (value) => (dataPeriodsStore.filters.fiscalYear = value),
})

const selectedReconciliationStatus = computed({
	get: () => dataPeriodsStore.filters.reconciliationStatus,
	set: (value) => (dataPeriodsStore.filters.reconciliationStatus = value),
})

// Local data for tabs
const periods = computed(() => dataPeriodsStore.periods)

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

// Methods
const fetchData = async () => {
	await dataPeriodsStore.fetchPeriods()
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
	selectedPeriod.value = null
	isEditMode.value = false
	showFormDialog.value = true
}

const editPeriod = async (period) => {
	try {
		selectedPeriod.value = await dataPeriodsStore.getPeriodDetails(period.name)
		isEditMode.value = true
		showFormDialog.value = true
	} catch (error) {
		console.error("Error fetching period details:", error)
	}
}

const handlePeriodSaved = async () => {
	showFormDialog.value = false
	await fetchData()
}

const closePeriod = async (period) => {
	try {
		await dataPeriodsStore.closePeriod(period.name)
	} catch (error) {
		console.error("Error closing period:", error)
	}
}

const reopenPeriod = async (period) => {
	try {
		await dataPeriodsStore.reopenPeriod(period.name)
	} catch (error) {
		console.error("Error reopening period:", error)
	}
}

const createFiscalYear = async () => {
	creatingFiscalYear.value = true
	try {
		// This will be called from a dialog, so we need to implement the dialog first
		// For now, just show a placeholder
		showSuccessMessage("Fiscal year creation dialog would open here")
	} catch (error) {
		showErrorMessage("Failed to open fiscal year creation dialog")
	} finally {
		creatingFiscalYear.value = false
	}
}

const createNewPeriodType = () => {
	// This will be called from a dialog, so we need to implement the dialog first
	// For now, just show a placeholder
	showSuccessMessage("Period type creation dialog would open here")
}

const editPeriodType = (type) => {
	// TODO: Implement period type editing
	console.log("Edit period type:", type.name)
}

const saveSettings = async (settingsData) => {
	savingSettings.value = true
	try {
		await createResource({
			url: "mkaguzi.api.data_period.save_period_settings",
			params: { settings: settingsData }
		}).fetch()
		periodSettings.value = { ...periodSettings.value, ...settingsData }
		showSuccessMessage("Settings saved successfully")
	} catch (error) {
		showErrorMessage("Failed to save settings")
	} finally {
		savingSettings.value = false
	}
}

const exportPeriods = async () => {
	exporting.value = true
	try {
		const result = await createResource({
			url: "mkaguzi.api.data_period.export_data_periods",
			params: { filters: currentFilters.value }
		}).fetch()
		const csvContent = generateCSVFromData(result.data, result.columns)
		downloadCSV(csvContent, `data-periods-${new Date().toISOString().split('T')[0]}.csv`)
		showSuccessMessage(`Exported ${result.data.length} data periods`)
	} catch (error) {
		showErrorMessage("Failed to export data periods")
	} finally {
		exporting.value = false
	}
}

// Lifecycle
onMounted(async () => {
	await fetchData()
	await loadDataPeriods()
	await loadPeriodTypes()
})
</script>