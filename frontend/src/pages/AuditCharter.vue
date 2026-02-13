<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit Charter</h1>
        <p class="text-gray-600 mt-1">Internal audit charter governance document</p>
      </div>
      <Button v-if="charter" variant="outline" @click="openInDesk">
        <ExternalLinkIcon class="h-4 w-4 mr-2" />
        Edit in Desk
      </Button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <Spinner class="h-8 w-8" />
    </div>

    <!-- Charter Content -->
    <template v-else-if="charter">
      <!-- Status Bar -->
      <div class="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <Badge :variant="getStatusVariant(charter.status)">{{ charter.status }}</Badge>
          <Badge v-if="charter.approval_status" :variant="getApprovalVariant(charter.approval_status)">
            {{ charter.approval_status }}
          </Badge>
          <span class="text-sm text-gray-600">Version {{ charter.version || '1.0' }}</span>
        </div>
        <div class="flex items-center space-x-4 text-sm text-gray-600">
          <span>Effective: {{ formatDate(charter.effective_date) }}</span>
          <span v-if="charter.approved_by">Approved by: {{ charter.approved_by }}</span>
        </div>
      </div>

      <!-- Charter Sections -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Section Navigation (sidebar) -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-lg border border-gray-200 p-4 sticky top-4">
            <h3 class="font-semibold text-gray-900 mb-3">Sections</h3>
            <nav class="space-y-1">
              <button
                v-for="section in sections"
                :key="section.id"
                @click="activeSection = section.id"
                :class="[
                  'w-full text-left px-3 py-2 rounded-lg text-sm',
                  activeSection === section.id
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                ]"
              >
                {{ section.label }}
              </button>
            </nav>
          </div>
        </div>

        <!-- Content Area -->
        <div class="lg:col-span-3 space-y-6">
          <div v-if="activeSection === 'purpose'" class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Purpose</h2>
            <div class="prose prose-sm max-w-none" v-html="charter.purpose_statement"></div>
          </div>

          <div v-if="activeSection === 'authority'" class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Authority</h2>
            <div class="prose prose-sm max-w-none" v-html="charter.authority_definition"></div>
          </div>

          <div v-if="activeSection === 'responsibility'" class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Responsibility</h2>
            <div class="prose prose-sm max-w-none" v-html="charter.responsibility_definition"></div>
          </div>

          <div v-if="activeSection === 'reporting'" class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Reporting Structure</h2>
            <div class="prose prose-sm max-w-none" v-html="charter.reporting_structure"></div>
            <div class="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-200">
              <div>
                <p class="text-sm text-gray-600">Chief Audit Executive</p>
                <p class="font-medium">{{ charter.cae_name || '-' }}</p>
                <p class="text-sm text-gray-500">{{ charter.cae_title || 'Chief Audit Executive' }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">Audit Committee Chair</p>
                <p class="font-medium">{{ charter.audit_committee_chair || '-' }}</p>
              </div>
            </div>
          </div>

          <div v-if="activeSection === 'scope'" class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Scope & Objectives</h2>
            <div v-if="charter.audit_scope" class="prose prose-sm max-w-none" v-html="charter.audit_scope"></div>
            <div v-if="charter.audit_objectives" class="mt-4">
              <h3 class="font-medium text-gray-900 mb-2">Objectives</h3>
              <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ charter.audit_objectives }}</p>
            </div>
          </div>

          <div v-if="activeSection === 'independence'" class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Independence</h2>
            <div v-if="charter.independence_clause" class="prose prose-sm max-w-none" v-html="charter.independence_clause"></div>
            <p v-else class="text-gray-500">Not specified.</p>
          </div>

          <div v-if="activeSection === 'governance'" class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Governance & Standards</h2>
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p class="text-sm text-gray-600">Framework</p>
                <p class="font-medium">{{ charter.governance_framework || '-' }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">IIA Compliant</p>
                <Badge :variant="charter.iiacompliant ? 'success' : 'secondary'">
                  {{ charter.iiacompliant ? 'Yes' : 'No' }}
                </Badge>
              </div>
              <div>
                <p class="text-sm text-gray-600">Review Schedule</p>
                <p class="font-medium">{{ charter.review_schedule || '-' }}</p>
              </div>
            </div>
            <div v-if="charter.standard_compliance" class="mt-4">
              <h3 class="font-medium text-gray-900 mb-2">Standard Compliance</h3>
              <div class="prose prose-sm max-w-none" v-html="charter.standard_compliance"></div>
            </div>
          </div>

          <div v-if="activeSection === 'notes'" class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Additional Notes</h2>
            <div v-if="charter.additional_notes" class="prose prose-sm max-w-none" v-html="charter.additional_notes"></div>
            <p v-else class="text-gray-500">No additional notes.</p>
          </div>
        </div>
      </div>
    </template>

    <!-- No Charter -->
    <div v-else class="bg-white rounded-lg border border-gray-200 p-12 text-center">
      <FileTextIcon class="h-12 w-12 text-gray-300 mx-auto mb-3" />
      <p class="text-gray-600">No audit charter found.</p>
      <p class="text-sm text-gray-500 mt-1">Create one via the Frappe desk.</p>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, Spinner } from "frappe-ui"
import { createResource } from "frappe-ui"
import {
	ExternalLinkIcon,
	FileTextIcon,
} from "lucide-vue-next"
import { onMounted, ref } from "vue"

const loading = ref(true)
const charter = ref(null)
const activeSection = ref("purpose")

const sections = [
	{ id: "purpose", label: "Purpose" },
	{ id: "authority", label: "Authority" },
	{ id: "responsibility", label: "Responsibility" },
	{ id: "reporting", label: "Reporting Structure" },
	{ id: "scope", label: "Scope & Objectives" },
	{ id: "independence", label: "Independence" },
	{ id: "governance", label: "Governance & Standards" },
	{ id: "notes", label: "Additional Notes" },
]

const getStatusVariant = (status) => {
	const map = { Draft: "secondary", Active: "success", Expired: "danger", Superseded: "warning" }
	return map[status] || "secondary"
}

const getApprovalVariant = (status) => {
	const map = { Pending: "warning", Approved: "success", Rejected: "danger" }
	return map[status] || "secondary"
}

const formatDate = (date) => {
	if (!date) return "-"
	return new Date(date).toLocaleDateString()
}

const openInDesk = () => {
	if (charter.value) {
		window.open(`/app/audit-charter/${charter.value.name}`, "_blank")
	}
}

const loadCharter = async () => {
	loading.value = true
	try {
		const res = await createResource({
			url: "frappe.client.get_list",
			params: {
				doctype: "Audit Charter",
				fields: ["name"],
				filters: { status: "Active" },
				order_by: "effective_date desc",
				limit_page_length: 1,
			},
		}).fetch()

		if (res && res.length > 0) {
			const detail = await createResource({
				url: "frappe.client.get",
				params: { doctype: "Audit Charter", name: res[0].name },
			}).fetch()
			charter.value = detail
		} else {
			const allRes = await createResource({
				url: "frappe.client.get_list",
				params: {
					doctype: "Audit Charter",
					fields: ["name"],
					order_by: "creation desc",
					limit_page_length: 1,
				},
			}).fetch()
			if (allRes && allRes.length > 0) {
				const detail = await createResource({
					url: "frappe.client.get",
					params: { doctype: "Audit Charter", name: allRes[0].name },
				}).fetch()
				charter.value = detail
			}
		}
	} catch (err) {
		console.error("Failed to load charter:", err)
	} finally {
		loading.value = false
	}
}

onMounted(() => {
	loadCharter()
})
</script>
