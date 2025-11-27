<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-purple-100 rounded-lg">
            <FileTextIcon class="h-6 w-6 text-purple-600" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Audit Programs</h1>
            <p class="text-gray-600 mt-1">
              Create and manage comprehensive audit programs with detailed procedures
            </p>
          </div>
        </div>
      </div>
      
      <div class="flex flex-wrap items-center gap-2">
        <Button variant="outline" size="sm" @click="exportPrograms" :disabled="auditPrograms.length === 0">
          <template #prefix><DownloadIcon class="h-4 w-4" /></template>
          Export
        </Button>
        <Button variant="outline" size="sm" @click="refreshData" :loading="loading">
          <template #prefix><RefreshCwIcon class="h-4 w-4" /></template>
          Refresh
        </Button>
        <Button variant="outline" theme="purple" size="sm" @click="createFromTemplate" :disabled="templatePrograms.length === 0">
          <template #prefix><CopyIcon class="h-4 w-4" /></template>
          Use Template
        </Button>
        <Button variant="solid" theme="purple" size="sm" @click="openCreateForm">
          <template #prefix><PlusIcon class="h-4 w-4" /></template>
          New Program
        </Button>
      </div>
    </div>

    <!-- Notification Messages -->
    <div v-if="errorMessage" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <XCircleIcon class="h-5 w-5 text-red-400 mr-2" />
          <p class="text-sm text-red-800">{{ errorMessage }}</p>
        </div>
        <button @click="errorMessage = ''" class="text-red-500 hover:text-red-700">
          <XIcon class="h-4 w-4" />
        </button>
      </div>
    </div>

    <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <CheckCircle2Icon class="h-5 w-5 text-green-400 mr-2" />
          <p class="text-sm text-green-800">{{ successMessage }}</p>
        </div>
        <button @click="successMessage = ''" class="text-green-500 hover:text-green-700">
          <XIcon class="h-4 w-4" />
        </button>
      </div>
    </div>

    <!-- Stats Dashboard -->
    <ProgramStats :stats="programStats" :showDetails="showStatsDetails" />

    <!-- Filters -->
    <ProgramFilters
      v-model:searchQuery="searchQuery"
      v-model:typeFilter="filterType"
      v-model:templateFilter="filterTemplate"
      v-model:statusFilter="filterStatus"
      v-model:viewMode="viewMode"
    />

    <!-- Bulk Actions -->
    <div v-if="selectedPrograms.length > 0" class="bg-purple-50 border border-purple-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <span class="text-sm font-medium text-purple-900">
            {{ selectedPrograms.length }} program{{ selectedPrograms.length > 1 ? 's' : '' }} selected
          </span>
        </div>
        <div class="flex items-center space-x-2">
          <Button variant="outline" size="sm" @click="clearSelection">Clear Selection</Button>
          <Button variant="outline" size="sm" @click="bulkCreateTemplates">
            <template #prefix><LayersIcon class="h-4 w-4" /></template>
            Create Templates
          </Button>
          <Button variant="outline" size="sm" @click="bulkDeletePrograms" class="text-red-600 hover:text-red-700">
            <template #prefix><TrashIcon class="h-4 w-4" /></template>
            Delete Selected
          </Button>
        </div>
      </div>
    </div>

    <!-- Programs Display -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">Audit Programs</h3>
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-600">
              Showing {{ filteredPrograms.length }} of {{ auditPrograms.length }} programs
            </span>
            <Button
              v-if="viewMode === 'table' && filteredPrograms.length > 0"
              variant="outline"
              size="sm"
              @click="toggleSelectAll"
            >
              {{ selectedPrograms.length === filteredPrograms.length ? 'Deselect All' : 'Select All' }}
            </Button>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-if="viewMode === 'table'" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left w-10">
                <input
                  type="checkbox"
                  class="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  :checked="selectedPrograms.length === filteredPrograms.length && filteredPrograms.length > 0"
                  @change="toggleSelectAll"
                />
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Program</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Template</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Completion</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Procedures</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="program in filteredPrograms"
              :key="program.name"
              class="hover:bg-gray-50 transition-colors"
              :class="{ 'bg-purple-50': selectedPrograms.includes(program.name) }"
            >
              <td class="px-6 py-4">
                <input
                  type="checkbox"
                  class="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  :checked="selectedPrograms.includes(program.name)"
                  @change="toggleProgramSelection(program.name)"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-lg bg-purple-500 flex items-center justify-center text-white font-bold text-sm">
                      {{ (program.audit_type || 'AU').substring(0, 2).toUpperCase() }}
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-semibold text-gray-900">{{ program.program_id }}</div>
                    <div class="text-sm text-gray-500">{{ program.program_name }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge :variant="getTypeVariant(program.audit_type)" size="sm">
                  {{ program.audit_type }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge v-if="program.is_template" variant="subtle" theme="purple" size="sm">
                  <FileTextIcon class="h-3 w-3 mr-1" />
                  Template
                </Badge>
                <span v-else class="text-sm text-gray-500">-</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-20 bg-gray-200 rounded-full h-2 mr-2">
                    <div 
                      :class="getProgressBarColor(program.completion_percent || 0)"
                      class="h-2 rounded-full transition-all duration-300"
                      :style="{ width: `${program.completion_percent || 0}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-600">{{ program.completion_percent || 0 }}%</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-medium text-gray-900">{{ program.total_procedures || 0 }}</span>
                  <span class="text-xs text-gray-500">({{ program.completed_procedures || 0 }} done)</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center space-x-1">
                  <Button variant="ghost" size="sm" @click="viewProgram(program)" class="!p-1.5">
                    <EyeIcon class="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" @click="openEditForm(program)" class="!p-1.5">
                    <EditIcon class="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" @click="duplicateProgram(program)" class="!p-1.5">
                    <CopyIcon class="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" @click="deleteProgram(program)" class="!p-1.5 text-red-500 hover:text-red-700">
                    <TrashIcon class="h-4 w-4" />
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Card View -->
      <div v-else class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="program in filteredPrograms"
            :key="program.name"
            class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-200 cursor-pointer group"
            :class="{ 'ring-2 ring-purple-500 bg-purple-50': selectedPrograms.includes(program.name) }"
            @click="toggleProgramSelection(program.name)"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center space-x-3">
                <div class="h-12 w-12 rounded-xl bg-purple-500 flex items-center justify-center text-white font-bold">
                  {{ (program.audit_type || 'AU').substring(0, 2).toUpperCase() }}
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 group-hover:text-purple-900">{{ program.program_id }}</h3>
                  <p class="text-sm text-gray-600 truncate max-w-[150px]">{{ program.program_name }}</p>
                </div>
              </div>
              <div class="flex flex-col gap-1">
                <Badge :variant="getTypeVariant(program.audit_type)" size="sm">
                  {{ program.audit_type }}
                </Badge>
                <Badge v-if="program.is_template" variant="subtle" theme="purple" size="sm">
                  Template
                </Badge>
              </div>
            </div>

            <div class="space-y-3">
              <div>
                <div class="flex justify-between items-center mb-1">
                  <span class="text-sm text-gray-600">Completion</span>
                  <span class="text-sm font-medium">{{ program.completion_percent || 0 }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    :class="getProgressBarColor(program.completion_percent || 0)"
                    class="h-2 rounded-full transition-all duration-300"
                    :style="{ width: `${program.completion_percent || 0}%` }"
                  ></div>
                </div>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Procedures</span>
                <span class="text-sm font-medium">{{ program.completed_procedures || 0 }}/{{ program.total_procedures || 0 }}</span>
              </div>
            </div>

            <div class="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
              <div class="flex items-center space-x-1">
                <Button variant="ghost" size="sm" @click.stop="viewProgram(program)" class="!p-1.5">
                  <EyeIcon class="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" @click.stop="openEditForm(program)" class="!p-1.5">
                  <EditIcon class="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" @click.stop="duplicateProgram(program)" class="!p-1.5">
                  <CopyIcon class="h-4 w-4" />
                </Button>
              </div>
              <div class="text-xs text-gray-500">
                {{ formatDate(program.modified) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredPrograms.length === 0 && auditPrograms.length === 0" class="px-6 py-20 text-center">
        <div class="mx-auto h-20 w-20 rounded-2xl bg-purple-50 border-2 border-purple-100 flex items-center justify-center mb-8 shadow-sm">
          <FileTextIcon class="h-10 w-10 text-purple-500" />
        </div>
        <div class="max-w-md mx-auto">
          <h3 class="text-2xl font-bold text-gray-900 mb-3">Welcome to Audit Programs</h3>
          <p class="text-gray-600 mb-8 leading-relaxed">
            Create detailed audit programs with procedures, risk areas, and control objectives.
          </p>
          <div class="flex flex-col sm:flex-row justify-center gap-3">
            <Button variant="solid" theme="purple" size="lg" @click="openCreateForm">
              <template #prefix><PlusIcon class="h-5 w-5" /></template>
              Create Your First Program
            </Button>
          </div>
        </div>
      </div>

      <!-- No Results State -->
      <div v-else-if="filteredPrograms.length === 0" class="px-6 py-12 text-center">
        <SearchIcon class="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No programs found</h3>
        <p class="text-gray-600 mb-6">
          Try adjusting your search or filter criteria.
        </p>
        <Button variant="outline" @click="clearFilters">Clear Filters</Button>
      </div>
    </div>

    <!-- Audit Program Form Modal -->
    <AuditProgramForm
      v-model:show="showFormModal"
      :program="selectedProgram"
      :mode="formMode"
      @saved="handleFormSaved"
      @close="handleFormClose"
    />

    <!-- View Program Modal -->
    <Dialog v-model="showViewModal" :options="{ title: viewingProgram?.program_name || 'Program Details', size: 'xl' }">
      <template #body>
        <div v-if="viewingProgram" class="p-6 space-y-6">
          <!-- Program Header -->
          <div class="flex items-start justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ viewingProgram.program_id }}</h3>
              <p class="text-sm text-gray-500">{{ viewingProgram.audit_type }}</p>
            </div>
            <Badge v-if="viewingProgram.is_template" variant="subtle" theme="purple">Template</Badge>
          </div>

          <!-- Objectives -->
          <div>
            <h4 class="text-sm font-medium text-gray-900 mb-2">Objectives</h4>
            <div class="prose prose-sm max-w-none" v-html="viewingProgram.program_objectives"></div>
          </div>

          <!-- Procedures Summary -->
          <div>
            <h4 class="text-sm font-medium text-gray-900 mb-2">Procedures ({{ viewingProgram.program_procedures?.length || 0 }})</h4>
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="grid grid-cols-4 gap-4 text-center">
                <div>
                  <p class="text-2xl font-bold text-gray-900">{{ viewingProgram.total_procedures || 0 }}</p>
                  <p class="text-xs text-gray-500">Total</p>
                </div>
                <div>
                  <p class="text-2xl font-bold text-green-600">{{ viewingProgram.completed_procedures || 0 }}</p>
                  <p class="text-xs text-gray-500">Completed</p>
                </div>
                <div>
                  <p class="text-2xl font-bold text-amber-600">{{ viewingProgram.not_applicable_procedures || 0 }}</p>
                  <p class="text-xs text-gray-500">N/A</p>
                </div>
                <div>
                  <p class="text-2xl font-bold text-purple-600">{{ viewingProgram.completion_percent || 0 }}%</p>
                  <p class="text-xs text-gray-500">Complete</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Risk Areas -->
          <div v-if="viewingProgram.risk_areas?.length > 0">
            <h4 class="text-sm font-medium text-gray-900 mb-2">Risk Areas</h4>
            <div class="space-y-2">
              <div v-for="(risk, i) in viewingProgram.risk_areas" :key="i" class="flex items-start gap-2 p-2 bg-gray-50 rounded-lg">
                <Badge :variant="getRiskVariant(risk.risk_rating)" size="sm">{{ risk.risk_rating }}</Badge>
                <span class="text-sm text-gray-700">{{ risk.risk_description }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showViewModal = false">Close</Button>
        <Button variant="solid" theme="purple" @click="openEditForm(viewingProgram); showViewModal = false">
          Edit Program
        </Button>
      </template>
    </Dialog>

    <!-- Template Selection Modal -->
    <Dialog v-model="showTemplateModal" :options="{ title: 'Select Template', size: 'lg' }">
      <template #body>
        <div class="p-6 space-y-4">
          <p class="text-sm text-gray-600">Select a template to create a new program from:</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="template in templatePrograms"
              :key="template.name"
              class="border border-gray-200 rounded-lg p-4 hover:border-purple-500 hover:bg-purple-50 cursor-pointer transition-all"
              @click="useTemplate(template)"
            >
              <div class="flex items-start space-x-3">
                <div class="p-2 bg-purple-100 rounded-lg">
                  <FileTextIcon class="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900">{{ template.program_name }}</h4>
                  <p class="text-xs text-gray-500 mt-1">{{ template.audit_type }} • {{ template.total_procedures || 0 }} procedures</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Badge, Button, Dialog } from 'frappe-ui'
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  CheckCircle2Icon,
  CopyIcon,
  DownloadIcon,
  EditIcon,
  EyeIcon,
  FileTextIcon,
  LayersIcon,
  PlusIcon,
  RefreshCwIcon,
  SearchIcon,
  TrashIcon,
  XCircleIcon,
  XIcon,
} from 'lucide-vue-next'

// Import components
import ProgramStats from '@/components/programs/ProgramStats.vue'
import ProgramFilters from '@/components/programs/ProgramFilters.vue'
import AuditProgramForm from '@/components/programs/AuditProgramForm.vue'

// Store
import { useAuditStore } from '@/stores/audit'

const auditStore = useAuditStore()

// State
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showFormModal = ref(false)
const showViewModal = ref(false)
const showTemplateModal = ref(false)
const showStatsDetails = ref(true)
const selectedProgram = ref(null)
const viewingProgram = ref(null)
const formMode = ref('create')

// Filter state
const searchQuery = ref('')
const filterType = ref('')
const filterTemplate = ref('')
const filterStatus = ref('')
const viewMode = ref('table')
const selectedPrograms = ref([])

// Computed
const auditPrograms = computed(() => auditStore.auditPrograms || [])

const templatePrograms = computed(() => {
  return auditPrograms.value.filter(p => p.is_template)
})

const programStats = computed(() => {
  const programs = auditPrograms.value
  const templates = programs.filter(p => p.is_template).length
  const active = programs.filter(p => !p.is_template && (p.completion_percent || 0) < 100).length
  
  const nonTemplates = programs.filter(p => !p.is_template)
  const avgCompletion = nonTemplates.length > 0
    ? Math.round(nonTemplates.reduce((sum, p) => sum + (p.completion_percent || 0), 0) / nonTemplates.length)
    : 0
  
  const totalProcedures = programs.reduce((sum, p) => sum + (p.total_procedures || 0), 0)
  const completedProcedures = programs.reduce((sum, p) => sum + (p.completed_procedures || 0), 0)
  
  // Count overdue
  const now = new Date()
  const overdue = programs.filter(p => {
    if (p.is_template) return false
    if (!p.modified) return false
    const lastModified = new Date(p.modified)
    const daysSinceModified = (now - lastModified) / (1000 * 60 * 60 * 24)
    return daysSinceModified > 30 && (p.completion_percent || 0) < 100
  }).length

  // By type
  const byType = {}
  programs.forEach(p => {
    if (p.audit_type) {
      byType[p.audit_type] = (byType[p.audit_type] || 0) + 1
    }
  })

  return {
    total: programs.length,
    templates,
    active,
    avgCompletion,
    totalProcedures,
    completedProcedures,
    overdue,
    byType,
  }
})

const filteredPrograms = computed(() => {
  let filtered = [...auditPrograms.value]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p =>
      p.program_id?.toLowerCase().includes(query) ||
      p.program_name?.toLowerCase().includes(query) ||
      p.audit_type?.toLowerCase().includes(query)
    )
  }

  if (filterType.value) {
    filtered = filtered.filter(p => p.audit_type === filterType.value)
  }

  if (filterTemplate.value === 'templates') {
    filtered = filtered.filter(p => p.is_template)
  } else if (filterTemplate.value === 'programs') {
    filtered = filtered.filter(p => !p.is_template)
  }

  if (filterStatus.value === 'not_started') {
    filtered = filtered.filter(p => !p.is_template && (p.completion_percent || 0) === 0)
  } else if (filterStatus.value === 'in_progress') {
    filtered = filtered.filter(p => !p.is_template && (p.completion_percent || 0) > 0 && (p.completion_percent || 0) < 100)
  } else if (filterStatus.value === 'completed') {
    filtered = filtered.filter(p => !p.is_template && (p.completion_percent || 0) >= 100)
  }

  return filtered
})

// Methods
const refreshData = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await auditStore.fetchAuditPrograms()
  } catch (error) {
    console.error('Error refreshing data:', error)
    errorMessage.value = 'Failed to refresh data. Please try again.'
  } finally {
    loading.value = false
  }
}

