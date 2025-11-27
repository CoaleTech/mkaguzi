import { createResource } from "frappe-ui"
import { defineStore } from "pinia"

export const useDataPeriodsStore = defineStore("dataPeriods", {
	state: () => ({
		periods: [],
		selectedPeriod: null,
		loading: false,
		saving: false,
		error: null,
		searchQuery: "",
		filters: {
			status: "",
			periodType: "",
			fiscalYear: "",
			reconciliationStatus: "",
		},
	}),

	getters: {
		filteredPeriods: (state) => {
			let filtered = state.periods

			if (state.searchQuery) {
				const search = state.searchQuery.toLowerCase()
				filtered = filtered.filter(
					(p) =>
						p.period_name?.toLowerCase().includes(search) ||
						p.period_id?.toLowerCase().includes(search) ||
						p.description?.toLowerCase().includes(search)
				)
			}

			if (state.filters.status) {
				filtered = filtered.filter((p) => p.status === state.filters.status)
			}

			if (state.filters.periodType) {
				filtered = filtered.filter(
					(p) => p.period_type === state.filters.periodType
				)
			}

			if (state.filters.fiscalYear) {
				filtered = filtered.filter(
					(p) => p.fiscal_year === state.filters.fiscalYear
				)
			}

			if (state.filters.reconciliationStatus) {
				filtered = filtered.filter(
					(p) => p.reconciliation_status === state.filters.reconciliationStatus
				)
			}

			return filtered
		},

		stats: (state) => {
			const total = state.periods.length
			const open = state.periods.filter((p) => p.status === "Open").length
			const locked = state.periods.filter((p) => p.status === "Locked").length
			const closed = state.periods.filter((p) => p.status === "Closed").length

			// Calculate average data quality and completeness
			const periodsWithQuality = state.periods.filter(
				(p) => p.data_quality_score !== null && p.data_quality_score !== undefined
			)
			const avgDataQuality =
				periodsWithQuality.length > 0
					? Math.round(
							periodsWithQuality.reduce(
								(sum, p) => sum + (p.data_quality_score || 0),
								0
							) / periodsWithQuality.length
					  )
					: 0

			const periodsWithCompleteness = state.periods.filter(
				(p) =>
					p.data_completeness_score !== null &&
					p.data_completeness_score !== undefined
			)
			const avgCompleteness =
				periodsWithCompleteness.length > 0
					? Math.round(
							periodsWithCompleteness.reduce(
								(sum, p) => sum + (p.data_completeness_score || 0),
								0
							) / periodsWithCompleteness.length
					  )
					: 0

			// By fiscal year
			const byFiscalYear = {}
			state.periods.forEach((p) => {
				const year = p.fiscal_year || "Unknown"
				if (!byFiscalYear[year]) {
					byFiscalYear[year] = 0
				}
				byFiscalYear[year]++
			})

			// By period type
			const byPeriodType = {}
			state.periods.forEach((p) => {
				const type = p.period_type || "Unknown"
				if (!byPeriodType[type]) {
					byPeriodType[type] = 0
				}
				byPeriodType[type]++
			})

			return {
				total,
				open,
				locked,
				closed,
				avgDataQuality,
				avgCompleteness,
				byFiscalYear,
				byPeriodType,
			}
		},

		fiscalYears: (state) => {
			const years = new Set(state.periods.map((p) => p.fiscal_year).filter(Boolean))
			return Array.from(years).sort().reverse()
		},
	},

	actions: {
		async fetchPeriods() {
			try {
				this.loading = true
				this.error = null

				const response = await createResource({
					url: "frappe.client.get_list",
					params: {
						doctype: "Data Period",
						fields: [
							"name",
							"period_id",
							"period_name",
							"period_type",
							"fiscal_year",
							"start_date",
							"end_date",
							"status",
							"description",
							"company",
							"data_completeness_score",
							"data_quality_score",
							"reconciliation_status",
							"is_locked",
							"locked_by",
							"locked_date",
							"closure_date",
							"closed_by",
							"closure_notes",
							"creation",
							"modified",
						],
						limit_page_length: 0,
						order_by: "start_date desc",
					},
				}).fetch()

				this.periods = response || []
			} catch (err) {
				console.error("Error fetching data periods:", err)
				this.error = err.message || "Failed to fetch data periods"
				this.periods = []
			} finally {
				this.loading = false
			}
		},

		async getPeriodDetails(periodId) {
			try {
				this.loading = true
				const response = await createResource({
					url: "frappe.client.get",
					params: {
						doctype: "Data Period",
						name: periodId,
					},
				}).fetch()

				this.selectedPeriod = response
				return response
			} catch (err) {
				console.error("Error fetching period details:", err)
				throw err
			} finally {
				this.loading = false
			}
		},

		async createPeriod(periodData) {
			try {
				this.saving = true
				const response = await createResource({
					url: "frappe.client.insert",
					params: {
						doc: {
							doctype: "Data Period",
							...periodData,
						},
					},
				}).fetch()

				await this.fetchPeriods()
				return response
			} catch (err) {
				console.error("Error creating period:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		async updatePeriod(periodId, updates) {
			try {
				this.saving = true
				const response = await createResource({
					url: "frappe.client.set_value",
					params: {
						doctype: "Data Period",
						name: periodId,
						fieldname: updates,
					},
				}).fetch()

				await this.fetchPeriods()
				return response
			} catch (err) {
				console.error("Error updating period:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		async savePeriod(periodData) {
			if (periodData.name) {
				return this.updatePeriod(periodData.name, periodData)
			} else {
				return this.createPeriod(periodData)
			}
		},

		async lockPeriod(periodId) {
			try {
				this.saving = true
				await createResource({
					url: "frappe.client.set_value",
					params: {
						doctype: "Data Period",
						name: periodId,
						fieldname: {
							is_locked: 1,
							locked_date: new Date().toISOString().split("T")[0],
							status: "Locked",
						},
					},
				}).fetch()

				await this.fetchPeriods()
			} catch (err) {
				console.error("Error locking period:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		async unlockPeriod(periodId) {
			try {
				this.saving = true
				await createResource({
					url: "frappe.client.set_value",
					params: {
						doctype: "Data Period",
						name: periodId,
						fieldname: {
							is_locked: 0,
							locked_date: null,
							locked_by: null,
							status: "Open",
						},
					},
				}).fetch()

				await this.fetchPeriods()
			} catch (err) {
				console.error("Error unlocking period:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		async closePeriod(periodId, notes = "") {
			try {
				this.saving = true
				await createResource({
					url: "frappe.client.set_value",
					params: {
						doctype: "Data Period",
						name: periodId,
						fieldname: {
							status: "Closed",
							closure_date: new Date().toISOString().split("T")[0],
							closure_notes: notes,
						},
					},
				}).fetch()

				await this.fetchPeriods()
			} catch (err) {
				console.error("Error closing period:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		async reopenPeriod(periodId) {
			try {
				this.saving = true
				await createResource({
					url: "frappe.client.set_value",
					params: {
						doctype: "Data Period",
						name: periodId,
						fieldname: {
							status: "Open",
							closure_date: null,
							closed_by: null,
							closure_notes: null,
						},
					},
				}).fetch()

				await this.fetchPeriods()
			} catch (err) {
				console.error("Error reopening period:", err)
				throw err
			} finally {
				this.saving = false
			}
		},

		async deletePeriod(periodId) {
			try {
				this.saving = true
				await createResource({
					url: "frappe.client.delete",
					params: {
						doctype: "Data Period",
						name: periodId,
					},
				}).fetch()

				await this.fetchPeriods()
			} catch (err) {
				console.error("Error deleting period:", err)
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
				periodType: "",
				fiscalYear: "",
				reconciliationStatus: "",
			}
		},
	},
})
