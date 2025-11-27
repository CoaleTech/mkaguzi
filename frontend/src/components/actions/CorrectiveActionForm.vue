<template>
  <Dialog
    v-model="dialogVisible"
    :options="{
      title: mode === 'edit' ? 'Edit Corrective Action Plan' : 'Create Corrective Action Plan',
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
                :class="currentSection === index ? 'bg-orange-100 border border-orange-300' : 'hover:bg-gray-100'"
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
                <span class="text-xs font-semibold text-orange-600">{{ overallProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  class="bg-orange-600 h-1.5 rounded-full transition-all duration-500"
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
                description="Action plan identification and status"
                :sectionNumber="1"
                color="orange"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Plan ID <span class="text-red-500">*</span>
                    </label>
                    <div class="flex gap-2">
                      <FormControl
                        v-model="form.plan_id"
                        placeholder="e.g., CAP-2025-001"
                        class="flex-1"
                      />
                      <Button variant="outline" size="sm" @click="generatePlanId">
                        <RefreshCwIcon class="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Audit Finding <span class="text-red-500">*</span>
                    </label>
                    <LinkField
                      v-model="form.audit_finding"
                      doctype="Audit Finding"
                      placeholder="Link to finding"
                    />
                  </div>

                  <FormControl
                    v-model="form.title"
                    label="Title"
                    placeholder="Action plan title"
                    :required="true"
                  />

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Status <span class="text-red-500">*</span>
                    </label>
                    <FormControl
                      type="select"
                      v-model="form.status"
                      :options="statusOptions"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Priority <span class="text-red-500">*</span>
                    </label>
                    <FormControl
                      type="select"
                      v-model="form.priority"
                      :options="priorityOptions"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
                  <FormControl
                    v-model="form.start_date"
                    type="date"
                    label="Start Date"
                  />
                  <FormControl
                    v-model="form.target_completion_date"
                    type="date"
                    label="Target Completion Date"
                    :required="true"
                  />
                  <FormControl
                    v-model="form.actual_completion_date"
                    type="date"
                    label="Actual Completion Date"
                  />
                </div>
              </div>
            </div>

            <!-- Section 2: Plan Details -->
            <div v-show="currentSection === 1" class="space-y-6">
              <SectionHeader
                title="Plan Details"
                description="Action description, root cause, and expected outcomes"
                :sectionNumber="2"
                color="blue"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Action Description <span class="text-red-500">*</span>
                  </label>
                  <TextEditor
                    :content="form.action_description"
                    @change="form.action_description = $event"
                    placeholder="Describe the corrective action to be taken..."
                    :editable="true"
                    editorClass="min-h-[150px] prose-sm"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Root Cause Analysis</label>
                  <TextEditor
                    :content="form.root_cause_analysis"
                    @change="form.root_cause_analysis = $event"
                    placeholder="Analyze the root cause of the finding..."
                    :editable="true"
                    editorClass="min-h-[120px] prose-sm"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Expected Outcomes</label>
                  <TextEditor
                    :content="form.expected_outcomes"
                    @change="form.expected_outcomes = $event"
                    placeholder="What outcomes are expected from this action..."
                    :editable="true"
                    editorClass="min-h-[120px] prose-sm"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Success Criteria</label>
                  <TextEditor
                    :content="form.success_criteria"
                    @change="form.success_criteria = $event"
                    placeholder="Define measurable criteria for success..."
                    :editable="true"
                    editorClass="min-h-[120px] prose-sm"
                  />
                </div>
              </div>
            </div>

            <!-- Section 3: Responsibility -->
            <div v-show="currentSection === 2" class="space-y-6">
              <SectionHeader
                title="Responsibility"
                description="Assign accountability and supporting team"
                :sectionNumber="3"
                color="green"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Responsible Person <span class="text-red-500">*</span>
                    </label>
                    <LinkField
                      v-model="form.responsible_person"
                      doctype="User"
                      placeholder="Select responsible person"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Responsible Department <span class="text-red-500">*</span>
                    </label>
                    <LinkField
                      v-model="form.responsible_department"
                      doctype="Department"
                      placeholder="Select department"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Accountable Person</label>
                    <LinkField
                      v-model="form.accountable_person"
                      doctype="User"
                      placeholder="Select accountable person"
                    />
                  </div>

                  <FormControl
                    v-model="form.supporting_team"
                    type="textarea"
                    label="Supporting Team"
                    placeholder="List team members supporting this action..."
                    rows="3"
                  />
                </div>
              </div>
            </div>

            <!-- Section 4: Resources -->
            <div v-show="currentSection === 3" class="space-y-6">
              <SectionHeader
                title="Resources"
                description="Budget and resource allocation"
                :sectionNumber="4"
                color="amber"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormControl
                    v-model="form.estimated_cost"
                    type="number"
                    label="Estimated Cost"
                    placeholder="0.00"
                  />
                  <FormControl
                    v-model="form.actual_cost"
                    type="number"
                    label="Actual Cost"
                    placeholder="0.00"
                  />
                  <FormControl
                    v-model="form.resources_required"
                    type="textarea"
                    label="Resources Required"
                    placeholder="List the resources needed..."
                    rows="3"
                  />
                  <FormControl
                    v-model="form.allocated_resources"
                    type="textarea"
                    label="Allocated Resources"
                    placeholder="List the resources allocated..."
                    rows="3"
                  />
                </div>
              </div>
            </div>

            <!-- Section 5: Milestones -->
            <div v-show="currentSection === 4" class="space-y-6">
              <SectionHeader
                title="Milestones"
                description="Track progress with key milestones"
                :sectionNumber="5"
                color="purple"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="flex items-center justify-between mb-4">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Milestones</h4>
                    <p class="text-xs text-gray-500">{{ form.milestones?.length || 0 }} milestones defined</p>
                  </div>
                  <Button variant="outline" size="sm" @click="addMilestone">
                    <template #prefix><PlusIcon class="h-4 w-4" /></template>
                    Add Milestone
                  </Button>
                </div>

                <div v-if="form.milestones?.length > 0" class="space-y-4">
                  <div
                    v-for="(milestone, index) in form.milestones"
                    :key="index"
                    class="border border-gray-200 rounded-lg p-4 hover:border-orange-300 transition-colors"
                  >
                    <div class="flex items-start justify-between mb-4">
                      <Badge :variant="getMilestoneStatusVariant(milestone.status)" size="sm">
                        {{ milestone.status || 'Not Started' }}
                      </Badge>
                      <Button variant="ghost" size="sm" @click="removeMilestone(index)" class="text-red-500">
                        <TrashIcon class="h-4 w-4" />
                      </Button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div class="md:col-span-2">
                        <FormControl
                          v-model="milestone.milestone_description"
                          label="Description"
                          placeholder="Milestone description..."
                          size="sm"
                        />
                      </div>
                      <FormControl
                        v-model="milestone.due_date"
                        type="date"
                        label="Due Date"
                        size="sm"
                      />
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Status</label>
                        <FormControl
                          type="select"
                          v-model="milestone.status"
                          :options="milestoneStatusOptions"
                          size="sm"
                        />
                      </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                      <FormControl
                        v-model="milestone.completion_date"
                        type="date"
                        label="Completion Date"
                        size="sm"
                      />
                      <FormControl
                        v-model="milestone.notes"
                        label="Notes"
                        placeholder="Additional notes..."
                        size="sm"
                      />
                    </div>
                  </div>
                </div>

                <div v-else class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                  <FlagIcon class="mx-auto h-12 w-12 text-gray-400" />
                  <h3 class="mt-2 text-sm font-medium text-gray-900">No milestones defined</h3>
                  <p class="mt-1 text-sm text-gray-500">Add milestones to track progress.</p>
                  <Button variant="outline" size="sm" class="mt-4" @click="addMilestone">
                    <template #prefix><PlusIcon class="h-4 w-4" /></template>
                    Add First Milestone
                  </Button>
                </div>
              </div>
            </div>

            <!-- Section 6: Progress Tracking -->
            <div v-show="currentSection === 5" class="space-y-6">
              <SectionHeader
                title="Progress Tracking"
                description="Track overall progress and updates"
                :sectionNumber="6"
                color="cyan"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Overall Progress</label>
                    <FormControl
                      type="select"
                      v-model="form.overall_progress"
                      :options="progressOptions"
                    />
                  </div>
                  <FormControl
                    v-model="form.completion_percentage"
                    type="number"
                    label="Completion %"
                    placeholder="0"
                    min="0"
                    max="100"
                  />
                  <FormControl
                    v-model="form.last_progress_update"
                    type="date"
                    label="Last Progress Update"
                  />
                </div>

                <div class="mt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Progress Notes</label>
                  <TextEditor
                    :content="form.progress_notes"
                    @change="form.progress_notes = $event"
                    placeholder="Document progress updates..."
                    :editable="true"
                    editorClass="min-h-[120px] prose-sm"
                  />
                </div>
              </div>
            </div>

            <!-- Section 7: Issues & Risks -->
            <div v-show="currentSection === 6" class="space-y-6">
              <SectionHeader
                title="Issues & Risks"
                description="Document issues and mitigation actions"
                :sectionNumber="7"
                color="red"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Identified Issues</label>
                  <TextEditor
                    :content="form.identified_issues"
                    @change="form.identified_issues = $event"
                    placeholder="Document any identified issues..."
                    :editable="true"
                    editorClass="min-h-[120px] prose-sm"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Mitigation Actions</label>
                  <TextEditor
                    :content="form.mitigation_actions"
                    @change="form.mitigation_actions = $event"
                    placeholder="Describe mitigation actions taken..."
                    :editable="true"
                    editorClass="min-h-[120px] prose-sm"
                  />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      v-model="form.escalation_required"
                      class="h-4 w-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                    />
                    <label class="text-sm text-gray-700">Escalation Required</label>
                  </div>
                  <FormControl
                    v-if="form.escalation_required"
                    v-model="form.escalation_details"
                    type="textarea"
                    label="Escalation Details"
                    placeholder="Describe escalation details..."
                    rows="2"
                  />
                </div>
              </div>
            </div>

            <!-- Section 8: Verification & Closure -->
            <div v-show="currentSection === 7" class="space-y-6">
              <SectionHeader
                title="Verification & Closure"
                description="Verification, approval, and closure details"
                :sectionNumber="8"
                color="orange"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Verification -->
                <div>
                  <h4 class="text-sm font-semibold text-gray-900 mb-4 flex items-center">
                    <ShieldCheckIcon class="h-4 w-4 mr-2 text-green-600" />
                    Verification
                  </h4>
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        v-model="form.verification_required"
                        class="h-4 w-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                      />
                      <label class="text-sm text-gray-700">Verification Required</label>
                    </div>
                    <div v-if="form.verification_required">
                      <label class="block text-sm font-medium text-gray-700 mb-1">Verification Method</label>
                      <FormControl
                        type="select"
                        v-model="form.verification_method"
                        :options="verificationMethodOptions"
                      />
                    </div>
                    <FormControl
                      v-if="form.verification_required"
                      v-model="form.verification_date"
                      type="date"
                      label="Verification Date"
                    />
                  </div>
                  <div v-if="form.verification_required" class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Verified By</label>
                      <LinkField
                        v-model="form.verified_by"
                        doctype="User"
                        placeholder="Select verifier"
                      />
                    </div>
                  </div>
                  <div v-if="form.verification_required" class="mt-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Verification Results</label>
                    <TextEditor
                      :content="form.verification_results"
                      @change="form.verification_results = $event"
                      placeholder="Document verification results..."
                      :editable="true"
                      editorClass="min-h-[100px] prose-sm"
                    />
                  </div>
                </div>

                <!-- Approval -->
                <div class="border-t border-gray-200 pt-6">
                  <h4 class="text-sm font-semibold text-gray-900 mb-4 flex items-center">
                    <CheckCircle2Icon class="h-4 w-4 mr-2 text-blue-600" />
                    Approval
                  </h4>
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        v-model="form.approval_required"
                        class="h-4 w-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                      />
                      <label class="text-sm text-gray-700">Approval Required</label>
                    </div>
                    <div v-if="form.approval_required">
                      <label class="block text-sm font-medium text-gray-700 mb-1">Approved By</label>
                      <LinkField
                        v-model="form.approved_by"
                        doctype="User"
                        placeholder="Select approver"
                      />
                    </div>
                    <FormControl
                      v-if="form.approval_required"
                      v-model="form.approval_date"
                      type="date"
                      label="Approval Date"
                    />
                  </div>
                  <FormControl
                    v-if="form.approval_required"
                    v-model="form.approval_notes"
                    type="textarea"
                    label="Approval Notes"
                    placeholder="Add approval notes..."
                    rows="2"
                    class="mt-4"
                  />
                </div>

                <!-- Closure -->
                <div class="border-t border-gray-200 pt-6">
                  <h4 class="text-sm font-semibold text-gray-900 mb-4 flex items-center">
                    <ArchiveIcon class="h-4 w-4 mr-2 text-gray-600" />
                    Closure
                  </h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Closure Reason</label>
                      <FormControl
                        type="select"
                        v-model="form.closure_reason"
                        :options="closureReasonOptions"
                      />
                    </div>
                  </div>
                  <div class="mt-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Closure Notes</label>
                    <TextEditor
                      :content="form.closure_notes"
                      @change="form.closure_notes = $event"
                      placeholder="Document closure details..."
                      :editable="true"
                      editorClass="min-h-[100px] prose-sm"
                    />
                  </div>
                  <div class="mt-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Lessons Learned</label>
                    <TextEditor
                      :content="form.lessons_learned"
                      @change="form.lessons_learned = $event"
                      placeholder="Document lessons learned..."
                      :editable="true"
                      editorClass="min-h-[100px] prose-sm"
                    />
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
            theme="orange"
            @click="nextSection"
          >
            Next
            <template #suffix><ChevronRightIcon class="h-4 w-4" /></template>
          </Button>

          <Button
            v-else
            variant="solid"
            theme="orange"
            @click="submitForm"
            :loading="submitting"
            :disabled="!isFormValid"
          >
            <template #prefix><CheckIcon class="h-4 w-4" /></template>
            {{ mode === 'edit' ? 'Update Plan' : 'Create Plan' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Badge, Button, Dialog, FormControl, TextEditor } from 'frappe-ui'
import {
  ArchiveIcon,
  CheckCircle2Icon,
  CheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  FlagIcon,
  PlusIcon,
  RefreshCwIcon,
  SaveIcon,
  ShieldCheckIcon,
  TrashIcon,
} from 'lucide-vue-next'
import SectionHeader from '@/components/Common/SectionHeader.vue'
import LinkField from '@/components/Common/fields/LinkField.vue'
import { useCorrectiveActionsStore } from '@/stores/correctiveActions'

// Props
const props = defineProps({
  show: { type: Boolean, default: false },
  action: { type: Object, default: null },
  mode: { type: String, default: 'create' },
})

// Emit
const emit = defineEmits(['update:show', 'saved', 'close'])

// Store
const correctiveActionsStore = useCorrectiveActionsStore()

// State
const currentSection = ref(0)
const saving = ref(false)
const submitting = ref(false)
const lastSaved = ref(null)

// Computed for dialog visibility (to avoid v-model on prop)
const dialogVisible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value),
})

