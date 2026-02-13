<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <Button variant="ghost" @click="$router.push('/audit-execution/engagements')">
          <ArrowLeftIcon class="h-4 w-4" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ engagement?.engagement_title || 'Engagement Details' }}</h1>
          <p class="text-gray-600 mt-1">
            {{ engagement?.engagement_id || '' }}
            <Badge v-if="engagement" :variant="getStatusVariant(engagement.status)" class="ml-2">
              {{ engagement.status }}
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

    <template v-else-if="engagement">
      <!-- Summary Cards -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Audit Type</p>
          <p class="text-sm font-bold text-gray-900">{{ engagement.audit_type }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Period</p>
          <p class="text-sm font-bold text-gray-900">{{ formatDate(engagement.period_start) }} - {{ formatDate(engagement.period_end) }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Lead Auditor</p>
          <p class="text-sm font-bold text-gray-900">{{ engagement.lead_auditor || '-' }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Findings</p>
          <p class="text-sm font-bold" :class="engagement.findings_count > 0 ? 'text-orange-600' : 'text-gray-900'">
            {{ engagement.findings_count || 0 }}
            <span v-if="engagement.high_risk_findings_count" class="text-red-600">({{ engagement.high_risk_findings_count }} high)</span>
          </p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-sm text-gray-600">Budget</p>
          <p class="text-sm font-bold text-gray-900">
            {{ engagement.actual_hours || 0 }}h / {{ engagement.budgeted_hours || 0 }}h
            <span v-if="engagement.budget_variance_percent" :class="engagement.budget_variance_percent > 0 ? 'text-red-600' : 'text-green-600'" class="text-xs">
              ({{ engagement.budget_variance_percent > 0 ? '+' : '' }}{{ Math.round(engagement.budget_variance_percent) }}%)
            </span>
          </p>
        </div>
      </div>

      <!-- Tabs -->
      <div class="bg-white rounded-lg border border-gray-200">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px overflow-x-auto">
            <button
              v-for="tab in visibleTabs"
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
              <span v-if="tab.count !== undefined && tab.count > 0" class="ml-1 text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-full">
                {{ tab.count }}
              </span>
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- Overview Tab -->
          <div v-if="activeTab === 'overview'" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <h3 class="font-semibold text-gray-900">General Information</h3>
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <p class="text-sm text-gray-600">Audit Approach</p>
                    <p class="font-medium text-sm">{{ engagement.audit_approach || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Sampling Method</p>
                    <p class="font-medium text-sm">{{ engagement.sampling_methodology || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Materiality</p>
                    <p class="font-medium text-sm">{{ engagement.materiality_threshold ? formatCurrency(engagement.materiality_threshold) : '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Audit Universe</p>
                    <p class="font-medium text-sm">{{ engagement.audit_universe || '-' }}</p>
                  </div>
                </div>
              </div>
              <div class="space-y-4">
                <h3 class="font-semibold text-gray-900">Timeline</h3>
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <p class="text-sm text-gray-600">Planning</p>
                    <p class="font-medium text-sm">{{ formatDate(engagement.planning_start) }} - {{ formatDate(engagement.planning_end) }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Fieldwork</p>
                    <p class="font-medium text-sm">{{ formatDate(engagement.fieldwork_start) }} - {{ formatDate(engagement.fieldwork_end) }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Reporting</p>
                    <p class="font-medium text-sm">{{ formatDate(engagement.reporting_start) }} - {{ formatDate(engagement.reporting_end) }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Completion</p>
                    <p class="font-medium text-sm">{{ formatDate(engagement.actual_completion_date) || 'In progress' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="engagement.audit_objectives">
              <h3 class="font-semibold text-gray-900 mb-2">Objectives</h3>
              <div class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="engagement.audit_objectives"></div>
            </div>
            <div v-if="engagement.audit_scope">
              <h3 class="font-semibold text-gray-900 mb-2">Scope</h3>
              <div class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="engagement.audit_scope"></div>
            </div>
            <div v-if="engagement.scope_exclusions">
              <h3 class="font-semibold text-gray-900 mb-2">Scope Exclusions</h3>
              <p class="text-sm text-gray-700 bg-gray-50 rounded-lg p-4">{{ engagement.scope_exclusions }}</p>
            </div>

            <!-- Opinion -->
            <div v-if="engagement.overall_audit_opinion" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 class="font-semibold text-blue-900 mb-2">Overall Audit Opinion</h3>
              <Badge :variant="getOpinionVariant(engagement.overall_audit_opinion)">{{ engagement.overall_audit_opinion }}</Badge>
              <div v-if="engagement.opinion_rationale" class="prose prose-sm max-w-none mt-2" v-html="engagement.opinion_rationale"></div>
            </div>
          </div>

          <!-- Team Tab -->
          <div v-if="activeTab === 'team'" class="space-y-4">
            <div v-if="engagement.audit_team && engagement.audit_team.length > 0">
              <table class="w-full">
                <thead>
                  <tr class="border-b border-gray-200 bg-gray-50">
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Team Member</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Role</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Allocation %</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Hours</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="member in engagement.audit_team" :key="member.name" class="border-b border-gray-100">
                    <td class="px-4 py-2">
                      <div class="flex items-center space-x-2">
                        <Avatar :label="member.team_member || member.user" size="sm" />
                        <span class="text-sm font-medium">{{ member.team_member || member.user }}</span>
                      </div>
                    </td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ member.role || '-' }}</td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ member.allocation_percent || member.allocation || '-' }}%</td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ member.planned_hours || member.hours || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No team members assigned.</p>
          </div>

          <!-- Contacts Tab -->
          <div v-if="activeTab === 'contacts'" class="space-y-4">
            <div v-if="engagement.key_contacts && engagement.key_contacts.length > 0">
              <div v-for="contact in engagement.key_contacts" :key="contact.name" class="border border-gray-200 rounded-lg p-4 flex items-center justify-between">
                <div>
                  <p class="font-medium text-gray-900">{{ contact.contact_name || contact.full_name || '-' }}</p>
                  <p class="text-sm text-gray-600">{{ contact.contact_type || contact.designation || '-' }}</p>
                  <div class="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                    <span v-if="contact.email">{{ contact.email }}</span>
                    <span v-if="contact.phone">{{ contact.phone }}</span>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No key contacts defined.</p>
          </div>

          <!-- Data Requirements Tab -->
          <div v-if="activeTab === 'data_reqs'" class="space-y-4">
            <div v-if="engagement.data_periods && engagement.data_periods.length > 0">
              <table class="w-full">
                <thead>
                  <tr class="border-b border-gray-200 bg-gray-50">
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Period</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Type</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Status</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">Start</th>
                    <th class="text-left text-xs font-medium text-gray-500 uppercase px-4 py-2">End</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="period in engagement.data_periods" :key="period.name" class="border-b border-gray-100">
                    <td class="px-4 py-2 text-sm text-gray-900">{{ period.period_name || period.data_period || '-' }}</td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ period.period_type || '-' }}</td>
                    <td class="px-4 py-2">
                      <Badge v-if="period.status" :variant="period.status === 'Completed' ? 'success' : 'secondary'">{{ period.status }}</Badge>
                    </td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ formatDate(period.start_date) }}</td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ formatDate(period.end_date) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No data periods defined.</p>
          </div>

          <!-- Working Papers Tab -->
          <div v-if="activeTab === 'working_papers'" class="space-y-4">
            <div v-if="linkedWorkingPapers.length > 0">
              <div v-for="wp in linkedWorkingPapers" :key="wp.name" class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-gray-900">{{ wp.working_paper_title || wp.name }}</p>
                    <p class="text-sm text-gray-600">{{ wp.working_paper_type || '-' }}</p>
                  </div>
                  <Badge :variant="wp.review_status === 'Reviewed' ? 'success' : 'secondary'">
                    {{ wp.review_status || wp.status || '-' }}
                  </Badge>
                </div>
              </div>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No working papers linked.</p>
          </div>

          <!-- Findings Tab -->
          <div v-if="activeTab === 'findings'" class="space-y-4">
            <div v-if="linkedFindings.length > 0">
              <div v-for="finding in linkedFindings" :key="finding.name"
                class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                @click="$router.push(`/findings/${finding.name}`)"
              >
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-gray-900">{{ finding.finding_title }}</p>
                    <p class="text-sm text-gray-600">{{ finding.finding_category }}</p>
                  </div>
                  <div class="flex items-center space-x-2">
                    <Badge :variant="getSeverityVariant(finding.severity || finding.risk_rating)">
                      {{ finding.severity || finding.risk_rating }}
                    </Badge>
                    <Badge :variant="getFindingStatusVariant(finding.finding_status)">
                      {{ finding.finding_status }}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-gray-500 text-center py-6">No findings for this engagement.</p>
          </div>

          <!-- Program Tab -->
          <div v-if="activeTab === 'program'" class="space-y-4">
            <div v-if="engagement.audit_program_reference">
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-600">Linked Audit Program</p>
                <p class="font-medium text-blue-600">{{ engagement.audit_program_reference }}</p>
              </div>
            </div>
            <div v-if="engagement.report_reference" class="bg-gray-50 rounded-lg p-4">
              <p class="text-sm text-gray-600">Audit Report</p>
              <router-link :to="`/reports/audit-reports/${engagement.report_reference}`" class="font-medium text-blue-600 hover:underline">
                {{ engagement.report_reference }}
              </router-link>
            </div>
            <p v-if="!engagement.audit_program_reference && !engagement.report_reference" class="text-gray-500 text-center py-6">
              No program or report linked.
            </p>
          </div>

          <!-- Quality Review Tab -->
          <div v-if="activeTab === 'quality'" class="space-y-4">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-gray-50 rounded p-3">
                <p class="text-sm text-gray-600">Review Status</p>
                <Badge v-if="engagement.review_status" :variant="engagement.review_status === 'Completed' ? 'success' : 'secondary'">
                  {{ engagement.review_status }}
                </Badge>
                <span v-else class="font-medium text-sm">Not Started</span>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-sm text-gray-600">Reviewer</p>
                <p class="font-medium text-sm">{{ engagement.quality_reviewer || '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-sm text-gray-600">Review Date</p>
                <p class="font-medium text-sm">{{ formatDate(engagement.review_date) }}</p>
              </div>
              <div class="bg-gray-50 rounded p-3">
                <p class="text-sm text-gray-600">Quality Score</p>
                <p class="text-xl font-bold" :class="engagement.quality_score >= 80 ? 'text-green-600' : engagement.quality_score >= 50 ? 'text-yellow-600' : 'text-red-600'">
                  {{ engagement.quality_score != null ? engagement.quality_score : '-' }}
                </p>
              </div>
            </div>
            <div v-if="engagement.review_comments">
              <h4 class="font-medium text-gray-900 mb-2">Review Comments</h4>
              <div class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="engagement.review_comments"></div>
            </div>
          </div>

          <!-- ESG Tab -->
          <div v-if="activeTab === 'esg'" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-600">ESG Framework</p>
                <p class="font-medium">{{ engagement.esg_framework || '-' }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">Reporting Framework</p>
                <p class="font-medium">{{ engagement.esg_reporting_framework || '-' }}</p>
              </div>
            </div>
            <div v-if="engagement.environmental_standards">
              <h4 class="font-medium text-gray-900 mb-2">Environmental Standards</h4>
              <p class="text-sm text-gray-700 bg-gray-50 rounded-lg p-4">{{ engagement.environmental_standards }}</p>
            </div>
            <div v-if="engagement.sustainability_goals">
              <h4 class="font-medium text-gray-900 mb-2">Sustainability Goals</h4>
              <div class="prose prose-sm max-w-none bg-gray-50 rounded-lg p-4" v-html="engagement.sustainability_goals"></div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Error State -->
    <div v-else class="text-center py-12">
      <p class="text-gray-600">Failed to load engagement details.</p>
      <Button @click="loadEngagement" class="mt-4">Retry</Button>
    </div>
  </div>
</template>

<script setup>
import { Avatar, Badge, Button, Spinner } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	ArrowLeftIcon,
	ExternalLinkIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()

const loading = ref(true)
const engagement = ref(null)
const activeTab = ref("overview")
const linkedWorkingPapers = ref([])
const linkedFindings = ref([])

const isESG = computed(() => {
	if (!engagement.value) return false
	const esgTypes = ["Environmental Compliance", "ESG Assessment", "Sustainability Review", "Carbon Footprint Audit", "Biodiversity Impact", "Supply Chain Sustainability", "Climate Change", "Social Responsibility", "Governance Review"]
	return esgTypes.includes(engagement.value.audit_type) || engagement.value.esg_framework
})

const visibleTabs = computed(() => {
	const tabs = [
		{ id: "overview", label: "Overview" },
		{ id: "team", label: "Team", count: engagement.value?.audit_team?.length || 0 },
		{ id: "contacts", label: "Contacts", count: engagement.value?.key_contacts?.length || 0 },
		{ id: "data_reqs", label: "Data Periods", count: engagement.value?.data_periods?.length || 0 },
		{ id: "working_papers", label: "Working Papers", count: linkedWorkingPapers.value.length },
		{ id: "findings", label: "Findings", count: linkedFindings.value.length },
		{ id: "program", label: "Program & Report" },
		{ id: "quality", label: "Quality Review" },
	]
	if (isESG.value) {
		tabs.push({ id: "esg", label: "ESG" })
	}
	return tabs
})

const loadEngagement = async () => {
	loading.value = true
	try {
		const res = await createResource({
			url: "frappe.client.get",
			params: { doctype: "Audit Engagement", name: route.params.id },
		}).fetch()
		engagement.value = res
		if (res) {
			await Promise.all([loadWorkingPapers(), loadFindings()])
		}
	} catch (err) {
		console.error("Failed to load engagement:", err)
	} finally {
		loading.value = false
	}
}

const loadWorkingPapers = async () => {
	try {
		const res = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Working Paper",
				fields: ["name", "working_paper_title", "working_paper_type", "review_status", "status"],
				filters: { engagement_reference: route.params.id },
				limit_page_length: 100,
			},
		}).fetch()
		linkedWorkingPapers.value = res || []
	} catch (err) {
		console.error("Failed to load working papers:", err)
	}
}

const loadFindings = async () => {
	try {
		const res = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Audit Finding",
				fields: ["name", "finding_title", "finding_category", "severity", "risk_rating", "finding_status"],
				filters: { engagement_reference: route.params.id },
				limit_page_length: 100,
			},
		}).fetch()
		linkedFindings.value = res || []
	} catch (err) {
		console.error("Failed to load findings:", err)
	}
}

const getStatusVariant = (status) => {
	const map = { Planning: "secondary", Fieldwork: "info", Reporting: "warning", "Management Review": "warning", "Quality Review": "info", Finalized: "success", Issued: "success", "On Hold": "danger", Cancelled: "danger" }
	return map[status] || "secondary"
}

const getOpinionVariant = (opinion) => {
	const map = { Satisfactory: "success", "Satisfactory with Minor Issues": "info", "Needs Improvement": "warning", Unsatisfactory: "danger" }
	return map[opinion] || "secondary"
}

const getSeverityVariant = (s) => ({ Critical: "danger", High: "warning", Medium: "info", Low: "secondary" })[s] || "secondary"
const getFindingStatusVariant = (s) => ({ Open: "danger", "Action in Progress": "warning", "Pending Verification": "info", Closed: "success" })[s] || "secondary"

const formatDate = (date) => {
	if (!date) return "-"
	return new Date(date).toLocaleDateString()
}

const formatCurrency = (val) => {
	if (val == null) return "-"
	return new Intl.NumberFormat(undefined, { style: "currency", currency: "KES" }).format(val)
}

const openInDesk = () => {
	if (engagement.value) {
		window.open(`/app/audit-engagement/${engagement.value.name}`, "_blank")
	}
}

onMounted(() => {
	loadEngagement()
})
</script>
