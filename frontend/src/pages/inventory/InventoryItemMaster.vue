<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Inventory Item Master</h1>
        <p class="text-gray-600">Manage inventory items for stock take audits</p>
      </div>
      <div class="flex gap-2">
        <Button @click="refreshData" :loading="loading" variant="outline" size="sm">
          <RefreshCw class="w-4 h-4" />
        </Button>
        <Button @click="downloadTemplate" variant="outline" size="sm">
          <Download class="w-4 h-4 mr-2" />
          Template
        </Button>
        <Button @click="showImportModal = true" variant="outline" size="sm">
          <Upload class="w-4 h-4 mr-2" />
          Import
        </Button>
        <Button @click="createItem">
          <Plus class="w-4 h-4 mr-2" />
          New Item
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by item code..."
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @input="debouncedSearch"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
          <select
            v-model="filters.category"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @change="loadItems"
          >
            <option value="">All Categories</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ABC Class</label>
          <select
            v-model="filters.abc_classification"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @change="loadItems"
          >
            <option value="">All Classes</option>
            <option value="A - High Value">A - High Value</option>
            <option value="B - Medium Value">B - Medium Value</option>
            <option value="C - Low Value">C - Low Value</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filters.is_active"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            @change="loadItems"
          >
            <option value="">All</option>
            <option :value="1">Active</option>
            <option :value="0">Inactive</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Total Items</p>
        <p class="text-2xl font-bold">{{ totalCount }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">Active Items</p>
        <p class="text-2xl font-bold text-green-600">{{ items.filter(i => i.is_active).length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">A-Class Items</p>
        <p class="text-2xl font-bold text-blue-600">{{ items.filter(i => i.abc_classification === 'A - High Value').length }}</p>
      </div>
      <div class="bg-white rounded-lg border p-4">
        <p class="text-sm text-gray-500">High Risk</p>
        <p class="text-2xl font-bold text-red-600">{{ items.filter(i => i.risk_classification === 'High Risk').length }}</p>
      </div>
    </div>

    <!-- Items Table -->
    <div class="bg-white rounded-lg border shadow-sm">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item Code</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">UOM</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Valuation</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Warehouse</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ABC</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="item in items" 
              :key="item.name"
              class="hover:bg-gray-50 cursor-pointer"
              @click="viewItem(item.name)"
            >
              <td class="px-4 py-3 whitespace-nowrap">
                <span class="font-medium text-gray-900">{{ item.item_code }}</span>
              </td>
              <td class="px-4 py-3">
                <span class="text-gray-600 line-clamp-1">{{ item.item_description }}</span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-gray-500">{{ item.category }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-gray-500">{{ item.unit_of_measure }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-right text-gray-900">
                {{ formatCurrency(item.valuation_rate) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-gray-500">{{ item.warehouse }}</td>
              <td class="px-4 py-3 whitespace-nowrap">
                <Badge :variant="getABCVariant(item.abc_classification)">
                  {{ item.abc_classification?.charAt(0) || '-' }}
                </Badge>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <Badge :variant="item.is_active ? 'green' : 'gray'">
                  {{ item.is_active ? 'Active' : 'Inactive' }}
                </Badge>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-right">
                <Button variant="ghost" size="sm" @click.stop="editItem(item)">
                  <Edit2 class="w-4 h-4" />
                </Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div v-if="items.length === 0 && !loading" class="p-12 text-center text-gray-500">
        <Package class="w-12 h-12 mx-auto mb-3 text-gray-300" />
        <p>No items found</p>
        <Button variant="outline" size="sm" class="mt-2" @click="createItem">
          Add First Item
        </Button>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-4 py-3 border-t flex items-center justify-between">
        <p class="text-sm text-gray-500">
          Showing {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalCount) }} of {{ totalCount }}
        </p>
        <div class="flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
          >
            Previous
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
          >
            Next
          </Button>
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <Dialog v-model="showImportModal" :options="{ title: 'Import Items from CSV' }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <p class="text-sm text-gray-600 mb-4">
              Upload a CSV file with your inventory items. 
              <a href="#" @click.prevent="downloadTemplate" class="text-blue-600 hover:underline">
                Download the template
              </a> to see the required format.
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">CSV File</label>
            <input
              type="file"
              accept=".csv"
              @change="handleFileSelect"
              class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>
          <div v-if="importResult" class="p-4 rounded-lg" :class="importResult.errors?.length ? 'bg-yellow-50' : 'bg-green-50'">
            <p class="font-medium" :class="importResult.errors?.length ? 'text-yellow-800' : 'text-green-800'">
              {{ importResult.imported }} items imported successfully
            </p>
            <div v-if="importResult.errors?.length" class="mt-2 text-sm text-yellow-700">
              <p class="font-medium">Errors ({{ importResult.total_errors }}):</p>
              <ul class="list-disc list-inside mt-1">
                <li v-for="(error, i) in importResult.errors.slice(0, 5)" :key="i">{{ error }}</li>
                <li v-if="importResult.errors.length > 5">...and {{ importResult.errors.length - 5 }} more</li>
              </ul>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showImportModal = false">Cancel</Button>
        <Button @click="importItems" :loading="importing" :disabled="!selectedFile">Import</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { useInventoryAuditStore } from "@/stores/useInventoryAuditStore"
import { Badge, Button, Dialog } from "frappe-ui"
import {
	Download,
	Edit2,
	Package,
	Plus,
	RefreshCw,
	Upload,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const store = useInventoryAuditStore()

const loading = ref(false)
const importing = ref(false)
const showImportModal = ref(false)
const selectedFile = ref(null)
const importResult = ref(null)
const searchQuery = ref("")

const filters = ref({
	category: "",
	abc_classification: "",
	is_active: "",
})

const categories = ref([
	"Electronics",
	"Raw Materials",
	"Finished Goods",
	"Consumables",
	"Packaging",
])

const items = computed(() => store.items)
const totalCount = computed(() => store.itemsTotalCount)
const currentPage = computed(() => store.itemsPage)
const pageSize = computed(() => store.itemsPageSize)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

onMounted(async () => {
	await loadItems()
})

async function loadItems() {
	loading.value = true
	try {
		const filterObj = { ...filters.value }
		if (searchQuery.value) {
			filterObj.search = searchQuery.value
		}
		// Remove empty filters
		Object.keys(filterObj).forEach((key) => {
			if (filterObj[key] === "") delete filterObj[key]
		})
		await store.loadItems(filterObj, currentPage.value, pageSize.value)
	} finally {
		loading.value = false
	}
}

async function refreshData() {
	searchQuery.value = ""
	filters.value = { category: "", abc_classification: "", is_active: "" }
	await loadItems()
}

let searchTimeout = null
function debouncedSearch() {
	clearTimeout(searchTimeout)
	searchTimeout = setTimeout(() => {
		loadItems()
	}, 300)
}

async function changePage(page) {
	await store.loadItems(filters.value, page, pageSize.value)
}

async function downloadTemplate() {
	try {
		const result = await store.getItemImportTemplate()
		const blob = new Blob([result.content], { type: "text/csv" })
		const url = URL.createObjectURL(blob)
		const a = document.createElement("a")
		a.href = url
		a.download = result.filename
		a.click()
		URL.revokeObjectURL(url)
	} catch (error) {
		console.error("Error downloading template:", error)
	}
}

function handleFileSelect(event) {
	selectedFile.value = event.target.files[0]
	importResult.value = null
}

async function importItems() {
	if (!selectedFile.value) return

	importing.value = true
	try {
		const content = await selectedFile.value.text()
		importResult.value = await store.importItemsFromCSV(content)
		if (!importResult.value.errors?.length) {
			showImportModal.value = false
		}
	} catch (error) {
		console.error("Error importing items:", error)
	} finally {
		importing.value = false
	}
}

function createItem() {
	router.push("/inventory-audit/items/new")
}

function viewItem(name) {
	router.push(`/inventory-audit/items/${name}`)
}

function editItem(item) {
	router.push(`/inventory-audit/items/${item.name}/edit`)
}

function formatCurrency(amount) {
	return new Intl.NumberFormat("en-US", {
		style: "currency",
		currency: "KES",
		minimumFractionDigits: 0,
	}).format(amount || 0)
}

function getABCVariant(classification) {
	if (classification?.includes("A")) return "red"
	if (classification?.includes("B")) return "yellow"
	return "gray"
}
</script>
