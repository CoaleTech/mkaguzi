<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <Button variant="ghost" @click="goBack">
          <ArrowLeft class="w-5 h-5" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">
            Issue Details
          </h1>
          <p class="text-gray-500 mt-1">
            {{ issue.name }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="editIssue">
          <Edit class="w-4 h-4 mr-2" />
          Edit Issue
        </Button>
        <Button variant="solid" @click="resolveIssue" :disabled="issue.status === 'Resolved'">
          <CheckCircle class="w-4 h-4 mr-2" />
          {{ issue.status === 'Resolved' ? 'Resolved' : 'Mark Resolved' }}
        </Button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Issue Overview -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Issue Overview</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Issue Type</label>
              <p class="mt-1 text-sm text-gray-900">{{ issue.issue_type || '-' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Severity</label>
              <Badge :variant="getSeverityVariant(issue.severity)">
                {{ issue.severity || 'Medium' }}
              </Badge>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Status</label>
              <Badge :variant="getStatusVariant(issue.status)">
                {{ issue.status || 'Open' }}
              </Badge>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Priority</label>
              <Badge :variant="getPriorityVariant(issue.priority)">
                {{ issue.priority || 'Medium' }}
              </Badge>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Reported By</label>
              <p class="mt-1 text-sm text-gray-900">{{ issue.reported_by || '-' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Assigned To</label>
              <p class="mt-1 text-sm text-gray-900">{{ issue.assigned_to || '-' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Reported Date</label>
              <p class="mt-1 text-sm text-gray-900">{{ formatDate(issue.reported_date) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Due Date</label>
              <p class="mt-1 text-sm text-gray-900">{{ formatDate(issue.due_date) }}</p>
            </div>
          </div>
        </div>

        <!-- Issue Description -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Issue Description</h3>
          <div class="prose max-w-none">
            <p class="text-gray-700 whitespace-pre-wrap">{{ issue.description || 'No description provided.' }}</p>
          </div>
        </div>

        <!-- Resolution Details -->
        <div v-if="issue.status === 'Resolved'" class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Resolution Details</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Resolution</label>
              <p class="mt-1 text-sm text-gray-900 whitespace-pre-wrap">{{ issue.resolution || '-' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Resolved By</label>
              <p class="mt-1 text-sm text-gray-900">{{ issue.resolved_by || '-' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Resolved Date</label>
              <p class="mt-1 text-sm text-gray-900">{{ formatDate(issue.resolved_date) }}</p>
            </div>
          </div>
        </div>

        <!-- Comments -->
        <div class="bg-white rounded-lg border p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Comments</h3>
            <Button variant="outline" size="sm" @click="showCommentModal = true">
              <MessageSquare class="w-4 h-4 mr-2" />
              Add Comment
            </Button>
          </div>

          <div v-if="comments.length === 0" class="text-center py-8 text-gray-500">
            No comments yet.
          </div>

          <div v-else class="space-y-4">
            <div v-for="comment in comments" :key="comment.name" class="border-l-4 border-blue-500 pl-4">
              <div class="flex items-start justify-between">
                <div class="flex items-center gap-2">
                  <span class="font-medium text-sm text-gray-900">{{ comment.user }}</span>
                  <span class="text-xs text-gray-500">{{ formatDateTime(comment.creation) }}</span>
                </div>
              </div>
              <p class="mt-2 text-sm text-gray-700 whitespace-pre-wrap">{{ comment.comment }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Quick Actions -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div class="space-y-2">
            <Button variant="outline" class="w-full justify-start" @click="editIssue">
              <Edit class="w-4 h-4 mr-2" />
              Edit Issue
            </Button>
            <Button
              variant="outline"
              class="w-full justify-start"
              @click="resolveIssue"
              :disabled="issue.status === 'Resolved'"
            >
              <CheckCircle class="w-4 h-4 mr-2" />
              {{ issue.status === 'Resolved' ? 'Already Resolved' : 'Mark Resolved' }}
            </Button>
            <Button variant="outline" class="w-full justify-start" @click="duplicateIssue">
              <Copy class="w-4 h-4 mr-2" />
              Duplicate Issue
            </Button>
          </div>
        </div>

        <!-- Related Records -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Related Records</h3>
          <div class="space-y-3">
            <div v-if="issue.stock_take_session">
              <label class="block text-sm font-medium text-gray-700">Stock Take Session</label>
              <Button
                variant="link"
                class="p-0 h-auto text-blue-600 hover:text-blue-800"
                @click="goToSession(issue.stock_take_session)"
              >
                {{ issue.session_name || issue.stock_take_session }}
              </Button>
            </div>
            <div v-if="issue.variance_case">
              <label class="block text-sm font-medium text-gray-700">Variance Case</label>
              <Button
                variant="link"
                class="p-0 h-auto text-blue-600 hover:text-blue-800"
                @click="goToVarianceCase(issue.variance_case)"
              >
                {{ issue.case_name || issue.variance_case }}
              </Button>
            </div>
            <div v-if="issue.audit_plan">
              <label class="block text-sm font-medium text-gray-700">Audit Plan</label>
              <Button
                variant="link"
                class="p-0 h-auto text-blue-600 hover:text-blue-800"
                @click="goToAuditPlan(issue.audit_plan)"
              >
                {{ issue.plan_name || issue.audit_plan }}
              </Button>
            </div>
          </div>
        </div>

        <!-- Timeline -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
          <div class="space-y-3">
            <div class="flex items-start gap-3">
              <div class="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">Issue Created</p>
                <p class="text-xs text-gray-500">{{ formatDateTime(issue.creation) }}</p>
              </div>
            </div>
            <div v-if="issue.status === 'Resolved'" class="flex items-start gap-3">
              <div class="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">Issue Resolved</p>
                <p class="text-xs text-gray-500">{{ formatDateTime(issue.resolved_date) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Comment Modal -->
    <Dialog v-model="showCommentModal" :options="{ title: 'Add Comment' }">
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            type="textarea"
            v-model="newComment"
            placeholder="Enter your comment..."
            :rows="4"
          />
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showCommentModal = false">Cancel</Button>
        <Button variant="solid" @click="addComment" :loading="addingComment">
          Add Comment
        </Button>
      </template>
    </Dialog>

    <!-- Resolve Modal -->
    <Dialog v-model="showResolveModal" :options="{ title: 'Resolve Issue' }">
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            type="textarea"
            v-model="resolutionText"
            placeholder="Describe how this issue was resolved..."
            :rows="4"
            label="Resolution Details"
          />
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showResolveModal = false">Cancel</Button>
        <Button variant="solid" @click="confirmResolve" :loading="resolving">
          Resolve Issue
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Badge, Dialog, FormControl } from 'frappe-ui'
import { call } from 'frappe-ui'
import {
  ArrowLeft,
  Edit,
  CheckCircle,
  MessageSquare,
  Copy
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const issue = ref({})
const comments = ref([])
const showCommentModal = ref(false)
const showResolveModal = ref(false)
const newComment = ref('')
const resolutionText = ref('')
const addingComment = ref(false)
const resolving = ref(false)

onMounted(async () => {
  await loadIssue()
  await loadComments()
})

async function loadIssue() {
  try {
    const result = await call('frappe.client.get', {
      doctype: 'Issue Log',
      name: route.params.id
    })
    issue.value = result
  } catch (error) {
    console.error('Error loading issue:', error)
  }
}

async function loadComments() {
  try {
    const result = await call('frappe.client.get_list', {
      doctype: 'Comment',
      filters: {
        reference_doctype: 'Issue Log',
        reference_name: route.params.id
      },
      fields: ['name', 'comment', 'user', 'creation'],
      order_by: 'creation desc'
    })
    comments.value = result
  } catch (error) {
    console.error('Error loading comments:', error)
  }
}

function getSeverityVariant(severity) {
  const variants = {
    'Low': 'outline',
    'Medium': 'secondary',
    'High': 'destructive',
    'Critical': 'destructive'
  }
  return variants[severity] || 'secondary'
}

function getStatusVariant(status) {
  const variants = {
    'Open': 'secondary',
    'In Progress': 'outline',
    'Resolved': 'solid',
    'Closed': 'outline'
  }
  return variants[status] || 'secondary'
}

function getPriorityVariant(priority) {
  const variants = {
    'Low': 'outline',
    'Medium': 'secondary',
    'High': 'destructive',
    'Urgent': 'destructive'
  }
  return variants[priority] || 'secondary'
}

function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleDateString()
}

function formatDateTime(dateTime) {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString()
}

function goBack() {
  router.push('/inventory-audit/issues')
}

function editIssue() {
  router.push(`/inventory-audit/issues/${route.params.id}/edit`)
}

function resolveIssue() {
  if (issue.value.status === 'Resolved') return
  showResolveModal.value = true
}

async function confirmResolve() {
  resolving.value = true
  try {
    await call('frappe.client.set_value', {
      doctype: 'Issue Log',
      name: route.params.id,
      fieldname: {
        status: 'Resolved',
        resolution: resolutionText.value,
        resolved_by: frappe.session.user,
        resolved_date: new Date().toISOString().split('T')[0]
      }
    })
    await loadIssue()
    showResolveModal.value = false
    resolutionText.value = ''
  } catch (error) {
    console.error('Error resolving issue:', error)
  } finally {
    resolving.value = false
  }
}

async function addComment() {
  if (!newComment.value.trim()) return

  addingComment.value = true
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'Comment',
        reference_doctype: 'Issue Log',
        reference_name: route.params.id,
        comment: newComment.value,
        comment_type: 'Comment'
      }
    })
    await loadComments()
    showCommentModal.value = false
    newComment.value = ''
  } catch (error) {
    console.error('Error adding comment:', error)
  } finally {
    addingComment.value = false
  }
}

function duplicateIssue() {
  router.push(`/inventory-audit/issues/new?duplicate=${route.params.id}`)
}

function goToSession(sessionId) {
  router.push(`/inventory-audit/sessions/${sessionId}`)
}

function goToVarianceCase(caseId) {
  router.push(`/inventory-audit/variance-cases/${caseId}`)
}

function goToAuditPlan(planId) {
  router.push(`/inventory-audit/plans/${planId}`)
}
</script>
