<template>
  <div class="board-stats">
    <div class="stats-grid">
      <!-- Audit Coverage -->
      <div class="stat-card">
        <div class="stat-header">
          <h3>Audit Coverage</h3>
          <Target class="stat-icon" />
        </div>
        <div class="stat-value">{{ Math.round(boardMetrics.auditCoverage) }}%</div>
        <div class="stat-trend" :class="getTrendClass(boardMetrics.auditCoverageTrend)">
          <TrendingUp v-if="boardMetrics.auditCoverageTrend > 0" />
          <TrendingDown v-else />
          {{ Math.abs(boardMetrics.auditCoverageTrend) }}% from last period
        </div>
      </div>

      <!-- Open Findings -->
      <div class="stat-card">
        <div class="stat-header">
          <h3>Open Findings</h3>
          <AlertTriangle class="stat-icon" />
        </div>
        <div class="stat-value">{{ boardMetrics.openFindings }}</div>
        <div class="stat-trend" :class="getTrendClass(-boardMetrics.findingsTrend)">
          <TrendingDown v-if="boardMetrics.findingsTrend > 0" />
          <TrendingUp v-else />
          {{ Math.abs(boardMetrics.findingsTrend) }} from last period
        </div>
      </div>

      <!-- Compliance Score -->
      <div class="stat-card">
        <div class="stat-header">
          <h3>Compliance Score</h3>
          <ShieldCheck class="stat-icon" />
        </div>
        <div class="stat-value">{{ Math.round(boardMetrics.complianceScore) }}%</div>
        <div class="stat-trend" :class="getTrendClass(boardMetrics.complianceTrend)">
          <TrendingUp v-if="boardMetrics.complianceTrend > 0" />
          <TrendingDown v-else />
          {{ Math.abs(boardMetrics.complianceTrend) }}% from last period
        </div>
      </div>

      <!-- Risk Level -->
      <div class="stat-card">
        <div class="stat-header">
          <h3>Risk Level</h3>
          <AlertCircle class="stat-icon" />
        </div>
        <div class="stat-value risk-level" :class="getRiskLevelClass(boardMetrics.overallRisk)">
          {{ boardMetrics.overallRisk }}
        </div>
        <div class="stat-trend">
          Based on current assessments
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { AlertCircle, AlertTriangle, ShieldCheck, Target, TrendingDown, TrendingUp } from "lucide-vue-next"

defineProps({
  boardMetrics: {
    type: Object,
    required: true,
    default: () => ({
      auditCoverage: 0,
      auditCoverageTrend: 0,
      openFindings: 0,
      findingsTrend: 0,
      complianceScore: 0,
      complianceTrend: 0,
      overallRisk: "Medium"
    })
  }
})

// Utility methods
const getTrendClass = (trend) => {
  return trend > 0 ? "positive" : trend < 0 ? "negative" : "neutral"
}

const getRiskLevelClass = (level) => {
  const classes = {
    Low: "low-risk",
    Medium: "medium-risk",
    High: "high-risk",
    Critical: "critical-risk",
  }
  return classes[level] || "medium-risk"
}
</script>

<style scoped>
.board-stats {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stat-header h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
  margin: 0;
}

.stat-icon {
  color: var(--primary-color);
  font-size: 1.25rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.stat-value.risk-level {
  font-size: 1.5rem;
  text-transform: uppercase;
  font-weight: 600;
}

.stat-value.low-risk {
  color: #10b981;
}

.stat-value.medium-risk {
  color: #f59e0b;
}

.stat-value.high-risk {
  color: #ef4444;
}

.stat-value.critical-risk {
  color: #dc2626;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-trend.positive {
  color: #10b981;
}

.stat-trend.negative {
  color: #ef4444;
}

.stat-trend.neutral {
  color: var(--text-muted);
}

/* Responsive design */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 1rem;
  }

  .stat-value {
    font-size: 1.5rem;
  }
}
</style>