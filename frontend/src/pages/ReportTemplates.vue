<template>
  <div class="report-templates">
    <div class="flex h-screen bg-gray-50">
      <!-- Sidebar -->
      <div class="w-80 bg-white border-r border-gray-200 flex flex-col">
        <!-- Header -->
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-center gap-3">
            <div class="h-12 w-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg">
              <FileTextIcon class="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 class="text-lg font-bold text-gray-900">Report Templates</h2>
              <p class="text-sm text-gray-600">Custom report designs</p>
            </div>
          </div>
        </div>

        <!-- Template Actions -->
        <div class="flex-1 overflow-y-auto p-4">
          <div class="space-y-6">
            <!-- Create Template -->
            <div>
              <Button @click="createNewTemplate" class="w-full" variant="solid">
                <PlusIcon class="h-4 w-4 mr-2" />
                Create Template
              </Button>
            </div>

            <!-- Template Categories -->
            <div>
              <div class="text-sm font-medium text-gray-700 mb-3">Categories</div>
              <div class="space-y-2">
                <button
                  v-for="category in categories"
                  :key="category.id"
                  @click="filterByCategory(category.id)"
                  :class="[
                    'w-full text-left px-3 py-2 rounded-lg text-sm transition-colors',
                    activeCategory === category.id
                      ? 'bg-purple-100 text-purple-700 border border-purple-200'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <component :is="category.icon" class="h-4 w-4 inline mr-2" />
                  {{ category.name }}
                </button>
              </div>
            </div>

            <!-- Template Library -->
            <div>
              <div class="text-sm font-medium text-gray-700 mb-3">Template Library</div>
              <div class="space-y-2">
                <div
                  v-for="template in filteredTemplates"
                  :key="template.id"
                  @click="selectTemplate(template)"
                  :class="[
                    'p-3 rounded-lg border cursor-pointer transition-all',
                    selectedTemplate?.id === template.id
                      ? 'border-purple-300 bg-purple-50 shadow-sm'
                      : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                  ]"
                >
                  <div class="flex items-center gap-3">
                    <div class="h-10 w-10 rounded-lg bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center">
                      <component :is="template.icon" class="h-5 w-5 text-white" />
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-gray-900 truncate">{{ template.name }}</div>
                      <div class="text-xs text-gray-500">{{ template.description }}</div>
                    </div>
                  </div>
                  <div class="mt-2 flex items-center justify-between text-xs text-gray-500">
                    <span>{{ template.usage_count }} uses</span>
                    <span>{{ formatDate(template.updated_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="flex-1 overflow-hidden">
        <!-- Header -->
        <div class="bg-white border-b border-gray-200 p-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">
                {{ selectedTemplate ? selectedTemplate.name : 'Custom Report Templates' }}
              </h1>
              <p class="text-gray-600">
                {{ selectedTemplate ? selectedTemplate.description : 'Create and manage professional audit report templates' }}
              </p>
            </div>
            <div class="flex items-center gap-4" v-if="selectedTemplate">
              <Button @click="duplicateTemplate" variant="outline" size="sm">
                <CopyIcon class="h-4 w-4 mr-2" />
                Duplicate
              </Button>
              <Button @click="editTemplate" variant="outline" size="sm">
                <EditIcon class="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button @click="generateReport" variant="solid" size="sm">
                <FileTextIcon class="h-4 w-4 mr-2" />
                Generate Report
              </Button>
            </div>
          </div>
        </div>

        <!-- Template Content -->
        <div class="p-6 overflow-y-auto h-full">
          <div v-if="!selectedTemplate" class="text-center py-12">
            <div class="h-24 w-24 mx-auto mb-6 rounded-full bg-gray-100 flex items-center justify-center">
              <FileTextIcon class="h-12 w-12 text-gray-400" />
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">No Template Selected</h3>
            <p class="text-gray-600 mb-6">Choose a template from the sidebar or create a new one to get started.</p>
            <Button @click="createNewTemplate" variant="solid">
              <PlusIcon class="h-4 w-4 mr-2" />
              Create Your First Template
            </Button>
          </div>

          <div v-else class="space-y-6">
            <!-- Template Preview -->
            <div class="bg-white rounded-lg border border-gray-200 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Template Preview</h3>
                <div class="flex items-center gap-2">
                  <Button @click="previewTemplate" variant="outline" size="sm">
                    <EyeIcon class="h-4 w-4 mr-2" />
                    Preview
                  </Button>
                </div>
              </div>
              <div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <div class="space-y-4">
                  <!-- Header Section -->
                  <div class="text-center border-b border-gray-300 pb-4">
                    <div class="h-12 w-32 mx-auto mb-2 bg-gray-300 rounded flex items-center justify-center">
                      <span class="text-xs text-gray-600">Company Logo</span>
                    </div>
                    <h2 class="text-xl font-bold text-gray-900">{{ selectedTemplate.name }}</h2>
                    <p class="text-sm text-gray-600">Generated on {{ formatDate(new Date()) }}</p>
                  </div>

                  <!-- Content Sections -->
                  <div class="space-y-4">
                    <div v-for="section in selectedTemplate.sections" :key="section.id" class="border border-gray-200 rounded p-4">
                      <h4 class="font-medium text-gray-900 mb-2">{{ section.title }}</h4>
                      <div class="text-sm text-gray-600">
                        <div v-if="section.type === 'text'" class="prose prose-sm max-w-none">
                          <p>{{ section.content || 'Sample content for ' + section.title.toLowerCase() }}</p>
                        </div>
                        <div v-else-if="section.type === 'chart'" class="h-32 bg-gray-200 rounded flex items-center justify-center">
                          <BarChartIcon class="h-8 w-8 text-gray-400" />
                        </div>
                        <div v-else-if="section.type === 'table'" class="border border-gray-300 rounded">
                          <div class="p-2 bg-gray-100 text-xs font-medium">Sample Table</div>
                          <div class="p-2 text-xs">Row 1, Column 1 | Row 1, Column 2</div>
                          <div class="p-2 text-xs">Row 2, Column 1 | Row 2, Column 2</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Footer -->
                  <div class="text-center border-t border-gray-300 pt-4 text-xs text-gray-500">
                    <p>Confidential - Internal Audit Report</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Template Details -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Template Info -->
              <div class="bg-white rounded-lg border border-gray-200 p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Template Information</h3>
                <div class="space-y-3">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Category</label>
                    <p class="text-sm text-gray-900">{{ getCategoryName(selectedTemplate.category) }}</p>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Created By</label>
                    <p class="text-sm text-gray-900">{{ selectedTemplate.created_by }}</p>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Last Modified</label>
                    <p class="text-sm text-gray-900">{{ formatDate(selectedTemplate.updated_at) }}</p>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Usage Count</label>
                    <p class="text-sm text-gray-900">{{ selectedTemplate.usage_count }} reports generated</p>
                  </div>
                </div>
              </div>

              <!-- Branding Settings -->
              <div class="bg-white rounded-lg border border-gray-200 p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Branding & Styling</h3>
                <div class="space-y-3">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Primary Color</label>
                    <div class="flex items-center gap-2">
                      <div
                        class="w-6 h-6 rounded border border-gray-300"
                        :style="{ backgroundColor: selectedTemplate.branding?.primary_color || '#7C3AED' }"
                      ></div>
                      <span class="text-sm text-gray-900">{{ selectedTemplate.branding?.primary_color || '#7C3AED' }}</span>
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Font Family</label>
                    <p class="text-sm text-gray-900">{{ selectedTemplate.branding?.font_family || 'Inter' }}</p>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Logo</label>
                    <p class="text-sm text-gray-900">{{ selectedTemplate.branding?.logo_url ? 'Custom logo uploaded' : 'Default logo' }}</p>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Header Style</label>
                    <p class="text-sm text-gray-900 capitalize">{{ selectedTemplate.branding?.header_style || 'centered' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Recent Reports -->
            <div class="bg-white rounded-lg border border-gray-200 p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Recent Reports</h3>
              <div class="space-y-3">
                <div v-if="recentReports.length === 0" class="text-center py-8 text-gray-500">
                  <FileTextIcon class="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p>No reports generated yet</p>
                </div>
                <div
                  v-for="report in recentReports"
                  :key="report.id"
                  class="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                >
                  <div>
                    <div class="font-medium text-gray-900">{{ report.title }}</div>
                    <div class="text-sm text-gray-500">{{ formatDate(report.generated_at) }}</div>
                  </div>
                  <div class="flex items-center gap-2">
                    <Button @click="downloadReport(report)" variant="ghost" size="sm">
                      <DownloadIcon class="h-4 w-4" />
                    </Button>
                    <Button @click="viewReport(report)" variant="ghost" size="sm">
                      <EyeIcon class="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Template Builder Modal -->
    <Dialog v-model="showTemplateBuilder" :options="{ size: '4xl' }">
      <template #body>
        <ReportTemplateBuilder
          :template="editingTemplate"
          @save="handleTemplateSave"
          @cancel="showTemplateBuilder = false"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Button, Dialog } from 'frappe-ui'
import {
  FileTextIcon,
  PlusIcon,
  CopyIcon,
  EditIcon,
  EyeIcon,
  DownloadIcon,
  BarChartIcon,
  ShieldIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  TrendingUpIcon,
} from 'lucide-vue-next'
import { ref, computed, onMounted } from 'vue'
import { call } from 'frappe-ui'
import ReportTemplateBuilder from '@/components/reports/ReportTemplateBuilder.vue'

// Reactive state
const showTemplateBuilder = ref(false)
const editingTemplate = ref(null)
const selectedTemplate = ref(null)
const activeCategory = ref('all')

// Template data
const templates = ref([
  {
    id: 'audit-summary',
    name: 'Audit Summary Report',
    description: 'Comprehensive audit findings and recommendations',
    category: 'audit',
    icon: ShieldIcon,
    usage_count: 45,
    created_by: 'John Smith',
    updated_at: new Date(Date.now() - 86400000),
    sections: [
      { id: 'executive-summary', title: 'Executive Summary', type: 'text' },
      { id: 'findings-overview', title: 'Key Findings', type: 'chart' },
      { id: 'risk-assessment', title: 'Risk Assessment', type: 'table' },
      { id: 'recommendations', title: 'Recommendations', type: 'text' }
    ],
    branding: {
      primary_color: '#7C3AED',
      font_family: 'Inter',
      header_style: 'centered'
    }
  },
  {
    id: 'compliance-report',
    name: 'Compliance Status Report',
    description: 'SOX, GDPR, and regulatory compliance overview',
    category: 'compliance',
    icon: CheckCircleIcon,
    usage_count: 32,
    created_by: 'Sarah Johnson',
    updated_at: new Date(Date.now() - 172800000),
    sections: [
      { id: 'compliance-overview', title: 'Compliance Overview', type: 'chart' },
      { id: 'regulatory-status', title: 'Regulatory Status', type: 'table' },
      { id: 'gaps-identified', title: 'Gaps Identified', type: 'text' },
      { id: 'action-plan', title: 'Action Plan', type: 'text' }
    ],
    branding: {
      primary_color: '#10B981',
      font_family: 'Inter',
      header_style: 'left-aligned'
    }
  },
  {
    id: 'risk-analysis',
    name: 'Risk Analysis Report',
    description: 'Detailed risk assessment and mitigation strategies',
    category: 'risk',
    icon: AlertTriangleIcon,
    usage_count: 28,
    created_by: 'Mike Davis',
    updated_at: new Date(Date.now() - 259200000),
    sections: [
      { id: 'risk-heatmap', title: 'Risk Heatmap', type: 'chart' },
      { id: 'top-risks', title: 'Top Risks Identified', type: 'table' },
      { id: 'mitigation-strategies', title: 'Mitigation Strategies', type: 'text' },
      { id: 'monitoring-plan', title: 'Monitoring Plan', type: 'text' }
    ],
    branding: {
      primary_color: '#F59E0B',
      font_family: 'Inter',
      header_style: 'centered'
    }
  }
])

const categories = ref([
  { id: 'all', name: 'All Templates', icon: FileTextIcon },
  { id: 'audit', name: 'Audit Reports', icon: ShieldIcon },
  { id: 'compliance', name: 'Compliance', icon: CheckCircleIcon },
  { id: 'risk', name: 'Risk Analysis', icon: AlertTriangleIcon },
  { id: 'financial', name: 'Financial', icon: TrendingUpIcon }
])

const recentReports = ref([
  {
    id: 'report-001',
    title: 'Q4 2025 Audit Summary',
    generated_at: new Date(Date.now() - 3600000),
    template_id: 'audit-summary'
  },
  {
    id: 'report-002',
    title: 'GDPR Compliance Review',
    generated_at: new Date(Date.now() - 7200000),
    template_id: 'compliance-report'
  }
])

// Computed properties
const filteredTemplates = computed(() => {
  if (activeCategory.value === 'all') {
    return templates.value
  }
  return templates.value.filter(template => template.category === activeCategory.value)
})

// Methods
const createNewTemplate = () => {
  editingTemplate.value = null
  showTemplateBuilder.value = true
}

const selectTemplate = (template) => {
  selectedTemplate.value = template
}

const editTemplate = () => {
  editingTemplate.value = selectedTemplate.value
  showTemplateBuilder.value = true
}

const duplicateTemplate = async () => {
  const newName = prompt('Enter name for duplicated template:', `${selectedTemplate.value.name} (Copy)`)
  if (!newName) return

  try {
    const response = await call("mkaguzi.api.reports.duplicate_report_template", {
      template_id: selectedTemplate.value.id,
      new_name: newName
    })

    if (response.success) {
      await loadTemplates()
      selectedTemplate.value = response.data
    } else {
      alert(response.message || 'Failed to duplicate template')
    }
  } catch (error) {
    console.error('Duplicate template error:', error)
    alert('Failed to duplicate template. Please try again.')
  }
}

const generateReport = async () => {
  try {
    // Generate report using template API
    const response = await call("mkaguzi.api.reports.generate_report_from_template", {
      template_id: selectedTemplate.value.id,
      report_data: {} // Additional report data can be passed here
    })

    if (response.success) {
      // Add to recent reports
      const newReport = {
        id: `report-${Date.now()}`,
        title: `${selectedTemplate.value.name} - ${new Date().toLocaleDateString()}`,
        generated_at: new Date(),
        template_id: selectedTemplate.value.id
      }
      recentReports.value.unshift(newReport)

      // Show success message
      console.log('Report generated successfully:', response.data)
    }
  } catch (error) {
    console.error('Report generation error:', error)
  }
}

const deleteTemplate = async () => {
  if (!confirm(`Are you sure you want to delete "${selectedTemplate.value.name}"? This action cannot be undone.`)) {
    return
  }

  try {
    const response = await call("mkaguzi.api.reports.delete_report_template", {
      template_id: selectedTemplate.value.id
    })

    if (response.success) {
      await loadTemplates()
      selectedTemplate.value = null
    } else {
      alert(response.message || 'Failed to delete template')
    }
  } catch (error) {
    console.error('Delete template error:', error)
    alert('Failed to delete template. Please try again.')
  }
}

const filterByCategory = (categoryId) => {
  activeCategory.value = categoryId
}

const getCategoryName = (categoryId) => {
  const category = categories.value.find(c => c.id === categoryId)
  return category ? category.name : categoryId
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const handleTemplateSave = async (template) => {
  try {
    let response
    if (editingTemplate.value) {
      // Update existing template
      response = await call("mkaguzi.api.reports.update_report_template", {
        template_id: editingTemplate.value.id,
        template_data: template
      })
    } else {
      // Create new template
      response = await call("mkaguzi.api.reports.create_report_template", {
        template_data: template
      })
    }

    if (response.success) {
      // Reload templates
      await loadTemplates()
      showTemplateBuilder.value = false
      editingTemplate.value = null
    } else {
      alert(response.message || 'Failed to save template')
    }
  } catch (error) {
    console.error('Template save error:', error)
    alert('Failed to save template. Please try again.')
  }
}

const downloadReport = (report) => {
  console.log('Download report:', report.id)
}

const viewReport = (report) => {
  console.log('View report:', report.id)
}

// Lifecycle hooks
onMounted(() => {
  // Load templates from API
  loadTemplates()
})

const loadTemplates = async () => {
  try {
    // Load templates from backend
    const response = await call("mkaguzi.api.reports.get_report_templates")
    if (response.success) {
      templates.value = response.data
    }
  } catch (error) {
    console.error('Load templates error:', error)
  }
}
</script>

<style scoped>
/* Custom scrollbar for sidebar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>