<template>
  <Dialog
    v-model="dialogVisible"
    :options="{
      title: mode === 'edit' ? 'Edit Audit Entity' : 'Create Audit Entity',
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
                :class="currentSection === index ? 'bg-gray-100 border border-gray-300' : 'hover:bg-gray-100'"
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
                <span class="text-xs font-semibold text-gray-900">{{ overallProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  class="bg-gray-900 h-1.5 rounded-full transition-all duration-500"
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
                description="Entity identification and classification"
                :sectionNumber="1"
                color="gray"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Universe ID <span class="text-red-500">*</span>
                    </label>
                    <div class="flex gap-2">
                      <FormControl
                        v-model="form.universe_id"
                        placeholder="e.g., AUE-001"
                        class="flex-1"
                      />
                      <Button variant="outline" size="sm" @click="generateUniverseId">
                        <RefreshCwIcon class="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <FormControl
                    v-model="form.auditable_entity"
                    label="Auditable Entity"
                    placeholder="Enter entity name"
                    :required="true"
                  />

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Entity Type <span class="text-red-500">*</span>
                    </label>
                    <FormControl
                      type="select"
                      v-model="form.entity_type"
                      :options="entityTypeOptions"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Department</label>
                    <LinkField
                      v-model="form.department"
                      doctype="Department"
                      placeholder="Select department"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                    <FormControl
                      type="select"
                      v-model="form.location"
                      :options="locationOptions"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Process Owner</label>
                    <LinkField
                      v-model="form.process_owner"
                      doctype="User"
                      placeholder="Select process owner"
                    />
                  </div>
                </div>

                <div class="mt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <TextEditor
                    :content="form.description"
                    @change="form.description = $event"
                    placeholder="Describe the auditable entity..."
                    :editable="true"
                    editorClass="min-h-[120px] prose-sm"
                  />
                </div>

                <div class="mt-6 flex items-center space-x-3">
                  <input
                    type="checkbox"
                    v-model="form.is_active"
                    class="h-4 w-4 text-gray-900 border-gray-300 rounded focus:ring-gray-900"
                  />
                  <label class="text-sm text-gray-700">Entity is Active</label>
                </div>
              </div>
            </div>

            <!-- Section 2: Risk Assessment -->
            <div v-show="currentSection === 1" class="space-y-6">
              <SectionHeader
                title="Risk Assessment"
                description="Inherent and residual risk evaluation"
                :sectionNumber="2"
                color="gray"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Inherent Risk Rating <span class="text-red-500">*</span>
                    </label>
                    <FormControl
                      type="select"
                      v-model="form.inherent_risk_rating"
                      :options="riskRatingOptions"
                    />
                  </div>

                  <FormControl
                    v-model="form.inherent_risk_score"
                    type="number"
                    label="Inherent Risk Score"
                    placeholder="0-100"
                    min="0"
                    max="100"
                  />

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Control Environment Rating
                    </label>
                    <FormControl
                      type="select"
                      v-model="form.control_environment_rating"
                      :options="controlEnvironmentOptions"
                    />
                  </div>

                  <FormControl
                    v-model="form.control_effectiveness_score"
                    type="number"
                    label="Control Effectiveness Score"
                    placeholder="0-100"
                    min="0"
                    max="100"
                  />

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Residual Risk Rating
                    </label>
                    <FormControl
                      type="select"
                      v-model="form.residual_risk_rating"
                      :options="riskRatingOptions"
                      disabled
                    />
                    <p class="text-xs text-gray-500 mt-1">Auto-calculated</p>
                  </div>

                  <FormControl
                    v-model="form.residual_risk_score"
                    type="number"
                    label="Residual Risk Score"
                    placeholder="Auto-calculated"
                    disabled
                  />
                </div>

                <!-- Risk Score Visualization -->
                <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h4 class="text-sm font-medium text-gray-900 mb-3">Risk Score Summary</h4>
                  <div class="grid grid-cols-3 gap-4">
                    <div class="text-center p-3 bg-white rounded-lg border">
                      <p class="text-2xl font-bold" :class="getRiskScoreColor(form.inherent_risk_score)">
                        {{ form.inherent_risk_score || 0 }}
                      </p>
                      <p class="text-xs text-gray-500">Inherent Risk</p>
                    </div>
                    <div class="text-center p-3 bg-white rounded-lg border">
                      <p class="text-2xl font-bold text-blue-600">
                        {{ form.control_effectiveness_score || 0 }}
                      </p>
                      <p class="text-xs text-gray-500">Control Score</p>
                    </div>
                    <div class="text-center p-3 bg-white rounded-lg border">
                      <p class="text-2xl font-bold" :class="getRiskScoreColor(form.residual_risk_score)">
                        {{ form.residual_risk_score || 0 }}
                      </p>
                      <p class="text-xs text-gray-500">Residual Risk</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 3: Risk Factors -->
            <div v-show="currentSection === 2" class="space-y-6">
              <SectionHeader
                title="Risk Factors"
                description="Identified risk factors for this entity"
                :sectionNumber="3"
                color="gray"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="flex items-center justify-between mb-4">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Risk Factors</h4>
                    <p class="text-xs text-gray-500">{{ form.risk_factors?.length || 0 }} factors identified</p>
                  </div>
                  <Button variant="outline" size="sm" @click="addRiskFactor">
                    <template #prefix><PlusIcon class="h-4 w-4" /></template>
                    Add Risk Factor
                  </Button>
                </div>

                <div v-if="form.risk_factors?.length > 0" class="space-y-4">
                  <div
                    v-for="(factor, index) in form.risk_factors"
                    :key="index"
                    class="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
                  >
                    <div class="flex items-start justify-between mb-4">
                      <Badge :variant="getRiskBadgeVariant(factor.risk_impact)" size="sm">
                        {{ factor.risk_impact || 'Not Rated' }}
                      </Badge>
                      <Button variant="ghost" size="sm" @click="removeRiskFactor(index)" class="text-red-500">
                        <TrashIcon class="h-4 w-4" />
                      </Button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Category</label>
                        <FormControl
                          type="select"
                          v-model="factor.risk_category"
                          :options="riskCategoryOptions"
                          size="sm"
                        />
                      </div>
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Impact</label>
                        <FormControl
                          type="select"
                          v-model="factor.risk_impact"
                          :options="impactOptions"
                          size="sm"
                        />
                      </div>
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Likelihood</label>
                        <FormControl
                          type="select"
                          v-model="factor.risk_likelihood"
                          :options="likelihoodOptions"
                          size="sm"
                        />
                      </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                      <FormControl
                        v-model="factor.risk_description"
                        type="textarea"
                        label="Description"
                        placeholder="Describe the risk factor..."
                        rows="2"
                        size="sm"
                      />
                      <div class="grid grid-cols-2 gap-4">
                        <FormControl
                          v-model="factor.risk_weight"
                          type="number"
                          label="Weight (%)"
                          placeholder="0-100"
                          min="0"
                          max="100"
                          size="sm"
                        />
                        <div>
                          <label class="block text-xs font-medium text-gray-700 mb-1">Mitigation</label>
                          <FormControl
                            type="select"
                            v-model="factor.mitigation_status"
                            :options="mitigationStatusOptions"
                            size="sm"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-else class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                  <AlertTriangleIcon class="mx-auto h-12 w-12 text-gray-400" />
                  <h3 class="mt-2 text-sm font-medium text-gray-900">No risk factors defined</h3>
                  <p class="mt-1 text-sm text-gray-500">Add risk factors to assess this entity.</p>
                  <Button variant="outline" size="sm" class="mt-4" @click="addRiskFactor">
                    <template #prefix><PlusIcon class="h-4 w-4" /></template>
                    Add First Risk Factor
                  </Button>
                </div>
              </div>
            </div>

            <!-- Section 4: Key Controls -->
            <div v-show="currentSection === 3" class="space-y-6">
              <SectionHeader
                title="Key Controls"
                description="Controls mitigating identified risks"
                :sectionNumber="4"
                color="gray"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="flex items-center justify-between mb-4">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">Key Controls</h4>
                    <p class="text-xs text-gray-500">{{ form.key_controls?.length || 0 }} controls defined</p>
                  </div>
                  <Button variant="outline" size="sm" @click="addKeyControl">
                    <template #prefix><PlusIcon class="h-4 w-4" /></template>
                    Add Control
                  </Button>
                </div>

                <div v-if="form.key_controls?.length > 0" class="space-y-4">
                  <div
                    v-for="(control, index) in form.key_controls"
                    :key="index"
                    class="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
                  >
                    <div class="flex items-start justify-between mb-4">
                      <div class="flex items-center gap-2">
                        <Badge variant="subtle" size="sm">{{ control.control_id || 'New' }}</Badge>
                        <Badge :variant="getControlEffectivenessVariant(control.control_effectiveness)" size="sm">
                          {{ control.control_effectiveness || 'Not Rated' }}
                        </Badge>
                      </div>
                      <Button variant="ghost" size="sm" @click="removeKeyControl(index)" class="text-red-500">
                        <TrashIcon class="h-4 w-4" />
                      </Button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <FormControl
                        v-model="control.control_id"
                        label="Control ID"
                        placeholder="CTL-001"
                        size="sm"
                      />
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Type</label>
                        <FormControl
                          type="select"
                          v-model="control.control_type"
                          :options="controlTypeOptions"
                          size="sm"
                        />
                      </div>
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Frequency</label>
                        <FormControl
                          type="select"
                          v-model="control.control_frequency"
                          :options="controlFrequencyOptions"
                          size="sm"
                        />
                      </div>
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Effectiveness</label>
                        <FormControl
                          type="select"
                          v-model="control.control_effectiveness"
                          :options="controlEffectivenessOptions"
                          size="sm"
                        />
                      </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                      <div class="md:col-span-2">
                        <FormControl
                          v-model="control.control_description"
                          type="textarea"
                          label="Description"
                          placeholder="Describe the control..."
                          rows="2"
                          size="sm"
                        />
                      </div>
                      <div>
                        <label class="block text-xs font-medium text-gray-700 mb-1">Control Owner</label>
                        <LinkField
                          v-model="control.control_owner"
                          doctype="User"
                          placeholder="Select owner"
                        />
                      </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4 mt-4">
                      <FormControl
                        v-model="control.last_tested_date"
                        type="date"
                        label="Last Tested"
                        size="sm"
                      />
                      <FormControl
                        v-model="control.next_test_date"
                        type="date"
                        label="Next Test Date"
                        size="sm"
                      />
                    </div>
                  </div>
                </div>

                <div v-else class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                  <ShieldIcon class="mx-auto h-12 w-12 text-gray-400" />
                  <h3 class="mt-2 text-sm font-medium text-gray-900">No controls defined</h3>
                  <p class="mt-1 text-sm text-gray-500">Add key controls for this entity.</p>
                  <Button variant="outline" size="sm" class="mt-4" @click="addKeyControl">
                    <template #prefix><PlusIcon class="h-4 w-4" /></template>
                    Add First Control
                  </Button>
                </div>
              </div>
            </div>

            <!-- Section 5: Audit Planning -->
            <div v-show="currentSection === 4" class="space-y-6">
              <SectionHeader
                title="Audit Planning"
                description="Audit frequency and scheduling information"
                :sectionNumber="5"
                color="gray"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Audit Frequency <span class="text-red-500">*</span>
                    </label>
                    <FormControl
                      type="select"
                      v-model="form.audit_frequency"
                      :options="auditFrequencyOptions"
                    />
                  </div>

                  <FormControl
                    v-model="form.last_audit_date"
                    type="date"
                    label="Last Audit Date"
                  />

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Last Audit Reference</label>
                    <LinkField
                      v-model="form.last_audit_reference"
                      doctype="Audit Engagement"
                      placeholder="Select engagement"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Last Audit Opinion</label>
                    <FormControl
                      type="select"
                      v-model="form.last_audit_opinion"
                      :options="auditOpinionOptions"
                    />
                  </div>

                  <FormControl
                    v-model="form.next_scheduled_audit"
                    type="date"
                    label="Next Scheduled Audit"
                    disabled
                  />

                  <div class="flex items-center space-x-3 pt-6">
                    <input
                      type="checkbox"
                      v-model="form.mandatory_audit"
                      class="h-4 w-4 text-gray-900 border-gray-300 rounded focus:ring-gray-900"
                    />
                    <label class="text-sm text-gray-700">Mandatory Audit (Regulatory)</label>
                  </div>
                </div>

                <div v-if="form.mandatory_audit" class="mt-6">
                  <FormControl
                    v-model="form.regulatory_reference"
                    label="Regulatory Reference"
                    placeholder="Enter regulatory requirement reference..."
                  />
                </div>

                <!-- Audit History Summary -->
                <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h4 class="text-sm font-medium text-gray-900 mb-3">Audit History Summary</h4>
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="text-center p-3 bg-white rounded-lg border">
                      <p class="text-lg font-bold text-gray-900">{{ form.last_audit_date ? formatDate(form.last_audit_date) : 'Never' }}</p>
                      <p class="text-xs text-gray-500">Last Audited</p>
                    </div>
                    <div class="text-center p-3 bg-white rounded-lg border">
                      <Badge :variant="getOpinionVariant(form.last_audit_opinion)" size="sm">
                        {{ form.last_audit_opinion || 'N/A' }}
                      </Badge>
                      <p class="text-xs text-gray-500 mt-1">Last Opinion</p>
                    </div>
                    <div class="text-center p-3 bg-white rounded-lg border">
                      <p class="text-lg font-bold text-blue-600">{{ form.audit_frequency || 'Not Set' }}</p>
                      <p class="text-xs text-gray-500">Frequency</p>
                    </div>
                    <div class="text-center p-3 bg-white rounded-lg border">
                      <p class="text-lg font-bold" :class="form.mandatory_audit ? 'text-red-600' : 'text-gray-600'">
                        {{ form.mandatory_audit ? 'Yes' : 'No' }}
                      </p>
                      <p class="text-xs text-gray-500">Mandatory</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 6: Additional Information -->
            <div v-show="currentSection === 5" class="space-y-6">
              <SectionHeader
                title="Additional Information"
                description="Notes and data source references"
                :sectionNumber="6"
                color="gray"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                  <TextEditor
                    :content="form.notes"
                    @change="form.notes = $event"
                    placeholder="Add any additional notes..."
                    :editable="true"
                    editorClass="min-h-[200px] prose-sm"
                  />
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
            theme="gray"
            @click="nextSection"
          >
            Next
            <template #suffix><ChevronRightIcon class="h-4 w-4" /></template>
          </Button>

          <Button
            v-else
            variant="solid"
            theme="gray"
            @click="submitForm"
            :loading="submitting"
            :disabled="!isFormValid"
          >
            <template #prefix><CheckIcon class="h-4 w-4" /></template>
            {{ mode === 'edit' ? 'Update Entity' : 'Create Entity' }}
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
  AlertTriangleIcon,
  CheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  PlusIcon,
  RefreshCwIcon,
  SaveIcon,
  ShieldIcon,
  TrashIcon,
} from 'lucide-vue-next'
import SectionHeader from '@/components/Common/SectionHeader.vue'
import LinkField from '@/components/Common/fields/LinkField.vue'
import { useAuditStore } from '@/stores/audit'

// Props
const props = defineProps({
  show: { type: Boolean, default: false },
  entity: { type: Object, default: null },
  mode: { type: String, default: 'create' },
})

// Emit
const emit = defineEmits(['update:show', 'saved', 'close'])

// Store
const auditStore = useAuditStore()

// State
const currentSection = ref(0)
const saving = ref(false)
const submitting = ref(false)
const lastSaved = ref(null)

// Computed for dialog visibility
const dialogVisible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value),
})

