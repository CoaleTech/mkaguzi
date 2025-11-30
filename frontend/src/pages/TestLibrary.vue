<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Test Library</h1>
        <p class="text-gray-600">Manage standardized audit tests and procedures</p>
      </div>
      <div class="flex gap-2">
        <Button @click="refreshData" :loading="loading" variant="outline" size="sm">
          <RefreshCw class="w-4 h-4" />
        </Button>
        <Button @click="importTests" variant="outline" size="sm">
          <Upload class="w-4 h-4" />
        </Button>
        <Button @click="createTest">
          <Plus class="w-4 h-4 mr-2" />
          New Test
        </Button>
      </div>
    </div>

    <!-- Filters Section -->
    <TestFilters
      v-model:searchQuery="searchQuery"
      v-model:selectedCategory="selectedCategory"
      v-model:selectedTestType="selectedTestType"
      v-model:selectedStatus="selectedStatus"
      @refresh="refreshData"
      @create="createTest"
    />

    <!-- Summary Stats -->
    <TestStats :tests="filteredTests" :active-filter="activeFilter" @filter="handleStatsFilter" />

    <!-- Tests List -->
    <div class="bg-white rounded-lg border shadow-sm">
      <div v-if="filteredTests.length > 0" class="divide-y divide-gray-200">
        <div v-for="category in groupedTests" :key="category.name" class="p-4">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <FileText class="w-5 h-5" />
              <span>{{ category.name }}</span>
              <Badge variant="gray" size="sm">{{ category.tests.length }}</Badge>
            </h3>
            <Button
              @click="toggleCategory(category.name)"
              variant="ghost"
              size="sm"
            >
              <ChevronDown v-if="expandedCategories.includes(category.name)" class="w-4 h-4" />
              <ChevronRight v-else class="w-4 h-4" />
            </Button>
          </div>

          <div v-show="expandedCategories.includes(category.name)" class="space-y-3">
            <div
              v-for="test in category.tests"
              :key="test.name"
              class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              @click="viewTest(test.name)"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-3 mb-2">
                    <h4 class="font-medium text-gray-900">{{ test.test_name }}</h4>
                    <Badge :variant="getTestTypeVariant(test.test_logic_type)">
                      {{ test.test_logic_type }}
                    </Badge>
                    <Badge :variant="getStatusVariant(test.status)" size="sm">
                      {{ test.status }}
                    </Badge>
                  </div>
                  <p class="text-sm text-gray-600 mb-2 line-clamp-2">{{ test.description }}</p>

                  <!-- Test Details -->
                  <div class="flex items-center gap-6 text-sm text-gray-500">
                    <div class="flex items-center gap-1">
                      <Target class="w-4 h-4" />
                      <span>{{ test.objective || 'No objective' }}</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <Database class="w-4 h-4" />
                      <span>{{ test.data_source || 'No data source' }}</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <Clock class="w-4 h-4" />
                      <span>{{ test.estimated_time || 0 }} mins</span>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-3 ml-4">
                  <!-- Usage Stats -->
                  <div class="text-right text-sm">
                    <p class="text-gray-900 font-medium">{{ test.usage_count || 0 }}</p>
                    <p class="text-gray-500">executions</p>
                  </div>

                  <!-- Actions -->
                  <Dropdown :options="getTestActions(test)">
                    <template #default="{ open }">
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal class="w-4 h-4" />
                      </Button>
                    </template>
                  </Dropdown>
                </div>
              </div>

              <!-- Test Steps Preview -->
              <div v-if="test.test_steps?.length" class="mt-3 pt-3 border-t border-gray-100">
                <div class="flex items-center gap-2 mb-2">
                  <List class="w-4 h-4 text-gray-400" />
                  <span class="text-sm font-medium text-gray-700">Test Steps ({{ test.test_steps.length }})</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs text-gray-600">
                  <div v-for="(step, index) in test.test_steps.slice(0, 3)" :key="index" class="flex items-center gap-1">
                    <span class="w-4 h-4 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs">{{ index + 1 }}</span>
                    <span class="truncate">{{ step.description || step.step_description }}</span>
                  </div>
                  <div v-if="test.test_steps.length > 3" class="flex items-center gap-1 text-gray-500">
                    <span>+{{ test.test_steps.length - 3 }} more steps</span>
                  </div>
                </div>
              </div>

              <!-- Test Execution History -->
              <div v-if="test.recent_executions?.length" class="mt-3 pt-3 border-t border-gray-100">
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center gap-2">
                    <Activity class="w-4 h-4 text-gray-400" />
                    <span class="text-sm font-medium text-gray-700">Recent Executions</span>
                  </div>
                  <Button variant="ghost" size="sm" @click.stop="viewTestHistory(test.name)">
                    View All
                  </Button>
                </div>
                <div class="flex items-center gap-4">
                  <div v-for="execution in test.recent_executions.slice(0, 3)" :key="execution.name" class="flex items-center gap-2">
                    <div :class="['w-3 h-3 rounded-full', getExecutionStatusColor(execution.result)]"></div>
                    <span class="text-xs text-gray-600">{{ formatDate(execution.execution_date) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="p-12 text-center text-gray-500">
        <Database class="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No tests found</h3>
        <p class="text-gray-600 mb-6">
          {{ searchQuery || selectedCategory || selectedTestType ? 'Try adjusting your filters' : 'Create your first audit test to get started' }}
        </p>
        <Button @click="createTest">
          <Plus class="w-4 h-4 mr-2" />
          Create Test
        </Button>
      </div>
    </div>

    <!-- Test Library Form Dialog -->
    <TestLibraryForm
      v-model:show="showFormDialog"
      :test-data="selectedTest"
      :is-edit-mode="isEditMode"
      @saved="handleTestSaved"
    />
  </div>
</template>

<script setup>
import TestFilters from "@/components/testlibrary/TestFilters.vue"
import TestLibraryForm from "@/components/testlibrary/TestLibraryForm.vue"
import TestStats from "@/components/testlibrary/TestStats.vue"
import { useTestLibraryStore } from "@/stores/testLibrary"
import { Badge, Button, Dropdown, FormControl } from "frappe-ui"
import {
	Activity,
	ChevronDown,
	ChevronRight,
	Clock,
	Database,
	FileText,
	List,
	MoreHorizontal,
	Plus,
	RefreshCw,
	Target,
	Upload,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

// Store
const testLibraryStore = useTestLibraryStore()

// Reactive data
const loading = computed(() => testLibraryStore.loading)
const saving = computed(() => testLibraryStore.saving)
const searchQuery = computed({
	get: () => testLibraryStore.searchQuery,
	set: (value) => (testLibraryStore.searchQuery = value),
})
const selectedCategory = computed({
	get: () => testLibraryStore.selectedCategory,
	set: (value) => (testLibraryStore.selectedCategory = value),
})
const selectedTestType = computed({
	get: () => testLibraryStore.selectedTestType,
	set: (value) => (testLibraryStore.selectedTestType = value),
})
const selectedStatus = computed({
	get: () => testLibraryStore.selectedStatus,
	set: (value) => (testLibraryStore.selectedStatus = value),
})
const expandedCategories = ref([])
const showFormDialog = ref(false)
const isEditMode = ref(false)
const selectedTest = ref(null)
const activeFilter = ref("")

// Computed properties
const filteredTests = computed(() => testLibraryStore.filteredTests)
const groupedTests = computed(() => testLibraryStore.groupedTests)
const stats = computed(() => testLibraryStore.stats)

// Methods
const fetchTests = async () => {
	await testLibraryStore.fetchTests()
}

const refreshData = async () => {
	await testLibraryStore.fetchTests()
}

const createTest = () => {
	selectedTest.value = null
	isEditMode.value = false
	showFormDialog.value = true
}

const handleTestSaved = async () => {
	showFormDialog.value = false
	await testLibraryStore.fetchTests()
}

const importTests = () => {
	// TODO: Implement import functionality
	console.log("Import tests")
}

const viewTest = async (testId) => {
	try {
		selectedTest.value = await testLibraryStore.getTestDetails(testId)
		isEditMode.value = true
		showFormDialog.value = true
	} catch (error) {
		console.error("Error fetching test details:", error)
	}
}

const viewTestHistory = (testId) => {
	// TODO: Implement test history view
	console.log("View test history:", testId)
}

const toggleCategory = (categoryName) => {
	const index = expandedCategories.value.indexOf(categoryName)
	if (index > -1) {
		expandedCategories.value.splice(index, 1)
	} else {
		expandedCategories.value.push(categoryName)
	}
}

const getTestActions = (test) => {
	return [
		{
			label: "Execute Test",
			value: "execute",
			handler: () => executeTest(test),
		},
		{ label: "Edit Test", value: "edit", handler: () => editTest(test) },
		{ label: "Clone Test", value: "clone", handler: () => cloneTest(test) },
		{ label: "Export", value: "export", handler: () => exportTest(test) },
		{ label: "Archive", value: "archive", handler: () => archiveTest(test) },
	]
}

const executeTest = (test) => {
	// TODO: Implement test execution
	console.log("Execute test:", test.name)
}

const editTest = async (test) => {
	try {
		selectedTest.value = await testLibraryStore.getTestDetails(test.name)
		isEditMode.value = true
		showFormDialog.value = true
	} catch (error) {
		console.error("Error fetching test details:", error)
	}
}

const cloneTest = (test) => {
	// TODO: Implement test cloning
	console.log("Clone test:", test.name)
}

const exportTest = (test) => {
	// TODO: Implement test export
	console.log("Export test:", test.name)
}

const archiveTest = (test) => {
	// TODO: Implement test archiving
	console.log("Archive test:", test.name)
}

const getTestTypeVariant = (testType) => {
	const variants = {
		"SQL Query": "blue",
		"Python Script": "green",
		"Built-in Function": "purple",
	}
	return variants[testType] || "gray"
}

const getStatusVariant = (status) => {
	const variants = {
		Active: "green",
		Draft: "gray",
		"Under Review": "blue",
		Archived: "red",
	}
	return variants[status] || "gray"
}

const getExecutionStatusColor = (result) => {
	const colors = {
		Pass: "bg-green-500",
		Fail: "bg-red-500",
		Inconclusive: "bg-yellow-500",
		"N/A": "bg-gray-500",
	}
	return colors[result] || "bg-gray-500"
}

const handleStatsFilter = (filterKey, filterValue) => {
	if (filterKey === "status") {
		selectedStatus.value = filterValue
	} else if (filterKey === "test_type") {
		selectedTestType.value = filterValue
	} else if (filterKey === "test_logic_type") {
		selectedTestType.value = filterValue
	}
	activeFilter.value = filterValue
}

// Lifecycle
onMounted(async () => {
	await fetchTests()
})
</script>

<style scoped>
.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}

.transition-colors {
  transition-property: background-color, border-color, color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
</style>