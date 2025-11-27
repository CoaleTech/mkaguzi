<template>
  <Dialog
    v-model="isOpen"
    :options="{
      title: '',
      size: '7xl',
    }"
  >
    <template #body>
      <div class="flex h-[85vh] overflow-hidden bg-gray-50 -m-4">
        <!-- Left Sidebar - Progress Navigation -->
        <div class="w-72 bg-white border-r border-gray-200 flex flex-col">
          <!-- Header -->
          <div class="p-6 border-b border-gray-200 bg-gradient-to-r from-red-50 to-orange-50">
            <div class="flex items-center gap-3">
              <div class="h-12 w-12 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center shadow-lg">
                <AlertTriangleIcon class="h-6 w-6 text-white" />
              </div>
              <div>
                <h2 class="text-lg font-bold text-gray-900">
                  {{ isEditMode ? 'Edit Risk Assessment' : 'New Risk Assessment' }}
                </h2>
                <p class="text-sm text-gray-600">{{ formProgress }}% Complete</p>
              </div>
            </div>
            <!-- Progress Bar -->
            <div class="mt-4 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-red-500 to-orange-500 transition-all duration-500"
                :style="{ width: `${formProgress}%` }"
              />
            </div>
          </div>

          <!-- Section Navigation -->
          <nav class="flex-1 overflow-y-auto p-4">
            <div class="space-y-1">
              <button
                v-for="(section, index) in sections"
                :key="section.id"
                @click="navigateToSection(section.id)"
                class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all duration-200"
                :class="{
                  'bg-red-50 text-red-700 border-2 border-red-200 shadow-sm': activeSection === section.id,
                  'hover:bg-gray-50 text-gray-700': activeSection !== section.id
                }"
              >
                <!-- Section Number/Status -->
                <div
                  class="flex-shrink-0 h-8 w-8 rounded-lg flex items-center justify-center text-sm font-semibold transition-colors"
                  :class="getSectionStatusClass(section.id)"
                >
                  <component
                    v-if="getSectionStatus(section.id) === 'complete'"
                    :is="CheckIcon"
                    class="h-4 w-4"
                  />
                  <component
                    v-else-if="getSectionStatus(section.id) === 'error'"
                    :is="AlertCircleIcon"
                    class="h-4 w-4"
                  />
                  <span v-else>{{ index + 1 }}</span>
                </div>

                <!-- Section Info -->
                <div class="flex-1 min-w-0">
                  <div class="font-medium truncate">{{ section.label }}</div>
                  <div class="text-xs text-gray-500 truncate">{{ section.description }}</div>
                </div>

                <!-- Status Indicator -->
                <ChevronRightIcon
                  v-if="activeSection === section.id"
                  class="h-4 w-4 text-red-500 flex-shrink-0"
                />
              </button>
            </div>
          </nav>

          <!-- Footer Actions -->
          <div class="p-4 border-t border-gray-200 bg-gray-50 space-y-2">
            <Button
              variant="outline"
              class="w-full justify-center"
              @click="saveDraft"
              :loading="isSavingDraft"
            >
              <SaveIcon class="h-4 w-4 mr-2" />
              Save Draft
            </Button>
            <div class="text-xs text-center text-gray-500">
              Draft saved {{ lastSavedText }}
            </div>
          </div>
        </div>

        <!-- Main Content Area -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <!-- Top Navigation -->
          <div class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <div class="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                @click="prevSection"
                :disabled="isFirstSection"
              >
                <ChevronLeftIcon class="h-4 w-4 mr-1" />
                Previous
              </Button>
              <span class="text-sm text-gray-600">
                Step {{ currentSectionIndex }} of {{ sections.length }}
              </span>
              <Button
                variant="ghost"
                size="sm"
                @click="nextSection"
                :disabled="isLastSection"
              >
                Next
                <ChevronRightIcon class="h-4 w-4 ml-1" />
              </Button>
            </div>

            <div class="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                @click="closeForm"
              >
                <XIcon class="h-4 w-4 mr-1" />
                Cancel
              </Button>
              <Button
                variant="solid"
                theme="red"
                size="sm"
                @click="submitForm"
                :loading="isSaving"
                :disabled="!isFormValid"
              >
                <CheckCircleIcon class="h-4 w-4 mr-2" />
                {{ isEditMode ? 'Update Assessment' : 'Create Assessment' }}
              </Button>
            </div>
          </div>

          <!-- Section Content -->
          <div class="flex-1 overflow-y-auto p-6">
            <!-- Section 1: Basic Information -->
            <div v-show="activeSection === 'basic'" class="space-y-6 max-w-4xl">
              <SectionHeader
                title="Basic Information"
                description="Provide essential details about the risk assessment"
                icon="Info"
              />

              <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormControl
                    label="Assessment Name"
                    v-model="form.assessment_name"
                    required
                    placeholder="Enter assessment name"
                    :error="errors.assessment_name"
                    @input="clearError('assessment_name')"
                  />
                  <FormControl
                    label="Assessment Date"
                    type="date"
                    v-model="form.assessment_date"
                    required
                    :error="errors.assessment_date"
                    @input="clearError('assessment_date')"
                  />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Fiscal Year <span class="text-red-500">*</span>
                    </label>
                    <LinkField
                      v-model="form.fiscal_year"
                      doctype="Fiscal Year"
                      placeholder="Select fiscal year"
                      :error="errors.fiscal_year"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Assessment Period <span class="text-red-500">*</span>
                    </label>
                    <Select
                      v-model="form.assessment_period"
                      :options="periodOptions"
                      placeholder="Select period"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Status
                    </label>
                    <Select
                      v-model="form.status"
                      :options="statusOptions"
                      placeholder="Select status"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 2: Scope & Methodology -->
            <div v-show="activeSection === 'scope'" class="space-y-6 max-w-4xl">
              <SectionHeader
                title="Scope & Methodology"
                description="Define the assessment scope and methodologies to be used"
                icon="Target"
              />

              <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
                <FormControl
                  label="Assessment Scope"
                  type="textarea"
                  v-model="form.assessment_scope"
                  placeholder="Describe the scope of this risk assessment..."
                  rows="4"
                  :error="errors.assessment_scope"
                  @input="clearError('assessment_scope')"
                />

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-3">
                    Assessment Methodology
                  </label>
                  <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                    <label
                      v-for="method in methodologyOptions"
                      :key="method.value"
                      class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                      :class="{ 'bg-red-50 border-red-200': isMethodSelected(method.value) }"
                    >
                      <input
                        type="checkbox"
                        :value="method.value"
                        v-model="selectedMethodologies"
                        class="rounded border-gray-300 text-red-600 focus:ring-red-500"
                      />
                      <span class="text-sm font-medium text-gray-700">{{ method.label }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 3: Assessment Team -->
            <div v-show="activeSection === 'team'" class="space-y-6 max-w-4xl">
              <SectionHeader
                title="Assessment Team"
                description="Add team members who will participate in this assessment"
                icon="Users"
              />

              <div class="bg-white rounded-xl border border-gray-200 p-6">
                <InlineChildTable
                  v-model="form.assessment_team"
                  title="Team Members"
                  :columns="teamColumns"
                  :defaultRow="defaultTeamMember"
                  addButtonLabel="Add Team Member"
                />
              </div>
            </div>

            <!-- Section 4: Risk Register -->
            <div v-show="activeSection === 'risks'" class="space-y-6 max-w-5xl">
              <SectionHeader
                title="Risk Register"
                description="Identify and assess risks in this assessment"
                icon="AlertTriangle"
              />

              <!-- Risk Summary Cards -->
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-red-50 rounded-xl border border-red-200 p-4">
                  <p class="text-xs font-semibold text-red-700 uppercase">Critical</p>
                  <p class="text-2xl font-bold text-red-900">{{ riskCounts.critical }}</p>
                </div>
                <div class="bg-orange-50 rounded-xl border border-orange-200 p-4">
                  <p class="text-xs font-semibold text-orange-700 uppercase">High</p>
                  <p class="text-2xl font-bold text-orange-900">{{ riskCounts.high }}</p>
                </div>
                <div class="bg-yellow-50 rounded-xl border border-yellow-200 p-4">
                  <p class="text-xs font-semibold text-yellow-700 uppercase">Medium</p>
                  <p class="text-2xl font-bold text-yellow-900">{{ riskCounts.medium }}</p>
                </div>
                <div class="bg-green-50 rounded-xl border border-green-200 p-4">
                  <p class="text-xs font-semibold text-green-700 uppercase">Low</p>
                  <p class="text-2xl font-bold text-green-900">{{ riskCounts.low }}</p>
                </div>
              </div>

              <div class="bg-white rounded-xl border border-gray-200 p-6">
                <ChildTable
                  v-model="form.risk_register"
                  title="Risk Register"
                  :columns="riskRegisterColumns"
                  :formFields="riskRegisterFormFields"
                  :defaultRow="defaultRiskEntry"
                  addButtonLabel="Add Risk"
                  modalTitle="Risk Entry"
                  @row-click="onRiskRowClick"
                />
              </div>

              <!-- Risk Heat Map Visualization -->
              <div v-if="form.risk_register.length > 0" class="bg-white rounded-xl border border-gray-200 p-6">
                <h4 class="text-lg font-semibold text-gray-900 mb-4">Risk Heat Map</h4>
                <RiskHeatMap
                  :matrixData="computedHeatMapData"
                  :likelihoodLevels="likelihoodLevels"
                  :impactLevels="impactLevels"
                  :selectedRisks="[]"
                  @risk-click="onHeatMapRiskClick"
                />
              </div>
            </div>

            <!-- Section 5: Action Plan -->
            <div v-show="activeSection === 'actions'" class="space-y-6 max-w-5xl">
              <SectionHeader
                title="Action Plan"
                description="Define mitigation actions for identified risks"
                icon="ListChecks"
              />

              <div class="bg-white rounded-xl border border-gray-200 p-6">
                <ChildTable
                  v-model="form.action_plan"
                  title="Mitigation Actions"
                  :columns="actionPlanColumns"
                  :formFields="actionPlanFormFields"
                  :defaultRow="defaultActionEntry"
                  addButtonLabel="Add Action"
                  modalTitle="Action Item"
                />
              </div>

              <!-- Action Summary -->
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-gray-50 rounded-xl border border-gray-200 p-4">
                  <p class="text-xs font-semibold text-gray-600 uppercase">Total Actions</p>
                  <p class="text-2xl font-bold text-gray-900">{{ form.action_plan.length }}</p>
                </div>
                <div class="bg-blue-50 rounded-xl border border-blue-200 p-4">
                  <p class="text-xs font-semibold text-blue-700 uppercase">Planned</p>
                  <p class="text-2xl font-bold text-blue-900">{{ actionCounts.planned }}</p>
                </div>
                <div class="bg-yellow-50 rounded-xl border border-yellow-200 p-4">
                  <p class="text-xs font-semibold text-yellow-700 uppercase">In Progress</p>
                  <p class="text-2xl font-bold text-yellow-900">{{ actionCounts.inProgress }}</p>
                </div>
                <div class="bg-green-50 rounded-xl border border-green-200 p-4">
                  <p class="text-xs font-semibold text-green-700 uppercase">Completed</p>
                  <p class="text-2xl font-bold text-green-900">{{ actionCounts.completed }}</p>
                </div>
              </div>
            </div>

            <!-- Section 6: Summary & Recommendations -->
            <div v-show="activeSection === 'summary'" class="space-y-6 max-w-4xl">
              <SectionHeader
                title="Summary & Recommendations"
                description="Provide overall assessment summary and key recommendations"
                icon="FileText"
              />

              <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
                <!-- Overall Risk Score -->
                <div class="bg-gradient-to-r from-red-50 to-orange-50 rounded-xl p-6 border border-red-200">
                  <div class="flex items-center justify-between mb-4">
                    <div>
                      <h4 class="text-lg font-semibold text-gray-900">Overall Risk Score</h4>
                      <p class="text-sm text-gray-600">Based on identified risks</p>
                    </div>
                    <div class="text-right">
                      <p class="text-3xl font-bold" :class="overallRiskColor">
                        {{ form.overall_risk_score || calculateOverallRiskScore() }}
                      </p>
                      <Badge :variant="overallRiskVariant" size="sm">
                        {{ form.overall_risk_rating || calculateOverallRiskRating() }}
                      </Badge>
                    </div>
                  </div>
                  <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      class="h-full transition-all duration-500"
                      :class="overallRiskBarColor"
                      :style="{ width: `${(form.overall_risk_score || calculateOverallRiskScore()) * 4}%` }"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <FormControl
                    label="Assessment Summary"
                    type="textarea"
                    v-model="form.assessment_summary"
                    placeholder="Summarize the key findings and conclusions..."
                    rows="6"
                  />
                  <FormControl
                    label="Recommendations"
                    type="textarea"
                    v-model="form.recommendations"
                    placeholder="Provide key recommendations based on the assessment..."
                    rows="6"
                  />
                </div>
              </div>

              <!-- Top Risks Summary -->
              <div v-if="topRisks.length > 0" class="bg-white rounded-xl border border-gray-200 p-6">
                <h4 class="text-lg font-semibold text-gray-900 mb-4">Top Risks</h4>
                <div class="space-y-3">
                  <div
                    v-for="(risk, index) in topRisks"
                    :key="risk.risk_id"
                    class="flex items-center gap-4 p-4 rounded-lg border"
                    :class="getRiskBorderClass(risk.inherent_risk_score)"
                  >
                    <div
                      class="h-8 w-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
                      :class="getRiskBgClass(risk.inherent_risk_score)"
                    >
                      {{ index + 1 }}
                    </div>
                    <div class="flex-1">
                      <p class="font-medium text-gray-900">{{ risk.risk_title }}</p>
                      <p class="text-sm text-gray-600">{{ risk.risk_category }}</p>
                    </div>
                    <Badge :variant="getRiskVariant(risk.inherent_risk_score)" size="sm">
                      Score: {{ risk.inherent_risk_score }}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 7: Approvals -->
            <div v-show="activeSection === 'approvals'" class="space-y-6 max-w-4xl">
              <SectionHeader
                title="Approvals"
                description="Track preparation, review, and approval of the assessment"
                icon="UserCheck"
              />

              <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Prepared By
                    </label>
                    <LinkField
                      v-model="form.prepared_by"
                      doctype="User"
                      placeholder="Select preparer"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Reviewed By
                    </label>
                    <LinkField
                      v-model="form.reviewed_by"
                      doctype="User"
                      placeholder="Select reviewer"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Approved By
                    </label>
                    <LinkField
                      v-model="form.approved_by"
                      doctype="User"
                      placeholder="Select approver"
                    />
                  </div>
                </div>

                <!-- Approval Timeline -->
                <div class="border-t border-gray-200 pt-6">
                  <h4 class="text-sm font-semibold text-gray-700 mb-4">Approval Timeline</h4>
                  <div class="relative">
                    <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />
                    <div class="space-y-6">
                      <div class="relative flex items-start gap-4">
                        <div class="h-8 w-8 rounded-full bg-green-100 border-2 border-green-500 flex items-center justify-center z-10">
                          <CheckIcon class="h-4 w-4 text-green-600" />
                        </div>
                        <div>
                          <p class="font-medium text-gray-900">Created</p>
                          <p class="text-sm text-gray-600">{{ formatDate(form.creation) || 'Pending' }}</p>
                        </div>
                      </div>
                      <div class="relative flex items-start gap-4">
                        <div
                          class="h-8 w-8 rounded-full border-2 flex items-center justify-center z-10"
                          :class="form.reviewed_by ? 'bg-green-100 border-green-500' : 'bg-gray-100 border-gray-300'"
                        >
                          <component
                            :is="form.reviewed_by ? CheckIcon : ClockIcon"
                            class="h-4 w-4"
                            :class="form.reviewed_by ? 'text-green-600' : 'text-gray-400'"
                          />
                        </div>
                        <div>
                          <p class="font-medium text-gray-900">Reviewed</p>
                          <p class="text-sm text-gray-600">
                            {{ form.reviewed_by || 'Awaiting review' }}
                          </p>
                        </div>
                      </div>
                      <div class="relative flex items-start gap-4">
                        <div
                          class="h-8 w-8 rounded-full border-2 flex items-center justify-center z-10"
                          :class="form.approved_by ? 'bg-green-100 border-green-500' : 'bg-gray-100 border-gray-300'"
                        >
                          <component
                            :is="form.approved_by ? CheckIcon : ClockIcon"
                            class="h-4 w-4"
                            :class="form.approved_by ? 'text-green-600' : 'text-gray-400'"
                          />
                        </div>
                        <div>
                          <p class="font-medium text-gray-900">Approved</p>
                          <p class="text-sm text-gray-600">
                            {{ form.approved_by || 'Awaiting approval' }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Navigation -->
          <div class="bg-white border-t border-gray-200 px-6 py-4">
            <div class="flex items-center justify-between">
              <Button
                variant="outline"
                @click="prevSection"
                :disabled="isFirstSection"
              >
                <ChevronLeftIcon class="h-4 w-4 mr-2" />
                Previous
              </Button>

              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500">
                  {{ completedSections }} of {{ sections.length }} sections complete
                </span>
              </div>

              <div class="flex items-center gap-3">
                <Button
                  v-if="!isLastSection"
                  variant="solid"
                  theme="gray"
                  @click="nextSection"
                >
                  Next Section
                  <ChevronRightIcon class="h-4 w-4 ml-2" />
                </Button>
                <Button
                  v-else
                  variant="solid"
                  theme="red"
                  @click="submitForm"
                  :loading="isSaving"
                  :disabled="!isFormValid"
                >
                  <CheckCircleIcon class="h-4 w-4 mr-2" />
                  {{ isEditMode ? 'Update Assessment' : 'Create Assessment' }}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import ChildTable from "@/components/Common/ChildTable.vue"
import InlineChildTable from "@/components/Common/InlineChildTable.vue"
import LinkField from "@/components/Common/fields/LinkField.vue"
import SectionHeader from "@/components/Common/SectionHeader.vue"
import RiskHeatMap from "@/components/risk/RiskHeatMap.vue"
import { useMultiSectionForm } from "@/composables/useMultiSectionForm"
import { Badge, Button, Dialog, FormControl, Select } from "frappe-ui"
import {
  AlertCircleIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  CheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ClockIcon,
  SaveIcon,
  XIcon,
} from "lucide-vue-next"
import { computed, reactive, ref, watch } from "vue"

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  assessment: {
    type: Object,
    default: null,
  },
  mode: {
    type: String,
    default: "create", // 'create' or 'edit'
  },
})

