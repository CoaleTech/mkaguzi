<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Corrective Actions</h1>
        <p class="text-gray-600 mt-1">
          Track and manage corrective action plans and remediation activities
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button @click="createNewAction">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Corrective Action
        </Button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <ClipboardListIcon class="h-6 w-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Actions</p>
            <p class="text-2xl font-bold text-gray-900">{{ totalActions }}</p>
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
            <p class="text-2xl font-bold text-gray-900">{{ inProgressActions }}</p>
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
            <p class="text-2xl font-bold text-gray-900">{{ completedActions }}</p>
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
            <p class="text-2xl font-bold text-gray-900">{{ overdueActions }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Corrective Actions Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="p-6">
        <DataTable
          :columns="columns"
          :data="correctiveActions"
          :loading="loading"
          :pagination="true"
          :sortable="true"
          :filterable="true"
          @row-click="onActionClick"
        >
          <!-- Priority Column -->
          <template #column-priority="{ row }">
            <Badge :variant="getPriorityVariant(row.priority)">
              {{ row.priority || 'Medium' }}
            </Badge>
          </template>

          <!-- Status Column -->
          <template #column-status="{ row }">
            <Badge :variant="getStatusVariant(row.status)">
              {{ row.status || 'Open' }}
            </Badge>
          </template>

          <!-- Progress Column -->
          <template #column-overall_progress="{ row }">
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

          <!-- Actions Column -->
          <template #column-actions="{ row }">
            <div class="flex items-center space-x-2">
              <Button variant="ghost" size="sm" @click="viewAction(row)">
                <EyeIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="editAction(row)">
                <EditIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                color="red"
                @click="deleteAction(row)"
              >
                <TrashIcon class="h-4 w-4" />
              </Button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>
  </div>
</template>

<script setup>
import { DataTable } from "@/components/Common"
import { useAuditStore } from "@/stores/audit"
import { Badge, Button } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	AlertTriangleIcon,
	CheckCircleIcon,
	ClipboardListIcon,
	ClockIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	PlusIcon,
	TrashIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const auditStore = useAuditStore()

// Reactive state
const loading = ref(false)

// Computed properties
const correctiveActions = computed(() => auditStore.correctiveActionPlans)

const totalActions = computed(() => correctiveActions.value.length)

const inProgressActions = computed(
	() =>
		correctiveActions.value.filter((action) => action.status === "In Progress")
			.length,
)

const completedActions = computed(
	() =>
		correctiveActions.value.filter((action) => action.status === "Completed")
			.length,
)

const overdueActions = computed(() => {
	const now = new Date()
	return correctiveActions.value.filter((action) => {
		if (!action.target_completion_date || action.status === "Completed")
			return false
		return new Date(action.target_completion_date) < now
	}).length
})

const columns = [
	{ key: "plan_id", label: "Action ID", sortable: true, width: "120px" },
	{ key: "title", label: "Action Title", sortable: true },
	{ key: "priority", label: "Priority", sortable: true, width: "100px" },
	{ key: "status", label: "Status", sortable: true, width: "120px" },
	{
		key: "overall_progress",
		label: "Progress",
		sortable: true,
		width: "150px",
	},
	{
		key: "audit_finding",
		label: "Related Finding",
		sortable: true,
		width: "150px",
	},
	{
		key: "responsible_person",
		label: "Responsible Person",
		sortable: true,
		width: "150px",
	},
	{
		key: "responsible_department",
		label: "Department",
		sortable: true,
		width: "120px",
	},
	{
		key: "target_completion_date",
		label: "Due Date",
		sortable: true,
		width: "100px",
	},
	{ key: "creation", label: "Created", sortable: true, width: "100px" },
	{ key: "actions", label: "Actions", width: "120px" },
]

// Methods
const fetchCorrectiveActions = async () => {
	loading.value = true
	try {
		await auditStore.fetchCorrectiveActionPlans()
	} catch (error) {
		console.error("Error loading corrective actions:", error)
	} finally {
		loading.value = false
	}
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

const getStatusVariant = (status) => {
	const variants = {
		Open: "danger",
		"In Progress": "warning",
		"Pending Review": "info",
		Completed: "success",
		Cancelled: "secondary",
	}
	return variants[status] || "secondary"
}

const onActionClick = (action) => {
	router.push(`/corrective-actions/${action.name}`)
}

const viewAction = (action) => {
	router.push(`/corrective-actions/${action.name}`)
}

const editAction = (action) => {
	router.push(`/corrective-actions/${action.name}/edit`)
}

const deleteAction = (action) => {
	if (confirm("Are you sure you want to delete this corrective action?")) {
		// Delete logic will be implemented
		console.log("Deleting action:", action.name)
	}
}

const createNewAction = () => {
	router.push("/corrective-actions/new")
}

// Lifecycle
onMounted(async () => {
	await fetchCorrectiveActions()
})
</script>