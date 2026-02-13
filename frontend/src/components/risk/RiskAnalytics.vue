<template>
  <div class="risk-analytics">
    <div class="analytics-header">
      <h3>Risk Analytics & Insights</h3>
      <div class="header-actions">
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
          @click="exportAnalytics"
        >
          <DownloadIcon class="h-4 w-4 mr-1" />
          Export
        </Button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Analyzing risk data...</p>
    </div>

    <div v-else class="analytics-content">
      <!-- Key Metrics Grid -->
      <div class="metrics-grid">
        <div class="metric-card total">
          <div class="metric-header">
            <BarChart3Icon class="h-6 w-6" />
            <span>Total Risks</span>
          </div>
          <div class="metric-value">{{ statistics.total }}</div>
          <div class="metric-trend positive">+5% from last month</div>
        </div>

        <div class="metric-card critical">
          <div class="metric-header">
            <AlertTriangleIcon class="h-6 w-6" />
            <span>Critical Risks</span>
          </div>
          <div class="metric-value">{{ statistics.byLevel.Critical || 0 }}</div>
          <div class="metric-trend negative">+2 from last month</div>
        </div>

        <div class="metric-card high">
          <div class="metric-header">
            <AlertCircleIcon class="h-6 w-6" />
            <span>High Risks</span>
          </div>
          <div class="metric-value">{{ statistics.byLevel.High || 0 }}</div>
          <div class="metric-trend neutral">No change</div>
        </div>

        <div class="metric-card score">
          <div class="metric-header">
            <TrendingUpIcon class="h-6 w-6" />
            <span>Avg Risk Score</span>
          </div>
          <div class="metric-value">{{ statistics.avgRiskScore }}</div>
          <div class="metric-trend positive">-0.5 from last month</div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <div class="chart-row">
          <!-- Risk Level Distribution -->
          <div class="chart-container">
            <div class="chart-header">
              <h4>Risk Level Distribution</h4>
              <Button variant="ghost" size="sm">
                <MoreVerticalIcon class="h-4 w-4" />
              </Button>
            </div>
            <div class="chart-content">
              <div class="donut-chart">
                <div class="chart-legend">
                  <div
                    v-for="(count, level) in statistics.byLevel"
                    :key="level"
                    class="legend-item"
                  >
                    <div
                      class="legend-color"
                      :style="{ backgroundColor: getRiskColor(level) }"
                    ></div>
                    <span class="legend-label">{{ level }}</span>
                    <span class="legend-value">{{ count }}</span>
                  </div>
                </div>
                <div class="mock-donut">
                  <PieChartIcon class="h-24 w-24 text-gray-300" />
                  <p class="chart-placeholder-text">Interactive donut chart</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Category Breakdown -->
          <div class="chart-container">
            <div class="chart-header">
              <h4>Risk by Category</h4>
              <Button variant="ghost" size="sm">
                <MoreVerticalIcon class="h-4 w-4" />
              </Button>
            </div>
            <div class="chart-content">
              <div class="category-bars">
                <div
                  v-for="(count, category) in statistics.byCategory"
                  :key="category"
                  class="category-bar"
                >
                  <div class="bar-header">
                    <component :is="getCategoryIcon(category)" class="h-4 w-4" />
                    <span class="category-name">{{ formatCategoryName(category) }}</span>
                    <span class="category-count">{{ count }}</span>
                  </div>
                  <div class="bar-container">
                    <div
                      class="bar-fill"
                      :style="{
                        width: `${(count / statistics.total) * 100}%`,
                        backgroundColor: getCategoryColor(category)
                      }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Risk Trends -->
        <div class="chart-container full-width">
          <div class="chart-header">
            <h4>Risk Trends Over Time</h4>
            <div class="chart-controls">
              <Button
                v-for="period in timePeriods"
                :key="period.value"
                :variant="selectedPeriod === period.value ? 'solid' : 'outline'"
                size="sm"
                @click="selectedPeriod = period.value"
              >
                {{ period.label }}
              </Button>
            </div>
          </div>
          <div class="chart-content">
            <div class="trend-chart">
              <TrendingUpIcon class="h-32 w-32 text-gray-300" />
              <p class="chart-placeholder-text">Interactive trend line chart would be rendered here</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Risk Insights -->
      <div class="insights-section">
        <h4>Risk Insights & Recommendations</h4>
        <div class="insights-grid">
          <div class="insight-card alert">
            <AlertTriangleIcon class="h-5 w-5" />
            <div class="insight-content">
              <h5>High-Risk Areas</h5>
              <p>Financial and operational risks represent 60% of your critical risk exposure.</p>
              <Button variant="outline" size="sm">View Details</Button>
            </div>
          </div>

          <div class="insight-card success">
            <CheckCircleIcon class="h-5 w-5" />
            <div class="insight-content">
              <h5>Improving Trends</h5>
              <p>Compliance risks have decreased by 25% this quarter thanks to new controls.</p>
              <Button variant="outline" size="sm">View Report</Button>
            </div>
          </div>

          <div class="insight-card info">
            <InfoIcon class="h-5 w-5" />
            <div class="insight-content">
              <h5>Action Required</h5>
              <p>15 mitigation actions are overdue and require immediate attention.</p>
              <Button variant="outline" size="sm">Review Actions</Button>
            </div>
          </div>

          <div class="insight-card warning">
            <ClockIcon class="h-5 w-5" />
            <div class="insight-content">
              <h5>Review Schedule</h5>
              <p>8 risks are due for quarterly review within the next 30 days.</p>
              <Button variant="outline" size="sm">Schedule Reviews</Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Risk Heat Map Summary -->
      <div class="heatmap-summary">
        <h4>Risk Matrix Summary</h4>
        <div class="mini-heatmap">
          <div class="heatmap-grid">
            <div
              v-for="i in 25"
              :key="i"
              class="mini-cell"
              :class="getMiniCellClass(i)"
            ></div>
          </div>
          <div class="heatmap-labels">
            <div class="axis-label">Impact →</div>
            <div class="axis-label vertical">← Likelihood</div>
          </div>
        </div>
        <div class="heatmap-stats">
          <div class="stat-item">
            <span class="stat-label">Highest Concentration:</span>
            <span class="stat-value">Medium Impact, Likely Probability</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Risk Coverage:</span>
            <span class="stat-value">18 of 25 matrix cells populated</span>
          </div>
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
	BarChart3Icon,
	CheckCircleIcon,
	ClockIcon,
	DollarSignIcon,
	DownloadIcon,
	InfoIcon,
	MonitorIcon,
	MoreVerticalIcon,
	PieChartIcon,
	RefreshCwIcon,
	SettingsIcon,
	ShieldIcon,
	TargetIcon,
	TrendingUpIcon,
} from "lucide-vue-next"
import { computed, ref } from "vue"