// Emits
const emit = defineEmits(["update:modelValue", "submit", "cancel", "save-draft"])

// Dialog state
const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
})

const isEditMode = computed(() => props.mode === "edit")

// Form data
const form = reactive({
  assessment_id: "",
  assessment_name: "",
  assessment_date: new Date().toISOString().split("T")[0],
  fiscal_year: "",
  assessment_period: "Annual",
  status: "Planning",
  assessment_scope: "",
  methodology: "",
  assessment_team: [],
  risk_register: [],
  action_plan: [],
  top_risks: [],
  overall_risk_score: 0,
  overall_risk_rating: "",
  assessment_summary: "",
  recommendations: "",
  prepared_by: "",
  reviewed_by: "",
  approved_by: "",
})

// Selected methodologies (array for checkboxes)
const selectedMethodologies = ref([])

// Section definitions
const sections = [
  {
    id: "basic",
    label: "Basic Information",
    description: "Assessment details",
    requiredFields: ["assessment_name", "assessment_date", "fiscal_year", "assessment_period"],
  },
  {
    id: "scope",
    label: "Scope & Methodology",
    description: "Assessment scope",
    requiredFields: ["assessment_scope"],
  },
  {
    id: "team",
    label: "Assessment Team",
    description: "Team members",
    requiredFields: [],
  },
  {
    id: "risks",
    label: "Risk Register",
    description: "Identified risks",
    requiredFields: [],
  },
  {
    id: "actions",
    label: "Action Plan",
    description: "Mitigation actions",
    requiredFields: [],
  },
  {
    id: "summary",
    label: "Summary",
    description: "Assessment summary",
    requiredFields: [],
  },
  {
    id: "approvals",
    label: "Approvals",
    description: "Review & approval",
    requiredFields: [],
  },
]

