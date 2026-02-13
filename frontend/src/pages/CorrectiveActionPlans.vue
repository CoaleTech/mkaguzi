<template>
  <div class="min-h-screen bg-gray-50/50">
    <div class="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page Header -->
      <div class="mb-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 flex items-center">
              <ClipboardCheckIcon class="h-7 w-7 mr-3 text-orange-600" />
              Corrective Action Plans
            </h1>
            <p class="text-gray-600 mt-1">
              Track and manage corrective actions for audit findings
            </p>
          </div>
          <div class="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              @click="showStatsDetails = !showStatsDetails"
            >
              <BarChart3Icon class="h-4 w-4 mr-1" />
              {{ showStatsDetails ? 'Hide' : 'Show' }} Analytics
            </Button>
          </div>
        </div>
      </div>

      <!-- Stats Component -->
      <ActionStats :stats="stats" :showDetails="showStatsDetails" />

      <!-- Filters Component -->
      <ActionFilters
        v-model="filters"
        @create="openCreateModal"
        @refresh="fetchPlans"
        @export="exportPlans"
      />

      <!-- Main Content -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <!-- Loading State -->
        <div v-if="loading" class="p-12 text-center">
          <LoaderIcon class="h-8 w-8 animate-spin text-orange-600 mx-auto" />
          <p class="text-gray-500 mt-3">Loading action plans...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredPlans.length === 0" class="p-12 text-center">
          <ClipboardXIcon class="h-16 w-16 text-gray-300 mx-auto" />
          <h3 class="mt-4 text-lg font-medium text-gray-900">No action plans found</h3>
          <p class="text-gray-500 mt-2">
            {{ hasFilters ? 'Try adjusting your filters' : 'Get started by creating your first corrective action plan' }}
          </p>
          <Button
            v-if="!hasFilters"
            variant="solid"
            theme="gray"
            class="mt-4"
            @click="openCreateModal"
          >
            <PlusIcon class="h-4 w-4 mr-1" />
            Create Action Plan
          </Button>
        </div>

        <!-- Data Table -->
        <div v-else>
          <DataTable
            :columns="columns"
            :data="filteredPlans"
            :sortable="true"
            @row-click="viewPlan"
          >
            <!-- Plan ID Column -->
            <template #column-plan_id="{ row }">
              <span class="font-mono text-sm text-gray-900">{{ row.plan_id }}</span>
            </template>

            <!-- Title Column -->
            <template #column-title="{ row }">
              <div class="max-w-md">
                <p class="font-medium text-gray-900 truncate">{{ row.title }}</p>
                <p v-if="row.audit_finding" class="text-xs text-gray-500 truncate">
                  Finding: {{ row.audit_finding }}
                </p>
              </div>
            </template>

            <!-- Status Column -->
            <template #column-status="{ row }">
              <Badge :variant="getStatusVariant(row.status)" size="sm">
                <component :is="getStatusIcon(row.status)" class="h-3 w-3 mr-1" />
                {{ row.status || 'Draft' }}
              </Badge>
            </template>

            <!-- Priority Column -->
            <template #column-priority="{ row }">
              <Badge :variant="getPriorityVariant(row.priority)" size="sm">
                {{ row.priority || 'Medium' }}
              </Badge>
            </template>

            <!-- Responsible Column -->
            <template #column-responsible_person="{ row }">
              <div class="flex items-center">
                <div class="h-7 w-7 rounded-full bg-orange-100 flex items-center justify-center mr-2">
                  <span class="text-xs font-medium text-orange-700">
                    {{ getInitials(row.responsible_person) }}
                  </span>
                </div>
                <span class="text-sm text-gray-900">{{ formatUserName(row.responsible_person) }}</span>
              </div>
            </template>

            <!-- Progress Column -->
            <template #column-completion_percentage="{ row }">
              <div class="flex items-center gap-2">
                <div class="w-20 bg-gray-200 rounded-full h-2">
                  <div
                    class="h-2 rounded-full transition-all duration-300"
                    :class="getProgressColor(row.completion_percentage)"
                    :style="{ width: `${row.completion_percentage || 0}%` }"
                  ></div>
                </div>
                <span class="text-sm font-medium text-gray-700 w-10">
                  {{ row.completion_percentage || 0 }}%
                </span>
              </div>
            </template>

            <!-- Due Date Column -->
            <template #column-target_completion_date="{ row }">
              <div class="flex items-center" :class="getDueDateClass(row)">
                <CalendarIcon class="h-4 w-4 mr-1.5" />
                <span>{{ formatDate(row.target_completion_date) }}</span>
                <Badge
                  v-if="isOverdue(row)"
                  variant="subtle"
                  size="sm"
                  class="ml-2 text-red-600 bg-red-50"
                >
                  Overdue
                </Badge>
              </div>
            </template>

            <!-- Actions Column -->
            <template #column-actions="{ row }">
              <div class="flex items-center gap-1">
                <Button variant="ghost" size="sm" @click.stop="viewPlan(row)" title="View">
                  <EyeIcon class="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" @click.stop="editPlan(row)" title="Edit">
                  <EditIcon class="h-4 w-4" />
                </Button>
                <Dropdown :options="getRowActions(row)">
                  <template #default="{ toggleDropdown }">
                    <Button variant="ghost" size="sm" @click.stop="toggleDropdown">
                      <MoreHorizontalIcon class="h-4 w-4" />
                    </Button>
                  </template>
                </Dropdown>
              </div>
            </template>
          </DataTable>

          <!-- Pagination -->
          <div class="border-t border-gray-200 px-6 py-4 flex items-center justify-between">
            <p class="text-sm text-gray-700">
              Showing <span class="font-medium">{{ filteredPlans.length }}</span> of
              <span class="font-medium">{{ plans.length }}</span> action plans
            </p>
          </div>
        </div>
      </div>

      <!-- Form Modal -->
      <CorrectiveActionForm
        :show="showFormModal"
        :action="selectedAction"
        :mode="formMode"
        @update:show="showFormModal = $event"
        @saved="onPlanSaved"
        @close="closeFormModal"
      />

      <!-- Delete Confirmation Dialog -->
      <Dialog
        v-model="showDeleteDialog"
        :options="{ title: 'Delete Action Plan', size: 'sm' }"
      >
        <template #body>
          <p class="text-gray-600">
            Are you sure you want to delete this corrective action plan? This action cannot be undone.
          </p>
        </template>
        <template #actions>
          <Button variant="outline" @click="showDeleteDialog = false">Cancel</Button>
          <Button variant="solid" theme="red" @click="confirmDelete" :loading="deleting">
            Delete
          </Button>
        </template>
      </Dialog>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, reactive } from 'vue'
