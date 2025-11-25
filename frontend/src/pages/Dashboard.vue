<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-gray-600 mt-1">
          Overview of audit activities and key metrics
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Select
          v-model="selectedPeriod"
          :options="periodOptions"
          class="w-32"
        />
        <Button
          variant="outline"
          @click="refreshData"
          :loading="loading"
        >
          <RefreshCwIcon class="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Active Engagements -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Active Engagements</p>
            <p class="text-3xl font-bold text-gray-900">{{ stats.activeEngagements }}</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-full">
            <FileTextIcon class="h-6 w-6 text-blue-600" />
          </div>
        </div>
        <div class="mt-4 flex items-center text-sm">
          <TrendingUpIcon class="h-4 w-4 text-green-500 mr-1" />
          <span class="text-green-600 font-medium">+12%</span>
          <span class="text-gray-500 ml-1">from last month</span>
        </div>
      </div>

      <!-- Open Findings -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Open Findings</p>
            <p class="text-3xl font-bold text-gray-900">{{ stats.openFindings }}</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-full">
            <AlertTriangleIcon class="h-6 w-6 text-yellow-600" />
          </div>
        </div>
        <div class="mt-4 flex items-center text-sm">
          <TrendingDownIcon class="h-4 w-4 text-red-500 mr-1" />
          <span class="text-red-600 font-medium">-5%</span>
          <span class="text-gray-500 ml-1">from last month</span>
        </div>
      </div>

      <!-- Compliance Score -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Compliance Score</p>
            <p class="text-3xl font-bold text-gray-900">{{ stats.complianceScore }}%</p>
          </div>
          <div class="p-3 bg-green-100 rounded-full">
            <CheckCircleIcon class="h-6 w-6 text-green-600" />
          </div>
        </div>
        <div class="mt-4 flex items-center text-sm">
          <TrendingUpIcon class="h-4 w-4 text-green-500 mr-1" />
          <span class="text-green-600 font-medium">+2%</span>
          <span class="text-gray-500 ml-1">from last month</span>
        </div>
      </div>

      <!-- Risk Level -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Overall Risk</p>
            <p class="text-3xl font-bold text-gray-900">{{ stats.overallRisk }}</p>
          </div>
          <div class="p-3 bg-red-100 rounded-full">
            <AlertCircleIcon class="h-6 w-6 text-red-600" />
          </div>
        </div>
        <div class="mt-4 flex items-center text-sm">
          <MinusIcon class="h-4 w-4 text-gray-500 mr-1" />
          <span class="text-gray-600 font-medium">No change</span>
          <span class="text-gray-500 ml-1">from last month</span>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Audit Status Chart -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Audit Status Overview</h3>
          <Button variant="ghost" size="sm">
            <MoreHorizontalIcon class="h-4 w-4" />
          </Button>
        </div>
        <div class="h-64">
          <canvas ref="auditStatusChartRef" class="w-full h-full"></canvas>
        </div>
      </div>

      <!-- Risk Distribution Chart -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Risk Distribution</h3>
          <Button variant="ghost" size="sm">
            <MoreHorizontalIcon class="h-4 w-4" />
          </Button>
        </div>
        <div class="h-64">
          <canvas ref="riskDistributionChartRef" class="w-full h-full"></canvas>
        </div>
      </div>
    </div>

    <!-- Recent Activities and Upcoming Tasks -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent Activities -->
      <div class="bg-white rounded-lg border border-gray-200">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">Recent Activities</h3>
            <Button variant="ghost" size="sm">
              View All
            </Button>
          </div>
        </div>
        <div class="divide-y divide-gray-200">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="px-6 py-4 hover:bg-gray-50"
          >
            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0">
                <div
                  :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center',
                    getActivityIconBg(activity.type)
                  ]"
                >
                  <component
                    :is="getActivityIcon(activity.type)"
                    class="h-4 w-4 text-white"
                  />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900">
                  {{ activity.title }}
                </p>
                <p class="text-sm text-gray-500">
                  {{ activity.description }}
                </p>
                <p class="text-xs text-gray-400 mt-1">
                  {{ formatDate(activity.timestamp) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Tasks -->
      <div class="bg-white rounded-lg border border-gray-200">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">Upcoming Tasks</h3>
            <Button variant="ghost" size="sm">
              View All
            </Button>
          </div>
        </div>
        <div class="divide-y divide-gray-200">
          <div
            v-for="task in upcomingTasks"
            :key="task.id"
            class="px-6 py-4 hover:bg-gray-50"
          >
            <div class="flex items-start space-x-3">
              <Checkbox
                :checked="task.completed"
                @change="toggleTask(task)"
                class="mt-0.5"
              />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900">
                  {{ task.title }}
                </p>
                <p class="text-sm text-gray-500">
                  {{ task.description }}
                </p>
                <div class="flex items-center space-x-2 mt-1">
                  <Badge
                    :variant="getPriorityVariant(task.priority)"
                    size="sm"
                  >
                    {{ task.priority }}
                  </Badge>
                  <span class="text-xs text-gray-400">
                    Due {{ formatDate(task.dueDate) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Button
          variant="outline"
          class="h-20 flex flex-col items-center justify-center space-y-2"
          @click="$router.push('/engagements/new')"
        >
          <PlusIcon class="h-6 w-6" />
          <span class="text-sm">New Engagement</span>
        </Button>
        <Button
          variant="outline"
          class="h-20 flex flex-col items-center justify-center space-y-2"
          @click="$router.push('/findings')"
        >
          <SearchIcon class="h-6 w-6" />
          <span class="text-sm">Review Findings</span>
        </Button>
        <Button
          variant="outline"
          class="h-20 flex flex-col items-center justify-center space-y-2"
          @click="$router.push('/reports')"
        >
          <BarChart3Icon class="h-6 w-6" />
          <span class="text-sm">Generate Report</span>
        </Button>
        <Button
          variant="outline"
          class="h-20 flex flex-col items-center justify-center space-y-2"
          @click="$router.push('/compliance')"
        >
          <CheckSquareIcon class="h-6 w-6" />
          <span class="text-sm">Compliance Check</span>
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuditStore } from "@/stores/audit"
import { useDataStore } from "@/stores/data"
import {
	ArcElement,
	BarController,
	BarElement,
	CategoryScale,
	Chart as ChartJS,
	Legend,
	LinearScale,
	PieController,
	Title,
	Tooltip,
} from "chart.js"
import { Badge, Button, Checkbox, Select } from "frappe-ui"
import {
	AlertCircleIcon,
	AlertTriangleIcon,
	BarChart3Icon,
	CheckCircleIcon,
	CheckSquareIcon,
	FileTextIcon,
	MinusIcon,
	MoreHorizontalIcon,
	PlusIcon,
	RefreshCwIcon,
	SearchIcon,
	TrendingDownIcon,
	TrendingUpIcon,
} from "lucide-vue-next"
import { computed, nextTick, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

ChartJS.register(
	ArcElement,
	Tooltip,
	Legend,
	CategoryScale,
	LinearScale,
	BarElement,
	BarController,
	Title,
	PieController,
)

const router = useRouter()
const auditStore = useAuditStore()
const dataStore = useDataStore()

// Reactive state
const loading = ref(false)
const selectedPeriod = ref("month")

// Chart refs
const auditStatusChartRef = ref(null)
const riskDistributionChartRef = ref(null)

// Constants
const periodOptions = [
	{ label: "Week", value: "week" },
	{ label: "Month", value: "month" },
	{ label: "Quarter", value: "quarter" },
	{ label: "Year", value: "year" },
]

// Computed properties
const stats = computed(() => ({
	activeEngagements: auditStore.activeEngagements.length,
	openFindings: auditStore.findings.filter((f) => f.finding_status === "Open")
		.length,
	complianceScore: 87, // This could be calculated from real data
	overallRisk: "Medium", // This could be calculated from risk assessments
}))

const auditStatusData = computed(() => {
	const engagements = auditStore.engagements
	const statusCounts = {
		Planning: 0,
		"In Progress": 0,
		Review: 0,
		Completed: 0,
	}

	engagements.forEach((engagement) => {
		const status = engagement.status
		if (status === "planned") statusCounts["Planning"]++
		else if (status === "in_progress") statusCounts["In Progress"]++
		else if (status === "under_review") statusCounts["Review"]++
		else if (status === "completed") statusCounts["Completed"]++
	})

	return {
		labels: Object.keys(statusCounts),
		datasets: [
			{
				data: Object.values(statusCounts),
				backgroundColor: [
					"#3B82F6", // Blue
					"#F59E0B", // Yellow
					"#8B5CF6", // Purple
					"#10B981", // Green
				],
				borderWidth: 1,
			},
		],
	}
})

const riskDistributionData = computed(() => {
	const findings = auditStore.findings
	const riskCounts = {
		Low: 0,
		Medium: 0,
		High: 0,
		Critical: 0,
	}

	findings.forEach((finding) => {
		const risk = finding.risk_rating
		if (riskCounts.hasOwnProperty(risk)) {
			riskCounts[risk]++
		}
	})

	return {
		labels: Object.keys(riskCounts),
		datasets: [
			{
				label: "Risk Count",
				data: Object.values(riskCounts),
				backgroundColor: [
					"#10B981", // Green
					"#F59E0B", // Yellow
					"#EF4444", // Red
					"#7C2D12", // Dark Red
				],
				borderWidth: 1,
			},
		],
	}
})

const recentActivities = computed(() => {
	const activities = []

	// Add recent engagements
	auditStore.engagements.slice(0, 2).forEach((engagement) => {
		activities.push({
			id: `engagement-${engagement.name}`,
			type: "engagement",
			title: "Audit engagement updated",
			description: `${engagement.engagement_title}`,
			timestamp: new Date(engagement.modified),
		})
	})

	// Add recent findings
	auditStore.findings.slice(0, 2).forEach((finding) => {
		activities.push({
			id: `finding-${finding.name}`,
			type: "finding",
			title: "New finding reported",
			description: `${finding.finding_title}`,
			timestamp: new Date(finding.creation),
		})
	})

	return activities.sort((a, b) => b.timestamp - a.timestamp).slice(0, 5)
})

const upcomingTasks = computed(() => {
	const tasks = []

	// Add upcoming tasks from findings with due dates
	auditStore.findings
		.filter((f) => f.target_completion_date)
		.sort(
			(a, b) =>
				new Date(a.target_completion_date) - new Date(b.target_completion_date),
		)
		.slice(0, 3)
		.forEach((finding) => {
			tasks.push({
				id: `finding-${finding.name}`,
				title: `Review finding: ${finding.finding_title}`,
				description: "Complete corrective action review",
				priority:
					finding.risk_rating === "Critical"
						? "high"
						: finding.risk_rating === "High"
							? "high"
							: "medium",
				dueDate: new Date(finding.target_completion_date),
				completed: false,
			})
		})

	return tasks
})

// Methods
const refreshData = async () => {
	loading.value = true
	try {
		// Refresh audit data
		await auditStore.fetchEngagements()
		await auditStore.fetchFindings()
		await dataStore.fetchDataPeriods()
	} finally {
		loading.value = false
	}
}

const initializeCharts = () => {
	if (auditStatusChartRef.value) {
		new ChartJS(auditStatusChartRef.value, {
			type: "pie",
			data: auditStatusData.value,
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: {
						position: "bottom",
					},
					title: {
						display: false,
					},
				},
			},
		})
	}

	if (riskDistributionChartRef.value) {
		new ChartJS(riskDistributionChartRef.value, {
			type: "bar",
			data: riskDistributionData.value,
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: {
						display: false,
					},
					title: {
						display: false,
					},
				},
				scales: {
					y: {
						beginAtZero: true,
					},
				},
			},
		})
	}
}

const getActivityIcon = (type) => {
	const icons = {
		engagement: FileTextIcon,
		finding: AlertTriangleIcon,
		report: BarChart3Icon,
	}
	return icons[type] || FileTextIcon
}

const getActivityIconBg = (type) => {
	const colors = {
		engagement: "bg-blue-500",
		finding: "bg-yellow-500",
		report: "bg-green-500",
	}
	return colors[type] || "bg-gray-500"
}

const getPriorityVariant = (priority) => {
	const variants = {
		low: "secondary",
		medium: "warning",
		high: "danger",
	}
	return variants[priority] || "secondary"
}

const toggleTask = (task) => {
	task.completed = !task.completed
	// In a real app, this would update the backend
}

const formatDate = (date) => {
	return new Date(date).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	})
}

// Lifecycle
onMounted(async () => {
	await refreshData()
	await nextTick()
	initializeCharts()
})
</script>