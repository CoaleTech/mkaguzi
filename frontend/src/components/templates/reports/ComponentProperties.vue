<template>
  <div class="component-properties">
    <div class="space-y-4">
      <!-- Component Type Display -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Component Type</label>
        <div class="text-sm text-gray-900 bg-gray-100 px-3 py-2 rounded">
          {{ getComponentTypeLabel(component.type) }}
        </div>
      </div>

      <!-- Dynamic Properties based on component type -->
      <template v-if="component.type === 'heading'">
        <FormControl
          label="Heading Level"
          v-model="localProperties.level"
          type="select"
          :options="headingLevelOptions"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Heading Text"
          v-model="localProperties.text"
          type="text"
          placeholder="Enter heading text"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Use Variable"
          v-model="localProperties.useVariable"
          type="select"
          :options="variableOptions"
          placeholder="Select a variable (optional)"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Text Alignment"
          v-model="localProperties.alignment"
          type="select"
          :options="alignmentOptions"
          @update:model-value="updateProperties"
        />
      </template>

      <template v-else-if="component.type === 'paragraph'">
        <FormControl
          label="Paragraph Text"
          v-model="localProperties.text"
          type="textarea"
          placeholder="Enter paragraph text"
          rows="4"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Use Variable"
          v-model="localProperties.useVariable"
          type="select"
          :options="variableOptions"
          placeholder="Select a variable (optional)"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Text Alignment"
          v-model="localProperties.alignment"
          type="select"
          :options="alignmentOptions"
          @update:model-value="updateProperties"
        />
      </template>

      <template v-else-if="component.type === 'table'">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Columns</label>
          <div class="space-y-2">
            <div
              v-for="(column, index) in localProperties.columns"
              :key="index"
              class="flex items-center space-x-2"
            >
              <FormControl
                v-model="localProperties.columns[index]"
                type="text"
                placeholder="Column name"
                class="flex-1"
                @update:model-value="updateProperties"
              />
              <Button
                @click="removeColumn(index)"
                variant="ghost"
                size="sm"
                class="text-red-600"
                :disabled="localProperties.columns.length <= 1"
              >
                <X class="w-4 h-4" />
              </Button>
            </div>
            <Button @click="addColumn" variant="outline" size="sm">
              <Plus class="w-4 h-4 mr-1" />
              Add Column
            </Button>
          </div>
        </div>

        <FormControl
          label="Data Source"
          v-model="localProperties.dataSource"
          type="select"
          :options="dataSourceOptions"
          @update:model-value="updateProperties"
        />

        <div class="flex items-center">
          <input
            id="showHeaders"
            v-model="localProperties.showHeaders"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            @change="updateProperties"
          />
          <label for="showHeaders" class="ml-2 block text-sm text-gray-900">
            Show Headers
          </label>
        </div>

        <div class="flex items-center">
          <input
            id="striped"
            v-model="localProperties.striped"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            @change="updateProperties"
          />
          <label for="striped" class="ml-2 block text-sm text-gray-900">
            Striped Rows
          </label>
        </div>
      </template>

      <template v-else-if="component.type === 'chart'">
        <FormControl
          label="Chart Type"
          v-model="localProperties.chartType"
          type="select"
          :options="chartTypeOptions"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Data Source"
          v-model="localProperties.dataSource"
          type="select"
          :options="dataSourceOptions"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Chart Title"
          v-model="localProperties.title"
          type="text"
          placeholder="Chart title"
          @update:model-value="updateProperties"
        />

        <div class="grid grid-cols-2 gap-4">
          <FormControl
            label="Width"
            v-model="localProperties.width"
            type="number"
            placeholder="400"
            @update:model-value="updateProperties"
          />

          <FormControl
            label="Height"
            v-model="localProperties.height"
            type="number"
            placeholder="300"
            @update:model-value="updateProperties"
          />
        </div>

        <div class="flex items-center">
          <input
            id="showLegend"
            v-model="localProperties.showLegend"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            @change="updateProperties"
          />
          <label for="showLegend" class="ml-2 block text-sm text-gray-900">
            Show Legend
          </label>
        </div>
      </template>

      <template v-else-if="component.type === 'metric'">
        <FormControl
          label="Metric Label"
          v-model="localProperties.label"
          type="text"
          placeholder="Metric label"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Value"
          v-model="localProperties.value"
          type="text"
          placeholder="{{ total_amount }}"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Use Variable"
          v-model="localProperties.useVariable"
          type="select"
          :options="variableOptions"
          placeholder="Select a variable (optional)"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Format"
          v-model="localProperties.format"
          type="select"
          :options="formatOptions"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Size"
          v-model="localProperties.size"
          type="select"
          :options="sizeOptions"
          @update:model-value="updateProperties"
        />
      </template>

      <template v-else-if="component.type === 'section'">
        <FormControl
          label="Section Title"
          v-model="localProperties.title"
          type="text"
          placeholder="Section title"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Background Color"
          v-model="localProperties.backgroundColor"
          type="color"
          @update:model-value="updateProperties"
        />

        <div class="flex items-center">
          <input
            id="collapsible"
            v-model="localProperties.collapsible"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            @change="updateProperties"
          />
          <label for="collapsible" class="ml-2 block text-sm text-gray-900">
            Collapsible
          </label>
        </div>
      </template>

      <template v-else-if="component.type === 'divider'">
        <FormControl
          label="Style"
          v-model="localProperties.style"
          type="select"
          :options="dividerStyleOptions"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Thickness"
          v-model="localProperties.thickness"
          type="number"
          min="1"
          max="10"
          @update:model-value="updateProperties"
        />

        <FormControl
          label="Color"
          v-model="localProperties.color"
          type="color"
          @update:model-value="updateProperties"
        />
      </template>

      <template v-else-if="component.type === 'spacer'">
        <FormControl
          label="Height (px)"
          v-model="localProperties.height"
          type="number"
          min="1"
          max="200"
          @update:model-value="updateProperties"
        />
      </template>

      <template v-else-if="component.type === 'list'">
        <FormControl
          label="List Type"
          v-model="localProperties.listType"
          type="select"
          :options="listTypeOptions"
          @update:model-value="updateProperties"
        />

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">List Items</label>
          <div class="space-y-2">
            <div
              v-for="(item, index) in localProperties.items"
              :key="index"
              class="flex items-center space-x-2"
            >
              <FormControl
                v-model="localProperties.items[index]"
                type="text"
                placeholder="List item"
                class="flex-1"
                @update:model-value="updateProperties"
              />
              <Button
                @click="removeListItem(index)"
                variant="ghost"
                size="sm"
                class="text-red-600"
                :disabled="localProperties.items.length <= 1"
              >
                <X class="w-4 h-4" />
              </Button>
            </div>
            <Button @click="addListItem" variant="outline" size="sm">
              <Plus class="w-4 h-4 mr-1" />
              Add Item
            </Button>
          </div>
        </div>
      </template>

      <!-- Common Properties -->
      <div class="border-t pt-4">
        <h4 class="text-sm font-medium text-gray-700 mb-3">Layout</h4>

        <div class="grid grid-cols-2 gap-4">
          <FormControl
            label="Margin Top"
            v-model="localProperties.marginTop"
            type="number"
            min="0"
            max="100"
            @update:model-value="updateProperties"
          />

          <FormControl
            label="Margin Bottom"
            v-model="localProperties.marginBottom"
            type="number"
            min="0"
            max="100"
            @update:model-value="updateProperties"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <FormControl
            label="Padding Left"
            v-model="localProperties.paddingLeft"
            type="number"
            min="0"
            max="100"
            @update:model-value="updateProperties"
          />

          <FormControl
            label="Padding Right"
            v-model="localProperties.paddingRight"
            type="number"
            min="0"
            max="100"
            @update:model-value="updateProperties"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Plus, X } from "lucide-vue-next"
