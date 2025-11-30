<template>
  <div class="flex items-center space-x-4 mb-6 pb-4 border-b border-gray-200">
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
      <p v-if="description" class="text-sm text-gray-500">{{ description }}</p>
    </div>
    <div
      v-if="step"
      class="ml-auto px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600"
    >
      Step {{ step }} of {{ totalSteps }}
    </div>
  </div>
</template>

<script setup>
import {
	AlertTriangleIcon,
	BookUserIcon,
	CalendarIcon,
	ClipboardCheckIcon,
	ClipboardListIcon,
	DatabaseIcon,
	FileCheck2Icon,
	FileTextIcon,
	FolderIcon,
	MessageCircleIcon,
	RefreshCwIcon,
	SearchIcon,
	SettingsIcon,
	ShieldCheckIcon,
	TargetIcon,
	UsersIcon,
} from "lucide-vue-next"
import { computed, markRaw } from "vue"

const props = defineProps({
	title: {
		type: String,
		required: true,
	},
	description: {
		type: String,
		default: "",
	},
	icon: {
		type: [String, Object],
		default: "file-text",
	},
	step: {
		type: [String, Number],
		default: null,
	},
	totalSteps: {
		type: [String, Number],
		default: 8,
	},
	color: {
		type: String,
		default: "blue",
	},
})

const iconMap = {
	"file-text": FileTextIcon,
	target: TargetIcon,
	settings: SettingsIcon,
	calendar: CalendarIcon,
	users: UsersIcon,
	"book-user": BookUserIcon,
	database: DatabaseIcon,
	folder: FolderIcon,
	search: SearchIcon,
	"message-circle": MessageCircleIcon,
	"clipboard-check": ClipboardCheckIcon,
	"refresh-cw": RefreshCwIcon,
	"shield-check": ShieldCheckIcon,
	"file-check": FileCheck2Icon,
	"clipboard-list": ClipboardListIcon,
	"alert-triangle": AlertTriangleIcon,
}

const iconComponent = computed(() => {
	// If icon is passed as component object, use it directly
	if (typeof props.icon === "object") {
		return markRaw(props.icon)
	}
	// Otherwise look up by string name
	return iconMap[props.icon] || FileTextIcon
})

const colorMap = {
	green: { bg: "bg-green-100", icon: "text-green-600" },
	blue: { bg: "bg-blue-100", icon: "text-blue-600" },
	purple: { bg: "bg-purple-100", icon: "text-purple-600" },
	amber: { bg: "bg-amber-100", icon: "text-amber-600" },
	red: { bg: "bg-red-100", icon: "text-red-600" },
	yellow: { bg: "bg-yellow-100", icon: "text-yellow-600" },
	orange: { bg: "bg-orange-100", icon: "text-orange-600" },
	gray: { bg: "bg-gray-100", icon: "text-gray-600" },
}

const bgColorClass = computed(
	() => colorMap[props.color]?.bg || colorMap.blue.bg,
)
const iconColorClass = computed(
	() => colorMap[props.color]?.icon || colorMap.blue.icon,
)
</script>
