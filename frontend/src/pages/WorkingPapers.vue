<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Working Papers</h1>
        <p class="text-gray-600 mt-1">
          Manage audit working papers and documentation
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button @click="createNewWorkingPaper">
          <PlusIcon class="h-4 w-4 mr-2" />
          New Working Paper
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Input
          v-model="filters.search"
          placeholder="Search working papers..."
          class="w-full"
        />
        <Select
          v-model="filters.engagement"
          :options="engagementOptions"
          placeholder="All Engagements"
        />
        <Select
          v-model="filters.type"
          :options="typeOptions"
          placeholder="All Types"
        />
        <Select
          v-model="filters.status"
          :options="statusOptions"
          placeholder="All Status"
        />
        <Select
          v-model="filters.preparedBy"
          :options="preparedByOptions"
          placeholder="All Preparers"
        />
      </div>
    </div>

    <!-- Working Papers Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="p-6">
        <DataTable
          :columns="columns"
          :data="filteredWorkingPapers"
          :loading="loading"
          :pagination="true"
          :sortable="true"
          @row-click="onWorkingPaperClick"
        >
          <!-- Type Column -->
          <template #column-wp_type="{ row }">
            <Badge variant="secondary">
              {{ row.wp_type || 'Planning Memo' }}
            </Badge>
          </template>

          <!-- Status Column -->
          <template #column-review_status="{ row }">
            <Badge :variant="getStatusVariant(row.review_status)">
              {{ row.review_status || 'Not Reviewed' }}
            </Badge>
          </template>

          <!-- Actions Column -->
          <template #column-actions="{ row }">
            <div class="flex items-center space-x-2">
              <Button variant="ghost" size="sm" @click="viewWorkingPaper(row)">
                <EyeIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="editWorkingPaper(row)">
                <EditIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="duplicateWorkingPaper(row)">
                <CopyIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                color="red"
                @click="deleteWorkingPaper(row)"
              >
                <TrashIcon class="h-4 w-4" />
              </Button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Working Paper Modal -->
    <Dialog v-model="showWorkingPaperModal" :options="{ size: '4xl' }">
      <template #body>
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-semibold">
              {{ isEditing ? 'Edit Working Paper' : 'Create New Working Paper' }}
            </h3>
            <p class="text-gray-600 mt-1">
              {{ isEditing ? 'Update working paper details' : 'Create a new working paper for audit documentation' }}
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Basic Information -->
            <div class="space-y-4">
              <FormControl label="Working Paper ID">
                <Input
                  v-model="workingPaperForm.working_paper_id"
                  placeholder="WP-001"
                  :disabled="isEditing"
                />
              </FormControl>

              <FormControl label="Title" required>
                <Input
                  v-model="workingPaperForm.wp_title"
                  placeholder="Enter working paper title"
                />
              </FormControl>

              <FormControl label="Reference Number">
                <Input
                  v-model="workingPaperForm.wp_reference_no"
                  placeholder="REF-001"
                />
              </FormControl>

              <FormControl label="Type" required>
                <Select
                  v-model="workingPaperForm.wp_type"
                  :options="wpTypeOptions"
                />
              </FormControl>

              <FormControl label="Engagement" required>
                <Select
                  v-model="workingPaperForm.engagement_reference"
                  :options="engagementOptions"
                />
              </FormControl>

              <FormControl label="Procedure">
                <Select
                  v-model="workingPaperForm.procedure_reference"
                  :options="procedureOptions"
                />
              </FormControl>
            </div>

            <!-- Assignment & Status -->
            <div class="space-y-4">
              <FormControl label="Prepared By" required>
                <Select
                  v-model="workingPaperForm.prepared_by"
                  :options="userOptions"
                />
              </FormControl>

              <FormControl label="Preparation Date" required>
                <Input
                  v-model="workingPaperForm.preparation_date"
                  type="date"
                />
              </FormControl>

              <FormControl label="Reviewed By">
                <Select
                  v-model="workingPaperForm.reviewed_by"
                  :options="userOptions"
                />
              </FormControl>

              <FormControl label="Review Date">
                <Input
                  v-model="workingPaperForm.review_date"
                  type="date"
                />
              </FormControl>

              <FormControl label="Review Status">
                <Select
                  v-model="workingPaperForm.review_status"
                  :options="reviewStatusOptions"
                />
              </FormControl>
            </div>
          </div>

          <!-- Work Performed -->
          <FormControl label="Work Performed" required>
            <textarea
              v-model="workingPaperForm.work_performed"
              class="w-full h-32 p-3 border border-gray-300 rounded-md resize-vertical"
              placeholder="Describe the work performed..."
            />
          </FormControl>

          <!-- Objective & Scope -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormControl label="Objective">
              <textarea
                v-model="workingPaperForm.objective"
                class="w-full h-24 p-3 border border-gray-300 rounded-md resize-vertical"
                placeholder="Working paper objective..."
              />
            </FormControl>

            <FormControl label="Scope">
              <textarea
                v-model="workingPaperForm.scope"
                class="w-full h-24 p-3 border border-gray-300 rounded-md resize-vertical"
                placeholder="Working paper scope..."
              />
            </FormControl>
          </div>
        </div>
      </template>

      <template #actions>
        <Button variant="outline" @click="closeWorkingPaperModal">
          Cancel
        </Button>
        <Button @click="saveWorkingPaper">
          {{ isEditing ? 'Update' : 'Create' }} Working Paper
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { DataTable } from "@/components/Common"
import { useAuditStore } from "@/stores/audit"
import { Badge, Button, Dialog, FormControl, Input, Select } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	CopyIcon,
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
const showWorkingPaperModal = ref(false)
const isEditing = ref(false)
const currentWorkingPaper = ref(null)

