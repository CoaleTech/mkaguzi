import { createResource } from "frappe-ui"
import { defineStore } from "pinia"

export const useComplianceStore = defineStore("compliance", {
	state: () => ({
		complianceRequirements: [],
		complianceChecklists: [],
		taxComplianceTrackers: [],
		loading: false,
		error: null,
	}),

	getters: {
		activeRequirements: (state) => {
			return state.complianceRequirements.filter((req) => req.is_active)
		},

		requirementsByCategory: (state) => {
			const categories = {}
			state.complianceRequirements.forEach((req) => {
				const category = req.compliance_category || "Other"
				if (!categories[category]) {
					categories[category] = []
				}
				categories[category].push(req)
			})
			return categories
		},

		requirementsByRegulatoryBody: (state) => {
			const bodies = {}
			state.complianceRequirements.forEach((req) => {
				const body = req.regulatory_body || "Other"
				if (!bodies[body]) {
					bodies[body] = []
				}
				bodies[body].push(req)
			})
			return bodies
		},

		activeChecklists: (state) => {
			return state.complianceChecklists.filter((list) => list.docstatus === 0)
		},

		checklistSummary: (state) => {
			const summary = {
				total: state.complianceChecklists.length,
				completed: 0,
				overdue: 0,
				alerts: 0,
			}

			state.complianceChecklists.forEach((list) => {
				if (list.completion_percent === 100) {
					summary.completed++
				}
				if (list.overdue_requirements > 0) {
					summary.overdue++
				}
				if (list.alerts && list.alerts.length > 0) {
					summary.alerts++
				}
			})

			return summary
		},

		taxComplianceSummary: (state) => {
			if (state.taxComplianceTrackers.length === 0) return null

			const totalScore = state.taxComplianceTrackers.reduce(
				(sum, tracker) => sum + (tracker.compliance_score || 0),
				0,
			)
			const avgScore = totalScore / state.taxComplianceTrackers.length

			const filings = {
				vat: state.taxComplianceTrackers.filter((t) => t.vat_return_filed)
					.length,
				paye: state.taxComplianceTrackers.filter((t) => t.paye_return_filed)
					.length,
				wht: state.taxComplianceTrackers.filter((t) => t.wht_return_filed)
					.length,
				nssf: state.taxComplianceTrackers.filter((t) => t.nssf_return_filed)
					.length,
				nhif: state.taxComplianceTrackers.filter((t) => t.nhif_return_filed)
					.length,
			}

			return {
				totalTrackers: state.taxComplianceTrackers.length,
				averageScore: Math.round(avgScore),
				filings,
			}
		},
	},

	actions: {
		async fetchComplianceRequirements() {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "frappe.client.get_list",
					params: {
						doctype: "Compliance Requirement",
						fields: [
							"name",
							"requirement_id",
							"requirement_name",
							"regulatory_body",
							"regulation_reference",
							"compliance_category",
							"description",
							"frequency",
							"due_date_calculation",
							"fixed_due_day",
							"due_days_after_period",
							"responsible_person",
							"responsible_department",
							"is_active",
							"creation",
							"modified",
						],
						limit_page_length: 1000,
						order_by: "regulatory_body, compliance_category",
					},
				}).fetch()

				this.complianceRequirements = response || []
			} catch (err) {
				console.error("Error fetching compliance requirements:", err)
				this.error = err.message || "Failed to fetch compliance requirements"
				// If permission error, set empty array
				if (err.message && err.message.includes("PermissionError")) {
					console.warn("No permission to access Compliance Requirement doctype")
					this.complianceRequirements = []
				}
			} finally {
				this.loading = false
			}
		},

		async fetchComplianceChecklists() {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "frappe.client.get_list",
					params: {
						doctype: "Compliance Checklist",
						fields: [
							"name",
							"checklist_id",
							"compliance_period",
							"period_type",
							"period_month",
							"fiscal_year",
							"total_requirements",
							"completed_requirements",
							"overdue_requirements",
							"completion_percent",
							"prepared_by",
							"reviewed_by",
							"approved_by",
							"creation",
							"modified",
							"docstatus",
						],
						limit_page_length: 1000,
						order_by: "modified desc",
					},
				}).fetch()

				this.complianceChecklists = response || []
			} catch (err) {
				console.error("Error fetching compliance checklists:", err)
				this.error = err.message || "Failed to fetch compliance checklists"
				if (err.message && err.message.includes("PermissionError")) {
					console.warn("No permission to access Compliance Checklist doctype")
					this.complianceChecklists = []
				}
			} finally {
				this.loading = false
			}
		},

		async fetchTaxComplianceTrackers() {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "frappe.client.get_list",
					params: {
						doctype: "Tax Compliance Tracker",
						fields: [
							"name",
							"tracker_id",
							"tax_period",
							"compliance_score",
							"vat_return_filed",
							"paye_return_filed",
							"wht_return_filed",
							"nssf_return_filed",
							"nhif_return_filed",
							"creation",
							"modified",
						],
						limit_page_length: 1000,
						order_by: "modified desc",
					},
				}).fetch()

				this.taxComplianceTrackers = response || []
			} catch (err) {
				console.error("Error fetching tax compliance trackers:", err)
				this.error = err.message || "Failed to fetch tax compliance trackers"
				if (err.message && err.message.includes("PermissionError")) {
					console.warn("No permission to access Tax Compliance Tracker doctype")
					this.taxComplianceTrackers = []
				}
			} finally {
				this.loading = false
			}
		},

		async createComplianceRequirement(requirementData) {
			try {
				const response = await createResource({
					url: "frappe.client.insert",
					params: {
						doc: {
							doctype: "Compliance Requirement",
							...requirementData,
						},
					},
				}).fetch()

				await this.fetchComplianceRequirements() // Refresh the list
				return response
			} catch (err) {
				console.error("Error creating compliance requirement:", err)
				throw err
			}
		},

		async updateComplianceRequirement(requirementId, updates) {
			try {
				const response = await createResource({
					url: "frappe.client.set_value",
					params: {
						doctype: "Compliance Requirement",
						name: requirementId,
						fieldname: updates,
					},
				}).fetch()

				await this.fetchComplianceRequirements() // Refresh the list
				return response
			} catch (err) {
				console.error("Error updating compliance requirement:", err)
				throw err
			}
		},

		async createComplianceChecklist(checklistData) {
			try {
				const response = await createResource({
					url: "frappe.client.insert",
					params: {
						doc: {
							doctype: "Compliance Checklist",
							...checklistData,
						},
					},
				}).fetch()

				await this.fetchComplianceChecklists() // Refresh the list
				return response
			} catch (err) {
				console.error("Error creating compliance checklist:", err)
				throw err
			}
		},

		async createTaxComplianceTracker(trackerData) {
			try {
				const response = await createResource({
					url: "frappe.client.insert",
					params: {
						doc: {
							doctype: "Tax Compliance Tracker",
							...trackerData,
						},
					},
				}).fetch()

				await this.fetchTaxComplianceTrackers() // Refresh the list
				return response
			} catch (err) {
				console.error("Error creating tax compliance tracker:", err)
				throw err
			}
		},

		async getChecklistDetails(checklistId) {
			try {
				const response = await createResource({
					url: "frappe.client.get",
					params: {
						doctype: "Compliance Checklist",
						name: checklistId,
					},
				}).fetch()

				return response
			} catch (err) {
				console.error("Error fetching checklist details:", err)
				throw err
			}
		},

		async getTaxTrackerDetails(trackerId) {
			try {
				const response = await createResource({
					url: "frappe.client.get",
					params: {
						doctype: "Tax Compliance Tracker",
						name: trackerId,
					},
				}).fetch()

				return response
			} catch (err) {
				console.error("Error fetching tax tracker details:", err)
				throw err
			}
		},

		async getRequirementDetails(requirementId) {
			try {
				const response = await createResource({
					url: "frappe.client.get",
					params: {
						doctype: "Compliance Requirement",
						name: requirementId,
					},
				}).fetch()

				return response
			} catch (err) {
				console.error("Error fetching requirement details:", err)
				throw err
			}
		},

		async createStandardRequirements() {
			try {
				const response = await createResource({
					url: "mkaguzi.api.create_standard_kenya_requirements",
				}).fetch()

				await this.fetchComplianceRequirements() // Refresh the list
				return response
			} catch (err) {
				console.error("Error creating standard requirements:", err)
				throw err
			}
		},
	},
})
