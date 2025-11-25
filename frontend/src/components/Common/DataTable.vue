<template>
  <div class="w-full">
    <!-- Table Header -->
    <div class="flex items-center justify-between border-b border-gray-200 bg-gray-50 px-4 py-3">
      <div class="flex items-center space-x-4">
        <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
        <Badge v-if="totalRows" variant="secondary">
          {{ totalRows }} {{ totalRows === 1 ? 'record' : 'records' }}
        </Badge>
      </div>

      <div class="flex items-center space-x-2">
        <!-- Search -->
        <div class="relative">
          <SearchIcon class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            v-model="searchQuery"
            placeholder="Search..."
            class="w-64 pl-10"
            @input="handleSearch"
          />
        </div>

        <!-- Filters -->
        <Button
          v-if="showFilters"
          variant="outline"
          @click="showFilterDialog = true"
        >
          <FilterIcon class="h-4 w-4" />
          Filters
        </Button>

        <!-- Export -->
        <Button
          v-if="exportable"
          variant="outline"
          @click="handleExport"
        >
          <DownloadIcon class="h-4 w-4" />
          Export
        </Button>

        <!-- Bulk Actions -->
        <div v-if="selectedRows.length > 0" class="flex items-center space-x-2">
          <span class="text-sm text-gray-600">
            {{ selectedRows.length }} selected
          </span>
          <Button
            v-for="action in bulkActions"
            :key="action.key"
            variant="outline"
            size="sm"
            @click="handleBulkAction(action)"
          >
            {{ action.label }}
          </Button>
        </div>
      </div>
    </div>

    <!-- Table Content -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <!-- Table Header -->
        <thead class="bg-gray-50">
          <tr>
            <!-- Selection Column -->
            <th v-if="selectable" class="w-12 px-6 py-3">
              <Checkbox
                :model-value="allSelected"
                @update:model-value="toggleAllSelection"
              />
            </th>

            <!-- Data Columns -->
            <th
              v-for="column in visibleColumns"
              :key="column.key"
              class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
              :class="{ 'cursor-pointer hover:bg-gray-100': column.sortable }"
              @click="column.sortable && handleSort(column.key)"
            >
              <div class="flex items-center space-x-1">
                <span>{{ column.label }}</span>
                <div v-if="column.sortable" class="flex flex-col">
                  <ChevronUpIcon
                    class="h-3 w-3"
                    :class="{ 'text-blue-600': sortField === column.key && sortOrder === 'asc' }"
                  />
                  <ChevronDownIcon
                    class="h-3 w-3 -mt-1"
                    :class="{ 'text-blue-600': sortField === column.key && sortOrder === 'desc' }"
                  />
                </div>
              </div>
            </th>

            <!-- Actions Column -->
            <th v-if="rowActions.length > 0" class="w-32 px-6 py-3 text-right">
              Actions
            </th>
          </tr>
        </thead>

        <!-- Table Body -->
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr
            v-for="row in paginatedData"
            :key="row.name || row.id"
            class="hover:bg-gray-50"
            :class="{ 'bg-blue-50': selectedRows.includes(row.name || row.id) }"
          >
            <!-- Selection Column -->
            <td v-if="selectable" class="px-6 py-4">
              <Checkbox
                :model-value="selectedRows.includes(row.name || row.id)"
                @update:model-value="toggleRowSelection(row.name || row.id)"
              />
            </td>

            <!-- Data Columns -->
            <td
              v-for="column in visibleColumns"
              :key="column.key"
              class="px-6 py-4 text-sm text-gray-900"
            >
              <slot
                :name="`column-${column.key}`"
                :row="row"
                :value="getCellValue(row, column)"
              >
                {{ formatCellValue(getCellValue(row, column), column) }}
              </slot>
            </td>

            <!-- Actions Column -->
            <td v-if="rowActions.length > 0" class="px-6 py-4 text-right">
              <Dropdown :options="getRowActions(row)">
                <Button variant="ghost" size="sm">
                  <MoreHorizontalIcon class="h-4 w-4" />
                </Button>
              </Dropdown>
            </td>
          </tr>

          <!-- Empty State -->
          <tr v-if="paginatedData.length === 0">
            <td
              :colspan="totalColumns"
              class="px-6 py-12 text-center text-gray-500"
            >
              <div class="flex flex-col items-center space-y-2">
                <DatabaseIcon class="h-8 w-8 text-gray-400" />
                <p>{{ emptyMessage }}</p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Table Footer -->
    <div v-if="showPagination" class="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3">
      <!-- Page Size Selector -->
      <div class="flex items-center space-x-2">
        <span class="text-sm text-gray-700">Rows per page:</span>
        <Select
          v-model="pageSize"
          :options="pageSizeOptions"
          class="w-20"
        />
      </div>

      <!-- Pagination Info -->
      <div class="text-sm text-gray-700">
        {{ paginationInfo }}
      </div>

      <!-- Pagination Controls -->
      <div class="flex items-center space-x-2">
        <Button
          variant="outline"
          size="sm"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          <ChevronLeftIcon class="h-4 w-4" />
          Previous
        </Button>

        <div class="flex items-center space-x-1">
          <Button
            v-for="page in visiblePages"
            :key="page"
            variant="outline"
            size="sm"
            :class="{ 'bg-blue-600 text-white': page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </Button>
        </div>

        <Button
          variant="outline"
          size="sm"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          Next
          <ChevronRightIcon class="h-4 w-4" />
        </Button>
      </div>
    </div>

    <!-- Filter Dialog -->
    <Dialog
      v-model="showFilterDialog"
      title="Filter Data"
      :options="{
        size: 'lg'
      }"
    >
      <template #body>
        <div class="space-y-4">
          <div v-for="filter in availableFilters" :key="filter.key" class="grid grid-cols-3 gap-4 items-end">
            <div>
              <label class="block text-sm font-medium text-gray-700">{{ filter.label }}</label>
              <Select
                v-model="activeFilters[filter.key].operator"
                :options="filterOperators"
                placeholder="Operator"
              />
            </div>
            <div>
              <Input
                v-model="activeFilters[filter.key].value"
                :placeholder="filter.placeholder || 'Value'"
                :type="filter.type || 'text'"
              />
            </div>
            <div>
              <Button
                variant="outline"
                size="sm"
                @click="removeFilter(filter.key)"
              >
                <XIcon class="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div class="flex justify-between">
            <Button variant="outline" @click="clearAllFilters">
              Clear All
            </Button>
            <div class="space-x-2">
              <Button variant="outline" @click="showFilterDialog = false">
                Cancel
              </Button>
              <Button @click="applyFilters">
                Apply Filters
              </Button>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import {
	Badge,
	Button,
	Checkbox,
	Dialog,
	Dropdown,
	Input,
	Select,
} from "frappe-ui"
import {
	ChevronDownIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	ChevronUpIcon,
	DatabaseIcon,
	DownloadIcon,
	FilterIcon,
	MoreHorizontalIcon,
	SearchIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, ref, watch } from "vue"