const filters = ref({
	search: "",
	engagement: "",
	type: "",
	status: "",
	preparedBy: "",
})

const workingPaperForm = ref({
	working_paper_id: "",
	wp_title: "",
	wp_reference_no: "",
	wp_type: "Planning Memo",
	engagement_reference: "",
	procedure_reference: "",
	prepared_by: "",
	preparation_date: "",
	reviewed_by: "",
	review_date: "",
	review_status: "Not Reviewed",
	work_performed: "",
	objective: "",
	scope: "",
})

// Computed properties
const workingPapers = computed(() => auditStore.workingPapers)

const filteredWorkingPapers = computed(() => {
	let filtered = workingPapers.value

	if (filters.value.search) {
		filtered = filtered.filter(
			(wp) =>
				wp.wp_title
					?.toLowerCase()
					.includes(filters.value.search.toLowerCase()) ||
				wp.working_paper_id
					?.toLowerCase()
					.includes(filters.value.search.toLowerCase()),
		)
	}

	if (filters.value.engagement) {
		filtered = filtered.filter(
			(wp) => wp.engagement_reference === filters.value.engagement,
		)
	}

	if (filters.value.type) {
		filtered = filtered.filter((wp) => wp.wp_type === filters.value.type)
	}

	if (filters.value.status) {
		filtered = filtered.filter(
			(wp) => wp.review_status === filters.value.status,
		)
	}

	if (filters.value.preparedBy) {
		filtered = filtered.filter(
			(wp) => wp.prepared_by === filters.value.preparedBy,
		)
	}

	return filtered
})

const columns = [
	{ key: "working_paper_id", label: "WP ID", sortable: true },
	{ key: "wp_title", label: "Title", sortable: true },
	{ key: "wp_type", label: "Type", sortable: true },
	{ key: "engagement_reference", label: "Engagement", sortable: true },
	{ key: "prepared_by", label: "Prepared By", sortable: true },
	{ key: "preparation_date", label: "Date", sortable: true },
	{ key: "review_status", label: "Status", sortable: true },
	{ key: "actions", label: "Actions", width: "160px" },
]

const engagementOptions = computed(() => {
	const engagements = auditStore.engagements
	return [
		{ label: "All Engagements", value: "" },
		...engagements.map((eng) => ({
			label: eng.engagement_title,
			value: eng.name,
		})),
	]
})

const typeOptions = [
	{ label: "All Types", value: "" },
	{ label: "Planning Memo", value: "Planning Memo" },
	{ label: "Risk Assessment", value: "Risk Assessment" },
	{ label: "Walkthrough", value: "Walkthrough" },
	{ label: "Test of Controls", value: "Test of Controls" },
	{ label: "Substantive Test", value: "Substantive Test" },
	{ label: "Analytical Review", value: "Analytical Review" },
	{ label: "Data Analytics", value: "Data Analytics" },
	{ label: "Summary", value: "Summary" },
	{ label: "Other", value: "Other" },
]

const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Not Reviewed", value: "Not Reviewed" },
	{ label: "Under Review", value: "Under Review" },
	{ label: "Review Complete", value: "Review Complete" },
	{ label: "Revision Required", value: "Revision Required" },
]

const preparedByOptions = computed(() => {
	const preparers = new Set()
	workingPapers.value.forEach((wp) => {
		if (wp.prepared_by) {
			preparers.add(wp.prepared_by)
		}
	})

	return [
		{ label: "All Preparers", value: "" },
		...Array.from(preparers).map((preparer) => ({
			label: preparer,
			value: preparer,
		})),
	]
})

