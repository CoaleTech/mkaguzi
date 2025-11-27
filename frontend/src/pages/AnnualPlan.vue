<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-blue-100 rounded-lg">
            <CalendarIcon class="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Annual Audit Plan</h1>
            <p class="text-gray-600 mt-1">
              Create and manage comprehensive annual audit planning
            </p>
          </div>
        </div>
      </div>
      
      <div class="flex flex-wrap items-center gap-2">
        <Button variant="outline" size="sm" @click="exportPlans" :loading="exporting">
          <template #prefix><DownloadIcon class="h-4 w-4" /></template>
          Export
        </Button>
        <Button variant="outline" size="sm" @click="showTemplateModal = true">
          <template #prefix><FileTextIcon class="h-4 w-4" /></template>
          Templates
        </Button>
        <Button variant="outline" size="sm" @click="showCapacityModal = true">
          <template #prefix><BarChart3Icon class="h-4 w-4" /></template>
          Capacity
        </Button>
        <Button variant="outline" size="sm" @click="refreshData" :loading="loading">
          <template #prefix><RefreshCwIcon class="h-4 w-4" /></template>
          Refresh
        </Button>
        <Button variant="solid" theme="blue" size="sm" @click="openCreateForm">
          <template #prefix><PlusIcon class="h-4 w-4" /></template>
          New Plan
        </Button>
      </div>
    </div>

    <!-- Stats Dashboard -->
    <PlanStats :stats="planStats" :showDetails="showStatsDetails" />

    <!-- Filters -->
    <PlanFilters
      v-model:searchQuery="searchQuery"
      v-model:statusFilter="statusFilter"
      v-model:yearFilter="yearFilter"
      v-model:periodFilter="periodFilter"
      v-model:viewMode="viewMode"
    />

    <!-- Quick Actions Bar -->
    <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <h3 class="text-sm font-semibold text-gray-900">Quick Actions</h3>
          <Button
            variant="outline"
            size="sm"
            @click="showBulkModal = true"
            :disabled="selectedPlans.length === 0"
          >
            <template #prefix><LayersIcon class="h-4 w-4" /></template>
            Bulk Actions ({{ selectedPlans.length }})
          </Button>
        </div>
        <div class="text-sm text-gray-600">
          Showing {{ filteredPlans.length }} of {{ annualPlans.length }} plans
        </div>
      </div>
    </div>

    <!-- Plans Display -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">Annual Audit Plans</h3>
          <div class="flex items-center space-x-2">
            <Button
              v-if="viewMode === 'table' && filteredPlans.length > 0"
              variant="outline"
              size="sm"
              @click="selectAllPlans"
            >
              {{ selectedPlans.length === filteredPlans.length ? 'Deselect All' : 'Select All' }}
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
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  :checked="selectedPlans.length === filteredPlans.length && filteredPlans.length > 0"
                  @change="selectAllPlans"
                />
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  @click="sortBy('plan_id')">
                <div class="flex items-center space-x-1">
                  <span>Plan ID</span>
                  <ArrowUpDownIcon class="h-3 w-3" />
                </div>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  @click="sortBy('plan_year')">
                <div class="flex items-center space-x-1">
                  <span>Year</span>
                  <ArrowUpDownIcon class="h-3 w-3" />
                </div>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Utilization</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Planned Audits</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="plan in filteredPlans"
              :key="plan.name"
              class="hover:bg-gray-50 transition-colors"
              :class="{ 'bg-blue-50': selectedPlans.includes(plan.name) }"
            >
              <td class="px-6 py-4">
                <input
                  type="checkbox"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  :checked="selectedPlans.includes(plan.name)"
                  @change="togglePlanSelection(plan.name)"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-lg bg-blue-500 flex items-center justify-center text-white font-bold text-sm">
                      {{ plan.plan_year?.toString().slice(-2) || 'NA' }}
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-semibold text-gray-900">{{ plan.plan_id }}</div>
                    <div class="text-sm text-gray-500">{{ plan.plan_period }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ plan.plan_year }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <Badge :variant="getStatusVariant(plan.status)" size="sm">
                  {{ plan.status }}
                </Badge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-20 bg-gray-200 rounded-full h-2 mr-2">
                    <div 
                      class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      :style="{ width: `${getPlanProgress(plan)}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-600">{{ getPlanProgress(plan) }}%</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span class="text-sm font-medium text-gray-900">{{ plan.utilization_percentage || 0 }}%</span>
                  <div class="ml-2 w-12 bg-gray-200 rounded-full h-1.5">
                    <div 
                      class="h-1.5 rounded-full transition-all duration-300"
                      :class="getUtilizationColor(plan.utilization_percentage || 0)"
                      :style="{ width: `${Math.min(plan.utilization_percentage || 0, 100)}%` }"
                    ></div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-medium text-gray-900">{{ (plan.planned_audits || []).length }}</span>
                  <span class="text-xs text-gray-500">audits</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center space-x-1">
                  <Button variant="ghost" size="sm" @click="viewPlan(plan)" class="!p-1.5">
                    <EyeIcon class="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" @click="openEditForm(plan)" class="!p-1.5">
                    <EditIcon class="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" @click="duplicatePlan(plan)" class="!p-1.5">
                    <CopyIcon class="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" @click="deletePlan(plan)" class="!p-1.5 text-red-500 hover:text-red-700">
                    <TrashIcon class="h-4 w-4" />
                  </Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Card View -->
      <div v-else-if="viewMode === 'cards'" class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="plan in filteredPlans"
            :key="plan.name"
            class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-200 cursor-pointer group"
            :class="{ 'ring-2 ring-blue-500 bg-blue-50': selectedPlans.includes(plan.name) }"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center space-x-3">
                <div class="h-12 w-12 rounded-xl bg-blue-500 flex items-center justify-center text-white font-bold">
                  {{ plan.plan_year?.toString().slice(-2) || 'NA' }}
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 group-hover:text-blue-900">{{ plan.plan_id }}</h3>
                  <p class="text-sm text-gray-600">{{ plan.plan_period }} Plan</p>
                </div>
              </div>
              <Badge :variant="getStatusVariant(plan.status)" size="sm">
                {{ plan.status }}
              </Badge>
            </div>

            <div class="space-y-3">
              <div>
                <div class="flex justify-between items-center mb-1">
                  <span class="text-sm text-gray-600">Progress</span>
                  <span class="text-sm font-medium">{{ getPlanProgress(plan) }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    :style="{ width: `${getPlanProgress(plan)}%` }"
                  ></div>
                </div>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Utilization</span>
                <span class="text-sm font-medium">{{ plan.utilization_percentage || 0 }}%</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Planned Audits</span>
                <span class="text-sm font-medium">{{ (plan.planned_audits || []).length }}</span>
              </div>
            </div>

            <div class="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
              <div class="flex items-center space-x-1">
                <Button variant="ghost" size="sm" @click.stop="viewPlan(plan)" class="!p-1.5">
                  <EyeIcon class="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" @click.stop="openEditForm(plan)" class="!p-1.5">
                  <EditIcon class="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" @click.stop="duplicatePlan(plan)" class="!p-1.5">
                  <CopyIcon class="h-4 w-4" />
                </Button>
              </div>
              <div class="text-xs text-gray-500">
                {{ formatDate(plan.modified) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Timeline View -->
      <div v-else-if="viewMode === 'timeline'" class="p-6">
        <div class="relative">
          <div class="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>
          <div v-for="(plan, index) in filteredPlans" :key="plan.name" class="relative flex items-start mb-8 last:mb-0">
            <div class="flex-shrink-0 w-16 h-16 rounded-xl bg-blue-500 flex items-center justify-center text-white font-bold text-lg z-10">
              {{ plan.plan_year?.toString().slice(-2) || 'NA' }}
            </div>
            <div class="ml-6 flex-1 bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
              <div class="flex items-start justify-between mb-3">
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">{{ plan.plan_id }}</h3>
                  <p class="text-sm text-gray-500">{{ plan.plan_period }} • {{ plan.plan_year }}</p>
                </div>
                <Badge :variant="getStatusVariant(plan.status)" size="sm">{{ plan.status }}</Badge>
              </div>
              <div class="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <p class="text-xs text-gray-500">Planned Audits</p>
                  <p class="text-lg font-semibold text-gray-900">{{ (plan.planned_audits || []).length }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-500">Utilization</p>
                  <p class="text-lg font-semibold text-gray-900">{{ plan.utilization_percentage || 0 }}%</p>
                </div>
                <div>
                  <p class="text-xs text-gray-500">Days Planned</p>
                  <p class="text-lg font-semibold text-gray-900">{{ plan.total_planned_days || 0 }}</p>
                </div>
              </div>
              <div class="flex items-center justify-end space-x-2">
                <Button variant="outline" size="sm" @click="viewPlan(plan)">View</Button>
                <Button variant="outline" size="sm" @click="openEditForm(plan)">Edit</Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredPlans.length === 0 && annualPlans.length === 0" class="px-6 py-20 text-center">
        <div class="mx-auto h-20 w-20 rounded-2xl bg-blue-50 border-2 border-blue-100 flex items-center justify-center mb-8 shadow-sm">
          <CalendarIcon class="h-10 w-10 text-blue-500" />
        </div>
        <div class="max-w-md mx-auto">
          <h3 class="text-2xl font-bold text-gray-900 mb-3">Welcome to Annual Planning</h3>
          <p class="text-gray-600 mb-8 leading-relaxed">
            Create comprehensive annual audit plans. Set up your audit universe, allocate resources, and track planned activities.
          </p>
          <div class="flex flex-col sm:flex-row justify-center gap-3">
            <Button variant="solid" theme="blue" size="lg" @click="openCreateForm">
              <template #prefix><PlusIcon class="h-5 w-5" /></template>
              Create Your First Plan
            </Button>
            <Button variant="outline" size="lg" @click="showTemplateModal = true">
              <template #prefix><FileTextIcon class="h-5 w-5" /></template>
              Browse Templates
            </Button>
          </div>
        </div>
      </div>

      <!-- No Results State -->
      <div v-else-if="filteredPlans.length === 0" class="px-6 py-12 text-center">
        <SearchIcon class="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No plans found</h3>
        <p class="text-gray-600 mb-6">
          Try adjusting your search or filter criteria.
        </p>
        <Button variant="outline" @click="clearFilters">Clear Filters</Button>
      </div>
    </div>

    <!-- Annual Plan Form Modal -->
    <AnnualPlanForm
      v-model:show="showFormModal"
      :plan="selectedPlan"
      :mode="formMode"
      @saved="handleFormSaved"
      @close="handleFormClose"
    />

    <!-- Template Modal -->
    <Dialog v-model="showTemplateModal" :options="{ title: 'Plan Templates', size: 'lg' }">
      <template #body>
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="template in planTemplates"
            :key="template.id"
            class="border border-gray-200 rounded-lg p-4 hover:border-blue-500 hover:bg-blue-50 cursor-pointer transition-all"
            @click="applyTemplate(template)"
          >
            <div class="flex items-start space-x-3">
              <div class="p-2 bg-blue-100 rounded-lg">
                <component :is="template.icon" class="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h4 class="font-semibold text-gray-900">{{ template.name }}</h4>
                <p class="text-sm text-gray-500 mt-1">{{ template.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Bulk Actions Modal -->
    <Dialog v-model="showBulkModal" :options="{ title: 'Bulk Actions', size: 'md' }">
      <template #body>
        <div class="p-6 space-y-4">
          <p class="text-gray-600">{{ selectedPlans.length }} plan(s) selected</p>
          <div class="grid grid-cols-2 gap-3">
            <Button variant="outline" @click="bulkUpdateStatus">
              <template #prefix><RefreshCwIcon class="h-4 w-4" /></template>
              Update Status
            </Button>
            <Button variant="outline" @click="bulkExport">
              <template #prefix><DownloadIcon class="h-4 w-4" /></template>
              Export Selected
            </Button>
            <Button variant="outline" @click="bulkDuplicate">
              <template #prefix><CopyIcon class="h-4 w-4" /></template>
              Duplicate
            </Button>
            <Button variant="outline" theme="red" @click="bulkDelete">
              <template #prefix><TrashIcon class="h-4 w-4" /></template>
              Delete Selected
            </Button>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Capacity Planning Modal -->
    <Dialog v-model="showCapacityModal" :options="{ title: 'Capacity Planning', size: 'xl' }">
      <template #body>
        <div class="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="md:col-span-2">
            <div class="bg-white border border-gray-200 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Resource Allocation Overview</h3>
              <div class="space-y-4">
                <div v-for="resource in capacityData" :key="resource.name" class="flex items-center">
                  <div class="w-32 text-sm text-gray-600">{{ resource.name }}</div>
                  <div class="flex-1 mx-3">
                    <div class="w-full bg-gray-100 rounded-full h-4">
                      <div
                        class="h-4 rounded-full transition-all duration-300"
                        :class="resource.utilization > 90 ? 'bg-red-500' : resource.utilization > 75 ? 'bg-amber-500' : 'bg-green-500'"
                        :style="{ width: `${resource.utilization}%` }"
                      ></div>
                    </div>
                  </div>
                  <div class="w-16 text-sm font-medium text-gray-900 text-right">{{ resource.utilization }}%</div>
                </div>
              </div>
            </div>
          </div>
          <div class="space-y-4">
            <div class="bg-blue-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-blue-900 mb-4">Summary</h3>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between">
                  <span class="text-blue-700">Total Capacity</span>
                  <span class="font-medium text-blue-900">{{ totalCapacity }} days</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-blue-700">Allocated</span>
                  <span class="font-medium text-blue-900">{{ allocatedCapacity }} days</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-blue-700">Available</span>
                  <span class="font-medium text-blue-900">{{ totalCapacity - allocatedCapacity }} days</span>
                </div>
              </div>
            </div>
            <div class="bg-amber-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-amber-900 mb-4">Insights</h3>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between">
                  <span class="text-amber-700">Active Plans</span>
                  <span class="font-medium text-amber-900">{{ planStats.active }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-amber-700">Upcoming Audits</span>
                  <span class="font-medium text-amber-900">{{ planStats.upcoming }}</span>
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  CalendarIcon,
  DownloadIcon,
  FileTextIcon,
  BarChart3Icon,
  RefreshCwIcon,
  PlusIcon,
  ArrowUpDownIcon,
  EyeIcon,
  EditIcon,
  CopyIcon,
  TrashIcon,
  SearchIcon,
  LayersIcon,
  ClipboardListIcon,
  BuildingIcon,
  ShieldCheckIcon,
} from 'lucide-vue-next'

// Import components
import PlanStats from '@/components/annualplan/PlanStats.vue'
import PlanFilters from '@/components/annualplan/PlanFilters.vue'
import AnnualPlanForm from '@/components/annualplan/AnnualPlanForm.vue'

// Store
import { useAuditStore } from '@/stores/audit'

const router = useRouter()
const auditStore = useAuditStore()

// State
const loading = ref(false)
const exporting = ref(false)
const showFormModal = ref(false)
const showTemplateModal = ref(false)
const showBulkModal = ref(false)
const showCapacityModal = ref(false)
const showStatsDetails = ref(true)
const selectedPlan = ref(null)
const formMode = ref('create')

// Filter state
const searchQuery = ref('')
const statusFilter = ref('')
const yearFilter = ref('')
const periodFilter = ref('')
const viewMode = ref('table')
const selectedPlans = ref([])
const sortField = ref('plan_year')
const sortDirection = ref('desc')

// Computed
const annualPlans = computed(() => auditStore.annualPlans || [])

const planStats = computed(() => {
  const plans = annualPlans.value
  const active = plans.filter(p => p.status === 'Active').length
  const draft = plans.filter(p => p.status === 'Draft').length
  const approved = plans.filter(p => p.status === 'Approved').length
  const completed = plans.filter(p => p.status === 'Completed').length
  
  const plannedAudits = plans.reduce((sum, p) => sum + (p.planned_audits?.length || 0), 0)
  const totalDays = plans.reduce((sum, p) => sum + (p.total_planned_days || 0), 0)
  
  const activePlans = plans.filter(p => ['Active', 'Approved'].includes(p.status))
  const avgUtilization = activePlans.length > 0
    ? Math.round(activePlans.reduce((sum, p) => sum + (p.utilization_percentage || 0), 0) / activePlans.length)
    : 0

  // Count upcoming audits (next 30 days)
  const today = new Date()
  const thirtyDaysLater = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000)
  let upcoming = 0
  plans.forEach(plan => {
    (plan.planned_audits || []).forEach(audit => {
      if (audit.planned_start_date) {
        const startDate = new Date(audit.planned_start_date)
        if (startDate >= today && startDate <= thirtyDaysLater) {
          upcoming++
        }
      }
    })
  })

  return {
    total: plans.length,
    active,
    draft,
    approved,
    completed,
    plannedAudits,
    avgUtilization,
    upcoming,
    totalDays,
    byQuarter: { q1: 0, q2: 0, q3: 0, q4: 0 },
  }
})

const filteredPlans = computed(() => {
  let filtered = [...annualPlans.value]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(plan =>
      plan.plan_id?.toLowerCase().includes(query) ||
      plan.status?.toLowerCase().includes(query) ||
      plan.plan_objectives?.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(plan => plan.status === statusFilter.value)
  }

  if (yearFilter.value) {
    filtered = filtered.filter(plan => plan.plan_year?.toString() === yearFilter.value.toString())
  }

  if (periodFilter.value) {
    filtered = filtered.filter(plan => plan.plan_period === periodFilter.value)
  }

  filtered.sort((a, b) => {
    const aVal = a[sortField.value] || ''
    const bVal = b[sortField.value] || ''
    if (sortDirection.value === 'asc') {
      return aVal > bVal ? 1 : -1
    }
    return aVal < bVal ? 1 : -1
  })

  return filtered
})

// Capacity data
const capacityData = computed(() => {
  return [
    { name: 'Financial Audits', utilization: 78 },
    { name: 'Operational Audits', utilization: 65 },
    { name: 'Compliance Audits', utilization: 82 },
    { name: 'IT Audits', utilization: 45 },
    { name: 'Special Reviews', utilization: 30 },
  ]
})

const totalCapacity = computed(() => {
  return annualPlans.value.reduce((sum, p) => sum + (p.total_available_days || 0), 0) || 1000
})

const allocatedCapacity = computed(() => {
  return annualPlans.value.reduce((sum, p) => sum + (p.total_planned_days || 0), 0)
})

// Plan templates
const planTemplates = [
  {
    id: 'standard',
    name: 'Standard Annual Plan',
    description: 'Comprehensive annual audit plan template',
    icon: CalendarIcon,
  },
  {
    id: 'financial',
    name: 'Financial Focus',
    description: 'Emphasis on financial audits and controls',
    icon: ClipboardListIcon,
  },
  {
    id: 'compliance',
    name: 'Compliance-Driven',
    description: 'Focus on regulatory compliance audits',
    icon: ShieldCheckIcon,
  },
  {
    id: 'operational',
    name: 'Operational Excellence',
    description: 'Emphasis on operational efficiency audits',
    icon: BuildingIcon,
  },
]

// Methods
const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      auditStore.fetchAnnualPlans(),
      auditStore.fetchAuditUniverse(),
    ])
  } finally {
    loading.value = false
  }
}

const openCreateForm = () => {
  selectedPlan.value = null
  formMode.value = 'create'
  showFormModal.value = true
}

const openEditForm = async (plan) => {
  selectedPlan.value = plan
  formMode.value = 'edit'
  showFormModal.value = true
}

const viewPlan = (plan) => {
  router.push(`/audit-planning/annual-plan/${plan.name}`)
}

const duplicatePlan = async (plan) => {
  try {
    const planDetails = await auditStore.fetchAnnualPlanDetails(plan.name)
    if (planDetails) {
      selectedPlan.value = {
        ...planDetails,
        plan_id: `${planDetails.plan_id}_copy`,
        status: 'Draft',
        name: null,
      }
      formMode.value = 'create'
      showFormModal.value = true
    }
  } catch (error) {
    console.error('Error duplicating plan:', error)
  }
}

const deletePlan = async (plan) => {
  if (confirm(`Are you sure you want to delete ${plan.plan_id}?`)) {
    try {
      await auditStore.deleteAnnualPlan(plan.name)
      await refreshData()
    } catch (error) {
      console.error('Error deleting plan:', error)
    }
  }
}

const handleFormSaved = async () => {
  showFormModal.value = false
  selectedPlan.value = null
  await refreshData()
}

const handleFormClose = () => {
  showFormModal.value = false
  selectedPlan.value = null
}

const applyTemplate = (template) => {
  selectedPlan.value = { template: template.id }
  formMode.value = 'create'
  showTemplateModal.value = false
  showFormModal.value = true
}

// Utility methods
const getStatusVariant = (status) => {
  const variants = {
    'Draft': 'subtle',
    'Pending Approval': 'warning',
    'Approved': 'success',
    'Active': 'info',
    'Completed': 'success',
    'Cancelled': 'subtle',
  }
  return variants[status] || 'subtle'
}

const getPlanProgress = (plan) => {
  return Math.min(plan.utilization_percentage || 0, 100)
}

const getUtilizationColor = (utilization) => {
  if (utilization >= 90) return 'bg-red-500'
  if (utilization >= 75) return 'bg-amber-500'
  if (utilization >= 50) return 'bg-green-500'
  return 'bg-blue-500'
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
const togglePlanSelection = (planName) => {
  const index = selectedPlans.value.indexOf(planName)
  if (index > -1) {
    selectedPlans.value.splice(index, 1)
  } else {
    selectedPlans.value.push(planName)
  }
}

const selectAllPlans = () => {
  if (selectedPlans.value.length === filteredPlans.value.length) {
    selectedPlans.value = []
  } else {
    selectedPlans.value = filteredPlans.value.map(plan => plan.name)
  }
}

const sortBy = (field) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  yearFilter.value = ''
  periodFilter.value = ''
  selectedPlans.value = []
}

// Export & Bulk actions
const exportPlans = async () => {
  exporting.value = true
  try {
    console.log('Exporting plans...', selectedPlans.value.length || filteredPlans.value.length, 'plans')
  } finally {
    exporting.value = false
  }
}

const bulkUpdateStatus = () => {
  console.log('Bulk update status for:', selectedPlans.value)
  showBulkModal.value = false
}

const bulkExport = () => {
  console.log('Bulk export for:', selectedPlans.value)
  showBulkModal.value = false
}

const bulkDuplicate = () => {
  console.log('Bulk duplicate for:', selectedPlans.value)
  showBulkModal.value = false
}

const bulkDelete = () => {
  if (confirm(`Are you sure you want to delete ${selectedPlans.value.length} plan(s)?`)) {
    console.log('Bulk delete for:', selectedPlans.value)
    showBulkModal.value = false
    selectedPlans.value = []
  }
}

// Lifecycle
onMounted(async () => {
  await refreshData()
})
</script>
