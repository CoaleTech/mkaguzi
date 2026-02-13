<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Compliance Requirements</h1>
        <p class="text-gray-600">Manage regulatory compliance requirements and obligations.</p>
      </div>
      <div class="flex gap-2">
        <Button @click="createStandardRequirements" variant="outline" class="flex items-center gap-2">
          <Download class="w-4 h-4" />
          Load Standards
        </Button>
        <Button @click="showCreateRequirementDialog = true" class="flex items-center gap-2">
          <Plus class="w-4 h-4" />
          Add Requirement
        </Button>
      </div>
    </div>

    <!-- Summary Cards -->
    <ComplianceStats
      :total-requirements="complianceRequirements.length"
      :active-requirements-count="activeRequirements.length"
      :regulatory-bodies-count="Object.keys(requirementsByRegulatoryBody).length"
      :categories-count="Object.keys(requirementsByCategory).length"
    />

    <!-- Filters -->
    <ComplianceFilters :filters="filters" @clear-filters="clearFilters" />

    <!-- Requirements Table -->
    <div class="bg-white rounded-lg border shadow-sm">
      <div class="p-4 border-b">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold">Compliance Requirements</h2>
          <div class="flex gap-2">
            <Button
              @click="fetchComplianceRequirements"
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
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requirement ID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Regulatory Body</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Frequency</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Responsible</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="req in filteredRequirements" :key="req.name" class="hover:bg-gray-50">
              <td class="px-4 py-3">
                <div class="font-medium">{{ req.requirement_id }}</div>
                <div class="text-sm text-gray-500">{{ req.name }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="font-medium">{{ req.requirement_name }}</div>
                <div class="text-sm text-gray-600 line-clamp-2">{{ req.description }}</div>
              </td>
              <td class="px-4 py-3">
                <Badge :variant="getRegulatoryBodyVariant(req.regulatory_body)">
                  {{ req.regulatory_body }}
                </Badge>
              </td>
              <td class="px-4 py-3">
                <Badge :variant="getCategoryVariant(req.compliance_category)">
                  {{ req.compliance_category }}
                </Badge>
              </td>
              <td class="px-4 py-3">
                <div>{{ req.frequency }}</div>
                <div v-if="req.due_date_calculation" class="text-xs text-gray-500">
                  {{ getDueDateText(req) }}
                </div>
              </td>
              <td class="px-4 py-3">
                <div v-if="req.responsible_person">{{ req.responsible_person }}</div>
                <div v-if="req.responsible_department" class="text-sm text-gray-500">
                  {{ req.responsible_department }}
                </div>
              </td>
              <td class="px-4 py-3">
                <Badge :variant="req.is_active ? 'green' : 'gray'">
                  {{ req.is_active ? 'Active' : 'Inactive' }}
                </Badge>
              </td>
              <td class="px-4 py-3">
                <div class="flex gap-1">
                  <Button
                    @click="viewRequirement(req)"
                    variant="outline"
                    size="sm"
                  >
                    <Eye class="w-4 h-4" />
                  </Button>
                  <Button
                    @click="editRequirement(req)"
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

      <div v-if="filteredRequirements.length === 0 && !loading" class="p-8 text-center text-gray-500">
        <FileText class="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p>No compliance requirements found.</p>
        <div class="mt-4 space-x-2">
          <Button @click="createStandardRequirements">Load Standard Requirements</Button>
          <Button @click="showCreateRequirementDialog = true" variant="outline">Add Custom Requirement</Button>
        </div>
      </div>
    </div>

    <!-- Create Requirement Dialog -->
    <Dialog v-model="showCreateRequirementDialog" :options="{ title: 'Add Compliance Requirement', size: '2xl' }">
      <template #body-content>
        <ComplianceRequirementForm v-model:form-data="newRequirement" />
      </template>
      <template #actions>
        <Button variant="outline" @click="showCreateRequirementDialog = false">Cancel</Button>
        <Button @click="createRequirement" :loading="creating">Create Requirement</Button>
      </template>
    </Dialog>

    <!-- Requirement Detail Dialog -->
    <Dialog v-model="showRequirementDetailDialog" :options="{ title: 'Requirement Details', size: '4xl' }">
      <template #body-content>
        <div v-if="selectedRequirement" class="space-y-6">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <h3 class="font-semibold">Basic Information</h3>
              <div class="mt-2 space-y-1 text-sm">
                <p><span class="font-medium">ID:</span> {{ selectedRequirement.requirement_id }}</p>
                <p><span class="font-medium">Name:</span> {{ selectedRequirement.requirement_name }}</p>
                <p><span class="font-medium">Regulatory Body:</span> {{ selectedRequirement.regulatory_body }}</p>
                <p><span class="font-medium">Category:</span> {{ selectedRequirement.compliance_category }}</p>
                <p><span class="font-medium">Frequency:</span> {{ selectedRequirement.frequency }}</p>
                <p><span class="font-medium">Status:</span>
                  <Badge :variant="selectedRequirement.is_active ? 'green' : 'gray'" class="ml-2">
                    {{ selectedRequirement.is_active ? 'Active' : 'Inactive' }}
                  </Badge>
                </p>
              </div>
            </div>
            <div>
              <h3 class="font-semibold">Responsibility</h3>
              <div class="mt-2 space-y-1 text-sm">
                <p v-if="selectedRequirement.responsible_person"><span class="font-medium">Person:</span> {{ selectedRequirement.responsible_person }}</p>
                <p v-if="selectedRequirement.responsible_department"><span class="font-medium">Department:</span> {{ selectedRequirement.responsible_department }}</p>
                <p><span class="font-medium">Due Date Calculation:</span> {{ selectedRequirement.due_date_calculation }}</p>
                <p v-if="selectedRequirement.fixed_due_day"><span class="font-medium">Fixed Due Day:</span> {{ selectedRequirement.fixed_due_day }}</p>
                <p v-if="selectedRequirement.due_days_after_period"><span class="font-medium">Days After Period:</span> {{ selectedRequirement.due_days_after_period }}</p>
              </div>
            </div>
          </div>

          <div>
            <h3 class="font-semibold">Description</h3>
            <p class="mt-2 text-sm">{{ selectedRequirement.description }}</p>
          </div>

          <div v-if="selectedRequirement.applicability">
            <h3 class="font-semibold">Applicability</h3>
            <p class="mt-2 text-sm">{{ selectedRequirement.applicability }}</p>
          </div>

          <div v-if="selectedRequirement.requirement_details && selectedRequirement.requirement_details.length > 0">
            <h3 class="font-semibold">Requirement Details</h3>
            <div class="mt-2 space-y-2">
              <div v-for="detail in selectedRequirement.requirement_details" :key="detail.name" class="p-3 border rounded">
                <p class="font-medium">{{ detail.detail_type }}</p>
                <p class="text-sm text-gray-600">{{ detail.description }}</p>
                <Badge :variant="detail.mandatory ? 'red' : 'gray'" class="mt-1">
                  {{ detail.mandatory ? 'Mandatory' : 'Optional' }}
                </Badge>
              </div>
            </div>
          </div>

          <div v-if="selectedRequirement.penalties_for_non_compliance && selectedRequirement.penalties_for_non_compliance.length > 0">
            <h3 class="font-semibold text-red-600">Penalties for Non-Compliance</h3>
            <div class="mt-2 space-y-2">
              <div v-for="penalty in selectedRequirement.penalties_for_non_compliance" :key="penalty.name" class="p-3 bg-red-50 border border-red-200 rounded">
                <p class="font-medium">{{ penalty.penalty_type }}</p>
                <p class="text-sm">{{ penalty.description }}</p>
                <p v-if="penalty.penalty_amount_range" class="text-sm font-medium text-red-600">
                  Amount Range: {{ penalty.penalty_amount_range }}
                </p>
              </div>
            </div>
          </div>

          <div v-if="selectedRequirement.bc_data_sources && selectedRequirement.bc_data_sources.length > 0">
            <h3 class="font-semibold">BC Data Sources</h3>
            <div class="mt-2 space-y-2">
              <div v-for="source in selectedRequirement.bc_data_sources" :key="source.name" class="p-3 border rounded">
                <p class="font-medium">{{ source.data_source_name }}</p>
                <p class="text-sm text-gray-600">{{ source.description }}</p>
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
	Building,
	CheckCircle,
	Download,
	Edit,
	Eye,
	FileText,
	Plus,
	RefreshCw,
	Tag,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useComplianceStore } from "../stores/compliance"
