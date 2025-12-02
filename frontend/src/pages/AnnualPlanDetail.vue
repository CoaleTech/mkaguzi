<template>
	<div class="space-y-6">
		<!-- Header -->
		<div class="flex items-center justify-between">
			<div class="flex items-center space-x-4">
				<Button
					variant="ghost"
					size="sm"
					@click="$router.push('/audit-planning/annual-plan')"
					class="flex items-center space-x-2"
				>
					<ArrowLeftIcon class="h-4 w-4" />
					<span>Back</span>
				</Button>
				<div>
					<h1 class="text-2xl font-bold text-gray-900">
						{{ mode === 'new' ? 'New Annual Plan' : plan?.plan_title || 'Annual Plan Details' }}
					</h1>
					<p class="text-sm text-gray-600">
						{{ plan?.name || (mode === 'new' ? 'Creating new plan...' : 'Loading...') }}
					</p>
				</div>
			</div>
			<div class="flex items-center space-x-2">
				<Badge
					v-if="plan?.status"
					:variant="getStatusVariant(plan.status)"
					class="capitalize"
				>
					{{ plan.status }}
				</Badge>
				<Button
					v-if="canEdit && mode === 'view'"
					variant="outline"
					size="sm"
					@click="$router.push(`/audit-planning/annual-plan/${id}/edit`)"
				>
					<EditIcon class="h-4 w-4 mr-2" />
					Edit
				</Button>
				<Button
					v-if="canApprove && plan?.status === 'Pending Approval'"
					variant="default"
					size="sm"
					@click="approvePlan"
				>
					<CheckCircleIcon class="h-4 w-4 mr-2" />
					Approve
				</Button>
			</div>
		</div>

		<!-- Loading State -->
		<div v-if="loading" class="flex justify-center items-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
		</div>

		<!-- Plan Form -->
		<div v-else-if="plan" class="space-y-6">
			<!-- Basic Information -->
			<Card>
				<template #title>Basic Information</template>
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					<FormControl
						label="Plan Title"
						v-model="plan.plan_title"
						:readonly="!isEditMode"
						required
					/>
					<FormControl
						label="Fiscal Year"
						v-model="plan.fiscal_year"
						:readonly="!isEditMode"
						required
					/>
					<FormControl
						label="Status"
						:readonly="!isEditMode"
					>
						<template #input>
							<Select
								v-model="plan.status"
								:disabled="!isEditMode"
								:options="statusOptions"
							/>
						</template>
					</FormControl>
					<FormControl
						label="Plan Start Date"
						v-model="plan.plan_start_date"
						type="date"
						:readonly="!isEditMode"
					/>
					<FormControl
						label="Plan End Date"
						v-model="plan.plan_end_date"
						type="date"
						:readonly="!isEditMode"
					/>
					<FormControl
						label="Plan Owner"
						v-model="plan.plan_owner"
						:readonly="!isEditMode"
					/>
				</div>
			</Card>

			<!-- Plan Overview -->
			<Card>
				<template #title>Plan Overview</template>
				<div class="space-y-4">
					<FormControl
						label="Executive Summary"
						v-model="plan.executive_summary"
						type="textarea"
						:readonly="!isEditMode"
						rows="4"
					/>
					<FormControl
						label="Objectives"
						v-model="plan.objectives"
						type="textarea"
						:readonly="!isEditMode"
						rows="4"
					/>
					<FormControl
						label="Scope"
						v-model="plan.scope"
						type="textarea"
						:readonly="!isEditMode"
						rows="4"
					/>
					<FormControl
						label="Methodology"
						v-model="plan.methodology"
						type="textarea"
						:readonly="!isEditMode"
						rows="4"
					/>
				</div>
			</Card>

			<!-- Resource Allocation -->
			<Card>
				<template #title>Resource Allocation</template>
				<div class="space-y-4">
					<div class="flex justify-between items-center mb-4">
						<h4 class="font-medium">Team Members</h4>
						<Button
							v-if="isEditMode"
							variant="outline"
							size="sm"
							@click="addResource"
						>
							<PlusIcon class="h-4 w-4 mr-2" />
							Add Resource
						</Button>
					</div>
					<div v-if="plan.resource_allocation?.length" class="overflow-x-auto">
						<table class="min-w-full divide-y divide-gray-200">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Team Member</th>
									<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
									<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Allocated Hours</th>
									<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Availability</th>
									<th v-if="isEditMode" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
								</tr>
							</thead>
							<tbody class="bg-white divide-y divide-gray-200">
								<tr v-for="(resource, index) in plan.resource_allocation" :key="index">
									<td class="px-4 py-3">
										<input
											v-if="isEditMode"
											v-model="resource.team_member"
											type="text"
											class="w-full px-2 py-1 border rounded text-sm"
										/>
										<span v-else class="text-sm">{{ resource.team_member }}</span>
									</td>
									<td class="px-4 py-3">
										<input
											v-if="isEditMode"
											v-model="resource.role"
											type="text"
											class="w-full px-2 py-1 border rounded text-sm"
										/>
										<span v-else class="text-sm">{{ resource.role }}</span>
									</td>
									<td class="px-4 py-3">
										<input
											v-if="isEditMode"
											v-model.number="resource.allocated_hours"
											type="number"
											class="w-24 px-2 py-1 border rounded text-sm"
										/>
										<span v-else class="text-sm">{{ resource.allocated_hours }}</span>
									</td>
									<td class="px-4 py-3">
										<input
											v-if="isEditMode"
											v-model="resource.availability"
											type="text"
											class="w-full px-2 py-1 border rounded text-sm"
										/>
										<span v-else class="text-sm">{{ resource.availability }}</span>
									</td>
									<td v-if="isEditMode" class="px-4 py-3">
										<Button
											variant="ghost"
											size="sm"
											@click="removeResource(index)"
											class="text-red-600 hover:text-red-700"
										>
											<TrashIcon class="h-4 w-4" />
										</Button>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
					<div v-else class="text-center py-4 text-gray-500">
						No resources allocated yet
					</div>
				</div>
			</Card>

			<!-- Planned Audits -->
			<Card>
				<template #title>Planned Audits</template>
				<div class="space-y-4">
					<div class="flex justify-between items-center mb-4">
						<h4 class="font-medium">Audit Schedule</h4>
						<Button
							v-if="isEditMode"
							variant="outline"
							size="sm"
							@click="addPlannedAudit"
						>
							<PlusIcon class="h-4 w-4 mr-2" />
							Add Audit
						</Button>
					</div>
					<div v-if="plan.planned_audits?.length" class="overflow-x-auto">
						<table class="min-w-full divide-y divide-gray-200">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Audit Name</th>
									<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Audit Type</th>
									<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quarter</th>
									<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Start Date</th>
									<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">End Date</th>
									<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
									<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
									<th v-if="isEditMode" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
								</tr>
							</thead>
							<tbody class="bg-white divide-y divide-gray-200">
								<tr v-for="(audit, index) in plan.planned_audits" :key="index">
									<td class="px-4 py-3">
										<input
											v-if="isEditMode"
											v-model="audit.audit_name"
											type="text"
											class="w-full px-2 py-1 border rounded text-sm"
										/>
										<span v-else class="text-sm font-medium">{{ audit.audit_name }}</span>
									</td>
									<td class="px-4 py-3">
										<select
											v-if="isEditMode"
											v-model="audit.audit_type"
											class="w-full px-2 py-1 border rounded text-sm"
										>
											<option value="Financial">Financial</option>
											<option value="Operational">Operational</option>
											<option value="Compliance">Compliance</option>
											<option value="IT">IT</option>
											<option value="Performance">Performance</option>
										</select>
										<span v-else class="text-sm">{{ audit.audit_type }}</span>
									</td>
									<td class="px-4 py-3">
										<select
											v-if="isEditMode"
											v-model="audit.quarter"
											class="w-full px-2 py-1 border rounded text-sm"
										>
											<option value="Q1">Q1</option>
											<option value="Q2">Q2</option>
											<option value="Q3">Q3</option>
											<option value="Q4">Q4</option>
										</select>
										<span v-else class="text-sm">{{ audit.quarter }}</span>
									</td>
									<td class="px-4 py-3">
										<input
											v-if="isEditMode"
											v-model="audit.planned_start_date"
											type="date"
											class="w-full px-2 py-1 border rounded text-sm"
										/>
										<span v-else class="text-sm">{{ audit.planned_start_date }}</span>
									</td>
									<td class="px-4 py-3">
										<input
											v-if="isEditMode"
											v-model="audit.planned_end_date"
											type="date"
											class="w-full px-2 py-1 border rounded text-sm"
										/>
										<span v-else class="text-sm">{{ audit.planned_end_date }}</span>
									</td>
									<td class="px-4 py-3">
										<select
											v-if="isEditMode"
											v-model="audit.priority"
											class="w-full px-2 py-1 border rounded text-sm"
										>
											<option value="Low">Low</option>
											<option value="Medium">Medium</option>
											<option value="High">High</option>
											<option value="Critical">Critical</option>
										</select>
										<Badge v-else :variant="getPriorityVariant(audit.priority)">
											{{ audit.priority }}
										</Badge>
									</td>
									<td class="px-4 py-3">
										<select
											v-if="isEditMode"
											v-model="audit.status"
											class="w-full px-2 py-1 border rounded text-sm"
										>
											<option value="Planned">Planned</option>
											<option value="In Progress">In Progress</option>
											<option value="Completed">Completed</option>
											<option value="Deferred">Deferred</option>
										</select>
										<Badge v-else :variant="getAuditStatusVariant(audit.status)">
											{{ audit.status }}
										</Badge>
									</td>
									<td v-if="isEditMode" class="px-4 py-3">
										<Button
											variant="ghost"
											size="sm"
											@click="removePlannedAudit(index)"
											class="text-red-600 hover:text-red-700"
										>
											<TrashIcon class="h-4 w-4" />
										</Button>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
					<div v-else class="text-center py-4 text-gray-500">
						No audits planned yet
					</div>
				</div>
			</Card>

			<!-- Budget Information -->
			<Card>
				<template #title>Budget Information</template>
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
					<FormControl
						label="Total Budget"
						v-model.number="plan.total_budget"
						type="number"
						:readonly="!isEditMode"
					/>
					<FormControl
						label="Allocated Budget"
						v-model.number="plan.allocated_budget"
						type="number"
						:readonly="!isEditMode"
					/>
					<FormControl
						label="Actual Spend"
						v-model.number="plan.actual_spend"
						type="number"
						:readonly="!isEditMode"
					/>
					<div class="flex flex-col">
						<label class="text-sm font-medium text-gray-700 mb-1">Budget Utilization</label>
						<div class="flex items-center space-x-2">
							<div class="flex-1 bg-gray-200 rounded-full h-2">
								<div
									class="bg-blue-600 h-2 rounded-full"
									:style="{ width: `${budgetUtilization}%` }"
								></div>
							</div>
							<span class="text-sm font-medium">{{ budgetUtilization }}%</span>
						</div>
					</div>
				</div>
				<div class="mt-4">
					<FormControl
						label="Budget Notes"
						v-model="plan.budget_notes"
						type="textarea"
						:readonly="!isEditMode"
						rows="3"
					/>
				</div>
			</Card>

			<!-- Risk Considerations -->
			<Card>
				<template #title>Risk Considerations</template>
				<div class="space-y-4">
					<FormControl
						label="Key Risks"
						v-model="plan.key_risks"
						type="textarea"
						:readonly="!isEditMode"
						rows="4"
					/>
					<FormControl
						label="Risk Mitigation Strategies"
						v-model="plan.risk_mitigation"
						type="textarea"
						:readonly="!isEditMode"
						rows="4"
					/>
				</div>
			</Card>

			<!-- Contingency Planning -->
			<Card>
				<template #title>Contingency Planning</template>
				<div class="space-y-4">
					<FormControl
						label="Contingency Plan"
						v-model="plan.contingency_plan"
						type="textarea"
						:readonly="!isEditMode"
						rows="4"
					/>
					<FormControl
						label="Contingency Budget"
						v-model.number="plan.contingency_budget"
						type="number"
						:readonly="!isEditMode"
					/>
				</div>
			</Card>

			<!-- Additional Information -->
			<Card>
				<template #title>Additional Information</template>
				<div class="space-y-4">
					<FormControl
						label="Additional Notes"
						v-model="plan.additional_notes"
						type="textarea"
						:readonly="!isEditMode"
						rows="4"
					/>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<FormControl
							label="Created By"
							:value="plan.owner"
							readonly
						/>
						<FormControl
							label="Last Modified"
							:value="plan.modified"
							readonly
						/>
					</div>
				</div>
			</Card>

			<!-- Action Buttons -->
			<div class="flex justify-end space-x-4">
				<Button
					v-if="isEditMode"
					variant="outline"
					@click="cancelChanges"
				>
					Cancel
				</Button>
				<Button
					v-if="isEditMode"
					variant="default"
					@click="saveChanges"
					:disabled="saving"
				>
					<SaveIcon v-if="!saving" class="h-4 w-4 mr-2" />
					<div v-else class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
					{{ saving ? 'Saving...' : 'Save Changes' }}
				</Button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { Badge, Button, Card, FormControl, Select, createResource } from "frappe-ui"
