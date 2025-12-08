<template>
  <div class="report-template-builder">
    <div class="space-y-6">
      <!-- Header -->
      <div class="border-b border-gray-200 pb-4">
        <h2 class="text-xl font-bold text-gray-900">
          {{ isEditing ? 'Edit Template' : 'Create New Template' }}
        </h2>
        <p class="text-sm text-gray-600 mt-1">
          Design a professional report template with custom branding and content sections
        </p>
      </div>

      <!-- Basic Information -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Template Name</label>
          <input
            v-model="templateForm.name"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Enter template name"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
          <select
            v-model="templateForm.category"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="audit">Audit Reports</option>
            <option value="compliance">Compliance</option>
            <option value="risk">Risk Analysis</option>
            <option value="financial">Financial</option>
            <option value="operational">Operational</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
        <textarea
          v-model="templateForm.description"
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          placeholder="Describe the purpose and content of this template"
        ></textarea>
      </div>

      <!-- Branding Section -->
      <div class="border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Branding & Styling</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Primary Color</label>
            <div class="flex items-center gap-2">
              <input
                v-model="templateForm.branding.primary_color"
                type="color"
                class="w-12 h-8 border border-gray-300 rounded cursor-pointer"
              />
              <input
                v-model="templateForm.branding.primary_color"
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="#7C3AED"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Font Family</label>
            <select
              v-model="templateForm.branding.font_family"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="Inter">Inter</option>
              <option value="Roboto">Roboto</option>
              <option value="Open Sans">Open Sans</option>
              <option value="Lato">Lato</option>
              <option value="Poppins">Poppins</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Header Style</label>
            <select
              v-model="templateForm.branding.header_style"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="centered">Centered</option>
              <option value="left-aligned">Left Aligned</option>
              <option value="right-aligned">Right Aligned</option>
            </select>
          </div>
        </div>

        <!-- Logo Upload -->
        <div class="mt-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">Company Logo</label>
          <div class="flex items-center gap-4">
            <div class="h-16 w-32 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
              <div v-if="!templateForm.branding.logo_url" class="text-center">
                <UploadIcon class="h-6 w-6 text-gray-400 mx-auto mb-1" />
                <span class="text-xs text-gray-500">Upload Logo</span>
              </div>
              <img
                v-else
                :src="templateForm.branding.logo_url"
                alt="Logo"
                class="h-full w-full object-contain"
              />
            </div>
            <div class="flex-1">
              <input
                type="file"
                ref="logoInput"
                @change="handleLogoUpload"
                accept="image/*"
                class="hidden"
              />
              <Button @click="$refs.logoInput.click()" variant="outline" size="sm">
                <UploadIcon class="h-4 w-4 mr-2" />
                Choose File
              </Button>
              <p class="text-xs text-gray-500 mt-1">PNG, JPG up to 2MB</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Content Sections -->
      <div class="border border-gray-200 rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Content Sections</h3>
          <Button @click="addSection" variant="outline" size="sm">
            <PlusIcon class="h-4 w-4 mr-2" />
            Add Section
          </Button>
        </div>

        <div class="space-y-4">
          <div
            v-for="(section, index) in templateForm.sections"
            :key="section.id"
            class="border border-gray-200 rounded-lg p-4"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <GripVerticalIcon class="h-4 w-4 text-gray-400 cursor-move" />
                <span class="text-sm font-medium text-gray-900">Section {{ index + 1 }}</span>
              </div>
              <Button @click="removeSection(index)" variant="ghost" size="sm" class="text-red-600 hover:text-red-700">
                <TrashIcon class="h-4 w-4" />
              </Button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Section Title</label>
                <input
                  v-model="section.title"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Enter section title"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
                <select
                  v-model="section.type"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="text">Text Content</option>
                  <option value="chart">Chart/Graph</option>
                  <option value="table">Data Table</option>
                  <option value="metrics">Key Metrics</option>
                </select>
              </div>
            </div>

            <!-- Content Preview/Input -->
            <div class="mt-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Content</label>
              <div v-if="section.type === 'text'" class="space-y-2">
                <textarea
                  v-model="section.content"
                  rows="4"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Enter the content for this section, or leave blank to use dynamic content"
                ></textarea>
                <p class="text-xs text-gray-500">
                  Leave blank to use AI-generated content based on report data
                </p>
              </div>
              <div v-else-if="section.type === 'chart'" class="space-y-2">
                <select
                  v-model="section.chart_type"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="bar">Bar Chart</option>
                  <option value="line">Line Chart</option>
                  <option value="pie">Pie Chart</option>
                  <option value="doughnut">Doughnut Chart</option>
                </select>
                <p class="text-xs text-gray-500">
                  Chart will be populated with relevant data when report is generated
                </p>
              </div>
              <div v-else-if="section.type === 'table'" class="space-y-2">
                <input
                  v-model="section.table_title"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Table title (optional)"
                />
                <p class="text-xs text-gray-500">
                  Table will be populated with relevant data when report is generated
                </p>
              </div>
              <div v-else-if="section.type === 'metrics'" class="space-y-2">
                <div class="grid grid-cols-2 gap-2">
                  <input
                    v-model="section.metric_1"
                    type="text"
                    class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Metric 1"
                  />
                  <input
                    v-model="section.metric_2"
                    type="text"
                    class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Metric 2"
                  />
                  <input
                    v-model="section.metric_3"
                    type="text"
                    class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Metric 3"
                  />
                  <input
                    v-model="section.metric_4"
                    type="text"
                    class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Metric 4"
                  />
                </div>
                <p class="text-xs text-gray-500">
                  Metrics will be populated with key performance indicators
                </p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="templateForm.sections.length === 0" class="text-center py-8 text-gray-500">
          <FileTextIcon class="h-8 w-8 mx-auto mb-2 text-gray-300" />
          <p>No sections added yet</p>
          <Button @click="addSection" variant="outline" size="sm" class="mt-2">
            <PlusIcon class="h-4 w-4 mr-2" />
            Add First Section
          </Button>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="flex items-center justify-end gap-4 pt-6 border-t border-gray-200">
        <Button @click="$emit('cancel')" variant="outline">
          Cancel
        </Button>
        <Button @click="saveTemplate" variant="solid" :loading="saving">
          <SaveIcon class="h-4 w-4 mr-2" />
          {{ isEditing ? 'Update Template' : 'Create Template' }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button } from 'frappe-ui'
