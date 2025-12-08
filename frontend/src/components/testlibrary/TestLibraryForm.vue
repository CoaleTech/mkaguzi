<template>
  <Dialog
    v-model="dialogVisible"
    :options="{
      title: isEditMode ? 'Edit Test' : 'Create Audit Test',
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
                  v-model="formData.test_id"
                  label="Test ID"
                  type="text"
                  placeholder="Auto-generated"
                  disabled
                />
                <FormControl
                  v-model="formData.test_name"
                  label="Test Name *"
                  type="text"
                  placeholder="Enter test name"
                />
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Test Category *</label>
                  <Select
                    v-model="formData.test_category"
                    :options="categoryOptions"
                    placeholder="Select category"
                  />
                </div>
              </div>

              <div class="grid grid-cols-3 gap-4">
                <FormControl
                  v-model="formData.sub_category"
                  label="Sub Category"
                  type="text"
                  placeholder="Enter sub-category"
                />
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Risk Area</label>
                  <LinkField
                    v-model="formData.risk_area"
                    doctype="Risk Type"
                    placeholder="Select risk area"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Audit Type</label>
                  <Select
                    v-model="formData.test_type"
                    :options="testTypeOptions"
                    placeholder="Select type"
                  />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <TextEditor
                  v-model="formData.description"
                  :content="formData.description"
                  placeholder="Describe the test..."
                  editor-class="prose-sm max-w-none min-h-[100px]"
                  :bubbleMenu="true"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Objective</label>
                <TextEditor
                  v-model="formData.objective"
                  :content="formData.objective"
                  placeholder="What is the objective of this test?"
                  editor-class="prose-sm max-w-none min-h-[100px]"
                  :bubbleMenu="true"
                />
              </div>
            </div>

            <!-- Section 2: Data Source Requirements -->
            <div v-show="currentSectionIndex === 1" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Data Source</label>
                  <LinkField
                    v-model="formData.data_source"
                    doctype="BC Data Source"
                    placeholder="Select data source"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Data DocType</label>
                  <LinkField
                    v-model="formData.data_doctype"
                    doctype="DocType"
                    placeholder="Select DocType"
                  />
                </div>
              </div>

              <!-- Required Data Fields Child Table -->
              <div class="mt-6">
                <InlineChildTable
                  v-model="formData.required_data_fields"
                  title="Required Data Fields"
                  modalTitle="Data Field"
                  :columns="requiredDataFieldsColumns"
                  :autoAddRow="false"
                />
              </div>

              <!-- Data Filters Child Table -->
              <div class="mt-6">
                <InlineChildTable
                  v-model="formData.data_filters"
                  title="Data Filters"
                  modalTitle="Data Filter"
                  :columns="dataFiltersColumns"
                  :autoAddRow="false"
                />
              </div>
            </div>

            <!-- Section 3: Test Logic -->
            <div v-show="currentSectionIndex === 2" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Test Logic Type *</label>
                  <Select
                    v-model="formData.test_logic_type"
                    :options="logicTypeOptions"
                    placeholder="Select logic type"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Built-in Function</label>
                  <LinkField
                    v-model="formData.builtin_function"
                    doctype="Built In Function"
                    placeholder="Select function"
                    :disabled="formData.test_logic_type !== 'Built-in Function'"
                  />
                </div>
              </div>

              <!-- SQL Query Editor -->
              <div v-if="formData.test_logic_type === 'SQL Query'" class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  <Database class="h-4 w-4 inline mr-1" />
                  SQL Query
                </label>
                <div class="border rounded-lg overflow-hidden">
                  <div class="bg-gray-800 px-3 py-2 text-xs text-gray-400 flex items-center justify-between">
                    <span>SQL</span>
                    <Button variant="ghost" size="sm" class="text-gray-400 hover:text-white" @click="formatSQL">
                      Format
                    </Button>
                  </div>
                  <textarea
                    v-model="formData.sql_query"
                    class="w-full h-64 p-4 font-mono text-sm bg-gray-900 text-green-400 focus:outline-none resize-none"
                    placeholder="-- Enter your SQL query here
