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
    <div class="bg-white rounded-lg border shadow-sm p-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Search -->
        <div class="flex-1 min-w-64">
          <FormControl
            v-model="searchQuery"
            placeholder="Search tests..."
            type="text"
          >
            <template #prefix>
              <Search class="w-4 h-4 text-gray-400" />
            </template>
          </FormControl>
        </div>

        <!-- Category Filter -->
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-gray-700">Category:</span>
          <FormControl
            v-model="selectedCategory"
            :options="categoryOptions"
            type="select"
            class="w-40"
          />
        </div>

        <!-- Test Type Filter -->
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-gray-700">Type:</span>
          <FormControl
            v-model="selectedTestType"
            :options="testTypeOptions"
            type="select"
            class="w-40"
          />
        </div>

        <!-- Status Filter -->
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-gray-700">Status:</span>
          <FormControl
            v-model="selectedStatus"
            :options="statusOptions"
            type="select"
            class="w-40"
          />
        </div>
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div class="bg-white p-4 rounded-lg border shadow-sm text-center">
        <p class="text-2xl font-bold text-blue-600">{{ stats.total }}</p>
        <p class="text-sm text-gray-600">Total Tests</p>
      </div>
      <div class="bg-white p-4 rounded-lg border shadow-sm text-center">
        <p class="text-2xl font-bold text-green-600">{{ stats.active }}</p>
        <p class="text-sm text-gray-600">Active</p>
      </div>
      <div class="bg-white p-4 rounded-lg border shadow-sm text-center">
        <p class="text-2xl font-bold text-purple-600">{{ stats.substantive }}</p>
        <p class="text-sm text-gray-600">Substantive</p>
      </div>
      <div class="bg-white p-4 rounded-lg border shadow-sm text-center">
        <p class="text-2xl font-bold text-orange-600">{{ stats.controls }}</p>
        <p class="text-sm text-gray-600">Controls</p>
      </div>
      <div class="bg-white p-4 rounded-lg border shadow-sm text-center">
        <p class="text-2xl font-bold text-gray-600">{{ stats.analytical }}</p>
        <p class="text-sm text-gray-600">Analytical</p>
      </div>
    </div>

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

    <!-- Create Test Dialog -->
    <Dialog v-model="showCreateDialog" :options="{ title: 'Create New Test' }">
      <template #body-content>
        <div class="space-y-4">
          <FormControl label="Test Name" v-model="newTest.test_name" type="text" required />
          <FormControl label="Category" v-model="newTest.category" :options="categoryOptions" type="select" required />
          <FormControl label="Test Type" v-model="newTest.test_logic_type" :options="testTypeOptions" type="select" required />
          <FormControl label="Description" v-model="newTest.description" type="textarea" />
          <FormControl label="Objective" v-model="newTest.objective" type="textarea" />
          <FormControl label="Data Source" v-model="newTest.data_source" type="text" />
          <FormControl label="Estimated Time (minutes)" v-model="newTest.estimated_time" type="number" />
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showCreateDialog = false">Cancel</Button>
        <Button @click="saveTest" :loading="saving">Create Test</Button>
      </template>
    </Dialog>

    <!-- Test Detail Dialog -->
    <Dialog v-model="showDetailDialog" :options="{ title: 'Test Details', size: '4xl' }">
      <template #body-content>
        <div v-if="selectedTest" class="space-y-6">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <h3 class="font-semibold">Test Information</h3>
              <div class="mt-2 space-y-1 text-sm">
                <p><span class="font-medium">Name:</span> {{ selectedTest.test_name }}</p>
                <p><span class="font-medium">Category:</span> {{ selectedTest.category }}</p>
                <p><span class="font-medium">Type:</span> {{ selectedTest.test_logic_type }}</p>
                <p><span class="font-medium">Status:</span> {{ selectedTest.status }}</p>
                <p><span class="font-medium">Usage Count:</span> {{ selectedTest.usage_count || 0 }}</p>
              </div>
            </div>
            <div>
              <h3 class="font-semibold">Test Details</h3>
              <div class="mt-2 space-y-1 text-sm">
                <p><span class="font-medium">Objective:</span> {{ selectedTest.objective || 'N/A' }}</p>
                <p><span class="font-medium">Data Source:</span> {{ selectedTest.data_source || 'N/A' }}</p>
                <p><span class="font-medium">Estimated Time:</span> {{ selectedTest.estimated_time || 0 }} minutes</p>
                <p><span class="font-medium">Created:</span> {{ formatDate(selectedTest.creation) }}</p>
                <p><span class="font-medium">Modified:</span> {{ formatDate(selectedTest.modified) }}</p>
              </div>
            </div>
          </div>

          <div>
            <h3 class="font-semibold">Description</h3>
            <p class="mt-2 text-sm text-gray-600">{{ selectedTest.description || 'No description provided.' }}</p>
          </div>

          <!-- Test Steps -->
          <div v-if="selectedTest.test_steps?.length">
            <h3 class="font-semibold mb-2">Test Steps</h3>
            <div class="space-y-2">
              <div v-for="(step, index) in selectedTest.test_steps" :key="index" class="flex items-start gap-3 p-3 border rounded">
                <span class="w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-medium">{{ index + 1 }}</span>
                <div class="flex-1">
                  <p class="text-sm">{{ step.description || step.step_description }}</p>
                  <p v-if="step.expected_result" class="text-xs text-gray-600 mt-1">Expected: {{ step.expected_result }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Executions -->
          <div v-if="selectedTest.recent_executions?.length">
            <h3 class="font-semibold mb-2">Recent Executions</h3>
            <div class="space-y-2">
              <div v-for="execution in selectedTest.recent_executions" :key="execution.name" class="flex items-center justify-between p-3 border rounded">
                <div class="flex items-center gap-3">
                  <div :class="['w-3 h-3 rounded-full', getExecutionStatusColor(execution.result)]"></div>
                  <span class="text-sm">{{ formatDate(execution.execution_date) }}</span>
                  <span class="text-sm text-gray-600">{{ execution.executed_by }}</span>
                </div>
                <Badge :variant="execution.result === 'Pass' ? 'green' : execution.result === 'Fail' ? 'red' : 'yellow'">
                  {{ execution.result }}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { useTestLibraryStore } from "@/stores/testLibrary"
import { Badge, Button, Dialog, Dropdown, FormControl } from "frappe-ui"
import {
	Activity,
	ChevronDown,
	ChevronRight,
	Clock,
	Database,
	Database as DatabaseIcon,
	FileText,
	List,
	MoreHorizontal,
	Plus,
	RefreshCw,
	Search,
	Target,
	Upload,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"

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
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const selectedTest = ref(null)
const newTest = ref({
	test_name: "",
	category: "",
	test_logic_type: "",
	description: "",
	objective: "",
	data_source_type: "Database Table",
	status: "Active",
})

// Filter options
const categoryOptions = [
	{ label: "All Categories", value: "" },
	{ label: "Duplicate Detection", value: "Duplicate Detection" },
	{ label: "Outlier Analysis", value: "Outlier Analysis" },
	{ label: "Trend Analysis", value: "Trend Analysis" },
	{ label: "Ratio Analysis", value: "Ratio Analysis" },
	{ label: "Completeness Check", value: "Completeness Check" },
	{ label: "Validity Check", value: "Validity Check" },
	{ label: "Accuracy Check", value: "Accuracy Check" },
	{ label: "Timeliness Check", value: "Timeliness Check" },
	{ label: "Consistency Check", value: "Consistency Check" },
	{ label: "Custom Analysis", value: "Custom Analysis" },
]

const testTypeOptions = [
	{ label: "All Types", value: "" },
	{ label: "SQL Query", value: "SQL Query" },
	{ label: "Python Script", value: "Python Script" },
	{ label: "Built-in Function", value: "Built-in Function" },
]

const statusOptions = [
	{ label: "All Statuses", value: "" },
	{ label: "Active", value: "Active" },
	{ label: "Draft", value: "Draft" },
	{ label: "Under Review", value: "Under Review" },
	{ label: "Archived", value: "Archived" },
]

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
	newTest.value = {
		test_name: "",
		category: "",
		test_logic_type: "",
		description: "",
		objective: "",
		data_source_type: "Database Table",
		status: "Active",
	}
	showCreateDialog.value = true
}

const saveTest = async () => {
	try {
		await testLibraryStore.createTest(newTest.value)
		showCreateDialog.value = false
	} catch (error) {
		console.error("Error saving test:", error)
	}
}

const importTests = () => {
	// TODO: Implement import functionality
	console.log("Import tests")
}

const viewTest = async (testId) => {
	try {
		selectedTest.value = await testLibraryStore.getTestDetails(testId)
		showDetailDialog.value = true
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

const editTest = (test) => {
	// TODO: Implement test editing
	console.log("Edit test:", test.name)
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

const formatDate = (dateStr) => {
	if (!dateStr) return "N/A"
	return new Date(dateStr).toLocaleDateString("en-US", {
		year: "numeric",
		month: "short",
		day: "numeric",
	})
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