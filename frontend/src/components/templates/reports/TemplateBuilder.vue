<template>
  <div class="report-template-builder">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Report Template Builder</h1>
        <p class="text-gray-600 mt-1">Create and customize report templates with drag-and-drop components</p>
      </div>
      <div class="flex items-center space-x-3">
        <Button @click="previewReport" variant="outline">
          <Eye class="w-4 h-4 mr-2" />
          Preview
        </Button>
        <Button @click="saveTemplate" :loading="saving" variant="solid">
          <Save class="w-4 h-4 mr-2" />
          Save Template
        </Button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Left Sidebar -->
      <div class="lg:col-span-1">
        <!-- Tab Navigation -->
        <div class="bg-white rounded-lg border border-gray-200 mb-4">
          <div class="border-b border-gray-200">
            <nav class="flex">
              <button
                @click="activeTab = 'components'"
                :class="['flex-1 py-2 px-4 text-center text-sm font-medium', activeTab === 'components' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700']"
              >
                Components
              </button>
              <button
                @click="activeTab = 'variables'"
                :class="['flex-1 py-2 px-4 text-center text-sm font-medium', activeTab === 'variables' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700']"
              >
                Variables
              </button>
            </nav>
          </div>

          <!-- Components Tab -->
          <div v-if="activeTab === 'components'" class="p-4">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Components</h3>

            <!-- Component Categories -->
            <div class="space-y-4">
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">Layout</h4>
                <div class="space-y-2">
                  <div
                    v-for="component in layoutComponents"
                    :key="component.type"
                    class="component-item"
                    draggable="true"
                    @dragstart="onDragStart($event, component)"
                  >
                    <component :is="component.icon" class="w-4 h-4 mr-2" />
                    {{ component.label }}
                  </div>
                </div>
              </div>

              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">Content</h4>
                <div class="space-y-2">
                  <div
                    v-for="component in contentComponents"
                    :key="component.type"
                    class="component-item"
                    draggable="true"
                    @dragstart="onDragStart($event, component)"
                  >
                    <component :is="component.icon" class="w-4 h-4 mr-2" />
                    {{ component.label }}
                  </div>
                </div>
              </div>

              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">Data</h4>
                <div class="space-y-2">
                  <div
                    v-for="component in dataComponents"
                    :key="component.type"
                    class="component-item"
                    draggable="true"
                    @dragstart="onDragStart($event, component)"
                  >
                    <component :is="component.icon" class="w-4 h-4 mr-2" />
                    {{ component.label }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Variables Tab -->
          <div v-if="activeTab === 'variables'" class="p-4">
            <TemplateVariables
              :template-id="currentTemplateId"
              :category="templateSettings.category"
              @variables-updated="onVariablesUpdated"
            />
          </div>
        </div>

        <!-- Template Settings -->
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Settings</h3>

          <div class="space-y-4">
            <FormControl
              label="Template Name"
              v-model="templateSettings.name"
              type="text"
              placeholder="Report Template Name"
            />

            <FormControl
              label="Category"
              v-model="templateSettings.category"
              type="select"
              :options="categoryOptions"
            />

            <FormControl
              label="Page Size"
              v-model="templateSettings.pageSize"
              type="select"
              :options="pageSizeOptions"
            />

            <FormControl
              label="Orientation"
              v-model="templateSettings.orientation"
              type="select"
              :options="orientationOptions"
            />

            <div class="flex items-center">
              <input
                id="showHeader"
                v-model="templateSettings.showHeader"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="showHeader" class="ml-2 block text-sm text-gray-900">
                Show Header
              </label>
            </div>

            <div class="flex items-center">
              <input
                id="showFooter"
                v-model="templateSettings.showFooter"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="showFooter" class="ml-2 block text-sm text-gray-900">
                Show Footer
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Canvas -->
      <div class="lg:col-span-3">
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <!-- Canvas Header -->
          <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <span class="text-sm font-medium text-gray-700">Report Canvas</span>
            <div class="flex items-center space-x-2">
              <Button @click="undo" :disabled="!canUndo" variant="ghost" size="sm">
                <Undo class="w-4 h-4" />
              </Button>
              <Button @click="redo" :disabled="!canRedo" variant="ghost" size="sm">
                <Redo class="w-4 h-4" />
              </Button>
              <Button @click="clearCanvas" variant="ghost" size="sm" class="text-red-600">
                <Trash2 class="w-4 h-4" />
              </Button>
            </div>
          </div>

          <!-- Canvas Area -->
          <div
            class="canvas-area min-h-96 p-4"
            :class="canvasClass"
            @drop="onDrop"
            @dragover.prevent
          >
            <!-- Header Section -->
            <div
              v-if="templateSettings.showHeader"
              class="report-header mb-4 p-4 border-b-2 border-gray-300"
            >
              <div class="text-center">
                <h1 class="text-2xl font-bold text-gray-900">{{ templateSettings.name || 'Report Title' }}</h1>
                <p class="text-gray-600 mt-2">Generated on {{ new Date().toLocaleDateString() }}</p>
              </div>
            </div>

            <!-- Droppable Components Area -->
            <div class="report-body space-y-4">
              <div
                v-for="(component, index) in canvasComponents"
                :key="component.id"
                class="component-wrapper relative group"
                :class="{ 'selected': selectedComponent === component.id }"
                @click="selectComponent(component.id)"
              >
                <!-- Component Toolbar -->
                <div class="component-toolbar absolute -top-8 left-0 bg-white border border-gray-200 rounded px-2 py-1 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity z-10">
                  <div class="flex items-center space-x-1">
                    <Button @click.stop="moveComponent(index, -1)" :disabled="index === 0" variant="ghost" size="sm" class="p-1">
                      <ChevronUp class="w-3 h-3" />
                    </Button>
                    <Button @click.stop="moveComponent(index, 1)" :disabled="index === canvasComponents.length - 1" variant="ghost" size="sm" class="p-1">
                      <ChevronDown class="w-3 h-3" />
                    </Button>
                    <Button @click.stop="duplicateComponent(component)" variant="ghost" size="sm" class="p-1">
                      <Copy class="w-3 h-3" />
                    </Button>
                    <Button @click.stop="deleteComponent(index)" variant="ghost" size="sm" class="p-1 text-red-600">
                      <Trash2 class="w-3 h-3" />
                    </Button>
                  </div>
                </div>

                <!-- Render Component -->
                <component
                  :is="getComponentRenderer(component.type)"
                  :component="component"
                  :is-selected="selectedComponent === component.id"
                  @update="updateComponent(component.id, $event)"
                />
              </div>

              <!-- Drop Zone -->
              <div
                v-if="canvasComponents.length === 0"
                class="drop-zone border-2 border-dashed border-gray-300 rounded-lg p-8 text-center text-gray-500"
              >
                <FileText class="w-12 h-12 mx-auto mb-4" />
                <p>Drag components here to build your report</p>
              </div>
            </div>

            <!-- Footer Section -->
            <div
              v-if="templateSettings.showFooter"
              class="report-footer mt-8 pt-4 border-t-2 border-gray-300"
            >
              <div class="text-center text-sm text-gray-600">
                <p>Confidential - Internal Use Only</p>
                <p>Page 1 of 1</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Component Properties Panel -->
        <div v-if="selectedComponent" class="bg-white rounded-lg border border-gray-200 p-4 mt-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Component Properties</h3>

          <ComponentProperties
            :component="getSelectedComponent()"
            :available-variables="availableVariables"
            @update="updateSelectedComponent"
          />
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <Dialog
      v-model="showPreview"
      :options="{
        title: 'Report Preview',
        size: '6xl'
      }"
    >
      <template #body-content>
        <ReportPreview
          v-if="showPreview"
          :template="builtTemplate"
          :settings="templateSettings"
          @close="showPreview = false"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import {
	BarChart3,
	ChevronDown,
	ChevronUp,
	Copy,
	Eye,
	FileText,
	Image,
	Layout,
	PieChart,
	Redo,
	Save,
	Table,
	Trash2,
	Type,
	Undo,
} from "lucide-vue-next"
import { computed, reactive, ref } from "vue"

