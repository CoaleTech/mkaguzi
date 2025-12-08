<template>
  <BaseChart
    title="Findings Over Time"
    subtitle="Trend of audit findings creation"
    type="line"
    :data="chartData"
    :options="chartOptions"
    :show-refresh="true"
    :show-export="true"
    :loading="loading"
    height="300"
    @refresh="$emit('refresh')"
    @export="$emit('export')"
  />
</template>

<script setup>
import { computed } from "vue"
import BaseChart from "./BaseChart.vue"

// Props
const props = defineProps({
	findings: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

// Emits
const emit = defineEmits(["refresh", "export"])

// Computed
const timelineData = computed(() => {
	const monthlyCounts = {}

	for (const finding of props.findings) {
		if (finding.creation) {
			const date = new Date(finding.creation)
			const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`

			if (!monthlyCounts[monthKey]) {
				monthlyCounts[monthKey] = 0
			}
			monthlyCounts[monthKey]++
		}
	}

	// Sort by date
	const sortedMonths = Object.keys(monthlyCounts).sort()

	return {
		labels: sortedMonths.map((month) => {
			const [year, monthNum] = month.split("-")
			const date = new Date(year, monthNum - 1)
			return date.toLocaleDateString("en-US", {
				year: "numeric",
				month: "short",
			})
		}),
		data: sortedMonths.map((month) => monthlyCounts[month]),
	}
})

const chartData = computed(() => {
	return {
		labels: timelineData.value.labels,
		datasets: [
			{
				label: "Findings Created",
				data: timelineData.value.data,
				borderColor: "#3B82F6",
				backgroundColor: "rgba(59, 130, 246, 0.1)",
				borderWidth: 2,
				fill: true,
				tension: 0.4,
			},
		],
	}
})

const chartOptions = computed(() => ({
	scales: {
		y: {
			beginAtZero: true,
			ticks: {
				stepSize: 1,
			},
		},
	},
	plugins: {
		legend: {
			display: false,
		},
	},
}))
</script>