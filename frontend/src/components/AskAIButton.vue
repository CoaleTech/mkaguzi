<template>
  <div class="ai-ask-button-wrapper">
    <Button
      :variant="variant"
      :size="size"
      :loading="isLoading"
      :disabled="disabled"
      @click="handleAskAI"
      class="ai-ask-button"
      v-bind="$attrs"
    >
      <template #prefix>
        <component :is="iconComponent" :class="iconClass" />
      </template>
      {{ buttonText }}
    </Button>
    
    <!-- Context depth dropdown -->
    <Dropdown v-if="showDepthSelector" :options="depthOptions" placement="bottom-end">
      <template #default="{ togglePopover }">
        <Button
          variant="ghost"
          size="sm"
          @click="togglePopover"
          class="ml-1"
        >
          <Settings class="w-3 h-3" />
        </Button>
      </template>
    </Dropdown>
    
    <!-- Share button -->
    <Button
      v-if="showShareButton"
      variant="ghost"
      size="sm"
      @click="showShareModal = true"
      class="ml-1"
    >
      <Share2 class="w-4 h-4" />
    </Button>
    
    <!-- Suggestions indicator -->
    <div 
      v-if="showSuggestions && suggestions.length > 0" 
      class="suggestions-badge"
      @click="showSuggestionsPanel = !showSuggestionsPanel"
    >
      <Lightbulb class="w-3 h-3" />
      {{ suggestions.length }}
    </div>
    
    <!-- Multi-context indicator -->
    <Button
      v-if="enableMultiContext"
      variant="ghost"
      size="sm"
      @click="toggleMultiContext"
      :class="{ 'active': isInMultiContext }"
      class="ml-1"
    >
      <Layers class="w-4 h-4" />
      <span v-if="multiContextCount > 0" class="context-count">{{ multiContextCount }}</span>
    </Button>
    
    <!-- Share Modal -->
    <ShareContextModal
      v-if="showShareModal"
      :pageType="pageType"
      :documentId="documentId"
      @close="showShareModal = false"
      @shared="onContextShared"
    />
    
    <!-- Suggestions Panel -->
    <LearnedSuggestions
      v-if="showSuggestionsPanel && showSuggestions"
      :suggestions="suggestions"
      @select="onSuggestionSelected"
      @close="showSuggestionsPanel = false"
    />
  </div>
</template>

<script setup>
import { Button, Dropdown } from 'frappe-ui'
import { Brain, MessageSquare, Sparkles, Settings, Share2, Lightbulb, Layers } from 'lucide-vue-next'
import { useAIContext } from '@/composables/useAIContext'
import { useAIContextStore } from '@/stores/useAIContextStore'
import { computed, ref, watch, onMounted } from 'vue'
import ShareContextModal from './ShareContextModal.vue'
import LearnedSuggestions from './LearnedSuggestions.vue'

