import { createResource } from "frappe-ui"
import { computed, ref } from "vue"
import { defineStore } from "pinia"

export const useAgentStore = defineStore("agents", () => {
	// State
	const agents = ref([])
	const executions = ref([])
	const currentExecution = ref(null)
	const agentConfigs = ref([])
	const loading = ref(false)
	const error = ref(null)

	// Computed
	const runningExecutions = computed(() =>
		executions.value.filter((e) => e.status === "Running")
	)
	const completedExecutions = computed(() =>
		executions.value.filter((e) => e.status === "Completed")
	)
	const failedExecutions = computed(() =>
		executions.value.filter((e) => e.status === "Failed")
	)
	const activeConfigs = computed(() =>
		agentConfigs.value.filter((c) => c.is_active)
	)
	const avgDuration = computed(() => {
		const completed = executions.value.filter((e) => e.duration_seconds > 0)
		if (completed.length === 0) return 0
		return (
			completed.reduce((sum, e) => sum + e.duration_seconds, 0) /
			completed.length
		)
	})

	// Actions
	const fetchAvailableAgents = async () => {
		try {
			const res = await createResource({
				url: "mkaguzi.api.agents.get_available_agents",
			}).fetch()
			agents.value = res || []
		} catch (err) {
			console.error("Failed to fetch agents:", err)
			agents.value = []
		}
	}

	const fetchExecutions = async (filters = {}) => {
		loading.value = true
		error.value = null
		try {
			const params = {
				doctype: "Agent Execution Log",
				fields: [
					"name", "agent_id", "agent_type", "agent_name", "task_type",
					"task_name", "status", "start_time", "end_time", "duration_seconds",
					"total_findings", "critical_findings", "high_severity_findings",
					"records_processed", "error_occurred", "error_message",
					"engagement_reference", "working_paper_reference",
					"progress_percentage", "execution_mode", "priority",
					"total_tests", "passed_tests", "failed_tests",
				],
				filters: filters,
				order_by: "start_time desc",
				limit_page_length: 100,
			}
			const res = await createResource({
				url: "frappe.client.get_list",
				params,
			}).fetch()
			executions.value = res || []
		} catch (err) {
			console.error("Failed to fetch executions:", err)
			error.value = err.message || "Failed to load executions"
			executions.value = []
		} finally {
			loading.value = false
		}
	}

	const fetchExecutionDetail = async (name) => {
		loading.value = true
		error.value = null
		try {
			const res = await createResource({
				url: "frappe.client.get",
				params: { doctype: "Agent Execution Log", name },
			}).fetch()
			currentExecution.value = res || null
			return res
		} catch (err) {
			console.error("Failed to fetch execution detail:", err)
			error.value = err.message || "Failed to load execution"
			currentExecution.value = null
		} finally {
			loading.value = false
		}
	}

	const executeAgent = async (agentType, params = {}) => {
		try {
			const res = await createResource({
				url: "mkaguzi.api.agents.execute_agent",
				params: { agent_type: agentType, ...params },
			}).fetch()
			await fetchExecutions()
			return res
		} catch (err) {
			console.error("Failed to execute agent:", err)
			throw err
		}
	}

	const runAllAgents = async (params = {}) => {
		try {
			const res = await createResource({
				url: "mkaguzi.api.agents.run_all_agents_background",
				params,
			}).fetch()
			return res
		} catch (err) {
			console.error("Failed to run all agents:", err)
			throw err
		}
	}

	const cancelExecution = async (executionName) => {
		try {
			await createResource({
				url: "mkaguzi.api.agents.cancel_agent_execution",
				params: { execution_id: executionName },
			}).fetch()
			await fetchExecutions()
		} catch (err) {
			console.error("Failed to cancel execution:", err)
			throw err
		}
	}

	const fetchAgentConfigs = async () => {
		try {
			const res = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Agent Configuration",
					fields: [
						"name", "agent_type", "configuration_name", "is_active",
						"description", "priority", "execution_schedule",
						"timeout_seconds", "max_memory_mb", "max_cpu_percent",
						"max_concurrent_tasks", "log_level",
						"notification_on_failure",
					],
					limit_page_length: 50,
				},
			}).fetch()
			agentConfigs.value = res || []
		} catch (err) {
			console.error("Failed to fetch agent configs:", err)
			agentConfigs.value = []
		}
	}

	const fetchAgentConfigDetail = async (name) => {
		try {
			return await createResource({
				url: "frappe.client.get",
				params: { doctype: "Agent Configuration", name },
			}).fetch()
		} catch (err) {
			console.error("Failed to fetch config detail:", err)
			return null
		}
	}

	const updateAgentConfig = async (name, fieldname, value) => {
		try {
			await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Agent Configuration",
					name,
					fieldname,
					value,
				},
			}).fetch()
			await fetchAgentConfigs()
		} catch (err) {
			console.error("Failed to update config:", err)
			throw err
		}
	}

	return {
		agents,
		executions,
		currentExecution,
		agentConfigs,
		loading,
		error,
		runningExecutions,
		completedExecutions,
		failedExecutions,
		activeConfigs,
		avgDuration,
		fetchAvailableAgents,
		fetchExecutions,
		fetchExecutionDetail,
		executeAgent,
		runAllAgents,
		cancelExecution,
		fetchAgentConfigs,
		fetchAgentConfigDetail,
		updateAgentConfig,
	}
})