import ComponentProperties from "./reports/ComponentProperties.vue"
import ReportPreview from "./reports/ReportPreview.vue"
import TemplateVariables from "./reports/TemplateVariables.vue"

// Props
const props = defineProps({
	initialTemplate: {
		type: Object,
		default: () => ({}),
	},
})

// Emits
const emit = defineEmits(["save", "cancel"])

// Reactive data
const canvasComponents = ref([])
const selectedComponent = ref(null)
const showPreview = ref(false)
const saving = ref(false)
const activeTab = ref("components")
const availableVariables = ref([])

const templateSettings = reactive({
	name: "",
	category: "Audit Report",
	pageSize: "A4",
	orientation: "portrait",
	showHeader: true,
	showFooter: true,
})

// Component definitions
const layoutComponents = [
	{ type: "section", label: "Section", icon: Layout },
	{ type: "divider", label: "Divider", icon: "div" },
	{ type: "spacer", label: "Spacer", icon: "div" },
]

const contentComponents = [
	{ type: "heading", label: "Heading", icon: Type },
	{ type: "paragraph", label: "Paragraph", icon: Type },
	{ type: "list", label: "List", icon: "ul" },
]

const dataComponents = [
	{ type: "table", label: "Table", icon: Table },
	{ type: "chart", label: "Chart", icon: BarChart3 },
	{ type: "metric", label: "Metric", icon: "div" },
]

