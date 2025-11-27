import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useApiIntegrationStore = defineStore("apiIntegration", () => {
	// State
	const integrations = ref([])
	const connections = ref([])
	const webhooks = ref([])
	const syncJobs = ref([])
	const apiLogs = ref([])
	const transformations = ref([])
	const endpoints = ref([])
	const authProviders = ref([])
	const rateLimits = ref([])
	const loading = ref(false)
	const error = ref(null)

	// Sample data initialization
	const initializeSampleData = () => {
		// API Integrations
		integrations.value = [
			{
				id: "int_001",
				name: "Salesforce CRM",
				type: "REST",
				status: "Active",
				description: "Customer relationship management integration",
				base_url: "https://company.salesforce.com/services/data/v54.0/",
				auth_type: "OAuth2",
				version: "v54.0",
				rate_limit: 15000,
				rate_period: "hour",
				health_status: "Healthy",
				last_sync: "2025-11-25T10:30:00Z",
				next_sync: "2025-11-25T11:30:00Z",
				sync_frequency: "hourly",
				created: "2025-11-15T09:00:00Z",
				created_by: "John Doe",
				tags: ["CRM", "Customer Data", "Sales"],
				metadata: {
					total_requests: 125680,
					successful_requests: 124892,
					failed_requests: 788,
					avg_response_time: 245,
					last_error: null,
					uptime_percentage: 99.37,
				},
			},
			{
				id: "int_002",
				name: "SAP ERP",
				type: "REST",
				status: "Active",
				description: "Enterprise resource planning system integration",
				base_url: "https://erp.company.com/api/v2/",
				auth_type: "API_Key",
				version: "v2.1",
				rate_limit: 5000,
				rate_period: "hour",
				health_status: "Warning",
				last_sync: "2025-11-25T10:15:00Z",
				next_sync: "2025-11-25T12:15:00Z",
				sync_frequency: "every_2_hours",
				created: "2025-11-10T14:20:00Z",
				created_by: "Jane Smith",
				tags: ["ERP", "Financial Data", "Procurement"],
				metadata: {
					total_requests: 87340,
					successful_requests: 85120,
					failed_requests: 2220,
					avg_response_time: 1200,
					last_error: "Rate limit exceeded",
					uptime_percentage: 97.45,
				},
			},
			{
				id: "int_003",
				name: "Microsoft Graph",
				type: "GraphQL",
				status: "Active",
				description: "Microsoft 365 integration for user and document data",
				base_url: "https://graph.microsoft.com/v1.0/",
				auth_type: "OAuth2",
				version: "v1.0",
				rate_limit: 10000,
				rate_period: "minute",
				health_status: "Healthy",
				last_sync: "2025-11-25T10:45:00Z",
				next_sync: "2025-11-25T11:00:00Z",
				sync_frequency: "every_15_minutes",
				created: "2025-11-20T11:30:00Z",
				created_by: "Mike Johnson",
				tags: ["Microsoft 365", "Documents", "Users"],
				metadata: {
					total_requests: 45680,
					successful_requests: 45321,
					failed_requests: 359,
					avg_response_time: 180,
					last_error: null,
					uptime_percentage: 99.21,
				},
			},
			{
				id: "int_004",
				name: "AWS CloudWatch",
				type: "REST",
				status: "Inactive",
				description: "Infrastructure monitoring and logging",
				base_url: "https://monitoring.us-east-1.amazonaws.com/",
				auth_type: "AWS_Signature",
				version: "2010-08-01",
				rate_limit: 20000,
				rate_period: "hour",
				health_status: "Disconnected",
				last_sync: "2025-11-24T18:30:00Z",
				next_sync: null,
				sync_frequency: "daily",
				created: "2025-11-18T16:45:00Z",
				created_by: "Sarah Wilson",
				tags: ["AWS", "Monitoring", "Logs"],
				metadata: {
					total_requests: 12450,
					successful_requests: 12089,
					failed_requests: 361,
					avg_response_time: 320,
					last_error: "Authentication failed",
					uptime_percentage: 97.1,
				},
			},
		]

		// API Connections
		connections.value = [
			{
				id: "conn_001",
				integration_id: "int_001",
				name: "Salesforce Production",
				environment: "Production",
				status: "Connected",
				connection_string: "https://company.salesforce.com",
				auth_config: {
					client_id: "sf_client_123",
					client_secret: "***",
					refresh_token: "***",
					access_token: "***",
					expires_at: "2025-11-25T12:30:00Z",
				},
				test_endpoint: "/sobjects/Account",
				last_tested: "2025-11-25T10:00:00Z",
				test_status: "Success",
				created: "2025-11-15T09:00:00Z",
			},
			{
				id: "conn_002",
				integration_id: "int_002",
				name: "SAP Production",
				environment: "Production",
				status: "Connected",
				connection_string: "https://erp.company.com",
				auth_config: {
					api_key: "***",
					username: "api_user",
					password: "***",
				},
				test_endpoint: "/health",
				last_tested: "2025-11-25T09:45:00Z",
				test_status: "Warning",
				created: "2025-11-10T14:20:00Z",
			},
			{
				id: "conn_003",
				integration_id: "int_003",
				name: "Microsoft Graph Production",
				environment: "Production",
				status: "Connected",
				connection_string: "https://graph.microsoft.com",
				auth_config: {
					tenant_id: "tenant_123",
					client_id: "graph_client_456",
					client_secret: "***",
					scope: "https://graph.microsoft.com/.default",
				},
				test_endpoint: "/me",
				last_tested: "2025-11-25T10:30:00Z",
				test_status: "Success",
				created: "2025-11-20T11:30:00Z",
			},
		]

		// Webhooks
		webhooks.value = [
			{
				id: "wh_001",
				integration_id: "int_001",
				name: "Salesforce Account Updates",
				url: "/api/webhooks/salesforce/accounts",
				method: "POST",
				status: "Active",
				events: ["account.created", "account.updated", "account.deleted"],
				secret: "wh_secret_123",
				retry_attempts: 3,
				timeout: 30,
				last_triggered: "2025-11-25T09:15:00Z",
				total_deliveries: 1250,
				successful_deliveries: 1198,
				failed_deliveries: 52,
				created: "2025-11-15T09:30:00Z",
				created_by: "John Doe",
			},
			{
				id: "wh_002",
				integration_id: "int_002",
				name: "SAP Purchase Order Events",
				url: "/api/webhooks/sap/purchase-orders",
				method: "POST",
				status: "Active",
				events: ["po.created", "po.approved", "po.rejected"],
				secret: "wh_secret_456",
				retry_attempts: 5,
				timeout: 45,
				last_triggered: "2025-11-25T08:30:00Z",
				total_deliveries: 856,
				successful_deliveries: 789,
				failed_deliveries: 67,
				created: "2025-11-10T15:00:00Z",
				created_by: "Jane Smith",
			},
			{
				id: "wh_003",
				integration_id: "int_003",
				name: "Microsoft Teams Messages",
				url: "/api/webhooks/teams/messages",
				method: "POST",
				status: "Paused",
				events: ["message.created", "message.updated"],
				secret: "wh_secret_789",
				retry_attempts: 3,
				timeout: 30,
				last_triggered: "2025-11-24T16:45:00Z",
				total_deliveries: 2340,
				successful_deliveries: 2301,
				failed_deliveries: 39,
				created: "2025-11-20T12:00:00Z",
				created_by: "Mike Johnson",
			},
		]

		// Sync Jobs
		syncJobs.value = [
			{
				id: "job_001",
				integration_id: "int_001",
				name: "Daily Customer Sync",
				type: "Scheduled",
				status: "Running",
				schedule: "0 2 * * *", // Daily at 2 AM
				next_run: "2025-11-26T02:00:00Z",
				last_run: "2025-11-25T02:00:00Z",
				duration: 1200, // seconds
				records_processed: 15680,
				records_created: 45,
				records_updated: 234,
				records_failed: 12,
				success_rate: 99.2,
				created: "2025-11-15T10:00:00Z",
				created_by: "John Doe",
			},
			{
				id: "job_002",
				integration_id: "int_002",
				name: "Hourly Financial Data Sync",
				type: "Scheduled",
				status: "Completed",
				schedule: "0 * * * *", // Every hour
				next_run: "2025-11-25T11:00:00Z",
				last_run: "2025-11-25T10:00:00Z",
				duration: 450,
				records_processed: 2340,
				records_created: 12,
				records_updated: 89,
				records_failed: 3,
				success_rate: 97.1,
				created: "2025-11-10T16:00:00Z",
				created_by: "Jane Smith",
			},
			{
				id: "job_003",
				integration_id: "int_003",
				name: "User Directory Sync",
				type: "Manual",
				status: "Failed",
				schedule: null,
				next_run: null,
				last_run: "2025-11-25T09:30:00Z",
				duration: 180,
				records_processed: 0,
				records_created: 0,
				records_updated: 0,
				records_failed: 1,
				success_rate: 0,
				error_message: "Authentication token expired",
				created: "2025-11-20T14:00:00Z",
				created_by: "Mike Johnson",
			},
		]

		// API Logs
		apiLogs.value = [
			{
				id: "log_001",
				integration_id: "int_001",
				endpoint: "/sobjects/Account/query",
				method: "GET",
				status_code: 200,
				response_time: 234,
				request_size: 1024,
				response_size: 15680,
				timestamp: "2025-11-25T10:45:30Z",
				user_agent: "MkaguziApp/1.0",
				ip_address: "192.168.1.100",
				success: true,
				error_message: null,
			},
			{
				id: "log_002",
				integration_id: "int_002",
				endpoint: "/api/v2/purchase-orders",
				method: "POST",
				status_code: 429,
				response_time: 1200,
				request_size: 2048,
				response_size: 512,
				timestamp: "2025-11-25T10:44:15Z",
				user_agent: "MkaguziApp/1.0",
				ip_address: "192.168.1.100",
				success: false,
				error_message: "Rate limit exceeded",
			},
			{
				id: "log_003",
				integration_id: "int_003",
				endpoint: "/v1.0/users",
				method: "GET",
				status_code: 200,
				response_time: 145,
				request_size: 512,
				response_size: 8920,
				timestamp: "2025-11-25T10:43:00Z",
				user_agent: "MkaguziApp/1.0",
				ip_address: "192.168.1.100",
				success: true,
				error_message: null,
			},
		]

		// Data Transformations
		transformations.value = [
			{
				id: "trans_001",
				integration_id: "int_001",
				name: "Salesforce Contact to User",
				description: "Transform Salesforce contacts to internal user format",
				source_format: "salesforce_contact",
				target_format: "mkaguzi_user",
				transformation_rules: [
					{
						source_field: "FirstName",
						target_field: "first_name",
						type: "direct_mapping",
					},
					{
						source_field: "LastName",
						target_field: "last_name",
						type: "direct_mapping",
					},
					{
						source_field: "Email",
						target_field: "email",
						type: "direct_mapping",
						validation: "email",
					},
					{
						source_field: "Account.Name",
						target_field: "company",
						type: "nested_mapping",
					},
				],
				status: "Active",
				created: "2025-11-15T11:00:00Z",
				created_by: "John Doe",
			},
			{
				id: "trans_002",
				integration_id: "int_002",
				name: "SAP Financial to Transaction",
				description: "Transform SAP financial records to audit transactions",
				source_format: "sap_financial",
				target_format: "mkaguzi_transaction",
				transformation_rules: [
					{
						source_field: "BUKRS",
						target_field: "company_code",
						type: "direct_mapping",
					},
					{
						source_field: "BELNR",
						target_field: "document_number",
						type: "direct_mapping",
					},
					{
						source_field: "WRBTR",
						target_field: "amount",
						type: "direct_mapping",
						validation: "numeric",
					},
					{
						source_field: "WAERS",
						target_field: "currency",
						type: "lookup",
						lookup_table: "currency_codes",
					},
				],
				status: "Active",
				created: "2025-11-10T17:00:00Z",
				created_by: "Jane Smith",
			},
		]

		// Auth Providers
		authProviders.value = [
			{
				id: "auth_001",
				name: "OAuth2 Provider",
				type: "OAuth2",
				configuration: {
					authorization_url: "https://oauth.provider.com/auth",
					token_url: "https://oauth.provider.com/token",
					scope: "read write",
					redirect_uri: "https://mkaguzi.app/oauth/callback",
				},
				active_tokens: 15,
				created: "2025-11-15T08:00:00Z",
			},
			{
				id: "auth_002",
				name: "API Key Provider",
				type: "API_Key",
				configuration: {
					header_name: "X-API-Key",
					key_location: "header",
				},
				active_tokens: 8,
				created: "2025-11-10T12:00:00Z",
			},
		]
	}

	// Initialize sample data on store creation
	initializeSampleData()

	// Computed properties
	const activeIntegrations = computed(() =>
		integrations.value.filter((integration) => integration.status === "Active"),
	)

	const healthyIntegrations = computed(() =>
		integrations.value.filter(
			(integration) => integration.health_status === "Healthy",
		),
	)

	const runningJobs = computed(() =>
		syncJobs.value.filter((job) => job.status === "Running"),
	)

	const activeWebhooks = computed(() =>
		webhooks.value.filter((webhook) => webhook.status === "Active"),
	)

	const recentLogs = computed(() =>
		[...apiLogs.value]
			.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
			.slice(0, 50),
	)

	const integrationStats = computed(() => {
		const total = integrations.value.length
		const active = activeIntegrations.value.length
		const healthy = healthyIntegrations.value.length
		const warning = integrations.value.filter(
			(i) => i.health_status === "Warning",
		).length
		const failed = integrations.value.filter(
			(i) => i.health_status === "Error" || i.health_status === "Disconnected",
		).length

		return {
			total,
			active,
			healthy,
			warning,
			failed,
			uptime: total > 0 ? Math.round((healthy / total) * 100) : 0,
		}
	})

	const syncStats = computed(() => {
		const total = syncJobs.value.length
		const running = runningJobs.value.length
		const completed = syncJobs.value.filter(
			(job) => job.status === "Completed",
		).length
		const failed = syncJobs.value.filter(
			(job) => job.status === "Failed",
		).length
		const scheduled = syncJobs.value.filter(
			(job) => job.type === "Scheduled",
		).length

		return {
			total,
			running,
			completed,
			failed,
			scheduled,
		}
	})

	const webhookStats = computed(() => {
		const total = webhooks.value.length
		const active = activeWebhooks.value.length
		const paused = webhooks.value.filter((wh) => wh.status === "Paused").length
		const totalDeliveries = webhooks.value.reduce(
			(sum, wh) => sum + wh.total_deliveries,
			0,
		)
		const successfulDeliveries = webhooks.value.reduce(
			(sum, wh) => sum + wh.successful_deliveries,
			0,
		)
		const successRate =
			totalDeliveries > 0
				? Math.round((successfulDeliveries / totalDeliveries) * 100)
				: 0

		return {
			total,
			active,
			paused,
			totalDeliveries,
			successfulDeliveries,
			successRate,
		}
	})

	// Actions - Integration Management
	const loadIntegrations = async () => {
		loading.value = true
		error.value = null

		try {
			// Simulate API call
			await new Promise((resolve) => setTimeout(resolve, 1000))
			// In a real app, this would fetch from the API
			console.log("Integrations loaded:", integrations.value.length)
		} catch (err) {
			error.value = err.message
		} finally {
			loading.value = false
		}
	}

	const createIntegration = async (integrationData) => {
		loading.value = true
		error.value = null

		try {
			const newIntegration = {
				id: `int_${Date.now()}`,
				...integrationData,
				status: "Inactive",
				health_status: "Unknown",
				created: new Date().toISOString(),
				metadata: {
					total_requests: 0,
					successful_requests: 0,
					failed_requests: 0,
					avg_response_time: 0,
					last_error: null,
					uptime_percentage: 0,
				},
			}

			integrations.value.push(newIntegration)
			return newIntegration
		} catch (err) {
			error.value = err.message
			throw err
		} finally {
			loading.value = false
		}
	}

	const updateIntegration = async (integrationId, updates) => {
		const index = integrations.value.findIndex((i) => i.id === integrationId)
		if (index !== -1) {
			integrations.value[index] = { ...integrations.value[index], ...updates }
		}
	}

	const deleteIntegration = async (integrationId) => {
		const index = integrations.value.findIndex((i) => i.id === integrationId)
		if (index !== -1) {
			integrations.value.splice(index, 1)

			// Also remove related connections, webhooks, etc.
			connections.value = connections.value.filter(
				(c) => c.integration_id !== integrationId,
			)
			webhooks.value = webhooks.value.filter(
				(w) => w.integration_id !== integrationId,
			)
			syncJobs.value = syncJobs.value.filter(
				(j) => j.integration_id !== integrationId,
			)
		}
	}

	const testConnection = async (connectionId) => {
		const connection = connections.value.find((c) => c.id === connectionId)
		if (connection) {
			// Simulate connection test
			await new Promise((resolve) => setTimeout(resolve, 2000))

			const success = Math.random() > 0.3 // 70% success rate
			connection.last_tested = new Date().toISOString()
			connection.test_status = success ? "Success" : "Failed"

			return success
		}
		return false
	}

	// Actions - Webhook Management
	const createWebhook = async (webhookData) => {
		const newWebhook = {
			id: `wh_${Date.now()}`,
			...webhookData,
			total_deliveries: 0,
			successful_deliveries: 0,
			failed_deliveries: 0,
			created: new Date().toISOString(),
		}

		webhooks.value.push(newWebhook)
		return newWebhook
	}

	const updateWebhook = async (webhookId, updates) => {
		const index = webhooks.value.findIndex((w) => w.id === webhookId)
		if (index !== -1) {
			webhooks.value[index] = { ...webhooks.value[index], ...updates }
		}
	}

	const deleteWebhook = async (webhookId) => {
		const index = webhooks.value.findIndex((w) => w.id === webhookId)
		if (index !== -1) {
			webhooks.value.splice(index, 1)
		}
	}

	const testWebhook = async (webhookId) => {
		const webhook = webhooks.value.find((w) => w.id === webhookId)
		if (webhook) {
			// Simulate webhook test
			await new Promise((resolve) => setTimeout(resolve, 1500))

			const success = Math.random() > 0.2 // 80% success rate
			webhook.last_triggered = new Date().toISOString()

			if (success) {
				webhook.successful_deliveries += 1
			} else {
				webhook.failed_deliveries += 1
			}
			webhook.total_deliveries += 1

			return success
		}
		return false
	}

	// Actions - Sync Job Management
	const createSyncJob = async (jobData) => {
		const newJob = {
			id: `job_${Date.now()}`,
			...jobData,
			status: "Pending",
			records_processed: 0,
			records_created: 0,
			records_updated: 0,
			records_failed: 0,
			success_rate: 0,
			created: new Date().toISOString(),
		}

		syncJobs.value.push(newJob)
		return newJob
	}

	const runSyncJob = async (jobId) => {
		const job = syncJobs.value.find((j) => j.id === jobId)
		if (job) {
			job.status = "Running"
			job.last_run = new Date().toISOString()

			// Simulate job execution
			await new Promise((resolve) => setTimeout(resolve, 3000))

			const success = Math.random() > 0.2 // 80% success rate

			if (success) {
				job.status = "Completed"
				job.records_processed = Math.floor(Math.random() * 1000) + 100
				job.records_created = Math.floor(Math.random() * 50)
				job.records_updated = Math.floor(Math.random() * 200)
				job.records_failed = Math.floor(Math.random() * 10)
				job.success_rate = Math.round(
					((job.records_processed - job.records_failed) /
						job.records_processed) *
						100,
				)
			} else {
				job.status = "Failed"
				job.error_message = "Connection timeout occurred"
			}

			// Set next run time if scheduled
			if (job.type === "Scheduled" && job.schedule) {
				// Simple next run calculation (in real app, use cron parser)
				job.next_run = new Date(Date.now() + 60 * 60 * 1000).toISOString() // 1 hour from now
			}

			return success
		}
		return false
	}

	const pauseSyncJob = async (jobId) => {
		const job = syncJobs.value.find((j) => j.id === jobId)
		if (job) {
			job.status = "Paused"
			job.next_run = null
		}
	}

	const resumeSyncJob = async (jobId) => {
		const job = syncJobs.value.find((j) => j.id === jobId)
		if (job) {
			job.status = "Scheduled"
			if (job.schedule) {
				job.next_run = new Date(Date.now() + 60 * 60 * 1000).toISOString()
			}
		}
	}

	// Actions - Data Transformation
	const createTransformation = async (transformationData) => {
		const newTransformation = {
			id: `trans_${Date.now()}`,
			...transformationData,
			status: "Active",
			created: new Date().toISOString(),
		}

		transformations.value.push(newTransformation)
		return newTransformation
	}

	const testTransformation = async (transformationId, sampleData) => {
		const transformation = transformations.value.find(
			(t) => t.id === transformationId,
		)
		if (transformation) {
			// Simulate transformation test
			await new Promise((resolve) => setTimeout(resolve, 1000))

			const result = {
				success: Math.random() > 0.1, // 90% success rate
				transformed_data: {
					// Mock transformed data based on rules
					...sampleData,
					transformed: true,
					transformation_id: transformationId,
				},
				validation_errors: [],
			}

			return result
		}
		return null
	}

	// Actions - API Logs
	const getApiLogs = (filters = {}) => {
		let logs = [...apiLogs.value]

		if (filters.integration_id) {
			logs = logs.filter((log) => log.integration_id === filters.integration_id)
		}

		if (filters.status_code) {
			logs = logs.filter((log) => log.status_code === filters.status_code)
		}

		if (filters.start_date) {
			logs = logs.filter(
				(log) => new Date(log.timestamp) >= new Date(filters.start_date),
			)
		}

		if (filters.end_date) {
			logs = logs.filter(
				(log) => new Date(log.timestamp) <= new Date(filters.end_date),
			)
		}

		return logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
	}

	const clearApiLogs = (integrationId = null) => {
		if (integrationId) {
			apiLogs.value = apiLogs.value.filter(
				(log) => log.integration_id !== integrationId,
			)
		} else {
			apiLogs.value = []
		}
	}

	// Actions - Rate Limiting
	const checkRateLimit = (integrationId) => {
		const integration = integrations.value.find((i) => i.id === integrationId)
		if (integration) {
			// Simple rate limiting check
			const now = Date.now()
			const periodMs =
				integration.rate_period === "hour" ? 60 * 60 * 1000 : 60 * 1000
			const recentLogs = apiLogs.value.filter(
				(log) =>
					log.integration_id === integrationId &&
					now - new Date(log.timestamp).getTime() < periodMs,
			)

			return {
				current: recentLogs.length,
				limit: integration.rate_limit,
				remaining: Math.max(0, integration.rate_limit - recentLogs.length),
				reset_at: new Date(now + periodMs).toISOString(),
			}
		}
		return null
	}

	// Utility functions
	const getIntegrationById = (id) => integrations.value.find((i) => i.id === id)
	const getConnectionById = (id) => connections.value.find((c) => c.id === id)
	const getWebhookById = (id) => webhooks.value.find((w) => w.id === id)
	const getSyncJobById = (id) => syncJobs.value.find((j) => j.id === id)
	const getTransformationById = (id) =>
		transformations.value.find((t) => t.id === id)

	return {
		// State
		integrations,
		connections,
		webhooks,
		syncJobs,
		apiLogs,
		transformations,
		endpoints,
		authProviders,
		rateLimits,
		loading,
		error,

		// Computed
		activeIntegrations,
		healthyIntegrations,
		runningJobs,
		activeWebhooks,
		recentLogs,
		integrationStats,
		syncStats,
		webhookStats,

		// Actions
		loadIntegrations,
		createIntegration,
		updateIntegration,
		deleteIntegration,
		testConnection,
		createWebhook,
		updateWebhook,
		deleteWebhook,
		testWebhook,
		createSyncJob,
		runSyncJob,
		pauseSyncJob,
		resumeSyncJob,
		createTransformation,
		testTransformation,
		getApiLogs,
		clearApiLogs,
		checkRateLimit,

		// Utilities
		getIntegrationById,
		getConnectionById,
		getWebhookById,
		getSyncJobById,
		getTransformationById,
	}
})
