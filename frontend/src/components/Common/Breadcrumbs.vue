<template>
  <nav class="flex" aria-label="Breadcrumb">
    <ol class="flex items-center space-x-2">
      <li>
        <router-link
          to="/"
          class="text-gray-500 hover:text-gray-700"
        >
          <HomeIcon class="h-4 w-4" />
        </router-link>
      </li>
      <li v-for="(item, index) in items" :key="index" class="flex items-center">
        <ChevronRightIcon class="h-4 w-4 text-gray-400" />
        <component
          :is="item.to && !item.isActive ? 'router-link' : 'span'"
          :to="item.to"
          :class="[
            'text-sm font-medium',
            item.isActive
              ? 'text-gray-900'
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          {{ item.label }}
        </component>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { ChevronRightIcon, HomeIcon } from "lucide-vue-next"

defineProps({
	items: {
		type: Array,
		default: () => [],
	},
})
</script>