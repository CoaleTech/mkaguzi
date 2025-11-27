<template>
	<div class="space-y-6">
		<!-- Header -->
		<div class="flex items-center justify-between">
			<div class="flex items-center space-x-4">
				<Button
					variant="ghost"
					size="sm"
					@click="$router.go(-1)"
					class="flex items-center space-x-2"
				>
					<ArrowLeftIcon class="h-4 w-4" />
					<span>Back</span>
				</Button>
				<div>
					<h1 class="text-2xl font-bold text-gray-900">
						Risk Assessment Details
					</h1>
					<p class="text-sm text-gray-600">
						{{ assessment?.assessment_id || 'Loading...' }}
					</p>
				</div>
			</div>
			<div class="flex items-center space-x-2">
				<Badge
					:variant="getStatusVariant(assessment?.status)"
					class="capitalize"
				>
					{{ assessment?.status || 'Draft' }}
				</Badge>
				<Button
					v-if="canEdit"
					variant="outline"
					size="sm"
					@click="toggleEditMode"
				>
					<EditIcon class="h-4 w-4 mr-2" />
					{{ isEditMode ? 'Cancel' : 'Edit' }}
				</Button>
				<Button
					v-if="canApprove && assessment?.status === 'Review'"
					variant="default"
					size="sm"
					@click="approveAssessment"
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

		<!-- Assessment Form -->
		<div v-else-if="assessment" class="space-y-6">
			<!-- Basic Information -->
			<Card>
				<template #title>Assessment Information</template>
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					<FormControl
						label="Assessment ID"
						:value="assessment.assessment_id"
						readonly
					/>
					<FormControl
						label="Assessment Name"
						v-model="assessment.assessment_name"
						:readonly="!isEditMode"
						required
					/>
					<FormControl
						label="Fiscal Year"
						v-model="assessment.fiscal_year"
						:readonly="!isEditMode"
						required
					/>
					<FormControl
						label="Assessment Date"
						v-model="assessment.assessment_date"
						type="date"
						:readonly="!isEditMode"
						required
					/>
					<FormControl
						label="Assessment Period"
						v-model="assessment.assessment_period"
						:readonly="!isEditMode"
						required
					>
						<template #input>
							<Select
								v-model="assessment.assessment_period"
								:disabled="!isEditMode"
								:options="periodOptions"
							/>
						</template>
					</FormControl>
					<FormControl
						label="Status"
						v-model="assessment.status"
						:readonly="!isEditMode"
						required
					>
						<template #input>
							<Select
								v-model="assessment.status"
								:disabled="!isEditMode"
								:options="statusOptions"
							/>
						</template>
					</FormControl>
				</div>
			</Card>

			<!-- Assessment Team -->
			<Card>
				<template #title>Assessment Team</template>
				<div class="space-y-4">
					<div v-for="(member, index) in assessment.assessment_team" :key="index" class="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 border rounded-lg">
						<FormControl
							label="Team Member"
							v-model="member.team_member"
							:readonly="!isEditMode"
						/>
						<FormControl
							label="Role"
							v-model="member.role"
							:readonly="!isEditMode"
						/>
						<div class="flex items-end space-x-2">
							<Button
								v-if="isEditMode"
								variant="outline"
								size="sm"
								@click="removeTeamMember(index)"
								class="text-red-600 hover:text-red-700"
							>
								<TrashIcon class="h-4 w-4" />
							</Button>
						</div>
					</div>
					<Button
						v-if="isEditMode"
						variant="outline"
						size="sm"
						@click="addTeamMember"
						class="w-full"
					>
						<PlusIcon class="h-4 w-4 mr-2" />
						Add Team Member
					</Button>
				</div>
			</Card>

			<!-- Assessment Scope & Methodology -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<Card>
					<template #title>Assessment Scope</template>
					<FormControl
						v-model="assessment.assessment_scope"
						:readonly="!isEditMode"
						type="textarea"
						rows="6"
					/>
				</Card>
				<Card>
					<template #title>Methodology</template>
					<div class="space-y-4">
						<div v-for="method in methodologyOptions" :key="method.value" class="flex items-center space-x-2">
							<input
								:id="`method-${method.value}`"
								v-model="assessment.methodology"
								:value="method.value"
								type="checkbox"
								:disabled="!isEditMode"
								class="rounded border-gray-300"
							/>
							<label :for="`method-${method.value}`" class="text-sm">
								{{ method.label }}
							</label>
						</div>
					</div>
				</Card>
			</div>

			<!-- Risk Register -->
			<Card>
				<template #title>Risk Register</template>
				<div class="space-y-4">
					<div class="flex justify-between items-center">
						<h3 class="text-lg font-semibold">Identified Risks</h3>
						<Button
							v-if="isEditMode"
							variant="outline"
							size="sm"
							@click="addRiskEntry"
						>
							<PlusIcon class="h-4 w-4 mr-2" />
							Add Risk
						</Button>
					</div>
					<div class="overflow-x-auto">
						<table class="min-w-full divide-y divide-gray-200">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
										Risk ID
									</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
										Description
									</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
										Category
									</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
										Likelihood
									</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
										Impact
									</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
										Inherent Risk
									</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
										Actions
									</th>
								</tr>
							</thead>
							<tbody class="bg-white divide-y divide-gray-200">
								<tr v-for="(risk, index) in assessment.risk_register" :key="index">
									<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
										{{ risk.risk_id }}
									</td>
									<td class="px-6 py-4 text-sm text-gray-900">
										{{ risk.risk_title }}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
										{{ risk.risk_category }}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
										{{ risk.likelihood_score }}/5
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
										{{ risk.impact_score }}/5
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<Badge :variant="getRiskVariant(risk.inherent_risk_score)">
											{{ risk.inherent_risk_score }}/25
										</Badge>
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
										<Button
											v-if="isEditMode"
											variant="ghost"
											size="sm"
											@click="editRiskEntry(index)"
										>
											<EditIcon class="h-4 w-4" />
										</Button>
										<Button
											v-if="isEditMode"
											variant="ghost"
											size="sm"
											@click="removeRiskEntry(index)"
											class="text-red-600 hover:text-red-700"
										>
											<TrashIcon class="h-4 w-4" />
										</Button>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>
			</Card>

			<!-- Risk Heat Map -->
			<Card>
				<template #title>Risk Heat Map</template>
				<div class="flex justify-center">
					<RiskHeatMap
						:risks="assessment.risk_register"
						:heatMapData="assessment.risk_heat_map_data"
					/>
				</div>
			</Card>

			<!-- Action Plan -->
			<Card>
				<template #title>Action Plan</template>
				<div class="space-y-4">
					<div class="flex justify-between items-center">
						<h3 class="text-lg font-semibold">Mitigation Actions</h3>
						<Button
							v-if="isEditMode"
							variant="outline"
							size="sm"
							@click="addAction"
						>
							<PlusIcon class="h-4 w-4 mr-2" />
							Add Action
						</Button>
					</div>
					<div class="space-y-4">
						<div v-for="(action, index) in assessment.action_plan" :key="index" class="p-4 border rounded-lg">
							<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
								<FormControl
									label="Action ID"
									:value="action.action_id"
									readonly
								/>
								<FormControl
									label="Action Description"
									v-model="action.action_description"
									:readonly="!isEditMode"
								/>
								<FormControl
									label="Responsible Party"
									v-model="action.responsible_party"
									:readonly="!isEditMode"
								/>
								<FormControl
									label="Target Completion Date"
									v-model="action.target_completion_date"
									type="date"
									:readonly="!isEditMode"
								/>
								<FormControl
									label="Status"
									v-model="action.status"
									:readonly="!isEditMode"
								>
									<template #input>
										<Select
											v-model="action.status"
											:disabled="!isEditMode"
											:options="actionStatusOptions"
										/>
									</template>
								</FormControl>
								<FormControl
									label="Priority"
									v-model="action.priority"
									:readonly="!isEditMode"
								>
									<template #input>
										<Select
											v-model="action.priority"
											:disabled="!isEditMode"
											:options="priorityOptions"
										/>
									</template>
								</FormControl>
								<FormControl
									label="Estimated Cost"
									v-model="action.estimated_cost"
									type="number"
									:readonly="!isEditMode"
								/>
								<FormControl
									label="Actual Completion Date"
									v-model="action.actual_completion_date"
									type="date"
									:readonly="!isEditMode"
								/>
							</div>
						</div>
					</div>
				</div>
			</Card>

			<!-- Top Risks Summary -->
			<Card>
				<template #title>Top Risks Summary</template>
				<div class="space-y-4">
					<div v-for="risk in assessment.top_risks" :key="risk.risk_id" class="p-4 border rounded-lg">
						<div class="flex items-center justify-between">
							<div>
								<h4 class="font-semibold">{{ risk.risk_description }}</h4>
								<p class="text-sm text-gray-600">Risk Score: {{ risk.inherent_risk_score }}/25</p>
							</div>
							<Badge :variant="getRiskVariant(risk.inherent_risk_score)">
								{{ getRiskLevel(risk.inherent_risk_score) }}
							</Badge>
						</div>
					</div>
				</div>
			</Card>

			<!-- Assessment Summary & Recommendations -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<Card>
					<template #title>Assessment Summary</template>
					<FormControl
						v-model="assessment.assessment_summary"
						:readonly="!isEditMode"
						type="textarea"
						rows="6"
					/>
				</Card>
				<Card>
					<template #title>Recommendations</template>
					<FormControl
						v-model="assessment.recommendations"
						:readonly="!isEditMode"
						type="textarea"
						rows="6"
					/>
				</Card>
			</div>

			<!-- Approval Information -->
			<Card>
				<template #title>Approval Information</template>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<FormControl
						label="Prepared By"
						:value="assessment.prepared_by"
						readonly
					/>
					<FormControl
						label="Reviewed By"
						v-model="assessment.reviewed_by"
						:readonly="!isEditMode"
					/>
					<FormControl
						label="Approved By"
						v-model="assessment.approved_by"
						:readonly="!isEditMode"
					/>
					<FormControl
						label="Approval Date"
						:value="assessment.approval_date"
						readonly
					/>
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

		<!-- Risk Entry Modal -->
		<Dialog v-model="showRiskModal">
			<template #title>{{ editingRiskIndex !== null ? 'Edit Risk Entry' : 'Add Risk Entry' }}</template>
			<div class="space-y-4">
				<FormControl
					label="Risk ID"
					v-model="riskForm.risk_id"
					required
				/>
				<FormControl
					label="Risk Title"
					v-model="riskForm.risk_title"
					required
				/>
				<FormControl
					label="Risk Description"
					v-model="riskForm.risk_description"
					type="textarea"
					required
				/>
				<FormControl
					label="Risk Category"
					v-model="riskForm.risk_category"
					required
				/>
				<FormControl
					label="Risk Subcategory"
					v-model="riskForm.risk_subcategory"
				/>
				<FormControl
					label="Auditable Entity"
					v-model="riskForm.auditable_entity"
				/>
				<FormControl
					label="Threat Source"
					v-model="riskForm.threat_source"
				/>
				<FormControl
					label="Vulnerability"
					v-model="riskForm.vulnerability"
				/>
				<div class="grid grid-cols-2 gap-4">
					<FormControl
						label="Likelihood Score (1-5)"
						v-model.number="riskForm.likelihood_score"
						type="number"
						min="1"
						max="5"
						required
					/>
					<FormControl
						label="Impact Score (1-5)"
						v-model.number="riskForm.impact_score"
						type="number"
						min="1"
						max="5"
						required
					/>
				</div>
				<FormControl
					label="Control Effectiveness"
					v-model="riskForm.control_effectiveness"
				/>
				<FormControl
					label="Existing Controls"
					v-model="riskForm.existing_controls"
					type="textarea"
				/>
				<FormControl
					label="Risk Owner"
					v-model="riskForm.risk_owner"
				/>
				<FormControl
					label="Risk Response"
					v-model="riskForm.risk_response"
				/>
				<FormControl
					label="Target Risk Score"
					v-model.number="riskForm.target_risk_score"
					type="number"
				/>
			</div>
			<template #actions>
				<Button variant="outline" @click="closeRiskModal">
					Cancel
				</Button>
				<Button @click="saveRiskEntry">
					{{ editingRiskIndex !== null ? 'Update' : 'Add' }} Risk
				</Button>
			</template>
		</Dialog>
	</div>
