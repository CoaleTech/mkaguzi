<template>
  <div class="report-preview">
    <!-- Preview Header -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-gray-900">Report Preview</h2>
      <div class="flex items-center space-x-3">
        <Button @click="exportPDF" variant="outline">
          <Download class="w-4 h-4 mr-2" />
          Export PDF
        </Button>
        <Button @click="printReport" variant="outline">
          <Printer class="w-4 h-4 mr-2" />
          Print
        </Button>
        <Button @click="$emit('close')" variant="solid">
          Close
        </Button>
      </div>
    </div>

    <!-- Preview Container -->
    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <!-- Report Content -->
      <div
        class="report-content p-8"
        :class="previewClass"
        ref="reportContent"
      >
        <!-- Header -->
        <div v-if="settings.showHeader" class="report-header mb-8 pb-4 border-b-2 border-gray-300">
          <div class="text-center">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ settings.name || 'Report Title' }}</h1>
            <p class="text-gray-600">Generated on {{ formatDate(new Date()) }}</p>
            <p class="text-gray-600">Category: {{ settings.category }}</p>
          </div>
        </div>

        <!-- Report Body -->
        <div class="report-body space-y-6">
          <div
            v-for="component in template.components"
            :key="component.id"
            class="component-preview"
            :style="getComponentStyle(component)"
          >
            <!-- Render Component Based on Type -->
            <template v-if="component.type === 'heading'">
              <component
                :is="`h${component.properties.level || 1}`"
                :class="getHeadingClass(component.properties.level || 1)"
              >
                {{ component.properties.text || 'Heading Text' }}
              </component>
            </template>

            <template v-else-if="component.type === 'paragraph'">
              <p
                :class="getParagraphClass(component.properties.alignment)"
                v-html="renderTemplate(component.properties.text || 'Paragraph text content')"
              ></p>
            </template>

            <template v-else-if="component.type === 'table'">
              <div class="table-container">
                <table :class="getTableClass(component.properties)">
                  <thead v-if="component.properties.showHeaders !== false">
                    <tr>
                      <th
                        v-for="column in component.properties.columns"
                        :key="column"
                        class="px-4 py-2 text-left font-semibold text-gray-900 bg-gray-50 border-b"
                      >
                        {{ column }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <!-- Sample data for preview -->
                    <tr
                      v-for="i in 3"
                      :key="i"
                      :class="{ 'bg-gray-50': component.properties.striped && i % 2 === 0 }"
                    >
                      <td
                        v-for="column in component.properties.columns"
                        :key="column"
                        class="px-4 py-2 border-b border-gray-200"
                      >
                        Sample {{ column.toLowerCase() }} {{ i }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </template>

            <template v-else-if="component.type === 'chart'">
              <div class="chart-container">
                <h4 v-if="component.properties.title" class="text-lg font-semibold mb-4">
                  {{ component.properties.title }}
                </h4>
                <div
                  class="chart-placeholder bg-gray-100 border-2 border-dashed border-gray-300 rounded flex items-center justify-center"
                  :style="{ width: (component.properties.width || 400) + 'px', height: (component.properties.height || 300) + 'px' }"
                >
                  <div class="text-center text-gray-500">
                    <BarChart3 class="w-12 h-12 mx-auto mb-2" />
                    <p>{{ getChartTypeLabel(component.properties.chartType) }}</p>
                    <p class="text-sm">Chart Preview</p>
                  </div>
                </div>
                <div v-if="component.properties.showLegend" class="chart-legend mt-2">
                  <div class="flex flex-wrap gap-4 text-sm">
                    <div v-for="i in 3" :key="i" class="flex items-center">
                      <div class="w-3 h-3 rounded mr-2" :style="{ backgroundColor: getChartColor(i) }"></div>
                      <span>Series {{ i }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <template v-else-if="component.type === 'metric'">
              <div class="metric-card bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                <div class="text-center">
                  <div :class="getMetricValueClass(component.properties.size)">
                    {{ renderTemplate(component.properties.value || '0') }}
                  </div>
                  <div class="text-gray-600 mt-2">
                    {{ component.properties.label || 'Metric Label' }}
                  </div>
                </div>
              </div>
            </template>

            <template v-else-if="component.type === 'section'">
              <div
                class="section-container"
                :style="{ backgroundColor: component.properties.backgroundColor || 'transparent' }"
              >
                <h3 v-if="component.properties.title" class="text-xl font-semibold mb-4">
                  {{ component.properties.title }}
                </h3>
                <div class="section-content">
                  <!-- Section content would be rendered here -->
                  <p class="text-gray-600 italic">Section content goes here...</p>
                </div>
              </div>
            </template>

            <template v-else-if="component.type === 'divider'">
              <hr
                :class="getDividerClass(component.properties.style)"
                :style="{
                  height: (component.properties.thickness || 1) + 'px',
                  backgroundColor: component.properties.color || '#e5e7eb'
                }"
              />
            </template>

            <template v-else-if="component.type === 'spacer'">
              <div :style="{ height: (component.properties.height || 20) + 'px' }"></div>
            </template>

            <template v-else-if="component.type === 'list'">
              <component
                :is="component.properties.listType || 'ul'"
                :class="getListClass(component.properties.listType)"
              >
                <li
                  v-for="item in component.properties.items"
                  :key="item"
                  v-html="renderTemplate(item)"
                ></li>
              </component>
            </template>

            <!-- Fallback for unknown component types -->
            <template v-else>
              <div class="unknown-component bg-yellow-50 border border-yellow-200 rounded p-4">
                <p class="text-yellow-800">Unknown component type: {{ component.type }}</p>
              </div>
            </template>
          </div>
        </div>

        <!-- Footer -->
        <div v-if="settings.showFooter" class="report-footer mt-12 pt-4 border-t-2 border-gray-300">
          <div class="text-center text-sm text-gray-600">
            <p class="font-semibold">Confidential - Internal Use Only</p>
            <p>Generated by Internal Audit System</p>
            <p>Page 1 of 1</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { BarChart3, Download, Printer } from "lucide-vue-next"
import { computed, ref } from "vue"

// Props
const props = defineProps({
	template: {
		type: Object,
		required: true,
	},
	settings: {
		type: Object,
		required: true,
	},
})

// Emits
const emit = defineEmits(["close"])

// Refs
const reportContent = ref(null)

// Computed
const previewClass = computed(() => {
	return {
		"preview-portrait": props.settings.orientation === "portrait",
		"preview-landscape": props.settings.orientation === "landscape",
	}
})

// Methods
const formatDate = (date) => {
	return date.toLocaleDateString("en-US", {
		year: "numeric",
		month: "long",
		day: "numeric",
	})
}

const getComponentStyle = (component) => {
	const style = {}

	if (component.properties) {
		if (component.properties.marginTop) {
			style.marginTop = component.properties.marginTop + "px"
		}
		if (component.properties.marginBottom) {
			style.marginBottom = component.properties.marginBottom + "px"
		}
		if (component.properties.paddingLeft) {
			style.paddingLeft = component.properties.paddingLeft + "px"
		}
		if (component.properties.paddingRight) {
			style.paddingRight = component.properties.paddingRight + "px"
		}
	}

	return style
}

const getHeadingClass = (level) => {
	const classes = {
		1: "text-3xl font-bold text-gray-900 mb-4",
		2: "text-2xl font-semibold text-gray-900 mb-3",
		3: "text-xl font-semibold text-gray-900 mb-2",
		4: "text-lg font-medium text-gray-900 mb-2",
		5: "text-base font-medium text-gray-900 mb-2",
		6: "text-sm font-medium text-gray-900 mb-1",
	}
	return classes[level] || classes[1]
}

const getParagraphClass = (alignment) => {
	const classes = {
		left: "text-left",
		center: "text-center",
		right: "text-right",
		justify: "text-justify",
	}
	return `text-gray-700 leading-relaxed ${classes[alignment] || classes.left}`
}

const getTableClass = (properties) => {
	let classes = "min-w-full divide-y divide-gray-200"

	if (properties.striped) {
		classes += " table-striped"
	}

	return classes
}

const getChartTypeLabel = (type) => {
	const labels = {
		bar: "Bar Chart",
		line: "Line Chart",
		pie: "Pie Chart",
		doughnut: "Doughnut Chart",
		area: "Area Chart",
	}
	return labels[type] || "Chart"
}

const getChartColor = (index) => {
	const colors = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"]
	return colors[index - 1] || colors[0]
}

const getMetricValueClass = (size) => {
	const classes = {
		sm: "text-2xl font-bold text-gray-900",
		md: "text-3xl font-bold text-gray-900",
		lg: "text-4xl font-bold text-gray-900",
		xl: "text-5xl font-bold text-gray-900",
	}
	return classes[size] || classes.md
}

const getDividerClass = (style) => {
	const classes = {
		solid: "border-gray-300",
		dashed: "border-dashed border-gray-300",
		dotted: "border-dotted border-gray-300",
		double: "border-double border-gray-300",
	}
	return classes[style] || classes.solid
}

const getListClass = (type) => {
	const classes = {
		ul: "list-disc list-inside space-y-1",
		ol: "list-decimal list-inside space-y-1",
	}
	return `text-gray-700 ${classes[type] || classes.ul}`
}

const renderTemplate = (text) => {
	// Simple template rendering for preview
	// In a real implementation, this would use Jinja2 or similar
	return text.replace(/\{\{([^}]+)\}\}/g, (match, variable) => {
		// Mock some common variables
		const mockData = {
			total_amount: "$125,000",
			total_records: "1,234",
			current_date: new Date().toLocaleDateString(),
			company_name: "Sample Company Ltd.",
		}
		return mockData[variable.trim()] || match
	})
}

const exportPDF = async () => {
	try {
		// In a real implementation, this would use a PDF generation library
		// For now, we'll use the browser's print functionality
		window.print()
	} catch (error) {
		console.error("Error exporting PDF:", error)
	}
}

const printReport = () => {
	window.print()
}
</script>

<style scoped>
.report-content {
  font-family: 'Times New Roman', serif;
  line-height: 1.6;
  color: #374151;
}

.preview-portrait {
  max-width: 595px; /* A4 width */
  margin: 0 auto;
}

.preview-landscape {
  max-width: 842px; /* A4 height */
  margin: 0 auto;
}

.table-container {
  overflow-x: auto;
}

.chart-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-card {
  max-width: 300px;
  margin: 0 auto;
}

.section-container {
  padding: 1rem;
  border-radius: 0.5rem;
}

.unknown-component {
  border-left: 4px solid #f59e0b;
}

@media print {
  .report-preview {
    box-shadow: none;
  }

  .report-content {
    box-shadow: none;
    border: none;
  }
}
</style>