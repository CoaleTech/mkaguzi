/**
 * AI Context Management Composable
 * Provides functionality to collect, manage, and pass context data to AI Specialist
 * Enhanced with enriched context API, versioning, templates, and analytics
 */

import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource, call } from 'frappe-ui'

// Lazy load pako for decompression
let pakoModule = null
const loadPako = async () => {
  if (!pakoModule) {
    try {
      pakoModule = await import('pako')
    } catch (e) {
      console.warn('pako not available, compression disabled')
    }
  }
  return pakoModule
}

// Context collectors for different page types
const contextCollectors = {
  // VAT Reconciliation context
  'VATReconciliationDetail': (pageData) => ({
    page_type: 'vat_reconciliation',
    ...pageData // pageData is already the processed context from getVATReconciliationContext()
  }),

  // VAT Reconciliation List context
  'VATReconciliation': (pageData) => ({
    page_type: 'vat_reconciliation_list',
    ...pageData // pageData is already the processed context from getVATReconciliationListContext()
  }),

  // Risk Assessment context
  'RiskAssessmentDetail': (pageData) => ({
    page_type: 'risk_assessment',
    ...pageData // pageData is already the processed context from getRiskAssessmentContext()
  }),

  // Audit Universe context
  'AuditUniverseDetail': (pageData) => ({
    page_type: 'audit_universe',
    ...pageData // pageData is already the processed context from getAuditUniverseContext()
  }),

  // Annual Plan context
  'AnnualPlanDetail': (pageData) => ({
    page_type: 'annual_plan',
    ...pageData // pageData is already the processed context from getAnnualPlanContext()
  }),

  // Findings context
  'FindingDetail': (pageData) => ({
    page_type: 'audit_finding',
    ...pageData // pageData is already the processed context from getFindingContext()
  }),

  // Dashboard context
  'Dashboard': (pageData) => ({
    page_type: 'dashboard',
    ...pageData // pageData is already the processed context from getDashboardContext()
  }),

  // Stock Take Detail collector
  'StockTakeDetail': (pageData) => ({
    page_type: 'stock-take',
    ...pageData // pageData is already the processed context from getStockTakeContext()
  }),

  // Variance Case Detail collector
  'VarianceCaseDetail': (pageData) => ({
    page_type: 'variance-case',
    ...pageData // pageData is already the processed context from getVarianceCaseContext()
  }),

  // Engagement Detail collector
  'EngagementDetail': (pageData) => ({
    page_type: 'engagement',
    ...pageData // pageData is already the processed context from getEngagementContext()
  }),

  // Audit Plan Detail collector
  'AuditPlanDetail': (pageData) => ({
    page_type: 'audit-plan',
    ...pageData // pageData is already the processed context from getAuditPlanContext()
  }),

  // Default context collector
  'default': (pageData) => ({
    page_type: 'generic',
    page_title: pageData.pageTitle || 'Unknown Page',
    page_description: pageData.pageDescription || 'No specific context available',
    data_summary: pageData.dataSummary || {}
  })
}