import { Badge, Button, Dialog, Dropdown, createResource } from 'frappe-ui'
import {
  BarChart3Icon,
  CalendarIcon,
  ClipboardCheckIcon,
  ClipboardXIcon,
  EditIcon,
  EyeIcon,
  FileTextIcon,
  FlagIcon,
  LoaderIcon,
  MoreHorizontalIcon,
  PauseCircleIcon,
  PlayCircleIcon,
  PlusIcon,
  TrashIcon,
  XCircleIcon,
  CheckCircleIcon,
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { DataTable } from '@/components/Common'
import ActionStats from '@/components/actions/ActionStats.vue'
import ActionFilters from '@/components/actions/ActionFilters.vue'
import CorrectiveActionForm from '@/components/actions/CorrectiveActionForm.vue'

const router = useRouter()

// State
const loading = ref(false)
const plans = ref([])
const showStatsDetails = ref(false)
const showFormModal = ref(false)
const showDeleteDialog = ref(false)
const selectedAction = ref(null)
const formMode = ref('create')
const deleting = ref(false)
const planToDelete = ref(null)

const filters = reactive({
  search: '',
  status: '',
  priority: '',
  dueRange: '',
  responsiblePerson: '',
})

// Columns
const columns = [
  { key: 'plan_id', label: 'Plan ID', sortable: true, width: '120px' },
  { key: 'title', label: 'Title', sortable: true },
  { key: 'status', label: 'Status', sortable: true, width: '130px' },
  { key: 'priority', label: 'Priority', sortable: true, width: '100px' },
  { key: 'responsible_person', label: 'Responsible', sortable: true, width: '160px' },
  { key: 'completion_percentage', label: 'Progress', sortable: true, width: '140px' },
  { key: 'target_completion_date', label: 'Due Date', sortable: true, width: '150px' },
  { key: 'actions', label: 'Actions', width: '120px' },
]

// Computed
const hasFilters = computed(() => {
  return filters.search || filters.status || filters.priority || filters.dueRange || filters.responsiblePerson
})

const filteredPlans = computed(() => {
  let result = [...plans.value]

  if (filters.search) {
    const search = filters.search.toLowerCase()
    result = result.filter(p =>
      p.plan_id?.toLowerCase().includes(search) ||
      p.title?.toLowerCase().includes(search) ||
      p.audit_finding?.toLowerCase().includes(search)
    )
  }

  if (filters.status) {
    result = result.filter(p => p.status === filters.status)
  }

  if (filters.priority) {
    result = result.filter(p => p.priority === filters.priority)
  }

  if (filters.responsiblePerson) {
    result = result.filter(p => p.responsible_person === filters.responsiblePerson)
  }

  if (filters.dueRange) {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())

    result = result.filter(p => {
      if (!p.target_completion_date) return filters.dueRange === 'later'
      const dueDate = new Date(p.target_completion_date)

      switch (filters.dueRange) {
        case 'overdue':
          return dueDate < today && p.status !== 'Completed' && p.status !== 'Cancelled'
        case 'today':
          return dueDate.toDateString() === today.toDateString()
        case 'this_week':
          const weekEnd = new Date(today)
          weekEnd.setDate(today.getDate() + 7)
          return dueDate >= today && dueDate <= weekEnd
        case 'this_month':
          return dueDate.getMonth() === today.getMonth() && dueDate.getFullYear() === today.getFullYear()
        case 'later':
          const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1)
          return dueDate >= nextMonth
        default:
          return true
      }
    })
  }

  return result
})

