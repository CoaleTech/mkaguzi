<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Corrective Action Plans</h1>
        <p class="text-gray-600 mt-1">
          Manage corrective action plans for audit findings
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button @click="createNewPlan">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Action Plan
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filters.status"
            @change="applyFilters"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="Draft">Draft</option>
            <option value="Approved">Approved</option>
            <option value="In Progress">In Progress</option>
            <option value="On Hold">On Hold</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
          <select
            v-model="filters.priority"
            @change="applyFilters"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Responsible Person</label>
          <input
            v-model="filters.responsiblePerson"
            @input="applyFilters"
            type="text"
            placeholder="Search by person..."
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Due Date Range</label>
          <select
            v-model="filters.dueDateRange"
            @change="applyFilters"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Dates</option>
            <option value="overdue">Overdue</option>
            <option value="this_week">This Week</option>
            <option value="this_month">This Month</option>
            <option value="next_month">Next Month</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Action Plans Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="p-6">
        <DataTable
          :columns="columns"
          :data="filteredPlans"
          :loading="loading"
          :pagination="true"
          :sortable="true"
          :filterable="true"
          @row-click="onPlanClick"
        >
          <!-- Status Column -->
          <template #column-status="{ row }">
            <Badge :variant="getStatusVariant(row.status)">
              {{ row.status || 'Draft' }}
            </Badge>
          </template>

          <!-- Priority Column -->
          <template #column-priority="{ row }">
            <Badge :variant="getPriorityVariant(row.priority)">
              {{ row.priority || 'Medium' }}
            </Badge>
          </template>

          <!-- Progress Column -->
          <template #column-completion_percentage="{ row }">
            <div class="flex items-center space-x-2">
              <div class="w-20 bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-600 h-2 rounded-full"
                  :style="{ width: `${row.completion_percentage || 0}%` }"
                ></div>
              </div>
              <span class="text-sm text-gray-600">{{ row.completion_percentage || 0 }}%</span>
            </div>
          </template>

          <!-- Due Date Column -->
          <template #column-target_completion_date="{ row }">
            <div :class="getDueDateClass(row.target_completion_date)">
              {{ formatDate(row.target_completion_date) }}
            </div>
          </template>

          <!-- Actions Column -->
          <template #column-actions="{ row }">
            <div class="flex items-center space-x-2">
              <Button variant="ghost" size="sm" @click="viewPlan(row)">
                <EyeIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="editPlan(row)">
                <EditIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="addMilestone(row)">
                <PlusIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                color="red"
                @click="deletePlan(row)"
              >
                <TrashIcon class="h-4 w-4" />
              </Button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <FileTextIcon class="h-6 w-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Plans</p>
            <p class="text-2xl font-bold text-gray-900">{{ plans.value.length }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <CheckCircleIcon class="h-6 w-6 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Completed</p>
            <p class="text-2xl font-bold text-gray-900">{{ completedPlansCount }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <ClockIcon class="h-6 w-6 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">In Progress</p>
            <p class="text-2xl font-bold text-gray-900">{{ inProgressPlansCount }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-red-100 rounded-lg">
            <AlertTriangleIcon class="h-6 w-6 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Overdue</p>
            <p class="text-2xl font-bold text-gray-900">{{ overduePlansCount }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { DataTable } from "@/components/Common"
import { Badge, Button } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	AlertTriangleIcon,
	CheckCircleIcon,
	ClockIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	FileTextIcon,
	PlusIcon,
	TrashIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

// Reactive state
const loading = ref(false)
const plans = ref([])
const filters = ref({
	status: "",
	priority: "",
	responsiblePerson: "",
	dueDateRange: "",
})

// Computed properties
const filteredPlans = computed(() => {
	let filtered = plans.value

	if (filters.value.status) {
		filtered = filtered.filter((p) => p.status === filters.value.status)
	}

	if (filters.value.priority) {
		filtered = filtered.filter((p) => p.priority === filters.value.priority)
	}

	if (filters.value.responsiblePerson) {
		filtered = filtered.filter((p) =>
			p.responsible_person
				?.toLowerCase()
				.includes(filters.value.responsiblePerson.toLowerCase()),
		)
	}

	if (filters.value.dueDateRange) {
		const now = new Date()
		filtered = filtered.filter((p) => {
			if (!p.target_completion_date) return false
			const dueDate = new Date(p.target_completion_date)

			switch (filters.value.dueDateRange) {
				case "overdue":
					return dueDate < now
				case "this_week":
					const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
					return dueDate >= now && dueDate <= weekFromNow
				case "this_month":
					const monthFromNow = new Date(
						now.getFullYear(),
						now.getMonth() + 1,
						now.getDate(),
					)
					return dueDate >= now && dueDate <= monthFromNow
				case "next_month":
					const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1)
					const monthAfterNext = new Date(
						now.getFullYear(),
						now.getMonth() + 2,
						1,
					)
					return dueDate >= nextMonth && dueDate < monthAfterNext
				default:
					return true
			}
		})
	}

	return filtered
})

const completedPlansCount = computed(() => {
	return plans.value.filter((p) => p.status === "Completed").length
})

const inProgressPlansCount = computed(() => {
	return plans.value.filter((p) => p.status === "In Progress").length
})

const overduePlansCount = computed(() => {
	const now = new Date()
	return plans.value.filter((p) => {
		return (
			p.target_completion_date &&
			new Date(p.target_completion_date) < now &&
			p.status !== "Completed" &&
			p.status !== "Cancelled"
		)
	}).length
})

const columns = [
	{ key: "plan_id", label: "Plan ID", sortable: true, width: "120px" },
	{ key: "title", label: "Title", sortable: true },
	{ key: "status", label: "Status", sortable: true, width: "100px" },
	{ key: "priority", label: "Priority", sortable: true, width: "80px" },
	{
		key: "responsible_person",
		label: "Responsible",
		sortable: true,
		width: "120px",
	},
	{
		key: "completion_percentage",
		label: "Progress",
		sortable: true,
		width: "120px",
	},
	{
		key: "target_completion_date",
		label: "Due Date",
		sortable: true,
		width: "100px",
	},
	{ key: "actions", label: "Actions", width: "140px" },
]

// Methods
const fetchPlans = async () => {
	loading.value = true
	try {
		const response = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Corrective Action Plan",
				fields: [
					"name",
					"plan_id",
					"audit_finding",
					"title",
					"status",
					"priority",
					"start_date",
					"target_completion_date",
					"actual_completion_date",
					"responsible_person",
					"responsible_department",
					"overall_progress",
					"completion_percentage",
					"last_progress_update",
					"creation",
					"modified",
				],
				limit_page_length: 1000,
				order_by: "creation desc",
			},
		}).fetch()
		plans.value = response || []
	} catch (error) {
		console.error("Error loading corrective action plans:", error)
		plans.value = []
	} finally {
		loading.value = false
	}
}

