import { call } from "frappe-ui"
import { onMounted, onUnmounted, ref, watch } from "vue"

// Frappe realtime events
export function useChatRealtime(roomName, currentUser) {
	const isConnected = ref(false)
	const typingUsers = ref([])
	const onlineUsers = ref([])
	let connectRetryCount = 0
	const MAX_CONNECT_RETRIES = 50 // 5 seconds max (50 * 100ms)

	// Event callbacks
	const callbacks = {
		onMessageCreated: [],
		onMessageUpdated: [],
		onMessageDeleted: [],
		onReactionAdded: [],
		onReactionRemoved: [],
		onTypingStart: [],
		onTypingStop: [],
		onUserJoined: [],
		onUserLeft: [],
		onPresenceUpdate: [],
	}

	// Typing debounce
	let typingTimeout = null
	const TYPING_TIMEOUT = 3000

	/**
	 * Initialize real-time listeners
	 */
	const connect = () => {
		console.log("useChatRealtime connect called")
		if (!window.frappe?.realtime) {
			connectRetryCount++
			if (connectRetryCount >= MAX_CONNECT_RETRIES) {
				console.error("Frappe realtime not available after maximum retries")
				return
			}
			console.warn(
				`Frappe realtime not available, retry ${connectRetryCount}/${MAX_CONNECT_RETRIES}`,
			)
			// Retry connection after a short delay
			setTimeout(() => {
				connect()
			}, 100)
			return
		}

		console.log("Frappe realtime available, setting up listeners")
		isConnected.value = true
		connectRetryCount = 0 // Reset retry count on success
		setupListeners()
	}

	/**
	 * Setup event listeners using Frappe realtime
	 */
	const setupListeners = () => {
		if (!window.frappe?.realtime) return

		// Remove existing listeners first to avoid duplicates
		cleanupListeners()

		// Message events
		window.frappe.realtime.on("mkaguzi_chat_message", (data) => {
			console.log("Received mkaguzi_chat_message event:", data)
			callbacks.onMessageCreated.forEach((cb) => cb(data))
		})

		window.frappe.realtime.on("mkaguzi_message_updated", (data) => {
			console.log("Received mkaguzi_message_updated event:", data)
			callbacks.onMessageUpdated.forEach((cb) => cb(data))
		})

		window.frappe.realtime.on("mkaguzi_message_deleted", (data) => {
			console.log("Received mkaguzi_message_deleted event:", data)
			callbacks.onMessageDeleted.forEach((cb) => cb(data))
		})

		// Reaction events
		window.frappe.realtime.on("mkaguzi_reaction_added", (data) => {
			callbacks.onReactionAdded.forEach((cb) => cb(data))
		})

		window.frappe.realtime.on("mkaguzi_reaction_removed", (data) => {
			callbacks.onReactionRemoved.forEach((cb) => cb(data))
		})

		// Typing events
		window.frappe.realtime.on("mkaguzi_typing_start", (data) => {
			if (data.room === roomName.value && data.user !== currentUser.value) {
				if (!typingUsers.value.find((u) => u.user === data.user)) {
					typingUsers.value.push({
						user: data.user,
						full_name: data.full_name,
					})
				}
				callbacks.onTypingStart.forEach((cb) => cb(data))

				// Auto-remove after timeout
				setTimeout(() => {
					typingUsers.value = typingUsers.value.filter(
						(u) => u.user !== data.user,
					)
				}, TYPING_TIMEOUT)
			}
		})

		window.frappe.realtime.on("mkaguzi_typing_stop", (data) => {
			if (data.room === roomName.value) {
				typingUsers.value = typingUsers.value.filter(
					(u) => u.user !== data.user,
				)
				callbacks.onTypingStop.forEach((cb) => cb(data))
			}
		})

		// Presence events
		window.frappe.realtime.on("mkaguzi_user_joined", (data) => {
			if (data.room === roomName.value) {
				if (!onlineUsers.value.includes(data.user)) {
					onlineUsers.value.push(data.user)
				}
				callbacks.onUserJoined.forEach((cb) => cb(data))
			}
		})

		window.frappe.realtime.on("mkaguzi_user_left", (data) => {
			if (data.room === roomName.value) {
				onlineUsers.value = onlineUsers.value.filter((u) => u !== data.user)
				callbacks.onUserLeft.forEach((cb) => cb(data))
			}
		})

		window.frappe.realtime.on("mkaguzi_presence_update", (data) => {
			if (data.room === roomName.value) {
				onlineUsers.value = data.online_users || []
				callbacks.onPresenceUpdate.forEach((cb) => cb(data))
			}
		})
	}

	/**
	 * Cleanup existing listeners
	 */
	const cleanupListeners = () => {
		if (!window.frappe?.realtime) return

		// Note: Frappe realtime doesn't provide a way to remove specific listeners
		// The listeners will be replaced when setupListeners is called again
	}

	/**
	 * Join a chat room
	 */
	const joinRoom = async () => {
		if (!roomName.value) {
			console.log("joinRoom called but no room name")
			return
		}

		console.log("Joining room:", roomName.value)
		try {
			await call("mkaguzi.api.chat.join_room_realtime", {
				room_name: roomName.value,
			})

			console.log("Successfully joined room, setting up listeners")
			// Re-setup listeners for the new room
			setupListeners()
		} catch (error) {
			console.error("Failed to join room:", error)
		}
	}

	/**
	 * Leave current room
	 */
	const leaveRoom = async () => {
		if (!roomName.value) return

		try {
			await call("mkaguzi.api.chat.leave_room_realtime", {
				room_name: roomName.value,
			})
		} catch (error) {
			console.error("Failed to leave room:", error)
		}
	}

	/**
	 * Send typing indicator
	 */
	const sendTyping = async (isTyping = true) => {
		if (!roomName.value) return

		try {
			if (isTyping) {
				// Call API to start typing
				await call("mkaguzi.api.chat.start_typing", {
					room_name: roomName.value,
				})

				// Clear previous timeout
				if (typingTimeout) {
					clearTimeout(typingTimeout)
				}

				// Auto-stop typing after timeout
				typingTimeout = setTimeout(() => {
					sendTyping(false)
				}, TYPING_TIMEOUT)
			} else {
				// Call API to stop typing
				await call("mkaguzi.api.chat.stop_typing", {
					room_name: roomName.value,
				})

				if (typingTimeout) {
					clearTimeout(typingTimeout)
					typingTimeout = null
				}
			}
		} catch (error) {
			console.error("Failed to send typing indicator:", error)
		}
	}

	/**
	 * Emit message created event (for optimistic updates - not needed with realtime)
	 */
	const emitMessageCreated = (message) => {
		// Messages are published from backend, no need to emit from frontend
	}

	/**
	 * Emit message updated event (for optimistic updates - not needed with realtime)
	 */
	const emitMessageUpdated = (message) => {
		// Messages are published from backend, no need to emit from frontend
	}

	/**
	 * Emit message deleted event (for optimistic updates - not needed with realtime)
	 */
	const emitMessageDeleted = (messageName) => {
		// Messages are published from backend, no need to emit from frontend
	}

	/**
	 * Emit reaction events (placeholder for future implementation)
	 */
	const emitReactionAdded = (messageName, emoji, user) => {
		// TODO: Implement reaction API
	}

	const emitReactionRemoved = (messageName, emoji, user) => {
		// TODO: Implement reaction API
	}

	/**
	 * Register event callbacks
	 */
	const on = (event, callback) => {
		const eventName = `on${event.charAt(0).toUpperCase()}${event.slice(1)}`
		if (callbacks[eventName]) {
			callbacks[eventName].push(callback)
		}
		return () => off(event, callback)
	}

	const off = (event, callback) => {
		const eventName = `on${event.charAt(0).toUpperCase()}${event.slice(1)}`
		if (callbacks[eventName]) {
			callbacks[eventName] = callbacks[eventName].filter(
				(cb) => cb !== callback,
			)
		}
	}

	/**
	 * Disconnect and cleanup
	 */
	const disconnect = () => {
		if (typingTimeout) {
			clearTimeout(typingTimeout)
		}

		leaveRoom()

		// Remove all listeners
		if (window.frappe?.realtime) {
			// Note: Frappe doesn't have a direct way to remove all listeners for specific events
			// They are cleaned up when the page unloads
		}

		isConnected.value = false
		typingUsers.value = []
		onlineUsers.value = []
	}

	// Auto-connect on mount
	onMounted(() => {
		connect()
	})

	// Watch for room changes and re-setup listeners
	watch(roomName, (newRoom, oldRoom) => {
		if (newRoom && newRoom !== oldRoom && isConnected.value) {
			setupListeners()
		}
	})

	// Cleanup on unmount
	onUnmounted(() => {
		disconnect()
	})

	return {
		// State
		isConnected,
		typingUsers,
		onlineUsers,

		// Methods
		connect,
		disconnect,
		joinRoom,
		leaveRoom,
		sendTyping,

		// Emit methods (deprecated with realtime)
		emitMessageCreated,
		emitMessageUpdated,
		emitMessageDeleted,
		emitReactionAdded,
		emitReactionRemoved,

		// Event registration
		on,
		off,
	}
}
