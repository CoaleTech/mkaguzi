<template>
  <div class="risk-heatmap">
    <!-- Legend -->
    <div class="heatmap-legend">
      <h4>Risk Level Legend</h4>
      <div class="legend-items">
        <div class="legend-item critical">
          <div class="legend-color"></div>
          <span>Critical (16-25)</span>
        </div>
        <div class="legend-item high">
          <div class="legend-color"></div>
          <span>High (13-20)</span>
        </div>
        <div class="legend-item medium">
          <div class="legend-color"></div>
          <span>Medium (6-12)</span>
        </div>
        <div class="legend-item low">
          <div class="legend-color"></div>
          <span>Low (1-5)</span>
        </div>
      </div>
    </div>

    <!-- Heat Map Grid -->
    <div class="heatmap-container">
      <!-- Y-Axis Label (Impact) -->
      <div class="y-axis-label">
        <span>Impact</span>
      </div>

      <!-- Impact Labels -->
      <div class="impact-labels">
        <div 
          v-for="impact in impactLevelsReversed" 
          :key="impact.id"
          class="impact-label"
          :title="impact.description"
        >
          <span class="label-text">{{ impact.label }}</span>
          <span class="label-number">{{ impact.id }}</span>
        </div>
      </div>

      <!-- Matrix Grid -->
      <div class="matrix-grid">
        <div 
          v-for="(row, rowIndex) in matrixData" 
          :key="rowIndex"
          class="matrix-row"
        >
          <div
            v-for="(cell, colIndex) in row"
            :key="`${rowIndex}-${colIndex}`"
            class="matrix-cell"
            :class="[
              `risk-${cell.level.toLowerCase()}`,
              { 'has-risks': cell.count > 0, 'selected': hasSelectedRisks(cell.risks) }
            ]"
            :style="{ backgroundColor: cell.color + '20', borderColor: cell.color }"
            @click="onCellClick(cell)"
          >
            <div class="cell-content">
              <div class="risk-count">{{ cell.count }}</div>
              <div v-if="cell.count > 0" class="risk-indicators">
                <div
                  v-for="risk in cell.risks.slice(0, 3)"
                  :key="risk.name"
                  class="risk-indicator"
                  :class="{ 'selected': selectedRisks.includes(risk.name) }"
                  :title="risk.title"
                  @click.stop="onRiskClick(risk)"
                >
                  <component 
                    :is="getCategoryIcon(risk.category)" 
                    class="h-3 w-3"
                  />
                </div>
                <div 
                  v-if="cell.count > 3"
                  class="risk-indicator more"
                  :title="`+${cell.count - 3} more risks`"
                >
                  +{{ cell.count - 3 }}
                </div>
              </div>
            </div>

            <!-- Tooltip -->
            <div class="cell-tooltip">
              <div class="tooltip-header">
                <strong>{{ cell.level }} Risk</strong>
                <span>(L:{{ cell.likelihood }}, I:{{ cell.impact }})</span>
              </div>
              <div v-if="cell.count > 0" class="tooltip-risks">
                <div class="tooltip-risk-count">{{ cell.count }} risk(s)</div>
                <ul>
                  <li 
                    v-for="risk in cell.risks.slice(0, 5)" 
                    :key="risk.name"
                  >
                    {{ risk.title }}
                  </li>
                  <li v-if="cell.count > 5">
                    ...and {{ cell.count - 5 }} more
                  </li>
                </ul>
              </div>
              <div v-else class="no-risks">No risks in this category</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Likelihood Labels -->
      <div class="likelihood-labels">
        <div 
          v-for="likelihood in likelihoodLevels" 
          :key="likelihood.id"
          class="likelihood-label"
          :title="likelihood.description"
        >
          <span class="label-number">{{ likelihood.id }}</span>
          <span class="label-text">{{ likelihood.label }}</span>
        </div>
      </div>

      <!-- X-Axis Label (Likelihood) -->
      <div class="x-axis-label">
        <span>Likelihood</span>
      </div>
    </div>

    <!-- Risk Detail Panel -->
    <div v-if="selectedCell" class="risk-detail-panel">
      <div class="panel-header">
        <h4>{{ selectedCell.level }} Risk Cell</h4>
        <div class="cell-coordinates">
          Likelihood: {{ selectedCell.likelihood }}, Impact: {{ selectedCell.impact }}
        </div>
        <Button
          variant="ghost"
          size="sm"
          @click="selectedCell = null"
        >
          <XIcon class="h-4 w-4" />
        </Button>
      </div>

      <div class="panel-content">
        <div v-if="selectedCell.count > 0" class="risks-list">
          <div
            v-for="risk in selectedCell.risks"
            :key="risk.name"
            class="risk-item"
            :class="{ 'selected': selectedRisks.includes(risk.name) }"
            @click="toggleRiskSelection(risk.name)"
          >
            <div class="risk-info">
              <div class="risk-title">{{ risk.title }}</div>
              <div class="risk-meta">
                <span class="category">{{ getCategoryLabel(risk.category) }}</span>
                <span class="owner">{{ risk.risk_owner }}</span>
                <span class="status">{{ risk.status }}</span>
              </div>
            </div>
            <div class="risk-actions">
              <Button
                variant="outline"
                size="sm"
                @click.stop="onRiskClick(risk)"
              >
                View
              </Button>
              <input
                type="checkbox"
                :checked="selectedRisks.includes(risk.name)"
                @change="$emit('risk-select', risk.name)"
              />
            </div>
          </div>
        </div>
        <div v-else class="no-risks-message">
          <AlertCircleIcon class="h-8 w-8 text-gray-300" />
          <p>No risks in this category</p>
          <Button
            variant="outline"
            size="sm"
            @click="createRiskInCell(selectedCell)"
          >
            <PlusIcon class="h-4 w-4 mr-1" />
            Add Risk Here
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import {
	AlertCircleIcon,
	AlertTriangleIcon,
	DollarSignIcon,
	MonitorIcon,
	PlusIcon,
	SettingsIcon,
	ShieldIcon,
	TargetIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, ref } from "vue"

