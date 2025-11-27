<template>
  <Dialog
    v-model="dialogVisible"
    :options="{
      title: isEditMode ? 'Edit Follow-up Tracker' : 'Create Follow-up Tracker',
      size: '7xl',
    }"
  >
    <template #body-content>
      <div class="flex h-[75vh]">
        <!-- Left Sidebar: Section Navigation -->
        <div class="w-52 border-r bg-gray-50 p-4 flex flex-col">
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
              <div class="grid grid-cols-2 gap-4">
                <FormControl
                  v-model="formData.tracker_id"
                  label="Tracker ID *"
                  type="text"
                  placeholder="e.g., FUT-2025-001"
                />
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Audit Finding *</label>
                  <LinkField
                    v-model="formData.audit_finding"
                    doctype="Audit Finding"
                    placeholder="Select finding"
                  />
                </div>
              </div>

              <FormControl
                v-model="formData.finding_title"
                label="Finding Title"
                type="text"
                disabled
              />

              <div class="grid grid-cols-3 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Status *</label>
                  <Select
                    v-model="formData.status"
                    :options="statusOptions"
                    placeholder="Select status"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Follow-up Type *</label>
                  <Select
                    v-model="formData.follow_up_type"
                    :options="followUpTypeOptions"
                    placeholder="Select type"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Frequency *</label>
                  <Select
                    v-model="formData.frequency"
                    :options="frequencyOptions"
                    placeholder="Select frequency"
                  />
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <FormControl
                  v-model="formData.start_date"
                  label="Start Date *"
                  type="date"
                />
                <FormControl
                  v-model="formData.next_due_date"
                  label="Next Due Date"
                  type="date"
                />
              </div>
            </div>

            <!-- Section 2: Follow-up Details -->
            <div v-show="currentSectionIndex === 1" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Responsible Person *</label>
                  <LinkField
                    v-model="formData.responsible_person"
                    doctype="User"
                    placeholder="Select person"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Responsible Department *</label>
                  <LinkField
                    v-model="formData.responsible_department"
                    doctype="Department"
                    placeholder="Select department"
                  />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Follow-up Objective *</label>
                <TextEditor
                  v-model="formData.follow_up_objective"
                  :content="formData.follow_up_objective"
                  placeholder="Describe the objective of this follow-up..."
                  editor-class="prose-sm max-w-none min-h-[100px]"
                  :bubbleMenu="true"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Success Criteria</label>
                <TextEditor
                  v-model="formData.success_criteria"
                  :content="formData.success_criteria"
                  placeholder="Define the criteria for successful completion..."
                  editor-class="prose-sm max-w-none min-h-[100px]"
                  :bubbleMenu="true"
                />
              </div>
            </div>

            <!-- Section 3: Activities & History -->
            <div v-show="currentSectionIndex === 2" class="space-y-4">
              <!-- Follow-up Activities Table -->
              <div>
                <div class="flex items-center justify-between mb-3">
                  <h4 class="text-sm font-medium text-gray-700">Follow-up Activities</h4>
                  <Button size="sm" @click="addActivity">
                    <template #prefix><Plus class="h-4 w-4" /></template>
                    Add Activity
                  </Button>
                </div>
                <div class="border rounded-lg overflow-hidden max-h-64 overflow-y-auto">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50 sticky top-0">
                      <tr>
                        <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Date</th>
                        <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Activity Type</th>
                        <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Description</th>
                        <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">By</th>
                        <th class="px-3 py-2 w-12"></th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="(activity, idx) in formData.follow_up_activities" :key="idx">
                        <td class="px-3 py-2">
                          <FormControl v-model="activity.activity_date" type="date" size="sm" />
                        </td>
                        <td class="px-3 py-2">
                          <Select v-model="activity.activity_type" :options="activityTypeOptions" size="sm" />
                        </td>
                        <td class="px-3 py-2">
                          <FormControl v-model="activity.description" type="text" size="sm" />
                        </td>
                        <td class="px-3 py-2">
                          <FormControl v-model="activity.performed_by" type="text" size="sm" />
                        </td>
                        <td class="px-3 py-2">
                          <Button variant="ghost" size="sm" @click="removeActivity(idx)">
                            <Trash2 class="h-4 w-4 text-red-500" />
                          </Button>
                        </td>
                      </tr>
                      <tr v-if="!formData.follow_up_activities?.length">
                        <td colspan="5" class="px-4 py-8 text-center text-gray-500 text-sm">
                          No activities recorded. Click "Add Activity" to add one.
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Last Follow-up Info -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-700 mb-3">Last Follow-up</h4>
                <div class="grid grid-cols-2 gap-4">
                  <FormControl
                    v-model="formData.last_follow_up_date"
                    label="Date"
                    type="date"
                    disabled
                  />
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">By</label>
                    <LinkField
                      v-model="formData.last_follow_up_by"
                      doctype="User"
                      disabled
                    />
                  </div>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Last Findings</label>
                <TextEditor
                  v-model="formData.last_findings"
                  :content="formData.last_findings"
                  placeholder="Findings from last follow-up..."
                  editor-class="prose-sm max-w-none min-h-[80px]"
                  :bubbleMenu="true"
                  disabled
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Next Steps</label>
                <TextEditor
                  v-model="formData.next_steps"
                  :content="formData.next_steps"
                  placeholder="Define next steps..."
                  editor-class="prose-sm max-w-none min-h-[80px]"
                  :bubbleMenu="true"
                />
              </div>
            </div>

            <!-- Section 4: Progress Assessment -->
            <div v-show="currentSectionIndex === 3" class="space-y-4">
              <div class="grid grid-cols-3 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Current Status</label>
                  <Select
                    v-model="formData.current_status"
                    :options="currentStatusOptions"
                    placeholder="Select status"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Progress Rating</label>
                  <div class="flex items-center gap-1 mt-2">
                    <button
                      v-for="star in 5"
                      :key="star"
                      @click="formData.progress_rating = star"
                      class="focus:outline-none"
                    >
                      <Star
                        class="h-6 w-6"
                        :class="star <= formData.progress_rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'"
                      />
                    </button>
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Effectiveness Rating</label>
                  <div class="flex items-center gap-1 mt-2">
                    <button
                      v-for="star in 5"
                      :key="star"
                      @click="formData.effectiveness_rating = star"
                      class="focus:outline-none"
                    >
                      <Star
                        class="h-6 w-6"
                        :class="star <= formData.effectiveness_rating ? 'text-green-400 fill-green-400' : 'text-gray-300'"
                      />
                    </button>
                  </div>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Issues Identified</label>
                <TextEditor
                  v-model="formData.issues_identified"
                  :content="formData.issues_identified"
                  placeholder="Document any issues identified..."
                  editor-class="prose-sm max-w-none min-h-[100px]"
                  :bubbleMenu="true"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Recommendations</label>
                <TextEditor
                  v-model="formData.recommendations"
                  :content="formData.recommendations"
                  placeholder="Provide recommendations..."
                  editor-class="prose-sm max-w-none min-h-[100px]"
                  :bubbleMenu="true"
                />
              </div>
            </div>

            <!-- Section 5: Escalation -->
            <div v-show="currentSectionIndex === 4" class="space-y-4">
              <div class="flex items-center gap-3 p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <input
                  type="checkbox"
                  v-model="formData.escalation_required"
                  class="rounded border-gray-300 h-5 w-5"
                />
                <div>
                  <span class="font-medium text-orange-800">Escalation Required</span>
                  <p class="text-sm text-orange-600">Check if this issue needs to be escalated to higher management.</p>
                </div>
              </div>

              <div v-if="formData.escalation_required" class="space-y-4 p-4 bg-gray-50 rounded-lg">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Escalation Level</label>
                    <Select
                      v-model="formData.escalation_level"
                      :options="escalationLevelOptions"
                      placeholder="Select level"
                    />
                  </div>
                  <FormControl
                    v-model="formData.escalation_date"
                    label="Escalation Date"
                    type="date"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Escalation Reason</label>
                  <FormControl
                    v-model="formData.escalation_reason"
                    type="textarea"
                    :rows="3"
                    placeholder="Describe the reason for escalation..."
                  />
                </div>
              </div>
            </div>

            <!-- Section 6: Closure -->
            <div v-show="currentSectionIndex === 5" class="space-y-4">
              <div class="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                <input
                  type="checkbox"
                  v-model="formData.closure_criteria_met"
                  class="rounded border-gray-300 h-5 w-5"
                />
                <div>
                  <span class="font-medium text-green-800">Closure Criteria Met</span>
                  <p class="text-sm text-green-600">Check if all success criteria have been satisfied.</p>
                </div>
              </div>

              <div class="grid grid-cols-3 gap-4">
                <FormControl
                  v-model="formData.closure_date"
                  label="Closure Date"
                  type="date"
                />
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Closed By</label>
                  <LinkField
                    v-model="formData.closed_by"
                    doctype="User"
                    placeholder="Select user"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Closure Reason</label>
                  <Select
                    v-model="formData.closure_reason"
                    :options="closureReasonOptions"
                    placeholder="Select reason"
                  />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Final Assessment</label>
                <TextEditor
                  v-model="formData.final_assessment"
                  :content="formData.final_assessment"
                  placeholder="Provide final assessment..."
                  editor-class="prose-sm max-w-none min-h-[120px]"
                  :bubbleMenu="true"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <TextEditor
                  v-model="formData.notes"
                  :content="formData.notes"
                  placeholder="Additional notes..."
                  editor-class="prose-sm max-w-none min-h-[80px]"
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
                @click="saveTracker"
                :loading="saving"
              >
                <template #prefix><Save class="h-4 w-4" /></template>
                {{ isEditMode ? 'Update Tracker' : 'Create Tracker' }}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { Dialog, Button, FormControl, TextEditor, Select } from 'frappe-ui'
