<template>
  <div class="global-search">
    <!-- Search Header -->
    <div class="search-header">
      <div class="search-input-container">
        <div class="search-input-wrapper">
          <SearchIcon class="search-icon h-5 w-5" />
          <input
            ref="searchInput"
            v-model="searchQuery"
            type="text"
            placeholder="Search across all audit data..."
            class="search-input"
            @keydown.enter="handleSearch"
            @input="handleInputChange"
            @focus="showSuggestions = true"
          />
          <div class="search-actions">
            <Button
              v-if="searchQuery"
              variant="ghost"
              size="sm"
              @click="clearSearch"
            >
              <XIcon class="h-4 w-4" />
            </Button>
            <Button
              variant="solid"
              size="sm"
              @click="handleSearch"
              :loading="loading.search"
              :disabled="!searchQuery.trim()"
            >
              Search
            </Button>
          </div>
        </div>

        <!-- Auto-complete Suggestions -->
        <div
          v-if="showSuggestions && suggestions.length"
          class="suggestions-dropdown"
        >
          <div
            v-for="(suggestion, index) in suggestions"
            :key="index"
            class="suggestion-item"
            @click="selectSuggestion(suggestion)"
          >
            <component :is="getDocTypeIcon(suggestion.doctype)" class="h-4 w-4" />
            <span class="suggestion-text">{{ suggestion.text }}</span>
            <span class="suggestion-type">{{ suggestion.doctype }}</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <Button
          variant="outline"
          size="sm"
          @click="showFilters = !showFilters"
          :class="{ 'active': showFilters || filterCount > 0 }"
        >
          <FilterIcon class="h-4 w-4 mr-1" />
          Filters
          <span v-if="filterCount" class="filter-badge">{{ filterCount }}</span>
        </Button>
        
        <Button
          variant="outline"
          size="sm"
          @click="showAnalytics = !showAnalytics"
          :class="{ 'active': showAnalytics }"
        >
          <BarChartIcon class="h-4 w-4 mr-1" />
          Analytics
        </Button>
        
        <Dropdown>
          <template #trigger>
            <Button variant="outline" size="sm">
              <MoreVerticalIcon class="h-4 w-4" />
            </Button>
          </template>
          <template #content>
            <div class="dropdown-content">
              <button
                v-if="hasResults"
                @click="exportResults('excel')"
                class="dropdown-item"
              >
                <DownloadIcon class="h-4 w-4" />
                Export Results
              </button>
              <button
                v-if="searchQuery"
                @click="saveCurrentSearch"
                class="dropdown-item"
              >
                <BookmarkIcon class="h-4 w-4" />
                Save Search
              </button>
              <button
                @click="showSavedSearches = !showSavedSearches"
                class="dropdown-item"
              >
                <FolderIcon class="h-4 w-4" />
                Saved Searches
              </button>
              <button
                @click="showSearchHistory = !showSearchHistory"
                class="dropdown-item"
              >
                <ClockIcon class="h-4 w-4" />
                Search History
              </button>
            </div>
          </template>
        </Dropdown>
      </div>
    </div>

    <!-- Filters Panel -->
    <div v-if="showFilters" class="filters-panel">
      <SearchFilters
        :available-filters="availableFilters"
        :active-filters="activeFilters"
        @filter-added="handleFilterAdded"
        @filter-removed="handleFilterRemoved"
        @filters-cleared="handleFiltersClear"
      />
    </div>

    <!-- Analytics Panel -->
    <div v-if="showAnalytics" class="analytics-panel">
      <SearchAnalytics
        :analytics-data="analyticsData"
        :loading="loading.analytics"
        @refresh="refreshAnalytics"
        @export="exportAnalytics"
      />
    </div>

    <!-- Search Results -->
    <div class="search-content">
      <!-- Results Header -->
      <div v-if="hasSearched" class="results-header">
        <div class="results-info">
          <h3 class="results-title">
            {{ hasResults ? `${totalResults} results` : 'No results' }}
            <span v-if="searchQuery" class="search-query">for "{{ searchQuery }}"</span>
          </h3>
          <p v-if="searchDuration" class="search-time">
            Found in {{ (searchDuration * 1000).toFixed(0) }}ms
          </p>
        </div>
        
        <div class="results-actions">
          <Select
            v-model="sortBy"
            :options="sortOptions"
            placeholder="Sort by..."
            @change="handleSortChange"
          />
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading.search" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Searching across all data...</p>
      </div>

      <!-- Results by DocType -->
      <div v-else-if="hasResults" class="results-container">
        <div
          v-for="(results, doctype) in resultsByDocType"
          :key="doctype"
          class="doctype-results"
        >
          <div class="doctype-header">
            <component :is="getDocTypeIcon(doctype)" class="h-5 w-5" />
            <h4 class="doctype-title">{{ getDocTypeLabel(doctype) }}</h4>
            <span class="doctype-count">{{ results.length }}</span>
          </div>
          
          <div class="results-list">
            <SearchResultItem
              v-for="result in results"
              :key="result.name"
              :result="result"
              :search-query="searchQuery"
              @click="handleResultClick"
            />
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="hasSearched && !hasResults" class="empty-state">
        <SearchIcon class="h-16 w-16 text-gray-300" />
        <h3>No results found</h3>
        <p>Try adjusting your search terms or filters</p>
        <div class="empty-actions">
          <Button variant="outline" @click="clearFilters">
            Clear Filters
          </Button>
          <Button variant="outline" @click="showSearchTips = true">
            Search Tips
          </Button>
        </div>
      </div>

      <!-- Default State -->
      <div v-else class="default-state">
        <div class="recent-searches" v-if="recentSearches.length">
          <h4>Recent Searches</h4>
          <div class="search-chips">
            <button
              v-for="search in recentSearches"
              :key="search.query"
              class="search-chip"
              @click="loadRecentSearch(search)"
            >
              {{ search.query }}
            </button>
          </div>
        </div>
        
        <div class="search-suggestions">
          <h4>Quick Search</h4>
          <div class="suggestion-grid">
            <button
              v-for="doctype in searchableDocTypes"
              :key="doctype.doctype"
              class="doctype-suggestion"
              @click="searchByDocType(doctype.doctype)"
            >
              <component :is="doctype.icon" class="h-6 w-6" />
              <span>{{ doctype.label }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Saved Searches Modal -->
    <Modal v-model="showSavedSearches" title="Saved Searches">
      <SavedSearches
        :saved-searches="savedSearches"
        @load-search="loadSavedSearch"
        @delete-search="deleteSavedSearch"
      />
    </Modal>

    <!-- Search History Modal -->
    <Modal v-model="showSearchHistory" title="Search History">
      <SearchHistory
        :search-history="searchHistory"
        @load-search="loadHistorySearch"
        @clear-history="clearSearchHistory"
      />
    </Modal>

    <!-- Search Tips Modal -->
    <Modal v-model="showSearchTips" title="Search Tips">
      <SearchTips />
    </Modal>
  </div>
</template>

<script setup>
import { Button, Dropdown, Modal, Select } from "frappe-ui"
import {
	AlertTriangleIcon,
	BarChartIcon,
	BookmarkIcon,
	CalendarIcon,
	CheckSquareIcon,
	ClockIcon,
	DownloadIcon,
	FileIcon,
	FilterIcon,
	FolderIcon,
	MoreVerticalIcon,
	SearchIcon,
	ShieldIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, nextTick, onMounted, ref, watch } from "vue"
import { useSearchStore } from "../stores/useSearchStore"
import SavedSearches from "./search/SavedSearches.vue"
import SearchAnalytics from "./search/SearchAnalytics.vue"
import SearchFilters from "./search/SearchFilters.vue"
import SearchHistory from "./search/SearchHistory.vue"
import SearchResultItem from "./search/SearchResultItem.vue"
import SearchTips from "./search/SearchTips.vue"

const searchStore = useSearchStore()

// State
const searchInput = ref(null)
const searchQuery = ref("")
const showSuggestions = ref(false)
const showFilters = ref(false)
const showAnalytics = ref(false)
const showSavedSearches = ref(false)
const showSearchHistory = ref(false)
const showSearchTips = ref(false)
const suggestions = ref([])
const analyticsData = ref({})
const hasSearched = ref(false)
const sortBy = ref("relevance")

// Destructure store
const {
	searchResults,
	searchHistory,
	savedSearches,
	activeFilters,
	loading,
	error,
	searchableDocTypes,
	hasResults,
	resultsByDocType,
	totalResults,
	searchDuration,
	availableFilters,
	recentSearches,
	filterCount,
} = searchStore

// Computed
const sortOptions = [
	{ label: "Relevance", value: "relevance" },
	{ label: "Date Created", value: "creation" },
	{ label: "Date Modified", value: "modified" },
	{ label: "Name", value: "name" },
]

// Methods
const handleSearch = async () => {
	if (!searchQuery.value.trim()) return

	hasSearched.value = true
	showSuggestions.value = false

	try {
		await searchStore.performSearch(searchQuery.value, activeFilters.value, {
			include_analytics: showAnalytics.value,
		})

		if (showAnalytics.value) {
			await refreshAnalytics()
		}
	} catch (err) {
		console.error("Search failed:", err)
	}
}

const handleInputChange = async (event) => {
	const query = event.target.value

	if (query.length >= 2) {
		try {
			suggestions.value = await searchStore.getAutocompleteSuggestions(query)
		} catch (err) {
			console.error("Failed to get suggestions:", err)
		}
	} else {
		suggestions.value = []
	}
}

const selectSuggestion = (suggestion) => {
	searchQuery.value = suggestion.text
	showSuggestions.value = false
	nextTick(() => {
		handleSearch()
	})
}

const loadRecentSearch = (search) => {
	searchQuery.value = search.query
	searchStore.activeFilters = search.filters
	handleSearch()
}

const searchByDocType = (doctype) => {
	searchQuery.value = ""
	searchStore.activeFilters = {}
	searchStore.addFilter("doctype", doctype)
	handleSearch()
}

const clearSearch = () => {
	searchQuery.value = ""
	searchStore.clearSearch()
	hasSearched.value = false
	suggestions.value = []
	showSuggestions.value = false
}

const handleFilterAdded = (filter) => {
	searchStore.addFilter(filter.field, filter.value, filter.operator)
	if (hasSearched.value) {
		handleSearch()
	}
}

const handleFilterRemoved = (field, index) => {
	searchStore.removeFilter(field, index)
	if (hasSearched.value) {
		handleSearch()
	}
}

const handleFiltersClear = () => {
	searchStore.clearFilters()
	if (hasSearched.value) {
		handleSearch()
	}
}

const handleSortChange = (newSort) => {
	sortBy.value = newSort
	if (hasSearched.value) {
		handleSearch()
	}
}

const handleResultClick = (result) => {
	// Navigate to the specific record
	// This would typically use Vue Router
	console.log("Navigate to:", result.doctype, result.name)
}

const saveCurrentSearch = async () => {
	try {
		const searchData = {
			name: searchQuery.value,
			query: searchQuery.value,
			filters: activeFilters.value,
			options: {
				sort_by: sortBy.value,
			},
		}

		await searchStore.saveSearch(searchData)
		// Show success message
	} catch (err) {
		console.error("Failed to save search:", err)
	}
}

const loadSavedSearch = async (searchId) => {
	try {
		const search = await searchStore.loadSavedSearch(searchId)
		if (search) {
			searchQuery.value = search.query
			sortBy.value = search.options?.sort_by || "relevance"
			hasSearched.value = true
		}
		showSavedSearches.value = false
	} catch (err) {
		console.error("Failed to load saved search:", err)
	}
}

const deleteSavedSearch = async (searchId) => {
	try {
		await searchStore.deleteSavedSearch(searchId)
	} catch (err) {
		console.error("Failed to delete saved search:", err)
	}
}

const loadHistorySearch = (search) => {
	searchQuery.value = search.query
	searchStore.activeFilters = search.filters
	handleSearch()
	showSearchHistory.value = false
}

const clearSearchHistory = () => {
	searchStore.searchHistory = []
	searchStore.saveSearchHistory()
}

const exportResults = async (format) => {
	try {
		await searchStore.exportSearchResults(format)
	} catch (err) {
		console.error("Failed to export results:", err)
	}
}

const refreshAnalytics = async () => {
	try {
		analyticsData.value = await searchStore.getAnalytics(
			[],
			activeFilters.value,
		)
	} catch (err) {
		console.error("Failed to refresh analytics:", err)
	}
}

const exportAnalytics = (format) => {
	// Export analytics data
	console.log("Export analytics:", format)
}

const getDocTypeIcon = (doctype) => {
	const iconMap = {
		"Audit Finding": AlertTriangleIcon,
		"Control Procedure": ShieldIcon,
		"Audit Test": CheckSquareIcon,
		"Audit Plan": CalendarIcon,
		Evidence: FileIcon,
	}
	return iconMap[doctype] || FileIcon
}

const getDocTypeLabel = (doctype) => {
	const docTypeConfig = searchableDocTypes.value.find(
		(dt) => dt.doctype === doctype,
	)
	return docTypeConfig?.label || doctype
}

// Watchers
watch(searchQuery, (newQuery) => {
	if (!newQuery) {
		suggestions.value = []
		showSuggestions.value = false
	}
})

// Click outside to close suggestions
const handleClickOutside = (event) => {
	if (!event.target.closest(".search-input-container")) {
		showSuggestions.value = false
	}
}

// Initialize
onMounted(async () => {
	await searchStore.initialize()
	document.addEventListener("click", handleClickOutside)
})

// Cleanup
onUnmounted(() => {
	document.removeEventListener("click", handleClickOutside)
})
</script>

<style scoped>
.global-search {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}

.search-header {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.search-input-container {
  flex: 1;
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.search-input-wrapper:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.1);
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: none;
  outline: none;
  font-size: 1rem;
  background: transparent;
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
}

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 0.5rem 0.5rem;
  max-height: 300px;
  overflow-y: auto;
  z-index: 50;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.suggestion-item:hover {
  background: var(--background-color);
}

.suggestion-text {
  flex: 1;
  font-weight: 500;
}

.suggestion-type {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.quick-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.quick-actions .active {
  background: var(--primary-color);
  color: white;
}

.filter-badge {
  background: var(--error-color);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.125rem 0.375rem;
  border-radius: 0.75rem;
  margin-left: 0.5rem;
}

.filters-panel,
.analytics-panel {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.results-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.search-query {
  color: var(--primary-color);
}

.search-time {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0.25rem 0 0 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.doctype-results {
  margin-bottom: 2rem;
}

.doctype-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--background-color);
  border-radius: 0.375rem;
}

.doctype-title {
  flex: 1;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.doctype-count {
  background: var(--primary-color);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 0.75rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.empty-state,
.default-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 1rem 0 0.5rem 0;
}

.empty-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1.5rem;
}

.recent-searches {
  margin-bottom: 2rem;
}

.recent-searches h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.search-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.search-chip {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.search-chip:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.search-suggestions h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.doctype-suggestion {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.doctype-suggestion:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.dropdown-content {
  padding: 0.5rem;
  min-width: 200px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: none;
  background: none;
  text-align: left;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background: var(--background-color);
}

@media (max-width: 768px) {
  .search-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .results-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .suggestion-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .search-chips {
    justify-content: flex-start;
  }
}
</style>