import {
  PlusIcon,
  UploadIcon,
  GripVerticalIcon,
  TrashIcon,
  FileTextIcon,
  SaveIcon,
} from 'lucide-vue-next'
import { ref, computed, watch } from 'vue'

// Props
const props = defineProps({
  template: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['save', 'cancel'])

// Reactive state
const saving = ref(false)
const logoInput = ref(null)

// Template form
const templateForm = ref({
  id: '',
  name: '',
  description: '',
  category: 'audit',
  sections: [],
  branding: {
    primary_color: '#7C3AED',
    font_family: 'Inter',
    header_style: 'centered',
    logo_url: null
  }
})

// Computed properties
const isEditing = computed(() => !!props.template)

// Methods
const addSection = () => {
  templateForm.value.sections.push({
    id: `section-${Date.now()}`,
    title: `Section ${templateForm.value.sections.length + 1}`,
    type: 'text',
    content: '',
    chart_type: 'bar',
    table_title: '',
    metric_1: '',
    metric_2: '',
    metric_3: '',
    metric_4: ''
  })
}

const removeSection = (index) => {
  templateForm.value.sections.splice(index, 1)
}

const handleLogoUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // In a real implementation, you would upload the file to the server
    // For now, we'll create a data URL
    const reader = new FileReader()
    reader.onload = (e) => {
      templateForm.value.branding.logo_url = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const saveTemplate = async () => {
  if (!templateForm.value.name.trim()) {
    alert('Please enter a template name')
    return
  }

  if (templateForm.value.sections.length === 0) {
    alert('Please add at least one content section')
    return
  }

  saving.value = true

  try {
    // In a real implementation, save to backend
    const templateToSave = {
      ...templateForm.value,
      id: isEditing.value ? props.template.id : `template-${Date.now()}`
    }

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))

    emit('save', templateToSave)
  } catch (error) {
    console.error('Save template error:', error)
    alert('Failed to save template. Please try again.')
  } finally {
    saving.value = false
  }
}

// Watch for prop changes
watch(() => props.template, (newTemplate) => {
  if (newTemplate) {
    templateForm.value = {
      ...newTemplate,
      branding: {
        primary_color: '#7C3AED',
        font_family: 'Inter',
        header_style: 'centered',
        logo_url: null,
        ...newTemplate.branding
      }
    }
  } else {
    // Reset form for new template
    templateForm.value = {
      id: '',
      name: '',
      description: '',
      category: 'audit',
      sections: [],
      branding: {
        primary_color: '#7C3AED',
        font_family: 'Inter',
        header_style: 'centered',
        logo_url: null
      }
    }
  }
}, { immediate: true })

// Initialize with default section if creating new template
if (!isEditing.value) {
  addSection()
}
</script>

<style scoped>
/* Custom styles for drag and drop */
.cursor-move {
  cursor: move;
}
</style>