import LinkField from '@/components/Common/fields/LinkField.vue'
import SectionHeader from '@/components/Common/SectionHeader.vue'
import {
  Info,
  FileText,
  History,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Save,
  Plus,
  Trash2,
  Star,
} from 'lucide-vue-next'

const props = defineProps({
  show: { type: Boolean, default: false },
  tracker: { type: Object, default: null },
})

const emit = defineEmits(['update:show', 'saved'])

const dialogVisible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val),
})

const isEditMode = computed(() => !!props.tracker?.name)
const saving = ref(false)
const currentSectionIndex = ref(0)

// Section definitions
const sections = [
  { id: 'basic', title: 'Basic Info', icon: Info, description: 'Tracker identification and scheduling' },
  { id: 'details', title: 'Details', icon: FileText, description: 'Objectives and responsibility' },
  { id: 'history', title: 'Activities', icon: History, description: 'Follow-up activities and history' },
  { id: 'progress', title: 'Progress', icon: TrendingUp, description: 'Progress assessment and ratings' },
  { id: 'escalation', title: 'Escalation', icon: AlertTriangle, description: 'Escalation management' },
  { id: 'closure', title: 'Closure', icon: CheckCircle2, description: 'Closure and final assessment' },
]

// Form data
const formData = reactive({
  tracker_id: '',
  audit_finding: '',
  finding_title: '',
  status: 'Active',
  follow_up_type: '',
  frequency: '',
  start_date: '',
  next_due_date: '',
  responsible_person: '',
  responsible_department: '',
  follow_up_objective: '',
  success_criteria: '',
  follow_up_activities: [],
  last_follow_up_date: '',
  last_follow_up_by: '',
  last_findings: '',
  next_steps: '',
  current_status: '',
  progress_rating: 0,
  effectiveness_rating: 0,
  issues_identified: '',
  recommendations: '',
  escalation_required: false,
  escalation_level: '',
  escalation_reason: '',
  escalation_date: '',
  closure_criteria_met: false,
  closure_date: '',
  closed_by: '',
  closure_reason: '',
  final_assessment: '',
  notes: '',
})

