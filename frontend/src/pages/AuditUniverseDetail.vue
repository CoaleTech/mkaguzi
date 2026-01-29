<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <Button variant="ghost" @click="goBack">
          <ArrowLeftIcon class="h-4 w-4 mr-2" />
          Back to Audit Universe
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">
            {{ mode === 'new' ? 'New Audit Universe Entity' : entity?.auditable_entity || 'Audit Universe Entity' }}
          </h1>
          <p class="text-gray-600 mt-1">
            {{ mode === 'view' ? 'View entity details and risk assessment' : mode === 'edit' ? 'Edit entity information' : 'Create new auditable entity' }}
          </p>
        </div>
      </div>
      <div class="flex items-center space-x-3" v-if="mode !== 'new'">
        <Badge :variant="getRiskVariant(entity?.residual_risk_rating)">
          {{ entity?.residual_risk_rating }} Risk
        </Badge>
        <Badge :variant="entity?.is_active ? 'success' : 'secondary'">
          {{ entity?.is_active ? 'Active' : 'Inactive' }}
        </Badge>
        <div class="flex items-center space-x-2">
          <Button
            v-if="mode === 'view'"
            variant="outline"
            @click="switchMode('edit')"
          >
            <EditIcon class="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button
            v-if="mode === 'edit'"
            variant="outline"
            @click="switchMode('view')"
          >
            <EyeIcon class="h-4 w-4 mr-2" />
            View
          </Button>
          <Button
            v-if="mode === 'view' && canScheduleAudit"
            variant="outline"
            @click="scheduleAudit"
          >
            <CalendarIcon class="h-4 w-4 mr-2" />
            Schedule Audit
          </Button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <span class="ml-3 text-gray-600">Loading...</span>
    </div>

    <!-- Main Content -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Form -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Basic Information -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Auditable Entity *</label>
              <Input
                v-model="form.auditable_entity"
                :readonly="mode === 'view'"
                placeholder="e.g., Accounts Payable, IT Security Controls"
                class="w-full"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Entity Type *</label>
              <Select
                v-model="form.entity_type"
                :options="entityTypeOptions"
                :disabled="mode === 'view'"
                placeholder="Select entity type"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Department</label>
              <Select
                v-model="form.department"
                :options="departmentOptions"
                :disabled="mode === 'view'"
                placeholder="Select department"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <Select
                v-model="form.location"
                :options="locationOptions"
                :disabled="mode === 'view'"
                placeholder="Select location"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Process Owner</label>
              <Input
                v-model="form.process_owner"
                :readonly="mode === 'view'"
                placeholder="Name of responsible person"
                class="w-full"
              />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <Textarea
                v-model="form.description"
                :readonly="mode === 'view'"
                placeholder="Detailed description of the auditable entity"
                rows="3"
                class="w-full"
              />
            </div>
          </div>
        </div>

        <!-- Risk Assessment -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Risk Assessment</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Inherent Risk -->
            <div class="space-y-4">
              <h4 class="font-medium text-gray-900">Inherent Risk</h4>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Risk Rating</label>
                <Select
                  v-model="form.inherent_risk_rating"
                  :options="riskRatingOptions"
                  :disabled="mode === 'view'"
                  @change="calculateRiskScores"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Risk Score</label>
                <Input
                  v-model.number="form.inherent_risk_score"
                  :readonly="mode === 'view'"
                  type="number"
                  min="1"
                  max="25"
                  @input="calculateResidualRisk"
                />
              </div>
            </div>

            <!-- Control Environment -->
            <div class="space-y-4">
              <h4 class="font-medium text-gray-900">Control Environment</h4>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Control Rating</label>
                <Select
                  v-model="form.control_environment_rating"
                  :options="controlRatingOptions"
                  :disabled="mode === 'view'"
                  @change="calculateRiskScores"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Effectiveness Score</label>
                <Input
                  v-model.number="form.control_effectiveness_score"
                  :readonly="mode === 'view'"
                  type="number"
                  min="1"
                  max="5"
                  @input="calculateResidualRisk"
                />
              </div>
            </div>
          </div>

          <!-- Residual Risk (Calculated) -->
          <div class="mt-6 p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="font-medium text-gray-900">Residual Risk</h4>
                <p class="text-sm text-gray-600">Calculated based on inherent risk and control effectiveness</p>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold" :class="getRiskColorClass(form.residual_risk_rating)">
                  {{ form.residual_risk_rating }}
                </div>
                <div class="text-sm text-gray-600">Score: {{ form.residual_risk_score }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Risk Factors -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Risk Factors</h3>
            <Button
              v-if="mode !== 'view'"
              variant="outline"
              size="sm"
              @click="addRiskFactor"
            >
              <PlusIcon class="h-4 w-4 mr-2" />
              Add Factor
            </Button>
          </div>
          <div class="space-y-4">
            <div
              v-for="(factor, index) in form.risk_factors"
              :key="index"
              class="p-4 border border-gray-200 rounded-lg"
            >
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <Select
                    v-model="factor.risk_category"
                    :options="riskCategoryOptions"
                    :disabled="mode === 'view'"
                    size="sm"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Likelihood</label>
                  <Select
                    v-model="factor.likelihood"
                    :options="likelihoodOptions"
                    :disabled="mode === 'view'"
                    size="sm"
                    @change="calculateFactorScore(factor)"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Impact</label>
                  <Select
                    v-model="factor.impact"
                    :options="impactOptions"
                    :disabled="mode === 'view'"
                    size="sm"
                    @change="calculateFactorScore(factor)"
                  />
                </div>
                <div class="flex items-end space-x-2">
                  <div class="flex-1">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Score</label>
                    <Input
                      v-model.number="factor.risk_score"
                      readonly
                      size="sm"
                      class="text-center font-medium"
                    />
                  </div>
                  <Button
                    v-if="mode !== 'view'"
                    variant="ghost"
                    size="sm"
                    @click="removeRiskFactor(index)"
                    class="text-red-600 hover:text-red-700"
                  >
                    <XIcon class="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div class="mt-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <Textarea
                  v-model="factor.risk_description"
                  :readonly="mode === 'view'"
                  placeholder="Describe the risk factor"
                  rows="2"
                  size="sm"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Key Controls -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Key Controls</h3>
            <Button
              v-if="mode !== 'view'"
              variant="outline"
              size="sm"
              @click="addKeyControl"
            >
              <PlusIcon class="h-4 w-4 mr-2" />
              Add Control
            </Button>
          </div>
          <div class="space-y-4">
            <div
              v-for="(control, index) in form.key_controls"
              :key="index"
              class="p-4 border border-gray-200 rounded-lg"
            >
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Control Description</label>
                  <Textarea
                    v-model="control.control_description"
                    :readonly="mode === 'view'"
                    placeholder="Describe the control activity"
                    rows="2"
                    size="sm"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Control Type</label>
                  <Select
                    v-model="control.control_type"
                    :options="controlTypeOptions"
                    :disabled="mode === 'view'"
                    size="sm"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
                  <Select
                    v-model="control.control_frequency"
                    :options="frequencyOptions"
                    :disabled="mode === 'view'"
                    size="sm"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Effectiveness</label>
                  <Select
                    v-model="control.control_effectiveness"
                    :options="effectivenessOptions"
                    :disabled="mode === 'view'"
                    size="sm"
                  />
                </div>
                <div class="flex items-end">
                  <Button
                    v-if="mode !== 'view'"
                    variant="ghost"
                    size="sm"
                    @click="removeKeyControl(index)"
                    class="text-red-600 hover:text-red-700"
                  >
                    <XIcon class="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Audit Information -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Audit Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Audit Frequency</label>
              <Select
                v-model="form.audit_frequency"
                :options="auditFrequencyOptions"
                :disabled="mode === 'view'"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Last Audit Date</label>
              <Input
                v-model="form.last_audit_date"
                :readonly="mode === 'view'"
                type="date"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Last Audit Opinion</label>
              <Select
                v-model="form.last_audit_opinion"
                :options="auditOpinionOptions"
                :disabled="mode === 'view'"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Next Scheduled Audit</label>
              <Input
                v-model="form.next_scheduled_audit"
                :readonly="mode === 'view'"
                type="date"
              />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Regulatory Reference</label>
              <Input
                v-model="form.regulatory_reference"
                :readonly="mode === 'view'"
                placeholder="e.g., CBK Prudential Guidelines"
              />
            </div>
          </div>
          <div class="mt-4">
            <Checkbox
              v-model="form.mandatory_audit"
              :disabled="mode === 'view'"
              label="Mandatory Regulatory Audit"
            />
          </div>
        </div>

        <!-- Additional Information -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Additional Information</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
              <Textarea
                v-model="form.notes"
                :readonly="mode === 'view'"
                placeholder="Additional notes and comments"
                rows="3"
              />
            </div>
            <div>
              <Checkbox
                v-model="form.is_active"
                :disabled="mode === 'view'"
                label="Entity is Active"
              />
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div v-if="mode !== 'view'" class="flex items-center justify-end space-x-3">
          <Button variant="outline" @click="cancel">
            Cancel
          </Button>
          <Button @click="save" :loading="saving">
            {{ mode === 'new' ? 'Create Entity' : 'Save Changes' }}
          </Button>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Risk Summary Card -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Risk Summary</h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Inherent Risk:</span>
              <Badge :variant="getRiskVariant(form.inherent_risk_rating)">
                {{ form.inherent_risk_rating }} ({{ form.inherent_risk_score }})
              </Badge>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Control Effectiveness:</span>
              <Badge :variant="getControlVariant(form.control_environment_rating)">
                {{ form.control_environment_rating }} ({{ form.control_effectiveness_score }})
              </Badge>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Residual Risk:</span>
              <Badge :variant="getRiskVariant(form.residual_risk_rating)">
                {{ form.residual_risk_rating }} ({{ form.residual_risk_score }})
              </Badge>
            </div>
          </div>
        </div>

        <!-- Audit Schedule Card -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Audit Schedule</h3>
          <div class="space-y-4">
            <div>
              <span class="text-sm text-gray-600">Frequency:</span>
              <p class="font-medium">{{ form.audit_frequency || 'Not set' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-600">Last Audit:</span>
              <p class="font-medium">{{ form.last_audit_date ? formatDate(form.last_audit_date) : 'Never' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-600">Next Scheduled:</span>
              <p class="font-medium">{{ form.next_scheduled_audit ? formatDate(form.next_scheduled_audit) : 'Not scheduled' }}</p>
            </div>
            <div v-if="isOverdue">
              <Badge variant="danger">Overdue</Badge>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div v-if="mode === 'view'" class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div class="space-y-3">
            <Button variant="outline" class="w-full justify-start" @click="scheduleAudit">
              <CalendarIcon class="h-4 w-4 mr-2" />
              Schedule Audit
            </Button>
            <Button variant="outline" class="w-full justify-start" @click="viewAuditHistory">
              <HistoryIcon class="h-4 w-4 mr-2" />
              View Audit History
            </Button>
            <Button variant="outline" class="w-full justify-start" @click="generateReport">
              <FileTextIcon class="h-4 w-4 mr-2" />
              Generate Report
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, Checkbox, Input, Select, Textarea } from "frappe-ui"
import {
	ArrowLeftIcon,
	CalendarIcon,
	EditIcon,
	EyeIcon,
	FileTextIcon,
	HistoryIcon,
	PlusIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"

// Props
const props = defineProps({
	entityId: {
		type: String,
		default: null,
	},
	mode: {
		type: String,
		default: "view",
		validator: (value) => ["view", "edit", "new"].includes(value),
	},
})

// Composables
const router = useRouter()
const route = useRoute()

// Reactive state
const loading = ref(false)
const saving = ref(false)
const entity = ref(null)

const form = ref({
	auditable_entity: "",
	entity_type: "",
	department: "",
	location: "",
	description: "",
	process_owner: "",
	inherent_risk_rating: "",
	inherent_risk_score: 1,
	control_environment_rating: "",
	control_effectiveness_score: 1,
	residual_risk_rating: "",
	residual_risk_score: 1,
	risk_factors: [],
	key_controls: [],
	audit_frequency: "",
	last_audit_date: "",
	last_audit_opinion: "",
	next_scheduled_audit: "",
	mandatory_audit: false,
	regulatory_reference: "",
	notes: "",
	is_active: true,
})

// Options
const entityTypeOptions = [
	{ label: "Process", value: "Process" },
	{ label: "Function", value: "Function" },
	{ label: "Department", value: "Department" },
	{ label: "Location", value: "Location" },
	{ label: "System", value: "System" },
	{ label: "Compliance Area", value: "Compliance Area" },
]

const departmentOptions = [
	{ label: "Finance", value: "Finance" },
	{ label: "IT", value: "IT" },
	{ label: "Operations", value: "Operations" },
	{ label: "HR", value: "HR" },
	{ label: "Sales", value: "Sales" },
	{ label: "Procurement", value: "Procurement" },
]

const locationOptions = [
	{ label: "Head Office", value: "Head Office" },
	{ label: "Branch 1", value: "Branch 1" },
	{ label: "Branch 2", value: "Branch 2" },
	{ label: "Warehouse", value: "Warehouse" },
	{ label: "All Locations", value: "All" },
]

const riskRatingOptions = [
	{ label: "Critical", value: "Critical" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

const controlRatingOptions = [
	{ label: "Strong", value: "Strong" },
	{ label: "Adequate", value: "Adequate" },
	{ label: "Weak", value: "Weak" },
	{ label: "Not Assessed", value: "Not Assessed" },
]

const riskCategoryOptions = [
	{ label: "Financial", value: "Financial" },
	{ label: "Operational", value: "Operational" },
	{ label: "Compliance", value: "Compliance" },
	{ label: "Strategic", value: "Strategic" },
	{ label: "IT", value: "IT" },
	{ label: "Reputational", value: "Reputational" },
]

const likelihoodOptions = [
	{ label: "Rare", value: "Rare" },
	{ label: "Unlikely", value: "Unlikely" },
	{ label: "Possible", value: "Possible" },
	{ label: "Likely", value: "Likely" },
	{ label: "Almost Certain", value: "Almost Certain" },
]

const impactOptions = [
	{ label: "Insignificant", value: "Insignificant" },
	{ label: "Minor", value: "Minor" },
	{ label: "Moderate", value: "Moderate" },
	{ label: "Major", value: "Major" },
	{ label: "Catastrophic", value: "Catastrophic" },
]

const controlTypeOptions = [
	{ label: "Preventive", value: "Preventive" },
	{ label: "Detective", value: "Detective" },
	{ label: "Corrective", value: "Corrective" },
]

const frequencyOptions = [
	{ label: "Continuous", value: "Continuous" },
	{ label: "Daily", value: "Daily" },
	{ label: "Weekly", value: "Weekly" },
	{ label: "Monthly", value: "Monthly" },
	{ label: "Quarterly", value: "Quarterly" },
	{ label: "Annually", value: "Annually" },
]

const effectivenessOptions = [
	{ label: "Effective", value: "Effective" },
	{ label: "Partially Effective", value: "Partially Effective" },
	{ label: "Ineffective", value: "Ineffective" },
	{ label: "Not Tested", value: "Not Tested" },
]

const auditFrequencyOptions = [
	{ label: "Quarterly", value: "Quarterly" },
	{ label: "Semi-Annual", value: "Semi-Annual" },
	{ label: "Annual", value: "Annual" },
	{ label: "Bi-Annual", value: "Bi-Annual" },
	{ label: "Tri-Annual", value: "Tri-Annual" },
	{ label: "As Needed", value: "As Needed" },
]

const auditOpinionOptions = [
	{ label: "Satisfactory", value: "Satisfactory" },
	{ label: "Needs Improvement", value: "Needs Improvement" },
	{ label: "Unsatisfactory", value: "Unsatisfactory" },
]

const dataTypeOptions = [
	{ label: "General Ledger Entries", value: "General Ledger Entries" },
	{ label: "Item Master Data", value: "Item Master Data" },
	{ label: "Item Ledger Entries", value: "Item Ledger Entries" },
	{ label: "Sales Invoices", value: "Sales Invoices" },
	{ label: "Purchase Invoices", value: "Purchase Invoices" },
	{ label: "Customer Ledger Entries", value: "Customer Ledger Entries" },
	{ label: "Vendor Ledger Entries", value: "Vendor Ledger Entries" },
	{
		label: "Bank Account Ledger Entries",
		value: "Bank Account Ledger Entries",
	},
]

const relevanceOptions = [
	{ label: "Primary", value: "Primary" },
	{ label: "Secondary", value: "Secondary" },
	{ label: "Reference", value: "Reference" },
]

// Computed properties
const isOverdue = computed(() => {
	if (!form.value.next_scheduled_audit) return false
	const nextAudit = new Date(form.value.next_scheduled_audit)
	const today = new Date()
	return nextAudit < today
})

const canScheduleAudit = computed(() => {
	return form.value.is_active && form.value.auditable_entity
})

// Methods
const goBack = () => {
	router.push("/audit-planning/universe")
}

const switchMode = (newMode) => {
	if (newMode === "edit") {
		router.push(`/audit-planning/universe/${props.entityId}/edit`)
	} else {
		router.push(`/audit-planning/universe/${props.entityId}`)
	}
}

const loadEntity = async () => {
	if (props.mode === "new") return

	loading.value = true
	try {
		// In a real app, this would be an API call
		// For now, we'll simulate loading mock data
		await new Promise((resolve) => setTimeout(resolve, 1000))

		// Mock data - replace with actual API call
		entity.value = {
			universe_id: "AU-001",
			auditable_entity: "Accounts Payable",
			entity_type: "Process",
			department: "Finance",
			location: "Head Office",
			description: "Processing of vendor payments and expense reimbursements",
			process_owner: "John Doe",
			inherent_risk_rating: "High",
			inherent_risk_score: 15,
			control_environment_rating: "Adequate",
			control_effectiveness_score: 3,
			residual_risk_rating: "Medium",
			residual_risk_score: 5,
			risk_factors: [
				{
					risk_category: "Financial",
					risk_description: "Payment errors leading to overpayments",
					likelihood: "Possible",
					impact: "Moderate",
					risk_score: 12,
				},
			],
			key_controls: [
				{
					control_description: "Three-way matching of PO, receipt, and invoice",
					control_type: "Preventive",
					control_frequency: "Continuous",
					control_effectiveness: "Effective",
				},
			],
			audit_frequency: "Quarterly",
			last_audit_date: "2023-10-15",
			last_audit_opinion: "Satisfactory",
			next_scheduled_audit: "2024-01-15",
			mandatory_audit: false,
			regulatory_reference: "",
			notes: "Regular monitoring required due to high transaction volume",
			is_active: true,
		}

		// Populate form with entity data
		Object.assign(form.value, entity.value)
	} catch (error) {
		console.error("Error loading entity:", error)
	} finally {
		loading.value = false
	}
}

const calculateRiskScores = () => {
	// Calculate inherent risk score based on rating
	const inherentScores = { Critical: 25, High: 15, Medium: 8, Low: 3 }
	form.value.inherent_risk_score =
		inherentScores[form.value.inherent_risk_rating] || 1

	// Calculate control effectiveness score based on rating
	const controlScores = { Strong: 5, Adequate: 3, Weak: 1, "Not Assessed": 1 }
	form.value.control_effectiveness_score =
		controlScores[form.value.control_environment_rating] || 1

	calculateResidualRisk()
}

const calculateResidualRisk = () => {
	// Simple residual risk calculation: inherent risk / control effectiveness
	const residualScore = Math.round(
		form.value.inherent_risk_score / form.value.control_effectiveness_score,
	)

	form.value.residual_risk_score = residualScore

	// Determine residual risk rating
	if (residualScore >= 20) form.value.residual_risk_rating = "Critical"
	else if (residualScore >= 12) form.value.residual_risk_rating = "High"
	else if (residualScore >= 6) form.value.residual_risk_rating = "Medium"
	else form.value.residual_risk_rating = "Low"
}

const calculateFactorScore = (factor) => {
	const likelihoodScores = {
		Rare: 1,
		Unlikely: 2,
		Possible: 3,
		Likely: 4,
		"Almost Certain": 5,
	}
	const impactScores = {
		Insignificant: 1,
		Minor: 2,
		Moderate: 3,
		Major: 4,
		Catastrophic: 5,
	}

	const likelihoodScore = likelihoodScores[factor.likelihood] || 1
	const impactScore = impactScores[factor.impact] || 1

	factor.risk_score = likelihoodScore * impactScore
}

const addRiskFactor = () => {
	form.value.risk_factors.push({
		risk_category: "",
		risk_description: "",
		likelihood: "",
		impact: "",
		risk_score: 1,
	})
}

const removeRiskFactor = (index) => {
	form.value.risk_factors.splice(index, 1)
}

const addKeyControl = () => {
	form.value.key_controls.push({
		control_description: "",
		control_type: "",
		control_frequency: "",
		control_effectiveness: "",
	})
}

const removeKeyControl = (index) => {
	form.value.key_controls.splice(index, 1)
}

const getRiskVariant = (rating) => {
	const variants = {
		Critical: "danger",
		High: "danger",
		Medium: "warning",
		Low: "success",
	}
	return variants[rating] || "secondary"
}

const getControlVariant = (rating) => {
	const variants = {
		Strong: "success",
		Adequate: "warning",
		Weak: "danger",
		"Not Assessed": "secondary",
	}
	return variants[rating] || "secondary"
}

const getRiskColorClass = (rating) => {
	const classes = {
		Critical: "text-red-600",
		High: "text-red-600",
		Medium: "text-yellow-600",
		Low: "text-green-600",
	}
	return classes[rating] || "text-gray-600"
}

const formatDate = (date) => {
	return new Date(date).toLocaleDateString()
}

const save = async () => {
	saving.value = true
	try {
		// In a real app, this would be an API call
		await new Promise((resolve) => setTimeout(resolve, 1000))

		if (props.mode === "new") {
			// Create new entity
			console.log("Creating new entity:", form.value)
			// Redirect to the new entity's detail page
			router.push("/audit-planning/universe")
		} else {
			// Update existing entity
			console.log("Updating entity:", form.value)
			// Stay on the same page or redirect
			router.push(`/audit-planning/universe/${props.entityId}`)
		}
	} catch (error) {
		console.error("Error saving entity:", error)
	} finally {
		saving.value = false
	}
}

const cancel = () => {
	if (props.mode === "new") {
		goBack()
	} else {
		switchMode("view")
	}
}

const scheduleAudit = () => {
	// Navigate to audit scheduling or open modal
	console.log("Schedule audit for entity:", props.entityId)
}

const viewAuditHistory = () => {
	// Navigate to audit history page
	console.log("View audit history for entity:", props.entityId)
}

const generateReport = () => {
	// Generate entity report
	console.log("Generate report for entity:", props.entityId)
}

// Lifecycle
onMounted(() => {
	loadEntity()
})

// Watch for route changes
watch(
	() => props.mode,
	(newMode) => {
		if (newMode === "edit" && entity.value) {
			Object.assign(form.value, entity.value)
		}
	},
)
</script>