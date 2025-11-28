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
            {{ isEdit ? 'Edit Variance Case' : 'New Variance Case' }}
          </h1>
          <p class="text-gray-500 mt-1">
            {{ isEdit ? `Editing ${route.params.id}` : 'Create a new inventory variance case' }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="solid" @click="saveCase" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          {{ isEdit ? 'Save Changes' : 'Create Case' }}
        </Button>
      </div>
    </div>

    <!-- Form -->
    <div class="max-w-4xl">
      <div class="space-y-6">
        <!-- Item Information -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Item Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Item Code <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="autocomplete"
                v-model="form.item_code"
                :options="itemOptions"
                placeholder="Select or search item"
                @change="onItemChange"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Item Name</label>
              <FormControl
                type="text"
                v-model="form.item_name"
                placeholder="Item name"
                :readonly="true"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Warehouse</label>
              <FormControl
                type="autocomplete"
                v-model="form.warehouse"
                :options="warehouseOptions"
                placeholder="Select warehouse"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Branch</label>
              <FormControl
                type="text"
                v-model="form.branch"
                placeholder="Branch location"
              />
            </div>
          </div>
        </div>

        <!-- Variance Details -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Variance Details</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                System Qty <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="number"
                v-model="form.system_qty"
                placeholder="0"
                @input="calculateVariance"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Counted Qty <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="number"
                v-model="form.counted_qty"
                placeholder="0"
                @input="calculateVariance"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Variance Qty</label>
              <div :class="['p-2 rounded-lg font-medium text-center', varianceQtyClass]">
                {{ form.variance_qty > 0 ? '+' : '' }}{{ form.variance_qty || 0 }}
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Unit Cost</label>
              <FormControl
                type="number"
                v-model="form.unit_cost"
                placeholder="0.00"
                @input="calculateVariance"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Variance Value</label>
              <div :class="['p-2 rounded-lg font-medium text-center', varianceQtyClass]">
                {{ formatCurrency(form.variance_value) }}
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">UOM</label>
              <FormControl
                type="text"
                v-model="form.uom"
                placeholder="e.g., Nos, Kg"
              />
            </div>
          </div>
        </div>

        <!-- Classification -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Classification</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <FormControl
                type="select"
                v-model="form.status"
                :options="statusOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <FormControl
                type="select"
                v-model="form.priority"
                :options="priorityOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <FormControl
                type="select"
                v-model="form.category"
                :options="categoryOptions"
              />
            </div>
          </div>
        </div>

        <!-- Linked Documents -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Linked Documents</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Stock Take Session</label>
              <FormControl
                type="autocomplete"
                v-model="form.stock_take_session"
                :options="sessionOptions"
                placeholder="Link to session"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Audit Plan</label>
              <FormControl
                type="autocomplete"
                v-model="form.audit_plan"
                :options="auditPlanOptions"
                placeholder="Link to audit plan"
              />
            </div>
          </div>
        </div>

        <!-- Investigation Assignment -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Investigation Assignment</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Assigned To</label>
              <FormControl
                type="autocomplete"
                v-model="form.assigned_to"
                :options="userOptions"
                placeholder="Assign investigator"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
              <FormControl
                type="date"
                v-model="form.due_date"
              />
            </div>
          </div>
        </div>

        <!-- Investigation Details (for editing) -->
        <div v-if="isEdit" class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Investigation Details</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Root Cause</label>
              <FormControl
                type="select"
                v-model="form.root_cause"
                :options="rootCauseOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Investigation Notes</label>
              <FormControl
                type="textarea"
                v-model="form.investigation_notes"
                placeholder="Document investigation findings..."
                :rows="4"
              />
            </div>
          </div>
        </div>

        <!-- Resolution (for editing resolved cases) -->
        <div v-if="isEdit && (form.status === 'Resolved' || form.status === 'Written Off')" class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Resolution</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Resolution Type</label>
              <FormControl
                type="select"
                v-model="form.resolution_type"
                :options="resolutionTypeOptions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Resolved Date</label>
              <FormControl
                type="date"
                v-model="form.resolved_date"
              />
            </div>

            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Resolution Notes</label>
              <FormControl
                type="textarea"
                v-model="form.resolution_notes"
                placeholder="Document resolution details..."
                :rows="3"
              />
            </div>
          </div>
        </div>

        <!-- Notes -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Additional Notes</h3>
          <FormControl
            type="textarea"
            v-model="form.notes"
            placeholder="Any additional notes..."
            :rows="3"
          />
        </div>
      </div>

      <!-- Form Actions (Bottom) -->
      <div class="flex items-center justify-end gap-3 mt-6 pt-6 border-t">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="solid" @click="saveCase" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          {{ isEdit ? 'Save Changes' : 'Create Case' }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, FormControl } from 'frappe-ui'
import { call } from 'frappe-ui'
import { ArrowLeft, Save } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const saving = ref(false)
const userOptions = ref([])
const itemOptions = ref([])
const warehouseOptions = ref([])
const sessionOptions = ref([])
const auditPlanOptions = ref([])

const isEdit = computed(() => route.params.id && route.params.id !== 'new')

const form = ref({
  item_code: '',
  item_name: '',
  warehouse: '',
  branch: '',
  system_qty: 0,
  counted_qty: 0,
  variance_qty: 0,
  unit_cost: 0,
  variance_value: 0,
  uom: 'Nos',
  status: 'Open',
  priority: 'Medium',
  category: '',
  stock_take_session: '',
  audit_plan: '',
  assigned_to: '',
  due_date: '',
  root_cause: '',
  investigation_notes: '',
  resolution_type: '',
  resolved_date: '',
  resolution_notes: '',
  notes: ''
})

const varianceQtyClass = computed(() => {
  if (form.value.variance_qty === 0) return 'bg-gray-100 text-gray-700'
  return form.value.variance_qty < 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
})

onMounted(async () => {
  await Promise.all([
    loadUsers(),
    loadItems(),
    loadWarehouses(),
    loadSessions(),
    loadAuditPlans()
  ])
  
  if (isEdit.value) {
    await loadCase()
  }
  
  // Check for prefilled data from query params
  if (route.query.session) {
    form.value.stock_take_session = route.query.session
  }
  if (route.query.item_code) {
    form.value.item_code = route.query.item_code
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

async function loadItems() {
  try {
    const items = await call('frappe.client.get_list', {
      doctype: 'Item',
      fields: ['name', 'item_name', 'stock_uom', 'valuation_rate'],
      limit_page_length: 0
    })
    itemOptions.value = items.map(i => ({
      label: `${i.name} - ${i.item_name}`,
      value: i.name,
      item_name: i.item_name,
      uom: i.stock_uom,
      cost: i.valuation_rate
    }))
  } catch (error) {
    console.error('Error loading items:', error)
  }
}

async function loadWarehouses() {
  try {
    const warehouses = await call('frappe.client.get_list', {
      doctype: 'Warehouse',
      fields: ['name', 'warehouse_name'],
      limit_page_length: 0
    })
    warehouseOptions.value = warehouses.map(w => ({
      label: w.warehouse_name || w.name,
      value: w.name
    }))
  } catch (error) {
    console.error('Error loading warehouses:', error)
  }
}

async function loadSessions() {
  try {
    const sessions = await call('frappe.client.get_list', {
      doctype: 'Stock Take Session',
      fields: ['name', 'session_name', 'scheduled_date'],
      limit_page_length: 50,
      order_by: 'scheduled_date desc'
    })
    sessionOptions.value = sessions.map(s => ({
      label: s.session_name || s.name,
      value: s.name
    }))
  } catch (error) {
    console.error('Error loading sessions:', error)
  }
}

async function loadAuditPlans() {
  try {
    const plans = await call('frappe.client.get_list', {
      doctype: 'Inventory Audit Plan',
      filters: { status: ['in', ['Planned', 'In Progress']] },
      fields: ['name', 'plan_title'],
      limit_page_length: 0
    })
    auditPlanOptions.value = plans.map(p => ({
      label: p.plan_title || p.name,
      value: p.name
    }))
  } catch (error) {
    console.error('Error loading audit plans:', error)
  }
}

async function loadCase() {
  try {
    const doc = await call('frappe.client.get', {
      doctype: 'Inventory Variance Case',
      name: route.params.id
    })
    
    form.value = {
      item_code: doc.item_code || '',
      item_name: doc.item_name || '',
      warehouse: doc.warehouse || '',
      branch: doc.branch || '',
      system_qty: doc.system_qty || 0,
      counted_qty: doc.counted_qty || 0,
      variance_qty: doc.variance_qty || 0,
      unit_cost: doc.unit_cost || 0,
      variance_value: doc.variance_value || 0,
      uom: doc.uom || 'Nos',
      status: doc.status || 'Open',
      priority: doc.priority || 'Medium',
      category: doc.category || '',
      stock_take_session: doc.stock_take_session || '',
      audit_plan: doc.audit_plan || '',
      assigned_to: doc.assigned_to || '',
      due_date: doc.due_date || '',
      root_cause: doc.root_cause || '',
      investigation_notes: doc.investigation_notes || '',
      resolution_type: doc.resolution_type || '',
      resolved_date: doc.resolved_date || '',
      resolution_notes: doc.resolution_notes || '',
      notes: doc.notes || ''
    }
  } catch (error) {
    console.error('Error loading case:', error)
  }
}

function onItemChange(value) {
  const item = itemOptions.value.find(i => i.value === value)
  if (item) {
    form.value.item_name = item.item_name
    form.value.uom = item.uom || 'Nos'
    form.value.unit_cost = item.cost || 0
    calculateVariance()
  }
}

function calculateVariance() {
  form.value.variance_qty = (form.value.counted_qty || 0) - (form.value.system_qty || 0)
  form.value.variance_value = form.value.variance_qty * (form.value.unit_cost || 0)
  
  // Auto-set priority based on variance value
  const absValue = Math.abs(form.value.variance_value)
  if (absValue > 100000) {
    form.value.priority = 'Critical'
  } else if (absValue > 50000) {
    form.value.priority = 'High'
  } else if (absValue > 10000) {
    form.value.priority = 'Medium'
  } else {
    form.value.priority = 'Low'
  }
}

function formatCurrency(value) {
  if (value === null || value === undefined) return 'KES 0'
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES'
  }).format(value)
}

async function saveCase() {
  // Validate required fields
  if (!form.value.item_code) {
    alert('Item code is required')
    return
  }

  saving.value = true
  
  try {
    if (isEdit.value) {
      // Update existing
      await call('frappe.client.set_value', {
        doctype: 'Inventory Variance Case',
        name: route.params.id,
        fieldname: form.value
      })
      router.push(`/inventory-audit/variance-cases/${route.params.id}`)
    } else {
      // Create new
      const result = await call('frappe.client.insert', {
        doc: {
          doctype: 'Inventory Variance Case',
          ...form.value
        }
      })
      router.push(`/inventory-audit/variance-cases/${result.name}`)
    }
  } catch (error) {
    console.error('Error saving case:', error)
    alert('Error saving case: ' + error.message)
  } finally {
    saving.value = false
  }
}

function goBack() {
  if (isEdit.value) {
    router.push(`/inventory-audit/variance-cases/${route.params.id}`)
  } else {
    router.push('/inventory-audit/variance-cases')
  }
}

// Options
const statusOptions = [
  { label: 'Open', value: 'Open' },
  { label: 'Under Investigation', value: 'Under Investigation' },
  { label: 'Resolved', value: 'Resolved' },
  { label: 'Written Off', value: 'Written Off' },
  { label: 'Closed', value: 'Closed' }
]

const priorityOptions = [
  { label: 'Critical', value: 'Critical' },
  { label: 'High', value: 'High' },
  { label: 'Medium', value: 'Medium' },
  { label: 'Low', value: 'Low' }
]

const categoryOptions = [
  { label: 'Shortage', value: 'Shortage' },
  { label: 'Overage', value: 'Overage' },
  { label: 'Damaged', value: 'Damaged' },
  { label: 'Expired', value: 'Expired' },
  { label: 'Misplaced', value: 'Misplaced' },
  { label: 'Data Entry Error', value: 'Data Entry Error' },
  { label: 'Theft', value: 'Theft' },
  { label: 'Unknown', value: 'Unknown' }
]

const rootCauseOptions = [
  { label: 'Not Determined', value: '' },
  { label: 'Theft / Pilferage', value: 'Theft / Pilferage' },
  { label: 'Data Entry Error', value: 'Data Entry Error' },
  { label: 'Receiving Error', value: 'Receiving Error' },
  { label: 'Shipping Error', value: 'Shipping Error' },
  { label: 'Damage / Spoilage', value: 'Damage / Spoilage' },
  { label: 'Misplacement', value: 'Misplacement' },
  { label: 'System Error', value: 'System Error' },
  { label: 'Vendor Issue', value: 'Vendor Issue' },
  { label: 'Process Failure', value: 'Process Failure' },
  { label: 'Other', value: 'Other' }
]

const resolutionTypeOptions = [
  { label: 'Adjusted', value: 'Adjusted' },
  { label: 'Written Off', value: 'Written Off' },
  { label: 'No Action Required', value: 'No Action Required' },
  { label: 'Transferred', value: 'Transferred' },
  { label: 'Recovered', value: 'Recovered' }
]
</script>
