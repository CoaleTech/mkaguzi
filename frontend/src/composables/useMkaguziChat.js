/**
 * Mkaguzi Chat Composable
 * Provides reactive chat functionality with RAG-enhanced AI responses
 */

import { call, createResource } from "frappe-ui"
import { computed, onMounted, onUnmounted, ref, watch } from "vue"

// API base path
const API_BASE = "mkaguzi.api.chat"

/**
 * Main chat composable for managing rooms, messages, and AI interactions
 */
export function useMkaguziChat() {
	// State
	const rooms = ref([])
	const selectedRoom = ref(null) // Renamed from currentRoom for consistency
	const currentRoom = selectedRoom // Alias for backward compatibility
	const messages = ref([])
	const participants = ref([])
	const users = ref([])
	const loading = ref(false)
	const roomsLoading = ref(false)
	const messagesLoading = ref(false)
	const usersLoading = ref(false)
	const sendingMessage = ref(false)
	const hasMoreMessages = ref(false)
	const error = ref(null)
	const aiSettings = ref(null)
	const indexStats = ref(null)
	const currentUser = ref("")

	// Resources
	const roomsResource = createResource({
		url: `${API_BASE}.get_rooms`,
		onSuccess: (data) => {
			rooms.value = data?.rooms || []
		},
		onError: (err) => {
			error.value = err.message || "Failed to load rooms"
			console.error("Failed to load rooms:", err)
		},
	})

	const settingsResource = createResource({
		url: `${API_BASE}.get_chat_settings`,
		onSuccess: (data) => {
			aiSettings.value = data
		},
		onError: (err) => {
			console.error("Failed to load AI settings:", err)
		},
	})

	// Computed
	const engagementRooms = computed(() =>
		rooms.value.filter((r) => r.room_type === "Engagement"),
	)

	const directRooms = computed(() =>
		rooms.value.filter((r) => r.room_type === "Direct"),
	)

	const groupRooms = computed(() =>
		rooms.value.filter((r) => r.room_type === "Group"),
	)

	const isAiEnabled = computed(
		() =>
			aiSettings.value?.enable_ai_chat && aiSettings.value?.openrouter_api_key,
	)

	const selectedModel = computed(
		() =>
			aiSettings.value?.default_model ||
			"meta-llama/llama-3.1-8b-instruct:free",
	)

	// Methods
	const fetchRooms = async () => {
		roomsLoading.value = true
		error.value = null
		try {
			await roomsResource.fetch()
		} finally {
			roomsLoading.value = false
		}
	}

	// Alias for backward compatibility
	const loadRooms = fetchRooms

	const loadSettings = async () => {
		try {
			await settingsResource.fetch()
		} catch (err) {
			console.error("Failed to load settings:", err)
		}
	}

	const fetchUsers = async (query = "", limit = 50) => {
		usersLoading.value = true
		try {
			const response = await call(`${API_BASE}.search_users`, {
				query,
				limit,
			})
			// Handle both frappe-ui call (direct data) and frappe.call (wrapped in message)
			users.value = response?.message || response || []
		} catch (err) {
			console.error("Failed to load users:", err)
			users.value = []
		} finally {
			usersLoading.value = false
		}
	}

	const createRoom = async (roomData) => {
		loading.value = true
		error.value = null
		try {
			const response = await call(`${API_BASE}.create_room`, {
				room_name: roomData.room_name,
				room_type: roomData.room_type || "Group",
				linked_engagement:
					roomData.linked_engagement || roomData.engagement || null,
				is_ai_enabled: roomData.is_ai_enabled !== false,
				participants: roomData.participants || [],
			})

			if (response) {
				await fetchRooms()
				return response
			}
		} catch (err) {
			error.value = err.message || "Failed to create room"
			throw err
		} finally {
			loading.value = false
		}
	}

	const selectRoom = async (room) => {
		const roomName = typeof room === "string" ? room : room?.name
		if (!roomName) return

		messagesLoading.value = true
		error.value = null
		try {
			const response = await call(`${API_BASE}.get_room_details`, {
				room_name: roomName,
			})

			if (response) {
				selectedRoom.value = response
				participants.value = response.participants || []
				await loadMessages(roomName)
			}
			return response
		} catch (err) {
			error.value = err.message || "Failed to load room"
			throw err
		} finally {
			messagesLoading.value = false
		}
	}

	const loadMessages = async (roomName, limit = 50, offset = 0) => {
		try {
			const response = await call(`${API_BASE}.get_messages`, {
				room_name: roomName || selectedRoom.value?.name,
				limit,
				offset,
			})

			if (response) {
				if (offset === 0) {
					messages.value = response || []
				} else {
					// Prepend older messages
					messages.value = [...(response || []), ...messages.value]
				}
				hasMoreMessages.value = (response?.length || 0) >= limit
			}
		} catch (err) {
			error.value = err.message || "Failed to load messages"
			throw err
		}
	}

	const loadMoreMessages = async () => {
		if (!selectedRoom.value || !hasMoreMessages.value) return

		const offset = messages.value.length
		await loadMessages(selectedRoom.value.name, 50, offset)
	}

	const sendMessage = async (
		content,
		replyTo = null,
		isAiPrompt = false,
		messageType = "User",
	) => {
		if (!selectedRoom.value) {
			throw new Error("No room selected")
		}

		sendingMessage.value = true
		error.value = null
		try {
			const response = await call(`${API_BASE}.send_message`, {
				room_name: selectedRoom.value.name,
				content,
				message_type: messageType,
				reply_to: replyTo,
			})

			if (response && response.message) {
				// Add the actual message object to local messages
				messages.value.push(response.message)

				// If AI prompt, get AI response
				if (isAiPrompt && selectedRoom.value.is_ai_enabled) {
					await getAiResponse(content)
				}

				return response.message
			}
		} catch (err) {
			error.value = err.message || "Failed to send message"
			throw err
		} finally {
			sendingMessage.value = false
		}
	}

	const editMessage = async (messageName, newContent) => {
		try {
			const response = await call(`${API_BASE}.edit_message`, {
				message_name: messageName,
				content: newContent,
			})

			if (response) {
				// Update local message
				const idx = messages.value.findIndex((m) => m.name === messageName)
				if (idx !== -1) {
					messages.value[idx] = { ...messages.value[idx], ...response }
				}
				return response
			}
		} catch (err) {
			error.value = err.message || "Failed to edit message"
			throw err
		}
	}

	const deleteMessage = async (messageName) => {
		try {
			await call(`${API_BASE}.delete_message`, {
				message_name: messageName,
			})

			// Remove from local messages
			messages.value = messages.value.filter((m) => m.name !== messageName)
		} catch (err) {
			error.value = err.message || "Failed to delete message"
			throw err
		}
	}

	const addReaction = async (messageName, emoji) => {
		try {
			const response = await call(`${API_BASE}.add_reaction`, {
				message_name: messageName,
				emoji,
			})

			// Update local message reactions
			const idx = messages.value.findIndex((m) => m.name === messageName)
			if (idx !== -1 && response) {
				messages.value[idx].reactions = response.reactions
			}
			return response
		} catch (err) {
			error.value = err.message || "Failed to add reaction"
			throw err
		}
	}

	const removeReaction = async (messageName, emoji) => {
		try {
			const response = await call(`${API_BASE}.remove_reaction`, {
				message_name: messageName,
				emoji,
			})

			// Update local message reactions
			const idx = messages.value.findIndex((m) => m.name === messageName)
			if (idx !== -1 && response) {
				messages.value[idx].reactions = response.reactions
			}
			return response
		} catch (err) {
			error.value = err.message || "Failed to remove reaction"
			throw err
		}
	}

	const getAiResponse = async (userMessage) => {
		if (!selectedRoom.value) {
			throw new Error("No room selected")
		}

		if (!isAiEnabled.value) {
			throw new Error("AI assistant is not enabled")
		}

		error.value = null
		try {
			const response = await call(`${API_BASE}.get_ai_response`, {
				room_name: selectedRoom.value.name,
				user_message: userMessage,
				include_context: true,
			})

			if (response) {
				// Add AI message to local messages
				if (response.message) {
					messages.value.push(response.message)
				}
				return response
			}
		} catch (err) {
			error.value = err.message || "Failed to get AI response"
			throw err
		}
	}

	const testAiConnection = async () => {
		try {
			const response = await call(`${API_BASE}.test_ai_connection`)
			return response
		} catch (err) {
			error.value = err.message || "AI connection test failed"
			throw err
		}
	}

	const indexDocuments = async (engagementId) => {
		try {
			const response = await call(`${API_BASE}.index_documents`, {
				engagement_id: engagementId,
			})
			return response
		} catch (err) {
			error.value = err.message || "Failed to index documents"
			throw err
		}
	}

	const getIndexStats = async () => {
		try {
			const response = await call(`${API_BASE}.get_index_stats`)
			indexStats.value = response
			return response
		} catch (err) {
			console.error("Failed to get index stats:", err)
		}
	}

	const getActiveEngagements = async () => {
		try {
			const response = await call(`${API_BASE}.get_active_engagements`)
			return response?.engagements || []
		} catch (err) {
			console.error("Failed to get engagements:", err)
			return []
		}
	}

	// ==================== Direct Message Methods ====================

	/**
	 * Get or create a DM room with another user
	 * @param {string} targetUser - The user to start a DM with
	 * @returns {Promise<object>} The DM room details
	 */
	const getOrCreateDM = async (targetUser) => {
		loading.value = true
		error.value = null
		try {
			const response = await call(`${API_BASE}.get_or_create_dm`, {
				target_user: targetUser,
			})

			if (response) {
				// Refresh rooms list to include the new/existing DM
				await fetchRooms()
				return response
			}
		} catch (err) {
			error.value = err.message || "Failed to create direct message"
			throw err
		} finally {
			loading.value = false
		}
	}

	/**
	 * Start a DM conversation with a user and select the room
	 * @param {string} targetUser - The user to start a DM with
	 * @returns {Promise<object>} The selected DM room
	 */
	const startDirectMessage = async (targetUser) => {
		try {
			const dmRoom = await getOrCreateDM(targetUser)
			if (dmRoom) {
				await selectRoom(dmRoom.name)
				return dmRoom
			}
		} catch (err) {
			console.error("Failed to start DM:", err)
			throw err
		}
	}

	/**
	 * Get all DM rooms for the current user
	 * @returns {Promise<array>} List of DM rooms
	 */
	const getUserDMRooms = async () => {
		try {
			const response = await call(`${API_BASE}.get_user_dm_rooms`)
			return response?.rooms || []
		} catch (err) {
			console.error("Failed to get DM rooms:", err)
			return []
		}
	}

	// Computed for DM rooms (Private type with 2 participants)
	const dmRooms = computed(() =>
		rooms.value.filter((r) => r.room_type === "Private" && r.is_dm),
	)

	// Initialize current user
	const initCurrentUser = async () => {
		try {
			// Use frappe-ui call instead of frappe.call
			const response = await call("frappe.auth.get_logged_user")
			currentUser.value = response?.message || response || "Administrator"
		} catch {
			currentUser.value = "Administrator"
		}
	}

	// Real-time updates via Frappe's socket
	const setupRealtime = () => {
		if (typeof frappe !== "undefined" && frappe.realtime) {
			frappe.realtime.on("mkaguzi_chat_message", (data) => {
				if (selectedRoom.value && data.room === selectedRoom.value.name) {
					// Check if message already exists
					const exists = messages.value.some(
						(m) => m.name === data.message?.name,
					)
					if (!exists && data.message) {
						messages.value.push(data.message)
					}
				}
			})

			frappe.realtime.on("mkaguzi_message_updated", (data) => {
				if (selectedRoom.value && data.room === selectedRoom.value.name) {
					const idx = messages.value.findIndex(
						(m) => m.name === data.message?.name,
					)
					if (idx !== -1 && data.message) {
						messages.value[idx] = { ...messages.value[idx], ...data.message }
					}
				}
			})

			frappe.realtime.on("mkaguzi_message_deleted", (data) => {
				if (selectedRoom.value && data.room === selectedRoom.value.name) {
					messages.value = messages.value.filter(
						(m) => m.name !== data.message_name,
					)
				}
			})
		}
	}

	const cleanupRealtime = () => {
		if (typeof frappe !== "undefined" && frappe.realtime) {
			frappe.realtime.off("mkaguzi_chat_message")
			frappe.realtime.off("mkaguzi_message_updated")
			frappe.realtime.off("mkaguzi_message_deleted")
		}
	}

	// Initialize on mount
	initCurrentUser()

	return {
		// State
		rooms,
		selectedRoom,
		currentRoom, // Alias
		messages,
		participants,
		users,
		loading,
		roomsLoading,
		messagesLoading,
		usersLoading,
		sendingMessage,
		hasMoreMessages,
		error,
		aiSettings,
		indexStats,
		currentUser,

		// Computed
		engagementRooms,
		directRooms,
		groupRooms,
		dmRooms,
		isAiEnabled,
		selectedModel,

		// Methods
		fetchRooms,
		loadRooms, // Alias
		loadSettings,
		fetchUsers,
		createRoom,
		selectRoom,
		loadMessages,
		loadMoreMessages,
		sendMessage,
		editMessage,
		deleteMessage,
		addReaction,
		removeReaction,
		getAiResponse,
		testAiConnection,
		indexDocuments,
		getIndexStats,
		getActiveEngagements,

		// Direct Message Methods
		getOrCreateDM,
		startDirectMessage,
		getUserDMRooms,

		// Realtime
		setupRealtime,
		cleanupRealtime,
	}
}