</template>

<script setup>
import RiskHeatMap from "@/components/RiskHeatMap.vue"
import { Badge, Button, Card, Dialog, FormControl, Select } from "frappe-ui"
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

// Route and router
const route = useRoute()
const router = useRouter()

// Props
const props = defineProps({
	assessmentId: {
		type: String,
		default: null,
	},
	mode: {
		type: String,
		default: "view", // 'view', 'edit', 'new'
	},
})

// Reactive data
const assessment = ref(null)
const loading = ref(true)
const saving = ref(false)
const isEditMode = ref(props.mode === "edit" || props.mode === "new")
const showRiskModal = ref(false)
const editingRiskIndex = ref(null)

// Form data
const riskForm = ref({
	risk_id: "",
	risk_title: "",
	risk_description: "",
	risk_category: "",
	risk_subcategory: "",
	auditable_entity: "",
	threat_source: "",
	vulnerability: "",
	likelihood_score: 1,
	impact_score: 1,
	control_effectiveness: "",
	existing_controls: "",
	risk_owner: "",
	risk_response: "",
	target_risk_score: 0,
	likelihood_rationale: "",
	impact_rationale: "",
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
	{ label: "Interview", value: "interview" },
	{ label: "Workshop", value: "workshop" },
	{ label: "Survey", value: "survey" },
	{ label: "Document Review", value: "document_review" },
	{ label: "Data Analysis", value: "data_analysis" },
]

const actionStatusOptions = [
	{ label: "Planned", value: "Planned" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Completed", value: "Completed" },
	{ label: "Overdue", value: "Overdue" },
]

const priorityOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Medium", value: "Medium" },
	{ label: "High", value: "High" },
	{ label: "Critical", value: "Critical" },
]

// Computed properties
const canEdit = computed(() => {
	return assessment.value?.status !== "Approved"
})

const canApprove = computed(() => {
	// Check user permissions for approval
	return true // Placeholder - implement based on user roles
})

// Methods
const loadAssessment = async () => {
	try {
		loading.value = true

		if (props.mode === "new") {
			// Create new assessment
			assessment.value = {
				assessment_id: "",
				assessment_name: "",
				assessment_date: new Date().toISOString().split("T")[0],
				fiscal_year: new Date().getFullYear().toString(),
				assessment_period: "Annual",
				assessment_team: [],
				assessment_scope: "",
				methodology: [],
				status: "Planning",
				risk_register: [],
				action_plan: [],
				risk_heat_map_data: {},
				top_risks: [],
				assessment_summary: "",
				recommendations: "",
				prepared_by: "",
				reviewed_by: "",
				approved_by: "",
				approval_date: "",
			}
		} else {
			// Load existing assessment
			const assessmentId = props.assessmentId || route.params.id
			if (!assessmentId) {
				throw new Error("Assessment ID is required")
			}

			// TODO: Replace with actual Frappe API call
			const response = await fetch(
				`/api/resource/Risk Assessment/${assessmentId}`,
			)
			if (response.ok) {
				assessment.value = await response.json()
			} else {
				throw new Error("Failed to load assessment")
			}
		}
	} catch (error) {
		console.error("Error loading assessment:", error)

		// For now, create mock data for existing assessments
		if (props.mode !== "new") {
			const assessmentId = props.assessmentId || route.params.id
			assessment.value = {
				name: assessmentId,
				assessment_id: `RA-2024-${String(assessmentId).padStart(4, "0")}`,
				assessment_name: "Annual Risk Assessment 2024",
				assessment_date: "2024-01-15",
				fiscal_year: "2024",
				assessment_period: "Annual",
				assessment_team: [
					{ team_member: "John Doe", role: "Lead" },
					{ team_member: "Jane Smith", role: "Member" },
				],
				assessment_scope:
					"Comprehensive risk assessment covering all business units and processes.",
				methodology: ["interview", "workshop", "document_review"],
				status: "In Progress",
				risk_register: [
					{
						risk_id: "R001",
						risk_title: "Financial reporting errors",
						risk_description:
							"Financial reporting errors due to manual processes",
						risk_category: "Operational",
						risk_subcategory: "Financial Reporting",
						auditable_entity: "Finance Department",
						threat_source: "Human error",
						vulnerability: "Manual data entry",
						likelihood_score: 4,
						impact_score: 5,
						inherent_risk_score: 20,
						control_effectiveness: "Adequate",
						existing_controls: "Basic review process",
						risk_owner: "Finance Manager",
						risk_response: "Mitigate",
						target_risk_score: 10,
						likelihood_rationale: "High volume of manual entries",
						impact_rationale: "Material impact on financial statements",
					},
				],
				action_plan: [
					{
						action_id: "A001",
						action_description:
							"Implement automated financial reporting system",
						action_type: "System Enhancement",
						priority: "High",
						responsible_party: "IT Department",
						target_completion_date: "2024-06-30",
						estimated_cost: 50000,
						resource_required: "IT team and software licenses",
						status: "In Progress",
						actual_completion_date: "",
						effectiveness_review_date: "",
						review_notes: "",
					},
				],
				risk_heat_map_data: {},
				top_risks: [],
				assessment_summary: "The assessment identified several key risks...",
				recommendations: "Implement automated systems and enhance training...",
				prepared_by: "John Doe",
				reviewed_by: "",
				approved_by: "",
				approval_date: "",
			}
		}
	} finally {
		loading.value = false
	}
}

const toggleEditMode = () => {
	if (props.mode === "view") {
		// Navigate to edit route
		router.push(
			`/audit-planning/risk-assessment/${props.assessmentId || route.params.id}/edit`,
		)
	} else {
		// Cancel edit mode
		cancelChanges()
	}
}

const saveChanges = async () => {
	try {
		saving.value = true

		// Calculate inherent risk scores
		assessment.value.risk_register.forEach((risk) => {
			risk.inherent_risk_score = risk.likelihood_score * risk.impact_score
		})

		// Generate assessment ID if creating new
		if (props.mode === "new" && !assessment.value.assessment_id) {
			const year = assessment.value.fiscal_year.slice(-2)
			// TODO: Get next number from API
			const nextNumber = Math.floor(Math.random() * 1000) + 1
			assessment.value.assessment_id = `RA-${assessment.value.fiscal_year}-${String(nextNumber).padStart(4, "0")}`
		}

		let response
		if (props.mode === "new") {
			// TODO: Replace with actual Frappe API call for creating
			response = await fetch("/api/resource/Risk Assessment", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(assessment.value),
			})
		} else {
			// TODO: Replace with actual Frappe API call for updating
			const assessmentId = props.assessmentId || route.params.id
			response = await fetch(`/api/resource/Risk Assessment/${assessmentId}`, {
				method: "PUT",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(assessment.value),
			})
		}

		if (response.ok) {
			const savedAssessment = await response.json()

			if (props.mode === "new") {
				// Redirect to detail view after creating
				router.push(`/audit-planning/risk-assessment/${savedAssessment.name}`)
			} else {
				isEditMode.value = false
				// Reload to get updated data
				await loadAssessment()
			}
		} else {
			throw new Error("Failed to save changes")
		}
	} catch (error) {
		console.error("Error saving changes:", error)
	} finally {
		saving.value = false
	}
}

