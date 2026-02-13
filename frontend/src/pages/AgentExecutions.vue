<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">AI Agent Dashboard</h1>
        <p class="text-gray-600 mt-1">Monitor and manage AI audit agents</p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline" @click="refreshData">
          <RefreshCwIcon class="h-4 w-4 mr-2" />
          Refresh
        </Button>
        <Button @click="runAllAgents" :disabled="isRunningAll">
          <PlayIcon class="h-4 w-4 mr-2" />
          {{ isRunningAll ? 'Running...' : 'Run All Agents' }}
        </Button>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Total Executions</p>
        <p class="text-2xl font-bold text-gray-900">{{ store.executions.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Running</p>
        <p class="text-2xl font-bold text-blue-600">{{ store.runningExecutions.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Completed</p>
        <p class="text-2xl font-bold text-green-600">{{ store.completedExecutions.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Failed</p>
        <p class="text-2xl font-bold text-red-600">{{ store.failedExecutions.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Avg Duration</p>
        <p class="text-2xl font-bold text-gray-900">{{ formatDuration(store.avgDuration) }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Active Configs</p>
        <p class="text-2xl font-bold text-gray-900">{{ store.activeConfigs.length }}</p>
      </div>
    </div>

    <!-- Agent Type Cards -->
    <div>
      <h2 class="text-lg font-semibold text-gray-900 mb-3">Agent Types</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="agentType in agentTypes"
          :key="agentType.value"
          class="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-center space-x-3">
              <div :class="['rounded-lg p-2', agentType.bgColor]">
                <component :is="agentType.icon" :class="['h-5 w-5', agentType.iconColor]" />
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">{{ agentType.label }}</h3>
                <p class="text-sm text-gray-600">{{ agentType.description }}</p>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-between mt-4">
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-500">
                {{ getAgentTypeCount(agentType.value, 'Completed') }} completed
              </span>
              <span v-if="getAgentTypeCount(agentType.value, 'Running') > 0" class="text-sm text-blue-600 font-medium">
                {{ getAgentTypeCount(agentType.value, 'Running') }} running
              </span>
            </div>
            <Button
              size="sm"
              @click="runAgent(agentType.value)"
              :disabled="getAgentTypeCount(agentType.value, 'Running') > 0"
            >
              <PlayIcon class="h-3 w-3 mr-1" />
              Run
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="flex flex-wrap items-center gap-3">
        <FormControl
          type="select"
          v-model="filters.agent_type"
          :options="[{ label: 'All Agent Types', value: '' }, ...agentTypes.map(a => ({ label: a.label, value: a.value }))]"
          placeholder="Agent Type"
          class="w-44"
        />
        <FormControl
          type="select"
          v-model="filters.status"
          :options="statusOptions"
          placeholder="Status"
          class="w-36"
        />
        <FormControl
          type="date"
          v-model="filters.from_date"
          placeholder="From Date"
          class="w-40"
        />
        <FormControl
          type="date"
          v-model="filters.to_date"
          placeholder="To Date"
          class="w-40"
        />
        <Button variant="outline" size="sm" @click="resetFilters">
          Clear Filters
        </Button>
      </div>
    </div>

    <!-- Execution Log Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900">Execution Log</h2>
      </div>

      <!-- Loading -->
      <div v-if="store.loading" class="flex justify-center items-center py-12">
        <Spinner class="h-8 w-8" />
      </div>

      <!-- Table -->
      <div v-else-if="filteredExecutions.length > 0" class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-200 bg-gray-50">
              <th class="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Agent</th>
              <th class="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Task</th>
              <th class="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Status</th>
              <th class="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Started</th>
              <th class="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Duration</th>
              <th class="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Findings</th>
              <th class="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Tests</th>
              <th class="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Records</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="exec in paginatedExecutions"
              :key="exec.name"
              class="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
              @click="viewExecution(exec)"
            >
              <td class="px-6 py-3">
                <div class="flex items-center space-x-2">
                  <Badge :variant="getAgentBadgeVariant(exec.agent_type)">
                    {{ exec.agent_type }}
                  </Badge>
                </div>
              </td>
              <td class="px-6 py-3">
                <span class="text-sm text-gray-900">{{ exec.task_name || exec.task_type }}</span>
              </td>
              <td class="px-6 py-3">
                <Badge :variant="getStatusBadgeVariant(exec.status)">
                  {{ exec.status }}
                </Badge>
              </td>
              <td class="px-6 py-3">
                <span class="text-sm text-gray-600">{{ formatDateTime(exec.start_time) }}</span>
              </td>
              <td class="px-6 py-3">
                <span class="text-sm text-gray-600">{{ formatDuration(exec.duration_seconds) }}</span>
              </td>
              <td class="px-6 py-3">
                <div class="flex items-center space-x-1">
                  <span class="text-sm font-medium">{{ exec.total_findings || 0 }}</span>
                  <span v-if="exec.critical_findings > 0" class="text-xs text-red-600">({{ exec.critical_findings }} critical)</span>
                </div>
              </td>
              <td class="px-6 py-3">
                <div v-if="exec.total_tests > 0" class="flex items-center space-x-1">
                  <span class="text-sm text-green-600">{{ exec.passed_tests }}</span>
                  <span class="text-sm text-gray-400">/</span>
                  <span class="text-sm">{{ exec.total_tests }}</span>
                </div>
                <span v-else class="text-sm text-gray-400">-</span>
              </td>
              <td class="px-6 py-3">
                <span class="text-sm text-gray-600">{{ (exec.records_processed || 0).toLocaleString() }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <CpuIcon class="h-12 w-12 text-gray-300 mx-auto mb-3" />
        <p class="text-gray-600">No agent executions found.</p>
        <p class="text-sm text-gray-500 mt-1">Run an agent to get started.</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredExecutions.length > pageSize" class="flex items-center justify-between px-6 py-3 border-t border-gray-200">
        <span class="text-sm text-gray-600">
          Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, filteredExecutions.length) }}
          of {{ filteredExecutions.length }}
        </span>
        <div class="flex items-center space-x-2">
          <Button variant="outline" size="sm" :disabled="currentPage <= 1" @click="currentPage--">
            Previous
          </Button>
          <Button variant="outline" size="sm" :disabled="currentPage >= totalPages" @click="currentPage++">
            Next
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAgentStore } from "@/stores/agents"
import { Badge, Button, FormControl, Spinner } from "frappe-ui"
import {
	ActivityIcon,
	AlertTriangleIcon,
	CpuIcon,
	DollarSignIcon,
	EyeIcon,
	PlayIcon,
	RefreshCwIcon,
	SearchIcon,
	ShieldCheckIcon,
	BellIcon,
	BoxIcon,
} from "lucide-vue-next"
import { computed, onMounted, reactive, ref, watch } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const store = useAgentStore()

const isRunningAll = ref(false)
const currentPage = ref(1)
const pageSize = 20

const agentTypes = [
	{ value: "Financial", label: "Financial Agent", description: "Analyzes financial data and transactions", icon: DollarSignIcon, bgColor: "bg-green-100", iconColor: "text-green-600" },
	{ value: "Risk", label: "Risk Agent", description: "Evaluates risk factors and indicators", icon: AlertTriangleIcon, bgColor: "bg-orange-100", iconColor: "text-orange-600" },
	{ value: "Compliance", label: "Compliance Agent", description: "Checks regulatory compliance", icon: ShieldCheckIcon, bgColor: "bg-blue-100", iconColor: "text-blue-600" },
	{ value: "Discovery", label: "Discovery Agent", description: "Discovers anomalies and patterns", icon: SearchIcon, bgColor: "bg-gray-100", iconColor: "text-gray-600" },
	{ value: "Notification", label: "Notification Agent", description: "Manages alerts and notifications", icon: BellIcon, bgColor: "bg-yellow-100", iconColor: "text-yellow-600" },
	{ value: "Asset", label: "Asset Agent", description: "Reviews asset management controls", icon: BoxIcon, bgColor: "bg-gray-100", iconColor: "text-gray-600" },
]

const statusOptions = [
	{ label: "All Statuses", value: "" },
	{ label: "Pending", value: "Pending" },
	{ label: "Running", value: "Running" },
	{ label: "Completed", value: "Completed" },
	{ label: "Failed", value: "Failed" },
	{ label: "Cancelled", value: "Cancelled" },
	{ label: "Timeout", value: "Timeout" },
]

const filters = reactive({
	agent_type: "",
	status: "",
	from_date: "",
	to_date: "",
})

const filteredExecutions = computed(() => {
	let result = store.executions
	if (filters.agent_type) {
		result = result.filter((e) => e.agent_type === filters.agent_type)
	}
	if (filters.status) {
		result = result.filter((e) => e.status === filters.status)
	}
	if (filters.from_date) {
		result = result.filter((e) => e.start_time >= filters.from_date)
	}
	if (filters.to_date) {
		result = result.filter((e) => e.start_time <= filters.to_date + " 23:59:59")
	}
	return result
})

const totalPages = computed(() => Math.ceil(filteredExecutions.value.length / pageSize))
const paginatedExecutions = computed(() => {
	const start = (currentPage.value - 1) * pageSize
	return filteredExecutions.value.slice(start, start + pageSize)
})

watch(filters, () => { currentPage.value = 1 })

const getAgentTypeCount = (type, status) => {
	return store.executions.filter((e) => e.agent_type === type && e.status === status).length
}

const getAgentBadgeVariant = (type) => {
	const map = { Financial: "success", Risk: "warning", Compliance: "info", Discovery: "subtle", Notification: "warning", Asset: "secondary" }
	return map[type] || "secondary"
}

const getStatusBadgeVariant = (status) => {
	const map = { Pending: "secondary", Running: "info", Completed: "success", Failed: "danger", Cancelled: "warning", Timeout: "danger" }
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

const resetFilters = () => {
	filters.agent_type = ""
	filters.status = ""
	filters.from_date = ""
	filters.to_date = ""
}

const viewExecution = (exec) => {
	router.push(`/audit-execution/agent-dashboard/${exec.name}`)
}

const runAgent = async (agentType) => {
	try {
		await store.executeAgent(agentType)
	} catch (err) {
		console.error("Run agent failed:", err)
	}
}

const runAllAgents = async () => {
	isRunningAll.value = true
	try {
		await store.runAllAgents()
		await store.fetchExecutions()
	} catch (err) {
		console.error("Run all agents failed:", err)
	} finally {
		isRunningAll.value = false
	}
}

const refreshData = async () => {
	await Promise.all([
		store.fetchExecutions(),
		store.fetchAgentConfigs(),
	])
}

onMounted(() => {
	refreshData()
})
</script>
