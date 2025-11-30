<template>
  <Dialog
    v-model="dialogVisible"
    :options="{
      title: isEditMode ? 'Edit Data Period' : 'Create Data Period',
      size: '5xl',
    }"
  >
    <template #body-content>
      <div class="flex h-[65vh]">
        <!-- Left Sidebar: Section Navigation -->
        <div class="w-52 border-r bg-gray-50 p-4 flex flex-col">
          <div class="space-y-1 flex-1">
            <button
              v-for="(section, index) in sections"
              :key="section.id"
              @click="goToSection(index)"
              class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors"
              :class="
                currentSectionIndex === index
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              "
            >
              <component
                :is="section.icon"
                class="h-4 w-4"
                :class="getSectionStatusClass(index)"
              />
              <span class="text-sm">{{ section.title }}</span>
              <CheckCircle2
                v-if="isSectionComplete(index)"
                class="h-4 w-4 ml-auto text-green-500"
              />
            </button>
          </div>

          <!-- Progress Indicator -->
          <div class="mt-4 pt-4 border-t">
            <div class="text-xs text-gray-500 mb-2">
              Progress: {{ completedSections }}/{{ sections.length }} sections
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full transition-all"
                :style="{ width: `${progressPercentage}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Main Content Area -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <!-- Section Header -->
          <SectionHeader
            :icon="sections[currentSectionIndex]?.icon"
            :title="sections[currentSectionIndex]?.title"
            :description="sections[currentSectionIndex]?.description"
          />

          <!-- Section Content -->
          <div class="flex-1 overflow-y-auto p-6">
            <!-- Section 1: Period Details -->
            <div v-show="currentSectionIndex === 0" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <FormControl
                  v-model="formData.period_id"
                  label="Period ID *"
                  type="text"
                  placeholder="e.g., 2025-Q1"
                />
                <FormControl
                  v-model="formData.period_name"
                  label="Period Name *"
                  type="text"
                  placeholder="e.g., Q1 2025"
                />
              </div>

              <div class="grid grid-cols-3 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Period Type</label>
                  <Select
                    v-model="formData.period_type"
                    :options="periodTypeOptions"
                    placeholder="Select type"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Fiscal Year</label>
                  <LinkField
                    v-model="formData.fiscal_year"
                    doctype="Fiscal Year"
                    placeholder="Select fiscal year"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <Select
                    v-model="formData.status"
                    :options="statusOptions"
                    placeholder="Select status"
                  />
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <FormControl
                  v-model="formData.start_date"
                  label="Start Date *"
                  type="date"
                />
                <FormControl
                  v-model="formData.end_date"
                  label="End Date *"
                  type="date"
                />
              </div>

              <!-- Period Duration Display -->
              <div v-if="formData.start_date && formData.end_date" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div class="flex items-center gap-2">
                  <CalendarRange class="h-5 w-5 text-blue-600" />
                  <span class="text-sm text-blue-700">
                    Period Duration: <strong>{{ periodDuration }} days</strong>
                  </span>
                </div>
              </div>
            </div>

            <!-- Section 2: Data Quality -->
            <div v-show="currentSectionIndex === 1" class="space-y-4">
              <!-- Quality Score Cards -->
              <div class="grid grid-cols-2 gap-4">
                <div class="p-4 bg-white rounded-lg border">
                  <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-medium text-gray-700">Data Completeness</span>
                    <Badge :theme="getScoreTheme(formData.data_completeness_score)">
                      {{ formData.data_completeness_score || 0 }}%
                    </Badge>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-3">
                    <div
                      class="h-3 rounded-full transition-all"
                      :class="getScoreColor(formData.data_completeness_score)"
                      :style="{ width: `${formData.data_completeness_score || 0}%` }"
                    ></div>
                  </div>
                </div>

                <div class="p-4 bg-white rounded-lg border">
                  <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-medium text-gray-700">Data Quality</span>
                    <Badge :theme="getScoreTheme(formData.data_quality_score)">
                      {{ formData.data_quality_score || 0 }}%
                    </Badge>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-3">
                    <div
                      class="h-3 rounded-full transition-all"
                      :class="getScoreColor(formData.data_quality_score)"
                      :style="{ width: `${formData.data_quality_score || 0}%` }"
                    ></div>
                  </div>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Reconciliation Status</label>
                <Select
                  v-model="formData.reconciliation_status"
                  :options="reconciliationOptions"
                  placeholder="Select status"
                />
              </div>

              <!-- Import Checklist -->
              <div class="mt-6">
                <div class="flex items-center justify-between mb-3">
                  <h4 class="text-sm font-medium text-gray-700">Import Checklist</h4>
                  <Button size="sm" @click="addChecklistItem">
                    <template #prefix><Plus class="h-4 w-4" /></template>
                    Add Item
                  </Button>
                </div>
                <div class="border rounded-lg overflow-hidden">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Import Type</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Status</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Records</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Imported Date</th>
                        <th class="px-4 py-2 w-16"></th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="(item, idx) in formData.import_checklist" :key="idx">
                        <td class="px-4 py-2">
                          <FormControl v-model="item.import_type" type="text" size="sm" />
                        </td>
                        <td class="px-4 py-2">
                          <Select
                            v-model="item.status"
                            :options="importStatusOptions"
                            size="sm"
                          />
                        </td>
                        <td class="px-4 py-2">
                          <FormControl v-model="item.record_count" type="number" size="sm" />
                        </td>
                        <td class="px-4 py-2">
                          <FormControl v-model="item.imported_date" type="date" size="sm" />
                        </td>
                        <td class="px-4 py-2">
                          <Button variant="ghost" size="sm" @click="removeChecklistItem(idx)">
                            <Trash2 class="h-4 w-4 text-red-500" />
                          </Button>
                        </td>
                      </tr>
                      <tr v-if="!formData.import_checklist?.length">
                        <td colspan="5" class="px-4 py-8 text-center text-gray-500 text-sm">
                          No import checklist items. Click "Add Item" to add one.
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Section 3: Approval & Lock -->
            <div v-show="currentSectionIndex === 2" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Approved By</label>
                  <LinkField
                    v-model="formData.approved_by"
                    doctype="User"
                    placeholder="Select approver"
                  />
                </div>
                <FormControl
                  v-model="formData.approval_date"
                  label="Approval Date"
                  type="datetime-local"
                />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <FormControl
                  v-model="formData.lock_date"
                  label="Lock Date"
                  type="date"
                />
                <FormControl
                  v-model="formData.archive_date"
                  label="Archive Date"
                  type="date"
                />
              </div>

              <!-- Status Actions -->
              <div class="mt-6 bg-gray-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-700 mb-4">Period Actions</h4>
                <div class="flex flex-wrap gap-3">
                  <Button
                    variant="outline"
                    @click="lockPeriod"
                    :disabled="formData.status === 'Locked' || formData.status === 'Archived'"
                  >
                    <template #prefix><Lock class="h-4 w-4" /></template>
                    Lock Period
                  </Button>
                  <Button
                    variant="outline"
                    @click="unlockPeriod"
                    :disabled="formData.status !== 'Locked'"
                  >
                    <template #prefix><Unlock class="h-4 w-4" /></template>
                    Unlock Period
                  </Button>
                  <Button
                    variant="outline"
                    theme="orange"
                    @click="archivePeriod"
                    :disabled="formData.status === 'Archived'"
                  >
                    <template #prefix><Archive class="h-4 w-4" /></template>
                    Archive Period
                  </Button>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <TextEditor
                  v-model="formData.notes"
                  :content="formData.notes"
                  placeholder="Additional notes about this period..."
                  editor-class="prose-sm max-w-none min-h-[120px]"
                  :bubbleMenu="true"
                />
              </div>
            </div>
          </div>

          <!-- Footer Navigation -->
          <div class="border-t bg-gray-50 px-6 py-4 flex items-center justify-between">
            <Button
              variant="outline"
              @click="previousSection"
              :disabled="currentSectionIndex === 0"
            >
              <template #prefix><ChevronLeft class="h-4 w-4" /></template>
              Previous
            </Button>

            <div class="flex items-center gap-2">
              <Button variant="outline" @click="closeDialog">Cancel</Button>
              <Button
                v-if="currentSectionIndex < sections.length - 1"
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
                @click="savePeriod"
                :loading="saving"
              >
                <template #prefix><Save class="h-4 w-4" /></template>
                {{ isEditMode ? 'Update Period' : 'Create Period' }}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import SectionHeader from "@/components/Common/SectionHeader.vue"
