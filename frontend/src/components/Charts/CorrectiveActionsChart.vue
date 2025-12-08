<template>
  <BaseChart
    title="Corrective Actions Progress"
    subtitle="Status of corrective action plans"
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
	correctiveActions: {
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
		"Not Started": 0,
		"In Progress": 0,
		Completed: 0,
		Overdue: 0,
	}

	for (const action of props.correctiveActions) {
		const status = action.status || "Not Started"
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
				label: "Number of Actions",
				data: counts,
				backgroundColor: [
					"#6B7280", // Not Started - Gray
					"#3B82F6", // In Progress - Blue
					"#10B981", // Completed - Green
					"#EF4444", // Overdue - Red
				],
				borderColor: [
					"#4B5563", // Not Started border
					"#2563EB", // In Progress border
					"#059669", // Completed border
					"#DC2626", // Overdue border
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