// Child table configurations
const childTables = {
  assessment_team: "Assessment Team Member",
  risk_register: "Risk Assessment Register",
  action_plan: "Risk Assessment Action",
}

// Validation function
const validateSection = (sectionId, formData) => {
  const errors = {}
  const section = sections.find((s) => s.id === sectionId)

  if (!section) return errors

  for (const field of section.requiredFields || []) {
    const value = formData[field]
    if (!value || (Array.isArray(value) && value.length === 0)) {
      errors[field] = `${field.replace(/_/g, " ")} is required`
    }
  }

  return errors
}

// Use the multi-section form composable
const {
  activeSection,
  errors,
  isSaving,
  isSavingDraft,
  hasUnsavedChanges,
  completedSections,
  formProgress,
  isFormValid,
  isFirstSection,
  isLastSection,
  currentSectionIndex,
  getSectionStatus,
  getSectionStatusClass,
  navigateToSection,
  nextSection,
  prevSection,
  clearError,
  clearAllErrors,
  prepareFormData,
  resetForm,
  loadFormData,
} = useMultiSectionForm({
  sections,
  form,
  validateSection,
  childTables,
})

// Options
const periodOptions = [
  { label: "Annual", value: "Annual" },
  { label: "Mid-Year", value: "Mid-Year" },
  { label: "Quarterly", value: "Quarterly" },
  { label: "Ad-hoc", value: "Ad-hoc" },
]

