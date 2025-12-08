<template>
  <div class="real-time-dashboard">
    <div class="flex h-screen bg-gray-50">
      <!-- Sidebar -->
      <div class="w-80 bg-white border-r border-gray-200 flex flex-col">
        <!-- Header -->
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-center gap-3">
            <div class="h-12 w-12 rounded-xl bg-gradient-to-br from-green-500 to-blue-600 flex items-center justify-center shadow-lg">
              <ActivityIcon class="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 class="text-lg font-bold text-gray-900">Real-Time Dashboard</h2>
              <p class="text-sm text-gray-600">Live predictive analytics</p>
            </div>
          </div>
        </div>

        <!-- Dashboard Controls -->
        <div class="flex-1 overflow-y-auto p-4">
          <div class="space-y-6">
            <!-- Refresh Controls -->
            <div>
              <div class="text-sm font-medium text-gray-700 mb-3">Live Updates</div>
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Auto-refresh</span>
                  <button
                    @click="toggleAutoRefresh"
                    class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
                    :class="autoRefresh ? 'bg-green-600' : 'bg-gray-200'"
                  >
                    <span
                      class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                      :class="autoRefresh ? 'translate-x-6' : 'translate-x-1'"
                    />
                  </button>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-sm text-gray-600">Interval:</span>
                  <select
                    v-model="refreshInterval"
                    class="text-sm border border-gray-300 rounded px-2 py-1"
                    @change="updateRefreshInterval"
                  >
                    <option value="5000">5s</option>
                    <option value="10000">10s</option>
                    <option value="30000">30s</option>
                    <option value="60000">1m</option>
                  </select>
                </div>
                <div class="text-xs text-gray-500">
                  Last updated: {{ formatTime(lastUpdate) }}
                </div>
              </div>
            </div>

            <!-- Dashboard Widgets -->
            <div>
              <div class="text-sm font-medium text-gray-700 mb-3">Active Widgets</div>
              <div class="space-y-2">
                <label
                  v-for="widget in availableWidgets"
                  :key="widget.id"
                  class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    v-model="activeWidgets"
                    :value="widget.id"
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    @change="updateActiveWidgets"
                  />
                  <component :is="widget.icon" class="h-4 w-4 text-gray-600" />
                  <span class="text-sm text-gray-900">{{ widget.title }}</span>
                </label>
              </div>
            </div>

            <!-- Alert Settings -->
            <div>
              <div class="text-sm font-medium text-gray-700 mb-3">Alert Thresholds</div>
              <div class="space-y-3">
                <div>
                  <label class="block text-xs text-gray-600 mb-1">Risk Score Alert</label>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    step="0.1"
                    v-model="alertThresholds.riskScore"
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    @input="updateAlertThresholds"
                  />
                  <div class="text-xs text-gray-500 mt-1">{{ alertThresholds.riskScore }}/5</div>
                </div>
                <div>
                  <label class="block text-xs text-gray-600 mb-1">Anomaly Confidence</label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    v-model="alertThresholds.anomalyConfidence"
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    @input="updateAlertThresholds"
                  />
                  <div class="text-xs text-gray-500 mt-1">{{ (alertThresholds.anomalyConfidence * 100).toFixed(0) }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Dashboard -->
      <div class="flex-1 overflow-hidden">
        <!-- Header -->
        <div class="bg-white border-b border-gray-200 p-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Live Audit Analytics</h1>
              <p class="text-gray-600">Real-time predictive insights and monitoring</p>
            </div>
            <div class="flex items-center gap-4">
              <div class="flex items-center gap-2">
                <div class="h-3 w-3 rounded-full bg-green-500 animate-pulse"></div>
                <span class="text-sm text-gray-600">Live</span>
              </div>
              <Button @click="refreshDashboard" variant="outline" size="sm">
                <RefreshCwIcon class="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>

        <!-- Dashboard Grid -->
        <div class="p-6 overflow-y-auto h-full">
          <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">

            <!-- Risk Score Trend -->
            <div v-if="activeWidgets.includes('risk-trend')" class="bg-white rounded-lg border border-gray-200 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Risk Score Trend</h3>
                <TrendingUpIcon class="h-5 w-5 text-red-500" />
              </div>
              <div class="h-64">
                <BaseChart
                  type="line"
                  :data="riskTrendData"
                  :options="chartOptions"
                  height="250"
                />
              </div>
              <div class="mt-4 flex items-center justify-between text-sm">
                <span class="text-gray-600">Current: {{ currentRiskScore.toFixed(2) }}/5</span>
                <span :class="trendClass">{{ trendDirection }}</span>
              </div>
            </div>

            <!-- Predictive Analytics -->
            <div v-if="activeWidgets.includes('predictive-analytics')" class="bg-white rounded-lg border border-gray-200 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Predictive Analytics</h3>
                <BarChart3Icon class="h-5 w-5 text-blue-500" />
              </div>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Next Month Risk</span>
                  <span class="text-lg font-bold text-gray-900">{{ predictiveRisk.toFixed(2) }}/5</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full transition-all duration-500"
                    :style="{ width: (predictiveRisk / 5) * 100 + '%' }"
                  ></div>
                </div>
                <div class="text-xs text-gray-500">
                  Confidence: {{ (predictiveConfidence * 100).toFixed(1) }}%
                </div>
              </div>
            </div>

            <!-- Anomaly Detection -->
            <div v-if="activeWidgets.includes('anomaly-detection')" class="bg-white rounded-lg border border-gray-200 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Anomaly Detection</h3>
                <AlertTriangleIcon class="h-5 w-5 text-orange-500" />
              </div>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Active Anomalies</span>
                  <span class="text-2xl font-bold text-orange-600">{{ anomalyCount }}</span>
                </div>
                <div class="space-y-2">
                  <div
                    v-for="anomaly in recentAnomalies.slice(0, 3)"
                    :key="anomaly.id"
                    class="flex items-center justify-between p-2 bg-orange-50 rounded"
                  >
                    <span class="text-xs text-gray-700">{{ anomaly.description }}</span>
                    <span class="text-xs font-medium text-orange-700">{{ (anomaly.confidence * 100).toFixed(0) }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Control Effectiveness -->
            <div v-if="activeWidgets.includes('control-effectiveness')" class="bg-white rounded-lg border border-gray-200 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Control Effectiveness</h3>
                <ShieldIcon class="h-5 w-5 text-green-500" />
              </div>
              <div class="h-64">
                <BaseChart
                  type="doughnut"
                  :data="controlEffectivenessData"
                  :options="doughnutOptions"
                  height="250"
                />
              </div>
              <div class="mt-4 text-center">
                <div class="text-2xl font-bold text-green-600">{{ controlEffectiveness.toFixed(1) }}%</div>
                <div class="text-xs text-gray-500">Overall Effectiveness</div>
              </div>
            </div>

            <!-- Compliance Status -->
            <div v-if="activeWidgets.includes('compliance-status')" class="bg-white rounded-lg border border-gray-200 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Compliance Status</h3>
                <CheckCircleIcon class="h-5 w-5 text-green-500" />
              </div>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">SOX Compliance</span>
                  <div class="flex items-center gap-2">
                    <div class="h-2 w-2 rounded-full bg-green-500"></div>
                    <span class="text-sm font-medium text-green-700">{{ complianceStatus.sox }}%</span>
                  </div>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">GDPR Compliance</span>
                  <div class="flex items-center gap-2">
                    <div class="h-2 w-2 rounded-full bg-yellow-500"></div>
                    <span class="text-sm font-medium text-yellow-700">{{ complianceStatus.gdpr }}%</span>
                  </div>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Internal Policies</span>
                  <div class="flex items-center gap-2">
                    <div class="h-2 w-2 rounded-full bg-green-500"></div>
                    <span class="text-sm font-medium text-green-700">{{ complianceStatus.internal }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- ML Model Performance -->
            <div v-if="activeWidgets.includes('ml-performance')" class="bg-white rounded-lg border border-gray-200 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">ML Model Performance</h3>
                <BrainIcon class="h-5 w-5 text-purple-500" />
              </div>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Best Algorithm</span>
                  <span class="text-sm font-medium text-purple-700">{{ bestAlgorithm }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Accuracy</span>
                  <span class="text-sm font-medium text-gray-900">{{ (mlAccuracy * 100).toFixed(1) }}%</span>
                </div>
                <div class="space-y-2">
                  <div class="text-xs text-gray-600">Top Features:</div>
                  <div
                    v-for="feature in topFeatures.slice(0, 3)"
                    :key="feature.name"
                    class="flex items-center justify-between"
                  >
                    <span class="text-xs text-gray-700">{{ feature.name }}</span>
                    <span class="text-xs font-medium text-gray-900">{{ (feature.importance * 100).toFixed(1) }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Audit Efficiency -->
            <div v-if="activeWidgets.includes('audit-efficiency')" class="bg-white rounded-lg border border-gray-200 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Audit Efficiency</h3>
                <ClockIcon class="h-5 w-5 text-indigo-500" />
              </div>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Avg. Audit Time</span>
                  <span class="text-lg font-bold text-gray-900">{{ auditEfficiency.avgTime }}h</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">Issues per Hour</span>
                  <span class="text-lg font-bold text-green-600">{{ auditEfficiency.issuesPerHour }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">AI Assistance</span>
                  <span class="text-lg font-bold text-blue-600">{{ auditEfficiency.aiAssistance }}%</span>
                </div>
              </div>
            </div>

            <!-- Real-time Alerts -->
            <div v-if="activeWidgets.includes('real-time-alerts')" class="bg-white rounded-lg border border-gray-200 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Real-Time Alerts</h3>
                <BellIcon class="h-5 w-5 text-red-500" />
              </div>
              <div class="space-y-3 max-h-64 overflow-y-auto">
                <div
                  v-for="alert in recentAlerts.slice(0, 5)"
                  :key="alert.id"
                  class="p-3 rounded-lg border-l-4"
                  :class="alert.severity === 'high' ? 'border-l-red-500 bg-red-50' :
                          alert.severity === 'medium' ? 'border-l-yellow-500 bg-yellow-50' :
                          'border-l-blue-500 bg-blue-50'"
                >
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-gray-900">{{ alert.title }}</span>
                    <span class="text-xs text-gray-500">{{ formatTime(alert.timestamp) }}</span>
                  </div>
                  <p class="text-xs text-gray-600 mt-1">{{ alert.message }}</p>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button } from 'frappe-ui'
import {
  ActivityIcon,
  TrendingUpIcon,
  BarChart3Icon,
  AlertTriangleIcon,
  ShieldIcon,
  CheckCircleIcon,
  BrainIcon,
  ClockIcon,
  BellIcon,
  RefreshCwIcon,
} from 'lucide-vue-next'
import { ref, onMounted, onUnmounted, computed } from 'vue'
import BaseChart from '@/components/Charts/BaseChart.vue'
import { call } from 'frappe-ui'

// Reactive state
const autoRefresh = ref(true)
const refreshInterval = ref('10000') // 10 seconds
const lastUpdate = ref(new Date())
const activeWidgets = ref([
  'risk-trend',
  'predictive-analytics',
  'anomaly-detection',
  'control-effectiveness',
  'compliance-status'
])

const alertThresholds = ref({
  riskScore: 3.5,
  anomalyConfidence: 0.7
})

// Dashboard data
const riskTrendData = ref({
  labels: [],
  datasets: [{
    label: 'Risk Score',
    data: [],
    borderColor: 'rgb(239, 68, 68)',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    tension: 0.4
  }]
})

const controlEffectivenessData = ref({
  labels: ['Effective', 'Needs Improvement', 'Critical'],
  datasets: [{
    data: [75, 20, 5],
    backgroundColor: [
      'rgb(34, 197, 94)',
      'rgb(251, 191, 36)',
      'rgb(239, 68, 68)'
    ]
  }]
})

const currentRiskScore = ref(3.2)
const predictiveRisk = ref(3.6)
const predictiveConfidence = ref(0.87)
const anomalyCount = ref(3)
const controlEffectiveness = ref(78.5)
const bestAlgorithm = ref('Random Forest')
const mlAccuracy = ref(0.91)

// Available widgets
const availableWidgets = ref([
  { id: 'risk-trend', title: 'Risk Score Trend', icon: TrendingUpIcon },
  { id: 'predictive-analytics', title: 'Predictive Analytics', icon: BarChart3Icon },
  { id: 'anomaly-detection', title: 'Anomaly Detection', icon: AlertTriangleIcon },
  { id: 'control-effectiveness', title: 'Control Effectiveness', icon: ShieldIcon },
  { id: 'compliance-status', title: 'Compliance Status', icon: CheckCircleIcon },
  { id: 'ml-performance', title: 'ML Performance', icon: BrainIcon },
  { id: 'audit-efficiency', title: 'Audit Efficiency', icon: ClockIcon },
  { id: 'real-time-alerts', title: 'Real-Time Alerts', icon: BellIcon }
])

// Mock data for demonstration
const recentAnomalies = ref([
  { id: 1, description: 'Unusual transaction volume spike', confidence: 0.89 },
  { id: 2, description: 'Control effectiveness drop', confidence: 0.76 },
  { id: 3, description: 'Compliance score variation', confidence: 0.82 }
])

const complianceStatus = ref({
  sox: 94,
  gdpr: 87,
  internal: 96
})

const auditEfficiency = ref({
  avgTime: 42,
  issuesPerHour: 2.3,
  aiAssistance: 68
})

const topFeatures = ref([
  { name: 'Control Effectiveness', importance: 0.35 },
  { name: 'Findings Count', importance: 0.28 },
  { name: 'Compliance Score', importance: 0.22 }
])

const recentAlerts = ref([
  {
    id: 1,
    title: 'High Risk Alert',
    message: 'Risk score exceeded threshold of 3.5',
    severity: 'high',
    timestamp: new Date(Date.now() - 300000)
  },
  {
    id: 2,
    title: 'Anomaly Detected',
    message: 'Unusual pattern in transaction data',
    severity: 'medium',
    timestamp: new Date(Date.now() - 600000)
  }
])

// Chart options
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 5
    }
  }
})

const doughnutOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
})

