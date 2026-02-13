<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <Button variant="ghost" @click="$router.push('/findings/list')">
          <ArrowLeftIcon class="h-4 w-4" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ finding?.finding_title || 'Finding Details' }}</h1>
          <p class="text-gray-600 mt-1">
            {{ finding?.finding_id || '' }}
            <Badge v-if="finding" :variant="getSeverityVariant(finding.severity || finding.risk_rating)" class="ml-2">
              {{ finding.severity || finding.risk_rating }}
            </Badge>
            <Badge v-if="finding" :variant="getFindingStatusVariant(finding.finding_status)" class="ml-1">
              {{ finding.finding_status }}
            </Badge>
          </p>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <Button variant="outline" @click="openInDesk">
          <ExternalLinkIcon class="h-4 w-4 mr-2" />
          Edit in Desk
        </Button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <template v-else-if="finding">
      <!-- Summary Cards -->
      <div class="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Category</p>
          <p class="text-sm font-bold text-gray-900">{{ finding.finding_category }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Risk Category</p>
          <p class="text-sm font-bold text-gray-900">{{ finding.risk_category || '-' }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Financial Impact</p>
          <p class="text-sm font-bold" :class="finding.financial_impact ? 'text-red-600' : 'text-gray-900'">
            {{ finding.financial_impact ? formatCurrency(finding.financial_impact) : '-' }}
          </p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Exception Rate</p>
          <p class="text-sm font-bold text-gray-900">{{ finding.exception_rate != null ? finding.exception_rate + '%' : '-' }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Overdue Days</p>
          <p class="text-sm font-bold" :class="finding.overdue_days > 0 ? 'text-red-600' : 'text-gray-900'">
            {{ finding.overdue_days || 0 }}
          </p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">AI Review</p>
          <Badge v-if="finding.ai_review_status" :variant="getAIReviewVariant(finding.ai_review_status)">
            {{ finding.ai_review_status }}
          </Badge>
          <span v-else class="text-sm text-gray-400">-</span>
        </div>
      </div>

      <!-- Severity Mismatch Warning -->
      <div v-if="finding.severity_mismatch" class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-center space-x-2">
        <AlertTriangleIcon class="h-5 w-5 text-yellow-600 flex-shrink-0" />
        <p class="text-sm text-yellow-800">
          AI suggests severity <strong>{{ finding.ai_severity_suggestion }}</strong> but current rating is <strong>{{ finding.severity || finding.risk_rating }}</strong>.
        </p>
      </div>

      <!-- Tabs -->
      <div class="bg-white rounded-lg border border-gray-200">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px overflow-x-auto">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'px-5 py-3 text-sm font-medium border-b-2 whitespace-nowrap',
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              {{ tab.label }}
              <span v-if="tab.count > 0" class="ml-1 text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-full">{{ tab.count }}</span>
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- 4C Structure Tab -->
          <div v-if="activeTab === '4c'" class="space-y-6">
            <div>
              <h3 class="font-semibold text-gray-900 mb-2 flex items-center">
                <span class="bg-red-100 text-red-700 text-xs font-bold px-2 py-0.5 rounded mr-2">Condition</span>
                What was found
              </h3>
              <div v-if="finding.condition" class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="finding.condition"></div>
              <p v-else class="text-gray-500">Not specified.</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-2 flex items-center">
                <span class="bg-blue-100 text-blue-700 text-xs font-bold px-2 py-0.5 rounded mr-2">Criteria</span>
                What should be
              </h3>
              <div v-if="finding.criteria" class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="finding.criteria"></div>
              <p v-else class="text-gray-500">Not specified.</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-2 flex items-center">
                <span class="bg-yellow-100 text-yellow-700 text-xs font-bold px-2 py-0.5 rounded mr-2">Cause</span>
                Why it happened
              </h3>
              <div v-if="finding.cause" class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="finding.cause"></div>
              <p v-else class="text-gray-500">Not specified.</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-2 flex items-center">
                <span class="bg-gray-100 text-gray-700 text-xs font-bold px-2 py-0.5 rounded mr-2">Consequence</span>
                What is the impact
              </h3>
              <div v-if="finding.consequence" class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="finding.consequence"></div>
              <p v-else class="text-gray-500">Not specified.</p>
            </div>

            <!-- Additional context -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-200">
              <div>
                <p class="text-sm text-gray-600">Engagement</p>
                <router-link v-if="finding.engagement_reference" :to="`/engagements/${finding.engagement_reference}`" class="text-blue-600 hover:underline font-medium">
                  {{ finding.engagement_reference }}
                </router-link>
                <span v-else class="text-gray-400">-</span>
              </div>
              <div>
                <p class="text-sm text-gray-600">Working Paper</p>
                <span class="font-medium">{{ finding.working_paper_reference || '-' }}</span>
              </div>
              <div>
                <p class="text-sm text-gray-600">Likelihood / Impact</p>
                <span class="font-medium">{{ finding.likelihood || '-' }} / {{ finding.impact || '-' }}</span>
              </div>
              <div>
                <p class="text-sm text-gray-600">Risk Score</p>
                <span class="font-medium">{{ finding.risk_score || '-' }}</span>
              </div>
            </div>

            <div v-if="finding.recommendation">
              <h3 class="font-semibold text-gray-900 mb-2">Recommendation</h3>
              <div class="prose prose-sm max-w-none bg-blue-50 rounded-lg p-4" v-html="finding.recommendation"></div>
            </div>
          </div>

          <!-- Evidence Tab -->
          <div v-if="activeTab === 'evidence'" class="space-y-4">
            <div v-if="finding.evidence && finding.evidence.length > 0">
              <div v-for="ev in finding.evidence" :key="ev.name" class="border border-gray-200 rounded-lg p-4 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <FileTextIcon class="h-5 w-5 text-gray-400" />
                  <div>
                    <p class="font-medium text-sm text-gray-900">{{ ev.evidence_title || ev.description || ev.name }}</p>
                    <p class="text-xs text-gray-500">{{ ev.evidence_type || '-' }}</p>
                  </div>
                </div>
                <Button v-if="ev.file || ev.attachment" variant="outline" size="sm" @click="downloadFile(ev.file || ev.attachment)">
                  <DownloadIcon class="h-3 w-3 mr-1" /> Download
                </Button>
              </div>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No evidence attached.</p>
            <div class="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Sample Size</p>
                <p class="font-medium">{{ finding.sample_size || '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Exceptions Found</p>
                <p class="font-medium">{{ finding.exceptions_found || '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Exception Rate</p>
                <p class="font-medium">{{ finding.exception_rate != null ? finding.exception_rate + '%' : '-' }}</p>
              </div>
            </div>
          </div>

          <!-- Action Plan Tab -->
          <div v-if="activeTab === 'action_plan'" class="space-y-4">
            <div v-if="finding.action_plan_description" class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="finding.action_plan_description"></div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Responsible Person</p>
                <p class="font-medium text-sm">{{ finding.responsible_person || '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Department</p>
                <p class="font-medium text-sm">{{ finding.responsible_department || '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Target Date</p>
                <p class="font-medium text-sm">{{ formatDate(finding.target_completion_date) }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Estimated Cost</p>
                <p class="font-medium text-sm">{{ finding.estimated_cost ? formatCurrency(finding.estimated_cost) : '-' }}</p>
              </div>
            </div>

            <!-- Management Response -->
            <div class="pt-4 border-t border-gray-200">
              <h4 class="font-medium text-gray-900 mb-2">Management Response</h4>
              <div class="grid grid-cols-3 gap-4">
                <div>
                  <p class="text-sm text-gray-600">Agreement</p>
                  <Badge v-if="finding.management_agrees" :variant="finding.management_agrees === 'Agree' ? 'success' : finding.management_agrees === 'Partially Agree' ? 'warning' : 'danger'">
                    {{ finding.management_agrees }}
                  </Badge>
                  <span v-else class="text-gray-400 text-sm">Pending</span>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Responded By</p>
                  <p class="font-medium text-sm">{{ finding.responded_by || '-' }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Response Date</p>
                  <p class="font-medium text-sm">{{ formatDate(finding.response_date) }}</p>
                </div>
              </div>
              <div v-if="finding.management_comments" class="mt-3 prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="finding.management_comments"></div>
            </div>

            <!-- Milestones -->
            <div v-if="finding.milestones && finding.milestones.length > 0" class="pt-4 border-t border-gray-200">
              <h4 class="font-medium text-gray-900 mb-2">Action Milestones</h4>
              <div class="space-y-2">
                <div v-for="ms in finding.milestones" :key="ms.name" class="flex items-center space-x-3 border-l-2 pl-4 py-2"
                  :class="ms.status === 'Completed' ? 'border-green-500' : 'border-gray-300'"
                >
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">{{ ms.milestone_name || ms.title }}</p>
                    <p class="text-xs text-gray-500">Due: {{ formatDate(ms.due_date || ms.target_date) }}</p>
                  </div>
                  <Badge :variant="ms.status === 'Completed' ? 'success' : 'secondary'">{{ ms.status || 'Pending' }}</Badge>
                </div>
              </div>
            </div>
          </div>

          <!-- Follow-up Tab -->
          <div v-if="activeTab === 'follow_up'" class="space-y-4">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Follow-up Required</p>
                <p class="font-medium">{{ finding.follow_up_required ? 'Yes' : 'No' }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Frequency</p>
                <p class="font-medium">{{ finding.follow_up_frequency || '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Next Follow-up</p>
                <p class="font-medium">{{ formatDate(finding.next_follow_up_date) }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Escalation</p>
                <Badge v-if="finding.escalation_required" variant="danger">{{ finding.escalation_level || 'Required' }}</Badge>
                <span v-else class="font-medium">None</span>
              </div>
            </div>

            <div v-if="finding.follow_up_history && finding.follow_up_history.length > 0">
              <h4 class="font-medium text-gray-900 mb-2">Follow-up History</h4>
              <div class="space-y-3">
                <div v-for="fu in finding.follow_up_history" :key="fu.name" class="border border-gray-200 rounded-lg p-3">
                  <div class="flex items-center justify-between">
                    <p class="text-sm font-medium text-gray-900">{{ fu.activity_type || fu.follow_up_type || 'Follow-up' }}</p>
                    <span class="text-xs text-gray-500">{{ formatDate(fu.follow_up_date || fu.date) }}</span>
                  </div>
                  <p v-if="fu.notes || fu.remarks" class="text-sm text-gray-600 mt-1">{{ fu.notes || fu.remarks }}</p>
                  <p class="text-xs text-gray-500 mt-1">By: {{ fu.performed_by || fu.user || '-' }}</p>
                </div>
              </div>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No follow-up history.</p>
          </div>

          <!-- AI Review Tab -->
          <div v-if="activeTab === 'ai_review'" class="space-y-4">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">AI Review Status</p>
                <Badge v-if="finding.ai_review_status" :variant="getAIReviewVariant(finding.ai_review_status)">
                  {{ finding.ai_review_status }}
                </Badge>
                <span v-else class="text-gray-400">Not reviewed</span>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">AI Severity Suggestion</p>
                <Badge v-if="finding.ai_severity_suggestion" :variant="getSeverityVariant(finding.ai_severity_suggestion)">
                  {{ finding.ai_severity_suggestion }}
                </Badge>
                <span v-else class="text-gray-400">-</span>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Model Used</p>
                <p class="font-medium text-sm">{{ finding.ai_model_used || '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Reviewed On</p>
                <p class="font-medium text-sm">{{ finding.ai_reviewed_on ? formatDateTime(finding.ai_reviewed_on) : '-' }}</p>
              </div>
            </div>
            <div v-if="finding.ai_review_notes">
              <h4 class="font-medium text-gray-900 mb-2">AI Review Notes</h4>
              <div class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="finding.ai_review_notes"></div>
            </div>
            <div v-if="finding.ai_root_cause_analysis">
              <h4 class="font-medium text-gray-900 mb-2">AI Root Cause Analysis</h4>
              <div class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="finding.ai_root_cause_analysis"></div>
            </div>
            <div v-if="finding.ai_recommendation_refinement">
              <h4 class="font-medium text-gray-900 mb-2">AI Recommendation Refinement</h4>
              <div class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="finding.ai_recommendation_refinement"></div>
            </div>
            <div v-if="finding.ai_risk_narrative">
              <h4 class="font-medium text-gray-900 mb-2">AI Risk Narrative</h4>
              <p class="text-sm text-gray-700 bg-gray-50 rounded-lg p-4">{{ finding.ai_risk_narrative }}</p>
            </div>

            <!-- Agent info if auto-generated -->
            <div v-if="finding.auto_generated" class="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <p class="text-sm text-gray-800">
                Auto-generated by <strong>{{ finding.source_agent }}</strong> agent.
                <router-link v-if="finding.agent_execution_log" :to="`/audit-execution/agent-dashboard/${finding.agent_execution_log}`" class="text-gray-900 hover:underline ml-1">
                  View execution log
                </router-link>
              </p>
            </div>
          </div>

          <!-- Related Findings Tab -->
          <div v-if="activeTab === 'related'" class="space-y-4">
            <!-- Repeat finding info -->
            <div v-if="finding.repeat_finding" class="bg-orange-50 border border-orange-200 rounded-lg p-3">
              <p class="text-sm text-orange-800">
                This is a <strong>repeat finding</strong> ({{ finding.repeat_count || 1 }}x).
                Previous: {{ finding.previous_finding_reference || '-' }} ({{ formatDate(finding.previous_finding_date) }})
              </p>
            </div>

            <div v-if="finding.related_findings && finding.related_findings.length > 0">
              <h4 class="font-medium text-gray-900 mb-2">Related Findings</h4>
              <div v-for="rel in finding.related_findings" :key="rel.name" class="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 cursor-pointer"
                @click="$router.push(`/findings/${rel.related_finding}`)"
              >
                <p class="font-medium text-sm text-blue-600">{{ rel.related_finding }}</p>
                <p v-if="rel.relationship_type" class="text-xs text-gray-500">{{ rel.relationship_type }}</p>
              </div>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No related findings linked.</p>
          </div>

          <!-- Status History Tab -->
          <div v-if="activeTab === 'status_history'" class="space-y-4">
            <div v-if="finding.status_history && finding.status_history.length > 0">
              <div class="space-y-3">
                <div v-for="change in finding.status_history" :key="change.name" class="flex items-start space-x-3 border-l-2 border-blue-200 pl-4 py-2">
                  <div>
                    <div class="flex items-center space-x-2">
                      <Badge variant="secondary">{{ change.from_status || '-' }}</Badge>
                      <ArrowRightIcon class="h-3 w-3 text-gray-400" />
                      <Badge :variant="getFindingStatusVariant(change.to_status)">{{ change.to_status }}</Badge>
                    </div>
                    <p v-if="change.reason || change.notes" class="text-sm text-gray-600 mt-1">{{ change.reason || change.notes }}</p>
                    <p class="text-xs text-gray-500 mt-1">{{ change.changed_by || '-' }} on {{ formatDateTime(change.changed_on || change.creation) }}</p>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No status changes recorded.</p>
          </div>

          <!-- Verification Tab -->
          <div v-if="activeTab === 'verification'" class="space-y-4">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Verification Status</p>
                <Badge v-if="finding.verification_status" :variant="getVerificationVariant(finding.verification_status)">
                  {{ finding.verification_status }}
                </Badge>
                <span v-else class="font-medium text-sm">Pending</span>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Method</p>
                <p class="font-medium text-sm">{{ finding.verification_method || '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Verified By</p>
                <p class="font-medium text-sm">{{ finding.verified_by || '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-xs text-gray-500">Verification Date</p>
                <p class="font-medium text-sm">{{ formatDate(finding.verification_date) }}</p>
              </div>
            </div>
            <div v-if="finding.verification_results">
              <h4 class="font-medium text-gray-900 mb-2">Verification Results</h4>
              <div class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="finding.verification_results"></div>
            </div>

            <!-- Closure -->
            <div v-if="finding.closure_date" class="pt-4 border-t border-gray-200">
              <h4 class="font-medium text-gray-900 mb-2">Closure Information</h4>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-green-50 rounded p-3">
                  <p class="text-xs text-gray-500">Closure Date</p>
                  <p class="font-medium text-sm">{{ formatDate(finding.closure_date) }}</p>
                </div>
                <div class="bg-green-50 rounded p-3">
                  <p class="text-xs text-gray-500">Closed By</p>
                  <p class="font-medium text-sm">{{ finding.closed_by || '-' }}</p>
                </div>
                <div class="bg-green-50 rounded p-3">
                  <p class="text-xs text-gray-500">Closure Reason</p>
                  <p class="font-medium text-sm">{{ finding.closure_reason || '-' }}</p>
                </div>
                <div v-if="finding.closure_approved_by" class="bg-green-50 rounded p-3">
                  <p class="text-xs text-gray-500">Approved By</p>
                  <p class="font-medium text-sm">{{ finding.closure_approved_by }}</p>
                </div>
              </div>
              <div v-if="finding.closure_notes" class="mt-3 prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="finding.closure_notes"></div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Error State -->
    <div v-else class="text-center py-12">
      <p class="text-gray-600">Failed to load finding details.</p>
      <Button @click="loadFinding" class="mt-4">Retry</Button>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, Spinner } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	AlertTriangleIcon,
	ArrowLeftIcon,
	ArrowRightIcon,
	DownloadIcon,
	ExternalLinkIcon,
	FileTextIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()

const loading = ref(true)
const finding = ref(null)
const activeTab = ref("4c")

const tabs = computed(() => [
	{ id: "4c", label: "4C Structure" },
	{ id: "evidence", label: "Evidence", count: finding.value?.evidence?.length || 0 },
	{ id: "action_plan", label: "Action Plan", count: finding.value?.milestones?.length || 0 },
	{ id: "follow_up", label: "Follow-up", count: finding.value?.follow_up_history?.length || 0 },
	{ id: "ai_review", label: "AI Review", count: finding.value?.ai_review_status ? 1 : 0 },
	{ id: "related", label: "Related", count: finding.value?.related_findings?.length || 0 },
	{ id: "status_history", label: "Status History", count: finding.value?.status_history?.length || 0 },
	{ id: "verification", label: "Verification" },
])

const loadFinding = async () => {
	loading.value = true
	try {
		const res = await createResource({
			url: "frappe.client.get",
			params: { doctype: "Audit Finding", name: route.params.id },
		}).fetch()
		finding.value = res
	} catch (err) {
		console.error("Failed to load finding:", err)
	} finally {
		loading.value = false
	}
}

const getSeverityVariant = (s) => ({ Critical: "danger", High: "warning", Medium: "info", Low: "secondary" })[s] || "secondary"
const getFindingStatusVariant = (s) => ({ Open: "danger", "Action in Progress": "warning", "Pending Verification": "info", Closed: "success", "Accepted as Risk": "secondary", "Management Override": "danger" })[s] || "secondary"
const getAIReviewVariant = (s) => ({ Pending: "warning", Reviewed: "success", Skipped: "secondary", Failed: "danger" })[s] || "secondary"
const getVerificationVariant = (s) => ({ Pending: "secondary", "Verified-Closed": "success", "Verified-Partially Implemented": "warning", "Not Implemented": "danger" })[s] || "secondary"

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : "-"
const formatDateTime = (dt) => dt ? new Date(dt).toLocaleString() : "-"
const formatCurrency = (v) => v != null ? new Intl.NumberFormat(undefined, { style: "currency", currency: "KES" }).format(v) : "-"

const downloadFile = (url) => { if (url) window.open(url) }

const openInDesk = () => {
	if (finding.value) window.open(`/app/audit-finding/${finding.value.name}`, "_blank")
}

onMounted(() => { loadFinding() })
</script>