const getStatusVariant = (status) => {
	const variants = {
		Draft: "secondary",
		Approved: "info",
		"In Progress": "warning",
		"On Hold": "secondary",
		Completed: "success",
		Cancelled: "danger",
	}
	return variants[status] || "secondary"
}

const getPriorityVariant = (priority) => {
	const variants = {
		Critical: "danger",
		High: "danger",
		Medium: "warning",
		Low: "success",
	}
	return variants[priority] || "secondary"
}

const getDueDateClass = (date) => {
	if (!date) return "text-gray-900"
	const now = new Date()
	const dueDate = new Date(date)
	const diffTime = dueDate - now
	const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

	if (diffDays < 0) return "text-red-600 font-medium"
	if (diffDays <= 7) return "text-yellow-600 font-medium"
	return "text-gray-900"
}

const formatDate = (date) => {
	if (!date) return "Not set"
	return new Date(date).toLocaleDateString()
}

const applyFilters = () => {
	// Filters are applied reactively through computed property
}

const onPlanClick = (plan) => {
	router.push(`/corrective-actions/${plan.name}`)
}

const viewPlan = (plan) => {
	router.push(`/corrective-actions/${plan.name}`)
}

const editPlan = (plan) => {
	router.push(`/corrective-actions/${plan.name}/edit`)
}

const addMilestone = (plan) => {
	router.push(`/corrective-actions/${plan.name}/milestone`)
}

const deletePlan = (plan) => {
	if (confirm("Are you sure you want to delete this corrective action plan?")) {
		// Delete logic will be implemented
	}
}

const createNewPlan = () => {
	router.push("/corrective-actions/new")
}

// Lifecycle
onMounted(async () => {
	await fetchPlans()
})
</script>