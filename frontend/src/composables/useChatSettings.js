import { call, createResource } from "frappe-ui"
import { ref } from "vue"

export function useChatSettings() {
	const settings = ref(null)
	const loading = ref(false)
	const error = ref("")

	// API endpoints
	const GET_SETTINGS_URL =
		"mkaguzi.chat_system.doctype.chat_settings.chat_settings.get_chat_settings"
	const SAVE_SETTINGS_URL =
		"mkaguzi.chat_system.doctype.chat_settings.chat_settings.save_chat_settings"
	const RESET_CACHE_URL =
		"mkaguzi.chat_system.doctype.chat_settings.chat_settings.reset_chat_settings_cache"

	// Load settings from backend
	const loadSettings = async () => {
		loading.value = true
		error.value = ""

		try {
			const response = await call(GET_SETTINGS_URL)
			settings.value = response
		} catch (err) {
			error.value = err.message || "Failed to load chat settings"
			console.error("Error loading chat settings:", err)
		} finally {
			loading.value = false
		}
	}

	// Save settings to backend
	const saveSettings = async () => {
		if (!settings.value) return

		loading.value = true
		error.value = ""

		try {
			// Update the Chat Settings doctype using frappe client
			const saveResource = createResource({
				url: "frappe.client.save",
				params: {
					doc: {
						doctype: "Chat Settings",
						name: "Default",
						...settings.value,
					},
				},
			})

			await saveResource.submit()

			// Clear cache after saving
			await resetCache()
		} catch (err) {
			error.value = err.message || "Failed to save chat settings"
			console.error("Error saving chat settings:", err)
			throw err
		} finally {
			loading.value = false
		}
	}

	// Reset settings to defaults
	const resetSettings = async () => {
		loading.value = true
		error.value = ""

		try {
			// Call the create_default_chat_settings method
			await call(
				"mkaguzi.chat_system.doctype.chat_settings.chat_settings.create_default_chat_settings",
			)

			// Reload settings after reset
			await loadSettings()
		} catch (err) {
			error.value = err.message || "Failed to reset chat settings"
			console.error("Error resetting chat settings:", err)
			throw err
		} finally {
			loading.value = false
		}
	}

	// Reset cache
	const resetCache = async () => {
		try {
			await call(RESET_CACHE_URL)
		} catch (err) {
			console.warn("Failed to reset cache:", err)
			// Don't throw error for cache reset failures
		}
	}

	// Update individual setting
	const updateSetting = (key, value) => {
		if (settings.value) {
			settings.value[key] = value
		}
	}

	// Get specific setting value
	const getSetting = (key, defaultValue = null) => {
		return settings.value ? settings.value[key] : defaultValue
	}

	return {
		settings,
		loading,
		error,
		loadSettings,
		saveSettings,
		resetSettings,
		resetCache,
		updateSetting,
		getSetting,
	}
}