SELECT 
    field1,
    field2,
    COUNT(*) as count
FROM `tabDocType`
WHERE condition = 'value'
GROUP BY field1, field2
HAVING COUNT(*) > 1;"
                  ></textarea>
                </div>
              </div>

              <!-- Python Script Editor -->
              <div v-if="formData.test_logic_type === 'Python Script'" class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  <FileCode class="h-4 w-4 inline mr-1" />
                  Python Script
                </label>
                <div class="border rounded-lg overflow-hidden">
                  <div class="bg-gray-800 px-3 py-2 text-xs text-gray-400 flex items-center justify-between">
                    <span>Python</span>
                    <div class="flex gap-2">
                      <Button variant="ghost" size="sm" class="text-gray-400 hover:text-white" @click="insertTemplate">
                        Insert Template
                      </Button>
                    </div>
                  </div>
                  <textarea
                    v-model="formData.python_script"
                    class="w-full h-64 p-4 font-mono text-sm bg-gray-900 text-yellow-300 focus:outline-none resize-none"
                    placeholder="# Enter your Python script here
def execute(data, params):
    '''
    Args:
        data: List of records from data source
        params: Test parameters dictionary
    Returns:
        dict: {
            'status': 'Pass'/'Fail'/'Warning',
            'exceptions': list,
            'summary': dict
        }
    '''
    exceptions = []
    
    for record in data:
        # Your test logic here
        pass
    
    return {
        'status': 'Pass' if not exceptions else 'Fail',
        'exceptions': exceptions,
        'summary': {'total': len(data), 'exceptions': len(exceptions)}
    }"
                  ></textarea>
                </div>
              </div>

              <!-- Test Parameters Child Table -->
              <div class="mt-6">
                <InlineChildTable
                  v-model="formData.test_parameters"
                  title="Test Parameters"
                  modalTitle="Parameter"
                  :columns="testParametersColumns"
                  :autoAddRow="false"
                />
              </div>
            </div>

            <!-- Section 4: Expected Results -->
            <div v-show="currentSectionIndex === 3" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Expected Result Description</label>
                <TextEditor
                  v-model="formData.expected_result"
                  :content="formData.expected_result"
                  placeholder="Describe the expected results..."
                  editor-class="prose-sm max-w-none min-h-[100px]"
                  :bubbleMenu="true"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Interpretation Guidelines</label>
                <TextEditor
                  v-model="formData.interpretation_guide"
                  :content="formData.interpretation_guide"
                  placeholder="How should results be interpreted?"
                  editor-class="prose-sm max-w-none min-h-[100px]"
                  :bubbleMenu="true"
                />
              </div>

              <!-- Expected Results Child Table -->
              <div class="mt-6">
                <InlineChildTable
                  v-model="formData.expected_results"
                  title="Expected Result Conditions"
                  modalTitle="Expected Result"
                  :columns="expectedResultsColumns"
                  :autoAddRow="false"
                />
              </div>
            </div>

            <!-- Section 5: Threshold Settings -->

            <!-- Section 5: Threshold Settings -->
            <div v-show="currentSectionIndex === 4" class="space-y-4">
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <div class="flex items-start gap-3">
                  <AlertCircle class="h-5 w-5 text-blue-600 mt-0.5" />
                  <div class="text-sm text-blue-700">
                    <p class="font-medium">Configure Thresholds</p>
                    <p>Define thresholds to automatically classify test results as Pass, Warning, or Fail based on metrics.</p>
                  </div>
                </div>
              </div>

              <!-- Threshold Settings Child Table -->
              <div class="mt-4">
                <InlineChildTable
                  v-model="formData.threshold_settings"
                  title="Threshold Configurations"
                  modalTitle="Threshold"
                  :columns="thresholdSettingsColumns"
                  :autoAddRow="false"
                />
              </div>
            </div>

            <!-- Section 6: Status & Usage -->
            <div v-show="currentSectionIndex === 5" class="space-y-4">
              <div class="grid grid-cols-3 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Status *</label>
                  <Select
                    v-model="formData.status"
                    :options="statusOptions"
                    placeholder="Select status"
                  />
                </div>
                <FormControl
                  v-model="formData.version"
                  label="Version"
                  type="text"
                  placeholder="e.g., 1.0.0"
                />
                <FormControl
                  v-model="formData.last_updated"
                  label="Last Updated"
                  type="date"
                  disabled
                />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Created By</label>
                  <LinkField
                    v-model="formData.created_by"
                    doctype="User"
                    placeholder="Select user"
                    disabled
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Reviewed By</label>
                  <LinkField
                    v-model="formData.reviewed_by"
                    doctype="User"
                    placeholder="Select reviewer"
                  />
                </div>
              </div>

              <!-- Usage Statistics (Read-only) -->
              <div class="mt-6 bg-gray-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-700 mb-4">Usage Statistics</h4>
                <div class="grid grid-cols-3 gap-4">
                  <div class="bg-white rounded-lg p-4 border">
                    <div class="text-2xl font-bold text-blue-600">{{ formData.usage_count || 0 }}</div>
                    <div class="text-sm text-gray-500">Total Executions</div>
                  </div>
                  <div class="bg-white rounded-lg p-4 border">
                    <div class="text-2xl font-bold text-green-600">{{ formData.success_rate || 0 }}%</div>
                    <div class="text-sm text-gray-500">Success Rate</div>
                  </div>
                  <div class="bg-white rounded-lg p-4 border">
                    <div class="text-2xl font-bold text-gray-600">{{ formData.last_execution || 'Never' }}</div>
                    <div class="text-sm text-gray-500">Last Execution</div>
                  </div>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <TextEditor
                  v-model="formData.notes"
                  :content="formData.notes"
                  placeholder="Additional notes..."
                  editor-class="prose-sm max-w-none min-h-[100px]"
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
                @click="saveTest"
                :loading="saving"
              >
                <template #prefix><Save class="h-4 w-4" /></template>
                {{ isEditMode ? 'Update Test' : 'Create Test' }}
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
import { Button, Dialog, FormControl, Select, TextEditor } from "frappe-ui"
import {
	Activity,
	AlertCircle,
	CheckCircle2,
	ChevronLeft,
	ChevronRight,
	Database,
	FileCode,
	Info,
	Plus,
	Save,
	SlidersHorizontal,
	Target,
	Trash2,
} from "lucide-vue-next"
import { computed, reactive, ref, watch } from "vue"

