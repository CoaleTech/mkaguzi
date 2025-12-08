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
        <AskAIButton
          page-component="Dashboard"
          :contextData="getDashboardContext()"
          button-text="Ask AI"
          variant="solid"
          theme="purple"
          size="sm"
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

    <!-- Enhanced KPI Cards -->
    <AuditKPICards
      :findings="auditStore.findings"
      :corrective-actions="auditStore.correctiveActions"
      :previous-findings="previousMonthFindings"
    />

    <!-- Advanced Analytics Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <FindingsStatusChart
        :findings="auditStore.findings"
        :loading="loading"
        @refresh="refreshData"
        @export="exportChart('findings-status')"
      />
      <FindingsRiskChart
        :findings="auditStore.findings"
        :loading="loading"
        @refresh="refreshData"
        @export="exportChart('findings-risk')"
      />
    </div>

    <!-- Timeline and Progress Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <FindingsTimelineChart
        :findings="auditStore.findings"
        :loading="loading"
        @refresh="refreshData"
        @export="exportChart('findings-timeline')"
      />
      <CorrectiveActionsChart
        :corrective-actions="auditStore.correctiveActions"
        :loading="loading"
        @refresh="refreshData"
        @export="exportChart('corrective-actions')"
      />
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
import AuditKPICards from "@/components/Charts/AuditKPICards.vue"
import CorrectiveActionsChart from "@/components/Charts/CorrectiveActionsChart.vue"
import FindingsRiskChart from "@/components/Charts/FindingsRiskChart.vue"
import FindingsStatusChart from "@/components/Charts/FindingsStatusChart.vue"
import FindingsTimelineChart from "@/components/Charts/FindingsTimelineChart.vue"
import AskAIButton from "@/components/AskAIButton.vue"
import { useAuditStore } from "@/stores/audit"
import { useDataStore } from "@/stores/data"
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
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const auditStore = useAuditStore()
const dataStore = useDataStore()

// Reactive state
const loading = ref(false)
const selectedPeriod = ref("month")

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

// Previous month findings for comparison (mock data - in real app this would come from API)
const previousMonthFindings = computed(() => {
	// This would typically be fetched from the API
	// For now, return a mock array with slightly different numbers
	const currentCount = auditStore.findings.length
	const previousCount = Math.max(
		0,
		currentCount - Math.floor(currentCount * 0.1),
	)
	return Array(previousCount)
		.fill({})
		.map((_, i) => ({ name: `prev-${i}` }))
})

// Get dashboard context for AI
const getDashboardContext = () => {
	return {
		total_entities: stats.value.activeEngagements,
		active_audits: stats.value.activeEngagements,
		open_findings: stats.value.openFindings,
		overdue_tasks: upcomingTasks.value.filter(task => task.priority === 'high').length,
		compliance_score: 85, // Mock compliance score
		recent_activities: recentActivities.value.slice(0, 5).map(activity => ({
			type: activity.type,
			description: activity.description,
			date: activity.timestamp
		}))
	}
}

// Methods
const refreshData = async () => {
	loading.value = true
	try {
		// Refresh audit data
		await auditStore.fetchEngagements()
		await auditStore.fetchFindings()
		await auditStore.fetchCorrectiveActions()
		await dataStore.fetchDataPeriods()
	} finally {
		loading.value = false
	}
}

const exportChart = (chartType) => {
	// In a real implementation, this would export the chart as PNG/PDF
	console.log(`Exporting ${chartType} chart`)
	// You could use html2canvas or similar library to export charts
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
})
</script>