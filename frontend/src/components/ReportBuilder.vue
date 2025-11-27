<template>
  <div class="report-builder">
    <!-- Header -->
    <div class="builder-header">
      <div class="header-content">
        <h2 class="builder-title">
          <FileTextIcon class="title-icon" />
          Report Builder
        </h2>
        <p class="builder-description">
          Create custom reports with drag-and-drop sections, charts, and data tables
        </p>
      </div>
      <div class="header-actions">
        <Button variant="outline" @click="showTemplateModal = true">
          <LayoutTemplateIcon class="h-4 w-4 mr-2" />
          Use Template
        </Button>
        <Button variant="outline" @click="previewReport" :disabled="!reportData.title">
          <EyeIcon class="h-4 w-4 mr-2" />
          Preview
        </Button>
        <Button @click="saveReport" :disabled="!reportData.title || saving">
          <SaveIcon v-if="!saving" class="h-4 w-4 mr-2" />
          <Loader2Icon v-else class="h-4 w-4 mr-2 spinning" />
          {{ saving ? 'Saving...' : 'Save Report' }}
        </Button>
      </div>
    </div>

    <!-- Report Configuration -->
    <div class="report-config">
      <div class="config-section">
        <h3 class="config-title">Report Configuration</h3>
        
        <div class="config-grid">
          <div class="config-group">
            <label class="config-label">Report Title *</label>
            <Input
              v-model="reportData.title"
              placeholder="Enter report title"
              required
              class="config-input"
            />
          </div>

          <div class="config-group">
            <label class="config-label">Report Type *</label>
            <Select
              v-model="reportData.report_type"
              :options="reportStore.reportTypes"
              placeholder="Select report type"
              required
              class="config-select"
            />
          </div>

          <div class="config-group">
            <label class="config-label">Status</label>
            <Select
              v-model="reportData.status"
              :options="statusOptions"
              placeholder="Select status"
              class="config-select"
            />
          </div>

          <div class="config-group">
            <label class="config-label">Tags</label>
            <Input
              v-model="reportData.tags"
              placeholder="Enter tags separated by commas"
              class="config-input"
            />
          </div>
        </div>

        <div class="config-group full-width">
          <label class="config-label">Description</label>
          <textarea
            v-model="reportData.description"
            placeholder="Enter report description"
            class="config-textarea"
            rows="3"
          ></textarea>
        </div>
      </div>
    </div>

    <!-- Main Builder Area -->
    <div class="builder-main">
      <!-- Section Library -->
      <div class="section-library">
        <h3 class="library-title">Section Library</h3>
        <p class="library-description">Drag sections to build your report</p>
        
        <div class="section-items">
          <div
            v-for="sectionType in reportStore.sectionTypes"
            :key="sectionType.value"
            class="section-item"
            draggable="true"
            @dragstart="startDrag($event, sectionType)"
          >
            <component :is="sectionType.icon + 'Icon'" class="section-icon" />
            <span class="section-label">{{ sectionType.label }}</span>
          </div>
        </div>

        <!-- Chart Types -->
        <div class="subsection">
          <h4 class="subsection-title">Chart Types</h4>
          <div class="chart-items">
            <div
              v-for="chartType in reportStore.chartTypes"
              :key="chartType.value"
              class="chart-item"
              draggable="true"
              @dragstart="startChartDrag($event, chartType)"
            >
              <component :is="chartType.icon + 'Icon'" class="chart-icon" />
              <span class="chart-label">{{ chartType.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Report Canvas -->
      <div class="report-canvas">
        <div class="canvas-header">
          <h3 class="canvas-title">Report Sections</h3>
          <div class="canvas-actions">
            <Button variant="ghost" size="sm" @click="clearAll" v-if="reportData.sections.length > 0">
              <TrashIcon class="h-4 w-4 mr-1" />
              Clear All
            </Button>
          </div>
        </div>

        <div
          class="canvas-area"
          @drop="handleDrop"
          @dragover.prevent
          @dragenter.prevent
        >
          <!-- Drop Zone when empty -->
          <div v-if="reportData.sections.length === 0" class="empty-canvas">
            <FileTextIcon class="empty-icon" />
            <h4>Start Building Your Report</h4>
            <p>Drag sections from the library to create your custom report</p>
          </div>

          <!-- Report Sections -->
          <div v-else class="report-sections">
            <div
              v-for="(section, index) in reportData.sections"
              :key="section.id"
              class="report-section"
              :class="{ 'selected': selectedSection === index }"
              @click="selectSection(index)"
            >
              <div class="section-header">
                <div class="section-info">
                  <component :is="getSectionIcon(section.type) + 'Icon'" class="h-5 w-5" />
                  <span class="section-title">{{ section.title || getSectionTitle(section.type) }}</span>
                </div>
                <div class="section-actions">
                  <Button variant="ghost" size="sm" @click.stop="moveSection(index, -1)" :disabled="index === 0">
                    <ArrowUpIcon class="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" @click.stop="moveSection(index, 1)" :disabled="index === reportData.sections.length - 1">
                    <ArrowDownIcon class="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" @click.stop="editSection(index)">
                    <EditIcon class="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" @click.stop="removeSection(index)">
                    <XIcon class="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div class="section-content">
                <component
                  :is="getSectionComponent(section.type)"
                  :section="section"
                  :preview="true"
                  @update="updateSection(index, $event)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section Properties Panel -->
      <div class="properties-panel" v-if="selectedSection !== null">
        <h3 class="panel-title">Section Properties</h3>
        
        <div class="property-group">
          <label class="property-label">Section Title</label>
          <Input
            v-model="currentSectionData.title"
            placeholder="Enter section title"
            @input="updateCurrentSection"
          />
        </div>

        <component
          :is="getSectionPropertiesComponent(currentSectionData.type)"
          :section="currentSectionData"
          @update="updateCurrentSection"
        />
      </div>
    </div>

    <!-- Template Modal -->
    <div v-if="showTemplateModal" class="modal-overlay">
      <div class="modal-container large">
        <div class="modal-header">
          <h3 class="modal-title">Select Report Template</h3>
          <Button variant="ghost" size="sm" @click="showTemplateModal = false">
            <XIcon class="h-4 w-4" />
          </Button>
        </div>

        <div class="template-grid">
          <div
            v-for="template in reportStore.activeTemplates"
            :key="template.name"
            class="template-card"
            @click="applyTemplate(template)"
          >
            <div class="template-header">
              <component :is="reportStore.getReportIcon(template.template_type) + 'Icon'" class="template-icon" />
              <div class="template-info">
                <h4 class="template-name">{{ template.template_name }}</h4>
                <p class="template-type">{{ template.template_type }}</p>
              </div>
            </div>
            <p class="template-description">{{ template.description || 'No description available' }}</p>
            <div class="template-meta">
              <Badge v-if="template.is_default" variant="secondary">Default</Badge>
              <span class="template-sections">{{ template.sections?.length || 0 }} sections</span>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="reportStore.activeTemplates.length === 0" class="empty-templates">
            <LayoutTemplateIcon class="empty-icon" />
            <h4>No Templates Available</h4>
            <p>Create your first template to get started</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <div v-if="showPreviewModal" class="modal-overlay">
      <div class="modal-container extra-large">
        <div class="modal-header">
          <h3 class="modal-title">Report Preview</h3>
          <div class="preview-actions">
            <Select
              v-model="previewFormat"
              :options="formatOptions"
              class="format-select"
            />
            <Button variant="outline" @click="exportPreview">
              <DownloadIcon class="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="ghost" size="sm" @click="showPreviewModal = false">
              <XIcon class="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div class="preview-content">
          <div v-if="reportStore.loading" class="preview-loading">
            <Loader2Icon class="loading-icon" />
            <p>Generating preview...</p>
          </div>

          <div v-else-if="reportStore.previewData" class="report-preview">
            <div class="preview-report">
              <div class="report-header">
                <h1 class="report-title">{{ reportData.title }}</h1>
                <p class="report-meta">
                  Generated on {{ formatDate(new Date()) }} | {{ reportData.report_type }}
                </p>
              </div>

              <div class="report-body">
                <div
                  v-for="(section, index) in reportData.sections"
                  :key="section.id"
                  class="preview-section"
                >
                  <component
                    :is="getSectionComponent(section.type)"
                    :section="section"
                    :data="reportStore.previewData.sections?.[index]"
                    :preview="false"
                  />
                </div>
              </div>
            </div>
          </div>

          <div v-else class="preview-error">
            <AlertTriangleIcon class="error-icon" />
            <h4>Preview Error</h4>
            <p>{{ reportStore.error || 'Failed to generate preview' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useReportsStore } from "@/stores/reports"
import { Badge, Button, Input, Select } from "frappe-ui"
import {
	AlertTriangleIcon,
	ArrowDownIcon,
	ArrowUpIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	FileTextIcon,
	LayoutTemplateIcon,
	Loader2Icon,
	SaveIcon,
	TrashIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"

import ChartSection from "./sections/ChartSection.vue"
import FindingsSection from "./sections/FindingsSection.vue"
import FooterSection from "./sections/FooterSection.vue"
// Section components imports
import HeaderSection from "./sections/HeaderSection.vue"
import ImageSection from "./sections/ImageSection.vue"
import PageBreakSection from "./sections/PageBreakSection.vue"
import TableSection from "./sections/TableSection.vue"
import TextSection from "./sections/TextSection.vue"

import ChartProperties from "./properties/ChartProperties.vue"
import FindingsProperties from "./properties/FindingsProperties.vue"
// Properties components imports
import HeaderProperties from "./properties/HeaderProperties.vue"
import ImageProperties from "./properties/ImageProperties.vue"
import TableProperties from "./properties/TableProperties.vue"
import TextProperties from "./properties/TextProperties.vue"

// Props
const props = defineProps({
	reportId: {
		type: String,
		default: null,
	},
	templateId: {
		type: String,
		default: null,
	},
})

// Store
const reportStore = useReportsStore()

// Reactive state
const reportData = ref({
	title: "",
	report_type: "",
	status: "Draft",
	description: "",
	tags: "",
	sections: [],
})

const selectedSection = ref(null)
const showTemplateModal = ref(false)
const showPreviewModal = ref(false)
const saving = ref(false)
const previewFormat = ref("pdf")

// Options
const statusOptions = [
	{ label: "Draft", value: "Draft" },
	{ label: "Published", value: "Published" },
	{ label: "Archived", value: "Archived" },
]

const formatOptions = [
	{ label: "PDF", value: "pdf" },
	{ label: "Excel", value: "xlsx" },
	{ label: "Word", value: "docx" },
	{ label: "HTML", value: "html" },
]

// Computed properties
const currentSectionData = computed(() => {
	return selectedSection.value !== null
		? reportData.value.sections[selectedSection.value]
		: {}
})

// Methods
const startDrag = (event, sectionType) => {
	event.dataTransfer.setData(
		"application/json",
		JSON.stringify({
			type: "section",
			sectionType: sectionType.value,
			label: sectionType.label,
			icon: sectionType.icon,
		}),
	)
}

const startChartDrag = (event, chartType) => {
	event.dataTransfer.setData(
		"application/json",
		JSON.stringify({
			type: "chart",
			chartType: chartType.value,
			label: chartType.label,
			icon: chartType.icon,
		}),
	)
}

const handleDrop = (event) => {
	event.preventDefault()
	const data = JSON.parse(event.dataTransfer.getData("application/json"))

	if (data.type === "section") {
		addSection(data.sectionType, data.label)
	} else if (data.type === "chart") {
		addChartSection(data.chartType, data.label)
	}
}

const addSection = (type, label) => {
	const newSection = {
		id: generateSectionId(),
		type: type,
		title: label,
		order: reportData.value.sections.length,
		config: getDefaultSectionConfig(type),
	}

	reportData.value.sections.push(newSection)
	selectedSection.value = reportData.value.sections.length - 1
}

const addChartSection = (chartType, label) => {
	const newSection = {
		id: generateSectionId(),
		type: "chart",
		title: label,
		order: reportData.value.sections.length,
		config: {
			chart_type: chartType,
			title: label,
			data_source: "",
			x_field: "",
			y_field: "",
			filters: [],
			styling: {
				width: "100%",
				height: 400,
				colors: ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"],
			},
		},
	}

	reportData.value.sections.push(newSection)
	selectedSection.value = reportData.value.sections.length - 1
}

const removeSection = (index) => {
	reportData.value.sections.splice(index, 1)
	if (selectedSection.value === index) {
		selectedSection.value = null
	} else if (selectedSection.value > index) {
		selectedSection.value--
	}
}

const moveSection = (index, direction) => {
	const newIndex = index + direction
	if (newIndex >= 0 && newIndex < reportData.value.sections.length) {
		const section = reportData.value.sections.splice(index, 1)[0]
		reportData.value.sections.splice(newIndex, 0, section)
		selectedSection.value = newIndex
	}
}

const selectSection = (index) => {
	selectedSection.value = selectedSection.value === index ? null : index
}

const editSection = (index) => {
	selectedSection.value = index
}

const updateSection = (index, updates) => {
	reportData.value.sections[index] = {
		...reportData.value.sections[index],
		...updates,
	}
}

const updateCurrentSection = (updates) => {
	if (selectedSection.value !== null) {
		const section = reportData.value.sections[selectedSection.value]
		if (typeof updates === "object" && updates !== null) {
			reportData.value.sections[selectedSection.value] = {
				...section,
				...updates,
			}
		} else {
			// Handle direct property updates
			reportData.value.sections[selectedSection.value] = { ...section }
		}
	}
}

const clearAll = () => {
	if (confirm("Are you sure you want to clear all sections?")) {
		reportData.value.sections = []
		selectedSection.value = null
	}
}

const saveReport = async () => {
	try {
		saving.value = true

		const reportPayload = {
			...reportData.value,
			tags: reportData.value.tags
				? reportData.value.tags.split(",").map((t) => t.trim())
				: [],
		}

		if (props.reportId) {
			await reportStore.updateCustomReport(props.reportId, reportPayload)
		} else {
			await reportStore.createCustomReport(reportPayload)
		}

		// Success feedback
		alert("Report saved successfully!")
	} catch (error) {
		console.error("Error saving report:", error)
		alert("Failed to save report. Please try again.")
	} finally {
		saving.value = false
	}
}

const previewReport = async () => {
	try {
		await reportStore.previewReport(reportData.value)
		showPreviewModal.value = true
	} catch (error) {
		console.error("Error previewing report:", error)
		alert("Failed to preview report. Please check your configuration.")
	}
}

const exportPreview = async () => {
	try {
		const reportId = props.reportId || "preview"
		await reportStore.exportReport(reportId, previewFormat.value, {
			preview_data: reportStore.previewData,
		})
	} catch (error) {
		console.error("Error exporting report:", error)
		alert("Failed to export report. Please try again.")
	}
}

const applyTemplate = async (template) => {
	try {
		// Load template details
		const templateData = await reportStore.getTemplateById(template.name)

		reportData.value = {
			title: `${template.template_name} - Copy`,
			report_type: template.template_type,
			status: "Draft",
			description: template.description,
			tags: template.tags || "",
			sections: templateData.sections || [],
		}

		showTemplateModal.value = false
		selectedSection.value = null
	} catch (error) {
		console.error("Error applying template:", error)
		alert("Failed to apply template. Please try again.")
	}
}

// Utility methods
const generateSectionId = () => {
	return `section_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

const getDefaultSectionConfig = (type) => {
	const configs = {
		header: {
			level: 1,
			text: "Section Header",
			alignment: "left",
			styling: { color: "#000", fontSize: "2rem" },
		},
		text: {
			content: "Enter your text content here...",
			alignment: "left",
			styling: { fontSize: "1rem", lineHeight: 1.5 },
		},
		table: {
			data_source: "",
			columns: [],
			filters: [],
			pagination: true,
			styling: { striped: true, bordered: true },
		},
		chart: {
			chart_type: "bar",
			data_source: "",
			x_field: "",
			y_field: "",
			filters: [],
			styling: { width: "100%", height: 400 },
		},
		findings: {
			finding_types: [],
			status_filter: "",
			severity_filter: "",
			group_by: "finding_type",
		},
		image: {
			src: "",
			alt: "",
			alignment: "center",
			styling: { width: "100%", maxWidth: "600px" },
		},
		pagebreak: {},
		footer: {
			content: "© 2025 Internal Audit Department",
			alignment: "center",
			styling: { fontSize: "0.875rem", color: "#666" },
		},
	}

	return configs[type] || {}
}

const getSectionComponent = (type) => {
	const components = {
		header: HeaderSection,
		text: TextSection,
		table: TableSection,
		chart: ChartSection,
		findings: FindingsSection,
		image: ImageSection,
		pagebreak: PageBreakSection,
		footer: FooterSection,
	}
	return components[type] || TextSection
}

const getSectionPropertiesComponent = (type) => {
	const components = {
		header: HeaderProperties,
		text: TextProperties,
		table: TableProperties,
		chart: ChartProperties,
		findings: FindingsProperties,
		image: ImageProperties,
		pagebreak: null,
		footer: TextProperties,
	}
	return components[type]
}

const getSectionIcon = (type) => {
	const icons = {
		header: "Heading1",
		text: "Type",
		table: "Table",
		chart: "BarChart3",
		findings: "AlertTriangle",
		image: "Image",
		pagebreak: "Minus",
		footer: "AlignLeft",
	}
	return icons[type] || "FileText"
}

const getSectionTitle = (type) => {
	const titles = {
		header: "Header Section",
		text: "Text Content",
		table: "Data Table",
		chart: "Chart/Graph",
		findings: "Finding List",
		image: "Image/Logo",
		pagebreak: "Page Break",
		footer: "Footer Section",
	}
	return titles[type] || "Section"
}

const formatDate = (date) => {
	return new Date(date).toLocaleDateString("en-US", {
		year: "numeric",
		month: "long",
		day: "numeric",
	})
}

// Watchers
watch(
	() => props.reportId,
	async (newReportId) => {
		if (newReportId) {
			const report = await reportStore.getReportById(newReportId)
			if (report) {
				reportData.value = {
					title: report.title,
					report_type: report.report_type,
					status: report.status,
					description: report.description,
					tags: Array.isArray(report.tags)
						? report.tags.join(", ")
						: report.tags || "",
					sections: report.sections || [],
				}
			}
		}
	},
	{ immediate: true },
)

watch(
	() => props.templateId,
	async (newTemplateId) => {
		if (newTemplateId) {
			const template = await reportStore.getTemplateById(newTemplateId)
			if (template) {
				applyTemplate(template)
			}
		}
	},
	{ immediate: true },
)

// Lifecycle
onMounted(async () => {
	await Promise.all([
		reportStore.fetchReportTemplates(),
		reportStore.fetchCustomReports(),
	])
})
</script>

<style scoped>
.report-builder {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--background-color);
}

.builder-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--card-background);
}

.header-content .builder-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.title-icon {
  color: var(--primary-color);
}

.builder-description {
  color: var(--text-muted);
  margin: 0.5rem 0 0 0;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.report-config {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--card-background);
}

.config-section {
  max-width: 1200px;
  margin: 0 auto;
}

.config-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.config-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.config-group.full-width {
  grid-column: 1 / -1;
}

.config-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
}

.config-textarea {
  width: 100%;
  min-height: 80px;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  resize: vertical;
  font-family: inherit;
}

.builder-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.section-library {
  width: 280px;
  border-right: 1px solid var(--border-color);
  background: var(--card-background);
  padding: 1.5rem;
  overflow-y: auto;
}

.library-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.library-description {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0 0 1.5rem 0;
}

.section-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.section-item,
.chart-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  cursor: grab;
  transition: all 0.15s ease;
  background: var(--background-color);
}

.section-item:hover,
.chart-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-item:active,
.chart-item:active {
  cursor: grabbing;
}

.section-icon,
.chart-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--primary-color);
  flex-shrink: 0;
}

.section-label,
.chart-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
}

.subsection {
  margin-top: 2rem;
}

.subsection-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.chart-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.report-canvas {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--background-color);
}

.canvas-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--card-background);
}

.canvas-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.canvas-actions {
  display: flex;
  gap: 0.5rem;
}

.canvas-area {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.empty-canvas {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-canvas h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.report-sections {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.report-section {
  background: var(--card-background);
  border: 2px solid var(--border-color);
  border-radius: 0.5rem;
  transition: border-color 0.15s ease;
}

.report-section.selected {
  border-color: var(--primary-color);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--background-color);
  border-radius: 0.5rem 0.5rem 0 0;
}

.section-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-title {
  font-weight: 500;
  color: var(--text-color);
}

.section-actions {
  display: flex;
  gap: 0.25rem;
}

.section-content {
  padding: 1.5rem;
}

.properties-panel {
  width: 320px;
  border-left: 1px solid var(--border-color);
  background: var(--card-background);
  padding: 1.5rem;
  overflow-y: auto;
}

.panel-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1.5rem 0;
}

.property-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.property-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: var(--card-background);
  border-radius: 0.5rem;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-container.large {
  max-width: 1000px;
}

.modal-container.extra-large {
  max-width: 1200px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.preview-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.format-select {
  width: 120px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  padding: 1.5rem;
}

.template-card {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.template-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.template-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.template-icon {
  width: 2.5rem;
  height: 2.5rem;
  color: var(--primary-color);
}

.template-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.template-type {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0;
}

.template-description {
  font-size: 0.875rem;
  color: var(--text-color);
  margin-bottom: 1rem;
  line-height: 1.4;
}

.template-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-sections {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.empty-templates {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.preview-content {
  max-height: calc(90vh - 120px);
  overflow-y: auto;
}

.preview-loading,
.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-icon,
.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.loading-icon {
  color: var(--primary-color);
  animation: spin 1s linear infinite;
}

.error-icon {
  color: var(--danger-color);
}

.report-preview {
  padding: 2rem;
  background: white;
  min-height: 100%;
}

.preview-report {
  max-width: 21cm;
  margin: 0 auto;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.report-header {
  text-align: center;
  margin-bottom: 3rem;
  border-bottom: 2px solid #eee;
  padding-bottom: 2rem;
}

.report-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.report-meta {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.report-body {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.preview-section {
  padding: 1rem 0;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive design */
@media (max-width: 1024px) {
  .builder-main {
    flex-direction: column;
  }

  .section-library {
    width: 100%;
    max-height: 300px;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }

  .properties-panel {
    width: 100%;
    max-height: 300px;
    border-left: none;
    border-top: 1px solid var(--border-color);
  }

  .config-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .builder-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .header-actions {
    justify-content: flex-end;
  }

  .modal-container {
    width: 95%;
    max-height: 95vh;
  }

  .template-grid {
    grid-template-columns: 1fr;
  }
}
</style>