<template>
  <div class="flex items-center space-x-4">
    <div
      class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
      :class="bgColorClass"
    >
      <component
        :is="iconComponent"
        class="h-5 w-5"
        :class="iconColorClass"
      />
    </div>
    <div>
      <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
      <p class="text-sm text-gray-500">{{ description }}</p>
    </div>
    <div
      v-if="step"
      class="ml-auto px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600"
    >
      Step {{ step }} of 8
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  FileTextIcon,
  TargetIcon,
  SettingsIcon,
  CalendarIcon,
  UsersIcon,
  BookUserIcon,
  DatabaseIcon,
  FolderIcon,
} from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: 'file-text'
  },
  step: {
    type: [String, Number],
    default: null
  },
  color: {
    type: String,
    default: 'green'
  }
})

const iconMap = {
  'file-text': FileTextIcon,
  'target': TargetIcon,
  'settings': SettingsIcon,
  'calendar': CalendarIcon,
  'users': UsersIcon,
  'book-user': BookUserIcon,
  'database': DatabaseIcon,
  'folder': FolderIcon,
}

const iconComponent = computed(() => iconMap[props.icon] || FileTextIcon)

const colorMap = {
  green: { bg: 'bg-green-100', icon: 'text-green-600' },
  blue: { bg: 'bg-blue-100', icon: 'text-blue-600' },
  purple: { bg: 'bg-gray-100', icon: 'text-gray-600' },
  amber: { bg: 'bg-amber-100', icon: 'text-amber-600' },
  red: { bg: 'bg-red-100', icon: 'text-red-600' },
}

const bgColorClass = computed(() => colorMap[props.color]?.bg || colorMap.green.bg)
const iconColorClass = computed(() => colorMap[props.color]?.icon || colorMap.green.icon)
</script>