// Form data
const form = ref(getDefaultForm())

function getDefaultForm() {
  return {
    universe_id: '',
    auditable_entity: '',
    entity_type: 'Process',
    department: '',
    location: '',
    description: '',
    process_owner: '',
    is_active: true,
    inherent_risk_rating: 'Medium',
    inherent_risk_score: 0,
    control_environment_rating: 'Adequate',
    control_effectiveness_score: 0,
    residual_risk_rating: '',
    residual_risk_score: 0,
    risk_factors: [],
    key_controls: [],
    audit_frequency: 'Annual',
    last_audit_date: '',
    last_audit_reference: '',
    last_audit_opinion: '',
    next_scheduled_audit: '',
    mandatory_audit: false,
    regulatory_reference: '',
    bc_data_sources: [],
    notes: '',
  }
}

// Sections
const sections = [
  { id: 'basic', title: 'Basic Information', description: 'Entity details' },
  { id: 'risk', title: 'Risk Assessment', description: 'Risk ratings' },
  { id: 'factors', title: 'Risk Factors', description: 'Identified risks' },
  { id: 'controls', title: 'Key Controls', description: 'Mitigating controls' },
  { id: 'planning', title: 'Audit Planning', description: 'Scheduling' },
  { id: 'notes', title: 'Additional Info', description: 'Notes & references' },
]