import LinkField from "@/components/Common/fields/LinkField.vue"
import {
	Badge,
	Button,
	Dialog,
	FormControl,
	Select,
	TextEditor,
} from "frappe-ui"
import {
	Archive,
	BarChart3,
	CalendarRange,
	CheckCircle2,
	ChevronLeft,
	ChevronRight,
	Lock,
	Plus,
	Save,
	Shield,
	Trash2,
	Unlock,
} from "lucide-vue-next"
import { computed, reactive, ref, watch } from "vue"

const props = defineProps({
	show: { type: Boolean, default: false },
	period: { type: Object, default: null },
})

const emit = defineEmits(["update:show", "saved"])

const dialogVisible = computed({
	get: () => props.show,
	set: (val) => emit("update:show", val),
})

const isEditMode = computed(() => !!props.period?.name)
const saving = ref(false)
const currentSectionIndex = ref(0)

// Section definitions
const sections = [
	{
		id: "details",
		title: "Period Details",
		icon: CalendarRange,
		description: "Define period identification and dates",
	},
	{
		id: "quality",
		title: "Data Quality",
		icon: BarChart3,
		description: "Track data completeness and imports",
	},
	{
		id: "approval",
		title: "Approval & Lock",
		icon: Shield,
		description: "Manage period approval and archiving",
	},
]