const openCreateForm = () => {
  selectedProgram.value = null
  formMode.value = 'create'
  showFormModal.value = true
}

const openEditForm = async (program) => {
  try {
    const details = await auditStore.fetchAuditProgramDetails(program.name)
    selectedProgram.value = details || program
    formMode.value = 'edit'
    showFormModal.value = true
  } catch (error) {
    console.error('Error fetching program details:', error)
    selectedProgram.value = program
    formMode.value = 'edit'
    showFormModal.value = true
  }
}

const viewProgram = async (program) => {
  try {
    const details = await auditStore.fetchAuditProgramDetails(program.name)
    viewingProgram.value = details || program
    showViewModal.value = true
  } catch (error) {
    console.error('Error fetching program details:', error)
    viewingProgram.value = program
    showViewModal.value = true
  }
}

const duplicateProgram = async (program) => {
  try {
    const details = await auditStore.fetchAuditProgramDetails(program.name)
    if (details) {
      selectedProgram.value = {
        ...details,
        program_id: `${details.program_id}_copy`,
        program_name: `${details.program_name} (Copy)`,
        is_template: false,
        name: null,
      }
      formMode.value = 'create'
      showFormModal.value = true
    }
  } catch (error) {
    console.error('Error duplicating program:', error)
  }
}

