<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit Archive</h1>
        <p class="text-gray-600 mt-1">Archived audit documents and records</p>
      </div>
      <Button variant="outline" @click="fetchArchives">
        <RefreshCwIcon class="h-4 w-4 mr-2" />
        Refresh
      </Button>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="flex flex-wrap items-center gap-3">
        <FormControl type="text" v-model="search" placeholder="Search by name or type..." class="w-52" />
        <FormControl type="select" v-model="filterDoctype" :options="doctypeOptions" class="w-48" />
        <FormControl type="date" v-model="filterFromDate" placeholder="From Date" class="w-40" />
        <FormControl type="date" v-model="filterToDate" placeholder="To Date" class="w-40" />
        <Button variant="outline" size="sm" @click="resetFilters">Clear</Button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <!-- Archive List -->
    <div v-else-if="filteredArchives.length > 0" class="bg-white rounded-lg border border-gray-200 overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-200 bg-gray-50">
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Name</th>
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Original DocType</th>
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Original Document</th>
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Archived By</th>
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Archived On</th>
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Reason</th>
            <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="archive in paginatedArchives"
            :key="archive.name"
            class="border-b border-gray-100 hover:bg-gray-50"
          >
            <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ archive.name }}</td>
            <td class="px-4 py-3">
              <Badge variant="secondary">{{ archive.original_doctype }}</Badge>
            </td>
            <td class="px-4 py-3 text-sm text-gray-600">{{ archive.original_name }}</td>
            <td class="px-4 py-3 text-sm text-gray-600">{{ archive.archived_by }}</td>
            <td class="px-4 py-3 text-sm text-gray-600">{{ formatDateTime(archive.archived_on) }}</td>
            <td class="px-4 py-3 text-sm text-gray-600">{{ truncate(archive.archive_reason, 50) }}</td>
            <td class="px-4 py-3">
              <Button variant="outline" size="sm" @click="viewArchive(archive)">
                <EyeIcon class="h-3 w-3 mr-1" />
                View
              </Button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="filteredArchives.length > pageSize" class="flex items-center justify-between px-4 py-3 border-t border-gray-200">
        <span class="text-sm text-gray-600">
          {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, filteredArchives.length) }} of {{ filteredArchives.length }}
        </span>
        <div class="flex space-x-2">
          <Button variant="outline" size="sm" :disabled="currentPage <= 1" @click="currentPage--">Previous</Button>
          <Button variant="outline" size="sm" :disabled="currentPage >= totalPages" @click="currentPage++">Next</Button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="bg-white rounded-lg border border-gray-200 p-12 text-center">
      <ArchiveIcon class="h-12 w-12 text-gray-300 mx-auto mb-3" />
      <p class="text-gray-600">No archived documents found.</p>
    </div>

    <!-- Detail Dialog -->
    <Dialog v-model="showDetail" :options="{ title: 'Archived Document', size: 'xl' }">
      <template #body-content>
        <div v-if="archiveDetail" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-600">Original DocType</p>
              <p class="font-medium">{{ archiveDetail.original_doctype }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Original Name</p>
              <p class="font-medium">{{ archiveDetail.original_name }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Archived By</p>
              <p class="font-medium">{{ archiveDetail.archived_by }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Archived On</p>
              <p class="font-medium">{{ formatDateTime(archiveDetail.archived_on) }}</p>
            </div>
          </div>
          <div v-if="archiveDetail.archive_reason">
            <p class="text-sm text-gray-600 mb-1">Archive Reason</p>
            <p class="text-sm text-gray-700">{{ archiveDetail.archive_reason }}</p>
          </div>
          <div v-if="archiveDetail.archived_data">
            <p class="text-sm text-gray-600 mb-1">Archived Data</p>
            <pre class="bg-gray-900 text-green-400 rounded-lg p-4 text-sm overflow-x-auto max-h-96">{{ formatJSON(archiveDetail.archived_data) }}</pre>
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
	ArchiveIcon,
	EyeIcon,
	RefreshCwIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

const loading = ref(false)
const archives = ref([])
const showDetail = ref(false)
const archiveDetail = ref(null)
const search = ref("")
const filterDoctype = ref("")
const filterFromDate = ref("")
const filterToDate = ref("")
const currentPage = ref(1)
const pageSize = 25

const doctypeOptions = computed(() => {
	const types = [...new Set(archives.value.map((a) => a.original_doctype).filter(Boolean))]
	return [{ label: "All Types", value: "" }, ...types.map((t) => ({ label: t, value: t }))]
})

const filteredArchives = computed(() => {
	let result = archives.value
	if (search.value) {
		const q = search.value.toLowerCase()
		result = result.filter((a) => a.original_name?.toLowerCase().includes(q) || a.original_doctype?.toLowerCase().includes(q) || a.name?.toLowerCase().includes(q))
	}
	if (filterDoctype.value) result = result.filter((a) => a.original_doctype === filterDoctype.value)
	if (filterFromDate.value) result = result.filter((a) => a.archived_on >= filterFromDate.value)
	if (filterToDate.value) result = result.filter((a) => a.archived_on <= filterToDate.value + " 23:59:59")
	return result
})

const totalPages = computed(() => Math.ceil(filteredArchives.value.length / pageSize))
const paginatedArchives = computed(() => {
	const start = (currentPage.value - 1) * pageSize
	return filteredArchives.value.slice(start, start + pageSize)
})

const formatDateTime = (dt) => dt ? new Date(dt).toLocaleString() : "-"
const truncate = (str, len) => {
	if (!str) return "-"
	return str.length > len ? str.substring(0, len) + "..." : str
}
const formatJSON = (data) => {
	try { return JSON.stringify(JSON.parse(data), null, 2) } catch { return data }
}

const resetFilters = () => {
	search.value = ""
	filterDoctype.value = ""
	filterFromDate.value = ""
	filterToDate.value = ""
	currentPage.value = 1
}

const fetchArchives = async () => {
	loading.value = true
	try {
		const res = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Audit Archive",
				fields: ["name", "original_doctype", "original_name", "archived_by", "archived_on", "archive_reason"],
				order_by: "archived_on desc",
				limit_page_length: 500,
			},
		}).fetch()
		archives.value = res || []
	} catch (err) {
		console.error("Failed to fetch archives:", err)
	} finally {
		loading.value = false
	}
}

const viewArchive = async (archive) => {
	archiveDetail.value = null
	showDetail.value = true
	try {
		archiveDetail.value = await createResource({
			url: "frappe.client.get",
			params: { doctype: "Audit Archive", name: archive.name },
		}).fetch()
	} catch (err) {
		console.error("Failed to load archive:", err)
	}
}

onMounted(() => { fetchArchives() })
</script>