// Options
const entityTypeOptions = [
  { label: 'Process', value: 'Process' },
  { label: 'Function', value: 'Function' },
  { label: 'Department', value: 'Department' },
  { label: 'Location', value: 'Location' },
  { label: 'System', value: 'System' },
  { label: 'Compliance Area', value: 'Compliance Area' },
]

const locationOptions = [
  { label: 'Head Office', value: 'Head Office' },
  { label: 'Branch 1', value: 'Branch 1' },
  { label: 'Branch 2', value: 'Branch 2' },
  { label: 'Warehouse', value: 'Warehouse' },
  { label: 'All', value: 'All' },
]

const riskRatingOptions = [
  { label: 'Critical', value: 'Critical' },
  { label: 'High', value: 'High' },
  { label: 'Medium', value: 'Medium' },
  { label: 'Low', value: 'Low' },
]

const controlEnvironmentOptions = [
  { label: 'Strong', value: 'Strong' },
  { label: 'Adequate', value: 'Adequate' },
  { label: 'Weak', value: 'Weak' },
  { label: 'Not Assessed', value: 'Not Assessed' },
]

const riskCategoryOptions = [
  { label: 'Financial', value: 'Financial' },
  { label: 'Operational', value: 'Operational' },
  { label: 'Compliance', value: 'Compliance' },
  { label: 'Strategic', value: 'Strategic' },
  { label: 'Reputational', value: 'Reputational' },
  { label: 'Technology', value: 'Technology' },
  { label: 'Human Resources', value: 'Human Resources' },
]

