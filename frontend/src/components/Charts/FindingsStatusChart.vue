<template>
  <BaseChart
    title="Audit Findings by Status"
    subtitle="Distribution of findings across different statuses"
    type="doughnut"
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
const statusCounts = computed(() => {
	const counts = {
		Open: 0,
		"In Progress": 0,
		Resolved: 0,
		Closed: 0,
	}

	for (const finding of props.findings) {
		const status = finding.status || "Open"
		if (counts[status] !== undefined) {
			counts[status]++
		}
	}

	return counts
})

const chartData = computed(() => {
	const statuses = Object.keys(statusCounts.value)
	const counts = Object.values(statusCounts.value)

	return {
		labels: statuses,
		datasets: [
			{
				data: counts,
				backgroundColor: [
					"#EF4444", // Open - Red
					"#F59E0B", // In Progress - Yellow
					"#10B981", // Resolved - Green
					"#6B7280", // Closed - Gray
				],
				borderWidth: 2,
				borderColor: "#FFFFFF",
			},
		],
	}
})

const chartOptions = computed(() => ({
	plugins: {
		legend: {
			position: "bottom",
			labels: {
				padding: 20,
				usePointStyle: true,
			},
		},
		tooltip: {
			callbacks: {
				label: (context) => {
					const total = context.dataset.data.reduce((a, b) => a + b, 0)
					const percentage = ((context.parsed / total) * 100).toFixed(1)
					return `${context.label}: ${context.parsed} (${percentage}%)`
				},
			},
		},
	},
}))
</script>