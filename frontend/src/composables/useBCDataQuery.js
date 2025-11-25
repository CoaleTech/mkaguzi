import { createResource } from "frappe-ui"
import { computed, ref } from "vue"

export function useBCDataQuery(doctype) {
	const filters = ref({})
	const columns = ref([])
	const data = ref([])
	const loading = ref(false)
	const error = ref(null)

	const resource = createResource({
		url: "frappe.client.get_list",
		params: computed(() => ({
			doctype,
			fields: columns.value.length > 0 ? columns.value : ["*"],
			filters: filters.value,
			limit_page_length: 100,
		})),
		auto: false,
	})

	const fetchData = async () => {
		try {
			loading.value = true
			error.value = null
			await resource.submit()
			data.value = resource.data || []
		} catch (err) {
			error.value = err.message
			data.value = []
		} finally {
			loading.value = false
		}
	}

	const exportToExcel = async () => {
		// This would call a backend API to export data
		console.log("Export to Excel functionality to be implemented")
	}

	const setFilters = (newFilters) => {
		filters.value = newFilters
	}

	const setColumns = (newColumns) => {
		columns.value = newColumns
	}

	const clearFilters = () => {
		filters.value = {}
	}

	return {
		filters,
		columns,
		data,
		loading,
		error,
		fetchData,
		exportToExcel,
		setFilters,
		setColumns,
		clearFilters,
	}
}
