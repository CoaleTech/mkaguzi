<template>
  <div class="search-analytics">
    <div class="analytics-header">
      <h4>Analytics</h4>
      <div class="analytics-actions">
        <Button
          variant="outline"
          size="sm"
          @click="$emit('refresh')"
          :loading="loading"
        >
          <RefreshCwIcon class="h-4 w-4 mr-1" />
          Refresh
        </Button>
        <Button
          variant="outline"
          size="sm"
          @click="$emit('export', 'pdf')"
        >
          <DownloadIcon class="h-4 w-4 mr-1" />
          Export
        </Button>
      </div>
    </div>

    <div v-if="loading" class="analytics-loading">
      <div class="loading-spinner"></div>
      <p>Analyzing data...</p>
    </div>

    <div v-else-if="analyticsData && Object.keys(analyticsData).length" class="analytics-content">
      <!-- Key Metrics -->
      <div class="metrics-grid">
        <div
          v-for="metric in keyMetrics"
          :key="metric.id"
          class="metric-card"
        >
          <div class="metric-icon">
            <component :is="metric.icon" class="h-6 w-6" />
          </div>
          <div class="metric-info">
            <h5>{{ metric.label }}</h5>
            <div class="metric-value">{{ metric.value }}</div>
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts-section">
        <h5>Data Distribution</h5>
        <div class="mock-chart">
          <div class="chart-placeholder">
            <BarChartIcon class="h-12 w-12 text-gray-300" />
            <p>Interactive charts would be rendered here</p>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-analytics">
      <BarChartIcon class="h-16 w-16 text-gray-300" />
      <h5>No Analytics Data</h5>
      <p>Perform a search to see analytics</p>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import { BarChartIcon, DownloadIcon, RefreshCwIcon } from "lucide-vue-next"
import { computed } from "vue"

const props = defineProps({
	analyticsData: {
		type: Object,
		default: () => ({}),
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["refresh", "export"])

const keyMetrics = computed(() => {
	if (!props.analyticsData.metrics) return []

	return [
		{
			id: "total_records",
			label: "Total Records",
			value: props.analyticsData.metrics.total_records || 0,
			icon: BarChartIcon,
		},
	]
})
</script>

<style scoped>
.search-analytics {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.analytics-header h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.analytics-actions {
  display: flex;
  gap: 0.5rem;
}

.analytics-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
}

.metric-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  background: var(--primary-light);
  border-radius: 0.5rem;
  color: var(--primary-color);
}

.metric-info h5 {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-muted);
  margin: 0 0 0.25rem 0;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
}

.charts-section h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.mock-chart {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 2rem;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
  color: var(--text-muted);
}

.no-analytics {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
  color: var(--text-muted);
}

.no-analytics h5 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}
</style>