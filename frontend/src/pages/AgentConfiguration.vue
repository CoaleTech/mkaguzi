<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Agent Configuration</h1>
        <p class="text-gray-600 mt-1">Manage AI agent settings and schedules</p>
      </div>
      <Button variant="outline" @click="refreshConfigs">
        <RefreshCwIcon class="h-4 w-4 mr-2" />
        Refresh
      </Button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <!-- Config List -->
    <div v-else-if="store.agentConfigs.length > 0" class="space-y-4">
      <div
        v-for="config in store.agentConfigs"
        :key="config.name"
        class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
        @click="selectConfig(config)"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center space-x-4">
            <div :class="['rounded-lg p-3', config.is_active ? 'bg-green-100' : 'bg-gray-100']">
              <CpuIcon :class="['h-6 w-6', config.is_active ? 'text-green-600' : 'text-gray-400']" />
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">{{ config.configuration_name }}</h3>
              <p class="text-sm text-gray-600">{{ config.agent_type }} Agent</p>
              <p v-if="config.description" class="text-sm text-gray-500 mt-1">{{ config.description }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <Badge v-if="config.priority" :variant="getPriorityVariant(config.priority)">
              {{ config.priority }}
            </Badge>
            <button
              @click.stop="toggleActive(config)"
              :class="[
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                config.is_active ? 'bg-green-600' : 'bg-gray-300'
              ]"
            >
              <span
                :class="[
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  config.is_active ? 'translate-x-6' : 'translate-x-1'
                ]"
              />
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mt-4 pt-4 border-t border-gray-100">
          <div>
            <p class="text-xs text-gray-500">Schedule</p>
            <p class="text-sm font-medium">{{ config.execution_schedule || 'Manual' }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-500">Timeout</p>
            <p class="text-sm font-medium">{{ config.timeout_seconds || 300 }}s</p>
          </div>
          <div>
            <p class="text-xs text-gray-500">Max Memory</p>
            <p class="text-sm font-medium">{{ config.max_memory_mb || 512 }} MB</p>
          </div>
          <div>
            <p class="text-xs text-gray-500">Max CPU</p>
            <p class="text-sm font-medium">{{ config.max_cpu_percent || 80 }}%</p>
          </div>
          <div>
            <p class="text-xs text-gray-500">Log Level</p>
            <p class="text-sm font-medium">{{ config.log_level || 'INFO' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="bg-white rounded-lg border border-gray-200 p-12 text-center">
      <CpuIcon class="h-12 w-12 text-gray-300 mx-auto mb-3" />
      <p class="text-gray-600">No agent configurations found.</p>
      <p class="text-sm text-gray-500 mt-1">Agent configurations are created via the Frappe desk.</p>
    </div>

    <!-- Detail Dialog -->
    <Dialog v-model="showDetail" :options="{ title: selectedConfig?.configuration_name || 'Configuration', size: 'xl' }">
      <template #body-content>
        <div v-if="configDetail" class="space-y-6">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600">Agent Type</p>
              <p class="font-medium">{{ configDetail.agent_type }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Status</p>
              <Badge :variant="configDetail.is_active ? 'success' : 'secondary'">
                {{ configDetail.is_active ? 'Active' : 'Inactive' }}
              </Badge>
            </div>
            <div>
              <p class="text-sm text-gray-600">Priority</p>
              <Badge :variant="getPriorityVariant(configDetail.priority)">{{ configDetail.priority }}</Badge>
            </div>
            <div>
              <p class="text-sm text-gray-600">Schedule</p>
              <p class="font-medium">{{ configDetail.execution_schedule || 'Manual' }}</p>
            </div>
          </div>

          <div>
            <p class="text-sm text-gray-600 mb-1">Description</p>
            <p class="text-sm text-gray-700">{{ configDetail.description || 'No description' }}</p>
          </div>

          <div>
            <h4 class="font-medium text-gray-900 mb-2">Resource Limits</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Timeout</p>
                <p class="font-medium">{{ configDetail.timeout_seconds }}s</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Max Memory</p>
                <p class="font-medium">{{ configDetail.max_memory_mb }} MB</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Max CPU</p>
                <p class="font-medium">{{ configDetail.max_cpu_percent }}%</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Concurrent Tasks</p>
                <p class="font-medium">{{ configDetail.max_concurrent_tasks }}</p>
              </div>
            </div>
          </div>

          <div v-if="configDetail.config_json">
            <h4 class="font-medium text-gray-900 mb-2">Configuration JSON</h4>
            <pre class="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto max-h-64">{{ formatJSON(configDetail.config_json) }}</pre>
          </div>

          <div>
            <h4 class="font-medium text-gray-900 mb-2">Logging</h4>
            <div class="grid grid-cols-3 gap-3">
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Logging</p>
                <p class="font-medium">{{ configDetail.enable_logging ? 'Enabled' : 'Disabled' }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Log Level</p>
                <p class="font-medium">{{ configDetail.log_level }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Failure Alerts</p>
                <p class="font-medium">{{ configDetail.notification_on_failure ? 'Yes' : 'No' }}</p>
              </div>
            </div>
          </div>

          <div v-if="configDetail.notes">
            <h4 class="font-medium text-gray-900 mb-2">Notes</h4>
            <p class="text-sm text-gray-700">{{ configDetail.notes }}</p>
          </div>
        </div>
        <div v-else class="flex justify-center py-8">
          <Spinner class="h-6 w-6" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { useAgentStore } from "@/stores/agents"
import { Badge, Button, Dialog, Spinner } from "frappe-ui"
import {
	CpuIcon,
	RefreshCwIcon,
} from "lucide-vue-next"
import { onMounted, ref } from "vue"

const store = useAgentStore()
const loading = ref(false)
const showDetail = ref(false)
const selectedConfig = ref(null)
const configDetail = ref(null)

const getPriorityVariant = (priority) => {
	const map = { Low: "secondary", Medium: "info", High: "warning", Critical: "danger" }
	return map[priority] || "secondary"
}

const formatJSON = (data) => {
	if (!data) return ""
	try {
		return JSON.stringify(JSON.parse(data), null, 2)
	} catch {
		return data
	}
}

const refreshConfigs = async () => {
	loading.value = true
	try {
		await store.fetchAgentConfigs()
	} finally {
		loading.value = false
	}
}

const selectConfig = async (config) => {
	selectedConfig.value = config
	showDetail.value = true
	configDetail.value = null
	configDetail.value = await store.fetchAgentConfigDetail(config.name)
}

const toggleActive = async (config) => {
	try {
		await store.updateAgentConfig(config.name, "is_active", config.is_active ? 0 : 1)
	} catch (err) {
		console.error("Toggle failed:", err)
	}
}

onMounted(() => {
	refreshConfigs()
})
</script>
