<template>
  <div class="table-section">
    <h4 v-if="section.config?.title" class="table-title">
      {{ section.config.title }}
    </h4>

    <div v-if="preview && !data" class="table-preview">
      <div class="preview-info">
        <TableIcon class="preview-icon" />
        <div class="preview-text">
          <h5>Data Table</h5>
          <p>Table will display data from: {{ section.config?.data_source || 'No data source configured' }}</p>
          <p v-if="section.config?.columns?.length">Columns: {{ section.config.columns.length }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="data && data.length > 0" class="data-table">
      <table class="report-table" :class="tableClasses">
        <thead>
          <tr>
            <th
              v-for="column in visibleColumns"
              :key="column.key"
              :style="getColumnStyle(column)"
            >
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in paginatedData" :key="index">
            <td
              v-for="column in visibleColumns"
              :key="column.key"
              :style="getColumnStyle(column)"
            >
              {{ formatCellValue(row[column.key], column) }}
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="section.config?.pagination && totalPages > 1" class="table-pagination">
        <Button
          variant="ghost"
          size="sm"
          @click="previousPage"
          :disabled="currentPage === 1"
        >
          Previous
        </Button>
        <span class="page-info">
          Page {{ currentPage }} of {{ totalPages }} ({{ data.length }} records)
        </span>
        <Button
          variant="ghost"
          size="sm"
          @click="nextPage"
          :disabled="currentPage === totalPages"
        >
          Next
        </Button>
      </div>
    </div>

    <div v-else class="empty-table">
      <TableIcon class="empty-icon" />
      <p>No data available for this table</p>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import { TableIcon } from "lucide-vue-next"
import { computed, ref } from "vue"

const props = defineProps({
	section: {
		type: Object,
		required: true,
	},
	data: {
		type: Array,
		default: () => [],
	},
	preview: {
		type: Boolean,
		default: true,
	},
})

const currentPage = ref(1)
const pageSize = 10

const visibleColumns = computed(() => {
	return props.section.config?.columns?.filter((col) => !col.hidden) || []
})

const tableClasses = computed(() => {
	const styling = props.section.config?.styling || {}
	const classes = ["data-table"]

	if (styling.striped) classes.push("table-striped")
	if (styling.bordered) classes.push("table-bordered")
	if (styling.hover) classes.push("table-hover")

	return classes.join(" ")
})

const totalPages = computed(() => {
	if (!props.section.config?.pagination) return 1
	return Math.ceil(props.data.length / pageSize)
})

const paginatedData = computed(() => {
	if (!props.section.config?.pagination) return props.data

	const start = (currentPage.value - 1) * pageSize
	const end = start + pageSize
	return props.data.slice(start, end)
})

const getColumnStyle = (column) => {
	const style = {}
	if (column.width) style.width = column.width
	if (column.align) style.textAlign = column.align
	return style
}

const formatCellValue = (value, column) => {
	if (value === null || value === undefined) return "-"

	switch (column.type) {
		case "currency":
			return new Intl.NumberFormat("en-US", {
				style: "currency",
				currency: column.currency || "USD",
			}).format(value)

		case "number":
			return new Intl.NumberFormat("en-US", {
				minimumFractionDigits: column.decimals || 0,
				maximumFractionDigits: column.decimals || 2,
			}).format(value)

		case "date":
			return new Date(value).toLocaleDateString()

		case "datetime":
			return new Date(value).toLocaleString()

		case "boolean":
			return value ? "Yes" : "No"

		case "percent":
			return `${(value * 100).toFixed(column.decimals || 1)}%`

		default:
			return String(value)
	}
}

const previousPage = () => {
	if (currentPage.value > 1) {
		currentPage.value--
	}
}

const nextPage = () => {
	if (currentPage.value < totalPages.value) {
		currentPage.value++
	}
}
</script>

<style scoped>
.table-section {
  margin: 1.5rem 0;
}

.table-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.table-preview {
  padding: 2rem;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  background: #f9fafb;
}

.preview-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  text-align: left;
}

.preview-icon {
  width: 3rem;
  height: 3rem;
  color: #6b7280;
  flex-shrink: 0;
}

.preview-text h5 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.preview-text p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0.25rem 0;
}

.data-table {
  overflow-x: auto;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  background: white;
}

.report-table th {
  background: #f3f4f6;
  color: #1f2937;
  font-weight: 600;
  padding: 0.75rem;
  text-align: left;
  border: 1px solid #e5e7eb;
}

.report-table td {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  color: #374151;
}

.table-striped tbody tr:nth-child(even) {
  background: #f9fafb;
}

.table-bordered {
  border: 1px solid #e5e7eb;
}

.table-hover tbody tr:hover {
  background: #f3f4f6;
}

.table-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding: 0.5rem 0;
}

.page-info {
  font-size: 0.875rem;
  color: #6b7280;
}

.empty-table {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
  color: #6b7280;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  background: #f9fafb;
}

.empty-icon {
  width: 3rem;
  height: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-table p {
  margin: 0;
  font-size: 0.875rem;
}

/* Responsive table */
@media (max-width: 768px) {
  .data-table {
    font-size: 0.75rem;
  }
  
  .report-table th,
  .report-table td {
    padding: 0.5rem 0.25rem;
  }
  
  .table-pagination {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
}
</style>