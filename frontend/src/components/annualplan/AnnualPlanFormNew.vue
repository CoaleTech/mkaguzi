<template>
  <Dialog
    v-model="isOpen"
    :options="{
      title: isEditMode ? 'Edit Annual Audit Plan' : 'Create Annual Audit Plan',
      size: 'full'
    }"
  >
    <template #body-content>
      <div class="h-[80vh] flex">
        <!-- Progress Sidebar -->
        <div class="w-64 bg-gray-50 border-r border-gray-200 flex-shrink-0 overflow-y-auto">
          <div class="p-5">
            <h4 class="text-sm font-semibold text-gray-900 mb-4">Form Sections</h4>
            <nav class="space-y-1">
              <button
                v-for="(section, index) in formSections"
                :key="section.id"
                @click="activeSection = section.id"
                class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-all"
                :class="[
                  activeSection === section.id
                    ? 'bg-blue-100 border border-blue-300 text-blue-800'
                    : 'hover:bg-gray-100 text-gray-700'
                ]"
              >
                <div
                  class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0"
                  :class="getSectionStatusClass(section.id)"
                >
                  <CheckIcon v-if="getSectionStatus(section.id) === 'complete'" class="h-3 w-3" />
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium truncate">{{ section.label }}</div>
                  <div class="text-xs text-gray-500">{{ section.description }}</div>
                </div>
              </button>
            </nav>

            <!-- Progress Summary -->
            <div class="mt-6 p-4 bg-white rounded-lg border border-gray-200">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Progress</span>
                <span class="text-sm font-bold text-blue-600">{{ formProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${formProgress}%` }"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-2">
                {{ completedSections }} of {{ formSections.length }} sections complete
              </p>
            </div>
          </div>
        </div>

        <!-- Main Form Content -->
        <div class="flex-1 overflow-y-auto">
          <div class="p-6 max-w-5xl mx-auto">
            <!-- Section: Basic Information -->
            <div v-show="activeSection === 'basic'" class="space-y-6">
              <SectionHeader
                title="Basic Information"
                description="Essential plan details and identification"
                icon="calendar"
                step="1"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <!-- Plan Title -->
                  <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Plan Title <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="form.plan_title"
                      type="text"
                      placeholder="e.g., Annual Audit Plan 2025"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                      :class="errors.plan_title ? 'border-red-300' : 'border-gray-300'"
                    />
                    <p v-if="errors.plan_title" class="mt-1 text-xs text-red-500">{{ errors.plan_title }}</p>
                  </div>

                  <!-- Fiscal Year -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Fiscal Year <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="form.fiscal_year"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      :class="errors.fiscal_year ? 'border-red-300' : 'border-gray-300'"
                    >
                      <option v-for="year in fiscalYearOptions" :key="year" :value="year">{{ year }}</option>
                    </select>
                    <p v-if="errors.fiscal_year" class="mt-1 text-xs text-red-500">{{ errors.fiscal_year }}</p>
                  </div>
                </div>

                <!-- Status and Dates Row -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mt-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Status <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="form.status"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Plan Period
                    </label>
                    <select
                      v-model="form.plan_period"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option v-for="opt in periodOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Plan Start Date <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="form.plan_start_date"
                      type="date"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      :class="errors.plan_start_date ? 'border-red-300' : 'border-gray-300'"
                    />
                    <p v-if="errors.plan_start_date" class="mt-1 text-xs text-red-500">{{ errors.plan_start_date }}</p>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Plan End Date <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="form.plan_end_date"
                      type="date"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      :class="errors.plan_end_date ? 'border-red-300' : 'border-gray-300'"
                    />
                    <p v-if="errors.plan_end_date" class="mt-1 text-xs text-red-500">{{ errors.plan_end_date }}</p>
                  </div>
                </div>

                <!-- Plan Owner -->
                <div class="mt-6 max-w-md">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Plan Owner
                  </label>
                  <LinkField
                    v-model="form.plan_owner"
                    doctype="User"
                    :filters="{ enabled: 1 }"
                    placeholder="Select plan owner"
                  />
                </div>
              </div>
            </div>

            <!-- Section: Overview -->
            <div v-show="activeSection === 'overview'" class="space-y-6">
              <SectionHeader
                title="Plan Overview"
                description="Executive summary, objectives, scope, and methodology"
                icon="file-text"
                step="2"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Executive Summary -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Executive Summary <span class="text-red-500">*</span>
                  </label>
                  <textarea
                    v-model="form.executive_summary"
                    rows="4"
                    placeholder="Provide a high-level summary of the annual audit plan..."
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                    :class="errors.executive_summary ? 'border-red-300' : 'border-gray-300'"
                  ></textarea>
                  <p v-if="errors.executive_summary" class="mt-1 text-xs text-red-500">{{ errors.executive_summary }}</p>
                </div>

                <!-- Objectives -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Objectives <span class="text-red-500">*</span>
                  </label>
                  <textarea
                    v-model="form.objectives"
                    rows="4"
                    placeholder="Define the primary objectives of this audit plan..."
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                    :class="errors.objectives ? 'border-red-300' : 'border-gray-300'"
                  ></textarea>
                  <p v-if="errors.objectives" class="mt-1 text-xs text-red-500">{{ errors.objectives }}</p>
                </div>

                <!-- Scope -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Scope
                  </label>
                  <textarea
                    v-model="form.scope"
                    rows="4"
                    placeholder="Define the boundaries and areas covered by this audit plan..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  ></textarea>
                </div>

                <!-- Methodology -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Methodology
                  </label>
                  <textarea
                    v-model="form.methodology"
                    rows="4"
                    placeholder="Describe the audit approach and methodology..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Section: Resources -->
            <div v-show="activeSection === 'resources'" class="space-y-6">
              <SectionHeader
                title="Resource Allocation"
                description="Team members, roles, and capacity planning"
                icon="users"
                step="3"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <!-- Resource Allocation Child Table - Inline Editable -->
                <InlineChildTable
                  v-model="form.resource_allocation"
                  title="Team Resources"
                  modal-title="Resource"
                  :columns="resourceColumns"
                  :validate="validateResource"
                  :auto-add-row="true"
                />

                <!-- Capacity Summary -->
                <div class="mt-6 border-t border-gray-200 pt-6">
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-blue-50 rounded-lg p-4">
                      <h5 class="text-sm font-medium text-blue-800 mb-1">Total Available Days</h5>
                      <input
                        v-model.number="form.total_available_days"
                        type="number"
                        min="0"
                        placeholder="0"
                        class="w-full px-2 py-1.5 text-sm border border-blue-200 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div class="bg-amber-50 rounded-lg p-4">
                      <h5 class="text-sm font-medium text-amber-800 mb-1">Total Planned Days</h5>
                      <input
                        v-model.number="form.total_planned_days"
                        type="number"
                        min="0"
                        placeholder="0"
                        class="w-full px-2 py-1.5 text-sm border border-amber-200 rounded focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                      />
                    </div>
                    <div class="bg-green-50 rounded-lg p-4">
                      <h5 class="text-sm font-medium text-green-800 mb-1">Utilization %</h5>
                      <div class="text-2xl font-bold text-green-700">
                        {{ utilizationPercentage }}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Planned Audits -->
            <div v-show="activeSection === 'audits'" class="space-y-6">
              <SectionHeader
                title="Planned Audits"
                description="Schedule and prioritize audit engagements"
                icon="clipboard-list"
                step="4"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <!-- Planned Audits Child Table - Inline Editable -->
                <InlineChildTable
                  v-model="form.planned_audits"
                  title="Audit Schedule"
                  modal-title="Planned Audit"
                  :columns="auditColumns"
                  :validate="validateAudit"
                  :auto-add-row="true"
                  :required="true"
                />
              </div>
            </div>

            <!-- Section: Budget -->
            <div v-show="activeSection === 'budget'" class="space-y-6">
              <SectionHeader
                title="Budget Information"
                description="Financial allocation and tracking"
                icon="dollar-sign"
                step="5"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Budget Fields -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Total Budget
                    </label>
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                      <input
                        v-model.number="form.total_budget"
                        type="number"
                        min="0"
                        step="1000"
                        placeholder="0.00"
                        class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Allocated Budget
                    </label>
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                      <input
                        v-model.number="form.allocated_budget"
                        type="number"
                        min="0"
                        step="1000"
                        placeholder="0.00"
                        class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Actual Spend
                    </label>
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                      <input
                        v-model.number="form.actual_spend"
                        type="number"
                        min="0"
                        step="100"
                        placeholder="0.00"
                        class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                <!-- Budget Utilization Bar -->
                <div class="bg-gray-50 rounded-lg p-4">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">Budget Utilization</span>
                    <span class="text-sm font-bold" :class="budgetUtilizationClass">{{ budgetUtilization }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-3">
                    <div
                      class="h-3 rounded-full transition-all duration-300"
                      :class="budgetUtilizationBarClass"
                      :style="{ width: `${Math.min(budgetUtilization, 100)}%` }"
                    ></div>
                  </div>
                </div>

                <!-- Budget Notes -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Budget Notes
                  </label>
                  <textarea
                    v-model="form.budget_notes"
                    rows="3"
                    placeholder="Additional budget notes or comments..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Section: Risk -->
            <div v-show="activeSection === 'risk'" class="space-y-6">
              <SectionHeader
                title="Risk Considerations"
                description="Key risks and mitigation strategies"
                icon="alert-triangle"
                step="6"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Key Risks -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Key Risks
                  </label>
                  <textarea
                    v-model="form.key_risks"
                    rows="4"
                    placeholder="Identify key risks that may impact the audit plan..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  ></textarea>
                </div>

                <!-- Risk Mitigation Strategies -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Risk Mitigation Strategies
                  </label>
                  <textarea
                    v-model="form.risk_mitigation"
                    rows="4"
                    placeholder="Describe strategies to mitigate identified risks..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Section: Contingency -->
            <div v-show="activeSection === 'contingency'" class="space-y-6">
              <SectionHeader
                title="Contingency Planning"
                description="Backup plans and contingency budget"
                icon="shield"
                step="7"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Contingency Plan -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Contingency Plan
                  </label>
                  <textarea
                    v-model="form.contingency_plan"
                    rows="4"
                    placeholder="Describe contingency measures and backup plans..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  ></textarea>
                </div>

                <!-- Contingency Budget -->
                <div class="max-w-md">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Contingency Budget
                  </label>
                  <div class="relative">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                    <input
                      v-model.number="form.contingency_budget"
                      type="number"
                      min="0"
                      step="1000"
                      placeholder="0.00"
                      class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Additional -->
            <div v-show="activeSection === 'additional'" class="space-y-6">
              <SectionHeader
                title="Additional Information"
                description="Notes and supplementary details"
                icon="info"
                step="8"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Additional Notes -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Additional Notes
                  </label>
                  <textarea
                    v-model="form.additional_notes"
                    rows="5"
                    placeholder="Any additional information or comments..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Section: Review -->
            <div v-show="activeSection === 'review'" class="space-y-6">
              <SectionHeader
                title="Review & Submit"
                description="Review your plan before saving"
                icon="check-circle"
                step="9"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <!-- Validation Summary -->
                <div class="space-y-4">
                  <h4 class="font-semibold text-gray-900">Validation Checklist</h4>
                  
                  <div class="space-y-2">
                    <div 
                      v-for="check in validationChecks" 
                      :key="check.label"
                      class="flex items-center space-x-3 p-3 rounded-lg"
                      :class="check.valid ? 'bg-green-50' : 'bg-red-50'"
                    >
                      <div 
                        class="w-6 h-6 rounded-full flex items-center justify-center"
                        :class="check.valid ? 'bg-green-500 text-white' : 'bg-red-500 text-white'"
                      >
                        <CheckIcon v-if="check.valid" class="h-4 w-4" />
                        <XIcon v-else class="h-4 w-4" />
                      </div>
                      <span :class="check.valid ? 'text-green-800' : 'text-red-800'">
                        {{ check.label }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Plan Summary -->
                <div class="mt-6 border-t border-gray-200 pt-6">
                  <h4 class="font-semibold text-gray-900 mb-4">Plan Summary</h4>
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="bg-gray-50 rounded-lg p-4">
                      <p class="text-xs text-gray-500">Fiscal Year</p>
                      <p class="text-lg font-semibold text-gray-900">{{ form.fiscal_year }}</p>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-4">
                      <p class="text-xs text-gray-500">Planned Audits</p>
                      <p class="text-lg font-semibold text-gray-900">{{ form.planned_audits?.length || 0 }}</p>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-4">
                      <p class="text-xs text-gray-500">Team Members</p>
                      <p class="text-lg font-semibold text-gray-900">{{ form.resource_allocation?.length || 0 }}</p>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-4">
                      <p class="text-xs text-gray-500">Total Budget</p>
                      <p class="text-lg font-semibold text-gray-900">${{ formatNumber(form.total_budget) }}</p>
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
        <!-- Left: Status and Navigation -->
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2">
            <div
              class="w-3 h-3 rounded-full"
              :class="isFormValid ? 'bg-green-500' : 'bg-amber-500'"
            ></div>
            <span class="text-sm font-medium" :class="isFormValid ? 'text-green-700' : 'text-amber-700'">
              {{ isFormValid ? 'Ready to save' : 'Complete required fields' }}
            </span>
          </div>

          <!-- Section Navigation -->
          <div class="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              :disabled="currentSectionIndex === 0"
              @click="goToPreviousSection"
            >
              <ChevronLeftIcon class="h-4 w-4 mr-1" />
              Previous
            </Button>
            <Button
              variant="ghost"
              size="sm"
              :disabled="currentSectionIndex === formSections.length - 1"
              @click="goToNextSection"
            >
              Next
              <ChevronRightIcon class="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>

        <!-- Right: Action Buttons -->
        <div class="flex items-center space-x-3">
          <Button variant="outline" @click="handleCancel" :disabled="isSaving">
            Cancel
          </Button>
          <Button
            v-if="!isEditMode"
            variant="outline"
            theme="gray"
            @click="saveAsDraft"
            :loading="isSavingDraft"
            :disabled="isSaving"
          >
            Save as Draft
          </Button>
          <Button
            variant="solid"
            theme="blue"
            @click="handleSubmit"
            :loading="isSaving"
          >
            <template #prefix>
              <PlusIcon v-if="!isEditMode" class="h-4 w-4" />
              <CheckIcon v-else class="h-4 w-4" />
            </template>
            {{ isEditMode ? 'Update Plan' : 'Create Plan' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { Button, Dialog } from "frappe-ui"
import {
	CheckIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	PlusIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, onMounted, reactive, ref, watch } from "vue"

// Import custom components
import InlineChildTable from "@/components/Common/InlineChildTable.vue"
import LinkField from "@/components/Common/fields/LinkField.vue"
import SectionHeader from "@/components/engagement/EngagementSectionHeader.vue"

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
const emit = defineEmits([
	"update:modelValue",
	"created",
	"updated",
	"cancelled",
])

// Dialog visibility
const isOpen = computed({
	get: () => props.modelValue,
	set: (val) => emit("update:modelValue", val),
})

// Edit mode detection
const isEditMode = computed(() => !!props.plan?.name)

// Form Sections
const formSections = [
	{ id: "basic", label: "Basic Information", description: "Core details" },
	{
		id: "overview",
		label: "Plan Overview",
		description: "Summary & objectives",
	},
	{ id: "resources", label: "Resources", description: "Team allocation" },
	{ id: "audits", label: "Planned Audits", description: "Audit schedule" },
	{ id: "budget", label: "Budget", description: "Financial planning" },
	{ id: "risk", label: "Risk", description: "Risk considerations" },
	{ id: "contingency", label: "Contingency", description: "Backup plans" },
	{ id: "additional", label: "Additional", description: "Notes & extras" },
	{ id: "review", label: "Review & Submit", description: "Final review" },
]

const activeSection = ref("basic")

// Form State
const form = reactive({
	// Basic Information
	plan_title: "",
	fiscal_year: new Date().getFullYear().toString(),
	status: "Draft",
	plan_period: "Annual",
	plan_start_date: "",
	plan_end_date: "",
	plan_owner: "",

	// Overview
	executive_summary: "",
	objectives: "",
	scope: "",
	methodology: "",

	// Resources
	resource_allocation: [],
	total_available_days: 0,
	total_planned_days: 0,

	// Planned Audits
	planned_audits: [],

	// Budget
	total_budget: 0,
	allocated_budget: 0,
	actual_spend: 0,
	budget_notes: "",

	// Risk
	key_risks: "",
	risk_mitigation: "",

	// Contingency
	contingency_plan: "",
	contingency_budget: 0,

	// Additional
	additional_notes: "",
})

const errors = reactive({})
const isSaving = ref(false)
const isSavingDraft = ref(false)

// Options
const fiscalYearOptions = computed(() => {
	const currentYear = new Date().getFullYear()
	return [currentYear - 1, currentYear, currentYear + 1, currentYear + 2].map(
		String,
	)
})

const statusOptions = [
	{ label: "Draft", value: "Draft" },
	{ label: "Pending Approval", value: "Pending Approval" },
	{ label: "Approved", value: "Approved" },
	{ label: "Active", value: "Active" },
	{ label: "Completed", value: "Completed" },
	{ label: "Archived", value: "Archived" },
]

const periodOptions = [
	{ label: "Annual", value: "Annual" },
	{ label: "Semi-Annual", value: "Semi-Annual" },
	{ label: "Quarterly", value: "Quarterly" },
]

// Inline Columns for Resource Allocation
const resourceColumns = [
	{
		key: "team_member",
		label: "Team Member",
		width: "200px",
		fieldType: "text",
		required: true,
		placeholder: "Enter name",
	},
	{
		key: "role",
		label: "Role",
		width: "150px",
		fieldType: "select",
		options: [
			{ label: "Chief Audit Executive", value: "Chief Audit Executive" },
			{ label: "Audit Manager", value: "Audit Manager" },
			{ label: "Senior Auditor", value: "Senior Auditor" },
			{ label: "Staff Auditor", value: "Staff Auditor" },
			{ label: "IT Auditor", value: "IT Auditor" },
			{ label: "External Consultant", value: "External Consultant" },
		],
		required: true,
	},
	{
		key: "allocated_hours",
		label: "Hours",
		width: "100px",
		fieldType: "number",
		placeholder: "0",
	},
	{
		key: "availability",
		label: "Availability",
		width: "120px",
		fieldType: "select",
		options: [
			{ label: "Full-time", value: "Full-time" },
			{ label: "Part-time", value: "Part-time" },
			{ label: "Contract", value: "Contract" },
		],
		defaultValue: "Full-time",
	},
]

const validateResource = (data) => {
	const errs = {}
	if (!data.team_member) errs.team_member = "Team member is required"
	if (!data.role) errs.role = "Role is required"
	return Object.keys(errs).length ? errs : null
}

// Inline Columns for Planned Audits
const auditColumns = [
	{
		key: "audit_name",
		label: "Audit Name",
		width: "200px",
		fieldType: "text",
		required: true,
		placeholder: "Enter audit name",
	},
	{
		key: "audit_type",
		label: "Type",
		width: "130px",
		fieldType: "select",
		options: [
			{ label: "Financial", value: "Financial" },
			{ label: "Operational", value: "Operational" },
			{ label: "Compliance", value: "Compliance" },
			{ label: "IT", value: "IT" },
			{ label: "Performance", value: "Performance" },
			{ label: "Integrated", value: "Integrated" },
		],
		required: true,
	},
	{
		key: "quarter",
		label: "Quarter",
		width: "90px",
		fieldType: "select",
		options: [
			{ label: "Q1", value: "Q1" },
			{ label: "Q2", value: "Q2" },
			{ label: "Q3", value: "Q3" },
			{ label: "Q4", value: "Q4" },
		],
		required: true,
	},
	{
		key: "planned_start_date",
		label: "Start Date",
		width: "130px",
		fieldType: "date",
	},
	{
		key: "planned_end_date",
		label: "End Date",
		width: "130px",
		fieldType: "date",
	},
	{
		key: "priority",
		label: "Priority",
		width: "110px",
		fieldType: "select",
		options: [
			{ label: "Low", value: "Low" },
			{ label: "Medium", value: "Medium" },
			{ label: "High", value: "High" },
			{ label: "Critical", value: "Critical" },
		],
		defaultValue: "Medium",
		component: "Badge",
		badgeTheme: {
			Low: "gray",
			Medium: "blue",
			High: "orange",
			Critical: "red",
		},
	},
	{
		key: "status",
		label: "Status",
		width: "110px",
		fieldType: "select",
		options: [
			{ label: "Planned", value: "Planned" },
			{ label: "In Progress", value: "In Progress" },
			{ label: "Completed", value: "Completed" },
			{ label: "Deferred", value: "Deferred" },
		],
		defaultValue: "Planned",
		component: "Badge",
		badgeTheme: {
			Planned: "gray",
			"In Progress": "blue",
			Completed: "green",
			Deferred: "orange",
		},
	},
]

const validateAudit = (data) => {
	const errs = {}
	if (!data.audit_name) errs.audit_name = "Audit name is required"
	if (!data.audit_type) errs.audit_type = "Audit type is required"
	if (!data.quarter) errs.quarter = "Quarter is required"
	if (data.planned_start_date && data.planned_end_date) {
		if (new Date(data.planned_end_date) < new Date(data.planned_start_date)) {
			errs.planned_end_date = "End date must be after start date"
		}
	}
	return Object.keys(errs).length ? errs : null
}

// Computed Properties
const currentSectionIndex = computed(() =>
	formSections.findIndex((s) => s.id === activeSection.value),
)

const utilizationPercentage = computed(() => {
	if (!form.total_available_days) return 0
	return Math.round((form.total_planned_days / form.total_available_days) * 100)
})

const budgetUtilization = computed(() => {
	if (!form.total_budget) return 0
	return Math.round((form.actual_spend / form.total_budget) * 100)
})

const budgetUtilizationClass = computed(() => {
	if (budgetUtilization.value > 90) return "text-red-600"
	if (budgetUtilization.value > 75) return "text-amber-600"
	return "text-green-600"
})

const budgetUtilizationBarClass = computed(() => {
	if (budgetUtilization.value > 90) return "bg-red-500"
	if (budgetUtilization.value > 75) return "bg-amber-500"
	return "bg-green-500"
})

const getSectionStatus = (sectionId) => {
	switch (sectionId) {
		case "basic":
			return form.plan_title &&
				form.fiscal_year &&
				form.plan_start_date &&
				form.plan_end_date
				? "complete"
				: form.plan_title || form.fiscal_year
					? "partial"
					: "incomplete"
		case "overview":
			return form.executive_summary && form.objectives
				? "complete"
				: form.executive_summary || form.objectives
					? "partial"
					: "incomplete"
		case "resources":
			return form.resource_allocation.length > 0 ? "complete" : "incomplete"
		case "audits":
			return form.planned_audits.length > 0 ? "complete" : "incomplete"
		case "budget":
			return form.total_budget > 0 ? "complete" : "incomplete"
		case "risk":
			return form.key_risks ? "complete" : "incomplete"
		case "contingency":
			return form.contingency_plan ? "complete" : "incomplete"
		case "additional":
			return "complete" // Optional section
		case "review":
			return "complete" // Review section
		default:
			return "incomplete"
	}
}

const getSectionStatusClass = (sectionId) => {
	const status = getSectionStatus(sectionId)
	if (status === "complete") return "bg-green-500 text-white"
	if (status === "partial") return "bg-amber-500 text-white"
	return "bg-gray-300 text-gray-600"
}

const completedSections = computed(
	() =>
		formSections.filter((s) => getSectionStatus(s.id) === "complete").length,
)

const formProgress = computed(() =>
	Math.round((completedSections.value / formSections.length) * 100),
)

const validationChecks = computed(() => [
	{ label: "Plan title provided", valid: !!form.plan_title },
	{ label: "Fiscal year selected", valid: !!form.fiscal_year },
	{
		label: "Plan dates specified",
		valid: !!form.plan_start_date && !!form.plan_end_date,
	},
	{ label: "Executive summary provided", valid: !!form.executive_summary },
	{ label: "Objectives defined", valid: !!form.objectives },
	{
		label: "At least one audit planned",
		valid: form.planned_audits.length > 0,
	},
])

const isFormValid = computed(() => {
	return !!(
		form.plan_title &&
		form.fiscal_year &&
		form.plan_start_date &&
		form.plan_end_date &&
		form.executive_summary &&
		form.objectives &&
		form.planned_audits.length > 0
	)
})

// Methods
const formatNumber = (num) => {
	if (!num) return "0"
	return num.toLocaleString()
}

const goToPreviousSection = () => {
	const idx = currentSectionIndex.value
	if (idx > 0) {
		activeSection.value = formSections[idx - 1].id
	}
}

const goToNextSection = () => {
	const idx = currentSectionIndex.value
	if (idx < formSections.length - 1) {
		activeSection.value = formSections[idx + 1].id
	}
}

const validateForm = () => {
	const errs = {}

	if (!form.plan_title) errs.plan_title = "Plan title is required"
	if (!form.fiscal_year) errs.fiscal_year = "Fiscal year is required"
	if (!form.plan_start_date) errs.plan_start_date = "Start date is required"
	if (!form.plan_end_date) errs.plan_end_date = "End date is required"
	if (!form.executive_summary)
		errs.executive_summary = "Executive summary is required"
	if (!form.objectives) errs.objectives = "Objectives are required"

	if (form.plan_start_date && form.plan_end_date) {
		if (new Date(form.plan_end_date) < new Date(form.plan_start_date)) {
			errs.plan_end_date = "End date must be after start date"
		}
	}

	if (form.planned_audits.length === 0) {
		errs.planned_audits = "At least one audit is required"
	}

	Object.assign(errors, errs)
	return Object.keys(errs).length === 0
}

const prepareFormData = () => {
	return {
		...form,
		resource_allocation: form.resource_allocation.map((r) => ({
			...r,
			doctype: "Annual Audit Plan Resource",
		})),
		planned_audits: form.planned_audits.map((a) => ({
			...a,
			doctype: "Annual Audit Plan Item",
		})),
	}
}

const handleSubmit = async () => {
	if (!validateForm()) {
		const firstErrorSection = formSections.find((s) => {
			const status = getSectionStatus(s.id)
			return status !== "complete"
		})
		if (firstErrorSection) {
			activeSection.value = firstErrorSection.id
		}
		return
	}

	try {
		isSaving.value = true
		const formData = prepareFormData()

		if (isEditMode.value) {
			emit("updated", { ...formData, name: props.plan.name })
		} else {
			emit("created", formData)
		}

		isOpen.value = false
	} catch (error) {
		console.error("Error saving plan:", error)
	} finally {
		isSaving.value = false
	}
}

const saveAsDraft = async () => {
	try {
		isSavingDraft.value = true
		const formData = prepareFormData()
		emit("created", { ...formData, status: "Draft" })
		isOpen.value = false
	} catch (error) {
		console.error("Error saving draft:", error)
	} finally {
		isSavingDraft.value = false
	}
}

const handleCancel = () => {
	emit("cancelled")
	isOpen.value = false
}

const resetForm = () => {
	Object.keys(form).forEach((key) => {
		if (Array.isArray(form[key])) {
			form[key] = []
		} else if (typeof form[key] === "number") {
			form[key] = 0
		} else {
			form[key] = ""
		}
	})
	form.status = "Draft"
	form.plan_period = "Annual"
	form.fiscal_year = new Date().getFullYear().toString()
	Object.keys(errors).forEach((key) => delete errors[key])
	activeSection.value = "basic"
}

const loadPlanData = (plan) => {
	if (!plan) return

	Object.keys(form).forEach((key) => {
		if (plan[key] !== undefined) {
			form[key] = plan[key]
		}
	})
}

// Watchers
watch(
	() => props.modelValue,
	(newVal) => {
		if (newVal) {
			if (props.plan) {
				loadPlanData(props.plan)
			} else {
				resetForm()
			}
		}
	},
)

watch(
	() => props.plan,
	(newVal) => {
		if (newVal && props.modelValue) {
			loadPlanData(newVal)
		}
	},
	{ deep: true },
)
</script>
