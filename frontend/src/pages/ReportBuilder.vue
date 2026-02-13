<template>
  <div class="p-6 max-w-7xl mx-auto">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <Columns class="w-8 h-8 text-blue-600" />
          Report Builder
        </h1>
        <p class="text-gray-600 mt-2 text-lg">Create custom reports with drag-and-drop functionality</p>
      </div>
      <div class="flex flex-wrap gap-3">
        <Button @click="saveReport" :loading="saving" variant="outline" class="flex items-center gap-2">
          <Save class="w-4 h-4" />
          Save Report
        </Button>
        <Button @click="previewReport" :loading="generating" class="flex items-center gap-2">
          <Eye class="w-4 h-4" />
          Preview
        </Button>
        <Button @click="exportReport" :loading="exporting" variant="outline" class="flex items-center gap-2">
          <Download class="w-4 h-4" />
          Export
        </Button>
      </div>
    </div>

    <!-- Report Configuration -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
      <!-- Data Source Selection -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-lg border shadow-sm p-4 h-fit">
          <h3 class="font-semibold mb-4 flex items-center gap-2">
            <Database class="w-5 h-5 text-blue-600" />
            Data Source
          </h3>
          <div class="space-y-4">
            <FormControl
              label="Select DocType"
              v-model="reportConfig.doctype"
              type="select"
              :options="doctypeOptions"
              @change="loadFields"
              required
            />
            <div v-if="reportConfig.doctype" class="space-y-3">
              <h4 class="font-medium text-sm text-gray-700 flex items-center justify-between">
                Available Fields
                <Badge variant="secondary" size="sm">{{ availableFields.length }}</Badge>
              </h4>
              <div class="space-y-2 max-h-80 overflow-y-auto border rounded-md p-2 bg-gray-50">
                <div
                  v-for="field in availableFields"
                  :key="field.fieldname"
                  class="flex items-center justify-between gap-2 p-2 border rounded cursor-pointer hover:bg-white hover:shadow-sm transition-all duration-200"
                  @dragstart="onDragStart($event, field)"
                  draggable="true"
                >
                  <div class="flex items-center gap-2 flex-1 min-w-0">
                    <Database class="w-4 h-4 text-gray-500 flex-shrink-0" />
                    <span class="text-sm truncate">{{ field.label }}</span>
                  </div>
                  <Badge
                    :variant="getFieldTypeVariant(field.fieldtype)"
                    size="sm"
                    class="flex-shrink-0"
                  >
                    {{ field.fieldtype }}
                  </Badge>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Report Builder Canvas -->
      <div class="lg:col-span-3">
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="font-semibold flex items-center gap-2">
              <Columns class="w-5 h-5 text-green-600" />
              Report Canvas
            </h3>
            <div class="flex gap-2">
              <Button @click="clearCanvas" variant="outline" size="sm" class="flex items-center gap-2">
                <Trash2 class="w-4 h-4" />
                Clear
              </Button>
            </div>
          </div>

          <!-- Drop Zones -->
          <div class="space-y-6">
            <!-- Columns Section -->
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 min-h-32 transition-all duration-200 hover:border-blue-400 hover:bg-blue-50/50"
                 @dragover.prevent
                 @drop="onDrop($event, 'columns')">
              <div class="flex items-center justify-between mb-4">
                <h4 class="font-medium flex items-center gap-2 text-gray-700">
                  <Columns class="w-4 h-4 text-blue-600" />
                  Columns
                </h4>
                <Badge variant="secondary" size="sm">{{ selectedColumns.length }}</Badge>
              </div>
              <div class="flex flex-wrap gap-2 min-h-16">
                <div
                  v-for="(field, index) in selectedColumns"
                  :key="field.fieldname"
                  class="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 hover:bg-blue-100 transition-colors duration-200"
                >
                  <Database class="w-3 h-3 text-blue-600 flex-shrink-0" />
                  <span class="text-sm font-medium">{{ field.label }}</span>
                  <Button @click="removeField('columns', index)" variant="ghost" size="sm" class="p-0 h-5 w-5 hover:bg-blue-200">
                    <X class="w-3 h-3" />
                  </Button>
                </div>
                <div v-if="selectedColumns.length === 0" class="flex items-center justify-center w-full min-h-16 text-gray-500 text-sm">
                  <div class="text-center">
                    <Columns class="w-8 h-8 mx-auto mb-2 opacity-50" />
                    Drag fields here to add columns to your report
                  </div>
                </div>
              </div>
            </div>

            <!-- Filters Section -->
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 min-h-32 transition-all duration-200 hover:border-green-400 hover:bg-green-50/50"
                 @dragover.prevent
                 @drop="onDrop($event, 'filters')">
              <div class="flex items-center justify-between mb-4">
                <h4 class="font-medium flex items-center gap-2 text-gray-700">
                  <Filter class="w-4 h-4 text-green-600" />
                  Filters
                </h4>
                <Badge variant="secondary" size="sm">{{ selectedFilters.length }}</Badge>
              </div>
              <div class="space-y-3 min-h-16">
                <div
                  v-for="(filter, index) in selectedFilters"
                  :key="filter.field.fieldname"
                  class="flex items-center gap-3 bg-green-50 border border-green-200 rounded-lg p-3 hover:bg-green-100 transition-colors duration-200"
                >
                  <Filter class="w-4 h-4 text-green-600 flex-shrink-0" />
                  <div class="flex-1 min-w-0">
                    <span class="text-sm font-medium block">{{ filter.field.label }}</span>
                  </div>
                  <FormControl
                    v-model="filter.operator"
                    type="select"
                    :options="filterOperators"
                    class="w-20 flex-shrink-0"
                    size="sm"
                  />
                  <FormControl
                    v-model="filter.value"
                    :type="getFilterInputType(filter.field)"
                    placeholder="Value"
                    class="flex-1 min-w-32"
                    size="sm"
                  />
                  <Button @click="removeField('filters', index)" variant="ghost" size="sm" class="p-0 h-6 w-6 hover:bg-green-200 flex-shrink-0">
                    <X class="w-4 h-4" />
                  </Button>
                </div>
                <div v-if="selectedFilters.length === 0" class="flex items-center justify-center w-full min-h-16 text-gray-500 text-sm">
                  <div class="text-center">
                    <Filter class="w-8 h-8 mx-auto mb-2 opacity-50" />
                    Drag fields here to add filters to your report
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Report Settings -->
    <div class="bg-white rounded-lg border shadow-sm p-6 mb-6">
      <h3 class="font-semibold mb-6 flex items-center gap-2">
        <Save class="w-5 h-5 text-gray-900" />
        Report Settings
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <FormControl
          label="Report Title"
          v-model="reportConfig.title"
          type="text"
          placeholder="Enter report title"
          required
        />
        <FormControl
          label="Report Type"
          v-model="reportConfig.type"
          type="select"
          :options="reportTypeOptions"
        />
        <FormControl
          label="Chart Type"
          v-model="reportConfig.chartType"
          type="select"
          :options="chartTypeOptions"
        />
      </div>
      <div class="mt-6">
        <FormControl
          label="Description"
          v-model="reportConfig.description"
          type="textarea"
          placeholder="Optional description"
          rows="3"
        />
      </div>
    </div>

    <!-- Report Preview -->
    <div v-if="reportData.length > 0" class="bg-white rounded-lg border shadow-sm p-6">
      <div class="flex justify-between items-center mb-6">
        <h3 class="font-semibold flex items-center gap-2">
          <Eye class="w-5 h-5 text-indigo-600" />
          Report Preview
          <Badge variant="secondary" size="sm">{{ reportData.length }} rows</Badge>
        </h3>
        <div class="flex gap-2">
          <Button @click="refreshPreview" :loading="generating" variant="outline" size="sm" class="flex items-center gap-2">
            <RefreshCw class="w-4 h-4" />
            Refresh
          </Button>
        </div>
      </div>

      <!-- Data Table -->
      <div class="overflow-x-auto border rounded-lg">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                v-for="column in selectedColumns"
                :key="column.fieldname"
                class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider border-b"
              >
                <div class="flex items-center gap-2">
                  <Database class="w-4 h-4 text-gray-500" />
                  {{ column.label }}
                </div>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="(row, rowIndex) in reportData.slice(0, 10)"
              :key="row.name || row.id || rowIndex"
              class="hover:bg-gray-50 transition-colors duration-150"
            >
              <td
                v-for="column in selectedColumns"
                :key="column.fieldname"
                class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
              >
                {{ formatCellValue(row[column.fieldname], column) }}
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="reportData.length > 10" class="text-center py-4 text-gray-500 bg-gray-50 border-t">
          <div class="flex items-center justify-center gap-2">
            <Eye class="w-4 h-4" />
            Showing first 10 rows of {{ reportData.length }} total rows
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, FormControl } from "frappe-ui"
import {
	Columns,
	Database,
	Download,
	Eye,
	Filter,
	RefreshCw,
	Save,
	Trash2,
	X,
} from "lucide-vue-next"
import { onMounted, ref } from "vue"