import ComplianceStats from "../components/compliance/ComplianceStats.vue"
import ComplianceFilters from "../components/compliance/ComplianceFilters.vue"
import ComplianceRequirementForm from "../components/compliance/ComplianceRequirementForm.vue"

// Store
const complianceStore = useComplianceStore()

// Reactive data
const showCreateRequirementDialog = ref(false)
const showRequirementDetailDialog = ref(false)
const showEditDialog = ref(false)
const editMode = ref(false)
const selectedRequirement = ref(null)
const creating = ref(false)
const filters = ref({
	regulatory_body: "",
	compliance_category: "",
	is_active: "",
})
const newRequirement = ref({
	requirement_id: "",
	requirement_name: "",
	regulatory_body: "",
	compliance_category: "",
	description: "",
	frequency: "",
	responsible_person: "",
	responsible_department: "",
	is_active: true,
})

// Computed
const complianceRequirements = computed(
	() => complianceStore.complianceRequirements,
)
const activeRequirements = computed(() => complianceStore.activeRequirements)
const requirementsByRegulatoryBody = computed(
	() => complianceStore.requirementsByRegulatoryBody,
)
const requirementsByCategory = computed(
	() => complianceStore.requirementsByCategory,
)
const loading = computed(() => complianceStore.loading)

const filteredRequirements = computed(() => {
	let filtered = complianceRequirements.value

	if (filters.value.regulatory_body) {
		filtered = filtered.filter(
			(req) => req.regulatory_body === filters.value.regulatory_body,
		)
	}

	if (filters.value.compliance_category) {
		filtered = filtered.filter(
			(req) => req.compliance_category === filters.value.compliance_category,
		)
	}

	if (filters.value.is_active !== "") {
		const isActive = filters.value.is_active === "true"
		filtered = filtered.filter((req) => req.is_active === isActive)
	}

	return filtered
})