// Computed properties
const trendDirection = computed(() => {
  const data = riskTrendData.value.datasets[0].data
  if (data.length < 2) return 'Stable'
  const recent = data.slice(-5)
  const avgRecent = recent.reduce((a, b) => a + b, 0) / recent.length
  const avgEarlier = data.slice(-10, -5).reduce((a, b) => a + b, 0) / 5
  if (avgRecent > avgEarlier + 0.1) return '↗ Increasing'
  if (avgRecent < avgEarlier - 0.1) return '↘ Decreasing'
  return '→ Stable'
})

const trendClass = computed(() => {
  const direction = trendDirection.value
  if (direction.includes('Increasing')) return 'text-red-600 font-medium'
  if (direction.includes('Decreasing')) return 'text-green-600 font-medium'
  return 'text-gray-600'
})

// Methods
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const updateRefreshInterval = () => {
  if (autoRefresh.value) {
    stopAutoRefresh()
    startAutoRefresh()
  }
}

const updateActiveWidgets = () => {
  // Save to localStorage
  localStorage.setItem('dashboard-widgets', JSON.stringify(activeWidgets.value))
}

const updateAlertThresholds = () => {
  // Save to localStorage
  localStorage.setItem('alert-thresholds', JSON.stringify(alertThresholds.value))
}