const wpTypeOptions = typeOptions.slice(1) // Remove "All Types" option
const reviewStatusOptions = statusOptions.slice(1) // Remove "All Status" option

const procedureOptions = computed(() => {
	// This would be populated from audit procedures related to the selected engagement
	return [{ label: "Select Procedure", value: "" }]
})

const userOptions = computed(() => {
	// This would be populated from system users
	return [
		{ label: "Select User", value: "" },
		{ label: "John Doe", value: "john.doe@example.com" },
		{ label: "Jane Smith", value: "jane.smith@example.com" },
	]
})

// Methods
const getStatusVariant = (status) => {
	const variants = {
		"Not Reviewed": "secondary",
		"Under Review": "warning",
		"Review Complete": "success",
		"Revision Required": "danger",
	}
	return variants[status] || "secondary"
}

const onWorkingPaperClick = (workingPaper) => {
	router.push(`/working-papers/${workingPaper.name}`)
}

const viewWorkingPaper = (workingPaper) => {
	router.push(`/working-papers/${workingPaper.name}`)
}

const editWorkingPaper = (workingPaper) => {
	currentWorkingPaper.value = workingPaper
	isEditing.value = true

	// Populate form with existing data
	workingPaperForm.value = {
		working_paper_id: workingPaper.working_paper_id || "",
		wp_title: workingPaper.wp_title || "",
		wp_reference_no: workingPaper.wp_reference_no || "",
		wp_type: workingPaper.wp_type || "Planning Memo",
		engagement_reference: workingPaper.engagement_reference || "",
		procedure_reference: workingPaper.procedure_reference || "",
		prepared_by: workingPaper.prepared_by || "",
		preparation_date: workingPaper.preparation_date || "",
		reviewed_by: workingPaper.reviewed_by || "",
		review_date: workingPaper.review_date || "",
		review_status: workingPaper.review_status || "Not Reviewed",
		work_performed: workingPaper.work_performed || "",
		objective: workingPaper.objective || "",
		scope: workingPaper.scope || "",
	}

	showWorkingPaperModal.value = true
}

const duplicateWorkingPaper = (workingPaper) => {
	currentWorkingPaper.value = null
	isEditing.value = false

	// Populate form with duplicated data
	workingPaperForm.value = {
		working_paper_id: "",
		wp_title: `${workingPaper.wp_title} (Copy)`,
		wp_reference_no: "",
		wp_type: workingPaper.wp_type || "Planning Memo",
		engagement_reference: workingPaper.engagement_reference || "",
		procedure_reference: workingPaper.procedure_reference || "",
		prepared_by: "",
		preparation_date: new Date().toISOString().split("T")[0],
		reviewed_by: "",
		review_date: "",
		review_status: "Not Reviewed",
		work_performed: workingPaper.work_performed || "",
		objective: workingPaper.objective || "",
		scope: workingPaper.scope || "",
	}

	showWorkingPaperModal.value = true
}

const deleteWorkingPaper = (workingPaper) => {
	if (confirm("Are you sure you want to delete this working paper?")) {
		// Delete logic will be implemented with API call
		// For now, we'll refresh the list
		auditStore.fetchWorkingPapers()
	}
}

const createNewWorkingPaper = () => {
	currentWorkingPaper.value = null
	isEditing.value = false

	// Reset form
	workingPaperForm.value = {
		working_paper_id: "",
		wp_title: "",
		wp_reference_no: "",
		wp_type: "Planning Memo",
		engagement_reference: "",
		procedure_reference: "",
		prepared_by: "",
		preparation_date: new Date().toISOString().split("T")[0],
		reviewed_by: "",
		review_date: "",
		review_status: "Not Reviewed",
		work_performed: "",
		objective: "",
		scope: "",
	}

	showWorkingPaperModal.value = true
}

const closeWorkingPaperModal = () => {
	showWorkingPaperModal.value = false
	currentWorkingPaper.value = null
	isEditing.value = false
}

const saveWorkingPaper = async () => {
	try {
		if (isEditing.value) {
			// Update existing working paper
			await auditStore.updateWorkingPaper(
				currentWorkingPaper.value.name,
				workingPaperForm.value,
			)
		} else {
			// Create new working paper
			await auditStore.createWorkingPaper(workingPaperForm.value)
		}

		closeWorkingPaperModal()
	} catch (error) {
		console.error("Error saving working paper:", error)
	}
}

// Lifecycle
onMounted(async () => {
	loading.value = true
	try {
		await auditStore.fetchEngagements()
		await auditStore.fetchWorkingPapers()
	} catch (error) {
		console.error("Error loading data:", error)
	} finally {
		loading.value = false
	}
})
</script>