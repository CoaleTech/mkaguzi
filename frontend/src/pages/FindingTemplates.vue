<template>
  <div class="finding-templates-page">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Finding Templates</h1>
        <p class="text-gray-600 mt-1">Create and manage reusable templates for common audit findings</p>
      </div>
      <div class="flex items-center space-x-3">
        <Button @click="refreshTemplates" :loading="loading" variant="outline">
          <RefreshCw class="w-4 h-4 mr-2" />
          Refresh
        </Button>
        <Button @click="createNewTemplate" variant="solid">
          <Plus class="w-4 h-4 mr-2" />
          New Template
        </Button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-50 rounded-lg">
            <FileText class="w-6 h-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Templates</p>
            <p class="text-2xl font-bold text-gray-900">{{ templates.length }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-50 rounded-lg">
            <CheckCircle class="w-6 h-6 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Active Templates</p>
            <p class="text-2xl font-bold text-gray-900">{{ activeTemplatesCount }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-50 rounded-lg">
            <TrendingUp class="w-6 h-6 text-yellow-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Most Used</p>
            <p class="text-2xl font-bold text-gray-900">{{ mostUsedTemplate?.template_name || 'N/A' }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-purple-50 rounded-lg">
            <Tag class="w-6 h-6 text-purple-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Categories</p>
            <p class="text-2xl font-bold text-gray-900">{{ uniqueCategories.length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <FormControl
          label="Finding Category"
          v-model="filters.category"
          type="select"
          :options="categoryOptions"
          @change="applyFilters"
        />
        <FormControl
          label="Risk Area"
          v-model="filters.riskArea"
          type="select"
          :options="riskAreaOptions"
          @change="applyFilters"
        />
        <FormControl
          label="Status"
          v-model="filters.status"
          type="select"
          :options="statusOptions"
          @change="applyFilters"
        />
        <FormControl
          label="Search"
          v-model="filters.search"
          type="text"
          placeholder="Search templates..."
          @input="debouncedSearch"
        />
      </div>
    </div>

    <!-- Templates Grid -->
    <div v-if="filteredTemplates.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="template in filteredTemplates"
        :key="template.name"
        class="template-card bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-all cursor-pointer"
        @click="editTemplate(template)"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center space-x-3">
            <div class="p-2 bg-blue-50 rounded-lg">
              <FileText class="w-6 h-6 text-blue-600" />
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-900 truncate">{{ template.template_name }}</h3>
              <p class="text-sm text-gray-500">{{ template.finding_category }}</p>
            </div>
          </div>
          <div v-if="!template.is_active" class="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded">
            Inactive
          </div>
          <div v-else class="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
            Active
          </div>
        </div>

        <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ template.description }}</p>

        <div class="flex items-center justify-between text-sm text-gray-500 mb-4">
          <div class="flex items-center space-x-4">
            <span v-if="template.risk_category" class="px-2 py-1 bg-gray-100 rounded text-xs">
              {{ template.risk_category }}
            </span>
            <span v-if="template.usage_count" class="flex items-center">
              <Eye class="w-4 h-4 mr-1" />
              Used {{ template.usage_count }} times
            </span>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <Button
              @click.stop="duplicateTemplate(template)"
              variant="ghost"
              size="sm"
              class="p-1"
            >
              <Copy class="w-4 h-4" />
            </Button>
            <Button
              @click.stop="previewTemplate(template)"
              variant="ghost"
              size="sm"
              class="p-1"
            >
              <Eye class="w-4 h-4" />
            </Button>
            <Button
              @click.stop="toggleTemplateStatus(template)"
              variant="ghost"
              size="sm"
              class="p-1"
              :class="template.is_active ? 'text-red-600' : 'text-green-600'"
            >
              <component :is="template.is_active ? DeactivateIcon : ActivateIcon" class="w-4 h-4" />
            </Button>
          </div>
          <div class="text-xs text-gray-400">
            {{ formatDate(template.modified) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading" class="text-center py-12">
      <FileText class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No finding templates found</h3>
      <p class="text-gray-500 mb-6">Get started by creating your first finding template to streamline audit processes.</p>
      <Button @click="createNewTemplate" variant="solid">
        <Plus class="w-4 h-4 mr-2" />
        Create First Template
      </Button>
    </div>

    <!-- Loading State -->
    <div v-else class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p class="text-gray-500">Loading templates...</p>
    </div>

    <!-- Template Form Dialog -->
    <Dialog
      v-model="showTemplateForm"
      :options="{
        size: '4xl',
        title: isEditing ? 'Edit Finding Template' : 'Create Finding Template',
      }"
    >
      <template #body>
        <FindingTemplateForm
          :template="selectedTemplate"
          :is-editing="isEditing"
          @save="handleTemplateSave"
          @cancel="showTemplateForm = false"
        />
      </template>
    </Dialog>

    <!-- Template Preview Dialog -->
    <Dialog
      v-model="showPreview"
      :options="{
        size: '3xl',
        title: 'Template Preview',
      }"
    >
      <template #body>
        <FindingTemplatePreview
          :template="selectedTemplate"
          @close="showPreview = false"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import FindingTemplateForm from "@/components/findings/FindingTemplateForm.vue"
import FindingTemplatePreview from "@/components/findings/FindingTemplatePreview.vue"
import { useAuditStore } from "@/stores/audit"
import { createResource } from "frappe-ui"
import {
	CheckCircle,
	Copy,
	Eye,
	FileText,
	Plus,
	Power,
	PowerOff,
	RefreshCw,
	Tag,
	TrendingUp,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

export default {
	name: "FindingTemplates",
	components: {
		FindingTemplateForm,
		FindingTemplatePreview,
	},
	setup() {
		const auditStore = useAuditStore()

		// State
		const loading = ref(false)
		const templates = ref([])
		const showTemplateForm = ref(false)
		const showPreview = ref(false)
		const selectedTemplate = ref(null)
		const isEditing = ref(false)

		// Filters
		const filters = ref({
			category: "",
			riskArea: "",
			status: "",
			search: "",
		})

		// Options
		const categoryOptions = [
			{ label: "All Categories", value: "" },
			{ label: "Financial Reporting", value: "Financial Reporting" },
			{ label: "Internal Controls", value: "Internal Controls" },
			{ label: "Compliance", value: "Compliance" },
			{ label: "Operational", value: "Operational" },
			{ label: "IT Security", value: "IT Security" },
			{ label: "Procurement", value: "Procurement" },
			{ label: "HR Management", value: "HR Management" },
		]

		const riskAreaOptions = [
			{ label: "All Risk Categories", value: "" },
			{ label: "High", value: "High" },
			{ label: "Medium", value: "Medium" },
			{ label: "Low", value: "Low" },
		]

		const statusOptions = [
			{ label: "All Status", value: "" },
			{ label: "Active", value: "active" },
			{ label: "Inactive", value: "inactive" },
		]

		// Computed
		const activeTemplatesCount = computed(() => {
			return templates.value.filter((t) => t.is_active).length
		})

		const mostUsedTemplate = computed(() => {
			if (templates.value.length === 0) return null
			return templates.value.reduce((prev, current) =>
				(prev.usage_count || 0) > (current.usage_count || 0) ? prev : current,
			)
		})

		const uniqueCategories = computed(() => {
			const categories = templates.value
				.map((t) => t.finding_category)
				.filter(Boolean)
			return [...new Set(categories)]
		})

		const filteredTemplates = computed(() => {
			let filtered = templates.value

			if (filters.value.category) {
				filtered = filtered.filter(
					(t) => t.finding_category === filters.value.category,
				)
			}

			if (filters.value.riskArea) {
				filtered = filtered.filter(
					(t) => t.risk_category === filters.value.riskArea,
				)
			}

			if (filters.value.status) {
				const isActive = filters.value.status === "active"
				filtered = filtered.filter((t) => t.is_active === isActive)
			}

			if (filters.value.search) {
				const search = filters.value.search.toLowerCase()
				filtered = filtered.filter(
					(t) =>
						t.template_name?.toLowerCase().includes(search) ||
						t.description?.toLowerCase().includes(search) ||
						t.finding_category?.toLowerCase().includes(search) ||
						t.risk_category?.toLowerCase().includes(search),
				)
			}

			return filtered
		})

		// Methods
		const refreshTemplates = async () => {
			loading.value = true
			try {
				await auditStore.fetchFindingTemplates()
				templates.value = auditStore.findingTemplates
			} catch (error) {
				console.error("Error refreshing templates:", error)
			} finally {
				loading.value = false
			}
		}

		const createNewTemplate = () => {
			selectedTemplate.value = null
			isEditing.value = false
			showTemplateForm.value = true
		}

		const editTemplate = (template) => {
			selectedTemplate.value = { ...template }
			isEditing.value = true
			showTemplateForm.value = true
		}

		const duplicateTemplate = async (template) => {
			try {
				const duplicatedTemplate = {
					...template,
					template_name: `${template.template_name} (Copy)`,
					name: undefined, // Let the backend generate new name
				}
				await createResource({
					url: "frappe.client.insert",
					params: {
						doc: {
							doctype: "Finding Template",
							...duplicatedTemplate,
						},
					},
				}).fetch()
				await refreshTemplates()
			} catch (error) {
				console.error("Error duplicating template:", error)
			}
		}

		const previewTemplate = (template) => {
			selectedTemplate.value = template
			showPreview.value = true
		}

		const toggleTemplateStatus = async (template) => {
			try {
				await createResource({
					url: "frappe.client.set_value",
					params: {
						doctype: "Finding Template",
						name: template.name,
						fieldname: "is_active",
						value: !template.is_active,
					},
				}).fetch()
				await refreshTemplates()
			} catch (error) {
				console.error("Error toggling template status:", error)
			}
		}

		const handleTemplateSave = async () => {
			showTemplateForm.value = false
			await refreshTemplates()
		}

		const applyFilters = () => {
			// Filters are reactive, no need to do anything
		}

		const debouncedSearch = (() => {
			let timeout
			return () => {
				clearTimeout(timeout)
				timeout = setTimeout(applyFilters, 300)
			}
		})()

		const formatDate = (dateString) => {
			if (!dateString) return ""
			return new Date(dateString).toLocaleDateString()
		}

		// Lifecycle
		onMounted(() => {
			refreshTemplates()
		})

		return {
			// State
			loading,
			templates,
			showTemplateForm,
			showPreview,
			selectedTemplate,
			isEditing,
			filters,

			// Options
			categoryOptions,
			riskAreaOptions,
			statusOptions,

			// Computed
			activeTemplatesCount,
			mostUsedTemplate,
			uniqueCategories,
			filteredTemplates,

			// Methods
			refreshTemplates,
			createNewTemplate,
			editTemplate,
			duplicateTemplate,
			previewTemplate,
			toggleTemplateStatus,
			handleTemplateSave,
			applyFilters,
			debouncedSearch,
			formatDate,

			// Icons
			Plus,
			RefreshCw,
			FileText,
			CheckCircle,
			TrendingUp,
			Tag,
			Eye,
			Copy,
			DeactivateIcon: PowerOff,
			ActivateIcon: Power,
		}
	},
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-card:hover {
  transform: translateY(-2px);
}
</style>