let refreshTimer = null

const startAutoRefresh = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  refreshTimer = setInterval(() => {
    refreshDashboard()
  }, parseInt(refreshInterval.value))
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const refreshDashboard = async () => {
  try {
    // Update timestamp
    lastUpdate.value = new Date()

    // Fetch real-time data from APIs
    await Promise.all([
      updateRiskTrend(),
      updatePredictiveAnalytics(),
      updateAnomalyDetection(),
      updateControlEffectiveness(),
      updateComplianceStatus(),
      updateMLPerformance(),
      updateAuditEfficiency(),
      checkAlerts()
    ])

  } catch (error) {
    console.error('Dashboard refresh error:', error)
  }
}

const updateRiskTrend = async () => {
  try {
    // Simulate real-time risk data updates
    const newRiskScore = 3.0 + Math.random() * 1.5
    currentRiskScore.value = newRiskScore

    // Update chart data
    const now = new Date()
    const timeLabel = now.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit'
    })

    riskTrendData.value.labels.push(timeLabel)
    riskTrendData.value.datasets[0].data.push(newRiskScore)

    // Keep only last 20 data points
    if (riskTrendData.value.labels.length > 20) {
      riskTrendData.value.labels.shift()
      riskTrendData.value.datasets[0].data.shift()
    }

    riskTrendData.value = { ...riskTrendData.value } // Trigger reactivity
  } catch (error) {
    console.error('Risk trend update error:', error)
  }
}

