<template>
  <div class="finding-template-form">
    <div class="space-y-8">
      <!-- Section 1: Basic Information -->
      <div class="space-y-6">
        <SectionHeader
          title="Basic Information"
          description="Define the template name, category, and basic properties"
          :sectionNumber="1"
          color="blue"
        />

        <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormControl
              v-model="formData.template_name"
              label="Template Name"
              placeholder="e.g., Revenue Recognition Error"
              :required="true"
            />

            <FormControl
              v-model="formData.finding_category"
              label="Finding Category"
              type="select"
              :options="categoryOptions"
              :required="true"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <FormControl
              v-model="formData.risk_category"
              label="Risk Category"
              type="select"
              :options="riskCategoryOptions"
              :required="true"
            />

            <FormControl
              v-model="formData.is_active"
              label="Status"
              type="select"
              :options="statusOptions"
            />
          </div>

          <div class="mt-6">
            <FormControl
              v-model="formData.description"
              label="Description"
              placeholder="Brief description of this finding template"
              :required="true"
            />
          </div>

          <div class="mt-6">
            <div class="flex items-center space-x-2">
              <input
                id="is_active"
                v-model="formData.is_active"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="is_active" class="text-sm font-medium text-gray-700">
                Active Template
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 2: Template Content -->
      <div class="space-y-6">
        <SectionHeader
          title="Template Content"
          description="Define the standard content that will be pre-filled when using this template"
          :sectionNumber="2"
          color="purple"
        />

        <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <div class="space-y-6">
            <!-- Condition Template -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Condition Template <span class="text-red-500">*</span>
              </label>
              <p class="text-xs text-gray-500 mb-2">Standard description of what is typically observed</p>
              <TextEditor
                :content="formData.condition_template"
                @change="formData.condition_template = $event"
                placeholder="Describe the typical condition or situation found during audits..."
                :editable="true"
                editorClass="min-h-[120px] prose-sm"
              />
            </div>

            <!-- Criteria Template -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Criteria Template <span class="text-red-500">*</span>
              </label>
              <p class="text-xs text-gray-500 mb-2">Standard expectations or requirements</p>
              <TextEditor
                :content="formData.criteria_template"
                @change="formData.criteria_template = $event"
                placeholder="Describe the standard, policy, or expectation that should be met..."
                :editable="true"
                editorClass="min-h-[120px] prose-sm"
              />
            </div>

            <!-- Cause Template -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Cause Template
              </label>
              <p class="text-xs text-gray-500 mb-2">Common reasons why this finding occurs</p>
              <TextEditor
                :content="formData.cause_template"
                @change="formData.cause_template = $event"
                placeholder="Describe typical causes or reasons for this type of finding..."
                :editable="true"
                editorClass="min-h-[100px] prose-sm"
              />
            </div>

            <!-- Effect Template -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Effect Template
              </label>
              <p class="text-xs text-gray-500 mb-2">Impact or consequences of this finding</p>
              <TextEditor
                :content="formData.effect_template"
                @change="formData.effect_template = $event"
                placeholder="Describe the potential impact or consequences..."
                :editable="true"
                editorClass="min-h-[100px] prose-sm"
              />
            </div>

            <!-- Recommendation Template -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Recommendation Template <span class="text-red-500">*</span>
              </label>
              <p class="text-xs text-gray-500 mb-2">Suggested corrective actions</p>
              <TextEditor
                :content="formData.recommendation_template"
                @change="formData.recommendation_template = $event"
                placeholder="Provide standard recommendations for addressing this finding..."
                :editable="true"
                editorClass="min-h-[120px] prose-sm"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Section 3: Default Values -->
      <div class="space-y-6">
        <SectionHeader
          title="Default Values"
          description="Set default values that will be pre-filled when using this template"
          :sectionNumber="3"
          color="green"
        />

        <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormControl
              v-model="formData.default_priority"
              label="Default Priority Level"
              type="select"
              :options="priorityOptions"
            />

            <FormControl
              v-model="formData.default_business_unit"
              label="Default Business Unit"
              placeholder="e.g., Finance, Operations, IT"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <FormControl
              v-model="formData.default_responsible_person"
              label="Default Responsible Person"
              placeholder="Name or role"
            />

            <FormControl
              v-model="formData.default_target_days"
              label="Default Target Days"
              type="number"
              placeholder="e.g., 30"
              min="1"
            />
          </div>

          <div class="mt-6">
            <div class="flex items-center space-x-2">
              <input
                id="repeat_finding_default"
                v-model="formData.repeat_finding_default"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="repeat_finding_default" class="text-sm font-medium text-gray-700">
                Mark as Repeat Finding by Default
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 4: Usage Tracking -->
      <div class="space-y-6">
        <SectionHeader
          title="Usage Tracking"
          description="Track how often this template is used and its effectiveness"
          :sectionNumber="4"
          color="orange"
        />

        <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="text-center p-4 bg-gray-50 rounded-lg">
              <div class="text-2xl font-bold text-gray-900">{{ formData.usage_count || 0 }}</div>
              <div class="text-sm text-gray-600">Times Used</div>
            </div>

            <div class="text-center p-4 bg-blue-50 rounded-lg">
              <div class="text-2xl font-bold text-blue-900">{{ effectivenessRate }}%</div>
              <div class="text-sm text-blue-600">Effectiveness Rate</div>
            </div>

            <div class="text-center p-4 bg-green-50 rounded-lg">
              <div class="text-2xl font-bold text-green-900">{{ avgResolutionDays || 'N/A' }}</div>
              <div class="text-sm text-green-600">Avg Resolution (Days)</div>
            </div>
          </div>

          <div class="mt-6">
            <FormControl
              v-model="formData.tags"
              label="Tags"
              placeholder="Comma-separated tags for better organization"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Form Actions -->
    <div class="flex items-center justify-end space-x-3 mt-8 pt-6 border-t border-gray-200">
      <Button @click="$emit('cancel')" variant="outline">
        Cancel
      </Button>
      <Button @click="saveTemplate" :loading="saving" variant="solid">
        {{ isEditing ? 'Update Template' : 'Create Template' }}
      </Button>
    </div>
  </div>