const statusOptions = [
  { label: "Planning", value: "Planning" },
  { label: "In Progress", value: "In Progress" },
  { label: "Review", value: "Review" },
  { label: "Finalized", value: "Finalized" },
  { label: "Approved", value: "Approved" },
]

const methodologyOptions = [
  { label: "Interview", value: "Interview" },
  { label: "Workshop", value: "Workshop" },
  { label: "Survey", value: "Survey" },
  { label: "Document Review", value: "Document Review" },
  { label: "Data Analysis", value: "Data Analysis" },
  { label: "Self-Assessment", value: "Self-Assessment" },
]

// Team member columns
const teamColumns = [
  { key: "team_member", label: "Team Member", type: "link", doctype: "User" },
  { key: "role", label: "Role", type: "select", options: ["Lead", "Member", "Observer", "SME"] },
]

const defaultTeamMember = {
  team_member: "",
  role: "Member",
}

// Risk register columns (simplified for table display)
const riskRegisterColumns = [
  { key: "risk_id", label: "Risk ID", width: "100px" },
  { key: "risk_title", label: "Risk Title" },
  { key: "risk_category", label: "Category", width: "120px" },
  { key: "likelihood_score", label: "Likelihood", width: "90px" },
  { key: "impact_score", label: "Impact", width: "80px" },
  { key: "inherent_risk_score", label: "Score", width: "80px", computed: true },
  { key: "inherent_risk_rating", label: "Rating", width: "100px" },
]