// Reactive data
const reportConfig = ref({
	doctype: "",
	title: "",
	type: "Custom Report",
	chartType: "Table Only",
	description: "",
})

const availableFields = ref([])
const selectedColumns = ref([])
const selectedFilters = ref([])
const reportData = ref([])

const saving = ref(false)
const generating = ref(false)
const exporting = ref(false)

// Options
const doctypeOptions = [
	{ label: "Audit Engagement", value: "Audit Engagement" },
	{ label: "Audit Finding", value: "Audit Finding" },
	{ label: "Corrective Action", value: "Corrective Action" },
	{ label: "Compliance Requirement", value: "Compliance Requirement" },
	{ label: "Risk Assessment", value: "Risk Assessment" },
]

const reportTypeOptions = [
	{ label: "Custom Report", value: "Custom Report" },
	{ label: "Summary Report", value: "Summary Report" },
	{ label: "Detailed Report", value: "Detailed Report" },
	{ label: "Compliance Report", value: "Compliance Report" },
]

const chartTypeOptions = [
	{ label: "Table Only", value: "Table Only" },
	{ label: "Bar Chart", value: "Bar Chart" },
	{ label: "Line Chart", value: "Line Chart" },
	{ label: "Pie Chart", value: "Pie Chart" },
	{ label: "Doughnut Chart", value: "Doughnut Chart" },
]

