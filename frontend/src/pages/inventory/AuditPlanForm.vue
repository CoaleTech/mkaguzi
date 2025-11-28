<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <Button variant="ghost" @click="goBack">
          <ArrowLeft class="w-5 h-5" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">
            {{ isEdit ? 'Edit Audit Plan' : 'New Audit Plan' }}
          </h1>
          <p class="text-gray-500 mt-1">
            {{ isEdit ? `Editing ${route.params.id}` : 'Create a new inventory audit plan' }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="solid" @click="savePlan" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          {{ isEdit ? 'Save Changes' : 'Create Plan' }}
        </Button>
      </div>
    </div>

    <!-- Form -->
    <div class="max-w-4xl">
      <div class="space-y-6">
        <!-- Basic Information -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Plan Title <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="text"
                v-model="form.plan_title"
                placeholder="e.g., Q4 2025 Warehouse A Cycle Count"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Audit Period <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="select"
                v-model="form.audit_period"
                :options="periodOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Audit Scope <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="select"
                v-model="form.audit_scope"
                :options="scopeOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <FormControl
                type="select"
                v-model="form.status"
                :options="statusOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Audit Year</label>
              <FormControl
                type="number"
                v-model="form.audit_year"
                placeholder="2025"
              />
            </div>
          </div>
        </div>

        <!-- Location -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Location</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Branch</label>
              <FormControl
                type="text"
                v-model="form.branch"
                placeholder="e.g., Nairobi HQ"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Warehouse</label>
              <FormControl
                type="text"
                v-model="form.warehouse"
                placeholder="e.g., Main Warehouse"
              />
            </div>
          </div>
        </div>

        <!-- Lead Auditor & Sampling -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Audit Configuration</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Lead Auditor</label>
              <FormControl
                type="autocomplete"
                v-model="form.lead_auditor"
                :options="userOptions"
                placeholder="Select lead auditor"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Sampling Strategy</label>
              <FormControl
                type="select"
                v-model="form.sampling_strategy"
                :options="samplingOptions"
              />
            </div>
          </div>
        </div>

        <!-- Materiality Thresholds -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Materiality Thresholds</h3>
          <p class="text-sm text-gray-500 mb-4">
            Define thresholds for identifying material variances during stock takes.
          </p>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Materiality Type</label>
              <FormControl
                type="select"
                v-model="form.materiality_type"
                :options="materialityTypeOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Quantity Threshold</label>
              <FormControl
                type="number"
                v-model="form.materiality_threshold_qty"
                placeholder="0"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Amount Threshold (KES)</label>
              <FormControl
                type="number"
                v-model="form.materiality_threshold_amount"
                placeholder="0"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Percent Threshold (%)</label>
              <FormControl
                type="number"
                v-model="form.materiality_threshold_percent"
                placeholder="5"
              />
            </div>
          </div>
        </div>

        <!-- Timeline -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Planned Start Date</label>
              <FormControl
                type="date"
                v-model="form.planned_start_date"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Planned End Date</label>
              <FormControl
                type="date"
                v-model="form.planned_end_date"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">SLA Days</label>
              <FormControl
                type="number"
                v-model="form.sla_days"
                placeholder="e.g., 7"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">SLA Due Date</label>
              <FormControl
                type="date"
                v-model="form.sla_due_date"
              />
            </div>
          </div>
        </div>

        <!-- Team Members -->
        <div class="bg-white rounded-lg border p-6">
          <TeamMemberTable
            v-model="form.team_members"
            title="Audit Team Members"
          />
        </div>

        <!-- Notes -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Notes</h3>
          <FormControl
            type="textarea"
            v-model="form.notes"
            placeholder="Additional notes or instructions for this audit plan..."
            :rows="4"
          />
        </div>
      </div>

      <!-- Form Actions (Bottom) -->
      <div class="flex items-center justify-end gap-3 mt-6 pt-6 border-t">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="solid" @click="savePlan" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          {{ isEdit ? 'Save Changes' : 'Create Plan' }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, FormControl } from 'frappe-ui'
import { call } from 'frappe-ui'
import { ArrowLeft, Save } from 'lucide-vue-next'
import { TeamMemberTable } from '@/components/inventory-audit'
import { useInventoryAuditStore } from '@/stores/useInventoryAuditStore'

const route = useRoute()
const router = useRouter()
const store = useInventoryAuditStore()

const saving = ref(false)
const userOptions = ref([])

const isEdit = computed(() => route.params.id && route.params.id !== 'new')

const form = ref({
  plan_title: '',
  status: 'Planned',
  audit_period: 'Monthly',
  audit_scope: 'Cycle Count',
  audit_year: new Date().getFullYear(),
  branch: '',
  warehouse: '',
  lead_auditor: '',
  sampling_strategy: '',
  materiality_type: 'Combined',
  materiality_threshold_qty: 0,
  materiality_threshold_amount: 0,
  materiality_threshold_percent: 5,
  planned_start_date: '',
  planned_end_date: '',
  sla_days: 7,
  sla_due_date: '',
  team_members: [],
  notes: ''
})

onMounted(async () => {
  await loadUsers()
  if (isEdit.value) {
    await loadPlan()
  }
})

async function loadUsers() {
  try {
    const users = await call('frappe.client.get_list', {
      doctype: 'User',
      filters: { enabled: 1, user_type: 'System User' },
      fields: ['name', 'full_name'],
      limit_page_length: 0
    })
    userOptions.value = users.map(u => ({
      label: u.full_name || u.name,
      value: u.name
    }))
  } catch (error) {
    console.error('Error loading users:', error)
  }
}

async function loadPlan() {
  try {
    const plan = await call('frappe.client.get', {
      doctype: 'Inventory Audit Plan',
      name: route.params.id
    })
    
    form.value = {
      plan_title: plan.plan_title || '',
      status: plan.status || 'Planned',
      audit_period: plan.audit_period || 'Monthly',
      audit_scope: plan.audit_scope || 'Cycle Count',
      audit_year: plan.audit_year || new Date().getFullYear(),
      branch: plan.branch || '',
      warehouse: plan.warehouse || '',
      lead_auditor: plan.lead_auditor || '',
      sampling_strategy: plan.sampling_strategy || '',
      materiality_type: plan.materiality_type || 'Combined',
      materiality_threshold_qty: plan.materiality_threshold_qty || 0,
      materiality_threshold_amount: plan.materiality_threshold_amount || 0,
      materiality_threshold_percent: plan.materiality_threshold_percent || 5,
      planned_start_date: plan.planned_start_date || '',
      planned_end_date: plan.planned_end_date || '',
      sla_days: plan.sla_days || 7,
      sla_due_date: plan.sla_due_date || '',
      team_members: plan.team_members || [],
      notes: plan.notes || ''
    }
  } catch (error) {
    console.error('Error loading plan:', error)
  }
}

async function savePlan() {
  // Validate required fields
  if (!form.value.plan_title) {
    alert('Plan title is required')
    return
  }
  if (!form.value.audit_period) {
    alert('Audit period is required')
    return
  }
  if (!form.value.audit_scope) {
    alert('Audit scope is required')
    return
  }

  saving.value = true
  
  try {
    if (isEdit.value) {
      // Update existing
      await call('frappe.client.set_value', {
        doctype: 'Inventory Audit Plan',
        name: route.params.id,
        fieldname: form.value
      })
      router.push(`/inventory-audit/plans/${route.params.id}`)
    } else {
      // Create new
      const result = await call('frappe.client.insert', {
        doc: {
          doctype: 'Inventory Audit Plan',
          ...form.value
        }
      })
      router.push(`/inventory-audit/plans/${result.name}`)
    }
  } catch (error) {
    console.error('Error saving plan:', error)
    alert('Error saving plan: ' + error.message)
  } finally {
    saving.value = false
  }
}

function goBack() {
  if (isEdit.value) {
    router.push(`/inventory-audit/plans/${route.params.id}`)
  } else {
    router.push('/inventory-audit/plans')
  }
}

// Options
const statusOptions = [
  { label: 'Planned', value: 'Planned' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Closed', value: 'Closed' },
  { label: 'Cancelled', value: 'Cancelled' }
]

const periodOptions = [
  { label: 'Daily', value: 'Daily' },
  { label: 'Weekly', value: 'Weekly' },
  { label: 'Monthly', value: 'Monthly' },
  { label: 'Quarterly', value: 'Quarterly' },
  { label: 'Ad Hoc', value: 'Ad Hoc' }
]

const scopeOptions = [
  { label: 'Cycle Count', value: 'Cycle Count' },
  { label: 'Full Count', value: 'Full Count' },
  { label: 'Sales Returns', value: 'Sales Returns' },
  { label: 'Damaged Stock', value: 'Damaged Stock' },
  { label: 'GRN Audit', value: 'GRN Audit' },
  { label: 'Dispatch Audit', value: 'Dispatch Audit' }
]

const samplingOptions = [
  { label: 'ABC Analysis', value: 'ABC Analysis' },
  { label: 'Velocity Based', value: 'Velocity Based' },
  { label: 'Risk Based', value: 'Risk Based' },
  { label: 'Random', value: 'Random' },
  { label: 'Full Population', value: 'Full Population' }
]

const materialityTypeOptions = [
  { label: 'Quantity', value: 'Quantity' },
  { label: 'Amount', value: 'Amount' },
  { label: 'Percentage', value: 'Percentage' },
  { label: 'Combined', value: 'Combined' }
]
</script>
