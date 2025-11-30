import { createResource } from "frappe-ui"
import { defineStore } from "pinia"

export const useFollowUpStore = defineStore("followup", {
	state: () => ({
		trackers: [],
		selectedTracker: null,
		loading: false,
		saving: false,
		error: null,
		searchQuery: "",
		filters: {
			status: "",
			followUpType: "",
			frequency: "",
			currentStatus: "",
			responsiblePerson: "",
			auditFinding: "",
		},
	}),

	getters: {
		filteredTrackers: (state) => {
			let filtered = state.trackers

			if (state.searchQuery) {
				const search = state.searchQuery.toLowerCase()
				filtered = filtered.filter(
					(t) =>
						t.tracker_id?.toLowerCase().includes(search) ||
						t.finding_title?.toLowerCase().includes(search) ||
						t.description?.toLowerCase().includes(search),
				)
			}

			if (state.filters.status) {
				filtered = filtered.filter((t) => t.status === state.filters.status)
			}

			if (state.filters.followUpType) {
				filtered = filtered.filter(
					(t) => t.follow_up_type === state.filters.followUpType,
				)
			}

			if (state.filters.frequency) {
				filtered = filtered.filter(
					(t) => t.frequency === state.filters.frequency,
				)
			}

			if (state.filters.currentStatus) {
				filtered = filtered.filter(
					(t) => t.current_status === state.filters.currentStatus,
				)
			}

			if (state.filters.responsiblePerson) {
				const search = state.filters.responsiblePerson.toLowerCase()
				filtered = filtered.filter((t) =>
					t.responsible_person?.toLowerCase().includes(search),
				)
			}

			if (state.filters.auditFinding) {
				filtered = filtered.filter(
					(t) => t.audit_finding === state.filters.auditFinding,
				)
			}

			return filtered
		},

		stats: (state) => {
			const total = state.trackers.length
			const active = state.trackers.filter((t) => t.status === "Active").length
			const completed = state.trackers.filter(
				(t) => t.status === "Completed",
			).length
			const onHold = state.trackers.filter((t) => t.status === "On Hold").length

			const now = new Date()
			const overdue = state.trackers.filter((t) => {
				if (!t.next_due_date || t.status !== "Active") return false
				return new Date(t.next_due_date) < now
			}).length

			const atRisk = state.trackers.filter(
				(t) =>
					t.current_status === "At Risk" || t.current_status === "Off Track",
			).length

			// Status distribution
			const statusDistribution = {
				Active: active,
				Completed: completed,
				"On Hold": onHold,
				Cancelled: state.trackers.filter((t) => t.status === "Cancelled")
					.length,
			}

			// Progress by type
			const progressByType = {}
			state.trackers.forEach((t) => {
				const type = t.follow_up_type || "Other"
				if (!progressByType[type]) {
					progressByType[type] = { total: 0, completed: 0 }
				}
				progressByType[type].total++
				if (t.status === "Completed") {
					progressByType[type].completed++
				}
			})

			return {
				total,
				active,
				completed,
				onHold,
				overdue,
				atRisk,
				statusDistribution,
				progressByType,
			}
		},
	},

	actions: {
		async fetchTrackers() {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "frappe.client.get_list",
					params: {
						doctype: "Follow-up Tracker",
						fields: [
							"name",
							"tracker_id",
							"audit_finding",
							"finding_title",
							"status",
							"follow_up_type",
							"frequency",
							"start_date",
							"next_due_date",
							"last_follow_up_date",
							"responsible_person",
							"responsible_department",
							"current_status",
							"progress_rating",
							"effectiveness_rating",
							"escalation_required",
							"escalation_level",
							"closure_date",
							"closure_criteria_met",
							"closure_reason",
							"creation",
							"modified",
						],
						limit_page_length: 0,
						order_by: "modified desc",
					},
				}).fetch()

				this.trackers = response || []
			} catch (err) {
				console.error("Error fetching follow-up trackers:", err)
				this.error = err.message || "Failed to fetch follow-up trackers"
				this.trackers = []
			} finally {
				this.loading = false
			}
		},

		async getTrackerDetails(trackerId) {
			try {
				this.loading = true
				const response = await createResource({
					url: "frappe.client.get",
					params: {
						doctype: "Follow-up Tracker",
						name: trackerId,
					},
				}).fetch()

				this.selectedTracker = response
				return response
			} catch (err) {
				console.error("Error fetching tracker details:", err)
				throw err
			} finally {
				this.loading = false
			}
		},

		async createTracker(trackerData) {
			try {
				this.saving = true
				const response = await createResource({
					url: "frappe.client.insert",
					params: {
						doc: {
							doctype: "Follow-up Tracker",
							...trackerData,
						},
					},
				}).fetch()

				await this.fetchTrackers()
				return response
			} catch (err) {
				console.error("Error creating tracker:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		async updateTracker(trackerId, updates) {
			try {
				this.saving = true
				const response = await createResource({
					url: "frappe.client.set_value",
					params: {
						doctype: "Follow-up Tracker",
						name: trackerId,
						fieldname: updates,
					},
				}).fetch()

				await this.fetchTrackers()
				return response
			} catch (err) {
				console.error("Error updating tracker:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		async saveTracker(trackerData) {
			if (trackerData.name) {
				return this.updateTracker(trackerData.name, trackerData)
			} else {
				return this.createTracker(trackerData)
			}
		},

		async deleteTracker(trackerId) {
			try {
				this.saving = true
				await createResource({
					url: "frappe.client.delete",
					params: {
						doctype: "Follow-up Tracker",
						name: trackerId,
					},
				}).fetch()

				await this.fetchTrackers()
			} catch (err) {
				console.error("Error deleting tracker:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		async addFollowUpActivity(trackerId, activityData) {
			try {
				this.saving = true

				// Get current tracker
				const tracker = await this.getTrackerDetails(trackerId)
				const activities = tracker.follow_up_activities || []

				// Add new activity
				activities.push({
					...activityData,
					activity_date:
						activityData.activity_date ||
						new Date().toISOString().split("T")[0],
				})

				// Update tracker with new activity
				await createResource({
					url: "frappe.client.set_value",
					params: {
						doctype: "Follow-up Tracker",
						name: trackerId,
						fieldname: {
							follow_up_activities: activities,
							last_follow_up_date: new Date().toISOString().split("T")[0],
						},
					},
				}).fetch()

				await this.fetchTrackers()
			} catch (err) {
				console.error("Error adding follow-up activity:", err)
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
				followUpType: "",
				frequency: "",
				currentStatus: "",
				responsiblePerson: "",
				auditFinding: "",
			}
		},
	},
})
