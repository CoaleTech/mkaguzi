<template>
  <div class="template-marketplace">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Template Marketplace</h1>
        <p class="text-gray-600 mt-1">Discover, share, and import templates from the community</p>
      </div>
      <div class="flex items-center space-x-3">
        <Button @click="syncMarketplace" :loading="syncing" variant="outline">
          <RefreshCw class="w-4 h-4 mr-2" />
          Sync
        </Button>
        <Button @click="showPublishDialog = true" variant="solid">
          <Upload class="w-4 h-4 mr-2" />
          Publish Template
        </Button>
      </div>
    </div>

    <!-- Featured Templates -->
    <div v-if="featuredTemplates.length > 0" class="mb-8">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Featured Templates</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="template in featuredTemplates"
          :key="template.name"
          class="featured-template-card bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
          @click="viewTemplate(template)"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center space-x-2">
              <div class="p-1.5 bg-blue-100 rounded">
                <Star class="w-4 h-4 text-blue-600" />
              </div>
              <span class="text-xs font-medium text-blue-700">FEATURED</span>
            </div>
            <div class="flex items-center text-yellow-500">
              <Star class="w-4 h-4 fill-current" />
              <span class="text-sm ml-1">{{ template.rating || 0 }}</span>
            </div>
          </div>
          <h3 class="font-semibold text-gray-900 mb-1">{{ template.template_name }}</h3>
          <p class="text-sm text-gray-600 mb-2">{{ template.template_type }} • {{ template.category }}</p>
          <p class="text-sm text-gray-500 line-clamp-2">{{ template.description }}</p>
          <div class="flex items-center justify-between mt-3 text-xs text-gray-500">
            <span>by {{ template.author }}</span>
            <span>{{ template.download_count || 0 }} downloads</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <FormControl
          label="Template Type"
          v-model="filters.template_type"
          type="select"
          :options="templateTypeOptions"
          @change="loadTemplates"
        />
        <FormControl
          label="Category"
          v-model="filters.category"
          type="select"
          :options="categoryOptions"
          @change="loadTemplates"
        />
        <FormControl
          label="Search"
          v-model="searchQuery"
          type="text"
          placeholder="Search templates..."
          @input="debouncedSearch"
        />
        <div class="flex items-end">
          <Button @click="clearFilters" variant="outline" class="w-full">
            Clear Filters
          </Button>
        </div>
      </div>
    </div>

    <!-- Templates Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="template in marketplaceTemplates"
        :key="template.name"
        class="marketplace-card bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center space-x-3">
            <div class="p-2 bg-gray-100 rounded-lg">
              <component :is="getTemplateIcon(template.template_type)" class="w-6 h-6 text-gray-600" />
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">{{ template.template_name }}</h3>
              <p class="text-sm text-gray-500">{{ template.template_type }} • v{{ template.version }}</p>
            </div>
          </div>
          <div class="flex items-center text-yellow-500">
            <Star class="w-4 h-4 fill-current" />
            <span class="text-sm ml-1">{{ template.rating || 0 }}</span>
          </div>
        </div>

        <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ template.description }}</p>

        <div class="flex items-center justify-between text-sm text-gray-500 mb-4">
          <span>by {{ template.author }}</span>
          <span>{{ template.download_count || 0 }} downloads</span>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <Button
              @click="viewTemplate(template)"
              variant="ghost"
              size="sm"
            >
              <Eye class="w-4 h-4 mr-1" />
              View
            </Button>
            <Button
              @click="rateTemplate(template, 5)"
              variant="ghost"
              size="sm"
              class="text-yellow-600"
            >
              <Star class="w-4 h-4" />
            </Button>
          </div>
          <Button
            @click="importTemplate(template)"
            :loading="importing === template.name"
            variant="solid"
            size="sm"
          >
            <Download class="w-4 h-4 mr-1" />
            Import
          </Button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && marketplaceTemplates.length === 0" class="text-center py-12">
      <Package class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
      <p class="text-gray-600 mb-6">
        {{ searchQuery || filters.template_type || filters.category ? 'Try adjusting your search or filters' : 'Be the first to publish a template!' }}
      </p>
      <Button @click="showPublishDialog = true" variant="solid">
        <Upload class="w-4 h-4 mr-2" />
        Publish Template
      </Button>
    </div>

    <!-- Publish Template Dialog -->
    <Dialog
      v-model="showPublishDialog"
      :options="{
        title: 'Publish Template to Marketplace',
        size: '3xl'
      }"
    >
      <template #body-content>
        <PublishTemplateForm
          v-if="showPublishDialog"
          @published="onTemplatePublished"
          @cancel="showPublishDialog = false"
        />
      </template>
    </Dialog>

    <!-- Template Detail Dialog -->
    <Dialog
      v-model="showTemplateDetail"
      :options="{
        title: 'Template Details',
        size: '4xl'
      }"
    >
      <template #body-content>
        <TemplateDetail
          v-if="showTemplateDetail"
          :template="selectedTemplate"
          @import="importTemplate($event)"
          @close="showTemplateDetail = false"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { call } from "frappe-ui"
