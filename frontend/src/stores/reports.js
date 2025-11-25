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
		loading: false,
		error: null,
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
	},
})
