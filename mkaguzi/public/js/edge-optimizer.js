/**
 * Edge Computing Optimization Module for Mobile AI Operations
 * Handles model optimization, compression, and edge deployment strategies
 */

class EdgeComputingOptimizer {
  constructor() {
    this.optimizedModels = new Map()
    this.deviceCapabilities = null
    this.optimizationStrategies = new Map()
    this.performanceMetrics = new Map()
    
    this.initialize()
  }

  async initialize() {
    this.deviceCapabilities = await this.assessDeviceCapabilities()
    this.setupOptimizationStrategies()
    
    console.log('Edge Computing Optimizer initialized:', {
      device: this.deviceCapabilities.deviceClass,
      strategies: this.optimizationStrategies.size
    })
  }

  async assessDeviceCapabilities() {
    const capabilities = {
      // Hardware assessment
      cores: navigator.hardwareConcurrency || 1,
      memory: navigator.deviceMemory || this.estimateMemory(),
      gpu: await this.assessGPUCapabilities(),
      
      // Performance assessment
      cpuBenchmark: await this.benchmarkCPU(),
      memoryBenchmark: await this.benchmarkMemory(),
      
      // Network assessment
      connection: navigator.connection ? {
        effectiveType: navigator.connection.effectiveType,
        downlink: navigator.connection.downlink,
        rtt: navigator.connection.rtt,
        saveData: navigator.connection.saveData
      } : null,
      
      // Battery status
      battery: await this.getBatteryInfo(),
      
      // Storage assessment
      storage: await this.assessStorageCapabilities(),
      
      // Device classification
      deviceClass: 'unknown',
      isMobile: /Mobi|Android/i.test(navigator.userAgent),
      isLowEnd: false
    }

    // Classify device based on capabilities
    capabilities.deviceClass = this.classifyDevice(capabilities)
    capabilities.isLowEnd = capabilities.deviceClass === 'low-end'

    return capabilities
  }

  estimateMemory() {
    // Fallback memory estimation for browsers that don't support deviceMemory
    const userAgent = navigator.userAgent.toLowerCase()
    
    if (userAgent.includes('mobile') || userAgent.includes('android')) {
      return userAgent.includes('premium') ? 8 : 4 // GB
    }
    
    return 8 // Default assumption for desktop
  }

  async assessGPUCapabilities() {
    try {
      const canvas = document.createElement('canvas')
      const gl = canvas.getContext('webgl2') || canvas.getContext('webgl')
      
      if (!gl) return { supported: false }

      const debugInfo = gl.getExtension('WEBGL_debug_renderer_info')
      
      return {
        supported: true,
        renderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'Unknown',
        vendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : 'Unknown',
        version: gl.getParameter(gl.VERSION),
        maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
        maxVertexAttribs: gl.getParameter(gl.MAX_VERTEX_ATTRIBS),
        webgl2: gl instanceof WebGL2RenderingContext
      }
    } catch (error) {
      return { supported: false, error: error.message }
    }
  }

  async benchmarkCPU() {
    const startTime = performance.now()
    
    // Simple CPU benchmark - calculate primes
    let count = 0
    for (let i = 2; i < 10000; i++) {
      let isPrime = true
      for (let j = 2; j < Math.sqrt(i); j++) {
        if (i % j === 0) {
          isPrime = false
          break
        }
      }
      if (isPrime) count++
    }
    
    const duration = performance.now() - startTime
    const score = Math.round(10000 / duration) // Higher is better
    
    return {
      duration,
      score,
      classification: score > 50 ? 'high' : score > 20 ? 'medium' : 'low'
    }
  }

  async benchmarkMemory() {
    const startTime = performance.now()
    
    try {
      // Memory allocation test
      const arrays = []
      const chunkSize = 1024 * 1024 // 1MB chunks
      let allocated = 0
      
      while (allocated < 50 * 1024 * 1024 && performance.now() - startTime < 1000) { // Max 50MB or 1 second
        try {
          arrays.push(new Uint8Array(chunkSize))
          allocated += chunkSize
        } catch (e) {
          break
        }
      }
      
      const duration = performance.now() - startTime
      
      return {
        allocatedMB: Math.round(allocated / (1024 * 1024)),
        duration,
        throughputMBps: Math.round((allocated / (1024 * 1024)) / (duration / 1000))
      }
    } catch (error) {
      return { error: error.message, allocatedMB: 0, throughputMBps: 0 }
    }
  }