// Options
const statusOptions = [
  { label: 'Active', value: 'Active' },
  { label: 'Completed', value: 'Completed' },
  { label: 'On Hold', value: 'On Hold' },
  { label: 'Cancelled', value: 'Cancelled' },
]

const followUpTypeOptions = [
  { label: 'Corrective Action Monitoring', value: 'Corrective Action Monitoring' },
  { label: 'Preventive Measure Verification', value: 'Preventive Measure Verification' },
  { label: 'Process Improvement Tracking', value: 'Process Improvement Tracking' },
  { label: 'Risk Mitigation Assessment', value: 'Risk Mitigation Assessment' },
  { label: 'Compliance Verification', value: 'Compliance Verification' },
]

const frequencyOptions = [
  { label: 'Monthly', value: 'Monthly' },
  { label: 'Quarterly', value: 'Quarterly' },
  { label: 'Semi-Annual', value: 'Semi-Annual' },
  { label: 'Annual', value: 'Annual' },
  { label: 'One-time', value: 'One-time' },
  { label: 'As Needed', value: 'As Needed' },
]

const activityTypeOptions = [
  { label: 'Review', value: 'Review' },
  { label: 'Meeting', value: 'Meeting' },
  { label: 'Document Request', value: 'Document Request' },
  { label: 'Testing', value: 'Testing' },
  { label: 'Observation', value: 'Observation' },
  { label: 'Other', value: 'Other' },
]