// Form data
const form = ref(getDefaultForm())

function getDefaultForm() {
  return {
    plan_id: '',
    audit_finding: '',
    title: '',
    status: 'Draft',
    priority: 'Medium',
    start_date: '',
    target_completion_date: '',
    actual_completion_date: '',
    action_description: '',
    root_cause_analysis: '',
    expected_outcomes: '',
    success_criteria: '',
    responsible_person: '',
    responsible_department: '',
    accountable_person: '',
    supporting_team: '',
    estimated_cost: 0,
    actual_cost: 0,
    resources_required: '',
    allocated_resources: '',
    milestones: [],
    overall_progress: 'Not Started',
    completion_percentage: 0,
    last_progress_update: '',
    progress_notes: '',
    identified_issues: '',
    mitigation_actions: '',
    escalation_required: false,
    escalation_details: '',
    verification_required: true,
    verification_method: '',
    verification_date: '',
    verified_by: '',
    verification_results: '',
    approval_required: false,
    approved_by: '',
    approval_date: '',
    approval_notes: '',
    closure_reason: '',
    closure_notes: '',
    lessons_learned: '',
  }
}

// Sections
const sections = [
  { id: 'basic', title: 'Basic Information', description: 'Plan ID and status' },
  { id: 'details', title: 'Plan Details', description: 'Description and analysis' },
  { id: 'responsibility', title: 'Responsibility', description: 'Assign ownership' },
  { id: 'resources', title: 'Resources', description: 'Budget allocation' },
  { id: 'milestones', title: 'Milestones', description: 'Track progress' },
  { id: 'progress', title: 'Progress Tracking', description: 'Overall progress' },
  { id: 'issues', title: 'Issues & Risks', description: 'Document issues' },
  { id: 'closure', title: 'Verification & Closure', description: 'Complete the plan' },
]

