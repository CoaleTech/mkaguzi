import { io } from "socket.io-client"

let socket = null
export function initSocket() {
	const host = window.location.hostname
	const port = window.location.port || 80
	const protocol = window.location.protocol === "https:" ? "https" : "http"

	// Try to get socketio_port from config, fallback to default
	let socketioPort = 9023 // default
	try {
		// Try to get from common_site_config if available
		const confScript = document.querySelector("script[data-config]")
		if (confScript && confScript.dataset.config) {
			const config = JSON.parse(confScript.dataset.config)
			socketioPort = config.socketio_port || 9023
		}
	} catch (e) {
		console.warn("Could not read socketio config, using default port 9023")
	}

	// Get site name - default to 'ukaguzi' from config
	const siteName = "ukaguzi" // Hardcoded for now, should match default_site in config
	const url = `${protocol}://${host}:${socketioPort}/${siteName}`

	console.log("Connecting to Socket.IO at:", url)

	socket = io(url, {
		withCredentials: true,
		reconnectionAttempts: 5,
		transports: ["websocket", "polling"],
		timeout: 20000,
	})

	socket.on("connect", () => {
		console.log("Socket.IO connected successfully")
	})

	socket.on("connect_error", (error) => {
		console.error("Socket.IO connection error:", error)
	})

	socket.on("disconnect", (reason) => {
		console.log("Socket.IO disconnected:", reason)
	})

	return socket
}

export function useSocket() {
	return socket
}