// Options
const categoryOptions = [
	{ label: "Audit Report", value: "Audit Report" },
	{ label: "Compliance Report", value: "Compliance Report" },
	{ label: "Financial Report", value: "Financial Report" },
	{ label: "Risk Assessment", value: "Risk Assessment" },
	{ label: "Custom Report", value: "Custom Report" },
]

const pageSizeOptions = [
	{ label: "A4", value: "A4" },
	{ label: "A3", value: "A3" },
	{ label: "Letter", value: "Letter" },
	{ label: "Legal", value: "Legal" },
]

const orientationOptions = [
	{ label: "Portrait", value: "portrait" },
	{ label: "Landscape", value: "landscape" },
]

// Computed
const canvasClass = computed(() => {
	return {
		"canvas-portrait": templateSettings.orientation === "portrait",
		"canvas-landscape": templateSettings.orientation === "landscape",
	}
})

const canUndo = computed(() => false) // TODO: Implement undo/redo
const canRedo = computed(() => false) // TODO: Implement undo/redo

const builtTemplate = computed(() => ({
	components: canvasComponents.value,
	settings: templateSettings,
}))

const currentTemplateId = computed(() => {
	return props.initialTemplate?.name || null
})

// Methods
const onDragStart = (event, component) => {
	event.dataTransfer.setData("application/json", JSON.stringify(component))
}

const onDrop = (event) => {
	event.preventDefault()
	try {
		const componentData = JSON.parse(
			event.dataTransfer.getData("application/json"),
		)
		addComponent(componentData)
	} catch (error) {
		console.error("Error dropping component:", error)
	}
}

const addComponent = (componentData) => {
	const newComponent = {
		id: generateId(),
		type: componentData.type,
		label: componentData.label,
		properties: getDefaultProperties(componentData.type),
	}

	canvasComponents.value.push(newComponent)
	selectedComponent.value = newComponent.id
}

const selectComponent = (componentId) => {
	selectedComponent.value = componentId
}

const updateComponent = (componentId, updates) => {
	const component = canvasComponents.value.find((c) => c.id === componentId)
	if (component) {
		Object.assign(component, updates)
	}
}

const updateSelectedComponent = (updates) => {
	if (selectedComponent.value) {
		updateComponent(selectedComponent.value, updates)
	}
}

const getSelectedComponent = () => {
	return canvasComponents.value.find((c) => c.id === selectedComponent.value)
}

const deleteComponent = (index) => {
	if (selectedComponent.value === canvasComponents.value[index].id) {
		selectedComponent.value = null
	}
	canvasComponents.value.splice(index, 1)
}

const duplicateComponent = (component) => {
	const duplicated = {
		...component,
		id: generateId(),
		label: `${component.label} (Copy)`,
	}
	canvasComponents.value.push(duplicated)
	selectedComponent.value = duplicated.id
}

const moveComponent = (index, direction) => {
	const newIndex = index + direction
	if (newIndex >= 0 && newIndex < canvasComponents.value.length) {
		const component = canvasComponents.value.splice(index, 1)[0]
		canvasComponents.value.splice(newIndex, 0, component)
	}
}

const clearCanvas = () => {
	if (confirm("Are you sure you want to clear the entire canvas?")) {
		canvasComponents.value = []
		selectedComponent.value = null
	}
}

const getComponentRenderer = (type) => {
	// This would return the appropriate Vue component for rendering
	// For now, return a placeholder
	return "div"
}

const getDefaultProperties = (type) => {
	const defaults = {
		heading: { level: 1, text: "Heading Text" },
		paragraph: { text: "Paragraph text content" },
		table: { columns: ["Column 1", "Column 2"], data: [] },
		chart: { type: "bar", data: [] },
		section: { title: "Section Title" },
		divider: {},
		spacer: { height: 20 },
	}
	return defaults[type] || {}
}

