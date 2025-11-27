import { createResource } from "frappe-ui"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useDashboardStore = defineStore("dashboard", () => {
	// State
	const dashboards = ref([])
	const activeDashboard = ref(null)
	const widgets = ref([])
	const loading = ref({
		dashboards: false,
		widgets: false,
		save: false,
		data: false,
	})
	const error = ref(null)

	// Widget Types Configuration
	const widgetTypes = ref([
		{
			id: "kpi-card",
			name: "KPI Card",
			icon: "TrendingUpIcon",
			category: "metrics",
			description: "Display key performance indicators",
			defaultSize: { width: 2, height: 2 },
			configSchema: [
				{ field: "title", label: "Title", type: "text", required: true },
				{ field: "metric", label: "Metric", type: "select", required: true },
				{
					field: "format",
					label: "Format",
					type: "select",
					options: ["number", "currency", "percentage"],
				},
				{ field: "trend", label: "Show Trend", type: "boolean" },
				{ field: "comparison", label: "Comparison Period", type: "select" },
			],
		},
		{
			id: "chart",
			name: "Chart",
			icon: "BarChartIcon",
			category: "charts",
			description: "Various chart types for data visualization",
			defaultSize: { width: 4, height: 3 },
			configSchema: [
				{ field: "title", label: "Chart Title", type: "text", required: true },
				{
					field: "chart_type",
					label: "Chart Type",
					type: "select",
					required: true,
					options: ["bar", "line", "pie", "donut", "area", "scatter"],
				},
				{
					field: "data_source",
					label: "Data Source",
					type: "select",
					required: true,
				},
				{ field: "x_field", label: "X-Axis Field", type: "select" },
				{ field: "y_field", label: "Y-Axis Field", type: "select" },
				{ field: "group_by", label: "Group By", type: "select" },
				{
					field: "aggregation",
					label: "Aggregation",
					type: "select",
					options: ["count", "sum", "avg", "min", "max"],
				},
			],
		},
		{
			id: "table",
			name: "Data Table",
			icon: "TableIcon",
			category: "data",
			description: "Tabular data display with sorting and filtering",
			defaultSize: { width: 6, height: 4 },
			configSchema: [
				{ field: "title", label: "Table Title", type: "text", required: true },
				{
					field: "data_source",
					label: "Data Source",
					type: "select",
					required: true,
				},
				{ field: "columns", label: "Columns", type: "multiselect" },
				{ field: "filters", label: "Filters", type: "json" },
				{ field: "sort_by", label: "Sort By", type: "select" },
				{
					field: "page_size",
					label: "Rows Per Page",
					type: "number",
					default: 10,
				},
			],
		},
		{
			id: "gauge",
			name: "Gauge",
			icon: "GaugeIcon",
			category: "metrics",
			description: "Progress or performance gauge",
			defaultSize: { width: 3, height: 3 },
			configSchema: [
				{ field: "title", label: "Title", type: "text", required: true },
				{ field: "metric", label: "Metric", type: "select", required: true },
				{ field: "min_value", label: "Min Value", type: "number", default: 0 },
				{
					field: "max_value",
					label: "Max Value",
					type: "number",
					default: 100,
				},
				{ field: "threshold_ranges", label: "Threshold Ranges", type: "json" },
			],
		},
		{
			id: "list",
			name: "List Widget",
			icon: "ListIcon",
			category: "data",
			description: "Recent items or activity feed",
			defaultSize: { width: 3, height: 4 },
			configSchema: [
				{ field: "title", label: "Title", type: "text", required: true },
				{
					field: "data_source",
					label: "Data Source",
					type: "select",
					required: true,
				},
				{ field: "display_field", label: "Display Field", type: "select" },
				{ field: "subtitle_field", label: "Subtitle Field", type: "select" },
				{ field: "limit", label: "Item Limit", type: "number", default: 5 },
				{ field: "show_icons", label: "Show Icons", type: "boolean" },
			],
		},
		{
			id: "progress-bar",
			name: "Progress Bar",
			icon: "ActivityIcon",
			category: "metrics",
			description: "Progress tracking for goals or tasks",
			defaultSize: { width: 4, height: 2 },
			configSchema: [
				{ field: "title", label: "Title", type: "text", required: true },
				{
					field: "current_value",
					label: "Current Value",
					type: "select",
					required: true,
				},
				{ field: "target_value", label: "Target Value", type: "select" },
				{
					field: "format",
					label: "Format",
					type: "select",
					options: ["number", "percentage"],
				},
				{ field: "color_scheme", label: "Color Scheme", type: "select" },
			],
		},
		{
			id: "heatmap",
			name: "Heatmap",
			icon: "GridIcon",
			category: "charts",
			description: "Calendar or matrix heatmap visualization",
			defaultSize: { width: 6, height: 4 },
			configSchema: [
				{ field: "title", label: "Title", type: "text", required: true },
				{
					field: "data_source",
					label: "Data Source",
					type: "select",
					required: true,
				},
				{ field: "date_field", label: "Date Field", type: "select" },
				{ field: "value_field", label: "Value Field", type: "select" },
				{ field: "color_scale", label: "Color Scale", type: "select" },
			],
		},
		{
			id: "stat-grid",
			name: "Stats Grid",
			icon: "GridIcon",
			category: "metrics",
			description: "Grid of statistics and metrics",
			defaultSize: { width: 4, height: 3 },
			configSchema: [
				{ field: "title", label: "Title", type: "text", required: true },
				{ field: "stats", label: "Statistics", type: "json", required: true },
				{
					field: "layout",
					label: "Layout",
					type: "select",
					options: ["2x2", "3x2", "4x2"],
				},
				{ field: "show_changes", label: "Show Changes", type: "boolean" },
			],
		},
	])

	// Data Sources Configuration
	const dataSources = ref([
		{
			id: "audit_findings",
			name: "Audit Findings",
			doctype: "Audit Finding",
			fields: [
				{ name: "finding_title", label: "Finding Title", type: "Data" },
				{ name: "finding_type", label: "Finding Type", type: "Select" },
				{ name: "severity", label: "Severity", type: "Select" },
				{ name: "status", label: "Status", type: "Select" },
				{ name: "creation", label: "Created On", type: "Datetime" },
				{ name: "due_date", label: "Due Date", type: "Date" },
				{ name: "department", label: "Department", type: "Link" },
				{ name: "risk_level", label: "Risk Level", type: "Select" },
			],
		},
		{
			id: "control_procedures",
			name: "Control Procedures",
			doctype: "Control Procedure",
			fields: [
				{ name: "procedure_name", label: "Procedure Name", type: "Data" },
				{ name: "control_type", label: "Control Type", type: "Select" },
				{ name: "frequency", label: "Frequency", type: "Select" },
				{ name: "effectiveness", label: "Effectiveness", type: "Select" },
				{ name: "last_tested", label: "Last Tested", type: "Date" },
				{ name: "owner", label: "Owner", type: "Link" },
				{ name: "process_area", label: "Process Area", type: "Link" },
			],
		},
		{
			id: "audit_tests",
			name: "Audit Tests",
			doctype: "Audit Test",
			fields: [
				{ name: "test_name", label: "Test Name", type: "Data" },
				{ name: "test_type", label: "Test Type", type: "Select" },
				{ name: "status", label: "Status", type: "Select" },
				{ name: "completion_date", label: "Completion Date", type: "Date" },
				{ name: "result", label: "Result", type: "Select" },
				{ name: "sample_size", label: "Sample Size", type: "Int" },
				{ name: "errors_found", label: "Errors Found", type: "Int" },
			],
		},
		{
			id: "audit_plans",
			name: "Audit Plans",
			doctype: "Audit Plan",
			fields: [
				{ name: "plan_name", label: "Plan Name", type: "Data" },
				{ name: "audit_type", label: "Audit Type", type: "Select" },
				{ name: "status", label: "Status", type: "Select" },
				{ name: "start_date", label: "Start Date", type: "Date" },
				{ name: "end_date", label: "End Date", type: "Date" },
				{
					name: "completion_percentage",
					label: "Completion %",
					type: "Percent",
				},
				{ name: "auditor", label: "Auditor", type: "Link" },
			],
		},
	])

	// Resources
	const dashboardResource = createResource({
		url: "mkaguzi.api.dashboards.get_dashboards",
		auto: false,
	})

	const widgetDataResource = createResource({
		url: "mkaguzi.api.dashboards.get_widget_data",
		auto: false,
	})

	// Actions
	const fetchDashboards = async (filters = {}) => {
		try {
			loading.value.dashboards = true
			error.value = null

			const response = await dashboardResource.fetch({
				params: { filters },
			})

			dashboards.value = response || []
			return response
		} catch (err) {
			error.value = err.message
			console.error("Failed to fetch dashboards:", err)
		} finally {
			loading.value.dashboards = false
		}
	}

	const createDashboard = async (dashboardData) => {
		try {
			loading.value.save = true
			error.value = null

			const response = await createResource({
				url: "mkaguzi.api.dashboards.create_dashboard",
				auto: false,
			}).fetch({
				params: dashboardData,
			})

			if (response) {
				activeDashboard.value = response
				await fetchDashboards()
				return response
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to create dashboard:", err)
			throw err
		} finally {
			loading.value.save = false
		}
	}

	const updateDashboard = async (dashboardId, updates) => {
		try {
			loading.value.save = true
			error.value = null

			const response = await createResource({
				url: "mkaguzi.api.dashboards.update_dashboard",
				auto: false,
			}).fetch({
				params: {
					dashboard_id: dashboardId,
					...updates,
				},
			})

			if (response) {
				if (activeDashboard.value?.name === dashboardId) {
					activeDashboard.value = { ...activeDashboard.value, ...response }
				}
				await fetchDashboards()
				return response
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to update dashboard:", err)
			throw err
		} finally {
			loading.value.save = false
		}
	}

	const deleteDashboard = async (dashboardId) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.dashboards.delete_dashboard",
				auto: false,
			}).fetch({
				params: { dashboard_id: dashboardId },
			})

			if (response) {
				dashboards.value = dashboards.value.filter(
					(d) => d.name !== dashboardId,
				)
				if (activeDashboard.value?.name === dashboardId) {
					activeDashboard.value = null
				}
				return response
			}
		} catch (err) {
			error.value = err.message
			console.error("Failed to delete dashboard:", err)
			throw err
		}
	}

	const addWidget = async (dashboardId, widgetData) => {
		try {
			loading.value.save = true
			error.value = null

			const response = await createResource({
				url: "mkaguzi.api.dashboards.add_widget",
				auto: false,
			}).fetch({
				params: {
					dashboard_id: dashboardId,
					widget_data: widgetData,
				},
			})

			if (response && activeDashboard.value?.name === dashboardId) {
				activeDashboard.value.widgets = [
					...(activeDashboard.value.widgets || []),
					response,
				]
			}

			return response
		} catch (err) {
			error.value = err.message
			console.error("Failed to add widget:", err)
			throw err
		} finally {
			loading.value.save = false
		}
	}

	const updateWidget = async (widgetId, updates) => {
		try {
			loading.value.save = true
			error.value = null

			const response = await createResource({
				url: "mkaguzi.api.dashboards.update_widget",
				auto: false,
			}).fetch({
				params: {
					widget_id: widgetId,
					...updates,
				},
			})

			if (response && activeDashboard.value) {
				const widgetIndex = activeDashboard.value.widgets.findIndex(
					(w) => w.name === widgetId,
				)
				if (widgetIndex !== -1) {
					activeDashboard.value.widgets[widgetIndex] = {
						...activeDashboard.value.widgets[widgetIndex],
						...response,
					}
				}
			}

			return response
		} catch (err) {
			error.value = err.message
			console.error("Failed to update widget:", err)
			throw err
		} finally {
			loading.value.save = false
		}
	}

	const removeWidget = async (dashboardId, widgetId) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.dashboards.remove_widget",
				auto: false,
			}).fetch({
				params: {
					dashboard_id: dashboardId,
					widget_id: widgetId,
				},
			})

			if (response && activeDashboard.value?.name === dashboardId) {
				activeDashboard.value.widgets = activeDashboard.value.widgets.filter(
					(w) => w.name !== widgetId,
				)
			}

			return response
		} catch (err) {
			error.value = err.message
			console.error("Failed to remove widget:", err)
			throw err
		}
	}

	const getWidgetData = async (widgetId, config = {}) => {
		try {
			loading.value.data = true
			error.value = null

			const response = await widgetDataResource.fetch({
				params: {
					widget_id: widgetId,
					config: config,
				},
			})

			return response
		} catch (err) {
			error.value = err.message
			console.error("Failed to fetch widget data:", err)
			throw err
		} finally {
			loading.value.data = false
		}
	}

	const refreshDashboardData = async (dashboardId) => {
		try {
			loading.value.data = true

			const dashboard =
				dashboards.value.find((d) => d.name === dashboardId) ||
				activeDashboard.value
			if (!dashboard?.widgets) return

			// Fetch data for all widgets in parallel
			const widgetDataPromises = dashboard.widgets.map(async (widget) => {
				try {
					const data = await getWidgetData(widget.name, widget.config)
					return { widgetId: widget.name, data }
				} catch (err) {
					console.error(
						`Failed to refresh data for widget ${widget.name}:`,
						err,
					)
					return { widgetId: widget.name, error: err.message }
				}
			})

			const results = await Promise.all(widgetDataPromises)

			// Update widget data
			results.forEach((result) => {
				if (activeDashboard.value) {
					const widgetIndex = activeDashboard.value.widgets.findIndex(
						(w) => w.name === result.widgetId,
					)
					if (widgetIndex !== -1) {
						activeDashboard.value.widgets[widgetIndex].data = result.data
						activeDashboard.value.widgets[widgetIndex].last_updated =
							new Date().toISOString()
					}
				}
			})

			return results
		} catch (err) {
			error.value = err.message
			console.error("Failed to refresh dashboard data:", err)
		} finally {
			loading.value.data = false
		}
	}

	const duplicateDashboard = async (dashboardId) => {
		try {
			loading.value.save = true

			const originalDashboard = dashboards.value.find(
				(d) => d.name === dashboardId,
			)
			if (!originalDashboard) throw new Error("Dashboard not found")

			const duplicateData = {
				...originalDashboard,
				name: `${originalDashboard.name} (Copy)`,
				title: `${originalDashboard.title} (Copy)`,
			}
			delete duplicateData.name

			const response = await createDashboard(duplicateData)
			return response
		} catch (err) {
			error.value = err.message
			console.error("Failed to duplicate dashboard:", err)
			throw err
		}
	}

	const exportDashboard = async (dashboardId, format = "json") => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.dashboards.export_dashboard",
				auto: false,
			}).fetch({
				params: {
					dashboard_id: dashboardId,
					format: format,
				},
			})

			if (response?.download_url) {
				// Trigger download
				const link = document.createElement("a")
				link.href = response.download_url
				link.download = `dashboard_${dashboardId}.${format}`
				link.click()
			}

			return response
		} catch (err) {
			error.value = err.message
			console.error("Failed to export dashboard:", err)
			throw err
		}
	}

	// Computed
	const dashboardsByCategory = computed(() => {
		const categories = {}
		dashboards.value.forEach((dashboard) => {
			const category = dashboard.category || "General"
			if (!categories[category]) {
				categories[category] = []
			}
			categories[category].push(dashboard)
		})
		return categories
	})

	const widgetsByCategory = computed(() => {
		const categories = {}
		widgetTypes.value.forEach((widgetType) => {
			const category = widgetType.category || "other"
			if (!categories[category]) {
				categories[category] = []
			}
			categories[category].push(widgetType)
		})
		return categories
	})

	const availableDataSources = computed(() => dataSources.value)

	const getDataSourceFields = (dataSourceId) => {
		const source = dataSources.value.find((ds) => ds.id === dataSourceId)
		return source?.fields || []
	}

	const getWidgetType = (widgetTypeId) => {
		return widgetTypes.value.find((wt) => wt.id === widgetTypeId)
	}

	// Initialize
	const initialize = async () => {
		await fetchDashboards()
	}

	return {
		// State
		dashboards,
		activeDashboard,
		widgets,
		loading,
		error,
		widgetTypes,
		dataSources,

		// Actions
		fetchDashboards,
		createDashboard,
		updateDashboard,
		deleteDashboard,
		addWidget,
		updateWidget,
		removeWidget,
		getWidgetData,
		refreshDashboardData,
		duplicateDashboard,
		exportDashboard,
		initialize,

		// Computed
		dashboardsByCategory,
		widgetsByCategory,
		availableDataSources,

		// Helper methods
		getDataSourceFields,
		getWidgetType,
	}
})
