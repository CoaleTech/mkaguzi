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
        <Button @click="showCreateForm = true" :loading="saving">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Corrective Action
        </Button>
      </div>
    </div>

    <!-- Action Stats -->
    <ActionStats
      :stats="stats"
      :loading="loading"
      :show-details="true"
    />

    <!-- Action Filters -->
    <ActionFilters
      v-model="filters"
      @refresh="fetchActions"
      @export="exportActions"
      @create="showCreateForm = true"
    />

    <!-- Corrective Actions Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="p-6">
        <DataTable
          :columns="columns"
          :data="filteredActions"
          :loading="loading"
          :pagination="true"
          :sortable="true"
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
              {{ row.status || 'Draft' }}
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

    <!-- Corrective Action Form Modal -->
    <CorrectiveActionForm
      v-model:show="showCreateForm"
      :action="selectedAction"
      :mode="formMode"
      @saved="onActionSaved"
      @close="onFormClose"
    />
  </div>
</template>

<script setup>
import { DataTable } from "@/components/Common"
import ActionFilters from "@/components/actions/ActionFilters.vue"
import ActionStats from "@/components/actions/ActionStats.vue"
import CorrectiveActionForm from "@/components/actions/CorrectiveActionForm.vue"
import { useCorrectiveActionsStore } from "@/stores/correctiveActions"
import { Badge, Button } from "frappe-ui"
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
const store = useCorrectiveActionsStore()

// Reactive state
const showCreateForm = ref(false)
const selectedAction = ref(null)
const formMode = ref("create")

// Computed properties
const actions = computed(() => store.actions)
const filteredActions = computed(() => store.filteredActions)
const stats = computed(() => store.stats)
const loading = computed(() => store.loading)
const saving = computed(() => store.saving)
const filters = computed({
	get: () => ({
		search: store.searchQuery,
		...store.filters,
	}),
	set: (value) => {
		store.searchQuery = value.search || ""
		store.setFilters(value)
	},
})

// Legacy computed properties for backward compatibility
const totalActions = computed(() => stats.value.total)
const inProgressActions = computed(() => stats.value.inProgress)
const completedActions = computed(() => stats.value.completed)
const overdueActions = computed(() => stats.value.overdue)

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
const fetchActions = async () => {
	await store.fetchActions()
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
		Draft: "secondary",
		Approved: "info",
		"In Progress": "warning",
		"On Hold": "secondary",
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
	selectedAction.value = action
	formMode.value = "edit"
	showCreateForm.value = true
}

const deleteAction = async (action) => {
	if (confirm("Are you sure you want to delete this corrective action?")) {
		try {
			await store.deleteAction(action.name)
		} catch (error) {
			console.error("Error deleting action:", error)
		}
	}
}

const exportActions = () => {
	// Export logic will be implemented
	console.log("Exporting actions...")
}

const onActionSaved = () => {
	showCreateForm.value = false
	selectedAction.value = null
	formMode.value = "create"
}

const onFormClose = () => {
	showCreateForm.value = false
	selectedAction.value = null
	formMode.value = "create"
}

// Lifecycle
onMounted(async () => {
	await fetchActions()
})
</script>