const generateId = () => {
	return `component_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

const previewReport = () => {
	showPreview.value = true
}

const saveTemplate = async () => {
	saving.value = true
	try {
		// Convert canvas to template format
		const templateContent = generateTemplateContent()

		const templateData = {
			template_name: templateSettings.name,
			template_type: "Report",
			category: templateSettings.category,
			template_content: templateContent,
			template_config: JSON.stringify({
				builder: {
					components: canvasComponents.value,
					settings: templateSettings,
				},
			}),
			template_engine: "Jinja2",
		}

		emit("save", templateData)
	} catch (error) {
		console.error("Error saving template:", error)
	} finally {
		saving.value = false
	}
}

const fetchAvailableVariables = async () => {
	if (!currentTemplateId.value) return

	try {
		const response = await fetch(
			`/api/method/mkaguzi.api.templates.get_template_variables`,
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					template_name: currentTemplateId.value,
				}),
			},
		)

		if (response.ok) {
			const data = await response.json()
			availableVariables.value = data.message || []
		} else {
			console.error("Failed to fetch variables")
			availableVariables.value = []
		}
	} catch (error) {
		console.error("Error fetching variables:", error)
		availableVariables.value = []
	}
}

const generateTemplateContent = () => {
	// Convert canvas components to Jinja2 template with variable support
	let content = ""

	canvasComponents.value.forEach((component) => {
		switch (component.type) {
			case "heading":
				const headingText = component.properties.useVariable
					? `{{ ${component.properties.useVariable} }}`
					: component.properties.text || "{{ heading_text }}"
				content += `# ${headingText}\n\n`
				break
			case "paragraph":
				const paragraphText = component.properties.useVariable
					? `{{ ${component.properties.useVariable} }}`
					: component.properties.text || "{{ paragraph_content }}"
				content += `${paragraphText}\n\n`
				break
			case "table":
				content +=
					"| " +
					(component.properties.columns || ["Column 1", "Column 2"]).join(
						" | ",
					) +
					" |\n"
				content +=
					"|" +
					(component.properties.columns || ["Column 1", "Column 2"])
						.map(() => "---")
						.join("|") +
					"|\n"
				content += "{% for row in table_data %}\n"
				content +=
					"| " +
					(component.properties.columns || ["Column 1", "Column 2"])
						.map((col) => `{{ row.${col.toLowerCase().replace(" ", "_")} }}`)
						.join(" | ") +
					" |\n"
				content += "{% endfor %}\n\n"
				break
			case "metric":
				const metricValue = component.properties.useVariable
					? `{{ ${component.properties.useVariable} }}`
					: component.properties.value || "{{ metric_value }}"
				content += `**${component.properties.label || "Metric"}:** ${metricValue}\n\n`
				break
			case "section":
				content += `## ${component.properties.title || "{{ section_title }}"}\n\n`
				break
			default:
				content += `<!-- ${component.type} component -->\n\n`
		}
	})

	return content
}

// Initialize from existing template if provided
if (props.initialTemplate) {
	// Load existing template data
	templateSettings.name = props.initialTemplate.template_name || ""
	templateSettings.category = props.initialTemplate.category || "Audit Report"

	if (props.initialTemplate.template_config) {
		try {
			const config = JSON.parse(props.initialTemplate.template_config)
			if (config.builder) {
				canvasComponents.value = config.builder.components || []
				Object.assign(templateSettings, config.builder.settings || {})
			}
		} catch (error) {
			console.error("Error loading template config:", error)
		}
	}

	// Fetch available variables for the template
	fetchAvailableVariables()
}
</script>

<style scoped>
.component-item {
  @apply flex items-center p-2 border border-gray-200 rounded cursor-move hover:bg-gray-50 transition-colors;
}

.canvas-area {
  background: white;
  min-height: 600px;
}

.canvas-portrait {
  max-width: 595px; /* A4 width in pixels at 72 DPI */
  margin: 0 auto;
}

.canvas-landscape {
  max-width: 842px; /* A4 height in pixels at 72 DPI */
  margin: 0 auto;
}

.component-wrapper {
  @apply border border-transparent hover:border-blue-300 rounded transition-colors;
}

.component-wrapper.selected {
  @apply border-blue-500 bg-blue-50;
}

.drop-zone {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.component-toolbar {
  white-space: nowrap;
}

.report-header,
.report-footer {
  background: white;
}
</style>