const impactOptions = [
  { label: 'Critical', value: 'Critical' },
  { label: 'High', value: 'High' },
  { label: 'Medium', value: 'Medium' },
  { label: 'Low', value: 'Low' },
]

const likelihoodOptions = [
  { label: 'Very High', value: 'Very High' },
  { label: 'High', value: 'High' },
  { label: 'Medium', value: 'Medium' },
  { label: 'Low', value: 'Low' },
]

const mitigationStatusOptions = [
  { label: 'Not Mitigated', value: 'Not Mitigated' },
  { label: 'Partially Mitigated', value: 'Partially Mitigated' },
  { label: 'Fully Mitigated', value: 'Fully Mitigated' },
  { label: 'Accepted', value: 'Accepted' },
]

const controlTypeOptions = [
  { label: 'Preventive', value: 'Preventive' },
  { label: 'Detective', value: 'Detective' },
  { label: 'Corrective', value: 'Corrective' },
  { label: 'Directive', value: 'Directive' },
]

const controlFrequencyOptions = [
  { label: 'Continuous', value: 'Continuous' },
  { label: 'Daily', value: 'Daily' },
  { label: 'Weekly', value: 'Weekly' },
  { label: 'Monthly', value: 'Monthly' },
  { label: 'Quarterly', value: 'Quarterly' },
  { label: 'Annually', value: 'Annually' },
  { label: 'Ad-hoc', value: 'Ad-hoc' },
]

