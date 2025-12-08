<template>
  <Dialog
    v-model="dialogVisible"
    :options="{
      title: isEditMode ? 'Edit Test Execution' : 'New Test Execution',
      size: '7xl',
    }"
  >
    <template #body-content>
      <div class="flex h-[75vh]">
        <!-- Left Sidebar: Section Navigation -->
        <div class="w-56 border-r bg-gray-50 p-4 flex flex-col">
          <div class="space-y-1 flex-1">
            <button
              v-for="(section, index) in sections"
              :key="section.id"
              @click="goToSection(index)"
              class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors"
              :class="
                currentSectionIndex === index
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              "
            >
              <component
                :is="section.icon"
                class="h-4 w-4"
                :class="getSectionStatusClass(index)"
              />
              <span class="text-sm">{{ section.title }}</span>
              <CheckCircle2
                v-if="isSectionComplete(index)"
                class="h-4 w-4 ml-auto text-green-500"
              />
            </button>
          </div>

          <!-- Progress Indicator -->
          <div class="mt-4 pt-4 border-t">
            <div class="text-xs text-gray-500 mb-2">
              Progress: {{ completedSections }}/{{ sections.length }} sections
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full transition-all"
                :style="{ width: `${progressPercentage}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Main Content Area -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <!-- Section Header -->
          <SectionHeader
            :icon="sections[currentSectionIndex]?.icon"
            :title="sections[currentSectionIndex]?.title"
            :description="sections[currentSectionIndex]?.description"
          />

          <!-- Section Content -->
          <div class="flex-1 overflow-y-auto p-6">
            <!-- Section 1: Basic Information -->
            <div v-show="currentSectionIndex === 0" class="space-y-4">
              <div class="grid grid-cols-3 gap-4">
                <FormControl
                  v-model="formData.execution_id"
                  label="Execution ID"
                  type="text"
                  placeholder="Auto-generated"
                  disabled
                />
                <FormControl
                  v-model="formData.execution_name"
                  label="Execution Name *"
                  type="text"
                  placeholder="Enter execution name"
                />
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Test Library *</label>
                  <LinkField
                    v-model="formData.test_library_reference"
                    doctype="Audit Test Library"
                    placeholder="Select test"
                  />
                </div>
              </div>

              <div class="grid grid-cols-3 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Execution Type *</label>
                  <Select
                    v-model="formData.execution_type"
                    :options="executionTypeOptions"
                    placeholder="Select type"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <Select
                    v-model="formData.priority"
                    :options="priorityOptions"
                    placeholder="Select priority"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Status *</label>
                  <Select
                    v-model="formData.status"
                    :options="statusOptions"
                    placeholder="Select status"
                  />
                </div>
              </div>
            </div>

            <!-- Section 2: Schedule -->
            <div v-show="currentSectionIndex === 1" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <FormControl
                  v-model="formData.scheduled_start_date"
                  label="Scheduled Start Date"
                  type="datetime-local"
                />
                <FormControl
                  v-model="formData.scheduled_end_date"
                  label="Scheduled End Date"
                  type="datetime-local"
                />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <FormControl
                  v-model="formData.actual_start_date"
                  label="Actual Start Date"
                  type="datetime-local"
                  disabled
                />
                <FormControl
                  v-model="formData.actual_end_date"
                  label="Actual End Date"
                  type="datetime-local"
                  disabled
                />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <FormControl
                  v-model="formData.duration_seconds"
                  label="Duration (Seconds)"
                  type="number"
                  disabled
                />
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Progress</label>
                  <div class="flex items-center gap-3">
                    <div class="flex-1 bg-gray-200 rounded-full h-3">
                      <div
                        class="h-3 rounded-full transition-all"
                        :class="getProgressColor(formData.progress_percentage)"
                        :style="{ width: `${formData.progress_percentage || 0}%` }"
                      ></div>
                    </div>
                    <span class="text-sm font-medium">{{ formData.progress_percentage || 0 }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 3: Execution Parameters -->
            <div v-show="currentSectionIndex === 2" class="space-y-4">
              <InlineChildTable
                v-model="formData.execution_parameters"
                title="Execution Parameters"
                modalTitle="Parameter"
                :columns="executionParametersColumns"
                :autoAddRow="false"
              />
            </div>

            <!-- Section 4: Results Summary -->
            <div v-show="currentSectionIndex === 3" class="space-y-4">
              <!-- Result Summary Cards -->
              <div class="grid grid-cols-4 gap-4">
                <div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div class="text-2xl font-bold text-blue-700">{{ formData.total_tests || 0 }}</div>
                  <div class="text-sm text-blue-600">Total Tests</div>
                </div>
                <div class="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div class="text-2xl font-bold text-green-700">{{ formData.passed_tests || 0 }}</div>
                  <div class="text-sm text-green-600">Passed</div>
                </div>
                <div class="p-4 bg-red-50 rounded-lg border border-red-200">
                  <div class="text-2xl font-bold text-red-700">{{ formData.failed_tests || 0 }}</div>
                  <div class="text-sm text-red-600">Failed</div>
                </div>
                <div class="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <div class="text-2xl font-bold text-yellow-700">{{ formData.warning_tests || 0 }}</div>
                  <div class="text-sm text-yellow-600">Warnings</div>
                </div>
              </div>

              <div class="grid grid-cols-3 gap-4">
                <FormControl
                  v-model="formData.total_records_processed"
                  label="Records Processed"
                  type="number"
                  disabled
                />
                <FormControl
                  v-model="formData.exceptions_found"
                  label="Exceptions Found"
                  type="number"
                  disabled
                />
                <FormControl
                  v-model="formData.critical_findings"
                  label="Critical Findings"
                  type="number"
                  disabled
                />
              </div>

              <!-- Test Results Table -->
              <div class="mt-6">
                <InlineChildTable
                  v-model="formData.test_results"
                  title="Detailed Results"
                  modalTitle="Test Result"
                  :columns="testResultsColumns"
                  :autoAddRow="false"
                />
              </div>
            </div>

            <!-- Section 5: Execution Logs -->
            <div v-show="currentSectionIndex === 4" class="space-y-4">
              <InlineChildTable
                v-model="formData.execution_logs"
                title="Execution Logs"
                modalTitle="Log Entry"
                :columns="executionLogsColumns"
                :autoAddRow="false"
              />

              <div class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">Error Details</label>
                <TextEditor
                  v-model="formData.error_details"
                  :content="formData.error_details"
                  placeholder="Error details will appear here if any errors occur..."
                  editor-class="prose-sm max-w-none min-h-[100px]"
                  :bubbleMenu="true"
                />
              </div>
            </div>

            <!-- Section 6: Performance Metrics -->
            <div v-show="currentSectionIndex === 5" class="space-y-4">
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <div class="flex items-start gap-3">
                  <Gauge class="h-5 w-5 text-blue-600 mt-0.5" />
                  <div class="text-sm text-blue-700">
                    <p class="font-medium">Performance Metrics</p>
                    <p>These metrics are automatically captured during test execution.</p>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-3 gap-4">
                <div class="p-4 bg-white rounded-lg border">
                  <div class="flex items-center gap-2 mb-2">
                    <Clock class="h-5 w-5 text-gray-400" />
                    <span class="text-sm text-gray-600">Execution Time</span>
                  </div>
                  <div class="text-2xl font-bold text-gray-900">
                    {{ formatDuration(formData.execution_time_ms) }}
                  </div>
                </div>
                <div class="p-4 bg-white rounded-lg border">
                  <div class="flex items-center gap-2 mb-2">
                    <HardDrive class="h-5 w-5 text-gray-400" />
                    <span class="text-sm text-gray-600">Memory Usage</span>
                  </div>
                  <div class="text-2xl font-bold text-gray-900">
                    {{ formData.memory_usage_mb || 0 }} MB
                  </div>
                </div>
                <div class="p-4 bg-white rounded-lg border">
                  <div class="flex items-center gap-2 mb-2">
                    <Cpu class="h-5 w-5 text-gray-400" />
                    <span class="text-sm text-gray-600">CPU Usage</span>
                  </div>
                  <div class="text-2xl font-bold text-gray-900">
                    {{ formData.cpu_usage_percent || 0 }}%
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div class="p-4 bg-white rounded-lg border">
                  <div class="flex items-center gap-2 mb-2">
                    <Zap class="h-5 w-5 text-gray-400" />
                    <span class="text-sm text-gray-600">Throughput</span>
                  </div>
                  <div class="text-2xl font-bold text-gray-900">
                    {{ formData.records_per_second || 0 }} <span class="text-sm font-normal text-gray-500">records/sec</span>
                  </div>
                </div>
                <div class="p-4 bg-white rounded-lg border">
                  <div class="flex items-center gap-2 mb-2">
                    <Database class="h-5 w-5 text-gray-400" />
                    <span class="text-sm text-gray-600">Queries Executed</span>
                  </div>
                  <div class="text-2xl font-bold text-gray-900">
                    {{ formData.queries_executed || 0 }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 7: Audit Trail & Notes -->
            <div v-show="currentSectionIndex === 6" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Created By</label>
                  <LinkField
                    v-model="formData.created_by"
                    doctype="User"
                    placeholder="Auto-filled"
                    disabled
                  />
                </div>
                <FormControl
                  v-model="formData.creation_date"
                  label="Creation Date"
                  type="datetime-local"
                  disabled
                />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Approved By</label>
                  <LinkField
                    v-model="formData.approved_by"
                    doctype="User"
                    placeholder="Select approver"
                  />
                </div>
                <FormControl
                  v-model="formData.approval_date"
                  label="Approval Date"
                  type="datetime-local"
                />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Last Modified By</label>
                  <LinkField
                    v-model="formData.last_modified_by"
                    doctype="User"
                    placeholder="Auto-filled"
                    disabled
                  />
                </div>
                <FormControl
                  v-model="formData.last_modified_date"
                  label="Last Modified Date"
                  type="datetime-local"
                  disabled
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <TextEditor
                  v-model="formData.notes"
                  :content="formData.notes"
                  placeholder="Additional notes..."
                  editor-class="prose-sm max-w-none min-h-[120px]"
                  :bubbleMenu="true"
                />
              </div>
            </div>
          </div>

          <!-- Footer Navigation -->
          <div class="border-t bg-gray-50 px-6 py-4 flex items-center justify-between">
            <Button
              variant="outline"
              @click="previousSection"
              :disabled="currentSectionIndex === 0"
            >
              <template #prefix><ChevronLeft class="h-4 w-4" /></template>
              Previous
            </Button>

            <div class="flex items-center gap-2">
              <Button variant="outline" @click="closeDialog">Cancel</Button>
              <Button
                v-if="currentSectionIndex < sections.length - 1"
                variant="solid"
                @click="nextSection"
              >
                Next
                <template #suffix><ChevronRight class="h-4 w-4" /></template>
              </Button>
              <Button
                v-else
                variant="solid"
                theme="green"
                @click="saveExecution"
                :loading="saving"
              >
                <template #prefix><Save class="h-4 w-4" /></template>
                {{ isEditMode ? 'Update Execution' : 'Create Execution' }}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import InlineChildTable from "@/components/Common/InlineChildTable.vue"
import SectionHeader from "@/components/Common/SectionHeader.vue"
import LinkField from "@/components/Common/fields/LinkField.vue"
import {
	Badge,
	Button,
	Dialog,
	FormControl,
	Select,
	TextEditor,
} from "frappe-ui"
import {
	BarChart3,
	Calendar,
	CheckCircle2,
	ChevronLeft,
	ChevronRight,
	ClipboardList,
	Clock,
	Cpu,
	Database,
	FileText,
	Gauge,
	HardDrive,
	Info,
	Plus,
	Save,
	SlidersHorizontal,
	Trash2,
	Zap,
} from "lucide-vue-next"
import { computed, reactive, ref, watch } from "vue"

const props = defineProps({
	show: { type: Boolean, default: false },
	execution: { type: Object, default: null },
})

const emit = defineEmits(["update:show", "saved"])

const dialogVisible = computed({
	get: () => props.show,
	set: (val) => emit("update:show", val),
})

const isEditMode = computed(() => !!props.execution?.name)
const saving = ref(false)
const currentSectionIndex = ref(0)

// Section definitions
const sections = [
	{
		id: "basic",
		title: "Basic Information",
		icon: Info,
		description: "Execution identification and configuration",
	},
	{
		id: "schedule",
		title: "Schedule",
		icon: Calendar,
		description: "Execution timing and progress",
	},
	{
		id: "parameters",
		title: "Parameters",
		icon: SlidersHorizontal,
		description: "Test execution parameters",
	},
	{
		id: "results",
		title: "Results",
		icon: BarChart3,
		description: "Test results and findings",
	},
	{
		id: "logs",
		title: "Logs",
		icon: FileText,
		description: "Execution logs and errors",
	},
	{
		id: "performance",
		title: "Performance",
		icon: Gauge,
		description: "Performance metrics",
	},
	{
		id: "audit",
		title: "Audit Trail",
		icon: ClipboardList,
		description: "Audit information and notes",
	},
]

// Form data
const formData = reactive({
	// Basic
	execution_id: "",
	execution_name: "",
	test_library_reference: "",
	execution_type: "Manual",
	priority: "Medium",
	status: "Pending",
	// Schedule
	scheduled_start_date: "",
	scheduled_end_date: "",
	actual_start_date: "",
	actual_end_date: "",
	duration_seconds: 0,
	progress_percentage: 0,
	// Parameters
	execution_parameters: [],
	// Results
	test_results: [],
	result_summary: true,
	total_tests: 0,
	passed_tests: 0,
	failed_tests: 0,
	warning_tests: 0,
	total_records_processed: 0,
	exceptions_found: 0,
	critical_findings: 0,
	// Logs
	execution_logs: [],
	error_details: "",
	// Performance
	performance_metrics: true,
	execution_time_ms: 0,
	memory_usage_mb: 0,
	cpu_usage_percent: 0,
	records_per_second: 0,
	queries_executed: 0,
	// Audit
	created_by: "",
	creation_date: "",
	approved_by: "",
	approval_date: "",
	last_modified_by: "",
	last_modified_date: "",
	notes: "",
})

// Options
const executionTypeOptions = [
	{ label: "Manual", value: "Manual" },
	{ label: "Scheduled", value: "Scheduled" },
	{ label: "Batch", value: "Batch" },
	{ label: "API", value: "API" },
]

const priorityOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Medium", value: "Medium" },
	{ label: "High", value: "High" },
	{ label: "Critical", value: "Critical" },
]

const statusOptions = [
	{ label: "Pending", value: "Pending" },
	{ label: "Queued", value: "Queued" },
	{ label: "Running", value: "Running" },
	{ label: "Completed", value: "Completed" },
	{ label: "Failed", value: "Failed" },
	{ label: "Cancelled", value: "Cancelled" },
	{ label: "Paused", value: "Paused" },
]

const paramTypeOptions = [
	{ label: "String", value: "String" },
	{ label: "Integer", value: "Integer" },
	{ label: "Float", value: "Float" },
	{ label: "Date", value: "Date" },
	{ label: "Boolean", value: "Boolean" },
]

const logLevelOptions = [
	{ label: "DEBUG", value: "DEBUG" },
	{ label: "INFO", value: "INFO" },
	{ label: "WARNING", value: "WARNING" },
	{ label: "ERROR", value: "ERROR" },
	{ label: "SUCCESS", value: "SUCCESS" },
]

// Column definitions for child tables
const executionParametersColumns = [
	{
		key: "parameter_name",
		label: "Parameter Name",
		fieldType: "text",
		width: "150px",
		required: true,
	},
	{
		key: "parameter_value",
		label: "Value",
		fieldType: "text",
		width: "120px",
		required: true,
	},
	{
		key: "parameter_type",
		label: "Type",
		fieldType: "select",
		width: "100px",
		options: paramTypeOptions,
		required: true,
	},
	{
		key: "description",
		label: "Description",
		fieldType: "text",
		width: "200px",
	},
]

const testResultsColumns = [
	{
		key: "test_name",
		label: "Test Name",
		fieldType: "text",
		width: "150px",
		required: true,
	},
	{
		key: "status",
		label: "Status",
		fieldType: "select",
		width: "100px",
		options: resultStatusOptions,
		required: true,
	},
	{
		key: "exception_count",
		label: "Exceptions",
		fieldType: "int",
		width: "100px",
	},
	{ key: "message", label: "Message", fieldType: "text", width: "200px" },
]

const executionLogsColumns = [
	{
		key: "timestamp",
		label: "Timestamp",
		fieldType: "datetime",
		width: "150px",
		required: true,
	},
	{
		key: "level",
		label: "Level",
		fieldType: "select",
		width: "100px",
		options: logLevelOptions,
		required: true,
	},
	{
		key: "message",
		label: "Message",
		fieldType: "text",
		width: "250px",
		required: true,
	},
]

// Watch for execution prop changes
watch(
	() => props.execution,
	(newExec) => {
		if (newExec) {
			Object.keys(formData).forEach((key) => {
				if (newExec[key] !== undefined) {
					formData[key] = newExec[key]
				}
			})
		} else {
			resetForm()
		}
	},
	{ immediate: true },
)

// Section validation
const sectionValidation = computed(() => [
	!!(
		formData.execution_name &&
		formData.test_library_reference &&
		formData.execution_type &&
		formData.status
	),
	true, // Schedule - optional
	true, // Parameters - optional
	true, // Results - read-only mostly
	true, // Logs - optional
	true, // Performance - read-only
	true, // Audit - optional
])

const completedSections = computed(
	() => sectionValidation.value.filter(Boolean).length,
)

const progressPercentage = computed(() =>
	Math.round((completedSections.value / sections.length) * 100),
)

function isSectionComplete(index) {
	return sectionValidation.value[index]
}

function getSectionStatusClass(index) {
	if (currentSectionIndex.value === index) return "text-blue-600"
	if (isSectionComplete(index)) return "text-green-500"
	return "text-gray-400"
}

function goToSection(index) {
	currentSectionIndex.value = index
}

function nextSection() {
	if (currentSectionIndex.value < sections.length - 1) {
		currentSectionIndex.value++
	}
}

function previousSection() {
	if (currentSectionIndex.value > 0) {
		currentSectionIndex.value--
	}
}

// Helper functions
function getProgressColor(pct) {
	if (pct >= 100) return "bg-green-500"
	if (pct >= 50) return "bg-blue-500"
	if (pct > 0) return "bg-yellow-500"
	return "bg-gray-300"
}

function getLogLevelTheme(level) {
	const themes = {
		INFO: "blue",
		WARNING: "orange",
		ERROR: "red",
		DEBUG: "gray",
		SUCCESS: "green",
	}
	return themes[level] || "gray"
}

function formatDuration(ms) {
	if (!ms) return "0ms"
	if (ms < 1000) return `${ms}ms`
	if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`
	return `${(ms / 60000).toFixed(2)}m`
}

// Child table management - handled by InlineChildTable component

function resetForm() {
	Object.keys(formData).forEach((key) => {
		if (Array.isArray(formData[key])) {
			formData[key] = []
		} else if (typeof formData[key] === "number") {
			formData[key] = 0
		} else if (typeof formData[key] === "boolean") {
			formData[key] = true
		} else {
			formData[key] = ""
		}
	})
	formData.execution_type = "Manual"
	formData.priority = "Medium"
	formData.status = "Pending"
	currentSectionIndex.value = 0
}

function closeDialog() {
	emit("update:show", false)
	resetForm()
}

async function saveExecution() {
	saving.value = true
	try {
		console.log("Saving execution:", formData)
		emit("saved", { ...formData })
		closeDialog()
	} catch (error) {
		console.error("Error saving execution:", error)
	} finally {
		saving.value = false
	}
}
</script>
