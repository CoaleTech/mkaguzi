<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Annual Audit Plan</h1>
        <p class="text-gray-600 mt-1">
          Create and manage comprehensive annual audit planning
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button
          variant="outline"
          @click="refreshData"
          :loading="loading"
        >
          <RefreshCwIcon class="h-4 w-4 mr-2" />
          Refresh
        </Button>
        <Button
          @click="showCreateModal = true"
          class="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          New Plan
        </Button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Active Plans</p>
            <p class="text-3xl font-bold text-gray-900">{{ activePlansCount }}</p>
          </div>
          <div class="p-3 bg-green-100 rounded-full">
            <CheckCircleIcon class="h-6 w-6 text-green-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Planned Audits</p>
            <p class="text-3xl font-bold text-gray-900">{{ plannedAuditsCount }}</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-full">
            <ClipboardListIcon class="h-6 w-6 text-blue-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Resource Utilization</p>
            <p class="text-3xl font-bold text-gray-900">{{ averageUtilization }}%</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-full">
            <UsersIcon class="h-6 w-6 text-yellow-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Upcoming Audits</p>
            <p class="text-3xl font-bold text-gray-900">{{ upcomingAuditsCount }}</p>
          </div>
          <div class="p-3 bg-purple-100 rounded-full">
            <CalendarIcon class="h-6 w-6 text-purple-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Plans List -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Annual Audit Plans</h3>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Plan ID
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Year
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Utilization
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="plan in annualPlans"
              :key="plan.name"
              class="hover:bg-gray-50"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ plan.plan_id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ plan.plan_year }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge
                  :variant="getStatusVariant(plan.status)"
                  size="sm"
                >
                  {{ plan.status }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ plan.utilization_percentage || 0 }}%
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="viewPlan(plan)"
                  >
                    <EyeIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="editPlan(plan)"
                  >
                    <EditIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="duplicatePlan(plan)"
                  >
                    <CopyIcon class="h-4 w-4" />
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="annualPlans.length === 0" class="px-6 py-12 text-center">
        <CalendarIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">No audit plans</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating a new annual audit plan.</p>
        <div class="mt-6">
          <Button @click="showCreateModal = true">
            <PlusIcon class="h-4 w-4 mr-2" />
            New Plan
          </Button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Plan Modal -->
    <Dialog
      v-model="showCreateModal"
      :title="editingPlan ? 'Edit Annual Plan' : 'Create Annual Plan'"
      size="4xl"
    >
      <template #body>
        <div class="space-y-6">
          <!-- Basic Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormControl
              v-model="planForm.plan_id"
              label="Plan ID"
              placeholder="Enter plan ID"
              :required="true"
            />
            <FormControl
              v-model="planForm.plan_year"
              type="number"
              label="Plan Year"
              placeholder="2025"
              :required="true"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Select
              v-model="planForm.plan_period"
              :options="periodOptions"
              label="Plan Period"
              placeholder="Select period"
            />
            <Select
              v-model="planForm.status"
              :options="statusOptions"
              label="Status"
              placeholder="Select status"
            />
          </div>

          <!-- Plan Overview -->
          <div class="space-y-4">
            <h4 class="text-lg font-medium text-gray-900">Plan Overview</h4>
            <FormControl
              v-model="planForm.plan_objectives"
              type="textarea"
              label="Plan Objectives"
              placeholder="Enter the main objectives of this audit plan"
              rows="3"
            />
            <FormControl
              v-model="planForm.scope_and_coverage"
              type="textarea"
              label="Scope and Coverage"
              placeholder="Describe the scope and coverage of audits"
              rows="3"
            />
            <FormControl
              v-model="planForm.key_assumptions"
              type="textarea"
              label="Key Assumptions"
              placeholder="List key assumptions for this plan"
              rows="3"
            />
          </div>

          <!-- Resource Summary -->
          <div class="space-y-4">
            <h4 class="text-lg font-medium text-gray-900">Resource Summary</h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <FormControl
                v-model="planForm.total_available_days"
                type="number"
                label="Total Available Days"
                placeholder="0"
              />
              <FormControl
                v-model="planForm.total_planned_days"
                type="number"
                label="Total Planned Days"
                placeholder="0"
              />
              <FormControl
                v-model="planForm.utilization_percentage"
                type="number"
                label="Utilization %"
                placeholder="0"
                readonly
              />
            </div>
          </div>

          <!-- Planned Audits -->
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <h4 class="text-lg font-medium text-gray-900">Planned Audits</h4>
              <Button
                variant="outline"
                size="sm"
                @click="addPlannedAudit"
              >
                <PlusIcon class="h-4 w-4 mr-2" />
                Add Audit
              </Button>
            </div>

            <div class="space-y-4">
              <div
                v-for="(audit, index) in planForm.planned_audits"
                :key="index"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <Select
                    v-model="audit.audit_universe"
                    :options="auditUniverseOptions"
                    label="Audit Universe"
                    placeholder="Select universe"
                  />
                  <Select
                    v-model="audit.audit_type"
                    :options="auditTypeOptions"
                    label="Audit Type"
                    placeholder="Select type"
                  />
                  <Select
                    v-model="audit.priority"
                    :options="priorityOptions"
                    label="Priority"
                    placeholder="Select priority"
                  />
                  <FormControl
                    v-model="audit.planned_days"
                    type="number"
                    label="Planned Days"
                    placeholder="0"
                  />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <FormControl
                    v-model="audit.planned_start_date"
                    type="date"
                    label="Start Date"
                  />
                  <FormControl
                    v-model="audit.planned_end_date"
                    type="date"
                    label="End Date"
                  />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <FormControl
                    v-model="audit.lead_auditor"
                    label="Lead Auditor"
                    placeholder="Select auditor"
                  />
                  <FormControl
                    v-model="audit.objectives"
                    type="textarea"
                    label="Objectives"
                    placeholder="Audit objectives"
                    rows="2"
                  />
                </div>

                <div class="flex justify-end mt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    @click="removePlannedAudit(index)"
                  >
                    <TrashIcon class="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end space-x-3">
          <Button
            variant="outline"
            @click="showCreateModal = false"
          >
            Cancel
          </Button>
          <Button
            @click="savePlan"
            :loading="saving"
            class="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {{ editingPlan ? 'Update' : 'Create' }} Plan
          </Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { useAuditStore } from "@/stores/audit"
