<template>
  <div class="bg-white rounded-xl border p-4">
    <div class="flex flex-wrap items-center gap-4">
      <!-- Search -->
      <div class="flex-1 min-w-[200px] max-w-md">
        <FormControl
          v-model="localFilters.search"
          type="text"
          placeholder="Search tests by name, ID, or description..."
          :debounce="300"
          @update:modelValue="emitFilters"
        >
          <template #prefix>
            <Search class="h-4 w-4 text-gray-400" />
          </template>
        </FormControl>
      </div>

      <!-- Category Filter -->
      <div class="w-48">
        <Select
          v-model="localFilters.category"
          :options="categoryOptions"
          placeholder="All Categories"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Test Type Filter -->
      <div class="w-40">
        <Select
          v-model="localFilters.testType"
          :options="testTypeOptions"
          placeholder="All Types"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Logic Type Filter -->
      <div class="w-44">
        <Select
          v-model="localFilters.logicType"
          :options="logicTypeOptions"
          placeholder="All Logic Types"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Status Filter -->
      <div class="w-36">
        <Select
          v-model="localFilters.status"
          :options="statusOptions"
          placeholder="All Status"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2 ml-auto">
        <Button
          v-if="hasActiveFilters"
          variant="outline"
          @click="clearFilters"
        >
          <template #prefix><X class="h-4 w-4" /></template>
          Clear
        </Button>
        <Button variant="outline" @click="$emit('refresh')">
          <template #prefix><RefreshCw class="h-4 w-4" /></template>
          Refresh
        </Button>
        <Button variant="solid" @click="$emit('create')">
          <template #prefix><Plus class="h-4 w-4" /></template>
          New Test
        </Button>
      </div>
    </div>

    <!-- Active Filter Tags -->
    <div v-if="hasActiveFilters" class="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t">
      <span class="text-xs text-gray-500">Active filters:</span>
      <Badge
        v-if="localFilters.search"
        theme="blue"
        class="cursor-pointer"
        @click="removeFilter('search')"
      >
        Search: "{{ localFilters.search }}"
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.category"
        theme="purple"
        class="cursor-pointer"
        @click="removeFilter('category')"
      >
        Category: {{ localFilters.category }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.testType"
        theme="indigo"
        class="cursor-pointer"
        @click="removeFilter('testType')"
      >
        Type: {{ localFilters.testType }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.logicType"
        theme="orange"
        class="cursor-pointer"
        @click="removeFilter('logicType')"
      >
        Logic: {{ localFilters.logicType }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
      <Badge
        v-if="localFilters.status"
        theme="green"
        class="cursor-pointer"
        @click="removeFilter('status')"
      >
        Status: {{ localFilters.status }}
        <X class="h-3 w-3 ml-1" />
      </Badge>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, FormControl, Select } from "frappe-ui"
import { Plus, RefreshCw, Search, X } from "lucide-vue-next"
import { computed, reactive, watch } from "vue"

const props = defineProps({
	filters: {
		type: Object,
		default: () => ({}),
	},
})

const emit = defineEmits(["update:filters", "refresh", "create"])

const localFilters = reactive({
	search: "",
	category: "",
	testType: "",
	logicType: "",
	status: "",
})

// Watch for external filter changes
watch(
	() => props.filters,
	(newFilters) => {
		if (newFilters) {
			Object.assign(localFilters, newFilters)
		}
	},
	{ immediate: true, deep: true },
)

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
	{ label: "Substantive", value: "Substantive" },
	{ label: "Controls", value: "Controls" },
	{ label: "Analytical", value: "Analytical" },
	{ label: "Compliance", value: "Compliance" },
]

const logicTypeOptions = [
	{ label: "All Logic Types", value: "" },
	{ label: "SQL Query", value: "SQL Query" },
	{ label: "Python Script", value: "Python Script" },
	{ label: "Built-in Function", value: "Built-in Function" },
]

const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Active", value: "Active" },
	{ label: "Inactive", value: "Inactive" },
	{ label: "Under Review", value: "Under Review" },
]

const hasActiveFilters = computed(() => {
	return Object.values(localFilters).some((v) => v !== "")
})

function emitFilters() {
	emit("update:filters", { ...localFilters })
}

function removeFilter(key) {
	localFilters[key] = ""
	emitFilters()
}

function clearFilters() {
	Object.keys(localFilters).forEach((key) => {
		localFilters[key] = ""
	})
	emitFilters()
}
</script>
