<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit Findings</h1>
        <p class="text-gray-600 mt-1">
          Review and manage audit findings and observations
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline" @click="exportFindings">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button variant="solid" theme="blue" @click="showFormDialog = true">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Finding
        </Button>
      </div>
    </div>

    <!-- Stats Dashboard -->
    <FindingsStats :stats="findingsStats" />

    <!-- Filters -->
    <FindingsFilters
      v-model="filters"
      :engagement-options="engagementOptions"
      :user-options="userOptions"
      @filter-change="handleFilterChange"
    />

    <!-- Findings Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="p-6">
        <DataTable
          :columns="columns"
          :data="filteredFindings"
          :loading="loading"
          :pagination="true"
          :sortable="true"
          :filterable="false"
          @row-click="onFindingClick"
        >
          <!-- Finding ID with link -->
          <template #column-finding_id="{ row }">
            <span class="text-blue-600 font-medium cursor-pointer hover:underline" @click.stop="viewFinding(row)">
              {{ row.finding_id }}
            </span>
          </template>

          <!-- Risk Rating Column -->
          <template #column-risk_rating="{ row }">
            <Badge :theme="getSeverityTheme(row.risk_rating)" variant="subtle">
              {{ row.risk_rating || 'Medium' }}
            </Badge>
          </template>

          <!-- Status Column -->
          <template #column-finding_status="{ row }">
            <Badge :theme="getStatusTheme(row.finding_status)" variant="subtle">
              {{ row.finding_status || 'Open' }}
            </Badge>
          </template>

          <!-- Due Date with overdue indicator -->
          <template #column-target_completion_date="{ row }">
            <div class="flex items-center">
              <span :class="isOverdue(row.target_completion_date) ? 'text-red-600 font-medium' : 'text-gray-600'">
                {{ formatDate(row.target_completion_date) }}
              </span>
              <AlertCircleIcon
                v-if="isOverdue(row.target_completion_date) && row.finding_status !== 'Closed'"
                class="h-4 w-4 text-red-500 ml-1"
              />
            </div>
          </template>

          <!-- Actions Column -->
          <template #column-actions="{ row }">
            <div class="flex items-center space-x-2">
              <Button variant="ghost" size="sm" @click.stop="viewFinding(row)" title="View">
                <EyeIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click.stop="editFinding(row)" title="Edit">
                <EditIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click.stop="deleteFinding(row)"
                title="Delete"
              >
                <TrashIcon class="h-4 w-4 text-red-500" />
              </Button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Finding Form Dialog -->
    <AuditFindingForm
      v-model="showFormDialog"
      :finding="selectedFinding"
      @saved="handleFindingSaved"
      @close="handleFormClose"
    />
  </div>
</template>

<script setup>
import { DataTable } from "@/components/Common"
import AuditFindingForm from "@/components/findings/AuditFindingForm.vue"
import FindingsFilters from "@/components/findings/FindingsFilters.vue"
import FindingsStats from "@/components/findings/FindingsStats.vue"
import { useAuditStore } from "@/stores/audit"
import { Badge, Button } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	AlertCircleIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	PlusIcon,
	TrashIcon,
} from "lucide-vue-next"
import { computed, onMounted, reactive, ref, watch } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const auditStore = useAuditStore()

// Reactive state
const loading = ref(false)
const showFormDialog = ref(false)
const selectedFinding = ref(null)
const filters = reactive({
	search: "",
	status: "",
	category: "",
	riskRating: "",
	engagement: "",
	dateFrom: "",
	dateTo: "",
	responsiblePerson: "",
	followUpRequired: "",
	overdueOnly: false,
	repeatFindingsOnly: false,
	includeInReport: false,
})

// Options for filters
const engagementOptions = ref([])
const userOptions = ref([])

// Computed properties
const findings = computed(() => auditStore.findings)

// Filtered findings based on active filters
const filteredFindings = computed(() => {
	let result = [...findings.value]

	// Search filter
	if (filters.search) {
		const search = filters.search.toLowerCase()
		result = result.filter(
			(f) =>
				f.finding_id?.toLowerCase().includes(search) ||
				f.finding_title?.toLowerCase().includes(search) ||
				f.condition?.toLowerCase().includes(search),
		)
	}

	// Status filter
	if (filters.status) {
		result = result.filter((f) => f.finding_status === filters.status)
	}

	// Category filter
	if (filters.category) {
		result = result.filter((f) => f.finding_category === filters.category)
	}

	// Risk rating filter
	if (filters.riskRating) {
		result = result.filter((f) => f.risk_rating === filters.riskRating)
	}

	// Engagement filter
	if (filters.engagement) {
		result = result.filter((f) => f.engagement_reference === filters.engagement)
	}

	// Overdue filter
	if (filters.overdueOnly) {
		result = result.filter(
			(f) =>
				isOverdue(f.target_completion_date) && f.finding_status !== "Closed",
		)
	}

	// Repeat findings filter
	if (filters.repeatFindingsOnly) {
		result = result.filter((f) => f.repeat_finding)
	}

	return result
})

