<template>
  <div class="risk-assessment-matrix">
    <!-- Header Controls -->
    <div class="matrix-header">
      <div class="header-title">
        <h2>Risk Assessment Matrix</h2>
        <p>Interactive risk visualization and management</p>
      </div>
      <div class="header-actions">
        <div class="view-controls">
          <Button
            :variant="matrixView === 'heatmap' ? 'solid' : 'outline'"
            size="sm"
            @click="setMatrixView('heatmap')"
          >
            <Grid3X3Icon class="h-4 w-4 mr-1" />
            Heat Map
          </Button>
          <Button
            :variant="matrixView === 'list' ? 'solid' : 'outline'"
            size="sm"
            @click="setMatrixView('list')"
          >
            <ListIcon class="h-4 w-4 mr-1" />
            List View
          </Button>
          <Button
            :variant="matrixView === 'analytics' ? 'solid' : 'outline'"
            size="sm"
            @click="setMatrixView('analytics')"
          >
            <BarChart3Icon class="h-4 w-4 mr-1" />
            Analytics
          </Button>
        </div>
        <div class="action-buttons">
          <Button
            variant="outline"
            size="sm"
            @click="showCreateRiskModal = true"
          >
            <PlusIcon class="h-4 w-4 mr-1" />
            Add Risk
          </Button>
          <Dropdown :options="exportOptions">
            <template #default="{ toggle }">
              <Button
                variant="outline"
                size="sm"
                @click="toggle()"
              >
                <DownloadIcon class="h-4 w-4 mr-1" />
                Export
              </Button>
            </template>
          </Dropdown>
          <Button
            variant="solid"
            size="sm"
            @click="refreshData"
            :loading="loading.risks"
          >
            <RefreshCwIcon class="h-4 w-4 mr-1" />
            Refresh
          </Button>
        </div>
      </div>
    </div>

    <!-- Risk Filters -->
    <RiskFilters
      v-model:filters="filters"
      :categories="riskCategories"
      :loading="loading.risks"
      @apply-filters="applyFilters"
      @clear-filters="clearAllFilters"
    />

    <!-- Matrix Views -->
    <div class="matrix-content">
      <!-- Heat Map View -->
      <div v-if="matrixView === 'heatmap'" class="heatmap-view">
        <RiskHeatMap
          :matrix-data="riskMatrixData"
          :likelihood-levels="matrixConfig.likelihood.levels"
          :impact-levels="matrixConfig.impact.levels"
          :selected-risks="selectedRisks"
          @cell-click="onMatrixCellClick"
          @risk-click="onRiskClick"
          @risk-select="toggleRiskSelection"
        />
      </div>

      <!-- List View -->
      <div v-if="matrixView === 'list'" class="list-view">
        <RiskList
          :risks="filteredRisks"
          :categories="riskCategories"
          :selected-risks="selectedRisks"
          :loading="loading.risks"
          @risk-click="onRiskClick"
          @risk-select="toggleRiskSelection"
          @risk-edit="onRiskEdit"
          @risk-delete="onRiskDelete"
        />
      </div>

      <!-- Analytics View -->
      <div v-if="matrixView === 'analytics'" class="analytics-view">
        <RiskAnalytics
          :statistics="riskStatistics"
          :analytics-data="riskAnalytics"
          :categories="riskCategories"
          :loading="loading.analytics"
          @refresh="loadRiskAnalytics"
        />
      </div>
    </div>

    <!-- Risk Summary Cards -->
    <div class="risk-summary">
      <div class="summary-cards">
        <div class="summary-card critical">
          <div class="card-icon">
            <AlertTriangleIcon class="h-6 w-6" />
          </div>
          <div class="card-content">
            <h4>{{ riskStatistics.byLevel.Critical || 0 }}</h4>
            <p>Critical Risks</p>
          </div>
        </div>
        <div class="summary-card high">
          <div class="card-icon">
            <AlertCircleIcon class="h-6 w-6" />
          </div>
          <div class="card-content">
            <h4>{{ riskStatistics.byLevel.High || 0 }}</h4>
            <p>High Risks</p>
          </div>
        </div>
        <div class="summary-card medium">
          <div class="card-icon">
            <AlertTriangleIcon class="h-6 w-6" />
          </div>
          <div class="card-content">
            <h4>{{ riskStatistics.byLevel.Medium || 0 }}</h4>
            <p>Medium Risks</p>
          </div>
        </div>
        <div class="summary-card low">
          <div class="card-icon">
            <CheckCircleIcon class="h-6 w-6" />
          </div>
          <div class="card-content">
            <h4>{{ riskStatistics.byLevel.Low || 0 }}</h4>
            <p>Low Risks</p>
          </div>
        </div>
        <div class="summary-card total">
          <div class="card-icon">
            <BarChart3Icon class="h-6 w-6" />
          </div>
          <div class="card-content">
            <h4>{{ riskStatistics.total }}</h4>
            <p>Total Risks</p>
          </div>
        </div>
        <div class="summary-card overdue">
          <div class="card-icon">
            <ClockIcon class="h-6 w-6" />
          </div>
          <div class="card-content">
            <h4>{{ overdueMitigations.length }}</h4>
            <p>Overdue Actions</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Risk Modal -->
    <Dialog
      v-model="showCreateRiskModal"
      :options="{ title: 'Create New Risk', size: 'lg' }"
    >
      <CreateRiskForm
        :categories="riskCategories"
        :likelihood-levels="matrixConfig.likelihood.levels"
        :impact-levels="matrixConfig.impact.levels"
        @submit="onCreateRisk"
        @cancel="showCreateRiskModal = false"
      />
    </Dialog>

    <!-- Risk Detail Modal -->
    <Dialog
      v-model="showRiskDetailModal"
      :options="{ title: 'Risk Details', size: 'xl' }"
    >
      <RiskDetail
        v-if="currentRisk"
        :risk="currentRisk"
        :categories="riskCategories"
        :mitigation-actions="riskMitigations"
        @update="onRiskUpdate"
        @close="showRiskDetailModal = false"
        @create-mitigation="onCreateMitigation"
      />
    </Dialog>

    <!-- Bulk Actions Bar -->
    <div v-if="selectedRisks.length > 0" class="bulk-actions">
      <div class="selected-count">
        {{ selectedRisks.length }} risk(s) selected
      </div>
      <div class="bulk-buttons">
        <Button
          variant="outline"
          size="sm"
          @click="bulkUpdateStatus"
        >
          Update Status
        </Button>
        <Button
          variant="outline"
          size="sm"
          @click="bulkAssignOwner"
        >
          Assign Owner
        </Button>
        <Button
          variant="outline"
          size="sm"
          @click="bulkExport"
        >
          Export Selected
        </Button>
        <Button
          variant="ghost"
          size="sm"
          @click="clearRiskSelection"
        >
          Clear Selection
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRiskAssessmentStore } from "@/stores/useRiskAssessmentStore"
import { Button, Dialog, Dropdown } from "frappe-ui"
import {
	AlertCircleIcon,
	AlertTriangleIcon,
	BarChart3Icon,
	CheckCircleIcon,
	ClockIcon,
	DownloadIcon,
	Grid3X3Icon,
	ListIcon,
	PlusIcon,
	RefreshCwIcon,
} from "lucide-vue-next"
import { storeToRefs } from "pinia"
import { computed, onMounted, ref } from "vue"

