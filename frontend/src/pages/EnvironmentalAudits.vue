<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Environmental Audits</h1>
        <p class="text-gray-600 mt-1">ESG and environmental compliance tracking</p>
      </div>
      <Button variant="outline" @click="fetchAudits">
        <RefreshCwIcon class="h-4 w-4 mr-2" />
        Refresh
      </Button>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Total</p>
        <p class="text-2xl font-bold text-gray-900">{{ audits.length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">In Progress</p>
        <p class="text-2xl font-bold text-blue-600">{{ audits.filter(a => a.status === 'In Progress').length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Completed</p>
        <p class="text-2xl font-bold text-green-600">{{ audits.filter(a => a.status === 'Completed').length }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Avg ESG Score</p>
        <p class="text-2xl font-bold text-gray-900">{{ avgEsgScore }}</p>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <p class="text-sm text-gray-600">Non-Compliant</p>
        <p class="text-2xl font-bold text-red-600">{{ audits.filter(a => a.compliance_status === 'Non-Compliant').length }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="flex flex-wrap items-center gap-3">
        <FormControl type="text" v-model="search" placeholder="Search..." class="w-48" />
        <FormControl type="select" v-model="filterType" :options="auditTypeOptions" class="w-48" />
        <FormControl type="select" v-model="filterStatus" :options="statusOptions" class="w-36" />
        <Button variant="outline" size="sm" @click="resetFilters">Clear</Button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <!-- Audit Cards -->
    <div v-else-if="filteredAudits.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="audit in filteredAudits"
        :key="audit.name"
        class="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow cursor-pointer"
        @click="showAuditDetail(audit)"
      >
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="font-semibold text-gray-900">{{ audit.audit_title }}</h3>
            <p class="text-sm text-gray-500">{{ audit.audit_type }}</p>
          </div>
          <Badge :variant="getStatusVariant(audit.status)">{{ audit.status }}</Badge>
        </div>

        <div class="grid grid-cols-3 gap-3 mb-3">
          <div>
            <p class="text-xs text-gray-500">ESG Score</p>
            <p class="text-lg font-bold" :class="audit.esg_score >= 70 ? 'text-green-600' : audit.esg_score >= 40 ? 'text-yellow-600' : 'text-red-600'">
              {{ audit.esg_score != null ? audit.esg_score : '-' }}
            </p>
          </div>
          <div>
            <p class="text-xs text-gray-500">Risk Level</p>
            <Badge v-if="audit.risk_level" :variant="getRiskVariant(audit.risk_level)">{{ audit.risk_level }}</Badge>
          </div>
          <div>
            <p class="text-xs text-gray-500">Compliance</p>
            <Badge v-if="audit.compliance_status" :variant="getComplianceVariant(audit.compliance_status)">{{ audit.compliance_status }}</Badge>
          </div>
        </div>

        <div class="flex items-center justify-between text-xs text-gray-500">
          <span v-if="audit.esg_framework">{{ audit.esg_framework }}</span>
          <span>{{ audit.start_date ? formatDate(audit.start_date) : '' }} - {{ audit.end_date ? formatDate(audit.end_date) : '' }}</span>
        </div>

        <!-- Target vs Actual Reduction -->
        <div v-if="audit.target_reduction" class="mt-3 pt-3 border-t border-gray-100">
          <div class="flex items-center justify-between text-sm mb-1">
            <span class="text-gray-600">Reduction Progress</span>
            <span class="font-medium">{{ audit.actual_reduction || 0 }}% / {{ audit.target_reduction }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-green-500 h-2 rounded-full"
              :style="{ width: Math.min(((audit.actual_reduction || 0) / audit.target_reduction) * 100, 100) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="bg-white rounded-lg border border-gray-200 p-12 text-center">
      <LeafIcon class="h-12 w-12 text-gray-300 mx-auto mb-3" />
      <p class="text-gray-600">No environmental audits found.</p>
    </div>

    <!-- Detail Dialog -->
    <Dialog v-model="showDetail" :options="{ title: selectedAudit?.audit_title || 'Environmental Audit', size: 'xl' }">
      <template #body-content>
        <div v-if="auditDetail" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600">Audit Type</p>
              <p class="font-medium">{{ auditDetail.audit_type }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">ESG Framework</p>
              <p class="font-medium">{{ auditDetail.esg_framework || '-' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Environmental Category</p>
              <p class="font-medium">{{ auditDetail.environmental_category || '-' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Carbon Footprint Scope</p>
              <p class="font-medium">{{ auditDetail.carbon_footprint_scope || '-' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Sustainability Rating</p>
              <Badge v-if="auditDetail.sustainability_rating" :variant="getSustainabilityVariant(auditDetail.sustainability_rating)">
                {{ auditDetail.sustainability_rating }}
              </Badge>
            </div>
            <div>
              <p class="text-sm text-gray-600">Assigned To</p>
              <p class="font-medium">{{ auditDetail.assigned_to || '-' }}</p>
            </div>
          </div>

          <!-- Environmental Metrics -->
          <h4 class="font-medium text-gray-900 pt-2">Environmental Metrics</h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="bg-gray-50 rounded p-3">
              <p class="text-xs text-gray-500">Carbon Emissions</p>
              <p class="font-medium">{{ auditDetail.carbon_emissions ? formatCurrency(auditDetail.carbon_emissions) : '-' }}</p>
            </div>
            <div class="bg-gray-50 rounded p-3">
              <p class="text-xs text-gray-500">Energy Consumption</p>
              <p class="font-medium">{{ auditDetail.energy_consumption ? formatCurrency(auditDetail.energy_consumption) : '-' }}</p>
            </div>
            <div class="bg-gray-50 rounded p-3">
              <p class="text-xs text-gray-500">Water Usage</p>
              <p class="font-medium">{{ auditDetail.water_usage ? formatCurrency(auditDetail.water_usage) : '-' }}</p>
            </div>
            <div class="bg-gray-50 rounded p-3">
              <p class="text-xs text-gray-500">Waste Generation</p>
              <p class="font-medium">{{ auditDetail.waste_generation ? formatCurrency(auditDetail.waste_generation) : '-' }}</p>
            </div>
          </div>

          <div v-if="auditDetail.environmental_scope">
            <h4 class="font-medium text-gray-900 mb-1">Scope</h4>
            <div class="prose prose-sm max-w-none" v-html="auditDetail.environmental_scope"></div>
          </div>
          <div v-if="auditDetail.esg_recommendations">
            <h4 class="font-medium text-gray-900 mb-1">Recommendations</h4>
            <div class="prose prose-sm max-w-none" v-html="auditDetail.esg_recommendations"></div>
          </div>
        </div>
        <div v-else class="flex justify-center py-8"><Spinner class="h-6 w-6" /></div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Badge, Button, Dialog, FormControl, Spinner } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	LeafIcon,
	RefreshCwIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

const loading = ref(false)
const audits = ref([])
const showDetail = ref(false)
const selectedAudit = ref(null)
const auditDetail = ref(null)
const search = ref("")
const filterType = ref("")
const filterStatus = ref("")

const auditTypeOptions = [
	{ label: "All Types", value: "" },
	{ label: "Environmental Compliance", value: "Environmental Compliance" },
	{ label: "ESG Assessment", value: "ESG Assessment" },
	{ label: "Sustainability Review", value: "Sustainability Review" },
	{ label: "Carbon Footprint Audit", value: "Carbon Footprint Audit" },
	{ label: "Biodiversity Impact", value: "Biodiversity Impact" },
	{ label: "Supply Chain Sustainability", value: "Supply Chain Sustainability" },
]

const statusOptions = [
	{ label: "All Statuses", value: "" },
	{ label: "Planned", value: "Planned" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Completed", value: "Completed" },
	{ label: "On Hold", value: "On Hold" },
	{ label: "Cancelled", value: "Cancelled" },
]

const avgEsgScore = computed(() => {
	const scored = audits.value.filter((a) => a.esg_score != null)
	if (scored.length === 0) return "-"
	return Math.round(scored.reduce((s, a) => s + a.esg_score, 0) / scored.length)
})

const filteredAudits = computed(() => {
	let result = audits.value
	if (search.value) {
		const q = search.value.toLowerCase()
		result = result.filter((a) => a.audit_title?.toLowerCase().includes(q))
	}
	if (filterType.value) result = result.filter((a) => a.audit_type === filterType.value)
	if (filterStatus.value) result = result.filter((a) => a.status === filterStatus.value)
	return result
})

const getStatusVariant = (s) => ({ Planned: "secondary", "In Progress": "info", Completed: "success", "On Hold": "warning", Cancelled: "danger" })[s] || "secondary"
const getRiskVariant = (r) => ({ Low: "secondary", Medium: "warning", High: "danger", Critical: "danger" })[r] || "secondary"
const getComplianceVariant = (c) => ({ "Fully Compliant": "success", "Mostly Compliant": "info", "Partially Compliant": "warning", "Non-Compliant": "danger", "Not Assessed": "secondary" })[c] || "secondary"
const getSustainabilityVariant = (r) => ({ Excellent: "success", Good: "info", Satisfactory: "warning", "Needs Improvement": "warning", Poor: "danger" })[r] || "secondary"

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : "-"
const formatCurrency = (v) => v != null ? Number(v).toLocaleString() : "-"

const resetFilters = () => { search.value = ""; filterType.value = ""; filterStatus.value = "" }

const fetchAudits = async () => {
	loading.value = true
	try {
		const res = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Environmental Audit",
				fields: [
					"name", "audit_id", "audit_title", "audit_type", "status",
					"priority", "esg_framework", "esg_score", "compliance_status",
					"risk_level", "sustainability_rating", "start_date", "end_date",
					"target_reduction", "actual_reduction", "environmental_category",
				],
				order_by: "creation desc",
				limit_page_length: 200,
			},
		}).fetch()
		audits.value = res || []
	} catch (err) {
		console.error("Failed to fetch environmental audits:", err)
	} finally {
		loading.value = false
	}
}

const showAuditDetail = async (audit) => {
	selectedAudit.value = audit
	auditDetail.value = null
	showDetail.value = true
	try {
		auditDetail.value = await createResource({
			url: "frappe.client.get",
			params: { doctype: "Environmental Audit", name: audit.name },
		}).fetch()
	} catch (err) {
		console.error("Failed to load detail:", err)
	}
}

onMounted(() => { fetchAudits() })
</script>
