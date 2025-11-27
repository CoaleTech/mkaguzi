<template>
  <div class="integration-settings">
    <!-- Header -->
    <div class="settings-header">
      <div class="header-left">
        <h3>Integration Settings</h3>
        <p>Configure global settings and preferences for API integrations</p>
      </div>
      
      <div class="header-actions">
        <Button variant="outline" @click="resetToDefaults">
          <RotateCcw class="w-4 h-4 mr-2" />
          Reset to Defaults
        </Button>
        
        <Button variant="solid" @click="saveSettings" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          Save Settings
        </Button>
      </div>
    </div>

    <!-- Settings Navigation -->
    <div class="settings-navigation">
      <div class="nav-list">
        <button
          v-for="section in settingsSections"
          :key="section.id"
          class="nav-button"
          :class="{ 'active': activeSection === section.id }"
          @click="activeSection = section.id"
        >
          <component :is="section.icon" class="w-4 h-4" />
          {{ section.label }}
        </button>
      </div>
    </div>

    <!-- Settings Content -->
    <div class="settings-content">
      <!-- General Settings -->
      <div v-if="activeSection === 'general'" class="settings-section">
        <div class="section-header">
          <h4>General Settings</h4>
          <p>Basic configuration options for API integrations</p>
        </div>
        
        <div class="settings-form">
          <div class="form-group">
            <label class="form-label">Default Timeout (seconds)</label>
            <FormControl
              type="number"
              v-model="settings.general.default_timeout"
              placeholder="30"
              class="form-input"
            />
            <div class="form-hint">
              Default timeout for API requests. Set to 0 for no timeout.
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Max Concurrent Requests</label>
            <FormControl
              type="number"
              v-model="settings.general.max_concurrent_requests"
              placeholder="10"
              class="form-input"
            />
            <div class="form-hint">
              Maximum number of concurrent API requests per integration.
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Request Queue Size</label>
            <FormControl
              type="number"
              v-model="settings.general.queue_size"
              placeholder="100"
              class="form-input"
            />
            <div class="form-hint">
              Maximum number of requests that can be queued per integration.
            </div>
          </div>
          
          <div class="form-group checkbox-group">
            <Checkbox
              v-model="settings.general.enable_request_logging"
              label="Enable Request Logging"
            />
            <div class="form-hint">
              Log all API requests and responses for debugging purposes.
            </div>
          </div>
          
          <div class="form-group checkbox-group">
            <Checkbox
              v-model="settings.general.enable_caching"
              label="Enable Response Caching"
            />
            <div class="form-hint">
              Cache API responses to improve performance and reduce API calls.
            </div>
          </div>
          
          <div v-if="settings.general.enable_caching" class="form-group">
            <label class="form-label">Cache TTL (seconds)</label>
            <FormControl
              type="number"
              v-model="settings.general.cache_ttl"
              placeholder="3600"
              class="form-input"
            />
            <div class="form-hint">
              Time-to-live for cached responses in seconds.
            </div>
          </div>
        </div>
      </div>

      <!-- Rate Limiting Settings -->
      <div v-else-if="activeSection === 'rate-limiting'" class="settings-section">
        <div class="section-header">
          <h4>Rate Limiting</h4>
          <p>Configure rate limiting and throttling for API integrations</p>
        </div>
        
        <div class="settings-form">
          <div class="form-group checkbox-group">
            <Checkbox
              v-model="settings.rate_limiting.enable_global_rate_limiting"
              label="Enable Global Rate Limiting"
            />
            <div class="form-hint">
              Apply rate limiting across all integrations globally.
            </div>
          </div>
          
          <div v-if="settings.rate_limiting.enable_global_rate_limiting" class="rate-limiting-config">
            <div class="form-group">
              <label class="form-label">Global Rate Limit</label>
              <div class="rate-limit-input">
                <FormControl
                  type="number"
                  v-model="settings.rate_limiting.global_requests_per_minute"
                  placeholder="1000"
                  class="form-input"
                />
                <span class="rate-limit-unit">requests per minute</span>
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">Burst Limit</label>
              <FormControl
                type="number"
                v-model="settings.rate_limiting.burst_limit"
                placeholder="100"
                class="form-input"
              />
              <div class="form-hint">
                Maximum number of requests allowed in a burst.
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Rate Limit Strategy</label>
            <Dropdown :options="rateLimitStrategies" @click="handleRateLimitStrategy">
              <template #default>
                <Button variant="outline" class="w-full justify-between">
                  {{ settings.rate_limiting.strategy || 'Select Strategy' }}
                  <ChevronDown class="w-4 h-4" />
                </Button>
              </template>
            </Dropdown>
            <div class="form-hint">
              Choose how to handle requests that exceed rate limits.
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Retry Configuration</label>
            <div class="retry-config">
              <div class="retry-item">
                <label>Max Retries</label>
                <FormControl
                  type="number"
                  v-model="settings.rate_limiting.max_retries"
                  placeholder="3"
                  class="form-input small"
                />
              </div>
              <div class="retry-item">
                <label>Retry Delay (ms)</label>
                <FormControl
                  type="number"
                  v-model="settings.rate_limiting.retry_delay"
                  placeholder="1000"
                  class="form-input small"
                />
              </div>
              <div class="retry-item">
                <label>Backoff Multiplier</label>
                <FormControl
                  type="number"
                  v-model="settings.rate_limiting.backoff_multiplier"
                  placeholder="2"
                  class="form-input small"
                  step="0.1"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Security Settings -->
      <div v-else-if="activeSection === 'security'" class="settings-section">
        <div class="section-header">
          <h4>Security Settings</h4>
          <p>Configure security and authentication options</p>
        </div>
        
        <div class="settings-form">
          <div class="form-group checkbox-group">
            <Checkbox
              v-model="settings.security.enforce_https"
              label="Enforce HTTPS"
            />
            <div class="form-hint">
              Only allow HTTPS connections for all integrations.
            </div>
          </div>
          
          <div class="form-group checkbox-group">
            <Checkbox
              v-model="settings.security.verify_ssl_certificates"
              label="Verify SSL Certificates"
            />
            <div class="form-hint">
              Verify SSL certificates for all HTTPS connections.
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Allowed IP Ranges</label>
            <textarea
              v-model="settings.security.allowed_ip_ranges"
              class="form-textarea"
              placeholder="192.168.1.0/24&#10;10.0.0.0/8"
              rows="4"
            ></textarea>
            <div class="form-hint">
              Comma-separated list of IP ranges allowed to access integrations. Leave empty to allow all IPs.
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">API Key Encryption</label>
            <Dropdown :options="encryptionOptions" @click="handleEncryptionOption">
              <template #default>
                <Button variant="outline" class="w-full justify-between">
                  {{ settings.security.encryption_method || 'Select Method' }}
                  <ChevronDown class="w-4 h-4" />
                </Button>
              </template>
            </Dropdown>
            <div class="form-hint">
              Encryption method for storing API keys and secrets.
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Session Timeout (minutes)</label>
            <FormControl
              type="number"
              v-model="settings.security.session_timeout"
              placeholder="60"
              class="form-input"
            />
            <div class="form-hint">
              Automatic logout time for integration sessions.
            </div>
          </div>
          
          <div class="form-group checkbox-group">
            <Checkbox
              v-model="settings.security.enable_audit_logging"
              label="Enable Audit Logging"
            />
            <div class="form-hint">
              Log all security-related events and authentication attempts.
            </div>
          </div>
        </div>
      </div>

      <!-- Monitoring Settings -->
      <div v-else-if="activeSection === 'monitoring'" class="settings-section">
        <div class="section-header">
          <h4>Monitoring & Alerts</h4>
          <p>Configure monitoring thresholds and alert preferences</p>
        </div>
        
        <div class="settings-form">
          <div class="form-group checkbox-group">
            <Checkbox
              v-model="settings.monitoring.enable_health_checks"
              label="Enable Health Checks"
            />
            <div class="form-hint">
              Automatically check the health of all integrations.
            </div>
          </div>
          
          <div v-if="settings.monitoring.enable_health_checks" class="health-check-config">
            <div class="form-group">
              <label class="form-label">Health Check Interval (minutes)</label>
              <FormControl
                type="number"
                v-model="settings.monitoring.health_check_interval"
                placeholder="5"
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">Health Check Timeout (seconds)</label>
              <FormControl
                type="number"
                v-model="settings.monitoring.health_check_timeout"
                placeholder="10"
                class="form-input"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Alert Thresholds</label>
            <div class="threshold-config">
              <div class="threshold-item">
                <label>Error Rate (%)</label>
                <FormControl
                  type="number"
                  v-model="settings.monitoring.error_rate_threshold"
                  placeholder="5"
                  class="form-input small"
                  step="0.1"
                />
              </div>
              <div class="threshold-item">
                <label>Response Time (ms)</label>
                <FormControl
                  type="number"
                  v-model="settings.monitoring.response_time_threshold"
                  placeholder="5000"
                  class="form-input small"
                />
              </div>
              <div class="threshold-item">
                <label>Uptime (%)</label>
                <FormControl
                  type="number"
                  v-model="settings.monitoring.uptime_threshold"
                  placeholder="99"
                  class="form-input small"
                  step="0.1"
                />
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Notification Channels</label>
            <div class="notification-channels">
              <div class="channel-item">
                <Checkbox
                  v-model="settings.monitoring.notifications.email.enabled"
                  label="Email"
                />
                <FormControl
                  v-if="settings.monitoring.notifications.email.enabled"
                  type="email"
                  v-model="settings.monitoring.notifications.email.recipients"
                  placeholder="admin@example.com"
                  class="form-input"
                />
              </div>
              
              <div class="channel-item">
                <Checkbox
                  v-model="settings.monitoring.notifications.webhook.enabled"
                  label="Webhook"
                />
                <FormControl
                  v-if="settings.monitoring.notifications.webhook.enabled"
                  type="url"
                  v-model="settings.monitoring.notifications.webhook.url"
                  placeholder="https://hooks.slack.com/..."
                  class="form-input"
                />
              </div>
              
              <div class="channel-item">
                <Checkbox
                  v-model="settings.monitoring.notifications.sms.enabled"
                  label="SMS"
                />
                <FormControl
                  v-if="settings.monitoring.notifications.sms.enabled"
                  type="tel"
                  v-model="settings.monitoring.notifications.sms.number"
                  placeholder="+1234567890"
                  class="form-input"
                />
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Retention Policy</label>
            <div class="retention-config">
              <div class="retention-item">
                <label>Logs Retention (days)</label>
                <FormControl
                  type="number"
                  v-model="settings.monitoring.retention.logs_days"
                  placeholder="30"
                  class="form-input small"
                />
              </div>
              <div class="retention-item">
                <label>Metrics Retention (days)</label>
                <FormControl
                  type="number"
                  v-model="settings.monitoring.retention.metrics_days"
                  placeholder="90"
                  class="form-input small"
                />
              </div>
              <div class="retention-item">
                <label>Events Retention (days)</label>
                <FormControl
                  type="number"
                  v-model="settings.monitoring.retention.events_days"
                  placeholder="180"
                  class="form-input small"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Data Settings -->
      <div v-else-if="activeSection === 'data'" class="settings-section">
        <div class="section-header">
          <h4>Data Management</h4>
          <p>Configure data processing and storage options</p>
        </div>
        
        <div class="settings-form">
          <div class="form-group">
            <label class="form-label">Default Data Format</label>
            <Dropdown :options="dataFormats" @click="handleDataFormat">
              <template #default>
                <Button variant="outline" class="w-full justify-between">
                  {{ settings.data.default_format || 'Select Format' }}
                  <ChevronDown class="w-4 h-4" />
                </Button>
              </template>
            </Dropdown>
          </div>
          
          <div class="form-group">
            <label class="form-label">Batch Size</label>
            <FormControl
              type="number"
              v-model="settings.data.batch_size"
              placeholder="100"
              class="form-input"
            />
            <div class="form-hint">
              Number of records to process in each batch operation.
            </div>
          </div>
          
          <div class="form-group checkbox-group">
            <Checkbox
              v-model="settings.data.enable_compression"
              label="Enable Data Compression"
            />
            <div class="form-hint">
              Compress data during transfer and storage.
            </div>
          </div>
          
          <div class="form-group checkbox-group">
            <Checkbox
              v-model="settings.data.enable_encryption"
              label="Enable Data Encryption"
            />
            <div class="form-hint">
              Encrypt sensitive data at rest and in transit.
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Data Validation Rules</label>
            <div class="validation-rules">
              <div class="rule-item">
                <Checkbox
                  v-model="settings.data.validation.required_fields"
                  label="Enforce Required Fields"
                />
              </div>
              <div class="rule-item">
                <Checkbox
                  v-model="settings.data.validation.data_types"
                  label="Validate Data Types"
                />
              </div>
              <div class="rule-item">
                <Checkbox
                  v-model="settings.data.validation.format_validation"
                  label="Format Validation"
                />
              </div>
              <div class="rule-item">
                <Checkbox
                  v-model="settings.data.validation.custom_rules"
                  label="Custom Validation Rules"
                />
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Error Handling Strategy</label>
            <Dropdown :options="errorHandlingStrategies" @click="handleErrorStrategy">
              <template #default>
                <Button variant="outline" class="w-full justify-between">
                  {{ settings.data.error_handling || 'Select Strategy' }}
                  <ChevronDown class="w-4 h-4" />
                </Button>
              </template>
            </Dropdown>
          </div>
        </div>
      </div>

      <!-- Advanced Settings -->
      <div v-else-if="activeSection === 'advanced'" class="settings-section">
        <div class="section-header">
          <h4>Advanced Settings</h4>
          <p>Advanced configuration options for power users</p>
        </div>
        
        <div class="settings-form">
          <div class="form-group">
            <label class="form-label">Custom Headers</label>
            <div class="headers-config">
              <div
                v-for="(header, index) in settings.advanced.custom_headers"
                :key="index"
                class="header-item"
              >
                <FormControl
                  type="text"
                  v-model="header.name"
                  placeholder="Header Name"
                  class="form-input"
                />
                <FormControl
                  type="text"
                  v-model="header.value"
                  placeholder="Header Value"
                  class="form-input"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  @click="removeHeader(index)"
                >
                  <X class="w-3 h-3" />
                </Button>
              </div>
              <Button
                variant="ghost"
                size="sm"
                @click="addHeader"
              >
                <Plus class="w-3 h-3 mr-1" />
                Add Header
              </Button>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Environment Variables</label>
            <textarea
              v-model="settings.advanced.environment_variables"
              class="form-textarea"
              placeholder="API_BASE_URL=https://api.example.com&#10;DEBUG_MODE=true"
              rows="6"
            ></textarea>
            <div class="form-hint">
              Key-value pairs for environment variables (one per line).
            </div>
          </div>
          
          <div class="form-group checkbox-group">
            <Checkbox
              v-model="settings.advanced.enable_debug_mode"
              label="Enable Debug Mode"
            />
            <div class="form-hint">
              Enable detailed logging and debugging features.
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Connection Pool Size</label>
            <FormControl
              type="number"
              v-model="settings.advanced.connection_pool_size"
              placeholder="20"
              class="form-input"
            />
            <div class="form-hint">
              Maximum number of connections in the connection pool.
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Custom Scripts</label>
            <textarea
              v-model="settings.advanced.custom_scripts"
              class="form-textarea"
              placeholder="// Custom initialization scripts"
              rows="8"
            ></textarea>
            <div class="form-hint">
              JavaScript code to run during integration initialization.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Actions -->
    <div class="settings-actions">
      <div class="actions-left">
        <Button
          variant="ghost"
          @click="exportSettings"
        >
          <Download class="w-3 h-3 mr-1" />
          Export Settings
        </Button>
        
        <Button
          variant="ghost"
          @click="importSettings"
        >
          <Upload class="w-3 h-3 mr-1" />
          Import Settings
        </Button>
      </div>
      
      <div class="actions-right">
        <Button
          variant="outline"
          @click="resetSettings"
        >
          Cancel
        </Button>
        
        <Button
          variant="solid"
          @click="saveSettings"
          :loading="saving"
        >
          Save Settings
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Checkbox, Dropdown, FormControl } from "frappe-ui"
import {
	Activity,
	ChevronDown,
	Database,
	Download,
	Plus,
	RotateCcw,
	Save,
	Settings,
	Shield,
	Sliders,
	Upload,
	X,
} from "lucide-vue-next"
import { reactive, ref } from "vue"