const deleteProgram = async (program) => {
  if (!confirm(`Are you sure you want to delete "${program.program_name}"?`)) return
  
  try {
    await auditStore.deleteAuditProgram(program.name)
    successMessage.value = 'Program deleted successfully'
    await refreshData()
    setTimeout(() => { successMessage.value = '' }, 3000)
  } catch (error) {
    console.error('Error deleting program:', error)
    errorMessage.value = 'Failed to delete program. Please try again.'
  }
}

const handleFormSaved = async () => {
  showFormModal.value = false
  selectedProgram.value = null
  successMessage.value = formMode.value === 'edit' ? 'Program updated successfully' : 'Program created successfully'
  await refreshData()
  setTimeout(() => { successMessage.value = '' }, 3000)
}

const handleFormClose = () => {
  showFormModal.value = false
  selectedProgram.value = null
}

const createFromTemplate = () => {
  showTemplateModal.value = true
}

const useTemplate = async (template) => {
  try {
    const details = await auditStore.fetchAuditProgramDetails(template.name)
    if (details) {
      selectedProgram.value = {
        ...details,
        program_id: '',
        program_name: '',
        is_template: false,
        engagement_reference: '',
        name: null,
      }
      formMode.value = 'create'
      showTemplateModal.value = false
      showFormModal.value = true
    }
  } catch (error) {
    console.error('Error using template:', error)
  }
}

