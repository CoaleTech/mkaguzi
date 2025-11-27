<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Compliance Checklist</h1>
        <p class="text-gray-600">Manage regulatory compliance requirements and track completion status.</p>
      </div>
      <Button @click="createChecklist" class="flex items-center gap-2">
        <Plus class="w-4 h-4" />
        Create Checklist
      </Button>
    </div>

    <!-- Summary Stats -->
    <ChecklistStats :stats="stats" />

    <!-- Filters -->
    <ChecklistFilters
      v-model:searchQuery="searchQuery"
      v-model:selectedPeriodType="selectedPeriodType"
      v-model:selectedStatus="selectedStatus"
      v-model:selectedCompletionStatus="selectedCompletionStatus"
      v-model:selectedAlertLevel="selectedAlertLevel"
    />

    <!-- Checklists Table -->
    <div class="bg-white rounded-lg border shadow-sm">
      <div class="p-4 border-b">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold">Compliance Checklists</h2>
          <div class="flex gap-2">
            <Button
              @click="fetchComplianceChecklists"
              :loading="loading"
              variant="outline"
              size="sm"
            >
              <RefreshCw class="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Checklist ID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Progress</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="checklist in complianceChecklists" :key="checklist.name" class="hover:bg-gray-50">
              <td class="px-4 py-3">
                <div class="font-medium">{{ checklist.checklist_id }}</div>
                <div class="text-sm text-gray-500">{{ checklist.name }}</div>
              </td>
              <td class="px-4 py-3">
                <div>{{ checklist.period_month || checklist.fiscal_year }}</div>
                <div class="text-sm text-gray-500">{{ checklist.compliance_period }}</div>
              </td>
              <td class="px-4 py-3">
                <Badge :variant="getPeriodTypeVariant(checklist.period_type)">
                  {{ checklist.period_type }}
                </Badge>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      class="h-2 rounded-full"
                      :class="getProgressColor(checklist.completion_percent)"
                      :style="{ width: `${checklist.completion_percent || 0}%` }"
                    ></div>
                  </div>
                  <span class="text-sm">{{ checklist.completion_percent || 0 }}%</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="flex flex-col gap-1">
                  <Badge :variant="getStatusVariant(checklist)">
                    {{ getStatusText(checklist) }}
                  </Badge>
                  <div v-if="checklist.overdue_requirements > 0" class="text-xs text-red-600">
                    {{ checklist.overdue_requirements }} overdue
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="flex gap-1">
                  <Button
                    @click="viewChecklist(checklist)"
                    variant="outline"
                    size="sm"
                  >
                    <Eye class="w-4 h-4" />
                  </Button>
                  <Button
                    @click="editChecklist(checklist)"
                    variant="outline"
                    size="sm"
                  >
                    <Edit class="w-4 h-4" />
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="complianceChecklists.length === 0 && !loading" class="p-8 text-center text-gray-500">
        <FileText class="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p>No compliance checklists found.</p>
        <Button @click="createChecklist" class="mt-4">
          Create Your First Checklist
        </Button>
      </div>
    </div>

    <!-- Compliance Checklist Form Dialog -->
    <ComplianceChecklistForm
      v-model:show="showFormDialog"
      :checklist-data="selectedChecklist"
      :is-edit-mode="isEditMode"
      @saved="handleChecklistSaved"
    />
  </div>
</template>

<script setup>
import ChecklistFilters from "@/components/checklist/ChecklistFilters.vue"
import ChecklistStats from "@/components/checklist/ChecklistStats.vue"
import ComplianceChecklistForm from "@/components/checklist/ComplianceChecklistForm.vue"
import { useComplianceStore } from "@/stores/compliance"
import { Badge, Button } from "frappe-ui"
import {
	Edit,
	Eye,
	FileText,
	Plus,
	RefreshCw,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

// Store
const complianceStore = useComplianceStore()

// Reactive data
const showFormDialog = ref(false)
const isEditMode = ref(false)
const selectedChecklist = ref(null)

// Store bindings
const loading = computed(() => complianceStore.loading)
const complianceChecklists = computed(() => complianceStore.complianceChecklists)
const checklistSummary = computed(() => complianceStore.checklistSummary)

// Filter bindings
const searchQuery = ref("")
const selectedPeriodType = ref("")
const selectedStatus = ref("")
const selectedCompletionStatus = ref("")
const selectedAlertLevel = ref("")

// Stats computed from store data
const stats = computed(() => {
	const checklists = complianceChecklists.value
	const total = checklists.length
	const completed = checklists.filter(c => c.completion_percent === 100).length
	const overdue = checklists.filter(c => (c.overdue_requirements || 0) > 0).length
	const inProgress = checklists.filter(c => c.completion_percent > 0 && c.completion_percent < 100).length
	const alerts = checklists.filter(c => (c.alerts?.length || 0) > 0).length

	return {
		total,
		completed,
		overdue,
		inProgress,
		alerts
	}
})

// Methods
const fetchComplianceChecklists = async () => {
	await complianceStore.fetchComplianceChecklists()
}

const createChecklist = () => {
	selectedChecklist.value = null
	isEditMode.value = false
	showFormDialog.value = true
}

const viewChecklist = async (checklist) => {
	try {
		selectedChecklist.value = await complianceStore.getChecklistDetails(checklist.name)
		isEditMode.value = true
		showFormDialog.value = true
	} catch (error) {
		console.error("Error fetching checklist details:", error)
	}
}

const editChecklist = async (checklist) => {
	try {
		selectedChecklist.value = await complianceStore.getChecklistDetails(checklist.name)
		isEditMode.value = true
		showFormDialog.value = true
	} catch (error) {
		console.error("Error fetching checklist details:", error)
	}
}

const handleChecklistSaved = async () => {
	showFormDialog.value = false
	await fetchComplianceChecklists()
}

const getPeriodTypeVariant = (type) => {
	const variants = {
		Monthly: "blue",
		Quarterly: "green",
		Annual: "purple",
	}
	return variants[type] || "gray"
}

const getProgressColor = (percent) => {
	if (percent >= 80) return "bg-green-500"
	if (percent >= 50) return "bg-yellow-500"
	return "bg-red-500"
}

const getStatusVariant = (checklist) => {
	if (checklist.overdue_requirements > 0) return "red"
	if (checklist.completion_percent === 100) return "green"
	if (checklist.completion_percent > 0) return "yellow"
	return "gray"
}

const getStatusText = (checklist) => {
	if (checklist.overdue_requirements > 0) return "Overdue"
	if (checklist.completion_percent === 100) return "Completed"
	if (checklist.completion_percent > 0) return "In Progress"
	return "Not Started"
}

// Lifecycle
onMounted(async () => {
	await fetchComplianceChecklists()
})
</script>