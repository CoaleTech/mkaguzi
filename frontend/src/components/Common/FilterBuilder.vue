<template>
  <div class="w-full">
    <!-- Active Filters Display -->
    <div v-if="activeFilters.length > 0" class="mb-4">
      <div class="flex flex-wrap gap-2">
        <div
          v-for="filter in activeFilters"
          :key="filter.id"
          class="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800"
        >
          <span class="font-medium">{{ filter.field.label }}:</span>
          <span class="ml-1">{{ filter.operator.label }}</span>
          <span class="ml-1 font-mono">{{ filter.value }}</span>
          <button
            @click="removeFilter(filter.id)"
            class="ml-2 text-blue-600 hover:text-blue-800"
          >
            <XIcon class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Filter Builder -->
    <div class="space-y-4">
      <!-- Filter Groups -->
      <div
        v-for="(group, groupIndex) in filterGroups"
        :key="groupIndex"
        class="rounded-lg border border-gray-200 bg-white p-4"
      >
        <!-- Group Header -->
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center space-x-2">
            <span class="text-sm font-medium text-gray-700">Filter Group {{ groupIndex + 1 }}</span>
            <Select
              v-model="group.logic"
              :options="logicOptions"
              size="sm"
              class="w-24"
            />
          </div>
          <div class="flex items-center space-x-2">
            <Button
              v-if="filterGroups.length > 1"
              variant="outline"
              size="sm"
              @click="removeFilterGroup(groupIndex)"
            >
              <MinusIcon class="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              @click="addFilterToGroup(groupIndex)"
            >
              <PlusIcon class="h-4 w-4" />
            </Button>
          </div>
        </div>

        <!-- Filters in Group -->
        <div class="space-y-3">
          <div
            v-for="(filter, filterIndex) in group.filters"
            :key="filterIndex"
            class="flex items-end space-x-3"
          >
            <!-- Field Selector -->
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Field</label>
              <Select
                v-model="filter.field"
                :options="availableFields"
                placeholder="Select field"
              />
            </div>

            <!-- Operator Selector -->
            <div class="w-40">
              <label class="block text-sm font-medium text-gray-700 mb-1">Operator</label>
              <Select
                v-model="filter.operator"
                :options="getOperatorsForField(filter.field)"
                placeholder="Operator"
              />
            </div>

            <!-- Value Input -->
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Value</label>
              <component
                :is="getInputComponent(filter.field)"
                v-model="filter.value"
                :placeholder="getPlaceholder(filter.field)"
                :type="getInputType(filter.field)"
                :options="getSelectOptions(filter.field)"
              />
            </div>

            <!-- Remove Filter -->
            <div class="pb-1">
              <Button
                variant="outline"
                size="sm"
                @click="removeFilterFromGroup(groupIndex, filterIndex)"
              >
                <XIcon class="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Add Group Button -->
      <div class="flex justify-between">
        <Button variant="outline" @click="addFilterGroup">
          <PlusIcon class="h-4 w-4 mr-2" />
          Add Filter Group
        </Button>

        <div class="space-x-2">
          <Button variant="outline" @click="clearAllFilters">
            Clear All
          </Button>
          <Button @click="applyFilters">
            Apply Filters
          </Button>
        </div>
      </div>
    </div>

    <!-- Preset Filters -->
    <div v-if="showPresets && savedPresets.length > 0" class="mt-6">
      <h4 class="text-sm font-medium text-gray-700 mb-2">Saved Filter Presets</h4>
      <div class="flex flex-wrap gap-2">
        <Button
          v-for="preset in savedPresets"
          :key="preset.id"
          variant="outline"
          size="sm"
          @click="loadPreset(preset)"
        >
          {{ preset.name }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, DatePicker, Input, Select } from "frappe-ui"
import { MinusIcon, PlusIcon, XIcon } from "lucide-vue-next"
import { computed, ref, watch } from "vue"

// Props
const props = defineProps({
	availableFields: {
		type: Array,
		required: true,
	},
	showPresets: {
		type: Boolean,
		default: true,
	},
	savedPresets: {
		type: Array,
		default: () => [],
	},
})

// Emits
const emit = defineEmits(["apply-filters", "save-preset"])

// Reactive state
const filterGroups = ref([
	{
		logic: "AND",
		filters: [
			{
				field: null,
				operator: null,
				value: "",
			},
		],
	},
])

const activeFilters = ref([])

