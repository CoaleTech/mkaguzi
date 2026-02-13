<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Risk Indicators</h1>
        <p class="text-gray-600 mt-1">Monitor key risk metrics and thresholds</p>
      </div>
      <Button variant="outline" @click="refreshIndicators">
        <RefreshCwIcon class="h-4 w-4 mr-2" />
        Refresh
      </Button>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Total Indicators</p>
        <p class="text-2xl font-bold text-gray-900">{{ store.riskIndicators.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Active</p>
        <p class="text-2xl font-bold text-green-600">{{ store.activeIndicators.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Alerts/Critical</p>
        <p class="text-2xl font-bold text-red-600">{{ store.alertIndicators.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Declining Trend</p>
        <p class="text-2xl font-bold text-orange-600">{{ decliningCount }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="flex flex-wrap items-center gap-3">
        <FormControl type="text" v-model="search" placeholder="Search indicators..." class="w-52" />
        <FormControl
          type="select"
          v-model="filterModule"
          :options="moduleOptions"
          class="w-36"
        />
        <FormControl
          type="select"
          v-model="filterStatus"
          :options="[{ label: 'All Statuses', value: '' }, { label: 'Active', value: 'Active' }, { label: 'Inactive', value: 'Inactive' }, { label: 'Alert', value: 'Alert' }, { label: 'Critical', value: 'Critical' }]"
          class="w-36"
        />
        <Button variant="outline" size="sm" @click="resetFilters">Clear</Button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <!-- Indicators Grid -->
    <div v-else-if="filteredIndicators.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="indicator in filteredIndicators"
        :key="indicator.name"
        class="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow cursor-pointer"
        @click="showIndicatorDetail(indicator)"
      >
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="font-semibold text-gray-900">{{ indicator.indicator_name }}</h3>
            <p class="text-sm text-gray-500">{{ indicator.module }}</p>
          </div>
          <Badge :variant="getStatusVariant(indicator.status)">{{ indicator.status }}</Badge>
        </div>

        <!-- Value Display -->
        <div class="flex items-end justify-between mb-3">
          <div>
            <p class="text-3xl font-bold text-gray-900">
              {{ indicator.current_value != null ? formatValue(indicator.current_value) : '-' }}
            </p>
            <p class="text-sm text-gray-500">
              Threshold: {{ indicator.threshold_value != null ? formatValue(indicator.threshold_value) : '-' }}
            </p>
          </div>
          <div class="flex items-center space-x-1">
            <component :is="getTrendIcon(indicator.trend_direction)" :class="['h-4 w-4', getTrendColor(indicator.trend_direction)]" />
            <span :class="['text-sm font-medium', getTrendColor(indicator.trend_direction)]">
              {{ indicator.trend_direction || 'Stable' }}
            </span>
          </div>
        </div>

        <!-- Progress Bar (value vs threshold) -->
        <div v-if="indicator.threshold_value > 0" class="mb-3">
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              :class="[
                'h-2 rounded-full',
                getProgressColor(indicator.current_value, indicator.threshold_value)
              ]"
              :style="{ width: Math.min((indicator.current_value / indicator.threshold_value) * 100, 100) + '%' }"
            ></div>
          </div>
        </div>

        <div class="flex items-center justify-between text-xs text-gray-500">
          <span>{{ indicator.indicator_type }}</span>
          <span>{{ indicator.frequency || 'Daily' }}</span>
          <span>{{ indicator.last_updated ? timeAgo(indicator.last_updated) : 'Never' }}</span>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="bg-white rounded-lg border border-gray-200 p-12 text-center">
      <ActivityIcon class="h-12 w-12 text-gray-300 mx-auto mb-3" />
      <p class="text-gray-600">No risk indicators found.</p>
    </div>

    <!-- Detail Dialog -->
    <Dialog v-model="showDetail" :options="{ title: selectedIndicator?.indicator_name || 'Indicator Details', size: 'xl' }">
      <template #body-content>
        <div v-if="indicatorDetail" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600">Indicator ID</p>
              <p class="font-medium">{{ indicatorDetail.indicator_id }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Module</p>
              <p class="font-medium">{{ indicatorDetail.module }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Type</p>
              <p class="font-medium">{{ indicatorDetail.indicator_type }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Calculation Method</p>
              <p class="font-medium">{{ indicatorDetail.calculation_method || '-' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Current Value</p>
              <p class="text-xl font-bold">{{ formatValue(indicatorDetail.current_value) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Threshold Value</p>
              <p class="text-xl font-bold text-gray-600">{{ formatValue(indicatorDetail.threshold_value) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Frequency</p>
              <p class="font-medium">{{ indicatorDetail.frequency }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Data Source</p>
              <p class="font-medium">{{ indicatorDetail.data_source || '-' }}</p>
            </div>
          </div>
          <div v-if="indicatorDetail.description">
            <p class="text-sm text-gray-600 mb-1">Description</p>
            <p class="text-sm text-gray-700">{{ indicatorDetail.description }}</p>
          </div>
          <div v-if="indicatorDetail.alert_triggers">
            <p class="text-sm text-gray-600 mb-1">Alert Triggers</p>
            <pre class="bg-gray-50 rounded p-3 text-sm overflow-x-auto max-h-32">{{ formatJSON(indicatorDetail.alert_triggers) }}</pre>
          </div>
          <div v-if="indicatorDetail.historical_data">
            <p class="text-sm text-gray-600 mb-1">Historical Data</p>
            <pre class="bg-gray-50 rounded p-3 text-sm overflow-x-auto max-h-48">{{ formatJSON(indicatorDetail.historical_data) }}</pre>
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
import { useRiskMonitoringStore } from "@/stores/riskMonitoring"
import { Badge, Button, Dialog, FormControl, Spinner } from "frappe-ui"
import {
	ActivityIcon,
	ArrowDownIcon,
	ArrowUpIcon,
	MinusIcon,
	RefreshCwIcon,
	TrendingDownIcon,
	TrendingUpIcon,
	ZapIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

const store = useRiskMonitoringStore()
const search = ref("")
const filterModule = ref("")
const filterStatus = ref("")
const showDetail = ref(false)
const selectedIndicator = ref(null)
const indicatorDetail = ref(null)

const moduleOptions = [
	{ label: "All Modules", value: "" },
	{ label: "Financial", value: "Financial" },
	{ label: "HR", value: "HR" },
	{ label: "Payroll", value: "Payroll" },
	{ label: "Inventory", value: "Inventory" },
	{ label: "Access Control", value: "Access Control" },
	{ label: "General", value: "General" },
]

const decliningCount = computed(() => store.riskIndicators.filter((i) => i.trend_direction === "Declining").length)

const filteredIndicators = computed(() => {
	let result = store.riskIndicators
	if (search.value) {
		const q = search.value.toLowerCase()
		result = result.filter((i) => i.indicator_name?.toLowerCase().includes(q) || i.indicator_id?.toLowerCase().includes(q))
	}
	if (filterModule.value) result = result.filter((i) => i.module === filterModule.value)
	if (filterStatus.value) result = result.filter((i) => i.status === filterStatus.value)
	return result
})

const getStatusVariant = (s) => ({ Active: "success", Inactive: "secondary", Alert: "warning", Critical: "danger" })[s] || "secondary"

const getTrendIcon = (trend) => {
	const map = { Improving: TrendingUpIcon, Stable: MinusIcon, Declining: TrendingDownIcon, Volatile: ZapIcon }
	return map[trend] || MinusIcon
}

const getTrendColor = (trend) => {
	const map = { Improving: "text-green-600", Stable: "text-gray-500", Declining: "text-red-600", Volatile: "text-orange-600" }
	return map[trend] || "text-gray-500"
}

const getProgressColor = (current, threshold) => {
	const ratio = current / threshold
	if (ratio >= 1) return "bg-red-500"
	if (ratio >= 0.8) return "bg-orange-500"
	if (ratio >= 0.6) return "bg-yellow-500"
	return "bg-green-500"
}

const formatValue = (val) => {
	if (val == null) return "-"
	if (typeof val === "number") return val.toLocaleString(undefined, { maximumFractionDigits: 2 })
	return val
}

const timeAgo = (dt) => {
	if (!dt) return "Never"
	const diff = (Date.now() - new Date(dt).getTime()) / 1000
	if (diff < 60) return "Just now"
	if (diff < 3600) return `${Math.round(diff / 60)}m ago`
	if (diff < 86400) return `${Math.round(diff / 3600)}h ago`
	return `${Math.round(diff / 86400)}d ago`
}

const formatJSON = (data) => {
	try { return JSON.stringify(JSON.parse(data), null, 2) } catch { return data }
}

const resetFilters = () => {
	search.value = ""
	filterModule.value = ""
	filterStatus.value = ""
}

const showIndicatorDetail = async (indicator) => {
	selectedIndicator.value = indicator
	indicatorDetail.value = null
	showDetail.value = true
	indicatorDetail.value = await store.fetchIndicatorDetail(indicator.name)
}

const refreshIndicators = () => store.fetchRiskIndicators()

onMounted(() => {
	store.fetchRiskIndicators()
})
</script>
