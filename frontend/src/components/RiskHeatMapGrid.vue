<template>
	<div class="risk-heat-map">
		<div class="grid grid-cols-6 gap-1 max-w-md mx-auto">
			<!-- Header row -->
			<div class="col-span-1"></div>
			<div v-for="impact in 5" :key="`impact-${impact}`" class="text-center text-sm font-medium text-gray-700 p-2">
				{{ impact }}
			</div>

			<!-- Grid rows -->
			<div v-for="likelihood in 5" :key="`likelihood-${likelihood}`" class="contents">
				<!-- Likelihood label -->
				<div class="text-center text-sm font-medium text-gray-700 p-2 flex items-center justify-center">
					{{ likelihood }}
				</div>

				<!-- Risk cells -->
				<div
					v-for="impact in 5"
					:key="`cell-${likelihood}-${impact}`"
					:class="getCellClass(likelihood, impact)"
					class="aspect-square rounded border cursor-pointer transition-all duration-200 hover:scale-105 flex items-center justify-center text-xs font-medium"
					@click="onCellClick(likelihood, impact)"
				>
					{{ getCellCount(likelihood, impact) }}
				</div>
			</div>
		</div>

		<!-- Legend -->
		<div class="flex justify-center mt-6 space-x-4">
			<div class="flex items-center space-x-2">
				<div class="w-4 h-4 bg-green-100 border border-green-300 rounded"></div>
				<span class="text-sm text-gray-600">Low (1-6)</span>
			</div>
			<div class="flex items-center space-x-2">
				<div class="w-4 h-4 bg-yellow-100 border border-yellow-300 rounded"></div>
				<span class="text-sm text-gray-600">Medium (7-12)</span>
			</div>
			<div class="flex items-center space-x-2">
				<div class="w-4 h-4 bg-orange-100 border border-orange-300 rounded"></div>
				<span class="text-sm text-gray-600">High (13-18)</span>
			</div>
			<div class="flex items-center space-x-2">
				<div class="w-4 h-4 bg-red-100 border border-red-300 rounded"></div>
				<span class="text-sm text-gray-600">Critical (19-25)</span>
			</div>
		</div>

		<!-- Axis labels -->
		<div class="text-center mt-4">
			<div class="grid grid-cols-2 gap-8 max-w-md mx-auto">
				<div class="text-sm text-gray-600">
					<div class="font-medium">Likelihood</div>
					<div class="text-xs">1 = Rare, 5 = Almost Certain</div>
				</div>
				<div class="text-sm text-gray-600">
					<div class="font-medium">Impact</div>
					<div class="text-xs">1 = Minor, 5 = Catastrophic</div>
				</div>
			</div>
		</div>

		<!-- Risk details modal -->
		<Dialog v-model="showDetailsModal">
			<template #title>Risks in {{ selectedCell.likelihood }}x{{ selectedCell.impact }} Cell</template>
			<div class="space-y-4 max-h-96 overflow-y-auto">
				<div v-if="cellRisks.length === 0" class="text-center text-gray-500 py-8">
					No risks in this cell
				</div>
				<div v-else class="space-y-3">
					<div
						v-for="risk in cellRisks"
						:key="risk.risk_id"
						class="p-3 border rounded-lg"
					>
						<div class="flex items-start justify-between">
							<div class="flex-1">
								<div class="font-medium text-sm">{{ risk.risk_id }}</div>
								<div class="text-sm text-gray-600 mt-1">{{ risk.risk_description }}</div>
								<div class="text-xs text-gray-500 mt-1">
									Category: {{ risk.risk_category }}
								</div>
							</div>
							<Badge :variant="getRiskVariant(risk.inherent_risk_score)" class="ml-2">
								{{ risk.inherent_risk_score }}/25
							</Badge>
						</div>
					</div>
				</div>
			</div>
		</Dialog>
	</div>
</template>

<script setup>
import { Badge, Dialog } from "frappe-ui"
import { computed, ref } from "vue"

// Props
const props = defineProps({
	risks: {
		type: Array,
		default: () => [],
	},
	heatMapData: {
		type: Object,
		default: () => ({}),
	},
})

// Reactive data
const showDetailsModal = ref(false)
const selectedCell = ref({ likelihood: 0, impact: 0 })

// Computed properties
const cellRisks = computed(() => {
	if (!selectedCell.value.likelihood || !selectedCell.value.impact) return []

	return props.risks.filter(
		(risk) =>
			risk.likelihood_score === selectedCell.value.likelihood &&
			risk.impact_score === selectedCell.value.impact,
	)
})

// Methods
const getCellClass = (likelihood, impact) => {
	const riskScore = likelihood * impact
	const count = getCellCount(likelihood, impact)

	let baseClass = "border-gray-200"

	// Risk level colors
	if (riskScore >= 19) {
		baseClass = "bg-red-100 border-red-300 text-red-800"
	} else if (riskScore >= 13) {
		baseClass = "bg-orange-100 border-orange-300 text-orange-800"
	} else if (riskScore >= 7) {
		baseClass = "bg-yellow-100 border-yellow-300 text-yellow-800"
	} else {
		baseClass = "bg-green-100 border-green-300 text-green-800"
	}

	// Add hover effect and count indicator
	if (count > 0) {
		baseClass += " font-bold"
	}

	return baseClass
}

const getCellCount = (likelihood, impact) => {
	const key = `${likelihood}-${impact}`
	return props.heatMapData[key] || 0
}

const onCellClick = (likelihood, impact) => {
	selectedCell.value = { likelihood, impact }
	showDetailsModal.value = true
}

const getRiskVariant = (score) => {
	if (score >= 20) return "destructive"
	if (score >= 15) return "warning"
	if (score >= 10) return "secondary"
	return "success"
}
</script>

<style scoped>
.risk-heat-map {
	@apply p-6 bg-white rounded-lg border;
}
</style>