const props = defineProps({
	initialSettings: {
		type: Object,
		default: () => ({}),
	},
})

const emit = defineEmits(["save", "reset", "export", "import"])

// Local state
const activeSection = ref("general")
const saving = ref(false)

// Settings sections
const settingsSections = [
	{ id: "general", label: "General", icon: Settings },
	{ id: "rate-limiting", label: "Rate Limiting", icon: Sliders },
	{ id: "security", label: "Security", icon: Shield },
	{ id: "monitoring", label: "Monitoring", icon: Activity },
	{ id: "data", label: "Data", icon: Database },
	{ id: "advanced", label: "Advanced", icon: Settings },
]

// Settings data structure
const settings = reactive({
	general: {
		default_timeout: 30,
		max_concurrent_requests: 10,
		queue_size: 100,
		enable_request_logging: true,
		enable_caching: false,
		cache_ttl: 3600,
	},
	rate_limiting: {
		enable_global_rate_limiting: false,
		global_requests_per_minute: 1000,
		burst_limit: 100,
		strategy: "Queue",
		max_retries: 3,
		retry_delay: 1000,
		backoff_multiplier: 2,
	},
	security: {
		enforce_https: true,
		verify_ssl_certificates: true,
		allowed_ip_ranges: "",
		encryption_method: "AES-256",
		session_timeout: 60,
		enable_audit_logging: true,
	},
	monitoring: {
		enable_health_checks: true,
		health_check_interval: 5,
		health_check_timeout: 10,
		error_rate_threshold: 5.0,
		response_time_threshold: 5000,
		uptime_threshold: 99.0,
		notifications: {
			email: {
				enabled: true,
				recipients: "",
			},
			webhook: {
				enabled: false,
				url: "",
			},
			sms: {
				enabled: false,
				number: "",
			},
		},
		retention: {
			logs_days: 30,
			metrics_days: 90,
			events_days: 180,
		},
	},
	data: {
		default_format: "JSON",
		batch_size: 100,
		enable_compression: true,
		enable_encryption: true,
		validation: {
			required_fields: true,
			data_types: true,
			format_validation: true,
			custom_rules: false,
		},
		error_handling: "Skip and Log",
	},
	advanced: {
		custom_headers: [],
		environment_variables: "",
		enable_debug_mode: false,
		connection_pool_size: 20,
		custom_scripts: "",
	},
})

