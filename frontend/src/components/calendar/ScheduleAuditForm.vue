<template>
  <Dialog
    v-model="isOpen"
    :options="{
      title: isEditMode ? 'Edit Audit Schedule' : 'Schedule New Audit',
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
                description="Essential audit scheduling details"
                icon="calendar"
                step="1"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- Calendar ID -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Calendar ID
                    </label>
                    <input
                      v-model="form.calendar_id"
                      type="text"
                      placeholder="Auto-generated if left blank"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                    />
                    <p class="mt-1 text-xs text-gray-500">Format: SC-YYYY-XXX</p>
                  </div>

                  <!-- Audit Universe -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Audit Universe <span class="text-red-500">*</span>
                    </label>
                    <LinkField
                      v-model="form.audit_universe"
                      doctype="Audit Universe"
                      placeholder="Select audit universe"
                      :required="true"
                      :error="errors.audit_universe"
                    />
                    <p v-if="errors.audit_universe" class="mt-1 text-xs text-red-500">{{ errors.audit_universe }}</p>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
                  <!-- Audit Type -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Audit Type <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="form.audit_type"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                      :class="errors.audit_type ? 'border-red-300' : 'border-gray-300'"
                    >
                      <option value="">Select audit type</option>
                      <option v-for="opt in auditTypeOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                    <p v-if="errors.audit_type" class="mt-1 text-xs text-red-500">{{ errors.audit_type }}</p>
                  </div>

                  <!-- Status -->
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

                  <!-- Annual Audit Plan -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Annual Audit Plan
                    </label>
                    <LinkField
                      v-model="form.annual_audit_plan"
                      doctype="Annual Audit Plan"
                      placeholder="Link to annual plan"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Timeline -->
            <div v-show="activeSection === 'timeline'" class="space-y-6">
              <SectionHeader
                title="Audit Timeline"
                description="Schedule dates and milestones"
                icon="clock"
                step="2"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Dates Row -->
                <div>
                  <h4 class="text-sm font-semibold text-gray-900 mb-4">Planned Dates</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        Planned Start Date <span class="text-red-500">*</span>
                      </label>
                      <input
                        v-model="form.planned_start_date"
                        type="date"
                        class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        :class="errors.planned_start_date ? 'border-red-300' : 'border-gray-300'"
                      />
                      <p v-if="errors.planned_start_date" class="mt-1 text-xs text-red-500">{{ errors.planned_start_date }}</p>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        Planned End Date <span class="text-red-500">*</span>
                      </label>
                      <input
                        v-model="form.planned_end_date"
                        type="date"
                        class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        :class="errors.planned_end_date ? 'border-red-300' : 'border-gray-300'"
                      />
                      <p v-if="errors.planned_end_date" class="mt-1 text-xs text-red-500">{{ errors.planned_end_date }}</p>
                    </div>
                  </div>
                </div>

                <!-- Actual Dates -->
                <div class="border-t border-gray-200 pt-6">
                  <h4 class="text-sm font-semibold text-gray-900 mb-4">Actual Dates (if started)</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        Actual Start Date
                      </label>
                      <input
                        v-model="form.actual_start_date"
                        type="date"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        Actual End Date
                      </label>
                      <input
                        v-model="form.actual_end_date"
                        type="date"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                <!-- Duration Info -->
                <div class="border-t border-gray-200 pt-6">
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-blue-50 rounded-lg p-4">
                      <h5 class="text-sm font-medium text-blue-800 mb-1">Estimated Days</h5>
                      <input
                        v-model.number="form.estimated_days"
                        type="number"
                        min="1"
                        placeholder="0"
                        class="w-full px-2 py-1.5 text-sm border border-blue-200 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div class="bg-amber-50 rounded-lg p-4">
                      <h5 class="text-sm font-medium text-amber-800 mb-1">Actual Days</h5>
                      <input
                        v-model.number="form.actual_days"
                        type="number"
                        min="0"
                        placeholder="0"
                        class="w-full px-2 py-1.5 text-sm border border-amber-200 rounded focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                      />
                    </div>
                    <div class="bg-green-50 rounded-lg p-4">
                      <h5 class="text-sm font-medium text-green-800 mb-1">Progress</h5>
                      <div class="flex items-center space-x-2">
                        <input
                          v-model.number="form.progress_percentage"
                          type="number"
                          min="0"
                          max="100"
                          placeholder="0"
                          class="w-20 px-2 py-1.5 text-sm border border-green-200 rounded focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        />
                        <span class="text-green-800 font-medium">%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Team -->
            <div v-show="activeSection === 'team'" class="space-y-6">
              <SectionHeader
                title="Audit Team"
                description="Assign auditors and team members"
                icon="users"
                step="3"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Lead Auditor -->
                <div class="max-w-md">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Lead Auditor <span class="text-red-500">*</span>
                  </label>
                  <LinkField
                    v-model="form.lead_auditor"
                    doctype="User"
                    :filters="{ enabled: 1 }"
                    placeholder="Select lead auditor"
                    :required="true"
                    :error="errors.lead_auditor"
                  />
                  <p v-if="errors.lead_auditor" class="mt-1 text-xs text-red-500">{{ errors.lead_auditor }}</p>
                </div>

                <!-- Audit Team Child Table - Inline Editable -->
                <div class="border-t border-gray-200 pt-6">
                  <InlineChildTable
                    v-model="form.audit_team"
                    title="Audit Team Members"
                    modal-title="Team Member"
                    :columns="teamMemberColumns"
                    :validate="validateTeamMember"
                    :auto-add-row="true"
                  />
                </div>
              </div>
            </div>

            <!-- Section: Scope & Objectives -->
            <div v-show="activeSection === 'scope'" class="space-y-6">
              <SectionHeader
                title="Scope & Objectives"
                description="Define audit scope and objectives"
                icon="target"
                step="4"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Objectives -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Audit Objectives <span class="text-red-500">*</span>
                  </label>
                  <textarea
                    v-model="form.objectives"
                    rows="4"
                    placeholder="Describe the primary objectives of this audit..."
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                    :class="errors.objectives ? 'border-red-300' : 'border-gray-300'"
                  ></textarea>
                  <p v-if="errors.objectives" class="mt-1 text-xs text-red-500">{{ errors.objectives }}</p>
                </div>

                <!-- Scope -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Audit Scope <span class="text-red-500">*</span>
                  </label>
                  <textarea
                    v-model="form.scope"
                    rows="4"
                    placeholder="Define the boundaries and areas covered by this audit..."
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                    :class="errors.scope ? 'border-red-300' : 'border-gray-300'"
                  ></textarea>
                  <p v-if="errors.scope" class="mt-1 text-xs text-red-500">{{ errors.scope }}</p>
                </div>

                <!-- Scope Exclusions -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Scope Exclusions
                  </label>
                  <textarea
                    v-model="form.scope_exclusions"
                    rows="3"
                    placeholder="Specify any areas explicitly excluded from this audit..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Section: Risks -->
            <div v-show="activeSection === 'risks'" class="space-y-6">
              <SectionHeader
                title="Key Risks"
                description="Identify risks and considerations"
                icon="alert-triangle"
                step="5"
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
                    placeholder="Identify key risks that may impact this audit..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  ></textarea>
                </div>

                <!-- Risk Assessment Reference -->
                <div class="max-w-md">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Risk Assessment Reference
                  </label>
                  <LinkField
                    v-model="form.risk_assessment_reference"
                    doctype="Risk Assessment"
                    placeholder="Link to risk assessment"
                  />
                </div>

                <!-- Priority -->
                <div class="max-w-md">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Priority Level
                  </label>
                  <select
                    v-model="form.priority"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option v-for="opt in priorityOptions" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Section: Resources -->
            <div v-show="activeSection === 'resources'" class="space-y-6">
              <SectionHeader
                title="Resources & Budget"
                description="Allocate resources and budget"
                icon="dollar-sign"
                step="6"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Budget Fields -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Budgeted Hours
                    </label>
                    <input
                      v-model.number="form.budgeted_hours"
                      type="number"
                      min="0"
                      step="0.5"
                      placeholder="0"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Actual Hours
                    </label>
                    <input
                      v-model.number="form.actual_hours"
                      type="number"
                      min="0"
                      step="0.5"
                      placeholder="0"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Estimated Cost
                    </label>
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                      <input
                        v-model.number="form.estimated_cost"
                        type="number"
                        min="0"
                        step="100"
                        placeholder="0.00"
                        class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Actual Cost
                    </label>
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                      <input
                        v-model.number="form.actual_cost"
                        type="number"
                        min="0"
                        step="100"
                        placeholder="0.00"
                        class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                <!-- Hours Utilization Bar -->
                <div class="bg-gray-50 rounded-lg p-4">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">Hours Utilization</span>
                    <span class="text-sm font-bold" :class="hoursUtilizationClass">{{ hoursUtilization }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-3">
                    <div
                      class="h-3 rounded-full transition-all duration-300"
                      :class="hoursUtilizationBarClass"
                      :style="{ width: `${Math.min(hoursUtilization, 100)}%` }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Notes -->
            <div v-show="activeSection === 'notes'" class="space-y-6">
              <SectionHeader
                title="Additional Notes"
                description="Notes and supplementary information"
                icon="file-text"
                step="7"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Notes -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Notes
                  </label>
                  <textarea
                    v-model="form.notes"
                    rows="5"
                    placeholder="Additional notes or comments..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  ></textarea>
                </div>

                <!-- Engagement Reference -->
                <div class="max-w-md">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Engagement Reference
                  </label>
                  <LinkField
                    v-model="form.engagement_reference"
                    doctype="Audit Engagement"
                    placeholder="Link to engagement"
                  />
                </div>
              </div>
            </div>

            <!-- Section: Review -->
            <div v-show="activeSection === 'review'" class="space-y-6">
              <SectionHeader
                title="Review & Submit"
                description="Review your schedule before saving"
                icon="check-circle"
                step="8"
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

                <!-- Schedule Summary -->
                <div class="mt-6 border-t border-gray-200 pt-6">
                  <h4 class="font-semibold text-gray-900 mb-4">Schedule Summary</h4>
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="bg-gray-50 rounded-lg p-4">
                      <p class="text-xs text-gray-500">Audit Type</p>
                      <p class="text-lg font-semibold text-gray-900">{{ form.audit_type || '-' }}</p>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-4">
                      <p class="text-xs text-gray-500">Status</p>
                      <p class="text-lg font-semibold text-gray-900">{{ form.status || 'Planned' }}</p>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-4">
                      <p class="text-xs text-gray-500">Estimated Days</p>
                      <p class="text-lg font-semibold text-gray-900">{{ form.estimated_days || 0 }}</p>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-4">
                      <p class="text-xs text-gray-500">Team Members</p>
                      <p class="text-lg font-semibold text-gray-900">{{ (form.audit_team?.length || 0) + 1 }}</p>
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
            {{ isEditMode ? 'Update Schedule' : 'Schedule Audit' }}
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
import { computed, reactive, ref, watch } from "vue"

// Import custom components
import InlineChildTable from "@/components/Common/InlineChildTable.vue"
import LinkField from "@/components/Common/fields/LinkField.vue"
import SectionHeader from "@/components/engagement/SectionHeader.vue"

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  schedule: {
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
const isEditMode = computed(() => !!props.schedule?.name)

// Form Sections
const formSections = [
  { id: "basic", label: "Basic Information", description: "Core details" },
  { id: "timeline", label: "Timeline", description: "Dates & schedule" },
  { id: "team", label: "Audit Team", description: "Team assignment" },
  { id: "scope", label: "Scope & Objectives", description: "Audit coverage" },
  { id: "risks", label: "Risks", description: "Risk considerations" },
  { id: "resources", label: "Resources", description: "Budget & hours" },
  { id: "notes", label: "Notes", description: "Additional info" },
  { id: "review", label: "Review & Submit", description: "Final review" },
]

const activeSection = ref("basic")

// Form State
const form = reactive({
  // Basic Information
  calendar_id: "",
  audit_universe: "",
  audit_type: "",
  status: "Planned",
  annual_audit_plan: "",

  // Timeline
  planned_start_date: "",
  planned_end_date: "",
  actual_start_date: "",
  actual_end_date: "",
  estimated_days: 0,
  actual_days: 0,
  progress_percentage: 0,

  // Team
  lead_auditor: "",
  audit_team: [],

  // Scope & Objectives
  objectives: "",
  scope: "",
  scope_exclusions: "",

  // Risks
  key_risks: "",
  risk_assessment_reference: "",
  priority: "Medium",

  // Resources
  budgeted_hours: 0,
  actual_hours: 0,
  estimated_cost: 0,
  actual_cost: 0,

  // Notes
  notes: "",
  engagement_reference: "",
})

const errors = reactive({})
const isSaving = ref(false)
const isSavingDraft = ref(false)

// Options
const auditTypeOptions = [
  { label: "Financial", value: "Financial" },
  { label: "Operational", value: "Operational" },
  { label: "Compliance", value: "Compliance" },
  { label: "IT", value: "IT" },
  { label: "Integrated", value: "Integrated" },
  { label: "Special Investigation", value: "Special Investigation" },
  { label: "Follow-up", value: "Follow-up" },
  { label: "Advisory", value: "Advisory" },
]

const statusOptions = [
  { label: "Planned", value: "Planned" },
  { label: "In Progress", value: "In Progress" },
  { label: "On Hold", value: "On Hold" },
  { label: "Completed", value: "Completed" },
  { label: "Cancelled", value: "Cancelled" },
  { label: "Deferred", value: "Deferred" },
]

const priorityOptions = [
  { label: "Low", value: "Low" },
  { label: "Medium", value: "Medium" },
  { label: "High", value: "High" },
  { label: "Critical", value: "Critical" },
]

// Inline Columns for Team Members
const teamMemberColumns = [
  {
    key: "team_member",
    label: "Team Member",
    width: "200px",
    fieldType: "link",
    doctype: "User",
    required: true,
    placeholder: "Select member",
  },
  {
    key: "role",
    label: "Role",
    width: "150px",
    fieldType: "select",
    options: [
      { label: "Lead Auditor", value: "Lead Auditor" },
      { label: "Senior Auditor", value: "Senior Auditor" },
      { label: "Staff Auditor", value: "Staff Auditor" },
      { label: "IT Auditor", value: "IT Auditor" },
      { label: "Subject Matter Expert", value: "Subject Matter Expert" },
      { label: "Observer", value: "Observer" },
    ],
    required: true,
  },
  {
    key: "planned_hours",
    label: "Planned Hours",
    width: "120px",
    fieldType: "number",
    placeholder: "0",
  },
  {
    key: "actual_hours",
    label: "Actual Hours",
    width: "120px",
    fieldType: "number",
    placeholder: "0",
  },
]

const validateTeamMember = (data) => {
  const errs = {}
  if (!data.team_member) errs.team_member = "Team member is required"
  if (!data.role) errs.role = "Role is required"
  return Object.keys(errs).length ? errs : null
}

// Computed Properties
const currentSectionIndex = computed(() =>
  formSections.findIndex((s) => s.id === activeSection.value)
)

const hoursUtilization = computed(() => {
  if (!form.budgeted_hours) return 0
  return Math.round((form.actual_hours / form.budgeted_hours) * 100)
})

const hoursUtilizationClass = computed(() => {
  if (hoursUtilization.value > 100) return "text-red-600"
  if (hoursUtilization.value > 90) return "text-amber-600"
  return "text-green-600"
})

const hoursUtilizationBarClass = computed(() => {
  if (hoursUtilization.value > 100) return "bg-red-500"
  if (hoursUtilization.value > 90) return "bg-amber-500"
  return "bg-green-500"
})

const getSectionStatus = (sectionId) => {
  switch (sectionId) {
    case "basic":
      return form.audit_universe && form.audit_type
        ? "complete"
        : form.audit_universe || form.audit_type
          ? "partial"
          : "incomplete"
    case "timeline":
      return form.planned_start_date && form.planned_end_date
        ? "complete"
        : form.planned_start_date || form.planned_end_date
          ? "partial"
          : "incomplete"
    case "team":
      return form.lead_auditor ? "complete" : "incomplete"
    case "scope":
      return form.objectives && form.scope
        ? "complete"
        : form.objectives || form.scope
          ? "partial"
          : "incomplete"
    case "risks":
      return form.key_risks ? "complete" : "incomplete"
    case "resources":
      return form.budgeted_hours > 0 ? "complete" : "incomplete"
    case "notes":
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
  () => formSections.filter((s) => getSectionStatus(s.id) === "complete").length
)

const formProgress = computed(() =>
  Math.round((completedSections.value / formSections.length) * 100)
)

const validationChecks = computed(() => [
  { label: "Audit universe selected", valid: !!form.audit_universe },
  { label: "Audit type selected", valid: !!form.audit_type },
  { label: "Planned dates specified", valid: !!form.planned_start_date && !!form.planned_end_date },
  { label: "Lead auditor assigned", valid: !!form.lead_auditor },
  { label: "Objectives defined", valid: !!form.objectives },
  { label: "Scope defined", valid: !!form.scope },
])

const isFormValid = computed(() => {
  return !!(
    form.audit_universe &&
    form.audit_type &&
    form.planned_start_date &&
    form.planned_end_date &&
    form.lead_auditor &&
    form.objectives &&
    form.scope
  )
})

// Methods
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

  if (!form.audit_universe) errs.audit_universe = "Audit universe is required"
  if (!form.audit_type) errs.audit_type = "Audit type is required"
  if (!form.planned_start_date) errs.planned_start_date = "Start date is required"
  if (!form.planned_end_date) errs.planned_end_date = "End date is required"
  if (!form.lead_auditor) errs.lead_auditor = "Lead auditor is required"
  if (!form.objectives) errs.objectives = "Objectives are required"
  if (!form.scope) errs.scope = "Scope is required"

  if (form.planned_start_date && form.planned_end_date) {
    if (new Date(form.planned_end_date) < new Date(form.planned_start_date)) {
      errs.planned_end_date = "End date must be after start date"
    }
  }

  Object.assign(errors, errs)
  return Object.keys(errs).length === 0
}

const prepareFormData = () => {
  return {
    ...form,
    audit_team: form.audit_team.map((m) => ({
      ...m,
      doctype: "Audit Calendar Team Member",
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
      emit("updated", { ...formData, name: props.schedule.name })
    } else {
      emit("created", formData)
    }

    isOpen.value = false
  } catch (error) {
    console.error("Error saving schedule:", error)
  } finally {
    isSaving.value = false
  }
}

const saveAsDraft = async () => {
  try {
    isSavingDraft.value = true
    const formData = prepareFormData()
    emit("created", { ...formData, status: "Planned" })
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
  form.status = "Planned"
  form.priority = "Medium"
  Object.keys(errors).forEach((key) => delete errors[key])
  activeSection.value = "basic"
}

const loadScheduleData = (schedule) => {
  if (!schedule) return

  Object.keys(form).forEach((key) => {
    if (schedule[key] !== undefined) {
      form[key] = schedule[key]
    }
  })
}

// Watchers
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal) {
      if (props.schedule) {
        loadScheduleData(props.schedule)
      } else {
        resetForm()
      }
    }
  }
)

watch(
  () => props.schedule,
  (newVal) => {
    if (newVal && props.modelValue) {
      loadScheduleData(newVal)
    }
  },
  { deep: true }
)
</script>
