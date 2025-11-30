<template>
  <div class="test-execution-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <PlayCircle class="title-icon" />
          Test Execution
        </h1>
        <p class="page-description">
          Execute and monitor audit tests with real-time results and detailed reporting
        </p>
      </div>
    </div>

    <!-- Filters Component -->
    <ExecutionFilters
      :filters="filters"
      @update:filters="handleFilterUpdate"
      @refresh="refreshExecutions"
      @create="showFormDialog = true"
    />

    <!-- Stats Component -->
    <div class="my-6">
      <ExecutionStats
        :executions="executions"
        :activeFilter="filters.status"
        @filter="handleStatsFilter"
        @select="viewExecutionDetails"
      />
    </div>

    <!-- Executions Table -->
    <div class="executions-section">
      <div class="table-container">
        <table class="executions-table">
          <thead>
            <tr>
              <th class="checkbox-column">
                <Checkbox
                  v-model="selectAll"
                  @change="toggleSelectAll"
                />
              </th>
              <th>Execution ID</th>
              <th>Test Name</th>
              <th>Category</th>
              <th>Status</th>
              <th>Start Time</th>
              <th>Duration</th>
              <th>Executed By</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="execution in executions"
              :key="execution.name"
              :class="{ 'selected-row': selectedExecutions.includes(execution.name) }"
            >
              <td class="checkbox-column">
                <Checkbox
                  v-model="selectedExecutions"
                  :value="execution.name"
                />
              </td>
              <td class="execution-id">{{ execution.execution_id }}</td>
              <td class="test-name">{{ execution.execution_name }}</td>
              <td class="category">
                <Badge :variant="getCategoryVariant(execution.execution_type)">
                  {{ execution.execution_type }}
                </Badge>
              </td>
              <td class="status">
                <Badge :variant="getStatusVariant(execution.status)">
                  {{ execution.status }}
                </Badge>
              </td>
              <td class="start-time">{{ formatDateTime(execution.actual_start_date) }}</td>
              <td class="duration">{{ calculateDuration(execution) }}</td>
              <td class="executed-by">{{ execution.created_by }}</td>
              <td class="actions">
                <div class="action-buttons">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="viewExecutionDetails(execution)"
                    title="View Details"
                  >
                    <Eye />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="downloadResults(execution)"
                    :disabled="execution.status !== 'Completed'"
                    title="Download Results"
                  >
                    <Download />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="cancelExecution(execution)"
                    :disabled="execution.status !== 'Running'"
                    title="Cancel Execution"
                  >
                    <X />
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="!executions.length && !loading" class="empty-state">
          <FileX class="empty-icon" />
          <h3>No Test Executions Found</h3>
          <p>Execute some tests to see results here.</p>
          <Button variant="solid" @click="showExecuteDialog = true">
            <Play />
            Execute Tests
          </Button>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <Loader2 class="loading-icon" />
          <p>Loading test executions...</p>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="executions.length" class="pagination-section">
        <div class="pagination-info">
          Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalCount) }} of {{ totalCount }} executions
        </div>
        <div class="pagination-controls">
          <Button
            variant="outline"
            size="sm"
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
          >
            <ChevronLeft />
            Previous
          </Button>
          <span class="page-indicator">Page {{ currentPage }} of {{ totalPages }}</span>
          <Button
            variant="outline"
            size="sm"
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
          >
            Next
            <ChevronRight />
          </Button>
        </div>
      </div>
    </div>

    <!-- Execution Details Dialog -->
    <Dialog v-model="showDetailsDialog" size="large">
      <template #title>
        <Eye />
        Execution Details: {{ selectedExecution?.execution_id }}
      </template>

      <div v-if="selectedExecution" class="execution-details">
        <div class="details-grid">
          <div class="detail-section">
            <h4>Execution Information</h4>
            <div class="detail-rows">
              <div class="detail-row">
                <span class="detail-label">Test Name:</span>
                <span class="detail-value">{{ selectedExecution.execution_name }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Category:</span>
                <span class="detail-value">{{ selectedExecution.execution_type }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Status:</span>
                <Badge :variant="getStatusVariant(selectedExecution.status)">
                  {{ selectedExecution.status }}
                </Badge>
              </div>
              <div class="detail-row">
                <span class="detail-label">Start Time:</span>
                <span class="detail-value">{{ formatDateTime(selectedExecution.actual_start_date) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">End Time:</span>
                <span class="detail-value">{{ formatDateTime(selectedExecution.actual_end_date) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Duration:</span>
                <span class="detail-value">{{ calculateDuration(selectedExecution) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Executed By:</span>
                <span class="detail-value">{{ selectedExecution.created_by }}</span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4>Test Results</h4>
            <div v-if="executionResults.length" class="results-list">
              <div
                v-for="result in executionResults"
                :key="result.name"
                class="result-item"
              >
                <div class="result-header">
                  <Badge :variant="getResultVariant(result.status)">
                    {{ result.status }}
                  </Badge>
                  <span class="result-description">{{ result.description }}</span>
                </div>
                <div v-if="result.error_message" class="result-error">
                  {{ result.error_message }}
                </div>
              </div>
            </div>
            <div v-else class="no-results">
              <FileX />
              <span>No results available</span>
            </div>
          </div>
        </div>
      </div>

      <template #actions>
        <Button variant="outline" @click="showDetailsDialog = false">
          Close
        </Button>
        <Button
          variant="solid"
          @click="downloadDetailedResults"
          :disabled="!executionResults.length"
        >
          <Download />
          Download Results
        </Button>
      </template>
    </Dialog>

    <!-- Test Execution Form Dialog -->
    <TestExecutionForm
      :show="showFormDialog"
      :execution="selectedExecutionForEdit"
      @update:show="showFormDialog = $event"
      @saved="handleExecutionSaved"
    />
  </div>
</template>

<script setup>
import ExecutionFilters from "@/components/execution/ExecutionFilters.vue"
import ExecutionStats from "@/components/execution/ExecutionStats.vue"
import TestExecutionForm from "@/components/execution/TestExecutionForm.vue"
import { useAuditStore } from "@/stores/audit"
import { useTestExecutionStore } from "@/stores/testExecution"
import { Badge, Button, Checkbox, Dialog, FormControl, Input } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	BarChart3,
	CheckCircle,
	ChevronLeft,
	ChevronRight,
	Download,
	Eye,
	FileX,
	Loader2,
	Play,
	PlayCircle,
	RefreshCw,
	Search,
	X,
	XCircle,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"

// Utility functions
const debounce = (func, delay) => {
	let timeoutId
	return (...args) => {
		clearTimeout(timeoutId)
		timeoutId = setTimeout(() => func.apply(null, args), delay)
	}
}

// Filter options
const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Running", value: "Running" },
	{ label: "Completed", value: "Completed" },
	{ label: "Failed", value: "Failed" },
	{ label: "Cancelled", value: "Cancelled" },
]

const categoryOptions = [
	{ label: "All Categories", value: "" },
	{ label: "Financial Controls", value: "Financial Controls" },
	{ label: "Operational Controls", value: "Operational Controls" },
	{ label: "Compliance", value: "Compliance" },
	{ label: "Data Integrity", value: "Data Integrity" },
	{ label: "Performance", value: "Performance" },
]

const executionTypeOptions = [
	{ label: "Manual", value: "Manual" },
	{ label: "Scheduled", value: "Scheduled" },
	{ label: "Batch", value: "Batch" },
]

const priorityOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Normal", value: "Normal" },
	{ label: "High", value: "High" },
	{ label: "Critical", value: "Critical" },
]

// Initialize stores
const testExecutionStore = useTestExecutionStore()
const auditStore = useAuditStore()

// Reactive data
const selectedExecutions = ref([])
const selectedTests = ref([])
const selectAll = ref(false)
const executing = ref(false)
const showExecuteDialog = ref(false)
const showDetailsDialog = ref(false)
const showFormDialog = ref(false)
const selectedExecution = ref(null)
const selectedExecutionForEdit = ref(null)
const executionResults = ref([])

// Filters
const filters = ref({
	status: "",
	search: "",
	testLibrary: "",
	executionType: "",
	priority: "",
	dateFrom: "",
	dateTo: "",
})

// Execution options
const executionOptions = ref({
	type: "Manual",
	scheduleTime: "",
	priority: "Normal",
})

// Pagination
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const totalPages = ref(0)

// Statistics computed from store
const stats = computed(() => ({
	running: testExecutionStore.executionStatuses.running,
	completed: testExecutionStore.executionStatuses.completed,
	failed: testExecutionStore.executionStatuses.failed,
	total: testExecutionStore.testExecutions.length,
}))

// Remove old API resources - now using store methods

// Computed properties
const executions = computed(() => {
	let filteredExecutions = testExecutionStore.testExecutions

	// Apply filters
	if (filters.value.status) {
		filteredExecutions = filteredExecutions.filter(
			(e) => e.status === filters.value.status,
		)
	}

	if (filters.value.category) {
		filteredExecutions = filteredExecutions.filter(
			(e) => e.execution_type === filters.value.category,
		)
	}

	if (filters.value.search) {
		const search = filters.value.search.toLowerCase()
		filteredExecutions = filteredExecutions.filter(
			(e) =>
				e.execution_name?.toLowerCase().includes(search) ||
				e.execution_id?.toLowerCase().includes(search),
		)
	}

	return filteredExecutions
})

const availableTests = computed(() => {
	return testExecutionStore.testLibraryTests
})

const selectedTestsData = computed(() => {
	return availableTests.value.filter((test) =>
		selectedTests.value.includes(test.name),
	)
})

const loading = computed(() => testExecutionStore.loading)

// Methods
const loadExecutions = async () => {
	await testExecutionStore.fetchTestExecutions()
}

const loadAvailableTests = async () => {
	// This would be implemented when test library store is available
	console.log("Loading available tests...")
}

// Filter handling methods
const handleFilterUpdate = (newFilters) => {
	Object.assign(filters.value, newFilters)
	currentPage.value = 1
	loadExecutions()
}

const handleStatsFilter = (filterKey, filterValue) => {
	if (filterKey && filterValue) {
		filters.value[filterKey] = filterValue
		currentPage.value = 1
		loadExecutions()
	}
}

const applyFilters = () => {
	currentPage.value = 1
	loadExecutions()
}

const debouncedSearch = debounce(applyFilters, 300)

// Execution form handlers
const handleExecutionSaved = async (executionData) => {
	try {
		if (selectedExecutionForEdit.value?.name) {
			await testExecutionStore.updateTestExecution(
				selectedExecutionForEdit.value.name,
				executionData,
			)
		} else {
			await testExecutionStore.createTestExecution(executionData)
		}
		showFormDialog.value = false
		selectedExecutionForEdit.value = null
		await loadExecutions()
	} catch (error) {
		console.error("Failed to save execution:", error)
	}
}

const editExecution = (execution) => {
	selectedExecutionForEdit.value = execution
	showFormDialog.value = true
}

const toggleSelectAll = () => {
	if (selectAll.value) {
		selectedExecutions.value = executions.value.map((e) => e.name)
	} else {
		selectedExecutions.value = []
	}
}

const toggleTestSelection = (testName) => {
	const index = selectedTests.value.indexOf(testName)
	if (index > -1) {
		selectedTests.value.splice(index, 1)
	} else {
		selectedTests.value.push(testName)
	}
}

const executeSelectedTests = async () => {
	if (!selectedTests.value.length) return

	executing.value = true

	try {
		// Create execution records for selected tests
		for (const testName of selectedTests.value) {
			const executionData = {
				execution_name: `${testName} - ${new Date().toLocaleDateString()}`,
				test_library_reference: testName,
				priority: executionOptions.value.priority,
				execution_type: executionOptions.value.type,
				status: "Pending",
			}
			await testExecutionStore.createTestExecution(executionData)
		}
		showExecuteDialog.value = false
		selectedTests.value = []
	} catch (error) {
		console.error("Failed to execute tests:", error)
	} finally {
		executing.value = false
	}
}

const viewExecutionDetails = async (execution) => {
	selectedExecution.value = execution
	showDetailsDialog.value = true

	// Load execution results
	try {
		const results = await testExecutionStore.fetchTestResults(execution.name)
		executionResults.value = results

		// Also load execution logs
		await testExecutionStore.fetchExecutionLogs(execution.name)
	} catch (error) {
		console.error("Failed to load execution results:", error)
		executionResults.value = []
	}
}

const cancelExecution = async (execution) => {
	try {
		await testExecutionStore.stopTestExecution(execution.name)
	} catch (error) {
		console.error("Failed to cancel execution:", error)
	}
}

const downloadResults = async (execution) => {
	try {
		const result = await testExecutionStore.exportTestResults(
			execution.name,
			"excel",
		)
		// Handle download result
		if (result.download_url) {
			window.open(result.download_url, "_blank")
		}
	} catch (error) {
		console.error("Failed to download results:", error)
	}
}

const downloadDetailedResults = () => {
	// Implementation for downloading detailed results
	console.log("Download detailed results")
}

const refreshExecutions = async () => {
	await loadExecutions()
}

const changePage = (page) => {
	currentPage.value = page
	loadExecutions()
}

// Utility methods
const getStatusVariant = (status) => {
	const variants = {
		Pending: "secondary",
		Running: "info",
		Completed: "success",
		Failed: "danger",
		Cancelled: "secondary",
	}
	return variants[status] || "secondary"
}

const getCategoryVariant = (category) => {
	const variants = {
		"Financial Controls": "blue",
		"Operational Controls": "green",
		Compliance: "orange",
		"Data Integrity": "purple",
		Performance: "cyan",
	}
	return variants[category] || "gray"
}

const getResultVariant = (status) => {
	const variants = {
		Passed: "green",
		Failed: "red",
		Warning: "orange",
	}
	return variants[status] || "gray"
}

const formatDateTime = (dateString) => {
	if (!dateString) return "N/A"
	return new Date(dateString).toLocaleString()
}

const calculateDuration = (execution) => {
	if (!execution.actual_start_date) return "N/A"

	const start = new Date(execution.actual_start_date)
	const end = execution.actual_end_date
		? new Date(execution.actual_end_date)
		: new Date()

	const diffMs = end - start
	const diffMins = Math.floor(diffMs / 60000)
	const diffSecs = Math.floor((diffMs % 60000) / 1000)

	if (diffMins > 0) {
		return `${diffMins}m ${diffSecs}s`
	} else {
		return `${diffSecs}s`
	}
}

// Watchers
watch(selectedExecutions, () => {
	selectAll.value =
		selectedExecutions.value.length === executions.value.length &&
		executions.value.length > 0
})

// Lifecycle
onMounted(async () => {
	await Promise.all([loadExecutions(), loadAvailableTests()])
})
</script>

<style scoped>
.test-execution-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.header-content h1 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.title-icon {
  color: var(--primary-color);
}

.page-description {
  color: var(--text-muted);
  margin: 0.5rem 0 0 0;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.filters-section {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
}

.date-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-range input {
  flex: 1;
}

.date-separator {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.stats-section {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-icon.running {
  background: #dbeafe;
  color: #2563eb;
}

.stat-icon.completed {
  background: #dcfce7;
  color: #16a34a;
}

.stat-icon.failed {
  background: #fee2e2;
  color: #dc2626;
}

.stat-icon.total {
  background: #f3f4f6;
  color: #6b7280;
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

.executions-section {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
}

.executions-table {
  width: 100%;
  border-collapse: collapse;
}

.executions-table th,
.executions-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.executions-table th {
  background: var(--background-color);
  font-weight: 600;
  color: var(--text-color);
  position: sticky;
  top: 0;
  z-index: 10;
}

.checkbox-column {
  width: 3rem;
  text-align: center;
}

.execution-id {
  font-family: monospace;
  font-size: 0.875rem;
}

.test-name {
  font-weight: 500;
}

.category,
.status {
  text-align: center;
}

.start-time,
.duration,
.executed-by {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.actions {
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
}

.selected-row {
  background: var(--primary-light);
}

.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon,
.loading-icon {
  font-size: 3rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: var(--text-muted);
  margin: 0 0 1.5rem 0;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  background: var(--background-color);
}

.pagination-info {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-indicator {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.execute-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.test-selection h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.test-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
}

.test-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.test-item:last-child {
  border-bottom: none;
}

.test-item:hover {
  background: var(--background-color);
}

.test-item.selected {
  background: var(--primary-light);
}

.test-info {
  flex: 1;
}

.test-info .test-name {
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.test-info .test-category {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.execution-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.option-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
}

.execution-details {
  max-height: 600px;
  overflow-y: auto;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.detail-section h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.detail-rows {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-color-2);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 500;
  color: var(--text-color);
  min-width: 120px;
}

.detail-value {
  color: var(--text-muted);
  text-align: right;
  flex: 1;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-item {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  background: var(--background-color);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.result-description {
  flex: 1;
  font-size: 0.875rem;
  color: var(--text-color);
}

.result-error {
  font-size: 0.875rem;
  color: var(--error-color);
  background: var(--error-light);
  padding: 0.5rem;
  border-radius: 0.25rem;
  border-left: 3px solid var(--error-color);
}

.no-results {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-style: italic;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
  }

  .header-actions {
    width: 100%;
    justify-content: stretch;
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .executions-table {
    font-size: 0.875rem;
  }

  .executions-table th,
  .executions-table td {
    padding: 0.5rem;
  }

  .pagination-section {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .execution-options {
    grid-template-columns: 1fr;
  }
}
</style>