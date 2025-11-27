import { createResource } from "frappe-ui"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useReportsStore = defineStore("reports", {
	state: () => ({
		auditReports: [],
		boardReports: [],
		managementDashboards: [],
		dataAnalyticsDashboards: [],
		reportTemplates: [],
		customReports: [],
		currentReport: null,
		currentTemplate: null,
		previewData: null,
		exportProgress: { progress: 0, status: "idle" },
		loading: false,
		error: null,
		reportTypes: [
			{ label: "Compliance Report", value: "Compliance Report" },
			{ label: "Audit Report", value: "Audit Report" },
			{ label: "Risk Assessment", value: "Risk Assessment" },
			{ label: "Control Testing", value: "Control Testing" },
			{ label: "Finding Summary", value: "Finding Summary" },
			{ label: "Management Letter", value: "Management Letter" },
			{ label: "Remediation Report", value: "Remediation Report" },
			{ label: "Custom Report", value: "Custom Report" },
		],
		exportFormats: [
			{ label: "PDF Document", value: "pdf", icon: "FileText" },
			{ label: "Excel Workbook", value: "xlsx", icon: "Sheet" },
			{ label: "Word Document", value: "docx", icon: "FileText" },
			{ label: "CSV Data", value: "csv", icon: "Database" },
			{ label: "JSON Data", value: "json", icon: "Code" },
			{ label: "HTML Page", value: "html", icon: "Globe" },
		],
		chartTypes: [
			{ label: "Bar Chart", value: "bar", icon: "BarChart3" },
			{ label: "Line Chart", value: "line", icon: "LineChart" },
			{ label: "Pie Chart", value: "pie", icon: "PieChart" },
			{ label: "Donut Chart", value: "donut", icon: "CircleDot" },
			{ label: "Area Chart", value: "area", icon: "AreaChart" },
			{ label: "Scatter Plot", value: "scatter", icon: "ScatterChart" },
			{ label: "Gauge Chart", value: "gauge", icon: "Gauge" },
			{ label: "KPI Card", value: "kpi", icon: "Activity" },
			{ label: "Table", value: "table", icon: "Table" },
		],
		sectionTypes: [
			{ label: "Header Section", value: "header", icon: "Heading1" },
			{ label: "Text Content", value: "text", icon: "Type" },
			{ label: "Data Table", value: "table", icon: "Table" },
			{ label: "Chart/Graph", value: "chart", icon: "BarChart3" },
			{ label: "Finding List", value: "findings", icon: "AlertTriangle" },
			{ label: "Image/Logo", value: "image", icon: "Image" },
			{ label: "Page Break", value: "pagebreak", icon: "Minus" },
			{ label: "Footer Section", value: "footer", icon: "AlignLeft" },
		],
	}),

	getters: {
		activeAuditReports: (state) => {
			return state.auditReports.filter((report) => report.docstatus === 0)
		},

		activeBoardReports: (state) => {
			return state.boardReports.filter((report) => report.is_active)
		},

		activeDashboards: (state) => {
			return state.managementDashboards.filter(
				(dashboard) => dashboard.is_active,
			)
		},

		defaultDashboards: (state) => {
			return state.managementDashboards.filter(
				(dashboard) => dashboard.is_default,
			)
		},

		reportsByStatus: (state) => {
			const statusGroups = {}
			state.auditReports.forEach((report) => {
				const status = report.report_status || "Draft"
				if (!statusGroups[status]) {
					statusGroups[status] = []
				}
				statusGroups[status].push(report)
			})
			return statusGroups
		},

		boardReportsByPeriod: (state) => {
			const periodGroups = {}
			state.boardReports.forEach((report) => {
				const period = report.reporting_period || "Other"
				if (!periodGroups[period]) {
					periodGroups[period] = []
				}
				periodGroups[period].push(report)
			})
			return periodGroups
		},

		dashboardKPIs: (state) => {
			// Aggregate KPIs from all active dashboards
			const kpis = {
				totalEngagements: 0,
				completedEngagements: 0,
				totalFindings: 0,
				criticalFindings: 0,
				complianceScore: 0,
				compliantItems: 0,
			}

			state.managementDashboards.forEach((dashboard) => {
				if (dashboard.is_active && dashboard.kpi_section) {
					kpis.totalEngagements += dashboard.total_engagements || 0
					kpis.completedEngagements += dashboard.completed_engagements || 0
					kpis.totalFindings += dashboard.total_findings || 0
					kpis.criticalFindings += dashboard.critical_findings || 0
					kpis.compliantItems += dashboard.compliant_items || 0
				}
			})

			// Calculate average compliance score
			const activeDashboards = state.managementDashboards.filter(
				(d) => d.is_active && d.compliance_section,
			)
			if (activeDashboards.length > 0) {
				const totalScore = activeDashboards.reduce(
					(sum, d) => sum + (d.compliance_score || 0),
					0,
				)
				kpis.complianceScore = totalScore / activeDashboards.length
			}

			return kpis
		},

		// Enhanced report management getters
		reportStats: (state) => ({
			total: state.customReports.length,
			published: state.customReports.filter((r) => r.status === "Published")
				.length,
			draft: state.customReports.filter((r) => r.status === "Draft").length,
			templates: state.reportTemplates.length,
			scheduled: state.customReports.filter((r) => r.is_scheduled).length,
		}),

		reportsByType: (state) => {
			const grouped = {}
			state.customReports.forEach((report) => {
				const type = report.report_type || "Other"
				if (!grouped[type]) {
					grouped[type] = []
				}
				grouped[type].push(report)
			})
			return grouped
		},

		recentReports: (state) => {
			return state.customReports
				.slice()
				.sort((a, b) => new Date(b.modified) - new Date(a.modified))
				.slice(0, 5)
		},

		scheduledReports: (state) => {
			return state.customReports.filter((r) => r.is_scheduled)
		},

		activeTemplates: (state) => {
			return state.reportTemplates.filter((t) => t.is_active)
		},

		defaultTemplates: (state) => {
			return state.reportTemplates.filter((t) => t.is_default)
		},
	},

	actions: {
		async fetchAuditReports() {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "frappe.client.get_list",
					params: {
						doctype: "Audit Report",
						fields: [
							"name",
							"report_id",
							"engagement_reference",
							"report_title",
							"report_type",
							"report_date",
							"report_status",
							"prepared_by",
							"creation",
							"modified",
							"docstatus",
						],
						limit_page_length: 1000,
						order_by: "modified desc",
					},
				}).fetch()

				this.auditReports = response || []
			} catch (err) {
				console.error("Error fetching audit reports:", err)
				this.error = err.message || "Failed to fetch audit reports"
				if (err.message && err.message.includes("PermissionError")) {
					console.warn("No permission to access Audit Report doctype")
					this.auditReports = []
				}
			} finally {
				this.loading = false
			}
		},

		async fetchBoardReports() {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "frappe.client.get_list",
					params: {
						doctype: "Board Report",
						fields: [
							"name",
							"report_id",
							"report_title",
							"reporting_period",
							"report_type",
							"report_status",
							"is_active",
							"prepared_by",
							"creation",
							"modified",
						],
						limit_page_length: 1000,
						order_by: "modified desc",
					},
				}).fetch()

				this.boardReports = response || []
			} catch (err) {
				console.error("Error fetching board reports:", err)
				this.error = err.message || "Failed to fetch board reports"
				if (err.message && err.message.includes("PermissionError")) {
					console.warn("No permission to access Board Report doctype")
					this.boardReports = []
				}
			} finally {
				this.loading = false
			}
		},

		async fetchManagementDashboards() {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "frappe.client.get_list",
					params: {
						doctype: "Management Dashboard",
						fields: [
							"name",
							"dashboard_id",
							"dashboard_title",
							"dashboard_type",
							"is_active",
							"is_default",
							"time_period",
							"last_updated",
							"total_engagements",
							"completed_engagements",
							"total_findings",
							"critical_findings",
							"compliance_score",
							"compliant_items",
							"creation",
							"modified",
						],
						limit_page_length: 1000,
						order_by: "modified desc",
					},
				}).fetch()

				this.managementDashboards = response || []
			} catch (err) {
				console.error("Error fetching management dashboards:", err)
				this.error = err.message || "Failed to fetch management dashboards"
				if (err.message && err.message.includes("PermissionError")) {
					console.warn("No permission to access Management Dashboard doctype")
					this.managementDashboards = []
				}
			} finally {
				this.loading = false
			}
		},

		async fetchDataAnalyticsDashboards() {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "frappe.client.get_list",
					params: {
						doctype: "Data Analytics Dashboard",
						fields: [
							"name",
							"dashboard_id",
							"dashboard_name",
							"dashboard_type",
							"is_active",
							"is_default",
							"last_refresh_date",
							"total_views",
							"creation",
							"modified",
						],
						limit_page_length: 1000,
						order_by: "modified desc",
					},
				}).fetch()

				this.dataAnalyticsDashboards = response || []
			} catch (err) {
				console.error("Error fetching data analytics dashboards:", err)
				this.error = err.message || "Failed to fetch data analytics dashboards"
				if (err.message && err.message.includes("PermissionError")) {
					console.warn(
						"No permission to access Data Analytics Dashboard doctype",
					)
					this.dataAnalyticsDashboards = []
				}
			} finally {
				this.loading = false
			}
		},

		async fetchReportTemplates() {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "frappe.client.get_list",
					params: {
						doctype: "Report Template",
						fields: [
							"name",
							"template_id",
							"template_name",
							"template_type",
							"description",
							"is_default",
							"is_active",
							"creation",
							"modified",
						],
						limit_page_length: 1000,
						order_by: "modified desc",
					},
				}).fetch()

				this.reportTemplates = response || []
			} catch (err) {
				console.error("Error fetching report templates:", err)
				this.error = err.message || "Failed to fetch report templates"
				if (err.message && err.message.includes("PermissionError")) {
					console.warn("No permission to access Report Template doctype")
					this.reportTemplates = []
				}
			} finally {
				this.loading = false
			}
		},

		async createAuditReport(reportData) {
			try {
				const response = await createResource({
					url: "frappe.client.insert",
					params: {
						doc: {
							doctype: "Audit Report",
							...reportData,
						},
					},
				}).fetch()

				await this.fetchAuditReports()
				return response
			} catch (err) {
				console.error("Error creating audit report:", err)
				throw err
			}
		},

		async createBoardReport(reportData) {
			try {
				const response = await createResource({
					url: "frappe.client.insert",
					params: {
						doc: {
							doctype: "Board Report",
							...reportData,
						},
					},
				}).fetch()

				await this.fetchBoardReports()
				return response
			} catch (err) {
				console.error("Error creating board report:", err)
				throw err
			}
		},

		async createManagementDashboard(dashboardData) {
			try {
				const response = await createResource({
					url: "frappe.client.insert",
					params: {
						doc: {
							doctype: "Management Dashboard",
							...dashboardData,
						},
					},
				}).fetch()

				await this.fetchManagementDashboards()
				return response
			} catch (err) {
				console.error("Error creating management dashboard:", err)
				throw err
			}
		},

		async getAuditReportDetails(reportId) {
			try {
				const response = await createResource({
					url: "frappe.client.get",
					params: {
						doctype: "Audit Report",
						name: reportId,
					},
				}).fetch()

				return response
			} catch (err) {
				console.error("Error fetching audit report details:", err)
				throw err
			}
		},

		async getBoardReportDetails(reportId) {
			try {
				const response = await createResource({
					url: "frappe.client.get",
					params: {
						doctype: "Board Report",
						name: reportId,
					},
				}).fetch()

				return response
			} catch (err) {
				console.error("Error fetching board report details:", err)
				throw err
			}
		},

		async getDashboardData(dashboardId) {
			try {
				const response = await createResource({
					url: "mkaguzi.api.get_dashboard_data",
					params: {
						dashboard_name: dashboardId,
					},
				}).fetch()

				return response
			} catch (err) {
				console.error("Error fetching dashboard data:", err)
				throw err
			}
		},

		async refreshDashboard(dashboardId) {
			try {
				const response = await createResource({
					url: "mkaguzi.api.refresh_dashboard",
					params: {
						dashboard_name: dashboardId,
					},
				}).fetch()

				await this.fetchManagementDashboards()
				return response
			} catch (err) {
				console.error("Error refreshing dashboard:", err)
				throw err
			}
		},

		async createDefaultDashboards() {
			try {
				const response = await createResource({
					url: "mkaguzi.api.create_default_dashboards",
				}).fetch()

				await this.fetchManagementDashboards()
				return response
			} catch (err) {
				console.error("Error creating default dashboards:", err)
				throw err
			}
		},

		// Enhanced Custom Report Management
		async fetchCustomReports(filters = {}) {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "mkaguzi.api.reports.get_custom_reports",
					params: { filters },
				}).fetch()

				this.customReports = response || []
			} catch (err) {
				console.error("Error fetching custom reports:", err)
				this.error = err.message || "Failed to fetch custom reports"
			} finally {
				this.loading = false
			}
		},

		async createCustomReport(reportData) {
			try {
				this.loading = true
				const response = await createResource({
					url: "mkaguzi.api.reports.create_custom_report",
					params: { report: reportData },
				}).fetch()

				this.customReports.unshift(response)
				this.currentReport = response
				return response
			} catch (err) {
				console.error("Error creating custom report:", err)
				this.error = err.message
				throw err
			} finally {
				this.loading = false
			}
		},

		async updateCustomReport(reportId, updates) {
			try {
				const response = await createResource({
					url: "mkaguzi.api.reports.update_custom_report",
					params: { report_id: reportId, updates },
				}).fetch()

				const index = this.customReports.findIndex((r) => r.name === reportId)
				if (index !== -1) {
					this.customReports[index] = {
						...this.customReports[index],
						...response,
					}
				}
				if (this.currentReport?.name === reportId) {
					this.currentReport = { ...this.currentReport, ...response }
				}
				return response
			} catch (err) {
				console.error("Error updating custom report:", err)
				throw err
			}
		},

		async deleteCustomReport(reportId) {
			try {
				await createResource({
					url: "mkaguzi.api.reports.delete_custom_report",
					params: { report_id: reportId },
				}).fetch()

				this.customReports = this.customReports.filter(
					(r) => r.name !== reportId,
				)
				if (this.currentReport?.name === reportId) {
					this.currentReport = null
				}
			} catch (err) {
				console.error("Error deleting custom report:", err)
				throw err
			}
		},

		async generateReport(reportId, parameters = {}) {
			try {
				this.loading = true
				const response = await createResource({
					url: "mkaguzi.api.reports.generate_report",
					params: { report_id: reportId, parameters },
				}).fetch()

				this.previewData = response
				return response
			} catch (err) {
				console.error("Error generating report:", err)
				this.error = err.message
				throw err
			} finally {
				this.loading = false
			}
		},

		async exportReport(reportId, format, options = {}) {
			try {
				this.exportProgress = { progress: 0, status: "exporting" }

				const response = await createResource({
					url: "mkaguzi.api.reports.export_report",
					params: { report_id: reportId, format, options },
				}).fetch()

				this.exportProgress = { progress: 100, status: "completed" }

				// Download the file
				if (response.download_url) {
					const link = document.createElement("a")
					link.href = response.download_url
					link.download = response.filename || `report.${format}`
					document.body.appendChild(link)
					link.click()
					document.body.removeChild(link)
				}

				return response
			} catch (err) {
				this.exportProgress = { progress: 0, status: "failed" }
				this.error = err.message
				throw err
			}
		},

		async previewReport(reportData) {
			try {
				const validationErrors = this.validateReportStructure(reportData)
				if (validationErrors.length > 0) {
					throw new Error(`Validation errors: ${validationErrors.join(", ")}`)
				}

				this.loading = true
				const response = await createResource({
					url: "mkaguzi.api.reports.preview_report",
					params: { report: reportData },
				}).fetch()

				this.previewData = response
				return response
			} catch (err) {
				console.error("Error previewing report:", err)
				this.error = err.message
				throw err
			} finally {
				this.loading = false
			}
		},

		async scheduleReport(reportId, scheduleConfig) {
			try {
				const response = await createResource({
					url: "mkaguzi.api.reports.schedule_report",
					params: { report_id: reportId, schedule: scheduleConfig },
				}).fetch()

				const report = this.customReports.find((r) => r.name === reportId)
				if (report) {
					report.is_scheduled = true
					report.schedule_config = scheduleConfig
				}
				return response
			} catch (err) {
				console.error("Error scheduling report:", err)
				throw err
			}
		},

		async unscheduleReport(reportId) {
			try {
				await createResource({
					url: "mkaguzi.api.reports.unschedule_report",
					params: { report_id: reportId },
				}).fetch()

				const report = this.customReports.find((r) => r.name === reportId)
				if (report) {
					report.is_scheduled = false
					report.schedule_config = null
				}
			} catch (err) {
				console.error("Error unscheduling report:", err)
				throw err
			}
		},

		// Template Management
		async createReportTemplate(templateData) {
			try {
				const response = await createResource({
					url: "mkaguzi.api.reports.create_template",
					params: { template: templateData },
				}).fetch()

				this.reportTemplates.unshift(response)
				this.currentTemplate = response
				return response
			} catch (err) {
				console.error("Error creating report template:", err)
				throw err
			}
		},

		async updateReportTemplate(templateId, updates) {
			try {
				const response = await createResource({
					url: "mkaguzi.api.reports.update_template",
					params: { template_id: templateId, updates },
				}).fetch()

				const index = this.reportTemplates.findIndex(
					(t) => t.name === templateId,
				)
				if (index !== -1) {
					this.reportTemplates[index] = {
						...this.reportTemplates[index],
						...response,
					}
				}
				return response
			} catch (err) {
				console.error("Error updating report template:", err)
				throw err
			}
		},

		async duplicateTemplate(templateId, newName) {
			try {
				const response = await createResource({
					url: "mkaguzi.api.reports.duplicate_template",
					params: { template_id: templateId, new_name: newName },
				}).fetch()

				this.reportTemplates.unshift(response)
				return response
			} catch (err) {
				console.error("Error duplicating template:", err)
				throw err
			}
		},

		// Data fetching utilities
		async fetchSectionData(sectionConfig) {
			try {
				return await createResource({
					url: "mkaguzi.api.reports.fetch_section_data",
					params: { config: sectionConfig },
				}).fetch()
			} catch (err) {
				console.error("Error fetching section data:", err)
				throw err
			}
		},

		async fetchAvailableFields(doctype) {
			try {
				return await createResource({
					url: "mkaguzi.api.reports.get_doctype_fields",
					params: { doctype },
				}).fetch()
			} catch (err) {
				console.error("Error fetching doctype fields:", err)
				throw err
			}
		},

		async fetchFilterOptions(doctype, field) {
			try {
				return await createResource({
					url: "mkaguzi.api.reports.get_field_options",
					params: { doctype, field },
				}).fetch()
			} catch (err) {
				console.error("Error fetching field options:", err)
				throw err
			}
		},

		// Utility functions
		validateReportStructure(reportData) {
			const errors = []

			if (!reportData.title || reportData.title.trim() === "") {
				errors.push("Report title is required")
			}

			if (!reportData.report_type) {
				errors.push("Report type is required")
			}

			if (!reportData.sections || reportData.sections.length === 0) {
				errors.push("Report must have at least one section")
			}

			// Validate sections
			if (reportData.sections) {
				reportData.sections.forEach((section, index) => {
					if (!section.type) {
						errors.push(`Section ${index + 1}: Section type is required`)
					}

					if (section.type === "chart" && !section.chart_config) {
						errors.push(`Section ${index + 1}: Chart configuration is required`)
					}

					if (section.type === "table" && !section.data_source) {
						errors.push(
							`Section ${index + 1}: Data source is required for table`,
						)
					}
				})
			}

			return errors
		},

		formatReportSize(size) {
			if (!size) return "N/A"
			const units = ["B", "KB", "MB", "GB"]
			let i = 0
			while (size >= 1024 && i < units.length - 1) {
				size /= 1024
				i++
			}
			return `${size.toFixed(1)} ${units[i]}`
		},

		getReportIcon(reportType) {
			const icons = {
				"Compliance Report": "Shield",
				"Audit Report": "Search",
				"Risk Assessment": "AlertTriangle",
				"Control Testing": "CheckCircle2",
				"Finding Summary": "List",
				"Management Letter": "Mail",
				"Remediation Report": "Tool",
				"Custom Report": "Settings",
			}
			return icons[reportType] || "FileText"
		},

		getStatusColor(status) {
			const colors = {
				Draft: "orange",
				Published: "green",
				Archived: "gray",
				Scheduled: "blue",
			}
			return colors[status] || "gray"
		},

		searchReports(query) {
			if (!query.trim()) return this.customReports

			const lowerQuery = query.toLowerCase()
			return this.customReports.filter(
				(report) =>
					report.title?.toLowerCase().includes(lowerQuery) ||
					report.description?.toLowerCase().includes(lowerQuery) ||
					report.report_type?.toLowerCase().includes(lowerQuery) ||
					report.tags?.some((tag) => tag.toLowerCase().includes(lowerQuery)),
			)
		},

		searchTemplates(query) {
			if (!query.trim()) return this.reportTemplates

			const lowerQuery = query.toLowerCase()
			return this.reportTemplates.filter(
				(template) =>
					template.template_name?.toLowerCase().includes(lowerQuery) ||
					template.description?.toLowerCase().includes(lowerQuery) ||
					template.template_type?.toLowerCase().includes(lowerQuery),
			)
		},

		// Getters
		getReportById(reportId) {
			return this.customReports.find((r) => r.name === reportId)
		},

		getTemplateById(templateId) {
			return this.reportTemplates.find((t) => t.name === templateId)
		},

		// Reset functions
		resetError() {
			this.error = null
		},

		resetPreviewData() {
			this.previewData = null
		},

		resetExportProgress() {
			this.exportProgress = { progress: 0, status: "idle" }
		},

		setCurrentReport(report) {
			this.currentReport = report
		},

		setCurrentTemplate(template) {
			this.currentTemplate = template
		},
	},
})