const stats = computed(() => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const weekEnd = new Date(today)
  weekEnd.setDate(today.getDate() + 7)
  const monthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0)

  const total = plans.value.length
  const inProgress = plans.value.filter(p => p.status === 'In Progress').length
  const completed = plans.value.filter(p => p.status === 'Completed').length
  const overdue = plans.value.filter(p => {
    return p.target_completion_date &&
      new Date(p.target_completion_date) < today &&
      p.status !== 'Completed' &&
      p.status !== 'Cancelled'
  }).length

  const dueThisWeek = plans.value.filter(p => {
    if (!p.target_completion_date || p.status === 'Completed') return false
    const dueDate = new Date(p.target_completion_date)
    return dueDate >= today && dueDate <= weekEnd
  }).length

  const dueThisMonth = plans.value.filter(p => {
    if (!p.target_completion_date || p.status === 'Completed') return false
    const dueDate = new Date(p.target_completion_date)
    return dueDate >= today && dueDate <= monthEnd
  }).length

  const dueLater = plans.value.filter(p => {
    if (!p.target_completion_date || p.status === 'Completed') return false
    const dueDate = new Date(p.target_completion_date)
    return dueDate > monthEnd
  }).length

  // Calculate average progress
  const plansWithProgress = plans.value.filter(p => p.completion_percentage != null)
  const avgProgress = plansWithProgress.length > 0
    ? Math.round(plansWithProgress.reduce((sum, p) => sum + (p.completion_percentage || 0), 0) / plansWithProgress.length)
    : 0

  // Group by status
  const byStatus = {}
  plans.value.forEach(p => {
    const status = p.status || 'Draft'
    byStatus[status] = (byStatus[status] || 0) + 1
  })

  // Group by priority
  const byPriority = {}
  plans.value.forEach(p => {
    const priority = p.priority || 'Medium'
    byPriority[priority] = (byPriority[priority] || 0) + 1
  })

  return {
    total,
    inProgress,
    completed,
    overdue,
    avgProgress,
    dueThisWeek,
    dueThisMonth,
    dueLater,
    byStatus,
    byPriority,
  }
})

// Methods
const fetchPlans = async () => {
  loading.value = true
  try {
    const response = await createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'Corrective Action Plan',
        fields: [
          'name',
          'plan_id',
          'audit_finding',
          'title',
          'status',
          'priority',
          'start_date',
          'target_completion_date',
          'actual_completion_date',
          'responsible_person',
          'responsible_department',
          'overall_progress',
          'completion_percentage',
          'last_progress_update',
          'creation',
          'modified',
        ],
        limit_page_length: 0,
        order_by: 'creation desc',
      },
    }).fetch()
    plans.value = response || []
  } catch (error) {
    console.error('Error loading corrective action plans:', error)
    plans.value = []
  } finally {
    loading.value = false
  }
}