/**
 * AI Assistant composable for direct AI interactions
 */
export function useAiAssistant() {
	const thinking = ref(false)
	const lastResponse = ref(null)
	const contextSources = ref([])
	const availableModels = ref([
		{
			value: "meta-llama/llama-3.1-8b-instruct:free",
			label: "Llama 3.1 8B (Free)",
		},
		{ value: "google/gemma-2-9b-it:free", label: "Gemma 2 9B (Free)" },
		{ value: "qwen/qwen-2.5-7b-instruct:free", label: "Qwen 2.5 7B (Free)" },
	])

	const askQuestion = async (question, roomName, options = {}) => {
		thinking.value = true
		lastResponse.value = null
		contextSources.value = []

		try {
			const response = await call(`${API_BASE}.get_ai_response`, {
				room_name: roomName,
				user_message: question,
				include_context: options.includeContext !== false,
			})

			if (response) {
				lastResponse.value = response.response
				contextSources.value = response.context_sources || []
				return response
			}
		} catch (err) {
			console.error("AI assistant error:", err)
			throw err
		} finally {
			thinking.value = false
		}
	}

	const getContextPreview = async (query, engagementId) => {
		try {
			// This would call a dedicated endpoint to preview retrieved context
			// For now, we return empty
			return []
		} catch (err) {
			console.error("Failed to get context preview:", err)
			return []
		}
	}

	return {
		thinking,
		lastResponse,
		contextSources,
		availableModels,
		askQuestion,
		getContextPreview,
	}
}

/**
 * RAG Index management composable
 */
export function useRagIndex() {
	const indexing = ref(false)
	const progress = ref(0)
	const stats = ref(null)

	const indexEngagement = async (engagementId) => {
		indexing.value = true
		progress.value = 0

		try {
			const response = await call(`${API_BASE}.index_documents`, {
				engagement_id: engagementId,
			})

			progress.value = 100
			return response
		} catch (err) {
			console.error("Indexing failed:", err)
			throw err
		} finally {
			indexing.value = false
		}
	}

	const rebuildIndex = async () => {
		indexing.value = true
		progress.value = 0

		try {
			// This would call a full rebuild endpoint
			const response = await call(
				"mkaguzi.chat_system.chat_service.rebuild_rag_index",
			)
			progress.value = 100
			return response
		} catch (err) {
			console.error("Rebuild failed:", err)
			throw err
		} finally {
			indexing.value = false
		}
	}

	const getStats = async () => {
		try {
			const response = await call(`${API_BASE}.get_index_stats`)
			stats.value = response
			return response
		} catch (err) {
			console.error("Failed to get stats:", err)
		}
	}

	return {
		indexing,
		progress,
		stats,
		indexEngagement,
		rebuildIndex,
		getStats,
	}
}

export default useMkaguziChat
