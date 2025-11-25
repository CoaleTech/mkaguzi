<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Report Builder</h1>
        <p class="text-gray-600">Create custom reports with drag-and-drop functionality</p>
      </div>
      <div class="flex gap-2">
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
        <div class="bg-white rounded-lg border shadow-sm p-4">
          <h3 class="font-semibold mb-4">Data Source</h3>
          <FormControl
            label="Select DocType"
            v-model="reportConfig.doctype"
            type="select"
            :options="doctypeOptions"
            @change="loadFields"
            required
          />
          <div v-if="reportConfig.doctype" class="mt-4">
            <h4 class="font-medium mb-2">Available Fields</h4>
            <div class="space-y-2 max-h-64 overflow-y-auto">
              <div
                v-for="field in availableFields"
                :key="field.fieldname"
                class="flex items-center gap-2 p-2 border rounded cursor-pointer hover:bg-gray-50"
                @dragstart="onDragStart($event, field)"
                draggable="true"
              >
                <Database class="w-4 h-4 text-gray-500" />
                <span class="text-sm">{{ field.label }}</span>
                <Badge v-if="field.fieldtype === 'Data'" variant="secondary" size="sm">{{ field.fieldtype }}</Badge>
                <Badge v-if="field.fieldtype === 'Date'" variant="info" size="sm">{{ field.fieldtype }}</Badge>
                <Badge v-if="field.fieldtype === 'Int'" variant="warning" size="sm">{{ field.fieldtype }}</Badge>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Report Builder Canvas -->
      <div class="lg:col-span-3">
        <div class="bg-white rounded-lg border shadow-sm p-4">
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-semibold">Report Canvas</h3>
            <div class="flex gap-2">
              <Button @click="clearCanvas" variant="outline" size="sm">
                <Trash2 class="w-4 h-4" />
              </Button>
            </div>
          </div>

          <!-- Drop Zones -->
          <div class="space-y-4">
            <!-- Columns Section -->
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-4 min-h-24"
                 @dragover.prevent
                 @drop="onDrop($event, 'columns')">
              <h4 class="font-medium mb-2 flex items-center gap-2">
                <Columns class="w-4 h-4" />
                Columns
                <Badge variant="secondary" size="sm">{{ selectedColumns.length }}</Badge>
              </h4>
              <div class="flex flex-wrap gap-2">
                <div
                  v-for="(field, index) in selectedColumns"
                  :key="field.fieldname"
                  class="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded px-3 py-1"
                >
                  <Database class="w-3 h-3 text-blue-600" />
                  <span class="text-sm">{{ field.label }}</span>
                  <Button @click="removeField('columns', index)" variant="ghost" size="sm" class="p-0 h-4 w-4">
                    <X class="w-3 h-3" />
                  </Button>
                </div>
              </div>
              <p v-if="selectedColumns.length === 0" class="text-gray-500 text-sm mt-2">
                Drag fields here to add columns to your report
              </p>
            </div>

            <!-- Filters Section -->
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-4 min-h-24"
                 @dragover.prevent
                 @drop="onDrop($event, 'filters')">
              <h4 class="font-medium mb-2 flex items-center gap-2">
                <Filter class="w-4 h-4" />
                Filters
                <Badge variant="secondary" size="sm">{{ selectedFilters.length }}</Badge>
              </h4>
              <div class="space-y-2">
                <div
                  v-for="(filter, index) in selectedFilters"
                  :key="filter.field.fieldname"
                  class="flex items-center gap-2 bg-green-50 border border-green-200 rounded p-2"
                >
                  <Filter class="w-3 h-3 text-green-600" />
                  <span class="text-sm">{{ filter.field.label }}</span>
                  <FormControl
                    v-model="filter.operator"
                    type="select"
                    :options="filterOperators"
                    class="w-24"
                    size="sm"
                  />
                  <FormControl
                    v-model="filter.value"
                    :type="getFilterInputType(filter.field)"
                    placeholder="Value"
                    class="flex-1"
                    size="sm"
                  />
                  <Button @click="removeField('filters', index)" variant="ghost" size="sm" class="p-0 h-6 w-6">
                    <X class="w-3 h-3" />
                  </Button>
                </div>
              </div>
              <p v-if="selectedFilters.length === 0" class="text-gray-500 text-sm mt-2">
                Drag fields here to add filters to your report
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Report Settings -->
    <div class="bg-white rounded-lg border shadow-sm p-4 mb-6">
      <h3 class="font-semibold mb-4">Report Settings</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
      <div class="mt-4">
        <FormControl
          label="Description"
          v-model="reportConfig.description"
          type="textarea"
          placeholder="Optional description"
        />
      </div>
    </div>

    <!-- Report Preview -->
    <div v-if="reportData.length > 0" class="bg-white rounded-lg border shadow-sm p-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-semibold">Report Preview</h3>
        <div class="flex gap-2">
          <Button @click="refreshPreview" :loading="generating" variant="outline" size="sm">
            <RefreshCw class="w-4 h-4" />
            Refresh
          </Button>
        </div>
      </div>

      <!-- Data Table -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                v-for="column in selectedColumns"
                :key="column.fieldname"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {{ column.label }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="row in reportData.slice(0, 10)" :key="row.name || row.id">
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
        <div v-if="reportData.length > 10" class="text-center py-4 text-gray-500">
          Showing first 10 rows of {{ reportData.length }} total rows
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
	{ label: "Test Execution", value: "Test Execution" },
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

		// Mock data generation - in real implementation, this would query Frappe
		const mockData = generateMockData()
		reportData.value = mockData
	} catch (error) {
		console.error("Error generating preview:", error)
	} finally {
		generating.value = false
	}
}

const refreshPreview = () => {
	previewReport()
}

const generateMockData = () => {
	const data = []
	const count = Math.floor(Math.random() * 50) + 10

	for (let i = 0; i < count; i++) {
		const row = {}
		selectedColumns.value.forEach((column) => {
			if (column.fieldtype === "Date") {
				const date = new Date()
				date.setDate(date.getDate() - Math.floor(Math.random() * 365))
				row[column.fieldname] = date.toISOString().split("T")[0]
			} else if (column.fieldtype === "Int") {
				row[column.fieldname] = Math.floor(Math.random() * 1000)
			} else {
				row[column.fieldname] = `Sample ${column.label} ${i + 1}`
			}
		})
		data.push(row)
	}

	return data
}

const saveReport = () => {
	if (!reportConfig.value.title) {
		alert("Please enter a report title")
		return
	}

	console.log("Saving report:", reportConfig.value)
	alert("Report saved successfully!")
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

const getFilterInputType = (field) => {
	if (field.fieldtype === "Date") return "date"
	if (field.fieldtype === "Int") return "number"
	return "text"
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
.drop-zone {
  transition: all 0.2s ease;
}

.drop-zone:hover {
  border-color: #3b82f6;
  background-color: #eff6ff;
}
</style>