const filterOperators = [
	{ label: "=", value: "=" },
	{ label: "!=", value: "!=" },
	{ label: ">", value: ">" },
	{ label: "<", value: "<" },
	{ label: ">=", value: ">=" },
	{ label: "<=", value: "<=" },
	{ label: "Like", value: "like" },
	{ label: "In", value: "in" },
	{ label: "Not In", value: "not in" },
]

// Methods
const getFilterInputType = (field) => {
	if (!field) return "text"
	const typeMap = {
		Data: "text",
		Int: "number",
		Float: "number",
		Currency: "number",
		Date: "date",
		Datetime: "datetime-local",
		Select: "select",
		Check: "checkbox",
		Link: "text",
		"Small Text": "text",
		"Text Editor": "text",
		"Long Text": "text",
	}
	return typeMap[field.fieldtype] || "text"
}

const loadFields = async () => {
	if (!reportConfig.value.doctype) return

	try {
		// Mock field loading - in real implementation, this would fetch from Frappe
		const mockFields = {
			"Audit Engagement": [
				{ fieldname: "name", label: "ID", fieldtype: "Data" },
				{ fieldname: "engagement_title", label: "Title", fieldtype: "Data" },
				{ fieldname: "audit_type", label: "Audit Type", fieldtype: "Select" },
				{ fieldname: "start_date", label: "Start Date", fieldtype: "Date" },
				{ fieldname: "end_date", label: "End Date", fieldtype: "Date" },
				{ fieldname: "status", label: "Status", fieldtype: "Select" },
				{ fieldname: "risk_rating", label: "Risk Rating", fieldtype: "Select" },
				{
					fieldname: "assigned_auditor",
					label: "Assigned Auditor",
					fieldtype: "Link",
				},
			],
			"Audit Finding": [
				{ fieldname: "name", label: "ID", fieldtype: "Data" },
				{ fieldname: "finding_title", label: "Title", fieldtype: "Data" },
				{ fieldname: "finding_type", label: "Type", fieldtype: "Select" },
				{ fieldname: "severity", label: "Severity", fieldtype: "Select" },
				{ fieldname: "status", label: "Status", fieldtype: "Select" },
				{
					fieldname: "engagement_reference",
					label: "Engagement",
					fieldtype: "Link",
				},
				{ fieldname: "finding_date", label: "Date", fieldtype: "Date" },
			],
			"Corrective Action": [
				{ fieldname: "name", label: "ID", fieldtype: "Data" },
				{ fieldname: "action_title", label: "Title", fieldtype: "Data" },
				{ fieldname: "status", label: "Status", fieldtype: "Select" },
				{ fieldname: "priority", label: "Priority", fieldtype: "Select" },
				{ fieldname: "due_date", label: "Due Date", fieldtype: "Date" },
				{ fieldname: "assigned_to", label: "Assigned To", fieldtype: "Link" },
				{ fieldname: "finding_reference", label: "Finding", fieldtype: "Link" },
			],
		}

		availableFields.value = mockFields[reportConfig.value.doctype] || []
	} catch (error) {
		console.error("Error loading fields:", error)
	}
}