const cancelChanges = () => {
	if (props.mode === "new") {
		// Go back to list for new assessments
		router.push("/audit-planning/risk-assessment")
	} else if (props.mode === "edit") {
		// Go back to view mode for existing assessments
		router.push(
			`/audit-planning/risk-assessment/${props.assessmentId || route.params.id}`,
		)
	} else {
		// Just exit edit mode
		isEditMode.value = false
		loadAssessment()
	}
}

const approveAssessment = async () => {
	try {
		assessment.value.status = "Approved"
		assessment.value.approved_by = "Current User" // TODO: Get from session
		assessment.value.approval_date = new Date().toISOString().split("T")[0]
		await saveChanges()
	} catch (error) {
		console.error("Error approving assessment:", error)
	}
}

const addTeamMember = () => {
	assessment.value.assessment_team.push({
		team_member: "",
		role: "",
	})
}

const removeTeamMember = (index) => {
	assessment.value.assessment_team.splice(index, 1)
}

const addRiskEntry = () => {
	editingRiskIndex.value = null
	riskForm.value = {
		risk_id: `R${String(assessment.value.risk_register.length + 1).padStart(3, "0")}`,
		risk_title: "",
		risk_description: "",
		risk_category: "",
		risk_subcategory: "",
		auditable_entity: "",
		threat_source: "",
		vulnerability: "",
		likelihood_score: 1,
		impact_score: 1,
		control_effectiveness: "",
		existing_controls: "",
		risk_owner: "",
		risk_response: "",
		target_risk_score: 0,
		likelihood_rationale: "",
		impact_rationale: "",
	}
	showRiskModal.value = true
}

