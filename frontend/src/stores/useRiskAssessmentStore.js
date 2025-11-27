import { call, createResource } from "frappe-ui"
import { defineStore } from "pinia"

export const useRiskAssessmentStore = defineStore("riskAssessment", {
	state: () => ({
		// Risk Matrix Configuration
		matrixConfig: {
			likelihood: {
				levels: [
					{
						id: 1,
						label: "Rare",
						description: "May occur only in exceptional circumstances",
						color: "#22c55e",
					},
					{
						id: 2,
						label: "Unlikely",
						description: "Could occur at some time",
						color: "#84cc16",
					},
					{
						id: 3,
						label: "Possible",
						description: "Might occur at some time",
						color: "#eab308",
					},
					{
						id: 4,
						label: "Likely",
						description: "Will probably occur in most circumstances",
						color: "#f97316",
					},
					{
						id: 5,
						label: "Almost Certain",
						description: "Expected to occur in most circumstances",
						color: "#ef4444",
					},
				],
			},
			impact: {
				levels: [
					{
						id: 1,
						label: "Insignificant",
						description: "Minimal impact on operations",
						color: "#22c55e",
					},
					{
						id: 2,
						label: "Minor",
						description: "Minor impact, easily manageable",
						color: "#84cc16",
					},
					{
						id: 3,
						label: "Moderate",
						description: "Moderate impact requiring management attention",
						color: "#eab308",
					},
					{
						id: 4,
						label: "Major",
						description: "Major impact with serious consequences",
						color: "#f97316",
					},
					{
						id: 5,
						label: "Catastrophic",
						description: "Extreme impact with severe consequences",
						color: "#ef4444",
					},
				],
			},
		},

		// Risk Categories
		riskCategories: [
			{
				id: "operational",
				label: "Operational Risk",
				color: "#3b82f6",
				icon: "Settings",
			},
			{
				id: "financial",
				label: "Financial Risk",
				color: "#10b981",
				icon: "DollarSign",
			},
			{
				id: "compliance",
				label: "Compliance Risk",
				color: "#f59e0b",
				icon: "Shield",
			},
			{
				id: "strategic",
				label: "Strategic Risk",
				color: "#8b5cf6",
				icon: "Target",
			},
			{
				id: "reputational",
				label: "Reputational Risk",
				color: "#ef4444",
				icon: "AlertTriangle",
			},
			{
				id: "technology",
				label: "Technology Risk",
				color: "#06b6d4",
				icon: "Monitor",
			},
		],

		// Current Risk Data
		risks: [],
		currentRisk: null,
		riskAnalytics: {},
		mitigationActions: [],
		riskHistory: [],

		// UI State
		loading: {
			risks: false,
			analytics: false,
			mitigations: false,
		},
		filters: {
			category: null,
			status: null,
			owner: null,
			riskLevel: null,
			dateRange: null,
		},
		selectedRisks: [],
		matrixView: "heatmap", // heatmap, list, detail

		// Risk Register
		riskRegister: {
			risks: [],
			totalRisks: 0,
			highRisks: 0,
			mediumRisks: 0,
			lowRisks: 0,
			overdueActions: 0,
		},
	}),

	getters: {
		// Risk Level Calculation
		calculateRiskLevel: (state) => (likelihood, impact) => {
			const score = likelihood * impact
			if (score <= 5) return { level: "Low", color: "#22c55e", priority: 1 }
			if (score <= 12) return { level: "Medium", color: "#eab308", priority: 2 }
			if (score <= 20) return { level: "High", color: "#f97316", priority: 3 }
			return { level: "Critical", color: "#ef4444", priority: 4 }
		},

		// Risk Matrix Data for Heat Map
		riskMatrixData: (state) => {
			const matrix = []
			for (let impact = 5; impact >= 1; impact--) {
				const row = []
				for (let likelihood = 1; likelihood <= 5; likelihood++) {
					const cellRisks = state.risks.filter(
						(risk) => risk.likelihood === likelihood && risk.impact === impact,
					)
					const riskLevel = state.calculateRiskLevel(likelihood, impact)
					row.push({
						likelihood,
						impact,
						risks: cellRisks,
						count: cellRisks.length,
						level: riskLevel.level,
						color: riskLevel.color,
						priority: riskLevel.priority,
					})
				}
				matrix.push(row)
			}
			return matrix
		},

		// Filtered Risks
		filteredRisks: (state) => {
			let filtered = [...state.risks]

			if (state.filters.category) {
				filtered = filtered.filter(
					(risk) => risk.category === state.filters.category,
				)
			}

			if (state.filters.status) {
				filtered = filtered.filter(
					(risk) => risk.status === state.filters.status,
				)
			}

			if (state.filters.owner) {
				filtered = filtered.filter(
					(risk) => risk.risk_owner === state.filters.owner,
				)
			}

			if (state.filters.riskLevel) {
				filtered = filtered.filter((risk) => {
					const level = state.calculateRiskLevel(risk.likelihood, risk.impact)
					return level.level === state.filters.riskLevel
				})
			}

			return filtered.sort((a, b) => {
				const aLevel = state.calculateRiskLevel(a.likelihood, a.impact)
				const bLevel = state.calculateRiskLevel(b.likelihood, b.impact)
				return bLevel.priority - aLevel.priority
			})
		},

		// Risk Statistics
		riskStatistics: (state) => {
			const stats = {
				total: state.risks.length,
				byLevel: { Low: 0, Medium: 0, High: 0, Critical: 0 },
				byCategory: {},
				byStatus: {},
				avgRiskScore: 0,
				trendsData: [],
			}

			state.risks.forEach((risk) => {
				const level = state.calculateRiskLevel(risk.likelihood, risk.impact)
				stats.byLevel[level.level]++
				stats.byCategory[risk.category] =
					(stats.byCategory[risk.category] || 0) + 1
				stats.byStatus[risk.status] = (stats.byStatus[risk.status] || 0) + 1
				stats.avgRiskScore += risk.likelihood * risk.impact
			})

			if (stats.total > 0) {
				stats.avgRiskScore =
					Math.round((stats.avgRiskScore / stats.total) * 10) / 10
			}

			return stats
		},

		// High Priority Risks
		highPriorityRisks: (state) => {
			return state.risks
				.filter((risk) => {
					const level = state.calculateRiskLevel(risk.likelihood, risk.impact)
					return level.priority >= 3 // High or Critical
				})
				.sort((a, b) => {
					const aLevel = state.calculateRiskLevel(a.likelihood, a.impact)
					const bLevel = state.calculateRiskLevel(b.likelihood, b.impact)
					return bLevel.priority - aLevel.priority
				})
		},

		// Overdue Mitigations
		overdueMitigations: (state) => {
			const today = new Date()
			return state.mitigationActions.filter(
				(action) =>
					action.due_date &&
					new Date(action.due_date) < today &&
					action.status !== "Completed",
			)
		},
	},

	actions: {
		// Load Risk Data
		async loadRisks(filters = {}) {
			this.loading.risks = true
			try {
				const response = await call("mkaguzi.api.risk_assessment.get_risks", {
					filters,
				})
				this.risks = response.risks || []
				this.riskAnalytics = response.analytics || {}
				await this.loadMitigationActions()
			} catch (error) {
				console.error("Error loading risks:", error)
				this.$q.notify({
					type: "negative",
					message: "Failed to load risks",
				})
			} finally {
				this.loading.risks = false
			}
		},

		// Create Risk
		async createRisk(riskData) {
			try {
				const response = await call("mkaguzi.api.risk_assessment.create_risk", {
					risk_data: riskData,
				})

				this.risks.push(response)
				this.currentRisk = response

				this.$q.notify({
					type: "positive",
					message: "Risk created successfully",
				})

				return response
			} catch (error) {
				console.error("Error creating risk:", error)
				this.$q.notify({
					type: "negative",
					message: "Failed to create risk",
				})
				throw error
			}
		},

		// Update Risk
		async updateRisk(riskName, updates) {
			try {
				const response = await call("mkaguzi.api.risk_assessment.update_risk", {
					risk_name: riskName,
					updates,
				})

				const index = this.risks.findIndex((r) => r.name === riskName)
				if (index !== -1) {
					this.risks[index] = { ...this.risks[index], ...response }
				}

				if (this.currentRisk?.name === riskName) {
					this.currentRisk = { ...this.currentRisk, ...response }
				}

				this.$q.notify({
					type: "positive",
					message: "Risk updated successfully",
				})

				return response
			} catch (error) {
				console.error("Error updating risk:", error)
				this.$q.notify({
					type: "negative",
					message: "Failed to update risk",
				})
				throw error
			}
		},

		// Delete Risk
		async deleteRisk(riskName) {
			try {
				await call("mkaguzi.api.risk_assessment.delete_risk", {
					risk_name: riskName,
				})

				this.risks = this.risks.filter((r) => r.name !== riskName)

				if (this.currentRisk?.name === riskName) {
					this.currentRisk = null
				}

				this.$q.notify({
					type: "positive",
					message: "Risk deleted successfully",
				})
			} catch (error) {
				console.error("Error deleting risk:", error)
				this.$q.notify({
					type: "negative",
					message: "Failed to delete risk",
				})
				throw error
			}
		},

		// Load Mitigation Actions
		async loadMitigationActions() {
			this.loading.mitigations = true
			try {
				const response = await call(
					"mkaguzi.api.risk_assessment.get_mitigation_actions",
				)
				this.mitigationActions = response || []
			} catch (error) {
				console.error("Error loading mitigation actions:", error)
			} finally {
				this.loading.mitigations = false
			}
		},

		// Create Mitigation Action
		async createMitigationAction(actionData) {
			try {
				const response = await call(
					"mkaguzi.api.risk_assessment.create_mitigation_action",
					{
						action_data: actionData,
					},
				)

				this.mitigationActions.push(response)

				this.$q.notify({
					type: "positive",
					message: "Mitigation action created successfully",
				})

				return response
			} catch (error) {
				console.error("Error creating mitigation action:", error)
				this.$q.notify({
					type: "negative",
					message: "Failed to create mitigation action",
				})
				throw error
			}
		},

		// Update Mitigation Action
		async updateMitigationAction(actionName, updates) {
			try {
				const response = await call(
					"mkaguzi.api.risk_assessment.update_mitigation_action",
					{
						action_name: actionName,
						updates,
					},
				)

				const index = this.mitigationActions.findIndex(
					(a) => a.name === actionName,
				)
				if (index !== -1) {
					this.mitigationActions[index] = {
						...this.mitigationActions[index],
						...response,
					}
				}

				this.$q.notify({
					type: "positive",
					message: "Mitigation action updated successfully",
				})

				return response
			} catch (error) {
				console.error("Error updating mitigation action:", error)
				this.$q.notify({
					type: "negative",
					message: "Failed to update mitigation action",
				})
				throw error
			}
		},

		// Generate Risk Report
		async generateRiskReport(format = "pdf", options = {}) {
			try {
				const response = await call(
					"mkaguzi.api.risk_assessment.generate_risk_report",
					{
						format,
						options: {
							include_matrix: true,
							include_analytics: true,
							include_mitigations: true,
							...options,
						},
					},
				)

				// Download the generated report
				const link = document.createElement("a")
				link.href = response.file_url
				link.download = response.filename
				document.body.appendChild(link)
				link.click()
				document.body.removeChild(link)

				this.$q.notify({
					type: "positive",
					message: "Risk report generated successfully",
				})

				return response
			} catch (error) {
				console.error("Error generating risk report:", error)
				this.$q.notify({
					type: "negative",
					message: "Failed to generate risk report",
				})
				throw error
			}
		},

		// Risk Assessment Analytics
		async loadRiskAnalytics() {
			this.loading.analytics = true
			try {
				const response = await call("mkaguzi.api.risk_assessment.get_analytics")
				this.riskAnalytics = response || {}
			} catch (error) {
				console.error("Error loading risk analytics:", error)
			} finally {
				this.loading.analytics = false
			}
		},

		// Set Current Risk
		setCurrentRisk(risk) {
			this.currentRisk = risk
		},

		// Clear Current Risk
		clearCurrentRisk() {
			this.currentRisk = null
		},

		// Update Filters
		updateFilters(filters) {
			this.filters = { ...this.filters, ...filters }
		},

		// Clear Filters
		clearFilters() {
			this.filters = {
				category: null,
				status: null,
				owner: null,
				riskLevel: null,
				dateRange: null,
			}
		},

		// Toggle Risk Selection
		toggleRiskSelection(riskName) {
			const index = this.selectedRisks.indexOf(riskName)
			if (index === -1) {
				this.selectedRisks.push(riskName)
			} else {
				this.selectedRisks.splice(index, 1)
			}
		},

		// Clear Risk Selection
		clearRiskSelection() {
			this.selectedRisks = []
		},

		// Set Matrix View
		setMatrixView(view) {
			this.matrixView = view
		},

		// Bulk Update Risks
		async bulkUpdateRisks(riskNames, updates) {
			try {
				const response = await call(
					"mkaguzi.api.risk_assessment.bulk_update_risks",
					{
						risk_names: riskNames,
						updates,
					},
				)

				// Update local state
				this.risks = this.risks.map((risk) => {
					if (riskNames.includes(risk.name)) {
						return { ...risk, ...updates }
					}
					return risk
				})

				this.$q.notify({
					type: "positive",
					message: `${riskNames.length} risks updated successfully`,
				})

				return response
			} catch (error) {
				console.error("Error bulk updating risks:", error)
				this.$q.notify({
					type: "negative",
					message: "Failed to update risks",
				})
				throw error
			}
		},
	},
})