import { computed, onMounted, reactive, ref, watch } from "vue"

// Props
const props = defineProps({
	component: {
		type: Object,
		required: true,
	},
	availableVariables: {
		type: Array,
		default: () => [],
	},
})

// Emits
const emit = defineEmits(["update"])

// Reactive data
const localProperties = reactive({})

// Options
const headingLevelOptions = [
	{ label: "H1", value: 1 },
	{ label: "H2", value: 2 },
	{ label: "H3", value: 3 },
	{ label: "H4", value: 4 },
	{ label: "H5", value: 5 },
	{ label: "H6", value: 6 },
]

const alignmentOptions = [
	{ label: "Left", value: "left" },
	{ label: "Center", value: "center" },
	{ label: "Right", value: "right" },
	{ label: "Justify", value: "justify" },
]

const dataSourceOptions = [
	{ label: "Static Data", value: "static" },
	{ label: "Dynamic Query", value: "dynamic" },
	{ label: "API Endpoint", value: "api" },
]

const chartTypeOptions = [
	{ label: "Bar Chart", value: "bar" },
	{ label: "Line Chart", value: "line" },
	{ label: "Pie Chart", value: "pie" },
	{ label: "Doughnut Chart", value: "doughnut" },
	{ label: "Area Chart", value: "area" },
]

