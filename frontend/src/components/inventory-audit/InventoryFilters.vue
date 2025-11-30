<template>
  <div class="inventory-filters bg-white rounded-lg border p-4">
    <div class="flex items-center justify-between mb-4">
      <h4 class="text-sm font-medium text-gray-700">Filters</h4>
      <Button
        v-if="hasActiveFilters"
        size="sm"
        variant="ghost"
        @click="clearFilters"
      >
        <X class="w-4 h-4 mr-1" />
        Clear
      </Button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Status Filter -->
      <div v-if="showFilter('status')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Status</label>
        <FormControl
          type="select"
          :options="statusOptions"
          v-model="filters.status"
          placeholder="All Statuses"
        />
      </div>

      <!-- Date Range Filter -->
      <div v-if="showFilter('date_range')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Date Range</label>
        <FormControl
          type="select"
          :options="dateRangeOptions"
          v-model="filters.date_range"
          placeholder="All Time"
        />
      </div>

      <!-- From Date -->
      <div v-if="showFilter('from_date') && filters.date_range === 'custom'">
        <label class="block text-xs font-medium text-gray-500 mb-1">From Date</label>
        <FormControl
          type="date"
          v-model="filters.from_date"
        />
      </div>

      <!-- To Date -->
      <div v-if="showFilter('to_date') && filters.date_range === 'custom'">
        <label class="block text-xs font-medium text-gray-500 mb-1">To Date</label>
        <FormControl
          type="date"
          v-model="filters.to_date"
        />
      </div>

      <!-- Warehouse Filter -->
      <div v-if="showFilter('warehouse')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Warehouse</label>
        <FormControl
          type="text"
          v-model="filters.warehouse"
          placeholder="All Warehouses"
        />
      </div>

      <!-- Branch Filter -->
      <div v-if="showFilter('branch')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Branch</label>
        <FormControl
          type="text"
          v-model="filters.branch"
          placeholder="All Branches"
        />
      </div>

      <!-- Auditor Filter -->
      <div v-if="showFilter('auditor')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Auditor</label>
        <FormControl
          type="autocomplete"
          :options="auditorOptions"
          v-model="filters.auditor"
          placeholder="All Auditors"
        />
      </div>

      <!-- Audit Period Filter -->
      <div v-if="showFilter('audit_period')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Audit Period</label>
        <FormControl
          type="select"
          :options="periodOptions"
          v-model="filters.audit_period"
          placeholder="All Periods"
        />
      </div>

      <!-- Audit Scope Filter -->
      <div v-if="showFilter('audit_scope')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Audit Scope</label>
        <FormControl
          type="select"
          :options="scopeOptions"
          v-model="filters.audit_scope"
          placeholder="All Scopes"
        />
      </div>

      <!-- Count Type Filter -->
      <div v-if="showFilter('count_type')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Count Type</label>
        <FormControl
          type="select"
          :options="countTypeOptions"
          v-model="filters.count_type"
          placeholder="All Types"
        />
      </div>

      <!-- Root Cause Filter -->
      <div v-if="showFilter('root_cause')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Root Cause</label>
        <FormControl
          type="select"
          :options="rootCauseOptions"
          v-model="filters.root_cause"
          placeholder="All Causes"
        />
      </div>

      <!-- Issue Type Filter -->
      <div v-if="showFilter('issue_type')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Issue Type</label>
        <FormControl
          type="select"
          :options="issueTypeOptions"
          v-model="filters.issue_type"
          placeholder="All Types"
        />
      </div>

      <!-- Severity Filter -->
      <div v-if="showFilter('severity')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Severity</label>
        <FormControl
          type="select"
          :options="severityOptions"
          v-model="filters.severity"
          placeholder="All Levels"
        />
      </div>

      <!-- SLA Status Filter -->
      <div v-if="showFilter('sla_status')">
        <label class="block text-xs font-medium text-gray-500 mb-1">SLA Status</label>
        <FormControl
          type="select"
          :options="slaStatusOptions"
          v-model="filters.sla_status"
          placeholder="All"
        />
      </div>

      <!-- Return Reason Filter -->
      <div v-if="showFilter('return_reason')">
        <label class="block text-xs font-medium text-gray-500 mb-1">Return Reason</label>
        <FormControl
          type="select"
          :options="returnReasonOptions"
          v-model="filters.return_reason"
          placeholder="All Reasons"
        />
      </div>

      <!-- Search -->
      <div v-if="showFilter('search')" class="md:col-span-2">
        <label class="block text-xs font-medium text-gray-500 mb-1">Search</label>
        <div class="relative">
          <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            v-model="filters.search"
            placeholder="Search..."
            class="w-full pl-10 pr-3 py-2 text-sm border rounded-lg focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
    </div>

    <!-- Apply Button -->
    <div class="flex justify-end mt-4 pt-4 border-t">
      <Button @click="applyFilters" variant="solid">
        <Filter class="w-4 h-4 mr-2" />
        Apply Filters
      </Button>
    </div>
  </div>
</template>