const updatePredictiveAnalytics = async () => {
  try {
    // Get predictive analytics from API
    const response = await call("mkaguzi.api.ai_specialist.get_advanced_predictive_analytics", {
      time_period: "1_month",
      analysis_type: "risk_focused",
      ml_algorithms: ["random_forest"]
    })

    if (response.success) {
      predictiveRisk.value = response.comprehensive_insights.average_risk || 3.6
      predictiveConfidence.value = response.comprehensive_insights.confidence || 0.87
    }
  } catch (error) {
    console.error('Predictive analytics update error:', error)
  }
}

const updateAnomalyDetection = async () => {
  try {
    // Generate sample data for anomaly detection
    const sampleData = Array.from({ length: 50 }, (_, i) => ({
      value: Math.random() * 10 + (i > 40 ? Math.random() * 10 : 0)
    }))

    const response = await call("mkaguzi.api.ai_specialist.get_anomaly_detection", {
      data_set: sampleData,
      detection_method: "isolation_forest",
      sensitivity: "medium"
    })

    if (response.success) {
      anomalyCount.value = response.anomalies_detected
      recentAnomalies.value = response.anomalies.slice(0, 3).map((a, i) => ({
        id: i + 1,
        description: `Anomaly at index ${a.index}`,
        confidence: a.confidence
      }))
    }
  } catch (error) {
    console.error('Anomaly detection update error:', error)
  }
}

