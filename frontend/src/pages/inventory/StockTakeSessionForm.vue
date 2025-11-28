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
            {{ isEdit ? 'Edit Session' : 'New Stock Take Session' }}
          </h1>
          <p class="text-gray-500 mt-1">
            {{ isEdit ? `Editing ${route.params.id}` : 'Create a new stock take session' }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="solid" @click="saveSession" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          {{ isEdit ? 'Save Changes' : 'Create Session' }}
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
                Session Name
              </label>
              <FormControl
                type="text"
                v-model="form.session_name"
                placeholder="e.g., Zone A Cycle Count - Week 48"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Session Type <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="select"
                v-model="form.session_type"
                :options="sessionTypeOptions"
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
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Linked Audit Plan
              </label>
              <FormControl
                type="autocomplete"
                v-model="form.audit_plan"
                :options="auditPlanOptions"
                placeholder="Select audit plan"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Scheduled Date <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="date"
                v-model="form.scheduled_date"
              />
            </div>
          </div>
        </div>

        <!-- Location -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Location</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
              <label class="block text-sm font-medium text-gray-700 mb-1">Zone</label>
              <FormControl
                type="text"
                v-model="form.zone"
                placeholder="e.g., Zone A"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Bin Location</label>
              <FormControl
                type="text"
                v-model="form.bin_location"
                placeholder="e.g., A-01-01"
              />
            </div>
          </div>
        </div>

        <!-- Assignment -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Assignment</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Assigned Counters</label>
              <FormControl
                type="text"
                v-model="form.assigned_counters"
                placeholder="e.g., John Doe, Jane Smith"
              />
              <p class="text-xs text-gray-500 mt-1">Comma-separated list of counter names</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Supervisor</label>
              <FormControl
                type="autocomplete"
                v-model="form.supervisor"
                :options="userOptions"
                placeholder="Select supervisor"
              />
            </div>
          </div>
        </div>

        <!-- Count Items -->
        <div class="bg-white rounded-lg border p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Items to Count</h3>
            <div class="flex items-center gap-2">
              <Button variant="outline" size="sm" @click="loadFromSnapshot">
                <Download class="w-4 h-4 mr-2" />
                Load from Snapshot
              </Button>
              <Button variant="outline" size="sm" @click="addItem">
                <Plus class="w-4 h-4 mr-2" />
                Add Item
              </Button>
            </div>
          </div>
          
          <PhysicalCountTable
            v-model="form.count_items"
            :readonly="false"
          />
        </div>

        <!-- Notes -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Notes</h3>
          <FormControl
            type="textarea"
            v-model="form.notes"
            placeholder="Additional notes or instructions for this session..."
            :rows="4"
          />
        </div>
      </div>

      <!-- Form Actions (Bottom) -->
      <div class="flex items-center justify-end gap-3 mt-6 pt-6 border-t">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button variant="outline" @click="saveAndAddAnother" :loading="saving">
          Save & Add Another
        </Button>
        <Button variant="solid" @click="saveSession" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          {{ isEdit ? 'Save Changes' : 'Create Session' }}
        </Button>
      </div>
    </div>

    <!-- Load from Snapshot Modal -->
    <Dialog v-model="showSnapshotModal" :options="{ title: 'Load Items from Snapshot' }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Select Snapshot</label>
            <FormControl
              type="autocomplete"
              v-model="selectedSnapshot"
              :options="snapshotOptions"
              placeholder="Search snapshots..."
            />
          </div>
          <div v-if="selectedSnapshot" class="p-4 bg-gray-50 rounded-lg">
            <p class="text-sm text-gray-600">
              This will load all items from the selected snapshot. Existing items will be replaced.
            </p>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showSnapshotModal = false">Cancel</Button>
        <Button variant="solid" @click="confirmLoadSnapshot" :disabled="!selectedSnapshot">
          Load Items
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, FormControl, Dialog } from 'frappe-ui'
import { call } from 'frappe-ui'
import { ArrowLeft, Save, Download, Plus } from 'lucide-vue-next'
import { PhysicalCountTable } from '@/components/inventory-audit'

const route = useRoute()
const router = useRouter()

const saving = ref(false)
const userOptions = ref([])
const auditPlanOptions = ref([])
const warehouseOptions = ref([])
const snapshotOptions = ref([])
const showSnapshotModal = ref(false)
const selectedSnapshot = ref('')

const isEdit = computed(() => route.params.id && route.params.id !== 'new')

const form = ref({
  session_name: '',
  session_type: 'Cycle Count',
  status: 'Scheduled',
  audit_plan: '',
  scheduled_date: new Date().toISOString().split('T')[0],
  warehouse: '',
  zone: '',
  bin_location: '',
  assigned_counters: '',
  supervisor: '',
  count_items: [],
  notes: ''
})

onMounted(async () => {
  await Promise.all([
    loadUsers(),
    loadAuditPlans(),
    loadWarehouses(),
    loadSnapshots()
  ])
  
  if (isEdit.value) {
    await loadSession()
  }
})

