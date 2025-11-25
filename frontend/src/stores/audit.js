import { createResource } from "frappe-ui"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useAuditStore = defineStore("audit", () => {
	// State
	const currentEngagement = ref(null)
	const auditPlan = ref(null)
	const findings = ref([])
	const engagements = ref([])
	const findingsCache = ref(new Map())

	// Audit Planning State
	const annualPlans = ref([])
	const auditPrograms = ref([])
	const auditCalendar = ref([])
	const auditProcedures = ref([])
	const auditUniverse = ref([])
	const riskAssessments = ref([])

	// Getters
	const activeEngagements = computed(() => {
		return engagements.value.filter(
			(e) => e.status === "in_progress" || e.status === "active",
		)
	})

	const criticalFindings = computed(() => {
		return findings.value.filter(
			(finding) => finding.risk_rating === "Critical",
		)
	})

	const overdueFindings = computed(() => {
		const now = new Date()
		return findings.value.filter((finding) => {
			if (!finding.due_date) return false
			return new Date(finding.due_date) < now && finding.status !== "Closed"
		})
	})

	const findingsByStatus = computed(() => {
		const statusCounts = {}
		findings.value.forEach((finding) => {
			statusCounts[finding.status] = (statusCounts[finding.status] || 0) + 1
		})
		return statusCounts
	})

	// Audit Planning Getters
	const activeAnnualPlans = computed(() => {
		return annualPlans.value.filter(
			(plan) => plan.status === "Active" || plan.status === "Approved",
		)
	})

	const plannedAudits = computed(() => {
		const audits = []
		annualPlans.value.forEach((plan) => {
			if (plan.planned_audits) {
				audits.push(...plan.planned_audits)
			}
		})
		return audits
	})

	const upcomingAudits = computed(() => {
		const now = new Date()
		return auditCalendar.value
			.filter((item) => {
				const startDate = new Date(item.planned_start_date)
				return startDate > now && item.status === "Planned"
			})
			.sort(
				(a, b) =>
					new Date(a.planned_start_date) - new Date(b.planned_start_date),
			)
	})

	const auditProgramTemplates = computed(() => {
		return auditPrograms.value.filter((program) => program.is_template)
	})

	// Risk Assessment Getters
	const criticalRiskAssessments = computed(() => {
		return riskAssessments.value.filter(
			(assessment) => assessment.overall_risk_rating === "Critical",
		)
	})

	const highRiskAssessments = computed(() => {
		return riskAssessments.value.filter(
			(assessment) => assessment.overall_risk_rating === "High",
		)
	})

	const riskAssessmentByStatus = computed(() => {
		const statusCounts = {}
		riskAssessments.value.forEach((assessment) => {
			statusCounts[assessment.approval_status] =
				(statusCounts[assessment.approval_status] || 0) + 1
		})
		return statusCounts
	})

	// Actions
	const setCurrentEngagement = (engagement) => {
		currentEngagement.value = engagement
	}

	const setAuditPlan = (plan) => {
		auditPlan.value = plan
	}

	const setFindings = (findingsList) => {
		findings.value = findingsList
		// Update cache
		findingsList.forEach((finding) => {
			findingsCache.value.set(finding.name, finding)
		})
	}

	const setEngagements = (engagementsList) => {
		engagements.value = engagementsList
	}

	const addFinding = (finding) => {
		findings.value.push(finding)
		findingsCache.value.set(finding.name, finding)
	}

	const addEngagement = (engagement) => {
		engagements.value.push(engagement)
	}

	const updateFinding = (findingName, updates) => {
		const index = findings.value.findIndex((f) => f.name === findingName)
		if (index !== -1) {
			findings.value[index] = { ...findings.value[index], ...updates }
			findingsCache.value.set(findingName, findings.value[index])
		}
	}

	const updateEngagement = (engagementName, updates) => {
		const index = engagements.value.findIndex((e) => e.name === engagementName)
		if (index !== -1) {
			engagements.value[index] = { ...engagements.value[index], ...updates }
		}
	}

	const removeFinding = (findingName) => {
		findings.value = findings.value.filter((f) => f.name !== findingName)
		findingsCache.value.delete(findingName)
	}

	const removeEngagement = (engagementName) => {
		engagements.value = engagements.value.filter(
			(e) => e.name !== engagementName,
		)
	}

	const getFindingById = (findingName) => {
		return findingsCache.value.get(findingName)
	}

	const getEngagementById = (engagementName) => {
		return engagements.value.find((e) => e.name === engagementName)
	}

	const fetchEngagements = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Audit Engagement",
					fields: [
						"name",
						"engagement_id",
						"engagement_title",
						"status",
						"audit_type",
						"period_start",
						"period_end",
						"creation",
						"modified",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			setEngagements(response || [])
		} catch (error) {
			console.error("Error fetching engagements:", error)
			setEngagements([])
		}
	}

	const fetchFindings = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Audit Finding",
					fields: [
						"name",
						"finding_id",
						"finding_title",
						"risk_rating",
						"creation",
						"modified",
						"engagement_reference",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			setFindings(response || [])
		} catch (error) {
			console.error("Error fetching findings:", error)
			setFindings([])
		}
	}

	// Audit Planning Actions
	const fetchAnnualPlans = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Annual Audit Plan",
					fields: [
						"name",
						"plan_id",
						"plan_year",
						"status",
						"total_available_days",
						"total_planned_days",
						"utilization_percentage",
						"creation",
						"modified",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			annualPlans.value = response || []
		} catch (error) {
			console.error("Error fetching annual plans:", error)
			annualPlans.value = []
		}
	}

	const fetchAnnualPlanDetails = async (planId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "Annual Audit Plan",
					name: planId,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error fetching annual plan details:", error)
			return null
		}
	}

	const createAnnualPlan = async (planData) => {
		try {
			const response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Annual Audit Plan",
						...planData,
					},
				},
			}).fetch()
			await fetchAnnualPlans() // Refresh the list
			return response
		} catch (error) {
			console.error("Error creating annual plan:", error)
			throw error
		}
	}

	const updateAnnualPlan = async (planId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Annual Audit Plan",
					name: planId,
					fieldname: updates,
				},
			}).fetch()
			await fetchAnnualPlans() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating annual plan:", error)
			throw error
		}
	}

	const fetchAuditPrograms = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Audit Program",
					fields: [
						"name",
						"program_id",
						"program_name",
						"audit_type",
						"is_template",
						"engagement_reference",
						"total_procedures",
						"completed_procedures",
						"completion_percent",
						"status",
						"creation",
						"modified",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			auditPrograms.value = response || []
		} catch (error) {
			console.error("Error fetching audit programs:", error)
			auditPrograms.value = []
		}
	}

	const fetchAuditProgramDetails = async (programId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "Audit Program",
					name: programId,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error fetching audit program details:", error)
			return null
		}
	}

	const createAuditProgram = async (programData) => {
		try {
			const response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Audit Program",
						...programData,
					},
				},
			}).fetch()
			await fetchAuditPrograms() // Refresh the list
			return response
		} catch (error) {
			console.error("Error creating audit program:", error)
			throw error
		}
	}

	const updateAuditProgram = async (programId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Audit Program",
					name: programId,
					fieldname: updates,
				},
			}).fetch()
			await fetchAuditPrograms() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating audit program:", error)
			throw error
		}
	}

	const fetchAuditCalendar = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Audit Calendar",
					fields: [
						"name",
						"calendar_id",
						"audit_universe",
						"audit_type",
						"status",
						"planned_start_date",
						"planned_end_date",
						"actual_start_date",
						"actual_end_date",
						"lead_auditor",
						"progress_percentage",
						"creation",
						"modified",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			auditCalendar.value = response || []
		} catch (error) {
			console.error("Error fetching audit calendar:", error)
			auditCalendar.value = []
		}
	}

	const fetchAuditCalendarDetails = async (calendarId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "Audit Calendar",
					name: calendarId,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error fetching audit calendar details:", error)
			return null
		}
	}

	const createAuditCalendarEntry = async (calendarData) => {
		try {
			const response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Audit Calendar",
						...calendarData,
					},
				},
			}).fetch()
			await fetchAuditCalendar() // Refresh the list
			return response
		} catch (error) {
			console.error("Error creating audit calendar entry:", error)
			throw error
		}
	}

	const updateAuditCalendarEntry = async (calendarId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Audit Calendar",
					name: calendarId,
					fieldname: updates,
				},
			}).fetch()
			await fetchAuditCalendar() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating audit calendar entry:", error)
			throw error
		}
	}

	const fetchAuditProcedures = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Audit Procedure",
					fields: [
						"name",
						"procedure_id",
						"procedure_name",
						"procedure_type",
						"risk_area",
						"estimated_hours",
						"status",
						"program_reference",
						"creation",
						"modified",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			auditProcedures.value = response || []
		} catch (error) {
			console.error("Error fetching audit procedures:", error)
			auditProcedures.value = []
		}
	}

	const fetchAuditUniverse = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Audit Universe",
					fields: [
						"name",
						"universe_id",
						"auditable_entity",
						"entity_type",
						"department",
						"location",
						"process_owner",
						"inherent_risk_rating",
						"last_audit_date",
						"next_scheduled_audit",
						"is_active",
						"creation",
						"modified",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			auditUniverse.value = response || []
		} catch (error) {
			console.error("Error fetching audit universe:", error)
			auditUniverse.value = []
		}
	}

	// Risk Assessment Actions
	const fetchRiskAssessments = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Risk Assessment",
					fields: [
						"name",
						"assessment_id",
						"assessment_name",
						"assessment_period",
						"assessment_date",
						"fiscal_year",
						"status",
						"prepared_by",
						"approved_by",
						"approval_date",
						"creation",
						"modified",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			riskAssessments.value = response || []
		} catch (error) {
			console.error("Error fetching risk assessments:", error)
			riskAssessments.value = []
		}
	}

	const fetchRiskAssessmentDetails = async (assessmentId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "Risk Assessment",
					name: assessmentId,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error fetching risk assessment details:", error)
			return null
		}
	}

	const createRiskAssessment = async (assessmentData) => {
		try {
			const response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Risk Assessment",
						...assessmentData,
					},
				},
			}).fetch()
			await fetchRiskAssessments() // Refresh the list
			return response
		} catch (error) {
			console.error("Error creating risk assessment:", error)
			throw error
		}
	}

	const updateRiskAssessment = async (assessmentId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Risk Assessment",
					name: assessmentId,
					fieldname: updates,
				},
			}).fetch()
			await fetchRiskAssessments() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating risk assessment:", error)
			throw error
		}
	}

	// Working Papers State
	const workingPapers = ref([])

	// Findings & Follow-up State
	const followUpTrackers = ref([])
	const correctiveActionPlans = ref([])
	const findingEvidence = ref([])
	const findingStatusChanges = ref([])
	const followUpActivities = ref([])

	// Working Papers Actions
	const fetchWorkingPapers = async () => {
		try {
			const response = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Working Paper",
					fields: [
						"name",
						"working_paper_id",
						"wp_title",
						"wp_reference_no",
						"wp_type",
						"engagement_reference",
						"procedure_reference",
						"prepared_by",
						"preparation_date",
						"reviewed_by",
						"review_date",
						"review_status",
						"work_performed",
						"objective",
						"scope",
						"creation",
						"modified",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			workingPapers.value = response || []
		} catch (error) {
			console.error("Error fetching working papers:", error)
			workingPapers.value = []
		}
	}

	const fetchWorkingPaperDetails = async (wpId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "Working Paper",
					name: wpId,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error fetching working paper details:", error)
			return null
		}
	}

	const createWorkingPaper = async (wpData) => {
		try {
			const response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Working Paper",
						...wpData,
					},
				},
			}).fetch()
			await fetchWorkingPapers() // Refresh the list
			return response
		} catch (error) {
			console.error("Error creating working paper:", error)
			throw error
		}
	}

	const updateWorkingPaper = async (wpId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Working Paper",
					name: wpId,
					fieldname: updates,
				},
			}).fetch()
			await fetchWorkingPapers() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating working paper:", error)
			throw error
		}
	}

	// Findings & Follow-up Actions
	const fetchFindingDetails = async (findingId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "Audit Finding",
					name: findingId,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error fetching finding details:", error)
			return null
		}
	}

	const createFinding = async (findingData) => {
		try {
			const response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Audit Finding",
						...findingData,
					},
				},
			}).fetch()
			await fetchFindings() // Refresh the list
			return response
		} catch (error) {
			console.error("Error creating finding:", error)
			throw error
		}
	}

	const updateFindingDetails = async (findingId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Audit Finding",
					name: findingId,
					fieldname: updates,
				},
			}).fetch()
			await fetchFindings() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating finding:", error)
			throw error
		}
	}

	const fetchFollowUpTrackers = async () => {
		try {
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
						"start_date",
						"next_due_date",
						"frequency",
						"responsible_person",
						"responsible_department",
						"last_follow_up_date",
						"current_status",
						"progress_rating",
						"creation",
						"modified",
					],
					limit_page_length: 1000,
				},
			}).fetch()
			followUpTrackers.value = response || []
		} catch (error) {
			console.error("Error fetching follow-up trackers:", error)
			followUpTrackers.value = []
		}
	}

	const fetchFollowUpTrackerDetails = async (trackerId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "Follow-up Tracker",
					name: trackerId,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error fetching follow-up tracker details:", error)
			return null
		}
	}

	const createFollowUpTracker = async (trackerData) => {
		try {
			const response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Follow-up Tracker",
						...trackerData,
					},
				},
			}).fetch()
			await fetchFollowUpTrackers() // Refresh the list
			return response
		} catch (error) {
			console.error("Error creating follow-up tracker:", error)
			throw error
		}
	}

	const updateFollowUpTracker = async (trackerId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Follow-up Tracker",
					name: trackerId,
					fieldname: updates,
				},
			}).fetch()
			await fetchFollowUpTrackers() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating follow-up tracker:", error)
			throw error
		}
	}

	const fetchCorrectiveActionPlans = async () => {
		try {
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
					limit_page_length: 1000,
				},
			}).fetch()
			correctiveActionPlans.value = response || []
		} catch (error) {
			console.error("Error fetching corrective action plans:", error)
			correctiveActionPlans.value = []
		}
	}

	const fetchCorrectiveActionPlanDetails = async (planId) => {
		try {
			const response = await createResource({
				url: "frappe.client.get",
				params: {
					doctype: "Corrective Action Plan",
					name: planId,
				},
			}).fetch()
			return response
		} catch (error) {
			console.error("Error fetching corrective action plan details:", error)
			return null
		}
	}

	const createCorrectiveActionPlan = async (planData) => {
		try {
			const response = await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Corrective Action Plan",
						...planData,
					},
				},
			}).fetch()
			await fetchCorrectiveActionPlans() // Refresh the list
			return response
		} catch (error) {
			console.error("Error creating corrective action plan:", error)
			throw error
		}
	}

	const updateCorrectiveActionPlan = async (planId, updates) => {
		try {
			const response = await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Corrective Action Plan",
					name: planId,
					fieldname: updates,
				},
			}).fetch()
			await fetchCorrectiveActionPlans() // Refresh the list
			return response
		} catch (error) {
			console.error("Error updating corrective action plan:", error)
			throw error
		}
	}

	const clearCache = () => {
		findingsCache.value.clear()
		findings.value = []
		engagements.value = []
		annualPlans.value = []
		auditPrograms.value = []
		auditCalendar.value = []
		auditProcedures.value = []
		auditUniverse.value = []
		riskAssessments.value = []
		workingPapers.value = []
		followUpTrackers.value = []
		correctiveActionPlans.value = []
		findingEvidence.value = []
		findingStatusChanges.value = []
		followUpActivities.value = []
		currentEngagement.value = null
		auditPlan.value = null
	}

	return {
		// State
		currentEngagement,
		auditPlan,
		findings,
		engagements,
		findingsCache,
		annualPlans,
		auditPrograms,
		auditCalendar,
		auditProcedures,
		auditUniverse,
		riskAssessments,
		workingPapers,
		followUpTrackers,
		correctiveActionPlans,
		findingEvidence,
		findingStatusChanges,
		followUpActivities,

		// Getters
		activeEngagements,
		criticalFindings,
		overdueFindings,
		findingsByStatus,
		activeAnnualPlans,
		plannedAudits,
		upcomingAudits,
		auditProgramTemplates,
		criticalRiskAssessments,
		highRiskAssessments,
		riskAssessmentByStatus,

		// Actions
		setCurrentEngagement,
		setAuditPlan,
		setFindings,
		setEngagements,
		addFinding,
		addEngagement,
		updateFinding,
		updateEngagement,
		removeFinding,
		removeEngagement,
		getFindingById,
		getEngagementById,
		fetchEngagements,
		fetchFindings,
		fetchFindingDetails,
		createFinding,
		updateFindingDetails,
		fetchAnnualPlans,
		fetchAnnualPlanDetails,
		createAnnualPlan,
		updateAnnualPlan,
		fetchAuditPrograms,
		fetchAuditProgramDetails,
		createAuditProgram,
		updateAuditProgram,
		fetchAuditCalendar,
		fetchAuditCalendarDetails,
		createAuditCalendarEntry,
		updateAuditCalendarEntry,
		fetchAuditProcedures,
		fetchAuditUniverse,
		fetchRiskAssessments,
		fetchRiskAssessmentDetails,
		createRiskAssessment,
		updateRiskAssessment,
		fetchWorkingPapers,
		fetchWorkingPaperDetails,
		createWorkingPaper,
		updateWorkingPaper,
		fetchFollowUpTrackers,
		fetchFollowUpTrackerDetails,
		createFollowUpTracker,
		updateFollowUpTracker,
		fetchCorrectiveActionPlans,
		fetchCorrectiveActionPlanDetails,
		createCorrectiveActionPlan,
		updateCorrectiveActionPlan,
		clearCache,
	}
})
