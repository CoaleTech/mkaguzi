<template>
  <Dialog v-model="isOpen" @close="$emit('close')">
    <template #body-title>
      <div class="flex items-center gap-2">
        <Share2 class="w-5 h-5 text-blue-500" />
        <span>Share Context</span>
      </div>
    </template>
    
    <template #body-content>
      <div class="space-y-4">
        <!-- Context info -->
        <div class="p-3 bg-gray-50 rounded-lg">
          <div class="text-sm text-gray-500">Sharing context for:</div>
          <div class="font-medium">{{ pageTypeLabel }}</div>
          <div v-if="documentId" class="text-sm text-gray-600">{{ documentId }}</div>
        </div>
        
        <!-- Message input -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Message (optional)
          </label>
          <Textarea
            v-model="message"
            placeholder="Add a note about this context..."
            rows="3"
          />
        </div>
        
        <!-- Expiry selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Link expires in
          </label>
          <Select v-model="expiryHours" :options="expiryOptions" />
        </div>
        
        <!-- Generated link (after sharing) -->
        <div v-if="shareUrl" class="p-3 bg-green-50 rounded-lg">
          <div class="flex items-center justify-between">
            <div class="text-sm text-green-700">Share link created!</div>
            <Button variant="ghost" size="sm" @click="copyLink">
              <Copy class="w-4 h-4 mr-1" />
              {{ copied ? 'Copied!' : 'Copy' }}
            </Button>
          </div>
          <Input
            v-model="shareUrl"
            readonly
            class="mt-2"
          />
          <div class="text-xs text-gray-500 mt-1">
            Expires: {{ expiresAt }}
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
        v-if="!shareUrl"
        variant="solid"
        :loading="isSharing"
        @click="shareContext"
      >
        <Share2 class="w-4 h-4 mr-1" />
        Create Share Link
      </Button>
      <Button 
        v-else
        variant="solid"
        @click="$emit('close')"
      >
        Done
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Dialog, Button, Textarea, Select, Input } from 'frappe-ui'
import { Share2, Copy } from 'lucide-vue-next'
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

const emit = defineEmits(['close', 'shared'])

const isOpen = ref(true)
const message = ref('')
const expiryHours = ref(24)
const shareUrl = ref('')
const expiresAt = ref('')
const isSharing = ref(false)
const error = ref('')
const copied = ref(false)

// Page type labels
const pageTypeLabels = {
  vat_reconciliation: 'VAT Reconciliation',
  vat_reconciliation_list: 'VAT Reconciliation List',
  risk_assessment: 'Risk Assessment',
  audit_finding: 'Audit Finding',
  audit_universe: 'Audit Universe',
  annual_plan: 'Annual Audit Plan',
  engagement: 'Engagement',
  stock_take: 'Stock Take Session',
  variance_case: 'Variance Case',
  dashboard: 'Dashboard',
  corrective_action: 'Corrective Action Plan',
  follow_up: 'Follow Up'
}

const pageTypeLabel = computed(() => pageTypeLabels[props.pageType] || props.pageType)

const expiryOptions = [
  { label: '1 hour', value: 1 },
  { label: '6 hours', value: 6 },
  { label: '24 hours', value: 24 },
  { label: '3 days', value: 72 },
  { label: '7 days', value: 168 }
]

// Share context API
const shareContextResource = createResource({
  url: 'mkaguzi.api.ai_specialist.share_context',
  makeParams: () => ({
    page_type: props.pageType,
    document_id: props.documentId,
    message: message.value,
    expires_in_hours: expiryHours.value
  }),
  onSuccess: (data) => {
    if (data.success) {
      const baseUrl = window.location.origin
      shareUrl.value = `${baseUrl}${data.share_url}`
      expiresAt.value = new Date(data.expires_at).toLocaleString()
      emit('shared', { shareId: data.share_id, shareUrl: shareUrl.value })
    } else {
      error.value = data.error || 'Failed to create share link'
    }
    isSharing.value = false
  },
  onError: (err) => {
    error.value = err.message || 'Failed to create share link'
    isSharing.value = false
  }
})

const shareContext = async () => {
  isSharing.value = true
  error.value = ''
  await shareContextResource.fetch()
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>
