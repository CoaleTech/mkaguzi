<template>
  <div class="finding-template-selector">
    <div class="space-y-4">
      <!-- Template Search -->
      <div class="flex items-center space-x-2">
        <div class="flex-1">
          <FormControl
            v-model="searchQuery"
            placeholder="Search templates by name, category, or risk area..."
            class="w-full"
          >
            <template #prefix>
              <Search class="w-4 h-4 text-gray-400" />
            </template>
          </FormControl>
        </div>
        <FormControl
          v-model="selectedCategory"
          type="select"
          :options="categoryFilterOptions"
          class="w-48"
          placeholder="All Categories"
        />
      </div>

      <!-- Template Suggestions -->
      <div v-if="filteredTemplates.length > 0" class="space-y-2">
        <h4 class="text-sm font-medium text-gray-700">Suggested Templates</h4>
        <div class="max-h-64 overflow-y-auto space-y-2">
          <div
            v-for="template in filteredTemplates"
            :key="template.name"
            class="template-option p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
            @click="selectTemplate(template)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-2 mb-1">
                  <h5 class="text-sm font-medium text-gray-900 truncate">{{ template.template_name }}</h5>
                  <Badge :theme="getCategoryTheme(template.finding_category)" size="sm">
                    {{ template.finding_category }}
                  </Badge>
                </div>
                <p class="text-xs text-gray-600 truncate">{{ template.template_title }}</p>
                <div class="flex items-center space-x-3 mt-2 text-xs text-gray-500">
                  <span>Risk: {{ template.typical_risk_rating || 'N/A' }}</span>
                  <span>Used: {{ template.usage_count || 0 }} times</span>
                </div>
              </div>
              <div class="flex items-center space-x-1 ml-2">
                <Button
                  @click.stop="previewTemplate(template)"
                  variant="ghost"
                  size="sm"
                  class="p-1"
                >
                  <Eye class="w-3 h-3" />
                </Button>
                <Button
                  @click.stop="applyTemplate(template)"
                  variant="ghost"
                  size="sm"
                  class="p-1 text-blue-600"
                >
                  <Check class="w-3 h-3" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Templates Found -->
      <div v-else-if="searchQuery || selectedCategory" class="text-center py-8">
        <FileText class="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <h4 class="text-sm font-medium text-gray-900 mb-1">No templates found</h4>
        <p class="text-xs text-gray-500">Try adjusting your search criteria</p>
      </div>

      <!-- Loading State -->
      <div v-else-if="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
        <p class="text-xs text-gray-500">Loading templates...</p>
      </div>

      <!-- Create Custom Option -->
      <div class="border-t border-gray-200 pt-4">
        <Button @click="createCustomFinding" variant="outline" class="w-full">
          <Plus class="w-4 h-4 mr-2" />
          Create Custom Finding
        </Button>
      </div>
    </div>

    <!-- Template Preview Modal -->
    <Dialog
      v-model="showPreview"
      :options="{
        size: '3xl',
        title: 'Template Preview',
      }"
    >
      <template #body>
        <FindingTemplatePreview
          :template="selectedTemplateForPreview"
          @close="showPreview = false"
          @use-template="handleUseTemplate"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { useAuditStore } from "@/stores/audit"
import { createResource } from "frappe-ui"
import { Check, Eye, FileText, Plus, Search } from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"
import FindingTemplatePreview from "./FindingTemplatePreview.vue"

export default {
	name: "FindingTemplateSelector",
	components: {
		FindingTemplatePreview,
	},
	emits: ["template-selected", "create-custom"],
	setup(props, { emit }) {
		const auditStore = useAuditStore()

		// State
		const searchQuery = ref("")
		const selectedCategory = ref("")
		const loading = ref(false)
		const showPreview = ref(false)
		const selectedTemplateForPreview = ref(null)

		// Options
		const categoryFilterOptions = [
			{ label: "All Categories", value: "" },
			{ label: "Financial Reporting", value: "Financial Reporting" },
			{ label: "Internal Controls", value: "Internal Controls" },
			{ label: "Compliance", value: "Compliance" },
			{ label: "Operational", value: "Operational" },
			{ label: "IT Security", value: "IT Security" },
			{ label: "Procurement", value: "Procurement" },
			{ label: "HR Management", value: "HR Management" },
		]

		// Computed
		const filteredTemplates = computed(() => {
			let templates = auditStore.findingTemplates

			if (selectedCategory.value) {
				templates = templates.filter(
					(t) => t.finding_category === selectedCategory.value,
				)
			}

			if (searchQuery.value) {
				const query = searchQuery.value.toLowerCase()
				templates = templates.filter(
					(t) =>
						t.template_name?.toLowerCase().includes(query) ||
						t.template_title?.toLowerCase().includes(query) ||
						t.finding_category?.toLowerCase().includes(query) ||
						t.risk_area?.toLowerCase().includes(query),
				)
			}

			// Sort by usage count (most used first)
			return templates.sort(
				(a, b) => (b.usage_count || 0) - (a.usage_count || 0),
			)
		})

		// Methods
		const loadTemplates = async () => {
			loading.value = true
			try {
				await auditStore.fetchFindingTemplates()
			} catch (error) {
				console.error("Error loading templates:", error)
			} finally {
				loading.value = false
			}
		}

		const selectTemplate = (template) => {
			emit("template-selected", template)
		}

		const previewTemplate = (template) => {
			selectedTemplateForPreview.value = template
			showPreview.value = true
		}

		const applyTemplate = async (template) => {
			try {
				// Increment usage count
				await createResource({
					url: "frappe.client.set_value",
					params: {
						doctype: "Finding Template",
						name: template.name,
						fieldname: "usage_count",
						value: (template.usage_count || 0) + 1,
					},
				}).fetch()

				emit("template-selected", template)
			} catch (error) {
				console.error("Error applying template:", error)
				// Still emit the template even if usage count update fails
				emit("template-selected", template)
			}
		}

		const createCustomFinding = () => {
			emit("create-custom")
		}

		const handleUseTemplate = (template) => {
			showPreview.value = false
			selectTemplate(template)
		}

		const getCategoryTheme = (category) => {
			const themes = {
				"Financial Reporting": "blue",
				"Internal Controls": "purple",
				Compliance: "green",
				Operational: "orange",
				"IT Security": "red",
				Procurement: "yellow",
				"HR Management": "indigo",
			}
			return themes[category] || "gray"
		}

		// Watch for category changes to refresh suggestions
		watch(selectedCategory, () => {
			if (selectedCategory.value) {
				loadTemplateSuggestions()
			}
		})

		const loadTemplateSuggestions = async () => {
			if (!selectedCategory.value) return

			try {
				const suggestions = await auditStore.getTemplateSuggestions(
					selectedCategory.value,
				)
				// The suggestions are already loaded in the store
			} catch (error) {
				console.error("Error loading template suggestions:", error)
			}
		}

		// Lifecycle
		onMounted(() => {
			loadTemplates()
		})

		return {
			// State
			searchQuery,
			selectedCategory,
			loading,
			showPreview,
			selectedTemplateForPreview,

			// Options
			categoryFilterOptions,

			// Computed
			filteredTemplates,

			// Methods
			selectTemplate,
			previewTemplate,
			applyTemplate,
			createCustomFinding,
			handleUseTemplate,
			getCategoryTheme,

			// Icons
			Search,
			Eye,
			Check,
			Plus,
			FileText,
		}
	},
}
</script>

<style scoped>
.template-option:hover {
  background-color: #f9fafb;
}
</style>