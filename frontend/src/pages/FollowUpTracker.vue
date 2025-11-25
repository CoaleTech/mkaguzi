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
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button @click="createNewTracker">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Follow-up Tracker
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
            <option value="Active">Active</option>
            <option value="Completed">Completed</option>
            <option value="On Hold">On Hold</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Follow-up Type</label>
          <select
            v-model="filters.followUpType"
            @change="applyFilters"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            <option value="Corrective Action Monitoring">Corrective Action Monitoring</option>
            <option value="Preventive Measure Verification">Preventive Measure Verification</option>
            <option value="Process Improvement Tracking">Process Improvement Tracking</option>
            <option value="Risk Mitigation Assessment">Risk Mitigation Assessment</option>
            <option value="Compliance Verification">Compliance Verification</option>
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

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <ActivityIcon class="h-6 w-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Active Trackers</p>
            <p class="text-2xl font-bold text-gray-900">{{ activeTrackersCount }}</p>
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
            <p class="text-2xl font-bold text-gray-900">{{ completedTrackersCount }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <AlertTriangleIcon class="h-6 w-6 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Overdue</p>
            <p class="text-2xl font-bold text-gray-900">{{ overdueTrackersCount }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-red-100 rounded-lg">
            <XCircleIcon class="h-6 w-6 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">At Risk</p>
            <p class="text-2xl font-bold text-gray-900">{{ atRiskTrackersCount }}</p>
          </div>
        </div>
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
	ActivityIcon,
	AlertTriangleIcon,
	CheckCircleIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	PlusIcon,
	TrashIcon,
	XCircleIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const auditStore = useAuditStore()

// Reactive state
const loading = ref(false)
const trackers = ref([])
const filters = ref({
	status: "",
	followUpType: "",
	responsiblePerson: "",
	dueDateRange: "",
})

// Computed properties
const filteredTrackers = computed(() => {
	let filtered = trackers.value

	if (filters.value.status) {
		filtered = filtered.filter((t) => t.status === filters.value.status)
	}

	if (filters.value.followUpType) {
		filtered = filtered.filter(
			(t) => t.follow_up_type === filters.value.followUpType,
		)
	}

	if (filters.value.responsiblePerson) {
		filtered = filtered.filter((t) =>
			t.responsible_person
				?.toLowerCase()
				.includes(filters.value.responsiblePerson.toLowerCase()),
		)
	}

	if (filters.value.dueDateRange) {
		const now = new Date()
		filtered = filtered.filter((t) => {
			if (!t.next_due_date) return false
			const dueDate = new Date(t.next_due_date)

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

const activeTrackersCount = computed(() => {
	return trackers.value.filter((t) => t.status === "Active").length
})

const completedTrackersCount = computed(() => {
	return trackers.value.filter((t) => t.status === "Completed").length
})

const overdueTrackersCount = computed(() => {
	const now = new Date()
	return trackers.value.filter((t) => {
		return (
			t.next_due_date &&
			new Date(t.next_due_date) < now &&
			t.status === "Active"
		)
	}).length
})

const atRiskTrackersCount = computed(() => {
	return trackers.value.filter(
		(t) => t.current_status === "At Risk" || t.current_status === "Off Track",
	).length
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
	loading.value = true
	try {
		const response = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Follow-up Tracker",
				fields: [
					"name",
					"tracker_id",
					"audit_finding",
					"finding_title",
					"status",
					"follow_up_type",
					"start_date",
					"next_due_date",
					"frequency",
					"responsible_person",
					"responsible_department",
					"last_follow_up_date",
					"current_status",
					"progress_rating",
					"creation",
					"modified",
				],
				limit_page_length: 1000,
				order_by: "creation desc",
			},
		}).fetch()
		trackers.value = response || []
	} catch (error) {
		console.error("Error loading follow-up trackers:", error)
		trackers.value = []
	} finally {
		loading.value = false
	}
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

const applyFilters = () => {
	// Filters are applied reactively through computed property
}

const onTrackerClick = (tracker) => {
	router.push(`/follow-up/${tracker.name}`)
}

const viewTracker = (tracker) => {
	router.push(`/follow-up/${tracker.name}`)
}

const editTracker = (tracker) => {
	router.push(`/follow-up/${tracker.name}/edit`)
}

const addFollowUpActivity = (tracker) => {
	router.push(`/follow-up/${tracker.name}/activity`)
}

const deleteTracker = (tracker) => {
	if (confirm("Are you sure you want to delete this follow-up tracker?")) {
		// Delete logic will be implemented
	}
}

const createNewTracker = () => {
	router.push("/follow-up/new")
}

// Lifecycle
onMounted(async () => {
	await fetchTrackers()
})
</script>