const editRiskEntry = (index) => {
	editingRiskIndex.value = index
	riskForm.value = { ...assessment.value.risk_register[index] }
	showRiskModal.value = true
}

const removeRiskEntry = (index) => {
	assessment.value.risk_register.splice(index, 1)
}

const saveRiskEntry = () => {
	const riskData = {
		...riskForm.value,
		inherent_risk_score:
			riskForm.value.likelihood_score * riskForm.value.impact_score,
	}

	if (editingRiskIndex.value !== null) {
		assessment.value.risk_register[editingRiskIndex.value] = riskData
	} else {
		assessment.value.risk_register.push(riskData)
	}

	closeRiskModal()
}

const closeRiskModal = () => {
	showRiskModal.value = false
	editingRiskIndex.value = null
	riskForm.value = {
		risk_id: "",
		risk_title: "",
		risk_description: "",
		risk_category: "",
		risk_subcategory: "",
		auditable_entity: "",
		threat_source: "",
		vulnerability: "",
		likelihood_score: 1,
		impact_score: 1,
		control_effectiveness: "",
		existing_controls: "",
		risk_owner: "",
		risk_response: "",
		target_risk_score: 0,
		likelihood_rationale: "",
		impact_rationale: "",
	}
}

const addAction = () => {
	assessment.value.action_plan.push({
		action_id: `A${String(assessment.value.action_plan.length + 1).padStart(3, "0")}`,
		action_description: "",
		action_type: "",
		priority: "Medium",
		responsible_party: "",
		target_completion_date: "",
		estimated_cost: 0,
		resource_required: "",
		status: "Not Started",
		actual_completion_date: "",
		effectiveness_review_date: "",
		review_notes: "",
	})
}