import CreateRiskForm from "./CreateRiskForm.vue"
import RiskAnalytics from "./RiskAnalytics.vue"
import RiskDetail from "./RiskDetail.vue"
// Components
import RiskFilters from "./RiskFilters.vue"
import RiskHeatMap from "./RiskHeatMap.vue"
import RiskList from "./RiskList.vue"

// Store
const riskStore = useRiskAssessmentStore()
const {
	risks,
	currentRisk,
	riskAnalytics,
	mitigationActions,
	loading,
	filters,
	selectedRisks,
	matrixView,
	matrixConfig,
	riskCategories,
	riskMatrixData,
	filteredRisks,
	riskStatistics,
	overdueMitigations,
} = storeToRefs(riskStore)

const {
	loadRisks,
	loadRiskAnalytics,
	createRisk,
	updateRisk,
	deleteRisk,
	setCurrentRisk,
	clearCurrentRisk,
	updateFilters,
	clearFilters,
	toggleRiskSelection,
	clearRiskSelection,
	setMatrixView,
	bulkUpdateRisks,
	generateRiskReport,
} = riskStore

// Modal State
const showCreateRiskModal = ref(false)
const showRiskDetailModal = ref(false)

// Computed
const riskMitigations = computed(() => {
	if (!currentRisk.value) return []
	return mitigationActions.value.filter(
		(action) => action.risk === currentRisk.value.name,
	)
})

