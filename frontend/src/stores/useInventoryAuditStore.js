import { call, createResource } from "frappe-ui"
import { defineStore } from "pinia"

export const useInventoryAuditStore = defineStore("inventoryAudit", {
	state: () => ({
		// Inventory Items
		items: [],
		activeItem: null,
		itemsLoading: false,
		itemsTotalCount: 0,
		itemsPage: 1,
		itemsPageSize: 50,

		// Audit Plans
		plans: [],
		activePlan: null,
		plansLoading: false,
		plansTotalCount: 0,
		plansPage: 1,
		plansPageSize: 50,

		// Stock Take Sessions
		sessions: [],
		activeSession: null,
		sessionsLoading: false,
		sessionsTotalCount: 0,
		sessionsPage: 1,
		sessionsPageSize: 50,

		// Variance Reconciliation Cases
		varianceCases: [],
		activeVarianceCase: null,
		varianceCasesLoading: false,
		varianceCasesTotalCount: 0,
		varianceCasesPage: 1,
		varianceCasesPageSize: 50,

		// Stock Take Audits
		returnAudits: [],
		activeReturnAudit: null,
		returnAuditsLoading: false,
		returnAuditsTotalCount: 0,
		returnAuditsPage: 1,
		returnAuditsPageSize: 50,

		// Stock Take Issues
		issues: [],
		activeIssue: null,
		issuesLoading: false,
		issuesTotalCount: 0,
		issuesPage: 1,
		issuesPageSize: 50,

		// Compliance Scorecards
		scorecards: [],
		activeScorecard: null,
		scorecardsLoading: false,
		scorecardHistory: [],

		// Dashboard statistics
		dashboardStats: {
			plans: { total: 0, active: 0, completed: 0 },
			sessions: { total: 0, in_progress: 0 },
			variance_cases: { total: 0, open: 0, sla_breached: 0 },
			issues: { total: 0, open: 0 },
			items: { total: 0, active: 0 },
			avg_compliance_score: 0,
		},
		dashboardLoading: false,

		// Filters
		filters: {
			plans: {},
			sessions: {},
			varianceCases: {},
			returnAudits: {},
			issues: {},
			items: {},
		},

		// UI State
		currentView: "dashboard",
		isLoading: false,
		error: null,

		// Options for dropdowns
		auditPeriodOptions: [
			{ value: "Daily", label: "Daily" },
			{ value: "Weekly", label: "Weekly" },
			{ value: "Monthly", label: "Monthly" },
			{ value: "Quarterly", label: "Quarterly" },
			{ value: "Ad Hoc", label: "Ad Hoc" },
		],
		auditScopeOptions: [
			{ value: "Full Warehouse", label: "Full Warehouse" },
			{ value: "Category", label: "Category" },
			{ value: "ABC Class", label: "ABC Class" },
			{ value: "High Value Items", label: "High Value Items" },
			{ value: "Fast Moving Items", label: "Fast Moving Items" },
			{ value: "Random Sample", label: "Random Sample" },
		],
		countTypeOptions: [
			{ value: "Full Physical Count", label: "Full Physical Count" },
			{ value: "Cycle Count", label: "Cycle Count" },
			{ value: "Random Sample", label: "Random Sample" },
			{ value: "Spot Check", label: "Spot Check" },
		],
		rootCauseOptions: [
			{ value: "Miscount", label: "Miscount" },
			{ value: "Theft", label: "Theft" },
			{ value: "Misplacement", label: "Misplacement" },
			{ value: "Wrong UOM", label: "Wrong UOM" },
			{ value: "Unrecorded Sales", label: "Unrecorded Sales" },
			{ value: "Unrecorded Receiving", label: "Unrecorded Receiving" },
			{ value: "Wrong Posting", label: "Wrong Posting" },
			{ value: "Expired/Damaged Stock", label: "Expired/Damaged Stock" },
			{ value: "System Error", label: "System Error" },
			{ value: "Data Entry Error", label: "Data Entry Error" },
		],
		issueTypeOptions: [
			{ value: "Count Discrepancy", label: "Count Discrepancy" },
			{ value: "Missing Documentation", label: "Missing Documentation" },
			{ value: "Process Violation", label: "Process Violation" },
			{ value: "System Access Issue", label: "System Access Issue" },
			{ value: "Equipment Failure", label: "Equipment Failure" },
			{ value: "Staff Unavailability", label: "Staff Unavailability" },
			{ value: "Location Access", label: "Location Access" },
			{ value: "Item Identification", label: "Item Identification" },
			{ value: "Condition Issue", label: "Condition Issue" },
			{ value: "Other", label: "Other" },
		],
		statusColors: {
			Planned: "blue",
			"In Progress": "yellow",
			Completed: "green",
			"On Hold": "gray",
			Cancelled: "red",
			New: "blue",
			"Under Investigation": "yellow",
			"Resolution Proposed": "orange",
			Resolved: "green",
			Closed: "gray",
			Open: "yellow",
			"Pending Approval": "orange",
			Approved: "green",
			Rejected: "red",
		},
		gradeColors: {
			A: "green",
			B: "blue",
			C: "yellow",
			D: "orange",
			F: "red",
		},
	}),

	getters: {
		// Plan getters
		getPlanById: (state) => (id) => {
			return state.plans.find((plan) => plan.name === id)
		},

		getActivePlans: (state) => {
			return state.plans.filter((plan) =>
				["Planned", "In Progress"].includes(plan.status),
			)
		},

		// Session getters
		getSessionById: (state) => (id) => {
			return state.sessions.find((session) => session.name === id)
		},

		getSessionsByPlan: (state) => (planId) => {
			return state.sessions.filter((session) => session.audit_plan === planId)
		},

		getPendingSignoffSessions: (state) => {
			return state.sessions.filter(
				(session) =>
					session.status === "Completed" &&
					(!session.team_signoff ||
						!session.supervisor_signoff ||
						!session.auditor_signoff),
			)
		},

		// Variance case getters
		getVarianceCaseById: (state) => (id) => {
			return state.varianceCases.find((vc) => vc.name === id)
		},

		getOpenVarianceCases: (state) => {
			return state.varianceCases.filter((vc) =>
				["New", "Under Investigation", "Resolution Proposed"].includes(
					vc.status,
				),
			)
		},

		getSlaBreachedCases: (state) => {
			return state.varianceCases.filter((vc) => vc.is_sla_breached)
		},

		// Issues getters
		getIssueById: (state) => (id) => {
			return state.issues.find((issue) => issue.name === id)
		},

		getOpenIssues: (state) => {
			return state.issues.filter((issue) =>
				["Open", "In Progress"].includes(issue.status),
			)
		},

		// Scorecard getters
		getScorecardById: (state) => (id) => {
			return state.scorecards.find((sc) => sc.name === id)
		},

		getScorecardByPlan: (state) => (planId) => {
			return state.scorecards.find((sc) => sc.audit_plan === planId)
		},

		// Dashboard metrics
		getComplianceOverview: (state) => {
			const scorecards = state.scorecards
			if (scorecards.length === 0) {
				return { avgScore: 0, gradeDistribution: {} }
			}

			const avgScore =
				scorecards.reduce(
					(sum, sc) => sum + (sc.overall_compliance_score || 0),
					0,
				) / scorecards.length

			const gradeDistribution = scorecards.reduce((acc, sc) => {
				const grade = sc.grade || "N/A"
				acc[grade] = (acc[grade] || 0) + 1
				return acc
			}, {})

			return { avgScore: Math.round(avgScore), gradeDistribution }
		},
	},

	actions: {
		// ========== Dashboard Actions ==========
		async loadDashboardStats() {
			this.dashboardLoading = true
			this.error = null

			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.get_inventory_dashboard_stats",
				)
				this.dashboardStats = result
			} catch (error) {
				this.error = `Failed to load dashboard stats: ${error.message}`
				console.error("Error loading dashboard stats:", error)
			} finally {
				this.dashboardLoading = false
			}
		},

		// ========== Inventory Items Actions ==========
		async loadItems(filters = {}, page = 1, pageSize = 50) {
			this.itemsLoading = true
			this.error = null

			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.get_inventory_items",
					{
						filters: JSON.stringify(filters),
						page,
						page_size: pageSize,
					},
				)
				this.items = result.items
				this.itemsTotalCount = result.total_count
				this.itemsPage = result.page
				this.itemsPageSize = result.page_size
				this.filters.items = filters
			} catch (error) {
				this.error = `Failed to load items: ${error.message}`
				console.error("Error loading items:", error)
			} finally {
				this.itemsLoading = false
			}
		},

		async getItemImportTemplate() {
			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.get_item_import_template",
				)
				return result
			} catch (error) {
				this.error = `Failed to get import template: ${error.message}`
				throw error
			}
		},

		async importItemsFromCSV(content) {
			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.import_items_from_csv",
					{ file_content: JSON.stringify({ content }) },
				)
				// Reload items after import
				await this.loadItems(this.filters.items)
				return result
			} catch (error) {
				this.error = `Failed to import items: ${error.message}`
				throw error
			}
		},

		// ========== Audit Plans Actions ==========
		async loadPlans(filters = {}, page = 1, pageSize = 50) {
			this.plansLoading = true
			this.error = null

			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.get_inventory_audit_plans",
					{
						filters: JSON.stringify(filters),
						page,
						page_size: pageSize,
					},
				)
				this.plans = result.plans
				this.plansTotalCount = result.total_count
				this.plansPage = result.page
				this.plansPageSize = result.page_size
				this.filters.plans = filters
			} catch (error) {
				this.error = `Failed to load plans: ${error.message}`
				console.error("Error loading plans:", error)
			} finally {
				this.plansLoading = false
			}
		},

		async createPlan(planData) {
			try {
				const doc = await call("frappe.client.insert", {
					doc: {
						doctype: "Inventory Audit Plan",
						...planData,
					},
				})
				await this.loadPlans(this.filters.plans)
				return doc
			} catch (error) {
				this.error = `Failed to create plan: ${error.message}`
				throw error
			}
		},

		async updatePlan(planName, updates) {
			try {
				await call("frappe.client.set_value", {
					doctype: "Inventory Audit Plan",
					name: planName,
					fieldname: updates,
				})
				await this.loadPlans(this.filters.plans)
			} catch (error) {
				this.error = `Failed to update plan: ${error.message}`
				throw error
			}
		},

		async loadPlanDetail(planName) {
			this.plansLoading = true
			this.error = null

			try {
				const doc = await call("frappe.client.get", {
					doctype: "Inventory Audit Plan",
					name: planName,
				})
				this.activePlan = doc
				return doc
			} catch (error) {
				this.error = `Failed to load plan: ${error.message}`
				console.error("Error loading plan detail:", error)
				throw error
			} finally {
				this.plansLoading = false
			}
		},

		async getSessionsByPlanId(planId) {
			try {
				const result = await call("frappe.client.get_list", {
					doctype: "Stock Take Session",
					filters: { audit_plan: planId },
					fields: [
						"name",
						"session_name",
						"session_type",
						"status",
						"scheduled_date",
						"warehouse",
					],
					order_by: "scheduled_date desc",
				})
				return result
			} catch (error) {
				console.error("Error loading sessions for plan:", error)
				return []
			}
		},

		// ========== Stock Take Sessions Actions ==========
		async loadSessions(filters = {}, page = 1, pageSize = 50) {
			this.sessionsLoading = true
			this.error = null

			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.get_stock_take_sessions",
					{
						filters: JSON.stringify(filters),
						page,
						page_size: pageSize,
					},
				)
				this.sessions = result.sessions
				this.sessionsTotalCount = result.total_count
				this.sessionsPage = result.page
				this.sessionsPageSize = result.page_size
				this.filters.sessions = filters
			} catch (error) {
				this.error = `Failed to load sessions: ${error.message}`
				console.error("Error loading sessions:", error)
			} finally {
				this.sessionsLoading = false
			}
		},

		async createSession(sessionData) {
			try {
				const doc = await call("frappe.client.insert", {
					doc: {
						doctype: "Stock Take Session",
						...sessionData,
					},
				})
				await this.loadSessions(this.filters.sessions)
				return doc
			} catch (error) {
				this.error = `Failed to create session: ${error.message}`
				throw error
			}
		},

		async calculateVariance(sessionName) {
			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.calculate_count_variance",
					{ session_name: sessionName },
				)
				await this.loadSessions(this.filters.sessions)
				return result
			} catch (error) {
				this.error = `Failed to calculate variance: ${error.message}`
				throw error
			}
		},

		async loadSessionDetail(sessionName) {
			this.sessionsLoading = true
			this.error = null

			try {
				const doc = await call("frappe.client.get", {
					doctype: "Stock Take Session",
					name: sessionName,
				})
				this.activeSession = doc
				return doc
			} catch (error) {
				this.error = `Failed to load session: ${error.message}`
				console.error("Error loading session detail:", error)
				throw error
			} finally {
				this.sessionsLoading = false
			}
		},

		async getVarianceCasesBySession(sessionName) {
			try {
				const result = await call("frappe.client.get_list", {
					doctype: "Inventory Variance Case",
					filters: { stock_take_session: sessionName },
					fields: [
						"name",
						"item_code",
						"item_name",
						"status",
						"variance_qty",
						"variance_value",
						"priority",
					],
				})
				return result
			} catch (error) {
				console.error("Error loading variance cases for session:", error)
				return []
			}
		},

		// ========== Variance Cases Actions ==========
		async loadVarianceCases(filters = {}, page = 1, pageSize = 50) {
			this.varianceCasesLoading = true
			this.error = null

			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.get_variance_cases",
					{
						filters: JSON.stringify(filters),
						page,
						page_size: pageSize,
					},
				)
				this.varianceCases = result.cases
				this.varianceCasesTotalCount = result.total_count
				this.varianceCasesPage = result.page
				this.varianceCasesPageSize = result.page_size
				this.filters.varianceCases = filters
			} catch (error) {
				this.error = `Failed to load variance cases: ${error.message}`
				console.error("Error loading variance cases:", error)
			} finally {
				this.varianceCasesLoading = false
			}
		},

		async updateVarianceCase(caseName, updates) {
			try {
				await call("frappe.client.set_value", {
					doctype: "Variance Reconciliation Case",
					name: caseName,
					fieldname: updates,
				})
				await this.loadVarianceCases(this.filters.varianceCases)
			} catch (error) {
				this.error = `Failed to update variance case: ${error.message}`
				throw error
			}
		},

		async loadVarianceCaseDetail(caseName) {
			this.varianceCasesLoading = true
			this.error = null

			try {
				const doc = await call("frappe.client.get", {
					doctype: "Inventory Variance Case",
					name: caseName,
				})
				this.activeVarianceCase = doc
				return doc
			} catch (error) {
				this.error = `Failed to load variance case: ${error.message}`
				console.error("Error loading variance case detail:", error)
				throw error
			} finally {
				this.varianceCasesLoading = false
			}
		},

		async createVarianceCaseFromSession(sessionName, countItemIdx) {
			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.create_variance_case_from_count",
					{ session_name: sessionName, count_item_idx: countItemIdx },
				)
				return result
			} catch (error) {
				this.error = `Failed to create variance case: ${error.message}`
				throw error
			}
		},

		// ========== Stock Take Audits Actions ==========
		async loadStockTakeAudits(filters = {}, page = 1, pageSize = 50) {
			this.returnAuditsLoading = true
			this.error = null

			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.get_stock_take_audits",
					{
						filters: JSON.stringify(filters),
						page,
						page_size: pageSize,
					},
				)
				this.returnAudits = result.audits
				this.returnAuditsTotalCount = result.total_count
				this.returnAuditsPage = result.page
				this.returnAuditsPageSize = result.page_size
				this.filters.returnAudits = filters
			} catch (error) {
				this.error = `Failed to load stock take audits: ${error.message}`
				console.error("Error loading stock take audits:", error)
			} finally {
				this.returnAuditsLoading = false
			}
		},

		async createStockTakeAudit(auditData) {
			try {
				const doc = await call("frappe.client.insert", {
					doc: {
						doctype: "Stock Take Audit",
						...auditData,
					},
				})
				await this.loadStockTakeAudits(this.filters.returnAudits)
				return doc
			} catch (error) {
				this.error = `Failed to create stock take audit: ${error.message}`
				throw error
			}
		},

		// ========== Stock Take Issues Actions ==========
		async loadIssues(filters = {}, page = 1, pageSize = 50) {
			this.issuesLoading = true
			this.error = null

			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.get_stock_take_issues",
					{
						filters: JSON.stringify(filters),
						page,
						page_size: pageSize,
					},
				)
				this.issues = result.issues
				this.issuesTotalCount = result.total_count
				this.issuesPage = result.page
				this.issuesPageSize = result.page_size
				this.filters.issues = filters
			} catch (error) {
				this.error = `Failed to load issues: ${error.message}`
				console.error("Error loading issues:", error)
			} finally {
				this.issuesLoading = false
			}
		},

		async createIssue(issueData) {
			try {
				const doc = await call("frappe.client.insert", {
					doc: {
						doctype: "Stock Take Issue Log",
						...issueData,
					},
				})
				await this.loadIssues(this.filters.issues)
				return doc
			} catch (error) {
				this.error = `Failed to create issue: ${error.message}`
				throw error
			}
		},

		// ========== Scorecards Actions ==========
		async loadScorecards(filters = {}) {
			this.scorecardsLoading = true
			this.error = null

			try {
				this.scorecards = await call(
					"mkaguzi.api.inventory_audit.get_compliance_scorecards",
					{ filters: JSON.stringify(filters) },
				)
			} catch (error) {
				this.error = `Failed to load scorecards: ${error.message}`
				console.error("Error loading scorecards:", error)
			} finally {
				this.scorecardsLoading = false
			}
		},

		async loadScorecardHistory(scorecardName) {
			try {
				this.scorecardHistory = await call(
					"mkaguzi.api.inventory_audit.get_scorecard_history",
					{ scorecard: scorecardName },
				)
			} catch (error) {
				this.error = `Failed to load scorecard history: ${error.message}`
				throw error
			}
		},

		async recalculateScorecard(planId) {
			try {
				const result = await call(
					"mkaguzi.api.inventory_audit.recalculate_scorecard",
					{ audit_plan: planId },
				)
				await this.loadScorecards()
				return result
			} catch (error) {
				this.error = `Failed to recalculate scorecard: ${error.message}`
				throw error
			}
		},

		// ========== Utility Actions ==========
		setActiveItem(item) {
			this.activeItem = item
		},

		setActivePlan(plan) {
			this.activePlan = plan
		},

		setActiveSession(session) {
			this.activeSession = session
		},

		setActiveVarianceCase(varianceCase) {
			this.activeVarianceCase = varianceCase
		},

		setActiveReturnAudit(returnAudit) {
			this.activeReturnAudit = returnAudit
		},

		setActiveIssue(issue) {
			this.activeIssue = issue
		},

		setActiveScorecard(scorecard) {
			this.activeScorecard = scorecard
		},

		setCurrentView(view) {
			this.currentView = view
		},

		clearError() {
			this.error = null
		},

		clearFilters() {
			this.filters = {
				plans: {},
				sessions: {},
				varianceCases: {},
				returnAudits: {},
				issues: {},
				items: {},
			}
		},

		getStatusColor(status) {
			return this.statusColors[status] || "gray"
		},

		getGradeColor(grade) {
			return this.gradeColors[grade] || "gray"
		},

		// Load all data for dashboard
		async loadAllData() {
			this.isLoading = true
			try {
				await Promise.all([
					this.loadDashboardStats(),
					this.loadPlans({}, 1, 10),
					this.loadSessions({}, 1, 10),
					this.loadVarianceCases({}, 1, 10),
					this.loadIssues({}, 1, 10),
					this.loadScorecards(),
				])
			} catch (error) {
				console.error("Error loading all data:", error)
			} finally {
				this.isLoading = false
			}
		},
	},
})
