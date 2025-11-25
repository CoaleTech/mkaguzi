import { createResource } from "frappe-ui"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useTestLibraryStore = defineStore("testLibrary", () => {
	// State
	const tests = ref([])
	const loading = ref(false)
	const saving = ref(false)

	// Filters
	const searchQuery = ref("")
	const selectedCategory = ref("")
	const selectedTestType = ref("")
	const selectedStatus = ref("")

	// API Resources
	const testsResource = createResource({
		url: "mkaguzi.api.test_library.get_tests",
		params: () => ({
			filters: {
				category: selectedCategory.value,
				test_type: selectedTestType.value,
				status: selectedStatus.value,
			},
			search: searchQuery.value,
		}),
		auto: false,
		onSuccess(data) {
			tests.value = data || []
		},
	})

	// Computed properties
	const filteredTests = computed(() => {
		let filtered = [...tests.value]

		// Search filter
		if (searchQuery.value) {
			const query = searchQuery.value.toLowerCase()
			filtered = filtered.filter(
				(test) =>
					test.test_name?.toLowerCase().includes(query) ||
					test.description?.toLowerCase().includes(query) ||
					test.objective?.toLowerCase().includes(query) ||
					test.test_category?.toLowerCase().includes(query),
			)
		}

		// Category filter
		if (selectedCategory.value) {
			filtered = filtered.filter(
				(test) => test.test_category === selectedCategory.value,
			)
		}

		// Test type filter
		if (selectedTestType.value) {
			filtered = filtered.filter(
				(test) => test.test_logic_type === selectedTestType.value,
			)
		}

		// Status filter
		if (selectedStatus.value) {
			filtered = filtered.filter((test) => test.status === selectedStatus.value)
		}

		return filtered
	})

	const groupedTests = computed(() => {
		const groups = {}

		filteredTests.value.forEach((test) => {
			const category = test.test_category || "Uncategorized"
			if (!groups[category]) {
				groups[category] = []
			}
			groups[category].push(test)
		})

		return Object.keys(groups)
			.map((category) => ({
				name: category,
				tests: groups[category],
			}))
			.sort((a, b) => a.name.localeCompare(b.name))
	})

	const stats = computed(() => {
		const stats = {
			total: tests.value.length,
			active: 0,
			substantive: 0,
			controls: 0,
			analytical: 0,
		}

		tests.value.forEach((test) => {
			if (test.status === "Active") {
				stats.active++
			}

			// Map test_logic_type to our categories
			const logicType = test.test_logic_type
			if (logicType === "SQL Query") {
				stats.substantive++
			} else if (logicType === "Python Script") {
				stats.controls++
			} else if (logicType === "Built-in Function") {
				stats.analytical++
			}
		})

		return stats
	})

	// Actions
	const fetchTests = async () => {
		loading.value = true
		try {
			await testsResource.reload()
		} catch (error) {
			console.error("Error fetching tests:", error)
		} finally {
			loading.value = false
		}
	}

	const createTest = async (testData) => {
		saving.value = true
		try {
			const response = await createResource({
				url: "mkaguzi.api.test_library.create_test",
				method: "POST",
				params: testData,
			}).submit()

			// Refresh the list
			await fetchTests()
			return response
		} catch (error) {
			console.error("Error creating test:", error)
			throw error
		} finally {
			saving.value = false
		}
	}

	const updateTest = async (testId, testData) => {
		saving.value = true
		try {
			const response = await createResource({
				url: "mkaguzi.api.test_library.update_test",
				method: "PUT",
				params: { name: testId, ...testData },
			}).submit()

			// Refresh the list
			await fetchTests()
			return response
		} catch (error) {
			console.error("Error updating test:", error)
			throw error
		} finally {
			saving.value = false
		}
	}

	const deleteTest = async (testId) => {
		try {
			await createResource({
				url: "mkaguzi.api.test_library.delete_test",
				method: "DELETE",
				params: { name: testId },
			}).submit()

			// Refresh the list
			await fetchTests()
		} catch (error) {
			console.error("Error deleting test:", error)
			throw error
		}
	}

	const executeTest = async (testId, parameters = {}) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.test_library.execute_test",
				method: "POST",
				params: { test_name: testId, parameters },
			}).submit()

			return response
		} catch (error) {
			console.error("Error executing test:", error)
			throw error
		}
	}

	const getTestDetails = async (testId) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.test_library.get_test_details",
				params: { name: testId },
			}).submit()

			return response
		} catch (error) {
			console.error("Error fetching test details:", error)
			throw error
		}
	}

	const getTestHistory = async (testId) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.test_library.get_test_history",
				params: { test_name: testId },
			}).submit()

			return response
		} catch (error) {
			console.error("Error fetching test history:", error)
			throw error
		}
	}

	const importTests = async (file) => {
		try {
			const formData = new FormData()
			formData.append("file", file)

			const response = await createResource({
				url: "mkaguzi.api.test_library.import_tests",
				method: "POST",
				params: formData,
			}).submit()

			// Refresh the list
			await fetchTests()
			return response
		} catch (error) {
			console.error("Error importing tests:", error)
			throw error
		}
	}

	const exportTests = async (filters = {}) => {
		try {
			const response = await createResource({
				url: "mkaguzi.api.test_library.export_tests",
				params: filters,
			}).submit()

			return response
		} catch (error) {
			console.error("Error exporting tests:", error)
			throw error
		}
	}

	// Reset filters
	const resetFilters = () => {
		searchQuery.value = ""
		selectedCategory.value = ""
		selectedTestType.value = ""
		selectedStatus.value = ""
	}

	return {
		// State
		tests,
		loading,
		saving,
		searchQuery,
		selectedCategory,
		selectedTestType,
		selectedStatus,

		// Computed
		filteredTests,
		groupedTests,
		stats,

		// Actions
		fetchTests,
		createTest,
		updateTest,
		deleteTest,
		executeTest,
		getTestDetails,
		getTestHistory,
		importTests,
		exportTests,
		resetFilters,
	}
})
