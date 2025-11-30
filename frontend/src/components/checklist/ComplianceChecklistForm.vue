<template>
  <Dialog
    v-model="dialogVisible"
    :options="{
      size: '7xl',
      title: isEditing ? 'Edit Compliance Checklist' : 'New Compliance Checklist',
    }"
  >
    <template #body-content>
      <div class="flex h-[75vh]">
        <!-- Section Navigation Sidebar -->
        <div class="w-56 border-r pr-4 flex-shrink-0">
          <nav class="space-y-1 sticky top-0">
            <button
              v-for="(section, index) in sections"
              :key="section.id"
              @click="activeSection = section.id"
              :class="[
                'w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
                activeSection === section.id
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-gray-600 hover:bg-gray-50',
              ]"
            >
              <component
                :is="section.icon"
                class="h-4 w-4"
                :class="activeSection === section.id ? 'text-blue-600' : 'text-gray-400'"
              />
              <span class="flex-1">{{ section.label }}</span>
              <CheckCircle
                v-if="isSectionComplete(section.id)"
                class="h-4 w-4 text-green-500"
              />
            </button>
          </nav>

          <!-- Progress Summary -->
          <div class="mt-6 pt-6 border-t">
            <div class="text-xs font-medium text-gray-500 mb-2">Completion</div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full transition-all"
                :style="{ width: `${completionPercentage}%` }"
              />
            </div>
            <div class="text-xs text-gray-500 mt-1">{{ completionPercentage }}% complete</div>
          </div>
        </div>

        <!-- Form Content -->
        <div class="flex-1 pl-6 overflow-y-auto">
          <!-- Basic Information Section -->
          <div v-show="activeSection === 'basic'" class="space-y-6">
            <SectionHeader
              title="Basic Information"
              description="Checklist identification and period details"
            />

            <div class="grid grid-cols-2 gap-6">
              <FormControl
                v-model="form.checklist_id"
                label="Checklist ID"
                type="text"
                :required="true"
                placeholder="Auto-generated if left empty"
              />
              <LinkField
                v-model="form.compliance_period"
                label="Compliance Period"
                doctype="Data Period"
                placeholder="Select period"
              />
            </div>

            <div class="grid grid-cols-3 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Period Type <span class="text-red-500">*</span>
                </label>
                <Select
                  v-model="form.period_type"
                  :options="periodTypeOptions"
                  placeholder="Select type"
                />
              </div>
              <FormControl
                v-model="form.period_month"
                label="Period Month"
                type="text"
                placeholder="e.g., January 2025"
              />
              <LinkField
                v-model="form.fiscal_year"
                label="Fiscal Year"
                doctype="Fiscal Year"
                placeholder="Select fiscal year"
              />
            </div>
          </div>

          <!-- Checklist Items Section -->
          <div v-show="activeSection === 'items'" class="space-y-6">
            <SectionHeader
              title="Checklist Items"
              description="Compliance requirements and their status"
            />

            <!-- Add Item Button -->
            <div class="flex justify-end">
              <Button variant="outline" @click="addChecklistItem">
                <template #prefix><Plus class="h-4 w-4" /></template>
                Add Item
              </Button>
            </div>

            <!-- Checklist Items Table -->
            <div class="border rounded-lg overflow-hidden">
              <table class="w-full">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Requirement
                    </th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Regulatory Body
                    </th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Due Date
                    </th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Verification
                    </th>
                    <th class="px-4 py-3 w-20"></th>
                  </tr>
                </thead>
                <tbody class="divide-y">
                  <tr
                    v-for="(item, index) in form.checklist_items"
                    :key="index"
                    class="hover:bg-gray-50"
                  >
                    <td class="px-4 py-3">
                      <LinkField
                        v-model="item.requirement"
                        doctype="Compliance Requirement"
                        placeholder="Select requirement"
                        size="sm"
                      />
                    </td>
                    <td class="px-4 py-3">
                      <FormControl
                        v-model="item.regulatory_body"
                        type="text"
                        size="sm"
                        :disabled="true"
                        placeholder="Auto-filled"
                      />
                    </td>
                    <td class="px-4 py-3">
                      <FormControl
                        v-model="item.due_date"
                        type="date"
                        size="sm"
                      />
                    </td>
                    <td class="px-4 py-3">
                      <Select
                        v-model="item.status"
                        :options="itemStatusOptions"
                        size="sm"
                      />
                    </td>
                    <td class="px-4 py-3">
                      <Select
                        v-model="item.verification_status"
                        :options="verificationStatusOptions"
                        size="sm"
                      />
                    </td>
                    <td class="px-4 py-3">
                      <div class="flex items-center gap-1">
                        <Button
                          size="sm"
                          variant="ghost"
                          @click="editChecklistItem(index)"
                        >
                          <Edit class="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          theme="red"
                          @click="removeChecklistItem(index)"
                        >
                          <Trash2 class="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="!form.checklist_items?.length">
                    <td colspan="6" class="px-4 py-8 text-center text-gray-500">
                      <ClipboardList class="h-8 w-8 mx-auto mb-2 text-gray-400" />
                      <p>No checklist items added</p>
                      <p class="text-sm mt-1">Click "Add Item" to add compliance requirements</p>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Summary Section -->
          <div v-show="activeSection === 'summary'" class="space-y-6">
            <SectionHeader
              title="Summary"
              description="Compliance completion overview"
            />

            <div class="grid grid-cols-4 gap-4">
              <div class="bg-blue-50 rounded-lg p-4 text-center">
                <p class="text-3xl font-bold text-blue-600">{{ form.total_requirements }}</p>
                <p class="text-sm text-blue-700">Total Requirements</p>
              </div>
              <div class="bg-green-50 rounded-lg p-4 text-center">
                <p class="text-3xl font-bold text-green-600">{{ form.completed_requirements }}</p>
                <p class="text-sm text-green-700">Completed</p>
              </div>
              <div class="bg-red-50 rounded-lg p-4 text-center">
                <p class="text-3xl font-bold text-red-600">{{ form.overdue_requirements }}</p>
                <p class="text-sm text-red-700">Overdue</p>
              </div>
              <div class="bg-purple-50 rounded-lg p-4 text-center">
                <p class="text-3xl font-bold text-purple-600">{{ form.completion_percent }}%</p>
                <p class="text-sm text-purple-700">Completion</p>
              </div>
            </div>

            <!-- Completion Progress Bar -->
            <div class="border rounded-lg p-6">
              <div class="flex items-center justify-between mb-3">
                <h4 class="font-medium text-gray-700">Overall Progress</h4>
                <Badge :theme="getCompletionTheme(form.completion_percent)" size="lg">
                  {{ form.completion_percent }}%
                </Badge>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-4">
                <div
                  class="h-4 rounded-full transition-all"
                  :class="getCompletionBarClass(form.completion_percent)"
                  :style="{ width: `${form.completion_percent || 0}%` }"
                />
              </div>
            </div>

            <!-- Status Breakdown -->
            <div class="border rounded-lg p-4">
              <h4 class="font-medium text-gray-700 mb-4">Status Breakdown</h4>
              <div class="space-y-3">
                <div
                  v-for="status in statusBreakdown"
                  :key="status.label"
                  class="flex items-center gap-3"
                >
                  <div class="w-28 text-sm text-gray-600">{{ status.label }}</div>
                  <div class="flex-1 bg-gray-100 rounded-full h-2">
                    <div
                      class="h-2 rounded-full"
                      :class="status.color"
                      :style="{ width: `${status.percentage}%` }"
                    />
                  </div>
                  <div class="w-12 text-sm text-gray-600 text-right">{{ status.count }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Alerts Section -->
          <div v-show="activeSection === 'alerts'" class="space-y-6">
            <SectionHeader
              title="Alerts"
              description="Compliance alerts and notifications"
            />

            <!-- Add Alert Button -->
            <div class="flex justify-end">
              <Button variant="outline" @click="addAlert">
                <template #prefix><Bell class="h-4 w-4" /></template>
                Add Alert
              </Button>
            </div>

            <!-- Alerts List -->
            <div class="space-y-3">
              <div
                v-for="(alert, index) in form.alerts"
                :key="index"
                class="border rounded-lg p-4"
                :class="getAlertBorderClass(alert.severity)"
              >
                <div class="flex items-start gap-4">
                  <div
                    class="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
                    :class="getAlertIconBgClass(alert.severity)"
                  >
                    <AlertTriangle
                      class="h-5 w-5"
                      :class="getAlertIconClass(alert.severity)"
                    />
                  </div>
                  <div class="flex-1 grid grid-cols-3 gap-4">
                    <LinkField
                      v-model="alert.requirement"
                      doctype="Compliance Requirement"
                      label="Requirement"
                      placeholder="Select requirement"
                    />
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Alert Type</label>
                      <Select
                        v-model="alert.alert_type"
                        :options="alertTypeOptions"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Severity</label>
                      <Select
                        v-model="alert.severity"
                        :options="severityOptions"
                      />
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    theme="red"
                    @click="removeAlert(index)"
                  >
                    <Trash2 class="h-4 w-4" />
                  </Button>
                </div>
                <div class="mt-3 ml-14">
                  <FormControl
                    v-model="alert.alert_message"
                    type="textarea"
                    :rows="2"
                    placeholder="Enter alert message..."
                  />
                </div>
              </div>

              <div v-if="!form.alerts?.length" class="border rounded-lg p-8 text-center text-gray-500">
                <Bell class="h-8 w-8 mx-auto mb-2 text-gray-400" />
                <p>No alerts configured</p>
                <p class="text-sm mt-1">Click "Add Alert" to create compliance alerts</p>
              </div>
            </div>
          </div>

          <!-- Approval Section -->
          <div v-show="activeSection === 'approval'" class="space-y-6">
            <SectionHeader
              title="Approval"
              description="Checklist review and approval workflow"
            />

            <div class="grid grid-cols-3 gap-6">
              <div class="border rounded-lg p-4">
                <div class="flex items-center gap-3 mb-4">
                  <div class="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center">
                    <FileEdit class="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 class="font-medium text-gray-700">Prepared By</h4>
                    <p class="text-xs text-gray-500">Person who prepared this checklist</p>
                  </div>
                </div>
                <LinkField
                  v-model="form.prepared_by"
                  doctype="User"
                  placeholder="Select user"
                  :disabled="true"
                />
              </div>

              <div class="border rounded-lg p-4">
                <div class="flex items-center gap-3 mb-4">
                  <div class="h-10 w-10 rounded-lg bg-purple-50 flex items-center justify-center">
                    <Eye class="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <h4 class="font-medium text-gray-700">Reviewed By</h4>
                    <p class="text-xs text-gray-500">Person who reviewed this checklist</p>
                  </div>
                </div>
                <LinkField
                  v-model="form.reviewed_by"
                  doctype="User"
                  placeholder="Select reviewer"
                />
              </div>

              <div class="border rounded-lg p-4">
                <div class="flex items-center gap-3 mb-4">
                  <div class="h-10 w-10 rounded-lg bg-green-50 flex items-center justify-center">
                    <CheckCircle class="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <h4 class="font-medium text-gray-700">Approved By</h4>
                    <p class="text-xs text-gray-500">Person who approved this checklist</p>
                  </div>
                </div>
                <LinkField
                  v-model="form.approved_by"
                  doctype="User"
                  placeholder="Select approver"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Checklist Item Detail Modal -->
      <Dialog
        v-model="showItemModal"
        :options="{ size: '3xl', title: 'Edit Checklist Item' }"
      >
        <template #body-content>
          <div v-if="editingItem" class="space-y-6">
            <div class="grid grid-cols-2 gap-6">
              <LinkField
                v-model="editingItem.requirement"
                label="Requirement"
                doctype="Compliance Requirement"
                :required="true"
              />
              <FormControl
                v-model="editingItem.regulatory_body"
                label="Regulatory Body"
                type="text"
                :disabled="true"
              />
            </div>

            <FormControl
              v-model="editingItem.description"
              label="Description"
              type="text"
              :disabled="true"
            />

            <div class="grid grid-cols-3 gap-6">
              <FormControl
                v-model="editingItem.due_date"
                label="Due Date"
                type="date"
              />
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <Select
                  v-model="editingItem.status"
                  :options="itemStatusOptions"
                />
              </div>
              <FormControl
                v-model="editingItem.completion_date"
                label="Completion Date"
                type="date"
              />
            </div>

            <div class="grid grid-cols-2 gap-6">
              <LinkField
                v-model="editingItem.completed_by"
                label="Completed By"
                doctype="User"
              />
              <FormControl
                v-model="editingItem.reference_no"
                label="Reference No"
                type="text"
              />
            </div>

            <div class="border-t pt-6">
              <h4 class="font-medium text-gray-700 mb-4">Payment Details</h4>
              <div class="grid grid-cols-3 gap-6">
                <FormControl
                  v-model="editingItem.amount_paid"
                  label="Amount Paid"
                  type="number"
                  placeholder="0.00"
                />
                <FormControl
                  v-model="editingItem.payment_date"
                  label="Payment Date"
                  type="date"
                />
                <FormControl
                  v-model="editingItem.payment_reference"
                  label="Payment Reference"
                  type="text"
                />
              </div>
            </div>

            <FormControl
              v-model="editingItem.notes"
              label="Notes"
              type="textarea"
              :rows="3"
            />

            <div class="border-t pt-6">
              <h4 class="font-medium text-gray-700 mb-4">Verification</h4>
              <div class="grid grid-cols-3 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <Select
                    v-model="editingItem.verification_status"
                    :options="verificationStatusOptions"
                  />
                </div>
                <LinkField
                  v-model="editingItem.verified_by"
                  label="Verified By"
                  doctype="User"
                />
                <FormControl
                  v-model="editingItem.verification_date"
                  label="Verification Date"
                  type="date"
                />
              </div>
              <div class="mt-4">
                <FormControl
                  v-model="editingItem.verification_notes"
                  label="Verification Notes"
                  type="textarea"
                  :rows="2"
                />
              </div>
            </div>
          </div>
        </template>
        <template #actions>
          <Button variant="outline" @click="showItemModal = false">Cancel</Button>
          <Button variant="solid" @click="saveItemEdit">Save Changes</Button>
        </template>
      </Dialog>
    </template>

    <template #actions>
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-2">
          <Button
            v-if="activeSection !== 'basic'"
            variant="outline"
            @click="previousSection"
          >
            <template #prefix><ChevronLeft class="h-4 w-4" /></template>
            Previous
          </Button>
        </div>
        <div class="flex items-center gap-2">
          <Button variant="outline" @click="dialogVisible = false">Cancel</Button>
          <Button
            v-if="activeSection !== 'approval'"
            variant="solid"
            @click="nextSection"
          >
            Next
            <template #suffix><ChevronRight class="h-4 w-4" /></template>
          </Button>
          <Button
            v-else
            variant="solid"
            theme="green"
            :loading="saving"
            @click="saveChecklist"
          >
            <template #prefix><Save class="h-4 w-4" /></template>
            {{ isEditing ? 'Update Checklist' : 'Create Checklist' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import SectionHeader from "@/components/Common/SectionHeader.vue"
import LinkField from "@/components/Common/fields/LinkField.vue"
import { Badge, Button, Dialog, FormControl, Select } from "frappe-ui"
import {
	AlertTriangle,
	BarChart3,
	Bell,
	CheckCircle,
	ChevronLeft,
	ChevronRight,
	ClipboardList,
	Edit,
	Eye,
	FileEdit,
	FileText,
	Plus,
	Save,
	Trash2,
	UserCheck,
} from "lucide-vue-next"
import { computed, reactive, ref, watch } from "vue"

const props = defineProps({
	show: { type: Boolean, default: false },
	checklist: { type: Object, default: null },
})

const emit = defineEmits(["update:show", "saved"])

const dialogVisible = computed({
	get: () => props.show,
	set: (val) => emit("update:show", val),
})

const isEditing = computed(() => !!props.checklist?.name)
const saving = ref(false)
const activeSection = ref("basic")
const showItemModal = ref(false)
const editingItem = ref(null)
const editingItemIndex = ref(-1)

const sections = [
	{ id: "basic", label: "Basic Info", icon: FileText },
	{ id: "items", label: "Checklist Items", icon: ClipboardList },
	{ id: "summary", label: "Summary", icon: BarChart3 },
	{ id: "alerts", label: "Alerts", icon: Bell },
	{ id: "approval", label: "Approval", icon: UserCheck },
]

const form = reactive({
	checklist_id: "",
	compliance_period: "",
	period_type: "",
	period_month: "",
	fiscal_year: "",
	checklist_items: [],
	total_requirements: 0,
	completed_requirements: 0,
	overdue_requirements: 0,
	completion_percent: 0,
	alerts: [],
	prepared_by: "",
	reviewed_by: "",
	approved_by: "",
})

const periodTypeOptions = [
	{ label: "Monthly", value: "Monthly" },
	{ label: "Quarterly", value: "Quarterly" },
	{ label: "Annual", value: "Annual" },
]

const itemStatusOptions = [
	{ label: "Not Started", value: "Not Started" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Completed", value: "Completed" },
	{ label: "Filed", value: "Filed" },
	{ label: "Overdue", value: "Overdue" },
	{ label: "Not Applicable", value: "Not Applicable" },
]

const verificationStatusOptions = [
	{ label: "Not Verified", value: "Not Verified" },
	{ label: "Verified", value: "Verified" },
	{ label: "Issues Found", value: "Issues Found" },
]

const alertTypeOptions = [
	{ label: "Due Soon", value: "Due Soon" },
	{ label: "Overdue", value: "Overdue" },
	{ label: "Missing Data", value: "Missing Data" },
]

const severityOptions = [
	{ label: "Critical", value: "Critical" },
	{ label: "High", value: "High" },
	{ label: "Medium", value: "Medium" },
	{ label: "Low", value: "Low" },
]

// Watch for checklist changes (edit mode)
watch(
	() => props.checklist,
	(newChecklist) => {
		if (newChecklist) {
			Object.keys(form).forEach((key) => {
				if (newChecklist[key] !== undefined) {
					form[key] = newChecklist[key]
				}
			})
		}
	},
	{ immediate: true },
)

// Reset form when dialog opens
watch(
	() => props.show,
	(newShow) => {
		if (newShow && !props.checklist) {
			Object.keys(form).forEach((key) => {
				if (key === "checklist_items" || key === "alerts") {
					form[key] = []
				} else if (typeof form[key] === "number") {
					form[key] = 0
				} else {
					form[key] = ""
				}
			})
			activeSection.value = "basic"
		}
	},
)

// Recalculate summary when items change
watch(
	() => form.checklist_items,
	() => {
		calculateSummary()
	},
	{ deep: true },
)

function calculateSummary() {
	const items = form.checklist_items || []
	form.total_requirements = items.length
	form.completed_requirements = items.filter((i) =>
		["Completed", "Filed"].includes(i.status),
	).length
	form.overdue_requirements = items.filter((i) => i.status === "Overdue").length
	form.completion_percent =
		items.length > 0
			? Math.round((form.completed_requirements / items.length) * 100)
			: 0
}

const statusBreakdown = computed(() => {
	const items = form.checklist_items || []
	const total = items.length || 1

	const statuses = [
		{ label: "Not Started", color: "bg-gray-400" },
		{ label: "In Progress", color: "bg-blue-500" },
		{ label: "Completed", color: "bg-green-500" },
		{ label: "Filed", color: "bg-purple-500" },
		{ label: "Overdue", color: "bg-red-500" },
		{ label: "Not Applicable", color: "bg-gray-300" },
	]

	return statuses.map((s) => {
		const count = items.filter((i) => i.status === s.label).length
		return {
			...s,
			count,
			percentage: Math.round((count / total) * 100),
		}
	})
})

// Checklist item management
function addChecklistItem() {
	form.checklist_items.push({
		requirement: "",
		regulatory_body: "",
		description: "",
		due_date: "",
		status: "Not Started",
		completion_date: "",
		completed_by: "",
		reference_no: "",
		amount_paid: 0,
		payment_date: "",
		payment_reference: "",
		supporting_documents: "",
		notes: "",
		verification_status: "Not Verified",
		verified_by: "",
		verification_date: "",
		verification_notes: "",
	})
}

function editChecklistItem(index) {
	editingItemIndex.value = index
	editingItem.value = { ...form.checklist_items[index] }
	showItemModal.value = true
}

function saveItemEdit() {
	if (editingItemIndex.value >= 0 && editingItem.value) {
		form.checklist_items[editingItemIndex.value] = { ...editingItem.value }
	}
	showItemModal.value = false
	editingItem.value = null
	editingItemIndex.value = -1
}

function removeChecklistItem(index) {
	form.checklist_items.splice(index, 1)
}

// Alert management
function addAlert() {
	form.alerts.push({
		requirement: "",
		alert_type: "",
		alert_message: "",
		severity: "Medium",
	})
}

function removeAlert(index) {
	form.alerts.splice(index, 1)
}

// Section navigation
const sectionIndex = computed(() =>
	sections.findIndex((s) => s.id === activeSection.value),
)

function nextSection() {
	if (sectionIndex.value < sections.length - 1) {
		activeSection.value = sections[sectionIndex.value + 1].id
	}
}

function previousSection() {
	if (sectionIndex.value > 0) {
		activeSection.value = sections[sectionIndex.value - 1].id
	}
}

// Section completion check
function isSectionComplete(sectionId) {
	switch (sectionId) {
		case "basic":
			return !!form.checklist_id && !!form.period_type
		case "items":
			return form.checklist_items?.length > 0
		case "summary":
			return true
		case "alerts":
			return true
		case "approval":
			return !!form.approved_by
		default:
			return false
	}
}

const completionPercentage = computed(() => {
	const completed = sections.filter((s) => isSectionComplete(s.id)).length
	return Math.round((completed / sections.length) * 100)
})

// Helpers
function getCompletionTheme(percent) {
	if (percent >= 90) return "green"
	if (percent >= 70) return "blue"
	if (percent >= 50) return "orange"
	return "red"
}

function getCompletionBarClass(percent) {
	if (percent >= 90) return "bg-green-500"
	if (percent >= 70) return "bg-blue-500"
	if (percent >= 50) return "bg-orange-500"
	return "bg-red-500"
}

function getAlertBorderClass(severity) {
	const classes = {
		Critical: "border-red-200 bg-red-50",
		High: "border-orange-200 bg-orange-50",
		Medium: "border-yellow-200 bg-yellow-50",
		Low: "border-blue-200 bg-blue-50",
	}
	return classes[severity] || "border-gray-200"
}

function getAlertIconBgClass(severity) {
	const classes = {
		Critical: "bg-red-100",
		High: "bg-orange-100",
		Medium: "bg-yellow-100",
		Low: "bg-blue-100",
	}
	return classes[severity] || "bg-gray-100"
}

function getAlertIconClass(severity) {
	const classes = {
		Critical: "text-red-600",
		High: "text-orange-600",
		Medium: "text-yellow-600",
		Low: "text-blue-600",
	}
	return classes[severity] || "text-gray-600"
}

async function saveChecklist() {
	saving.value = true
	try {
		// API call would go here
		await new Promise((resolve) => setTimeout(resolve, 1000))
		emit("saved", { ...form })
		dialogVisible.value = false
	} catch (error) {
		console.error("Failed to save checklist:", error)
	} finally {
		saving.value = false
	}
}
</script>