// Dropdown options
const rateLimitStrategies = [
	{ label: "Queue", value: "Queue" },
	{ label: "Reject", value: "Reject" },
	{ label: "Throttle", value: "Throttle" },
]

const encryptionOptions = [
	{ label: "AES-256", value: "AES-256" },
	{ label: "AES-128", value: "AES-128" },
	{ label: "RSA", value: "RSA" },
]

const dataFormats = [
	{ label: "JSON", value: "JSON" },
	{ label: "XML", value: "XML" },
	{ label: "CSV", value: "CSV" },
	{ label: "YAML", value: "YAML" },
]

const errorHandlingStrategies = [
	{ label: "Skip and Log", value: "Skip and Log" },
	{ label: "Stop on Error", value: "Stop on Error" },
	{ label: "Retry with Fallback", value: "Retry with Fallback" },
]

// Methods
const saveSettings = async () => {
	saving.value = true
	try {
		await new Promise((resolve) => setTimeout(resolve, 1000))
		emit("save", settings)
	} finally {
		saving.value = false
	}
}

const resetToDefaults = () => {
	emit("reset")
}

const resetSettings = () => {
	// Reset to initial settings
	Object.assign(settings, props.initialSettings)
}

const exportSettings = () => {
	emit("export", settings)
}

const importSettings = () => {
	emit("import")
}

