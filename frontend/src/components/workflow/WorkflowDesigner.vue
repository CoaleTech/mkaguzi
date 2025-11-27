<template>
  <div class="workflow-designer">
    <!-- Designer Header -->
    <div class="designer-header">
      <div class="header-left">
        <Button variant="ghost" @click="$emit('cancel')">
          <ArrowLeft class="w-4 h-4" />
          Back
        </Button>
        
        <div class="workflow-info">
          <h3>{{ workflow ? 'Edit Workflow' : 'Create Workflow' }}</h3>
          <p v-if="workflow">{{ workflow.name }}</p>
        </div>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="handlePreview">
          <Eye class="w-4 h-4 mr-2" />
          Preview
        </Button>
        
        <Button variant="outline" @click="handleValidate">
          <CheckCircle class="w-4 h-4 mr-2" />
          Validate
        </Button>
        
        <Button variant="solid" @click="handleSave" :loading="isSaving">
          <Save class="w-4 h-4 mr-2" />
          {{ workflow ? 'Update' : 'Create' }}
        </Button>
      </div>
    </div>

    <!-- Designer Toolbar -->
    <div class="designer-toolbar">
      <div class="toolbar-section">
        <h5>Workflow Properties</h5>
        <div class="properties-grid">
          <FormControl
            type="text"
            label="Name"
            v-model="workflowData.name"
            placeholder="Enter workflow name..."
            :error="errors.name"
            required
          />
          
          <FormControl
            type="select"
            label="Category"
            v-model="workflowData.category"
            :options="categoryOptions"
            placeholder="Select category..."
          />
          
          <FormControl
            type="textarea"
            label="Description"
            v-model="workflowData.description"
            placeholder="Describe this workflow..."
            rows="2"
          />
          
          <div class="checkbox-field">
            <input
              type="checkbox"
              id="is-active"
              v-model="workflowData.is_active"
            />
            <label for="is-active">Active</label>
          </div>
        </div>
      </div>
      
      <div class="toolbar-section">
        <h5>Triggers</h5>
        <div class="trigger-list">
          <div
            v-for="trigger in triggers"
            :key="trigger.id"
            class="trigger-item"
            draggable="true"
            @dragstart="handleDragStart('trigger', trigger)"
          >
            <component :is="getTriggerIcon(trigger.icon)" class="w-4 h-4" />
            <span>{{ trigger.label }}</span>
          </div>
        </div>
      </div>
      
      <div class="toolbar-section">
        <h5>Actions</h5>
        <div class="action-categories">
          <div
            v-for="category in actionCategories"
            :key="category.id"
            class="category-section"
          >
            <h6>{{ category.label }}</h6>
            <div class="action-items">
              <div
                v-for="action in getActionsByCategory(category.id)"
                :key="action.id"
                class="action-item"
                draggable="true"
                @dragstart="handleDragStart('action', action)"
              >
                <component :is="getActionIcon(action.icon)" class="w-3 h-3" />
                <span>{{ action.label }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="toolbar-section">
        <h5>Conditions</h5>
        <div class="condition-list">
          <div
            v-for="condition in conditions"
            :key="condition.id"
            class="condition-item"
            draggable="true"
            @dragstart="handleDragStart('condition', condition)"
          >
            <Filter class="w-4 h-4" />
            <span>{{ condition.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Designer Canvas -->
    <div class="designer-canvas">
      <div class="canvas-container">
        <!-- Canvas Grid -->
        <div class="canvas-grid"></div>
        
        <!-- Workflow Steps -->
        <div
          class="canvas-content"
          @drop="handleDrop"
          @dragover="handleDragOver"
          @click="handleCanvasClick"
        >
          <!-- Start Node -->
          <div
            class="workflow-node start-node"
            :style="{ transform: 'translate(50px, 50px)' }"
          >
            <div class="node-icon">
              <Play class="w-5 h-5" />
            </div>
            <div class="node-content">
              <h5>Start</h5>
              <p>Workflow begins</p>
            </div>
            <div class="node-connector right"></div>
          </div>

          <!-- Dynamic Workflow Steps -->
          <div
            v-for="(step, index) in workflowData.steps"
            :key="step.id"
            class="workflow-node step-node"
            :class="{ 
              'selected': selectedStep?.id === step.id,
              'trigger-node': step.type === 'trigger',
              'action-node': step.type === 'action',
              'condition-node': step.type === 'condition'
            }"
            :style="{ transform: `translate(${step.x || (200 + index * 200)}px, ${step.y || 150}px)` }"
            @click.stop="selectStep(step)"
            @mousedown="startDrag(step, $event)"
          >
            <div class="node-icon">
              <component :is="getStepIcon(step)" class="w-5 h-5" />
            </div>
            <div class="node-content">
              <h5>{{ step.name || getStepTypeLabel(step.type) }}</h5>
              <p>{{ getStepDescription(step) }}</p>
            </div>
            <div class="node-connector left"></div>
            <div class="node-connector right"></div>
            
            <!-- Node Actions -->
            <div class="node-actions">
              <Button variant="ghost" size="sm" @click.stop="editStep(step)">
                <Settings class="w-3 h-3" />
              </Button>
              <Button variant="ghost" size="sm" @click.stop="deleteStep(step.id)">
                <X class="w-3 h-3" />
              </Button>
            </div>
          </div>

          <!-- End Node -->
          <div
            class="workflow-node end-node"
            :style="{ 
              transform: `translate(${200 + workflowData.steps.length * 200}px, 50px)` 
            }"
          >
            <div class="node-connector left"></div>
            <div class="node-icon">
              <Square class="w-5 h-5" />
            </div>
            <div class="node-content">
              <h5>End</h5>
              <p>Workflow completes</p>
            </div>
          </div>

          <!-- Connections -->
          <svg class="connections-layer" width="100%" height="100%">
            <!-- Start to first step -->
            <path
              v-if="workflowData.steps.length > 0"
              :d="getConnectionPath(
                { x: 150, y: 100 },
                { x: workflowData.steps[0].x || 200, y: (workflowData.steps[0].y || 150) + 50 }
              )"
              class="connection-line"
            />
            
            <!-- Step to step connections -->
            <path
              v-for="(step, index) in workflowData.steps.slice(0, -1)"
              :key="`connection-${index}`"
              :d="getConnectionPath(
                { 
                  x: (step.x || (200 + index * 200)) + 150, 
                  y: (step.y || 150) + 50 
                },
                { 
                  x: workflowData.steps[index + 1].x || (200 + (index + 1) * 200), 
                  y: (workflowData.steps[index + 1].y || 150) + 50 
                }
              )"
              class="connection-line"
            />
            
            <!-- Last step to end -->
            <path
              v-if="workflowData.steps.length > 0"
              :d="getConnectionPath(
                { 
                  x: (workflowData.steps[workflowData.steps.length - 1].x || (200 + (workflowData.steps.length - 1) * 200)) + 150, 
                  y: (workflowData.steps[workflowData.steps.length - 1].y || 150) + 50 
                },
                { 
                  x: 200 + workflowData.steps.length * 200, 
                  y: 100 
                }
              )"
              class="connection-line"
            />
          </svg>
        </div>
      </div>
      
      <!-- Canvas Controls -->
      <div class="canvas-controls">
        <Button variant="outline" size="sm" @click="zoomIn">
          <ZoomIn class="w-4 h-4" />
        </Button>
        <Button variant="outline" size="sm" @click="zoomOut">
          <ZoomOut class="w-4 h-4" />
        </Button>
        <Button variant="outline" size="sm" @click="resetZoom">
          <RotateCcw class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Step Configuration Panel -->
    <div v-if="selectedStep" class="step-config-panel">
      <div class="panel-header">
        <h4>Configure Step</h4>
        <Button variant="ghost" size="sm" @click="selectedStep = null">
          <X class="w-4 h-4" />
        </Button>
      </div>
      
      <div class="panel-content">
        <StepConfigForm
          :step="selectedStep"
          :step-type="selectedStep.type"
          @update="updateStepConfig"
          @close="selectedStep = null"
        />
      </div>
    </div>

    <!-- Validation Results Modal -->
    <Dialog
      v-if="showValidationModal"
      :options="{ title: 'Workflow Validation', size: 'md' }"
      @close="showValidationModal = false"
    >
      <div class="validation-results">
        <div v-if="validationResults.isValid" class="validation-success">
          <CheckCircle class="w-6 h-6 text-green-500" />
          <h4>Workflow is Valid</h4>
          <p>Your workflow configuration is correct and ready to run.</p>
        </div>
        
        <div v-else class="validation-errors">
          <AlertTriangle class="w-6 h-6 text-red-500" />
          <h4>Validation Issues Found</h4>
          <ul>
            <li v-for="error in validationResults.errors" :key="error">
              {{ error }}
            </li>
          </ul>
        </div>
        
        <div v-if="validationResults.warnings?.length" class="validation-warnings">
          <AlertCircle class="w-6 h-6 text-yellow-500" />
          <h4>Warnings</h4>
          <ul>
            <li v-for="warning in validationResults.warnings" :key="warning">
              {{ warning }}
            </li>
          </ul>
        </div>
      </div>
    </Dialog>

    <!-- Preview Modal -->
    <Dialog
      v-if="showPreviewModal"
      :options="{ title: 'Workflow Preview', size: 'xl' }"
      @close="showPreviewModal = false"
    >
      <WorkflowPreview
        :workflow="workflowData"
        @execute="handleTestExecution"
      />
    </Dialog>
  </div>
