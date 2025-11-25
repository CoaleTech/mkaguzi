<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit Engagements</h1>
        <p class="text-gray-600 mt-1">
          Manage and track audit engagements
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button @click="createNewEngagement">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Engagement
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Input
          v-model="filters.search"
          placeholder="Search engagements..."
          class="w-full"
        />
        <Select
          v-model="filters.status"
          :options="statusOptions"
          placeholder="All Status"
        />
        <Select
          v-model="filters.type"
          :options="typeOptions"
          placeholder="All Types"
        />
        <Select
          v-model="filters.auditor"
          :options="auditorOptions"
          placeholder="All Auditors"
        />
      </div>
    </div>

    <!-- Engagements Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="p-6">
        <DataTable
          :columns="columns"
          :data="filteredEngagements"
          :loading="loading"
          :pagination="true"
          :sortable="true"
          @row-click="onEngagementClick"
        >
          <!-- Status Column -->
          <template #column-status="{ row }">
            <Badge :variant="getStatusVariant(row.status)">
              {{ getStatusLabel(row.status) }}
            </Badge>
          </template>

          <!-- Progress Column -->
          <template #column-progress="{ row }">
            <div class="flex items-center space-x-2">
              <div class="w-20 bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-600 h-2 rounded-full"
                  :style="{ width: `${calculateProgress(row)}%` }"
                ></div>
              </div>
              <span class="text-sm text-gray-600">{{ calculateProgress(row) }}%</span>
            </div>
          </template>

          <!-- Actions Column -->
          <template #column-actions="{ row }">
            <div class="flex items-center space-x-2">
              <Button variant="ghost" size="sm" @click="viewEngagement(row)">
                <EyeIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="editEngagement(row)">
                <EditIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                color="red"
                @click="deleteEngagement(row)"
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
import { Badge, Button, Input, Select } from "frappe-ui"
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
const auditStore = useAuditStore()

// Reactive state
const loading = ref(false)
const filters = ref({
	search: "",
	status: "",
	type: "",
	auditor: "",
})

// Computed properties
const engagements = computed(() => auditStore.engagements)

const filteredEngagements = computed(() => {
	let filtered = engagements.value

	if (filters.value.search) {
		filtered = filtered.filter(
			(engagement) =>
				engagement.engagement_title
					?.toLowerCase()
					.includes(filters.value.search.toLowerCase()) ||
				engagement.engagement_id
					?.toLowerCase()
					.includes(filters.value.search.toLowerCase()),
		)
	}

	if (filters.value.status) {
		filtered = filtered.filter(
			(engagement) => engagement.status === filters.value.status,
		)
	}

	if (filters.value.type) {
		filtered = filtered.filter(
			(engagement) => engagement.audit_type === filters.value.type,
		)
	}

	return filtered
})

const columns = [
	{ key: "engagement_id", label: "Engagement ID", sortable: true },
	{ key: "engagement_title", label: "Engagement Title", sortable: true },
	{ key: "audit_type", label: "Type", sortable: true },
	{ key: "status", label: "Status", sortable: true },
	{ key: "lead_auditor", label: "Lead Auditor", sortable: true },
	{ key: "period_start", label: "Start Date", sortable: true },
	{ key: "period_end", label: "End Date", sortable: true },
	{ key: "progress", label: "Progress", sortable: true },
	{ key: "actions", label: "Actions", width: "120px" },
]

const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Planning", value: "Planning" },
	{ label: "Fieldwork", value: "Fieldwork" },
	{ label: "Reporting", value: "Reporting" },
	{ label: "Management Review", value: "Management Review" },
	{ label: "Quality Review", value: "Quality Review" },
	{ label: "Finalized", value: "Finalized" },
	{ label: "Issued", value: "Issued" },
]

const typeOptions = [
	{ label: "All Types", value: "" },
	{ label: "Financial", value: "Financial" },
	{ label: "Operational", value: "Operational" },
	{ label: "Compliance", value: "Compliance" },
	{ label: "IT", value: "IT" },
	{ label: "Integrated", value: "Integrated" },
	{ label: "Special Investigation", value: "Special Investigation" },
	{ label: "Follow-up", value: "Follow-up" },
	{ label: "Advisory", value: "Advisory" },
]

const auditorOptions = computed(() => {
	const auditors = new Set()
	engagements.value.forEach((engagement) => {
		if (engagement.lead_auditor) {
			auditors.add(engagement.lead_auditor)
		}
	})

	return [
		{ label: "All Auditors", value: "" },
		...Array.from(auditors).map((auditor) => ({
			label: auditor,
			value: auditor,
		})),
	]
})

// Methods
const getStatusVariant = (status) => {
	const variants = {
		Planning: "secondary",
		Fieldwork: "warning",
		Reporting: "primary",
		"Management Review": "info",
		"Quality Review": "info",
		Finalized: "success",
		Issued: "success",
	}
	return variants[status] || "secondary"
}

const getStatusLabel = (status) => {
	return status || "Planning"
}

const calculateProgress = (engagement) => {
	// Calculate progress based on engagement timeline
	const now = new Date()
	const start = engagement.planning_start
		? new Date(engagement.planning_start)
		: null
	const end = engagement.actual_completion_date
		? new Date(engagement.actual_completion_date)
		: engagement.reporting_end
			? new Date(engagement.reporting_end)
			: engagement.fieldwork_end
				? new Date(engagement.fieldwork_end)
				: null

	if (!start || !end) return 0

	if (now < start) return 0
	if (now > end) return 100

	const total = end - start
	const elapsed = now - start
	return Math.round((elapsed / total) * 100)
}

const onEngagementClick = (engagement) => {
	router.push(`/engagements/${engagement.name}`)
}

const viewEngagement = (engagement) => {
	router.push(`/engagements/${engagement.name}`)
}

const editEngagement = (engagement) => {
	router.push(`/engagements/${engagement.name}/edit`)
}

const deleteEngagement = (engagement) => {
	if (confirm("Are you sure you want to delete this engagement?")) {
		// Delete logic will be implemented
	}
}

const createNewEngagement = () => {
	router.push("/engagements/new")
}

// Lifecycle
onMounted(async () => {
	loading.value = true
	try {
		await auditStore.fetchEngagements()
	} catch (error) {
		console.error("Error loading engagements:", error)
	} finally {
		loading.value = false
	}
})
</script>