const exportOptions = [
	{
		label: "Export Matrix (PDF)",
		onClick: () => generateRiskReport("pdf", { type: "matrix" }),
	},
	{
		label: "Export Risk Register (Excel)",
		onClick: () => generateRiskReport("excel", { type: "register" }),
	},
	{
		label: "Export Analytics Report",
		onClick: () => generateRiskReport("pdf", { type: "analytics" }),
	},
]

// Methods
const refreshData = async () => {
	await Promise.all([loadRisks(), loadRiskAnalytics()])
}

const applyFilters = (newFilters) => {
	updateFilters(newFilters)
}

const clearAllFilters = () => {
	clearFilters()
}

const onMatrixCellClick = (cellData) => {
	console.log("Matrix cell clicked:", cellData)
	// Could open a modal showing risks in that cell
}

const onRiskClick = (risk) => {
	setCurrentRisk(risk)
	showRiskDetailModal.value = true
}

const onRiskEdit = (risk) => {
	setCurrentRisk(risk)
	showRiskDetailModal.value = true
}

const onRiskDelete = async (risk) => {
	if (confirm(`Are you sure you want to delete the risk "${risk.title}"?`)) {
		await deleteRisk(risk.name)
	}
}

const onCreateRisk = async (riskData) => {
	try {
		await createRisk(riskData)
		showCreateRiskModal.value = false
	} catch (error) {
		console.error("Error creating risk:", error)
	}
}

const onRiskUpdate = async (riskName, updates) => {
	try {
		await updateRisk(riskName, updates)
	} catch (error) {
		console.error("Error updating risk:", error)
	}
}

const onCreateMitigation = (mitigationData) => {
	// Handle mitigation creation
	console.log("Create mitigation:", mitigationData)
}

const bulkUpdateStatus = () => {
	// Handle bulk status update
	console.log("Bulk update status for:", selectedRisks.value)
}

const bulkAssignOwner = () => {
	// Handle bulk owner assignment
	console.log("Bulk assign owner for:", selectedRisks.value)
}

const bulkExport = () => {
	// Handle bulk export
	console.log("Bulk export:", selectedRisks.value)
}

// Lifecycle
onMounted(() => {
	refreshData()
})
</script>

<style scoped>
.risk-assessment-matrix {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  min-height: 100vh;
}

.matrix-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

.header-title h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.header-title p {
  color: var(--text-muted);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.view-controls {
  display: flex;
  gap: 0.5rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.matrix-content {
  flex: 1;
  min-height: 400px;
}

.risk-summary {
  border-top: 1px solid var(--border-color);
  padding-top: 1.5rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.summary-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem;
}

.summary-card.critical .card-icon {
  background: #fee2e2;
  color: #ef4444;
}

.summary-card.high .card-icon {
  background: #fed7aa;
  color: #f97316;
}

.summary-card.medium .card-icon {
  background: #fef3c7;
  color: #eab308;
}

.summary-card.low .card-icon {
  background: #dcfce7;
  color: #22c55e;
}

.summary-card.total .card-icon {
  background: #e0e7ff;
  color: #6366f1;
}

.summary-card.overdue .card-icon {
  background: #f3e8ff;
  color: #8b5cf6;
}

.card-content h4 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.card-content p {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0;
}

.bulk-actions {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.selected-count {
  font-weight: 600;
  color: var(--text-color);
}

.bulk-buttons {
  display: flex;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .matrix-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .header-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    width: 100%;
  }

  .view-controls,
  .action-buttons {
    width: 100%;
    justify-content: stretch;
  }

  .summary-cards {
    grid-template-columns: 1fr;
  }

  .bulk-actions {
    position: static;
    transform: none;
    margin-top: 2rem;
  }
}
</style>