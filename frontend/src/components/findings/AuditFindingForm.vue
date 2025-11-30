<template>
  <Dialog
    v-model="showDialog"
    :options="{
      size: '7xl',
      title: isEditing ? 'Edit Audit Finding' : 'New Audit Finding',
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
                <CheckCircleIcon class="h-5 w-5 text-green-500" />
              </span>
              <span
                v-else-if="getSectionStatus(key) === 'partial'"
                class="ml-2 flex-shrink-0"
              >
                <ExclamationCircleIcon class="h-5 w-5 text-yellow-500" />
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
              description="Essential finding identification and classification details"
              :icon="DocumentTextIcon"
            />

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                label="Finding ID"
                v-model="formData.finding_id"
                type="text"
                placeholder="e.g., FND-2024-001"
                :required="true"
              />
              <FormControl
                label="Engagement Reference"
                v-model="formData.engagement_reference"
                type="autocomplete"
                :options="engagementOptions"
                placeholder="Select related engagement"
                :required="true"
              />
            </div>

            <FormControl
              label="Finding Title"
              v-model="formData.finding_title"
              type="text"
              placeholder="Enter a descriptive finding title"
              :required="true"
            />

            <div class="grid grid-cols-3 gap-6">
              <FormControl
                label="Finding Category"
                v-model="formData.finding_category"
                type="select"
                :options="categoryOptions"
                :required="true"
              />
              <FormControl
                label="Risk Rating"
                v-model="formData.risk_rating"
                type="select"
                :options="riskRatingOptions"
              />
              <FormControl
                label="Business Impact Rating"
                v-model="formData.business_impact_rating"
                type="select"
                :options="impactOptions"
              />
            </div>

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                label="Date Identified"
                v-model="formData.date_identified"
                type="date"
              />
              <FormControl
                label="Source Document"
                v-model="formData.source_document"
                type="text"
                placeholder="Reference to source workpaper"
              />
            </div>

            <!-- Affected Locations - Simple child table -->
            <div class="mt-6">
              <InlineChildTable
                v-model="formData.affected_locations"
                title="Affected Locations"
                :columns="affectedLocationColumns"
                addButtonLabel="Add Location"
              />
            </div>
          </div>

          <!-- Section 2: Finding Details -->
          <div v-show="activeSection === 'details'" class="space-y-6">
            <SectionHeader
              title="Finding Details"
              description="Document the condition, criteria, cause, and effect of the finding"
              :icon="ClipboardDocumentListIcon"
            />

            <div class="space-y-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Condition <span class="text-red-500">*</span>
                </label>
                <p class="text-xs text-gray-500 mb-2">What is the actual situation or state observed?</p>
                <TextEditor
                  v-model="formData.condition"
                  placeholder="Describe the current condition or situation found during the audit..."
                  :editorClass="'min-h-[150px] prose-sm'"
                  :bubbleMenu="true"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Criteria <span class="text-red-500">*</span>
                </label>
                <p class="text-xs text-gray-500 mb-2">What should be the expected state or standard?</p>
                <TextEditor
                  v-model="formData.criteria"
                  placeholder="Describe the standard, policy, or expectation that should be met..."
                  :editorClass="'min-h-[150px] prose-sm'"
                  :bubbleMenu="true"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Cause
                </label>
                <p class="text-xs text-gray-500 mb-2">Why did the condition occur?</p>
                <TextEditor
                  v-model="formData.cause"
                  placeholder="Describe the root cause or reason for the gap between condition and criteria..."
                  :editorClass="'min-h-[150px] prose-sm'"
                  :bubbleMenu="true"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Effect
                </label>
                <p class="text-xs text-gray-500 mb-2">What is the impact or consequence?</p>
                <TextEditor
                  v-model="formData.effect"
                  placeholder="Describe the actual or potential impact of this finding..."
                  :editorClass="'min-h-[150px] prose-sm'"
                  :bubbleMenu="true"
                />
              </div>
            </div>
          </div>

          <!-- Section 3: Evidence & Recommendation -->
          <div v-show="activeSection === 'evidence'" class="space-y-6">
            <SectionHeader
              title="Evidence & Recommendation"
              description="Supporting evidence and proposed corrective actions"
              :icon="DocumentMagnifyingGlassIcon"
            />

            <!-- Evidence Child Table -->
            <ChildTable
              v-model="formData.evidence"
              title="Supporting Evidence"
              :columns="evidenceColumns"
              :fields="evidenceFields"
              modalTitle="Evidence"
              emptyMessage="No evidence documented yet"
              :doctype="'Finding Evidence'"
            />

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                label="Sample Size Tested"
                v-model="formData.sample_size"
                type="number"
                placeholder="Number of items tested"
              />
              <FormControl
                label="Exceptions Found"
                v-model="formData.exceptions_found"
                type="number"
                placeholder="Number of exceptions identified"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Recommendation <span class="text-red-500">*</span>
              </label>
              <TextEditor
                v-model="formData.recommendation"
                placeholder="Provide specific, actionable recommendations to address the finding..."
                :editorClass="'min-h-[150px] prose-sm'"
                :bubbleMenu="true"
              />
            </div>
          </div>

          <!-- Section 4: Management Response -->
          <div v-show="activeSection === 'response'" class="space-y-6">
            <SectionHeader
              title="Management Response"
              description="Management's agreement and response to the finding"
              :icon="ChatBubbleLeftRightIcon"
            />

            <div class="grid grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Management Agrees</label>
                <div class="flex items-center space-x-4 mt-2">
                  <label class="inline-flex items-center">
                    <input
                      type="radio"
                      v-model="formData.management_agrees"
                      :value="1"
                      class="form-radio h-4 w-4 text-blue-600"
                    />
                    <span class="ml-2 text-sm text-gray-700">Yes</span>
                  </label>
                  <label class="inline-flex items-center">
                    <input
                      type="radio"
                      v-model="formData.management_agrees"
                      :value="0"
                      class="form-radio h-4 w-4 text-blue-600"
                    />
                    <span class="ml-2 text-sm text-gray-700">No</span>
                  </label>
                </div>
              </div>
              <FormControl
                label="Response Date"
                v-model="formData.response_date"
                type="date"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Management Comments
              </label>
              <TextEditor
                v-model="formData.management_comments"
                placeholder="Enter management's response and comments..."
                :editorClass="'min-h-[150px] prose-sm'"
                :bubbleMenu="true"
              />
            </div>

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                label="Responding Manager"
                v-model="formData.management_response_by"
                type="autocomplete"
                :options="userOptions"
                placeholder="Select responding manager"
              />
              <FormControl
                label="Response Received On"
                v-model="formData.management_response_date"
                type="date"
              />
            </div>
          </div>

          <!-- Section 5: Corrective Action Plan -->
          <div v-show="activeSection === 'action'" class="space-y-6">
            <SectionHeader
              title="Corrective Action Plan"
              description="Planned actions to address and resolve the finding"
              :icon="ClipboardDocumentCheckIcon"
            />

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Action Plan Description
              </label>
              <TextEditor
                v-model="formData.action_plan_description"
                placeholder="Describe the corrective action plan in detail..."
                :editorClass="'min-h-[150px] prose-sm'"
                :bubbleMenu="true"
              />
            </div>

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                label="Responsible Person"
                v-model="formData.responsible_person"
                type="autocomplete"
                :options="userOptions"
                placeholder="Select person responsible for implementation"
              />
              <FormControl
                label="Target Completion Date"
                v-model="formData.target_date"
                type="date"
              />
            </div>

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                label="Revised Target Date"
                v-model="formData.revised_target_date"
                type="date"
              />
              <FormControl
                label="Priority"
                v-model="formData.priority"
                type="select"
                :options="priorityOptions"
              />
            </div>

            <!-- Action Milestones Child Table -->
            <ChildTable
              v-model="formData.milestones"
              title="Action Milestones"
              :columns="milestoneColumns"
              :fields="milestoneFields"
              modalTitle="Milestone"
              emptyMessage="No milestones defined yet"
              :doctype="'Finding Action Milestone'"
            />
          </div>

          <!-- Section 6: Follow-up & Status -->
          <div v-show="activeSection === 'followup'" class="space-y-6">
            <SectionHeader
              title="Follow-up & Status"
              description="Track finding status and follow-up activities"
              :icon="ArrowPathIcon"
            />

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                label="Finding Status"
                v-model="formData.finding_status"
                type="select"
                :options="statusOptions"
                :required="true"
              />
              <FormControl
                label="Status Date"
                v-model="formData.status_date"
                type="date"
              />
            </div>

            <!-- Status History - Read-only display -->
            <ChildTable
              v-model="formData.status_history"
              title="Status History"
              :columns="statusHistoryColumns"
              :fields="statusHistoryFields"
              modalTitle="Status Change"
              emptyMessage="No status changes recorded"
              :doctype="'Finding Status Change'"
            />

            <div class="border-t border-gray-200 pt-6">
              <h4 class="text-sm font-medium text-gray-900 mb-4">Follow-up Settings</h4>
              <div class="grid grid-cols-3 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Follow-up Required</label>
                  <div class="flex items-center space-x-4 mt-2">
                    <label class="inline-flex items-center">
                      <input
                        type="radio"
                        v-model="formData.follow_up_required"
                        :value="1"
                        class="form-radio h-4 w-4 text-blue-600"
                      />
                      <span class="ml-2 text-sm text-gray-700">Yes</span>
                    </label>
                    <label class="inline-flex items-center">
                      <input
                        type="radio"
                        v-model="formData.follow_up_required"
                        :value="0"
                        class="form-radio h-4 w-4 text-blue-600"
                      />
                      <span class="ml-2 text-sm text-gray-700">No</span>
                    </label>
                  </div>
                </div>
                <FormControl
                  label="Follow-up Frequency"
                  v-model="formData.follow_up_frequency"
                  type="select"
                  :options="frequencyOptions"
                  :disabled="!formData.follow_up_required"
                />
                <FormControl
                  label="Next Follow-up Date"
                  v-model="formData.next_follow_up_date"
                  type="date"
                  :disabled="!formData.follow_up_required"
                />
              </div>
            </div>

            <!-- Follow-up History -->
            <ChildTable
              v-model="formData.follow_up_history"
              title="Follow-up History"
              :columns="followUpHistoryColumns"
              :fields="followUpHistoryFields"
              modalTitle="Follow-up Activity"
              emptyMessage="No follow-up activities recorded"
              :doctype="'Finding Follow-up Activity'"
            />
          </div>

          <!-- Section 7: Verification -->
          <div v-show="activeSection === 'verification'" class="space-y-6">
            <SectionHeader
              title="Verification"
              description="Verification of corrective action implementation"
              :icon="ShieldCheckIcon"
            />

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                label="Verification Date"
                v-model="formData.verification_date"
                type="date"
              />
              <FormControl
                label="Verified By"
                v-model="formData.verified_by"
                type="autocomplete"
                :options="userOptions"
                placeholder="Select verifier"
              />
            </div>

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                label="Verification Method"
                v-model="formData.verification_method"
                type="select"
                :options="verificationMethodOptions"
              />
              <FormControl
                label="Verification Status"
                v-model="formData.verification_status"
                type="select"
                :options="verificationStatusOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Verification Results
              </label>
              <TextEditor
                v-model="formData.verification_results"
                placeholder="Document the results of the verification testing..."
                :editorClass="'min-h-[150px] prose-sm'"
                :bubbleMenu="true"
              />
            </div>
          </div>

          <!-- Section 8: Closure & Reporting -->
          <div v-show="activeSection === 'closure'" class="space-y-6">
            <SectionHeader
              title="Closure & Reporting"
              description="Finding closure details and reporting preferences"
              :icon="DocumentCheckIcon"
            />

            <div class="bg-gray-50 rounded-lg p-4 mb-6">
              <h4 class="text-sm font-medium text-gray-900 mb-4">Closure Information</h4>
              <div class="grid grid-cols-2 gap-6">
                <FormControl
                  label="Closure Date"
                  v-model="formData.closure_date"
                  type="date"
                />
                <FormControl
                  label="Closed By"
                  v-model="formData.closed_by"
                  type="autocomplete"
                  :options="userOptions"
                  placeholder="Select person closing the finding"
                />
              </div>

              <div class="grid grid-cols-2 gap-6 mt-4">
                <FormControl
                  label="Closure Reason"
                  v-model="formData.closure_reason"
                  type="select"
                  :options="closureReasonOptions"
                />
                <FormControl
                  label="Final Disposition"
                  v-model="formData.final_disposition"
                  type="select"
                  :options="dispositionOptions"
                />
              </div>

              <div class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Closure Notes
                </label>
                <TextEditor
                  v-model="formData.closure_notes"
                  placeholder="Document any final notes or comments regarding the closure..."
                  :editorClass="'min-h-[100px] prose-sm'"
                  :bubbleMenu="true"
                />
              </div>
            </div>

            <!-- Reporting Options -->
            <div class="bg-blue-50 rounded-lg p-4">
              <h4 class="text-sm font-medium text-gray-900 mb-4">Reporting Options</h4>
              <div class="grid grid-cols-2 gap-4">
                <label class="inline-flex items-center">
                  <input
                    type="checkbox"
                    v-model="formData.include_in_report"
                    class="form-checkbox h-4 w-4 text-blue-600 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700">Include in Final Report</span>
                </label>
                <label class="inline-flex items-center">
                  <input
                    type="checkbox"
                    v-model="formData.reported_to_management"
                    class="form-checkbox h-4 w-4 text-blue-600 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700">Reported to Management</span>
                </label>
                <label class="inline-flex items-center">
                  <input
                    type="checkbox"
                    v-model="formData.reported_to_audit_committee"
                    class="form-checkbox h-4 w-4 text-blue-600 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700">Reported to Audit Committee</span>
                </label>
                <label class="inline-flex items-center">
                  <input
                    type="checkbox"
                    v-model="formData.reported_to_board"
                    class="form-checkbox h-4 w-4 text-blue-600 rounded"
                  />
                  <span class="ml-2 text-sm text-gray-700">Reported to Board</span>
                </label>
              </div>

              <div class="mt-4">
                <FormControl
                  label="Report Reference"
                  v-model="formData.report_reference"
                  type="text"
                  placeholder="Reference to the report containing this finding"
                />
              </div>
            </div>

            <!-- Related Findings -->
            <div class="mt-6">
              <ChildTable
                v-model="formData.related_findings"
                title="Related Findings"
                :columns="relatedFindingColumns"
                :fields="relatedFindingFields"
                modalTitle="Related Finding"
                emptyMessage="No related findings linked"
                :doctype="'Finding Related Finding'"
              />
            </div>

            <!-- Repeat Finding Information -->
            <div class="bg-yellow-50 rounded-lg p-4 mt-6">
              <h4 class="text-sm font-medium text-gray-900 mb-4">Repeat Finding Information</h4>
              <div class="grid grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Repeat Finding</label>
                  <div class="flex items-center space-x-4 mt-2">
                    <label class="inline-flex items-center">
                      <input
                        type="radio"
                        v-model="formData.repeat_finding"
                        :value="1"
                        class="form-radio h-4 w-4 text-yellow-600"
                      />
                      <span class="ml-2 text-sm text-gray-700">Yes</span>
                    </label>
                    <label class="inline-flex items-center">
                      <input
                        type="radio"
                        v-model="formData.repeat_finding"
                        :value="0"
                        class="form-radio h-4 w-4 text-yellow-600"
                      />
                      <span class="ml-2 text-sm text-gray-700">No</span>
                    </label>
                  </div>
                </div>
                <FormControl
                  v-if="formData.repeat_finding"
                  label="Previous Finding Reference"
                  v-model="formData.previous_finding_reference"
                  type="autocomplete"
                  :options="findingOptions"
                  placeholder="Link to previous finding"
                />
              </div>
            </div>
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
            :disabled="activeSection === 'closure'"
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
            {{ isEditing ? 'Update Finding' : 'Create Finding' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import ChildTable from "@/components/Common/ChildTable.vue"
import InlineChildTable from "@/components/Common/InlineChildTable.vue"
import SectionHeader from "@/components/Common/SectionHeader.vue"
import { useMultiSectionForm } from "@/composables/useMultiSectionForm"
import { Button, Dialog, FormControl, TextEditor } from "frappe-ui"
import {
	RefreshCwIcon as ArrowPathIcon,
	MessageCircleIcon as ChatBubbleLeftRightIcon,
	CheckCircle2Icon as CheckCircleIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	ClipboardCheckIcon as ClipboardDocumentCheckIcon,
	ClipboardListIcon as ClipboardDocumentListIcon,
	CloudIcon,
	FileCheck2Icon as DocumentCheckIcon,
	SearchIcon as DocumentMagnifyingGlassIcon,
	FileTextIcon as DocumentTextIcon,
	AlertCircleIcon as ExclamationCircleIcon,
	PlusIcon,
	ShieldCheckIcon,
} from "lucide-vue-next"
import { computed, onMounted, reactive, ref, watch } from "vue"

// Props
const props = defineProps({
	modelValue: {
		type: Boolean,
		default: false,
	},
	finding: {
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

const isEditing = computed(() => !!props.finding?.name)
const saving = ref(false)
const lastSaved = ref(null)

// Section definitions
const sections = {
	basic: { label: "Basic Information", icon: DocumentTextIcon },
	details: { label: "Finding Details", icon: ClipboardDocumentListIcon },
	evidence: {
		label: "Evidence & Recommendation",
		icon: DocumentMagnifyingGlassIcon,
	},
	response: { label: "Management Response", icon: ChatBubbleLeftRightIcon },
	action: { label: "Corrective Action Plan", icon: ClipboardDocumentCheckIcon },
	followup: { label: "Follow-up & Status", icon: ArrowPathIcon },
	verification: { label: "Verification", icon: ShieldCheckIcon },
	closure: { label: "Closure & Reporting", icon: DocumentCheckIcon },
}

// Section field mappings for validation
const sectionFields = {
	basic: [
		"finding_id",
		"engagement_reference",
		"finding_title",
		"finding_category",
	],
	details: ["condition", "criteria"],
	evidence: ["recommendation"],
	response: [],
	action: [],
	followup: ["finding_status"],
	verification: [],
	closure: [],
}

// Use multi-section form composable
const {
	activeSection,
	formProgress,
	setActiveSection,
	getSectionStatus,
	previousSection: prevSection,
	nextSection: nxtSection,
	validateForm,
	prepareFormData,
} = useMultiSectionForm(sections, sectionFields)

// Form data with all fields
const formData = reactive({
	// Basic Information
	finding_id: "",
	engagement_reference: "",
	finding_title: "",
	finding_category: "",
	risk_rating: "",
	business_impact_rating: "",
	date_identified: "",
	source_document: "",
	affected_locations: [],

	// Finding Details
	condition: "",
	criteria: "",
	cause: "",
	effect: "",

	// Evidence & Recommendation
	evidence: [],
	sample_size: null,
	exceptions_found: null,
	recommendation: "",

	// Management Response
	management_agrees: null,
	management_comments: "",
	response_date: "",
	management_response_by: "",
	management_response_date: "",

	// Corrective Action Plan
	action_plan_description: "",
	responsible_person: "",
	target_date: "",
	revised_target_date: "",
	priority: "",
	milestones: [],

	// Follow-up & Status
	finding_status: "Open",
	status_date: "",
	status_history: [],
	follow_up_required: 0,
	follow_up_frequency: "",
	next_follow_up_date: "",
	follow_up_history: [],

	// Verification
	verification_date: "",
	verified_by: "",
	verification_method: "",
	verification_status: "",
	verification_results: "",

	// Closure & Reporting
	closure_date: "",
	closed_by: "",
	closure_reason: "",
	final_disposition: "",
	closure_notes: "",
	include_in_report: false,
	reported_to_management: false,
	reported_to_audit_committee: false,
	reported_to_board: false,
	report_reference: "",

	// Related Findings
	related_findings: [],
	repeat_finding: 0,
	previous_finding_reference: "",
})

// Options for dropdowns
const categoryOptions = [
	{ label: "Control Weakness", value: "Control Weakness" },
	{ label: "Process Inefficiency", value: "Process Inefficiency" },
	{ label: "Compliance Gap", value: "Compliance Gap" },
	{ label: "Policy Violation", value: "Policy Violation" },
	{ label: "Documentation Issue", value: "Documentation Issue" },
	{ label: "Fraud Indicator", value: "Fraud Indicator" },
	{ label: "IT/System Issue", value: "IT/System Issue" },
	{ label: "Operational Risk", value: "Operational Risk" },
]

const riskRatingOptions = [
	{ label: "Critical", value: "Critical" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

const impactOptions = [
	{ label: "Severe", value: "Severe" },
	{ label: "Major", value: "Major" },
	{ label: "Moderate", value: "Moderate" },
	{ label: "Minor", value: "Minor" },
	{ label: "Insignificant", value: "Insignificant" },
]

const statusOptions = [
	{ label: "Open", value: "Open" },
	{ label: "Action in Progress", value: "Action in Progress" },
	{ label: "Pending Verification", value: "Pending Verification" },
	{ label: "Closed", value: "Closed" },
	{ label: "Accepted as Risk", value: "Accepted as Risk" },
	{ label: "Management Override", value: "Management Override" },
]

const priorityOptions = [
	{ label: "Urgent", value: "Urgent" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

const frequencyOptions = [
	{ label: "Weekly", value: "Weekly" },
	{ label: "Bi-weekly", value: "Bi-weekly" },
	{ label: "Monthly", value: "Monthly" },
	{ label: "Quarterly", value: "Quarterly" },
	{ label: "Semi-annually", value: "Semi-annually" },
	{ label: "Annually", value: "Annually" },
]

const verificationMethodOptions = [
	{ label: "Document Review", value: "Document Review" },
	{ label: "Re-testing", value: "Re-testing" },
	{ label: "Observation", value: "Observation" },
	{ label: "Interview", value: "Interview" },
	{ label: "Walkthrough", value: "Walkthrough" },
	{ label: "Data Analysis", value: "Data Analysis" },
]

const verificationStatusOptions = [
	{ label: "Not Started", value: "Not Started" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Verified - Effective", value: "Verified - Effective" },
	{
		label: "Verified - Partially Effective",
		value: "Verified - Partially Effective",
	},
	{ label: "Verified - Not Effective", value: "Verified - Not Effective" },
]

const closureReasonOptions = [
	{
		label: "Corrective Action Implemented",
		value: "Corrective Action Implemented",
	},
	{ label: "Risk Accepted", value: "Risk Accepted" },
	{ label: "Duplicate Finding", value: "Duplicate Finding" },
	{ label: "No Longer Applicable", value: "No Longer Applicable" },
	{ label: "Management Override", value: "Management Override" },
]

const dispositionOptions = [
	{ label: "Resolved", value: "Resolved" },
	{ label: "Partially Resolved", value: "Partially Resolved" },
	{ label: "Transferred", value: "Transferred" },
	{ label: "Deferred", value: "Deferred" },
]

// Placeholder options - would be fetched from API
const engagementOptions = ref([])
const userOptions = ref([])
const findingOptions = ref([])

// Child Table Configurations

// Affected Locations (simple - inline)
const affectedLocationColumns = [
	{
		key: "location",
		label: "Location",
		fieldType: "text",
		required: true,
		width: "200px",
	},
	{ key: "extent", label: "Extent/Notes", fieldType: "text", width: "300px" },
]

// Evidence (complex - modal)
const evidenceColumns = [
	{ key: "evidence_type", label: "Type", width: "120px" },
	{ key: "description", label: "Description", width: "250px" },
	{ key: "source", label: "Source", width: "150px" },
]

const evidenceFields = [
	{
		key: "evidence_type",
		label: "Evidence Type",
		type: "select",
		required: true,
		options: [
			{ label: "Document", value: "Document" },
			{ label: "Photo", value: "Photo" },
			{ label: "Data Analysis", value: "Data Analysis" },
			{ label: "Interview", value: "Interview" },
			{ label: "Observation", value: "Observation" },
			{ label: "Confirmation", value: "Confirmation" },
		],
	},
	{ key: "description", label: "Description", type: "text", required: true },
	{ key: "file", label: "Attachment", type: "attach" },
	{ key: "source", label: "Source", type: "text" },
	{ key: "reference", label: "Reference", type: "text" },
]

// Milestones (modal)
const milestoneColumns = [
	{ key: "milestone_description", label: "Description", width: "250px" },
	{ key: "due_date", label: "Due Date", width: "120px" },
	{ key: "status", label: "Status", width: "120px", component: "Badge" },
]

const milestoneFields = [
	{
		key: "milestone_description",
		label: "Milestone Description",
		type: "text",
		required: true,
	},
	{ key: "due_date", label: "Due Date", type: "date", required: true },
	{
		key: "status",
		label: "Status",
		type: "select",
		required: true,
		options: [
			{ label: "Not Started", value: "Not Started" },
			{ label: "In Progress", value: "In Progress" },
			{ label: "Completed", value: "Completed" },
			{ label: "Delayed", value: "Delayed" },
		],
	},
	{ key: "completion_date", label: "Completion Date", type: "date" },
	{ key: "notes", label: "Notes", type: "textarea" },
]

// Status History (modal, read-mostly)
const statusHistoryColumns = [
	{ key: "previous_status", label: "From", width: "120px" },
	{ key: "new_status", label: "To", width: "120px" },
	{ key: "changed_on", label: "Changed On", width: "150px" },
	{ key: "changed_by", label: "Changed By", width: "150px" },
]

const statusHistoryFields = [
	{
		key: "previous_status",
		label: "Previous Status",
		type: "select",
		options: statusOptions,
	},
	{
		key: "new_status",
		label: "New Status",
		type: "select",
		required: true,
		options: statusOptions,
	},
	{ key: "changed_on", label: "Changed On", type: "datetime", required: true },
	{
		key: "changed_by",
		label: "Changed By",
		type: "link",
		doctype: "User",
		required: true,
	},
	{ key: "reason", label: "Reason", type: "textarea" },
]

// Follow-up History (modal)
const followUpHistoryColumns = [
	{ key: "follow_up_date", label: "Date", width: "100px" },
	{ key: "follow_up_type", label: "Type", width: "150px" },
	{ key: "follow_up_by", label: "By", width: "150px" },
	{ key: "status", label: "Status", width: "100px", component: "Badge" },
]

const followUpHistoryFields = [
	{
		key: "follow_up_date",
		label: "Follow-up Date",
		type: "date",
		required: true,
	},
	{
		key: "follow_up_type",
		label: "Type",
		type: "select",
		required: true,
		options: [
			{ label: "Status Check", value: "Status Check" },
			{ label: "Progress Review", value: "Progress Review" },
			{
				label: "Implementation Verification",
				value: "Implementation Verification",
			},
			{ label: "Effectiveness Assessment", value: "Effectiveness Assessment" },
			{ label: "Closure Review", value: "Closure Review" },
		],
	},
	{
		key: "follow_up_by",
		label: "Follow-up By",
		type: "link",
		doctype: "User",
		required: true,
	},
	{ key: "findings", label: "Findings/Observations", type: "textarea" },
	{ key: "actions_taken", label: "Actions Taken", type: "textarea" },
	{ key: "next_follow_up_date", label: "Next Follow-up Date", type: "date" },
	{
		key: "status",
		label: "Status",
		type: "select",
		required: true,
		options: [
			{ label: "Open", value: "Open" },
			{ label: "In Progress", value: "In Progress" },
			{ label: "Completed", value: "Completed" },
			{ label: "Overdue", value: "Overdue" },
		],
	},
]

// Related Findings (modal)
const relatedFindingColumns = [
	{ key: "related_finding", label: "Related Finding", width: "200px" },
	{ key: "relationship_type", label: "Relationship", width: "150px" },
]

const relatedFindingFields = [
	{
		key: "related_finding",
		label: "Related Finding",
		type: "link",
		doctype: "Audit Finding",
		required: true,
	},
	{
		key: "relationship_type",
		label: "Relationship Type",
		type: "select",
		required: true,
		options: [
			{ label: "Duplicate", value: "Duplicate" },
			{ label: "Similar Issue", value: "Similar Issue" },
			{ label: "Root Cause", value: "Root Cause" },
			{ label: "Contributing Factor", value: "Contributing Factor" },
			{ label: "Follow-up Action", value: "Follow-up Action" },
			{ label: "Related Control", value: "Related Control" },
		],
	},
	{ key: "description", label: "Description", type: "textarea" },
]

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
		// Auto-save logic would go here
		lastSaved.value = new Date()
		// Could emit a draft-saved event or call API
	} catch (error) {
		console.error("Failed to save draft:", error)
	}
}

// Submit form
const submitForm = async () => {
	const validation = validateForm(formData)
	if (!validation.isValid) {
		// Show validation errors
		console.error("Validation errors:", validation.errors)
		// Navigate to first section with errors
		if (validation.errors.length > 0) {
			const firstErrorSection = Object.keys(sectionFields).find((section) =>
				sectionFields[section].some((field) =>
					validation.errors.includes(field),
				),
			)
			if (firstErrorSection) {
				setActiveSection(firstErrorSection)
			}
		}
		return
	}

	saving.value = true
	try {
		const data = prepareFormData(formData, {
			evidence: "Finding Evidence",
			affected_locations: "Finding Affected Location",
			milestones: "Finding Action Milestone",
			status_history: "Finding Status Change",
			follow_up_history: "Finding Follow-up Activity",
			related_findings: "Finding Related Finding",
		})

		// API call would go here
		// await createResource('Audit Finding').setValue.submit(data)

		emit("saved", data)
		closeDialog()
	} catch (error) {
		console.error("Failed to save finding:", error)
	} finally {
		saving.value = false
	}
}

// Close dialog
const closeDialog = () => {
	showDialog.value = false
	emit("close")
}

// Watch for finding prop changes (editing mode)
watch(
	() => props.finding,
	(newFinding) => {
		if (newFinding) {
			Object.keys(formData).forEach((key) => {
				if (newFinding[key] !== undefined) {
					formData[key] = newFinding[key]
				}
			})
		}
	},
	{ immediate: true, deep: true },
)

// Watch formData for auto-save
watch(
	formData,
	() => {
		// Debounced auto-save could be implemented here
	},
	{ deep: true },
)

// Lifecycle
onMounted(() => {
	// Fetch options data
	// fetchEngagements()
	// fetchUsers()
	// fetchFindings()
})
</script>

<style scoped>
/* Custom styles for the form */
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