const onDragStart = (event, field) => {
	event.dataTransfer.setData("application/json", JSON.stringify(field))
}

const onDrop = (event, section) => {
	event.preventDefault()
	try {
		const field = JSON.parse(event.dataTransfer.getData("application/json"))

		if (section === "columns") {
			if (
				!selectedColumns.value.find((col) => col.fieldname === field.fieldname)
			) {
				selectedColumns.value.push(field)
			}
		} else if (section === "filters") {
			if (
				!selectedFilters.value.find(
					(f) => f.field.fieldname === field.fieldname,
				)
			) {
				selectedFilters.value.push({
					field,
					operator: "=",
					value: "",
				})
			}
		}
	} catch (error) {
		console.error("Error handling drop:", error)
	}
}

const removeField = (section, index) => {
	if (section === "columns") {
		selectedColumns.value.splice(index, 1)
	} else if (section === "filters") {
		selectedFilters.value.splice(index, 1)
	}
}

const clearCanvas = () => {
	selectedColumns.value = []
	selectedFilters.value = []
	reportData.value = []
}

const previewReport = async () => {
	if (selectedColumns.value.length === 0) {
		alert("Please select at least one column for your report")
		return
	}

	try {
		generating.value = true

		// Real API call to Frappe backend for report data
		const result = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: reportConfig.value.source_doctype || "Audit Engagement",
				fields: selectedColumns.value.map((col) => col.fieldname),
				filters: reportConfig.value.filters || {},
				limit_page_length: reportConfig.value.limit || 100,
			},
		}).fetch()

		reportData.value = result || []
	} catch (error) {
		console.error("Error generating preview:", error)
		// Fallback to empty array on error
		reportData.value = []
	} finally {
		generating.value = false
	}
}

const refreshPreview = () => {
	previewReport()
}

const saveReport = async () => {
	if (!reportConfig.value.title) {
		alert("Please enter a report title")
		return
	}

	try {
		saving.value = true

		// Create or update report via Frappe API
		await createResource({
			url: "frappe.client.insert",
			params: {
				doc: {
					doctype: "Report Template",
					template_name: reportConfig.value.title,
					report_type: reportConfig.value.report_type || "Custom",
					template_config: JSON.stringify({
						columns: selectedColumns.value,
						filters: reportConfig.value.filters || {},
						sort_by: reportConfig.value.sortBy,
						sort_order: reportConfig.value.sortOrder || "asc",
					}),
					is_active: 1,
				},
			},
		}).fetch()

		alert("Report saved successfully!")
	} catch (error) {
		console.error("Error saving report:", error)
		alert("Failed to save report: " + error.message)
	} finally {
		saving.value = false
	}
}

