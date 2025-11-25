<template>
  <div class="bg-white rounded-lg border border-gray-200 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-medium text-gray-900">
          Risk Heat Map
        </h3>
        <p class="text-sm text-gray-500 mt-1">
          Visual representation of risk levels across different categories
        </p>
      </div>
      <div class="flex items-center space-x-2">
        <Button
          variant="outline"
          size="sm"
          @click="exportHeatMap"
        >
          <DownloadIcon class="h-4 w-4 mr-2" />
          Export
        </Button>
      </div>
    </div>

    <!-- Controls -->
    <div class="flex flex-wrap items-center gap-4 mb-6">
      <!-- Risk Scale Toggle -->
      <div class="flex items-center space-x-2">
        <label class="text-sm font-medium text-gray-700">Scale:</label>
        <div class="flex rounded-md">
          <button
            v-for="scale in riskScales"
            :key="scale.value"
            :class="[
              'px-3 py-1 text-sm font-medium rounded-l-md first:rounded-l-md last:rounded-r-md border',
              selectedScale === scale.value
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            ]"
            @click="selectedScale = scale.value"
          >
            {{ scale.label }}
          </button>
        </div>
      </div>

      <!-- Category Filter -->
      <div class="flex items-center space-x-2">
        <label class="text-sm font-medium text-gray-700">Category:</label>
        <Select
          v-model="selectedCategory"
          :options="categoryOptions"
          placeholder="All Categories"
          class="w-48"
        />
      </div>

      <!-- View Toggle -->
      <div class="flex items-center space-x-2">
        <label class="text-sm font-medium text-gray-700">View:</label>
        <div class="flex rounded-md">
          <button
            v-for="view in viewOptions"
            :key="view.value"
            :class="[
              'px-3 py-1 text-sm font-medium rounded-l-md first:rounded-l-md last:rounded-r-md border',
              selectedView === view.value
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            ]"
            @click="selectedView = view.value"
          >
            {{ view.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Heat Map Grid -->
    <div class="relative">
      <!-- Y-axis labels (Impact) -->
      <div class="absolute left-0 top-0 bottom-0 flex flex-col justify-between pr-4">
        <div
          v-for="level in impactLevels"
          :key="level.value"
          class="text-sm font-medium text-gray-700 text-right h-16 flex items-center justify-end"
        >
          {{ level.label }}
        </div>
      </div>

      <!-- Main Grid -->
      <div class="ml-20 relative">
        <!-- X-axis labels (Likelihood) -->
        <div class="flex mb-2">
          <div
            v-for="level in likelihoodLevels"
            :key="level.value"
            class="text-sm font-medium text-gray-700 text-center"
            :style="{ width: `${100 / likelihoodLevels.length}%` }"
          >
            {{ level.label }}
          </div>
        </div>

        <!-- Grid Cells -->
        <div class="grid gap-1" :style="{ gridTemplateColumns: `repeat(${likelihoodLevels.length}, 1fr)` }">
          <div
            v-for="impact in impactLevels"
            :key="impact.value"
            class="contents"
          >
            <div
              v-for="likelihood in likelihoodLevels"
              :key="likelihood.value"
              :class="[
                'h-16 w-full rounded border-2 border-white cursor-pointer transition-all hover:scale-105 relative group',
                getRiskColor(impact.value, likelihood.value)
              ]"
              @click="onCellClick(impact.value, likelihood.value)"
              @mouseenter="hoveredCell = { impact: impact.value, likelihood: likelihood.value }"
              @mouseleave="hoveredCell = null"
            >
              <!-- Risk Count -->
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-white font-bold text-lg">
                  {{ getRiskCount(impact.value, likelihood.value) }}
                </span>
              </div>

              <!-- Tooltip -->
              <div
                v-if="hoveredCell && hoveredCell.impact === impact.value && hoveredCell.likelihood === likelihood.value"
                class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg whitespace-nowrap z-10 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <div class="font-medium">
                  {{ getRiskLevel(impact.value, likelihood.value) }}
                </div>
                <div class="text-xs text-gray-300">
                  Impact: {{ impact.label }} | Likelihood: {{ likelihood.label }}
                </div>
                <div class="text-xs">
                  {{ getRiskCount(impact.value, likelihood.value) }} risks
                </div>
                <!-- Arrow -->
                <div class="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div class="mt-8">
      <h4 class="text-sm font-medium text-gray-700 mb-3">Risk Levels</h4>
      <div class="flex flex-wrap gap-4">
        <div
          v-for="level in riskLevels"
          :key="level.name"
          class="flex items-center space-x-2"
        >
          <div
            :class="['w-4 h-4 rounded', level.color]"
          ></div>
          <span class="text-sm text-gray-600">
            {{ level.name }} ({{ level.range }})
          </span>
        </div>
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="text-2xl font-bold text-gray-900">
          {{ totalRisks }}
        </div>
        <div class="text-sm text-gray-500">Total Risks</div>
      </div>
      <div class="bg-red-50 rounded-lg p-4">
        <div class="text-2xl font-bold text-red-600">
          {{ highRiskCount }}
        </div>
        <div class="text-sm text-gray-500">High Risk</div>
      </div>
      <div class="bg-yellow-50 rounded-lg p-4">
        <div class="text-2xl font-bold text-yellow-600">
          {{ mediumRiskCount }}
        </div>
        <div class="text-sm text-gray-500">Medium Risk</div>
      </div>
      <div class="bg-green-50 rounded-lg p-4">
        <div class="text-2xl font-bold text-green-600">
          {{ lowRiskCount }}
        </div>
        <div class="text-sm text-gray-500">Low Risk</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Select } from "frappe-ui"
