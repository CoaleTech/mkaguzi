import { createResource } from "frappe-ui"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useDataStore = defineStore("data", () => {
	// State
	const dataPeriods = ref([])

	// Data Management State
	const dashboards = ref([])
	const dashboardCharts = ref([])
	const dashboardDataSources = ref([])
	const dashboardFilters = ref([])
	const dataQualityMetrics = ref({})

	// Data Management Getters
	const activeDashboards = computed(() => {
		return dashboards.value.filter((d) => d.is_active)
	})

	const publicDashboards = computed(() => {
		return dashboards.value.filter((d) => d.dashboard_type === "Public")
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
		dataQualityMetrics.value = {}
	}

	const getDataPeriodByName = (name) => {
		return dataPeriods.value.find((period) => period.name === name)
	}

	return {
		// State
		dataPeriods,
		dashboards,
		dashboardCharts,
		dashboardDataSources,
		dashboardFilters,
		dataQualityMetrics,

		// Getters
		activeDataPeriods,
		activeDashboards,
		publicDashboards,
		dataCompleteness,

		// Actions
		setDataPeriods,
		addDataPeriod,
		updateDataPeriod,
		setDataQualityMetrics,
		updateDataQualityMetric,
		fetchDataPeriods,
		fetchDashboards,
		fetchDashboardDetails,
		createDashboard,
		updateDashboard,
		fetchDashboardCharts,
		fetchDashboardDataSources,
		fetchDataQualityMetrics,
		clearCache,
		getDataPeriodByName,
	}
})
