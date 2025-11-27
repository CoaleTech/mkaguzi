import { defineStore } from "pinia"

export const useComplianceStore = defineStore("compliance", {
	state: () => ({
		// Compliance Requirements
		requirements: [],
		activeRequirement: null,

		// Compliance Frameworks
		frameworks: [
			{
				id: "sox",
				name: "Sarbanes-Oxley Act (SOX)",
				description:
					"Corporate financial reporting and disclosure requirements",
				category: "Financial",
				jurisdiction: "US",
				sections: ["302", "404", "906"],
				color: "#3b82f6",
			},
			{
				id: "gdpr",
				name: "General Data Protection Regulation (GDPR)",
				description: "Data protection and privacy regulation",
				category: "Privacy",
				jurisdiction: "EU",
				sections: ["Article 5", "Article 6", "Article 17", "Article 25"],
				color: "#10b981",
			},
			{
				id: "iso27001",
				name: "ISO 27001",
				description: "Information security management standards",
				category: "Security",
				jurisdiction: "International",
				sections: ["A.5", "A.6", "A.8", "A.9", "A.12"],
				color: "#f59e0b",
			},
			{
				id: "pci_dss",
				name: "PCI DSS",
				description: "Payment Card Industry Data Security Standard",
				category: "Security",
				jurisdiction: "International",
				sections: ["Req 1", "Req 2", "Req 3", "Req 4"],
				color: "#ef4444",
			},
			{
				id: "hipaa",
				name: "HIPAA",
				description: "Health Insurance Portability and Accountability Act",
				category: "Healthcare",
				jurisdiction: "US",
				sections: ["Security Rule", "Privacy Rule", "Breach Rule"],
				color: "#8b5cf6",
			},
		],

		// Compliance Status tracking
		complianceStatus: [],

		// Assessment results
		assessments: [],
		activeAssessment: null,

		// Remediation plans
		remediationPlans: [],

		// Compliance reporting
		reports: [],
		reportTemplates: [],

		// Alerts and notifications
		alerts: [],
		upcomingDeadlines: [],

		// Evidence collection
		evidence: [],

		// Statistics and metrics
		statistics: {
			totalRequirements: 0,
			compliantRequirements: 0,
			nonCompliantRequirements: 0,
			partiallyCompliantRequirements: 0,
			overallComplianceScore: 0,
			upcomingDeadlinesCount: 0,
			criticalIssuesCount: 0,
			remediationTasksCount: 0,
		},

		// Filters and UI state
		selectedFrameworks: [],
		selectedStatuses: [],
		selectedCategories: [],
		currentView: "dashboard", // dashboard, requirements, assessments, reports
		isLoading: false,
		error: null,
	}),

	getters: {
		// Framework getters
		getFrameworkById: (state) => (id) => {
			return state.frameworks.find((framework) => framework.id === id)
		},

		getFrameworksByCategory: (state) => (category) => {
			return state.frameworks.filter(
				(framework) => framework.category === category,
			)
		},

		// Requirement getters
		getRequirementsByFramework: (state) => (frameworkId) => {
			return state.requirements.filter(
				(req) => req.framework_id === frameworkId,
			)
		},

		getRequirementsByStatus: (state) => (status) => {
			return state.requirements.filter(
				(req) => req.compliance_status === status,
			)
		},

		getOverdueRequirements: (state) => {
			const today = new Date()
			return state.requirements.filter((req) => {
				const dueDate = new Date(req.next_review_date)
				return dueDate < today && req.compliance_status !== "Compliant"
			})
		},

		// Assessment getters
		getRecentAssessments: (state) => {
			return state.assessments
				.sort(
					(a, b) => new Date(b.assessment_date) - new Date(a.assessment_date),
				)
				.slice(0, 5)
		},

		getAssessmentsByRequirement: (state) => (requirementId) => {
			return state.assessments.filter(
				(assessment) => assessment.requirement_id === requirementId,
			)
		},

		// Compliance metrics
		getComplianceScoreByFramework: (state) => {
			const frameworkScores = {}

			state.frameworks.forEach((framework) => {
				const requirements = state.requirements.filter(
					(req) => req.framework_id === framework.id,
				)
				if (requirements.length === 0) {
					frameworkScores[framework.id] = 0
					return
				}

				const compliantCount = requirements.filter(
					(req) => req.compliance_status === "Compliant",
				).length
				frameworkScores[framework.id] = Math.round(
					(compliantCount / requirements.length) * 100,
				)
			})

			return frameworkScores
		},

		getComplianceTrends: (state) => {
			// Calculate compliance trends over time
			const trends = []
			const months = [
				"Jan",
				"Feb",
				"Mar",
				"Apr",
				"May",
				"Jun",
				"Jul",
				"Aug",
				"Sep",
				"Oct",
				"Nov",
				"Dec",
			]

			months.forEach((month) => {
				// This would typically come from historical data
				const score = Math.floor(Math.random() * 20) + 75 // Placeholder
				trends.push({ month, score })
			})

			return trends
		},

		// Deadline tracking
		getUpcomingDeadlines: (state) => {
			const today = new Date()
			const thirtyDaysFromNow = new Date(
				today.getTime() + 30 * 24 * 60 * 60 * 1000,
			)

			return state.requirements
				.filter((req) => {
					const dueDate = new Date(req.next_review_date)
					return dueDate >= today && dueDate <= thirtyDaysFromNow
				})
				.sort(
					(a, b) => new Date(a.next_review_date) - new Date(b.next_review_date),
				)
		},

		getCriticalIssues: (state) => {
			return state.requirements.filter(
				(req) =>
					req.compliance_status === "Non-Compliant" &&
					req.risk_level === "High",
			)
		},

		// Filtered requirements
		getFilteredRequirements: (state) => {
			let filtered = state.requirements

			if (state.selectedFrameworks.length > 0) {
				filtered = filtered.filter((req) =>
					state.selectedFrameworks.includes(req.framework_id),
				)
			}

			if (state.selectedStatuses.length > 0) {
				filtered = filtered.filter((req) =>
					state.selectedStatuses.includes(req.compliance_status),
				)
			}

			if (state.selectedCategories.length > 0) {
				filtered = filtered.filter((req) => {
					const framework = state.frameworks.find(
						(f) => f.id === req.framework_id,
					)
					return (
						framework && state.selectedCategories.includes(framework.category)
					)
				})
			}

			return filtered
		},
	},

	actions: {
		// Load compliance data
		async loadComplianceData() {
			this.isLoading = true
			this.error = null

			try {
				await Promise.all([
					this.loadRequirements(),
					this.loadAssessments(),
					this.loadRemediationPlans(),
					this.loadReports(),
					this.loadAlerts(),
				])

				this.calculateStatistics()
			} catch (error) {
				this.error = `Failed to load compliance data: ${error.message}`
				console.error("Error loading compliance data:", error)
			} finally {
				this.isLoading = false
			}
		},

		// Load requirements
		async loadRequirements() {
			try {
				// Simulate API call with mock data
				const mockRequirements = [
					{
						id: "req-001",
						framework_id: "sox",
						section: "404",
						title: "Management Assessment of Internal Controls",
						description:
							"Annual assessment of the effectiveness of internal control over financial reporting",
						compliance_status: "Compliant",
						last_assessment_date: "2025-10-15T00:00:00Z",
						next_review_date: "2025-12-31T00:00:00Z",
						assigned_to: "audit.manager@company.com",
						risk_level: "High",
						control_type: "Management Review",
						evidence_required: [
							"Assessment Documentation",
							"Management Certification",
							"External Auditor Report",
						],
						remediation_status: "N/A",
						compliance_score: 95,
					},
					{
						id: "req-002",
						framework_id: "gdpr",
						section: "Article 25",
						title: "Data Protection by Design and by Default",
						description:
							"Implement appropriate technical and organizational measures to ensure data protection",
						compliance_status: "Partially Compliant",
						last_assessment_date: "2025-11-01T00:00:00Z",
						next_review_date: "2025-12-01T00:00:00Z",
						assigned_to: "privacy.officer@company.com",
						risk_level: "Medium",
						control_type: "Technical Control",
						evidence_required: [
							"Privacy Impact Assessment",
							"Technical Documentation",
							"Training Records",
						],
						remediation_status: "In Progress",
						compliance_score: 78,
					},
					{
						id: "req-003",
						framework_id: "iso27001",
						section: "A.12",
						title: "Operations Security",
						description:
							"Ensure correct and secure operations of information processing facilities",
						compliance_status: "Non-Compliant",
						last_assessment_date: "2025-09-15T00:00:00Z",
						next_review_date: "2025-11-30T00:00:00Z",
						assigned_to: "security.manager@company.com",
						risk_level: "High",
						control_type: "Operational Control",
						evidence_required: [
							"Security Procedures",
							"Monitoring Logs",
							"Incident Reports",
						],
						remediation_status: "Planned",
						compliance_score: 45,
					},
					{
						id: "req-004",
						framework_id: "pci_dss",
						section: "Req 3",
						title: "Protect Stored Cardholder Data",
						description:
							"Implement strong encryption and security measures for cardholder data storage",
						compliance_status: "Compliant",
						last_assessment_date: "2025-11-20T00:00:00Z",
						next_review_date: "2026-01-15T00:00:00Z",
						assigned_to: "security.team@company.com",
						risk_level: "Critical",
						control_type: "Technical Control",
						evidence_required: [
							"Encryption Documentation",
							"Key Management Procedures",
							"Vulnerability Scans",
						],
						remediation_status: "N/A",
						compliance_score: 98,
					},
					{
						id: "req-005",
						framework_id: "hipaa",
						section: "Security Rule",
						title: "Administrative Safeguards",
						description:
							"Implement administrative actions to protect electronic health information",
						compliance_status: "Partially Compliant",
						last_assessment_date: "2025-10-30T00:00:00Z",
						next_review_date: "2025-12-15T00:00:00Z",
						assigned_to: "compliance.officer@company.com",
						risk_level: "Medium",
						control_type: "Administrative Control",
						evidence_required: [
							"Policy Documentation",
							"Training Records",
							"Access Control Lists",
						],
						remediation_status: "In Progress",
						compliance_score: 72,
					},
				]

				this.requirements = mockRequirements
			} catch (error) {
				console.error("Error loading requirements:", error)
				throw error
			}
		},

		// Load assessments
		async loadAssessments() {
			try {
				const mockAssessments = [
					{
						id: "assess-001",
						requirement_id: "req-001",
						assessment_date: "2025-11-20T00:00:00Z",
						assessor: "senior.auditor@company.com",
						assessment_type: "Internal Review",
						findings:
							"Controls operating effectively. No significant deficiencies identified.",
						recommendations: "Continue current monitoring procedures.",
						status: "Completed",
						score: 95,
						evidence_collected: [
							"Control Testing Results",
							"Process Documentation",
							"Interview Notes",
						],
					},
					{
						id: "assess-002",
						requirement_id: "req-002",
						assessment_date: "2025-11-18T00:00:00Z",
						assessor: "privacy.specialist@company.com",
						assessment_type: "Gap Analysis",
						findings:
							"Some data processing activities lack adequate privacy controls.",
						recommendations:
							"Implement additional privacy-by-design measures in development process.",
						status: "Completed",
						score: 78,
						evidence_collected: [
							"Data Flow Diagrams",
							"Privacy Policies",
							"System Documentation",
						],
					},
					{
						id: "assess-003",
						requirement_id: "req-003",
						assessment_date: "2025-11-15T00:00:00Z",
						assessor: "security.auditor@company.com",
						assessment_type: "Compliance Audit",
						findings:
							"Multiple security control failures identified. Critical vulnerabilities present.",
						recommendations:
							"Immediate remediation required for high-risk findings.",
						status: "Completed",
						score: 45,
						evidence_collected: [
							"Vulnerability Reports",
							"Security Logs",
							"Configuration Reviews",
						],
					},
				]

				this.assessments = mockAssessments
			} catch (error) {
				console.error("Error loading assessments:", error)
				throw error
			}
		},

		// Load remediation plans
		async loadRemediationPlans() {
			try {
				const mockPlans = [
					{
						id: "plan-001",
						requirement_id: "req-002",
						title: "GDPR Privacy Controls Enhancement",
						description: "Implement additional privacy-by-design measures",
						priority: "Medium",
						status: "In Progress",
						assigned_to: "privacy.team@company.com",
						due_date: "2025-12-15T00:00:00Z",
						progress: 65,
						tasks: [
							{
								id: "task-001",
								title: "Update Privacy Impact Assessment Template",
								status: "Completed",
								due_date: "2025-11-30T00:00:00Z",
							},
							{
								id: "task-002",
								title: "Implement Privacy Controls in Development Process",
								status: "In Progress",
								due_date: "2025-12-10T00:00:00Z",
							},
							{
								id: "task-003",
								title: "Conduct Privacy Training for Development Team",
								status: "Not Started",
								due_date: "2025-12-15T00:00:00Z",
							},
						],
					},
					{
						id: "plan-002",
						requirement_id: "req-003",
						title: "ISO 27001 Operations Security Remediation",
						description: "Address critical security control failures",
						priority: "High",
						status: "Planned",
						assigned_to: "security.team@company.com",
						due_date: "2025-12-30T00:00:00Z",
						progress: 15,
						tasks: [
							{
								id: "task-004",
								title: "Patch Critical Vulnerabilities",
								status: "In Progress",
								due_date: "2025-12-01T00:00:00Z",
							},
							{
								id: "task-005",
								title: "Implement Enhanced Monitoring Controls",
								status: "Not Started",
								due_date: "2025-12-15T00:00:00Z",
							},
							{
								id: "task-006",
								title: "Update Security Procedures Documentation",
								status: "Not Started",
								due_date: "2025-12-30T00:00:00Z",
							},
						],
					},
				]

				this.remediationPlans = mockPlans
			} catch (error) {
				console.error("Error loading remediation plans:", error)
				throw error
			}
		},

		// Load reports
		async loadReports() {
			try {
				const mockReports = [
					{
						id: "report-001",
						title: "Q4 2025 SOX Compliance Report",
						type: "Compliance Summary",
						framework_id: "sox",
						generated_date: "2025-11-20T00:00:00Z",
						generated_by: "audit.manager@company.com",
						status: "Published",
						recipients: [
							"ceo@company.com",
							"cfo@company.com",
							"board@company.com",
						],
						file_path: "/reports/sox-q4-2025.pdf",
					},
					{
						id: "report-002",
						title: "GDPR Compliance Assessment Report",
						type: "Assessment Report",
						framework_id: "gdpr",
						generated_date: "2025-11-18T00:00:00Z",
						generated_by: "privacy.officer@company.com",
						status: "Draft",
						recipients: ["legal@company.com", "privacy.team@company.com"],
						file_path: "/reports/gdpr-assessment-nov-2025.pdf",
					},
				]

				this.reports = mockReports
			} catch (error) {
				console.error("Error loading reports:", error)
				throw error
			}
		},

		// Load alerts
		async loadAlerts() {
			try {
				const mockAlerts = [
					{
						id: "alert-001",
						type: "Deadline Warning",
						severity: "Medium",
						title: "ISO 27001 Review Due Soon",
						message: "Operations Security requirement review is due in 5 days",
						requirement_id: "req-003",
						created_date: "2025-11-25T00:00:00Z",
						is_read: false,
						action_required: true,
					},
					{
						id: "alert-002",
						type: "Compliance Issue",
						severity: "High",
						title: "Critical Non-Compliance Detected",
						message: "ISO 27001 Operations Security controls are non-compliant",
						requirement_id: "req-003",
						created_date: "2025-11-20T00:00:00Z",
						is_read: false,
						action_required: true,
					},
					{
						id: "alert-003",
						type: "Remediation Update",
						severity: "Low",
						title: "GDPR Remediation Progress",
						message: "Privacy controls enhancement plan is 65% complete",
						requirement_id: "req-002",
						created_date: "2025-11-24T00:00:00Z",
						is_read: true,
						action_required: false,
					},
				]

				this.alerts = mockAlerts
			} catch (error) {
				console.error("Error loading alerts:", error)
				throw error
			}
		},

		// Calculate statistics
		calculateStatistics() {
			const total = this.requirements.length
			const compliant = this.requirements.filter(
				(req) => req.compliance_status === "Compliant",
			).length
			const nonCompliant = this.requirements.filter(
				(req) => req.compliance_status === "Non-Compliant",
			).length
			const partiallyCompliant = this.requirements.filter(
				(req) => req.compliance_status === "Partially Compliant",
			).length

			this.statistics = {
				totalRequirements: total,
				compliantRequirements: compliant,
				nonCompliantRequirements: nonCompliant,
				partiallyCompliantRequirements: partiallyCompliant,
				overallComplianceScore:
					total > 0
						? Math.round(((compliant + partiallyCompliant * 0.5) / total) * 100)
						: 0,
				upcomingDeadlinesCount: this.getUpcomingDeadlines.length,
				criticalIssuesCount: this.getCriticalIssues.length,
				remediationTasksCount: this.remediationPlans.reduce(
					(count, plan) => count + plan.tasks.length,
					0,
				),
			}
		},

		// Create new requirement
		async createRequirement(requirementData) {
			try {
				const newRequirement = {
					id: `req-${Date.now()}`,
					...requirementData,
					compliance_status: "Not Assessed",
					compliance_score: 0,
					created_date: new Date().toISOString(),
					created_by: "current_user",
				}

				this.requirements.push(newRequirement)
				this.calculateStatistics()

				return newRequirement
			} catch (error) {
				this.error = `Failed to create requirement: ${error.message}`
				throw error
			}
		},

		// Update requirement
		async updateRequirement(requirementId, updates) {
			try {
				const requirement = this.requirements.find(
					(req) => req.id === requirementId,
				)
				if (!requirement) {
					throw new Error("Requirement not found")
				}

				Object.assign(requirement, updates, {
					updated_date: new Date().toISOString(),
					updated_by: "current_user",
				})

				this.calculateStatistics()

				return requirement
			} catch (error) {
				this.error = `Failed to update requirement: ${error.message}`
				throw error
			}
		},

		// Create assessment
		async createAssessment(assessmentData) {
			try {
				const newAssessment = {
					id: `assess-${Date.now()}`,
					...assessmentData,
					assessment_date: new Date().toISOString(),
					assessor: "current_user",
					status: "Completed",
				}

				this.assessments.push(newAssessment)

				// Update requirement compliance status based on assessment
				if (assessmentData.requirement_id) {
					const requirement = this.requirements.find(
						(req) => req.id === assessmentData.requirement_id,
					)
					if (requirement) {
						requirement.compliance_score = assessmentData.score
						requirement.last_assessment_date = newAssessment.assessment_date

						if (assessmentData.score >= 90) {
							requirement.compliance_status = "Compliant"
						} else if (assessmentData.score >= 70) {
							requirement.compliance_status = "Partially Compliant"
						} else {
							requirement.compliance_status = "Non-Compliant"
						}
					}
				}

				this.calculateStatistics()

				return newAssessment
			} catch (error) {
				this.error = `Failed to create assessment: ${error.message}`
				throw error
			}
		},

		// Create remediation plan
		async createRemediationPlan(planData) {
			try {
				const newPlan = {
					id: `plan-${Date.now()}`,
					...planData,
					status: "Planned",
					progress: 0,
					created_date: new Date().toISOString(),
					created_by: "current_user",
				}

				this.remediationPlans.push(newPlan)
				this.calculateStatistics()

				return newPlan
			} catch (error) {
				this.error = `Failed to create remediation plan: ${error.message}`
				throw error
			}
		},

		// Generate compliance report
		async generateReport(reportData) {
			try {
				const newReport = {
					id: `report-${Date.now()}`,
					...reportData,
					generated_date: new Date().toISOString(),
					generated_by: "current_user",
					status: "Generated",
				}

				this.reports.push(newReport)

				return newReport
			} catch (error) {
				this.error = `Failed to generate report: ${error.message}`
				throw error
			}
		},

		// Mark alert as read
		markAlertAsRead(alertId) {
			const alert = this.alerts.find((a) => a.id === alertId)
			if (alert) {
				alert.is_read = true
			}
		},

		// Dismiss alert
		dismissAlert(alertId) {
			const index = this.alerts.findIndex((a) => a.id === alertId)
			if (index > -1) {
				this.alerts.splice(index, 1)
			}
		},

		// Set filters
		setFrameworkFilters(frameworks) {
			this.selectedFrameworks = frameworks
		},

		setStatusFilters(statuses) {
			this.selectedStatuses = statuses
		},

		setCategoryFilters(categories) {
			this.selectedCategories = categories
		},

		// Set active items
		setActiveRequirement(requirement) {
			this.activeRequirement = requirement
		},

		setActiveAssessment(assessment) {
			this.activeAssessment = assessment
		},

		// Set current view
		setCurrentView(view) {
			this.currentView = view
		},

		// Clear state
		clearError() {
			this.error = null
		},

		clearFilters() {
			this.selectedFrameworks = []
			this.selectedStatuses = []
			this.selectedCategories = []
		},
	},
})