  async getBatteryInfo() {
    if ('getBattery' in navigator) {
      try {
        const battery = await navigator.getBattery()
        return {
          level: battery.level,
          charging: battery.charging,
          chargingTime: battery.chargingTime,
          dischargingTime: battery.dischargingTime
        }
      } catch (error) {
        return { supported: false, error: error.message }
      }
    }
    
    return { supported: false }
  }

  async assessStorageCapabilities() {
    try {
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        const estimate = await navigator.storage.estimate()
        return {
          quota: estimate.quota,
          usage: estimate.usage,
          usageDetails: estimate.usageDetails,
          available: estimate.quota - estimate.usage,
          percentUsed: (estimate.usage / estimate.quota) * 100
        }
      }
    } catch (error) {
      console.warn('Storage estimation failed:', error)
    }
    
    return { supported: false }
  }

  classifyDevice(capabilities) {
    const score = this.calculateDeviceScore(capabilities)
    
    if (score >= 80) return 'high-end'
    if (score >= 50) return 'mid-range'
    return 'low-end'
  }

  calculateDeviceScore(capabilities) {
    let score = 0
    
    // CPU score (0-30 points)
    score += Math.min(30, capabilities.cpuBenchmark.score)
    
    // Memory score (0-25 points)
    score += Math.min(25, capabilities.memory * 3)
    
    // GPU score (0-20 points)
    if (capabilities.gpu.supported) {
      score += 10
      if (capabilities.gpu.webgl2) score += 5
      if (capabilities.gpu.maxTextureSize > 4096) score += 5
    }
    
    // Core count score (0-15 points)
    score += Math.min(15, capabilities.cores * 2)
    
    // Network score (0-10 points)
    if (capabilities.connection) {
      const networkScore = {
        '4g': 10,
        '3g': 6,
        '2g': 2,
        'slow-2g': 1
      }[capabilities.connection.effectiveType] || 5
      
      score += networkScore
    }
    
    return Math.min(100, score)
  }

  setupOptimizationStrategies() {
    // Strategy for high-end devices
    this.optimizationStrategies.set('high-end', {
      modelCompression: 'minimal',
      quantization: 'fp16',
      batchSize: 8,
      cacheStrategy: 'aggressive',
      parallelInference: true,
      webGLAcceleration: true,
      maxModelSize: 50 * 1024 * 1024, // 50MB
      preloadModels: 5
    })

    // Strategy for mid-range devices
    this.optimizationStrategies.set('mid-range', {
      modelCompression: 'moderate',
      quantization: 'int8',
      batchSize: 4,
      cacheStrategy: 'balanced',
      parallelInference: false,
      webGLAcceleration: true,
      maxModelSize: 25 * 1024 * 1024, // 25MB
      preloadModels: 3
    })

    // Strategy for low-end devices
    this.optimizationStrategies.set('low-end', {
      modelCompression: 'aggressive',
      quantization: 'int4',
      batchSize: 1,
      cacheStrategy: 'conservative',
      parallelInference: false,
      webGLAcceleration: false,
      maxModelSize: 10 * 1024 * 1024, // 10MB
      preloadModels: 1
    })

    // Battery-aware strategy
    this.optimizationStrategies.set('battery-saver', {
      modelCompression: 'aggressive',
      quantization: 'int4',
      batchSize: 1,
      cacheStrategy: 'minimal',
      parallelInference: false,
      webGLAcceleration: false,
      maxModelSize: 5 * 1024 * 1024, // 5MB
      preloadModels: 1,
      inferenceThrottling: true,
      maxInferencesPerMinute: 10
    })
  }

  getOptimizationStrategy() {
    // Check battery level for battery-saver mode
    if (this.deviceCapabilities.battery?.level < 0.2 && !this.deviceCapabilities.battery.charging) {
      return this.optimizationStrategies.get('battery-saver')
    }

    // Use device class strategy
    return this.optimizationStrategies.get(this.deviceCapabilities.deviceClass) || 
           this.optimizationStrategies.get('low-end')
  }

  async optimizeModel(modelId, modelData, metadata) {
    const strategy = this.getOptimizationStrategy()
    const startTime = performance.now()

    try {
      let optimizedData = modelData

      // Apply model compression
      if (strategy.modelCompression !== 'minimal') {
        optimizedData = await this.compressModel(optimizedData, strategy.modelCompression)
      }

      // Apply quantization
      if (strategy.quantization !== 'fp32') {
        optimizedData = await this.quantizeModel(optimizedData, strategy.quantization)
      }

      // Create optimized metadata
      const optimizedMetadata = {
        ...metadata,
        optimizationStrategy: strategy,
        originalSize: modelData.byteLength,
        optimizedSize: optimizedData.byteLength,
        compressionRatio: modelData.byteLength / optimizedData.byteLength,
        optimizationTime: performance.now() - startTime,
        targetDevice: this.deviceCapabilities.deviceClass
      }

      // Cache optimized model
      this.optimizedModels.set(modelId, {
        data: optimizedData,
        metadata: optimizedMetadata,
        strategy: strategy
      })

      console.log(`Model ${modelId} optimized:`, {
        originalSize: Math.round(modelData.byteLength / 1024) + 'KB',
        optimizedSize: Math.round(optimizedData.byteLength / 1024) + 'KB',
        compressionRatio: optimizedMetadata.compressionRatio.toFixed(2)
      })

      return {
        success: true,
        optimizedData,
        metadata: optimizedMetadata
      }
    } catch (error) {
      console.error('Model optimization failed:', error)
      return {
        success: false,
        error: error.message,
        fallbackData: modelData,
        metadata
      }
    }
  }

  async compressModel(modelData, compressionLevel) {
    // Simulate different compression levels
    // In a real implementation, this would use actual model compression techniques
    
    const compressionRatios = {
      'minimal': 0.95,
      'moderate': 0.7,
      'aggressive': 0.4
    }

    const ratio = compressionRatios[compressionLevel] || 0.7
    const compressedSize = Math.floor(modelData.byteLength * ratio)
    
    // Simulate compression by creating a smaller buffer
    // In reality, this would involve actual model pruning, weight sharing, etc.
    const compressedData = new ArrayBuffer(compressedSize)
    const sourceView = new Uint8Array(modelData)
    const targetView = new Uint8Array(compressedData)
    
    // Copy essential data (simplified simulation)
    const step = Math.ceil(sourceView.length / targetView.length)
    for (let i = 0; i < targetView.length; i++) {
      targetView[i] = sourceView[i * step] || 0
    }

    return compressedData
  }

  async quantizeModel(modelData, quantizationType) {
    // Simulate quantization
    // Real implementation would convert weights to lower precision
    
    const quantizationReductions = {
      'fp16': 0.9,  // 16-bit floating point
      'int8': 0.75, // 8-bit integer
      'int4': 0.6   // 4-bit integer
    }

    const reduction = quantizationReductions[quantizationType] || 0.8
    const quantizedSize = Math.floor(modelData.byteLength * reduction)
    
    // Create quantized buffer
    const quantizedData = new ArrayBuffer(quantizedSize)
    const sourceView = new Uint8Array(modelData)
    const targetView = new Uint8Array(quantizedData)
    
    // Simple quantization simulation
    for (let i = 0; i < targetView.length; i++) {
      const sourceIndex = Math.floor((i / targetView.length) * sourceView.length)
      targetView[i] = sourceView[sourceIndex] || 0
    }

    return quantizedData
  }

  createInferenceEngine(modelId, optimizedModel) {
    const strategy = optimizedModel.strategy
    
    return {
      modelId,
      strategy,
      
      async predict(input) {
        const startTime = performance.now()
        
        try {
          // Throttle inference if in battery-saver mode
          if (strategy.inferenceThrottling) {
            await this.checkInferenceThrottle(modelId)
          }

          // Batch processing optimization
          const batchedInput = this.prepareBatchedInput(input, strategy.batchSize)
          
          // Perform inference (simulated)
          const result = await this.performOptimizedInference(
            modelId, 
            batchedInput, 
            optimizedModel, 
            strategy
          )
          
          const inferenceTime = performance.now() - startTime
          this.recordPerformanceMetric(modelId, inferenceTime)
          
          return {
            ...result,
            inferenceTime,
            strategy: strategy,
            optimized: true
          }
        } catch (error) {
          console.error('Optimized inference failed:', error)
          throw error
        }
      }
    }
  }

  async checkInferenceThrottle(modelId) {
    const now = Date.now()
    const key = `throttle_${modelId}`
    
    if (!this.performanceMetrics.has(key)) {
      this.performanceMetrics.set(key, { requests: [], limit: 10 })
    }

    const throttleData = this.performanceMetrics.get(key)
    const oneMinuteAgo = now - 60000

    // Remove old requests
    throttleData.requests = throttleData.requests.filter(time => time > oneMinuteAgo)

    // Check if limit exceeded
    if (throttleData.requests.length >= throttleData.limit) {
      const waitTime = 60000 - (now - throttleData.requests[0])
      if (waitTime > 0) {
        await new Promise(resolve => setTimeout(resolve, waitTime))
      }
    }

    // Record this request
    throttleData.requests.push(now)
  }

  prepareBatchedInput(input, batchSize) {
    if (batchSize === 1 || !Array.isArray(input)) {
      return input
    }

    // Group inputs into batches for more efficient processing
    const batches = []
    for (let i = 0; i < input.length; i += batchSize) {
      batches.push(input.slice(i, i + batchSize))
    }
    
    return batches
  }

  async performOptimizedInference(modelId, input, optimizedModel, strategy) {
    // Simulate optimized inference based on model type and strategy
    const metadata = optimizedModel.metadata
    const baseLatency = this.calculateBaseLatency(metadata.domain, strategy)
    
    // Add some realistic variance
    const latency = baseLatency * (0.8 + Math.random() * 0.4)
    
    // Simulate inference delay
    await new Promise(resolve => setTimeout(resolve, latency))

    // Generate results based on model domain
    switch (metadata.domain) {
      case 'fraud_detection':
        return this.simulateOptimizedFraudDetection(input, strategy)
      case 'image_variance':
        return this.simulateOptimizedImageVariance(input, strategy)
      case 'regional_nlp':
        return this.simulateOptimizedRegionalNLP(input, strategy)
      case 'anomaly_detection':
        return this.simulateOptimizedAnomalyDetection(input, strategy)
      default:
        return { prediction: 'unknown', confidence: 0.5, optimized: true }
    }
  }

  calculateBaseLatency(domain, strategy) {
    const baseLatencies = {
      'fraud_detection': 100,
      'image_variance': 200,
      'regional_nlp': 150,
      'anomaly_detection': 120
    }

    const base = baseLatencies[domain] || 150
    
    // Apply strategy multipliers
    const strategyMultipliers = {
      'high-end': 0.7,
      'mid-range': 1.0,
      'low-end': 1.5,
      'battery-saver': 2.0
    }

    const deviceMultiplier = strategyMultipliers[this.deviceCapabilities.deviceClass] || 1.0
    
    return base * deviceMultiplier
  }

  simulateOptimizedFraudDetection(input, strategy) {
    const baseConfidence = 0.8 + Math.random() * 0.15
    const optimizationPenalty = strategy.quantization === 'int4' ? 0.05 : 0.02
    
    return {
      prediction: baseConfidence > 0.7 ? 'fraud' : 'legitimate',
      confidence: Math.max(0.5, baseConfidence - optimizationPenalty),
      riskFactors: ['optimized_model_detection'],
      optimizationLevel: strategy.modelCompression
    }
  }

  simulateOptimizedImageVariance(input, strategy) {
    const baseAccuracy = 0.85 + Math.random() * 0.1
    const optimizationPenalty = strategy.modelCompression === 'aggressive' ? 0.08 : 0.03
    
    return {
      prediction: baseAccuracy > 0.75 ? 'significant_variance' : 'acceptable_variance',
      confidence: Math.max(0.6, baseAccuracy - optimizationPenalty),
      processingMode: 'edge_optimized',
      qualityScore: Math.max(0.7, 0.95 - optimizationPenalty)
    }
  }

  simulateOptimizedRegionalNLP(input, strategy) {
    const baseAccuracy = 0.82 + Math.random() * 0.12
    const optimizationPenalty = strategy.quantization === 'int4' ? 0.1 : 0.05
    
    return {
      prediction: baseAccuracy > 0.7 ? 'compliant' : 'non_compliant',
      confidence: Math.max(0.5, baseAccuracy - optimizationPenalty),
      processingSpeed: strategy.batchSize > 1 ? 'batched' : 'single',
      languageSupport: 'optimized_multilingual'
    }
  }

  simulateOptimizedAnomalyDetection(input, strategy) {
    const baseSensitivity = 0.78 + Math.random() * 0.15
    const optimizationPenalty = strategy.modelCompression === 'aggressive' ? 0.07 : 0.04
    
    return {
      prediction: baseSensitivity > 0.75 ? 'anomaly' : 'normal',
      confidence: Math.max(0.5, baseSensitivity - optimizationPenalty),
      detectionMode: 'edge_anomaly_detection',
      resourceEfficiency: strategy.modelCompression
    }
  }

  recordPerformanceMetric(modelId, inferenceTime) {
    const key = `perf_${modelId}`
    
    if (!this.performanceMetrics.has(key)) {
      this.performanceMetrics.set(key, { 
        times: [], 
        averageTime: 0,
        minTime: Infinity,
        maxTime: 0
      })
    }

    const metrics = this.performanceMetrics.get(key)
    metrics.times.push(inferenceTime)
    
    // Keep only last 100 measurements
    if (metrics.times.length > 100) {
      metrics.times = metrics.times.slice(-100)
    }

    // Update statistics
    metrics.averageTime = metrics.times.reduce((a, b) => a + b, 0) / metrics.times.length
    metrics.minTime = Math.min(metrics.minTime, inferenceTime)
    metrics.maxTime = Math.max(metrics.maxTime, inferenceTime)
  }

  getPerformanceMetrics(modelId) {
    const key = `perf_${modelId}`
    return this.performanceMetrics.get(key) || null
  }

  getOptimizedModel(modelId) {
    return this.optimizedModels.get(modelId)
  }

  getDeviceCapabilities() {
    return { ...this.deviceCapabilities }
  }

  getCurrentStrategy() {
    return this.getOptimizationStrategy()
  }

  async adaptToConditions() {
    // Re-assess device capabilities if battery status changed significantly
    if (this.deviceCapabilities.battery?.supported) {
      const currentBattery = await this.getBatteryInfo()
      const batteryChange = Math.abs(currentBattery.level - this.deviceCapabilities.battery.level)
      
      if (batteryChange > 0.1) { // 10% change
        this.deviceCapabilities.battery = currentBattery
        console.log('Adapting optimization strategy due to battery change:', currentBattery.level)
      }
    }

    // Adapt based on current performance
    const avgPerformance = this.calculateAveragePerformance()
    if (avgPerformance.degraded) {
      console.log('Performance degradation detected, switching to more aggressive optimization')
      return this.optimizationStrategies.get('battery-saver')
    }

    return this.getOptimizationStrategy()
  }

  calculateAveragePerformance() {
    const allMetrics = Array.from(this.performanceMetrics.values())
      .filter(metric => metric.averageTime !== undefined)
    
    if (allMetrics.length === 0) {
      return { averageTime: 0, degraded: false }
    }

    const overallAverage = allMetrics.reduce((sum, metric) => sum + metric.averageTime, 0) / allMetrics.length
    const degraded = overallAverage > 1000 // More than 1 second average

    return { averageTime: overallAverage, degraded }
  }
}

// Initialize Edge Computing Optimizer
const edgeOptimizer = new EdgeComputingOptimizer()

// Make it globally available
window.edgeOptimizer = edgeOptimizer

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = EdgeComputingOptimizer
}

console.log('Edge Computing Optimizer loaded')