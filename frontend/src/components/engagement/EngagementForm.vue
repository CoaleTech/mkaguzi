<template>
  <Dialog
    v-model="isOpen"
    :options="{
      title: isEditMode ? 'Edit Audit Engagement' : 'Create New Audit Engagement',
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
                    ? 'bg-gray-100 border border-gray-300 text-gray-800'
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
                <span class="text-sm font-bold text-gray-900">{{ formProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-gray-900 h-2 rounded-full transition-all duration-300"
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
                description="Essential engagement details and identification"
                icon="file-text"
                step="1"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <!-- Engagement ID -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Engagement ID <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="form.engagement_id"
                      type="text"
                      placeholder="Auto-generated if left blank"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition"
                      :class="errors.engagement_id ? 'border-red-300' : 'border-gray-300'"
                    />
                    <p v-if="errors.engagement_id" class="mt-1 text-xs text-red-500">{{ errors.engagement_id }}</p>
                    <p v-else class="mt-1 text-xs text-gray-500">Format: AE-YYYY-XXX</p>
                  </div>

                  <!-- Status -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Status <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="form.status"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    >
                      <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                  </div>

                  <!-- Audit Type -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Audit Type <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="form.audit_type"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition"
                      :class="errors.audit_type ? 'border-red-300' : 'border-gray-300'"
                    >
                      <option value="">Select audit type</option>
                      <option v-for="opt in auditTypeOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                    <p v-if="errors.audit_type" class="mt-1 text-xs text-red-500">{{ errors.audit_type }}</p>
                  </div>
                </div>

                <!-- Engagement Title -->
                <div class="mt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Engagement Title <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="form.engagement_title"
                    type="text"
                    placeholder="Enter a descriptive engagement title"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition"
                    :class="errors.engagement_title ? 'border-red-300' : 'border-gray-300'"
                  />
                  <p v-if="errors.engagement_title" class="mt-1 text-xs text-red-500">{{ errors.engagement_title }}</p>
                </div>

                <!-- References Row -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
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
                  </div>

                  <!-- Planned Audit Reference -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Planned Audit Reference
                    </label>
                    <LinkField
                      v-model="form.planned_audit_reference"
                      doctype="Annual Audit Plan Item"
                      placeholder="Link to annual plan"
                    />
                  </div>

                  <!-- Risk Assessment Reference -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Risk Assessment Reference
                    </label>
                    <LinkField
                      v-model="form.risk_assessment_reference"
                      doctype="Risk Assessment"
                      placeholder="Link to risk assessment"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Scope & Objectives -->
            <div v-show="activeSection === 'scope'" class="space-y-6">
              <SectionHeader
                title="Audit Scope & Objectives"
                description="Define what the audit will cover and its goals"
                icon="target"
                step="2"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Audit Objectives -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Audit Objectives <span class="text-red-500">*</span>
                  </label>
                  <textarea
                    v-model="form.audit_objectives"
                    rows="4"
                    placeholder="Describe the primary objectives of this audit engagement..."
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition"
                    :class="errors.audit_objectives ? 'border-red-300' : 'border-gray-300'"
                  ></textarea>
                  <p v-if="errors.audit_objectives" class="mt-1 text-xs text-red-500">{{ errors.audit_objectives }}</p>
                </div>

                <!-- Audit Scope -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Audit Scope <span class="text-red-500">*</span>
                  </label>
                  <textarea
                    v-model="form.audit_scope"
                    rows="4"
                    placeholder="Define the boundaries and areas covered by this audit..."
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition"
                    :class="errors.audit_scope ? 'border-red-300' : 'border-gray-300'"
                  ></textarea>
                  <p v-if="errors.audit_scope" class="mt-1 text-xs text-red-500">{{ errors.audit_scope }}</p>
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
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Section: Methodology -->
            <div v-show="activeSection === 'methodology'" class="space-y-6">
              <SectionHeader
                title="Audit Methodology"
                description="Define the approach and methods to be used"
                icon="settings"
                step="3"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <!-- Audit Approach -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Audit Approach <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="form.audit_approach"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    >
                      <option v-for="opt in auditApproachOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                  </div>

                  <!-- Materiality Threshold -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Materiality Threshold
                    </label>
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                      <input
                        v-model.number="form.materiality_threshold"
                        type="number"
                        min="0"
                        step="100"
                        placeholder="0.00"
                        class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <!-- Sampling Methodology -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Sampling Methodology
                    </label>
                    <select
                      v-model="form.sampling_methodology"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    >
                      <option v-for="opt in samplingMethodOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Timeline -->
            <div v-show="activeSection === 'timeline'" class="space-y-6">
              <SectionHeader
                title="Audit Period & Timeline"
                description="Set the audit period and key milestone dates"
                icon="calendar"
                step="4"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Audit Period -->
                <div>
                  <h4 class="text-sm font-semibold text-gray-900 mb-4">Audit Period</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        Period Start <span class="text-red-500">*</span>
                      </label>
                      <input
                        v-model="form.period_start"
                        type="date"
                        class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        :class="errors.period_start ? 'border-red-300' : 'border-gray-300'"
                      />
                      <p v-if="errors.period_start" class="mt-1 text-xs text-red-500">{{ errors.period_start }}</p>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        Period End <span class="text-red-500">*</span>
                      </label>
                      <input
                        v-model="form.period_end"
                        type="date"
                        class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        :class="errors.period_end ? 'border-red-300' : 'border-gray-300'"
                      />
                      <p v-if="errors.period_end" class="mt-1 text-xs text-red-500">{{ errors.period_end }}</p>
                    </div>
                  </div>
                </div>

                <!-- Engagement Timeline -->
                <div class="border-t border-gray-200 pt-6">
                  <h4 class="text-sm font-semibold text-gray-900 mb-4">Engagement Timeline</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <!-- Planning Phase -->
                    <div class="bg-gray-50 rounded-lg p-4">
                      <h5 class="text-sm font-medium text-gray-800 mb-3">Planning Phase</h5>
                      <div class="space-y-3">
                        <div>
                          <label class="block text-xs font-medium text-gray-700 mb-1">Start Date</label>
                          <input
                            v-model="form.planning_start"
                            type="date"
                            class="w-full px-2 py-1.5 text-sm border border-gray-200 rounded focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          />
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-gray-700 mb-1">End Date</label>
                          <input
                            v-model="form.planning_end"
                            type="date"
                            class="w-full px-2 py-1.5 text-sm border border-gray-200 rounded focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          />
                        </div>
                      </div>
                    </div>

                    <!-- Fieldwork Phase -->
                    <div class="bg-amber-50 rounded-lg p-4">
                      <h5 class="text-sm font-medium text-amber-800 mb-3">Fieldwork Phase</h5>
                      <div class="space-y-3">
                        <div>
                          <label class="block text-xs font-medium text-amber-700 mb-1">Start Date</label>
                          <input
                            v-model="form.fieldwork_start"
                            type="date"
                            class="w-full px-2 py-1.5 text-sm border border-amber-200 rounded focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                          />
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-amber-700 mb-1">End Date</label>
                          <input
                            v-model="form.fieldwork_end"
                            type="date"
                            class="w-full px-2 py-1.5 text-sm border border-amber-200 rounded focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                          />
                        </div>
                      </div>
                    </div>

                    <!-- Reporting Phase -->
                    <div class="bg-gray-50 rounded-lg p-4">
                      <h5 class="text-sm font-medium text-gray-800 mb-3">Reporting Phase</h5>
                      <div class="space-y-3">
                        <div>
                          <label class="block text-xs font-medium text-gray-700 mb-1">Start Date</label>
                          <input
                            v-model="form.reporting_start"
                            type="date"
                            class="w-full px-2 py-1.5 text-sm border border-gray-200 rounded focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          />
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-gray-700 mb-1">End Date</label>
                          <input
                            v-model="form.reporting_end"
                            type="date"
                            class="w-full px-2 py-1.5 text-sm border border-gray-200 rounded focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Team & Resources -->
            <div v-show="activeSection === 'team'" class="space-y-6">
              <SectionHeader
                title="Audit Team"
                description="Assign team members and define roles"
                icon="users"
                step="5"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Lead Auditor -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
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
                  </div>
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
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    />
                  </div>
                </div>

                <!-- Audit Team Child Table - Inline Editable -->
                <div class="border-t border-gray-200 pt-6">
                  <InlineChildTable
                    v-model="form.audit_team"
                    title="Audit Team Members"
                    modal-title="Team Member"
                    doctype="Audit Team Member"
                    :validate="validateTeamMember"
                    :required="true"
                    :auto-add-row="true"
                  />
                </div>
              </div>
            </div>

            <!-- Section: Contacts -->
            <div v-show="activeSection === 'contacts'" class="space-y-6">
              <SectionHeader
                title="Auditee Information"
                description="Process owners and key stakeholder contacts"
                icon="book-user"
                step="6"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Process Owner -->
                <div class="max-w-md">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Process Owner
                  </label>
                  <LinkField
                    v-model="form.process_owner"
                    doctype="User"
                    :filters="{ enabled: 1 }"
                    placeholder="Select process owner"
                  />
                </div>

                <!-- Key Contacts Child Table - Inline Editable -->
                <div class="border-t border-gray-200 pt-6">
                  <InlineChildTable
                    v-model="form.key_contacts"
                    title="Key Contacts"
                    modal-title="Contact"
                    :columns="keyContactsInlineColumns"
                    :form-fields="keyContactsFormFields"
                    :validate="validateContact"
                    :auto-add-row="true"
                  />
                </div>
              </div>
            </div>

            <!-- Section: Data Requirements -->
            <div v-show="activeSection === 'data'" class="space-y-6">
              <SectionHeader
                title="Data Requirements"
                description="Define data periods and BC data needs"
                icon="database"
                step="7"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-8">
                <!-- Data Periods - Inline Editable -->
                <InlineChildTable
                  v-model="form.data_periods"
                  title="Data Periods"
                  modal-title="Data Period"
                  :columns="dataPeriodsInlineColumns"
                  :form-fields="dataPeriodsFormFields"
                  :validate="validateDataPeriod"
                  :auto-add-row="true"
                />

                <!-- BC Data Requirements - Keep modal-based for complex fields -->
                <div class="border-t border-gray-200 pt-6">
                  <ChildTable
                    v-model="form.bc_data_requirements"
                    title="BC Data Requirements"
                    modal-title="Data Requirement"
                    :columns="bcDataReqColumns"
                    :form-fields="bcDataReqFormFields"
                    :validate="validateDataRequirement"
                  />
                </div>
              </div>
            </div>

            <!-- Section: Documentation -->
            <div v-show="activeSection === 'documentation'" class="space-y-6">
              <SectionHeader
                title="Documentation & Notes"
                description="Working papers, amendments, and additional notes"
                icon="folder"
                step="8"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Documentation References -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Audit Program Reference
                    </label>
                    <LinkField
                      v-model="form.audit_program_reference"
                      doctype="Audit Program"
                      placeholder="Link to audit program"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Working Papers Folder
                    </label>
                    <input
                      v-model="form.working_papers_folder"
                      type="text"
                      placeholder="Enter folder path or reference"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    />
                  </div>
                </div>

                <!-- Amendments -->
                <div class="border-t border-gray-200 pt-6">
                  <ChildTable
                    v-model="form.amendments"
                    title="Engagement Amendments"
                    modal-title="Amendment"
                    :columns="amendmentsColumns"
                    :form-fields="amendmentsFormFields"
                    :validate="validateAmendment"
                  />
                </div>

                <!-- Notes -->
                <div class="border-t border-gray-200 pt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Notes
                  </label>
                  <textarea
                    v-model="form.notes"
                    rows="4"
                    placeholder="Additional notes or comments..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  ></textarea>
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
            theme="gray"
            @click="handleSubmit"
            :loading="isSaving"
          >
            <template #prefix>
              <PlusIcon v-if="!isEditMode" class="h-4 w-4" />
              <CheckIcon v-else class="h-4 w-4" />
            </template>
            {{ isEditMode ? 'Update Engagement' : 'Create Engagement' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { Button, Dialog } from 'frappe-ui'
import {
  CheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  PlusIcon,
} from 'lucide-vue-next'

// Import custom components
import ChildTable from '@/components/Common/ChildTable.vue'
import InlineChildTable from '@/components/Common/InlineChildTable.vue'
import LinkField from '@/components/Common/fields/LinkField.vue'
import SectionHeader from '@/components/engagement/SectionHeader.vue'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  engagement: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'created', 'updated', 'cancelled'])

// Dialog visibility
const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// Edit mode detection
const isEditMode = computed(() => !!props.engagement?.name)

// Form Sections
const formSections = [
  { id: 'basic', label: 'Basic Information', description: 'Core details' },
  { id: 'scope', label: 'Scope & Objectives', description: 'Audit coverage' },
  { id: 'methodology', label: 'Methodology', description: 'Approach & methods' },
  { id: 'timeline', label: 'Timeline', description: 'Dates & phases' },
  { id: 'team', label: 'Audit Team', description: 'Team members' },
  { id: 'contacts', label: 'Contacts', description: 'Stakeholders' },
  { id: 'data', label: 'Data Requirements', description: 'Data needs' },
  { id: 'documentation', label: 'Documentation', description: 'Notes & files' },
]

const activeSection = ref('basic')

// Form State
const form = reactive({
  // Basic Information
  engagement_id: '',
  engagement_title: '',
  audit_type: '',
  status: 'Planning',
  planned_audit_reference: '',
  audit_universe: '',
  risk_assessment_reference: '',

  // Scope & Objectives
  audit_objectives: '',
  audit_scope: '',
  scope_exclusions: '',

  // Methodology
  audit_approach: 'Risk-Based',
  materiality_threshold: null,
  sampling_methodology: '',

  // Timeline
  period_start: '',
  period_end: '',
  planning_start: '',
  planning_end: '',
  fieldwork_start: '',
  fieldwork_end: '',
  reporting_start: '',
  reporting_end: '',
  actual_completion_date: '',

  // Team & Resources
  lead_auditor: '',
  budgeted_hours: null,
  process_owner: '',

  // Documentation
  audit_program_reference: '',
  working_papers_folder: '',
  notes: '',

  // Child Tables
  audit_team: [],
  key_contacts: [],
  data_periods: [],
  bc_data_requirements: [],
  amendments: [],
})

const errors = reactive({})
const isSaving = ref(false)
const isSavingDraft = ref(false)

// Options
const statusOptions = [
  { label: 'Planning', value: 'Planning' },
  { label: 'Fieldwork', value: 'Fieldwork' },
  { label: 'Reporting', value: 'Reporting' },
  { label: 'Management Review', value: 'Management Review' },
  { label: 'Quality Review', value: 'Quality Review' },
  { label: 'Finalized', value: 'Finalized' },
  { label: 'Issued', value: 'Issued' },
]

const auditTypeOptions = [
  { label: 'Financial', value: 'Financial' },
  { label: 'Operational', value: 'Operational' },
  { label: 'Compliance', value: 'Compliance' },
  { label: 'IT', value: 'IT' },
  { label: 'Integrated', value: 'Integrated' },
  { label: 'Special Investigation', value: 'Special Investigation' },
  { label: 'Follow-up', value: 'Follow-up' },
  { label: 'Advisory', value: 'Advisory' },
]

const auditApproachOptions = [
  { label: 'Risk-Based', value: 'Risk-Based' },
  { label: 'Controls-Based', value: 'Controls-Based' },
  { label: 'Substantive', value: 'Substantive' },
  { label: 'Compliance', value: 'Compliance' },
  { label: 'Combined', value: 'Combined' },
]

const samplingMethodOptions = [
  { label: 'Random', value: 'Random' },
  { label: 'Systematic', value: 'Systematic' },
  { label: 'Stratified', value: 'Stratified' },
  { label: 'Judgmental', value: 'Judgmental' },
  { label: 'Statistical', value: 'Statistical' },
  { label: '100% Testing', value: '100% Testing' },
]

// Child Table: Audit Team
const auditTeamColumns = [
  { key: 'team_member_name', label: 'Name', width: '180px' },
  { key: 'role', label: 'Role', width: '140px' },
  { key: 'budgeted_hours', label: 'Hours', width: '80px', format: (v) => v ? `${v}h` : '-' },
  { key: 'status', label: 'Status', width: '100px', component: 'Badge' },
]

// Validation aligned with audit_team_member.py backend logic
const validateTeamMember = (data, allRows = [], currentIndex = null) => {
  const errs = {}
  if (!data.team_member) errs.team_member = 'Team member is required'
  if (!data.role) errs.role = 'Role is required'

  // Validate planned_hours and actual_hours are non-negative
  if (data.planned_hours < 0) errs.planned_hours = 'Planned hours cannot be negative'
  if (data.actual_hours < 0) errs.actual_hours = 'Actual hours cannot be negative'

  return Object.keys(errs).length ? errs : null
}

// Child Table: Key Contacts
// Aligned with Audit Contact DocType field order
const keyContactsColumns = [
  { key: 'contact_type', label: 'Type', width: '140px' },
  { key: 'contact_name', label: 'Name', width: '180px' },
  { key: 'designation', label: 'Designation', width: '140px' },
  { key: 'email', label: 'Email', width: '180px' },
  { key: 'is_primary', label: 'Primary', width: '80px', format: (v) => v ? 'Yes' : 'No' },
]

// Inline editable columns for Key Contacts (ERPNext-style)
// Aligned with Audit Contact DocType: audit_contact.json
const keyContactsInlineColumns = [
  {
    key: 'contact_type',
    label: 'Type',
    width: '140px',
    fieldType: 'select',
    options: [
      { label: 'Management', value: 'Management' },
      { label: 'Process Owner', value: 'Process Owner' },
      { label: 'Subject Matter Expert', value: 'Subject Matter Expert' },
      { label: 'IT Contact', value: 'IT Contact' },
      { label: 'External Auditor', value: 'External Auditor' },
      { label: 'Other', value: 'Other' },
    ],
    required: true
  },
  {
    key: 'contact_name',
    label: 'Name',
    width: '160px',
    fieldType: 'text',
    required: true,
    placeholder: 'Enter name'
  },
  {
    key: 'designation',
    label: 'Designation',
    width: '130px',
    fieldType: 'text',
    placeholder: 'Job title'
  },
  {
    key: 'department',
    label: 'Department',
    width: '120px',
    fieldType: 'text',
    placeholder: 'Department'
  },
  {
    key: 'email',
    label: 'Email',
    width: '170px',
    fieldType: 'data',
    options: 'Email',
    placeholder: 'email@example.com'
  },
  {
    key: 'phone',
    label: 'Phone',
    width: '120px',
    fieldType: 'data',
    placeholder: '+1234567890'
  },
  {
    key: 'is_primary',
    label: 'Primary',
    width: '65px',
    fieldType: 'checkbox',
    defaultValue: false
  }
]

// Form fields aligned with Audit Contact DocType field order
const keyContactsFormFields = [
  {
    name: 'contact_type',
    label: 'Contact Type',
    component: 'select',
    props: {
      options: [
        { label: 'Management', value: 'Management' },
        { label: 'Process Owner', value: 'Process Owner' },
        { label: 'Subject Matter Expert', value: 'Subject Matter Expert' },
        { label: 'IT Contact', value: 'IT Contact' },
        { label: 'External Auditor', value: 'External Auditor' },
        { label: 'Other', value: 'Other' },
      ],
      required: true
    }
  },
  { name: 'contact_name', label: 'Contact Name', component: 'input', props: { type: 'text', required: true } },
  { name: 'designation', label: 'Designation', component: 'input', props: { type: 'text' } },
  { name: 'department', label: 'Department', component: 'input', props: { type: 'text' } },
  { name: 'email', label: 'Email', component: 'input', props: { type: 'email' } },
  { name: 'phone', label: 'Phone', component: 'input', props: { type: 'tel' } },
  { name: 'is_primary', label: 'Is Primary Contact', component: 'checkbox' },
  {
    name: 'communication_preference',
    label: 'Communication Preference',
    component: 'select',
    props: {
      options: [
        { label: 'Email', value: 'Email' },
        { label: 'Phone', value: 'Phone' },
        { label: 'Meeting', value: 'Meeting' },
        { label: 'All', value: 'All' },
      ]
    }
  },
  { name: 'notes', label: 'Notes', component: 'textarea', props: { rows: 2 } },
]

// Validation aligned with audit_contact.py backend logic
const validateContact = (data, allRows = [], currentIndex = null) => {
  const errs = {}
  if (!data.contact_type) errs.contact_type = 'Contact type is required'
  if (!data.contact_name) errs.contact_name = 'Contact name is required'
  
  // Email validation - matches validate_contact_info() in backend
  if (data.email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(data.email)) {
      errs.email = 'Invalid email address'
    }
  }
  
  // Phone validation - matches backend regex
  if (data.phone) {
    const phoneRegex = /^[\d\s\-\+\(\)\.]+$/
    if (!phoneRegex.test(data.phone)) {
      errs.phone = 'Invalid phone number format'
    }
  }
  
  // Primary contact validation - matches validate_primary_contact() in backend
  // Only one primary contact allowed per contact type
  if (data.is_primary && allRows.length > 0) {
    const otherPrimary = allRows.filter((row, idx) => 
      row.is_primary && row.contact_type === data.contact_type && idx !== currentIndex
    )
    if (otherPrimary.length > 0) {
      errs.is_primary = `Only one primary contact allowed per contact type (${data.contact_type})`
    }
  }
  
  return Object.keys(errs).length ? errs : null
}

// Child Table: Data Periods
const dataPeriodsColumns = [
  { key: 'period_name', label: 'Period', width: '200px' },
  { key: 'start_date', label: 'Start', width: '120px', format: (v) => v ? new Date(v).toLocaleDateString() : '-' },
  { key: 'end_date', label: 'End', width: '120px', format: (v) => v ? new Date(v).toLocaleDateString() : '-' },
  { key: 'data_completeness', label: 'Completeness', width: '120px', component: 'Badge' },
]

// Inline editable columns for Data Periods (ERPNext-style)
const dataPeriodsInlineColumns = [
  {
    key: 'period_name',
    label: 'Period Name',
    width: '200px',
    fieldType: 'text',
    required: true,
    placeholder: 'e.g., Q1 2024'
  },
  {
    key: 'start_date',
    label: 'Start Date',
    width: '130px',
    fieldType: 'date',
    required: true
  },
  {
    key: 'end_date',
    label: 'End Date',
    width: '130px',
    fieldType: 'date',
    required: true
  },
  {
    key: 'data_completeness',
    label: 'Completeness',
    width: '130px',
    fieldType: 'select',
    options: [
      { label: 'Complete', value: 'Complete' },
      { label: 'Partial', value: 'Partial' },
      { label: 'Missing', value: 'Missing' },
    ],
    defaultValue: 'Complete',
    component: 'Badge',
    badgeTheme: {
      'Complete': 'green',
      'Partial': 'orange',
      'Missing': 'red'
    }
  },
  {
    key: 'notes',
    label: 'Notes',
    width: '200px',
    fieldType: 'text',
    placeholder: 'Additional notes'
  }
]

const dataPeriodsFormFields = [
  { name: 'period_name', label: 'Period Name', component: 'input', props: { type: 'text', required: true } },
  { name: 'start_date', label: 'Start Date', component: 'input', props: { type: 'date', required: true } },
  { name: 'end_date', label: 'End Date', component: 'input', props: { type: 'date', required: true } },
  {
    name: 'data_completeness',
    label: 'Data Completeness',
    component: 'select',
    props: {
      options: [
        { label: 'Complete', value: 'Complete' },
        { label: 'Partial', value: 'Partial' },
        { label: 'Missing', value: 'Missing' },
      ]
    },
    defaultValue: 'Complete'
  },
  { name: 'notes', label: 'Notes', component: 'textarea', props: { rows: 2 } },
]

const validateDataPeriod = (data) => {
  const errs = {}
  if (!data.period_name) errs.period_name = 'Period name is required'
  if (!data.start_date) errs.start_date = 'Start date is required'
  if (!data.end_date) errs.end_date = 'End date is required'
  if (data.start_date && data.end_date && new Date(data.end_date) <= new Date(data.start_date)) {
    errs.end_date = 'End date must be after start date'
  }
  return Object.keys(errs).length ? errs : null
}

// Child Table: BC Data Requirements
const bcDataReqColumns = [
  { key: 'data_type', label: 'Type', width: '150px' },
  { key: 'description', label: 'Description', width: '250px' },
  { key: 'source_system', label: 'Source', width: '120px' },
  { key: 'priority', label: 'Priority', width: '100px', component: 'Badge' },
  { key: 'status', label: 'Status', width: '100px', component: 'Badge' },
]

const bcDataReqFormFields = [
  {
    name: 'data_type',
    label: 'Data Type',
    component: 'select',
    props: {
      options: [
        { label: 'General Ledger', value: 'General Ledger' },
        { label: 'Accounts Payable', value: 'Accounts Payable' },
        { label: 'Accounts Receivable', value: 'Accounts Receivable' },
        { label: 'Inventory', value: 'Inventory' },
        { label: 'Fixed Assets', value: 'Fixed Assets' },
        { label: 'Payroll', value: 'Payroll' },
        { label: 'Sales Transactions', value: 'Sales Transactions' },
        { label: 'Purchase Transactions', value: 'Purchase Transactions' },
        { label: 'Bank Statements', value: 'Bank Statements' },
        { label: 'Reconciliations', value: 'Reconciliations' },
        { label: 'Other', value: 'Other' },
      ],
      required: true
    }
  },
  { name: 'description', label: 'Description', component: 'textarea', props: { rows: 2, required: true } },
  { name: 'source_system', label: 'Source System', component: 'input', props: { type: 'text' } },
  { name: 'required_fields', label: 'Required Fields', component: 'textarea', props: { rows: 2 } },
  { name: 'date_range_required', label: 'Date Range Required', component: 'checkbox' },
  { name: 'period_start', label: 'Period Start', component: 'input', props: { type: 'date' } },
  { name: 'period_end', label: 'Period End', component: 'input', props: { type: 'date' } },
  {
    name: 'priority',
    label: 'Priority',
    component: 'select',
    props: {
      options: [
        { label: 'Low', value: 'Low' },
        { label: 'Medium', value: 'Medium' },
        { label: 'High', value: 'High' },
        { label: 'Critical', value: 'Critical' },
      ]
    },
    defaultValue: 'Medium'
  },
  {
    name: 'status',
    label: 'Status',
    component: 'select',
    props: {
      options: [
        { label: 'Requested', value: 'Requested' },
        { label: 'Received', value: 'Received' },
        { label: 'Under Review', value: 'Under Review' },
        { label: 'Approved', value: 'Approved' },
        { label: 'Rejected', value: 'Rejected' },
      ]
    },
    defaultValue: 'Requested'
  },
  { name: 'requested_date', label: 'Requested Date', component: 'input', props: { type: 'date' } },
  { name: 'received_date', label: 'Received Date', component: 'input', props: { type: 'date' } },
  { name: 'data_quality_notes', label: 'Data Quality Notes', component: 'textarea', props: { rows: 2 } },
]

// Validation aligned with audit_data_requirement.py backend logic
const validateDataRequirement = (data) => {
  const errs = {}
  if (!data.data_type) errs.data_type = 'Data type is required'
  if (!data.description) errs.description = 'Description is required'
  
  // Period date validation - matches validate_dates() in backend
  if (data.period_start && data.period_end) {
    if (new Date(data.period_end) < new Date(data.period_start)) {
      errs.period_end = 'Period end date cannot be before period start date'
    }
  }
  
  // Auto-set requested_date if not provided (frontend default)
  // Backend also does this in set_requested_date()
  
  return Object.keys(errs).length ? errs : null
}

// Child Table: Amendments
const amendmentsColumns = [
  { key: 'amendment_date', label: 'Date', width: '120px', format: (v) => v ? new Date(v).toLocaleDateString() : '-' },
  { key: 'amendment_type', label: 'Type', width: '150px' },
  { key: 'description', label: 'Description', width: '250px' },
  { key: 'status', label: 'Status', width: '100px', component: 'Badge' },
]

const amendmentsFormFields = [
  { name: 'amendment_date', label: 'Amendment Date', component: 'input', props: { type: 'date', required: true } },
  {
    name: 'amendment_type',
    label: 'Amendment Type',
    component: 'select',
    props: {
      options: [
        { label: 'Scope Change', value: 'Scope Change' },
        { label: 'Timeline Extension', value: 'Timeline Extension' },
        { label: 'Budget Adjustment', value: 'Budget Adjustment' },
        { label: 'Resource Change', value: 'Resource Change' },
        { label: 'Methodology Change', value: 'Methodology Change' },
        { label: 'Other', value: 'Other' },
      ],
      required: true
    }
  },
  { name: 'description', label: 'Description', component: 'textarea', props: { rows: 2, required: true } },
  { name: 'reason', label: 'Reason', component: 'textarea', props: { rows: 2, required: true } },
  {
    name: 'approved_by',
    label: 'Approved By',
    component: LinkField,
    props: { doctype: 'User', filters: { enabled: 1 } }
  },
  { name: 'impact_on_timeline', label: 'Impact on Timeline', component: 'textarea', props: { rows: 2 } },
  { name: 'impact_on_budget', label: 'Impact on Budget', component: 'textarea', props: { rows: 2 } },
  {
    name: 'status',
    label: 'Status',
    component: 'select',
    props: {
      options: [
        { label: 'Draft', value: 'Draft' },
        { label: 'Approved', value: 'Approved' },
        { label: 'Rejected', value: 'Rejected' },
        { label: 'Implemented', value: 'Implemented' },
      ]
    },
    defaultValue: 'Draft'
  },
]

// Validation aligned with engagement_amendment.py backend logic
const validateAmendment = (data) => {
  const errs = {}
  if (!data.amendment_date) errs.amendment_date = 'Amendment date is required'
  if (!data.amendment_type) errs.amendment_type = 'Amendment type is required'
  if (!data.description) errs.description = 'Description is required'
  if (!data.reason) errs.reason = 'Reason is required'
  
  // Approval validation - matches validate_approval() in backend
  // Approved By is required for Approved or Implemented status
  if ((data.status === 'Approved' || data.status === 'Implemented') && !data.approved_by) {
    errs.approved_by = `Approval required for status: ${data.status}`
  }
  
  return Object.keys(errs).length ? errs : null
}

// Computed Properties
const currentSectionIndex = computed(() => 
  formSections.findIndex(s => s.id === activeSection.value)
)

const getSectionStatus = (sectionId) => {
  switch (sectionId) {
    case 'basic':
      return (form.engagement_title && form.audit_type && form.audit_universe) ? 'complete' : 
             (form.engagement_title || form.audit_type) ? 'partial' : 'incomplete'
    case 'scope':
      return (form.audit_objectives && form.audit_scope) ? 'complete' :
             (form.audit_objectives || form.audit_scope) ? 'partial' : 'incomplete'
    case 'methodology':
      return form.audit_approach ? 'complete' : 'incomplete'
    case 'timeline':
      return (form.period_start && form.period_end) ? 'complete' :
             (form.period_start || form.period_end) ? 'partial' : 'incomplete'
    case 'team':
      return (form.lead_auditor && form.audit_team.length > 0) ? 'complete' :
             (form.lead_auditor || form.audit_team.length > 0) ? 'partial' : 'incomplete'
    case 'contacts':
      return form.key_contacts.length > 0 ? 'complete' : 'incomplete'
    case 'data':
      return (form.data_periods.length > 0 || form.bc_data_requirements.length > 0) ? 'complete' : 'incomplete'
    case 'documentation':
      return 'complete' // Optional section
    default:
      return 'incomplete'
  }
}

const getSectionStatusClass = (sectionId) => {
  const status = getSectionStatus(sectionId)
  if (status === 'complete') return 'bg-green-500 text-white'
  if (status === 'partial') return 'bg-amber-500 text-white'
  return 'bg-gray-300 text-gray-600'
}

const completedSections = computed(() => 
  formSections.filter(s => getSectionStatus(s.id) === 'complete').length
)

const formProgress = computed(() => 
  Math.round((completedSections.value / formSections.length) * 100)
)

const isFormValid = computed(() => {
  return !!(
    form.engagement_title &&
    form.audit_type &&
    form.audit_universe &&
    form.audit_objectives &&
    form.audit_scope &&
    form.audit_approach &&
    form.period_start &&
    form.period_end &&
    form.lead_auditor &&
    form.audit_team.length > 0
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

  // Required fields validation
  if (!form.engagement_title) errs.engagement_title = 'Engagement title is required'
  if (!form.audit_type) errs.audit_type = 'Audit type is required'
  if (!form.audit_universe) errs.audit_universe = 'Audit universe is required'
  if (!form.audit_objectives) errs.audit_objectives = 'Audit objectives are required'
  if (!form.audit_scope) errs.audit_scope = 'Audit scope is required'
  if (!form.period_start) errs.period_start = 'Period start is required'
  if (!form.period_end) errs.period_end = 'Period end is required'
  if (!form.lead_auditor) errs.lead_auditor = 'Lead auditor is required'

  // Date validations
  if (form.period_start && form.period_end) {
    if (new Date(form.period_end) < new Date(form.period_start)) {
      errs.period_end = 'Period end must be after period start'
    }
  }

  // Child table validation
  if (form.audit_team.length === 0) {
    errs.audit_team = 'At least one team member is required'
  }

  Object.assign(errors, errs)
  return Object.keys(errs).length === 0
}

const prepareFormData = () => {
  return {
    ...form,
    // Ensure child tables have the proper format
    audit_team: form.audit_team.map(m => ({
      ...m,
      doctype: 'Audit Team Member'
    })),
    key_contacts: form.key_contacts.map(c => ({
      ...c,
      doctype: 'Audit Contact'
    })),
    data_periods: form.data_periods.map(p => ({
      ...p,
      doctype: 'Audit Engagement Data Period'
    })),
    bc_data_requirements: form.bc_data_requirements.map(r => ({
      ...r,
      doctype: 'Audit Data Requirement'
    })),
    amendments: form.amendments.map(a => ({
      ...a,
      doctype: 'Engagement Amendment'
    })),
  }
}

const handleSubmit = async () => {
  if (!validateForm()) {
    // Navigate to the first section with errors
    const firstErrorSection = formSections.find(s => {
      const status = getSectionStatus(s.id)
      return status !== 'complete'
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
      emit('updated', { ...formData, name: props.engagement.name })
    } else {
      emit('created', formData)
    }

    isOpen.value = false
  } catch (error) {
    console.error('Error saving engagement:', error)
  } finally {
    isSaving.value = false
  }
}

const saveAsDraft = async () => {
  try {
    isSavingDraft.value = true
    const formData = prepareFormData()
    emit('created', { ...formData, status: 'Planning' })
    isOpen.value = false
  } catch (error) {
    console.error('Error saving draft:', error)
  } finally {
    isSavingDraft.value = false
  }
}

const handleCancel = () => {
  emit('cancelled')
  isOpen.value = false
}

const resetForm = () => {
  Object.keys(form).forEach(key => {
    if (Array.isArray(form[key])) {
      form[key] = []
    } else if (typeof form[key] === 'number') {
      form[key] = null
    } else {
      form[key] = ''
    }
  })
  form.status = 'Planning'
  form.audit_approach = 'Risk-Based'
  Object.keys(errors).forEach(key => delete errors[key])
  activeSection.value = 'basic'
}

const loadEngagementData = (engagement) => {
  if (!engagement) return

  Object.keys(form).forEach(key => {
    if (engagement[key] !== undefined) {
      form[key] = engagement[key]
    }
  })
}

// Watchers
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    if (props.engagement) {
      loadEngagementData(props.engagement)
    } else {
      resetForm()
    }
  }
})

watch(() => props.engagement, (newVal) => {
  if (newVal && props.modelValue) {
    loadEngagementData(newVal)
  }
}, { deep: true })
</script>
