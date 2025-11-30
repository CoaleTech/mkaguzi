<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <Button variant="ghost" @click="goBack">
          <ArrowLeft class="w-5 h-5" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">
            Compliance Scorecard
          </h1>
          <p class="text-gray-500 mt-1">
            {{ scorecard.name }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="editScorecard">
          <Edit class="w-4 h-4 mr-2" />
          Edit Scorecard
        </Button>
        <Button variant="solid" @click="generateReport">
          <FileText class="w-4 h-4 mr-2" />
          Generate Report
        </Button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Scorecard Overview -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Scorecard Overview</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Audit Plan</label>
              <p class="mt-1 text-sm text-gray-900">{{ scorecard.audit_plan_name || scorecard.audit_plan || '-' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Period</label>
              <p class="mt-1 text-sm text-gray-900">{{ scorecard.period || '-' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Status</label>
              <Badge :variant="getStatusVariant(scorecard.status)">
                {{ scorecard.status || 'Draft' }}
              </Badge>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Overall Score</label>
              <div class="flex items-center gap-2">
                <div class="text-2xl font-bold text-blue-600">{{ scorecard.overall_score || 0 }}%</div>
                <Badge :variant="getScoreVariant(scorecard.overall_score)">
                  {{ getScoreLabel(scorecard.overall_score) }}
                </Badge>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Created By</label>
              <p class="mt-1 text-sm text-gray-900">{{ scorecard.created_by || '-' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Created Date</label>
              <p class="mt-1 text-sm text-gray-900">{{ formatDate(scorecard.creation) }}</p>
            </div>
          </div>
        </div>

        <!-- Compliance Categories -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Compliance Categories</h3>

          <div v-if="scorecard.compliance_categories && scorecard.compliance_categories.length > 0" class="space-y-4">
            <div v-for="category in scorecard.compliance_categories" :key="category.name" class="border rounded-lg p-4">
              <div class="flex items-center justify-between mb-3">
                <h4 class="font-medium text-gray-900">{{ category.category_name }}</h4>
                <div class="flex items-center gap-2">
                  <span class="text-lg font-semibold text-blue-600">{{ category.score }}%</span>
                  <Badge :variant="getScoreVariant(category.score)">
                    {{ getScoreLabel(category.score) }}
                  </Badge>
                </div>
              </div>

              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">Total Checks:</span>
                  <span class="font-medium ml-2">{{ category.total_checks }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Passed:</span>
                  <span class="font-medium ml-2 text-green-600">{{ category.passed_checks }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Failed:</span>
                  <span class="font-medium ml-2 text-red-600">{{ category.failed_checks }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Weight:</span>
                  <span class="font-medium ml-2">{{ category.weight }}%</span>
                </div>
              </div>

              <div v-if="category.findings" class="mt-3">
                <p class="text-sm text-gray-700">{{ category.findings }}</p>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 text-gray-500">
            No compliance categories defined.
          </div>
        </div>

        <!-- Key Findings -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Key Findings</h3>
          <div class="prose max-w-none">
            <p class="text-gray-700 whitespace-pre-wrap">{{ scorecard.key_findings || 'No key findings recorded.' }}</p>
          </div>
        </div>

        <!-- Recommendations -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
          <div class="prose max-w-none">
            <p class="text-gray-700 whitespace-pre-wrap">{{ scorecard.recommendations || 'No recommendations provided.' }}</p>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Score Summary -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Score Summary</h3>
          <div class="space-y-4">
            <!-- Overall Score -->
            <div class="text-center">
              <div class="relative w-24 h-24 mx-auto mb-2">
                <svg class="w-24 h-24 transform -rotate-90" viewBox="0 0 24 24">
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="2"
                    fill="none"
                    class="text-gray-200"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="2"
                    fill="none"
                    :stroke-dasharray="`${(scorecard.overall_score || 0) * 0.628} 62.8`"
                    class="text-blue-600"
                  />
                </svg>
                <div class="absolute inset-0 flex items-center justify-center">
                  <span class="text-xl font-bold text-gray-900">{{ scorecard.overall_score || 0 }}%</span>
                </div>
              </div>
              <p class="text-sm text-gray-600">Overall Compliance</p>
            </div>

            <!-- Category Breakdown -->
            <div class="space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Categories Assessed:</span>
                <span class="font-medium">{{ scorecard.compliance_categories?.length || 0 }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Total Checks:</span>
                <span class="font-medium">{{ totalChecks }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Passed Checks:</span>
                <span class="font-medium text-green-600">{{ passedChecks }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Failed Checks:</span>
                <span class="font-medium text-red-600">{{ failedChecks }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div class="space-y-2">
            <Button variant="outline" class="w-full justify-start" @click="editScorecard">
              <Edit class="w-4 h-4 mr-2" />
              Edit Scorecard
            </Button>
            <Button variant="outline" class="w-full justify-start" @click="generateReport">
              <FileText class="w-4 h-4 mr-2" />
              Generate Report
            </Button>
            <Button variant="outline" class="w-full justify-start" @click="duplicateScorecard">
              <Copy class="w-4 h-4 mr-2" />
              Duplicate Scorecard
            </Button>
            <Button variant="outline" class="w-full justify-start" @click="exportData">
              <Download class="w-4 h-4 mr-2" />
              Export Data
            </Button>
          </div>
        </div>

        <!-- Related Records -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Related Records</h3>
          <div class="space-y-3">
            <div v-if="scorecard.audit_plan">
              <label class="block text-sm font-medium text-gray-700">Audit Plan</label>
              <Button
                variant="link"
                class="p-0 h-auto text-blue-600 hover:text-blue-800"
                @click="goToAuditPlan(scorecard.audit_plan)"
              >
                {{ scorecard.audit_plan_name || scorecard.audit_plan }}
              </Button>
            </div>
          </div>
        </div>

        <!-- Timeline -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
          <div class="space-y-3">
            <div class="flex items-start gap-3">
              <div class="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">Scorecard Created</p>
                <p class="text-xs text-gray-500">{{ formatDateTime(scorecard.creation) }}</p>
              </div>
            </div>
            <div v-if="scorecard.modified !== scorecard.creation" class="flex items-start gap-3">
              <div class="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">Last Modified</p>
                <p class="text-xs text-gray-500">{{ formatDateTime(scorecard.modified) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button } from "frappe-ui"
import { call } from "frappe-ui"
import { ArrowLeft, Copy, Download, Edit, FileText } from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

const route = useRoute()
const router = useRouter()

const scorecard = ref({})

const totalChecks = computed(() => {
	return (
		scorecard.value.compliance_categories?.reduce(
			(sum, cat) => sum + (cat.total_checks || 0),
			0,
		) || 0
	)
})

const passedChecks = computed(() => {
	return (
		scorecard.value.compliance_categories?.reduce(
			(sum, cat) => sum + (cat.passed_checks || 0),
			0,
		) || 0
	)
})

const failedChecks = computed(() => {
	return (
		scorecard.value.compliance_categories?.reduce(
			(sum, cat) => sum + (cat.failed_checks || 0),
			0,
		) || 0
	)
})

onMounted(async () => {
	await loadScorecard()
})

async function loadScorecard() {
	try {
		const result = await call("frappe.client.get", {
			doctype: "Compliance Scorecard",
			name: route.params.id,
		})
		scorecard.value = result
	} catch (error) {
		console.error("Error loading scorecard:", error)
	}
}

function getStatusVariant(status) {
	const variants = {
		Draft: "outline",
		"In Progress": "secondary",
		Completed: "solid",
		Approved: "solid",
	}
	return variants[status] || "outline"
}

function getScoreVariant(score) {
	if (score >= 90) return "solid"
	if (score >= 70) return "secondary"
	if (score >= 50) return "outline"
	return "destructive"
}

function getScoreLabel(score) {
	if (score >= 90) return "Excellent"
	if (score >= 80) return "Good"
	if (score >= 70) return "Satisfactory"
	if (score >= 60) return "Needs Improvement"
	return "Poor"
}

function formatDate(date) {
	if (!date) return "-"
	return new Date(date).toLocaleDateString()
}

function formatDateTime(dateTime) {
	if (!dateTime) return "-"
	return new Date(dateTime).toLocaleString()
}

function goBack() {
	router.push("/inventory-audit/scorecards")
}

function editScorecard() {
	router.push(`/inventory-audit/scorecards/${route.params.id}/edit`)
}

function generateReport() {
	// TODO: Implement report generation
	alert("Report generation feature coming soon!")
}

function duplicateScorecard() {
	router.push(`/inventory-audit/scorecards/new?duplicate=${route.params.id}`)
}

function exportData() {
	// TODO: Implement data export
	alert("Data export feature coming soon!")
}

function goToAuditPlan(planId) {
	router.push(`/inventory-audit/plans/${planId}`)
}
</script>