const props = defineProps({
	statistics: {
		type: Object,
		default: () => ({
			total: 0,
			byLevel: {},
			byCategory: {},
			avgRiskScore: 0,
		}),
	},
	analyticsData: {
		type: Object,
		default: () => ({}),
	},
	categories: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["refresh", "export"])

// Local state
const selectedPeriod = ref("3m")

// Time period options
const timePeriods = [
	{ label: "1M", value: "1m" },
	{ label: "3M", value: "3m" },
	{ label: "6M", value: "6m" },
	{ label: "1Y", value: "1y" },
]

// Category configuration
const categoryConfig = {
	operational: { icon: SettingsIcon, color: "#3b82f6" },
	financial: { icon: DollarSignIcon, color: "#10b981" },
	compliance: { icon: ShieldIcon, color: "#f59e0b" },
	strategic: { icon: TargetIcon, color: "#525252" },
	reputational: { icon: AlertTriangleIcon, color: "#ef4444" },
	technology: { icon: MonitorIcon, color: "#06b6d4" },
}

// Methods
const getRiskColor = (level) => {
	const colors = {
		Critical: "#ef4444",
		High: "#f97316",
		Medium: "#eab308",
		Low: "#22c55e",
	}
	return colors[level] || "#6b7280"
}

const getCategoryIcon = (category) => {
	return categoryConfig[category]?.icon || AlertTriangleIcon
}

const getCategoryColor = (category) => {
	return categoryConfig[category]?.color || "#6b7280"
}

const formatCategoryName = (category) => {
	return category.charAt(0).toUpperCase() + category.slice(1)
}

const getMiniCellClass = (index) => {
	// Mock data for demonstration
	const riskCounts = [
		0, 2, 1, 0, 3, 1, 4, 2, 1, 0, 0, 3, 5, 3, 1, 2, 1, 4, 2, 0, 1, 0, 2, 1, 0,
	]
	const count = riskCounts[index - 1] || 0

	if (count === 0) return "empty"
	if (count <= 2) return "low"
	if (count <= 4) return "medium"
	return "high"
}

const exportAnalytics = () => {
	emit("export", {
		type: "analytics",
		format: "pdf",
		period: selectedPeriod.value,
	})
}
</script>

<style scoped>
.risk-analytics {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.analytics-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
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

.analytics-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.metric-card {
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.metric-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  color: var(--text-muted);
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.metric-trend {
  font-size: 0.875rem;
  font-weight: 500;
}

.metric-trend.positive {
  color: #16a34a;
}

.metric-trend.negative {
  color: #dc2626;
}

.metric-trend.neutral {
  color: var(--text-muted);
}

.charts-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.chart-container {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
}

.chart-container.full-width {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.chart-header h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
}

.chart-content {
  padding: 1.5rem;
}

.donut-chart {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 1rem;
  height: 1rem;
  border-radius: 0.25rem;
}

.legend-label {
  font-weight: 500;
  color: var(--text-color);
}

.legend-value {
  font-weight: 600;
  color: var(--primary-color);
}

.mock-donut {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.chart-placeholder-text {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin: 0;
}

.category-bars {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.category-bar {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.bar-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-name {
  font-weight: 500;
  color: var(--text-color);
  flex: 1;
}

.category-count {
  font-weight: 600;
  color: var(--primary-color);
}

.bar-container {
  height: 0.5rem;
  background: var(--background-color);
  border-radius: 0.25rem;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 0.25rem;
  transition: width 0.3s ease;
}

.trend-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
}

.insights-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.insights-section h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.insight-card {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  border-left: 4px solid;
}

.insight-card.alert {
  border-left-color: #ef4444;
}

.insight-card.success {
  border-left-color: #22c55e;
}

.insight-card.info {
  border-left-color: #3b82f6;
}

.insight-card.warning {
  border-left-color: #f59e0b;
}

.insight-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.insight-content h5 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.insight-content p {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin: 0;
}

.heatmap-summary {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.heatmap-summary h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.mini-heatmap {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 2px;
  width: 150px;
  height: 150px;
}

.mini-cell {
  border-radius: 2px;
}

.mini-cell.empty {
  background: #f3f4f6;
}

.mini-cell.low {
  background: #22c55e;
}

.mini-cell.medium {
  background: #eab308;
}

.mini-cell.high {
  background: #ef4444;
}

.heatmap-labels {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.axis-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
}

.axis-label.vertical {
  writing-mode: vertical-lr;
  text-orientation: mixed;
  transform: rotate(180deg);
}

.heatmap-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.stat-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
}

@media (max-width: 768px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
  
  .donut-chart {
    flex-direction: column;
  }
  
  .mini-heatmap {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .insights-grid {
    grid-template-columns: 1fr;
  }
}
</style>