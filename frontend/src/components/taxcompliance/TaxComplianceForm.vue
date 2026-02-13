<template>
  <Dialog
    v-model="dialogVisible"
    :options="{
      size: '7xl',
      title: isEditing ? 'Edit Tax Compliance Tracker' : 'New Tax Compliance Tracker',
    }"
  >
    <template #body-content>
      <div class="flex h-[75vh]">
        <!-- Section Navigation Sidebar -->
        <div class="w-56 border-r pr-4 flex-shrink-0">
          <nav class="space-y-1 sticky top-0">
            <button
              v-for="(section, index) in sections"
              :key="section.id"
              @click="activeSection = section.id"
              :class="[
                'w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
                activeSection === section.id
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-gray-600 hover:bg-gray-50',
              ]"
            >
              <component
                :is="section.icon"
                class="h-4 w-4"
                :class="activeSection === section.id ? 'text-blue-600' : 'text-gray-400'"
              />
              <span class="flex-1">{{ section.label }}</span>
              <CheckCircle
                v-if="isSectionComplete(section.id)"
                class="h-4 w-4 text-green-500"
              />
            </button>
          </nav>

          <!-- Progress Summary -->
          <div class="mt-6 pt-6 border-t">
            <div class="text-xs font-medium text-gray-500 mb-2">Completion</div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full transition-all"
                :style="{ width: `${completionPercentage}%` }"
              />
            </div>
            <div class="text-xs text-gray-500 mt-1">{{ completionPercentage }}% complete</div>
          </div>
        </div>

        <!-- Form Content -->
        <div class="flex-1 pl-6 overflow-y-auto">
          <!-- Basic Information Section -->
          <div v-show="activeSection === 'basic'" class="space-y-6">
            <SectionHeader
              title="Basic Information"
              description="Tracker identification and tax period details"
            />

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                v-model="form.tracker_id"
                label="Tracker ID"
                type="text"
                :required="true"
                placeholder="Auto-generated if left empty"
              />
              <LinkField
                v-model="form.tax_period"
                label="Tax Period"
                doctype="Data Period"
                :required="true"
                placeholder="Select tax period"
              />
            </div>
          </div>

          <!-- VAT Compliance Section -->
          <div v-show="activeSection === 'vat'" class="space-y-6">
            <SectionHeader
              title="VAT Compliance"
              description="Value Added Tax calculations and filings"
            />

            <div class="grid grid-cols-3 gap-6">
              <FormControl
                v-model="form.vat_on_sales"
                label="VAT on Sales"
                type="number"
                placeholder="0.00"
                @change="calculateNetVat"
              />
              <FormControl
                v-model="form.vat_on_purchases"
                label="VAT on Purchases"
                type="number"
                placeholder="0.00"
                @change="calculateNetVat"
              />
              <FormControl
                v-model="form.net_vat_payable"
                label="Net VAT Payable"
                type="number"
                :disabled="true"
              />
            </div>

            <div class="border rounded-lg p-4 bg-gray-50">
              <h4 class="font-medium text-gray-700 mb-4">VAT Filing Details</h4>
              <div class="grid grid-cols-2 gap-6">
                <div class="flex items-center gap-3">
                  <input
                    type="checkbox"
                    v-model="form.vat_return_filed"
                    class="h-4 w-4 rounded border-gray-300 text-blue-600"
                  />
                  <label class="text-sm text-gray-700">VAT Return Filed</label>
                </div>
                <FormControl
                  v-model="form.vat_return_reference"
                  label="Return Reference"
                  type="text"
                  placeholder="Enter reference number"
                />
              </div>
              <div class="grid grid-cols-2 gap-6 mt-4">
                <FormControl
                  v-model="form.vat_filing_date"
                  label="Filing Date"
                  type="date"
                />
                <FormControl
                  v-model="form.vat_payment_date"
                  label="Payment Date"
                  type="date"
                />
              </div>
              <div class="grid grid-cols-2 gap-6 mt-4">
                <FormControl
                  v-model="form.vat_payment_amount"
                  label="Payment Amount"
                  type="number"
                  placeholder="0.00"
                />
                <FormControl
                  v-model="form.vat_payment_reference"
                  label="Payment Reference"
                  type="text"
                  placeholder="Enter payment reference"
                />
              </div>
              <div class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  VAT Reconciliation Document
                </label>
                <div class="border-2 border-dashed rounded-lg p-4 text-center">
                  <Upload class="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p class="text-sm text-gray-600">
                    <span class="text-blue-600 cursor-pointer hover:underline">
                      Click to upload
                    </span>
                    or drag and drop
                  </p>
                  <p class="text-xs text-gray-500 mt-1">PDF, XLS, XLSX up to 10MB</p>
                </div>
              </div>
            </div>
          </div>

          <!-- PAYE Compliance Section -->
          <div v-show="activeSection === 'paye'" class="space-y-6">
            <SectionHeader
              title="PAYE Compliance"
              description="Pay As You Earn tax calculations and filings"
            />

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                v-model="form.total_paye"
                label="Total PAYE"
                type="number"
                placeholder="0.00"
              />
              <div class="flex items-center gap-3 pt-6">
                <input
                  type="checkbox"
                  v-model="form.paye_return_filed"
                  class="h-4 w-4 rounded border-gray-300 text-blue-600"
                />
                <label class="text-sm text-gray-700">PAYE Return Filed</label>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-6">
              <FormControl
                v-model="form.paye_filing_date"
                label="Filing Date"
                type="date"
              />
              <FormControl
                v-model="form.paye_payment_date"
                label="Payment Date"
                type="date"
              />
              <FormControl
                v-model="form.paye_payment_reference"
                label="Payment Reference"
                type="text"
                placeholder="Enter reference"
              />
            </div>
          </div>

          <!-- Withholding Tax Section -->
          <div v-show="activeSection === 'wht'" class="space-y-6">
            <SectionHeader
              title="Withholding Tax Compliance"
              description="WHT calculations and filings"
            />

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                v-model="form.wht_on_services"
                label="WHT on Services"
                type="number"
                placeholder="0.00"
                @change="calculateTotalWht"
              />
              <FormControl
                v-model="form.wht_on_rent"
                label="WHT on Rent"
                type="number"
                placeholder="0.00"
                @change="calculateTotalWht"
              />
            </div>

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                v-model="form.wht_on_professional_fees"
                label="WHT on Professional Fees"
                type="number"
                placeholder="0.00"
                @change="calculateTotalWht"
              />
              <FormControl
                v-model="form.other_wht"
                label="Other WHT"
                type="number"
                placeholder="0.00"
                @change="calculateTotalWht"
              />
            </div>

            <div class="border rounded-lg p-4 bg-blue-50">
              <div class="flex items-center justify-between">
                <span class="font-medium text-blue-700">Total Withholding Tax</span>
                <span class="text-xl font-bold text-blue-800">
                  KES {{ formatNumber(form.total_wht || 0) }}
                </span>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-6">
              <div class="flex items-center gap-3">
                <input
                  type="checkbox"
                  v-model="form.wht_return_filed"
                  class="h-4 w-4 rounded border-gray-300 text-blue-600"
                />
                <label class="text-sm text-gray-700">WHT Return Filed</label>
              </div>
              <FormControl
                v-model="form.wht_filing_date"
                label="Filing Date"
                type="date"
              />
              <FormControl
                v-model="form.wht_payment_date"
                label="Payment Date"
                type="date"
              />
            </div>
          </div>

          <!-- Statutory Deductions Section (NSSF & NHIF) -->
          <div v-show="activeSection === 'statutory'" class="space-y-6">
            <SectionHeader
              title="Statutory Deductions"
              description="NSSF and NHIF contributions and filings"
            />

            <!-- NSSF -->
            <div class="border rounded-lg p-4">
              <h4 class="font-medium text-gray-700 mb-4 flex items-center gap-2">
                <Building class="h-5 w-5 text-blue-500" />
                NSSF Compliance
              </h4>
              <div class="grid grid-cols-3 gap-6">
                <FormControl
                  v-model="form.employee_contributions"
                  label="Employee Contributions"
                  type="number"
                  placeholder="0.00"
                  @change="calculateTotalNssf"
                />
                <FormControl
                  v-model="form.employer_contributions"
                  label="Employer Contributions"
                  type="number"
                  placeholder="0.00"
                  @change="calculateTotalNssf"
                />
                <FormControl
                  v-model="form.total_nssf"
                  label="Total NSSF"
                  type="number"
                  :disabled="true"
                />
              </div>
              <div class="grid grid-cols-2 gap-6 mt-4">
                <div class="flex items-center gap-3">
                  <input
                    type="checkbox"
                    v-model="form.nssf_return_filed"
                    class="h-4 w-4 rounded border-gray-300 text-blue-600"
                  />
                  <label class="text-sm text-gray-700">NSSF Return Filed</label>
                </div>
                <FormControl
                  v-model="form.nssf_payment_date"
                  label="Payment Date"
                  type="date"
                />
              </div>
            </div>

            <!-- NHIF -->
            <div class="border rounded-lg p-4">
              <h4 class="font-medium text-gray-700 mb-4 flex items-center gap-2">
                <Heart class="h-5 w-5 text-red-500" />
                NHIF Compliance
              </h4>
              <div class="grid grid-cols-2 gap-6">
                <FormControl
                  v-model="form.total_nhif"
                  label="Total NHIF"
                  type="number"
                  placeholder="0.00"
                />
                <FormControl
                  v-model="form.nhif_payment_date"
                  label="Payment Date"
                  type="date"
                />
              </div>
              <div class="flex items-center gap-3 mt-4">
                <input
                  type="checkbox"
                  v-model="form.nhif_return_filed"
                  class="h-4 w-4 rounded border-gray-300 text-blue-600"
                />
                <label class="text-sm text-gray-700">NHIF Return Filed</label>
              </div>
            </div>
          </div>

          <!-- Issues Section -->
          <div v-show="activeSection === 'issues'" class="space-y-6">
            <SectionHeader
              title="Issues & Compliance Score"
              description="Identified issues and overall compliance status"
            />

            <!-- Compliance Score -->
            <div class="border rounded-lg p-6 bg-gradient-to-r from-blue-50 to-gray-50">
              <div class="flex items-center justify-between mb-4">
                <h4 class="font-medium text-gray-700">Overall Compliance Score</h4>
                <Badge
                  :theme="getScoreTheme(form.compliance_score)"
                  size="lg"
                >
                  {{ form.compliance_score || 0 }}%
                </Badge>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-3">
                <div
                  class="h-3 rounded-full transition-all"
                  :class="getScoreBarClass(form.compliance_score)"
                  :style="{ width: `${form.compliance_score || 0}%` }"
                />
              </div>
            </div>

            <!-- Issues Table -->
            <div class="border rounded-lg overflow-hidden">
              <div class="bg-gray-50 px-4 py-3 border-b flex items-center justify-between">
                <h4 class="font-medium text-gray-700">Issues Identified</h4>
                <Button size="sm" variant="outline" @click="addIssue">
                  <template #prefix><Plus class="h-4 w-4" /></template>
                  Add Issue
                </Button>
              </div>
              <div class="divide-y max-h-64 overflow-y-auto">
                <div
                  v-for="(issue, index) in form.issues_identified"
                  :key="index"
                  class="p-4"
                >
                  <div class="grid grid-cols-12 gap-4 items-start">
                    <div class="col-span-2">
                      <Select
                        v-model="issue.issue_type"
                        :options="issueTypeOptions"
                        placeholder="Issue Type"
                      />
                    </div>
                    <div class="col-span-4">
                      <FormControl
                        v-model="issue.description"
                        type="textarea"
                        :rows="2"
                        placeholder="Describe the issue..."
                      />
                    </div>
                    <div class="col-span-2">
                      <FormControl
                        v-model="issue.financial_impact"
                        type="number"
                        placeholder="Impact"
                      />
                    </div>
                    <div class="col-span-2">
                      <Select
                        v-model="issue.resolution_status"
                        :options="resolutionStatusOptions"
                        placeholder="Status"
                      />
                    </div>
                    <div class="col-span-2 flex justify-end">
                      <Button
                        size="sm"
                        variant="ghost"
                        theme="red"
                        @click="removeIssue(index)"
                      >
                        <Trash2 class="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <div v-if="issue.resolution_notes || issue.resolution_status === 'Resolved'" class="mt-3">
                    <FormControl
                      v-model="issue.resolution_notes"
                      type="textarea"
                      :rows="2"
                      placeholder="Resolution notes..."
                    />
                  </div>
                </div>
                <div v-if="!form.issues_identified?.length" class="p-8 text-center text-gray-500">
                  <AlertCircle class="h-8 w-8 mx-auto mb-2 text-gray-400" />
                  <p>No issues identified</p>
                  <p class="text-sm mt-1">Click "Add Issue" to record any compliance issues</p>
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
            v-if="activeSection !== 'basic'"
            variant="outline"
            @click="previousSection"
          >
            <template #prefix><ChevronLeft class="h-4 w-4" /></template>
            Previous
          </Button>
        </div>
        <div class="flex items-center gap-2">
          <Button variant="outline" @click="dialogVisible = false">Cancel</Button>
          <Button
            v-if="activeSection !== 'issues'"
            variant="solid"
            @click="nextSection"
          >
            Next
            <template #suffix><ChevronRight class="h-4 w-4" /></template>
          </Button>
          <Button
            v-else
            variant="solid"
            theme="gray"
            :loading="saving"
            @click="saveTracker"
          >
            <template #prefix><Save class="h-4 w-4" /></template>
            {{ isEditing ? 'Update Tracker' : 'Create Tracker' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { Dialog, FormControl, Button, Badge, Select } from 'frappe-ui'
import SectionHeader from '@/components/Common/SectionHeader.vue'
import LinkField from '@/components/Common/fields/LinkField.vue'
import {
  FileText,
  Receipt,
  Briefcase,
  Percent,
  Building,
  Heart,
  AlertCircle,
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  Save,
  Plus,
  Trash2,
  Upload,
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

const isEditing = computed(() => !!props.tracker?.name)
const saving = ref(false)
const activeSection = ref('basic')

const sections = [
  { id: 'basic', label: 'Basic Info', icon: FileText },
  { id: 'vat', label: 'VAT', icon: Receipt },
  { id: 'paye', label: 'PAYE', icon: Briefcase },
  { id: 'wht', label: 'Withholding Tax', icon: Percent },
  { id: 'statutory', label: 'Statutory', icon: Building },
  { id: 'issues', label: 'Issues', icon: AlertCircle },
]

const form = reactive({
  tracker_id: '',
  tax_period: '',
  vat_on_sales: 0,
  vat_on_purchases: 0,
  net_vat_payable: 0,
  vat_return_filed: false,
  vat_return_reference: '',
  vat_filing_date: '',
  vat_payment_date: '',
  vat_payment_amount: 0,
  vat_payment_reference: '',
  vat_reconciliation: '',
  total_paye: 0,
  paye_return_filed: false,
  paye_filing_date: '',
  paye_payment_date: '',
  paye_payment_reference: '',
  wht_on_services: 0,
  wht_on_rent: 0,
  wht_on_professional_fees: 0,
  other_wht: 0,
  total_wht: 0,
  wht_return_filed: false,
  wht_filing_date: '',
  wht_payment_date: '',
  employee_contributions: 0,
  employer_contributions: 0,
  total_nssf: 0,
  nssf_return_filed: false,
  nssf_payment_date: '',
  total_nhif: 0,
  nhif_return_filed: false,
  nhif_payment_date: '',
  compliance_score: 0,
  issues_identified: [],
})

const issueTypeOptions = [
  { label: 'Late Filing', value: 'Late Filing' },
  { label: 'Late Payment', value: 'Late Payment' },
  { label: 'Underpayment', value: 'Underpayment' },
  { label: 'Documentation', value: 'Documentation' },
  { label: 'Other', value: 'Other' },
]

const resolutionStatusOptions = [
  { label: 'Open', value: 'Open' },
  { label: 'Resolved', value: 'Resolved' },
]

// Watch for tracker changes (edit mode)
watch(
  () => props.tracker,
  (newTracker) => {
    if (newTracker) {
      Object.keys(form).forEach((key) => {
        if (newTracker[key] !== undefined) {
          form[key] = newTracker[key]
        }
      })
    }
  },
  { immediate: true }
)

// Reset form when dialog opens
watch(
  () => props.show,
  (newShow) => {
    if (newShow && !props.tracker) {
      Object.keys(form).forEach((key) => {
        if (key === 'issues_identified') {
          form[key] = []
        } else if (typeof form[key] === 'boolean') {
          form[key] = false
        } else if (typeof form[key] === 'number') {
          form[key] = 0
        } else {
          form[key] = ''
        }
      })
      activeSection.value = 'basic'
    }
  }
)

// Calculations
function calculateNetVat() {
  form.net_vat_payable = (form.vat_on_sales || 0) - (form.vat_on_purchases || 0)
}

function calculateTotalWht() {
  form.total_wht =
    (form.wht_on_services || 0) +
    (form.wht_on_rent || 0) +
    (form.wht_on_professional_fees || 0) +
    (form.other_wht || 0)
}

function calculateTotalNssf() {
  form.total_nssf = (form.employee_contributions || 0) + (form.employer_contributions || 0)
}

// Issues management
function addIssue() {
  form.issues_identified.push({
    issue_type: '',
    description: '',
    financial_impact: 0,
    resolution_status: 'Open',
    resolution_notes: '',
  })
}

function removeIssue(index) {
  form.issues_identified.splice(index, 1)
}

// Section navigation
const sectionIndex = computed(() =>
  sections.findIndex((s) => s.id === activeSection.value)
)

function nextSection() {
  if (sectionIndex.value < sections.length - 1) {
    activeSection.value = sections[sectionIndex.value + 1].id
  }
}

function previousSection() {
  if (sectionIndex.value > 0) {
    activeSection.value = sections[sectionIndex.value - 1].id
  }
}

// Section completion check
function isSectionComplete(sectionId) {
  switch (sectionId) {
    case 'basic':
      return !!form.tracker_id && !!form.tax_period
    case 'vat':
      return form.vat_return_filed
    case 'paye':
      return form.paye_return_filed
    case 'wht':
      return form.wht_return_filed
    case 'statutory':
      return form.nssf_return_filed && form.nhif_return_filed
    case 'issues':
      return true
    default:
      return false
  }
}

const completionPercentage = computed(() => {
  const completed = sections.filter((s) => isSectionComplete(s.id)).length
  return Math.round((completed / sections.length) * 100)
})

// Helpers
function formatNumber(num) {
  return new Intl.NumberFormat('en-KE').format(num)
}

function getScoreTheme(score) {
  if (score >= 90) return 'green'
  if (score >= 70) return 'blue'
  if (score >= 50) return 'orange'
  return 'red'
}

function getScoreBarClass(score) {
  if (score >= 90) return 'bg-green-500'
  if (score >= 70) return 'bg-blue-500'
  if (score >= 50) return 'bg-orange-500'
  return 'bg-red-500'
}

async function saveTracker() {
  saving.value = true
  try {
    // API call would go here
    await new Promise((resolve) => setTimeout(resolve, 1000))
    emit('saved', { ...form })
    dialogVisible.value = false
  } catch (error) {
    console.error('Failed to save tracker:', error)
  } finally {
    saving.value = false
  }
}
</script>
