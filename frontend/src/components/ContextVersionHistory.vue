<template>
  <div class="context-version-history">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-medium flex items-center gap-2">
        <History class="w-5 h-5 text-gray-500" />
        Version History
      </h3>
      <Button variant="ghost" size="sm" @click="$emit('close')">
        <X class="w-4 h-4" />
      </Button>
    </div>
    
    <!-- Loading state -->
    <div v-if="isLoading" class="py-8 text-center">
      <Spinner class="mx-auto" />
      <div class="text-sm text-gray-500 mt-2">Loading history...</div>
    </div>
    
    <!-- Empty state -->
    <div v-else-if="!versions?.length" class="py-8 text-center">
      <History class="w-12 h-12 mx-auto text-gray-300" />
      <div class="text-sm text-gray-500 mt-2">No version history available</div>
    </div>
    
    <!-- Version timeline -->
    <div v-else class="relative">
      <!-- Compare mode toggle -->
      <div v-if="versions.length > 1" class="mb-4 flex items-center gap-2">
        <input
          type="checkbox"
          id="compareMode"
          v-model="compareMode"
          class="rounded border-gray-300"
        />
        <label for="compareMode" class="text-sm text-gray-600">
          Compare versions
        </label>
      </div>
      
      <!-- Version list -->
      <div class="space-y-4">
        <div
          v-for="(version, index) in versions"
          :key="version.name"
          class="relative pl-6"
        >
          <!-- Timeline line -->
          <div 
            v-if="index < versions.length - 1"
            class="absolute left-2 top-6 bottom-0 w-0.5 bg-gray-200"
          ></div>
          
          <!-- Timeline dot -->
          <div 
            :class="[
              'absolute left-0 top-2 w-4 h-4 rounded-full border-2',
              index === 0 
                ? 'bg-blue-500 border-blue-500' 
                : 'bg-white border-gray-300'
            ]"
          ></div>
          
          <!-- Version card -->
          <div 
            :class="[
              'border rounded-lg p-3 transition-colors',
              selectedVersions.includes(version.name)
                ? 'border-blue-500 bg-blue-50'
                : 'hover:bg-gray-50'
            ]"
          >
            <div class="flex items-start justify-between">
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-medium">v{{ version.version_number }}</span>
                  <span v-if="index === 0" class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                    Latest
                  </span>
                </div>
                <div class="text-sm text-gray-500">
                  {{ formatDate(version.creation) }}
                </div>
                <div v-if="version.created_by" class="text-xs text-gray-400 mt-1">
                  by {{ version.created_by }}
                </div>
              </div>
              
              <div class="flex items-center gap-1">
                <!-- Compare checkbox -->
                <input
                  v-if="compareMode"
                  type="checkbox"
                  :checked="selectedVersions.includes(version.name)"
                  @change="toggleVersionSelection(version.name)"
                  :disabled="!selectedVersions.includes(version.name) && selectedVersions.length >= 2"
                  class="rounded border-gray-300"
                />
                
                <!-- View button -->
                <Button 
                  v-else
                  variant="ghost" 
                  size="sm"
                  @click="viewVersion(version)"
                >
                  <Eye class="w-4 h-4" />
                </Button>
              </div>
            </div>
            
            <!-- Version preview -->
            <div 
              v-if="expandedVersion === version.name" 
              class="mt-3 pt-3 border-t"
            >
              <div class="text-xs text-gray-500 mb-2">Context snapshot:</div>
              <pre class="text-xs bg-gray-100 p-2 rounded overflow-auto max-h-40">{{ formatContext(version.context_data) }}</pre>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Compare button -->
      <div v-if="compareMode && selectedVersions.length === 2" class="mt-4">
        <Button variant="solid" class="w-full" @click="compareSelectedVersions">
          <GitCompare class="w-4 h-4 mr-1" />
          Compare Selected Versions
        </Button>
      </div>
      
      <!-- Comparison view -->
      <div v-if="comparisonData" class="mt-4 border rounded-lg p-4">
        <div class="flex items-center justify-between mb-3">
          <h4 class="font-medium">Version Comparison</h4>
          <Button variant="ghost" size="sm" @click="comparisonData = null">
            <X class="w-4 h-4" />
          </Button>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <div class="text-sm font-medium mb-2">
              v{{ comparisonData.version1?.version_number }}
            </div>
            <pre class="text-xs bg-gray-100 p-2 rounded overflow-auto max-h-60">{{ formatContext(comparisonData.version1?.context_data) }}</pre>
          </div>
          <div>
            <div class="text-sm font-medium mb-2">
              v{{ comparisonData.version2?.version_number }}
            </div>
            <pre class="text-xs bg-gray-100 p-2 rounded overflow-auto max-h-60">{{ formatContext(comparisonData.version2?.context_data) }}</pre>
          </div>
        </div>
        
        <!-- Summary of changes -->
        <div class="mt-3 pt-3 border-t">
          <div class="text-sm font-medium mb-2">Summary</div>
          <div class="text-sm text-gray-600">
            <div v-if="comparisonData.added_keys?.length">
              <span class="text-green-600">Added:</span> {{ comparisonData.added_keys.join(', ') }}
            </div>
            <div v-if="comparisonData.removed_keys?.length">
              <span class="text-red-600">Removed:</span> {{ comparisonData.removed_keys.join(', ') }}
            </div>
            <div v-if="comparisonData.modified_keys?.length">
              <span class="text-yellow-600">Modified:</span> {{ comparisonData.modified_keys.join(', ') }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button, Spinner } from 'frappe-ui'
import { History, Eye, X, GitCompare } from 'lucide-vue-next'
import { createResource } from 'frappe-ui'

const props = defineProps({
  pageType: {
    type: String,
    required: true
  },
  documentId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'restore'])

const isLoading = ref(true)
const versions = ref([])
const compareMode = ref(false)
const selectedVersions = ref([])
const expandedVersion = ref(null)
const comparisonData = ref(null)

// Fetch version history
const fetchVersionHistory = createResource({
  url: 'mkaguzi.api.ai_specialist.get_context_version_history',
  makeParams: () => ({
    page_type: props.pageType,
    document_id: props.documentId
  }),
  onSuccess: (data) => {
    versions.value = data.versions || []
    isLoading.value = false
  },
  onError: () => {
    isLoading.value = false
  }
})

// Compare versions
const compareVersionsResource = createResource({
  url: 'mkaguzi.api.ai_specialist.compare_context_versions',
  onSuccess: (data) => {
    comparisonData.value = data
  }
})

onMounted(() => {
  fetchVersionHistory.fetch()
})

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString()
}

const formatContext = (contextData) => {
  if (typeof contextData === 'string') {
    try {
      return JSON.stringify(JSON.parse(contextData), null, 2)
    } catch {
      return contextData
    }
  }
  return JSON.stringify(contextData, null, 2)
}

const viewVersion = (version) => {
  if (expandedVersion.value === version.name) {
    expandedVersion.value = null
  } else {
    expandedVersion.value = version.name
  }
}

const toggleVersionSelection = (versionName) => {
  const index = selectedVersions.value.indexOf(versionName)
  if (index > -1) {
    selectedVersions.value.splice(index, 1)
  } else if (selectedVersions.value.length < 2) {
    selectedVersions.value.push(versionName)
  }
}

const compareSelectedVersions = () => {
  if (selectedVersions.value.length === 2) {
    compareVersionsResource.fetch({
      version_id_1: selectedVersions.value[0],
      version_id_2: selectedVersions.value[1]
    })
  }
}
</script>

<style scoped>
.context-version-history {
  max-height: 80vh;
  overflow-y: auto;
}
</style>
