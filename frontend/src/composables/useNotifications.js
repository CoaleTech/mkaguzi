import { useUIStore } from "@/stores/ui"

export function useNotifications() {
	const uiStore = useUIStore()

	const success = (message) => {
		uiStore.showToast(message, "success")
	}

	const error = (message) => {
		uiStore.showToast(message, "error")
	}

	const warning = (message) => {
		uiStore.showToast(message, "warning")
	}

	const info = (message) => {
		uiStore.showToast(message, "info")
	}

	return { success, error, warning, info }
}
