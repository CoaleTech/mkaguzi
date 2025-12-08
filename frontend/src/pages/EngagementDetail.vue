<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ engagement?.title || 'Engagement Details' }}</h1>
        <p class="text-gray-600 mt-1">
          {{ engagement?.description || 'Loading engagement details...' }}
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline" @click="exportEngagement">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <AskAIButton contextType="engagement" :contextData="getEngagementContext()" />
        <Button @click="editEngagement">
          <EditIcon class="h-4 w-4 mr-2" />
          Edit
        </Button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <!-- Engagement Details -->
    <div v-else-if="engagement" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Overview Card -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Overview</h2>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600">Status</p>
              <Badge :variant="getStatusVariant(engagement.status)" class="mt-1">
                {{ engagement.status }}
              </Badge>
            </div>
            <div>
              <p class="text-sm text-gray-600">Type</p>
              <p class="font-medium">{{ engagement.type }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Start Date</p>
              <p class="font-medium">{{ formatDate(engagement.startDate) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">End Date</p>
              <p class="font-medium">{{ formatDate(engagement.endDate) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Lead Auditor</p>
              <p class="font-medium">{{ engagement.leadAuditor }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Budget</p>
              <p class="font-medium">${{ engagement.budget?.toLocaleString() }}</p>
            </div>
          </div>
        </div>

        <!-- Objectives -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Objectives</h2>
          <ul class="space-y-2">
            <li v-for="objective in engagement.objectives" :key="objective.id" class="flex items-start">
              <CheckCircleIcon class="h-5 w-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
              <span class="text-gray-700">{{ objective.description }}</span>
            </li>
          </ul>
        </div>

        <!-- Scope -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Scope</h2>
          <div class="prose prose-sm max-w-none">
            <p>{{ engagement.scope }}</p>
          </div>
        </div>

        <!-- Findings Summary -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Findings Summary</h2>
          <div class="grid grid-cols-3 gap-4">
            <div class="text-center">
              <p class="text-2xl font-bold text-red-600">{{ engagement.findings?.high || 0 }}</p>
              <p class="text-sm text-gray-600">High Risk</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-yellow-600">{{ engagement.findings?.medium || 0 }}</p>
              <p class="text-sm text-gray-600">Medium Risk</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-green-600">{{ engagement.findings?.low || 0 }}</p>
              <p class="text-sm text-gray-600">Low Risk</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Team Members -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Team Members</h3>
          <div class="space-y-3">
            <div v-for="member in engagement.team" :key="member.id" class="flex items-center">
              <Avatar :label="member.name" class="mr-3" />
              <div>
                <p class="font-medium text-sm">{{ member.name }}</p>
                <p class="text-xs text-gray-600">{{ member.role }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Progress -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Progress</h3>
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span>Planning</span>
              <span>{{ engagement.progress?.planning || 0 }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full"
                :style="{ width: `${engagement.progress?.planning || 0}%` }"
              ></div>
            </div>
          </div>
          <div class="space-y-2 mt-4">
            <div class="flex justify-between text-sm">
              <span>Execution</span>
              <span>{{ engagement.progress?.execution || 0 }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-green-600 h-2 rounded-full"
                :style="{ width: `${engagement.progress?.execution || 0}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div class="space-y-2">
            <Button variant="outline" block @click="addFinding">
              <PlusIcon class="h-4 w-4 mr-2" />
              Add Finding
            </Button>
            <Button variant="outline" block @click="scheduleMeeting">
              <CalendarIcon class="h-4 w-4 mr-2" />
              Schedule Meeting
            </Button>
            <Button variant="outline" block @click="uploadDocument">
              <UploadIcon class="h-4 w-4 mr-2" />
              Upload Document
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="text-center py-12">
      <p class="text-gray-600">Failed to load engagement details.</p>
      <Button @click="loadEngagement" class="mt-4">Retry</Button>
    </div>
  </div>
</template>

<script setup>
import { Avatar, Badge, Button, Spinner } from "frappe-ui"
import {
	CalendarIcon,
	CheckCircleIcon,
	DownloadIcon,
	EditIcon,
	PlusIcon,
	UploadIcon,
} from "lucide-vue-next"
import AskAIButton from "@/components/AskAIButton.vue"
import { onMounted, ref } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()

// Reactive state
const loading = ref(true)
const engagement = ref(null)

// Methods
const loadEngagement = async () => {
	loading.value = true
	try {
		// Mock data - replace with actual API call
		engagement.value = {
			id: route.params.id,
			title: "Annual Financial Audit 2024",
			description:
				"Comprehensive audit of financial statements and internal controls",
			status: "In Progress",
			type: "Financial Audit",
			startDate: "2024-01-01",
			endDate: "2024-12-31",
			leadAuditor: "John Doe",
			budget: 150000,
			objectives: [
				{ id: 1, description: "Assess effectiveness of internal controls" },
				{ id: 2, description: "Verify accuracy of financial statements" },
				{ id: 3, description: "Identify areas for process improvement" },
			],
			scope:
				"The audit will cover all financial processes, including accounts payable, accounts receivable, payroll, and fixed assets. The scope includes all company locations and subsidiaries.",
			findings: { high: 2, medium: 5, low: 8 },
			team: [
				{ id: 1, name: "John Doe", role: "Lead Auditor" },
				{ id: 2, name: "Jane Smith", role: "Senior Auditor" },
				{ id: 3, name: "Bob Johnson", role: "Staff Auditor" },
			],
			progress: { planning: 100, execution: 65 },
		}
	} catch (error) {
		console.error("Failed to load engagement:", error)
	} finally {
		loading.value = false
	}
}

const getStatusVariant = (status) => {
	const variants = {
		"Not Started": "secondary",
		"In Progress": "warning",
		Completed: "success",
		"On Hold": "danger",
	}
	return variants[status] || "secondary"
}

const formatDate = (date) => {
	return new Date(date).toLocaleDateString()
}

const exportEngagement = () => {
	// Export logic
}

const editEngagement = () => {
	// Navigate to edit
}

const addFinding = () => {
	// Navigate to add finding
}

const scheduleMeeting = () => {
	// Schedule meeting logic
}

const uploadDocument = () => {
	// Upload document logic
}

onMounted(() => {
	loadEngagement()
})

function getEngagementContext() {
	if (!engagement.value) return null

	const objectives = engagement.value.objectives || []
	const findings = engagement.value.findings || { high: 0, medium: 0, low: 0 }
	const totalFindings = findings.high + findings.medium + findings.low
	const duration = engagement.value.startDate && engagement.value.endDate ?
		Math.ceil((new Date(engagement.value.endDate) - new Date(engagement.value.startDate)) / (1000 * 60 * 60 * 24)) : 0

	return {
		page_type: 'engagement',
		page_title: `Engagement: ${engagement.value.title}`,
		title: engagement.value.title,
		description: engagement.value.description,
		status: engagement.value.status,
		type: engagement.value.type,
		start_date: engagement.value.startDate,
		end_date: engagement.value.endDate,
		duration_days: duration,
		lead_auditor: engagement.value.leadAuditor,
		budget: engagement.value.budget,
		objectives_count: objectives.length,
		objectives: objectives.map(obj => obj.description),
		scope: engagement.value.scope,
		findings_summary: {
			total: totalFindings,
			high: findings.high,
			medium: findings.medium,
			low: findings.low,
			high_percentage: totalFindings > 0 ? (findings.high / totalFindings * 100).toFixed(1) : 0
		},
		risk_assessment: {
			complexity: engagement.value.type === 'Financial Audit' ? 'high' : engagement.value.type === 'Operational Audit' ? 'medium' : 'low',
			critical_findings: findings.high > 0,
			timeline_pressure: duration < 90 ? 'high' : duration < 180 ? 'medium' : 'low',
			budget_utilization: engagement.value.budget > 100000 ? 'high' : engagement.value.budget > 50000 ? 'medium' : 'low'
		},
		progress_indicators: {
			has_scope_defined: !!engagement.value.scope,
			has_objectives: objectives.length > 0,
			has_findings: totalFindings > 0,
			is_on_track: engagement.value.status === 'In Progress' || engagement.value.status === 'Completed'
		},
		summary: {
			description: `${engagement.value.type} engagement: ${engagement.value.description}`,
			key_metrics: [
				`${objectives.length} audit objectives defined`,
				`${totalFindings} findings identified (${findings.high} high risk)`,
				`Budget: $${engagement.value.budget?.toLocaleString() || 'Not set'}`,
				`Duration: ${duration} days`
			]
		}
	}
}
</script>