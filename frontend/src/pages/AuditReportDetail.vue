<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <Button variant="ghost" @click="$router.push('/reports/audit-reports')">
          <ArrowLeftIcon class="h-4 w-4" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ report?.report_title || 'Audit Report' }}</h1>
          <p class="text-gray-600 mt-1">
            {{ report?.report_type || '' }}
            <Badge v-if="report" :variant="getStatusVariant(report.report_status)" class="ml-2">
              {{ report.report_status }}
            </Badge>
          </p>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <Button v-if="report?.report_file" variant="outline" @click="downloadReport">
          <DownloadIcon class="h-4 w-4 mr-2" />
          Download
        </Button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <template v-else-if="report">
      <!-- Summary Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Report Date</p>
          <p class="text-lg font-bold text-gray-900">{{ formatDate(report.report_date) }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Opinion</p>
          <Badge v-if="report.overall_audit_opinion" :variant="getOpinionVariant(report.overall_audit_opinion)">
            {{ report.overall_audit_opinion }}
          </Badge>
          <span v-else class="text-gray-400">-</span>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Key Findings</p>
          <p class="text-lg font-bold text-gray-900">{{ report.key_findings_summary?.length || 0 }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Version</p>
          <p class="text-lg font-bold text-gray-900">{{ report.version_number || '1.0' }}</p>
        </div>
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
                'px-6 py-3 text-sm font-medium border-b-2 whitespace-nowrap',
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- Overview Tab -->
          <div v-if="activeTab === 'overview'" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-3">
                <div>
                  <p class="text-sm text-gray-600">Report ID</p>
                  <p class="font-medium">{{ report.report_id }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Engagement</p>
                  <router-link v-if="report.engagement_reference" :to="`/engagements/${report.engagement_reference}`" class="text-blue-600 hover:underline font-medium">
                    {{ report.engagement_reference }}
                  </router-link>
                  <span v-else class="text-gray-400">-</span>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Report Period</p>
                  <p class="font-medium">{{ report.report_period || '-' }}</p>
                </div>
              </div>
              <div class="space-y-3">
                <div>
                  <p class="text-sm text-gray-600">Prepared By</p>
                  <p class="font-medium">{{ report.prepared_by || '-' }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Reviewed By</p>
                  <p class="font-medium">{{ report.reviewed_by || '-' }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Approved By</p>
                  <p class="font-medium">{{ report.approved_by || '-' }}</p>
                </div>
              </div>
            </div>
            <div v-if="report.management_acknowledgement" class="bg-green-50 border border-green-200 rounded-lg p-3">
              <p class="text-sm text-green-800">
                Management acknowledged on {{ formatDate(report.management_ack_date) }} by {{ report.management_ack_by }}
              </p>
            </div>
          </div>

          <!-- Executive Summary Tab -->
          <div v-if="activeTab === 'summary'" class="prose prose-sm max-w-none">
            <div v-if="report.executive_summary" v-html="report.executive_summary"></div>
            <p v-else class="text-gray-500">No executive summary provided.</p>
            <div v-if="report.background" class="mt-6">
              <h3>Background</h3>
              <div v-html="report.background"></div>
            </div>
            <div v-if="report.audit_scope" class="mt-6">
              <h3>Scope</h3>
              <div v-html="report.audit_scope"></div>
            </div>
            <div v-if="report.methodology" class="mt-6">
              <h3>Methodology</h3>
              <div v-html="report.methodology"></div>
            </div>
          </div>

          <!-- Key Findings Tab -->
          <div v-if="activeTab === 'key_findings'" class="space-y-4">
            <div v-if="report.key_findings_summary && report.key_findings_summary.length > 0">
              <div v-for="(finding, idx) in report.key_findings_summary" :key="finding.name || idx" class="border border-gray-200 rounded-lg p-4">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-gray-900">{{ finding.finding_title || finding.title || `Finding ${idx + 1}` }}</p>
                    <p v-if="finding.summary" class="text-sm text-gray-600 mt-1">{{ finding.summary }}</p>
                  </div>
                  <Badge v-if="finding.severity || finding.risk_rating" :variant="getSeverityVariant(finding.severity || finding.risk_rating)">
                    {{ finding.severity || finding.risk_rating }}
                  </Badge>
                </div>
              </div>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No key findings recorded.</p>
          </div>

          <!-- Detailed Findings Tab -->
          <div v-if="activeTab === 'detailed_findings'" class="space-y-4">
            <div v-if="report.detailed_findings && report.detailed_findings.length > 0">
              <table class="w-full">
                <thead>
                  <tr class="border-b border-gray-200 bg-gray-50">
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">#</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Finding</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Severity</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(finding, idx) in report.detailed_findings" :key="finding.name || idx" class="border-b border-gray-100">
                    <td class="px-4 py-2 text-sm text-gray-500">{{ idx + 1 }}</td>
                    <td class="px-4 py-2 text-sm text-gray-900">{{ finding.finding_title || finding.title }}</td>
                    <td class="px-4 py-2">
                      <Badge v-if="finding.severity" :variant="getSeverityVariant(finding.severity)">{{ finding.severity }}</Badge>
                    </td>
                    <td class="px-4 py-2">
                      <Badge v-if="finding.status" variant="secondary">{{ finding.status }}</Badge>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No detailed findings recorded.</p>
          </div>

          <!-- Opinion Tab -->
          <div v-if="activeTab === 'opinion'" class="space-y-6">
            <div v-if="report.overall_audit_opinion" class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Overall Audit Opinion</h3>
              <Badge :variant="getOpinionVariant(report.overall_audit_opinion)" class="text-base">
                {{ report.overall_audit_opinion }}
              </Badge>
            </div>
            <div v-if="report.opinion_basis">
              <h3 class="font-semibold text-gray-900 mb-2">Basis for Opinion</h3>
              <div class="prose prose-sm max-w-none" v-html="report.opinion_basis"></div>
            </div>
            <div v-if="report.positive_observations">
              <h3 class="font-semibold text-gray-900 mb-2">Positive Observations</h3>
              <div class="prose prose-sm max-w-none" v-html="report.positive_observations"></div>
            </div>
            <div v-if="report.areas_for_improvement">
              <h3 class="font-semibold text-gray-900 mb-2">Areas for Improvement</h3>
              <div class="prose prose-sm max-w-none" v-html="report.areas_for_improvement"></div>
            </div>
            <div v-if="report.conclusion">
              <h3 class="font-semibold text-gray-900 mb-2">Conclusion</h3>
              <div class="prose prose-sm max-w-none" v-html="report.conclusion"></div>
            </div>
          </div>

          <!-- Distribution Tab -->
          <div v-if="activeTab === 'distribution'" class="space-y-4">
            <div v-if="report.distribution_list && report.distribution_list.length > 0">
              <table class="w-full">
                <thead>
                  <tr class="border-b border-gray-200 bg-gray-50">
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Recipient</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Role</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Distributed</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in report.distribution_list" :key="item.name" class="border-b border-gray-100">
                    <td class="px-4 py-2 text-sm text-gray-900">{{ item.recipient || item.user }}</td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ item.role || '-' }}</td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ item.distributed_date ? formatDate(item.distributed_date) : '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No distribution list defined.</p>
          </div>

          <!-- Appendices Tab -->
          <div v-if="activeTab === 'appendices'" class="space-y-4">
            <div v-if="report.appendices && report.appendices.length > 0">
              <div v-for="(appendix, idx) in report.appendices" :key="appendix.name || idx" class="border border-gray-200 rounded-lg p-4">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="font-medium text-gray-900">{{ appendix.title || `Appendix ${idx + 1}` }}</p>
                    <p v-if="appendix.description" class="text-sm text-gray-600 mt-1">{{ appendix.description }}</p>
                  </div>
                  <Button v-if="appendix.file" variant="outline" size="sm" @click="downloadFile(appendix.file)">
                    <DownloadIcon class="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No appendices attached.</p>
          </div>

          <!-- Revision History Tab -->
          <div v-if="activeTab === 'revisions'" class="space-y-4">
            <div v-if="report.revision_history && report.revision_history.length > 0">
              <div class="space-y-3">
                <div v-for="rev in report.revision_history" :key="rev.name" class="flex items-start space-x-3 border-l-2 border-blue-200 pl-4 py-2">
                  <div>
                    <p class="text-sm font-medium text-gray-900">Version {{ rev.version || '-' }}</p>
                    <p class="text-sm text-gray-600">{{ rev.description || rev.changes || 'No description' }}</p>
                    <p class="text-xs text-gray-500 mt-1">{{ rev.revised_by || '-' }} on {{ formatDate(rev.revision_date || rev.creation) }}</p>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No revision history.</p>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-12">
      <p class="text-gray-600">Failed to load report details.</p>
      <Button @click="loadReport" class="mt-4">Retry</Button>
    </div>
  </div>
</template>

<script setup>
import { useAuditReportsStore } from "@/stores/auditReports"
import { Badge, Button, Spinner } from "frappe-ui"
import {
	ArrowLeftIcon,
	DownloadIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()
const store = useAuditReportsStore()

const activeTab = ref("overview")
const loading = computed(() => store.loading)
const report = computed(() => store.currentReport)

const tabs = [
	{ id: "overview", label: "Overview" },
	{ id: "summary", label: "Executive Summary" },
	{ id: "key_findings", label: "Key Findings" },
	{ id: "detailed_findings", label: "Detailed Findings" },
	{ id: "opinion", label: "Opinion & Conclusion" },
	{ id: "distribution", label: "Distribution" },
	{ id: "appendices", label: "Appendices" },
	{ id: "revisions", label: "Revision History" },
]

const loadReport = () => {
	store.fetchReportDetail(route.params.id)
}

const getStatusVariant = (status) => {
	const map = { Draft: "secondary", "Under Review": "warning", Finalized: "info", Issued: "success" }
	return map[status] || "secondary"
}

const getOpinionVariant = (opinion) => {
	const map = { Satisfactory: "success", "Satisfactory with Minor Improvements": "info", "Needs Improvement": "warning", Unsatisfactory: "danger" }
	return map[opinion] || "secondary"
}

const getSeverityVariant = (severity) => {
	const map = { Critical: "danger", High: "warning", Medium: "info", Low: "secondary" }
	return map[severity] || "secondary"
}

const formatDate = (date) => {
	if (!date) return "-"
	return new Date(date).toLocaleDateString()
}

const downloadReport = () => {
	if (report.value?.report_file) {
		window.open(report.value.report_file)
	}
}

const downloadFile = (url) => {
	if (url) window.open(url)
}

onMounted(() => {
	loadReport()
})
</script>