// Methods
const fetchComplianceRequirements = async () => {
	await complianceStore.fetchComplianceRequirements()
}

const createRequirement = async () => {
	try {
		creating.value = true
		await complianceStore.createComplianceRequirement(newRequirement.value)
		showCreateRequirementDialog.value = false
		newRequirement.value = {
			requirement_id: "",
			requirement_name: "",
			regulatory_body: "",
			compliance_category: "",
			description: "",
			frequency: "",
			responsible_person: "",
			responsible_department: "",
			is_active: true,
		}
	} catch (error) {
		console.error("Error creating requirement:", error)
	} finally {
		creating.value = false
	}
}

const createStandardRequirements = async () => {
	try {
		await complianceStore.createStandardRequirements()
	} catch (error) {
		console.error("Error creating standard requirements:", error)
	}
}

const viewRequirement = async (requirement) => {
	try {
		selectedRequirement.value = await complianceStore.getRequirementDetails(
			requirement.name,
		)
		showRequirementDetailDialog.value = true
	} catch (error) {
		console.error("Error fetching requirement details:", error)
	}
}

const editRequirement = (requirement) => {
	// Load requirement into edit mode
	editMode.value = true
	selectedRequirement.value = { ...requirement }
	showEditDialog.value = true
}

const clearFilters = () => {
	filters.value = {
		regulatory_body: "",
		compliance_category: "",
		is_active: "",
	}
}

const getRegulatoryBodyVariant = (body) => {
	const variants = {
		KRA: "blue",
		NSSF: "green",
		NHIF: "gray",
		NEMA: "green",
		"County Government": "orange",
	}
	return variants[body] || "gray"
}

const getCategoryVariant = (category) => {
	const variants = {
		Tax: "red",
		"Social Security": "blue",
		Environmental: "green",
		Licensing: "gray",
		"Health & Safety": "orange",
	}
	return variants[category] || "gray"
}

const getDueDateText = (req) => {
	if (req.due_date_calculation === "Fixed Date") {
		return `Due day: ${req.fixed_due_day}`
	} else if (req.due_date_calculation === "X Days After Period End") {
		return `${req.due_days_after_period} days after period`
	}
	return req.due_date_calculation
}

// Lifecycle
onMounted(async () => {
	await fetchComplianceRequirements()
})
</script>