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
            {{ isEdit ? 'Edit Issue' : 'Log New Issue' }}
          </h1>
          <p class="text-gray-500 mt-1">
            {{ isEdit ? `Editing ${route.params.id}` : 'Report a new stock take issue' }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="solid" @click="saveIssue" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          {{ isEdit ? 'Save Changes' : 'Log Issue' }}
        </Button>
      </div>
    </div>

    <!-- Form -->
    <div class="max-w-4xl">
      <div class="space-y-6">
        <!-- Basic Information -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Issue Type <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="select"
                v-model="form.issue_type"
                :options="issueTypeOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Severity</label>
              <FormControl
                type="select"
                v-model="form.severity"
                :options="severityOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <FormControl
                type="select"
                v-model="form.priority"
                :options="priorityOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <FormControl
                type="select"
                v-model="form.status"
                :options="statusOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Reported By</label>
              <FormControl
                type="autocomplete"
                v-model="form.reported_by"
                :options="userOptions"
                placeholder="Select user"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Assigned To</label>
              <FormControl
                type="autocomplete"
                v-model="form.assigned_to"
                :options="userOptions"
                placeholder="Select assignee"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Reported Date</label>
              <FormControl
                type="date"
                v-model="form.reported_date"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
              <FormControl
                type="date"
                v-model="form.due_date"
              />
            </div>
          </div>
        </div>

        <!-- Issue Details -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Issue Details</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Description <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="textarea"
                v-model="form.description"
                placeholder="Describe the issue in detail..."
                :rows="4"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <FormControl
                type="text"
                v-model="form.location"
                placeholder="Where did this issue occur?"
              />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Item Code</label>
                <FormControl
                  type="autocomplete"
                  v-model="form.item_code"
                  :options="itemOptions"
                  placeholder="Select affected item"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Quantity Affected</label>
                <FormControl
                  type="number"
                  v-model="form.quantity_affected"
                  placeholder="0"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Related Records -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Related Records</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Stock Take Session</label>
              <FormControl
                type="autocomplete"
                v-model="form.stock_take_session"
                :options="sessionOptions"
                placeholder="Link to session"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Variance Case</label>
              <FormControl
                type="autocomplete"
                v-model="form.variance_case"
                :options="varianceCaseOptions"
                placeholder="Link to variance case"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Audit Plan</label>
              <FormControl
                type="autocomplete"
                v-model="form.audit_plan"
                :options="auditPlanOptions"
                placeholder="Link to audit plan"
              />
            </div>
          </div>
        </div>

        <!-- Resolution (for resolved issues) -->
        <div v-if="form.status === 'Resolved'" class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Resolution Details</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Resolution</label>
              <FormControl
                type="textarea"
                v-model="form.resolution"
                placeholder="Describe how this issue was resolved..."
                :rows="3"
              />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Resolved By</label>
                <FormControl
                  type="autocomplete"
                  v-model="form.resolved_by"
                  :options="userOptions"
                  placeholder="Select user"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Resolved Date</label>
                <FormControl
                  type="date"
                  v-model="form.resolved_date"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Additional Notes -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Additional Notes</h3>
          <FormControl
            type="textarea"
            v-model="form.notes"
            placeholder="Any additional notes or observations..."
            :rows="3"
          />
        </div>
      </div>

      <!-- Form Actions (Bottom) -->
      <div class="flex items-center justify-end gap-3 mt-6 pt-6 border-t">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="solid" @click="saveIssue" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          {{ isEdit ? 'Save Changes' : 'Log Issue' }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, FormControl } from "frappe-ui"
import { call } from "frappe-ui"
import { ArrowLeft, Save } from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"

const route = useRoute()
const router = useRouter()

const saving = ref(false)
const userOptions = ref([])
const itemOptions = ref([])
const sessionOptions = ref([])
const varianceCaseOptions = ref([])
const auditPlanOptions = ref([])

const isEdit = computed(() => route.params.id && route.params.id !== "new")

const form = ref({
	issue_type: "",
	severity: "Medium",
	priority: "Medium",
	status: "Open",
	reported_by: "",
	assigned_to: "",
	reported_date: new Date().toISOString().split("T")[0],
	due_date: "",
	description: "",
	location: "",
	item_code: "",
	quantity_affected: 0,
	stock_take_session: "",
	variance_case: "",
	audit_plan: "",
	resolution: "",
	resolved_by: "",
	resolved_date: "",
	notes: "",
})

onMounted(async () => {
	await Promise.all([
		loadUsers(),
		loadItems(),
		loadSessions(),
		loadVarianceCases(),
		loadAuditPlans(),
	])

	if (isEdit.value) {
		await loadIssue()
	}

	// Set current user as reported_by if not editing
	if (!isEdit.value && !form.value.reported_by) {
		form.value.reported_by = frappe.session.user
	}
})

async function loadUsers() {
	try {
		const users = await call("frappe.client.get_list", {
			doctype: "User",
			filters: { enabled: 1, user_type: "System User" },
			fields: ["name", "full_name"],
			limit_page_length: 0,
		})
		userOptions.value = users.map((u) => ({
			label: u.full_name || u.name,
			value: u.name,
		}))
	} catch (error) {
		console.error("Error loading users:", error)
	}
}

async function loadItems() {
	try {
		const items = await call("frappe.client.get_list", {
			doctype: "Item",
			fields: ["name", "item_name"],
			limit_page_length: 0,
		})
		itemOptions.value = items.map((i) => ({
			label: `${i.name} - ${i.item_name}`,
			value: i.name,
		}))
	} catch (error) {
		console.error("Error loading items:", error)
	}
}

async function loadSessions() {
	try {
		const sessions = await call("frappe.client.get_list", {
			doctype: "Stock Take Session",
			fields: ["name", "title"],
			limit_page_length: 0,
		})
		sessionOptions.value = sessions.map((s) => ({
			label: s.title || s.name,
			value: s.name,
		}))
	} catch (error) {
		console.error("Error loading sessions:", error)
	}
}

async function loadVarianceCases() {
	try {
		const cases = await call("frappe.client.get_list", {
			doctype: "Variance Case",
			fields: ["name", "title"],
			limit_page_length: 0,
		})
		varianceCaseOptions.value = cases.map((c) => ({
			label: c.title || c.name,
			value: c.name,
		}))
	} catch (error) {
		console.error("Error loading variance cases:", error)
	}
}

async function loadAuditPlans() {
	try {
		const plans = await call("frappe.client.get_list", {
			doctype: "Audit Plan",
			fields: ["name", "title"],
			limit_page_length: 0,
		})
		auditPlanOptions.value = plans.map((p) => ({
			label: p.title || p.name,
			value: p.name,
		}))
	} catch (error) {
		console.error("Error loading audit plans:", error)
	}
}

async function loadIssue() {
	try {
		const issue = await call("frappe.client.get", {
			doctype: "Issue Log",
			name: route.params.id,
		})

		form.value = {
			issue_type: issue.issue_type || "",
			severity: issue.severity || "Medium",
			priority: issue.priority || "Medium",
			status: issue.status || "Open",
			reported_by: issue.reported_by || "",
			assigned_to: issue.assigned_to || "",
			reported_date: issue.reported_date || "",
			due_date: issue.due_date || "",
			description: issue.description || "",
			location: issue.location || "",
			item_code: issue.item_code || "",
			quantity_affected: issue.quantity_affected || 0,
			stock_take_session: issue.stock_take_session || "",
			variance_case: issue.variance_case || "",
			audit_plan: issue.audit_plan || "",
			resolution: issue.resolution || "",
			resolved_by: issue.resolved_by || "",
			resolved_date: issue.resolved_date || "",
			notes: issue.notes || "",
		}
	} catch (error) {
		console.error("Error loading issue:", error)
	}
}

async function saveIssue() {
	// Validate required fields
	if (!form.value.issue_type) {
		alert("Issue type is required")
		return
	}
	if (!form.value.description) {
		alert("Description is required")
		return
	}

	saving.value = true

	try {
		if (isEdit.value) {
			// Update existing
			await call("frappe.client.set_value", {
				doctype: "Issue Log",
				name: route.params.id,
				fieldname: form.value,
			})
			router.push(`/inventory-audit/issues/${route.params.id}`)
		} else {
			// Create new
			const result = await call("frappe.client.insert", {
				doc: {
					doctype: "Issue Log",
					...form.value,
				},
			})
			router.push(`/inventory-audit/issues/${result.name}`)
		}
	} catch (error) {
		console.error("Error saving issue:", error)
		alert("Error saving issue: " + error.message)
	} finally {
		saving.value = false
	}
}

function goBack() {
	if (isEdit.value) {
		router.push(`/inventory-audit/issues/${route.params.id}`)
	} else {
		router.push("/inventory-audit/issues")
	}
}

// Options
const issueTypeOptions = [
	{ label: "Stock Discrepancy", value: "Stock Discrepancy" },
	{ label: "Quality Issue", value: "Quality Issue" },
	{ label: "Documentation Error", value: "Documentation Error" },
	{ label: "Process Violation", value: "Process Violation" },
	{ label: "System Error", value: "System Error" },
	{ label: "Other", value: "Other" },
]

const severityOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Medium", value: "Medium" },
	{ label: "High", value: "High" },
	{ label: "Critical", value: "Critical" },
]

const priorityOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Medium", value: "Medium" },
	{ label: "High", value: "High" },
	{ label: "Urgent", value: "Urgent" },
]

const statusOptions = [
	{ label: "Open", value: "Open" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Resolved", value: "Resolved" },
	{ label: "Closed", value: "Closed" },
]
</script>
