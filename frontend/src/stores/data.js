import { createResource } from "frappe-ui"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useDataStore = defineStore("data", () => {
	// State
	const dataPeriods = ref([])
	const importStatus = ref(null)
	const bcDataCache = ref(new Map())

	// Data Management State
	const dashboards = ref([])
	const dashboardCharts = ref([])
	const dashboardDataSources = ref([])
	const dashboardFilters = ref([])
	const csvImportTypes = ref([])
	const csvImportFieldMappings = ref([])
	const csvImportHistory = ref([])
	const dataQualityMetrics = ref({})

	// Data Management Getters
	const activeDashboards = computed(() => {
		return dashboards.value.filter((d) => d.is_active)
	})

	const publicDashboards = computed(() => {
		return dashboards.value.filter((d) => d.dashboard_type === "Public")
	})

	const activeCsvImports = computed(() => {
		return csvImportTypes.value.filter((i) => i.is_active)
	})

	const activeDataPeriods = computed(() => {
		return dataPeriods.value.filter((p) => p.is_active)
	})

	const dataCompleteness = computed(() => {
		if (Object.keys(dataQualityMetrics.value).length === 0) return 0

		const metrics = Object.values(dataQualityMetrics.value)
		const total = metrics.length
		const complete = metrics.filter((m) => m.completeness >= 80).length

		return Math.round((complete / total) * 100)
	})

	// Data Management Actions
	const fetchDashboards = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Data Analytics Dashboard",
					fields: [
						"name",
						"dashboard_id",
						"dashboard_name",
						"dashboard_type",
						"description",
						"is_active",
						"is_default",
						"created_by",
						"creation_date",
						"last_refresh_date",
						"total_views",
						"last_viewed_date",
						"modified",
					],
					limit_page_length: 1000,
					order_by: "modified desc",
				},
			}).fetch()
			dashboards.value = response || []
		} catch (error) {
			console.error("Error fetching dashboards:", error)
			// If permission error, set empty array instead of throwing
			if (error.message && error.message.includes("PermissionError")) {
				console.warn("No permission to access Data Analytics Dashboard doctype")
				dashboards.value = []
			} else {
				dashboards.value = []
			}
		}
	}

	const fetchDashboardDetails = async (dashboardId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "Data Analytics Dashboard",
					name: dashboardId,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error fetching dashboard details:", error)
			return null
		}
	}

	const createDashboard = async (dashboardData) => {
		try {
			const response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Data Analytics Dashboard",
						...dashboardData,
					},
				},
			}).fetch()
			await fetchDashboards() // Refresh the list
			return response
		} catch (error) {
			console.error("Error creating dashboard:", error)
			throw error
		}
	}

	const updateDashboard = async (dashboardId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Data Analytics Dashboard",
					name: dashboardId,
					fieldname: updates,
				},
			}).fetch()
			await fetchDashboards() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating dashboard:", error)
			throw error
		}
	}

	const fetchDashboardCharts = async (dashboardId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Dashboard Chart",
					filters: {
						parent: dashboardId,
						parenttype: "Data Analytics Dashboard",
					},
					fields: [
						"name",
						"chart_name",
						"chart_type",
						"data_source",
						"x_axis_field",
						"y_axis_field",
						"chart_title",
						"width",
						"height",
						"position_x",
						"position_y",
						"is_active",
						"refresh_interval",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			dashboardCharts.value = response || []
			return response
		} catch (error) {
			// If permission error, handle silently since it's expected for restricted doctypes
			if (error.message && error.message.includes("PermissionError")) {
				console.warn("No permission to access Dashboard Chart doctype")
				dashboardCharts.value = []
				return []
			} else {
				console.error("Error fetching dashboard charts:", error)
				dashboardCharts.value = []
				return []
			}
		}
	}

	const fetchDashboardDataSources = async (dashboardId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Dashboard Data Source",
					filters: {
						parent: dashboardId,
						parenttype: "Data Analytics Dashboard",
					},
					fields: [
						"name",
						"data_source_name",
						"data_source_type",
						"connection_string",
						"query",
						"refresh_interval",
						"is_active",
						"last_refresh",
						"cache_enabled",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			dashboardDataSources.value = response || []
			return response
		} catch (error) {
			// If permission error, handle silently since it's expected for restricted doctypes
			if (error.message && error.message.includes("PermissionError")) {
				console.warn("No permission to access Dashboard Data Source doctype")
				dashboardDataSources.value = []
				return []
			} else {
				console.error("Error fetching dashboard data sources:", error)
				dashboardDataSources.value = []
				return []
			}
		}
	}

	const fetchCsvImportTypes = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "CSV Import Type",
					fields: [
						"name",
						"import_type_id",
						"import_name",
						"description",
						"bc_source_table",
						"target_doctype",
						"is_active",
						"import_frequency",
						"last_import_date",
						"total_records_imported",
						"successful_imports",
						"failed_imports",
						"creation",
						"modified",
						"field_mappings", // Include child table field mappings
					],
					limit_page_length: 1000,
					order_by: "modified desc",
				},
			}).fetch()
			csvImportTypes.value = response || []
			// Extract field mappings from all import types and flatten them
			const allFieldMappings = []
			csvImportTypes.value.forEach(importType => {
				if (importType.field_mappings && Array.isArray(importType.field_mappings)) {
					importType.field_mappings.forEach(mapping => {
						allFieldMappings.push({
							...mapping,
							import_type_name: importType.import_name || importType.name,
						})
					})
				}
			})
			csvImportFieldMappings.value = allFieldMappings
		} catch (error) {
			console.error("Error fetching CSV import types:", error)
			// If permission error, set empty array instead of throwing
			if (error.message && error.message.includes("PermissionError")) {
				console.warn("No permission to access CSV Import Type doctype")
				csvImportTypes.value = []
				csvImportFieldMappings.value = []
			} else {
				csvImportTypes.value = []
				csvImportFieldMappings.value = []
			}
		}
	}

	const fetchCsvImportTypeDetails = async (importTypeId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "CSV Import Type",
					name: importTypeId,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error fetching CSV import type details:", error)
			return null
		}
	}

	const createCsvImportType = async (importData) => {
		try {
			const response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "CSV Import Type",
						...importData,
					},
				},
			}).fetch()
			await fetchCsvImportTypes() // Refresh the list
			return response
		} catch (error) {
			console.error("Error creating CSV import type:", error)
			throw error
		}
	}

	const updateCsvImportType = async (importTypeId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "CSV Import Type",
					name: importTypeId,
					fieldname: updates,
				},
			}).fetch()
			await fetchCsvImportTypes() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating CSV import type:", error)
			throw error
		}
	}

	const executeCsvImport = async (importTypeId, csvData) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.execute_csv_import",
				params: {
					import_type_id: importTypeId,
					csv_data: csvData,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error executing CSV import:", error)
			throw error
		}
	}

	const fetchCsvImportFieldMappings = async () => {
		try {
			// CSV Import Field Mapping is a child table and cannot be queried directly
			// Field mappings should be accessed through their parent CSV Import Type records
			console.warn(
				"Skipping direct field mappings fetch - CSV Import Field Mapping is a child table",
			)
			csvImportFieldMappings.value = []
		} catch (error) {
			console.error("Error fetching CSV import field mappings:", error)
			csvImportFieldMappings.value = []
		}
	}

	const fetchCsvImportHistory = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "CSV Import History",
					fields: [
						"name",
						"import_type",
						"import_type_name",
						"file_name",
						"status",
						"started_at",
						"completed_at",
						"duration",
						"total_records",
						"records_processed",
						"records_failed",
						"success_rate",
						"error_message",
						"creation",
						"modified",
					],
					limit_page_length: 1000,
					order_by: "started_at desc",
				},
			}).fetch()
			csvImportHistory.value = response || []
		} catch (error) {
			console.error("Error fetching CSV import history:", error)
			// If permission error, set empty array instead of throwing
			if (error.message && error.message.includes("PermissionError")) {
				console.warn("No permission to access CSV Import History doctype")
				csvImportHistory.value = []
			} else {
				csvImportHistory.value = []
			}
		}
	}

	const fetchDataQualityMetrics = async () => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.get_data_quality_metrics",
			}).fetch()
			dataQualityMetrics.value = response || {}
			return response
		} catch (error) {
			console.error("Error fetching data quality metrics:", error)
			dataQualityMetrics.value = {}
			return {}
		}
	}

	// Actions
	const setDataPeriods = (periods) => {
		dataPeriods.value = periods
	}

	const addDataPeriod = (period) => {
		dataPeriods.value.push(period)
	}

	const updateDataPeriod = (periodName, updates) => {
		const index = dataPeriods.value.findIndex((p) => p.name === periodName)
		if (index !== -1) {
			dataPeriods.value[index] = { ...dataPeriods.value[index], ...updates }
		}
	}

	const setImportStatus = (status) => {
		importStatus.value = status
	}

	const cacheBCData = (key, data) => {
		bcDataCache.value.set(key, {
			data,
			timestamp: Date.now(),
		})
	}

	const getCachedBCData = (key) => {
		const cached = bcDataCache.value.get(key)
		if (!cached) return null

		// Check if cache is still valid (5 minutes)
		const isExpired = Date.now() - cached.timestamp > 5 * 60 * 1000
		if (isExpired) {
			bcDataCache.value.delete(key)
			return null
		}

		return cached.data
	}

	const setDataQualityMetrics = (metrics) => {
		dataQualityMetrics.value = metrics
	}

	const updateDataQualityMetric = (periodName, metric) => {
		dataQualityMetrics.value[periodName] = metric
	}

	const fetchDataPeriods = async () => {
		// Audit Engagement Data Period is a child table doctype that may not be accessible
		// Set empty array to avoid permission errors
		console.warn(
			"Skipping data periods fetch - Audit Engagement Data Period is a child table with restricted access",
		)
		setDataPeriods([])
	}

	const clearCache = () => {
		bcDataCache.value.clear()
		dataQualityMetrics.value = {}
	}

	const getDataPeriodByName = (name) => {
		return dataPeriods.value.find((period) => period.name === name)
	}

	return {
		// State
		dataPeriods,
		importStatus,
		bcDataCache,
		dashboards,
		dashboardCharts,
		dashboardDataSources,
		dashboardFilters,
		csvImportTypes,
		csvImportFieldMappings,
		csvImportHistory,
		dataQualityMetrics,

		// Getters
		activeDataPeriods,
		activeDashboards,
		publicDashboards,
		activeCsvImports,
		dataCompleteness,

		// Actions
		setDataPeriods,
		addDataPeriod,
		updateDataPeriod,
		setImportStatus,
		cacheBCData,
		getCachedBCData,
		setDataQualityMetrics,
		updateDataQualityMetric,
		fetchDataPeriods,
		fetchDashboards,
		fetchDashboardDetails,
		createDashboard,
		updateDashboard,
		fetchDashboardCharts,
		fetchDashboardDataSources,
		fetchCsvImportTypes,
		fetchCsvImportTypeDetails,
		createCsvImportType,
		updateCsvImportType,
		executeCsvImport,
		fetchCsvImportFieldMappings,
		fetchCsvImportHistory,
		fetchDataQualityMetrics,
		clearCache,
		getDataPeriodByName,
	}
})