const handleRateLimitStrategy = (option) => {
	settings.rate_limiting.strategy = option.value
}

const handleEncryptionOption = (option) => {
	settings.security.encryption_method = option.value
}

const handleDataFormat = (option) => {
	settings.data.default_format = option.value
}

const handleErrorStrategy = (option) => {
	settings.data.error_handling = option.value
}

const addHeader = () => {
	settings.advanced.custom_headers.push({
		name: "",
		value: "",
	})
}

const removeHeader = (index) => {
	settings.advanced.custom_headers.splice(index, 1)
}

// Initialize settings with props
if (props.initialSettings) {
	Object.assign(settings, props.initialSettings)
}
</script>

<style scoped>
.integration-settings {
  padding: 0;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.header-left h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.header-left p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Settings Navigation */
.settings-navigation {
  margin-bottom: 2rem;
}

.nav-list {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  color: var(--text-muted);
  font-weight: 500;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-button:hover {
  color: var(--text-color);
}

.nav-button.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

/* Settings Content */
.settings-content {
  min-height: 500px;
}

.settings-section {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 2rem;
}

.section-header {
  margin-bottom: 2rem;
}

.section-header h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.section-header p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.875rem;
}

/* Settings Form */
.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group.checkbox-group {
  flex-direction: row;
  align-items: flex-start;
  gap: 0.75rem;
}

.form-group.checkbox-group .form-hint {
  margin-left: auto;
  max-width: 300px;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
}

.form-input {
  max-width: 400px;
}

.form-input.small {
  max-width: 150px;
}

.form-textarea {
  width: 100%;
  max-width: 600px;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  font-family: monospace;
  font-size: 0.875rem;
  resize: vertical;
}

.form-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.4;
}

