<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ finding?.title || 'Finding Details' }}</h1>
        <p class="text-gray-600 mt-1">
          {{ finding?.description || 'Loading finding details...' }}
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline" @click="exportFinding">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button @click="editFinding">
          <EditIcon class="h-4 w-4 mr-2" />
          Edit
        </Button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <!-- Finding Details -->
    <div v-else-if="finding" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Details Card -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Details</h2>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600">Severity</p>
              <Badge :variant="getSeverityVariant(finding.severity)" class="mt-1">
                {{ finding.severity }}
              </Badge>
            </div>
            <div>
              <p class="text-sm text-gray-600">Status</p>
              <Badge :variant="getStatusVariant(finding.status)" class="mt-1">
                {{ finding.status }}
              </Badge>
            </div>
            <div>
              <p class="text-sm text-gray-600">Reported By</p>
              <p class="font-medium">{{ finding.reportedBy }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Reported Date</p>
              <p class="font-medium">{{ formatDate(finding.reportedDate) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Engagement</p>
              <p class="font-medium">{{ finding.engagement }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Category</p>
              <p class="font-medium">{{ finding.category }}</p>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Description</h2>
          <div class="prose prose-sm max-w-none">
            <p>{{ finding.description }}</p>
          </div>
        </div>

        <!-- Root Cause -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Root Cause Analysis</h2>
          <div class="prose prose-sm max-w-none">
            <p>{{ finding.rootCause }}</p>
          </div>
        </div>

        <!-- Impact -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Impact Assessment</h2>
          <div class="space-y-4">
            <div>
              <h3 class="font-medium text-gray-900">Financial Impact</h3>
              <p class="text-gray-700">{{ finding.impact.financial }}</p>
            </div>
            <div>
              <h3 class="font-medium text-gray-900">Operational Impact</h3>
              <p class="text-gray-700">{{ finding.impact.operational }}</p>
            </div>
            <div>
              <h3 class="font-medium text-gray-900">Compliance Impact</h3>
              <p class="text-gray-700">{{ finding.impact.compliance }}</p>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Recommendations</h2>
          <ul class="space-y-2">
            <li v-for="recommendation in finding.recommendations" :key="recommendation.id" class="flex items-start">
              <CheckCircleIcon class="h-5 w-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
              <span class="text-gray-700">{{ recommendation.description }}</span>
            </li>
          </ul>
        </div>

        <!-- Corrective Actions -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Corrective Actions</h2>
          <div class="space-y-4">
            <div v-for="action in finding.correctiveActions" :key="action.id" class="border border-gray-200 rounded-lg p-4">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="font-medium text-gray-900">{{ action.title }}</h3>
                  <p class="text-gray-600 mt-1">{{ action.description }}</p>
                  <div class="flex items-center space-x-4 mt-2">
                    <Badge :variant="getActionStatusVariant(action.status)">
                      {{ action.status }}
                    </Badge>
                    <span class="text-sm text-gray-500">
                      Due: {{ formatDate(action.dueDate) }}
                    </span>
                    <span class="text-sm text-gray-500">
                      Assigned to: {{ action.assignedTo }}
                    </span>
                  </div>
                </div>
                <Button variant="ghost" size="sm" @click="updateActionStatus(action)">
                  Update
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Evidence -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Evidence</h3>
          <div class="space-y-3">
            <div v-for="evidence in finding.evidence" :key="evidence.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div class="flex items-center">
                <FileTextIcon class="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p class="font-medium text-sm">{{ evidence.name }}</p>
                  <p class="text-xs text-gray-600">{{ evidence.type }}</p>
                </div>
              </div>
              <Button variant="ghost" size="sm" @click="viewEvidence(evidence)">
                View
              </Button>
            </div>
          </div>
          <Button variant="outline" block class="mt-4" @click="addEvidence">
            <PlusIcon class="h-4 w-4 mr-2" />
            Add Evidence
          </Button>
        </div>

        <!-- Timeline -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
          <div class="space-y-4">
            <div v-for="event in finding.timeline" :key="event.id" class="flex">
              <div class="flex-shrink-0">
                <div class="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-900">{{ event.title }}</p>
                <p class="text-xs text-gray-600">{{ formatDate(event.date) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div class="space-y-2">
            <Button variant="outline" block @click="addCorrectiveAction">
              <PlusIcon class="h-4 w-4 mr-2" />
              Add Action
            </Button>
            <Button variant="outline" block @click="scheduleFollowUp">
              <CalendarIcon class="h-4 w-4 mr-2" />
              Schedule Follow-up
            </Button>
            <Button variant="outline" block @click="notifyManagement">
              <MailIcon class="h-4 w-4 mr-2" />
              Notify Management
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="text-center py-12">
      <p class="text-gray-600">Failed to load finding details.</p>
      <Button @click="loadFinding" class="mt-4">Retry</Button>
    </div>
  </div>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { Badge, Button, Spinner } from "frappe-ui"
import {
	CalendarIcon,
	CheckCircleIcon,
	DownloadIcon,
	EditIcon,
	FileTextIcon,
	MailIcon,
	PlusIcon,
} from "lucide-vue-next"
import { onMounted, ref } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()

// Reactive state
const loading = ref(true)
const finding = ref(null)

// Methods
const loadFinding = async () => {
	loading.value = true
	try {
		const response = await createResource({
			url: "frappe.client.get",
			params: {
				doctype: "Audit Finding",
				name: route.params.id,
			},
		}).fetch()

		if (response) {
			finding.value = {
				...response,
				// Map field names to match the template expectations
				title: response.finding_title,
				description: response.finding_description,
				severity: response.risk_rating,
				status: response.finding_status,
				reportedBy: response.responsible_person,
				reportedDate: response.creation,
				engagement: response.engagement_reference,
				category: response.finding_category,
				rootCause: response.root_cause_analysis,
				impact: {
					financial: response.financial_impact,
					operational: response.operational_impact,
					compliance: response.compliance_impact,
				},
				recommendations: response.recommendations
					? response.recommendations
							.split("\n")
							.filter((r) => r.trim())
							.map((rec, idx) => ({
								id: idx + 1,
								description: rec.trim(),
							}))
					: [],
				correctiveActions: [], // Will be populated from corrective action plans
				evidence: response.finding_evidence || [],
				timeline: [], // Will be populated from status changes
			}
		}
	} catch (error) {
		console.error("Failed to load finding:", error)
	} finally {
		loading.value = false
	}
}

const getSeverityVariant = (severity) => {
	const variants = {
		High: "danger",
		Medium: "warning",
		Low: "success",
	}
	return variants[severity] || "secondary"
}

const getStatusVariant = (status) => {
	const variants = {
		Open: "danger",
		"In Progress": "warning",
		Resolved: "success",
		Closed: "secondary",
	}
	return variants[status] || "secondary"
}

const getActionStatusVariant = (status) => {
	const variants = {
		Pending: "secondary",
		"In Progress": "warning",
		Completed: "success",
		Overdue: "danger",
	}
	return variants[status] || "secondary"
}

const formatDate = (date) => {
	return new Date(date).toLocaleDateString()
}

const exportFinding = () => {
	// Export logic
}

const editFinding = () => {
	// Navigate to edit
}

const updateActionStatus = (action) => {
	// Update action status
}

const viewEvidence = (evidence) => {
	// View evidence
}

const addEvidence = () => {
	// Add evidence
}

const addCorrectiveAction = () => {
	// Add corrective action
}

const scheduleFollowUp = () => {
	// Schedule follow-up
}

const notifyManagement = () => {
	// Notify management
}

onMounted(() => {
	loadFinding()
})
</script>