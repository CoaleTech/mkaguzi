<template>
  <div class="workflow-automation-engine">
    <!-- Header -->
    <div class="workflow-header">
      <div class="header-content">
        <h2>Workflow Automation</h2>
        <p>Design, manage, and monitor automated business processes</p>
      </div>
      
      <div class="header-actions">
        <Button
          v-if="currentView !== 'designer'"
          variant="solid"
          @click="createNewWorkflow"
        >
          <template #prefix>
            <Plus class="w-4 h-4" />
          </template>
          Create Workflow
        </Button>
        
        <Dropdown :options="viewOptions" @click="handleViewChange">
          <template #default>
            <Button variant="outline">
              <template #prefix>
                <component :is="currentViewIcon" class="w-4 h-4" />
              </template>
              {{ currentViewLabel }}
              <ChevronDown class="w-4 h-4 ml-2" />
            </Button>
          </template>
        </Dropdown>
      </div>
    </div>

    <!-- Statistics Bar -->
    <div class="stats-bar">
      <div class="stat-item">
        <div class="stat-value">{{ workflowStore.statistics.totalWorkflows }}</div>
        <div class="stat-label">Total Workflows</div>
      </div>
      
      <div class="stat-item">
        <div class="stat-value">{{ workflowStore.statistics.activeWorkflows }}</div>
        <div class="stat-label">Active</div>
      </div>
      
      <div class="stat-item">
        <div class="stat-value">{{ workflowStore.getSuccessRate }}%</div>
        <div class="stat-label">Success Rate</div>
      </div>
      
      <div class="stat-item">
        <div class="stat-value">{{ runningInstancesCount }}</div>
        <div class="stat-label">Running Now</div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="workflow-content">
      <!-- List View -->
      <div v-if="currentView === 'list'" class="list-view">
        <WorkflowList
          :workflows="workflowStore.workflows"
          :loading="workflowStore.isLoading"
          :selected="workflowStore.selectedWorkflows"
          @select="handleWorkflowSelect"
          @execute="handleExecuteWorkflow"
          @edit="handleEditWorkflow"
          @duplicate="handleDuplicateWorkflow"
          @toggle-status="handleToggleStatus"
          @delete="handleDeleteWorkflow"
          @bulk-action="handleBulkAction"
        />
      </div>

      <!-- Designer View -->
      <div v-else-if="currentView === 'designer'" class="designer-view">
        <WorkflowDesigner
          :workflow="workflowStore.activeWorkflow"
          :triggers="workflowStore.triggerTypes"
          :conditions="workflowStore.conditionTypes"
          :actions="workflowStore.actionTypes"
          @save="handleSaveWorkflow"
          @cancel="handleCancelDesigner"
          @node-select="workflowStore.setSelectedNode"
        />
      </div>

      <!-- Instances View -->
      <div v-else-if="currentView === 'instances'" class="instances-view">
        <WorkflowInstances
          :instances="workflowStore.workflowInstances"
          :history="workflowStore.executionHistory"
          :loading="workflowStore.isLoading"
          @refresh="loadWorkflowInstances"
          @view-details="handleViewInstanceDetails"
          @cancel-instance="handleCancelInstance"
        />
      </div>

      <!-- Analytics View -->
      <div v-else-if="currentView === 'analytics'" class="analytics-view">
        <WorkflowAnalytics
          :workflows="workflowStore.workflows"
          :executions="workflowStore.executionHistory"
          :statistics="workflowStore.statistics"
          :performance="workflowStore.getWorkflowPerformance"
        />
      </div>
    </div>

    <!-- Create Workflow Modal -->
    <Dialog
      v-if="showCreateModal"
      :options="{ title: 'Create New Workflow', size: 'xl' }"
      @close="showCreateModal = false"
    >
      <CreateWorkflowForm
        :templates="workflowStore.workflowTemplates"
        :trigger-types="workflowStore.triggerTypes"
        @create="handleCreateWorkflow"
        @cancel="showCreateModal = false"
      />
    </Dialog>

    <!-- Workflow Details Modal -->
    <Dialog
      v-if="showDetailsModal && selectedWorkflow"
      :options="{ title: selectedWorkflow.name, size: 'xl' }"
      @close="showDetailsModal = false"
    >
      <WorkflowDetails
        :workflow="selectedWorkflow"
        :executions="getWorkflowExecutions(selectedWorkflow.id)"
        @edit="handleEditFromDetails"
        @execute="handleExecuteWorkflow"
        @duplicate="handleDuplicateWorkflow"
        @delete="handleDeleteWorkflow"
      />
    </Dialog>

    <!-- Execution Details Modal -->
    <Dialog
      v-if="showExecutionModal && selectedExecution"
      :options="{ title: 'Execution Details', size: 'lg' }"
      @close="showExecutionModal = false"
    >
      <ExecutionDetails
        :execution="selectedExecution"
        :workflow="getWorkflowById(selectedExecution.workflow_id)"
      />
    </Dialog>

    <!-- Loading State -->
    <div v-if="workflowStore.isLoading" class="loading-overlay">
      <div class="loading-content">
        <Spinner class="w-8 h-8" />
        <p>Loading workflows...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="workflowStore.error" class="error-state">
      <div class="error-content">
        <AlertTriangle class="w-8 h-8 text-red-500" />
        <h4>Error Loading Workflows</h4>
        <p>{{ workflowStore.error }}</p>
        <Button @click="retryLoad" variant="solid">
          Retry
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Dialog, Dropdown } from "frappe-ui"
import {
	AlertTriangle,
	BarChart3,
	ChevronDown,
	List,
	Play,
	Plus,
	Spinner,
	Workflow,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

import { useWorkflowStore } from "../../stores/useWorkflowStore"

import CreateWorkflowForm from "./CreateWorkflowForm.vue"
import ExecutionDetails from "./ExecutionDetails.vue"
import WorkflowAnalytics from "./WorkflowAnalytics.vue"
import WorkflowDesigner from "./WorkflowDesigner.vue"
import WorkflowDetails from "./WorkflowDetails.vue"
import WorkflowInstances from "./WorkflowInstances.vue"
// Components (to be created)
import WorkflowList from "./WorkflowList.vue"

// Store
const workflowStore = useWorkflowStore()

// Local state
const showCreateModal = ref(false)
const showDetailsModal = ref(false)
const showExecutionModal = ref(false)
const selectedWorkflow = ref(null)
const selectedExecution = ref(null)

// View management
const currentView = computed(() => workflowStore.currentView)

const viewOptions = [
	{
		label: "List View",
		value: "list",
		icon: List,
	},
	{
		label: "Designer",
		value: "designer",
		icon: Workflow,
	},
	{
		label: "Instances",
		value: "instances",
		icon: Play,
	},
	{
		label: "Analytics",
		value: "analytics",
		icon: BarChart3,
	},
]

const currentViewIcon = computed(() => {
	const view = viewOptions.find((v) => v.value === currentView.value)
	return view ? view.icon : List
})

const currentViewLabel = computed(() => {
	const view = viewOptions.find((v) => v.value === currentView.value)
	return view ? view.label : "List View"
})

// Computed
const runningInstancesCount = computed(() => {
	return workflowStore.getRunningInstances.length
})

// Methods
const createNewWorkflow = () => {
	showCreateModal.value = true
}

const handleViewChange = (option) => {
	workflowStore.setCurrentView(option.value)
}

const handleWorkflowSelect = (workflow) => {
	selectedWorkflow.value = workflow
	showDetailsModal.value = true
}

const handleExecuteWorkflow = async (workflow) => {
	try {
		await workflowStore.executeWorkflow(workflow.id)
		// Optionally show success message or redirect to instances view
		workflowStore.setCurrentView("instances")
	} catch (error) {
		console.error("Failed to execute workflow:", error)
	}
}

const handleEditWorkflow = (workflow) => {
	workflowStore.setActiveWorkflow(workflow)
	workflowStore.setCurrentView("designer")
}

const handleDuplicateWorkflow = async (workflow) => {
	try {
		await workflowStore.duplicateWorkflow(workflow.id)
	} catch (error) {
		console.error("Failed to duplicate workflow:", error)
	}
}

const handleToggleStatus = async (workflow) => {
	try {
		await workflowStore.toggleWorkflowStatus(workflow.id)
	} catch (error) {
		console.error("Failed to toggle workflow status:", error)
	}
}

const handleDeleteWorkflow = async (workflow) => {
	if (confirm(`Are you sure you want to delete "${workflow.name}"?`)) {
		try {
			await workflowStore.deleteWorkflow(workflow.id)
		} catch (error) {
			console.error("Failed to delete workflow:", error)
		}
	}
}

const handleBulkAction = async (action, workflowIds) => {
	try {
		switch (action) {
			case "activate":
				await workflowStore.bulkUpdateWorkflows(workflowIds, {
					is_active: true,
				})
				break
			case "deactivate":
				await workflowStore.bulkUpdateWorkflows(workflowIds, {
					is_active: false,
				})
				break
			case "delete":
				if (
					confirm(
						`Are you sure you want to delete ${workflowIds.length} workflows?`,
					)
				) {
					for (const id of workflowIds) {
						await workflowStore.deleteWorkflow(id)
					}
				}
				break
		}
		workflowStore.clearSelection()
	} catch (error) {
		console.error("Bulk action failed:", error)
	}
}

const handleCreateWorkflow = async (workflowData) => {
	try {
		const workflow = await workflowStore.createWorkflow(workflowData)
		showCreateModal.value = false

		if (workflowData.openInDesigner) {
			workflowStore.setActiveWorkflow(workflow)
			workflowStore.setCurrentView("designer")
		}
	} catch (error) {
		console.error("Failed to create workflow:", error)
	}
}

const handleSaveWorkflow = async (workflowData) => {
	try {
		if (workflowStore.activeWorkflow?.id) {
			await workflowStore.updateWorkflow(
				workflowStore.activeWorkflow.id,
				workflowData,
			)
		} else {
			await workflowStore.createWorkflow(workflowData)
		}
		workflowStore.setCurrentView("list")
	} catch (error) {
		console.error("Failed to save workflow:", error)
	}
}

const handleCancelDesigner = () => {
	workflowStore.setActiveWorkflow(null)
	workflowStore.setCurrentView("list")
}

const handleEditFromDetails = () => {
	showDetailsModal.value = false
	workflowStore.setActiveWorkflow(selectedWorkflow.value)
	workflowStore.setCurrentView("designer")
}

const handleViewInstanceDetails = (execution) => {
	selectedExecution.value = execution
	showExecutionModal.value = true
}

const handleCancelInstance = async (instanceId) => {
	try {
		// Implementation would cancel running instance
		console.log("Cancel instance:", instanceId)
	} catch (error) {
		console.error("Failed to cancel instance:", error)
	}
}

const loadWorkflowInstances = async () => {
	await workflowStore.loadWorkflowInstances()
}

const getWorkflowExecutions = (workflowId) => {
	return workflowStore.executionHistory.filter(
		(execution) => execution.workflow_id === workflowId,
	)
}

const getWorkflowById = (workflowId) => {
	return workflowStore.getWorkflowById(workflowId)
}

const retryLoad = async () => {
	workflowStore.clearError()
	await workflowStore.loadWorkflows()
}

// Lifecycle
onMounted(async () => {
	await workflowStore.loadWorkflows()
	await workflowStore.loadWorkflowInstances()
})
</script>

<style scoped>
.workflow-automation-engine {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.header-content h2 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.header-content p {
  color: var(--text-muted);
  font-size: 1.125rem;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.stats-bar {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-weight: 500;
}

.workflow-content {
  min-height: 600px;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
}

.list-view,
.designer-view,
.instances-view,
.analytics-view {
  height: 100%;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.loading-content p {
  color: var(--text-muted);
  margin: 0;
}

.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.error-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  max-width: 400px;
}

.error-content h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.error-content p {
  color: var(--text-muted);
  margin: 0;
}

@media (max-width: 768px) {
  .workflow-automation-engine {
    padding: 1rem;
  }
  
  .workflow-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .stats-bar {
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: center;
  }
  
  .stat-item {
    flex: 1;
    min-width: 120px;
  }
  
  .workflow-content {
    min-height: 500px;
  }
}

@media (max-width: 480px) {
  .stats-bar {
    grid-template-columns: repeat(2, 1fr);
    display: grid;
    gap: 1rem;
  }
  
  .header-actions {
    flex-direction: column;
  }
}
</style>