// Risk register form fields (for modal - 24 fields)
const riskRegisterFormFields = [
  { key: "risk_id", label: "Risk ID", type: "text", required: true },
  { key: "risk_title", label: "Risk Title", type: "text", required: true },
  { key: "risk_description", label: "Risk Description", type: "textarea", required: true },
  { key: "risk_category", label: "Category", type: "select", options: [
    "Strategic", "Operational", "Financial", "Compliance", "Technology", "Reputational"
  ], required: true },
  { key: "risk_subcategory", label: "Subcategory", type: "text" },
  { key: "auditable_entity", label: "Auditable Entity", type: "link", doctype: "Audit Universe Entity" },
  { key: "threat_source", label: "Threat Source", type: "text" },
  { key: "vulnerability", label: "Vulnerability", type: "textarea" },
  { key: "likelihood_score", label: "Likelihood Score (1-5)", type: "rating", required: true },
  { key: "likelihood_rationale", label: "Likelihood Rationale", type: "textarea" },
  { key: "impact_score", label: "Impact Score (1-5)", type: "rating", required: true },
  { key: "impact_rationale", label: "Impact Rationale", type: "textarea" },
  { key: "control_effectiveness", label: "Control Effectiveness", type: "select", options: [
    "Strong", "Adequate", "Weak", "Non-existent"
  ] },
  { key: "existing_controls", label: "Existing Controls", type: "textarea" },
  { key: "residual_likelihood", label: "Residual Likelihood (1-5)", type: "rating" },
  { key: "residual_impact", label: "Residual Impact (1-5)", type: "rating" },
  { key: "risk_owner", label: "Risk Owner", type: "link", doctype: "User" },
  { key: "risk_response", label: "Risk Response", type: "select", options: [
    "Accept", "Mitigate", "Transfer", "Avoid"
  ] },
  { key: "target_risk_score", label: "Target Risk Score", type: "number" },
  { key: "risk_velocity", label: "Risk Velocity", type: "select", options: [
    "Very Slow", "Slow", "Medium", "Fast", "Very Fast"
  ] },
  { key: "risk_trend", label: "Risk Trend", type: "select", options: [
    "Increasing", "Stable", "Decreasing"
  ] },
  { key: "last_review_date", label: "Last Review Date", type: "date" },
  { key: "next_review_date", label: "Next Review Date", type: "date" },
  { key: "notes", label: "Notes", type: "textarea" },
]

