<template>
  <div class="chart-section">
    <h4 v-if="section.config?.title" class="chart-title">
      {{ section.config.title }}
    </h4>

    <div v-if="preview && !data" class="chart-preview">
      <div class="preview-info">
        <component :is="getChartIcon() + 'Icon'" class="preview-icon" />
        <div class="preview-text">
          <h5>{{ getChartLabel() }}</h5>
          <p>Chart will display data from: {{ section.config?.data_source || 'No data source configured' }}</p>
          <p v-if="section.config?.x_field && section.config?.y_field">
            X-Axis: {{ section.config.x_field }} | Y-Axis: {{ section.config.y_field }}
          </p>
        </div>
      </div>
    </div>

    <div v-else-if="data && data.length > 0" class="chart-container">
      <canvas
        ref="chartCanvas"
        :style="chartStyle"
      ></canvas>
    </div>

    <div v-else class="empty-chart">
      <component :is="getChartIcon() + 'Icon'" class="empty-icon" />
      <p>No data available for this chart</p>
    </div>
  </div>
</template>

<script setup>
import {
	ActivityIcon,
	AreaChartIcon,
	BarChart3Icon,
	CircleDotIcon,
	GaugeIcon,
	LineChartIcon,
	PieChartIcon,
} from "lucide-vue-next"
import { computed, nextTick, onMounted, ref, watch } from "vue"

// Mock chart library - in real implementation, use Chart.js or similar
const Chart = {
	create: (canvas, config) => {
		const ctx = canvas.getContext("2d")
		return new MockChart(ctx, config)
	},
}

class MockChart {
	constructor(ctx, config) {
		this.ctx = ctx
		this.config = config
		this.render()
	}

	render() {
		const { ctx } = this
		const { width, height } = ctx.canvas

		// Clear canvas
		ctx.clearRect(0, 0, width, height)

		// Draw mock chart based on type
		const type = this.config.type
		const data = this.config.data?.datasets?.[0]?.data || []
		const labels = this.config.data?.labels || []

		if (type === "bar") {
			this.drawBarChart(data, labels)
		} else if (type === "line") {
			this.drawLineChart(data, labels)
		} else if (type === "pie" || type === "donut") {
			this.drawPieChart(data, labels)
		} else {
			this.drawPlaceholder()
		}
	}

	drawBarChart(data, labels) {
		const { ctx } = this
		const { width, height } = ctx.canvas
		const margin = 40
		const chartWidth = width - margin * 2
		const chartHeight = height - margin * 2

		if (data.length === 0) return this.drawPlaceholder()

		const maxValue = Math.max(...data)
		const barWidth = (chartWidth / data.length) * 0.8
		const barSpacing = (chartWidth / data.length) * 0.2

		ctx.fillStyle = "#3b82f6"

		data.forEach((value, index) => {
			const barHeight = (value / maxValue) * chartHeight
			const x = margin + index * (barWidth + barSpacing)
			const y = height - margin - barHeight

			ctx.fillRect(x, y, barWidth, barHeight)

			// Draw labels
			ctx.fillStyle = "#374151"
			ctx.font = "12px sans-serif"
			ctx.textAlign = "center"
			ctx.fillText(
				labels[index] || `Item ${index + 1}`,
				x + barWidth / 2,
				height - 10,
			)
			ctx.fillStyle = "#3b82f6"
		})
	}

	drawLineChart(data, labels) {
		const { ctx } = this
		const { width, height } = ctx.canvas
		const margin = 40
		const chartWidth = width - margin * 2
		const chartHeight = height - margin * 2

		if (data.length === 0) return this.drawPlaceholder()

		const maxValue = Math.max(...data)
		const stepX = chartWidth / (data.length - 1)

		ctx.strokeStyle = "#3b82f6"
		ctx.lineWidth = 2
		ctx.beginPath()

		data.forEach((value, index) => {
			const x = margin + index * stepX
			const y = height - margin - (value / maxValue) * chartHeight

			if (index === 0) {
				ctx.moveTo(x, y)
			} else {
				ctx.lineTo(x, y)
			}

			// Draw points
			ctx.fillStyle = "#3b82f6"
			ctx.beginPath()
			ctx.arc(x, y, 4, 0, 2 * Math.PI)
			ctx.fill()
		})

		ctx.stroke()
	}

	drawPieChart(data, labels) {
		const { ctx } = this
		const { width, height } = ctx.canvas
		const centerX = width / 2
		const centerY = height / 2
		const radius = Math.min(width, height) / 2 - 20

		if (data.length === 0) return this.drawPlaceholder()

		const total = data.reduce((sum, value) => sum + value, 0)
		const colors = [
			"#3b82f6",
			"#10b981",
			"#f59e0b",
			"#ef4444",
			"#525252",
			"#06b6d4",
		]

		let startAngle = 0

		data.forEach((value, index) => {
			const sliceAngle = (value / total) * 2 * Math.PI

			ctx.fillStyle = colors[index % colors.length]
			ctx.beginPath()
			ctx.moveTo(centerX, centerY)
			ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle)
			ctx.closePath()
			ctx.fill()

			startAngle += sliceAngle
		})
	}

	drawPlaceholder() {
		const { ctx } = this
		const { width, height } = ctx.canvas

		ctx.fillStyle = "#f3f4f6"
		ctx.fillRect(0, 0, width, height)

		ctx.fillStyle = "#9ca3af"
		ctx.font = "16px sans-serif"
		ctx.textAlign = "center"
		ctx.fillText("Chart Preview", width / 2, height / 2)
	}

	update() {
		this.render()
	}

	destroy() {
		// Cleanup if needed
	}
}