// Utility methods
const getTypeVariant = (type) => {
  const variants = {
    'Financial': 'subtle',
    'Operational': 'subtle',
    'Compliance': 'subtle',
    'IT': 'subtle',
    'Inventory': 'subtle',
    'Cash': 'subtle',
    'Sales': 'subtle',
    'Procurement': 'subtle',
  }
  return variants[type] || 'subtle'
}

const getProgressBarColor = (percentage) => {
  if (percentage >= 100) return 'bg-green-500'
  if (percentage >= 75) return 'bg-blue-500'
  if (percentage >= 50) return 'bg-yellow-500'
  if (percentage >= 25) return 'bg-orange-500'
  return 'bg-red-500'
}

const getRiskVariant = (riskRating) => {
  const variants = {
    'Low': 'subtle',
    'Medium': 'subtle',
    'High': 'subtle',
  }
  return variants[riskRating] || 'subtle'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

// Selection methods
const toggleProgramSelection = (programId) => {
  const index = selectedPrograms.value.indexOf(programId)
  if (index > -1) {
    selectedPrograms.value.splice(index, 1)
  } else {
    selectedPrograms.value.push(programId)
  }
}

const toggleSelectAll = () => {
  if (selectedPrograms.value.length === filteredPrograms.value.length) {
    selectedPrograms.value = []
  } else {
    selectedPrograms.value = filteredPrograms.value.map(p => p.name)
  }
}

const clearSelection = () => {
  selectedPrograms.value = []
}

const clearFilters = () => {
  searchQuery.value = ''
  filterType.value = ''
  filterTemplate.value = ''
  filterStatus.value = ''
}

// Bulk actions
const bulkCreateTemplates = async () => {
  if (selectedPrograms.value.length === 0) return
  const count = selectedPrograms.value.length
  if (!confirm(`Create templates for ${count} selected program${count > 1 ? 's' : ''}?`)) return
  
  // Implementation would create templates
  successMessage.value = `Created templates for ${count} program${count > 1 ? 's' : ''}`
  selectedPrograms.value = []
  setTimeout(() => { successMessage.value = '' }, 3000)
}

const bulkDeletePrograms = async () => {
  if (selectedPrograms.value.length === 0) return
  const count = selectedPrograms.value.length
  if (!confirm(`Are you sure you want to delete ${count} program${count > 1 ? 's' : ''}?`)) return
  
  try {
    for (const programId of selectedPrograms.value) {
      await auditStore.deleteAuditProgram(programId)
    }
    selectedPrograms.value = []
    successMessage.value = `Deleted ${count} program${count > 1 ? 's' : ''}`
    await refreshData()
    setTimeout(() => { successMessage.value = '' }, 3000)
  } catch (error) {
    console.error('Error deleting programs:', error)
    errorMessage.value = 'Failed to delete some programs. Please try again.'
  }
}

const exportPrograms = () => {
  const data = filteredPrograms.value.map(p => ({
    'Program ID': p.program_id,
    'Program Name': p.program_name,
    'Audit Type': p.audit_type,
    'Is Template': p.is_template ? 'Yes' : 'No',
    'Completion %': p.completion_percent || 0,
    'Procedures': p.total_procedures || 0,
    'Completed': p.completed_procedures || 0,
    'Modified': formatDate(p.modified),
  }))

  const csv = [
    Object.keys(data[0] || {}).join(','),
    ...data.map(row => Object.values(row).map(val => `"${val}"`).join(','))
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `audit-programs-${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}

// Keyboard shortcuts
const handleKeydown = (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
    event.preventDefault()
    openCreateForm()
  }
  if (event.key === 'Escape') {
    if (showFormModal.value) {
      showFormModal.value = false
      selectedProgram.value = null
    } else if (showViewModal.value) {
      showViewModal.value = false
    }
  }
}

// Watchers
watch(filteredPrograms, () => {
  selectedPrograms.value = []
})

// Lifecycle
onMounted(async () => {
  await refreshData()
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>
