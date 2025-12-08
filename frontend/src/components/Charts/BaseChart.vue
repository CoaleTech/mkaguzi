<template>
  <div class="bg-white rounded-lg border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
        <p v-if="subtitle" class="text-sm text-gray-600">{{ subtitle }}</p>
      </div>
      <div class="flex items-center space-x-2">
        <Button
          v-if="showRefresh"
          variant="ghost"
          size="sm"
          @click="$emit('refresh')"
          :loading="loading"
        >
          <RefreshCwIcon class="h-4 w-4" />
        </Button>
        <Button
          v-if="showExport"
          variant="ghost"
          size="sm"
          @click="$emit('export')"
        >
          <DownloadIcon class="h-4 w-4" />
        </Button>
      </div>
    </div>
    <div class="relative" :style="{ height: height + 'px' }">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import {
	ArcElement,
	BarController,
	BarElement,
	CategoryScale,
	Chart as ChartJS,
	DoughnutController,
	Legend,
	LineController,
	LineElement,
	LinearScale,
	PieController,
	PointElement,
	PolarAreaController,
	RadarController,
	RadialLinearScale,
	Title,
	Tooltip,
} from "chart.js"
import { Button } from "frappe-ui"
import { DownloadIcon, RefreshCwIcon } from "lucide-vue-next"
import { nextTick, onMounted, onUnmounted, ref, watch } from "vue"
import { Bar, Doughnut, Line, Pie, PolarArea, Radar } from "vue-chartjs"

// Register Chart.js components
ChartJS.register(
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
	BarElement,
	Title,
	Tooltip,
	Legend,
	ArcElement,
	RadialLinearScale,
	// Register controllers
	BarController,
	LineController,
	DoughnutController,
	PieController,
	PolarAreaController,
	RadarController,
)

// Props
const props = defineProps({
	title: {
		type: String,
		required: true,
	},
	subtitle: {
		type: String,
		default: "",
	},
	type: {
		type: String,
		default: "line",
		validator: (value) =>
			["line", "bar", "doughnut", "pie", "radar", "polarArea"].includes(value),
	},
	data: {
		type: Object,
		required: true,
	},
	options: {
		type: Object,
		default: () => ({}),
	},
	height: {
		type: Number,
		default: 300,
	},
	showRefresh: {
		type: Boolean,
		default: false,
	},
	showExport: {
		type: Boolean,
		default: false,
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

// Emits
const emit = defineEmits(["refresh", "export"])

// Refs
const chartCanvas = ref(null)
let chart = null

// Methods
const createChart = () => {
	// Destroy existing chart first
	destroyChart()

	if (!chartCanvas.value) return

	const ctx = chartCanvas.value.getContext("2d")

	const defaultOptions = {
		responsive: true,
		maintainAspectRatio: false,
		plugins: {
			legend: {
				position: "top",
			},
			title: {
				display: false,
			},
		},
		scales:
			props.type !== "doughnut" &&
			props.type !== "pie" &&
			props.type !== "radar" &&
			props.type !== "polarArea"
				? {
						y: {
							beginAtZero: true,
						},
					}
				: {},
	}

	const mergedOptions = { ...defaultOptions, ...props.options }

	chart = new ChartJS(ctx, {
		type: props.type,
		data: props.data,
		options: mergedOptions,
	})
}

const destroyChart = () => {
	if (chart) {
		chart.destroy()
		chart = null
	}
}

const updateChart = () => {
	if (chart) {
		chart.data = props.data
		chart.options = { ...chart.options, ...props.options }
		chart.update()
	}
}

// Watchers
watch(
	() => props.data,
	() => {
		if (chart) {
			updateChart()
		} else {
			nextTick(() => createChart())
		}
	},
	{ deep: true },
)

watch(
	() => props.options,
	() => {
		if (chart) {
			updateChart()
		}
	},
	{ deep: true },
)

// Lifecycle
onMounted(() => {
	nextTick(() => createChart())
})

onUnmounted(() => {
	destroyChart()
})
</script>