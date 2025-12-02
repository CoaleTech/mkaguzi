import { call } from "frappe-ui"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useVATReconciliationStore = defineStore("vatReconciliation", () => {
	// State
	const reconciliations = ref([])
	const activeReconciliation = ref(null)
	const reconciliationResults = ref([])
	const uploadedFiles = ref({
		system: null,
		itax: null,
		tims: null,
	})
	const loading = ref({
		list: false,
		detail: false,
		upload: false,
		reconcile: false,
		export: false,
	})
	const error = ref(null)
	const totalCount = ref(0)
	const page = ref(1)
	const pageSize = ref(50)
	const filters = ref({
		reconciliation_month: "",
		fiscal_year: "",
		reconciliation_type: "",
		status: "",
		search: "",
	})

	// Progress tracking for background jobs
	const jobProgress = ref({
		isRunning: false,
		percent: 0,
		status: "",
	})

	// Historical comparison data
	const historicalComparison = ref(null)
	const recurringDiscrepancies = ref([])

	// Results cache for performance optimization
	const resultsCache = ref({})
	const summaryCache = ref({}) // Separate cache for summary data (faster initial load)
	const cacheExpiry = ref(5 * 60 * 1000) // 5 minutes

	// Actions
	const fetchReconciliations = async (customFilters = null, customPage = 1) => {
		try {
			loading.value.list = true
			error.value = null

			const result = await call(
				"mkaguzi.api.vat_reconciliation.get_vat_reconciliations",
				{
					filters: JSON.stringify(customFilters || filters.value),
					page: customPage,
					page_size: pageSize.value,
				},
			)

			reconciliations.value = result.items || []
			totalCount.value = result.total_count || 0
			page.value = result.page || 1

			return result
		} catch (err) {
			error.value = `Failed to load reconciliations: ${err.message}`
			console.error("Failed to fetch reconciliations:", err)
		} finally {
			loading.value.list = false
		}
	}

	const fetchReconciliation = async (reconciliationId, forceRefresh = false) => {
		try {
			loading.value.detail = true
			error.value = null

			// Check summary cache first for faster initial load
			const cacheKey = `summary_${reconciliationId}`
			if (summaryCache.value[cacheKey] && !forceRefresh) {
				const cached = summaryCache.value[cacheKey]
				if (Date.now() - cached.timestamp < cacheExpiry.value) {
					console.log("Using cached summary for:", reconciliationId)
					activeReconciliation.value = cached.data
					updateUploadedFilesState(cached.data)
					loading.value.detail = false
					return cached.data
				} else {
					delete summaryCache.value[cacheKey]
				}
			}

			// Use lightweight API that doesn't load child tables
			const result = await call(
				"mkaguzi.api.vat_reconciliation.get_reconciliation_summary",
				{ reconciliation_id: reconciliationId }
			)

			if (result.success && result.data) {
				const doc = result.data
				activeReconciliation.value = doc

				// Cache the summary with timestamp
				summaryCache.value[cacheKey] = {
					data: doc,
					timestamp: Date.now()
				}

				// Update uploaded files state
				updateUploadedFilesState(doc)

				return doc
			}
		} catch (err) {
			error.value = `Failed to load reconciliation: ${err.message}`
			console.error("Failed to fetch reconciliation:", err)
		} finally {
			loading.value.detail = false
		}
	}

	// Helper function to update uploaded files state from doc
	const updateUploadedFilesState = (doc) => {
		uploadedFiles.value = {
			system: doc.system_data_file
				? { status: doc.system_data_status, rows: doc.system_data_rows }
				: null,
			itax: doc.itax_data_file
				? { status: doc.itax_data_status, rows: doc.itax_data_rows }
				: null,
			tims: doc.tims_data_file
				? { status: doc.tims_data_status, rows: doc.tims_data_rows }
				: null,
		}
	}

	const createReconciliation = async (data) => {
		try {
			loading.value.detail = true
			error.value = null

			const result = await call(
				"mkaguzi.api.vat_reconciliation.create_reconciliation",
				{
					reconciliation_type: data.reconciliation_type,
					reconciliation_month: data.reconciliation_month,
					fiscal_year: data.fiscal_year,
				},
			)

			if (result.success) {
				await fetchReconciliation(result.name)
				return result
			}
		} catch (err) {
			error.value = `Failed to create reconciliation: ${err.message}`
			console.error("Failed to create reconciliation:", err)
			throw err
		} finally {
			loading.value.detail = false
		}
	}

	const uploadFile = async (reconciliationId, fileType, file) => {
		try {
			loading.value.upload = true
			error.value = null

			const formData = new FormData()
			formData.append("file", file)

			const response = await fetch(
				`/api/method/mkaguzi.api.vat_reconciliation.upload_vat_file?reconciliation_id=${reconciliationId}&file_type=${fileType}`,
				{
					method: "POST",
					body: formData,
				},
			)

			if (!response.ok) {
				throw new Error(`Upload failed: ${response.statusText}`)
			}

			const data = await response.json()

			if (data.message?.success) {
				// Update local state
				uploadedFiles.value[fileType] = {
					status: "Validated",
					rows: data.message.row_count,
					columnMapping: data.message.column_mapping,
				}

				// Refresh reconciliation document
				await fetchReconciliation(reconciliationId)

				return data.message
			} else {
				throw new Error(
					data.message?.message || data.exc || "Upload failed",
				)
			}
		} catch (err) {
			error.value = `Failed to upload file: ${err.message}`
			console.error("Failed to upload file:", err)
			throw err
		} finally {
			loading.value.upload = false
		}
	}

	const runReconciliation = async (reconciliationId, useBackground = false) => {
		try {
			loading.value.reconcile = true
			error.value = null
			jobProgress.value = { isRunning: true, percent: 0, status: "Starting..." }

			const result = await call(
				"mkaguzi.api.vat_reconciliation.run_reconciliation",
				{
					reconciliation_id: reconciliationId,
					use_background: useBackground,
				},
			)

			if (result.background) {
				// Start polling for progress
				pollProgress(reconciliationId)
				return result
			} else {
				jobProgress.value = {
					isRunning: false,
					percent: 100,
					status: "Completed",
				}
				// Clear caches for fresh data after reconciliation
				clearResultsCache(reconciliationId)
				clearSummaryCache(reconciliationId)
				await fetchReconciliation(reconciliationId, true) // Force refresh
				return result
			}
		} catch (err) {
			error.value = `Failed to run reconciliation: ${err.message}`
			jobProgress.value = { isRunning: false, percent: 0, status: "Failed" }
			console.error("Failed to run reconciliation:", err)
			throw err
		} finally {
			loading.value.reconcile = false
		}
	}

	const pollProgress = async (reconciliationId) => {
		const pollInterval = setInterval(async () => {
			try {
				const progress = await call(
					"mkaguzi.api.vat_reconciliation.get_reconciliation_progress",
					{
						reconciliation_id: reconciliationId,
					},
				)

				jobProgress.value = {
					isRunning: progress.status === "Processing",
					percent: progress.progress_percent || 0,
					status: progress.status,
				}

				if (progress.status === "Completed" || progress.status === "Failed") {
					clearInterval(pollInterval)
					// Clear caches for fresh data after background reconciliation
					clearResultsCache(reconciliationId)
					clearSummaryCache(reconciliationId)
					await fetchReconciliation(reconciliationId, true) // Force refresh
				}
			} catch (err) {
				console.error("Error polling progress:", err)
				clearInterval(pollInterval)
			}
		}, 2000) // Poll every 2 seconds
	}

	const fetchResults = async (
		reconciliationId,
		filterStatus = null,
		resultPage = 1,
		forceRefresh = false
	) => {
		try {
			const cacheKey = `${reconciliationId}_${filterStatus || 'all'}_${resultPage}`
			
			// Check cache first (simple in-memory cache for current session)
			if (resultsCache.value[cacheKey] && !forceRefresh) {
				const cached = resultsCache.value[cacheKey]
				// Check if cache is still valid (not expired)
				if (Date.now() - cached.timestamp < cacheExpiry.value) {
					console.log("Using cached results for:", cacheKey)
					reconciliationResults.value = cached.items
					return cached
				} else {
					// Remove expired cache
					delete resultsCache.value[cacheKey]
				}
			}

			console.log("Fetching results for:", { reconciliationId, filterStatus, resultPage })
			
			const result = await call(
				"mkaguzi.api.vat_reconciliation.get_reconciliation_results",
				{
					reconciliation_id: reconciliationId,
					filter_status: filterStatus,
					page: resultPage,
					page_size: 100, // Increased page size for better UX
				},
			)
			
			console.log("API call result:", result)
			
			// Cache the result with timestamp
			resultsCache.value[cacheKey] = {
				...result,
				timestamp: Date.now()
			}
			
			reconciliationResults.value = result.items || []
			console.log("Results cached and set:", reconciliationResults.value.length, "items")
			
			return result
		} catch (err) {
			console.error("Failed to fetch results:", err)
			error.value = `Failed to load results: ${err.message}`
		}
	}

	const exportReport = async (reconciliationId, format = "excel") => {
		try {
			loading.value.export = true
			error.value = null

			const result = await call(
				"mkaguzi.api.vat_reconciliation.export_reconciliation_report",
				{
					reconciliation_id: reconciliationId,
					format: format,
				},
			)

			if (result.success && result.download_url) {
				// Trigger download
				window.open(result.download_url, "_blank")
				return result
			}
		} catch (err) {
			error.value = `Failed to export report: ${err.message}`
			console.error("Failed to export report:", err)
			throw err
		} finally {
			loading.value.export = false
		}
	}

	const compareWithPrevious = async (reconciliationId) => {
		try {
			const result = await call(
				"mkaguzi.api.vat_reconciliation.compare_with_previous_month",
				{
					reconciliation_id: reconciliationId,
				},
			)

			if (result.success) {
				historicalComparison.value = result.comparison
			}

			return result
		} catch (err) {
			console.error("Failed to compare with previous:", err)
		}
	}

	const fetchRecurringDiscrepancies = async (reconciliationId, months = 6) => {
		try {
			const result = await call(
				"mkaguzi.api.vat_reconciliation.get_recurring_discrepancies",
				{
					reconciliation_id: reconciliationId,
					months: months,
				},
			)

			if (result.success) {
				recurringDiscrepancies.value = result.recurring_discrepancies
			}

			return result
		} catch (err) {
			console.error("Failed to fetch recurring discrepancies:", err)
		}
	}

	const deleteReconciliation = async (reconciliationId) => {
		try {
			const result = await call(
				"mkaguzi.api.vat_reconciliation.delete_reconciliation",
				{
					reconciliation_id: reconciliationId,
				},
			)

			if (result.success) {
				await fetchReconciliations()
			}

			return result
		} catch (err) {
			error.value = `Failed to delete reconciliation: ${err.message}`
			console.error("Failed to delete reconciliation:", err)
			throw err
		}
	}

	const updateFilters = (newFilters) => {
		filters.value = { ...filters.value, ...newFilters }
		page.value = 1
		return fetchReconciliations()
	}

	const clearFilters = () => {
		filters.value = {
			reconciliation_month: "",
			fiscal_year: "",
			reconciliation_type: "",
			status: "",
			search: "",
		}
		page.value = 1
		return fetchReconciliations()
	}

	const clearResultsCache = (reconciliationId = null) => {
		if (reconciliationId) {
			// Clear cache for specific reconciliation
			const keysToDelete = Object.keys(resultsCache.value).filter(key => 
				key.startsWith(`${reconciliationId}_`)
			)
			keysToDelete.forEach(key => delete resultsCache.value[key])
		} else {
			// Clear all cache
			resultsCache.value = {}
		}
	}

	const clearSummaryCache = (reconciliationId = null) => {
		if (reconciliationId) {
			// Clear summary cache for specific reconciliation
			const cacheKey = `summary_${reconciliationId}`
			delete summaryCache.value[cacheKey]
		} else {
			// Clear all summary cache
			summaryCache.value = {}
		}
	}

	const resetUploadedFiles = () => {
		uploadedFiles.value = {
			system: null,
			itax: null,
			tims: null,
		}
	}

	// Getters
	const summaryStats = computed(() => {
		if (!activeReconciliation.value) return null

		return {
			totalMatched: activeReconciliation.value.total_matched || 0,
			totalUnmatchedA: activeReconciliation.value.total_unmatched_source_a || 0,
			totalUnmatchedB: activeReconciliation.value.total_unmatched_source_b || 0,
			totalDiscrepancies:
				activeReconciliation.value.total_amount_discrepancies || 0,
			totalVariance: activeReconciliation.value.total_variance_amount || 0,
			matchPercentage: activeReconciliation.value.match_percentage || 0,
			status: activeReconciliation.value.reconciliation_status || "",
		}
	})

	const matchedItems = computed(() => {
		return reconciliationResults.value.filter(
			(item) => item.match_status === "Matched",
		)
	})

	const unmatchedSourceA = computed(() => {
		return reconciliationResults.value.filter(
			(item) => item.match_status === "Unmatched Source A",
		)
	})

	const unmatchedSourceB = computed(() => {
		return reconciliationResults.value.filter(
			(item) => item.match_status === "Unmatched Source B",
		)
	})

	const discrepancies = computed(() => {
		return reconciliationResults.value.filter(
			(item) => item.match_status === "Amount Discrepancy",
		)
	})

	const isReadyForReconciliation = computed(() => {
		if (!activeReconciliation.value) return false

		const type = activeReconciliation.value.reconciliation_type

		if (type === "System vs iTax") {
			return (
				uploadedFiles.value.system?.status === "Validated" &&
				uploadedFiles.value.itax?.status === "Validated"
			)
		} else if (type === "System vs TIMs") {
			return (
				uploadedFiles.value.system?.status === "Validated" &&
				uploadedFiles.value.tims?.status === "Validated"
			)
		} else if (type === "iTax vs TIMs") {
			return (
				uploadedFiles.value.itax?.status === "Validated" &&
				uploadedFiles.value.tims?.status === "Validated"
			)
		}

		return false
	})

	const totalPages = computed(() => {
		return Math.ceil(totalCount.value / pageSize.value)
	})

	const listStats = computed(() => {
		const completed = reconciliations.value.filter(
			(r) => r.status === "Completed",
		).length
		const pending = reconciliations.value.filter((r) =>
			["Draft", "Files Uploaded", "Processing"].includes(r.status),
		).length
		const failed = reconciliations.value.filter(
			(r) => r.status === "Failed",
		).length

		const totalVariance = reconciliations.value.reduce(
			(sum, r) => sum + (r.total_variance_amount || 0),
			0,
		)
		const avgMatchRate =
			reconciliations.value.length > 0
				? reconciliations.value.reduce(
						(sum, r) => sum + (r.match_percentage || 0),
						0,
					) / reconciliations.value.length
				: 0

		return {
			total: reconciliations.value.length,
			completed,
			pending,
			failed,
			totalVariance,
			avgMatchRate,
		}
	})

	return {
		// State
		reconciliations,
		activeReconciliation,
		reconciliationResults,
		uploadedFiles,
		loading,
		error,
		totalCount,
		page,
		pageSize,
		filters,
		jobProgress,
		historicalComparison,
		recurringDiscrepancies,
		resultsCache,
		summaryCache,

		// Actions
		fetchReconciliations,
		fetchReconciliation,
		createReconciliation,
		uploadFile,
		runReconciliation,
		fetchResults,
		exportReport,
		compareWithPrevious,
		fetchRecurringDiscrepancies,
		deleteReconciliation,
		updateFilters,
		clearFilters,
		resetUploadedFiles,
		clearResultsCache,
		clearSummaryCache,

		// Getters
		summaryStats,
		matchedItems,
		unmatchedSourceA,
		unmatchedSourceB,
		discrepancies,
		isReadyForReconciliation,
		totalPages,
		listStats,
	}
})