// Props
const props = defineProps({
	title: {
		type: String,
		default: "Data Table",
	},
	columns: {
		type: Array,
		required: true,
	},
	data: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
	selectable: {
		type: Boolean,
		default: false,
	},
	exportable: {
		type: Boolean,
		default: true,
	},
	showFilters: {
		type: Boolean,
		default: true,
	},
	showPagination: {
		type: Boolean,
		default: true,
	},
	pageSize: {
		type: Number,
		default: 10,
	},
	emptyMessage: {
		type: String,
		default: "No data available",
	},
	rowActions: {
		type: Array,
		default: () => [],
	},
	bulkActions: {
		type: Array,
		default: () => [],
	},
	availableFilters: {
		type: Array,
		default: () => [],
	},
})

// Emits
const emit = defineEmits([
	"sort",
	"filter",
	"export",
	"row-action",
	"bulk-action",
	"selection-change",
])

// Reactive state
const searchQuery = ref("")
const sortField = ref("")
const sortOrder = ref("asc")
const currentPage = ref(1)
const pageSize = ref(props.pageSize)
const selectedRows = ref([])
const showFilterDialog = ref(false)
const activeFilters = ref({})

// Computed properties
const visibleColumns = computed(() => {
	return props.columns.filter((col) => !col.hidden)
})

const totalColumns = computed(() => {
	let count = visibleColumns.value.length
	if (props.selectable) count++
	if (props.rowActions.length > 0) count++
	return count
})

const filteredData = computed(() => {
	let result = [...props.data]

	// Apply search
	if (searchQuery.value) {
		result = result.filter((row) =>
			Object.values(row).some((value) =>
				String(value).toLowerCase().includes(searchQuery.value.toLowerCase()),
			),
		)
	}

	// Apply filters
	Object.entries(activeFilters.value).forEach(([key, filter]) => {
		if (filter.value) {
			result = result.filter((row) => {
				const cellValue = getCellValue(row, { key })
				return applyFilter(cellValue, filter)
			})
		}
	})

	// Apply sorting
	if (sortField.value) {
		result.sort((a, b) => {
			const aValue = getCellValue(a, { key: sortField.value })
			const bValue = getCellValue(b, { key: sortField.value })

			if (sortOrder.value === "asc") {
				return aValue > bValue ? 1 : -1
			} else {
				return aValue < bValue ? 1 : -1
			}
		})
	}

	return result
})

const paginatedData = computed(() => {
	if (!props.showPagination) return filteredData.value

	const start = (currentPage.value - 1) * pageSize.value
	const end = start + pageSize.value
	return filteredData.value.slice(start, end)
})

