<template>
  <div class="flex items-center space-x-4 mb-6">
    <div class="flex-shrink-0">
      <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
        <component :is="iconComponent" class="h-6 w-6 text-purple-600" />
      </div>
    </div>
    <div class="flex-1">
      <div class="flex items-center space-x-3">
        <h3 class="text-xl font-bold text-gray-900">{{ title }}</h3>
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
          Step {{ step }}
        </span>
      </div>
      <p class="text-gray-600 mt-1">{{ description }}</p>
    </div>
  </div>
</template>

<script setup>
import {
	CheckCircleIcon,
	ClipboardListIcon,
	FileTextIcon,
	UsersIcon,
} from "lucide-vue-next"
import { computed } from "vue"

// Props
const props = defineProps({
	title: {
		type: String,
		required: true,
	},
	description: {
		type: String,
		required: true,
	},
	icon: {
		type: String,
		default: "file-text",
	},
	step: {
		type: [String, Number],
		required: true,
	},
})

// Icon mapping
const iconComponent = computed(() => {
	const icons = {
		"file-text": FileTextIcon,
		"clipboard-list": ClipboardListIcon,
		users: UsersIcon,
		"check-circle": CheckCircleIcon,
	}
	return icons[props.icon] || FileTextIcon
})
</script>