import { useDebounceFn } from "@vueuse/core"
import { createResource } from "frappe-ui"
import { ref } from "vue"

/**
 * Composable for handling Link field operations with Frappe API
 * Provides search functionality with caching and debouncing
 *
 * @param {string} doctype - The doctype to search (e.g., 'User', 'Customer')
 * @param {object} filters - Optional filters for the search query
 * @returns {object} - Search methods and reactive state
 */
export function useLinkField(doctype, filters = {}) {
	const searchResults = ref([])
	const isSearching = ref(false)
	const searchCache = ref(new Map())
	const dataCache = ref(new Map())

	/**
	 * Search resource for Link field autocomplete
	 * Uses frappe.desk.search.search_link API
	 */
	const searchResource = createResource({
		url: "frappe.desk.search.search_link",
		params: {
			doctype,
			txt: "",
			filters: JSON.stringify(filters),
		},
		auto: false,
		transform: (data) => {
			if (!data) return []
			return data.map((item) => ({
				label: item.description || item.value,
				value: item.value,
			}))
		},
		onSuccess: (data) => {
			searchResults.value = data || []
			isSearching.value = false
		},
		onError: (error) => {
			console.error(`Link field search error for ${doctype}:`, error)
			searchResults.value = []
			isSearching.value = false
		},
	})

	/**
	 * Search for Link field options with debouncing and caching
	 * Debounced to 300ms to prevent excessive API calls
	 *
	 * @param {string} query - The search query
	 */
	const search = useDebounceFn(async (query) => {
		if (!query || query.trim() === "") {
			searchResults.value = []
			return
		}

		// Check cache first
		const cacheKey = `${doctype}:${query.toLowerCase()}`
		if (searchCache.value.has(cacheKey)) {
			searchResults.value = searchCache.value.get(cacheKey)
			return
		}

		// Perform search
		isSearching.value = true
		searchResource.params.txt = query

		try {
			await searchResource.fetch()

			// Cache the results
			searchCache.value.set(cacheKey, searchResults.value)
		} catch (error) {
			console.error("Search failed:", error)
			isSearching.value = false
		}
	}, 300)

	/**
	 * Get specific field values for a document
	 * Uses frappe.client.get_value API
	 *
	 * @param {string} name - The document name/ID
	 * @param {array} fields - Array of field names to fetch
	 * @returns {Promise<object>} - Object with field values
	 */
	const getValue = async (name, fields) => {
		if (!name || !fields || fields.length === 0) {
			return null
		}

		// Check cache first
		const cacheKey = `${doctype}:${name}:${fields.join(",")}`
		if (dataCache.value.has(cacheKey)) {
			return dataCache.value.get(cacheKey)
		}

		// Fetch data
		const resource = createResource({
			url: "frappe.client.get_value",
			params: {
				doctype,
				name,
				fieldname: JSON.stringify(fields),
			},
			auto: false,
		})

		try {
			await resource.fetch()
			const data = resource.data

			// Cache the result
			dataCache.value.set(cacheKey, data)

			return data
		} catch (error) {
			console.error(`Failed to fetch ${doctype} values:`, error)
			return null
		}
	}

	/**
	 * Clear all caches
	 * Useful when filters change or data needs to be refreshed
	 */
	const clearCache = () => {
		searchCache.value.clear()
		dataCache.value.clear()
		searchResults.value = []
	}

	/**
	 * Clear search results
	 */
	const clearResults = () => {
		searchResults.value = []
	}

	return {
		searchResults,
		isSearching,
		search,
		getValue,
		clearCache,
		clearResults,
	}
}