const getStatusVariant = (status) => {
  const variants = {
    'Draft': 'subtle',
    'Approved': 'subtle',
    'In Progress': 'subtle',
    'On Hold': 'subtle',
    'Completed': 'subtle',
    'Cancelled': 'subtle',
  }
  return variants[status] || 'subtle'
}

const getStatusIcon = (status) => {
  const icons = {
    'Draft': FileTextIcon,
    'Approved': CheckCircleIcon,
    'In Progress': PlayCircleIcon,
    'On Hold': PauseCircleIcon,
    'Completed': CheckCircleIcon,
    'Cancelled': XCircleIcon,
  }
  return icons[status] || FileTextIcon
}

const getPriorityVariant = (priority) => {
  return 'subtle'
}

const getProgressColor = (percentage) => {
  if (percentage >= 80) return 'bg-green-500'
  if (percentage >= 50) return 'bg-blue-500'
  if (percentage >= 25) return 'bg-amber-500'
  return 'bg-gray-400'
}

const getDueDateClass = (row) => {
  if (!row.target_completion_date) return 'text-gray-500'
  if (row.status === 'Completed' || row.status === 'Cancelled') return 'text-gray-500'
  
  const now = new Date()
  const dueDate = new Date(row.target_completion_date)
  const diffDays = Math.ceil((dueDate - now) / (1000 * 60 * 60 * 24))

  if (diffDays < 0) return 'text-red-600 font-medium'
  if (diffDays <= 7) return 'text-amber-600 font-medium'
  return 'text-gray-700'
}

const isOverdue = (row) => {
  if (!row.target_completion_date) return false
  if (row.status === 'Completed' || row.status === 'Cancelled') return false
  return new Date(row.target_completion_date) < new Date()
}

const formatDate = (date) => {
  if (!date) return 'Not set'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const getInitials = (name) => {
  if (!name) return '?'
  return name.split('@')[0].split('.').map(n => n.charAt(0).toUpperCase()).slice(0, 2).join('')
}

const formatUserName = (email) => {
  if (!email) return 'Unassigned'
  return email.split('@')[0].replace(/\./g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

const getRowActions = (row) => {
  return [
    {
      label: 'View Details',
      icon: EyeIcon,
      onClick: () => viewPlan(row),
    },
    {
      label: 'Edit Plan',
      icon: EditIcon,
      onClick: () => editPlan(row),
    },
    {
      label: 'Add Milestone',
      icon: FlagIcon,
      onClick: () => addMilestone(row),
    },
    {
      label: 'Delete',
      icon: TrashIcon,
      onClick: () => deletePlan(row),
    },
  ]
}

const openCreateModal = () => {
  selectedAction.value = null
  formMode.value = 'create'
  showFormModal.value = true
}

const closeFormModal = () => {
  showFormModal.value = false
  selectedAction.value = null
}

const viewPlan = (row) => {
  router.push(`/corrective-actions/${row.name}`)
}

const editPlan = (row) => {
  selectedAction.value = row
  formMode.value = 'edit'
  showFormModal.value = true
}

const addMilestone = (row) => {
  selectedAction.value = row
  formMode.value = 'edit'
  showFormModal.value = true
  // Could auto-navigate to milestones section
}

const deletePlan = (row) => {
  planToDelete.value = row
  showDeleteDialog.value = true
}

const confirmDelete = async () => {
  if (!planToDelete.value) return
  
  deleting.value = true
  try {
    await createResource({
      url: 'frappe.client.delete',
      params: {
        doctype: 'Corrective Action Plan',
        name: planToDelete.value.name,
      },
    }).fetch()
    await fetchPlans()
    showDeleteDialog.value = false
  } catch (error) {
    console.error('Error deleting plan:', error)
  } finally {
    deleting.value = false
    planToDelete.value = null
  }
}

const onPlanSaved = () => {
  fetchPlans()
  closeFormModal()
}

const exportPlans = () => {
  // Export functionality
  console.log('Exporting plans...')
}

// Lifecycle
onMounted(() => {
  fetchPlans()
})
</script>
