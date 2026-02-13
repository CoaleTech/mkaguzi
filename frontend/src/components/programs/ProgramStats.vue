<template>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 mb-6">
    <!-- Total Programs Card -->
    <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border border-gray-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-gray-700 uppercase tracking-wide">Total Programs</p>
          <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.total || 0 }}</p>
          <p class="text-xs text-gray-600 mt-1">{{ stats.templates || 0 }} templates</p>
        </div>
        <div class="p-3 bg-gray-900 rounded-xl shadow-sm">
          <FileTextIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Active Programs Card -->
    <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl border border-green-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-green-700 uppercase tracking-wide">Active</p>
          <p class="text-3xl font-bold text-green-900 mt-1">{{ stats.active || 0 }}</p>
          <p class="text-xs text-green-600 mt-1">Currently in use</p>
        </div>
        <div class="p-3 bg-green-500 rounded-xl shadow-sm">
          <PlayCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Completion Rate Card -->
    <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div class="w-full">
          <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide">Avg Completion</p>
          <p class="text-3xl font-bold text-blue-900 mt-1">{{ stats.avgCompletion || 0 }}%</p>
          <div class="w-full bg-blue-200 rounded-full h-2 mt-2">
            <div
              class="bg-blue-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${Math.min(stats.avgCompletion || 0, 100)}%` }"
            ></div>
          </div>
        </div>
        <div class="p-3 bg-blue-500 rounded-xl shadow-sm ml-3">
          <PercentIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Total Procedures Card -->
    <div class="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl border border-amber-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-amber-700 uppercase tracking-wide">Procedures</p>
          <p class="text-3xl font-bold text-amber-900 mt-1">{{ stats.totalProcedures || 0 }}</p>
          <p class="text-xs text-amber-600 mt-1">{{ stats.completedProcedures || 0 }} completed</p>
        </div>
        <div class="p-3 bg-amber-500 rounded-xl shadow-sm">
          <ClipboardCheckIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>

    <!-- Overdue Card -->
    <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-xl border border-red-200 p-5 hover:shadow-lg transition-all duration-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-red-700 uppercase tracking-wide">Overdue</p>
          <p class="text-3xl font-bold text-red-900 mt-1">{{ stats.overdue || 0 }}</p>
          <p class="text-xs text-red-600 mt-1">Need attention</p>
        </div>
        <div class="p-3 bg-red-500 rounded-xl shadow-sm">
          <AlertCircleIcon class="h-7 w-7 text-white" />
        </div>
      </div>
    </div>
  </div>

  <!-- Audit Type Distribution -->
  <div v-if="showDetails" class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
    <!-- Programs by Type -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h3 class="text-sm font-semibold text-gray-900 mb-4">Programs by Type</h3>
      <div class="space-y-3">
        <div v-for="type in typeDistribution" :key="type.label" class="flex items-center">
          <div class="w-24 text-sm text-gray-600">{{ type.label }}</div>
          <div class="flex-1 mx-3">
            <div class="w-full bg-gray-100 rounded-full h-3">
              <div
                class="h-3 rounded-full transition-all duration-300"
                :class="type.color"
                :style="{ width: `${type.percentage}%` }"
              ></div>
            </div>
          </div>
          <div class="w-12 text-sm font-medium text-gray-900 text-right">{{ type.count }}</div>
        </div>
      </div>
    </div>

    <!-- Procedure Status -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h3 class="text-sm font-semibold text-gray-900 mb-4">Procedure Status</h3>
      <div class="grid grid-cols-2 gap-3">
        <div v-for="status in procedureStatus" :key="status.label" class="text-center p-3 bg-gray-50 rounded-lg">
          <p class="text-lg font-bold" :class="status.color">{{ status.count }}</p>
          <p class="text-xs text-gray-500">{{ status.label }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  AlertCircleIcon,
  ClipboardCheckIcon,
  FileTextIcon,
  PercentIcon,
  PlayCircleIcon,
} from 'lucide-vue-next'

// Props
const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      total: 0,
      templates: 0,
      active: 0,
      avgCompletion: 0,
      totalProcedures: 0,
      completedProcedures: 0,
      overdue: 0,
      byType: {},
      proceduresByStatus: {},
    }),
  },
  showDetails: {
    type: Boolean,
    default: true,
  },
})

// Computed
const typeDistribution = computed(() => {
  const types = props.stats.byType || {}
  const total = Object.values(types).reduce((sum, count) => sum + count, 0) || 1
  
  const colors = {
    'Financial': 'bg-blue-500',
    'Operational': 'bg-green-500',
    'Compliance': 'bg-gray-400',
    'IT': 'bg-amber-500',
    'Inventory': 'bg-cyan-500',
    'Cash': 'bg-emerald-500',
    'Sales': 'bg-pink-500',
    'Procurement': 'bg-indigo-500',
  }

  return Object.entries(types).map(([label, count]) => ({
    label,
    count,
    percentage: (count / total) * 100,
    color: colors[label] || 'bg-gray-400',
  }))
})

const procedureStatus = computed(() => {
  const statuses = props.stats.proceduresByStatus || {}
  return [
    { label: 'Not Started', count: statuses['Not Started'] || 0, color: 'text-gray-600' },
    { label: 'In Progress', count: statuses['In Progress'] || 0, color: 'text-blue-600' },
    { label: 'Completed', count: statuses['Completed'] || 0, color: 'text-green-600' },
    { label: 'N/A', count: statuses['Not Applicable'] || 0, color: 'text-amber-600' },
  ]
})
</script>