</template>

<script setup>
import { Button, Dialog, FormControl } from "frappe-ui"
import {
	AlertCircle,
	AlertTriangle,
	ArrowLeft,
	Bell,
	CheckCircle,
	CheckSquare,
	Clock,
	Code,
	Edit,
	Eye,
	FileText,
	Filter,
	Link,
	Mail,
	Play,
	Plus,
	RotateCcw,
	Save,
	Settings,
	Square,
	X,
	Zap,
	ZoomIn,
	ZoomOut,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"

// Components
import StepConfigForm from "./StepConfigForm.vue"
import WorkflowPreview from "./WorkflowPreview.vue"

const props = defineProps({
	workflow: {
		type: Object,
		default: null,
	},
	triggers: {
		type: Array,
		default: () => [],
	},
	conditions: {
		type: Array,
		default: () => [],
	},
	actions: {
		type: Array,
		default: () => [],
	},
})

const emit = defineEmits(["save", "cancel", "node-select"])

// Local state
const workflowData = ref({
	name: "",
	description: "",
	category: "",
	is_active: true,
	steps: [],
	...props.workflow,
})

const selectedStep = ref(null)
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const canvasScale = ref(1)
const canvasOffset = ref({ x: 0, y: 0 })
const isSaving = ref(false)
const errors = ref({})

// Modals
const showValidationModal = ref(false)
const showPreviewModal = ref(false)
const validationResults = ref({ isValid: true, errors: [], warnings: [] })

// Options
const categoryOptions = [
	{ label: "Compliance", value: "compliance" },
	{ label: "Risk Management", value: "risk_management" },
	{ label: "Reporting", value: "reporting" },
	{ label: "Data Processing", value: "data_processing" },
	{ label: "Notifications", value: "notifications" },
]

const actionCategories = [
	{ id: "data", label: "Data Operations" },
	{ id: "notification", label: "Notifications" },
	{ id: "workflow", label: "Workflow" },
	{ id: "reporting", label: "Reporting" },
	{ id: "integration", label: "Integration" },
	{ id: "custom", label: "Custom" },
]

// Methods
const getTriggerIcon = (iconName) => {
	const icons = {
		clock: Clock,
		zap: Zap,
		play: Play,
		filter: Filter,
	}
	return icons[iconName] || Play
}

const getActionIcon = (iconName) => {
	const icons = {
		plus: Plus,
		edit: Edit,
		trash: X,
		mail: Mail,
		bell: Bell,
		"check-square": CheckSquare,
		"file-text": FileText,
		link: Link,
		code: Code,
	}
	return icons[iconName] || Plus
}

const getActionsByCategory = (category) => {
	return props.actions.filter((action) => action.category === category)
}

const getStepIcon = (step) => {
	if (step.type === "trigger") {
		const trigger = props.triggers.find((t) => t.id === step.trigger_type)
		return getTriggerIcon(trigger?.icon)
	} else if (step.type === "action") {
		const action = props.actions.find((a) => a.id === step.action_type)
		return getActionIcon(action?.icon)
	}
	return Filter
}

const getStepTypeLabel = (type) => {
	const labels = {
		trigger: "Trigger",
		condition: "Condition",
		action: "Action",
	}
	return labels[type] || "Step"
}

const getStepDescription = (step) => {
	if (step.description) return step.description

	if (step.type === "trigger") {
		const trigger = props.triggers.find((t) => t.id === step.trigger_type)
		return trigger?.description || "Workflow trigger"
	} else if (step.type === "action") {
		const action = props.actions.find((a) => a.id === step.action_type)
		return action?.description || "Workflow action"
	} else if (step.type === "condition") {
		const condition = props.conditions.find((c) => c.id === step.condition_type)
		return condition?.description || "Workflow condition"
	}

	return "Workflow step"
}

const handleDragStart = (type, item) => {
	const dragData = { type, item }
	// Store drag data for drop handling
	window.workflowDragData = dragData
}

const handleDragOver = (event) => {
	event.preventDefault()
}

const handleDrop = (event) => {
	event.preventDefault()

	if (!window.workflowDragData) return

	const { type, item } = window.workflowDragData
	const rect = event.currentTarget.getBoundingClientRect()
	const x =
		(event.clientX - rect.left - canvasOffset.value.x) / canvasScale.value
	const y =
		(event.clientY - rect.top - canvasOffset.value.y) / canvasScale.value

	const newStep = {
		id: `step-${Date.now()}`,
		type: type,
		name: `${item.label} ${workflowData.value.steps.length + 1}`,
		x: x - 75, // Center on drop point
		y: y - 50,
		config: {},
	}

	if (type === "trigger") {
		newStep.trigger_type = item.id
	} else if (type === "action") {
		newStep.action_type = item.id
	} else if (type === "condition") {
		newStep.condition_type = item.id
	}

	workflowData.value.steps.push(newStep)
	selectStep(newStep)

	delete window.workflowDragData
}

const handleCanvasClick = () => {
	selectedStep.value = null
}

const selectStep = (step) => {
	selectedStep.value = step
	emit("node-select", step)
}

const startDrag = (step, event) => {
	if (event.target.closest(".node-actions")) return

	isDragging.value = true
	const rect = event.currentTarget.getBoundingClientRect()
	dragOffset.value = {
		x: event.clientX - rect.left,
		y: event.clientY - rect.top,
	}

	const handleMouseMove = (e) => {
		if (!isDragging.value) return

		const canvas = document.querySelector(".canvas-content")
		const canvasRect = canvas.getBoundingClientRect()

		step.x =
			(e.clientX -
				canvasRect.left -
				dragOffset.value.x -
				canvasOffset.value.x) /
			canvasScale.value
		step.y =
			(e.clientY - canvasRect.top - dragOffset.value.y - canvasOffset.value.y) /
			canvasScale.value
	}

	const handleMouseUp = () => {
		isDragging.value = false
		document.removeEventListener("mousemove", handleMouseMove)
		document.removeEventListener("mouseup", handleMouseUp)
	}

	document.addEventListener("mousemove", handleMouseMove)
	document.addEventListener("mouseup", handleMouseUp)
}

const editStep = (step) => {
	selectStep(step)
}

const deleteStep = (stepId) => {
	const index = workflowData.value.steps.findIndex((s) => s.id === stepId)
	if (index > -1) {
		workflowData.value.steps.splice(index, 1)
		if (selectedStep.value?.id === stepId) {
			selectedStep.value = null
		}
	}
}

const updateStepConfig = (stepId, config) => {
	const step = workflowData.value.steps.find((s) => s.id === stepId)
	if (step) {
		Object.assign(step, config)
	}
}

const getConnectionPath = (start, end) => {
	const midX = (start.x + end.x) / 2
	return `M ${start.x} ${start.y} C ${midX} ${start.y}, ${midX} ${end.y}, ${end.x} ${end.y}`
}

const zoomIn = () => {
	canvasScale.value = Math.min(canvasScale.value * 1.2, 3)
}

const zoomOut = () => {
	canvasScale.value = Math.max(canvasScale.value * 0.8, 0.3)
}

const resetZoom = () => {
	canvasScale.value = 1
	canvasOffset.value = { x: 0, y: 0 }
}

const handleValidate = () => {
	const results = validateWorkflow()
	validationResults.value = results
	showValidationModal.value = true
}

const validateWorkflow = () => {
	const errors = []
	const warnings = []

	if (!workflowData.value.name?.trim()) {
		errors.push("Workflow name is required")
	}

	if (workflowData.value.steps.length === 0) {
		errors.push("Workflow must have at least one step")
	}

	// Check for triggers
	const triggerSteps = workflowData.value.steps.filter(
		(s) => s.type === "trigger",
	)
	if (triggerSteps.length === 0) {
		warnings.push("Workflow has no triggers and can only be run manually")
	}

	// Validate each step
	workflowData.value.steps.forEach((step, index) => {
		if (!step.name?.trim()) {
			errors.push(`Step ${index + 1} is missing a name`)
		}

		if (step.type === "condition" && !step.config?.condition) {
			errors.push(`Condition step "${step.name}" is not configured`)
		}

		if (step.type === "action" && !step.action_type) {
			errors.push(`Action step "${step.name}" has no action type selected`)
		}
	})

	return {
		isValid: errors.length === 0,
		errors,
		warnings,
	}
}

const handlePreview = () => {
	showPreviewModal.value = true
}

const handleTestExecution = () => {
	// Test execution logic
	console.log("Test execution:", workflowData.value)
}

const handleSave = async () => {
	// Validate form
	const newErrors = {}

	if (!workflowData.value.name?.trim()) {
		newErrors.name = "Workflow name is required"
	}

	errors.value = newErrors

	if (Object.keys(newErrors).length > 0) {
		return
	}

	isSaving.value = true

	try {
		await emit("save", workflowData.value)
	} catch (error) {
		console.error("Failed to save workflow:", error)
	} finally {
		isSaving.value = false
	}
}

// Watchers
watch(
	() => props.workflow,
	(newWorkflow) => {
		if (newWorkflow) {
			workflowData.value = { ...newWorkflow }
		}
	},
	{ immediate: true },
)
</script>

<style scoped>
.workflow-designer {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--background-color);
}