<script setup>
import { Button, FormControl } from "frappe-ui"
import { call } from "frappe-ui"
import { Filter, Search, X } from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		default: () => ({}),
	},
	enabledFilters: {
		type: Array,
		default: () => ["status", "date_range", "search"],
	},
	statusOptions: {
		type: Array,
		default: () => [],
	},
})

const emit = defineEmits(["update:modelValue", "apply", "clear"])

const filters = ref({ ...props.modelValue })

const auditorOptions = ref([])

onMounted(async () => {
	await loadAuditors()
})

async function loadAuditors() {
	try {
		const users = await call("frappe.client.get_list", {
			doctype: "User",
			filters: { enabled: 1, user_type: "System User" },
			fields: ["name", "full_name"],
			limit_page_length: 0,
		})
		auditorOptions.value = users.map((u) => ({
			label: u.full_name || u.name,
			value: u.name,
		}))
	} catch (error) {
		console.error("Error loading auditors:", error)
	}
}

watch(
	() => props.modelValue,
	(newVal) => {
		filters.value = { ...newVal }
	},
	{ deep: true },
)

function showFilter(name) {
	return props.enabledFilters.includes(name)
}

const hasActiveFilters = computed(() => {
	return Object.values(filters.value).some((v) => v && v !== "")
})

function clearFilters() {
	filters.value = {}
	emit("update:modelValue", {})
	emit("clear")
}

function applyFilters() {
	emit("update:modelValue", { ...filters.value })
	emit("apply", { ...filters.value })
}

// Static options
const dateRangeOptions = [
	{ label: "Today", value: "today" },
	{ label: "This Week", value: "this_week" },
	{ label: "This Month", value: "this_month" },
	{ label: "This Quarter", value: "this_quarter" },
	{ label: "This Year", value: "this_year" },
	{ label: "Last 7 Days", value: "last_7_days" },
	{ label: "Last 30 Days", value: "last_30_days" },
	{ label: "Custom", value: "custom" },
]

const periodOptions = [
	{ label: "Daily", value: "Daily" },
	{ label: "Weekly", value: "Weekly" },
	{ label: "Monthly", value: "Monthly" },
	{ label: "Quarterly", value: "Quarterly" },
	{ label: "Ad Hoc", value: "Ad Hoc" },
]

const scopeOptions = [
	{ label: "Cycle Count", value: "Cycle Count" },
	{ label: "Full Count", value: "Full Count" },
	{ label: "Sales Returns", value: "Sales Returns" },
	{ label: "Damaged Stock", value: "Damaged Stock" },
	{ label: "GRN Audit", value: "GRN Audit" },
	{ label: "Dispatch Audit", value: "Dispatch Audit" },
]

const countTypeOptions = [
	{ label: "Full Count", value: "Full Count" },
	{ label: "Cycle Count", value: "Cycle Count" },
	{ label: "Verification", value: "Verification" },
	{ label: "Ad Hoc", value: "Ad Hoc" },
]

const rootCauseOptions = [
	{ label: "Miscount", value: "Miscount" },
	{ label: "Theft", value: "Theft" },
	{ label: "Misplacement", value: "Misplacement" },
	{ label: "Wrong UOM", value: "Wrong UOM" },
	{ label: "Unrecorded Sales", value: "Unrecorded Sales" },
	{ label: "Unrecorded Receiving", value: "Unrecorded Receiving" },
	{ label: "Wrong Posting", value: "Wrong Posting" },
	{ label: "Expired/Damaged Stock", value: "Expired/Damaged Stock" },
	{ label: "System Error", value: "System Error" },
	{ label: "Data Entry Error", value: "Data Entry Error" },
]

const issueTypeOptions = [
	{ label: "Item Not Found", value: "Item Not Found" },
	{ label: "Mismatched Bin", value: "Mismatched Bin" },
	{ label: "Damaged Stock Unrecorded", value: "Damaged Stock Unrecorded" },
	{ label: "Expired Stock", value: "Expired Stock" },
	{ label: "Wrong UOM", value: "Wrong UOM" },
	{ label: "Missing GRN", value: "Missing GRN" },
	{ label: "Phantom Stock", value: "Phantom Stock" },
	{ label: "Negative Stock", value: "Negative Stock" },
	{ label: "Discrepancy in Transfer", value: "Discrepancy in Transfer" },
	{ label: "POS vs Inventory Mismatch", value: "POS vs Inventory Mismatch" },
]

const severityOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Medium", value: "Medium" },
	{ label: "High", value: "High" },
	{ label: "Critical", value: "Critical" },
]

const slaStatusOptions = [
	{ label: "On Track", value: "on_track" },
	{ label: "At Risk", value: "at_risk" },
	{ label: "Breached", value: "breached" },
]

const returnReasonOptions = [
	{ label: "Defective", value: "Defective" },
	{ label: "Wrong Item", value: "Wrong Item" },
	{ label: "Customer Changed Mind", value: "Customer Changed Mind" },
	{ label: "Expired", value: "Expired" },
	{ label: "Damaged", value: "Damaged" },
	{ label: "Other", value: "Other" },
]
</script>