export function useAIContext() {
  const route = useRoute()
  const router = useRouter()

  // Reactive state
  const currentContext = ref(null)
  const contextHistory = ref([])
  const isCollectingContext = ref(false)

  // Computed properties
  const hasContext = computed(() => !!currentContext.value)
  const contextType = computed(() => currentContext.value?.page_type || 'none')
  const contextSummary = computed(() => {
    if (!currentContext.value) return 'No context loaded'

    switch (currentContext.value.page_type) {
      case 'vat_reconciliation':
        return `VAT Reconciliation: ${currentContext.value.reconciliation_name} (${currentContext.value.match_percentage?.toFixed(1)}% match rate)`
      case 'vat_reconciliation_list':
        return `VAT Reconciliation Overview: ${currentContext.value.total_reconciliations} total reconciliations (${currentContext.value.average_match_rate}% avg match rate)`
      case 'risk_assessment':
        return `Risk Assessment: ${currentContext.value.assessment_name} (${currentContext.value.total_risks} risks identified)`
      case 'audit_universe':
        return `Audit Universe: ${currentContext.value.entity_name} (${currentContext.value.risk_rating} risk)`
      case 'audit_finding':
        return `Audit Finding: ${currentContext.value.finding_title} (${currentContext.value.risk_level} risk)`
      case 'dashboard':
        return `Dashboard: ${currentContext.value.total_entities} entities, ${currentContext.value.open_findings} open findings`
      default:
        return `Page: ${currentContext.value.page_title || 'Unknown'}`
    }
  })

  // Methods
  const collectPageContext = async (pageComponent, pageData = {}) => {
    isCollectingContext.value = true

    try {
      // Determine page type from component name or route
      const pageType = pageComponent?.__name || pageComponent?.name || route.name || 'default'
      const collector = contextCollectors[pageType] || contextCollectors.default

      // Collect context
      const context = {
        ...collector(pageData),
        collected_at: new Date().toISOString(),
        route_name: route.name,
        route_path: route.path,
        page_component: pageType
      }

      currentContext.value = context

      // Add to history
      contextHistory.value.unshift({
        ...context,
        id: Date.now()
      })

      // Keep only last 10 contexts
      if (contextHistory.value.length > 10) {
        contextHistory.value = contextHistory.value.slice(0, 10)
      }

      return context
    } catch (error) {
      console.error('Error collecting page context:', error)
      return null
    } finally {
      isCollectingContext.value = false
    }
  }

  const navigateToAISpecialist = (context = null) => {
    // Use provided context or current context
    const contextToUse = context || currentContext.value

    if (contextToUse) {
      // Store context in localStorage with a unique key
      const contextKey = `ai_context_${Date.now()}`
      localStorage.setItem(contextKey, JSON.stringify(contextToUse))

      // Navigate to AI Specialist with context reference
      router.push({
        name: 'AISpecialist',
        query: {
          context: contextKey,
          type: contextToUse.page_type
        }
      })
    } else {
      // Navigate without context
      router.push({ name: 'AISpecialist' })
    }
  }

  const loadContextFromStorage = (contextKey) => {
    try {
      const stored = localStorage.getItem(contextKey)
      if (stored) {
        const context = JSON.parse(stored)
        currentContext.value = context
        return context
      }
    } catch (error) {
      console.error('Error loading context from storage:', error)
    }
    return null
  }

  const clearContext = () => {
    currentContext.value = null
  }

  const getSuggestedCapability = (contextType) => {
    const suggestions = {
      'vat_reconciliation': 'insights',
      'risk_assessment': 'risk-analysis',
      'audit_universe': 'audit-planning',
      'audit_finding': 'finding-review',
      'dashboard': 'insights',
      'annual_plan': 'audit-planning',
      'stock-take': 'insights',
      'variance-case': 'insights',
      'engagement': 'audit-planning',
      'audit-plan': 'audit-planning',
      'default': 'insights'
    }
    return suggestions[contextType] || 'insights'
  }

  const getContextPrompt = (contextType) => {
    const prompts = {
      'vat_reconciliation': 'I have VAT reconciliation data loaded. I can help analyze discrepancies, match rates, and provide recommendations for improving the reconciliation process.',
      'risk_assessment': 'I have risk assessment data loaded. I can help evaluate risk levels, suggest mitigation strategies, and provide risk management recommendations.',
      'audit_universe': 'I have audit universe data loaded. I can help with audit planning, risk prioritization, and resource allocation recommendations.',
      'audit_finding': 'I have audit finding details loaded. I can help review the finding, assess its adequacy, and suggest improvements.',
      'dashboard': 'I have dashboard overview data loaded. I can help analyze trends, identify areas needing attention, and provide strategic recommendations.',
      'annual_plan': 'I have annual audit plan data loaded. I can help evaluate plan comprehensiveness, prioritize audit areas, assess resource allocation, and identify coverage gaps.',
      'stock-take': 'I have stock take audit data loaded. I can help analyze inventory variances, identify root causes, assess control weaknesses, and recommend corrective actions.',
      'variance-case': 'I have inventory variance case data loaded. I can help analyze the variance, identify potential root causes, assess investigation needs, and recommend corrective actions.',
      'engagement': 'I have audit engagement data loaded. I can help evaluate engagement scope, assess risk areas, recommend testing procedures, and provide audit planning guidance.',
      'audit-plan': 'I have audit plan data loaded. I can help evaluate plan comprehensiveness, assess risk coverage, recommend additional procedures, and provide audit execution guidance.',
      'default': 'I have page context data loaded. I can help analyze the information and provide relevant insights.'
    }
    return prompts[contextType] || prompts.default
  }

  // ==========================================
  // Enriched Context API Functions
  // ==========================================

  /**
   * Fetch enriched context from the backend API with caching, compression, and delta support
   * @param {string} pageType - Type of page/context
   * @param {string} documentId - Document identifier (optional)
   * @param {object} options - Additional options (depth, template, etc.)
   */
  const fetchEnrichedContext = async (pageType, documentId = null, options = {}) => {
    const {
      contextDepth = 'standard',
      templateId = null,
      previousHash = null,
      compress = true,
      enableLearning = true
    } = options

    try {
      isCollectingContext.value = true

      const result = await call('mkaguzi.api.ai_specialist.get_enriched_context', {
        page_type: pageType,
        document_id: documentId,
        context_depth: contextDepth,
        template_id: templateId,
        previous_hash: previousHash,
        compress
      })

      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch enriched context')
      }

      // Handle delta response
      if (result.is_delta) {
        // Merge delta changes with existing context
        if (currentContext.value) {
          currentContext.value = {
            ...currentContext.value,
            ...result.changes
          }
        }
        lastContextHash.value = result.context_hash
        return currentContext.value
      }

      // Handle compressed response
      let contextData = result.context
      if (result.compressed) {
        const pako = await loadPako()
        if (pako) {
          const binaryString = atob(contextData)
          const bytes = new Uint8Array(binaryString.length)
          for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i)
          }
          const decompressed = pako.inflate(bytes, { to: 'string' })
          contextData = JSON.parse(decompressed)
        }
      }

      // Store context and hash
      currentContext.value = contextData
      lastContextHash.value = result.context_hash

      // Record usage for learning
      if (enableLearning) {
        recordContextUsage(pageType, documentId)
      }

      return contextData
    } catch (error) {
      console.error('Error fetching enriched context:', error)
      throw error
    } finally {
      isCollectingContext.value = false
    }
  }

  /**
   * Record context usage for AI learning
   */
  const recordContextUsage = async (pageType, documentId = null, feedback = null) => {
    try {
      // Use analytics tracking which records usage internally
      await call('mkaguzi.api.ai_specialist.get_context_analytics', {
        page_type: pageType,
        document_id: documentId
      })
    } catch (error) {
      console.warn('Failed to record context usage:', error)
    }
  }

  /**
   * Get AI suggestions based on learned patterns
   */
  const getContextSuggestions = async (pageType, documentId = null, limit = 5) => {
    try {
      const result = await call('mkaguzi.api.ai_specialist.get_learned_context_suggestions', {
        current_page_type: pageType,
        current_document_id: documentId,
        limit
      })
      return result.suggestions || []
    } catch (error) {
      console.error('Failed to get suggestions:', error)
      return []
    }
  }

  /**
   * Create a context version snapshot
   */
  const createContextVersion = async (pageType, documentId = null) => {
    if (!currentContext.value) return null

    try {
      const result = await call('mkaguzi.api.ai_specialist.save_context_version', {
        page_type: pageType,
        document_id: documentId,
        context_data: JSON.stringify(currentContext.value)
      })
      return result
    } catch (error) {
      console.error('Failed to create version:', error)
      return null
    }
  }

  /**
   * Get context version history
   */
  const getContextVersionHistory = async (pageType, documentId = null, limit = 10) => {
    try {
      const result = await call('mkaguzi.api.ai_specialist.get_context_version_history', {
        page_type: pageType,
        document_id: documentId,
        limit
      })
      return result.versions || []
    } catch (error) {
      console.error('Failed to get version history:', error)
      return []
    }
  }

  /**
   * Apply a context template
   */
  const applyContextTemplate = async (templateId) => {
    try {
      const result = await call('mkaguzi.api.ai_specialist.get_context_template', {
        template_id: templateId
      })
      if (result.success) {
        return result.template
      }
      return null
    } catch (error) {
      console.error('Failed to apply template:', error)
      return null
    }
  }

  /**
   * Share context with another user
   */
  const shareContext = async (pageType, documentId = null, message = '', expiresInHours = 24) => {
    try {
      const result = await call('mkaguzi.api.ai_specialist.share_context', {
        page_type: pageType,
        document_id: documentId,
        message,
        expires_in_hours: expiresInHours
      })
      return result
    } catch (error) {
      console.error('Failed to share context:', error)
      return { success: false, error: error.message }
    }
  }

  /**
   * Track context access for analytics
   */
  const trackContextAccess = async (pageType, documentId = null, action = 'view') => {
    try {
      await call('mkaguzi.api.ai_specialist.track_context_access', {
        page_type: pageType,
        document_id: documentId,
        action
      })
    } catch (error) {
      console.warn('Failed to track access:', error)
    }
  }

  // Additional state for enhanced features
  const lastContextHash = ref(null)

  return {
    // State
    currentContext,
    contextHistory,
    isCollectingContext,
    lastContextHash,

    // Computed
    hasContext,
    contextType,
    contextSummary,

    // Core Methods
    collectPageContext,
    navigateToAISpecialist,
    loadContextFromStorage,
    clearContext,
    getSuggestedCapability,
    getContextPrompt,

    // Enriched Context API
    fetchEnrichedContext,
    recordContextUsage,
    getContextSuggestions,
    createContextVersion,
    getContextVersionHistory,
    applyContextTemplate,
    shareContext,
    trackContextAccess
  }
}