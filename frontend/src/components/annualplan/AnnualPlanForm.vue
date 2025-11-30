<template>
  <Dialog
    v-model="showDialog"
    :options="{
      size: '7xl',
      title: isEditing ? 'Edit Annual Audit Plan' : 'New Annual Audit Plan',
    }"
  >
    <template #body>
      <div class="flex h-[calc(100vh-180px)] overflow-hidden">
        <!-- Left Sidebar - Section Navigation -->
        <div class="w-72 bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto flex-shrink-0">
          <div class="mb-6">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Progress</span>
              <span class="text-sm text-gray-500">{{ formProgress }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${formProgress}%` }"
              ></div>
            </div>
          </div>

          <nav class="space-y-1">
            <button
              v-for="(section, key) in sections"
              :key="key"
              @click="setActiveSection(key)"
              class="w-full flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors"
              :class="[
                activeSection === key
                  ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-600'
                  : 'text-gray-600 hover:bg-gray-100'
              ]"
            >
              <component
                :is="section.icon"
                class="h-5 w-5 mr-3 flex-shrink-0"
                :class="activeSection === key ? 'text-blue-600' : 'text-gray-400'"
              />
              <span class="flex-1 text-left">{{ section.label }}</span>
              <span
                v-if="getSectionStatus(key) === 'complete'"
                class="ml-2 flex-shrink-0"
              >
                <CheckCircle2Icon class="h-5 w-5 text-green-500" />
              </span>
              <span
                v-else-if="getSectionStatus(key) === 'partial'"
                class="ml-2 flex-shrink-0"
              >
                <AlertCircleIcon class="h-5 w-5 text-yellow-500" />
              </span>
            </button>
          </nav>

          <!-- Draft Save Status -->
          <div class="mt-6 pt-4 border-t border-gray-200">
            <div class="flex items-center text-sm text-gray-500">
              <CloudIcon class="h-4 w-4 mr-2" />
              <span v-if="lastSaved">Saved {{ formatTimeAgo(lastSaved) }}</span>
              <span v-else>Not saved yet</span>
            </div>
          </div>
        </div>

        <!-- Main Content Area -->
        <div class="flex-1 overflow-y-auto p-6">
          <!-- Section 1: Basic Information -->
          <div v-show="activeSection === 'basic'" class="space-y-6">
            <SectionHeader
              title="Basic Information"
              description="Essential plan identification and classification"
              icon="file-text"
            />

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                label="Plan ID"
                v-model="formData.plan_id"
                type="text"
                placeholder="e.g., AAP-2025-001"
                :required="true"
              />
              <FormControl
                label="Plan Year"
                v-model="formData.plan_year"
                type="number"
                :placeholder="new Date().getFullYear().toString()"
                :required="true"
              />
            </div>

            <div class="grid grid-cols-3 gap-6">
              <FormControl
                label="Plan Period"
                v-model="formData.plan_period"
                type="select"
                :options="periodOptions"
                :required="true"
              />
              <FormControl
                label="Status"
                v-model="formData.status"
                type="select"
                :options="statusOptions"
              />
              <FormControl
                label="Prepared Date"
                v-model="formData.prepared_date"
                type="date"
                :required="true"
              />
            </div>

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                label="Prepared By"
                v-model="formData.prepared_by"
                type="autocomplete"
                :options="userOptions"
                placeholder="Select preparer"
                :required="true"
              />
              <FormControl
                label="Approved By"
                v-model="formData.approved_by"
                type="autocomplete"
                :options="userOptions"
                placeholder="Select approver"
              />
            </div>

            <FormControl
              label="Approved Date"
              v-model="formData.approved_date"
              type="date"
            />
          </div>

          <!-- Section 2: Plan Overview -->
          <div v-show="activeSection === 'overview'" class="space-y-6">
            <SectionHeader
              title="Plan Overview"
              description="Objectives, scope, and key assumptions for the audit plan"
              icon="target"
            />

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Plan Objectives <span class="text-red-500">*</span>
              </label>
              <p class="text-xs text-gray-500 mb-2">Define the main objectives of this annual audit plan</p>
              <TextEditor
                v-model="formData.plan_objectives"
                placeholder="Enter the key objectives for this annual audit plan..."
                :editorClass="'min-h-[150px] prose-sm'"
                :bubbleMenu="true"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Scope and Coverage <span class="text-red-500">*</span>
              </label>
              <p class="text-xs text-gray-500 mb-2">Describe the scope and coverage of planned audits</p>
              <TextEditor
                v-model="formData.scope_and_coverage"
                placeholder="Describe the scope and coverage areas..."
                :editorClass="'min-h-[150px] prose-sm'"
                :bubbleMenu="true"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Key Assumptions
              </label>
              <p class="text-xs text-gray-500 mb-2">List the key assumptions underlying this plan</p>
              <TextEditor
                v-model="formData.key_assumptions"
                placeholder="List the key assumptions for this plan..."
                :editorClass="'min-h-[120px] prose-sm'"
                :bubbleMenu="true"
              />
            </div>
          </div>

          <!-- Section 3: Resource Summary -->
          <div v-show="activeSection === 'resources'" class="space-y-6">
            <SectionHeader
              title="Resource Summary"
              description="Resource availability and utilization planning"
              icon="users"
            />

            <div class="bg-blue-50 rounded-lg p-4 mb-6">
              <h4 class="text-sm font-medium text-blue-900 mb-3">Resource Overview</h4>
              <div class="grid grid-cols-3 gap-4">
                <div class="text-center">
                  <p class="text-2xl font-bold text-blue-700">{{ formData.total_available_days || 0 }}</p>
                  <p class="text-xs text-blue-600">Available Days</p>
                </div>
                <div class="text-center">
                  <p class="text-2xl font-bold text-green-700">{{ formData.total_planned_days || 0 }}</p>
                  <p class="text-xs text-green-600">Planned Days</p>
                </div>
                <div class="text-center">
                  <p class="text-2xl font-bold" :class="utilizationColor">{{ formData.utilization_percentage || 0 }}%</p>
                  <p class="text-xs text-gray-600">Utilization</p>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-6">
              <FormControl
                label="Total Available Days"
                v-model="formData.total_available_days"
                type="number"
                placeholder="0"
              />
              <FormControl
                label="Total Planned Days"
                v-model="formData.total_planned_days"
                type="number"
                placeholder="0"
              />
              <FormControl
                label="Utilization %"
                v-model="formData.utilization_percentage"
                type="number"
                placeholder="0"
                :disabled="true"
              />
            </div>

            <!-- Resource Allocation Child Table -->
            <ChildTable
              v-model="formData.resource_allocation"
              title="Resource Allocation"
              :columns="resourceColumns"
              :fields="resourceFields"
              modalTitle="Resource"
              emptyMessage="No resources allocated yet"
              :doctype="'Annual Audit Plan Resource'"
            />
          </div>

          <!-- Section 4: Planned Audits -->
          <div v-show="activeSection === 'audits'" class="space-y-6">
            <SectionHeader
              title="Planned Audits"
              description="Schedule and plan individual audit engagements"
              icon="clipboard-list"
            />

            <!-- Planned Audits Child Table -->
            <ChildTable
              v-model="formData.planned_audits"
              title="Planned Audits"
              :columns="auditColumns"
              :fields="auditFields"
              modalTitle="Planned Audit"
              emptyMessage="No audits planned yet"
              :doctype="'Annual Audit Plan Item'"
              :required="true"
            />

            <!-- Audit Summary Stats -->
            <div v-if="formData.planned_audits.length > 0" class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-sm font-medium text-gray-900 mb-3">Audit Summary</h4>
              <div class="grid grid-cols-4 gap-4">
                <div class="text-center p-3 bg-white rounded-lg border border-gray-200">
                  <p class="text-xl font-bold text-gray-900">{{ formData.planned_audits.length }}</p>
                  <p class="text-xs text-gray-500">Total Audits</p>
                </div>
                <div class="text-center p-3 bg-white rounded-lg border border-gray-200">
                  <p class="text-xl font-bold text-red-600">{{ criticalAuditsCount }}</p>
                  <p class="text-xs text-gray-500">Critical/High</p>
                </div>
                <div class="text-center p-3 bg-white rounded-lg border border-gray-200">
                  <p class="text-xl font-bold text-blue-600">{{ totalAuditDays }}</p>
                  <p class="text-xs text-gray-500">Total Days</p>
                </div>
                <div class="text-center p-3 bg-white rounded-lg border border-gray-200">
                  <p class="text-xl font-bold text-green-600">{{ totalBudgetAllocated }}</p>
                  <p class="text-xs text-gray-500">Budget</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 5: Budget Allocation -->
          <div v-show="activeSection === 'budget'" class="space-y-6">
            <SectionHeader
              title="Budget Allocation"
              description="Plan and allocate budget across different categories"
              icon="calculator"
            />

            <!-- Budget Allocation Child Table -->
            <ChildTable
              v-model="formData.budget_allocation"
              title="Budget Items"
              :columns="budgetColumns"
              :fields="budgetFields"
              modalTitle="Budget Item"
              emptyMessage="No budget items added yet"
              :doctype="'Annual Audit Plan Budget'"
            />
          </div>

          <!-- Section 6: Risk Prioritization -->
          <div v-show="activeSection === 'risk'" class="space-y-6">
            <SectionHeader
              title="Risk-Based Prioritization"
              description="Prioritize audit areas based on risk assessment"
              icon="alert-triangle"
            />

            <!-- Risk Priority Child Table -->
            <ChildTable
              v-model="formData.risk_based_prioritization"
              title="Risk Priorities"
              :columns="riskPriorityColumns"
              :fields="riskPriorityFields"
              modalTitle="Risk Priority"
              emptyMessage="No risk priorities defined yet"
              :doctype="'Annual Audit Plan Risk Priority'"
            />
          </div>

          <!-- Section 7: Contingency & Monitoring -->
          <div v-show="activeSection === 'contingency'" class="space-y-6">
            <SectionHeader
              title="Contingency & Monitoring"
              description="Contingency planning and progress monitoring approach"
              icon="shield-check"
            />

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Contingency Plan
              </label>
              <p class="text-xs text-gray-500 mb-2">Describe contingency plans for unexpected situations</p>
              <TextEditor
                v-model="formData.contingency_plan"
                placeholder="Describe contingency plans and backup strategies..."
                :editorClass="'min-h-[150px] prose-sm'"
                :bubbleMenu="true"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Monitoring and Reporting
              </label>
              <p class="text-xs text-gray-500 mb-2">Define how progress will be monitored and reported</p>
              <TextEditor
                v-model="formData.monitoring_and_reporting"
                placeholder="Describe the monitoring and reporting approach..."
                :editorClass="'min-h-[150px] prose-sm'"
                :bubbleMenu="true"
              />
            </div>
          </div>

          <!-- Section 8: Additional Information -->
          <div v-show="activeSection === 'additional'" class="space-y-6">
            <SectionHeader
              title="Additional Information"
              description="Notes, attachments, and supplementary details"
              icon="file-check"
            />

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Notes
              </label>
              <TextEditor
                v-model="formData.notes"
                placeholder="Add any additional notes or comments..."
                :editorClass="'min-h-[150px] prose-sm'"
                :bubbleMenu="true"
              />
            </div>

            <FormControl
              label="Attachments"
              v-model="formData.attachments"
              type="file"
              placeholder="Upload supporting documents"
            />
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center space-x-2">
          <Button
            variant="subtle"
            @click="previousSection"
            :disabled="activeSection === 'basic'"
          >
            <ChevronLeftIcon class="h-4 w-4 mr-1" />
            Previous
          </Button>
          <Button
            variant="subtle"
            @click="nextSection"
            :disabled="activeSection === 'additional'"
          >
            Next
            <ChevronRightIcon class="h-4 w-4 ml-1" />
          </Button>
        </div>

        <div class="flex items-center space-x-3">
          <Button variant="subtle" @click="saveDraft">
            Save as Draft
          </Button>
          <Button variant="outline" @click="closeDialog">
            Cancel
          </Button>
          <Button variant="solid" theme="blue" @click="submitForm" :loading="saving">
            {{ isEditing ? 'Update Plan' : 'Create Plan' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import ChildTable from "@/components/Common/ChildTable.vue"
import SectionHeader from "@/components/Common/SectionHeader.vue"
import { useMultiSectionForm } from "@/composables/useMultiSectionForm"
import { Button, Dialog, FormControl, TextEditor } from "frappe-ui"
import {
	AlertCircleIcon,
	AlertTriangleIcon,
	CalculatorIcon,
	CheckCircle2Icon,
	ChevronLeftIcon,
	ChevronRightIcon,
	ClipboardListIcon,
	CloudIcon,
	FileCheck2Icon,
	FileTextIcon,
	ShieldCheckIcon,
	TargetIcon,
	UsersIcon,
} from "lucide-vue-next"
import { computed, onMounted, reactive, ref, watch } from "vue"

// Props
const props = defineProps({
	modelValue: {
		type: Boolean,
		default: false,
	},
	plan: {
		type: Object,
		default: null,
	},
})

// Emits
const emit = defineEmits(["update:modelValue", "saved", "close"])

// Dialog visibility
const showDialog = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

const isEditing = computed(() => !!props.plan?.name)
const saving = ref(false)
const lastSaved = ref(null)

// Section definitions
const sections = {
	basic: { label: "Basic Information", icon: FileTextIcon },
	overview: { label: "Plan Overview", icon: TargetIcon },
	resources: { label: "Resource Summary", icon: UsersIcon },
	audits: { label: "Planned Audits", icon: ClipboardListIcon },
	budget: { label: "Budget Allocation", icon: CalculatorIcon },
	risk: { label: "Risk Prioritization", icon: AlertTriangleIcon },
	contingency: { label: "Contingency & Monitoring", icon: ShieldCheckIcon },
	additional: { label: "Additional Information", icon: FileCheck2Icon },
}

// Section field mappings for validation
const sectionFields = {
	basic: [
		"plan_id",
		"plan_year",
		"plan_period",
		"prepared_by",
		"prepared_date",
	],
	overview: ["plan_objectives", "scope_and_coverage"],
	resources: [],
	audits: ["planned_audits"],
	budget: [],
	risk: [],
	contingency: [],
	additional: [],
}

// Use multi-section form composable
const {
	activeSection,
	formProgress,
	setActiveSection,
	getSectionStatus,
	validateForm,
	prepareFormData,
} = useMultiSectionForm(sections, sectionFields)

// Form data
const formData = reactive({
	// Basic Information
	plan_id: "",
	plan_year: new Date().getFullYear(),
	plan_period: "Annual",
	prepared_by: "",
	prepared_date: "",
	approved_by: "",
	approved_date: "",
	status: "Draft",

	// Plan Overview
	plan_objectives: "",
	scope_and_coverage: "",
	key_assumptions: "",

	// Resource Summary
	total_available_days: null,
	total_planned_days: null,
	utilization_percentage: null,
	resource_allocation: [],

	// Planned Audits
	planned_audits: [],

	// Budget Allocation
	budget_allocation: [],

	// Risk Prioritization
	risk_based_prioritization: [],

	// Contingency & Monitoring
	contingency_plan: "",
	monitoring_and_reporting: "",

	// Additional Information
	notes: "",
	attachments: "",
})

// Options
const periodOptions = [
	{ label: "Annual", value: "Annual" },
	{ label: "Semi-Annual", value: "Semi-Annual" },
	{ label: "Quarterly", value: "Quarterly" },
]

const statusOptions = [
	{ label: "Draft", value: "Draft" },
	{ label: "Submitted for Approval", value: "Submitted for Approval" },
	{ label: "Approved", value: "Approved" },
	{ label: "Rejected", value: "Rejected" },
	{ label: "Active", value: "Active" },
	{ label: "Completed", value: "Completed" },
]

const userOptions = ref([])

// Child Table Configurations

// Resource Allocation
const resourceColumns = [
	{ key: "auditor", label: "Auditor", width: "150px" },
	{ key: "role", label: "Role", width: "120px" },
	{ key: "available_days", label: "Available", width: "80px" },
	{ key: "allocated_days", label: "Allocated", width: "80px" },
	{ key: "utilization_percentage", label: "Util %", width: "80px" },
]

const resourceFields = [
	{
		key: "auditor",
		label: "Auditor",
		type: "link",
		doctype: "User",
		required: true,
	},
	{ key: "auditor_name", label: "Auditor Name", type: "text", readOnly: true },
	{
		key: "role",
		label: "Role",
		type: "select",
		required: true,
		options: [
			{ label: "Lead Auditor", value: "Lead Auditor" },
			{ label: "Senior Auditor", value: "Senior Auditor" },
			{ label: "Auditor", value: "Auditor" },
			{ label: "Trainee", value: "Trainee" },
			{ label: "Specialist", value: "Specialist" },
		],
	},
	{
		key: "available_days",
		label: "Available Days",
		type: "number",
		required: true,
	},
	{ key: "allocated_days", label: "Allocated Days", type: "number" },
	{
		key: "utilization_percentage",
		label: "Utilization %",
		type: "number",
		readOnly: true,
	},
	{ key: "skills_expertise", label: "Skills/Expertise", type: "textarea" },
	{
		key: "location",
		label: "Location",
		type: "select",
		options: [
			{ label: "Head Office", value: "Head Office" },
			{ label: "Branch 1", value: "Branch 1" },
			{ label: "Branch 2", value: "Branch 2" },
			{ label: "Remote", value: "Remote" },
		],
	},
	{ key: "cost_rate_per_day", label: "Cost Rate/Day", type: "currency" },
	{ key: "total_cost", label: "Total Cost", type: "currency", readOnly: true },
]

// Planned Audits
const auditColumns = [
	{ key: "audit_universe", label: "Audit Universe", width: "180px" },
	{ key: "audit_type", label: "Type", width: "100px" },
	{ key: "priority", label: "Priority", width: "80px", component: "Badge" },
	{ key: "planned_days", label: "Days", width: "60px" },
	{ key: "planned_start_date", label: "Start", width: "100px" },
]

const auditFields = [
	{
		key: "audit_universe",
		label: "Audit Universe",
		type: "link",
		doctype: "Audit Universe",
		required: true,
	},
	{
		key: "audit_type",
		label: "Audit Type",
		type: "select",
		required: true,
		options: [
			{ label: "Financial", value: "Financial" },
			{ label: "Operational", value: "Operational" },
			{ label: "Compliance", value: "Compliance" },
			{ label: "IT", value: "IT" },
			{ label: "Integrated", value: "Integrated" },
			{ label: "Special Investigation", value: "Special Investigation" },
			{ label: "Follow-up", value: "Follow-up" },
		],
	},
	{
		key: "priority",
		label: "Priority",
		type: "select",
		required: true,
		options: [
			{ label: "Critical", value: "Critical" },
			{ label: "High", value: "High" },
			{ label: "Medium", value: "Medium" },
			{ label: "Low", value: "Low" },
		],
	},
	{
		key: "planned_start_date",
		label: "Planned Start Date",
		type: "date",
		required: true,
	},
	{
		key: "planned_end_date",
		label: "Planned End Date",
		type: "date",
		required: true,
	},
	{
		key: "planned_days",
		label: "Planned Days",
		type: "number",
		required: true,
	},
	{
		key: "lead_auditor",
		label: "Lead Auditor",
		type: "link",
		doctype: "User",
		required: true,
	},
	{ key: "team_members", label: "Team Members", type: "textarea" },
	{ key: "objectives", label: "Objectives", type: "textarea" },
	{ key: "scope", label: "Scope", type: "textarea" },
	{
		key: "risk_assessment_reference",
		label: "Risk Assessment",
		type: "link",
		doctype: "Risk Assessment",
	},
	{ key: "budget_allocated", label: "Budget Allocated", type: "currency" },
]

// Budget Allocation
const budgetColumns = [
	{ key: "budget_category", label: "Category", width: "180px" },
	{ key: "planned_amount", label: "Planned", width: "120px" },
	{ key: "actual_amount", label: "Actual", width: "120px" },
	{ key: "variance", label: "Variance", width: "100px" },
]

const budgetFields = [
	{
		key: "budget_category",
		label: "Budget Category",
		type: "select",
		required: true,
		options: [
			{ label: "Personnel Costs", value: "Personnel Costs" },
			{ label: "Travel & Accommodation", value: "Travel & Accommodation" },
			{ label: "Training & Development", value: "Training & Development" },
			{ label: "Technology & Tools", value: "Technology & Tools" },
			{ label: "Consulting Services", value: "Consulting Services" },
			{ label: "Office Supplies", value: "Office Supplies" },
			{ label: "Miscellaneous", value: "Miscellaneous" },
			{ label: "Contingency", value: "Contingency" },
		],
	},
	{ key: "description", label: "Description", type: "textarea" },
	{
		key: "planned_amount",
		label: "Planned Amount",
		type: "currency",
		required: true,
	},
	{ key: "actual_amount", label: "Actual Amount", type: "currency" },
	{ key: "variance", label: "Variance", type: "currency", readOnly: true },
	{
		key: "variance_percentage",
		label: "Variance %",
		type: "number",
		readOnly: true,
	},
	{
		key: "budget_type",
		label: "Budget Type",
		type: "select",
		options: [
			{ label: "Fixed", value: "Fixed" },
			{ label: "Variable", value: "Variable" },
			{ label: "Contingency", value: "Contingency" },
		],
	},
	{
		key: "allocation_basis",
		label: "Allocation Basis",
		type: "select",
		options: [
			{ label: "Per Audit", value: "Per Audit" },
			{ label: "Per Day", value: "Per Day" },
			{ label: "Percentage of Total", value: "Percentage of Total" },
			{ label: "Fixed Amount", value: "Fixed Amount" },
		],
	},
	{ key: "notes", label: "Notes", type: "textarea" },
]

// Risk Priority
const riskPriorityColumns = [
	{ key: "audit_universe", label: "Audit Universe", width: "180px" },
	{
		key: "risk_rating",
		label: "Risk Rating",
		width: "100px",
		component: "Badge",
	},
	{
		key: "priority_level",
		label: "Priority",
		width: "100px",
		component: "Badge",
	},
	{ key: "planned_audit_timing", label: "Timing", width: "80px" },
]

const riskPriorityFields = [
	{
		key: "audit_universe",
		label: "Audit Universe",
		type: "link",
		doctype: "Audit Universe",
		required: true,
	},
	{
		key: "risk_rating",
		label: "Risk Rating",
		type: "select",
		required: true,
		options: [
			{ label: "Critical", value: "Critical" },
			{ label: "High", value: "High" },
			{ label: "Medium", value: "Medium" },
			{ label: "Low", value: "Low" },
		],
	},
	{ key: "risk_score", label: "Risk Score", type: "number", required: true },
	{ key: "last_assessment_date", label: "Last Assessment Date", type: "date" },
	{
		key: "audit_frequency",
		label: "Audit Frequency",
		type: "select",
		options: [
			{ label: "Quarterly", value: "Quarterly" },
			{ label: "Semi-Annual", value: "Semi-Annual" },
			{ label: "Annual", value: "Annual" },
			{ label: "Bi-Annual", value: "Bi-Annual" },
			{ label: "Tri-Annual", value: "Tri-Annual" },
			{ label: "As Needed", value: "As Needed" },
		],
	},
	{
		key: "priority_level",
		label: "Priority Level",
		type: "select",
		required: true,
		options: [
			{ label: "Critical", value: "Critical" },
			{ label: "High", value: "High" },
			{ label: "Medium", value: "Medium" },
			{ label: "Low", value: "Low" },
		],
	},
	{
		key: "justification",
		label: "Justification",
		type: "textarea",
		required: true,
	},
	{
		key: "planned_audit_timing",
		label: "Planned Timing",
		type: "select",
		options: [
			{ label: "Q1", value: "Q1" },
			{ label: "Q2", value: "Q2" },
			{ label: "Q3", value: "Q3" },
			{ label: "Q4", value: "Q4" },
			{ label: "H1", value: "H1" },
			{ label: "H2", value: "H2" },
			{ label: "As Required", value: "As Required" },
		],
	},
	{
		key: "resource_intensity",
		label: "Resource Intensity",
		type: "select",
		options: [
			{ label: "High", value: "High" },
			{ label: "Medium", value: "Medium" },
			{ label: "Low", value: "Low" },
		],
	},
]

// Computed properties
const utilizationColor = computed(() => {
	const util = formData.utilization_percentage || 0
	if (util >= 90) return "text-red-600"
	if (util >= 75) return "text-yellow-600"
	return "text-green-600"
})

const criticalAuditsCount = computed(() => {
	return formData.planned_audits.filter(
		(a) => a.priority === "Critical" || a.priority === "High",
	).length
})

const totalAuditDays = computed(() => {
	return formData.planned_audits.reduce(
		(sum, a) => sum + (a.planned_days || 0),
		0,
	)
})

const totalBudgetAllocated = computed(() => {
	const total = formData.planned_audits.reduce(
		(sum, a) => sum + (a.budget_allocated || 0),
		0,
	)
	return total.toLocaleString()
})

// Watch for utilization calculation
watch(
	[() => formData.total_available_days, () => formData.total_planned_days],
	() => {
		if (formData.total_available_days > 0) {
			formData.utilization_percentage = Math.round(
				(formData.total_planned_days / formData.total_available_days) * 100,
			)
		}
	},
)

// Navigation methods
const previousSection = () => {
	const keys = Object.keys(sections)
	const currentIndex = keys.indexOf(activeSection.value)
	if (currentIndex > 0) {
		setActiveSection(keys[currentIndex - 1])
	}
}

const nextSection = () => {
	const keys = Object.keys(sections)
	const currentIndex = keys.indexOf(activeSection.value)
	if (currentIndex < keys.length - 1) {
		setActiveSection(keys[currentIndex + 1])
	}
}

// Time formatting helper
const formatTimeAgo = (date) => {
	if (!date) return ""
	const seconds = Math.floor((new Date() - new Date(date)) / 1000)
	if (seconds < 60) return "just now"
	const minutes = Math.floor(seconds / 60)
	if (minutes < 60) return `${minutes}m ago`
	const hours = Math.floor(minutes / 60)
	if (hours < 24) return `${hours}h ago`
	const days = Math.floor(hours / 24)
	return `${days}d ago`
}

// Draft save
const saveDraft = async () => {
	try {
		lastSaved.value = new Date()
	} catch (error) {
		console.error("Failed to save draft:", error)
	}
}

// Submit form
const submitForm = async () => {
	const validation = validateForm(formData)
	if (!validation.isValid) {
		console.error("Validation errors:", validation.errors)
		return
	}

	saving.value = true
	try {
		const data = prepareFormData(formData, {
			planned_audits: "Annual Audit Plan Item",
			resource_allocation: "Annual Audit Plan Resource",
			budget_allocation: "Annual Audit Plan Budget",
			risk_based_prioritization: "Annual Audit Plan Risk Priority",
		})

		emit("saved", data)
		closeDialog()
	} catch (error) {
		console.error("Failed to save plan:", error)
	} finally {
		saving.value = false
	}
}

// Close dialog
const closeDialog = () => {
	showDialog.value = false
	emit("close")
}

// Watch for plan prop changes (editing mode)
watch(
	() => props.plan,
	(newPlan) => {
		if (newPlan) {
			Object.keys(formData).forEach((key) => {
				if (newPlan[key] !== undefined) {
					formData[key] = newPlan[key]
				}
			})
		}
	},
	{ immediate: true, deep: true },
)
</script>

<style scoped>
:deep(.ProseMirror) {
  min-height: 150px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

:deep(.ProseMirror:focus) {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
</style>
