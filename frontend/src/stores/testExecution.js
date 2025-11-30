import { createResource } from "frappe-ui"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useTestExecutionStore = defineStore("testExecution", () => {
	// State
	const testExecutions = ref([])
	const testResults = ref([])
	const testParameters = ref([])
	const testThresholds = ref([])
	const executionLogs = ref([])
	const currentExecution = ref(null)
	const loading = ref(false)
	const searchQuery = ref("")

	// Test Library Integration
	const testLibraryTests = ref([])
	const analyticalProcedures = ref([])

	// Filters
	const filters = ref({
		status: "",
		testLibrary: "",
		executionType: "",
		priority: "",
		dateFrom: "",
		dateTo: "",
	})

	// Execution Status Tracking
	const executionStatuses = ref({
		pending: 0,
		running: 0,
		completed: 0,
		failed: 0,
		cancelled: 0,
	})

	// Getters
	const activeExecutions = computed(() => {
		return testExecutions.value.filter(
			(e) =>
				e.execution_status === "Running" || e.execution_status === "Pending",
		)
	})

	const completedExecutions = computed(() => {
		return testExecutions.value.filter(
			(e) => e.execution_status === "Completed",
		)
	})

	const failedExecutions = computed(() => {
		return testExecutions.value.filter((e) => e.execution_status === "Failed")
	})

	const executionsByStatus = computed(() => {
		const grouped = {}
		testExecutions.value.forEach((execution) => {
			const status = execution.execution_status || "Unknown"
			if (!grouped[status]) grouped[status] = []
			grouped[status].push(execution)
		})
		return grouped
	})

	const executionProgress = computed(() => {
		if (!currentExecution.value) return 0
		const total = currentExecution.value.total_tests || 1
		const completed = currentExecution.value.completed_tests || 0
		return Math.round((completed / total) * 100)
	})

	// Filtered executions getter
	const filteredExecutions = computed(() => {
		let result = testExecutions.value

		// Apply search
		if (searchQuery.value) {
			const search = searchQuery.value.toLowerCase()
			result = result.filter(
				(e) =>
					e.execution_name?.toLowerCase().includes(search) ||
					e.execution_id?.toLowerCase().includes(search) ||
					e.test_library_name?.toLowerCase().includes(search),
			)
		}

		// Apply status filter
		if (filters.value.status) {
			result = result.filter((e) => e.execution_status === filters.value.status)
		}

		// Apply test library filter
		if (filters.value.testLibrary) {
			result = result.filter(
				(e) => e.test_library_id === filters.value.testLibrary,
			)
		}

		// Apply execution type filter
		if (filters.value.executionType) {
			result = result.filter(
				(e) => e.execution_type === filters.value.executionType,
			)
		}

		// Apply priority filter
		if (filters.value.priority) {
			result = result.filter((e) => e.priority_level === filters.value.priority)
		}

		// Apply date range filter
		if (filters.value.dateFrom) {
			result = result.filter(
				(e) => new Date(e.creation) >= new Date(filters.value.dateFrom),
			)
		}
		if (filters.value.dateTo) {
			result = result.filter(
				(e) => new Date(e.creation) <= new Date(filters.value.dateTo),
			)
		}

		return result
	})

	// Actions
	const setSearchQuery = (query) => {
		searchQuery.value = query
	}

	const clearSearchQuery = () => {
		searchQuery.value = ""
	}

	const setFilters = (newFilters) => {
		Object.assign(filters.value, newFilters)
	}

	const clearFilters = () => {
		filters.value = {
			status: "",
			testLibrary: "",
			executionType: "",
			priority: "",
			dateFrom: "",
			dateTo: "",
		}
	}

	// Actions
	const fetchTestExecutions = async (filters = {}) => {
		loading.value = true
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Test Execution",
					fields: [
						"name",
						"execution_id",
						"execution_name",
						"test_library_reference",
						"execution_type",
						"priority",
						"status",
						"actual_start_date",
						"actual_end_date",
						"duration_seconds",
						"progress_percentage",
						"total_tests",
						"passed_tests",
						"failed_tests",
						"warning_tests",
						"total_records_processed",
						"exceptions_found",
						"critical_findings",
						"created_by",
						"creation",
						"modified",
					],
					filters: filters,
					limit_page_length: 1000,
					order_by: "actual_start_date desc",
				},
			}).fetch()
			testExecutions.value = response || []
			updateExecutionStatuses()
		} catch (error) {
			console.error("Error fetching test executions:", error)
			testExecutions.value = []
		} finally {
			loading.value = false
		}
	}

	const fetchTestExecutionDetails = async (executionId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "Test Execution",
					name: executionId,
				},
			}).fetch()
			currentExecution.value = response
			return response
		} catch (error) {
			console.error("Error fetching test execution details:", error)
			return null
		}
	}

	const createTestExecution = async (executionData) => {
		try {
			const response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Test Execution",
						...executionData,
					},
				},
			}).fetch()
			await fetchTestExecutions() // Refresh the list
			return response
		} catch (error) {
			console.error("Error creating test execution:", error)
			throw error
		}
	}

	const updateTestExecution = async (executionId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Test Execution",
					name: executionId,
					fieldname: updates,
				},
			}).fetch()
			await fetchTestExecutions() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating test execution:", error)
			throw error
		}
	}

	const startTestExecution = async (executionId) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.test_execution.start_execution",
				params: {
					execution_id: executionId,
				},
			}).fetch()
			await fetchTestExecutionDetails(executionId)
			await fetchTestExecutions() // Refresh the list
			return response
		} catch (error) {
			console.error("Error starting test execution:", error)
			throw error
		}
	}

	const stopTestExecution = async (executionId) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.test_execution.stop_execution",
				params: {
					execution_id: executionId,
				},
			}).fetch()
			await fetchTestExecutionDetails(executionId)
			await fetchTestExecutions() // Refresh the list
			return response
		} catch (error) {
			console.error("Error stopping test execution:", error)
			throw error
		}
	}

	const fetchTestResults = async (executionId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Test Result",
					filters: {
						test_execution: executionId,
					},
					fields: [
						"name",
						"test_id",
						"test_name",
						"result_status",
						"actual_value",
						"expected_value",
						"variance",
						"threshold_met",
						"exception_count",
						"result_summary",
						"execution_time",
						"started_at",
						"completed_at",
					],
					limit_page_length: 1000,
					order_by: "started_at desc",
				},
			}).fetch()
			testResults.value = response || []
			return response
		} catch (error) {
			console.error("Error fetching test results:", error)
			testResults.value = []
			return []
		}
	}

	const fetchTestParameters = async (testLibraryId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Test Parameter",
					filters: {
						parent: testLibraryId,
						parenttype: "Audit Test Library",
					},
					fields: [
						"name",
						"parameter_name",
						"parameter_type",
						"default_value",
						"is_required",
						"description",
						"validation_rule",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			testParameters.value = response || []
			return response
		} catch (error) {
			console.error("Error fetching test parameters:", error)
			testParameters.value = []
			return []
		}
	}

	const fetchTestThresholds = async (testLibraryId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Test Threshold",
					filters: {
						parent: testLibraryId,
						parenttype: "Audit Test Library",
					},
					fields: [
						"name",
						"threshold_name",
						"threshold_type",
						"operator",
						"threshold_value",
						"warning_threshold",
						"critical_threshold",
						"description",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			testThresholds.value = response || []
			return response
		} catch (error) {
			console.error("Error fetching test thresholds:", error)
			testThresholds.value = []
			return []
		}
	}

	const fetchExecutionLogs = async (executionId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Execution Log",
					filters: {
						parent: executionId,
						parenttype: "Test Execution",
					},
					fields: [
						"name",
						"timestamp",
						"log_level",
						"message",
						"step_name",
						"duration_ms",
					],
					limit_page_length: 1000,
					order_by: "timestamp desc",
				},
			}).fetch()
			executionLogs.value = response || []
			return response
		} catch (error) {
			console.error("Error fetching execution logs:", error)
			executionLogs.value = []
			return []
		}
	}

	const fetchAnalyticalProcedureResults = async (executionId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Analytical Procedure Result",
					filters: {
						test_execution: executionId,
					},
					fields: [
						"name",
						"procedure_name",
						"procedure_type",
						"current_value",
						"prior_value",
						"budget_value",
						"variance_amount",
						"variance_percentage",
						"significance_level",
						"investigation_required",
						"conclusion",
						"completed_at",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			analyticalProcedures.value = response || []
			return response
		} catch (error) {
			console.error("Error fetching analytical procedure results:", error)
			analyticalProcedures.value = []
			return []
		}
	}

	const runAnalyticalProcedure = async (procedureData) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.test_execution.run_analytical_procedure",
				params: procedureData,
			}).fetch()
			return response
		} catch (error) {
			console.error("Error running analytical procedure:", error)
			throw error
		}
	}

	const exportTestResults = async (executionId, format = "excel") => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.test_execution.export_results",
				params: {
					execution_id: executionId,
					format: format,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error exporting test results:", error)
			throw error
		}
	}

	// Helper functions
	const updateExecutionStatuses = () => {
		const statuses = {
			pending: 0,
			running: 0,
			completed: 0,
			failed: 0,
			cancelled: 0,
		}

		testExecutions.value.forEach((execution) => {
			const status = execution.status?.toLowerCase() || "pending"
			if (statuses.hasOwnProperty(status)) {
				statuses[status]++
			}
		})

		executionStatuses.value = statuses
	}

	const getExecutionById = (executionId) => {
		return testExecutions.value.find((e) => e.name === executionId)
	}

	const getExecutionsByEngagement = (engagementId) => {
		return testExecutions.value.filter(
			(e) => e.audit_engagement === engagementId,
		)
	}

	const clearCurrentExecution = () => {
		currentExecution.value = null
		testResults.value = []
		executionLogs.value = []
		analyticalProcedures.value = []
	}

	const calculateExecutionMetrics = (execution) => {
		if (!execution) return null

		const totalTests = execution.total_tests || 0
		const completedTests = execution.completed_tests || 0
		const failedTests = execution.failed_tests || 0
		const successfulTests = completedTests - failedTests

		return {
			totalTests,
			completedTests,
			failedTests,
			successfulTests,
			successRate:
				totalTests > 0 ? Math.round((successfulTests / totalTests) * 100) : 0,
			completionRate:
				totalTests > 0 ? Math.round((completedTests / totalTests) * 100) : 0,
			failureRate:
				completedTests > 0
					? Math.round((failedTests / completedTests) * 100)
					: 0,
		}
	}

	return {
		// State
		testExecutions,
		testResults,
		testParameters,
		testThresholds,
		executionLogs,
		currentExecution,
		loading,
		searchQuery,
		filters,
		testLibraryTests,
		analyticalProcedures,
		executionStatuses,

		// Getters
		activeExecutions,
		completedExecutions,
		failedExecutions,
		executionsByStatus,
		executionProgress,
		filteredExecutions,

		// Actions
		setSearchQuery,
		clearSearchQuery,
		setFilters,
		clearFilters,
		fetchTestExecutions,
		fetchTestExecutionDetails,
		createTestExecution,
		updateTestExecution,
		startTestExecution,
		stopTestExecution,
		fetchTestResults,
		fetchTestParameters,
		fetchTestThresholds,
		fetchExecutionLogs,
		fetchAnalyticalProcedureResults,
		runAnalyticalProcedure,
		exportTestResults,

		// Helper functions
		getExecutionById,
		getExecutionsByEngagement,
		clearCurrentExecution,
		calculateExecutionMetrics,
	}
})