const props = defineProps({
	matrixData: {
		type: Array,
		default: () => [],
	},
	likelihoodLevels: {
		type: Array,
		default: () => [],
	},
	impactLevels: {
		type: Array,
		default: () => [],
	},
	selectedRisks: {
		type: Array,
		default: () => [],
	},
})

const emit = defineEmits([
	"cell-click",
	"risk-click",
	"risk-select",
	"create-risk",
])

// Local state
const selectedCell = ref(null)

// Computed
const impactLevelsReversed = computed(() => {
	return [...props.impactLevels].reverse()
})

// Category icons mapping
const categoryIcons = {
	operational: SettingsIcon,
	financial: DollarSignIcon,
	compliance: ShieldIcon,
	strategic: TargetIcon,
	reputational: AlertTriangleIcon,
	technology: MonitorIcon,
}

// Methods
const getCategoryIcon = (category) => {
	return categoryIcons[category] || AlertTriangleIcon
}

const getCategoryLabel = (category) => {
	const labels = {
		operational: "Operational",
		financial: "Financial",
		compliance: "Compliance",
		strategic: "Strategic",
		reputational: "Reputational",
		technology: "Technology",
	}
	return labels[category] || category
}

const hasSelectedRisks = (risks) => {
	return risks.some((risk) => props.selectedRisks.includes(risk.name))
}

const onCellClick = (cell) => {
	selectedCell.value = cell
	emit("cell-click", cell)
}

const onRiskClick = (risk) => {
	emit("risk-click", risk)
}

const toggleRiskSelection = (riskName) => {
	emit("risk-select", riskName)
}

const createRiskInCell = (cell) => {
	emit("create-risk", {
		likelihood: cell.likelihood,
		impact: cell.impact,
	})
}
</script>

<style scoped>
.risk-heatmap {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 1rem;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
}

.heatmap-legend h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.legend-items {
  display: flex;
  gap: 1.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.legend-color {
  width: 1rem;
  height: 1rem;
  border-radius: 0.25rem;
  border: 1px solid rgba(0, 0, 0, 0.2);
}

.legend-item.critical .legend-color {
  background: #ef4444;
}

.legend-item.high .legend-color {
  background: #f97316;
}

.legend-item.medium .legend-color {
  background: #eab308;
}

.legend-item.low .legend-color {
  background: #22c55e;
}

.heatmap-container {
  display: grid;
  grid-template-columns: auto auto 1fr auto;
  grid-template-rows: auto 1fr auto auto;
  gap: 0.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
}

.y-axis-label {
  grid-column: 1;
  grid-row: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  writing-mode: vertical-lr;
  text-orientation: mixed;
  font-weight: 600;
  color: var(--text-color);
  transform: rotate(180deg);
}

.impact-labels {
  grid-column: 2;
  grid-row: 2;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.impact-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 80px;
  padding: 0.5rem;
  font-size: 0.75rem;
  text-align: center;
}

.label-text {
  font-weight: 600;
  color: var(--text-color);
}

.label-number {
  font-weight: 700;
  color: var(--primary-color);
  font-size: 1rem;
}

.matrix-grid {
  grid-column: 3;
  grid-row: 2;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.matrix-row {
  display: flex;
  gap: 0;
}

.matrix-cell {
  position: relative;
  width: 100px;
  height: 80px;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.matrix-cell:hover {
  transform: scale(1.02);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.matrix-cell.has-risks {
  border-width: 2px;
}

.matrix-cell.selected {
  box-shadow: 0 0 0 2px var(--primary-color);
  z-index: 5;
}

.cell-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.risk-count {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
}

.risk-indicators {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2px;
  max-width: 100%;
}

.risk-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.risk-indicator:hover {
  transform: scale(1.2);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.risk-indicator.selected {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.risk-indicator.more {
  font-size: 0.625rem;
  font-weight: 700;
  background: var(--gray-100);
}

.cell-tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: var(--gray-900);
  color: white;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
  z-index: 1000;
  min-width: 200px;
}

.matrix-cell:hover .cell-tooltip {
  opacity: 1;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.tooltip-risks ul {
  margin: 0;
  padding-left: 1rem;
}

.tooltip-risks li {
  margin: 0.25rem 0;
}

.likelihood-labels {
  grid-column: 3;
  grid-row: 3;
  display: flex;
  gap: 0;
}

.likelihood-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100px;
  padding: 0.5rem;
  font-size: 0.75rem;
  text-align: center;
}

.x-axis-label {
  grid-column: 3;
  grid-row: 4;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--text-color);
  margin-top: 0.5rem;
}

.risk-detail-panel {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--background-color);
  border-bottom: 1px solid var(--border-color);
}

.panel-header h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.cell-coordinates {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.panel-content {
  padding: 1rem;
}

.risks-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.risk-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.risk-item:hover {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.risk-item.selected {
  background: var(--primary-light);
  border-color: var(--primary-color);
}

.risk-info {
  flex: 1;
}

.risk-title {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.risk-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.risk-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.no-risks-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .heatmap-legend {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .legend-items {
    flex-wrap: wrap;
  }

  .matrix-cell {
    width: 60px;
    height: 50px;
  }

  .likelihood-label,
  .impact-label {
    font-size: 0.625rem;
    padding: 0.25rem;
  }

  .likelihood-label {
    width: 60px;
  }

  .impact-label {
    height: 50px;
  }
}
</style>