const controlEffectivenessOptions = [
  { label: 'Very Effective', value: 'Very Effective' },
  { label: 'Effective', value: 'Effective' },
  { label: 'Partially Effective', value: 'Partially Effective' },
  { label: 'Ineffective', value: 'Ineffective' },
]

const auditFrequencyOptions = [
  { label: 'Quarterly', value: 'Quarterly' },
  { label: 'Semi-Annual', value: 'Semi-Annual' },
  { label: 'Annual', value: 'Annual' },
  { label: 'Bi-Annual', value: 'Bi-Annual' },
  { label: 'Tri-Annual', value: 'Tri-Annual' },
  { label: 'As Needed', value: 'As Needed' },
]

const auditOpinionOptions = [
  { label: 'Satisfactory', value: 'Satisfactory' },
  { label: 'Needs Improvement', value: 'Needs Improvement' },
  { label: 'Unsatisfactory', value: 'Unsatisfactory' },
]

// Watch for entity changes
watch(() => props.entity, (newEntity) => {
  if (newEntity) {
    form.value = {
      ...getDefaultForm(),
      ...newEntity,
      risk_factors: newEntity.risk_factors || [],
      key_controls: newEntity.key_controls || [],
      bc_data_sources: newEntity.bc_data_sources || [],
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

// Auto-calculate residual risk
watch([() => form.value.inherent_risk_score, () => form.value.control_effectiveness_score], () => {
  const inherent = form.value.inherent_risk_score || 0
  const control = form.value.control_effectiveness_score || 0
  form.value.residual_risk_score = Math.max(0, inherent - (inherent * control / 100))
  
  // Determine rating based on score
  if (form.value.residual_risk_score >= 75) {
    form.value.residual_risk_rating = 'Critical'
  } else if (form.value.residual_risk_score >= 50) {
    form.value.residual_risk_rating = 'High'
  } else if (form.value.residual_risk_score >= 25) {
    form.value.residual_risk_rating = 'Medium'
  } else {
    form.value.residual_risk_rating = 'Low'
  }
})

// Computed
const overallProgress = computed(() => {
  let completed = 0
  if (form.value.universe_id && form.value.auditable_entity && form.value.entity_type) completed += 20
  if (form.value.inherent_risk_rating) completed += 20
  if (form.value.risk_factors?.length > 0) completed += 20
  if (form.value.key_controls?.length > 0) completed += 20
  if (form.value.audit_frequency) completed += 20
  return completed
})

const isFormValid = computed(() => {
  return form.value.universe_id &&
    form.value.auditable_entity &&
    form.value.entity_type &&
    form.value.inherent_risk_rating
})

// Methods
const isSectionComplete = (sectionId) => {
  switch (sectionId) {
    case 'basic':
      return form.value.universe_id && form.value.auditable_entity && form.value.entity_type
    case 'risk':
      return !!form.value.inherent_risk_rating
    case 'factors':
      return form.value.risk_factors?.length > 0
    case 'controls':
      return form.value.key_controls?.length > 0
    case 'planning':
      return !!form.value.audit_frequency
    case 'notes':
      return true
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

const generateUniverseId = () => {
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0')
  form.value.universe_id = `AUE-${random}`
}

const addRiskFactor = () => {
  form.value.risk_factors.push({
    risk_category: 'Operational',
    risk_description: '',
    risk_impact: 'Medium',
    risk_likelihood: 'Medium',
    risk_weight: 0,
    mitigation_status: 'Not Mitigated',
  })
}

const removeRiskFactor = (index) => {
  form.value.risk_factors.splice(index, 1)
}

const addKeyControl = () => {
  form.value.key_controls.push({
    control_id: '',
    control_description: '',
    control_type: 'Preventive',
    control_owner: '',
    control_frequency: 'Monthly',
    control_effectiveness: 'Effective',
    last_tested_date: '',
    next_test_date: '',
  })
}

const removeKeyControl = (index) => {
  form.value.key_controls.splice(index, 1)
}

const getRiskScoreColor = (score) => {
  if (score >= 75) return 'text-red-600'
  if (score >= 50) return 'text-orange-600'
  if (score >= 25) return 'text-amber-600'
  return 'text-green-600'
}

const getRiskBadgeVariant = (impact) => {
  const variants = {
    'Critical': 'subtle',
    'High': 'subtle',
    'Medium': 'subtle',
    'Low': 'subtle',
  }
  return variants[impact] || 'subtle'
}

const getControlEffectivenessVariant = (effectiveness) => {
  return 'subtle'
}

const getOpinionVariant = (opinion) => {
  const variants = {
    'Satisfactory': 'subtle',
    'Needs Improvement': 'subtle',
    'Unsatisfactory': 'subtle',
  }
  return variants[opinion] || 'subtle'
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const saveDraft = async () => {
  saving.value = true
  try {
    if (props.mode === 'edit' && props.entity?.name) {
      await auditStore.updateAuditUniverse(props.entity.name, form.value)
    } else {
      await auditStore.createAuditUniverse(form.value)
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
    if (props.mode === 'edit' && props.entity?.name) {
      await auditStore.updateAuditUniverse(props.entity.name, form.value)
    } else {
      await auditStore.createAuditUniverse(form.value)
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