import {
	Download,
	Eye,
	FileText,
	Layout,
	Mail,
	Package,
	RefreshCw,
	Settings,
	Star,
	Upload,
	Wrench,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

import PublishTemplateForm from "./marketplace/PublishTemplateForm.vue"
import TemplateDetail from "./marketplace/TemplateDetail.vue"

// Reactive data
const marketplaceTemplates = ref([])
const featuredTemplates = ref([])
const loading = ref(false)
const syncing = ref(false)
const importing = ref("")
const showPublishDialog = ref(false)
const showTemplateDetail = ref(false)
const selectedTemplate = ref(null)

const filters = ref({
	template_type: "",
	category: "",
})

const searchQuery = ref("")

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

// Methods
const loadTemplates = async () => {
	loading.value = true
	try {
		const response = await call(
			"mkaguzi.mkaguzi.core.doctype.template_marketplace.template_marketplace.get_marketplace_templates",
			{
				filters: filters.value,
				search: searchQuery.value,
				limit: 100,
			},
		)
		marketplaceTemplates.value = response || []
	} catch (error) {
		console.error("Error loading marketplace templates:", error)
		marketplaceTemplates.value = []
	} finally {
		loading.value = false
	}
}

const loadFeaturedTemplates = async () => {
	try {
		const response = await call(
			"mkaguzi.mkaguzi.core.doctype.template_marketplace.template_marketplace.get_featured_templates",
		)
		featuredTemplates.value = response || []
	} catch (error) {
		console.error("Error loading featured templates:", error)
		featuredTemplates.value = []
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

const syncMarketplace = async () => {
	syncing.value = true
	try {
		await call(
			"mkaguzi.mkaguzi.core.doctype.template_marketplace.template_marketplace.sync_from_remote_marketplace",
		)
		await loadTemplates()
		await loadFeaturedTemplates()
	} catch (error) {
		console.error("Error syncing marketplace:", error)
	} finally {
		syncing.value = false
	}
}

const importTemplate = async (template) => {
	importing.value = template.name
	try {
		const importedTemplateName = await call(
			"mkaguzi.mkaguzi.core.doctype.template_marketplace.template_marketplace.import_from_marketplace",
			{
				marketplace_template_name: template.name,
			},
		)

		// Refresh local templates
		// You might want to emit an event to refresh the template manager

		alert(`Template "${template.template_name}" imported successfully!`)
	} catch (error) {
		console.error("Error importing template:", error)
		alert(`Failed to import template: ${error.message}`)
	} finally {
		importing.value = ""
	}
}

const rateTemplate = async (template, rating) => {
	try {
		await call(
			"mkaguzi.mkaguzi.core.doctype.template_marketplace.template_marketplace.rate_template",
			{
				marketplace_template_name: template.name,
				rating: rating,
			},
		)

		// Update local rating
		template.rating = rating
	} catch (error) {
		console.error("Error rating template:", error)
	}
}

const viewTemplate = (template) => {
	selectedTemplate.value = template
	showTemplateDetail.value = true
}

const clearFilters = () => {
	filters.value = {
		template_type: "",
		category: "",
	}
	searchQuery.value = ""
	loadTemplates()
}

const onTemplatePublished = () => {
	showPublishDialog.value = false
	loadTemplates()
	loadFeaturedTemplates()
}

let searchTimeout = null
const debouncedSearch = () => {
	clearTimeout(searchTimeout)
	searchTimeout = setTimeout(loadTemplates, 300)
}

// Lifecycle
onMounted(() => {
	loadTemplates()
	loadFeaturedTemplates()
})
</script>

<style scoped>
.marketplace-card {
  transition: all 0.2s ease;
}

.marketplace-card:hover {
  transform: translateY(-2px);
}

.featured-template-card {
  transition: all 0.2s ease;
}

.featured-template-card:hover {
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