const defaultRiskEntry = {
  risk_id: "",
  risk_title: "",
  risk_description: "",
  risk_category: "",
  risk_subcategory: "",
  auditable_entity: "",
  threat_source: "",
  vulnerability: "",
  likelihood_score: 3,
  likelihood_rationale: "",
  impact_score: 3,
  impact_rationale: "",
  inherent_risk_score: 9,
  inherent_risk_rating: "Medium",
  control_effectiveness: "Adequate",
  existing_controls: "",
  residual_likelihood: 0,
  residual_impact: 0,
  residual_risk_score: 0,
  residual_risk_rating: "",
  risk_owner: "",
  risk_response: "Mitigate",
  target_risk_score: 0,
  risk_velocity: "Medium",
  risk_trend: "Stable",
  last_review_date: "",
  next_review_date: "",
  notes: "",
}

// Action plan columns
const actionPlanColumns = [
  { key: "action_id", label: "Action ID", width: "100px" },
  { key: "action_description", label: "Description" },
  { key: "responsible_party", label: "Responsible", width: "150px" },
  { key: "target_completion_date", label: "Due Date", width: "120px" },
  { key: "priority", label: "Priority", width: "100px" },
  { key: "status", label: "Status", width: "120px" },
]

// Action plan form fields (12 fields)
const actionPlanFormFields = [
  { key: "action_id", label: "Action ID", type: "text", required: true },
  { key: "action_description", label: "Action Description", type: "textarea", required: true },
  { key: "action_type", label: "Action Type", type: "select", options: [
    "Process Improvement", "Control Enhancement", "Training", "System Enhancement", "Policy Update"
  ] },
  { key: "priority", label: "Priority", type: "select", options: ["Low", "Medium", "High", "Critical"], required: true },
  { key: "responsible_party", label: "Responsible Party", type: "link", doctype: "User", required: true },
  { key: "target_completion_date", label: "Target Completion Date", type: "date", required: true },
  { key: "estimated_cost", label: "Estimated Cost", type: "currency" },
  { key: "resource_required", label: "Resources Required", type: "text" },
  { key: "status", label: "Status", type: "select", options: [
    "Planned", "In Progress", "Completed", "Overdue", "Cancelled"
  ] },
  { key: "actual_completion_date", label: "Actual Completion Date", type: "date" },
  { key: "effectiveness_review_date", label: "Effectiveness Review Date", type: "date" },
  { key: "review_notes", label: "Review Notes", type: "textarea" },
]

