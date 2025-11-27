import { createResource } from "frappe-ui"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useSearchStore = defineStore("search", () => {
	// State
	const searchResults = ref([])
	const searchHistory = ref([])
	const savedSearches = ref([])
	const activeFilters = ref({})
	const searchQuery = ref("")
	const loading = ref({
		search: false,
		analytics: false,
		export: false,
	})
	const error = ref(null)
	const searchStats = ref({})

	// Search Configuration
	const searchableDocTypes = ref([
		{
			doctype: "Audit Finding",
			label: "Audit Findings",
			icon: "AlertTriangleIcon",
			searchFields: ["finding_title", "description", "recommendation"],
			filterFields: [
				{ field: "finding_type", label: "Finding Type", type: "select" },
				{ field: "severity", label: "Severity", type: "select" },
				{ field: "status", label: "Status", type: "select" },
				{ field: "department", label: "Department", type: "link" },
				{ field: "due_date", label: "Due Date", type: "daterange" },
				{ field: "risk_level", label: "Risk Level", type: "select" },
			],
			displayFields: [
				"finding_title",
				"finding_type",
				"severity",
				"status",
				"creation",
			],
			weightage: 1.0,
		},
		{
			doctype: "Control Procedure",
			label: "Control Procedures",
			icon: "ShieldIcon",
			searchFields: ["procedure_name", "description", "testing_approach"],
			filterFields: [
				{ field: "control_type", label: "Control Type", type: "select" },
				{ field: "frequency", label: "Frequency", type: "select" },
				{ field: "effectiveness", label: "Effectiveness", type: "select" },
				{ field: "process_area", label: "Process Area", type: "link" },
				{ field: "last_tested", label: "Last Tested", type: "daterange" },
				{ field: "automated", label: "Automated", type: "check" },
			],
			displayFields: [
				"procedure_name",
				"control_type",
				"frequency",
				"effectiveness",
				"last_tested",
			],
			weightage: 0.9,
		},
		{
			doctype: "Audit Test",
			label: "Audit Tests",
			icon: "CheckSquareIcon",
			searchFields: [
				"test_name",
				"procedure",
				"expected_result",
				"actual_result",
			],
			filterFields: [
				{ field: "test_type", label: "Test Type", type: "select" },
				{ field: "status", label: "Status", type: "select" },
				{ field: "result", label: "Result", type: "select" },
				{ field: "audit_plan", label: "Audit Plan", type: "link" },
				{
					field: "completion_date",
					label: "Completion Date",
					type: "daterange",
				},
				{ field: "sample_size", label: "Sample Size", type: "range" },
			],
			displayFields: [
				"test_name",
				"test_type",
				"status",
				"result",
				"completion_date",
			],
			weightage: 0.8,
		},
		{
			doctype: "Audit Plan",
			label: "Audit Plans",
			icon: "CalendarIcon",
			searchFields: ["plan_name", "scope", "objectives"],
			filterFields: [
				{ field: "audit_type", label: "Audit Type", type: "select" },
				{ field: "status", label: "Status", type: "select" },
				{ field: "start_date", label: "Start Date", type: "daterange" },
				{ field: "end_date", label: "End Date", type: "daterange" },
				{ field: "auditor", label: "Auditor", type: "link" },
				{
					field: "completion_percentage",
					label: "Completion %",
					type: "range",
				},
			],
			displayFields: [
				"plan_name",
				"audit_type",
				"status",
				"start_date",
				"end_date",
			],
			weightage: 0.7,
		},
		{
			doctype: "Evidence",
			label: "Evidence",
			icon: "FileIcon",
			searchFields: ["file_name", "description", "tags"],
			filterFields: [
				{ field: "evidence_type", label: "Evidence Type", type: "select" },
				{ field: "status", label: "Status", type: "select" },
				{ field: "file_type", label: "File Type", type: "select" },
				{ field: "upload_date", label: "Upload Date", type: "daterange" },
				{ field: "file_size", label: "File Size", type: "range" },
				{ field: "uploader", label: "Uploader", type: "link" },
			],
			displayFields: [
				"file_name",
				"evidence_type",
				"file_type",
				"status",
				"upload_date",
			],
			weightage: 0.6,
		},
	])

	// Analytics Configuration
	const analyticsMetrics = ref([
		{
			id: "findings_by_severity",
			name: "Findings by Severity",
			type: "distribution",
			doctype: "Audit Finding",
			groupBy: "severity",
			chartType: "pie",
		},
		{
			id: "findings_trend",
			name: "Findings Trend",
			type: "trend",
			doctype: "Audit Finding",
			dateField: "creation",
			chartType: "line",
		},
		{
			id: "control_effectiveness",
			name: "Control Effectiveness",
			type: "distribution",
			doctype: "Control Procedure",
			groupBy: "effectiveness",
			chartType: "bar",
		},
		{
			id: "test_results",
			name: "Test Results Summary",
			type: "distribution",
			doctype: "Audit Test",
			groupBy: "result",
			chartType: "donut",
		},
		{
			id: "completion_rates",
			name: "Audit Plan Completion Rates",
			type: "metric",
			doctype: "Audit Plan",
			aggregateField: "completion_percentage",
			aggregateFunction: "avg",
		},
	])

	// Resources
	const searchResource = createResource({
		url: "mkaguzi.api.search.global_search",
		auto: false,
	})

	const analyticsResource = createResource({
		url: "mkaguzi.api.search.get_analytics",
		auto: false,
	})

	const exportResource = createResource({
		url: "mkaguzi.api.search.export_results",
		auto: false,
	})

	// Actions
	const performSearch = async (query, filters = {}, options = {}) => {
		try {
			loading.value.search = true
			error.value = null

			// Add to search history if it's a new query
			if (query && !searchHistory.value.some((h) => h.query === query)) {
				searchHistory.value.unshift({
					query,
					timestamp: new Date().toISOString(),
					filters: { ...filters },
				})
				// Keep only last 20 searches
				searchHistory.value = searchHistory.value.slice(0, 20)
			}

			const response = await searchResource.fetch({
				params: {
					query,
					filters,
					doctypes:
						options.doctypes ||
						searchableDocTypes.value.map((dt) => dt.doctype),
					fuzzy: options.fuzzy ?? true,
					include_analytics: options.include_analytics ?? true,
					page_size: options.page_size || 50,
					page: options.page || 1,
				},
			})

			if (response) {
				searchResults.value = response.results || []
				searchStats.value = response.stats || {}
				searchQuery.value = query
				activeFilters.value = filters
				return response
			}
		} catch (err) {
			error.value = err.message
			console.error("Search failed:", err)
			throw err
		} finally {
			loading.value.search = false
		}
	}

	const getAutocompleteSuggestions = async (query, limit = 10) => {
		try {
			if (!query || query.length < 2) return []

			const response = await createResource({
				url: "mkaguzi.api.search.get_suggestions",
				auto: false,
			}).fetch({
				params: { query, limit },
			})

			return response || []
		} catch (err) {
			console.error("Failed to get suggestions:", err)
			return []
		}
	}

	const saveSearch = async (searchData) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.search.save_search",
				auto: false,
			}).fetch({
				params: searchData,
			})

			if (response) {
				savedSearches.value.push(response)
				return response
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to save search:", err)
			throw err
		}
	}

	const loadSavedSearch = async (searchId) => {
		try {
			const savedSearch = savedSearches.value.find((s) => s.name === searchId)
			if (savedSearch) {
				await performSearch(
					savedSearch.query,
					savedSearch.filters,
					savedSearch.options,
				)
				return savedSearch
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to load saved search:", err)
			throw err
		}
	}

	const deleteSavedSearch = async (searchId) => {
		try {
			await createResource({
				url: "mkaguzi.api.search.delete_saved_search",
				auto: false,
			}).fetch({
				params: { search_id: searchId },
			})

			savedSearches.value = savedSearches.value.filter(
				(s) => s.name !== searchId,
			)
		} catch (err) {
			error.value = err.message
			console.error("Failed to delete saved search:", err)
			throw err
		}
	}

	const getAnalytics = async (
		metricIds = [],
		filters = {},
		timeRange = "30d",
	) => {
		try {
			loading.value.analytics = true
			error.value = null

			const response = await analyticsResource.fetch({
				params: {
					metrics: metricIds.length
						? metricIds
						: analyticsMetrics.value.map((m) => m.id),
					filters,
					time_range: timeRange,
				},
			})

			return response || {}
		} catch (err) {
			error.value = err.message
			console.error("Failed to get analytics:", err)
			throw err
		} finally {
			loading.value.analytics = false
		}
	}

	const getAdvancedAnalytics = async (config) => {
		try {
			loading.value.analytics = true

			const response = await createResource({
				url: "mkaguzi.api.search.get_advanced_analytics",
				auto: false,
			}).fetch({
				params: config,
			})

			return response || {}
		} catch (err) {
			error.value = err.message
			console.error("Failed to get advanced analytics:", err)
			throw err
		} finally {
			loading.value.analytics = false
		}
	}

	const exportSearchResults = async (format = "excel", options = {}) => {
		try {
			loading.value.export = true

			const response = await exportResource.fetch({
				params: {
					results: searchResults.value,
					query: searchQuery.value,
					filters: activeFilters.value,
					format,
					...options,
				},
			})

			if (response?.download_url) {
				// Trigger download
				const link = document.createElement("a")
				link.href = response.download_url
				link.download = `search_results_${new Date().toISOString().split("T")[0]}.${format}`
				link.click()
				return response
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to export search results:", err)
			throw err
		} finally {
			loading.value.export = false
		}
	}

	const clearSearch = () => {
		searchResults.value = []
		searchQuery.value = ""
		activeFilters.value = {}
		searchStats.value = {}
		error.value = null
	}

	const addFilter = (field, value, operator = "equals") => {
		if (!activeFilters.value[field]) {
			activeFilters.value[field] = []
		}

		activeFilters.value[field].push({
			value,
			operator,
			timestamp: Date.now(),
		})
	}

	const removeFilter = (field, index = null) => {
		if (index !== null) {
			activeFilters.value[field].splice(index, 1)
			if (activeFilters.value[field].length === 0) {
				delete activeFilters.value[field]
			}
		} else {
			delete activeFilters.value[field]
		}
	}

	const clearFilters = () => {
		activeFilters.value = {}
	}

	// Computed
	const hasResults = computed(() => searchResults.value.length > 0)

	const resultsByDocType = computed(() => {
		const grouped = {}
		searchResults.value.forEach((result) => {
			const doctype = result.doctype
			if (!grouped[doctype]) {
				grouped[doctype] = []
			}
			grouped[doctype].push(result)
		})
		return grouped
	})

	const totalResults = computed(() => searchStats.value.total_results || 0)

	const searchDuration = computed(() => searchStats.value.search_duration || 0)

	const availableFilters = computed(() => {
		const filters = new Map()
		searchableDocTypes.value.forEach((doctype) => {
			doctype.filterFields.forEach((filter) => {
				filters.set(filter.field, {
					...filter,
					doctype: doctype.doctype,
				})
			})
		})
		return Array.from(filters.values())
	})

	const recentSearches = computed(() => searchHistory.value.slice(0, 10))

	const filterCount = computed(() =>
		Object.keys(activeFilters.value).reduce(
			(count, key) => count + activeFilters.value[key].length,
			0,
		),
	)

	// Initialize
	const initialize = async () => {
		try {
			// Load saved searches
			const response = await createResource({
				url: "mkaguzi.api.search.get_saved_searches",
				auto: false,
			}).fetch()

			savedSearches.value = response || []

			// Load search history from localStorage
			const history = localStorage.getItem("mkaguzi_search_history")
			if (history) {
				searchHistory.value = JSON.parse(history)
			}
		} catch (err) {
			console.error("Failed to initialize search store:", err)
		}
	}

	// Watch for search history changes and save to localStorage
	const saveSearchHistory = () => {
		localStorage.setItem(
			"mkaguzi_search_history",
			JSON.stringify(searchHistory.value),
		)
	}

	return {
		// State
		searchResults,
		searchHistory,
		savedSearches,
		activeFilters,
		searchQuery,
		loading,
		error,
		searchStats,
		searchableDocTypes,
		analyticsMetrics,

		// Actions
		performSearch,
		getAutocompleteSuggestions,
		saveSearch,
		loadSavedSearch,
		deleteSavedSearch,
		getAnalytics,
		getAdvancedAnalytics,
		exportSearchResults,
		clearSearch,
		addFilter,
		removeFilter,
		clearFilters,
		initialize,
		saveSearchHistory,

		// Computed
		hasResults,
		resultsByDocType,
		totalResults,
		searchDuration,
		availableFilters,
		recentSearches,
		filterCount,
	}
})