const updateControlEffectiveness = async () => {
  try {
    // Simulate control effectiveness updates
    const effective = 70 + Math.random() * 20
    const needsImprovement = 20 + Math.random() * 10
    const critical = 10 - Math.random() * 5

    controlEffectivenessData.value.datasets[0].data = [
      Math.round(effective),
      Math.round(needsImprovement),
      Math.round(critical)
    ]

    controlEffectiveness.value = effective
    controlEffectivenessData.value = { ...controlEffectivenessData.value }
  } catch (error) {
    console.error('Control effectiveness update error:', error)
  }
}

const updateComplianceStatus = async () => {
  try {
    // Simulate compliance status updates
    complianceStatus.value = {
      sox: 90 + Math.random() * 8,
      gdpr: 80 + Math.random() * 15,
      internal: 95 + Math.random() * 4
    }
  } catch (error) {
    console.error('Compliance status update error:', error)
  }
}

const updateMLPerformance = async () => {
  try {
    // Get ML performance data
    const response = await call("mkaguzi.api.ai_specialist.get_advanced_predictive_analytics", {
      time_period: "6_months",
      analysis_type: "comprehensive",
      ml_algorithms: ["random_forest", "gradient_boosting"]
    })

    if (response.success) {
      bestAlgorithm.value = response.comprehensive_insights.best_performing_algorithm.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
      mlAccuracy.value = response.comprehensive_insights.average_accuracy

      // Update top features
      const features = response.ml_results.random_forest?.feature_importance || {}
      topFeatures.value = Object.entries(features).map(([name, importance]) => ({
        name: name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        importance
      })).sort((a, b) => b.importance - a.importance)
    }
  } catch (error) {
    console.error('ML performance update error:', error)
  }
}

const updateAuditEfficiency = async () => {
  try {
    // Simulate audit efficiency updates
    auditEfficiency.value = {
      avgTime: 35 + Math.random() * 15,
      issuesPerHour: 2.0 + Math.random() * 0.8,
      aiAssistance: 60 + Math.random() * 20
    }
  } catch (error) {
    console.error('Audit efficiency update error:', error)
  }
}

const checkAlerts = async () => {
  try {
    // Check for new alerts based on thresholds
    const newAlerts = []

    if (currentRiskScore.value >= alertThresholds.value.riskScore) {
      newAlerts.push({
        id: Date.now(),
        title: 'Risk Threshold Exceeded',
        message: `Current risk score ${currentRiskScore.value.toFixed(2)} exceeds threshold of ${alertThresholds.value.riskScore}`,
        severity: 'high',
        timestamp: new Date()
      })
    }

    if (anomalyCount.value > 0) {
      const highConfidenceAnomalies = recentAnomalies.value.filter(a => a.confidence >= alertThresholds.value.anomalyConfidence)
      if (highConfidenceAnomalies.length > 0) {
        newAlerts.push({
          id: Date.now() + 1,
          title: 'High-Confidence Anomalies',
          message: `${highConfidenceAnomalies.length} anomalies detected with confidence ≥ ${(alertThresholds.value.anomalyConfidence * 100).toFixed(0)}%`,
          severity: 'medium',
          timestamp: new Date()
        })
      }
    }

    // Add new alerts to the list
    recentAlerts.value.unshift(...newAlerts)

    // Keep only last 10 alerts
    if (recentAlerts.value.length > 10) {
      recentAlerts.value = recentAlerts.value.slice(0, 10)
    }
  } catch (error) {
    console.error('Alert check error:', error)
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle hooks
onMounted(() => {
  // Load saved preferences
  const savedWidgets = localStorage.getItem('dashboard-widgets')
  if (savedWidgets) {
    activeWidgets.value = JSON.parse(savedWidgets)
  }

  const savedThresholds = localStorage.getItem('alert-thresholds')
  if (savedThresholds) {
    alertThresholds.value = JSON.parse(savedThresholds)
  }

  // Initialize with some data
  updateRiskTrend()

  // Start auto-refresh if enabled
  if (autoRefresh.value) {
    startAutoRefresh()
  }

  // Initial dashboard refresh
  refreshDashboard()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
/* Custom scrollbar for sidebar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>