const props = defineProps({
	show: { type: Boolean, default: false },
	test: { type: Object, default: null },
})

const emit = defineEmits(["update:show", "saved"])

const dialogVisible = computed({
	get: () => props.show,
	set: (val) => emit("update:show", val),
})

const isEditMode = computed(() => !!props.test?.name)
const saving = ref(false)
const currentSectionIndex = ref(0)

// Section definitions
const sections = [
	{
		id: "basic",
		title: "Basic Information",
		icon: Info,
		description: "Test identification and classification",
	},
	{
		id: "data",
		title: "Data Source",
		icon: Database,
		description: "Define data requirements and filters",
	},
	{
		id: "logic",
		title: "Test Logic",
		icon: FileCode,
		description: "Configure SQL query or Python script",
	},
	{
		id: "results",
		title: "Expected Results",
		icon: Target,
		description: "Define expected outcomes and interpretations",
	},
	{
		id: "thresholds",
		title: "Thresholds",
		icon: SlidersHorizontal,
		description: "Set warning and critical thresholds",
	},
	{
		id: "status",
		title: "Status & Usage",
		icon: Activity,
		description: "Status, versioning, and usage tracking",
	},
]

// Form data
const formData = reactive({
	// Basic Info
	test_id: "",
	test_name: "",
	test_category: "",
	sub_category: "",
	test_type: "",
	risk_area: "",
	description: "",
	objective: "",
	// Data Source
	data_source: "",
	data_doctype: "",
	required_data_fields: [],
	data_filters: [],
	// Test Logic
	test_logic_type: "",
	sql_query: "",
	python_script: "",
	builtin_function: "",
	test_parameters: [],
	// Expected Results
	expected_result: "",
	interpretation_guide: "",
	expected_results: [],
	// Thresholds
	threshold_settings: [],
	// Status
	status: "Active",
	version: "1.0.0",
	last_updated: "",
	created_by: "",
	reviewed_by: "",
	usage_count: 0,
	success_rate: 0,
	last_execution: "",
	notes: "",
})

