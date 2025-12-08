<template>
  <div class="multi-context-panel bg-white border rounded-lg shadow-sm">
    <div class="flex items-center justify-between p-3 border-b">
      <h3 class="text-sm font-medium flex items-center gap-2">
        <Layers class="w-4 h-4 text-purple-500" />
        Multi-Context Session
      </h3>
      <div class="flex items-center gap-1">
        <Button variant="ghost" size="sm" @click="refreshSession">
          <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': isRefreshing }" />
        </Button>
        <Button variant="ghost" size="sm" @click="$emit('close')">
          <X class="w-4 h-4" />
        </Button>
      </div>
    </div>
    
    <div class="p-3 space-y-3">
      <!-- Session info -->
      <div v-if="sessionId" class="flex items-center justify-between text-xs">
        <span class="text-gray-500">Session: {{ sessionId.substring(0, 8) }}...</span>
        <span class="text-gray-400">{{ contexts.length }} context(s)</span>
      </div>
      
      <!-- Context list -->
      <div v-if="contexts.length > 0" class="space-y-2 max-h-60 overflow-y-auto">
        <div
          v-for="(ctx, index) in contexts"
          :key="index"
          class="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center gap-2">
            <div 
              :class="[
                'w-2 h-2 rounded-full',
                getContextTypeColor(ctx.page_type)
              ]"
            ></div>
            <div>
              <div class="text-sm font-medium">{{ getContextLabel(ctx.page_type) }}</div>
              <div v-if="ctx.document_id" class="text-xs text-gray-500">
                {{ ctx.document_id }}
              </div>
            </div>
          </div>
          <Button 
            variant="ghost" 
            size="sm"
            @click="removeContext(index)"
          >
            <Trash2 class="w-3 h-3 text-red-500" />
          </Button>
        </div>
      </div>
      
      <!-- Empty state -->
      <div v-else class="py-6 text-center">
        <Layers class="w-10 h-10 mx-auto text-gray-300" />
        <div class="text-sm text-gray-500 mt-2">No contexts in session</div>
        <div class="text-xs text-gray-400">Add contexts to compare or combine</div>
      </div>
      
      <!-- Add context -->
      <div class="pt-2 border-t">
        <div class="text-xs font-medium text-gray-500 mb-2">Add Context</div>
        <div class="flex gap-2">
          <Select 
            v-model="newContextType"
            :options="contextTypeOptions"
            class="flex-1"
            placeholder="Select type..."
          />
          <Button variant="solid" size="sm" @click="addCurrentContext">
            <Plus class="w-4 h-4" />
          </Button>
        </div>
        <Input
          v-if="newContextType && needsDocumentId"
          v-model="newDocumentId"
          placeholder="Document ID..."
          class="mt-2"
        />
      </div>
      
      <!-- Actions -->
      <div v-if="contexts.length > 0" class="pt-2 border-t flex gap-2">
        <Button 
          variant="subtle" 
          size="sm"
          class="flex-1"
          @click="clearSession"
        >
          Clear All
        </Button>
        <Button 
          variant="solid" 
          size="sm"
          class="flex-1"
          @click="combineAndAsk"
        >
          <MessageSquare class="w-4 h-4 mr-1" />
          Ask AI
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button, Select, Input } from 'frappe-ui'
import { Layers, X, Plus, Trash2, RefreshCw, MessageSquare } from 'lucide-vue-next'
import { createResource } from 'frappe-ui'

const props = defineProps({
  initialSessionId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'askAI', 'sessionUpdated'])

const sessionId = ref(props.initialSessionId)
const contexts = ref([])
const newContextType = ref('')
const newDocumentId = ref('')
const isRefreshing = ref(false)

