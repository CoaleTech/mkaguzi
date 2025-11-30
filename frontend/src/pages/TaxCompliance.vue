<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Tax Compliance</h1>
        <p class="text-gray-600">Track tax compliance, filings, and payments across all tax types.</p>
      </div>
      <Button @click="createTracker" class="flex items-center gap-2">
        <Plus class="w-4 h-4" />
        Create Tracker
      </Button>
    </div>

    <!-- Summary Stats -->
    <TaxStats :stats="stats" />

    <!-- Filters -->
    <TaxFilters
      v-model:searchQuery="searchQuery"
      v-model:selectedTaxPeriod="selectedTaxPeriod"
      v-model:selectedComplianceScore="selectedComplianceScore"
      v-model:selectedVatStatus="selectedVatStatus"
      v-model:selectedPayeStatus="selectedPayeStatus"
    />

    <!-- Tax Compliance Trackers Table -->
    <div class="bg-white rounded-lg border shadow-sm">
      <div class="p-4 border-b">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold">Tax Compliance Trackers</h2>
          <div class="flex gap-2">
            <Button
              @click="fetchTaxComplianceTrackers"
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
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tracker ID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tax Period</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Compliance Score</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">VAT</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">PAYE</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">WHT</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">NSSF</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">NHIF</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="tracker in taxComplianceTrackers" :key="tracker.name" class="hover:bg-gray-50">
              <td class="px-4 py-3">
                <div class="font-medium">{{ tracker.tracker_id }}</div>
                <div class="text-sm text-gray-500">{{ tracker.name }}</div>
              </td>
              <td class="px-4 py-3">
                <div>{{ tracker.tax_period }}</div>
              </td>
              <td class="px-4 py-3">
                <Badge :variant="getScoreVariant(tracker.compliance_score)">
                  {{ tracker.compliance_score || 0 }}%
                </Badge>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1">
                  <CheckCircle v-if="tracker.vat_return_filed" class="w-4 h-4 text-green-500" />
                  <X v-else class="w-4 h-4 text-red-500" />
                  <span class="text-xs">Filed</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1">
                  <CheckCircle v-if="tracker.paye_return_filed" class="w-4 h-4 text-green-500" />
                  <X v-else class="w-4 h-4 text-red-500" />
                  <span class="text-xs">Filed</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1">
                  <CheckCircle v-if="tracker.wht_return_filed" class="w-4 h-4 text-green-500" />
                  <X v-else class="w-4 h-4 text-red-500" />
                  <span class="text-xs">Filed</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1">
                  <CheckCircle v-if="tracker.nssf_return_filed" class="w-4 h-4 text-green-500" />
                  <X v-else class="w-4 h-4 text-red-500" />
                  <span class="text-xs">Filed</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1">
                  <CheckCircle v-if="tracker.nhif_return_filed" class="w-4 h-4 text-green-500" />
                  <X v-else class="w-4 h-4 text-red-500" />
                  <span class="text-xs">Filed</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="flex gap-1">
                  <Button
                    @click="viewTracker(tracker)"
                    variant="outline"
                    size="sm"
                  >
                    <Eye class="w-4 h-4" />
                  </Button>
                  <Button
                    @click="editTracker(tracker)"
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

      <div v-if="taxComplianceTrackers.length === 0 && !loading" class="p-8 text-center text-gray-500">
        <Receipt class="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p>No tax compliance trackers found.</p>
        <Button @click="createTracker" class="mt-4">
          Create Your First Tracker
        </Button>
      </div>
    </div>

    <!-- Tax Compliance Form Dialog -->
    <TaxComplianceForm
      v-model:show="showFormDialog"
      :tracker-data="selectedTracker"
      :is-edit-mode="isEditMode"
      @saved="handleTrackerSaved"
    />
  </div>
</template>

<script setup>
import TaxComplianceForm from "@/components/taxcompliance/TaxComplianceForm.vue"
import TaxFilters from "@/components/taxcompliance/TaxFilters.vue"
import TaxStats from "@/components/taxcompliance/TaxStats.vue"
import { useComplianceStore } from "@/stores/compliance"
import { Badge, Button } from "frappe-ui"
import {
	CheckCircle,
	Edit,
	Eye,
	Plus,
	Receipt,
	RefreshCw,
	X,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

// Store
const complianceStore = useComplianceStore()

// Reactive data
const showFormDialog = ref(false)
const isEditMode = ref(false)
const selectedTracker = ref(null)

// Store bindings
const loading = computed(() => complianceStore.loading)
const taxComplianceTrackers = computed(
	() => complianceStore.taxComplianceTrackers,
)

// Filter bindings
const searchQuery = ref("")
const selectedTaxPeriod = ref("")
const selectedComplianceScore = ref("")
const selectedVatStatus = ref("")
const selectedPayeStatus = ref("")

// Stats computed from store data
const stats = computed(() => {
	const trackers = taxComplianceTrackers.value
	const totalTrackers = trackers.length
	const avgScore =
		totalTrackers > 0
			? Math.round(
					trackers.reduce((sum, t) => sum + (t.compliance_score || 0), 0) /
						totalTrackers,
				)
			: 0
	const vatFiled = trackers.filter((t) => t.vat_return_filed).length
	const payeFiled = trackers.filter((t) => t.paye_return_filed).length
	const compliant = trackers.filter(
		(t) => (t.compliance_score || 0) >= 80,
	).length

	return {
		total: totalTrackers,
		avgScore,
		vatFiled,
		payeFiled,
		compliant,
	}
})

// Methods
const fetchTaxComplianceTrackers = async () => {
	await complianceStore.fetchTaxComplianceTrackers()
}

const createTracker = () => {
	selectedTracker.value = null
	isEditMode.value = false
	showFormDialog.value = true
}

const viewTracker = async (tracker) => {
	try {
		selectedTracker.value = await complianceStore.getTaxTrackerDetails(
			tracker.name,
		)
		isEditMode.value = true
		showFormDialog.value = true
	} catch (error) {
		console.error("Error fetching tracker details:", error)
	}
}

const editTracker = async (tracker) => {
	try {
		selectedTracker.value = await complianceStore.getTaxTrackerDetails(
			tracker.name,
		)
		isEditMode.value = true
		showFormDialog.value = true
	} catch (error) {
		console.error("Error fetching tracker details:", error)
	}
}

const handleTrackerSaved = async () => {
	showFormDialog.value = false
	await fetchTaxComplianceTrackers()
}

const getScoreColor = (score) => {
	if (score >= 80) return "text-green-600"
	if (score >= 60) return "text-yellow-600"
	return "text-red-600"
}

const getScoreVariant = (score) => {
	if (score >= 80) return "green"
	if (score >= 60) return "yellow"
	return "red"
}

// Lifecycle
onMounted(async () => {
	await fetchTaxComplianceTrackers()
})
</script>