// Form data
const formData = reactive({
	period_id: "",
	period_name: "",
	period_type: "",
	fiscal_year: "",
	start_date: "",
	end_date: "",
	status: "Open",
	data_completeness_score: 0,
	data_quality_score: 0,
	reconciliation_status: "",
	import_checklist: [],
	approved_by: "",
	approval_date: "",
	lock_date: "",
	archive_date: "",
	notes: "",
})

// Options
const periodTypeOptions = [
	{ label: "Month", value: "Month" },
	{ label: "Quarter", value: "Quarter" },
	{ label: "Half-Year", value: "Half-Year" },
	{ label: "Year", value: "Year" },
	{ label: "Custom", value: "Custom" },
]

const statusOptions = [
	{ label: "Open", value: "Open" },
	{ label: "Locked", value: "Locked" },
	{ label: "Closed", value: "Closed" },
	{ label: "Archived", value: "Archived" },
]

const reconciliationOptions = [
	{ label: "Not Started", value: "Not Started" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Completed", value: "Completed" },
	{ label: "Issues Found", value: "Issues Found" },
]

const importStatusOptions = [
	{ label: "Pending", value: "Pending" },
	{ label: "In Progress", value: "In Progress" },
	{ label: "Completed", value: "Completed" },
	{ label: "Failed", value: "Failed" },
]

// Watch for period prop changes
watch(
	() => props.period,
	(newPeriod) => {
		if (newPeriod) {
			Object.keys(formData).forEach((key) => {
				if (newPeriod[key] !== undefined) {
					formData[key] = newPeriod[key]
				}
			})
		} else {
			resetForm()
		}
	},
	{ immediate: true },
)

// Computed properties
const periodDuration = computed(() => {
	if (!formData.start_date || !formData.end_date) return 0
	const start = new Date(formData.start_date)
	const end = new Date(formData.end_date)
	return Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
})

// Section validation
const sectionValidation = computed(() => [
	!!(
		formData.period_id &&
		formData.period_name &&
		formData.start_date &&
		formData.end_date
	),
	true, // Data Quality - optional
	true, // Approval - optional
])

const completedSections = computed(
	() => sectionValidation.value.filter(Boolean).length,
)

const progressPercentage = computed(() =>
	Math.round((completedSections.value / sections.length) * 100),
)

function isSectionComplete(index) {
	return sectionValidation.value[index]
}

function getSectionStatusClass(index) {
	if (currentSectionIndex.value === index) return "text-blue-600"
	if (isSectionComplete(index)) return "text-green-500"
	return "text-gray-400"
}

function goToSection(index) {
	currentSectionIndex.value = index
}

function nextSection() {
	if (currentSectionIndex.value < sections.length - 1) {
		currentSectionIndex.value++
	}
}

function previousSection() {
	if (currentSectionIndex.value > 0) {
		currentSectionIndex.value--
	}
}

// Helper functions
function getScoreTheme(score) {
	if (score >= 80) return "green"
	if (score >= 60) return "orange"
	if (score >= 40) return "yellow"
	return "red"
}

function getScoreColor(score) {
	if (score >= 80) return "bg-green-500"
	if (score >= 60) return "bg-yellow-500"
	if (score >= 40) return "bg-orange-500"
	return "bg-red-500"
}

// Child table management
function addChecklistItem() {
	formData.import_checklist.push({
		import_type: "",
		status: "Pending",
		record_count: 0,
		imported_date: "",
	})
}

function removeChecklistItem(index) {
	formData.import_checklist.splice(index, 1)
}

// Period actions
function lockPeriod() {
	formData.status = "Locked"
	formData.lock_date = new Date().toISOString().split("T")[0]
}

function unlockPeriod() {
	formData.status = "Open"
	formData.lock_date = ""
}

function archivePeriod() {
	formData.status = "Archived"
	formData.archive_date = new Date().toISOString().split("T")[0]
}

function resetForm() {
	Object.keys(formData).forEach((key) => {
		if (Array.isArray(formData[key])) {
			formData[key] = []
		} else if (typeof formData[key] === "number") {
			formData[key] = 0
		} else {
			formData[key] = ""
		}
	})
	formData.status = "Open"
	currentSectionIndex.value = 0
}

function closeDialog() {
	emit("update:show", false)
	resetForm()
}

async function savePeriod() {
	saving.value = true
	try {
		console.log("Saving period:", formData)
		emit("saved", { ...formData })
		closeDialog()
	} catch (error) {
		console.error("Error saving period:", error)
	} finally {
		saving.value = false
	}
}
</script>
