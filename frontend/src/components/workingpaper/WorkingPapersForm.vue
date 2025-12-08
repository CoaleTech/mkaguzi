<template>
  <Dialog
    v-model="isOpen"
    :options="{
      title: isEditMode ? 'Edit Working Paper' : 'Create New Working Paper',
      size: 'full'
    }"
  >
    <template #body-content>
      <div class="h-[80vh] flex">
        <!-- Progress Sidebar -->
        <div class="w-64 bg-gray-50 border-r border-gray-200 flex-shrink-0 overflow-y-auto">
          <div class="p-5">
            <h4 class="text-sm font-semibold text-gray-900 mb-4">Form Sections</h4>
            <nav class="space-y-1">
              <button
                v-for="(section, index) in formSections"
                :key="section.id"
                @click="activeSection = section.id"
                class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-all"
                :class="[
                  activeSection === section.id
                    ? 'bg-purple-100 border border-purple-300 text-purple-800'
                    : 'hover:bg-gray-100 text-gray-700'
                ]"
              >
                <div
                  class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0"
                  :class="getSectionStatusClass(section.id)"
                >
                  <CheckIcon v-if="getSectionStatus(section.id) === 'complete'" class="h-3 w-3" />
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium truncate">{{ section.label }}</div>
                  <div class="text-xs text-gray-500">{{ section.description }}</div>
                </div>
              </button>
            </nav>

            <!-- Progress Summary -->
            <div class="mt-6 p-4 bg-white rounded-lg border border-gray-200">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Progress</span>
                <span class="text-sm font-bold text-purple-600">{{ formProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-purple-500 h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${formProgress}%` }"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-2">
                {{ completedSections }} of {{ formSections.length }} sections complete
              </p>
            </div>
          </div>
        </div>

        <!-- Main Form Content -->
        <div class="flex-1 overflow-y-auto">
          <div class="p-6 max-w-5xl mx-auto">
            <!-- Section: Basic Information -->
            <div v-show="activeSection === 'basic'" class="space-y-6">
              <SectionHeader
                title="Basic Information"
                description="Essential working paper details and identification"
                icon="file-text"
                step="1"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <!-- Working Paper ID -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Working Paper ID <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="form.working_paper_id"
                      type="text"
                      placeholder="Auto-generated if left blank"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                      :class="errors.working_paper_id ? 'border-red-300' : 'border-gray-300'"
                    />
                    <p v-if="errors.working_paper_id" class="mt-1 text-xs text-red-500">{{ errors.working_paper_id }}</p>
                    <p v-else class="mt-1 text-xs text-gray-500">Format: WP-YYYY-XXX</p>
                  </div>

                  <!-- Status -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Review Status <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="form.review_status"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option v-for="opt in reviewStatusOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                  </div>

                  <!-- Type -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Type <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="form.wp_type"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                      :class="errors.wp_type ? 'border-red-300' : 'border-gray-300'"
                    >
                      <option value="">Select type</option>
                      <option v-for="opt in wpTypeOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                    <p v-if="errors.wp_type" class="mt-1 text-xs text-red-500">{{ errors.wp_type }}</p>
                  </div>
                </div>

                <!-- Title -->
                <div class="mt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Title <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="form.wp_title"
                    type="text"
                    placeholder="Enter working paper title"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                    :class="errors.wp_title ? 'border-red-300' : 'border-gray-300'"
                  />
                  <p v-if="errors.wp_title" class="mt-1 text-xs text-red-500">{{ errors.wp_title }}</p>
                </div>

                <!-- Reference Number -->
                <div class="mt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Reference Number
                  </label>
                  <input
                    v-model="form.wp_reference_no"
                    type="text"
                    placeholder="REF-001"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <!-- References Row -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  <!-- Engagement Reference -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Engagement Reference <span class="text-red-500">*</span>
                    </label>
                    <LinkField
                      v-model="form.engagement_reference"
                      doctype="Audit Engagement"
                      placeholder="Select audit engagement"
                      :required="true"
                      :error="errors.engagement_reference"
                    />
                  </div>

                  <!-- Procedure Reference -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Procedure Reference
                    </label>
                    <LinkField
                      v-model="form.procedure_reference"
                      doctype="Audit Procedure"
                      placeholder="Link to audit procedure"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Content & Work Performed -->
            <div v-show="activeSection === 'content'" class="space-y-6">
              <SectionHeader
                title="Content & Work Performed"
                description="Document the work performed and findings"
                icon="clipboard-list"
                step="2"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Work Performed -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Work Performed <span class="text-red-500">*</span>
                  </label>
                  <textarea
                    v-model="form.work_performed"
                    rows="6"
                    placeholder="Describe the work performed, procedures followed, and methodology used..."
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                    :class="errors.work_performed ? 'border-red-300' : 'border-gray-300'"
                  ></textarea>
                  <p v-if="errors.work_performed" class="mt-1 text-xs text-red-500">{{ errors.work_performed }}</p>
                </div>

                <!-- Objective -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Objective
                  </label>
                  <textarea
                    v-model="form.objective"
                    rows="3"
                    placeholder="What was the objective of this working paper?"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  ></textarea>
                </div>

                <!-- Scope -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Scope
                  </label>
                  <textarea
                    v-model="form.scope"
                    rows="3"
                    placeholder="Define the scope and boundaries of this working paper..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Section: Assignment & Timeline -->
            <div v-show="activeSection === 'assignment'" class="space-y-6">
              <SectionHeader
                title="Assignment & Timeline"
                description="Assign team members and track progress"
                icon="users"
                step="3"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Assignment Row -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- Prepared By -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Prepared By <span class="text-red-500">*</span>
                    </label>
                    <LinkField
                      v-model="form.prepared_by"
                      doctype="User"
                      :filters="{ enabled: 1 }"
                      placeholder="Select preparer"
                      :required="true"
                      :error="errors.prepared_by"
                    />
                  </div>

                  <!-- Reviewed By -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Reviewed By
                    </label>
                    <LinkField
                      v-model="form.reviewed_by"
                      doctype="User"
                      :filters="{ enabled: 1 }"
                      placeholder="Select reviewer"
                    />
                  </div>
                </div>

                <!-- Dates Row -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <!-- Preparation Date -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Preparation Date <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="form.preparation_date"
                      type="date"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      :class="errors.preparation_date ? 'border-red-300' : 'border-gray-300'"
                    />
                    <p v-if="errors.preparation_date" class="mt-1 text-xs text-red-500">{{ errors.preparation_date }}</p>
                  </div>

                  <!-- Review Date -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Review Date
                    </label>
                    <input
                      v-model="form.review_date"
                      type="date"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>

                  <!-- Due Date -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Due Date
                    </label>
                    <input
                      v-model="form.due_date"
                      type="date"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Section: Quality & Documentation -->
            <div v-show="activeSection === 'quality'" class="space-y-6">
              <SectionHeader
                title="Quality Control & Documentation"
                description="Quality assessment and documentation references"
                icon="check-circle"
                step="4"
              />

              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
                <!-- Quality Assessment -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- Quality Score -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Quality Score
                    </label>
                    <select
                      v-model="form.quality_score"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="">Select score</option>
                      <option value="1">1 - Poor</option>
                      <option value="2">2 - Below Average</option>
                      <option value="3">3 - Average</option>
                      <option value="4">4 - Good</option>
                      <option value="5">5 - Excellent</option>
                    </select>
                  </div>

                  <!-- Review Comments -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                      Review Comments
                    </label>
                    <textarea
                      v-model="form.review_comments"
                      rows="3"
                      placeholder="Reviewer feedback and comments..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    ></textarea>
                  </div>
                </div>

                <!-- Documentation References -->
                <div class="border-t border-gray-200 pt-6">
                  <h4 class="text-sm font-semibold text-gray-900 mb-4">Documentation References</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Supporting Documents -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        Supporting Documents
                      </label>
                      <textarea
                        v-model="form.supporting_documents"
                        rows="3"
                        placeholder="List supporting documents, references, and evidence..."
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      ></textarea>
                    </div>

                    <!-- File Attachments -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        File Attachments
                      </label>
                      <FileUploader
                        v-model="form.attachments"
                        :multiple="true"
                        accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                        placeholder="Upload working paper files"
                      />
                    </div>
                  </div>
                </div>

                <!-- Additional Notes -->
                <div class="border-t border-gray-200 pt-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1.5">
                    Additional Notes
                  </label>
                  <textarea
                    v-model="form.notes"
                    rows="3"
                    placeholder="Any additional notes or observations..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex items-center justify-between w-full">
        <!-- Left: Status and Navigation -->
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2">
            <div
              class="w-3 h-3 rounded-full"
              :class="isFormValid ? 'bg-green-500' : 'bg-amber-500'"
            ></div>
            <span class="text-sm font-medium" :class="isFormValid ? 'text-green-700' : 'text-amber-700'">
              {{ isFormValid ? 'Ready to save' : 'Complete required fields' }}
            </span>
          </div>

          <!-- Section Navigation -->
          <div class="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              :disabled="currentSectionIndex === 0"
              @click="goToPreviousSection"
            >
              <ChevronLeftIcon class="h-4 w-4 mr-1" />
              Previous
            </Button>
            <Button
              variant="ghost"
              size="sm"
              :disabled="currentSectionIndex === formSections.length - 1"
              @click="goToNextSection"
            >
              Next
              <ChevronRightIcon class="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>

        <!-- Right: Action Buttons -->
        <div class="flex items-center space-x-3">
          <Button variant="outline" @click="handleCancel" :disabled="isSaving">
            Cancel
          </Button>
          <Button
            v-if="!isEditMode"
            variant="outline"
            theme="gray"
            @click="saveAsDraft"
            :loading="isSavingDraft"
            :disabled="isSaving"
          >
            Save as Draft
          </Button>
          <Button
            variant="solid"
            theme="purple"
            @click="handleSubmit"
            :loading="isSaving"
          >
            <template #prefix>
              <PlusIcon v-if="!isEditMode" class="h-4 w-4" />
              <CheckIcon v-else class="h-4 w-4" />
            </template>
            {{ isEditMode ? 'Update Working Paper' : 'Create Working Paper' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { Button, Dialog } from "frappe-ui"
import {
	CheckCircleIcon,
	CheckIcon,
	ChevronLeftIcon,
	ChevronRightIcon,
	ClipboardListIcon,
	FileTextIcon,
	PlusIcon,
	UsersIcon,
} from "lucide-vue-next"
import { computed, onMounted, reactive, ref, watch } from "vue"

// Import custom components
import FileUploader from "@/components/Common/FileUploader.vue"
import LinkField from "@/components/Common/fields/LinkField.vue"
import SectionHeader from "@/components/workingpaper/WorkingPaperSectionHeader.vue"

// Props
const props = defineProps({
	modelValue: {
		type: Boolean,
		default: false,
	},
	workingPaper: {
		type: Object,
		default: null,
	},
})

// Emits
const emit = defineEmits([
	"update:modelValue",
	"created",
	"updated",
	"cancelled",
])

// Dialog visibility
const isOpen = computed({
	get: () => props.modelValue,
	set: (val) => emit("update:modelValue", val),
})

// Edit mode detection
const isEditMode = computed(() => !!props.workingPaper?.name)

// Form Sections
const formSections = [
	{
		id: "basic",
		label: "Basic Information",
		description: "Core details",
		icon: "file-text",
	},
	{
		id: "content",
		label: "Content & Work",
		description: "Documentation",
		icon: "clipboard-list",
	},
	{
		id: "assignment",
		label: "Assignment",
		description: "Team & timeline",
		icon: "users",
	},
	{
		id: "quality",
		label: "Quality Control",
		description: "Review & docs",
		icon: "check-circle",
	},
]

const activeSection = ref("basic")

// Form State
const form = reactive({
	// Basic Information
	working_paper_id: "",
	wp_title: "",
	wp_reference_no: "",
	wp_type: "",
	engagement_reference: "",
	procedure_reference: "",

	// Content & Work Performed
	work_performed: "",
	objective: "",
	scope: "",

	// Assignment & Timeline
	prepared_by: "",
	reviewed_by: "",
	preparation_date: "",
	review_date: "",
	due_date: "",
	review_status: "Not Reviewed",

	// Quality & Documentation
	quality_score: "",
	review_comments: "",
	supporting_documents: "",
	attachments: [],
	notes: "",
})

const errors = reactive({})
const isSaving = ref(false)
const isSavingDraft = ref(false)

// Options
const reviewStatusOptions = [
	{ label: "Not Reviewed", value: "Not Reviewed" },
	{ label: "Under Review", value: "Under Review" },
	{ label: "Review Complete", value: "Review Complete" },
	{ label: "Revision Required", value: "Revision Required" },
]

const wpTypeOptions = [
	{ label: "Planning Memo", value: "Planning Memo" },
	{ label: "Risk Assessment", value: "Risk Assessment" },
	{ label: "Walkthrough", value: "Walkthrough" },
	{ label: "Test of Controls", value: "Test of Controls" },
	{ label: "Substantive Test", value: "Substantive Test" },
	{ label: "Analytical Review", value: "Analytical Review" },
	{ label: "Data Analytics", value: "Data Analytics" },
	{ label: "Summary", value: "Summary" },
	{ label: "Other", value: "Other" },
]

// Computed Properties
const currentSectionIndex = computed(() =>
	formSections.findIndex((s) => s.id === activeSection.value),
)

const getSectionStatus = (sectionId) => {
	switch (sectionId) {
		case "basic":
			return form.wp_title && form.wp_type && form.engagement_reference
				? "complete"
				: form.wp_title || form.wp_type
					? "partial"
					: "incomplete"
		case "content":
			return form.work_performed ? "complete" : "incomplete"
		case "assignment":
			return form.prepared_by && form.preparation_date
				? "complete"
				: form.prepared_by || form.preparation_date
					? "partial"
					: "incomplete"
		case "quality":
			return "complete" // Optional section
		default:
			return "incomplete"
	}
}

const getSectionStatusClass = (sectionId) => {
	const status = getSectionStatus(sectionId)
	if (status === "complete") return "bg-purple-500 text-white"
	if (status === "partial") return "bg-amber-500 text-white"
	return "bg-gray-300 text-gray-600"
}

const completedSections = computed(
	() =>
		formSections.filter((s) => getSectionStatus(s.id) === "complete").length,
)

const formProgress = computed(() =>
	Math.round((completedSections.value / formSections.length) * 100),
)

const isFormValid = computed(() => {
	return !!(
		form.wp_title &&
		form.wp_type &&
		form.engagement_reference &&
		form.work_performed &&
		form.prepared_by &&
		form.preparation_date
	)
})

// Methods
const goToPreviousSection = () => {
	const idx = currentSectionIndex.value
	if (idx > 0) {
		activeSection.value = formSections[idx - 1].id
	}
}

const goToNextSection = () => {
	const idx = currentSectionIndex.value
	if (idx < formSections.length - 1) {
		activeSection.value = formSections[idx + 1].id
	}
}

const validateForm = () => {
	const errs = {}

	// Required fields validation
	if (!form.wp_title) errs.wp_title = "Working paper title is required"
	if (!form.wp_type) errs.wp_type = "Type is required"
	if (!form.engagement_reference)
		errs.engagement_reference = "Engagement reference is required"
	if (!form.work_performed) errs.work_performed = "Work performed is required"
	if (!form.prepared_by) errs.prepared_by = "Prepared by is required"
	if (!form.preparation_date)
		errs.preparation_date = "Preparation date is required"

	Object.assign(errors, errs)
	return Object.keys(errs).length === 0
}

const prepareFormData = () => {
	return {
		...form,
		// Ensure arrays are properly formatted
		attachments: Array.isArray(form.attachments) ? form.attachments : [],
	}
}

const handleSubmit = async () => {
	if (!validateForm()) {
		// Navigate to the first section with errors
		const firstErrorSection = formSections.find((s) => {
			const status = getSectionStatus(s.id)
			return status !== "complete"
		})
		if (firstErrorSection) {
			activeSection.value = firstErrorSection.id
		}
		return
	}

	try {
		isSaving.value = true
		const formData = prepareFormData()

		if (isEditMode.value) {
			emit("updated", { ...formData, name: props.workingPaper.name })
		} else {
			emit("created", formData)
		}

		isOpen.value = false
	} catch (error) {
		console.error("Error saving working paper:", error)
	} finally {
		isSaving.value = false
	}
}

const saveAsDraft = async () => {
	try {
		isSavingDraft.value = true
		const formData = prepareFormData()
		emit("created", { ...formData, review_status: "Not Reviewed" })
		isOpen.value = false
	} catch (error) {
		console.error("Error saving draft:", error)
	} finally {
		isSavingDraft.value = false
	}
}

const handleCancel = () => {
	emit("cancelled")
	isOpen.value = false
}

const resetForm = () => {
	Object.keys(form).forEach((key) => {
		if (Array.isArray(form[key])) {
			form[key] = []
		} else if (typeof form[key] === "number") {
			form[key] = null
		} else {
			form[key] = ""
		}
	})
	form.review_status = "Not Reviewed"
	Object.keys(errors).forEach((key) => delete errors[key])
	activeSection.value = "basic"
}

const loadWorkingPaperData = (workingPaper) => {
	if (!workingPaper) return

	Object.keys(form).forEach((key) => {
		if (workingPaper[key] !== undefined) {
			form[key] = workingPaper[key]
		}
	})
}

// Watchers
watch(
	() => props.modelValue,
	(newVal) => {
		if (newVal) {
			if (props.workingPaper) {
				loadWorkingPaperData(props.workingPaper)
			} else {
				resetForm()
			}
		}
	},
)

watch(
	() => props.workingPaper,
	(newVal) => {
		if (newVal && props.modelValue) {
			loadWorkingPaperData(newVal)
		}
	},
	{ deep: true },
)
</script>