</template>

<script>
import SectionHeader from "@/components/Common/SectionHeader.vue"
import TextEditor from "@/components/Common/TextEditor.vue"
import { createResource } from "frappe-ui"
import { computed, ref, watch } from "vue"

export default {
	name: "FindingTemplateForm",
	components: {
		SectionHeader,
		TextEditor,
	},
	props: {
		template: {
			type: Object,
			default: null,
		},
		isEditing: {
			type: Boolean,
			default: false,
		},
	},
	emits: ["save", "cancel"],
	setup(props, { emit }) {
		const saving = ref(false)

		// Form data
		const formData = ref({
			template_name: "",
			finding_category: "",
			risk_category: "",
			is_active: true,
			description: "",
			condition_template: "",
			criteria_template: "",
			cause_template: "",
			effect_template: "",
			recommendation_template: "",
			evidence_types: "",
			action_plan_template: "",
			responsible_roles: "",
			estimated_effort_days: "",
			resources_template: "",
			verification_methods: "",
			tags: "",
			usage_count: 0,
		})

		// Options
		const categoryOptions = [
			{ label: "Select Category", value: "" },
			{ label: "Control Deficiency", value: "Control Deficiency" },
			{ label: "Non-Compliance", value: "Non-Compliance" },
			{ label: "Inefficiency", value: "Inefficiency" },
			{ label: "Error", value: "Error" },
			{ label: "Fraud Indicator", value: "Fraud Indicator" },
			{ label: "Best Practice Opportunity", value: "Best Practice Opportunity" },
		]

		const riskCategoryOptions = [
			{ label: "Select Risk Category", value: "" },
			{ label: "Financial", value: "Financial" },
			{ label: "Operational", value: "Operational" },
			{ label: "Compliance", value: "Compliance" },
			{ label: "IT", value: "IT" },
			{ label: "Reputational", value: "Reputational" },
			{ label: "Strategic", value: "Strategic" },
		]

		const statusOptions = [
			{ label: "Active", value: true },
			{ label: "Inactive", value: false },
		]

		const riskRatingOptions = [
			{ label: "Select Risk Rating", value: "" },
			{ label: "Low", value: "Low" },
			{ label: "Medium", value: "Medium" },
			{ label: "High", value: "High" },
			{ label: "Critical", value: "Critical" },
		]

		const priorityOptions = [
			{ label: "Select Priority", value: "" },
			{ label: "Low", value: "Low" },
			{ label: "Medium", value: "Medium" },
			{ label: "High", value: "High" },
			{ label: "Critical", value: "Critical" },
		]

		// Computed
		const effectivenessRate = computed(() => {
			// This would be calculated based on actual usage data
			// For now, return a placeholder
			return "85"
		})

		const avgResolutionDays = computed(() => {
			// This would be calculated based on actual resolution data
			// For now, return a placeholder
			return "45"
		})

		// Watch for prop changes
		watch(
			() => props.template,
			(newTemplate) => {
				if (newTemplate) {
					formData.value = { ...newTemplate }
				}
			},
			{ immediate: true },
		)

		// Methods
		const saveTemplate = async () => {
			if (!validateForm()) return

			saving.value = true
			try {
				const templateData = {
					doctype: "Finding Template",
					...formData.value,
				}

				if (props.isEditing) {
					await createResource({
						url: "frappe.client.set_value",
						params: {
							doctype: "Finding Template",
							name: props.template.name,
							fieldname: formData.value,
						},
					}).fetch()
				} else {
					await createResource({
						url: "frappe.client.insert",
						params: {
							doc: templateData,
						},
					}).fetch()
				}

				emit("save")
			} catch (error) {
				console.error("Error saving template:", error)
				// Handle error (show toast, etc.)
			} finally {
				saving.value = false
			}
		}

		const validateForm = () => {
			const required = [
				"template_id",
				"template_name",
				"finding_category",
				"risk_area",
				"template_title",
				"condition_template",
				"criteria_template",
				"recommendation_template",
			]

			for (const field of required) {
				if (!formData.value[field]) {
					// Show validation error
					return false
				}
			}

			return true
		}

		return {
			saving,
			formData,
			categoryOptions,
			riskCategoryOptions,
			statusOptions,
			effectivenessRate,
			avgResolutionDays,
			saveTemplate,
		}
	},
}
</script>