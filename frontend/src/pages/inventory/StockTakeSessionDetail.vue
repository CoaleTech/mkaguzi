<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <Button variant="ghost" @click="goBack">
          <ArrowLeft class="w-5 h-5" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ session?.session_name || session?.name || 'Loading...' }}</h1>
          <p class="text-gray-500 mt-1">Stock Take Session</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Badge :variant="statusVariant">{{ session?.status }}</Badge>
        <Button variant="outline" @click="editSession">
          <Edit class="w-4 h-4 mr-2" />
          Edit
        </Button>
        <Button variant="solid" @click="startCount" v-if="session?.status === 'Scheduled'">
          <Play class="w-4 h-4 mr-2" />
          Start Counting
        </Button>
        <Button variant="solid" @click="submitForReview" v-if="session?.status === 'In Progress'">
          <CheckCircle class="w-4 h-4 mr-2" />
          Submit for Review
        </Button>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="session" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Session Overview -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Session Overview</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <span class="text-sm text-gray-500">Session Type</span>
              <p class="font-medium">{{ session.session_type }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Warehouse</span>
              <p class="font-medium">{{ session.warehouse || '-' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Zone</span>
              <p class="font-medium">{{ session.zone || '-' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Bin Location</span>
              <p class="font-medium">{{ session.bin_location || '-' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Scheduled Date</span>
              <p class="font-medium">{{ formatDate(session.scheduled_date) }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Assigned Counters</span>
              <p class="font-medium">{{ session.assigned_counters || '-' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Total Items</span>
              <p class="font-medium">{{ totalItems }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Items Counted</span>
              <p class="font-medium text-green-600">{{ countedItems }}</p>
            </div>
          </div>
        </div>

        <!-- Linked Audit Plan -->
        <div v-if="session.audit_plan" class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Linked Audit Plan</h3>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <ClipboardList class="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p class="font-medium">{{ session.audit_plan }}</p>
                <p class="text-sm text-gray-500">Inventory Audit Plan</p>
              </div>
            </div>
            <Button variant="outline" size="sm" @click="viewAuditPlan">
              <ExternalLink class="w-4 h-4 mr-1" />
              View Plan
            </Button>
          </div>
        </div>

        <!-- Count Items Table -->
        <div class="bg-white rounded-lg border p-6">
          <PhysicalCountTable
            v-model="session.count_items"
            :readonly="session.status === 'Completed' || session.status === 'Approved'"
            @update:modelValue="handleCountItemsUpdate"
          />
        </div>

        <!-- Variance Summary -->
        <div v-if="varianceStats.totalVariances > 0" class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Variance Summary</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <div class="flex items-center gap-2 mb-2">
                <AlertTriangle class="w-5 h-5 text-yellow-600" />
                <span class="text-sm text-yellow-700">Total Variances</span>
              </div>
              <p class="text-2xl font-bold text-yellow-700">{{ varianceStats.totalVariances }}</p>
            </div>
            <div class="p-4 bg-red-50 rounded-lg border border-red-200">
              <div class="flex items-center gap-2 mb-2">
                <TrendingDown class="w-5 h-5 text-red-600" />
                <span class="text-sm text-red-700">Shortages</span>
              </div>
              <p class="text-2xl font-bold text-red-700">{{ varianceStats.shortages }}</p>
            </div>
            <div class="p-4 bg-green-50 rounded-lg border border-green-200">
              <div class="flex items-center gap-2 mb-2">
                <TrendingUp class="w-5 h-5 text-green-600" />
                <span class="text-sm text-green-700">Overages</span>
              </div>
              <p class="text-2xl font-bold text-green-700">{{ varianceStats.overages }}</p>
            </div>
            <div class="p-4 bg-purple-50 rounded-lg border border-purple-200">
              <div class="flex items-center gap-2 mb-2">
                <DollarSign class="w-5 h-5 text-purple-600" />
                <span class="text-sm text-purple-700">Net Variance Value</span>
              </div>
              <p class="text-2xl font-bold text-purple-700">
                {{ formatCurrency(varianceStats.netVarianceValue) }}
              </p>
            </div>
          </div>

          <!-- Material Variances Alert -->
          <div v-if="varianceStats.materialVariances > 0" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-start gap-3">
              <AlertCircle class="w-5 h-5 text-red-600 mt-0.5" />
              <div>
                <p class="font-medium text-red-800">
                  {{ varianceStats.materialVariances }} Material Variance(s) Detected
                </p>
                <p class="text-sm text-red-600 mt-1">
                  These variances exceed the materiality thresholds and require investigation.
                </p>
                <Button variant="outline" size="sm" class="mt-2" @click="createVarianceCases">
                  Create Variance Cases
                </Button>
              </div>
            </div>
          </div>
        </div>

        <!-- Signoff Section -->
        <div class="bg-white rounded-lg border p-6">
          <SignoffSection
            :teamSignoff="session.team_signoff"
            :teamSignoffDate="session.team_signoff_date"
            :supervisorSignoff="session.supervisor_signoff"
            :supervisorSignoffDate="session.supervisor_signoff_date"
            :auditorSignoff="session.auditor_signoff"
            :auditorSignoffDate="session.auditor_signoff_date"
            :readonly="session.status === 'Approved'"
            @signoff="handleSignoff"
          />
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Quick Stats -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-gray-500">Progress</span>
              <span class="font-medium">{{ progressPercent }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${progressPercent}%` }"
              ></div>
            </div>
            <div class="pt-2 space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-gray-500">Items with Issues</span>
                <span class="font-medium text-yellow-600">{{ itemsWithIssues }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-500">Accuracy Rate</span>
                <span class="font-medium text-green-600">{{ accuracyRate }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Session Timeline -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
          <div class="space-y-4">
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Calendar class="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <p class="font-medium">Scheduled</p>
                <p class="text-sm text-gray-500">{{ formatDate(session.scheduled_date) }}</p>
              </div>
            </div>
            <div v-if="session.start_time" class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <Play class="w-4 h-4 text-green-600" />
              </div>
              <div>
                <p class="font-medium">Started</p>
                <p class="text-sm text-gray-500">{{ formatDateTime(session.start_time) }}</p>
              </div>
            </div>
            <div v-if="session.end_time" class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                <CheckCircle class="w-4 h-4 text-purple-600" />
              </div>
              <div>
                <p class="font-medium">Completed</p>
                <p class="text-sm text-gray-500">{{ formatDateTime(session.end_time) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Related Variance Cases -->
        <div v-if="varianceCases.length > 0" class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Variance Cases</h3>
          <div class="space-y-3">
            <div 
              v-for="vc in varianceCases" 
              :key="vc.name"
              class="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100"
              @click="viewVarianceCase(vc.name)"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="font-medium text-sm">{{ vc.name }}</span>
                <Badge :variant="getCaseStatusVariant(vc.status)" size="sm">
                  {{ vc.status }}
                </Badge>
              </div>
              <p class="text-sm text-gray-500">{{ vc.item_code }} - {{ vc.item_name }}</p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
          <div class="space-y-2">
            <Button variant="outline" class="w-full justify-start" @click="printCountSheet">
              <Printer class="w-4 h-4 mr-2" />
              Print Count Sheet
            </Button>
            <Button variant="outline" class="w-full justify-start" @click="exportToExcel">
              <Download class="w-4 h-4 mr-2" />
              Export to Excel
            </Button>
            <Button variant="outline" class="w-full justify-start" @click="viewAuditLog">
              <History class="w-4 h-4 mr-2" />
              View Audit Log
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
	PhysicalCountTable,
	SignoffSection,
} from "@/components/inventory-audit"
import { Badge, Button } from "frappe-ui"
import { call } from "frappe-ui"
import {
	AlertCircle,
	AlertTriangle,
	ArrowLeft,
	Calendar,
	CheckCircle,
	ClipboardList,
	DollarSign,
	Download,
	Edit,
	ExternalLink,
	History,
	Play,
	Printer,
	TrendingDown,
	TrendingUp,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const session = ref(null)
const varianceCases = ref([])

onMounted(async () => {
	await loadSession()
	await loadVarianceCases()
})

async function loadSession() {
	loading.value = true
	try {
		const doc = await call("frappe.client.get", {
			doctype: "Stock Take Session",
			name: route.params.id,
		})
		session.value = doc
	} catch (error) {
		console.error("Error loading session:", error)
	} finally {
		loading.value = false
	}
}

async function loadVarianceCases() {
	try {
		const cases = await call("frappe.client.get_list", {
			doctype: "Inventory Variance Case",
			filters: { stock_take_session: route.params.id },
			fields: [
				"name",
				"item_code",
				"item_name",
				"status",
				"variance_qty",
				"variance_value",
			],
		})
		varianceCases.value = cases
	} catch (error) {
		console.error("Error loading variance cases:", error)
	}
}

const statusVariant = computed(() => {
	const variants = {
		Scheduled: "subtle",
		"In Progress": "outline",
		"Pending Review": "warning",
		Completed: "success",
		Approved: "success",
		Cancelled: "subtle",
	}
	return variants[session.value?.status] || "subtle"
})

const totalItems = computed(() => session.value?.count_items?.length || 0)

const countedItems = computed(() => {
	if (!session.value?.count_items) return 0
	return session.value.count_items.filter(
		(i) => i.counted_qty !== null && i.counted_qty !== undefined,
	).length
})

const progressPercent = computed(() => {
	if (totalItems.value === 0) return 0
	return Math.round((countedItems.value / totalItems.value) * 100)
})

const itemsWithIssues = computed(() => {
	if (!session.value?.count_items) return 0
	return session.value.count_items.filter(
		(i) => i.condition && i.condition !== "Good",
	).length
})

const accuracyRate = computed(() => {
	if (countedItems.value === 0) return 100
	const accurateItems =
		session.value?.count_items?.filter((i) => i.variance_qty === 0).length || 0
	return Math.round((accurateItems / countedItems.value) * 100)
})

const varianceStats = computed(() => {
	if (!session.value?.count_items) {
		return {
			totalVariances: 0,
			shortages: 0,
			overages: 0,
			netVarianceValue: 0,
			materialVariances: 0,
		}
	}

	const items = session.value.count_items.filter((i) => i.variance_qty !== 0)
	return {
		totalVariances: items.length,
		shortages: items.filter((i) => (i.variance_qty || 0) < 0).length,
		overages: items.filter((i) => (i.variance_qty || 0) > 0).length,
		netVarianceValue: items.reduce(
			(sum, i) => sum + (i.variance_value || 0),
			0,
		),
		materialVariances: items.filter((i) => i.is_material).length,
	}
})

function formatDate(date) {
	if (!date) return "-"
	return new Date(date).toLocaleDateString()
}

function formatDateTime(datetime) {
	if (!datetime) return "-"
	return new Date(datetime).toLocaleString()
}

function formatCurrency(value) {
	if (value === null || value === undefined) return "-"
	return new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
	}).format(value)
}

function getCaseStatusVariant(status) {
	const variants = {
		Open: "warning",
		"Under Investigation": "outline",
		Resolved: "success",
		"Written Off": "subtle",
		Closed: "subtle",
	}
	return variants[status] || "subtle"
}

function goBack() {
	router.push("/inventory-audit/sessions")
}

function editSession() {
	router.push(`/inventory-audit/sessions/${route.params.id}/edit`)
}

function viewAuditPlan() {
	if (session.value?.audit_plan) {
		router.push(`/inventory-audit/plans/${session.value.audit_plan}`)
	}
}

function viewVarianceCase(name) {
	router.push(`/inventory-audit/variance-cases/${name}`)
}

async function startCount() {
	try {
		await call("frappe.client.set_value", {
			doctype: "Stock Take Session",
			name: route.params.id,
			fieldname: {
				status: "In Progress",
				start_time: new Date().toISOString(),
			},
		})
		await loadSession()
	} catch (error) {
		console.error("Error starting count:", error)
	}
}

async function submitForReview() {
	try {
		await call("frappe.client.set_value", {
			doctype: "Stock Take Session",
			name: route.params.id,
			fieldname: {
				status: "Pending Review",
				end_time: new Date().toISOString(),
			},
		})
		await loadSession()
	} catch (error) {
		console.error("Error submitting for review:", error)
	}
}

async function handleCountItemsUpdate(items) {
	// Auto-save count items
	try {
		await call("frappe.client.set_value", {
			doctype: "Stock Take Session",
			name: route.params.id,
			fieldname: { count_items: items },
		})
	} catch (error) {
		console.error("Error saving count items:", error)
	}
}

async function handleSignoff(type) {
	const fieldMap = {
		team: { team_signoff: 1, team_signoff_date: new Date().toISOString() },
		supervisor: {
			supervisor_signoff: 1,
			supervisor_signoff_date: new Date().toISOString(),
		},
		auditor: {
			auditor_signoff: 1,
			auditor_signoff_date: new Date().toISOString(),
		},
	}

	try {
		await call("frappe.client.set_value", {
			doctype: "Stock Take Session",
			name: route.params.id,
			fieldname: fieldMap[type],
		})
		await loadSession()
	} catch (error) {
		console.error("Error applying signoff:", error)
	}
}

function createVarianceCases() {
	// Navigate to create variance cases from material variances
	router.push(
		`/inventory-audit/sessions/${route.params.id}/create-variance-cases`,
	)
}

function printCountSheet() {
	window.open(
		`/api/method/frappe.utils.print_format.download_pdf?doctype=Stock Take Session&name=${route.params.id}&format=Count Sheet`,
		"_blank",
	)
}

function exportToExcel() {
	// Implementation for Excel export
	console.log("Export to Excel")
}

function viewAuditLog() {
	// Show audit log modal
	console.log("View Audit Log")
}
</script>
