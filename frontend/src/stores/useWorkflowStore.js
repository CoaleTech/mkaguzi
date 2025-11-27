import { defineStore } from "pinia"

export const useWorkflowStore = defineStore("workflow", {
	state: () => ({
		// Workflows
		workflows: [],
		activeWorkflow: null,
		workflowTemplates: [],

		// Workflow instances
		workflowInstances: [],
		activeInstance: null,

		// Triggers
		triggers: [],
		triggerTypes: [
			{
				id: "schedule",
				label: "Scheduled",
				icon: "clock",
				description: "Run on a specific schedule (daily, weekly, monthly)",
			},
			{
				id: "event",
				label: "Event-based",
				icon: "zap",
				description: "Triggered by system events or data changes",
			},
			{
				id: "manual",
				label: "Manual",
				icon: "play",
				description: "Manually triggered by users",
			},
			{
				id: "condition",
				label: "Condition-based",
				icon: "filter",
				description: "Triggered when specific conditions are met",
			},
		],

		// Conditions
		conditions: [],
		conditionTypes: [
			{
				id: "field_value",
				label: "Field Value",
				description: "Check if a field equals, contains, or matches a value",
			},
			{
				id: "date_range",
				label: "Date Range",
				description: "Check if a date falls within a specific range",
			},
			{
				id: "count",
				label: "Record Count",
				description: "Check the count of records matching criteria",
			},
			{
				id: "status",
				label: "Status Check",
				description: "Check the status of a record or process",
			},
			{
				id: "user_role",
				label: "User Role",
				description: "Check if user has specific role or permission",
			},
			{
				id: "custom",
				label: "Custom Logic",
				description: "Custom JavaScript condition evaluation",
			},
		],

		// Actions
		actions: [],
		actionTypes: [
			{
				id: "create_record",
				label: "Create Record",
				icon: "plus",
				description: "Create a new record in any DocType",
				category: "data",
			},
			{
				id: "update_record",
				label: "Update Record",
				icon: "edit",
				description: "Update existing record fields",
				category: "data",
			},
			{
				id: "delete_record",
				label: "Delete Record",
				icon: "trash",
				description: "Delete an existing record",
				category: "data",
			},
			{
				id: "send_email",
				label: "Send Email",
				icon: "mail",
				description: "Send email notifications",
				category: "notification",
			},
			{
				id: "send_notification",
				label: "Send Notification",
				icon: "bell",
				description: "Send in-app notifications",
				category: "notification",
			},
			{
				id: "create_task",
				label: "Create Task",
				icon: "check-square",
				description: "Create audit tasks or assignments",
				category: "workflow",
			},
			{
				id: "generate_report",
				label: "Generate Report",
				icon: "file-text",
				description: "Generate and distribute reports",
				category: "reporting",
			},
			{
				id: "call_webhook",
				label: "Call Webhook",
				icon: "link",
				description: "Make HTTP requests to external systems",
				category: "integration",
			},
			{
				id: "run_script",
				label: "Run Script",
				icon: "code",
				description: "Execute custom JavaScript code",
				category: "custom",
			},
		],

		// Execution history
		executionHistory: [],

		// Statistics
		statistics: {
			totalWorkflows: 0,
			activeWorkflows: 0,
			successRate: 0,
			totalExecutions: 0,
			failedExecutions: 0,
			avgExecutionTime: 0,
		},

		// UI State
		isLoading: false,
		error: null,
		selectedWorkflows: [],
		currentView: "list", // list, designer, instances, analytics
		designerState: {
			selectedNode: null,
			draggedNode: null,
			canvasScale: 1,
			canvasOffset: { x: 0, y: 0 },
		},
	}),

	getters: {
		// Workflow getters
		getWorkflowById: (state) => (id) => {
			return state.workflows.find((workflow) => workflow.id === id)
		},

		getActiveWorkflows: (state) => {
			return state.workflows.filter((workflow) => workflow.is_active)
		},

		getWorkflowsByCategory: (state) => (category) => {
			return state.workflows.filter(
				(workflow) => workflow.category === category,
			)
		},

		// Instance getters
		getInstancesByWorkflow: (state) => (workflowId) => {
			return state.workflowInstances.filter(
				(instance) => instance.workflow_id === workflowId,
			)
		},

		getRunningInstances: (state) => {
			return state.workflowInstances.filter(
				(instance) => instance.status === "Running",
			)
		},

		getRecentExecutions: (state) => {
			return state.executionHistory
				.sort((a, b) => new Date(b.executed_at) - new Date(a.executed_at))
				.slice(0, 10)
		},

		// Statistics getters
		getSuccessRate: (state) => {
			if (state.statistics.totalExecutions === 0) return 0
			return (
				((state.statistics.totalExecutions -
					state.statistics.failedExecutions) /
					state.statistics.totalExecutions) *
				100
			).toFixed(1)
		},

		getWorkflowPerformance: (state) => {
			return state.workflows.map((workflow) => ({
				id: workflow.id,
				name: workflow.name,
				executions: state.executionHistory.filter(
					(h) => h.workflow_id === workflow.id,
				).length,
				successRate: state.executionHistory.filter(
					(h) => h.workflow_id === workflow.id && h.status === "Success",
				).length,
				avgDuration: state.executionHistory
					.filter((h) => h.workflow_id === workflow.id && h.duration)
					.reduce((acc, h, _, arr) => acc + h.duration / arr.length, 0),
			}))
		},

		// Filter getters
		getActionsByCategory: (state) => (category) => {
			return state.actionTypes.filter((action) => action.category === category)
		},
	},

	actions: {
		// Load workflows
		async loadWorkflows() {
			this.isLoading = true
			this.error = null

			try {
				// Simulate API call
				const mockWorkflows = [
					{
						id: "wf-001",
						name: "Daily Compliance Check",
						description: "Automated daily compliance monitoring and reporting",
						category: "compliance",
						is_active: true,
						created_by: "admin",
						created_at: new Date(
							Date.now() - 5 * 24 * 60 * 60 * 1000,
						).toISOString(),
						last_run: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
						next_run: new Date(Date.now() + 23 * 60 * 60 * 1000).toISOString(),
						triggers: [
							{
								type: "schedule",
								config: { cron: "0 9 * * *", timezone: "UTC" },
							},
						],
						steps: [
							{
								id: "step-1",
								name: "Check Pending Audits",
								type: "condition",
								config: {
									doctype: "Audit Test",
									filters: { status: "Pending" },
									condition: "count > 0",
								},
							},
							{
								id: "step-2",
								name: "Send Alert Email",
								type: "send_email",
								config: {
									to: ["audit.manager@company.com"],
									subject: "Pending Audits Alert",
									template: "pending_audits_alert",
								},
							},
						],
						execution_count: 45,
						success_count: 44,
						last_status: "Success",
					},
					{
						id: "wf-002",
						name: "Risk Assessment Automation",
						description: "Automatically assess and categorize identified risks",
						category: "risk_management",
						is_active: true,
						created_by: "risk.manager",
						created_at: new Date(
							Date.now() - 10 * 24 * 60 * 60 * 1000,
						).toISOString(),
						last_run: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
						next_run: null,
						triggers: [
							{
								type: "event",
								config: { doctype: "Risk", event: "on_update" },
							},
						],
						steps: [
							{
								id: "step-1",
								name: "Calculate Risk Score",
								type: "run_script",
								config: {
									script: "risk.likelihood * risk.impact",
								},
							},
							{
								id: "step-2",
								name: "Update Risk Level",
								type: "update_record",
								config: {
									doctype: "Risk",
									fields: { risk_level: "calculated_level" },
								},
							},
							{
								id: "step-3",
								name: "High Risk Notification",
								type: "condition",
								config: {
									condition:
										"risk_level === 'High' || risk_level === 'Critical'",
								},
							},
							{
								id: "step-4",
								name: "Notify Risk Committee",
								type: "send_notification",
								config: {
									recipients: ["Risk Committee"],
									message: "High-risk item requires attention",
								},
							},
						],
						execution_count: 23,
						success_count: 22,
						last_status: "Success",
					},
					{
						id: "wf-003",
						name: "Audit Report Distribution",
						description: "Automatically generate and distribute audit reports",
						category: "reporting",
						is_active: false,
						created_by: "admin",
						created_at: new Date(
							Date.now() - 15 * 24 * 60 * 60 * 1000,
						).toISOString(),
						last_run: new Date(
							Date.now() - 7 * 24 * 60 * 60 * 1000,
						).toISOString(),
						next_run: null,
						triggers: [
							{
								type: "schedule",
								config: { cron: "0 17 * * 5", timezone: "UTC" },
							},
						],
						steps: [
							{
								id: "step-1",
								name: "Generate Weekly Report",
								type: "generate_report",
								config: {
									template: "weekly_audit_summary",
									format: "pdf",
								},
							},
							{
								id: "step-2",
								name: "Email to Stakeholders",
								type: "send_email",
								config: {
									to: ["management@company.com", "board@company.com"],
									subject: "Weekly Audit Report",
									attachment: "generated_report",
								},
							},
						],
						execution_count: 12,
						success_count: 11,
						last_status: "Failed",
					},
				]

				this.workflows = mockWorkflows
				this.statistics.totalWorkflows = mockWorkflows.length
				this.statistics.activeWorkflows = mockWorkflows.filter(
					(w) => w.is_active,
				).length

				await this.loadExecutionHistory()
			} catch (error) {
				this.error = `Failed to load workflows: ${error.message}`
				console.error("Error loading workflows:", error)
			} finally {
				this.isLoading = false
			}
		},

		// Load execution history
		async loadExecutionHistory() {
			try {
				const mockHistory = [
					{
						id: "exec-001",
						workflow_id: "wf-001",
						workflow_name: "Daily Compliance Check",
						status: "Success",
						executed_at: new Date(
							Date.now() - 1 * 60 * 60 * 1000,
						).toISOString(),
						duration: 45000,
						steps_completed: 2,
						steps_total: 2,
						output: "2 pending audits found, alert email sent",
					},
					{
						id: "exec-002",
						workflow_id: "wf-002",
						workflow_name: "Risk Assessment Automation",
						status: "Success",
						executed_at: new Date(
							Date.now() - 2 * 60 * 60 * 1000,
						).toISOString(),
						duration: 12000,
						steps_completed: 4,
						steps_total: 4,
						output: "Risk level updated to High, notification sent",
					},
					{
						id: "exec-003",
						workflow_id: "wf-003",
						workflow_name: "Audit Report Distribution",
						status: "Failed",
						executed_at: new Date(
							Date.now() - 7 * 24 * 60 * 60 * 1000,
						).toISOString(),
						duration: 8000,
						steps_completed: 1,
						steps_total: 2,
						error: "Failed to send email: SMTP connection timeout",
					},
					{
						id: "exec-004",
						workflow_id: "wf-001",
						workflow_name: "Daily Compliance Check",
						status: "Success",
						executed_at: new Date(
							Date.now() - 25 * 60 * 60 * 1000,
						).toISOString(),
						duration: 38000,
						steps_completed: 2,
						steps_total: 2,
						output: "0 pending audits found",
					},
				]

				this.executionHistory = mockHistory
				this.statistics.totalExecutions = mockHistory.length
				this.statistics.failedExecutions = mockHistory.filter(
					(h) => h.status === "Failed",
				).length
				this.statistics.avgExecutionTime =
					mockHistory.reduce((acc, h) => acc + (h.duration || 0), 0) /
					mockHistory.length
			} catch (error) {
				console.error("Error loading execution history:", error)
			}
		},

		// Load workflow instances
		async loadWorkflowInstances() {
			try {
				const mockInstances = [
					{
						id: "inst-001",
						workflow_id: "wf-001",
						workflow_name: "Daily Compliance Check",
						status: "Completed",
						started_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
						completed_at: new Date(
							Date.now() - 1 * 60 * 60 * 1000 + 45000,
						).toISOString(),
						current_step: null,
						progress: 100,
					},
					{
						id: "inst-002",
						workflow_id: "wf-002",
						workflow_name: "Risk Assessment Automation",
						status: "Running",
						started_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
						completed_at: null,
						current_step: "step-2",
						progress: 50,
					},
				]

				this.workflowInstances = mockInstances
			} catch (error) {
				console.error("Error loading workflow instances:", error)
			}
		},

		// Create workflow
		async createWorkflow(workflowData) {
			this.isLoading = true

			try {
				const newWorkflow = {
					id: `wf-${Date.now()}`,
					...workflowData,
					created_by: "current_user",
					created_at: new Date().toISOString(),
					execution_count: 0,
					success_count: 0,
					last_status: null,
					is_active: workflowData.is_active ?? true,
				}

				this.workflows.push(newWorkflow)
				this.statistics.totalWorkflows++
				if (newWorkflow.is_active) {
					this.statistics.activeWorkflows++
				}

				return newWorkflow
			} catch (error) {
				this.error = `Failed to create workflow: ${error.message}`
				throw error
			} finally {
				this.isLoading = false
			}
		},

		// Update workflow
		async updateWorkflow(workflowId, updates) {
			try {
				const workflow = this.getWorkflowById(workflowId)
				if (!workflow) {
					throw new Error("Workflow not found")
				}

				const wasActive = workflow.is_active
				Object.assign(workflow, updates, {
					updated_at: new Date().toISOString(),
				})

				// Update statistics
				if (wasActive !== workflow.is_active) {
					if (workflow.is_active) {
						this.statistics.activeWorkflows++
					} else {
						this.statistics.activeWorkflows--
					}
				}

				return workflow
			} catch (error) {
				this.error = `Failed to update workflow: ${error.message}`
				throw error
			}
		},

		// Delete workflow
		async deleteWorkflow(workflowId) {
			try {
				const index = this.workflows.findIndex((w) => w.id === workflowId)
				if (index === -1) {
					throw new Error("Workflow not found")
				}

				const workflow = this.workflows[index]
				this.workflows.splice(index, 1)

				this.statistics.totalWorkflows--
				if (workflow.is_active) {
					this.statistics.activeWorkflows--
				}

				// Remove related execution history
				this.executionHistory = this.executionHistory.filter(
					(h) => h.workflow_id !== workflowId,
				)
			} catch (error) {
				this.error = `Failed to delete workflow: ${error.message}`
				throw error
			}
		},

		// Execute workflow manually
		async executeWorkflow(workflowId) {
			try {
				const workflow = this.getWorkflowById(workflowId)
				if (!workflow) {
					throw new Error("Workflow not found")
				}

				// Create instance
				const instance = {
					id: `inst-${Date.now()}`,
					workflow_id: workflowId,
					workflow_name: workflow.name,
					status: "Running",
					started_at: new Date().toISOString(),
					completed_at: null,
					current_step: workflow.steps[0]?.id || null,
					progress: 0,
				}

				this.workflowInstances.push(instance)

				// Simulate execution (in real implementation, this would be handled by background job)
				setTimeout(() => {
					this.completeWorkflowInstance(
						instance.id,
						"Success",
						"Manual execution completed successfully",
					)
				}, 3000)

				return instance
			} catch (error) {
				this.error = `Failed to execute workflow: ${error.message}`
				throw error
			}
		},

		// Complete workflow instance
		completeWorkflowInstance(instanceId, status, output = null, error = null) {
			const instance = this.workflowInstances.find((i) => i.id === instanceId)
			if (instance) {
				instance.status = status
				instance.completed_at = new Date().toISOString()
				instance.progress = status === "Success" ? 100 : instance.progress

				// Add to execution history
				const execution = {
					id: `exec-${Date.now()}`,
					workflow_id: instance.workflow_id,
					workflow_name: instance.workflow_name,
					status,
					executed_at: instance.started_at,
					duration:
						new Date(instance.completed_at) - new Date(instance.started_at),
					steps_completed:
						status === "Success"
							? instance.progress
							: Math.floor(instance.progress * 0.01),
					steps_total:
						this.getWorkflowById(instance.workflow_id)?.steps?.length || 1,
					output,
					error,
				}

				this.executionHistory.unshift(execution)

				// Update workflow statistics
				const workflow = this.getWorkflowById(instance.workflow_id)
				if (workflow) {
					workflow.execution_count++
					workflow.last_run = instance.completed_at
					workflow.last_status = status

					if (status === "Success") {
						workflow.success_count++
					}
				}

				// Update global statistics
				this.statistics.totalExecutions++
				if (status === "Failed") {
					this.statistics.failedExecutions++
				}
			}
		},

		// Toggle workflow status
		async toggleWorkflowStatus(workflowId) {
			const workflow = this.getWorkflowById(workflowId)
			if (workflow) {
				await this.updateWorkflow(workflowId, {
					is_active: !workflow.is_active,
				})
			}
		},

		// Duplicate workflow
		async duplicateWorkflow(workflowId) {
			const workflow = this.getWorkflowById(workflowId)
			if (!workflow) {
				throw new Error("Workflow not found")
			}

			const duplicate = {
				...workflow,
				id: `wf-${Date.now()}`,
				name: `${workflow.name} (Copy)`,
				created_at: new Date().toISOString(),
				execution_count: 0,
				success_count: 0,
				last_status: null,
				last_run: null,
				is_active: false,
			}

			this.workflows.push(duplicate)
			this.statistics.totalWorkflows++

			return duplicate
		},

		// Bulk operations
		async bulkUpdateWorkflows(workflowIds, updates) {
			const results = []

			for (const workflowId of workflowIds) {
				try {
					const result = await this.updateWorkflow(workflowId, updates)
					results.push({ id: workflowId, success: true, result })
				} catch (error) {
					results.push({ id: workflowId, success: false, error: error.message })
				}
			}

			return results
		},

		// Set active workflow
		setActiveWorkflow(workflow) {
			this.activeWorkflow = workflow
		},

		// Set current view
		setCurrentView(view) {
			this.currentView = view
		},

		// Designer state management
		setSelectedNode(node) {
			this.designerState.selectedNode = node
		},

		setDraggedNode(node) {
			this.designerState.draggedNode = node
		},

		updateCanvasTransform(scale, offset) {
			this.designerState.canvasScale = scale
			this.designerState.canvasOffset = offset
		},

		// Clear state
		clearError() {
			this.error = null
		},

		clearSelection() {
			this.selectedWorkflows = []
		},
	},
})