// Stats calculation
const findingsStats = computed(() => {
	const all = findings.value
	const today = new Date()
	const thisMonth = new Date(today.getFullYear(), today.getMonth(), 1)

	const open = all.filter((f) => f.finding_status === "Open")
	const inProgress = all.filter(
		(f) => f.finding_status === "Action in Progress",
	)
	const pendingVerification = all.filter(
		(f) => f.finding_status === "Pending Verification",
	)
	const closed = all.filter((f) => f.finding_status === "Closed")

	// Overdue calculation
	const overdue = all.filter(
		(f) => f.finding_status !== "Closed" && isOverdue(f.target_completion_date),
	)

	// This month
	const createdThisMonth = all.filter((f) => new Date(f.creation) >= thisMonth)

	// By severity
	const bySeverity = {
		critical: open.filter((f) => f.risk_rating === "Critical").length,
		high: open.filter((f) => f.risk_rating === "High").length,
		medium: open.filter((f) => f.risk_rating === "Medium").length,
		low: open.filter((f) => f.risk_rating === "Low").length,
	}

	// Aging calculation for open findings
	const aging = calculateAging(all.filter((f) => f.finding_status !== "Closed"))

	return {
		total: all.length,
		thisMonth: createdThisMonth.length,
		open: open.length,
		overdue: overdue.length,
		inProgress: inProgress.length,
		pendingVerification: pendingVerification.length,
		closed: closed.length,
		closureRate:
			all.length > 0 ? Math.round((closed.length / all.length) * 100) : 0,
		bySeverity,
		aging,
	}
})

const columns = [
	{ key: "finding_id", label: "Finding ID", sortable: true, width: "120px" },
	{ key: "finding_title", label: "Finding Title", sortable: true },
	{ key: "risk_rating", label: "Risk Rating", sortable: true, width: "100px" },
	{ key: "finding_status", label: "Status", sortable: true, width: "140px" },
	{
		key: "engagement_reference",
		label: "Engagement",
		sortable: true,
		width: "150px",
	},
	{
		key: "responsible_person",
		label: "Responsible",
		sortable: true,
		width: "150px",
	},
	{
		key: "target_completion_date",
		label: "Due Date",
		sortable: true,
		width: "120px",
	},
	{ key: "actions", label: "Actions", width: "100px" },
]

// Helper functions
const calculateAging = (openFindings) => {
	const today = new Date()
	const aging = { days0to30: 0, days31to60: 0, days61to90: 0, days90plus: 0 }

	openFindings.forEach((f) => {
		const created = new Date(f.creation)
		const days = Math.floor((today - created) / (1000 * 60 * 60 * 24))

		if (days <= 30) aging.days0to30++
		else if (days <= 60) aging.days31to60++
		else if (days <= 90) aging.days61to90++
		else aging.days90plus++
	})

	return aging
}

const isOverdue = (dateStr) => {
	if (!dateStr) return false
	return new Date(dateStr) < new Date()
}

const formatDate = (dateStr) => {
	if (!dateStr) return "-"
	return new Date(dateStr).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	})
}

// Methods
const fetchFindings = async () => {
	loading.value = true
	try {
		const response = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Audit Finding",
				fields: [
					"name",
					"finding_id",
					"finding_title",
					"finding_status",
					"finding_category",
					"risk_rating",
					"engagement_reference",
					"responsible_person",
					"responsible_department",
					"target_completion_date",
					"creation",
					"modified",
					"condition",
					"effect",
					"recommendation",
					"repeat_finding",
					"follow_up_required",
				],
				limit_page_length: 1000,
				order_by: "creation desc",
			},
		}).fetch()

		auditStore.setFindings(response || [])
	} catch (error) {
		console.error("Error loading findings:", error)
		auditStore.setFindings([])
	} finally {
		loading.value = false
	}
}

const fetchOptions = async () => {
	// Fetch engagement options
	try {
		const engagements = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Audit Engagement",
				fields: ["name", "engagement_title"],
				limit_page_length: 500,
			},
		}).fetch()
		engagementOptions.value = (engagements || []).map((e) => ({
			label: e.engagement_title || e.name,
			value: e.name,
		}))
	} catch (error) {
		console.error("Error loading engagements:", error)
	}

	// Fetch user options
	try {
		const users = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "User",
				fields: ["name", "full_name"],
				filters: { enabled: 1 },
				limit_page_length: 500,
			},
		}).fetch()
		userOptions.value = (users || []).map((u) => ({
			label: u.full_name || u.name,
			value: u.name,
		}))
	} catch (error) {
		console.error("Error loading users:", error)
	}
}

const getSeverityTheme = (severity) => {
	const themes = {
		Critical: "red",
		High: "orange",
		Medium: "yellow",
		Low: "green",
	}
	return themes[severity] || "gray"
}

const getStatusTheme = (status) => {
	const themes = {
		Open: "red",
		"Action in Progress": "yellow",
		"Pending Verification": "blue",
		Closed: "green",
		"Accepted as Risk": "gray",
		"Management Override": "gray",
	}
	return themes[status] || "gray"
}

const handleFilterChange = (newFilters) => {
	Object.assign(filters, newFilters)
}

const onFindingClick = (finding) => {
	router.push(`/findings/${finding.name}`)
}

const viewFinding = (finding) => {
	router.push(`/findings/${finding.name}`)
}

const editFinding = (finding) => {
	selectedFinding.value = finding
	showFormDialog.value = true
}

const deleteFinding = (finding) => {
	if (confirm("Are you sure you want to delete this finding?")) {
		// Delete logic will be implemented
	}
}

const exportFindings = () => {
	// Export logic will be implemented
	console.log("Exporting findings...")
}

const handleFindingSaved = async (data) => {
	await fetchFindings()
	showFormDialog.value = false
	selectedFinding.value = null
}

const handleFormClose = () => {
	selectedFinding.value = null
}

// Lifecycle
onMounted(async () => {
	await Promise.all([fetchFindings(), fetchOptions()])
})
</script>