const props = defineProps({
	section: {
		type: Object,
		required: true,
	},
	data: {
		type: Array,
		default: () => [],
	},
	preview: {
		type: Boolean,
		default: true,
	},
})

const chartCanvas = ref(null)
const chartInstance = ref(null)

const chartStyle = computed(() => {
	const styling = props.section.config?.styling || {}
	return {
		width: styling.width || "100%",
		height: `${styling.height || 400}px`,
		maxWidth: "100%",
	}
})

const getChartIcon = () => {
	const type = props.section.config?.chart_type || "bar"
	const iconMap = {
		bar: "BarChart3",
		line: "LineChart",
		pie: "PieChart",
		donut: "CircleDot",
		area: "AreaChart",
		gauge: "Gauge",
		kpi: "Activity",
	}
	return iconMap[type] || "BarChart3"
}

const getChartLabel = () => {
	const type = props.section.config?.chart_type || "bar"
	const labelMap = {
		bar: "Bar Chart",
		line: "Line Chart",
		pie: "Pie Chart",
		donut: "Donut Chart",
		area: "Area Chart",
		gauge: "Gauge Chart",
		kpi: "KPI Card",
	}
	return labelMap[type] || "Chart"
}

const createChart = () => {
	if (!chartCanvas.value || props.preview) return

	const chartType = props.section.config?.chart_type || "bar"
	const chartData = prepareChartData()

	const config = {
		type: chartType,
		data: chartData,
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				legend: {
					display: true,
					position: "top",
				},
				title: {
					display: !!props.section.config?.title,
					text: props.section.config?.title,
				},
			},
			scales:
				chartType !== "pie" && chartType !== "donut"
					? {
							x: {
								display: true,
								title: {
									display: !!props.section.config?.x_axis_title,
									text: props.section.config?.x_axis_title,
								},
							},
							y: {
								display: true,
								title: {
									display: !!props.section.config?.y_axis_title,
									text: props.section.config?.y_axis_title,
								},
							},
						}
					: {},
		},
	}

	if (chartInstance.value) {
		chartInstance.value.destroy()
	}

	chartInstance.value = Chart.create(chartCanvas.value, config)
}

const prepareChartData = () => {
	if (!props.data || props.data.length === 0) {
		return {
			labels: ["No Data"],
			datasets: [
				{
					label: "No Data",
					data: [0],
					backgroundColor: ["#e5e7eb"],
					borderColor: ["#9ca3af"],
					borderWidth: 1,
				},
			],
		}
	}

	const xField = props.section.config?.x_field
	const yField = props.section.config?.y_field

	if (!xField || !yField) {
		return {
			labels: ["Configuration Required"],
			datasets: [
				{
					label: "Please configure X and Y fields",
					data: [1],
					backgroundColor: ["#fbbf24"],
					borderColor: ["#f59e0b"],
					borderWidth: 1,
				},
			],
		}
	}

	const labels = props.data.map((item) => item[xField])
	const dataValues = props.data.map((item) => item[yField])
	const colors = props.section.config?.styling?.colors || [
		"#3b82f6",
		"#10b981",
		"#f59e0b",
		"#ef4444",
	]

	return {
		labels: labels,
		datasets: [
			{
				label: props.section.config?.title || "Data Series",
				data: dataValues,
				backgroundColor: colors,
				borderColor: colors.map((color) => color),
				borderWidth: 1,
			},
		],
	}
}

// Lifecycle
onMounted(() => {
	nextTick(() => {
		if (!props.preview && props.data) {
			createChart()
		}
	})
})

// Watchers
watch(
	() => props.data,
	() => {
		nextTick(() => {
			if (!props.preview) {
				createChart()
			}
		})
	},
	{ deep: true },
)

watch(
	() => props.section.config,
	() => {
		nextTick(() => {
			if (!props.preview) {
				createChart()
			}
		})
	},
	{ deep: true },
)
</script>

<style scoped>
.chart-section {
  margin: 1.5rem 0;
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
  text-align: center;
}

.chart-preview {
  padding: 2rem;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  background: #f9fafb;
}

.preview-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  text-align: left;
}

.preview-icon {
  width: 3rem;
  height: 3rem;
  color: #6b7280;
  flex-shrink: 0;
}

.preview-text h5 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.preview-text p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0.25rem 0;
}

.chart-container {
  position: relative;
  width: 100%;
  margin: 1rem 0;
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.empty-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
  color: #6b7280;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  background: #f9fafb;
}

.empty-icon {
  width: 3rem;
  height: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-chart p {
  margin: 0;
  font-size: 0.875rem;
}

/* Responsive chart */
@media (max-width: 768px) {
  .chart-container {
    padding: 0.5rem;
  }
  
  .preview-info {
    flex-direction: column;
    text-align: center;
  }
  
  .preview-icon {
    margin-bottom: 0.5rem;
  }
}
</style>