<template>
  <div class="template-analytics">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Template Analytics</h1>
        <p class="text-gray-600 mt-1">Monitor template usage, performance, and engagement metrics</p>
      </div>
      <div class="flex items-center space-x-3">
        <Button @click="refreshData" :loading="loading" variant="outline">
          <RefreshCw class="w-4 h-4 mr-2" />
          Refresh
        </Button>
        <Button @click="exportAnalytics" variant="outline">
          <Download class="w-4 h-4 mr-2" />
          Export
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <FormControl
          label="Template"
          v-model="filters.template_id"
          type="select"
          :options="templateOptions"
          placeholder="All Templates"
          @update:model-value="applyFilters"
        />

        <FormControl
          label="Category"
          v-model="filters.category"
          type="select"
          :options="categoryOptions"
          placeholder="All Categories"
          @update:model-value="applyFilters"
        />

        <FormControl
          label="Date From"
          v-model="filters.date_from"
          type="date"
          @update:model-value="applyFilters"
        />

        <FormControl
          label="Date To"
          v-model="filters.date_to"
          type="date"
          @update:model-value="applyFilters"
        />
      </div>
    </div>

    <!-- Performance Metrics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <Eye class="w-6 h-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Views</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatNumber(performanceMetrics.total_views) }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <Play class="w-6 h-6 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Renders</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatNumber(performanceMetrics.total_renders) }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <Clock class="w-6 h-6 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Avg Render Time</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatTime(performanceMetrics.avg_render_time) }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-red-100 rounded-lg">
            <AlertTriangle class="w-6 h-6 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Success Rate</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatPercentage(performanceMetrics.avg_success_rate) }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Usage Trends Chart -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Usage Trends (Last 30 Days)</h3>
        <div class="h-64">
          <canvas ref="usageChart"></canvas>
        </div>
      </div>

      <!-- Top Templates -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Top Templates by Usage</h3>
        <div class="space-y-3">
          <div
            v-for="(template, index) in topTemplates"
            :key="template.template_name"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex items-center">
              <div class="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span class="text-sm font-medium text-blue-600">{{ index + 1 }}</span>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">{{ template.template_name }}</p>
                <p class="text-xs text-gray-500">{{ template.total_uses }} uses</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-medium text-gray-900">{{ formatTime(template.average_render_time) }}</p>
              <p class="text-xs text-gray-500">{{ formatPercentage(template.success_rate) }} success</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Detailed Analytics Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Detailed Analytics</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Template
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Views
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Uses
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Avg Time
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Success Rate
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Used
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="analytics in analyticsData"
              :key="analytics.name"
              class="hover:bg-gray-50"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ analytics.template_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                  {{ analytics.category }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatNumber(analytics.total_views) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatNumber(analytics.total_uses) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatTime(analytics.average_render_time) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                  :class="getSuccessRateClass(analytics.success_rate)"
                >
                  {{ formatPercentage(analytics.success_rate) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(analytics.last_used_date) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Error Summary -->
    <div v-if="errorSummary.total_errors > 0" class="bg-white rounded-lg border border-gray-200 p-6 mt-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Error Summary</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <p class="text-sm text-gray-600">Total Errors</p>
          <p class="text-2xl font-bold text-red-600">{{ formatNumber(errorSummary.total_errors) }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-600">Avg Errors per Template</p>
          <p class="text-2xl font-bold text-red-600">{{ formatNumber(errorSummary.avg_errors_per_template) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Chart from "chart.js/auto"
import {
	AlertTriangle,
	Clock,
	Download,
	Eye,
	Play,
	RefreshCw,
} from "lucide-vue-next"
import { computed, onMounted, reactive, ref } from "vue"

// Reactive data
const loading = ref(false)
const analyticsData = ref([])
const performanceMetrics = reactive({
	total_views: 0,
	total_renders: 0,
	avg_render_time: 0,
	avg_success_rate: 0,
})
const topTemplates = ref([])
const usageTrends = ref([])
const errorSummary = reactive({
	total_errors: 0,
	avg_errors_per_template: 0,
})

const filters = reactive({
	template_id: "",
	category: "",
	date_from: "",
	date_to: "",
})

const templateOptions = ref([])
const categoryOptions = [
	{ label: "All Categories", value: "" },
	{ label: "Audit Report", value: "Audit Report" },
	{ label: "Compliance Report", value: "Compliance Report" },
	{ label: "Financial Report", value: "Financial Report" },
	{ label: "Risk Assessment", value: "Risk Assessment" },
	{ label: "Custom Report", value: "Custom Report" },
]

// Refs
const usageChart = ref(null)
let chartInstance = null

// Methods
const loadAnalyticsData = async () => {
	loading.value = true
	try {
		const response = await fetch(
			"/api/method/mkaguzi.api.templates.get_analytics_dashboard_data",
		)
		const result = await response.json()

		if (result.message.success) {
			const data = result.message.data

			// Update performance metrics
			Object.assign(performanceMetrics, data.performance_metrics)

			// Update top templates
			topTemplates.value = data.top_templates || []

			// Update usage trends
			usageTrends.value = data.usage_trends || []

			// Update error summary
			Object.assign(errorSummary, data.error_summary)

			// Update chart
			updateChart()
		}
	} catch (error) {
		console.error("Error loading analytics data:", error)
	} finally {
		loading.value = false
	}
}

const loadAnalyticsTable = async () => {
	try {
		const params = new URLSearchParams()
		if (filters.template_id) params.append("template_id", filters.template_id)
		if (filters.category) params.append("category", filters.category)
		if (filters.date_from) params.append("date_from", filters.date_from)
		if (filters.date_to) params.append("date_to", filters.date_to)

		const response = await fetch(
			`/api/method/mkaguzi.api.templates.get_template_analytics?${params}`,
		)
		const result = await response.json()

		if (result.message.success) {
			analyticsData.value = result.message.data
		}
	} catch (error) {
		console.error("Error loading analytics table:", error)
	}
}

const loadTemplates = async () => {
	try {
		const response = await fetch(
			"/api/method/mkaguzi.api.templates.get_templates",
		)
		const result = await response.json()

		if (result.message.success) {
			templateOptions.value = [
				{ label: "All Templates", value: "" },
				...result.message.data.map((template) => ({
					label: template.template_name,
					value: template.name,
				})),
			]
		}
	} catch (error) {
		console.error("Error loading templates:", error)
	}
}

const updateChart = () => {
	if (!usageChart.value) return

	// Destroy existing chart
	if (chartInstance) {
		chartInstance.destroy()
	}

	const ctx = usageChart.value.getContext("2d")

	chartInstance = new Chart(ctx, {
		type: "line",
		data: {
			labels: usageTrends.value.map((trend) => trend.date),
			datasets: [
				{
					label: "Views",
					data: usageTrends.value.map((trend) => trend.views),
					borderColor: "rgb(59, 130, 246)",
					backgroundColor: "rgba(59, 130, 246, 0.1)",
					tension: 0.4,
				},
				{
					label: "Uses",
					data: usageTrends.value.map((trend) => trend.uses),
					borderColor: "rgb(16, 185, 129)",
					backgroundColor: "rgba(16, 185, 129, 0.1)",
					tension: 0.4,
				},
				{
					label: "Renders",
					data: usageTrends.value.map((trend) => trend.renders),
					borderColor: "rgb(245, 158, 11)",
					backgroundColor: "rgba(245, 158, 11, 0.1)",
					tension: 0.4,
				},
			],
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			scales: {
				y: {
					beginAtZero: true,
				},
			},
			plugins: {
				legend: {
					position: "top",
				},
			},
		},
	})
}

const applyFilters = () => {
	loadAnalyticsTable()
}

const refreshData = () => {
	loadAnalyticsData()
	loadAnalyticsTable()
}

const exportAnalytics = () => {
	// TODO: Implement export functionality
	console.log("Export analytics data")
}

// Utility methods
const formatNumber = (num) => {
	if (!num) return "0"
	return new Intl.NumberFormat().format(num)
}

const formatTime = (seconds) => {
	if (!seconds) return "0s"
	if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`
	return `${seconds.toFixed(2)}s`
}

const formatPercentage = (value) => {
	if (value === null || value === undefined) return "0%"
	return `${value.toFixed(1)}%`
}

const formatDate = (dateString) => {
	if (!dateString) return "Never"
	return new Date(dateString).toLocaleDateString()
}

const getSuccessRateClass = (rate) => {
	if (!rate) return "bg-gray-100 text-gray-800"
	if (rate >= 95) return "bg-green-100 text-green-800"
	if (rate >= 80) return "bg-yellow-100 text-yellow-800"
	return "bg-red-100 text-red-800"
}

// Lifecycle
onMounted(() => {
	loadTemplates()
	loadAnalyticsData()
	loadAnalyticsTable()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>