const currentStatusOptions = [
  { label: 'On Track', value: 'On Track' },
  { label: 'Behind Schedule', value: 'Behind Schedule' },
  { label: 'At Risk', value: 'At Risk' },
  { label: 'Off Track', value: 'Off Track' },
  { label: 'Completed Successfully', value: 'Completed Successfully' },
]

const escalationLevelOptions = [
  { label: 'Manager', value: 'Manager' },
  { label: 'Senior Management', value: 'Senior Management' },
  { label: 'Audit Committee', value: 'Audit Committee' },
  { label: 'Board', value: 'Board' },
]

const closureReasonOptions = [
  { label: 'Successfully Completed', value: 'Successfully Completed' },
  { label: 'No Longer Required', value: 'No Longer Required' },
  { label: 'Alternative Solution Implemented', value: 'Alternative Solution Implemented' },
  { label: 'Management Decision', value: 'Management Decision' },
]

// Watch for tracker prop changes
watch(
  () => props.tracker,
  (newTracker) => {
    if (newTracker) {
      Object.keys(formData).forEach((key) => {
        if (newTracker[key] !== undefined) {
          formData[key] = newTracker[key]
        }
      })
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

// Section validation
const sectionValidation = computed(() => [
  !!(formData.tracker_id && formData.audit_finding && formData.status && formData.follow_up_type && formData.frequency && formData.start_date),
  !!(formData.responsible_person && formData.responsible_department && formData.follow_up_objective),
  true, // Activities - optional
  true, // Progress - optional
  true, // Escalation - optional
  true, // Closure - optional
])

const completedSections = computed(() =>
  sectionValidation.value.filter(Boolean).length
)

const progressPercentage = computed(() =>
  Math.round((completedSections.value / sections.length) * 100)
)

function isSectionComplete(index) {
  return sectionValidation.value[index]
}

function getSectionStatusClass(index) {
  if (currentSectionIndex.value === index) return 'text-blue-600'
  if (isSectionComplete(index)) return 'text-green-500'
  return 'text-gray-400'
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
function addActivity() {
  formData.follow_up_activities.push({
    activity_date: new Date().toISOString().split('T')[0],
    activity_type: '',
    description: '',
    performed_by: '',
  })
}

function removeActivity(index) {
  formData.follow_up_activities.splice(index, 1)
}

function resetForm() {
  Object.keys(formData).forEach((key) => {
    if (Array.isArray(formData[key])) {
      formData[key] = []
    } else if (typeof formData[key] === 'boolean') {
      formData[key] = false
    } else if (typeof formData[key] === 'number') {
      formData[key] = 0
    } else {
      formData[key] = ''
    }
  })
  formData.status = 'Active'
  currentSectionIndex.value = 0
}

function closeDialog() {
  emit('update:show', false)
  resetForm()
}

async function saveTracker() {
  saving.value = true
  try {
    console.log('Saving tracker:', formData)
    emit('saved', { ...formData })
    closeDialog()
  } catch (error) {
    console.error('Error saving tracker:', error)
  } finally {
    saving.value = false
  }
}
</script>