// Watch for audit plan selection to inherit warehouse
watch(() => form.value.audit_plan, async (newPlan) => {
  if (newPlan && !isEdit.value) {
    try {
      const plan = await call('frappe.client.get_value', {
        doctype: 'Inventory Audit Plan',
        filters: { name: newPlan },
        fieldname: ['warehouse']
      })
      if (plan.warehouse) {
        form.value.warehouse = plan.warehouse
      }
    } catch (error) {
      console.error('Error loading plan details:', error)
    }
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

async function loadSnapshots() {
  try {
    const snapshots = await call('frappe.client.get_list', {
      doctype: 'Inventory Snapshot',
      filters: { status: 'Active' },
      fields: ['name', 'snapshot_date', 'warehouse'],
      limit_page_length: 50,
      order_by: 'snapshot_date desc'
    })
    snapshotOptions.value = snapshots.map(s => ({
      label: `${s.name} - ${s.warehouse} (${s.snapshot_date})`,
      value: s.name
    }))
  } catch (error) {
    console.error('Error loading snapshots:', error)
  }
}

async function loadSession() {
  try {
    const session = await call('frappe.client.get', {
      doctype: 'Stock Take Session',
      name: route.params.id
    })
    
    form.value = {
      session_name: session.session_name || '',
      session_type: session.session_type || 'Cycle Count',
      status: session.status || 'Scheduled',
      audit_plan: session.audit_plan || '',
      scheduled_date: session.scheduled_date || '',
      warehouse: session.warehouse || '',
      zone: session.zone || '',
      bin_location: session.bin_location || '',
      assigned_counters: session.assigned_counters || '',
      supervisor: session.supervisor || '',
      count_items: session.count_items || [],
      notes: session.notes || ''
    }
  } catch (error) {
    console.error('Error loading session:', error)
  }
}

async function saveSession() {
  // Validate required fields
  if (!form.value.session_type) {
    alert('Session type is required')
    return
  }
  if (!form.value.scheduled_date) {
    alert('Scheduled date is required')
    return
  }

  saving.value = true
  
  try {
    if (isEdit.value) {
      // Update existing
      await call('frappe.client.set_value', {
        doctype: 'Stock Take Session',
        name: route.params.id,
        fieldname: form.value
      })
      router.push(`/inventory-audit/sessions/${route.params.id}`)
    } else {
      // Create new
      const result = await call('frappe.client.insert', {
        doc: {
          doctype: 'Stock Take Session',
          ...form.value
        }
      })
      router.push(`/inventory-audit/sessions/${result.name}`)
    }
  } catch (error) {
    console.error('Error saving session:', error)
    alert('Error saving session: ' + error.message)
  } finally {
    saving.value = false
  }
}

async function saveAndAddAnother() {
  if (!form.value.session_type || !form.value.scheduled_date) {
    alert('Session type and scheduled date are required')
    return
  }

  saving.value = true
  
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'Stock Take Session',
        ...form.value
      }
    })
    
    // Reset form for next entry
    form.value = {
      session_name: '',
      session_type: 'Cycle Count',
      status: 'Scheduled',
      audit_plan: form.value.audit_plan, // Keep the audit plan
      scheduled_date: form.value.scheduled_date, // Keep the date
      warehouse: form.value.warehouse, // Keep warehouse
      zone: '',
      bin_location: '',
      assigned_counters: '',
      supervisor: '',
      count_items: [],
      notes: ''
    }
  } catch (error) {
    console.error('Error saving session:', error)
    alert('Error saving session: ' + error.message)
  } finally {
    saving.value = false
  }
}

function addItem() {
  form.value.count_items.push({
    item_code: '',
    item_name: '',
    system_qty: 0,
    counted_qty: null,
    variance_qty: 0,
    variance_value: 0,
    uom: 'Nos',
    condition: 'Good',
    notes: ''
  })
}

function loadFromSnapshot() {
  showSnapshotModal.value = true
}

async function confirmLoadSnapshot() {
  if (!selectedSnapshot.value) return
  
  try {
    const snapshot = await call('frappe.client.get', {
      doctype: 'Inventory Snapshot',
      name: selectedSnapshot.value
    })
    
    if (snapshot.items && snapshot.items.length > 0) {
      form.value.count_items = snapshot.items.map(item => ({
        item_code: item.item_code,
        item_name: item.item_name,
        system_qty: item.qty || 0,
        counted_qty: null,
        variance_qty: 0,
        variance_value: 0,
        uom: item.uom || 'Nos',
        condition: 'Good',
        notes: ''
      }))
    }
    
    if (snapshot.warehouse) {
      form.value.warehouse = snapshot.warehouse
    }
    
    showSnapshotModal.value = false
    selectedSnapshot.value = ''
  } catch (error) {
    console.error('Error loading snapshot:', error)
    alert('Error loading snapshot: ' + error.message)
  }
}

function goBack() {
  if (isEdit.value) {
    router.push(`/inventory-audit/sessions/${route.params.id}`)
  } else {
    router.push('/inventory-audit/sessions')
  }
}

// Options
const sessionTypeOptions = [
  { label: 'Cycle Count', value: 'Cycle Count' },
  { label: 'Full Count', value: 'Full Count' },
  { label: 'Spot Check', value: 'Spot Check' },
  { label: 'Blind Count', value: 'Blind Count' },
  { label: 'Verification', value: 'Verification' }
]

const statusOptions = [
  { label: 'Scheduled', value: 'Scheduled' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Pending Review', value: 'Pending Review' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Cancelled', value: 'Cancelled' }
]
</script>
