<template>
  <div class="template-manager">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Template Manager</h1>
        <p class="text-gray-600 mt-1">Manage and organize templates for reports, components, and pages</p>
      </div>
      <div class="flex items-center space-x-3">
        <Button @click="refreshTemplates" :loading="loading" variant="outline">
          <RefreshCw class="w-4 h-4 mr-2" />
          Refresh
        </Button>
        <Button @click="createTemplate" variant="solid">
          <Plus class="w-4 h-4 mr-2" />
          New Template
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <FormControl
          label="Template Type"
          v-model="filters.templateType"
          type="select"
          :options="templateTypeOptions"
          @change="applyFilters"
        />
        <FormControl
          label="Category"
          v-model="filters.category"
          type="select"
          :options="categoryOptions"
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
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="template in filteredTemplates"
        :key="template.name"
        class="template-card bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
        @click="editTemplate(template)"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center space-x-3">
            <div class="p-2 bg-blue-50 rounded-lg">
              <component :is="getTemplateIcon(template.template_type)" class="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">{{ template.template_name }}</h3>
              <p class="text-sm text-gray-500">{{ template.template_type }}</p>
            </div>
          </div>
          <div v-if="template.is_default" class="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
            Default
          </div>
        </div>

        <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ template.description }}</p>

        <div class="flex items-center justify-between text-sm text-gray-500">
          <div class="flex items-center space-x-4">
            <span v-if="template.category" class="px-2 py-1 bg-gray-100 rounded text-xs">
              {{ template.category }}
            </span>
            <span v-if="template.usage_count" class="flex items-center">
              <Eye class="w-4 h-4 mr-1" />
              {{ template.usage_count }}
            </span>
          </div>
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
              @click.stop="openTemplatePreview(template)"
              variant="ghost"
              size="sm"
              class="p-1"
            >
              <Eye class="w-4 h-4" />
            </Button>
            <Button
              @click.stop="deleteTemplate(template)"
              variant="ghost"
              size="sm"
              class="p-1 text-red-600 hover:text-red-700"
            >
              <Trash2 class="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredTemplates.length === 0" class="text-center py-12">
      <FileText class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
      <p class="text-gray-600 mb-6">
        {{ filters.templateType || filters.category || filters.search ? 'Try adjusting your filters' : 'Get started by creating your first template' }}
      </p>
      <Button @click="createTemplate" variant="solid">
        <Plus class="w-4 h-4 mr-2" />
        Create Template
      </Button>
    </div>

    <!-- Template Editor Modal -->
    <Dialog
      v-model="showEditor"
      :options="{
        title: isEditing ? 'Edit Template' : 'Create Template',
        size: '4xl'
      }"
    >
      <template #body-content>
        <TemplateEditor
          v-if="showEditor"
          :template="editingTemplate"
          :is-editing="isEditing"
          @save="saveTemplate"
          @cancel="closeEditor"
        />
      </template>
    </Dialog>

    <!-- Template Preview Modal -->
    <Dialog
      v-model="showPreview"
      :options="{
        title: 'Template Preview',
        size: '5xl'
      }"
    >
      <template #body-content>
        <TemplatePreview
          v-if="showPreview"
          :template="previewTemplate"
          @close="closePreview"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { call } from "frappe-ui"
import {
	Copy,
	Eye,
	FileText,
	Layout,
	Mail,
	Plus,
	RefreshCw,
	Settings,
	Trash2,
	Wrench,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"

import TemplateEditor from "./TemplateEditor.vue"
import TemplatePreview from "./TemplatePreview.vue"

// Props
const props = defineProps({
	initialFilters: {
		type: Object,
		default: () => ({}),
	},
})

// Reactive data
const templates = ref([])
const loading = ref(false)
const showEditor = ref(false)
const showPreview = ref(false)
const editingTemplate = ref(null)
const previewTemplate = ref(null)
const isEditing = ref(false)

const filters = ref({
	templateType: props.initialFilters.templateType || "",
	category: props.initialFilters.category || "",
	status: props.initialFilters.status || "",
	search: props.initialFilters.search || "",
})

// Options
const templateTypeOptions = [
	{ label: "All Types", value: "" },
	{ label: "Report", value: "Report" },
	{ label: "Component", value: "Component" },
	{ label: "Page", value: "Page" },
	{ label: "Email", value: "Email" },
	{ label: "Base", value: "Base" },
	{ label: "Utility", value: "Utility" },
]

const categoryOptions = [
	{ label: "All Categories", value: "" },
	{ label: "Audit Report", value: "Audit Report" },
	{ label: "Compliance", value: "Compliance" },
	{ label: "Risk Assessment", value: "Risk Assessment" },
	{ label: "Dashboard", value: "Dashboard" },
	{ label: "Form", value: "Form" },
	{ label: "Email Notification", value: "Email Notification" },
	{ label: "Print Template", value: "Print Template" },
	{ label: "API Response", value: "API Response" },
]

const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Active", value: "active" },
	{ label: "Inactive", value: "inactive" },
	{ label: "Default", value: "default" },
]