import { DownloadIcon } from "lucide-vue-next"
import { computed, ref, watch } from "vue"

// Props
const props = defineProps({
	risks: {
		type: Array,
		default: () => [],
	},
	categories: {
		type: Array,
		default: () => [],
	},
})

// Emits
const emit = defineEmits(["cell-click", "export"])

// Reactive state
const selectedScale = ref(5) // 3x3 or 5x5
const selectedCategory = ref("")
const selectedView = ref("count") // count or percentage
const hoveredCell = ref(null)

// Constants
const riskScales = [
	{ value: 3, label: "3x3" },
	{ value: 5, label: "5x5" },
]

const viewOptions = [
	{ value: "count", label: "Count" },
	{ value: "percentage", label: "Percentage" },
]

const impactLevels = computed(() => {
	if (selectedScale.value === 3) {
		return [
			{ value: 3, label: "High" },
			{ value: 2, label: "Medium" },
			{ value: 1, label: "Low" },
		]
	} else {
		return [
			{ value: 5, label: "Very High" },
			{ value: 4, label: "High" },
			{ value: 3, label: "Medium" },
			{ value: 2, label: "Low" },
			{ value: 1, label: "Very Low" },
		]
	}
})

const likelihoodLevels = computed(() => {
	if (selectedScale.value === 3) {
		return [
			{ value: 1, label: "Low" },
			{ value: 2, label: "Medium" },
			{ value: 3, label: "High" },
		]
	} else {
		return [
			{ value: 1, label: "Very Low" },
			{ value: 2, label: "Low" },
			{ value: 3, label: "Medium" },
			{ value: 4, label: "High" },
			{ value: 5, label: "Very High" },
		]
	}
})

const riskLevels = computed(() => {
	if (selectedScale.value === 3) {
		return [
			{ name: "Low", range: "1-2", color: "bg-green-500" },
			{ name: "Medium", range: "3-4", color: "bg-yellow-500" },
			{ name: "High", range: "5-9", color: "bg-red-500" },
		]
	} else {
		return [
			{ name: "Very Low", range: "1-4", color: "bg-green-200" },
			{ name: "Low", range: "5-8", color: "bg-green-400" },
			{ name: "Medium", range: "9-12", color: "bg-yellow-400" },
			{ name: "High", range: "13-16", color: "bg-orange-500" },
			{ name: "Very High", range: "17-25", color: "bg-red-500" },
		]
	}
})