.designer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: white;
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.workflow-info h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-color);
}

.workflow-info p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.designer-toolbar {
  width: 300px;
  background: white;
  border-right: 1px solid var(--border-color);
  padding: 1.5rem;
  overflow-y: auto;
  flex-shrink: 0;
}

.toolbar-section {
  margin-bottom: 2rem;
}

.toolbar-section h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.properties-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.checkbox-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-field label {
  font-weight: 500;
  color: var(--text-color);
}

.trigger-list,
.condition-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.trigger-item,
.condition-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  cursor: grab;
  transition: all 0.2s;
}

.trigger-item:hover,
.condition-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.trigger-item:active,
.condition-item:active {
  cursor: grabbing;
}

.trigger-item span,
.condition-item span {
  font-size: 0.875rem;
  font-weight: 500;
}

.action-categories {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.category-section h6 {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
}

.action-items {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.25rem;
  cursor: grab;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.action-item:hover {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.action-item:active {
  cursor: grabbing;
}

.designer-canvas {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.canvas-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: #fafafa;
}

.canvas-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(to right, #e5e7eb 1px, transparent 1px),
    linear-gradient(to bottom, #e5e7eb 1px, transparent 1px);
  background-size: 20px 20px;
  opacity: 0.5;
}

.canvas-content {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: auto;
  min-height: 800px;
  min-width: 1200px;
}

.workflow-node {
  position: absolute;
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
  width: 150px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.workflow-node:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.workflow-node.selected {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-light);
}

.start-node {
  border-color: #22c55e;
  background: #f0fdf4;
}

.end-node {
  border-color: #ef4444;
  background: #fef2f2;
}

.trigger-node {
  border-color: #3b82f6;
  background: #eff6ff;
}

.action-node {
  border-color: #f59e0b;
  background: #fffbeb;
}

.condition-node {
  border-color: #8b5cf6;
  background: #faf5ff;
}

.node-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  margin: 0 auto 0.5rem auto;
}

.node-content h5 {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  text-align: center;
  color: var(--text-color);
}

.node-content p {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0;
  text-align: center;
  line-height: 1.3;
}

.node-connector {
  position: absolute;
  width: 12px;
  height: 12px;
  background: var(--primary-color);
  border: 2px solid white;
  border-radius: 50%;
  top: 50%;
  transform: translateY(-50%);
}

.node-connector.left {
  left: -6px;
}

.node-connector.right {
  right: -6px;
}

.node-actions {
  position: absolute;
  top: -8px;
  right: -8px;
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.workflow-node:hover .node-actions {
  opacity: 1;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.connection-line {
  fill: none;
  stroke: var(--border-color);
  stroke-width: 2;
  marker-end: url(#arrowhead);
}

.canvas-controls {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  display: flex;
  gap: 0.5rem;
}

.step-config-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100vh;
  background: white;
  border-left: 1px solid var(--border-color);
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.panel-header h4 {
  font-weight: 600;
  margin: 0;
  color: var(--text-color);
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.validation-results {
  padding: 1rem;
}

.validation-success,
.validation-errors,
.validation-warnings {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
  margin-bottom: 1.5rem;
}

.validation-success h4 {
  color: #166534;
  margin: 0;
}

.validation-errors h4 {
  color: #991b1b;
  margin: 0;
}

.validation-warnings h4 {
  color: #92400e;
  margin: 0;
}

.validation-errors ul,
.validation-warnings ul {
  text-align: left;
  margin: 0;
  padding-left: 1.5rem;
}

.validation-errors li,
.validation-warnings li {
  margin-bottom: 0.5rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .workflow-designer {
    flex-direction: column;
  }
  
  .designer-toolbar {
    width: 100%;
    max-height: 200px;
    order: 2;
  }
  
  .designer-canvas {
    order: 1;
    flex: none;
    height: 400px;
  }
  
  .step-config-panel {
    width: 100%;
    height: 50vh;
    top: 50vh;
    right: 0;
  }
}

@media (max-width: 768px) {
  .designer-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .toolbar-section {
    margin-bottom: 1rem;
  }
  
  .workflow-node {
    width: 120px;
    padding: 0.75rem;
  }
  
  .node-content h5 {
    font-size: 0.75rem;
  }
  
  .node-content p {
    font-size: 0.625rem;
  }
}
</style>