// Options
const categoryOptions = [
	{ label: "Duplicate Detection", value: "Duplicate Detection" },
	{ label: "Outlier Analysis", value: "Outlier Analysis" },
	{ label: "Trend Analysis", value: "Trend Analysis" },
	{ label: "Ratio Analysis", value: "Ratio Analysis" },
	{ label: "Completeness Check", value: "Completeness Check" },
	{ label: "Validity Check", value: "Validity Check" },
	{ label: "Accuracy Check", value: "Accuracy Check" },
	{ label: "Timeliness Check", value: "Timeliness Check" },
	{ label: "Consistency Check", value: "Consistency Check" },
	{ label: "Custom Analysis", value: "Custom Analysis" },
]

const testTypeOptions = [
	{ label: "Substantive", value: "Substantive" },
	{ label: "Controls", value: "Controls" },
	{ label: "Analytical", value: "Analytical" },
	{ label: "Compliance", value: "Compliance" },
]

const logicTypeOptions = [
	{ label: "SQL Query", value: "SQL Query" },
	{ label: "Python Script", value: "Python Script" },
	{ label: "Built-in Function", value: "Built-in Function" },
]

const statusOptions = [
	{ label: "Active", value: "Active" },
	{ label: "Inactive", value: "Inactive" },
	{ label: "Under Review", value: "Under Review" },
]

const fieldTypeOptions = [
	{ label: "Data", value: "Data" },
	{ label: "Int", value: "Int" },
	{ label: "Float", value: "Float" },
	{ label: "Currency", value: "Currency" },
	{ label: "Date", value: "Date" },
	{ label: "Datetime", value: "Datetime" },
	{ label: "Link", value: "Link" },
	{ label: "Select", value: "Select" },
]

const operatorOptions = [
	{ label: "Equals (=)", value: "=" },
	{ label: "Not Equals (!=)", value: "!=" },
	{ label: "Greater Than (>)", value: ">" },
	{ label: "Less Than (<)", value: "<" },
	{ label: "Like", value: "like" },
	{ label: "In", value: "in" },
	{ label: "Between", value: "between" },
]

const parameterTypeOptions = [
	{ label: "String", value: "String" },
	{ label: "Integer", value: "Integer" },
	{ label: "Float", value: "Float" },
	{ label: "Date", value: "Date" },
	{ label: "Boolean", value: "Boolean" },
	{ label: "List", value: "List" },
]

const resultStatusOptions = [
	{ label: "Pass", value: "Pass" },
	{ label: "Fail", value: "Fail" },
	{ label: "Warning", value: "Warning" },
]

const severityOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Medium", value: "Medium" },
	{ label: "High", value: "High" },
	{ label: "Critical", value: "Critical" },
]

const thresholdOperatorOptions = [
	{ label: "Greater Than (>)", value: ">" },
	{ label: "Greater Than or Equal (>=)", value: ">=" },
	{ label: "Less Than (<)", value: "<" },
	{ label: "Less Than or Equal (<=)", value: "<=" },
	{ label: "Equals (=)", value: "=" },
	{ label: "Not Equals (!=)", value: "!=" },
]

// InlineChildTable Column Definitions
const requiredDataFieldsColumns = [
	{
		key: "field_name",
		label: "Field Name",
		fieldType: "text",
		width: "150px",
		required: true,
	},
	{
		key: "field_type",
		label: "Field Type",
		fieldType: "select",
		width: "120px",
		options: [
			{ label: "Data", value: "Data" },
			{ label: "Int", value: "Int" },
			{ label: "Float", value: "Float" },
			{ label: "Currency", value: "Currency" },
			{ label: "Date", value: "Date" },
			{ label: "Datetime", value: "Datetime" },
			{ label: "Link", value: "Link" },
			{ label: "Select", value: "Select" },
		],
	},
	{ key: "is_required", label: "Required", fieldType: "check", width: "80px" },
	{
		key: "description",
		label: "Description",
		fieldType: "text",
		width: "200px",
	},
]

