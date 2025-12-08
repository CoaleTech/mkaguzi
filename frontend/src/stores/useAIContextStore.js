/**
 * AI Context Store
 * Pinia store for managing AI context across the application
 * Enhanced with versioning, collaboration, learning, and analytics support
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { call } from 'frappe-ui'

export const useAIContextStore = defineStore('aiContext', () => {
  // Core State
  const currentContext = ref(null)
  const contextHistory = ref([])
  const isContextLoading = ref(false)
  const contextError = ref(null)

  // Enhanced State - Versioning
  const contextVersions = ref([])
  const currentVersionId = ref(null)
  const isVersionLoading = ref(false)

  // Enhanced State - Collaboration
  const collaborationSession = ref(null)
  const collaborationParticipants = ref([])
  const isCollaborating = ref(false)

  // Enhanced State - Learning
  const learnedSuggestions = ref([])
  const userAffinities = ref([])
  const isLearningEnabled = ref(true)

  // Enhanced State - Multi-Context
  const multiContextSession = ref(null)
  const sessionContexts = ref([])

  // Enhanced State - Templates
  const availableTemplates = ref([])
  const activeTemplate = ref(null)

  // Enhanced State - Metadata
  const contextMetadata = ref({
    lastFetched: null,
    contextHash: null,
    contextDepth: 'standard',
    isCompressed: false,
    fetchDuration: 0
  })

  // Computed
  const hasActiveContext = computed(() => !!currentContext.value)
  const contextType = computed(() => currentContext.value?.page_type || 'none')
  const contextTitle = computed(() => {
    if (!currentContext.value) return 'No Context'

    switch (currentContext.value.page_type) {
      case 'vat_reconciliation':
        return `VAT Reconciliation: ${currentContext.value.reconciliation_name || 'Unknown'}`
      case 'risk_assessment':
        return `Risk Assessment: ${currentContext.value.assessment_name || 'Unknown'}`
      case 'audit_universe':
        return `Audit Universe: ${currentContext.value.entity_name || 'Unknown'}`
      case 'audit_finding':
        return `Finding: ${currentContext.value.finding_title || 'Unknown'}`
      case 'dashboard':
        return 'Dashboard Overview'
      default:
        return currentContext.value.page_title || 'Page Context'
    }
  })

  const contextSummary = computed(() => {
    if (!currentContext.value) return null

    switch (currentContext.value.page_type) {
      case 'vat_reconciliation':
        return {
          icon: 'FileText',
          metrics: [
            { label: 'Match Rate', value: `${currentContext.value.match_percentage?.toFixed(1) || 0}%` },
            { label: 'Total Records', value: (currentContext.value.total_matched || 0) + (currentContext.value.total_unmatched_source_a || 0) + (currentContext.value.total_unmatched_source_b || 0) + (currentContext.value.total_amount_discrepancies || 0) },
            { label: 'Discrepancies', value: currentContext.value.total_amount_discrepancies || 0 }
          ]
        }
      case 'risk_assessment':
        return {
          icon: 'AlertTriangle',
          metrics: [
            { label: 'Total Risks', value: currentContext.value.risk_register_count || 0 },
            { label: 'High Risk', value: currentContext.value.high_risk_count || 0 },
            { label: 'Critical Risk', value: currentContext.value.critical_risk_count || 0 }
          ]
        }
      case 'audit_universe':
        return {
          icon: 'Target',
          metrics: [
            { label: 'Risk Rating', value: currentContext.value.risk_rating || 'Unknown' },
            { label: 'Open Findings', value: currentContext.value.open_findings || 0 },
            { label: 'Last Audit', value: currentContext.value.last_audit_date ? new Date(currentContext.value.last_audit_date).toLocaleDateString() : 'Never' }
          ]
        }
      case 'audit_finding':
        return {
          icon: 'CheckCircle',
          metrics: [
            { label: 'Risk Level', value: currentContext.value.risk_level || 'Unknown' },
            { label: 'Status', value: currentContext.value.status || 'Unknown' },
            { label: 'Category', value: currentContext.value.category || 'Unknown' }
          ]
        }
      case 'dashboard':
        return {
          icon: 'LayoutDashboard',
          metrics: [
            { label: 'Total Entities', value: currentContext.value.total_entities || 0 },
            { label: 'Open Findings', value: currentContext.value.open_findings || 0 },
            { label: 'Compliance Score', value: `${currentContext.value.compliance_score || 0}%` }
          ]
        }
      case 'annual_plan':
        return {
          icon: 'Calendar',
          metrics: [
            { label: 'Plan Year', value: currentContext.value.plan_year || 'Unknown' },
            { label: 'Total Audits', value: currentContext.value.total_audits || 0 },
            { label: 'High Risk Areas', value: currentContext.value.high_risk_count || 0 }
          ]
        }
      case 'stock-take':
        return {
          icon: 'Package',
          metrics: [
            { label: 'Total Items', value: currentContext.value.total_items || 0 },
            { label: 'Items with Variance', value: currentContext.value.items_with_variance || 0 },
            { label: 'Variance %', value: `${(currentContext.value.variance_percentage || 0).toFixed(1)}%` }
          ]
        }
      case 'variance-case':
        return {
          icon: 'TrendingUp',
          metrics: [
            { label: 'Variance Qty', value: currentContext.value.variance_quantity || 0 },
            { label: 'Variance Value', value: `$${(currentContext.value.variance_value || 0).toFixed(2)}` },
            { label: 'Priority', value: currentContext.value.priority || 'Unknown' }
          ]
        }
      case 'engagement':
        return {
          icon: 'Briefcase',
          metrics: [
            { label: 'Status', value: currentContext.value.status || 'Unknown' },
            { label: 'Type', value: currentContext.value.type || 'Unknown' },
            { label: 'Findings', value: currentContext.value.findings_summary?.total || 0 }
          ]
        }
      case 'audit-plan':
        return {
          icon: 'ClipboardList',
          metrics: [
            { label: 'Status', value: currentContext.value.status || 'Unknown' },
            { label: 'Sessions', value: currentContext.value.sessions_summary?.total || 0 },
            { label: 'Risk Items', value: currentContext.value.risk_assessment?.total_risk_items || 0 }
          ]
        }
      default:
        return {
          icon: 'File',
          metrics: [
            { label: 'Page Type', value: currentContext.value.page_type || 'Unknown' },
            { label: 'Data Points', value: Object.keys(currentContext.value.data_summary || {}).length }
          ]
        }
    }
  })

  // Actions
  const setContext = (context) => {
    currentContext.value = context
    contextError.value = null

    // Add to history
    if (context) {
      contextHistory.value.unshift({
        ...context,
        id: Date.now(),
        timestamp: new Date().toISOString()
      })

      // Keep only last 10 contexts
      if (contextHistory.value.length > 10) {
        contextHistory.value = contextHistory.value.slice(0, 10)
      }
    }
  }

  const clearContext = () => {
    currentContext.value = null
    contextError.value = null
  }

  const loadContextFromStorage = (contextKey) => {
    try {
      isContextLoading.value = true
      const stored = localStorage.getItem(contextKey)
      if (stored) {
        const context = JSON.parse(stored)
        setContext(context)
        return context
      }
    } catch (error) {
      contextError.value = `Failed to load context: ${error.message}`
      console.error('Error loading context from storage:', error)
    } finally {
      isContextLoading.value = false
    }
    return null
  }

  const saveContextToStorage = (context, key = null) => {
    try {
      const contextKey = key || `ai_context_${Date.now()}`
      localStorage.setItem(contextKey, JSON.stringify(context))
      return contextKey
    } catch (error) {
      contextError.value = `Failed to save context: ${error.message}`
      console.error('Error saving context to storage:', error)
      return null
    }
  }

  const removeContextFromStorage = (contextKey) => {
    try {
      localStorage.removeItem(contextKey)
    } catch (error) {
      console.error('Error removing context from storage:', error)
    }
  }

  const getContextForAI = () => {
    if (!currentContext.value) return null

    // Return context in format expected by AI backend
    return {
      page_type: currentContext.value.page_type,
      page_title: contextTitle.value,
      context_data: currentContext.value,
      collected_at: currentContext.value.collected_at,
      route_info: {
        name: currentContext.value.route_name,
        path: currentContext.value.route_path
      }
    }
  }

  const getSuggestedQuestions = (contextType) => {
    const questions = {
      'vat_reconciliation': [
        'What are the main issues with this reconciliation?',
        'Why is the match rate so low?',
        'Can you analyze the largest discrepancies?',
        'What recommendations do you have for improving this reconciliation?',
        'Are there any patterns in the unmatched records?'
      ],
      'risk_assessment': [
        'What are the highest risk items that need attention?',
        'How can we mitigate these risks?',
        'Are there any risk concentrations I should be aware of?',
        'What additional controls might be needed?',
        'How does this assessment compare to industry standards?'
      ],
      'audit_universe': [
        'Which entities should be prioritized for audit?',
        'What is the risk-based audit plan for next year?',
        'Are there any entities that need immediate attention?',
        'How can we optimize our audit resource allocation?',
        'What are the key risk indicators for these entities?'
      ],
      'audit_finding': [
        'Is this finding adequately documented?',
        'What additional evidence might be needed?',
        'Are the recommendations appropriate for the risk level?',
        'How should this finding be communicated?',
        'What follow-up actions are required?'
      ],
      'dashboard': [
        'What are the most critical issues requiring attention?',
        'How are we trending compared to last period?',
        'Which areas need immediate focus?',
        'What insights can you provide from this data?',
        'Are there any concerning patterns emerging?'
      ],
      'annual_plan': [
        'Is this audit plan comprehensive enough?',
        'Which areas should be prioritized for audit?',
        'Are the resource allocations appropriate?',
        'What risks are we not adequately covering?',
        'How does this plan compare to previous years?',
        'Are there any gaps in our audit coverage?'
      ],
      'stock-take': [
        'What are the main causes of these inventory variances?',
        'Which items need immediate investigation?',
        'Are there patterns in the variances I should be aware of?',
        'What control weaknesses might have caused these discrepancies?',
        'How should we address the high-value variances?',
        'What preventive measures can we implement?'
      ],
      'variance-case': [
        'What is the most likely root cause of this variance?',
        'Is this variance indicative of a larger control issue?',
        'What evidence should we collect to investigate this further?',
        'Are there similar variances in other items or locations?',
        'What corrective actions would you recommend?',
        'Should this be escalated for further investigation?'
      ],
      'engagement': [
        'Is the audit scope appropriate for the engagement objectives?',
        'What additional testing procedures should we consider?',
        'Are there any high-risk areas that need more attention?',
        'How should we allocate our audit resources effectively?',
        'What are the key risks to our audit opinion?',
        'Are we on track to meet our engagement deadlines?'
      ],
      'audit-plan': [
        'Is this audit plan comprehensive enough for the identified risks?',
        'What additional audit procedures should we include?',
        'Are the resource allocations appropriate for the plan scope?',
        'Which risk areas need more detailed testing?',
        'How should we prioritize the audit sessions?',
        'Are there any gaps in our audit coverage?'
      ],
      'default': [
        'What insights can you provide from this data?',
        'Are there any issues I should be aware of?',
        'What recommendations do you have?',
        'Can you help me analyze this information?',
        'What questions should I be asking about this data?'
      ]
    }
    return questions[contextType] || questions.default
  }

  // ==========================================
  // Enhanced Actions - Versioning
  // ==========================================

  const fetchVersionHistory = async (pageType, documentId = null) => {
    isVersionLoading.value = true
    try {
      const result = await call('mkaguzi.api.ai_specialist.get_context_version_history', {
        page_type: pageType,
        document_id: documentId
      })
      if (result.success) {
        contextVersions.value = result.versions || []
      }
    } catch (error) {
      console.error('Failed to fetch version history:', error)
    } finally {
      isVersionLoading.value = false
    }
  }

  const createVersion = async (pageType, documentId = null) => {
    if (!currentContext.value) return null
    try {
      const result = await call('mkaguzi.api.ai_specialist.save_context_version', {
        page_type: pageType,
        document_id: documentId,
        context_data: JSON.stringify(currentContext.value)
      })
      if (result.success) {
        currentVersionId.value = result.version_id
        await fetchVersionHistory(pageType, documentId)
        return result.version_id
      }
    } catch (error) {
      console.error('Failed to create version:', error)
    }
    return null
  }

  const loadVersion = async (versionId) => {
    try {
      const result = await call('mkaguzi.api.ai_specialist.get_context_version', {
        version_id: versionId
      })
      if (result.success && result.version) {
        let contextData = result.version.context_data
        if (typeof contextData === 'string') {
          contextData = JSON.parse(contextData)
        }
        currentContext.value = contextData
        currentVersionId.value = versionId
        return contextData
      }
    } catch (error) {
      console.error('Failed to load version:', error)
    }
    return null
  }

  // ==========================================
  // Enhanced Actions - Collaboration
  // ==========================================

  const startCollaboration = async (pageType, documentId = null) => {
    try {
      const sessionId = `collab_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      const result = await call('mkaguzi.api.ai_specialist.join_collaborative_session', {
        session_id: sessionId,
        page_type: pageType,
        document_id: documentId
      })
      if (result.success) {
        collaborationSession.value = {
          id: sessionId,
          pageType,
          documentId,
          startedAt: new Date().toISOString()
        }
        isCollaborating.value = true
        return sessionId
      }
    } catch (error) {
      console.error('Failed to start collaboration:', error)
    }
    return null
  }

  const endCollaboration = () => {
    collaborationSession.value = null
    collaborationParticipants.value = []
    isCollaborating.value = false
  }

  const refreshParticipants = async () => {
    if (!collaborationSession.value?.id) return
    try {
      const result = await call('mkaguzi.api.ai_specialist.get_session_participants', {
        session_id: collaborationSession.value.id
      })
      if (result.success) {
        collaborationParticipants.value = result.participants || []
      }
    } catch (error) {
      console.error('Failed to refresh participants:', error)
    }
  }

  // ==========================================
  // Enhanced Actions - Learning
  // ==========================================

  const fetchSuggestions = async (pageType, documentId = null) => {
    if (!isLearningEnabled.value) return
    try {
      const result = await call('mkaguzi.api.ai_specialist.get_learned_context_suggestions', {
        current_page_type: pageType,
        current_document_id: documentId,
        limit: 5
      })
      if (result.success) {
        learnedSuggestions.value = result.suggestions || []
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error)
    }
  }

  const fetchUserAffinities = async () => {
    try {
      const result = await call('mkaguzi.api.ai_specialist.get_user_affinities')
      if (result.success) {
        userAffinities.value = result.affinities || []
      }
    } catch (error) {
      console.error('Failed to fetch user affinities:', error)
    }
  }

  const recordUsage = async (pageType, documentId = null, feedback = null) => {
    if (!isLearningEnabled.value) return
    try {
      // Analytics tracking records usage internally
      await call('mkaguzi.api.ai_specialist.get_context_analytics', {
        page_type: pageType,
        document_id: documentId
      })
    } catch (error) {
      console.warn('Failed to record usage:', error)
    }
  }

  const toggleLearning = (enabled) => {
    isLearningEnabled.value = enabled
  }

  // ==========================================
  // Enhanced Actions - Multi-Context
  // ==========================================

  const createMultiContextSession = async () => {
    try {
      const result = await call('mkaguzi.api.ai_specialist.create_multi_context_session', {})
      if (result.success) {
        multiContextSession.value = result.session_id
        sessionContexts.value = []
        return result.session_id
      }
    } catch (error) {
      console.error('Failed to create multi-context session:', error)
    }
    return null
  }

  const addToSession = async (pageType, documentId = null) => {
    if (!multiContextSession.value) {
      await createMultiContextSession()
    }
    try {
      const result = await call('mkaguzi.api.ai_specialist.add_context_to_session', {
        session_id: multiContextSession.value,
        page_type: pageType,
        document_id: documentId
      })
      if (result.success) {
        sessionContexts.value = result.contexts || []
        return true
      }
    } catch (error) {
      console.error('Failed to add to session:', error)
    }
    return false
  }

  const removeFromSession = async (index) => {
    if (!multiContextSession.value) return false
    try {
      const result = await call('mkaguzi.api.ai_specialist.remove_context_from_session', {
        session_id: multiContextSession.value,
        context_index: index
      })
      if (result.success) {
        sessionContexts.value = result.contexts || []
        return true
      }
    } catch (error) {
      console.error('Failed to remove from session:', error)
    }
    return false
  }

  const clearMultiContextSession = async () => {
    if (!multiContextSession.value) return
    try {
      // Clear by removing each context - no dedicated clear API
      for (let i = sessionContexts.value.length - 1; i >= 0; i--) {
        await call('mkaguzi.api.ai_specialist.remove_context_from_session', {
          session_id: multiContextSession.value,
          page_type: sessionContexts.value[i].page_type,
          document_id: sessionContexts.value[i].document_id
        })
      }
      sessionContexts.value = []
    } catch (error) {
      console.error('Failed to clear session:', error)
    }
  }

  // ==========================================
  // Enhanced Actions - Templates
  // ==========================================

  const fetchTemplates = async (pageType = null) => {
    try {
      const result = await call('mkaguzi.api.ai_specialist.list_context_templates', {
        page_type: pageType
      })
      if (result.success) {
        availableTemplates.value = result.templates || []
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error)
    }
  }

  const applyTemplate = async (templateId) => {
    try {
      const result = await call('mkaguzi.api.ai_specialist.get_context_template', {
        template_id: templateId
      })
      if (result.success) {
        activeTemplate.value = result.template
        return result.template
      }
    } catch (error) {
      console.error('Failed to apply template:', error)
    }
    return null
  }

  const clearTemplate = () => {
    activeTemplate.value = null
  }

  // ==========================================
  // Enhanced Actions - Metadata
  // ==========================================

  const updateMetadata = (metadata) => {
    contextMetadata.value = {
      ...contextMetadata.value,
      ...metadata
    }
  }

  const setContextDepth = (depth) => {
    contextMetadata.value.contextDepth = depth
  }

  return {
    // Core State
    currentContext,
    contextHistory,
    isContextLoading,
    contextError,

    // Enhanced State - Versioning
    contextVersions,
    currentVersionId,
    isVersionLoading,

    // Enhanced State - Collaboration
    collaborationSession,
    collaborationParticipants,
    isCollaborating,

    // Enhanced State - Learning
    learnedSuggestions,
    userAffinities,
    isLearningEnabled,

    // Enhanced State - Multi-Context
    multiContextSession,
    sessionContexts,

    // Enhanced State - Templates
    availableTemplates,
    activeTemplate,

    // Enhanced State - Metadata
    contextMetadata,

    // Computed
    hasActiveContext,
    contextType,
    contextTitle,
    contextSummary,

    // Core Actions
    setContext,
    clearContext,
    loadContextFromStorage,
    saveContextToStorage,
    removeContextFromStorage,
    getContextForAI,
    getSuggestedQuestions,

    // Versioning Actions
    fetchVersionHistory,
    createVersion,
    loadVersion,

    // Collaboration Actions
    startCollaboration,
    endCollaboration,
    refreshParticipants,

    // Learning Actions
    fetchSuggestions,
    fetchUserAffinities,
    recordUsage,
    toggleLearning,

    // Multi-Context Actions
    createMultiContextSession,
    addToSession,
    removeFromSession,
    clearMultiContextSession,

    // Template Actions
    fetchTemplates,
    applyTemplate,
    clearTemplate,

    // Metadata Actions
    updateMetadata,
    setContextDepth
  }
})