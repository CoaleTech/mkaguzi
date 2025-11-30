<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <Button variant="ghost" @click="goBack">
          <ArrowLeft class="w-5 h-5" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">
            {{ isEdit ? 'Edit Stock Take' : 'New Stock Take' }}
          </h1>
          <p class="text-gray-500 mt-1">
            {{ isEdit ? `Editing ${route.params.id}` : 'Stock take for physical verification' }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="solid" @click="saveAudit" :loading="saving">
          <div class="flex items-center gap-2">
            <Save class="w-4 h-4" />
            <span>{{ isEdit ? 'Save Changes' : 'Create Stock Take' }}</span>
          </div>
        </Button>
      </div>
    </div>

    <!-- Form -->
    <div class="max-w-6xl">
      <div class="space-y-6">
        <!-- Basic Information -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Stock Take Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Stock Take Type <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="select"
                v-model="form.stock_take_type"
                :options="stockTakeTypeOptions"
                :disabled="isEdit"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Stock Take Date <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="date"
                v-model="form.audit_date"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Warehouse <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="select"
                v-model="form.warehouse"
                :options="warehouseOptions"
                placeholder="Select warehouse"
                @change="onWarehouseChange"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <FormControl
                type="select"
                v-model="form.status"
                :options="statusOptions"
                :disabled="true"
              />
            </div>
          </div>

          <!-- Deadlines -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Resolution Deadline</label>
              <div class="text-sm text-gray-600 bg-yellow-50 p-2 rounded">
                {{ resolutionDeadline || 'Deadline based on stock take type' }}
                <span class="text-yellow-700 ml-2">(Resolution required)</span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Investigation Deadline</label>
              <div class="text-sm text-gray-600 bg-blue-50 p-2 rounded">
                {{ investigationDeadline || '3 days from stock take date' }}
                <span class="text-blue-700 ml-2">(For items under investigation)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Import Section -->
        <div class="bg-white rounded-lg border p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Import Stock Items</h3>
            <div class="flex items-center gap-2">
              <Button variant="outline" size="sm" @click="downloadTemplate">
                <div class="flex items-center gap-2">
                  <Download class="w-4 h-4" />
                  <span>Download Template</span>
                </div>
              </Button>
              <Button variant="outline" size="sm" @click="showImportModal = true">
                <div class="flex items-center gap-2">
                  <Upload class="w-4 h-4" />
                  <span>Import from CSV</span>
                </div>
              </Button>
              <Button variant="outline" size="sm" @click="addItem">
                <div class="flex items-center gap-2">
                  <Plus class="w-4 h-4" />
                  <span>Add Item Manually</span>
                </div>
              </Button>
            </div>
          </div>

          <div class="text-sm text-gray-500 mb-4">
            Import stock items from Business Central CSV export. Download the template to see the required format. 
            Expected columns: Item Code, Description, System Qty, Item Value, Physical Qty, Pending Dispatch, Reason Provided
          </div>
        </div>

        <!-- Stock Take Items Table -->
        <div class="bg-white rounded-lg border p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Stock Take Items ({{ form.stock_take_items.length }})</h3>
            <div class="flex items-center gap-4 text-sm">
              <span class="text-gray-500">Pending: <strong class="text-yellow-600">{{ itemsPending }}</strong></span>
              <span class="text-gray-500">Verified: <strong class="text-green-600">{{ itemsVerified }}</strong></span>
              <span class="text-gray-500">Discrepancy: <strong class="text-red-600">{{ itemsDiscrepancy }}</strong></span>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">#</th>
                  <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item Code</th>
                  <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">System Qty</th>
                  <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">Item Value</th>
                  <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">Physical Qty</th>
                  <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">Pending Dispatch</th>
                  <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">Variance</th>
                  <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason Provided</th>
                  <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Proposed Resolution</th>
                  <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(item, index) in form.stock_take_items" :key="index" 
                    :class="getRowClass(item)"
                    class="hover:bg-gray-50">
                  <td class="px-3 py-3 text-sm text-gray-500">{{ index + 1 }}</td>
                  <td class="px-3 py-3">
                    <FormControl
                      type="text"
                      v-model="item.item_code"
                      placeholder="Item code"
                      class="w-32"
                    />
                  </td>
                  <td class="px-3 py-3">
                    <FormControl
                      type="text"
                      v-model="item.item_description"
                      placeholder="Description"
                      class="w-48"
                    />
                  </td>
                  <td class="px-3 py-3 text-right">
                    <FormControl
                      type="number"
                      v-model="item.system_quantity"
                      placeholder="0"
                      class="w-20 text-right"
                      :disabled="true"
                    />
                  </td>
                  <td class="px-3 py-3 text-right">
                    <FormControl
                      type="number"
                      v-model="item.unit_value"
                      placeholder="0.00"
                      class="w-20 text-right"
                      step="0.01"
                    />
                  </td>
                  <td class="px-3 py-3 text-right">
                    <FormControl
                      type="number"
                      v-model="item.physical_quantity"
                      placeholder="Count"
                      class="w-20 text-right"
                      @change="calculateVariance(index)"
                    />
                  </td>
                  <td class="px-3 py-3 text-right">
                    <FormControl
                      type="number"
                      v-model="item.pending_dispatch"
                      placeholder="0"
                      class="w-20 text-right"
                      @change="calculateVariance(index)"
                    />
                  </td>
                  <td class="px-3 py-3 text-right">
                    <span :class="item.variance_quantity !== 0 ? 'text-red-600 font-medium' : 'text-green-600'">
                      {{ item.variance_quantity || 0 }}
                    </span>
                  </td>
                  <td class="px-3 py-3">
                    <FormControl
                      type="text"
                      v-model="item.reason_provided"
                      placeholder="Reason for variance"
                      class="w-40"
                    />
                  </td>
                  <td class="px-3 py-3">
                    <FormControl
                      type="select"
                      v-model="item.resolution_type"
                      :options="resolutionOptions"
                      class="w-36"
                      :disabled="item.verification_status !== 'Verified-Discrepancy'"
                    />
                  </td>
                  <td class="px-3 py-3">
                    <div class="flex items-center gap-1">
                      <Button v-if="!item.physical_quantity && item.physical_quantity !== 0" 
                              variant="ghost" size="sm" @click="verifyItem(index, true)"
                              title="Mark as Match (Physical = System)">
                        <Check class="w-4 h-4 text-green-600" />
                      </Button>
                      <Button variant="ghost" size="sm" @click="removeItem(index)" title="Remove">
                        <Trash2 class="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
                  </td>
                  <td class="px-3 py-3">
                    <span :class="getStatusBadgeClass(item.verification_status)" class="px-2 py-1 text-xs rounded-full">
                      {{ item.verification_status || 'Pending' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="form.stock_take_items.length === 0">
                  <td colspan="12" class="px-4 py-8 text-center text-gray-500">
                    No stock take items. Import from CSV or add items manually.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Summary -->
          <div class="mt-4 pt-4 border-t bg-gray-50 -mx-6 -mb-6 px-6 py-4 rounded-b-lg">
            <div class="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
              <div>
                <span class="text-gray-500">Total Items:</span>
                <span class="font-semibold ml-2">{{ form.stock_take_items.length }}</span>
              </div>
              <div>
                <span class="text-gray-500">System Qty:</span>
                <span class="font-semibold ml-2">{{ totalSystemQty }}</span>
              </div>
              <div>
                <span class="text-gray-500">Physical Qty:</span>
                <span class="font-semibold ml-2">{{ totalPhysicalQty }}</span>
              </div>
              <div>
                <span class="text-gray-500">Total Variance:</span>
                <span class="font-semibold ml-2" :class="totalVariance !== 0 ? 'text-red-600' : 'text-green-600'">
                  {{ totalVariance }}
                </span>
              </div>
              <div>
                <span class="text-gray-500">Variance Value:</span>
                <span class="font-semibold ml-2 text-red-600">{{ formatCurrency(totalVarianceValue) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Notes -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Notes</h3>
          <FormControl
            type="textarea"
            v-model="form.notes"
            placeholder="Additional notes or observations from the stock take..."
            :rows="4"
          />
        </div>
      </div>

      <!-- Form Actions (Bottom) -->
      <div class="flex items-center justify-end gap-3 mt-6 pt-6 border-t">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="solid" @click="saveAudit" :loading="saving">
          <div class="flex items-center gap-2">
            <Save class="w-4 h-4" />
            <span>{{ isEdit ? 'Save Changes' : 'Create Stock Take' }}</span>
          </div>
        </Button>
      </div>
    </div>

    <!-- CSV Import Modal -->
    <Dialog v-model="showImportModal" :options="{ title: 'Import Stock Items from CSV' }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Upload CSV File</label>
            <input 
              type="file" 
              accept=".csv"
              @change="onFileSelected"
              class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>
          <div class="text-sm text-gray-500 bg-gray-50 p-3 rounded">
            <p class="font-medium mb-1">Expected CSV columns:</p>
            <p>Item Code, Description, System Qty, Item Value, Physical Qty, Pending Dispatch, Reason Provided</p>
          </div>
          <div v-if="csvPreview.length > 0" class="border rounded p-3">
            <p class="text-sm font-medium mb-2">Preview (first 5 rows):</p>
            <div class="overflow-x-auto text-xs">
              <table class="min-w-full">
                <thead>
                  <tr class="bg-gray-100">
                    <th v-for="col in csvHeaders" :key="col" class="px-2 py-1 text-left">{{ col }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in csvPreview.slice(0, 5)" :key="idx">
                    <td v-for="(val, col) in row" :key="col" class="px-2 py-1 border-t">{{ val }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showImportModal = false">Cancel</Button>
        <Button variant="solid" @click="confirmImport" :disabled="csvPreview.length === 0">
          Import {{ csvPreview.length }} Items
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Button, Dialog, FormControl } from "frappe-ui"
import { call } from "frappe-ui"
import {
	ArrowLeft,
	Check,
	Download,
	Plus,
	Save,
	Trash2,
	Upload,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

const route = useRoute()
const router = useRouter()

const saving = ref(false)
const warehouseOptions = ref([])
const showImportModal = ref(false)
const csvPreview = ref([])
const csvHeaders = ref([])
const csvContent = ref("")

const isEdit = computed(() => route.params.id && route.params.id !== "new")

const form = ref({
	stock_take_type: "Daily Stock Take",
	audit_date: new Date().toISOString().split("T")[0],
	warehouse: "",
	branch: "",
	status: "Draft",
	stock_take_items: [],
	notes: "",
})

const resolutionDeadline = computed(() => {
	if (!form.value.audit_date) return ""
	const date = new Date(form.value.audit_date)
	// Different deadlines based on stock take type
	const days =
		{
			"Sales Return": 0, // Same day
			"Daily Stock Take": 0, // Same day
			"Weekly Stock Take": 2, // 2 business days
			"Monthly Stock Take": 5, // 5 business days
		}[form.value.stock_take_type] || 0
	date.setDate(date.getDate() + days)
	return date.toISOString().split("T")[0]
})

const investigationDeadline = computed(() => {
	if (!form.value.audit_date) return ""
	const date = new Date(form.value.audit_date)
	date.setDate(date.getDate() + 3)
	return date.toISOString().split("T")[0]
})

const totalSystemQty = computed(() =>
	form.value.stock_take_items.reduce(
		(sum, item) => sum + (item.system_quantity || 0),
		0,
	),
)

const totalPhysicalQty = computed(() =>
	form.value.stock_take_items.reduce(
		(sum, item) => sum + (item.physical_quantity || 0),
		0,
	),
)

const totalVariance = computed(() =>
	form.value.stock_take_items.reduce(
		(sum, item) => sum + (item.variance_quantity || 0),
		0,
	),
)

const totalVarianceValue = computed(() =>
	form.value.stock_take_items.reduce(
		(sum, item) => sum + Math.abs(item.variance_value || 0),
		0,
	),
)

const itemsPending = computed(
	() =>
		form.value.stock_take_items.filter(
			(i) => !i.verification_status || i.verification_status === "Pending",
		).length,
)

const itemsVerified = computed(
	() =>
		form.value.stock_take_items.filter(
			(i) => i.verification_status === "Verified-Match",
		).length,
)

const itemsDiscrepancy = computed(
	() =>
		form.value.stock_take_items.filter(
			(i) => i.verification_status === "Verified-Discrepancy",
		).length,
)

onMounted(async () => {
	await loadWarehouses()
	if (isEdit.value) {
		await loadAudit()
	}
})

async function loadWarehouses() {
	try {
		const warehouses = await call("frappe.client.get_list", {
			doctype: "Warehouse Master",
			filters: { is_active: 1 },
			fields: ["name", "warehouse_code", "warehouse_name", "branch"],
			limit_page_length: 0,
		})
		warehouseOptions.value = warehouses.map((w) => ({
			label: `${w.warehouse_code} - ${w.warehouse_name}`,
			value: w.name,
			branch: w.branch,
		}))
	} catch (error) {
		console.error("Error loading warehouses:", error)
		warehouseOptions.value = []
	}
}

async function loadAudit() {
	try {
		const audit = await call("frappe.client.get", {
			doctype: "Stock Take Audit",
			name: route.params.id,
		})

		form.value = {
			stock_take_type: audit.stock_take_type || "Daily Stock Take",
			audit_date: audit.audit_date || "",
			warehouse: audit.warehouse || "",
			branch: audit.branch || "",
			status: audit.status || "Draft",
			stock_take_items: audit.stock_take_items || [],
			notes: audit.notes || "",
		}
	} catch (error) {
		console.error("Error loading audit:", error)
	}
}

function onWarehouseChange() {
	const wh = warehouseOptions.value.find(
		(w) => w.value === form.value.warehouse,
	)
	if (wh) {
		form.value.branch = wh.branch
	}
}

function addItem() {
	form.value.stock_take_items.push({
		item_code: "",
		item_description: "",
		system_quantity: 0,
		unit_value: 0,
		physical_quantity: null,
		pending_dispatch: 0,
		variance_quantity: 0,
		variance_value: 0,
		reason_provided: "",
		verification_status: "Pending",
		resolution_type: "",
	})
}

function removeItem(index) {
	form.value.stock_take_items.splice(index, 1)
}

function calculateVariance(index) {
	const item = form.value.stock_take_items[index]
	if (item.physical_quantity !== null && item.physical_quantity !== undefined) {
		// New variance formula: System Qty - Physical Qty - Pending Dispatch
		item.variance_quantity =
			(item.system_quantity || 0) -
			(item.physical_quantity || 0) -
			(item.pending_dispatch || 0)
		item.variance_value = item.variance_quantity * (item.unit_value || 0)

		// Auto-set verification status
		if (item.variance_quantity === 0) {
			item.verification_status = "Verified-Match"
		} else {
			item.verification_status = "Verified-Discrepancy"
		}
	}
}

function verifyItem(index, match) {
	const item = form.value.stock_take_items[index]
	if (match) {
		item.physical_quantity = item.system_quantity
		item.pending_dispatch = 0
		item.variance_quantity = 0
		item.variance_value = 0
		item.verification_status = "Verified-Match"
	}
}

function getRowClass(item) {
	if (item.verification_status === "Verified-Match") return "bg-green-50"
	if (item.verification_status === "Verified-Discrepancy") return "bg-red-50"
	return ""
}

function getStatusBadgeClass(status) {
	switch (status) {
		case "Verified-Match":
			return "bg-green-100 text-green-800"
		case "Verified-Discrepancy":
			return "bg-red-100 text-red-800"
		case "Resolved":
			return "bg-blue-100 text-blue-800"
		default:
			return "bg-yellow-100 text-yellow-800"
	}
}

function onFileSelected(event) {
	const file = event.target.files[0]
	if (!file) return

	const reader = new FileReader()
	reader.onload = (e) => {
		csvContent.value = e.target.result
		parseCSV(csvContent.value)
	}
	reader.readAsText(file)
}

function parseCSV(content) {
	const lines = content.split("\n").filter((line) => line.trim())
	if (lines.length < 2) return

	csvHeaders.value = lines[0].split(",").map((h) => h.trim().replace(/"/g, ""))
	csvPreview.value = lines.slice(1).map((line) => {
		const values = line.split(",").map((v) => v.trim().replace(/"/g, ""))
		const row = {}
		csvHeaders.value.forEach((h, i) => {
			row[h] = values[i] || ""
		})
		return row
	})
}

function downloadTemplate() {
	// Create sample CSV template with expected columns matching the table fields
	const headers = [
		"Item Code",
		"Description",
		"System Qty",
		"Item Value",
		"Physical Qty",
		"Pending Dispatch",
		"Reason Provided",
	]
	const sampleData = [
		[
			"ITEM001",
			"Sample Item 1",
			"100",
			"150.00",
			"95",
			"3",
			"Items in transit",
		],
		["ITEM002", "Sample Item 2", "50", "200.00", "52", "0", ""],
		["ITEM003", "Sample Item 3", "75", "75.50", "70", "2", "Damaged goods"],
	]

	// Combine headers and sample data
	const csvContent = [headers, ...sampleData]
		.map((row) => row.map((cell) => `"${cell}"`).join(","))
		.join("\n")

	// Create and download the file
	const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
	const link = document.createElement("a")
	const url = URL.createObjectURL(blob)
	link.setAttribute("href", url)
	link.setAttribute("download", "stock_take_template.csv")
	link.style.visibility = "hidden"
	document.body.appendChild(link)
	link.click()
	document.body.removeChild(link)
}

function confirmImport() {
	if (csvPreview.value.length === 0) return

	// Import items from CSV
	csvPreview.value.forEach((row) => {
		const item = {
			item_code: row["Item Code"] || "",
			item_description: row["Description"] || "",
			system_quantity: Number.parseFloat(row["System Qty"]) || 0,
			unit_value: Number.parseFloat(row["Item Value"]) || 0,
			physical_quantity: Number.parseFloat(row["Physical Qty"]) || null,
			pending_dispatch: Number.parseFloat(row["Pending Dispatch"]) || 0,
			reason_provided: row["Reason Provided"] || "",
			variance_quantity: 0,
			variance_value: 0,
			verification_status: "Pending",
			resolution_type: "",
		}

		// Calculate variance if physical quantity is provided
		if (
			item.physical_quantity !== null &&
			item.physical_quantity !== undefined
		) {
			item.variance_quantity =
				(item.system_quantity || 0) -
				(item.physical_quantity || 0) -
				(item.pending_dispatch || 0)
			item.variance_value = item.variance_quantity * (item.unit_value || 0)

			// Auto-set verification status
			if (item.variance_quantity === 0) {
				item.verification_status = "Verified-Match"
			} else {
				item.verification_status = "Verified-Discrepancy"
			}
		}

		form.value.stock_take_items.push(item)
	})

	// Close modal and reset
	showImportModal.value = false
	csvPreview.value = []
	csvHeaders.value = []
	csvContent.value = ""
}

function formatCurrency(value) {
	if (value === null || value === undefined) return "KES 0"
	return new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
	}).format(value)
}

async function saveAudit() {
	if (!form.value.audit_date) {
		alert("Stock take date is required")
		return
	}
	if (!form.value.warehouse) {
		alert("Warehouse is required")
		return
	}

	saving.value = true

	try {
		const docData = {
			doctype: "Stock Take Audit",
			stock_take_type: form.value.stock_take_type,
			audit_date: form.value.audit_date,
			warehouse: form.value.warehouse,
			branch: form.value.branch,
			notes: form.value.notes,
			stock_take_items: form.value.stock_take_items.map((item) => ({
				item_code: item.item_code,
				item_description: item.item_description,
				system_quantity: item.system_quantity,
				physical_quantity: item.physical_quantity,
				unit_value: item.unit_value,
				pending_dispatch: item.pending_dispatch,
				variance_quantity: item.variance_quantity,
				variance_value: item.variance_value,
				reason_provided: item.reason_provided,
				verification_status: item.verification_status,
				resolution_type: item.resolution_type,
			})),
		}

		if (isEdit.value) {
			await call("frappe.client.set_value", {
				doctype: "Stock Take Audit",
				name: route.params.id,
				fieldname: docData,
			})
			router.push(`/inventory-audit/stock-take/${route.params.id}`)
		} else {
			const result = await call("frappe.client.insert", { doc: docData })
			router.push(`/inventory-audit/stock-take/${result.name}`)
		}
	} catch (error) {
		console.error("Error saving audit:", error)
		alert("Error saving stock take: " + error.message)
	} finally {
		saving.value = false
	}
}

function goBack() {
	if (isEdit.value) {
		router.push(`/inventory-audit/stock-take/${route.params.id}`)
	} else {
		router.push("/inventory-audit/stock-take")
	}
}

const stockTakeTypeOptions = [
	{ label: "Sales Return", value: "Sales Return" },
	{ label: "Daily Stock Take", value: "Daily Stock Take" },
	{ label: "Weekly Stock Take", value: "Weekly Stock Take" },
	{ label: "Monthly Stock Take", value: "Monthly Stock Take" },
]

const statusOptions = [
	{ label: "Draft", value: "Draft" },
	{ label: "Physical Count Submitted", value: "Physical Count Submitted" },
	{ label: "Analyst Reviewed", value: "Analyst Reviewed" },
	{ label: "HOD Approved", value: "HOD Approved" },
	{ label: "Under Investigation", value: "Under Investigation" },
]

const resolutionOptions = [
	{ label: "Select Resolution...", value: "" },
	{ label: "Stock Amendment", value: "Stock Amendment" },
	{ label: "Charge Staff", value: "Charge Staff" },
	{ label: "Write-off", value: "Write-off" },
	{ label: "Under Investigation", value: "Under Investigation" },
]
</script>