// Computed properties
const logicOptions = [
	{ label: "AND", value: "AND" },
	{ label: "OR", value: "OR" },
]

const operators = {
	text: [
		{ label: "Equals", value: "eq" },
		{ label: "Contains", value: "contains" },
		{ label: "Starts with", value: "startswith" },
		{ label: "Ends with", value: "endswith" },
		{ label: "Is empty", value: "isempty" },
		{ label: "Is not empty", value: "isnotempty" },
	],
	number: [
		{ label: "Equals", value: "eq" },
		{ label: "Greater than", value: "gt" },
		{ label: "Less than", value: "lt" },
		{ label: "Greater than or equal", value: "gte" },
		{ label: "Less than or equal", value: "lte" },
		{ label: "Between", value: "between" },
	],
	date: [
		{ label: "Equals", value: "eq" },
		{ label: "Before", value: "lt" },
		{ label: "After", value: "gt" },
		{ label: "Between", value: "between" },
		{ label: "Is empty", value: "isempty" },
	],
	select: [
		{ label: "Equals", value: "eq" },
		{ label: "Not equals", value: "neq" },
		{ label: "Is empty", value: "isempty" },
		{ label: "Is not empty", value: "isnotempty" },
	],
}

// Methods
const addFilterGroup = () => {
	filterGroups.value.push({
		logic: "AND",
		filters: [
			{
				field: null,
				operator: null,
				value: "",
			},
		],
	})
}

const removeFilterGroup = (groupIndex) => {
	if (filterGroups.value.length > 1) {
		filterGroups.value.splice(groupIndex, 1)
	}
}

const addFilterToGroup = (groupIndex) => {
	filterGroups.value[groupIndex].filters.push({
		field: null,
		operator: null,
		value: "",
	})
}

const removeFilterFromGroup = (groupIndex, filterIndex) => {
	if (filterGroups.value[groupIndex].filters.length > 1) {
		filterGroups.value[groupIndex].filters.splice(filterIndex, 1)
	}
}

const getOperatorsForField = (field) => {
	if (!field) return []
	return operators[field.type] || operators.text
}

const getInputComponent = (field) => {
	if (!field) return "Input"

	switch (field.type) {
		case "date":
			return "DatePicker"
		case "select":
			return "Select"
		default:
			return "Input"
	}
}

const getInputType = (field) => {
	if (!field) return "text"

	switch (field.type) {
		case "number":
			return "number"
		case "date":
			return "date"
		default:
			return "text"
	}
}

const getPlaceholder = (field) => {
	if (!field) return "Enter value"
	return `Enter ${field.label.toLowerCase()}`
}

const getSelectOptions = (field) => {
	if (!field || field.type !== "select") return []
	return field.options || []
}

const applyFilters = () => {
	// Convert filter groups to active filters
	activeFilters.value = []

	filterGroups.value.forEach((group, groupIndex) => {
		group.filters.forEach((filter, filterIndex) => {
			if (
				filter.field &&
				filter.operator &&
				(filter.value ||
					filter.operator.value === "isempty" ||
					filter.operator.value === "isnotempty")
			) {
				activeFilters.value.push({
					id: `${groupIndex}-${filterIndex}`,
					field: filter.field,
					operator: filter.operator,
					value: filter.value,
					groupLogic: group.logic,
				})
			}
		})
	})

	emit("apply-filters", activeFilters.value)
}

const removeFilter = (filterId) => {
	activeFilters.value = activeFilters.value.filter((f) => f.id !== filterId)
	// Update filter groups based on active filters
	rebuildFilterGroups()
}

const clearAllFilters = () => {
	filterGroups.value = [
		{
			logic: "AND",
			filters: [
				{
					field: null,
					operator: null,
					value: "",
				},
			],
		},
	]
	activeFilters.value = []
	emit("apply-filters", [])
}

const rebuildFilterGroups = () => {
	// This would rebuild the filter groups UI based on active filters
	// Implementation depends on how you want to persist the group structure
}

const loadPreset = (preset) => {
	// Load a saved filter preset
	filterGroups.value = preset.groups
	applyFilters()
}

// Watchers
watch(
	() => props.availableFields,
	() => {
		// Reset invalid field selections when available fields change
		filterGroups.value.forEach((group) => {
			group.filters.forEach((filter) => {
				if (
					filter.field &&
					!props.availableFields.find((f) => f.value === filter.field.value)
				) {
					filter.field = null
					filter.operator = null
					filter.value = ""
				}
			})
		})
	},
)
</script>