const totalRows = computed(() => filteredData.value.length)

const totalPages = computed(() => {
	return Math.ceil(totalRows.value / pageSize.value)
})

const visiblePages = computed(() => {
	const pages = []
	const maxVisible = 5
	let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
	const end = Math.min(totalPages.value, start + maxVisible - 1)

	if (end - start + 1 < maxVisible) {
		start = Math.max(1, end - maxVisible + 1)
	}

	for (let i = start; i <= end; i++) {
		pages.push(i)
	}

	return pages
})

const paginationInfo = computed(() => {
	const start = (currentPage.value - 1) * pageSize.value + 1
	const end = Math.min(currentPage.value * pageSize.value, totalRows.value)
	return `${start}-${end} of ${totalRows.value}`
})

const allSelected = computed(() => {
	return (
		selectedRows.value.length === paginatedData.value.length &&
		paginatedData.value.length > 0
	)
})

const pageSizeOptions = [
	{ label: "10", value: 10 },
	{ label: "25", value: 25 },
	{ label: "50", value: 50 },
	{ label: "100", value: 100 },
]

const filterOperators = [
	{ label: "Equals", value: "eq" },
	{ label: "Contains", value: "contains" },
	{ label: "Starts with", value: "startswith" },
	{ label: "Ends with", value: "endswith" },
	{ label: "Greater than", value: "gt" },
	{ label: "Less than", value: "lt" },
]

// Methods
const getCellValue = (row, column) => {
	if (typeof column.key === "function") {
		return column.key(row)
	}
	return row[column.key]
}

const formatCellValue = (value, column) => {
	if (column.formatter) {
		return column.formatter(value)
	}

	if (value === null || value === undefined) {
		return "-"
	}

	if (column.type === "date" && value) {
		return new Date(value).toLocaleDateString()
	}

	if (column.type === "currency" && value) {
		return new Intl.NumberFormat("en-US", {
			style: "currency",
			currency: "USD",
		}).format(value)
	}

	return String(value)
}

const handleSearch = () => {
	currentPage.value = 1
	emit("filter", { search: searchQuery.value, filters: activeFilters.value })
}

const handleSort = (field) => {
	if (sortField.value === field) {
		sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc"
	} else {
		sortField.value = field
		sortOrder.value = "asc"
	}
	emit("sort", { field: sortField.value, order: sortOrder.value })
}

const handleExport = () => {
	emit("export", {
		data: filteredData.value,
		columns: visibleColumns.value,
		filename: `${props.title.toLowerCase().replace(/\s+/g, "_")}_export`,
	})
}

const toggleRowSelection = (rowId) => {
	const index = selectedRows.value.indexOf(rowId)
	if (index > -1) {
		selectedRows.value.splice(index, 1)
	} else {
		selectedRows.value.push(rowId)
	}
	emit("selection-change", selectedRows.value)
}

const toggleAllSelection = (selected) => {
	if (selected) {
		selectedRows.value = paginatedData.value.map((row) => row.name || row.id)
	} else {
		selectedRows.value = []
	}
	emit("selection-change", selectedRows.value)
}

const getRowActions = (row) => {
	return props.rowActions.map((action) => ({
		...action,
		onClick: () => emit("row-action", { action: action.key, row }),
	}))
}

const handleBulkAction = (action) => {
	emit("bulk-action", { action: action.key, rows: selectedRows.value })
}

const goToPage = (page) => {
	currentPage.value = page
}

const applyFilters = () => {
	showFilterDialog.value = false
	currentPage.value = 1
	emit("filter", { search: searchQuery.value, filters: activeFilters.value })
}

const removeFilter = (key) => {
	delete activeFilters.value[key]
}

const clearAllFilters = () => {
	activeFilters.value = {}
	searchQuery.value = ""
	currentPage.value = 1
	emit("filter", { search: "", filters: {} })
}

const applyFilter = (value, filter) => {
	const { operator, filterValue } = filter

	switch (operator) {
		case "eq":
			return value == filterValue
		case "contains":
			return String(value)
				.toLowerCase()
				.includes(String(filterValue).toLowerCase())
		case "startswith":
			return String(value)
				.toLowerCase()
				.startsWith(String(filterValue).toLowerCase())
		case "endswith":
			return String(value)
				.toLowerCase()
				.endsWith(String(filterValue).toLowerCase())
		case "gt":
			return Number(value) > Number(filterValue)
		case "lt":
			return Number(value) < Number(filterValue)
		default:
			return true
	}
}

// Watchers
watch(
	() => props.pageSize,
	(newSize) => {
		pageSize.value = newSize
		currentPage.value = 1
	},
)

watch(
	() => props.data,
	() => {
		currentPage.value = 1
		selectedRows.value = []
	},
)
</script>