const dataFiltersColumns = [
	{
		key: "filter_field",
		label: "Filter Field",
		fieldType: "text",
		width: "150px",
		required: true,
	},
	{
		key: "operator",
		label: "Operator",
		fieldType: "select",
		width: "120px",
		options: [
			{ label: "Equals (=)", value: "=" },
			{ label: "Not Equals (!=)", value: "!=" },
			{ label: "Greater Than (>)", value: ">" },
			{ label: "Less Than (<)", value: "<" },
			{ label: "Like", value: "like" },
			{ label: "In", value: "in" },
			{ label: "Between", value: "between" },
		],
	},
	{
		key: "default_value",
		label: "Default Value",
		fieldType: "text",
		width: "150px",
	},
	{ key: "is_dynamic", label: "Dynamic", fieldType: "check", width: "80px" },
]

const testParametersColumns = [
	{
		key: "parameter_name",
		label: "Parameter Name",
		fieldType: "text",
		width: "150px",
		required: true,
	},
	{
		key: "parameter_type",
		label: "Type",
		fieldType: "select",
		width: "100px",
		options: [
			{ label: "String", value: "String" },
			{ label: "Integer", value: "Integer" },
			{ label: "Float", value: "Float" },
			{ label: "Date", value: "Date" },
			{ label: "Boolean", value: "Boolean" },
			{ label: "List", value: "List" },
		],
	},
	{
		key: "default_value",
		label: "Default Value",
		fieldType: "text",
		width: "150px",
	},
	{
		key: "description",
		label: "Description",
		fieldType: "text",
		width: "200px",
	},
]

const expectedResultsColumns = [
	{
		key: "condition",
		label: "Condition",
		fieldType: "text",
		width: "200px",
		required: true,
	},
	{
		key: "result_status",
		label: "Result Status",
		fieldType: "select",
		width: "100px",
		options: [
			{ label: "Pass", value: "Pass" },
			{ label: "Fail", value: "Fail" },
			{ label: "Warning", value: "Warning" },
		],
	},
	{
		key: "severity",
		label: "Severity",
		fieldType: "select",
		width: "100px",
		options: [
			{ label: "Low", value: "Low" },
			{ label: "Medium", value: "Medium" },
			{ label: "High", value: "High" },
			{ label: "Critical", value: "Critical" },
		],
	},
	{
		key: "action_required",
		label: "Action Required",
		fieldType: "text",
		width: "180px",
	},
]

const thresholdSettingsColumns = [
	{
		key: "metric_name",
		label: "Metric",
		fieldType: "text",
		width: "150px",
		required: true,
	},
	{
		key: "operator",
		label: "Operator",
		fieldType: "select",
		width: "120px",
		options: [
			{ label: "Greater Than (>)", value: ">" },
			{ label: "Greater Than or Equal (>=)", value: ">=" },
			{ label: "Less Than (<)", value: "<" },
			{ label: "Less Than or Equal (<=)", value: "<=" },
			{ label: "Equals (=)", value: "=" },
			{ label: "Not Equals (!=)", value: "!=" },
		],
	},
	{
		key: "warning_threshold",
		label: "Warning",
		fieldType: "float",
		width: "100px",
	},
	{
		key: "critical_threshold",
		label: "Critical",
		fieldType: "float",
		width: "100px",
	},
	{
		key: "description",
		label: "Description",
		fieldType: "text",
		width: "180px",
	},
]