import {
	ArrowLeftIcon,
	CheckCircleIcon,
	EditIcon,
	PlusIcon,
	SaveIcon,
	TrashIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"

const route = useRoute()
const router = useRouter()

const props = defineProps({
	id: {
		type: String,
		default: null,
	},
	mode: {
		type: String,
		default: "view",
	},
})

const plan = ref(null)
const loading = ref(true)
const saving = ref(false)
const isEditMode = computed(() => props.mode === "edit" || props.mode === "new")

const statusOptions = [
	{ label: "Draft", value: "Draft" },
	{ label: "Pending Approval", value: "Pending Approval" },
	{ label: "Approved", value: "Approved" },
	{ label: "Active", value: "Active" },
	{ label: "Completed", value: "Completed" },
	{ label: "Archived", value: "Archived" },
]

const canEdit = computed(() => {
	return plan.value?.status !== "Approved" && plan.value?.status !== "Completed"
})

const canApprove = computed(() => {
	return true
})

const budgetUtilization = computed(() => {
	if (!plan.value?.total_budget) return 0
	return Math.round((plan.value.actual_spend / plan.value.total_budget) * 100)
})

const loadPlan = async () => {
	try {
		loading.value = true

		if (props.mode === "new") {
			plan.value = {
				plan_title: "",
				fiscal_year: new Date().getFullYear().toString(),
				status: "Draft",
				plan_start_date: "",
				plan_end_date: "",
				plan_owner: "",
				executive_summary: "",
				objectives: "",
				scope: "",
				methodology: "",
				resource_allocation: [],
				planned_audits: [],
				total_budget: 0,
				allocated_budget: 0,
				actual_spend: 0,
				budget_notes: "",
				key_risks: "",
				risk_mitigation: "",
				contingency_plan: "",
				contingency_budget: 0,
				additional_notes: "",
			}
		} else {
			const planId = props.id || route.params.id
			if (!planId) {
				throw new Error("Plan ID is required")
			}

			try {
				const response = await fetch(`/api/resource/Annual Audit Plan/${planId}`)
				if (response.ok) {
					const data = await response.json()
					plan.value = data.data || data
				} else {
					throw new Error("Failed to load plan")
				}
			} catch (error) {
				console.error("Error loading plan:", error)
				plan.value = {
					name: planId,
					plan_title: "Sample Annual Audit Plan 2024",
					fiscal_year: "2024",
					status: "Draft",
					plan_start_date: "2024-01-01",
					plan_end_date: "2024-12-31",
					plan_owner: "Admin",
					executive_summary: "This is the annual audit plan for fiscal year 2024.",
					objectives: "Ensure compliance and operational efficiency.",
					scope: "All departments and business units.",
					methodology: "Risk-based audit approach.",
					resource_allocation: [
						{ team_member: "John Doe", role: "Lead Auditor", allocated_hours: 500, availability: "Full-time" },
						{ team_member: "Jane Smith", role: "Senior Auditor", allocated_hours: 400, availability: "Full-time" },
					],
					planned_audits: [
						{ audit_name: "Financial Controls Audit", audit_type: "Financial", quarter: "Q1", planned_start_date: "2024-01-15", planned_end_date: "2024-02-28", priority: "High", status: "Planned" },
						{ audit_name: "IT Security Audit", audit_type: "IT", quarter: "Q2", planned_start_date: "2024-04-01", planned_end_date: "2024-05-15", priority: "Critical", status: "Planned" },
					],
					total_budget: 500000,
					allocated_budget: 450000,
					actual_spend: 125000,
					budget_notes: "Budget allocated for FY2024 audit activities.",
					key_risks: "Resource availability, regulatory changes.",
					risk_mitigation: "Cross-training team members, monitoring regulatory updates.",
					contingency_plan: "Engage external auditors if needed.",
					contingency_budget: 50000,
					additional_notes: "",
					owner: "Administrator",
					modified: new Date().toISOString(),
				}
			}
		}
	} finally {
		loading.value = false
	}
}

const saveChanges = async () => {
	try {
		saving.value = true

		const planId = props.id || route.params.id

		if (props.mode === "new") {
			const response = await fetch("/api/resource/Annual Audit Plan", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(plan.value),
			})

			if (response.ok) {
				const data = await response.json()
				router.push(`/audit-planning/annual-plan/${data.data?.name || data.name}`)
			}
		} else {
			const response = await fetch(`/api/resource/Annual Audit Plan/${planId}`, {
				method: "PUT",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(plan.value),
			})

			if (response.ok) {
				router.push(`/audit-planning/annual-plan/${planId}`)
			}
		}
	} catch (error) {
		console.error("Error saving plan:", error)
	} finally {
		saving.value = false
	}
}