const categoryOptions = computed(() => {
	const options = [{ label: "All Categories", value: "" }]
	props.categories.forEach((category) => {
		options.push({ label: category.name, value: category.id })
	})
	return options
})

const filteredRisks = computed(() => {
	let risks = props.risks

	if (selectedCategory.value) {
		risks = risks.filter((risk) => risk.category_id === selectedCategory.value)
	}

	return risks
})

const totalRisks = computed(() => filteredRisks.value.length)

const highRiskCount = computed(() => {
	return filteredRisks.value.filter(
		(risk) => getRiskLevelValue(risk.impact, risk.likelihood) >= 4,
	).length
})

const mediumRiskCount = computed(() => {
	return filteredRisks.value.filter((risk) => {
		const level = getRiskLevelValue(risk.impact, risk.likelihood)
		return level >= 2 && level <= 3
	}).length
})

const lowRiskCount = computed(() => {
	return filteredRisks.value.filter(
		(risk) => getRiskLevelValue(risk.impact, risk.likelihood) <= 1,
	).length
})

// Methods
const getRiskCount = (impact, likelihood) => {
	const count = filteredRisks.value.filter(
		(risk) => risk.impact === impact && risk.likelihood === likelihood,
	).length

	if (selectedView.value === "percentage" && totalRisks.value > 0) {
		return Math.round((count / totalRisks.value) * 100) + "%"
	}

	return count
}

const getRiskColor = (impact, likelihood) => {
	const riskValue = impact * likelihood

	if (selectedScale.value === 3) {
		if (riskValue >= 6) return "bg-red-500"
		if (riskValue >= 3) return "bg-yellow-500"
		return "bg-green-500"
	} else {
		if (riskValue >= 16) return "bg-red-500"
		if (riskValue >= 12) return "bg-orange-500"
		if (riskValue >= 9) return "bg-yellow-400"
		if (riskValue >= 5) return "bg-green-400"
		return "bg-green-200"
	}
}

const getRiskLevel = (impact, likelihood) => {
	const riskValue = impact * likelihood

	if (selectedScale.value === 3) {
		if (riskValue >= 6) return "High Risk"
		if (riskValue >= 3) return "Medium Risk"
		return "Low Risk"
	} else {
		if (riskValue >= 16) return "Very High Risk"
		if (riskValue >= 12) return "High Risk"
		if (riskValue >= 9) return "Medium Risk"
		if (riskValue >= 5) return "Low Risk"
		return "Very Low Risk"
	}
}

const getRiskLevelValue = (impact, likelihood) => {
	const riskValue = impact * likelihood

	if (selectedScale.value === 3) {
		if (riskValue >= 6) return 3 // High
		if (riskValue >= 3) return 2 // Medium
		return 1 // Low
	} else {
		if (riskValue >= 16) return 5 // Very High
		if (riskValue >= 12) return 4 // High
		if (riskValue >= 9) return 3 // Medium
		if (riskValue >= 5) return 2 // Low
		return 1 // Very Low
	}
}

const onCellClick = (impact, likelihood) => {
	const risks = filteredRisks.value.filter(
		(risk) => risk.impact === impact && risk.likelihood === likelihood,
	)

	emit("cell-click", {
		impact,
		likelihood,
		risks,
		riskLevel: getRiskLevel(impact, likelihood),
	})
}

const exportHeatMap = () => {
	emit("export", {
		scale: selectedScale.value,
		category: selectedCategory.value,
		view: selectedView.value,
		risks: filteredRisks.value,
	})
}

// Watch for scale changes to reset view
watch(selectedScale, () => {
	hoveredCell.value = null
})
</script>