/* Specialized Form Sections */
.rate-limiting-config,
.health-check-config {
  margin-left: 1rem;
  padding-left: 1rem;
  border-left: 2px solid var(--border-color);
  margin-top: 1rem;
}

.rate-limit-input {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rate-limit-unit {
  font-size: 0.875rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.retry-config,
.threshold-config,
.retention-config {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.retry-item,
.threshold-item,
.retention-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.retry-item label,
.threshold-item label,
.retention-item label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
}

.notification-channels {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 0.375rem;
}

.validation-rules {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.rule-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.headers-config {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 600px;
}

.header-item {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.header-item .form-input {
  flex: 1;
  max-width: none;
}

/* Settings Actions */
.settings-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  margin-top: 2rem;
}

.actions-left,
.actions-right {
  display: flex;
  gap: 0.75rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .settings-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .nav-list {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .nav-button {
    flex-shrink: 0;
    padding: 0.75rem 1rem;
  }
  
  .retry-config,
  .threshold-config,
  .retention-config {
    grid-template-columns: 1fr;
  }
  
  .settings-section {
    padding: 1.5rem;
  }
}

@media (max-width: 768px) {
  .form-group.checkbox-group {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .form-group.checkbox-group .form-hint {
    margin-left: 0;
    max-width: none;
  }
  
  .channel-item {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .header-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .rate-limit-input {
    flex-direction: column;
    align-items: stretch;
  }
  
  .settings-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .actions-left,
  .actions-right {
    justify-content: center;
  }
  
  .validation-rules {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .settings-section {
    padding: 1rem;
  }
  
  .form-input,
  .form-textarea {
    max-width: none;
  }
  
  .section-header {
    margin-bottom: 1.5rem;
  }
  
  .settings-form {
    gap: 1rem;
  }
}
</style>