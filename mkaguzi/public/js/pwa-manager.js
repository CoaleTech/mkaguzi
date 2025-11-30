/**
 * PWA Registration and AI Service Worker Management
 * Handles service worker registration, update management, and AI capabilities initialization
 */

class PWAManager {
  constructor() {
    this.serviceWorkerRegistration = null
    this.updateAvailable = false
    this.isOfflineReady = false
    this.aiCapabilities = {
      modelsLoaded: false,
      offlineInferenceReady: false,
      federatedSyncActive: false
    }
    
    this.initialize()
  }

  async initialize() {
    // Check PWA support
    if (!this.isPWASupported()) {
      console.warn('PWA features not fully supported in this browser')
      return
    }

    // Register service worker
    await this.registerServiceWorker()
    
    // Setup PWA event listeners
    this.setupEventListeners()
    
    // Initialize AI capabilities
    await this.initializeAICapabilities()
    
    // Setup periodic health checks
    this.startHealthMonitoring()
    
    console.log('PWA Manager initialized successfully')
  }

  isPWASupported() {
    return (
      'serviceWorker' in navigator &&
      'caches' in window &&
      'indexedDB' in window &&
      'fetch' in window
    )
  }

  async registerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
      console.warn('Service workers are not supported')
      return
    }

    try {
      const registration = await navigator.serviceWorker.register(
        '/assets/mkaguzi/js/workers/ai-service-worker.js',
        {
          scope: '/app/',
          updateViaCache: 'imports'
        }
      )

      this.serviceWorkerRegistration = registration
      console.log('AI Service Worker registered successfully')

      // Handle service worker updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed') {
              if (navigator.serviceWorker.controller) {
                // New update available
                this.updateAvailable = true
                this.notifyUpdateAvailable()
              } else {
                // Content is cached for the first time
                this.isOfflineReady = true
                this.notifyOfflineReady()
              }
            }
          })
        }
      })

      // Handle service worker messages
      navigator.serviceWorker.addEventListener('message', this.handleServiceWorkerMessage.bind(this))

      // Check for existing controller
      if (navigator.serviceWorker.controller) {
        console.log('Service worker is already controlling this page')
      }

      return registration
    } catch (error) {
      console.error('Service worker registration failed:', error)
      throw error
    }
  }

  setupEventListeners() {
    // Online/Offline status
    window.addEventListener('online', () => {
      this.handleOnlineStatusChange(true)
    })

    window.addEventListener('offline', () => {
      this.handleOnlineStatusChange(false)
    })

    // App installation
    window.addEventListener('beforeinstallprompt', (event) => {
      event.preventDefault()
      this.showInstallPrompt(event)
    })

    // App installed
    window.addEventListener('appinstalled', () => {
      console.log('PWA was installed successfully')
      this.trackEvent('pwa_installed')
    })

    // Visibility change for background sync
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && navigator.onLine) {
        this.triggerSync()
      }
    })
  }

  async initializeAICapabilities() {
    try {
      // Check AI model cache status
      const modelStatus = await this.checkAIModelStatus()
      console.log('AI Model Status:', modelStatus)

      // Initialize federated learning client
      await this.initializeFederatedLearning()

      // Preload critical AI models for offline use
      await this.preloadCriticalModels()

      this.aiCapabilities.offlineInferenceReady = true
      this.notifyAICapabilitiesReady()

    } catch (error) {
      console.error('Failed to initialize AI capabilities:', error)
    }
  }

  async checkAIModelStatus() {
    try {
      const response = await fetch('/api/method/mkaguzi.chat_system.api.models.get_status')
      return await response.json()
    } catch (error) {
      console.error('Failed to check AI model status:', error)
      return { models_available: false, error: error.message }
    }
  }

  async initializeFederatedLearning() {
    // Send initialization message to service worker
    if (this.serviceWorkerRegistration && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: 'INIT_FEDERATED_LEARNING',
        clientId: this.getClientId(),
        capabilities: this.getDeviceCapabilities()
      })
      
      this.aiCapabilities.federatedSyncActive = true
    }
  }

  async preloadCriticalModels() {
    const criticalModels = [
      'fraud_detection_v2',
      'image_variance_v3',
      'regional_nlp_v2',
      'anomaly_detection_v4'
    ]

    const loadPromises = criticalModels.map(async (modelId) => {
      try {
        const response = await fetch(`/api/method/mkaguzi.chat_system.api.models.download?model_id=${modelId}`)
        if (response.ok) {
          console.log(`Model ${modelId} cached for offline use`)
          return { modelId, status: 'cached' }
        }
      } catch (error) {
        console.warn(`Failed to cache model ${modelId}:`, error)
        return { modelId, status: 'failed', error: error.message }
      }
    })

    const results = await Promise.allSettled(loadPromises)
    this.aiCapabilities.modelsLoaded = results.some(r => r.status === 'fulfilled' && r.value.status === 'cached')
    
    return results
  }

  handleServiceWorkerMessage(event) {
    const { type, data } = event.data || {}

    switch (type) {
      case 'AI_INFERENCE_COMPLETE':
        this.handleInferenceComplete(data)
        break
      
      case 'FEDERATED_SYNC_STATUS':
        this.handleFederatedSyncStatus(data)
        break
      
      case 'MODEL_CACHE_UPDATE':
        this.handleModelCacheUpdate(data)
        break
      
      case 'OFFLINE_QUEUE_STATUS':
        this.handleOfflineQueueStatus(data)
        break

      default:
        console.log('Unknown service worker message:', event.data)
    }
  }

  handleInferenceComplete(data) {
    // Emit custom event for AI inference completion
    const event = new CustomEvent('ai-inference-complete', { detail: data })
    window.dispatchEvent(event)
  }

  handleFederatedSyncStatus(data) {
    console.log('Federated sync status:', data)
    this.aiCapabilities.federatedSyncActive = data.active
    
    // Notify UI components
    const event = new CustomEvent('federated-sync-status', { detail: data })
    window.dispatchEvent(event)
  }

  handleModelCacheUpdate(data) {
    console.log('Model cache updated:', data)
    this.aiCapabilities.modelsLoaded = data.modelsLoaded > 0
    
    // Notify UI components
    const event = new CustomEvent('ai-models-updated', { detail: data })
    window.dispatchEvent(event)
  }

  handleOfflineQueueStatus(data) {
    console.log('Offline queue status:', data)
    
    // Show notification if there are queued operations
    if (data.queuedOperations > 0) {
      this.showNotification(
        'Offline Operations Queued',
        `${data.queuedOperations} operations will sync when online`,
        'info'
      )
    }
  }

  handleOnlineStatusChange(isOnline) {
    console.log('Network status changed:', isOnline ? 'online' : 'offline')
    
    if (isOnline) {
      // Trigger federated sync when coming back online
      this.triggerSync()
      this.showNotification('Back Online', 'Syncing pending operations...', 'success')
    } else {
      this.showNotification('Offline Mode', 'Using cached content and AI models', 'warning')
    }

    // Notify UI components
    const event = new CustomEvent('network-status-change', { 
      detail: { isOnline, timestamp: Date.now() }
    })
    window.dispatchEvent(event)
  }

  async triggerSync() {
    if (this.serviceWorkerRegistration && 'sync' in this.serviceWorkerRegistration) {
      try {
        await this.serviceWorkerRegistration.sync.register('federated-sync')
        console.log('Background sync registered')
      } catch (error) {
        console.error('Failed to register background sync:', error)
      }
    }
  }

  async showInstallPrompt(event) {
    // Customize install prompt
    const installBanner = document.createElement('div')
    installBanner.className = 'pwa-install-banner'
    installBanner.innerHTML = `
      <div class="pwa-install-content">
        <div class="pwa-install-icon">📱</div>
        <div class="pwa-install-text">
          <h4>Install Mkaguzi AI Chat</h4>
          <p>Access offline AI capabilities and enhanced performance</p>
        </div>
        <div class="pwa-install-actions">
          <button id="pwa-install-accept" class="btn btn-primary btn-sm">Install</button>
          <button id="pwa-install-dismiss" class="btn btn-secondary btn-sm">Later</button>
        </div>
      </div>
    `

    document.body.appendChild(installBanner)

    // Handle install accept
    document.getElementById('pwa-install-accept').addEventListener('click', async () => {
      try {
        const choiceResult = await event.prompt()
        console.log('Install choice:', choiceResult.outcome)
        
        if (choiceResult.outcome === 'accepted') {
          this.trackEvent('pwa_install_accepted')
        } else {
          this.trackEvent('pwa_install_dismissed')
        }
      } catch (error) {
        console.error('Install prompt failed:', error)
      }
      
      installBanner.remove()
    })

    // Handle dismiss
    document.getElementById('pwa-install-dismiss').addEventListener('click', () => {
      this.trackEvent('pwa_install_dismissed')
      installBanner.remove()
    })

    // Auto-dismiss after 10 seconds
    setTimeout(() => {
      if (document.body.contains(installBanner)) {
        installBanner.remove()
      }
    }, 10000)
  }

  notifyUpdateAvailable() {
    this.showNotification(
      'App Update Available',
      'A new version is ready. Refresh to update.',
      'info',
      [
        {
          text: 'Refresh Now',
          action: () => this.activateUpdate()
        },
        {
          text: 'Later',
          action: () => {}
        }
      ]
    )
  }

  notifyOfflineReady() {
    this.showNotification(
      'Ready for Offline Use',
      'AI models cached and ready for offline inference',
      'success'
    )
  }

  notifyAICapabilitiesReady() {
    const capabilitiesCount = Object.values(this.aiCapabilities).filter(Boolean).length
    this.showNotification(
      'AI Capabilities Ready',
      `${capabilitiesCount}/3 AI features initialized successfully`,
      'success'
    )
  }

  async activateUpdate() {
    if (this.serviceWorkerRegistration && this.serviceWorkerRegistration.waiting) {
      // Tell the waiting service worker to skip waiting
      this.serviceWorkerRegistration.waiting.postMessage({ type: 'SKIP_WAITING' })
      
      // Reload the page when the new service worker takes control
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        window.location.reload()
      })
    }
  }

  showNotification(title, message, type = 'info', actions = []) {
    // Create custom notification (can be replaced with actual notification API)
    const notification = document.createElement('div')
    notification.className = `pwa-notification pwa-notification-${type}`
    
    notification.innerHTML = `
      <div class="pwa-notification-content">
        <div class="pwa-notification-title">${title}</div>
        <div class="pwa-notification-message">${message}</div>
        ${actions.length > 0 ? `
          <div class="pwa-notification-actions">
            ${actions.map((action, index) => 
              `<button class="pwa-notification-action" data-action="${index}">${action.text}</button>`
            ).join('')}
          </div>
        ` : ''}
      </div>
      <button class="pwa-notification-close">&times;</button>
    `

    // Handle action clicks
    actions.forEach((action, index) => {
      const actionButton = notification.querySelector(`[data-action="${index}"]`)
      if (actionButton) {
        actionButton.addEventListener('click', () => {
          action.action()
          notification.remove()
        })
      }
    })

    // Handle close button
    notification.querySelector('.pwa-notification-close').addEventListener('click', () => {
      notification.remove()
    })

    // Auto-remove after 5 seconds for info notifications
    if (type === 'info') {
      setTimeout(() => {
        if (document.body.contains(notification)) {
          notification.remove()
        }
      }, 5000)
    }

    document.body.appendChild(notification)
  }

  startHealthMonitoring() {
    // Check AI capabilities every 5 minutes
    setInterval(async () => {
      const status = await this.checkSystemHealth()
      
      if (status.issues.length > 0) {
        console.warn('System health issues detected:', status.issues)
        // Could show health notifications here
      }
    }, 300000) // 5 minutes
  }

  async checkSystemHealth() {
    const issues = []
    const capabilities = { ...this.aiCapabilities }

    try {
      // Check service worker status
      if (!navigator.serviceWorker.controller) {
        issues.push('Service worker not active')
      }

      // Check model cache
      const modelStatus = await this.checkAIModelStatus()
      if (!modelStatus.models_available) {
        issues.push('AI models not available')
        capabilities.modelsLoaded = false
      }

      // Check IndexedDB availability
      if (!('indexedDB' in window)) {
        issues.push('IndexedDB not available')
        capabilities.offlineInferenceReady = false
      }

      return { healthy: issues.length === 0, issues, capabilities }
    } catch (error) {
      issues.push(`Health check failed: ${error.message}`)
      return { healthy: false, issues, capabilities }
    }
  }

  getClientId() {
    let clientId = localStorage.getItem('mkaguzi_client_id')
    if (!clientId) {
      clientId = crypto.randomUUID()
      localStorage.setItem('mkaguzi_client_id', clientId)
    }
    return clientId
  }

  getDeviceCapabilities() {
    return {
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      hardwareConcurrency: navigator.hardwareConcurrency || 1,
      memory: navigator.deviceMemory || 'unknown',
      connection: navigator.connection ? {
        effectiveType: navigator.connection.effectiveType,
        downlink: navigator.connection.downlink,
        rtt: navigator.connection.rtt
      } : null,
      screen: {
        width: screen.width,
        height: screen.height,
        devicePixelRatio: window.devicePixelRatio || 1
      },
      webgl: this.checkWebGLSupport(),
      webassembly: typeof WebAssembly !== 'undefined',
      serviceWorker: 'serviceWorker' in navigator,
      indexedDB: 'indexedDB' in window,
      caches: 'caches' in window
    }
  }

  checkWebGLSupport() {
    try {
      const canvas = document.createElement('canvas')
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')
      return {
        supported: !!gl,
        version: gl ? gl.getParameter(gl.VERSION) : null,
        renderer: gl ? gl.getParameter(gl.RENDERER) : null
      }
    } catch (e) {
      return { supported: false, error: e.message }
    }
  }

  trackEvent(eventName, properties = {}) {
    // Analytics tracking (integrate with your analytics service)
    console.log('PWA Event:', eventName, properties)
    
    // Could send to analytics service here
    if (typeof frappe !== 'undefined' && frappe.call) {
      frappe.call({
        method: 'mkaguzi.chat_system.api.analytics.track_pwa_event',
        args: {
          event: eventName,
          properties: {
            ...properties,
            timestamp: Date.now(),
            client_id: this.getClientId(),
            user_agent: navigator.userAgent,
            url: window.location.href
          }
        },
        freeze: false // Don't show loading indicator
      })
    }
  }

  // Public API methods
  async performOfflineInference(modelId, inputData) {
    if (!this.aiCapabilities.offlineInferenceReady) {
      throw new Error('Offline inference not ready')
    }

    try {
      const response = await fetch('/api/method/mkaguzi.chat_system.api.inference.predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId, input_data: inputData })
      })

      return await response.json()
    } catch (error) {
      console.error('Offline inference failed:', error)
      throw error
    }
  }

  async cacheModel(modelId) {
    try {
      const response = await fetch(`/api/method/mkaguzi.chat_system.api.models.download?model_id=${modelId}`)
      return await response.json()
    } catch (error) {
      console.error('Model caching failed:', error)
      throw error
    }
  }

  getCapabilities() {
    return {
      ...this.aiCapabilities,
      isOnline: navigator.onLine,
      updateAvailable: this.updateAvailable,
      offlineReady: this.isOfflineReady,
      serviceWorkerReady: !!navigator.serviceWorker.controller
    }
  }
}

// Initialize PWA Manager
const pwaManager = new PWAManager()

// Make it available globally
window.pwaManager = pwaManager

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PWAManager
}

console.log('PWA Manager loaded and initializing...')