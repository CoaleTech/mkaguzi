<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Compliance Checklist</h1>
        <p class="text-gray-600">Manage regulatory compliance requirements and track completion status.</p>
      </div>
      <Button @click="showCreateChecklistDialog = true" class="flex items-center gap-2">
        <Plus class="w-4 h-4" />
        Create Checklist
      </Button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white p-4 rounded-lg border shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Total Checklists</p>
            <p class="text-2xl font-bold">{{ checklistSummary.total }}</p>
          </div>
          <FileText class="w-8 h-8 text-blue-500" />
        </div>
      </div>
      <div class="bg-white p-4 rounded-lg border shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Completed</p>
            <p class="text-2xl font-bold text-green-600">{{ checklistSummary.completed }}</p>
          </div>
          <CheckCircle class="w-8 h-8 text-green-500" />
        </div>
      </div>
      <div class="bg-white p-4 rounded-lg border shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Overdue</p>
            <p class="text-2xl font-bold text-red-600">{{ checklistSummary.overdue }}</p>
          </div>
          <AlertTriangle class="w-8 h-8 text-red-500" />
        </div>
      </div>
      <div class="bg-white p-4 rounded-lg border shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">With Alerts</p>
            <p class="text-2xl font-bold text-orange-600">{{ checklistSummary.alerts }}</p>
          </div>
          <Bell class="w-8 h-8 text-orange-500" />
        </div>
      </div>
    </div>

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
        <Button @click="showCreateChecklistDialog = true" class="mt-4">
          Create Your First Checklist
        </Button>
      </div>
    </div>

    <!-- Create Checklist Dialog -->
    <Dialog v-model="showCreateChecklistDialog" :options="{ title: 'Create Compliance Checklist' }">
      <template #body-content>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Period Type" v-model="newChecklist.period_type" type="select" :options="periodTypeOptions" required />
            <FormControl v-if="newChecklist.period_type === 'Monthly'" label="Period Month" v-model="newChecklist.period_month" type="text" placeholder="YYYY-MM" required />
            <FormControl v-else label="Fiscal Year" v-model="newChecklist.fiscal_year" type="link" doctype="Fiscal Year" />
          </div>
          <FormControl label="Compliance Period" v-model="newChecklist.compliance_period" type="link" doctype="Data Period" />
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showCreateChecklistDialog = false">Cancel</Button>
        <Button @click="createChecklist" :loading="creating">Create Checklist</Button>
      </template>
    </Dialog>

    <!-- Checklist Detail Dialog -->
    <Dialog v-model="showChecklistDetailDialog" :options="{ title: 'Checklist Details', size: '4xl' }">
      <template #body-content>
        <div v-if="selectedChecklist" class="space-y-6">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <h3 class="font-semibold">Checklist Information</h3>
              <div class="mt-2 space-y-1 text-sm">
                <p><span class="font-medium">ID:</span> {{ selectedChecklist.checklist_id }}</p>
                <p><span class="font-medium">Period:</span> {{ selectedChecklist.period_month || selectedChecklist.fiscal_year }}</p>
                <p><span class="font-medium">Type:</span> {{ selectedChecklist.period_type }}</p>
                <p><span class="font-medium">Progress:</span> {{ selectedChecklist.completion_percent }}%</p>
              </div>
            </div>
            <div>
              <h3 class="font-semibold">Summary</h3>
              <div class="mt-2 space-y-1 text-sm">
                <p><span class="font-medium">Total Requirements:</span> {{ selectedChecklist.total_requirements }}</p>
                <p><span class="font-medium">Completed:</span> {{ selectedChecklist.completed_requirements }}</p>
                <p><span class="font-medium">Overdue:</span> {{ selectedChecklist.overdue_requirements }}</p>
              </div>
            </div>
          </div>

          <!-- Alerts -->
          <div v-if="selectedChecklist.alerts && selectedChecklist.alerts.length > 0">
            <h3 class="font-semibold text-red-600 mb-2">Alerts</h3>
            <div class="space-y-2">
              <div v-for="alert in selectedChecklist.alerts" :key="alert.name" class="p-3 bg-red-50 border border-red-200 rounded">
                <div class="flex items-start gap-2">
                  <AlertTriangle class="w-4 h-4 text-red-500 mt-0.5" />
                  <div>
                    <p class="font-medium">{{ alert.alert_message }}</p>
                    <p class="text-sm text-gray-600">Severity: {{ alert.severity }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Checklist Items -->
          <div>
            <h3 class="font-semibold mb-2">Checklist Items</h3>
            <div class="space-y-2 max-h-96 overflow-y-auto">
              <div v-for="item in selectedChecklist.checklist_items || []" :key="item.name" class="p-3 border rounded">
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <p class="font-medium">{{ item.description }}</p>
                    <p class="text-sm text-gray-600">{{ item.regulatory_body }}</p>
                    <p v-if="item.due_date" class="text-xs text-gray-500">Due: {{ formatDate(item.due_date) }}</p>
                  </div>
                  <div class="flex items-center gap-2">
                    <Badge :variant="getItemStatusVariant(item.status)">
                      {{ item.status || 'Not Started' }}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Badge, Button, Dialog, FormControl } from "frappe-ui"
import {
	AlertTriangle,
	Bell,
	CheckCircle,
	Edit,
	Eye,
	FileText,
	Plus,
	RefreshCw,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useComplianceStore } from "../stores/compliance"

// Store
const complianceStore = useComplianceStore()

// Reactive data
const showCreateChecklistDialog = ref(false)
const showChecklistDetailDialog = ref(false)
const selectedChecklist = ref(null)
const creating = ref(false)
const newChecklist = ref({
	period_type: "Monthly",
	period_month: "",
	fiscal_year: "",
	compliance_period: "",
})

// Computed
const complianceChecklists = computed(
	() => complianceStore.complianceChecklists,
)
const checklistSummary = computed(() => complianceStore.checklistSummary)
const loading = computed(() => complianceStore.loading)

// Options
const periodTypeOptions = [
	{ label: "Monthly", value: "Monthly" },
	{ label: "Quarterly", value: "Quarterly" },
	{ label: "Annual", value: "Annual" },
]

// Methods
const fetchComplianceChecklists = async () => {
	await complianceStore.fetchComplianceChecklists()
}

const createChecklist = async () => {
	try {
		creating.value = true
		await complianceStore.createComplianceChecklist(newChecklist.value)
		showCreateChecklistDialog.value = false
		newChecklist.value = {
			period_type: "Monthly",
			period_month: "",
			fiscal_year: "",
			compliance_period: "",
		}
	} catch (error) {
		console.error("Error creating checklist:", error)
	} finally {
		creating.value = false
	}
}

const viewChecklist = async (checklist) => {
	try {
		selectedChecklist.value = await complianceStore.getChecklistDetails(
			checklist.name,
		)
		showChecklistDetailDialog.value = true
	} catch (error) {
		console.error("Error fetching checklist details:", error)
	}
}

const editChecklist = (checklist) => {
	// TODO: Implement edit functionality
	console.log("Edit checklist:", checklist)
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

const getItemStatusVariant = (status) => {
	const variants = {
		Completed: "green",
		Filed: "green",
		"In Progress": "yellow",
		Overdue: "red",
		"Not Started": "gray",
	}
	return variants[status] || "gray"
}

const formatDate = (dateString) => {
	if (!dateString) return ""
	return new Date(dateString).toLocaleDateString()
}

// Lifecycle
onMounted(async () => {
	await fetchComplianceChecklists()
})
</script>