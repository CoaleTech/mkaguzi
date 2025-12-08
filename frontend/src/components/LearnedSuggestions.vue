<template>
  <div class="learned-suggestions">
    <div class="flex items-center justify-between mb-3">
      <h4 class="text-sm font-medium flex items-center gap-2">
        <Lightbulb class="w-4 h-4 text-yellow-500" />
        AI Suggestions
      </h4>
      <Button variant="ghost" size="sm" @click="refreshSuggestions">
        <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': isLoading }" />
      </Button>
    </div>
    
    <!-- Loading state -->
    <div v-if="isLoading" class="py-4 text-center">
      <Spinner class="mx-auto w-5 h-5" />
      <div class="text-xs text-gray-500 mt-1">Analyzing patterns...</div>
    </div>
    
    <!-- Empty state -->
    <div v-else-if="!suggestions?.length && !affinities?.length" class="py-4 text-center">
      <Lightbulb class="w-8 h-8 mx-auto text-gray-300" />
      <div class="text-xs text-gray-500 mt-1">
        No suggestions yet. Use AI more to get personalized recommendations.
      </div>
    </div>
    
    <!-- Suggestions list -->
    <div v-else class="space-y-3">
      <!-- Context suggestions -->
      <div v-if="suggestions?.length" class="space-y-2">
        <div class="text-xs text-gray-500 font-medium">Recommended Contexts</div>
        <div
          v-for="suggestion in suggestions"
          :key="suggestion.context_key"
          class="p-2 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
          @click="applySuggestion(suggestion)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="text-sm font-medium">{{ suggestion.context_label }}</div>
              <div class="text-xs text-gray-500">{{ suggestion.reason }}</div>
            </div>
            <div class="flex items-center gap-1">
              <span 
                class="text-xs px-1.5 py-0.5 rounded"
                :class="getConfidenceClass(suggestion.confidence)"
              >
                {{ Math.round(suggestion.confidence * 100) }}%
              </span>
              <ArrowRight class="w-3 h-3 text-gray-400" />
            </div>
          </div>
          
          <!-- Explanation (optional) -->
          <div v-if="showExplanations && suggestion.explanation" class="mt-2 pt-2 border-t border-gray-200">
            <div class="text-xs text-gray-600 italic">
              <Info class="w-3 h-3 inline mr-1" />
              {{ suggestion.explanation }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- User affinities -->
      <div v-if="affinities?.length" class="space-y-2">
        <div class="text-xs text-gray-500 font-medium">Your Preferences</div>
        <div class="flex flex-wrap gap-2">
          <div
            v-for="affinity in topAffinities"
            :key="affinity.context_key"
            class="flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-700 rounded-full text-xs"
          >
            <Star class="w-3 h-3" />
            {{ affinity.context_label }}
            <span class="text-blue-500">({{ affinity.usage_count }}x)</span>
          </div>
        </div>
      </div>
      
      <!-- Learned patterns -->
      <div v-if="patterns?.length" class="space-y-2">
        <div class="text-xs text-gray-500 font-medium">Detected Patterns</div>
        <div class="space-y-1">
          <div
            v-for="pattern in patterns"
            :key="pattern.name"
            class="text-xs p-2 bg-purple-50 rounded flex items-start gap-2"
          >
            <TrendingUp class="w-3 h-3 text-purple-500 mt-0.5" />
            <div>
              <span class="font-medium text-purple-700">{{ pattern.pattern_type }}:</span>
              <span class="text-purple-600 ml-1">{{ pattern.description }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Toggle explanations -->
    <div class="mt-3 pt-2 border-t">
      <label class="flex items-center gap-2 text-xs text-gray-500 cursor-pointer">
        <input 
          type="checkbox" 
          v-model="showExplanations"
          class="rounded border-gray-300 w-3 h-3"
        />
        Show reasoning
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button, Spinner } from 'frappe-ui'
import { Lightbulb, RefreshCw, ArrowRight, Star, TrendingUp, Info } from 'lucide-vue-next'
import { createResource } from 'frappe-ui'

const props = defineProps({
  pageType: {
    type: String,
    required: true
  },
  documentId: {
    type: String,
    default: ''
  },
  maxSuggestions: {
    type: Number,
    default: 5
  }
})

const emit = defineEmits(['apply'])

const isLoading = ref(true)
const suggestions = ref([])
const affinities = ref([])
const patterns = ref([])
const showExplanations = ref(false)

// Top affinities (limit to 5)
const topAffinities = computed(() => {
  return affinities.value.slice(0, 5)
})

// Get suggestions resource
const suggestionsResource = createResource({
  url: 'mkaguzi.api.ai_specialist.get_learned_context_suggestions',
  makeParams: () => ({
    current_page_type: props.pageType,
    current_document_id: props.documentId,
    limit: props.maxSuggestions
  }),
  onSuccess: (data) => {
    if (data.success) {
      suggestions.value = data.suggestions || []
    }
  }
})

// Get user affinities resource
const affinitiesResource = createResource({
  url: 'mkaguzi.api.ai_specialist.get_user_affinities',
  onSuccess: (data) => {
    if (data.success) {
      affinities.value = data.affinities || []
    }
  }
})

// Get learned patterns resource
const patternsResource = createResource({
  url: 'mkaguzi.api.ai_specialist.analyze_context_patterns',
  makeParams: () => ({
    page_type: props.pageType
  }),
  onSuccess: (data) => {
    if (data.success) {
      patterns.value = data.patterns || []
    }
  }
})

onMounted(async () => {
  await refreshSuggestions()
})

const refreshSuggestions = async () => {
  isLoading.value = true
  try {
    await Promise.all([
      suggestionsResource.fetch(),
      affinitiesResource.fetch(),
      patternsResource.fetch()
    ])
  } finally {
    isLoading.value = false
  }
}

const applySuggestion = (suggestion) => {
  emit('apply', {
    pageType: suggestion.context_key.split(':')[0],
    documentId: suggestion.context_key.split(':')[1] || '',
    label: suggestion.context_label,
    confidence: suggestion.confidence
  })
}

const getConfidenceClass = (confidence) => {
  if (confidence >= 0.8) return 'bg-green-100 text-green-700'
  if (confidence >= 0.5) return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-600'
}
</script>

<style scoped>
.learned-suggestions {
  font-size: 14px;
}
</style>