const defaultActionEntry = {
  action_id: "",
  action_description: "",
  action_type: "",
  priority: "Medium",
  responsible_party: "",
  target_completion_date: "",
  estimated_cost: 0,
  resource_required: "",
  status: "Planned",
  actual_completion_date: "",
  effectiveness_review_date: "",
  review_notes: "",
}

// Likelihood and impact levels for heat map
const likelihoodLevels = [
  { id: 1, label: "Rare", description: "Unlikely to occur" },
  { id: 2, label: "Unlikely", description: "Could occur occasionally" },
  { id: 3, label: "Possible", description: "Might occur sometime" },
  { id: 4, label: "Likely", description: "Will probably occur" },
  { id: 5, label: "Almost Certain", description: "Expected to occur" },
]

const impactLevels = [
  { id: 1, label: "Negligible", description: "Minimal impact" },
  { id: 2, label: "Minor", description: "Some minor issues" },
  { id: 3, label: "Moderate", description: "Noticeable impact" },
  { id: 4, label: "Major", description: "Significant impact" },
  { id: 5, label: "Catastrophic", description: "Severe impact" },
]

// Draft save state
const lastSaved = ref(null)
const lastSavedText = computed(() => {
  if (!lastSaved.value) return "not yet saved"
  const diff = Date.now() - lastSaved.value
  if (diff < 60000) return "just now"
  if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`
  return "over an hour ago"
})

// Computed properties
const riskCounts = computed(() => {
  const counts = { critical: 0, high: 0, medium: 0, low: 0 }
  form.risk_register.forEach((risk) => {
    const score = risk.inherent_risk_score || (risk.likelihood_score * risk.impact_score)
    if (score >= 20) counts.critical++
    else if (score >= 15) counts.high++
    else if (score >= 10) counts.medium++
    else counts.low++
  })
  return counts
})

const actionCounts = computed(() => {
  const counts = { planned: 0, inProgress: 0, completed: 0 }
  form.action_plan.forEach((action) => {
    if (action.status === "Planned") counts.planned++
    else if (action.status === "In Progress") counts.inProgress++
    else if (action.status === "Completed") counts.completed++
  })
  return counts
})

const topRisks = computed(() => {
  return [...form.risk_register]
    .map((risk) => ({
      ...risk,
      inherent_risk_score: risk.inherent_risk_score || (risk.likelihood_score * risk.impact_score),
    }))
    .sort((a, b) => b.inherent_risk_score - a.inherent_risk_score)
    .slice(0, 5)
})

const computedHeatMapData = computed(() => {
  // Transform risk_register into heat map matrix format
  const matrix = []
  for (let i = 5; i >= 1; i--) {
    const row = []
    for (let j = 1; j <= 5; j++) {
      const risksInCell = form.risk_register.filter(
        (r) => r.likelihood_score === j && r.impact_score === i
      )
      const score = i * j
      let level = "Low"
      let color = "#22c55e"
      if (score >= 20) { level = "Critical"; color = "#ef4444" }
      else if (score >= 15) { level = "High"; color = "#f97316" }
      else if (score >= 10) { level = "Medium"; color = "#eab308" }

      row.push({
        likelihood: j,
        impact: i,
        level,
        color,
        count: risksInCell.length,
        risks: risksInCell,
      })
    }
    matrix.push(row)
  }
  return matrix
})

const overallRiskColor = computed(() => {
  const score = form.overall_risk_score || calculateOverallRiskScore()
  if (score >= 20) return "text-red-600"
  if (score >= 15) return "text-orange-600"
  if (score >= 10) return "text-yellow-600"
  return "text-green-600"
})

const overallRiskVariant = computed(() => {
  const score = form.overall_risk_score || calculateOverallRiskScore()
  if (score >= 20) return "destructive"
  if (score >= 15) return "warning"
  if (score >= 10) return "secondary"
  return "success"
})

const overallRiskBarColor = computed(() => {
  const score = form.overall_risk_score || calculateOverallRiskScore()
  if (score >= 20) return "bg-red-500"
  if (score >= 15) return "bg-orange-500"
  if (score >= 10) return "bg-yellow-500"
  return "bg-green-500"
})

// Methods
const isMethodSelected = (method) => {
  return selectedMethodologies.value.includes(method)
}

const calculateOverallRiskScore = () => {
  if (form.risk_register.length === 0) return 0
  const total = form.risk_register.reduce((sum, risk) => {
    return sum + (risk.inherent_risk_score || (risk.likelihood_score * risk.impact_score))
  }, 0)
  return Math.round(total / form.risk_register.length)
}

const calculateOverallRiskRating = () => {
  const score = calculateOverallRiskScore()
  if (score >= 20) return "Critical"
  if (score >= 15) return "High"
  if (score >= 10) return "Medium"
  return "Low"
}

const getRiskVariant = (score) => {
  if (score >= 20) return "destructive"
  if (score >= 15) return "warning"
  if (score >= 10) return "secondary"
  return "success"
}

const getRiskBorderClass = (score) => {
  if (score >= 20) return "border-red-200 bg-red-50"
  if (score >= 15) return "border-orange-200 bg-orange-50"
  if (score >= 10) return "border-yellow-200 bg-yellow-50"
  return "border-green-200 bg-green-50"
}

const getRiskBgClass = (score) => {
  if (score >= 20) return "bg-red-500"
  if (score >= 15) return "bg-orange-500"
  if (score >= 10) return "bg-yellow-500"
  return "bg-green-500"
}

const formatDate = (dateString) => {
  if (!dateString) return null
  return new Date(dateString).toLocaleDateString()
}

const onRiskRowClick = (risk) => {
  console.log("Risk clicked:", risk)
}

const onHeatMapRiskClick = (risk) => {
  console.log("Heat map risk clicked:", risk)
}

const saveDraft = async () => {
  isSavingDraft.value = true
  try {
    // Update methodology string from array
    form.methodology = selectedMethodologies.value.join(", ")
    
    const formData = prepareFormData()
    emit("save-draft", formData)
    lastSaved.value = Date.now()
  } catch (error) {
    console.error("Error saving draft:", error)
  } finally {
    isSavingDraft.value = false
  }
}

const submitForm = async () => {
  isSaving.value = true
  try {
    // Update methodology string from array
    form.methodology = selectedMethodologies.value.join(", ")
    
    // Calculate risk scores before submission
    form.risk_register.forEach((risk) => {
      risk.inherent_risk_score = risk.likelihood_score * risk.impact_score
      risk.inherent_risk_rating = getRiskRatingFromScore(risk.inherent_risk_score)
      if (risk.residual_likelihood && risk.residual_impact) {
        risk.residual_risk_score = risk.residual_likelihood * risk.residual_impact
        risk.residual_risk_rating = getRiskRatingFromScore(risk.residual_risk_score)
      }
    })

    // Update overall scores
    form.overall_risk_score = calculateOverallRiskScore()
    form.overall_risk_rating = calculateOverallRiskRating()

    // Update top risks
    form.top_risks = topRisks.value.map((risk) => ({
      risk_description: risk.risk_title,
      inherent_risk_score: risk.inherent_risk_score,
    }))

    const formData = prepareFormData()
    emit("submit", formData)
    isOpen.value = false
  } catch (error) {
    console.error("Error submitting form:", error)
  } finally {
    isSaving.value = false
  }
}

const getRiskRatingFromScore = (score) => {
  if (score >= 20) return "Critical"
  if (score >= 15) return "High"
  if (score >= 10) return "Medium"
  return "Low"
}

const closeForm = () => {
  if (hasUnsavedChanges.value) {
    if (confirm("You have unsaved changes. Are you sure you want to close?")) {
      emit("cancel")
      isOpen.value = false
    }
  } else {
    emit("cancel")
    isOpen.value = false
  }
}

// Watch for assessment prop changes (edit mode)
watch(
  () => props.assessment,
  (newAssessment) => {
    if (newAssessment) {
      loadFormData(newAssessment)
      // Parse methodology string back to array
      if (newAssessment.methodology) {
        selectedMethodologies.value = newAssessment.methodology.split(", ").filter(Boolean)
      }
    }
  },
  { immediate: true }
)

// Watch methodologies to update form
watch(
  selectedMethodologies,
  (newMethods) => {
    form.methodology = newMethods.join(", ")
  },
  { deep: true }
)
</script>

<style scoped>
/* Custom scrollbar for sidebar */
nav::-webkit-scrollbar {
  width: 4px;
}

nav::-webkit-scrollbar-track {
  background: transparent;
}

nav::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 2px;
}

nav::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