const removeAction = (index) => {
	assessment.value.action_plan.splice(index, 1)
}

const getStatusVariant = (status) => {
	const variants = {
		Planning: "secondary",
		"In Progress": "warning",
		Review: "info",
		Finalized: "success",
		Approved: "success",
	}
	return variants[status] || "secondary"
}

const getRiskVariant = (score) => {
	if (score >= 20) return "destructive"
	if (score >= 15) return "warning"
	if (score >= 10) return "secondary"
	return "success"
}

const getRiskLevel = (score) => {
	if (score >= 20) return "Critical"
	if (score >= 15) return "High"
	if (score >= 10) return "Medium"
	return "Low"
}

// Watch for risk register changes to update heat map
watch(
	() => assessment.value?.risk_register,
	(newRisks) => {
		if (newRisks) {
			updateHeatMapData()
		}
	},
	{ deep: true },
)

const updateHeatMapData = () => {
	if (!assessment.value) return

	const heatMap = {}
	assessment.value.risk_register.forEach((risk) => {
		const key = `${risk.likelihood_score}-${risk.impact_score}`
		heatMap[key] = (heatMap[key] || 0) + 1
	})

	assessment.value.risk_heat_map_data = heatMap

	// Update top risks
	assessment.value.top_risks = [...assessment.value.risk_register]
		.sort((a, b) => b.inherent_risk_score - a.inherent_risk_score)
		.slice(0, 5)
}

// Lifecycle
onMounted(() => {
	loadAssessment()
})
</script>