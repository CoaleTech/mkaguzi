<template>
  <div class="space-y-4">
    <!-- Stats Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
      <div
        v-for="stat in statsCards"
        :key="stat.label"
        class="bg-white rounded-xl border p-4 hover:shadow-md transition-shadow cursor-pointer"
        :class="stat.active ? 'ring-2 ring-blue-500' : ''"
        @click="$emit('filter', stat.filterKey, stat.filterValue)"
      >
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-lg" :class="stat.bgColor">
            <component :is="stat.icon" class="h-5 w-5" :class="stat.iconColor" />
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ stat.value }}</div>
            <div class="text-xs text-gray-500">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Status Distribution -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Current Status</h3>
        <div class="space-y-3">
          <div
            v-for="status in currentStatusDistribution"
            :key="status.name"
            class="flex items-center gap-3 cursor-pointer hover:bg-gray-50 p-1 rounded"
            @click="$emit('filter', 'current_status', status.name)"
          >
            <div class="w-3 h-3 rounded-full" :class="status.dotColor"></div>
            <div class="flex-1 text-sm text-gray-600">{{ status.name }}</div>
            <Badge :theme="status.theme">{{ status.count }}</Badge>
          </div>
        </div>
      </div>

      <!-- Due Date Overview -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Due Date Status</h3>
        <div class="grid grid-cols-3 gap-3">
          <div
            class="p-3 bg-red-50 border border-red-200 rounded-lg text-center cursor-pointer hover:shadow-sm"
            @click="$emit('filter', 'overdue', true)"
          >
            <div class="text-2xl font-bold text-red-700">{{ overdueCount }}</div>
            <div class="text-xs text-red-600">Overdue</div>
          </div>
          <div
            class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-center cursor-pointer hover:shadow-sm"
            @click="$emit('filter', 'due_soon', true)"
          >
            <div class="text-2xl font-bold text-yellow-700">{{ dueSoonCount }}</div>
            <div class="text-xs text-yellow-600">Due Soon</div>
          </div>
          <div
            class="p-3 bg-green-50 border border-green-200 rounded-lg text-center cursor-pointer hover:shadow-sm"
            @click="$emit('filter', 'on_time', true)"
          >
            <div class="text-2xl font-bold text-green-700">{{ onTimeCount }}</div>
            <div class="text-xs text-green-600">On Time</div>
          </div>
        </div>
      </div>

      <!-- Escalation Status -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Escalation Status</h3>
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Escalation Required</span>
            <Badge theme="red">{{ escalatedCount }}</Badge>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Not Escalated</span>
            <Badge theme="gray">{{ notEscalatedCount }}</Badge>
          </div>
          <div class="mt-4 pt-4 border-t">
            <div class="text-xs text-gray-500 mb-2">Escalation by Level</div>
            <div class="space-y-1">
              <div
                v-for="level in escalationLevelDistribution"
                :key="level.name"
                class="flex items-center justify-between text-sm"
              >
                <span class="text-gray-600">{{ level.name }}</span>
                <span class="font-medium text-gray-700">{{ level.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Average Ratings & Follow-up Types -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Average Ratings -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">Average Ratings</h3>
        <div class="grid grid-cols-2 gap-6">
          <div class="text-center">
            <div class="flex items-center justify-center gap-1 mb-2">
              <Star
                v-for="star in 5"
                :key="star"
                class="h-5 w-5"
                :class="star <= avgProgressRating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'"
              />
            </div>
            <div class="text-lg font-bold text-gray-900">{{ avgProgressRating.toFixed(1) }}</div>
            <div class="text-xs text-gray-500">Progress Rating</div>
          </div>
          <div class="text-center">
            <div class="flex items-center justify-center gap-1 mb-2">
              <Star
                v-for="star in 5"
                :key="star"
                class="h-5 w-5"
                :class="star <= avgEffectivenessRating ? 'text-green-400 fill-green-400' : 'text-gray-300'"
              />
            </div>
            <div class="text-lg font-bold text-gray-900">{{ avgEffectivenessRating.toFixed(1) }}</div>
            <div class="text-xs text-gray-500">Effectiveness Rating</div>
          </div>
        </div>
      </div>

      <!-- Follow-up Type Distribution -->
      <div class="bg-white rounded-xl border p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-4">By Follow-up Type</h3>
        <div class="space-y-2">
          <div
            v-for="type in followUpTypeDistribution"
            :key="type.name"
            class="flex items-center gap-3 cursor-pointer hover:bg-gray-50 p-1 rounded"
            @click="$emit('filter', 'follow_up_type', type.name)"
          >
            <div class="flex-1">
              <div class="flex items-center justify-between mb-1">
                <span class="text-sm text-gray-600 truncate max-w-[180px]">{{ type.name }}</span>
                <span class="text-sm font-medium text-gray-700">{{ type.count }}</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-2">
                <div
                  class="h-2 rounded-full"
                  :class="type.barColor"
                  :style="{ width: `${type.percentage}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Badge } from 'frappe-ui'
import {
  ListChecks,
  CheckCircle,
  Clock,
  Pause,
  XCircle,
  Star,
} from 'lucide-vue-next'

const props = defineProps({
  trackers: { type: Array, default: () => [] },
  activeFilter: { type: String, default: '' },
})

defineEmits(['filter'])

// Stats cards
const statsCards = computed(() => {
  const trackers = props.trackers
  const total = trackers.length
  const active = trackers.filter((t) => t.status === 'Active').length
  const completed = trackers.filter((t) => t.status === 'Completed').length
  const onHold = trackers.filter((t) => t.status === 'On Hold').length
  const cancelled = trackers.filter((t) => t.status === 'Cancelled').length

  return [
    { label: 'Total Trackers', value: total, icon: ListChecks, bgColor: 'bg-blue-100', iconColor: 'text-blue-600', filterKey: null, filterValue: null },
    { label: 'Active', value: active, icon: Clock, bgColor: 'bg-green-100', iconColor: 'text-green-600', filterKey: 'status', filterValue: 'Active', active: props.activeFilter === 'Active' },
    { label: 'Completed', value: completed, icon: CheckCircle, bgColor: 'bg-gray-100', iconColor: 'text-gray-600', filterKey: 'status', filterValue: 'Completed', active: props.activeFilter === 'Completed' },
    { label: 'On Hold', value: onHold, icon: Pause, bgColor: 'bg-yellow-100', iconColor: 'text-yellow-600', filterKey: 'status', filterValue: 'On Hold', active: props.activeFilter === 'On Hold' },
    { label: 'Cancelled', value: cancelled, icon: XCircle, bgColor: 'bg-gray-100', iconColor: 'text-gray-600', filterKey: 'status', filterValue: 'Cancelled', active: props.activeFilter === 'Cancelled' },
  ]
})

// Current status distribution
const currentStatusDistribution = computed(() => {
  const trackers = props.trackers
  const statuses = [
    { name: 'On Track', dotColor: 'bg-green-500', theme: 'green' },
    { name: 'Behind Schedule', dotColor: 'bg-yellow-500', theme: 'orange' },
    { name: 'At Risk', dotColor: 'bg-orange-500', theme: 'orange' },
    { name: 'Off Track', dotColor: 'bg-red-500', theme: 'red' },
    { name: 'Completed Successfully', dotColor: 'bg-blue-500', theme: 'blue' },
  ]

  return statuses.map((s) => ({
    ...s,
    count: trackers.filter((t) => t.current_status === s.name).length,
  })).filter((s) => s.count > 0)
})

// Due date calculations
const overdueCount = computed(() => {
  const today = new Date()
  return props.trackers.filter((t) => {
    if (t.status !== 'Active' || !t.next_due_date) return false
    return new Date(t.next_due_date) < today
  }).length
})

const dueSoonCount = computed(() => {
  const today = new Date()
  const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
  return props.trackers.filter((t) => {
    if (t.status !== 'Active' || !t.next_due_date) return false
    const dueDate = new Date(t.next_due_date)
    return dueDate >= today && dueDate <= weekFromNow
  }).length
})

const onTimeCount = computed(() => {
  const today = new Date()
  const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
  return props.trackers.filter((t) => {
    if (t.status !== 'Active' || !t.next_due_date) return false
    return new Date(t.next_due_date) > weekFromNow
  }).length
})

// Escalation stats
const escalatedCount = computed(() => {
  return props.trackers.filter((t) => t.escalation_required).length
})

const notEscalatedCount = computed(() => {
  return props.trackers.filter((t) => !t.escalation_required && t.status === 'Active').length
})

const escalationLevelDistribution = computed(() => {
  const levels = ['Manager', 'Senior Management', 'Audit Committee', 'Board']
  return levels.map((level) => ({
    name: level,
    count: props.trackers.filter((t) => t.escalation_level === level).length,
  })).filter((l) => l.count > 0)
})

// Average ratings
const avgProgressRating = computed(() => {
  const rated = props.trackers.filter((t) => t.progress_rating)
  if (!rated.length) return 0
  return rated.reduce((sum, t) => sum + t.progress_rating, 0) / rated.length
})

const avgEffectivenessRating = computed(() => {
  const rated = props.trackers.filter((t) => t.effectiveness_rating)
  if (!rated.length) return 0
  return rated.reduce((sum, t) => sum + t.effectiveness_rating, 0) / rated.length
})

// Follow-up type distribution
const followUpTypeDistribution = computed(() => {
  const trackers = props.trackers
  const total = trackers.length || 1
  const types = [
    'Corrective Action Monitoring',
    'Preventive Measure Verification',
    'Process Improvement Tracking',
    'Risk Mitigation Assessment',
    'Compliance Verification',
  ]
  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-gray-500',
    'bg-orange-500',
    'bg-indigo-500',
  ]

  return types.map((name, idx) => ({
    name,
    count: trackers.filter((t) => t.follow_up_type === name).length,
    percentage: Math.round((trackers.filter((t) => t.follow_up_type === name).length / total) * 100),
    barColor: colors[idx],
  })).filter((t) => t.count > 0)
})
</script>
