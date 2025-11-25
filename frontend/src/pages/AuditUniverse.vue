<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit Universe</h1>
        <p class="text-gray-600 mt-1">
          Manage auditable entities, risk areas, and audit planning scope
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
        <Button @click="createNewEntity">
          <PlusIcon class="h-4 w-4 mr-2" />
          Add Entity
        </Button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-6">
      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <BuildingIcon class="h-6 w-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Entities</p>
            <p class="text-2xl font-bold text-gray-900">{{ totalEntities }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center">
          <div class="p-2 bg-red-100 rounded-lg">
            <AlertTriangleIcon class="h-6 w-6 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Critical Risk</p>
            <p class="text-2xl font-bold text-gray-900">{{ criticalRiskCount }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center">
          <div class="p-2 bg-orange-100 rounded-lg">
            <AlertTriangleIcon class="h-6 w-6 text-orange-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">High Risk</p>
            <p class="text-2xl font-bold text-gray-900">{{ highRiskCount }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <ClockIcon class="h-6 w-6 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Due This Quarter</p>
            <p class="text-2xl font-bold text-gray-900">{{ dueThisQuarter }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <CheckCircleIcon class="h-6 w-6 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Inactive</p>
            <p class="text-2xl font-bold text-gray-900">{{ inactiveCount }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <div class="lg:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <Input
            v-model="searchQuery"
            placeholder="Search entities..."
            class="w-full"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Risk Level</label>
          <Select
            v-model="riskFilter"
            :options="riskOptions"
            placeholder="All Risk Levels"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Entity Type</label>
          <Select
            v-model="typeFilter"
            :options="typeOptions"
            placeholder="All Types"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Department</label>
          <Select
            v-model="departmentFilter"
            :options="departmentOptions"
            placeholder="All Departments"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <Select
            v-model="statusFilter"
            :options="statusOptions"
            placeholder="All Status"
          />
        </div>
      </div>
    </div>

    <!-- Audit Universe Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Auditable Entities</h3>
          <div class="flex items-center space-x-2">
            <Button variant="outline" size="sm" @click="toggleViewMode">
              <GridIcon v-if="viewMode === 'table'" class="h-4 w-4 mr-2" />
              <ListIcon v-else class="h-4 w-4 mr-2" />
              {{ viewMode === 'table' ? 'Card View' : 'Table View' }}
            </Button>
          </div>
        </div>

        <!-- Table View -->
        <DataTable
          v-if="viewMode === 'table'"
          :columns="columns"
          :data="filteredEntities"
          :loading="loading"
          :pagination="true"
          :sortable="true"
          @row-click="onEntityClick"
        >
          <!-- Risk Level Column -->
          <template #column-residualRiskRating="{ row }">
            <Badge :variant="getRiskVariant(row.residual_risk_rating)">
              {{ row.residual_risk_rating }}
            </Badge>
          </template>

          <!-- Status Column -->
          <template #column-isActive="{ row }">
            <Badge :variant="row.is_active ? 'success' : 'secondary'">
              {{ row.is_active ? 'Active' : 'Inactive' }}
            </Badge>
          </template>

          <!-- Last Audit Column -->
          <template #column-lastAuditDate="{ row }">
            <div v-if="row.last_audit_date">
              <p class="text-sm font-medium">{{ formatDate(row.last_audit_date) }}</p>
              <p class="text-xs text-gray-600">{{ row.last_audit_opinion }}</p>
            </div>
            <span v-else class="text-gray-400 text-sm">Never</span>
          </template>

          <!-- Next Audit Column -->
          <template #column-nextScheduledAudit="{ row }">
            <div v-if="row.next_scheduled_audit">
              <p class="text-sm font-medium">{{ formatDate(row.next_scheduled_audit) }}</p>
              <Badge
                v-if="isOverdue(row.next_scheduled_audit)"
                variant="danger"
                size="sm"
                class="mt-1"
              >
                Overdue
              </Badge>
            </div>
            <span v-else class="text-gray-400 text-sm">Not scheduled</span>
          </template>

          <!-- Actions Column -->
          <template #column-actions="{ row }">
            <div class="flex items-center space-x-2">
              <Button variant="ghost" size="sm" @click="viewEntity(row)">
                <EyeIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="editEntity(row)">
                <EditIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" @click="scheduleAudit(row)">
                <CalendarIcon class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click="toggleEntityStatus(row)"
                :class="row.is_active ? 'text-orange-600' : 'text-green-600'"
              >
                <PowerIcon class="h-4 w-4" />
              </Button>
            </div>
          </template>
        </DataTable>

        <!-- Card View -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="entity in filteredEntities"
            :key="entity.universe_id"
            class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
            @click="onEntityClick(entity)"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h4 class="font-semibold text-gray-900 truncate">{{ entity.auditable_entity }}</h4>
                <p class="text-sm text-gray-600">{{ entity.entity_type }}</p>
              </div>
              <Badge :variant="getRiskVariant(entity.residual_risk_rating)" size="sm">
                {{ entity.residual_risk_rating }}
              </Badge>
            </div>

            <div class="space-y-2 mb-4">
              <div class="flex items-center text-sm">
                <MapPinIcon class="h-4 w-4 text-gray-400 mr-2" />
                <span>{{ entity.location }}</span>
              </div>
              <div class="flex items-center text-sm">
                <UserIcon class="h-4 w-4 text-gray-400 mr-2" />
                <span>{{ entity.department }}</span>
              </div>
              <div v-if="entity.next_scheduled_audit" class="flex items-center text-sm">
                <CalendarIcon class="h-4 w-4 text-gray-400 mr-2" />
                <span :class="isOverdue(entity.next_scheduled_audit) ? 'text-red-600' : ''">
                  Next: {{ formatDate(entity.next_scheduled_audit) }}
                </span>
              </div>
            </div>

            <div class="flex items-center justify-between">
              <Badge :variant="entity.is_active ? 'success' : 'secondary'" size="sm">
                {{ entity.is_active ? 'Active' : 'Inactive' }}
              </Badge>
              <div class="flex items-center space-x-1">
                <Button variant="ghost" size="sm" @click.stop="viewEntity(entity)">
                  <EyeIcon class="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" @click.stop="editEntity(entity)">
                  <EditIcon class="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { DataTable } from "@/components/Common"
import { Badge, Button, Input, Select } from "frappe-ui"
import {
	AlertTriangleIcon,
	BuildingIcon,
	CalendarIcon,
	CheckCircleIcon,
	ClockIcon,
	DownloadIcon,
	EditIcon,
	EyeIcon,
	GridIcon,
	ListIcon,
	MapPinIcon,
	PlusIcon,
	PowerIcon,
	UserIcon,
} from "lucide-vue-next"
import { computed, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

// Reactive state
const loading = ref(false)
const searchQuery = ref("")
const riskFilter = ref("")
const typeFilter = ref("")
const departmentFilter = ref("")
const statusFilter = ref("")
const viewMode = ref("table") // "table" or "card"

const entities = ref([
	{
		universe_id: "AU-001",
		auditable_entity: "Accounts Payable",
		entity_type: "Process",
		department: "Finance",
		location: "Head Office",
		description: "Processing of vendor payments and expense reimbursements",
		process_owner: "John Doe",
		inherent_risk_rating: "High",
		inherent_risk_score: 15,
		control_environment_rating: "Adequate",
		control_effectiveness_score: 3,
		residual_risk_rating: "Medium",
		residual_risk_score: 5,
		risk_factors: [],
		key_controls: [],
		audit_frequency: "Quarterly",
		last_audit_date: "2023-10-15",
		last_audit_opinion: "Satisfactory",
		next_scheduled_audit: "2024-01-15",
		mandatory_audit: false,
		regulatory_reference: "",
		bc_data_sources: [],
		notes: "",
		is_active: true,
	},
	{
		universe_id: "AU-002",
		auditable_entity: "IT Security Controls",
		entity_type: "System",
		department: "IT",
		location: "Head Office",
		description: "Access controls, data protection, and cybersecurity measures",
		process_owner: "Jane Smith",
		inherent_risk_rating: "Critical",
		inherent_risk_score: 25,
		control_environment_rating: "Strong",
		control_effectiveness_score: 4,
		residual_risk_rating: "High",
		residual_risk_score: 6,
		risk_factors: [],
		key_controls: [],
		audit_frequency: "Quarterly",
		last_audit_date: "2023-08-20",
		last_audit_opinion: "Needs Improvement",
		next_scheduled_audit: "2023-11-20",
		mandatory_audit: true,
		regulatory_reference: "CBK Cybersecurity Guidelines",
		bc_data_sources: [],
		notes: "",
		is_active: true,
	},
	{
		universe_id: "AU-003",
		auditable_entity: "Inventory Management",
		entity_type: "Process",
		department: "Operations",
		location: "Warehouse",
		description: "Stock control, valuation, and warehouse operations",
		process_owner: "Bob Johnson",
		inherent_risk_rating: "Medium",
		inherent_risk_score: 8,
		control_environment_rating: "Adequate",
		control_effectiveness_score: 3,
		residual_risk_rating: "Low",
		residual_risk_score: 3,
		risk_factors: [],
		key_controls: [],
		audit_frequency: "Semi-Annual",
		last_audit_date: "2023-09-10",
		last_audit_opinion: "Satisfactory",
		next_scheduled_audit: "2024-03-10",
		mandatory_audit: false,
		regulatory_reference: "",
		bc_data_sources: [],
		notes: "",
		is_active: true,
	},
	{
		universe_id: "AU-004",
		auditable_entity: "HR Payroll",
		entity_type: "Process",
		department: "HR",
		location: "Head Office",
		description: "Employee compensation, benefits, and payroll processing",
		process_owner: "Alice Brown",
		inherent_risk_rating: "High",
		inherent_risk_score: 15,
		control_environment_rating: "Weak",
		control_effectiveness_score: 2,
		residual_risk_rating: "High",
		residual_risk_score: 8,
		risk_factors: [],
		key_controls: [],
		audit_frequency: "Quarterly",
		last_audit_date: null,
		last_audit_opinion: "",
		next_scheduled_audit: "2023-12-01",
		mandatory_audit: true,
		regulatory_reference: "Employment Act, PAYE Regulations",
		bc_data_sources: [],
		notes: "",
		is_active: true,
	},
	{
		universe_id: "AU-005",
		auditable_entity: "Sales Order Processing",
		entity_type: "Process",
		department: "Sales",
		location: "Head Office",
		description: "Customer order processing and fulfillment",
		process_owner: "Charlie Wilson",
		inherent_risk_rating: "Medium",
		inherent_risk_score: 8,
		control_environment_rating: "Adequate",
		control_effectiveness_score: 3,
		residual_risk_rating: "Low",
		residual_risk_score: 3,
		risk_factors: [],
		key_controls: [],
		audit_frequency: "Semi-Annual",
		last_audit_date: "2023-07-15",
		last_audit_opinion: "Satisfactory",
		next_scheduled_audit: "2024-01-15",
		mandatory_audit: false,
		regulatory_reference: "",
		bc_data_sources: [],
		notes: "",
		is_active: false,
	},
])

// Computed properties
const totalEntities = computed(() => entities.value.length)
const criticalRiskCount = computed(
	() =>
		entities.value.filter((e) => e.residual_risk_rating === "Critical").length,
)
const highRiskCount = computed(
	() => entities.value.filter((e) => e.residual_risk_rating === "High").length,
)
const dueThisQuarter = computed(() => {
	const now = new Date()
	const quarterEnd = new Date(
		now.getFullYear(),
		Math.floor(now.getMonth() / 3) * 3 + 3,
		0,
	)
	return entities.value.filter((e) => {
		if (!e.next_scheduled_audit) return false
		const dueDate = new Date(e.next_scheduled_audit)
		return dueDate <= quarterEnd
	}).length
})
const inactiveCount = computed(
	() => entities.value.filter((e) => !e.is_active).length,
)

const filteredEntities = computed(() => {
	return entities.value.filter((entity) => {
		const matchesSearch =
			!searchQuery.value ||
			entity.auditable_entity
				.toLowerCase()
				.includes(searchQuery.value.toLowerCase()) ||
			entity.description
				.toLowerCase()
				.includes(searchQuery.value.toLowerCase()) ||
			entity.process_owner
				.toLowerCase()
				.includes(searchQuery.value.toLowerCase())

		const matchesRisk =
			!riskFilter.value || entity.residual_risk_rating === riskFilter.value
		const matchesType =
			!typeFilter.value || entity.entity_type === typeFilter.value
		const matchesDepartment =
			!departmentFilter.value || entity.department === departmentFilter.value
		const matchesStatus =
			!statusFilter.value ||
			(statusFilter.value === "active" && entity.is_active) ||
			(statusFilter.value === "inactive" && !entity.is_active)

		return (
			matchesSearch &&
			matchesRisk &&
			matchesType &&
			matchesDepartment &&
			matchesStatus
		)
	})
})

const columns = [
	{ key: "auditable_entity", label: "Entity Name", sortable: true },
	{ key: "entity_type", label: "Type", sortable: true },
	{ key: "department", label: "Department", sortable: true },
	{ key: "location", label: "Location", sortable: true },
	{ key: "residual_risk_rating", label: "Risk Level", sortable: true },
	{ key: "is_active", label: "Status", sortable: true },
	{ key: "last_audit_date", label: "Last Audit", sortable: true },
	{ key: "next_scheduled_audit", label: "Next Due", sortable: true },
	{ key: "actions", label: "Actions", width: "140px" },
]

const riskOptions = [
	{ label: "All Risk Levels", value: "" },
	{ label: "Critical", value: "Critical" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

const typeOptions = [
	{ label: "All Types", value: "" },
	{ label: "Process", value: "Process" },
	{ label: "Function", value: "Function" },
	{ label: "Department", value: "Department" },
	{ label: "Location", value: "Location" },
	{ label: "System", value: "System" },
	{ label: "Compliance Area", value: "Compliance Area" },
]

const departmentOptions = [
	{ label: "All Departments", value: "" },
	{ label: "Finance", value: "Finance" },
	{ label: "IT", value: "IT" },
	{ label: "Operations", value: "Operations" },
	{ label: "HR", value: "HR" },
	{ label: "Sales", value: "Sales" },
	{ label: "Procurement", value: "Procurement" },
]

const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Active", value: "active" },
	{ label: "Inactive", value: "inactive" },
]

// Methods
const getRiskVariant = (risk) => {
	const variants = {
		Critical: "danger",
		High: "danger",
		Medium: "warning",
		Low: "success",
	}
	return variants[risk] || "secondary"
}

const formatDate = (date) => {
	return new Date(date).toLocaleDateString()
}

const isOverdue = (dateString) => {
	if (!dateString) return false
	const dueDate = new Date(dateString)
	const today = new Date()
	return dueDate < today
}

const toggleViewMode = () => {
	viewMode.value = viewMode.value === "table" ? "card" : "table"
}

const createNewEntity = () => {
	router.push("/audit-planning/universe/new")
}

const onEntityClick = (entity) => {
	router.push(`/audit-planning/universe/${entity.universe_id}`)
}

const viewEntity = (entity) => {
	router.push(`/audit-planning/universe/${entity.universe_id}`)
}

const editEntity = (entity) => {
	router.push(`/audit-planning/universe/${entity.universe_id}/edit`)
}

const scheduleAudit = (entity) => {
	// Navigate to audit scheduling
	console.log("Schedule audit for:", entity.universe_id)
}

const toggleEntityStatus = (entity) => {
	entity.is_active = !entity.is_active
	// In a real app, this would update the backend
	console.log(
		"Toggled status for:",
		entity.universe_id,
		"to:",
		entity.is_active,
	)
}
</script>