// Context type configuration
const contextTypeOptions = [
  { label: 'VAT Reconciliation', value: 'vat_reconciliation' },
  { label: 'VAT Reconciliation List', value: 'vat_reconciliation_list' },
  { label: 'Risk Assessment', value: 'risk_assessment' },
  { label: 'Audit Finding', value: 'audit_finding' },
  { label: 'Audit Universe', value: 'audit_universe' },
  { label: 'Annual Audit Plan', value: 'annual_plan' },
  { label: 'Engagement', value: 'engagement' },
  { label: 'Stock Take Session', value: 'stock_take' },
  { label: 'Variance Case', value: 'variance_case' },
  { label: 'Dashboard', value: 'dashboard' }
]

const contextTypeColors = {
  vat_reconciliation: 'bg-blue-500',
  vat_reconciliation_list: 'bg-blue-400',
  risk_assessment: 'bg-red-500',
  audit_finding: 'bg-orange-500',
  audit_universe: 'bg-purple-500',
  annual_plan: 'bg-green-500',
  engagement: 'bg-indigo-500',
  stock_take: 'bg-cyan-500',
  variance_case: 'bg-yellow-500',
  dashboard: 'bg-gray-500'
}

const needsDocumentId = computed(() => {
  const listTypes = ['vat_reconciliation_list', 'dashboard']
  return newContextType.value && !listTypes.includes(newContextType.value)
})

// Manage session resource
const manageSessionResource = createResource({
  url: 'mkaguzi.api.ai_specialist.create_multi_context_session'
})

// Add context resource
const addContextResource = createResource({
  url: 'mkaguzi.api.ai_specialist.add_context_to_session'
})

// Remove context resource
const removeContextResource = createResource({
  url: 'mkaguzi.api.ai_specialist.remove_context_from_session'
})

// Get session contexts resource
const getContextsResource = createResource({
  url: 'mkaguzi.api.ai_specialist.get_multi_context_session'
})

onMounted(async () => {
  if (!sessionId.value) {
    // Create new session
    const result = await manageSessionResource.fetch({})
    if (result.success) {
      sessionId.value = result.session_id
      emit('sessionUpdated', sessionId.value)
    }
  } else {
    await refreshSession()
  }
})

const refreshSession = async () => {
  if (!sessionId.value) return
  
  isRefreshing.value = true
  try {
    const result = await getContextsResource.fetch({
      session_id: sessionId.value
    })
    if (result.success) {
      contexts.value = result.contexts || []
    }
  } finally {
    isRefreshing.value = false
  }
}

const addCurrentContext = async () => {
  if (!newContextType.value) return
  if (needsDocumentId.value && !newDocumentId.value) return
  
  const result = await addContextResource.fetch({
    session_id: sessionId.value,
    page_type: newContextType.value,
    document_id: newDocumentId.value || null
  })
  
  if (result.success) {
    contexts.value = result.contexts || []
    newContextType.value = ''
    newDocumentId.value = ''
  }
}

const removeContext = async (index) => {
  const ctx = contexts.value[index]
  const result = await removeContextResource.fetch({
    session_id: sessionId.value,
    page_type: ctx.page_type,
    document_id: ctx.document_id
  })
  
  if (result.success) {
    contexts.value = result.contexts || []
  }
}

const clearSession = async () => {
  // Remove all contexts one by one - no dedicated clear API
  for (let i = contexts.value.length - 1; i >= 0; i--) {
    const ctx = contexts.value[i]
    await removeContextResource.fetch({
      session_id: sessionId.value,
      page_type: ctx.page_type,
      document_id: ctx.document_id
    })
  }
  contexts.value = []
}

const combineAndAsk = () => {
  emit('askAI', {
    sessionId: sessionId.value,
    contexts: contexts.value
  })
}

const getContextLabel = (pageType) => {
  const option = contextTypeOptions.find(o => o.value === pageType)
  return option?.label || pageType
}

const getContextTypeColor = (pageType) => {
  return contextTypeColors[pageType] || 'bg-gray-400'
}
</script>

<style scoped>
.multi-context-panel {
  min-width: 300px;
}
</style>
