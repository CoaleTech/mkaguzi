import { createResource } from "frappe-ui"
import { defineStore } from "pinia"

export const useCorrectiveActionsStore = defineStore("correctiveActions", {
	state: () => ({
		actions: [],
		selectedAction: null,
		loading: false,
		saving: false,
		error: null,
		searchQuery: "",
		filters: {
			status: "",
			priority: "",
			dueRange: "",
			responsiblePerson: "",
		},
	}),

	getters: {
		filteredActions: (state) => {
			let filtered = state.actions

			if (state.searchQuery) {
				const search = state.searchQuery.toLowerCase()
				filtered = filtered.filter(
					(a) =>
						a.plan_id?.toLowerCase().includes(search) ||
						a.title?.toLowerCase().includes(search) ||
						a.audit_finding?.toLowerCase().includes(search)
				)
			}

			if (state.filters.status) {
				filtered = filtered.filter((a) => a.status === state.filters.status)
			}

			if (state.filters.priority) {
				filtered = filtered.filter((a) => a.priority === state.filters.priority)
			}

			if (state.filters.dueRange) {
				const now = new Date()
				const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
				const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
				const monthFromNow = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000)

				filtered = filtered.filter((a) => {
					if (!a.target_completion_date) return false
					const dueDate = new Date(a.target_completion_date)

					switch (state.filters.dueRange) {
						case "overdue":
							return dueDate < today && a.status !== "Completed"
						case "today":
							return dueDate.toDateString() === today.toDateString()
						case "this_week":
							return dueDate >= today && dueDate <= weekFromNow
						case "this_month":
							return dueDate >= today && dueDate <= monthFromNow
						case "later":
							return dueDate > monthFromNow
						default:
							return true
					}
				})
			}

			if (state.filters.responsiblePerson) {
				const search = state.filters.responsiblePerson.toLowerCase()
				filtered = filtered.filter((a) =>
					a.responsible_person?.toLowerCase().includes(search)
				)
			}

			return filtered
		},

		stats: (state) => {
			const total = state.actions.length
			const inProgress = state.actions.filter((a) => a.status === "In Progress").length
			const completed = state.actions.filter((a) => a.status === "Completed").length

			const now = new Date()
			const overdue = state.actions.filter((a) => {
				if (!a.target_completion_date || a.status === "Completed") return false
				return new Date(a.target_completion_date) < now
			}).length

			const avgProgress = total > 0
				? Math.round(state.actions.reduce((sum, a) => sum + (a.completion_percentage || 0), 0) / total)
				: 0

			// Status distribution
			const statusDistribution = {
				Draft: state.actions.filter((a) => a.status === "Draft").length,
				Approved: state.actions.filter((a) => a.status === "Approved").length,
				"In Progress": inProgress,
				"On Hold": state.actions.filter((a) => a.status === "On Hold").length,
				Completed: completed,
				Cancelled: state.actions.filter((a) => a.status === "Cancelled").length,
			}

			// Priority distribution
			const priorityDistribution = {
				Critical: state.actions.filter((a) => a.priority === "Critical").length,
				High: state.actions.filter((a) => a.priority === "High").length,
				Medium: state.actions.filter((a) => a.priority === "Medium").length,
				Low: state.actions.filter((a) => a.priority === "Low").length,
			}

			return {
				total,
				inProgress,
				completed,
				overdue,
				avgProgress,
				statusDistribution,
				priorityDistribution,
			}
		},
	},

	actions: {
		async fetchActions() {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "frappe.client.get_list",
					params: {
						doctype: "Corrective Action Plan",
						fields: [
							"name",
							"plan_id",
							"audit_finding",
							"title",
							"status",
							"priority",
							"start_date",
							"target_completion_date",
							"actual_completion_date",
							"responsible_person",
							"responsible_department",
							"overall_progress",
							"completion_percentage",
							"creation",
							"modified",
						],
						limit_page_length: 0,
						order_by: "modified desc",
					},
				}).fetch()

				this.actions = response || []
			} catch (err) {
				console.error("Error fetching corrective actions:", err)
				this.error = err.message || "Failed to fetch corrective actions"
				this.actions = []
			} finally {
				this.loading = false
			}
		},

		async getActionDetails(actionId) {
			try {
				this.loading = true
				const response = await createResource({
					url: "frappe.client.get",
					params: {
						doctype: "Corrective Action Plan",
						name: actionId,
					},
				}).fetch()

				this.selectedAction = response
				return response
			} catch (err) {
				console.error("Error fetching action details:", err)
				throw err
			} finally {
				this.loading = false
			}
		},

		async createAction(actionData) {
			try {
				this.saving = true
				const response = await createResource({
					url: "frappe.client.insert",
					params: {
						doc: {
							doctype: "Corrective Action Plan",
							...actionData,
						},
					},
				}).fetch()

				await this.fetchActions()
				return response
			} catch (err) {
				console.error("Error creating action:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		async updateAction(actionId, updates) {
			try {
				this.saving = true
				const response = await createResource({
					url: "frappe.client.set_value",
					params: {
						doctype: "Corrective Action Plan",
						name: actionId,
						fieldname: updates,
					},
				}).fetch()

				await this.fetchActions()
				return response
			} catch (err) {
				console.error("Error updating action:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		async saveAction(actionData) {
			if (actionData.name) {
				return this.updateAction(actionData.name, actionData)
			} else {
				return this.createAction(actionData)
			}
		},

		async deleteAction(actionId) {
			try {
				this.saving = true
				await createResource({
					url: "frappe.client.delete",
					params: {
						doctype: "Corrective Action Plan",
						name: actionId,
					},
				}).fetch()

				await this.fetchActions()
			} catch (err) {
				console.error("Error deleting action:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		setFilters(filters) {
			this.filters = { ...this.filters, ...filters }
		},

		clearFilters() {
			this.searchQuery = ""
			this.filters = {
				status: "",
				priority: "",
				dueRange: "",
				responsiblePerson: "",
			}
		},
	},
})