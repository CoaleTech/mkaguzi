<template>
  <BaseChart
    title="Findings by Risk Level"
    subtitle="Risk distribution of audit findings"
    type="bar"
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
const riskCounts = computed(() => {
	const counts = {
		Critical: 0,
		High: 0,
		Medium: 0,
		Low: 0,
	}

	for (const finding of props.findings) {
		const risk = finding.risk_level || "Medium"
		if (counts[risk] !== undefined) {
			counts[risk]++
		}
	}

	return counts
})

const chartData = computed(() => {
	const risks = Object.keys(riskCounts.value)
	const counts = Object.values(riskCounts.value)

	return {
		labels: risks,
		datasets: [
			{
				label: "Number of Findings",
				data: counts,
				backgroundColor: [
					"#DC2626", // Critical - Red-600
					"#EA580C", // High - Orange-600
					"#D97706", // Medium - Amber-600
					"#16A34A", // Low - Green-600
				],
				borderColor: [
					"#B91C1C", // Critical border
					"#C2410C", // High border
					"#B45309", // Medium border
					"#15803D", // Low border
				],
				borderWidth: 1,
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