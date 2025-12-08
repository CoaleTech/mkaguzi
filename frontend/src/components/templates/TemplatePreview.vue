<template>
  <div class="template-preview">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-semibold text-gray-900">{{ template.template_name }}</h2>
        <p class="text-gray-600">{{ template.template_type }} • {{ template.category }}</p>
      </div>
      <div class="flex items-center space-x-3">
        <Button @click="renderPreview" :loading="rendering" variant="outline">
          <RefreshCw class="w-4 h-4 mr-2" />
          Render
        </Button>
        <Button @click="$emit('close')" variant="outline">
          Close
        </Button>
      </div>
    </div>

    <!-- Preview Controls -->
    <div class="bg-gray-50 rounded-lg p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Sample Data
          </label>
          <select
            v-model="selectedSampleData"
            @change="renderPreview"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">No sample data</option>
            <option v-for="sample in sampleDataOptions" :key="sample.value" :value="sample.value">
              {{ sample.label }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Output Format
          </label>
          <select
            v-model="outputFormat"
            @change="renderPreview"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="html">HTML</option>
            <option value="text">Plain Text</option>
            <option value="json">JSON</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Theme
          </label>
          <select
            v-model="theme"
            @change="applyTheme"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Preview Area -->
    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700">Preview</span>
        <div class="flex items-center space-x-2">
          <Button
            @click="copyPreview"
            variant="ghost"
            size="sm"
            :disabled="!renderedContent"
          >
            <Copy class="w-4 h-4 mr-1" />
            Copy
          </Button>
          <Button
            @click="downloadPreview"
            variant="ghost"
            size="sm"
            :disabled="!renderedContent"
          >
            <Download class="w-4 h-4 mr-1" />
            Download
          </Button>
        </div>
      </div>

      <div class="p-6 min-h-96">
        <!-- HTML Preview -->
        <div
          v-if="outputFormat === 'html' && renderedContent"
          v-html="renderedContent"
          class="prose max-w-none"
          :class="themeClass"
        ></div>

        <!-- Text Preview -->
        <pre
          v-else-if="outputFormat === 'text' && renderedContent"
          class="whitespace-pre-wrap font-mono text-sm bg-gray-50 p-4 rounded"
        >{{ renderedContent }}</pre>

        <!-- JSON Preview -->
        <pre
          v-else-if="outputFormat === 'json' && renderedContent"
          class="whitespace-pre-wrap font-mono text-sm bg-gray-50 p-4 rounded"
        >{{ formattedJson }}</pre>

        <!-- Loading State -->
        <div v-else-if="rendering" class="flex items-center justify-center py-12">
          <RefreshCw class="w-6 h-6 animate-spin text-gray-400 mr-2" />
          <span class="text-gray-600">Rendering preview...</span>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-12">
          <FileText class="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">No preview available</h3>
          <p class="text-gray-600 mb-6">Click "Render" to generate a preview of this template</p>
          <Button @click="renderPreview" variant="solid">
            <RefreshCw class="w-4 h-4 mr-2" />
            Render Preview
          </Button>
        </div>
      </div>
    </div>

    <!-- Template Info -->
    <div class="mt-6 bg-gray-50 rounded-lg p-4">
      <h3 class="text-sm font-medium text-gray-900 mb-3">Template Information</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <span class="text-gray-500">Engine:</span>
          <span class="ml-2 font-medium">{{ template.template_engine }}</span>
        </div>
        <div>
          <span class="text-gray-500">Status:</span>
          <span class="ml-2 font-medium" :class="template.is_active ? 'text-green-600' : 'text-red-600'">
            {{ template.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>
        <div>
          <span class="text-gray-500">Default:</span>
          <span class="ml-2 font-medium" :class="template.is_default ? 'text-blue-600' : 'text-gray-600'">
            {{ template.is_default ? 'Yes' : 'No' }}
          </span>
        </div>
        <div>
          <span class="text-gray-500">Usage:</span>
          <span class="ml-2 font-medium">{{ template.usage_count || 0 }}</span>
        </div>
      </div>
      <div v-if="template.description" class="mt-3">
        <span class="text-gray-500">Description:</span>
        <p class="mt-1 text-sm text-gray-700">{{ template.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { call } from "frappe-ui"
import { Copy, Download, FileText, RefreshCw } from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

// Props
const props = defineProps({
	template: {
		type: Object,
		required: true,
	},
})

// Emits
const emit = defineEmits(["close"])

// Reactive data
const selectedSampleData = ref("")
const outputFormat = ref("html")
const theme = ref("light")
const renderedContent = ref("")
const rendering = ref(false)

// Sample data options
const sampleDataOptions = [
	{ label: "Audit Report Data", value: "audit_report" },
	{ label: "Compliance Data", value: "compliance" },
	{ label: "Risk Assessment Data", value: "risk_assessment" },
	{ label: "Dashboard Data", value: "dashboard" },
	{ label: "Form Data", value: "form" },
]

// Computed
const themeClass = computed(() => {
	return theme.value === "dark" ? "prose-invert" : ""
})

const formattedJson = computed(() => {
	try {
		const parsed = JSON.parse(renderedContent.value)
		return JSON.stringify(parsed, null, 2)
	} catch {
		return renderedContent.value
	}
})

// Methods
const getSampleData = (type) => {
	const sampleData = {
		audit_report: {
			title: "Internal Audit Report",
			date: new Date().toLocaleDateString(),
			auditor: "John Doe",
			department: "Finance",
			findings: [
				{
					id: "F001",
					title: "Control Weakness in Accounts Payable",
					severity: "High",
					description:
						"Inadequate segregation of duties in the accounts payable process.",
					recommendation:
						"Implement additional approval levels for high-value transactions.",
				},
				{
					id: "F002",
					title: "Missing Documentation",
					severity: "Medium",
					description: "Several transactions lack supporting documentation.",
					recommendation:
						"Establish clear documentation requirements and training.",
				},
			],
			summary: {
				total_findings: 2,
				high_severity: 1,
				medium_severity: 1,
				low_severity: 0,
			},
		},
		compliance: {
			company: "Sample Corp",
			period: "Q1 2024",
			standards: ["SOX", "GDPR", "ISO 27001"],
			compliance_score: 85,
			issues: [
				{ area: "Data Protection", status: "Compliant", score: 90 },
				{ area: "Access Control", status: "Needs Improvement", score: 75 },
				{ area: "Audit Trail", status: "Compliant", score: 95 },
			],
		},
		risk_assessment: {
			project: "ERP Implementation",
			risks: [
				{
					description: "Data migration errors",
					probability: "High",
					impact: "High",
					mitigation: "Thorough testing",
				},
				{
					description: "User adoption issues",
					probability: "Medium",
					impact: "Medium",
					mitigation: "Training program",
				},
				{
					description: "Budget overruns",
					probability: "Low",
					impact: "High",
					mitigation: "Regular monitoring",
				},
			],
		},
		dashboard: {
			kpis: [
				{ name: "Audit Completion Rate", value: "87%", trend: "up" },
				{ name: "Open Findings", value: "23", trend: "down" },
				{ name: "Compliance Score", value: "92%", trend: "up" },
				{ name: "Risk Level", value: "Medium", trend: "stable" },
			],
			recent_activity: [
				{ action: "Audit completed", user: "Jane Smith", time: "2 hours ago" },
				{
					action: "Finding resolved",
					user: "Mike Johnson",
					time: "4 hours ago",
				},
				{ action: "Report generated", user: "Sarah Wilson", time: "1 day ago" },
			],
		},
		form: {
			name: "John Doe",
			email: "john.doe@company.com",
			department: "Finance",
			position: "Senior Accountant",
			submission_date: new Date().toISOString().split("T")[0],
			comments: "Please review the attached financial statements for Q1 2024.",
		},
	}

	return sampleData[type] || {}
}

const renderPreview = async () => {
	rendering.value = true
	try {
		const sampleData = selectedSampleData.value
			? getSampleData(selectedSampleData.value)
			: {}

		const result = await call(
			"mkaguzi.core.doctype.template_registry.template_registry.render_template",
			{
				template_name: props.template.template_name,
				context: sampleData,
				output_format: outputFormat.value,
			},
		)

		renderedContent.value = result.content || result
	} catch (error) {
		console.error("Error rendering template:", error)
		renderedContent.value = `Error rendering template: ${error.message}`
	} finally {
		rendering.value = false
	}
}

const copyPreview = async () => {
	try {
		await navigator.clipboard.writeText(renderedContent.value)
		// Could show a toast notification here
	} catch (error) {
		console.error("Error copying to clipboard:", error)
	}
}

const downloadPreview = () => {
	const blob = new Blob([renderedContent.value], {
		type: outputFormat.value === "html" ? "text/html" : "text/plain",
	})
	const url = URL.createObjectURL(blob)
	const a = document.createElement("a")
	a.href = url
	a.download = `${props.template.template_name}_preview.${outputFormat.value === "html" ? "html" : "txt"}`
	document.body.appendChild(a)
	a.click()
	document.body.removeChild(a)
	URL.revokeObjectURL(url)
}

const applyTheme = () => {
	// Theme is applied via CSS classes
}

// Lifecycle
onMounted(() => {
	// Auto-render if template has content
	if (props.template.template_content) {
		renderPreview()
	}
})
</script>

<style scoped>
.prose {
  max-width: none;
}

.prose-invert {
  color: #374151;
}

.prose-invert h1,
.prose-invert h2,
.prose-invert h3,
.prose-invert h4,
.prose-invert h5,
.prose-invert h6 {
  color: #111827;
}

.prose-invert p {
  color: #4b5563;
}
</style>