<template>
	<div class="space-y-6">
		<!-- Header -->
		<div class="flex items-center justify-between">
			<div>
				<h1 class="text-2xl font-bold text-gray-900">Risk Assessments</h1>
				<p class="text-gray-600">Conduct and manage comprehensive risk assessments</p>
			</div>
			<Button @click="createNewAssessment" class="bg-blue-600 hover:bg-blue-700 text-white">
				<PlusIcon class="h-4 w-4 mr-2" />
				New Assessment
			</Button>
		</div>

		<!-- Stats Cards -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-6">
			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Total Assessments</p>
						<p class="text-3xl font-bold text-gray-900">{{ riskAssessments.length }}</p>
					</div>
					<div class="p-3 bg-blue-100 rounded-full">
						<FileTextIcon class="h-6 w-6 text-blue-600" />
					</div>
				</div>
			</div>

			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Critical Risks</p>
						<p class="text-3xl font-bold text-red-600">{{ criticalRiskCount }}</p>
					</div>
					<div class="p-3 bg-red-100 rounded-full">
						<AlertTriangleIcon class="h-6 w-6 text-red-600" />
					</div>
				</div>
			</div>

			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">High Risks</p>
						<p class="text-3xl font-bold text-orange-600">{{ highRiskCount }}</p>
					</div>
					<div class="p-3 bg-orange-100 rounded-full">
						<AlertCircleIcon class="h-6 w-6 text-orange-600" />
					</div>
				</div>
			</div>

			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Approved</p>
						<p class="text-3xl font-bold text-green-600">{{ approvedCount }}</p>
					</div>
					<div class="p-3 bg-green-100 rounded-full">
						<CheckCircleIcon class="h-6 w-6 text-green-600" />
					</div>
				</div>
			</div>
		</div>

		<!-- Filters -->
		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center justify-between">
				<h3 class="text-lg font-medium text-gray-900">Risk Assessments</h3>
				<div class="flex items-center space-x-2">
					<Select
						v-model="filterStatus"
						:options="statusOptions"
						placeholder="All Statuses"
						class="w-40"
					/>
					<Select
						v-model="filterPeriod"
						:options="periodOptions"
						placeholder="All Periods"
						class="w-40"
					/>
					<Select
						v-model="filterYear"
						:options="yearOptions"
						placeholder="All Years"
						class="w-40"
					/>
				</div>
			</div>
		</div>

		<!-- Assessments Table -->
		<div class="bg-white rounded-lg border border-gray-200">
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Assessment ID
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Name
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Period
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Date
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Risks
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Status
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Actions
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						<tr
							v-for="assessment in filteredAssessments"
							:key="assessment.name"
							class="hover:bg-gray-50"
						>
							<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
								{{ assessment.assessment_id }}
							</td>
							<td class="px-6 py-4 text-sm text-gray-900">
								{{ assessment.assessment_name }}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
								{{ assessment.assessment_period }} {{ assessment.fiscal_year }}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
								{{ formatDate(assessment.assessment_date) }}
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
								{{ assessment.risk_register?.length || 0 }} risks
								<span v-if="assessment.top_risks?.length > 0" class="text-red-600 ml-1">
									({{ assessment.top_risks.length }} critical)
								</span>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<Badge
									:variant="getStatusVariant(assessment.status)"
									size="sm"
								>
									{{ assessment.status }}
								</Badge>
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
								<div class="flex items-center space-x-2">
									<Button
										variant="ghost"
										size="sm"
										@click="viewAssessment(assessment)"
									>
										<EyeIcon class="h-4 w-4" />
									</Button>
									<Button
										variant="ghost"
										size="sm"
										@click="editAssessment(assessment)"
									>
										<EditIcon class="h-4 w-4" />
									</Button>
									<Button
										variant="ghost"
										size="sm"
										@click="duplicateAssessment(assessment)"
									>
										<CopyIcon class="h-4 w-4" />
									</Button>
								</div>
							</td>
						</tr>
					</tbody>
				</table>
			</div>

			<div v-if="filteredAssessments.length === 0" class="px-6 py-12 text-center">
				<FileTextIcon class="mx-auto h-12 w-12 text-gray-400" />
				<h3 class="mt-2 text-sm font-medium text-gray-900">No risk assessments</h3>
				<p class="mt-1 text-sm text-gray-500">Get started by creating a new risk assessment.</p>
				<div class="mt-6">
					<Button @click="showCreateModal = true">
						<PlusIcon class="h-4 w-4 mr-2" />
						New Assessment
					</Button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { useAuditStore } from "@/stores/audit"
