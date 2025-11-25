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
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button @click="createNewFinding">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Finding
        </Button>
      </div>
    </div>

    <!-- Findings Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="p-6">
        <DataTable
          :columns="columns"
          :data="findings"
          :loading="loading"
          :pagination="true"
          :sortable="true"
          :filterable="true"
          @row-click="onFindingClick"
        >
          <!-- Severity Column -->
          <template #column-risk_rating="{ row }">
            <Badge :variant="getSeverityVariant(row.risk_rating)">
              {{ row.risk_rating || 'Medium' }}
            </Badge>
          </template>

          <!-- Status Column -->
          <template #column-finding_status="{ row }">
            <Badge :variant="getStatusVariant(row.finding_status)">
              {{ row.finding_status || 'Open' }}
            </Badge>
          </template>

          <!-- Actions Column -->
          <template #column-actions="{ row }">
            <div class="flex items-center space-x-2">
              <Button variant="ghost" size="sm" @click="viewFinding(row)">
                <EyeIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="editFinding(row)">
                <EditIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                color="red"
                @click="deleteFinding(row)"
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
const findings = computed(() => auditStore.findings)

const columns = [
	{ key: "finding_id", label: "Finding ID", sortable: true, width: "120px" },
	{ key: "finding_title", label: "Finding Title", sortable: true },
	{ key: "risk_rating", label: "Risk Rating", sortable: true, width: "100px" },
	{ key: "finding_status", label: "Status", sortable: true, width: "120px" },
	{
		key: "engagement_reference",
		label: "Engagement",
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

const getSeverityVariant = (severity) => {
	const variants = {
		Critical: "danger",
		High: "danger",
		Medium: "warning",
		Low: "success",
	}
	return variants[severity] || "secondary"
}

const getStatusVariant = (status) => {
	const variants = {
		Open: "danger",
		"Action in Progress": "warning",
		"Pending Verification": "info",
		Closed: "success",
		"Accepted as Risk": "secondary",
		"Management Override": "secondary",
	}
	return variants[status] || "secondary"
}

const onFindingClick = (finding) => {
	router.push(`/findings/${finding.name}`)
}

const viewFinding = (finding) => {
	router.push(`/findings/${finding.name}`)
}

const editFinding = (finding) => {
	router.push(`/findings/${finding.name}/edit`)
}

const deleteFinding = (finding) => {
	if (confirm("Are you sure you want to delete this finding?")) {
		// Delete logic will be implemented
	}
}

const createNewFinding = () => {
	router.push("/findings/new")
}

// Lifecycle
onMounted(async () => {
	await fetchFindings()
})
</script>