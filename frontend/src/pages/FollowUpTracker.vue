<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Follow-up Tracker</h1>
        <p class="text-gray-600 mt-1">
          Track and manage follow-up activities on audit findings
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline" @click="exportTrackers">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button @click="createNewTracker">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Follow-up Tracker
        </Button>
      </div>
    </div>

    <!-- Summary Stats -->
    <TrackerStats :stats="stats" />

    <!-- Filters -->
    <TrackerFilters
      v-model:searchQuery="searchQuery"
      v-model:selectedStatus="selectedStatus"
      v-model:selectedFollowUpType="selectedFollowUpType"
      v-model:selectedFrequency="selectedFrequency"
      v-model:selectedProgress="selectedProgress"
    />

    <!-- Follow-up Trackers Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="p-6">
        <DataTable
          :columns="columns"
          :data="filteredTrackers"
          :loading="loading"
          :pagination="true"
          :sortable="true"
          :filterable="true"
          @row-click="onTrackerClick"
        >
          <!-- Status Column -->
          <template #column-status="{ row }">
            <Badge :variant="getStatusVariant(row.status)">
              {{ row.status || 'Active' }}
            </Badge>
          </template>

          <!-- Progress Column -->
          <template #column-current_status="{ row }">
            <div class="flex items-center space-x-2">
              <Badge :variant="getProgressVariant(row.current_status)">
                {{ row.current_status || 'On Track' }}
              </Badge>
              <span v-if="row.progress_rating" class="text-sm text-gray-600">
                {{ row.progress_rating }}/5
              </span>
            </div>
          </template>

          <!-- Due Date Column -->
          <template #column-next_due_date="{ row }">
            <div class="text-sm">
              <div :class="getDueDateClass(row.next_due_date)">
                {{ formatDate(row.next_due_date) }}
              </div>
              <div v-if="row.frequency" class="text-gray-500 text-xs">
                {{ row.frequency }}
              </div>
            </div>
          </template>

          <!-- Actions Column -->
          <template #column-actions="{ row }">
            <div class="flex items-center space-x-2">
              <Button variant="ghost" size="sm" @click="viewTracker(row)">
                <EyeIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="editTracker(row)">
                <EditIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="addFollowUpActivity(row)">
                <PlusIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                color="red"
                @click="deleteTracker(row)"
              >
                <TrashIcon class="h-4 w-4" />
              </Button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Follow-up Form Dialog -->
    <FollowUpForm
      v-model:show="showFormDialog"
      :tracker-data="selectedTracker"
      :is-edit-mode="isEditMode"
      @saved="handleTrackerSaved"
    />
  </div>
</template>

