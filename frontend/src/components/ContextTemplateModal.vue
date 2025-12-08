<template>
  <Dialog v-model="isOpen" @close="$emit('close')">
    <template #body-title>
      <div class="flex items-center gap-2">
        <FileText class="w-5 h-5 text-purple-500" />
        <span>Context Templates</span>
      </div>
    </template>
    
    <template #body-content>
      <div class="space-y-4">
        <!-- Create new template toggle -->
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700">
            {{ isCreating ? 'Create New Template' : 'Select Template' }}
          </span>
          <Button variant="ghost" size="sm" @click="isCreating = !isCreating">
            {{ isCreating ? 'Browse Templates' : 'Create New' }}
          </Button>
        </div>
        
        <!-- Create new template form -->
        <div v-if="isCreating" class="space-y-3 p-4 border rounded-lg">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Template Name
            </label>
            <Input
              v-model="newTemplate.name"
              placeholder="e.g., Monthly VAT Review"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <Textarea
              v-model="newTemplate.description"
              placeholder="Describe when to use this template..."
              rows="2"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Page Type
            </label>
            <Select v-model="newTemplate.page_type" :options="pageTypeOptions" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Context Depth
            </label>
            <Select v-model="newTemplate.context_depth" :options="depthOptions" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Prompt Template
            </label>
            <Textarea
              v-model="newTemplate.prompt_template"
              placeholder="Initial prompt or instructions for AI..."
              rows="3"
            />
          </div>
          
          <div class="flex items-center gap-2">
            <input
              type="checkbox"
              id="isPublic"
              v-model="newTemplate.is_public"
              class="rounded border-gray-300"
            />
            <label for="isPublic" class="text-sm text-gray-600">
              Make this template available to all users
            </label>
          </div>
          
          <Button 
            variant="solid" 
            class="w-full mt-2"
            :loading="isCreatingTemplate"
            @click="createTemplate"
          >
            Create Template
          </Button>
        </div>
        
        <!-- Browse templates -->
        <div v-else class="space-y-2">
          <!-- Loading state -->
          <div v-if="templatesResource.loading" class="py-8 text-center">
            <Spinner class="mx-auto" />
            <div class="text-sm text-gray-500 mt-2">Loading templates...</div>
          </div>
          
          <!-- Empty state -->
          <div v-else-if="!templates?.length" class="py-8 text-center">
            <FileText class="w-12 h-12 mx-auto text-gray-300" />
            <div class="text-sm text-gray-500 mt-2">No templates available</div>
            <Button variant="subtle" size="sm" class="mt-2" @click="isCreating = true">
              Create your first template
            </Button>
          </div>
          
          <!-- Template list -->
          <div v-else class="max-h-80 overflow-y-auto space-y-2">
            <div
              v-for="template in templates"
              :key="template.name"
              :class="[
                'p-3 border rounded-lg cursor-pointer transition-colors',
                selectedTemplate?.name === template.name
                  ? 'border-blue-500 bg-blue-50'
                  : 'hover:bg-gray-50'
              ]"
              @click="selectedTemplate = template"
            >
              <div class="flex items-start justify-between">
                <div>
                  <div class="font-medium">{{ template.template_name }}</div>
                  <div class="text-sm text-gray-500">{{ template.description }}</div>
                </div>
                <div class="flex items-center gap-1">
                  <span v-if="template.is_public" class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                    Public
                  </span>
                  <span class="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                    {{ template.context_depth }}
                  </span>
                </div>
              </div>
              
              <!-- Template preview when selected -->
              <div v-if="selectedTemplate?.name === template.name" class="mt-2 pt-2 border-t">
                <div class="text-xs text-gray-500 mb-1">Prompt Template:</div>
                <div class="text-sm bg-gray-100 p-2 rounded">
                  {{ template.prompt_template || 'No prompt template defined' }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Error message -->
        <div v-if="error" class="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
          {{ error }}
        </div>
      </div>
    </template>
    
    <template #actions>
      <Button variant="subtle" @click="$emit('close')">
        Cancel
      </Button>
      <Button 
        v-if="!isCreating && selectedTemplate"
        variant="solid"
        @click="applyTemplate"
      >
        Apply Template
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Dialog, Button, Textarea, Select, Input, Spinner } from 'frappe-ui'
import { FileText } from 'lucide-vue-next'
import { createResource } from 'frappe-ui'

const props = defineProps({
  pageType: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'apply'])

const isOpen = ref(true)
const isCreating = ref(false)
const isCreatingTemplate = ref(false)
const selectedTemplate = ref(null)
const error = ref('')

// New template form data
const newTemplate = ref({
  name: '',
  description: '',
  page_type: props.pageType || 'vat_reconciliation',
  context_depth: 'standard',
  prompt_template: '',
  is_public: false
})

// Page type options
const pageTypeOptions = [
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

// Context depth options
const depthOptions = [
  { label: 'Minimal (5 items)', value: 'minimal' },
  { label: 'Standard (10 items)', value: 'standard' },
  { label: 'Detailed (25 items)', value: 'detailed' },
  { label: 'Full (50 items)', value: 'full' }
]

// Fetch templates resource
const templatesResource = createResource({
  url: 'mkaguzi.api.ai_specialist.list_context_templates',
  makeParams: () => ({
    page_type: props.pageType || null
  }),
  auto: true
})

const templates = computed(() => templatesResource.data?.templates || [])

// Create template resource
const createTemplateResource = createResource({
  url: 'mkaguzi.api.ai_specialist.create_context_template',
  makeParams: () => ({
    template_name: newTemplate.value.name,
    description: newTemplate.value.description,
    page_type: newTemplate.value.page_type,
    context_depth: newTemplate.value.context_depth,
    prompt_template: newTemplate.value.prompt_template,
    is_public: newTemplate.value.is_public
  }),
  onSuccess: (data) => {
    if (data.success) {
      // Reset form
      newTemplate.value = {
        name: '',
        description: '',
        page_type: props.pageType || 'vat_reconciliation',
        context_depth: 'standard',
        prompt_template: '',
        is_public: false
      }
      isCreating.value = false
      // Refresh templates list
      templatesResource.fetch()
    } else {
      error.value = data.error || 'Failed to create template'
    }
    isCreatingTemplate.value = false
  },
  onError: (err) => {
    error.value = err.message || 'Failed to create template'
    isCreatingTemplate.value = false
  }
})

const createTemplate = async () => {
  if (!newTemplate.value.name) {
    error.value = 'Template name is required'
    return
  }
  isCreatingTemplate.value = true
  error.value = ''
  await createTemplateResource.fetch()
}

const applyTemplate = () => {
  if (selectedTemplate.value) {
    emit('apply', {
      templateId: selectedTemplate.value.name,
      templateName: selectedTemplate.value.template_name,
      contextDepth: selectedTemplate.value.context_depth,
      promptTemplate: selectedTemplate.value.prompt_template
    })
    emit('close')
  }
}

// Watch for page type changes
watch(() => props.pageType, () => {
  templatesResource.fetch()
})
</script>
