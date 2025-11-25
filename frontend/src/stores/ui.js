import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useUIStore = defineStore("ui", () => {
	// State
	const sidebarCollapsed = ref(false)
	const theme = ref("light")
	const notifications = ref([])
	const toastMessages = ref([])
	const loadingStates = ref(new Map())

	// Getters
	const unreadNotifications = computed(() => {
		return notifications.value.filter((n) => !n.read)
	})

	const unreadCount = computed(() => {
		return unreadNotifications.value.length
	})

	const isLoading = computed(() => {
		return (key) => loadingStates.value.get(key) || false
	})

	const activeToastMessages = computed(() => {
		return toastMessages.value.filter((t) => !t.dismissed)
	})

	// Actions
	const toggleSidebar = () => {
		sidebarCollapsed.value = !sidebarCollapsed.value
	}

	const setSidebarCollapsed = (collapsed) => {
		sidebarCollapsed.value = collapsed
	}

	const setTheme = (newTheme) => {
		theme.value = newTheme
		document.documentElement.setAttribute("data-theme", newTheme)
		localStorage.setItem("theme", newTheme)
	}

	const toggleTheme = () => {
		const newTheme = theme.value === "dark" ? "light" : "dark"
		setTheme(newTheme)
	}

	const addNotification = (notification) => {
		notifications.value.unshift({
			id: Date.now(),
			read: false,
			timestamp: new Date(),
			...notification,
		})
	}

	const markNotificationAsRead = (notificationId) => {
		const notification = notifications.value.find(
			(n) => n.id === notificationId,
		)
		if (notification) {
			notification.read = true
		}
	}

	const markAllNotificationsAsRead = () => {
		notifications.value.forEach((n) => {
			n.read = true
		})
	}

	const removeNotification = (notificationId) => {
		notifications.value = notifications.value.filter(
			(n) => n.id !== notificationId,
		)
	}

	const clearNotifications = () => {
		notifications.value = []
	}

	const showToast = (message, type = "info", duration = 5000) => {
		const toast = {
			id: Date.now(),
			message,
			type, // 'success', 'error', 'warning', 'info'
			duration,
			dismissed: false,
			timestamp: new Date(),
		}

		toastMessages.value.unshift(toast)

		// Auto-dismiss after duration
		if (duration > 0) {
			setTimeout(() => {
				dismissToast(toast.id)
			}, duration)
		}

		return toast.id
	}

	const dismissToast = (toastId) => {
		const toast = toastMessages.value.find((t) => t.id === toastId)
		if (toast) {
			toast.dismissed = true
		}
	}

	const clearToasts = () => {
		toastMessages.value = []
	}

	const setLoading = (key, loading) => {
		if (loading) {
			loadingStates.value.set(key, true)
		} else {
			loadingStates.value.delete(key)
		}
	}

	const initializeTheme = () => {
		const savedTheme = localStorage.getItem("theme") || "light"
		setTheme(savedTheme)
	}

	return {
		// State
		sidebarCollapsed,
		theme,
		notifications,
		toastMessages,
		loadingStates,

		// Getters
		unreadNotifications,
		unreadCount,
		isLoading,
		activeToastMessages,

		// Actions
		toggleSidebar,
		setSidebarCollapsed,
		setTheme,
		toggleTheme,
		addNotification,
		markNotificationAsRead,
		markAllNotificationsAsRead,
		removeNotification,
		clearNotifications,
		showToast,
		dismissToast,
		clearToasts,
		setLoading,
		initializeTheme,
	}
})