const exportReport = async () => {
	try {
		exporting.value = true

		if (reportData.value.length === 0) {
			await previewReport()
		}

		// Mock export - in real implementation, this would generate and download file
		const csvContent = generateCSV()
		const blob = new Blob([csvContent], { type: "text/csv" })
		const url = window.URL.createObjectURL(blob)
		const a = document.createElement("a")
		a.href = url
		a.download = `${reportConfig.value.title || "report"}.csv`
		a.click()
		window.URL.revokeObjectURL(url)
	} catch (error) {
		console.error("Error exporting report:", error)
	} finally {
		exporting.value = false
	}
}

const generateCSV = () => {
	const headers = selectedColumns.value.map((col) => col.label).join(",")
	const rows = reportData.value.map((row) =>
		selectedColumns.value
			.map((col) => formatCellValue(row[col.fieldname], col))
			.join(","),
	)
	return [headers, ...rows].join("\n")
}

const getFieldTypeVariant = (fieldtype) => {
	const variants = {
		Data: "secondary",
		Date: "info",
		Int: "warning",
		Select: "success",
		Link: "primary",
		Text: "secondary",
		"Text Editor": "secondary",
		Check: "success",
	}
	return variants[fieldtype] || "secondary"
}

const formatCellValue = (value, field) => {
	if (!value) return ""

	if (field.fieldtype === "Date" && value) {
		return new Date(value).toLocaleDateString()
	}

	return String(value)
}

// Lifecycle
onMounted(() => {
	// Initialize any required data
})
</script>

<style scoped>
/* Enhanced drop zone styles */
.drop-zone {
  transition: all 0.2s ease;
}

.drop-zone:hover {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

/* Field item hover effects */
.field-item {
  transition: all 0.2s ease;
}

.field-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Column and filter item animations */
.column-item, .filter-item {
  transition: all 0.2s ease;
}

.column-item:hover, .filter-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Table improvements */
.report-table {
  border-collapse: separate;
  border-spacing: 0;
}

.report-table th {
  position: sticky;
  top: 0;
  background: #f9fafb;
  z-index: 10;
}

.report-table td {
  vertical-align: middle;
}

/* Responsive improvements */
@media (max-width: 1024px) {
  .report-builder-container {
    padding: 1rem;
  }

  .header-actions {
    flex-direction: column;
    width: 100%;
  }

  .header-actions .button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .report-builder-container {
    padding: 0.5rem;
  }

  .report-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .data-source-panel {
    order: 2;
  }

  .canvas-panel {
    order: 1;
  }

  .drop-zones {
    gap: 1rem;
  }

  .settings-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .table-container {
    font-size: 0.875rem;
  }

  .table-container th,
  .table-container td {
    padding: 0.5rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.5rem;
  }

  .page-description {
    font-size: 0.875rem;
  }

  .drop-zone {
    padding: 1rem;
  }

  .field-list {
    max-height: 200px;
  }

  .table-container {
    font-size: 0.75rem;
  }
}

/* Loading states */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

/* Empty states */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.empty-state-icon {
  opacity: 0.5;
  margin-bottom: 1rem;
}

.empty-state h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: #6b7280;
  margin: 0;
}

/* Badge improvements */
.field-count-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.125rem 0.5rem;
}

/* Button improvements */
.action-button {
  transition: all 0.2s ease;
}

.action-button:hover {
  transform: translateY(-1px);
}

/* Form control improvements */
.form-grid {
  gap: 1.5rem;
}

.form-grid .form-control {
  margin-bottom: 0;
}
</style>