<script setup>
import { DataTable } from "@/components/Common"
import FollowUpForm from "@/components/followup/FollowUpForm.vue"
import TrackerFilters from "@/components/followup/TrackerFilters.vue"
import TrackerStats from "@/components/followup/TrackerStats.vue"
import { useFollowUpStore } from "@/stores/followup"
import { Badge, Button } from "frappe-ui"
import {
	DownloadIcon,
	EditIcon,
	EyeIcon,
	PlusIcon,
	TrashIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const followUpStore = useFollowUpStore()

// Reactive state
const showFormDialog = ref(false)
const isEditMode = ref(false)
const selectedTracker = ref(null)

// Store bindings
const loading = computed(() => followUpStore.loading)
const filteredTrackers = computed(() => followUpStore.filteredTrackers)
const stats = computed(() => followUpStore.stats)

const searchQuery = computed({
	get: () => followUpStore.searchQuery,
	set: (value) => (followUpStore.searchQuery = value),
})

const selectedStatus = computed({
	get: () => followUpStore.filters.status,
	set: (value) => (followUpStore.filters.status = value),
})

const selectedFollowUpType = computed({
	get: () => followUpStore.filters.followUpType,
	set: (value) => (followUpStore.filters.followUpType = value),
})

const selectedFrequency = computed({
	get: () => followUpStore.filters.frequency,
	set: (value) => (followUpStore.filters.frequency = value),
})

const selectedProgress = computed({
	get: () => followUpStore.filters.responsiblePerson,
	set: (value) => (followUpStore.filters.responsiblePerson = value),
})

const columns = [
	{ key: "tracker_id", label: "Tracker ID", sortable: true, width: "120px" },
	{ key: "finding_title", label: "Finding Title", sortable: true },
	{ key: "status", label: "Status", sortable: true, width: "100px" },
	{ key: "follow_up_type", label: "Type", sortable: true, width: "150px" },
	{
		key: "responsible_person",
		label: "Responsible",
		sortable: true,
		width: "120px",
	},
	{ key: "current_status", label: "Progress", sortable: true, width: "120px" },
	{ key: "next_due_date", label: "Next Due", sortable: true, width: "100px" },
	{
		key: "last_follow_up_date",
		label: "Last Follow-up",
		sortable: true,
		width: "120px",
	},
	{ key: "actions", label: "Actions", width: "140px" },
]

// Methods
const fetchTrackers = async () => {
	await followUpStore.fetchTrackers()
}

const getStatusVariant = (status) => {
	const variants = {
		Active: "success",
		Completed: "secondary",
		"On Hold": "warning",
		Cancelled: "danger",
	}
	return variants[status] || "secondary"
}

const getProgressVariant = (status) => {
	const variants = {
		"On Track": "success",
		"Behind Schedule": "warning",
		"At Risk": "danger",
		"Off Track": "danger",
		"Completed Successfully": "secondary",
	}
	return variants[status] || "secondary"
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

const onTrackerClick = (tracker) => {
	viewTracker(tracker)
}

const viewTracker = async (tracker) => {
	try {
		selectedTracker.value = await followUpStore.getTrackerDetails(tracker.name)
		isEditMode.value = true
		showFormDialog.value = true
	} catch (error) {
		console.error("Error fetching tracker details:", error)
	}
}

const editTracker = async (tracker) => {
	try {
		selectedTracker.value = await followUpStore.getTrackerDetails(tracker.name)
		isEditMode.value = true
		showFormDialog.value = true
	} catch (error) {
		console.error("Error fetching tracker details:", error)
	}
}

const addFollowUpActivity = async (tracker) => {
	try {
		selectedTracker.value = await followUpStore.getTrackerDetails(tracker.name)
		isEditMode.value = true
		showFormDialog.value = true
	} catch (error) {
		console.error("Error fetching tracker details:", error)
	}
}

const deleteTracker = async (tracker) => {
	if (confirm("Are you sure you want to delete this follow-up tracker?")) {
		try {
			await followUpStore.deleteTracker(tracker.name)
		} catch (error) {
			console.error("Error deleting tracker:", error)
		}
	}
}

const createNewTracker = () => {
	selectedTracker.value = null
	isEditMode.value = false
	showFormDialog.value = true
}

const handleTrackerSaved = async () => {
	showFormDialog.value = false
	await fetchTrackers()
}

const exportTrackers = () => {
	try {
		exporting.value = true

		// Generate CSV from trackers data
		const headers = ["ID", "Follow-up ID", "Finding", "Action Required", "Due Date", "Status", "Assigned To"]
		const rows = trackers.value.map((tracker) => [
			tracker.name,
			tracker.follow_up_id,
			tracker.finding_reference,
			tracker.action_required,
			tracker.target_completion_date,
			tracker.status,
			tracker.assigned_to,
		])

		const csvContent = [headers, ...rows].map((row) => row.join(",")).join("\n")
		const blob = new Blob([csvContent], { type: "text/csv" })
		const url = window.URL.createObjectURL(blob)
		const a = document.createElement("a")
		a.href = url
		a.download = `follow-up-trackers-${new Date().toISOString().split("T")[0]}.csv`
		a.click()
		window.URL.revokeObjectURL(url)
	} catch (error) {
		console.error("Error exporting trackers:", error)
		alert("Failed to export trackers: " + error.message)
	} finally {
		exporting.value = false
	}
}

// Lifecycle
onMounted(async () => {
	await fetchTrackers()
})
</script>