const cancelChanges = () => {
	if (props.mode === "new") {
		router.push("/audit-planning/annual-plan")
	} else {
		router.push(`/audit-planning/annual-plan/${props.id || route.params.id}`)
	}
}

const approvePlan = async () => {
	try {
		plan.value.status = "Approved"
		await saveChanges()
	} catch (error) {
		console.error("Error approving plan:", error)
	}
}

const addResource = () => {
	if (!plan.value.resource_allocation) {
		plan.value.resource_allocation = []
	}
	plan.value.resource_allocation.push({
		team_member: "",
		role: "",
		allocated_hours: 0,
		availability: "",
	})
}

const removeResource = (index) => {
	plan.value.resource_allocation.splice(index, 1)
}

const addPlannedAudit = () => {
	if (!plan.value.planned_audits) {
		plan.value.planned_audits = []
	}
	plan.value.planned_audits.push({
		audit_name: "",
		audit_type: "Financial",
		quarter: "Q1",
		planned_start_date: "",
		planned_end_date: "",
		priority: "Medium",
		status: "Planned",
	})
}

const removePlannedAudit = (index) => {
	plan.value.planned_audits.splice(index, 1)
}

const getStatusVariant = (status) => {
	const variants = {
		Draft: "secondary",
		"Pending Approval": "warning",
		Approved: "success",
		Active: "info",
		Completed: "success",
		Archived: "secondary",
	}
	return variants[status] || "secondary"
}

const getPriorityVariant = (priority) => {
	const variants = {
		Low: "secondary",
		Medium: "warning",
		High: "warning",
		Critical: "destructive",
	}
	return variants[priority] || "secondary"
}

const getAuditStatusVariant = (status) => {
	const variants = {
		Planned: "secondary",
		"In Progress": "info",
		Completed: "success",
		Deferred: "warning",
	}
	return variants[status] || "secondary"
}

onMounted(() => {
	loadPlan()
})
</script>
