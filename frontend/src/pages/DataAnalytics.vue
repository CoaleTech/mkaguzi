<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Data Analytics</h1>
        <p class="text-gray-600 mt-1">
          Create and manage data analytics dashboards and visualizations
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button @click="createNewDashboard">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Dashboard
        </Button>
      </div>
    </div>

    <!-- Dashboard Tabs -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="border-b border-gray-200">
        <nav class="flex">
          <button
            @click="activeTab = 'dashboards'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'dashboards'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Dashboards
          </button>
          <button
            @click="activeTab = 'charts'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'charts'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Charts
          </button>
          <button
            @click="activeTab = 'data-sources'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'data-sources'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Data Sources
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Dashboards Tab -->
        <div v-if="activeTab === 'dashboards'">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- Create New Dashboard Card -->
            <div
              class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-blue-400 hover:bg-blue-50 cursor-pointer transition-colors"
              @click="createNewDashboard"
            >
              <div class="flex flex-col items-center justify-center h-full">
                <PlusIcon class="h-12 w-12 text-gray-400 mb-4" />
                <h3 class="text-lg font-medium text-gray-900 mb-2">Create New Dashboard</h3>
                <p class="text-sm text-gray-600 text-center">
                  Build a custom dashboard with charts and visualizations
                </p>
              </div>
            </div>

            <!-- Dashboard Cards -->
            <div
              v-for="dashboard in dataStore.dashboards"
              :key="dashboard.name"
              class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
              @click="viewDashboard(dashboard)"
            >
              <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                  <h3 class="text-lg font-medium text-gray-900 mb-1">
                    {{ dashboard.dashboard_name }}
                  </h3>
                  <p class="text-sm text-gray-600 mb-2">
                    {{ dashboard.description || 'No description' }}
                  </p>
                  <div class="flex items-center space-x-2">
                    <Badge :variant="getDashboardTypeVariant(dashboard.dashboard_type)">
                      {{ dashboard.dashboard_type }}
                    </Badge>
                    <Badge :variant="dashboard.is_active ? 'success' : 'secondary'">
                      {{ dashboard.is_active ? 'Active' : 'Inactive' }}
                    </Badge>
                  </div>
                </div>
                <Button variant="ghost" size="sm" @click.stop="editDashboard(dashboard)">
                  <EditIcon class="h-4 w-4" />
                </Button>
              </div>

              <div class="flex items-center justify-between text-sm text-gray-500">
                <span>Modified {{ formatDate(dashboard.modified) }}</span>
                <span>{{ dashboard.total_views || 0 }} views</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Tab -->
        <div v-if="activeTab === 'charts'">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-medium text-gray-900">Chart Library</h2>
            <Button @click="createNewChart">
              <PlusIcon class="h-4 w-4 mr-2" />
              New Chart
            </Button>
          </div>

          <!-- Permission Restricted Message -->
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <BarChart3Icon class="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-yellow-800 mb-2">Charts Feature Restricted</h3>
            <p class="text-yellow-700">
              The chart library is currently not available due to permission restrictions.
              Please contact your administrator for access to advanced analytics features.
            </p>
          </div>
        </div>

        <!-- Data Sources Tab -->
        <div v-if="activeTab === 'data-sources'">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-medium text-gray-900">Data Sources</h2>
            <Button @click="createNewDataSource">
              <PlusIcon class="h-4 w-4 mr-2" />
              New Data Source
            </Button>
          </div>

          <!-- Permission Restricted Message -->
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <DatabaseIcon class="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-yellow-800 mb-2">Data Sources Feature Restricted</h3>
            <p class="text-yellow-700">
              The data sources management is currently not available due to permission restrictions.
              Please contact your administrator for access to advanced data management features.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <DataAnalyticsStats
      :dashboards="dataStore.dashboards"
      :dashboard-charts="[]"
      :dashboard-data-sources="[]"
    />
  </div>
</template>

<script setup>
import { useDataStore } from "@/stores/data"
import { Badge, Button } from "frappe-ui"
import {
	BarChart3Icon,
	CheckCircleIcon,
	DatabaseIcon,
	DownloadIcon,
	EditIcon,
	PieChartIcon,
	PlusIcon,
} from "lucide-vue-next"
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import DataAnalyticsStats from "@/components/data/DataAnalyticsStats.vue"

const router = useRouter()
const dataStore = useDataStore()

// Reactive state
const activeTab = ref("dashboards")
const loading = ref(false)

// Methods
const fetchData = async () => {
	loading.value = true
	try {
		await Promise.all([
			dataStore.fetchDashboards(),
			// Note: Dashboard Charts and Data Sources are restricted doctypes
			// dataStore.fetchDashboardCharts(),
			// dataStore.fetchDashboardDataSources(),
		])
	} catch (error) {
		console.error("Error loading data analytics:", error)
	} finally {
		loading.value = false
	}
}

const getDashboardTypeVariant = (type) => {
	const variants = {
		Private: "secondary",
		Public: "success",
		Shared: "info",
	}
	return variants[type] || "secondary"
}

const getChartTypeVariant = (type) => {
	const variants = {
		"Line Chart": "info",
		"Bar Chart": "success",
		"Pie Chart": "warning",
		"Doughnut Chart": "warning",
		"Area Chart": "info",
		"Scatter Plot": "secondary",
		"Heat Map": "danger",
		Gauge: "secondary",
		Table: "secondary",
		"KPI Card": "success",
	}
	return variants[type] || "secondary"
}

const formatDate = (date) => {
	if (!date) return "Never"
	return new Date(date).toLocaleDateString()
}

const createNewDashboard = () => {
	router.push("/data-analytics/dashboard/new")
}

const viewDashboard = (dashboard) => {
	router.push(`/data-analytics/dashboard/${dashboard.name}`)
}

const editDashboard = (dashboard) => {
	router.push(`/data-analytics/dashboard/${dashboard.name}/edit`)
}

const createNewChart = () => {
	router.push("/data-analytics/chart/new")
}

const editChart = (chart) => {
	router.push(`/data-analytics/chart/${chart.name}/edit`)
}

const createNewDataSource = () => {
	router.push("/data-analytics/data-source/new")
}

const editDataSource = (source) => {
	router.push(`/data-analytics/data-source/${source.name}/edit`)
}

// Lifecycle
onMounted(async () => {
	await fetchData()
})
</script>