// Computed
const filteredTemplates = computed(() => {
	return templates.value.filter((template) => {
		const matchesType =
			!filters.value.templateType ||
			template.template_type === filters.value.templateType
		const matchesCategory =
			!filters.value.category || template.category === filters.value.category
		const matchesStatus =
			!filters.value.status ||
			(filters.value.status === "active" && template.is_active) ||
			(filters.value.status === "inactive" && !template.is_active) ||
			(filters.value.status === "default" && template.is_default)
		const matchesSearch =
			!filters.value.search ||
			template.template_name
				.toLowerCase()
				.includes(filters.value.search.toLowerCase()) ||
			template.description
				?.toLowerCase()
				.includes(filters.value.search.toLowerCase())

		return matchesType && matchesCategory && matchesStatus && matchesSearch
	})
})

// Methods
const loadTemplates = async () => {
	loading.value = true
	try {
		const response = await call(
			"mkaguzi.core.doctype.template_registry.template_registry.get_templates_by_category",
		)
		templates.value = response || []
	} catch (error) {
		console.error("Error loading templates:", error)
		templates.value = []
	} finally {
		loading.value = false
	}
}

const getTemplateIcon = (type) => {
	const icons = {
		Report: FileText,
		Component: Settings,
		Page: Layout,
		Email: Mail,
		Base: Layout,
		Utility: Wrench,
	}
	return icons[type] || FileText
}

const createTemplate = () => {
	editingTemplate.value = {
		template_name: "",
		template_type: "Report",
		category: "",
		description: "",
		template_content: "",
		template_config: "{}",
		template_engine: "Jinja2",
		is_active: true,
		is_default: false,
	}
	isEditing.value = false
	showEditor.value = true
}

const editTemplate = (template) => {
	editingTemplate.value = { ...template }
	isEditing.value = true
	showEditor.value = true
}

const duplicateTemplate = async (template) => {
	const duplicatedTemplate = {
		...template,
		name: null,
		template_id: null,
		template_name: `${template.template_name} (Copy)`,
		is_default: false,
		usage_count: 0,
		last_used: null,
	}

	editingTemplate.value = duplicatedTemplate
	isEditing.value = false
	showEditor.value = true
}

const openTemplatePreview = (template) => {
	previewTemplate.value = template
	showPreview.value = true
}

const deleteTemplate = async (template) => {
	if (confirm(`Are you sure you want to delete "${template.template_name}"?`)) {
		try {
			await call("frappe.client.delete", {
				doctype: "Template Registry",
				name: template.name,
			})

			await loadTemplates()
		} catch (error) {
			console.error("Error deleting template:", error)
		}
	}
}

const saveTemplate = async (templateData) => {
	try {
		if (isEditing.value) {
			await call("frappe.client.update", {
				doc: templateData,
				doctype: "Template Registry",
			})
		} else {
			await call("frappe.client.insert", {
				doc: templateData,
				doctype: "Template Registry",
			})
		}

		await loadTemplates()
		closeEditor()
	} catch (error) {
		console.error("Error saving template:", error)
		throw error
	}
}

const closeEditor = () => {
	showEditor.value = false
	editingTemplate.value = null
	isEditing.value = false
}

const closePreview = () => {
	showPreview.value = false
	previewTemplate.value = null
}

const refreshTemplates = () => {
	loadTemplates()
}

const applyFilters = () => {
	// Filters are reactive, no need to do anything
}

let searchTimeout = null
const debouncedSearch = () => {
	clearTimeout(searchTimeout)
	searchTimeout = setTimeout(applyFilters, 300)
}

// Lifecycle
onMounted(() => {
	loadTemplates()
})
</script>

<style scoped>
.template-card {
  transition: all 0.2s ease;
}

.template-card:hover {
  transform: translateY(-2px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  overflow: hidden;
}
</style>