<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Tax Compliance</h1>
        <p class="text-gray-600">Track tax compliance, filings, and payments across all tax types.</p>
      </div>
      <Button @click="showCreateTrackerDialog = true" class="flex items-center gap-2">
        <Plus class="w-4 h-4" />
        Create Tracker
      </Button>
    </div>

    <!-- Summary Cards -->
    <div v-if="taxComplianceSummary" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white p-4 rounded-lg border shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Total Trackers</p>
            <p class="text-2xl font-bold">{{ taxComplianceSummary.totalTrackers }}</p>
          </div>
          <FileText class="w-8 h-8 text-blue-500" />
        </div>
      </div>
      <div class="bg-white p-4 rounded-lg border shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Avg Compliance Score</p>
            <p class="text-2xl font-bold" :class="getScoreColor(taxComplianceSummary.averageScore)">
              {{ taxComplianceSummary.averageScore }}%
            </p>
          </div>
          <TrendingUp class="w-8 h-8 text-green-500" />
        </div>
      </div>
      <div class="bg-white p-4 rounded-lg border shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">VAT Returns Filed</p>
            <p class="text-2xl font-bold">{{ taxComplianceSummary.filings.vat }}</p>
          </div>
          <Receipt class="w-8 h-8 text-purple-500" />
        </div>
      </div>
      <div class="bg-white p-4 rounded-lg border shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">PAYE Returns Filed</p>
            <p class="text-2xl font-bold">{{ taxComplianceSummary.filings.paye }}</p>
          </div>
          <Users class="w-8 h-8 text-orange-500" />
        </div>
      </div>
    </div>

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
        <Button @click="showCreateTrackerDialog = true" class="mt-4">
          Create Your First Tracker
        </Button>
      </div>
    </div>

    <!-- Create Tracker Dialog -->
    <Dialog v-model="showCreateTrackerDialog" :options="{ title: 'Create Tax Compliance Tracker' }">
      <template #body-content>
        <div class="space-y-4">
          <FormControl label="Tax Period" v-model="newTracker.tax_period" type="link" doctype="Data Period" required />
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showCreateTrackerDialog = false">Cancel</Button>
        <Button @click="createTracker" :loading="creating">Create Tracker</Button>
      </template>
    </Dialog>

    <!-- Tracker Detail Dialog -->
    <Dialog v-model="showTrackerDetailDialog" :options="{ title: 'Tax Compliance Details', size: '5xl' }">
      <template #body-content>
        <div v-if="selectedTracker" class="space-y-6">
          <!-- Header -->
          <div class="grid grid-cols-3 gap-4">
            <div class="bg-blue-50 p-4 rounded-lg">
              <h3 class="font-semibold text-blue-800">Tracker Information</h3>
              <div class="mt-2 space-y-1 text-sm">
                <p><span class="font-medium">ID:</span> {{ selectedTracker.tracker_id }}</p>
                <p><span class="font-medium">Period:</span> {{ selectedTracker.tax_period }}</p>
                <p><span class="font-medium">Score:</span>
                  <Badge :variant="getScoreVariant(selectedTracker.compliance_score)" class="ml-2">
                    {{ selectedTracker.compliance_score || 0 }}%
                  </Badge>
                </p>
              </div>
            </div>
            <div class="bg-green-50 p-4 rounded-lg">
              <h3 class="font-semibold text-green-800">VAT Compliance</h3>
              <div class="mt-2 space-y-1 text-sm">
                <p><span class="font-medium">Net Payable:</span> {{ formatCurrency(selectedTracker.net_vat_payable) }}</p>
                <p><span class="font-medium">Return Filed:</span>
                  <CheckCircle v-if="selectedTracker.vat_return_filed" class="w-4 h-4 text-green-500 inline ml-1" />
                  <X v-else class="w-4 h-4 text-red-500 inline ml-1" />
                </p>
                <p v-if="selectedTracker.vat_filing_date"><span class="font-medium">Filed:</span> {{ formatDate(selectedTracker.vat_filing_date) }}</p>
              </div>
            </div>
            <div class="bg-purple-50 p-4 rounded-lg">
              <h3 class="font-semibold text-purple-800">PAYE Compliance</h3>
              <div class="mt-2 space-y-1 text-sm">
                <p><span class="font-medium">Total PAYE:</span> {{ formatCurrency(selectedTracker.total_paye) }}</p>
                <p><span class="font-medium">Return Filed:</span>
                  <CheckCircle v-if="selectedTracker.paye_return_filed" class="w-4 h-4 text-green-500 inline ml-1" />
                  <X v-else class="w-4 h-4 text-red-500 inline ml-1" />
                </p>
                <p v-if="selectedTracker.paye_filing_date"><span class="font-medium">Filed:</span> {{ formatDate(selectedTracker.paye_filing_date) }}</p>
              </div>
            </div>
          </div>

          <!-- Tax Sections -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- WHT Section -->
            <div class="border rounded-lg p-4">
              <h3 class="font-semibold mb-3">Withholding Tax (WHT)</h3>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span>Services:</span>
                  <span>{{ formatCurrency(selectedTracker.wht_on_services) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Rent:</span>
                  <span>{{ formatCurrency(selectedTracker.wht_on_rent) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Professional Fees:</span>
                  <span>{{ formatCurrency(selectedTracker.wht_on_professional_fees) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Other:</span>
                  <span>{{ formatCurrency(selectedTracker.other_wht) }}</span>
                </div>
                <hr class="my-2">
                <div class="flex justify-between font-medium">
                  <span>Total WHT:</span>
                  <span>{{ formatCurrency(selectedTracker.total_wht) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Return Filed:</span>
                  <CheckCircle v-if="selectedTracker.wht_return_filed" class="w-4 h-4 text-green-500" />
                  <X v-else class="w-4 h-4 text-red-500" />
                </div>
              </div>
            </div>

            <!-- Social Security Section -->
            <div class="border rounded-lg p-4">
              <h3 class="font-semibold mb-3">Social Security</h3>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span>NSSF Employee:</span>
                  <span>{{ formatCurrency(selectedTracker.employee_contributions) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>NSSF Employer:</span>
                  <span>{{ formatCurrency(selectedTracker.employer_contributions) }}</span>
                </div>
                <div class="flex justify-between font-medium">
                  <span>Total NSSF:</span>
                  <span>{{ formatCurrency(selectedTracker.total_nssf) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>NSSF Filed:</span>
                  <CheckCircle v-if="selectedTracker.nssf_return_filed" class="w-4 h-4 text-green-500" />
                  <X v-else class="w-4 h-4 text-red-500" />
                </div>
                <hr class="my-2">
                <div class="flex justify-between">
                  <span>NHIF Amount:</span>
                  <span>{{ formatCurrency(selectedTracker.total_nhif) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>NHIF Filed:</span>
                  <CheckCircle v-if="selectedTracker.nhif_return_filed" class="w-4 h-4 text-green-500" />
                  <X v-else class="w-4 h-4 text-red-500" />
                </div>
              </div>
            </div>
          </div>

          <!-- Issues -->
          <div v-if="selectedTracker.issues_identified && selectedTracker.issues_identified.length > 0">
            <h3 class="font-semibold text-red-600 mb-3">Issues Identified</h3>
            <div class="space-y-2">
              <div v-for="issue in selectedTracker.issues_identified" :key="issue.name" class="p-3 bg-red-50 border border-red-200 rounded">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <Badge :variant="getIssueTypeVariant(issue.issue_type)">
                        {{ issue.issue_type }}
                      </Badge>
                      <Badge :variant="issue.resolution_status === 'Resolved' ? 'green' : 'red'">
                        {{ issue.resolution_status }}
                      </Badge>
                    </div>
                    <p class="text-sm">{{ issue.description }}</p>
                    <p v-if="issue.financial_impact" class="text-sm font-medium text-red-600">
                      Impact: {{ formatCurrency(issue.financial_impact) }}
                    </p>
                    <p v-if="issue.resolution_notes" class="text-sm text-gray-600 mt-1">
                      {{ issue.resolution_notes }}
                    </p>
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
	CheckCircle,
	Edit,
	Eye,
	FileText,
	Plus,
	Receipt,
	RefreshCw,
	TrendingUp,
	Users,
	X,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useComplianceStore } from "../stores/compliance"

// Store
const complianceStore = useComplianceStore()

// Reactive data
const showCreateTrackerDialog = ref(false)
const showTrackerDetailDialog = ref(false)
const selectedTracker = ref(null)
const creating = ref(false)
const newTracker = ref({
	tax_period: "",
})

// Computed
const taxComplianceTrackers = computed(
	() => complianceStore.taxComplianceTrackers,
)
const taxComplianceSummary = computed(
	() => complianceStore.taxComplianceSummary,
)
const loading = computed(() => complianceStore.loading)

// Methods
const fetchTaxComplianceTrackers = async () => {
	await complianceStore.fetchTaxComplianceTrackers()
}

const createTracker = async () => {
	try {
		creating.value = true
		await complianceStore.createTaxComplianceTracker(newTracker.value)
		showCreateTrackerDialog.value = false
		newTracker.value = { tax_period: "" }
	} catch (error) {
		console.error("Error creating tracker:", error)
	} finally {
		creating.value = false
	}
}

const viewTracker = async (tracker) => {
	try {
		selectedTracker.value = await complianceStore.getTaxTrackerDetails(
			tracker.name,
		)
		showTrackerDetailDialog.value = true
	} catch (error) {
		console.error("Error fetching tracker details:", error)
	}
}

const editTracker = (tracker) => {
	// TODO: Implement edit functionality
	console.log("Edit tracker:", tracker)
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

const getIssueTypeVariant = (type) => {
	const variants = {
		"Late Filing": "red",
		"Late Payment": "red",
		Underpayment: "orange",
		Documentation: "yellow",
		Other: "gray",
	}
	return variants[type] || "gray"
}

const formatCurrency = (amount) => {
	if (amount === null || amount === undefined) return "KES 0.00"
	return new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
	}).format(amount)
}

const formatDate = (dateString) => {
	if (!dateString) return ""
	return new Date(dateString).toLocaleDateString()
}

// Lifecycle
onMounted(async () => {
	await fetchTaxComplianceTrackers()
})
</script>