import { useDataStore } from "@/stores/data"
import { Badge, Button, Dialog, FormControl, Select } from "frappe-ui"
import {
	CalendarIcon,
	CheckCircleIcon,
	ClipboardListIcon,
	CopyIcon,
	EditIcon,
	EyeIcon,
	PlusIcon,
	RefreshCwIcon,
	TrashIcon,
	UsersIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const auditStore = useAuditStore()
const dataStore = useDataStore()

// Reactive state
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const editingPlan = ref(null)

// Form data
const planForm = ref({
	plan_id: "",
	plan_year: new Date().getFullYear(),
	plan_period: "Annual",
	status: "Draft",
	plan_objectives: "",
	scope_and_coverage: "",
	key_assumptions: "",
	total_available_days: 0,
	total_planned_days: 0,
	utilization_percentage: 0,
	planned_audits: [],
})

// Options
const periodOptions = [
	{ label: "Annual", value: "Annual" },
	{ label: "Semi-Annual", value: "Semi-Annual" },
	{ label: "Quarterly", value: "Quarterly" },
]

const statusOptions = [
	{ label: "Draft", value: "Draft" },
	{ label: "Submitted for Approval", value: "Submitted for Approval" },
	{ label: "Approved", value: "Approved" },
	{ label: "Rejected", value: "Rejected" },
	{ label: "Active", value: "Active" },
	{ label: "Completed", value: "Completed" },
]

const auditTypeOptions = [
	{ label: "Financial", value: "Financial" },
	{ label: "Operational", value: "Operational" },
	{ label: "Compliance", value: "Compliance" },
	{ label: "IT", value: "IT" },
	{ label: "Integrated", value: "Integrated" },
	{ label: "Special Investigation", value: "Special Investigation" },
	{ label: "Follow-up", value: "Follow-up" },
]

const priorityOptions = [
	{ label: "Critical", value: "Critical" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

// Computed properties
const annualPlans = computed(() => auditStore.annualPlans)
const activePlansCount = computed(() => auditStore.activeAnnualPlans.length)
const plannedAuditsCount = computed(() => auditStore.plannedAudits.length)
const upcomingAuditsCount = computed(() => auditStore.upcomingAudits.length)
const averageUtilization = computed(() => {
	const plans = auditStore.activeAnnualPlans
	if (plans.length === 0) return 0
	const total = plans.reduce(
		(sum, plan) => sum + (plan.utilization_percentage || 0),
		0,
	)
	return Math.round(total / plans.length)
})

const auditUniverseOptions = computed(() => {
	return auditStore.auditUniverse.map((universe) => ({
		label: `${universe.universe_id} - ${universe.auditable_entity}`,
		value: universe.name,
	}))
})

// Methods
const refreshData = async () => {
	loading.value = true
	try {
		await Promise.all([
			auditStore.fetchAnnualPlans(),
			auditStore.fetchAuditUniverse(),
			auditStore.fetchAuditCalendar(),
		])
	} finally {
		loading.value = false
	}
}

const viewPlan = (plan) => {
	// Navigate to plan detail view
	router.push(`/audit-planning/annual-plan/${plan.name}`)
}

const editPlan = (plan) => {
	editingPlan.value = plan
	// Load plan data into form
	planForm.value = { ...plan }
	showCreateModal.value = true
}

const duplicatePlan = async (plan) => {
	try {
		const planDetails = await auditStore.fetchAnnualPlanDetails(plan.name)
		if (planDetails) {
			editingPlan.value = null
			planForm.value = {
				...planDetails,
				plan_id: `${planDetails.plan_id}_copy`,
				status: "Draft",
			}
			showCreateModal.value = true
		}
	} catch (error) {
		console.error("Error duplicating plan:", error)
	}
}

const addPlannedAudit = () => {
	planForm.value.planned_audits.push({
		audit_universe: "",
		audit_type: "",
		priority: "Medium",
		planned_start_date: "",
		planned_end_date: "",
		planned_days: 0,
		lead_auditor: "",
		objectives: "",
		scope: "",
	})
}

const removePlannedAudit = (index) => {
	planForm.value.planned_audits.splice(index, 1)
}

const savePlan = async () => {
	saving.value = true
	try {
		if (editingPlan.value) {
			await auditStore.updateAnnualPlan(editingPlan.value.name, planForm.value)
		} else {
			await auditStore.createAnnualPlan(planForm.value)
		}

		showCreateModal.value = false
		resetForm()
		await refreshData()
	} catch (error) {
		console.error("Error saving plan:", error)
	} finally {
		saving.value = false
	}
}

const resetForm = () => {
	planForm.value = {
		plan_id: "",
		plan_year: new Date().getFullYear(),
		plan_period: "Annual",
		status: "Draft",
		plan_objectives: "",
		scope_and_coverage: "",
		key_assumptions: "",
		total_available_days: 0,
		total_planned_days: 0,
		utilization_percentage: 0,
		planned_audits: [],
	}
	editingPlan.value = null
}

const getStatusVariant = (status) => {
	const variants = {
		Draft: "secondary",
		"Submitted for Approval": "warning",
		Approved: "success",
		Rejected: "danger",
		Active: "primary",
		Completed: "success",
	}
	return variants[status] || "secondary"
}

// Lifecycle
onMounted(async () => {
	await refreshData()
})
</script>