// Watch for test prop changes
watch(
	() => props.test,
	(newTest) => {
		if (newTest) {
			Object.keys(formData).forEach((key) => {
				if (newTest[key] !== undefined) {
					formData[key] = newTest[key]
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
	!!(formData.test_name && formData.test_category), // Basic Info
	true, // Data Source - optional
	!!formData.test_logic_type, // Test Logic
	true, // Expected Results - optional
	true, // Thresholds - optional
	!!formData.status, // Status
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

// Child table management
function addRequiredField() {
	formData.required_data_fields.push({
		field_name: "",
		field_type: "Data",
		is_required: true,
		description: "",
	})
}

function removeRequiredField(index) {
	formData.required_data_fields.splice(index, 1)
}

function addDataFilter() {
	formData.data_filters.push({
		filter_field: "",
		operator: "=",
		default_value: "",
		is_dynamic: false,
	})
}

function removeDataFilter(index) {
	formData.data_filters.splice(index, 1)
}

function addTestParameter() {
	formData.test_parameters.push({
		parameter_name: "",
		parameter_type: "String",
		default_value: "",
		description: "",
	})
}

function removeTestParameter(index) {
	formData.test_parameters.splice(index, 1)
}

function addExpectedResult() {
	formData.expected_results.push({
		condition: "",
		result_status: "Pass",
		severity: "Low",
		action_required: "",
	})
}

function removeExpectedResult(index) {
	formData.expected_results.splice(index, 1)
}

function addThreshold() {
	formData.threshold_settings.push({
		metric_name: "",
		operator: ">",
		warning_threshold: null,
		critical_threshold: null,
		description: "",
	})
}

function removeThreshold(index) {
	formData.threshold_settings.splice(index, 1)
}

// Helper functions
function formatSQL() {
	// Basic SQL formatting
	if (formData.sql_query) {
		formData.sql_query = formData.sql_query
			.replace(/\bSELECT\b/gi, "\nSELECT")
			.replace(/\bFROM\b/gi, "\nFROM")
			.replace(/\bWHERE\b/gi, "\nWHERE")
			.replace(/\bAND\b/gi, "\n  AND")
			.replace(/\bOR\b/gi, "\n  OR")
			.replace(/\bGROUP BY\b/gi, "\nGROUP BY")
			.replace(/\bORDER BY\b/gi, "\nORDER BY")
			.replace(/\bHAVING\b/gi, "\nHAVING")
			.replace(/\bLEFT JOIN\b/gi, "\nLEFT JOIN")
			.replace(/\bRIGHT JOIN\b/gi, "\nRIGHT JOIN")
			.replace(/\bINNER JOIN\b/gi, "\nINNER JOIN")
			.trim()
	}
}

function insertTemplate() {
	formData.python_script = `def execute(data, params):
    '''
    Execute the audit test logic.
    
    Args:
        data: List of records from data source
        params: Test parameters dictionary
        
    Returns:
        dict: {
            'status': 'Pass' | 'Fail' | 'Warning',
            'exceptions': list of exception records,
            'summary': summary statistics dict
        }
    '''
    exceptions = []
    summary = {
        'total_records': len(data),
        'exceptions_found': 0,
        'pass_rate': 100.0
    }
    
    for record in data:
        # Add your test logic here
        # Example: Check for specific conditions
        if some_condition(record):
            exceptions.append({
                'record': record,
                'reason': 'Description of exception'
            })
    
    summary['exceptions_found'] = len(exceptions)
    summary['pass_rate'] = round((1 - len(exceptions) / len(data)) * 100, 2) if data else 100
    
    return {
        'status': 'Pass' if not exceptions else 'Fail',
        'exceptions': exceptions,
        'summary': summary
    }

def some_condition(record):
    '''Helper function to check condition'''
    # Implement your condition logic
    return False
`
}

function resetForm() {
	Object.keys(formData).forEach((key) => {
		if (Array.isArray(formData[key])) {
			formData[key] = []
		} else if (typeof formData[key] === "number") {
			formData[key] = 0
		} else {
			formData[key] = ""
		}
	})
	formData.status = "Active"
	formData.version = "1.0.0"
	currentSectionIndex.value = 0
}

function closeDialog() {
	emit("update:show", false)
	resetForm()
}

async function saveTest() {
	saving.value = true
	try {
		// Save logic would go here
		console.log("Saving test:", formData)
		emit("saved", { ...formData })
		closeDialog()
	} catch (error) {
		console.error("Error saving test:", error)
	} finally {
		saving.value = false
	}
}
</script>
