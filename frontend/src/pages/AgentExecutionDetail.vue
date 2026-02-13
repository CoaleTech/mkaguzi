<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <Button variant="ghost" @click="$router.push('/audit-execution/agent-dashboard')">
          <ArrowLeftIcon class="h-4 w-4" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">
            {{ execution?.agent_name || execution?.agent_type || 'Agent Execution' }}
          </h1>
          <p class="text-gray-600 mt-1">
            {{ execution?.task_name || execution?.task_type || 'Loading...' }}
            <Badge v-if="execution" :variant="getStatusVariant(execution.status)" class="ml-2">
              {{ execution.status }}
            </Badge>
          </p>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <Button v-if="execution?.status === 'Running'" variant="outline" @click="cancelExecution">
          <XCircleIcon class="h-4 w-4 mr-2" />
          Cancel
        </Button>
        <Button v-if="execution?.working_paper_reference" variant="outline" @click="viewWorkingPaper">
          <FileTextIcon class="h-4 w-4 mr-2" />
          Working Paper
        </Button>
        <Button v-if="execution?.status === 'Completed' || execution?.status === 'Failed'" @click="rerunAgent">
          <RefreshCwIcon class="h-4 w-4 mr-2" />
          Re-run
        </Button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <template v-else-if="execution">
      <!-- Summary Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Duration</p>
          <p class="text-xl font-bold text-gray-900">{{ formatDuration(execution.duration_seconds) }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Records Processed</p>
          <p class="text-xl font-bold text-gray-900">{{ (execution.records_processed || 0).toLocaleString() }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Findings Generated</p>
          <p class="text-xl font-bold" :class="execution.total_findings > 0 ? 'text-orange-600' : 'text-gray-900'">
            {{ execution.total_findings || 0 }}
          </p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Test Pass Rate</p>
          <p class="text-xl font-bold" :class="testPassRate >= 80 ? 'text-green-600' : testPassRate >= 50 ? 'text-yellow-600' : 'text-red-600'">
            {{ execution.total_tests > 0 ? testPassRate + '%' : '-' }}
          </p>
        </div>
      </div>

      <!-- Progress Bar (if running) -->
      <div v-if="execution.status === 'Running' && execution.progress_percentage > 0" class="bg-white rounded-lg border border-gray-200 p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700">Progress</span>
          <span class="text-sm text-gray-600">{{ execution.progress_percentage }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-blue-600 h-2 rounded-full transition-all" :style="{ width: execution.progress_percentage + '%' }"></div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="bg-white rounded-lg border border-gray-200">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px overflow-x-auto">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'px-6 py-3 text-sm font-medium border-b-2 whitespace-nowrap',
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              {{ tab.label }}
              <span v-if="tab.count !== undefined" class="ml-1 text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-full">
                {{ tab.count }}
              </span>
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- Overview Tab -->
          <div v-if="activeTab === 'overview'" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <h3 class="font-semibold text-gray-900">Agent Information</h3>
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <p class="text-sm text-gray-600">Agent Type</p>
                    <Badge :variant="getAgentVariant(execution.agent_type)">{{ execution.agent_type }}</Badge>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Agent ID</p>
                    <p class="font-medium text-sm">{{ execution.agent_id }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Version</p>
                    <p class="font-medium text-sm">{{ execution.agent_version || '1.0.0' }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Execution Mode</p>
                    <p class="font-medium text-sm">{{ execution.execution_mode || 'Synchronous' }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Priority</p>
                    <Badge :variant="getPriorityVariant(execution.priority)">{{ execution.priority }}</Badge>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Triggered By</p>
                    <p class="font-medium text-sm">{{ execution.triggered_by || '-' }}</p>
                  </div>
                </div>
              </div>
              <div class="space-y-4">
                <h3 class="font-semibold text-gray-900">Timing</h3>
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <p class="text-sm text-gray-600">Start Time</p>
                    <p class="font-medium text-sm">{{ formatDateTime(execution.start_time) }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">End Time</p>
                    <p class="font-medium text-sm">{{ formatDateTime(execution.end_time) }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Duration</p>
                    <p class="font-medium text-sm">{{ formatDuration(execution.duration_seconds) }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Queue Wait</p>
                    <p class="font-medium text-sm">{{ formatDuration(execution.queue_wait_seconds) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Links -->
            <div v-if="execution.engagement_reference || execution.working_paper_reference" class="space-y-3">
              <h3 class="font-semibold text-gray-900">Links</h3>
              <div class="flex flex-wrap gap-3">
                <router-link
                  v-if="execution.engagement_reference"
                  :to="`/engagements/${execution.engagement_reference}`"
                  class="inline-flex items-center px-3 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm hover:bg-blue-100"
                >
                  <BriefcaseIcon class="h-4 w-4 mr-2" />
                  {{ execution.engagement_reference }}
                </router-link>
                <span
                  v-if="execution.working_paper_reference"
                  class="inline-flex items-center px-3 py-2 bg-gray-50 text-gray-700 rounded-lg text-sm"
                >
                  <FileTextIcon class="h-4 w-4 mr-2" />
                  {{ execution.working_paper_reference }}
                </span>
              </div>
            </div>

            <!-- Execution Summary -->
            <div v-if="execution.execution_summary">
              <h3 class="font-semibold text-gray-900 mb-2">Execution Summary</h3>
              <div class="bg-gray-50 rounded-lg p-4 text-sm text-gray-700 whitespace-pre-wrap">{{ execution.execution_summary }}</div>
            </div>
          </div>

          <!-- Test Evidence Tab -->
          <div v-if="activeTab === 'evidence'" class="space-y-4">
            <div v-if="execution.test_evidence && execution.test_evidence.length > 0">
              <div class="flex items-center space-x-4 mb-4">
                <span class="text-sm text-green-600 font-medium">{{ execution.passed_tests }} Passed</span>
                <span class="text-sm text-red-600 font-medium">{{ execution.failed_tests }} Failed</span>
                <span class="text-sm text-gray-600">{{ execution.total_tests }} Total</span>
              </div>
              <table class="w-full">
                <thead>
                  <tr class="border-b border-gray-200 bg-gray-50">
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Test Name</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Status</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Severity</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Records</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Threshold</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Time</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="test in execution.test_evidence" :key="test.name" class="border-b border-gray-100">
                    <td class="px-4 py-2 text-sm text-gray-900">{{ test.test_name }}</td>
                    <td class="px-4 py-2">
                      <Badge :variant="getTestStatusVariant(test.test_status)">{{ test.test_status }}</Badge>
                    </td>
                    <td class="px-4 py-2">
                      <Badge v-if="test.severity" :variant="getSeverityVariant(test.severity)">{{ test.severity }}</Badge>
                      <span v-else class="text-sm text-gray-400">-</span>
                    </td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ (test.records_processed || 0).toLocaleString() }}</td>
                    <td class="px-4 py-2">
                      <span v-if="test.threshold_breached" class="text-red-600 text-sm font-medium">Breached</span>
                      <span v-else class="text-sm text-gray-400">OK</span>
                    </td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ test.execution_time_ms ? test.execution_time_ms + 'ms' : '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <p>No test evidence recorded for this execution.</p>
            </div>
          </div>

          <!-- Findings Tab -->
          <div v-if="activeTab === 'findings'" class="space-y-4">
            <div v-if="linkedFindings.length > 0">
              <div v-for="finding in linkedFindings" :key="finding.name" class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer" @click="$router.push(`/findings/${finding.name}`)">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-gray-900">{{ finding.finding_title }}</p>
                    <p class="text-sm text-gray-600 mt-1">{{ finding.finding_category }}</p>
                  </div>
                  <div class="flex items-center space-x-2">
                    <Badge :variant="getSeverityVariant(finding.severity || finding.risk_rating)">
                      {{ finding.severity || finding.risk_rating }}
                    </Badge>
                    <Badge :variant="getFindingStatusVariant(finding.finding_status)">
                      {{ finding.finding_status }}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <p>No findings generated from this execution.</p>
            </div>
          </div>

          <!-- Execution Data Tab -->
          <div v-if="activeTab === 'data'" class="space-y-6">
            <div v-if="execution.input_data">
              <h3 class="font-semibold text-gray-900 mb-2">Input Data</h3>
              <pre class="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto max-h-96">{{ formatJSON(execution.input_data) }}</pre>
            </div>
            <div v-if="execution.output_data">
              <h3 class="font-semibold text-gray-900 mb-2">Output Data</h3>
              <pre class="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto max-h-96">{{ formatJSON(execution.output_data) }}</pre>
            </div>
            <div v-if="execution.result_json">
              <h3 class="font-semibold text-gray-900 mb-2">Result</h3>
              <pre class="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto max-h-96">{{ formatJSON(execution.result_json) }}</pre>
            </div>
            <div v-if="!execution.input_data && !execution.output_data && !execution.result_json" class="text-center py-8 text-gray-500">
              <p>No execution data available.</p>
            </div>
          </div>

          <!-- Performance Tab -->
          <div v-if="activeTab === 'performance'" class="space-y-6">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-600">Records Processed</p>
                <p class="text-xl font-bold text-gray-900">{{ (execution.records_processed || 0).toLocaleString() }}</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-600">Processing Speed</p>
                <p class="text-xl font-bold text-gray-900">{{ execution.records_per_second ? Math.round(execution.records_per_second) + '/s' : '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-600">Memory Usage</p>
                <p class="text-xl font-bold text-gray-900">{{ execution.memory_usage_mb ? execution.memory_usage_mb + ' MB' : '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-600">CPU Usage</p>
                <p class="text-xl font-bold text-gray-900">{{ execution.cpu_usage_percent ? execution.cpu_usage_percent + '%' : '-' }}</p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-600">Retry Count</p>
                <p class="text-lg font-medium">{{ execution.retry_count || 0 }} / {{ execution.max_retries || 3 }}</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-600">Queue Wait Time</p>
                <p class="text-lg font-medium">{{ formatDuration(execution.queue_wait_seconds) }}</p>
              </div>
            </div>
          </div>

          <!-- Errors Tab -->
          <div v-if="activeTab === 'errors'" class="space-y-4">
            <div v-if="execution.error_occurred">
              <div class="bg-red-50 border border-red-200 rounded-lg p-4 space-y-3">
                <div>
                  <p class="text-sm font-medium text-red-800">Error Type</p>
                  <p class="text-sm text-red-700">{{ execution.error_type || 'Unknown' }}</p>
                </div>
                <div>
                  <p class="text-sm font-medium text-red-800">Error Message</p>
                  <p class="text-sm text-red-700">{{ execution.error_message }}</p>
                </div>
                <div v-if="execution.error_traceback">
                  <p class="text-sm font-medium text-red-800 mb-1">Traceback</p>
                  <pre class="bg-red-900 text-red-200 rounded p-3 text-xs overflow-x-auto max-h-64">{{ execution.error_traceback }}</pre>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <CheckCircleIcon class="h-12 w-12 text-green-300 mx-auto mb-3" />
              <p>No errors occurred during this execution.</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Error State -->
    <div v-else class="text-center py-12">
      <p class="text-gray-600">Failed to load execution details.</p>
      <Button @click="loadExecution" class="mt-4">Retry</Button>
    </div>
  </div>
</template>

<script setup>
import { useAgentStore } from "@/stores/agents"
import { Badge, Button, Spinner } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	ArrowLeftIcon,
	BriefcaseIcon,
	CheckCircleIcon,
	FileTextIcon,
	RefreshCwIcon,
	XCircleIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

const route = useRoute()
const router = useRouter()
const store = useAgentStore()

const activeTab = ref("overview")
const linkedFindings = ref([])

const execution = computed(() => store.currentExecution)

const testPassRate = computed(() => {
	if (!execution.value || !execution.value.total_tests) return 0
	return Math.round((execution.value.passed_tests / execution.value.total_tests) * 100)
})

const tabs = computed(() => [
	{ id: "overview", label: "Overview" },
	{ id: "evidence", label: "Test Evidence", count: execution.value?.test_evidence?.length || 0 },
	{ id: "findings", label: "Findings", count: linkedFindings.value.length },
	{ id: "data", label: "Execution Data" },
	{ id: "performance", label: "Performance" },
	{ id: "errors", label: "Errors", count: execution.value?.error_occurred ? 1 : 0 },
])

const loadExecution = async () => {
	const id = route.params.id
	if (id) {
		await store.fetchExecutionDetail(id)
		if (execution.value?.finding_ids) {
			await loadLinkedFindings()
		}
	}
}

const loadLinkedFindings = async () => {
	if (!execution.value?.finding_ids) return
	const ids = execution.value.finding_ids.split(",").map((s) => s.trim()).filter(Boolean)
	if (ids.length === 0) return
	try {
		const res = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Audit Finding",
				fields: ["name", "finding_title", "finding_category", "severity", "risk_rating", "finding_status"],
				filters: { name: ["in", ids] },
			},
		}).fetch()
		linkedFindings.value = res || []
	} catch (err) {
		console.error("Failed to load linked findings:", err)
	}
}

const cancelExecution = async () => {
	try {
		await store.cancelExecution(route.params.id)
		await loadExecution()
	} catch (err) {
		console.error("Cancel failed:", err)
	}
}

const rerunAgent = async () => {
	if (!execution.value) return
	try {
		await store.executeAgent(execution.value.agent_type, {
			task_type: execution.value.task_type,
		})
		router.push("/audit-execution/agent-dashboard")
	} catch (err) {
		console.error("Re-run failed:", err)
	}
}

const viewWorkingPaper = () => {
	if (execution.value?.working_paper_reference) {
		router.push("/audit-execution/working-papers")
	}
}

const getStatusVariant = (status) => {
	const map = { Pending: "secondary", Running: "info", Completed: "success", Failed: "danger", Cancelled: "warning", Timeout: "danger" }
	return map[status] || "secondary"
}

const getAgentVariant = (type) => {
	const map = { Financial: "success", Risk: "warning", Compliance: "info", Discovery: "subtle", Notification: "warning" }
	return map[type] || "secondary"
}

const getPriorityVariant = (priority) => {
	const map = { Low: "secondary", Medium: "info", High: "warning", Critical: "danger" }
	return map[priority] || "secondary"
}

const getSeverityVariant = (severity) => {
	const map = { Critical: "danger", High: "warning", Medium: "info", Low: "secondary" }
	return map[severity] || "secondary"
}

const getTestStatusVariant = (status) => {
	const map = { Pass: "success", Fail: "danger", Warning: "warning", Error: "danger", Skipped: "secondary" }
	return map[status] || "secondary"
}

const getFindingStatusVariant = (status) => {
	const map = { Open: "danger", "Action in Progress": "warning", "Pending Verification": "info", Closed: "success" }
	return map[status] || "secondary"
}

const formatDateTime = (dt) => {
	if (!dt) return "-"
	return new Date(dt).toLocaleString()
}

const formatDuration = (seconds) => {
	if (!seconds || seconds === 0) return "-"
	if (seconds < 60) return `${Math.round(seconds)}s`
	if (seconds < 3600) return `${Math.round(seconds / 60)}m ${Math.round(seconds % 60)}s`
	return `${Math.floor(seconds / 3600)}h ${Math.round((seconds % 3600) / 60)}m`
}

const formatJSON = (data) => {
	if (!data) return ""
	try {
		return JSON.stringify(JSON.parse(data), null, 2)
	} catch {
		return data
	}
}

onMounted(() => {
	loadExecution()
})
</script>
