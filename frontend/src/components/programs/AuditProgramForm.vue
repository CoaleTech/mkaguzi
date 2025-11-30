<template>
  <Dialog
    v-model="dialogVisible"
    :options="{
      title: mode === 'edit' ? 'Edit Audit Program' : 'Create Audit Program',
      size: 'full',
    }"
  >
    <template #body>
      <div class="h-[80vh] flex">
        <!-- Progress Sidebar -->
        <div class="w-64 bg-gray-50 border-r border-gray-200 flex-shrink-0 overflow-y-auto">
          <div class="p-4">
            <h4 class="text-sm font-semibold text-gray-900 mb-3">Progress</h4>
            <div class="space-y-2">
              <div
                v-for="(section, index) in sections"
                :key="section.id"
                class="flex items-center space-x-2 p-2 rounded-lg cursor-pointer transition-all"
                :class="currentSection === index ? 'bg-purple-100 border border-purple-300' : 'hover:bg-gray-100'"
                @click="goToSection(index)"
              >
                <div
                  class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold"
                  :class="getSectionStatusClass(section.id)"
                >
                  <CheckIcon v-if="isSectionComplete(section.id)" class="h-3 w-3" />
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-gray-900 truncate">{{ section.title }}</div>
                  <div class="text-xs text-gray-500 truncate">{{ section.description }}</div>
                </div>
              </div>
            </div>

            <!-- Overall Progress -->
            <div class="mt-4 p-3 bg-white rounded-lg border border-gray-200">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-medium text-gray-700">Overall Progress</span>
                <span class="text-xs font-semibold text-purple-600">{{ overallProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  class="bg-purple-600 h-1.5 rounded-full transition-all duration-500"
                  :style="{ width: `${overallProgress}%` }"
                ></div>
              </div>
            </div>

            <!-- Auto-save Status -->
            <div v-if="lastSaved" class="mt-3 text-xs text-gray-500 text-center">
              Last saved: {{ lastSaved }}
            </div>
          </div>
        </div>

        <!-- Main Form Content -->
        <div class="flex-1 overflow-y-auto">
          <div class="p-6 space-y-8">
            <!-- Section 1: Basic Information -->
            <div v-show="currentSection === 0" class="space-y-6">
              <SectionHeader
                title="Basic Information"
                description="Program identification and type"
                :sectionNumber="1"
                color="purple"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Program ID <span class="text-red-500">*</span>
                    </label>
                    <div class="flex gap-2">
                      <FormControl
                        v-model="form.program_id"
                        placeholder="e.g., FIN-2025-001"
                        class="flex-1"
                      />
                      <Button variant="outline" size="sm" @click="generateProgramId">
                        <RefreshCwIcon class="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <FormControl
                    v-model="form.program_name"
                    label="Program Name"
                    placeholder="Enter program name"
                    :required="true"
                  />

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Audit Type <span class="text-red-500">*</span>
                    </label>
                    <FormControl
                      type="select"
                      v-model="form.audit_type"
                      :options="auditTypeOptions"
                      placeholder="Select audit type"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Is Template</label>
                    <div class="flex items-center mt-2">
                      <input
                        type="checkbox"
                        v-model="form.is_template"
                        class="h-4 w-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                      />
                      <span class="ml-2 text-sm text-gray-600">Save as reusable template</span>
                    </div>
                  </div>

                  <div v-if="!form.is_template">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Engagement Reference</label>
                    <LinkField
                      v-model="form.engagement_reference"
                      doctype="Audit Engagement"
                      placeholder="Link to engagement"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 2: Program Objectives -->
            <div v-show="currentSection === 1" class="space-y-6">
              <SectionHeader
                title="Program Objectives"
                description="Define the objectives of this audit program"
                :sectionNumber="2"
                color="blue"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Program Objectives <span class="text-red-500">*</span>
                </label>
                <TextEditor
                  :content="form.program_objectives"
                  @change="form.program_objectives = $event"
                  placeholder="Enter the objectives of this audit program..."
                  :editable="true"
                  editorClass="min-h-[200px] prose-sm"
                />
              </div>
            </div>

            <!-- Section 3: Audit Procedures -->
            <div v-show="currentSection === 2" class="space-y-6">
              <SectionHeader
                title="Audit Procedures"
                description="Define the detailed audit procedures to be performed"
                :sectionNumber="3"
                color="green"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="flex items-center justify-between mb-4">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Procedures</h4>
                    <p class="text-xs text-gray-500">{{ form.program_procedures?.length || 0 }} procedures defined</p>
                  </div>
                  <Button variant="outline" size="sm" @click="addProcedure">
                    <template #prefix><PlusIcon class="h-4 w-4" /></template>
                    Add Procedure
                  </Button>
                </div>

                <div v-if="form.program_procedures?.length > 0" class="space-y-4">
                  <div
                    v-for="(procedure, index) in form.program_procedures"
                    :key="index"
                    class="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors"
                  >
                    <div class="flex items-start justify-between mb-4">
                      <div class="flex items-center gap-2">
                        <Badge variant="subtle" theme="gray">{{ index + 1 }}</Badge>
                        <span class="text-sm font-medium text-gray-900">{{ procedure.procedure_no || 'New Procedure' }}</span>
                      </div>
                      <div class="flex items-center gap-1">
                        <Button variant="ghost" size="sm" @click="editProcedure(index)">
                          <EditIcon class="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" @click="removeProcedure(index)" class="text-red-500">
                          <TrashIcon class="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <FormControl
                        v-model="procedure.procedure_no"
                        label="Procedure No"
                        placeholder="e.g., P001"
                        size="sm"
                      />
                      <FormControl
                        v-model="procedure.procedure_section"
                        label="Section"
                        placeholder="e.g., Revenue Testing"
                        size="sm"
                      />
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Type</label>
                        <FormControl
                          type="select"
                          v-model="procedure.procedure_type"
                          :options="procedureTypeOptions"
                          size="sm"
                        />
                      </div>
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Status</label>
                        <FormControl
                          type="select"
                          v-model="procedure.status"
                          :options="procedureStatusOptions"
                          size="sm"
                        />
                      </div>
                    </div>

                    <div class="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Assertion</label>
                        <FormControl
                          type="select"
                          v-model="procedure.assertion"
                          :options="assertionOptions"
                          size="sm"
                        />
                      </div>
                      <FormControl
                        v-model="procedure.sample_size"
                        type="number"
                        label="Sample Size"
                        size="sm"
                      />
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Sampling Method</label>
                        <FormControl
                          type="select"
                          v-model="procedure.sampling_method"
                          :options="samplingMethodOptions"
                          size="sm"
                        />
                      </div>
                      <FormControl
                        v-model="procedure.budgeted_hours"
                        type="number"
                        label="Budgeted Hours"
                        size="sm"
                      />
                    </div>

                    <div class="mt-4">
                      <label class="block text-xs font-medium text-gray-700 mb-1">Procedure Description</label>
                      <textarea
                        v-model="procedure.procedure_description"
                        rows="2"
                        class="w-full text-sm border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="Describe the audit procedure..."
                      ></textarea>
                    </div>

                    <div class="mt-4">
                      <label class="block text-xs font-medium text-gray-700 mb-1">Control Objective</label>
                      <textarea
                        v-model="procedure.control_objective"
                        rows="2"
                        class="w-full text-sm border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="What control does this procedure test?"
                      ></textarea>
                    </div>
                  </div>
                </div>

                <div v-else class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                  <ClipboardListIcon class="mx-auto h-12 w-12 text-gray-400" />
                  <h3 class="mt-2 text-sm font-medium text-gray-900">No procedures defined</h3>
                  <p class="mt-1 text-sm text-gray-500">Add audit procedures to this program.</p>
                  <Button variant="outline" size="sm" class="mt-4" @click="addProcedure">
                    <template #prefix><PlusIcon class="h-4 w-4" /></template>
                    Add First Procedure
                  </Button>
                </div>
              </div>
            </div>

            <!-- Section 4: Risk Areas -->
            <div v-show="currentSection === 3" class="space-y-6">
              <SectionHeader
                title="Risk Areas"
                description="Identify key risk areas addressed by this program"
                :sectionNumber="4"
                color="amber"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="flex items-center justify-between mb-4">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Risk Areas</h4>
                    <p class="text-xs text-gray-500">{{ form.risk_areas?.length || 0 }} risk areas identified</p>
                  </div>
                  <Button variant="outline" size="sm" @click="addRiskArea">
                    <template #prefix><PlusIcon class="h-4 w-4" /></template>
                    Add Risk Area
                  </Button>
                </div>

                <div v-if="form.risk_areas?.length > 0" class="space-y-4">
                  <div
                    v-for="(risk, index) in form.risk_areas"
                    :key="index"
                    class="border border-gray-200 rounded-lg p-4 hover:border-amber-300 transition-colors"
                  >
                    <div class="flex items-start justify-between mb-4">
                      <Badge
                        :variant="getRiskBadgeVariant(risk.risk_rating)"
                        size="sm"
                      >
                        {{ risk.risk_rating || 'Unrated' }}
                      </Badge>
                      <Button variant="ghost" size="sm" @click="removeRiskArea(index)" class="text-red-500">
                        <TrashIcon class="h-4 w-4" />
                      </Button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div class="md:col-span-2">
                        <label class="block text-xs font-medium text-gray-700 mb-1">Risk Description</label>
                        <textarea
                          v-model="risk.risk_description"
                          rows="2"
                          class="w-full text-sm border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="Describe the risk..."
                        ></textarea>
                      </div>
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Risk Rating</label>
                        <FormControl
                          type="select"
                          v-model="risk.risk_rating"
                          :options="riskRatingOptions"
                        />
                      </div>
                    </div>

                    <div class="mt-4">
                      <label class="block text-xs font-medium text-gray-700 mb-1">Procedures Addressing Risk</label>
                      <textarea
                        v-model="risk.procedures_addressing_risk"
                        rows="2"
                        class="w-full text-sm border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="Which procedures address this risk?"
                      ></textarea>
                    </div>
                  </div>
                </div>

                <div v-else class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                  <AlertTriangleIcon class="mx-auto h-12 w-12 text-gray-400" />
                  <h3 class="mt-2 text-sm font-medium text-gray-900">No risk areas defined</h3>
                  <p class="mt-1 text-sm text-gray-500">Add risk areas to document what this program addresses.</p>
                  <Button variant="outline" size="sm" class="mt-4" @click="addRiskArea">
                    <template #prefix><PlusIcon class="h-4 w-4" /></template>
                    Add Risk Area
                  </Button>
                </div>
              </div>
            </div>

            <!-- Section 5: Review & Submit -->
            <div v-show="currentSection === 4" class="space-y-6">
              <SectionHeader
                title="Review & Submit"
                description="Review your program and submit"
                :sectionNumber="5"
                color="purple"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h4 class="text-lg font-semibold text-gray-900 mb-4">Program Summary</h4>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                  <div class="bg-gray-50 rounded-lg p-4">
                    <p class="text-xs text-gray-500 uppercase tracking-wide">Program ID</p>
                    <p class="text-lg font-semibold text-gray-900 mt-1">{{ form.program_id || 'Not set' }}</p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-4">
                    <p class="text-xs text-gray-500 uppercase tracking-wide">Audit Type</p>
                    <p class="text-lg font-semibold text-gray-900 mt-1">{{ form.audit_type || 'Not set' }}</p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-4">
                    <p class="text-xs text-gray-500 uppercase tracking-wide">Procedures</p>
                    <p class="text-lg font-semibold text-gray-900 mt-1">{{ form.program_procedures?.length || 0 }}</p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-4">
                    <p class="text-xs text-gray-500 uppercase tracking-wide">Risk Areas</p>
                    <p class="text-lg font-semibold text-gray-900 mt-1">{{ form.risk_areas?.length || 0 }}</p>
                  </div>
                </div>

                <!-- Validation Status -->
                <div class="border-t border-gray-200 pt-4">
                  <h5 class="text-sm font-medium text-gray-900 mb-3">Validation Status</h5>
                  <div class="space-y-2">
                    <div v-for="check in validationChecks" :key="check.label" class="flex items-center">
                      <component
                        :is="check.valid ? CheckCircle2Icon : XCircleIcon"
                        :class="check.valid ? 'text-green-500' : 'text-red-500'"
                        class="h-5 w-5 mr-2"
                      />
                      <span :class="check.valid ? 'text-gray-700' : 'text-red-600'" class="text-sm">
                        {{ check.label }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-2">
          <Button
            v-if="currentSection > 0"
            variant="outline"
            @click="previousSection"
          >
            <template #prefix><ChevronLeftIcon class="h-4 w-4" /></template>
            Previous
          </Button>
        </div>

        <div class="flex items-center gap-2">
          <Button variant="outline" @click="saveDraft" :loading="saving">
            <template #prefix><SaveIcon class="h-4 w-4" /></template>
            Save Draft
          </Button>

          <Button
            v-if="currentSection < sections.length - 1"
            variant="solid"
            theme="purple"
            @click="nextSection"
          >
            Next
            <template #suffix><ChevronRightIcon class="h-4 w-4" /></template>
          </Button>

          <Button
            v-else
            variant="solid"
            theme="purple"
            @click="submitForm"
            :loading="submitting"
            :disabled="!isFormValid"
          >
            <template #prefix><CheckIcon class="h-4 w-4" /></template>
            {{ mode === 'edit' ? 'Update Program' : 'Create Program' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import SectionHeader from "@/components/Common/SectionHeader.vue"
import LinkField from "@/components/Common/fields/LinkField.vue"
import { useAuditStore } from "@/stores/audit"
import { Badge, Button, Dialog, FormControl, TextEditor } from "frappe-ui"
import {
	AlertTriangleIcon,
	CheckCircle2Icon,
	CheckIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	ClipboardListIcon,
	EditIcon,
	PlusIcon,
	RefreshCwIcon,
	SaveIcon,
	TrashIcon,
	XCircleIcon,
} from "lucide-vue-next"
import { computed, ref, watch } from "vue"

// Props
const props = defineProps({
	show: { type: Boolean, default: false },
	program: { type: Object, default: null },
	mode: { type: String, default: "create" },
})

// Emit
const emit = defineEmits(["update:show", "saved", "close"])

// Store
const auditStore = useAuditStore()

// State
const currentSection = ref(0)
const saving = ref(false)
const submitting = ref(false)
const lastSaved = ref(null)

// Computed for dialog visibility (to avoid v-model on prop)
const dialogVisible = computed({
	get: () => props.show,
	set: (value) => emit("update:show", value),
})

// Form data
const form = ref(getDefaultForm())

function getDefaultForm() {
	return {
		program_id: "",
		program_name: "",
		audit_type: "",
		is_template: false,
		engagement_reference: "",
		program_objectives: "",
		program_procedures: [],
		risk_areas: [],
	}
}

// Sections
const sections = [
	{
		id: "basic",
		title: "Basic Information",
		description: "Program ID and type",
	},
	{
		id: "objectives",
		title: "Program Objectives",
		description: "Define objectives",
	},
	{
		id: "procedures",
		title: "Audit Procedures",
		description: "Detailed procedures",
	},
	{ id: "risks", title: "Risk Areas", description: "Key risk areas" },
	{ id: "review", title: "Review & Submit", description: "Review and submit" },
]

// Options
const auditTypeOptions = [
	{ label: "Financial", value: "Financial" },
	{ label: "Operational", value: "Operational" },
	{ label: "Compliance", value: "Compliance" },
	{ label: "IT", value: "IT" },
	{ label: "Inventory", value: "Inventory" },
	{ label: "Cash", value: "Cash" },
	{ label: "Sales", value: "Sales" },
	{ label: "Procurement", value: "Procurement" },
]

const procedureTypeOptions = [
	{ label: "Inquiry", value: "Inquiry" },
	{ label: "Observation", value: "Observation" },
	{ label: "Inspection", value: "Inspection" },
	{ label: "Re-performance", value: "Re-performance" },
	{ label: "Analytical", value: "Analytical" },
	{ label: "Confirmation", value: "Confirmation" },
	{ label: "Computation", value: "Computation" },
]

const procedureStatusOptions = [
	{ label: "Not Started", value: "Not Started" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Completed", value: "Completed" },
	{ label: "Not Applicable", value: "Not Applicable" },
]

const assertionOptions = [
	{ label: "Existence", value: "Existence" },
	{ label: "Completeness", value: "Completeness" },
	{ label: "Accuracy", value: "Accuracy" },
	{ label: "Valuation", value: "Valuation" },
	{ label: "Rights", value: "Rights" },
	{ label: "Presentation", value: "Presentation" },
	{ label: "Occurrence", value: "Occurrence" },
	{ label: "Cutoff", value: "Cutoff" },
]

const samplingMethodOptions = [
	{ label: "Random", value: "Random" },
	{ label: "Systematic", value: "Systematic" },
	{ label: "Judgmental", value: "Judgmental" },
	{ label: "100%", value: "100%" },
	{ label: "Other", value: "Other" },
]

const riskRatingOptions = [
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

// Watch for program changes
watch(
	() => props.program,
	(newProgram) => {
		if (newProgram) {
			form.value = {
				...getDefaultForm(),
				...newProgram,
				program_procedures: newProgram.program_procedures || [],
				risk_areas: newProgram.risk_areas || [],
			}
		} else {
			form.value = getDefaultForm()
		}
		currentSection.value = 0
	},
	{ immediate: true },
)

watch(
	() => props.show,
	(newShow) => {
		if (!newShow) {
			currentSection.value = 0
			lastSaved.value = null
		}
	},
)

// Computed
const overallProgress = computed(() => {
	let completed = 0
	if (form.value.program_id && form.value.program_name && form.value.audit_type)
		completed += 25
	if (form.value.program_objectives) completed += 25
	if (form.value.program_procedures?.length > 0) completed += 25
	completed += 25 // Review section always counts
	return completed
})

const isFormValid = computed(() => {
	return (
		form.value.program_id &&
		form.value.program_name &&
		form.value.audit_type &&
		form.value.program_objectives &&
		form.value.program_procedures?.length > 0
	)
})

const validationChecks = computed(() => [
	{ label: "Program ID is set", valid: !!form.value.program_id },
	{ label: "Program Name is set", valid: !!form.value.program_name },
	{ label: "Audit Type is selected", valid: !!form.value.audit_type },
	{ label: "Objectives are defined", valid: !!form.value.program_objectives },
	{
		label: "At least one procedure is added",
		valid: form.value.program_procedures?.length > 0,
	},
])

// Methods
const isSectionComplete = (sectionId) => {
	switch (sectionId) {
		case "basic":
			return (
				form.value.program_id &&
				form.value.program_name &&
				form.value.audit_type
			)
		case "objectives":
			return !!form.value.program_objectives
		case "procedures":
			return form.value.program_procedures?.length > 0
		case "risks":
			return true // Optional
		case "review":
			return true
		default:
			return false
	}
}

const getSectionStatusClass = (sectionId) => {
	if (isSectionComplete(sectionId)) {
		return "bg-green-500 text-white"
	}
	return "bg-gray-300 text-gray-600"
}

const goToSection = (index) => {
	currentSection.value = index
}

const previousSection = () => {
	if (currentSection.value > 0) {
		currentSection.value--
	}
}

const nextSection = () => {
	if (currentSection.value < sections.length - 1) {
		currentSection.value++
	}
}

const generateProgramId = () => {
	const year = new Date().getFullYear()
	const type = form.value.audit_type
		? form.value.audit_type.substring(0, 3).toUpperCase()
		: "AUD"
	const random = Math.floor(Math.random() * 1000)
		.toString()
		.padStart(3, "0")
	form.value.program_id = `${type}-${year}-${random}`
}

const addProcedure = () => {
	const count = form.value.program_procedures?.length || 0
	form.value.program_procedures.push({
		procedure_no: `P${(count + 1).toString().padStart(3, "0")}`,
		procedure_section: "",
		procedure_description: "",
		procedure_type: "",
		control_objective: "",
		assertion: "",
		sample_size: 0,
		sampling_method: "",
		assigned_to: "",
		budgeted_hours: 0,
		actual_hours: 0,
		status: "Not Started",
		completion_date: "",
		working_paper_reference: "",
		findings_count: 0,
		conclusion: "",
		notes: "",
	})
}

const removeProcedure = (index) => {
	form.value.program_procedures.splice(index, 1)
}

const editProcedure = (index) => {
	// Scroll to procedure or show modal - for now just focus
	console.log("Edit procedure", index)
}

const addRiskArea = () => {
	form.value.risk_areas.push({
		risk_description: "",
		risk_rating: "",
		procedures_addressing_risk: "",
	})
}

const removeRiskArea = (index) => {
	form.value.risk_areas.splice(index, 1)
}

const getRiskBadgeVariant = (rating) => {
	const variants = {
		High: "subtle",
		Medium: "subtle",
		Low: "subtle",
	}
	return variants[rating] || "subtle"
}

const saveDraft = async () => {
	saving.value = true
	try {
		if (props.mode === "edit" && props.program?.name) {
			await auditStore.updateAuditProgram(props.program.name, form.value)
		} else {
			await auditStore.createAuditProgram(form.value)
		}
		lastSaved.value = new Date().toLocaleTimeString()
	} catch (error) {
		console.error("Error saving draft:", error)
	} finally {
		saving.value = false
	}
}

const submitForm = async () => {
	submitting.value = true
	try {
		if (props.mode === "edit" && props.program?.name) {
			await auditStore.updateAuditProgram(props.program.name, form.value)
		} else {
			await auditStore.createAuditProgram(form.value)
		}
		emit("saved")
		emit("update:show", false)
	} catch (error) {
		console.error("Error submitting form:", error)
	} finally {
		submitting.value = false
	}
}
</script>