const formatOptions = [
	{ label: "Number", value: "number" },
	{ label: "Currency", value: "currency" },
	{ label: "Percentage", value: "percentage" },
	{ label: "Text", value: "text" },
]

const sizeOptions = [
	{ label: "Small", value: "sm" },
	{ label: "Medium", value: "md" },
	{ label: "Large", value: "lg" },
	{ label: "Extra Large", value: "xl" },
]

const dividerStyleOptions = [
	{ label: "Solid", value: "solid" },
	{ label: "Dashed", value: "dashed" },
	{ label: "Dotted", value: "dotted" },
	{ label: "Double", value: "double" },
]

const listTypeOptions = [
	{ label: "Bulleted List", value: "ul" },
	{ label: "Numbered List", value: "ol" },
]

// Computed
const variableOptions = computed(() => {
	const options = [{ label: "None", value: "" }]
	props.availableVariables.forEach((variable) => {
		options.push({
			label: `${variable.variable_name} (${variable.variable_type})`,
			value: variable.variable_name,
		})
	})
	return options
})

// Methods
const getComponentTypeLabel = (type) => {
	const labels = {
		heading: "Heading",
		paragraph: "Paragraph",
		table: "Table",
		chart: "Chart",
		metric: "Metric Card",
		section: "Section",
		divider: "Divider",
		spacer: "Spacer",
		list: "List",
	}
	return labels[type] || type
}

const updateProperties = () => {
	emit("update", { ...localProperties })
}

const addColumn = () => {
	if (!localProperties.columns) {
		localProperties.columns = []
	}
	localProperties.columns.push(`Column ${localProperties.columns.length + 1}`)
	updateProperties()
}

const removeColumn = (index) => {
	if (localProperties.columns && localProperties.columns.length > 1) {
		localProperties.columns.splice(index, 1)
		updateProperties()
	}
}

const addListItem = () => {
	if (!localProperties.items) {
		localProperties.items = []
	}
	localProperties.items.push(`Item ${localProperties.items.length + 1}`)
	updateProperties()
}

const removeListItem = (index) => {
	if (localProperties.items && localProperties.items.length > 1) {
		localProperties.items.splice(index, 1)
		updateProperties()
	}
}

// Initialize local properties when component changes
watch(
	() => props.component,
	(newComponent) => {
		if (newComponent && newComponent.properties) {
			Object.assign(localProperties, newComponent.properties)
		}
	},
	{ immediate: true, deep: true },
)

// Set default properties if not present
onMounted(() => {
	if (props.component && props.component.properties) {
		Object.assign(localProperties, props.component.properties)
	}
})
</script>

<style scoped>
/* Component-specific styles if needed */
</style>