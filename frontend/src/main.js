import { createPinia } from "pinia"
import { createApp } from "vue"

import App from "./App.vue"
import router from "./router"

import { io } from "socket.io-client"

import {
	Alert,
	Badge,
	Button,
	Dialog,
	ErrorMessage,
	FormControl,
	Input,
	TextInput,
	frappeRequest,
	pageMetaPlugin,
	resourcesPlugin,
	setConfig,
} from "frappe-ui"

import "./index.css"

import BaseTemplate from "./components/templates/BaseTemplate.vue"
import TemplateEditor from "./components/templates/TemplateEditor.vue"
// Import template components
import TemplateManager from "./components/templates/TemplateManager.vue"
import TemplateMarketplace from "./components/templates/TemplateMarketplace.vue"
import TemplatePreview from "./components/templates/TemplatePreview.vue"
import PublishTemplateForm from "./components/templates/marketplace/PublishTemplateForm.vue"
import TemplateDetail from "./components/templates/marketplace/TemplateDetail.vue"

const globalComponents = {
	Button,
	TextInput,
	Input,
	FormControl,
	ErrorMessage,
	Dialog,
	Alert,
	Badge,
	// Template components
	TemplateManager,
	TemplateEditor,
	TemplatePreview,
	BaseTemplate,
	TemplateMarketplace,
	PublishTemplateForm,
	TemplateDetail,
}

const app = createApp(App)
const pinia = createPinia()

setConfig("resourceFetcher", frappeRequest)

app.use(pinia)
app.use(router)
app.use(resourcesPlugin)
app.use(pageMetaPlugin)

for (const key in globalComponents) {
	app.component(key, globalComponents[key])
}

// Initialize socket.io connection for real-time features
const siteName = import.meta.env.DEV
	? window.location.hostname
	: window.site_name || "ukaguzi"
const socketUrl = `http://localhost:9023/${siteName}`

// Get the session cookie for authentication
const getCookie = (name) => {
	const value = `; ${document.cookie}`
	const parts = value.split(`; ${name}=`)
	if (parts.length === 2) return parts.pop().split(";").shift()
}

const sid = getCookie("sid") || getCookie("user_id")
const auth = sid ? { sid } : {}

const socket = io(socketUrl, {
	withCredentials: true,
	auth,
	transports: ["websocket", "polling"],
})
window.frappe = window.frappe || {}
window.frappe.realtime = socket

app.mount("#app")

// Expose components globally for page templates
window.mkaguzi = window.mkaguzi || {}
window.mkaguzi.components = {
	TemplateManager,
	TemplateEditor,
	TemplatePreview,
	BaseTemplate,
	TemplateMarketplace,
	PublishTemplateForm,
	TemplateDetail,
}
