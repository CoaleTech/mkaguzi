<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
  >
    <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></span>
    <component :is="icon" v-if="icon && !loading" class="h-4 w-4 mr-2" />
    <slot>{{ label }}</slot>
  </button>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
	variant: {
		type: String,
		default: "primary",
		validator: (value) =>
			["primary", "secondary", "outline", "danger"].includes(value),
	},
	size: {
		type: String,
		default: "default",
		validator: (value) => ["sm", "default", "lg"].includes(value),
	},
	type: {
		type: String,
		default: "button",
	},
	disabled: {
		type: Boolean,
		default: false,
	},
	loading: {
		type: Boolean,
		default: false,
	},
	icon: {
		type: [Object, Function],
		default: null,
	},
	label: {
		type: String,
		default: "",
	},
})

const emit = defineEmits(["click"])

const buttonClasses = computed(() => {
	const baseClasses =
		"inline-flex items-center justify-center font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors"

	const variantClasses = {
		primary:
			"bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 disabled:bg-blue-400",
		secondary:
			"bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500 disabled:bg-gray-400",
		outline:
			"border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-400",
		danger:
			"bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 disabled:bg-red-400",
	}

	const sizeClasses = {
		sm: "px-3 py-1.5 text-sm",
		default: "px-4 py-2 text-sm",
		lg: "px-6 py-3 text-base",
	}

	return [
		baseClasses,
		variantClasses[props.variant],
		sizeClasses[props.size],
		props.disabled || props.loading
			? "cursor-not-allowed opacity-60"
			: "cursor-pointer",
	].join(" ")
})

const handleClick = (event) => {
	if (!props.disabled && !props.loading) {
		emit("click", event)
	}
}
</script>