/**
 * AI-Enhanced Service Worker for Mkaguzi Audit Chat System
 * Provides offline AI inference, model caching, and federated learning synchronization
 */

const CACHE_VERSION = 'mkaguzi-ai-v2.1.0'
const STATIC_CACHE = `${CACHE_VERSION}-static`
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`
const AI_MODEL_CACHE = `${CACHE_VERSION}-ai-models`
const FEDERATED_CACHE = `${CACHE_VERSION}-federated`

// Cache configurations
const CACHE_CONFIG = {
  staticAssets: {
    maxAge: 86400000, // 24 hours
    resources: [
      '/app/chat',
      '/assets/mkaguzi/js/components/',
      '/assets/mkaguzi/css/',
      '/assets/frappe/css/frappe-web.css',
      '/assets/frappe/js/frappe-web.min.js'
    ]
  },
  aiModels: {
    maxAge: 604800000, // 7 days
    maxSize: 100 * 1024 * 1024, // 100MB total
    compressionLevel: 'high'
  },
  federatedData: {
    maxAge: 3600000, // 1 hour
    syncInterval: 300000, // 5 minutes
    batchSize: 50
  }
}

// AI Model Management
class AIModelCache {
  constructor() {
    this.modelStore = null
    this.initPromise = this.init()
  }

  async init() {
    if ('serviceWorker' in navigator && 'indexedDB' in window) {
      this.modelStore = await this.openModelDB()
    }
  }

  async openModelDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('MkaguziAIModels', 3)
      
      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result)
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result
        
        // Model metadata store
        if (!db.objectStoreNames.contains('models')) {
          const modelStore = db.createObjectStore('models', { keyPath: 'id' })
          modelStore.createIndex('domain', 'domain')
          modelStore.createIndex('version', 'version')
          modelStore.createIndex('lastUsed', 'lastUsed')
        }
        
        // Model binary data store
        if (!db.objectStoreNames.contains('modelData')) {
          const dataStore = db.createObjectStore('modelData', { keyPath: 'modelId' })
          dataStore.createIndex('size', 'size')
          dataStore.createIndex('compressed', 'compressed')
        }
        
        // Inference cache store
        if (!db.objectStoreNames.contains('inferenceCache')) {
          const cacheStore = db.createObjectStore('inferenceCache', { keyPath: 'hash' })
          cacheStore.createIndex('timestamp', 'timestamp')
          cacheStore.createIndex('modelId', 'modelId')
        }
      }
    })
  }

  async cacheModel(modelId, modelData, metadata) {
    await this.initPromise
    if (!this.modelStore) return false

    try {
      const transaction = this.modelStore.transaction(['models', 'modelData'], 'readwrite')
      
      // Compress model if needed
      const compressedData = await this.compressModel(modelData, metadata.compressionLevel)
      
      // Store metadata
      await this.putData(transaction.objectStore('models'), {
        id: modelId,
        domain: metadata.domain,
        version: metadata.version,
        size: compressedData.byteLength,
        lastUsed: Date.now(),
        compressed: true,
        accuracy: metadata.accuracy,
        capabilities: metadata.capabilities
      })
      
      // Store model data
      await this.putData(transaction.objectStore('modelData'), {
        modelId: modelId,
        data: compressedData,
        size: compressedData.byteLength,
        compressed: true
      })
      
      await this.enforceStorageQuota()
      return true
    } catch (error) {
      console.error('Failed to cache AI model:', error)
      return false
    }
  }

  async getModel(modelId) {
    await this.initPromise
    if (!this.modelStore) return null

    try {
      const transaction = this.modelStore.transaction(['models', 'modelData'], 'readonly')
      
      const metadata = await this.getData(transaction.objectStore('models'), modelId)
      if (!metadata) return null
      
      const modelData = await this.getData(transaction.objectStore('modelData'), modelId)
      if (!modelData) return null
      
      // Update last used timestamp
      metadata.lastUsed = Date.now()
      await this.updateData(this.modelStore.transaction(['models'], 'readwrite').objectStore('models'), metadata)
      
      // Decompress if needed
      const decompressedData = metadata.compressed 
        ? await this.decompressModel(modelData.data)
        : modelData.data
      
      return {
        metadata,
        data: decompressedData
      }
    } catch (error) {
      console.error('Failed to retrieve AI model:', error)
      return null
    }
  }

  async compressModel(data, level = 'medium') {
    if (typeof CompressionStream !== 'undefined') {
      const compressionLevel = {
        'low': 'gzip',
        'medium': 'deflate', 
        'high': 'deflate-raw'
      }[level] || 'deflate'
      
      const stream = new CompressionStream(compressionLevel)
      const writer = stream.writable.getWriter()
      const reader = stream.readable.getReader()
      
      writer.write(data)
      writer.close()
      
      const chunks = []
      let done = false
      
      while (!done) {
        const { value, done: streamDone } = await reader.read()
        done = streamDone
        if (value) chunks.push(value)
      }
      
      return new Uint8Array(chunks.reduce((acc, chunk) => [...acc, ...chunk], []))
    }
    
    // Fallback: simple compression simulation
    return data
  }

  async decompressModel(compressedData) {
    if (typeof DecompressionStream !== 'undefined') {
      const stream = new DecompressionStream('deflate')
      const writer = stream.writable.getWriter()
      const reader = stream.readable.getReader()
      
      writer.write(compressedData)
      writer.close()
      
      const chunks = []
      let done = false
      
      while (!done) {
        const { value, done: streamDone } = await reader.read()
        done = streamDone
        if (value) chunks.push(value)
      }
      
      return new Uint8Array(chunks.reduce((acc, chunk) => [...acc, ...chunk], []))
    }
    
    // Fallback: return as-is
    return compressedData
  }

  async enforceStorageQuota() {
    const models = await this.getAllModels()
    const totalSize = models.reduce((sum, model) => sum + (model.size || 0), 0)
    
    if (totalSize > CACHE_CONFIG.aiModels.maxSize) {
      // Remove least recently used models
      models.sort((a, b) => a.lastUsed - b.lastUsed)
      
      let sizeToRemove = totalSize - CACHE_CONFIG.aiModels.maxSize
      for (const model of models) {
        if (sizeToRemove <= 0) break
        
        await this.removeModel(model.id)
        sizeToRemove -= model.size
      }
    }
  }

  async getAllModels() {
    await this.initPromise
    if (!this.modelStore) return []
    
    const transaction = this.modelStore.transaction(['models'], 'readonly')
    const store = transaction.objectStore('models')
    
    return new Promise((resolve, reject) => {
      const request = store.getAll()
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  async removeModel(modelId) {
    await this.initPromise
    if (!this.modelStore) return
    
    const transaction = this.modelStore.transaction(['models', 'modelData'], 'readwrite')
    await Promise.all([
      this.deleteData(transaction.objectStore('models'), modelId),
      this.deleteData(transaction.objectStore('modelData'), modelId)
    ])
  }

  // Helper methods for IndexedDB operations
  putData(store, data) {
    return new Promise((resolve, reject) => {
      const request = store.put(data)
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  getData(store, key) {
    return new Promise((resolve, reject) => {
      const request = store.get(key)
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  updateData(store, data) {
    return new Promise((resolve, reject) => {
      const request = store.put(data)
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  deleteData(store, key) {
    return new Promise((resolve, reject) => {
      const request = store.delete(key)
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }
}

// Offline AI Inference Engine
class OfflineInferenceEngine {
  constructor(modelCache) {
    this.modelCache = modelCache
    this.loadedModels = new Map()
    this.inferenceQueue = []
    this.isProcessing = false
  }

  async loadModel(modelId) {
    if (this.loadedModels.has(modelId)) {
      return this.loadedModels.get(modelId)
    }

    const cachedModel = await this.modelCache.getModel(modelId)
    if (!cachedModel) {
      throw new Error(`Model ${modelId} not found in cache`)
    }

    // Simulate model loading (replace with actual ML framework)
    const model = {
      id: modelId,
      metadata: cachedModel.metadata,
      predict: this.createPredictFunction(cachedModel.data, cachedModel.metadata)
    }

    this.loadedModels.set(modelId, model)
    return model
  }

  createPredictFunction(modelData, metadata) {
    // This would integrate with actual ML frameworks like TensorFlow.js, ONNX.js, etc.
    return async (input) => {
      const startTime = performance.now()
      
      // Simulate inference based on model domain
      let result
      switch (metadata.domain) {
        case 'fraud_detection':
          result = this.simulateFraudDetection(input)
          break
        case 'image_variance':
          result = this.simulateImageVariance(input)
          break
        case 'regional_nlp':
          result = this.simulateRegionalNLP(input)
          break
        case 'anomaly_detection':
          result = this.simulateAnomalyDetection(input)
          break
        default:
          result = { prediction: 'unknown', confidence: 0.5 }
      }

      const inferenceTime = performance.now() - startTime
      
      // Cache inference result
      await this.cacheInferenceResult(input, result, metadata.id, inferenceTime)
      
      return {
        ...result,
        modelId: metadata.id,
        inferenceTime,
        timestamp: Date.now()
      }
    }
  }

  simulateFraudDetection(input) {
    // Simulate fraud detection logic
    const riskScore = Math.random()
    return {
      prediction: riskScore > 0.7 ? 'fraud' : 'legitimate',
      confidence: riskScore,
      riskFactors: ['amount_anomaly', 'time_pattern', 'location_mismatch'].slice(0, Math.floor(Math.random() * 3) + 1)
    }
  }

  simulateImageVariance(input) {
    // Simulate image variance detection
    const variance = Math.random()
    return {
      prediction: variance > 0.6 ? 'significant_variance' : 'acceptable_variance',
      confidence: variance,
      varianceAreas: ['top_left', 'center', 'bottom_right'].slice(0, Math.floor(Math.random() * 3) + 1),
      discrepancyType: variance > 0.8 ? 'inventory_mismatch' : 'normal_variation'
    }
  }

  simulateRegionalNLP(input) {
    // Simulate regional NLP processing
    const compliance = Math.random()
    const regulations = ['KRA_2023', 'URA_2024', 'TRA_2023']
    return {
      prediction: compliance > 0.7 ? 'compliant' : 'non_compliant',
      confidence: compliance,
      extractedEntities: ['tax_rate', 'registration_number', 'compliance_date'],
      applicableRegulations: regulations.slice(0, Math.floor(Math.random() * 3) + 1),
      complianceScore: Math.floor(compliance * 100)
    }
  }

  simulateAnomalyDetection(input) {
    // Simulate anomaly detection
    const anomalyScore = Math.random()
    return {
      prediction: anomalyScore > 0.75 ? 'anomaly' : 'normal',
      confidence: anomalyScore,
      anomalyType: anomalyScore > 0.9 ? 'critical' : anomalyScore > 0.75 ? 'warning' : 'normal',
      affectedMetrics: ['transaction_volume', 'user_behavior', 'system_performance'].slice(0, Math.floor(Math.random() * 3) + 1)
    }
  }

  async cacheInferenceResult(input, result, modelId, inferenceTime) {
    await this.modelCache.initPromise
    if (!this.modelCache.modelStore) return

    const hash = await this.hashInput(input)
    const cacheEntry = {
      hash,
      modelId,
      input,
      result,
      timestamp: Date.now(),
      inferenceTime
    }

    try {
      const transaction = this.modelCache.modelStore.transaction(['inferenceCache'], 'readwrite')
      await this.modelCache.putData(transaction.objectStore('inferenceCache'), cacheEntry)
      
      // Clean old cache entries
      await this.cleanInferenceCache()
    } catch (error) {
      console.error('Failed to cache inference result:', error)
    }
  }

  async getCachedInference(input, modelId) {
    await this.modelCache.initPromise
    if (!this.modelCache.modelStore) return null

    const hash = await this.hashInput(input)
    
    try {
      const transaction = this.modelCache.modelStore.transaction(['inferenceCache'], 'readonly')
      const cached = await this.modelCache.getData(transaction.objectStore('inferenceCache'), hash)
      
      if (cached && cached.modelId === modelId) {
        const age = Date.now() - cached.timestamp
        if (age < CACHE_CONFIG.federatedData.maxAge) {
          return cached.result
        }
      }
    } catch (error) {
      console.error('Failed to retrieve cached inference:', error)
    }
    
    return null
  }

  async hashInput(input) {
    const encoder = new TextEncoder()
    const data = encoder.encode(JSON.stringify(input))
    const hashBuffer = await crypto.subtle.digest('SHA-256', data)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
  }

  async cleanInferenceCache() {
    await this.modelCache.initPromise
    if (!this.modelCache.modelStore) return

    const cutoffTime = Date.now() - CACHE_CONFIG.federatedData.maxAge
    const transaction = this.modelCache.modelStore.transaction(['inferenceCache'], 'readwrite')
    const store = transaction.objectStore('inferenceCache')
    const index = store.index('timestamp')
    
    const range = IDBKeyRange.upperBound(cutoffTime)
    const request = index.openCursor(range)
    
    request.onsuccess = (event) => {
      const cursor = event.target.result
      if (cursor) {
        cursor.delete()
        cursor.continue()
      }
    }
  }

  async processInference(modelId, input) {
    // Check cache first
    const cached = await this.getCachedInference(input, modelId)
    if (cached) {
      return { ...cached, fromCache: true }
    }

    // Load model if not loaded
    const model = await this.loadModel(modelId)
    
    // Perform inference
    const result = await model.predict(input)
    return { ...result, fromCache: false }
  }
}

// Federated Learning Synchronization
class FederatedSync {
  constructor() {
    this.syncQueue = []
    this.lastSync = {}
    this.isOnline = navigator.onLine
    
    // Listen for online/offline events
    addEventListener('online', () => {
      this.isOnline = true
      this.processSyncQueue()
    })
    
    addEventListener('offline', () => {
      this.isOnline = false
    })
  }

  async queueUpdate(update) {
    this.syncQueue.push({
      ...update,
      timestamp: Date.now(),
      id: crypto.randomUUID()
    })

    if (this.isOnline) {
      await this.processSyncQueue()
    }
  }

  async processSyncQueue() {
    if (!this.isOnline || this.syncQueue.length === 0) return

    const batch = this.syncQueue.splice(0, CACHE_CONFIG.federatedData.batchSize)
    
    try {
      const response = await fetch('/api/method/mkaguzi.chat_system.api.federated.sync_updates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': await this.getCSRFToken()
        },
        body: JSON.stringify({
          updates: batch,
          client_id: await this.getClientId()
        })
      })

      if (response.ok) {
        const result = await response.json()
        await this.processServerUpdates(result.server_updates || [])
      } else {
        // Re-queue failed updates
        this.syncQueue.unshift(...batch)
      }
    } catch (error) {
      console.error('Federated sync failed:', error)
      // Re-queue failed updates
      this.syncQueue.unshift(...batch)
    }
  }

  async processServerUpdates(updates) {
    for (const update of updates) {
      switch (update.type) {
        case 'model_update':
          await this.handleModelUpdate(update)
          break
        case 'training_data':
          await this.handleTrainingData(update)
          break
        case 'aggregation_result':
          await this.handleAggregationResult(update)
          break
      }
    }
  }

  async handleModelUpdate(update) {
    // Update cached model with new weights/parameters
    const modelCache = globalThis.aiModelCache
    if (modelCache) {
      await modelCache.cacheModel(
        update.model_id,
        update.model_data,
        update.metadata
      )
    }
  }

  async handleTrainingData(update) {
    // Store federated training data for offline training
    // This would integrate with local training capabilities
    console.log('Received federated training data:', update)
  }

  async handleAggregationResult(update) {
    // Process aggregated model updates from federated learning
    console.log('Received aggregation result:', update)
  }

  async getCSRFToken() {
    try {
      const response = await fetch('/api/method/frappe.sessions.get_csrf_token')
      const data = await response.json()
      return data.message
    } catch (error) {
      console.error('Failed to get CSRF token:', error)
      return ''
    }
  }

  async getClientId() {
    let clientId = localStorage.getItem('mkaguzi_client_id')
    if (!clientId) {
      clientId = crypto.randomUUID()
      localStorage.setItem('mkaguzi_client_id', clientId)
    }
    return clientId
  }
}

// Initialize AI components
const aiModelCache = new AIModelCache()
const offlineInference = new OfflineInferenceEngine(aiModelCache)
const federatedSync = new FederatedSync()

// Make available globally for the service worker
globalThis.aiModelCache = aiModelCache
globalThis.offlineInference = offlineInference
globalThis.federatedSync = federatedSync

// Service Worker Event Handlers
self.addEventListener('install', (event) => {
  console.log('AI Service Worker installing...')
  
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then(cache => {
        return cache.addAll(CACHE_CONFIG.staticAssets.resources)
      }),
      aiModelCache.initPromise
    ])
  )
})

self.addEventListener('activate', (event) => {
  console.log('AI Service Worker activating...')
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (!cacheName.startsWith(CACHE_VERSION)) {
              return caches.delete(cacheName)
            }
          })
        )
      }),
      // Initialize periodic sync for federated learning
      self.registration.sync?.register('federated-sync')
    ])
  )
})

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)
  
  // Handle AI inference requests
  if (url.pathname.includes('/api/method/mkaguzi.chat_system.api.inference.predict')) {
    event.respondWith(handleInferenceRequest(event.request))
    return
  }
  
  // Handle model download requests
  if (url.pathname.includes('/api/method/mkaguzi.chat_system.api.models.download')) {
    event.respondWith(handleModelDownload(event.request))
    return
  }
  
  // Handle federated learning requests
  if (url.pathname.includes('/api/method/mkaguzi.chat_system.api.federated.')) {
    event.respondWith(handleFederatedRequest(event.request))
    return
  }
  
  // Standard caching strategy
  event.respondWith(handleStaticRequest(event.request))
})

// Handle background sync for federated learning
self.addEventListener('sync', (event) => {
  if (event.tag === 'federated-sync') {
    event.waitUntil(federatedSync.processSyncQueue())
  }
})

// Handle periodic background sync
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'federated-periodic-sync') {
    event.waitUntil(
      federatedSync.processSyncQueue().then(() => {
        return aiModelCache.enforceStorageQuota()
      })
    )
  }
})

// Request handlers
async function handleInferenceRequest(request) {
  try {
    const requestData = await request.json()
    const { model_id, input_data } = requestData
    
    // Try offline inference first
    const result = await offlineInference.processInference(model_id, input_data)
    
    if (result) {
      return new Response(JSON.stringify({
        success: true,
        result: result,
        offline: !navigator.onLine || result.fromCache
      }), {
        headers: { 'Content-Type': 'application/json' }
      })
    }
    
    // Fallback to network if available
    if (navigator.onLine) {
      return fetch(request)
    }
    
    throw new Error('Model not available offline')
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message,
      offline: true
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

async function handleModelDownload(request) {
  const url = new URL(request.url)
  const modelId = url.searchParams.get('model_id')
  
  // Check if model is already cached
  const cachedModel = await aiModelCache.getModel(modelId)
  if (cachedModel) {
    return new Response(JSON.stringify({
      success: true,
      cached: true,
      metadata: cachedModel.metadata
    }), {
      headers: { 'Content-Type': 'application/json' }
    })
  }
  
  // Download and cache model
  if (navigator.onLine) {
    try {
      const response = await fetch(request)
      if (response.ok) {
        const data = await response.json()
        
        // Cache the model
        await aiModelCache.cacheModel(modelId, data.model_data, data.metadata)
        
        return new Response(JSON.stringify({
          success: true,
          cached: true,
          downloaded: true,
          metadata: data.metadata
        }), {
          headers: { 'Content-Type': 'application/json' }
        })
      }
    } catch (error) {
      console.error('Model download failed:', error)
    }
  }
  
  return new Response(JSON.stringify({
    success: false,
    error: 'Model not available',
    offline: !navigator.onLine
  }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' }
  })
}

async function handleFederatedRequest(request) {
  const url = new URL(request.url)
  
  // Queue federated updates for background sync
  if (request.method === 'POST' && url.pathname.includes('update')) {
    const updateData = await request.json()
    await federatedSync.queueUpdate(updateData)
    
    return new Response(JSON.stringify({
      success: true,
      queued: true,
      will_sync: navigator.onLine
    }), {
      headers: { 'Content-Type': 'application/json' }
    })
  }
  
  // Forward other federated requests if online
  if (navigator.onLine) {
    return fetch(request)
  }
  
  return new Response(JSON.stringify({
    success: false,
    error: 'Offline - federated operation queued',
    offline: true
  }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' }
  })
}

async function handleStaticRequest(request) {
  const cache = await caches.open(STATIC_CACHE)
  const cachedResponse = await cache.match(request)
  
  if (cachedResponse) {
    // Serve from cache
    return cachedResponse
  }
  
  if (navigator.onLine) {
    try {
      const networkResponse = await fetch(request)
      
      // Cache successful responses
      if (networkResponse.ok) {
        const dynamicCache = await caches.open(DYNAMIC_CACHE)
        dynamicCache.put(request, networkResponse.clone())
      }
      
      return networkResponse
    } catch (error) {
      console.error('Network request failed:', error)
    }
  }
  
  // Return offline fallback
  return new Response(JSON.stringify({
    error: 'Offline - resource not cached',
    offline: true
  }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' }
  })
}

// Cleanup and maintenance
setInterval(async () => {
  await aiModelCache.enforceStorageQuota()
  await offlineInference.cleanInferenceCache()
}, 3600000) // Run every hour

console.log('AI Service Worker initialized with enhanced capabilities')