const props = defineProps({
  // Context data to collect
  contextData: {
    type: Object,
    default: () => ({})
  },
  // Page component name for context collection
  pageComponent: {
    type: String,
    default: ''
  },
  // Document ID for enriched context
  documentId: {
    type: String,
    default: ''
  },
  // Page type for enriched context
  pageType: {
    type: String,
    default: ''
  },
  // Context depth (summary, detailed, full, comprehensive)
  contextDepth: {
    type: String,
    default: 'detailed'
  },
  // Template ID to apply
  templateId: {
    type: String,
    default: ''
  },
  // Button variant
  variant: {
    type: String,
    default: 'solid'
  },
  // Button size
  size: {
    type: String,
    default: 'sm'
  },
  // Button theme
  theme: {
    type: String,
    default: 'blue'
  },
  // Custom button text
  buttonText: {
    type: String,
    default: 'Ask AI'
  },
  // Custom icon
  icon: {
    type: String,
    default: 'brain'
  },
  // Disabled state
  disabled: {
    type: Boolean,
    default: false
  },
  // Show context summary tooltip
  showTooltip: {
    type: Boolean,
    default: true
  },
  // Show share button
  showShareButton: {
    type: Boolean,
    default: false
  },
  // Show learned suggestions
  showSuggestions: {
    type: Boolean,
    default: false
  },
  // Enable multi-context mode
  enableMultiContext: {
    type: Boolean,
    default: false
  },
  // Show depth selector
  showDepthSelector: {
    type: Boolean,
    default: false
  },
  // Use enriched context API
  useEnrichedContext: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['context-collected', 'ai-navigated', 'error', 'shared', 'suggestion-selected', 'multi-context-toggled'])

const { collectPageContext, navigateToAISpecialist, fetchEnrichedContext, getLearnedSuggestions, addToMultiContextSession } = useAIContext()
const aiContextStore = useAIContextStore()

const isLoading = ref(false)
const showShareModal = ref(false)
const showSuggestionsPanel = ref(false)
const selectedDepth = ref(props.contextDepth)
const suggestions = ref([])
const isInMultiContext = ref(false)
const multiContextCount = ref(0)

// Icon mapping
const iconMap = {
  brain: Brain,
  message: MessageSquare,
  sparkles: Sparkles
}

const iconComponent = computed(() => iconMap[props.icon] || Brain)
const iconClass = computed(() => `w-${props.size === 'sm' ? 4 : 5} h-${props.size === 'sm' ? 4 : 5}`)

// Depth options for dropdown
const depthOptions = [
  { label: 'Summary', value: 'summary', description: 'Basic metrics and status' },
  { label: 'Detailed', value: 'detailed', description: 'Main document with child tables' },
  { label: 'Full', value: 'full', description: 'Complete with related documents' },
  { label: 'Comprehensive', value: 'comprehensive', description: 'Full plus analytics and trends' }
].map(opt => ({
  ...opt,
  onClick: () => {
    selectedDepth.value = opt.value
  }
}))

// Load suggestions on mount
onMounted(async () => {
  if (props.showSuggestions && props.pageType) {
    try {
      const result = await getLearnedSuggestions(props.pageType, props.documentId)
      if (result?.suggestions) {
        suggestions.value = result.suggestions
      }
    } catch (err) {
      console.error('Failed to load suggestions:', err)
    }
  }
  
  // Check if already in multi-context
  if (props.enableMultiContext) {
    const session = aiContextStore.multiContextSession
    if (session) {
      isInMultiContext.value = session.contexts.some(
        c => c.page_type === props.pageType && c.document_id === props.documentId
      )
      multiContextCount.value = session.contexts.length
    }
  }
})

// Watch for multi-context changes
watch(() => aiContextStore.multiContextSession, (session) => {
  if (session) {
    isInMultiContext.value = session.contexts.some(
      c => c.page_type === props.pageType && c.document_id === props.documentId
    )
    multiContextCount.value = session.contexts.length
  } else {
    isInMultiContext.value = false
    multiContextCount.value = 0
  }
}, { deep: true })

const handleAskAI = async () => {
  if (props.disabled) return

  isLoading.value = true

  try {
    let context
    
    // Use enriched context API if enabled and we have page type
    if (props.useEnrichedContext && props.pageType) {
      const enrichedResult = await fetchEnrichedContext(
        props.pageType,
        props.documentId,
        selectedDepth.value,
        props.templateId
      )
      
      if (enrichedResult?.success) {
        context = {
          page_type: props.pageType,
          page_title: props.contextData?.title || props.pageType,
          context_data: enrichedResult.context_data,
          metadata: enrichedResult.metadata,
          depth: enrichedResult.depth
        }
      }
    }
    
    // Fallback to legacy context collection
    if (!context) {
      context = await collectPageContext(
        { __name: props.pageComponent },
        props.contextData
      )
    }

    if (context) {
      // Store context in the global store
      aiContextStore.setContext(context)

      // Save to localStorage for persistence
      const contextKey = aiContextStore.saveContextToStorage(context)

      emit('context-collected', { context, contextKey })

      // Navigate to AI Specialist
      navigateToAISpecialist(context)

      emit('ai-navigated', { context, contextKey })
    } else {
      throw new Error('Failed to collect page context')
    }
  } catch (error) {
    console.error('Error in Ask AI:', error)
    emit('error', error)
  } finally {
    isLoading.value = false
  }
}

const toggleMultiContext = async () => {
  if (isInMultiContext.value) {
    // Remove from session
    await aiContextStore.removeFromMultiContextSession(props.pageType, props.documentId)
    isInMultiContext.value = false
  } else {
    // Add to session
    const result = await addToMultiContextSession(props.pageType, props.documentId)
    if (result?.success) {
      isInMultiContext.value = true
    }
  }
  emit('multi-context-toggled', { isInMultiContext: isInMultiContext.value })
}

const onContextShared = (shareInfo) => {
  showShareModal.value = false
  emit('shared', shareInfo)
}

const onSuggestionSelected = async (suggestion) => {
  showSuggestionsPanel.value = false
  emit('suggestion-selected', suggestion)
  
  // Navigate to suggested context
  if (suggestion.page_type) {
    await navigateToSuggestedContext(suggestion)
  }
}

const navigateToSuggestedContext = async (suggestion) => {
  // This would navigate to the suggested page type
  // Implementation depends on your routing structure
  console.log('Navigate to suggestion:', suggestion)
}
</script>

<style scoped>
.ai-ask-button-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.ai-ask-button {
  position: relative;
}

.ai-ask-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.ai-ask-button:disabled {
  transform: none;
  box-shadow: none;
}

.suggestions-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: #fef3c7;
  color: #92400e;
  border-radius: 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestions-badge:hover {
  background: #fde68a;
}

.context-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: #3b82f6;
  color: white;
  border-radius: 8px;
  font-size: 10px;
  margin-left: 4px;
}

.active {
  background: #dbeafe;
  color: #1d4ed8;
}
</style>