// Options
const statusOptions = [
  { label: 'Draft', value: 'Draft' },
  { label: 'Approved', value: 'Approved' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'On Hold', value: 'On Hold' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Cancelled', value: 'Cancelled' },
]

const priorityOptions = [
  { label: 'Low', value: 'Low' },
  { label: 'Medium', value: 'Medium' },
  { label: 'High', value: 'High' },
  { label: 'Critical', value: 'Critical' },
]

const milestoneStatusOptions = [
  { label: 'Not Started', value: 'Not Started' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Delayed', value: 'Delayed' },
]

const progressOptions = [
  { label: 'Not Started', value: 'Not Started' },
  { label: 'Planning', value: 'Planning' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Review', value: 'Review' },
  { label: 'Testing', value: 'Testing' },
  { label: 'Completed', value: 'Completed' },
]

const verificationMethodOptions = [
  { label: 'Document Review', value: 'Document Review' },
  { label: 'Re-testing', value: 'Re-testing' },
  { label: 'Observation', value: 'Observation' },
  { label: 'Interview', value: 'Interview' },
  { label: 'Data Analysis', value: 'Data Analysis' },
  { label: 'Audit Testing', value: 'Audit Testing' },
]

const closureReasonOptions = [
  { label: 'Successfully Completed', value: 'Successfully Completed' },
  { label: 'No Longer Applicable', value: 'No Longer Applicable' },
  { label: 'Alternative Solution', value: 'Alternative Solution' },
  { label: 'Cancelled by Management', value: 'Cancelled by Management' },
]

// Watch for action changes
watch(() => props.action, (newAction) => {
  if (newAction) {
    form.value = {
      ...getDefaultForm(),
      ...newAction,
      milestones: newAction.milestones || [],
    }
  } else {
    form.value = getDefaultForm()
  }
  currentSection.value = 0
}, { immediate: true })

watch(() => props.show, (newShow) => {
  if (!newShow) {
    currentSection.value = 0
    lastSaved.value = null
  }
})

// Computed
const overallProgress = computed(() => {
  let completed = 0
  if (form.value.plan_id && form.value.title && form.value.audit_finding) completed += 15
  if (form.value.action_description) completed += 15
  if (form.value.responsible_person && form.value.responsible_department) completed += 15
  completed += 10 // Resources optional
  if (form.value.milestones?.length > 0) completed += 15
  completed += 10 // Progress tracking
  completed += 10 // Issues & risks optional
  completed += 10 // Closure
  return completed
})

const isFormValid = computed(() => {
  return form.value.plan_id &&
    form.value.audit_finding &&
    form.value.title &&
    form.value.status &&
    form.value.priority &&
    form.value.target_completion_date &&
    form.value.action_description &&
    form.value.responsible_person &&
    form.value.responsible_department
})

// Methods
const isSectionComplete = (sectionId) => {
  switch (sectionId) {
    case 'basic':
      return form.value.plan_id && form.value.title && form.value.audit_finding && form.value.target_completion_date
    case 'details':
      return !!form.value.action_description
    case 'responsibility':
      return form.value.responsible_person && form.value.responsible_department
    case 'resources':
      return true // Optional
    case 'milestones':
      return form.value.milestones?.length > 0
    case 'progress':
      return true // Optional
    case 'issues':
      return true // Optional
    case 'closure':
      return true // Optional until closure
    default:
      return false
  }
}

const getSectionStatusClass = (sectionId) => {
  if (isSectionComplete(sectionId)) {
    return 'bg-green-500 text-white'
  }
  return 'bg-gray-300 text-gray-600'
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

const generatePlanId = () => {
  const year = new Date().getFullYear()
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0')
  form.value.plan_id = `CAP-${year}-${random}`
}

const addMilestone = () => {
  form.value.milestones.push({
    milestone_description: '',
    due_date: '',
    status: 'Not Started',
    completion_date: '',
    notes: '',
  })
}

const removeMilestone = (index) => {
  form.value.milestones.splice(index, 1)
}

const getMilestoneStatusVariant = (status) => {
  const variants = {
    'Not Started': 'subtle',
    'In Progress': 'subtle',
    'Completed': 'subtle',
    'Delayed': 'subtle',
  }
  return variants[status] || 'subtle'
}

const saveDraft = async () => {
  saving.value = true
  try {
    if (props.mode === 'edit' && props.action?.name) {
      await correctiveActionsStore.updateAction(props.action.name, form.value)
    } else {
      await correctiveActionsStore.createAction(form.value)
    }
    lastSaved.value = new Date().toLocaleTimeString()
  } catch (error) {
    console.error('Error saving draft:', error)
  } finally {
    saving.value = false
  }
}

const submitForm = async () => {
  submitting.value = true
  try {
    if (props.mode === 'edit' && props.action?.name) {
      await correctiveActionsStore.updateAction(props.action.name, form.value)
    } else {
      await correctiveActionsStore.createAction(form.value)
    }
    emit('saved')
    emit('update:show', false)
  } catch (error) {
    console.error('Error submitting form:', error)
  } finally {
    submitting.value = false
  }
}
</script>