import { Badge, Button, FormControl, Select } from "frappe-ui"
import {
	AlertCircleIcon,
	AlertTriangleIcon,
	CheckCircleIcon,
	CopyIcon,
	EditIcon,
	EyeIcon,
	FileTextIcon,
	PlusIcon,
	TrashIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const auditStore = useAuditStore()

// Reactive state
const loading = ref(false)
const saving = ref(false)
const filterStatus = ref("")
const filterPeriod = ref("")
const filterYear = ref("")

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
const riskAssessments = computed(() => auditStore.riskAssessments || [])

const criticalRiskCount = computed(() => {
	return riskAssessments.value.reduce((count, assessment) => {
		return count + (assessment.top_risks?.filter(risk => risk.inherent_risk_score >= 20).length || 0)
	}, 0)
})

const highRiskCount = computed(() => {
	return riskAssessments.value.reduce((count, assessment) => {
		return count + (assessment.top_risks?.filter(risk => risk.inherent_risk_score >= 15 && risk.inherent_risk_score < 20).length || 0)
	}, 0)
})

const approvedCount = computed(() => {
	return riskAssessments.value.filter(assessment => assessment.status === 'Approved').length
})

const yearOptions = computed(() => {
	const currentYear = new Date().getFullYear()
	const years = []
	for (let i = currentYear - 2; i <= currentYear + 2; i++) {
		years.push({ label: i.toString(), value: i.toString() })
	}
	return years
})

const filteredAssessments = computed(() => {
	let assessments = riskAssessments.value

	if (filterStatus.value) {
		assessments = assessments.filter(a => a.status === filterStatus.value)
	}

	if (filterPeriod.value) {
		assessments = assessments.filter(a => a.assessment_period === filterPeriod.value)
	}

	if (filterYear.value) {
		assessments = assessments.filter(a => a.fiscal_year === filterYear.value)
	}

	return assessments
})

// Methods
const refreshData = async () => {
	loading.value = true
	try {
		await auditStore.fetchRiskAssessments()
	} finally {
		loading.value = false
	}
}

const createNewAssessment = () => {
	router.push('/audit-planning/risk-assessment/new')
}

const viewAssessment = (assessment) => {
	router.push(`/audit-planning/risk-assessment/${assessment.name}`)
}

const editAssessment = (assessment) => {
	router.push(`/audit-planning/risk-assessment/${assessment.name}/edit`)
}

const duplicateAssessment = async (assessment) => {
	try {
		const assessmentDetails = await auditStore.fetchRiskAssessmentDetails(assessment.name)
		if (assessmentDetails) {
			// For now, just navigate to new assessment - in future could pre-populate
			router.push('/audit-planning/risk-assessment/new')
		}
	} catch (error) {
		console.error("Error duplicating assessment:", error)
	}
}

const formatDate = (dateString) => {
	if (!dateString) return ""
	return new Date(dateString).toLocaleDateString()
}

const getStatusVariant = (status) => {
	const variants = {
		'Planning': 'secondary',
		'In Progress': 'warning',
		'Review': 'info',
		'Finalized': 'success',
		'Approved': 'success'
	}
	return variants[status] || 'secondary'
}

// Lifecycle
onMounted(async () => {
	await refreshData()
})
</script>