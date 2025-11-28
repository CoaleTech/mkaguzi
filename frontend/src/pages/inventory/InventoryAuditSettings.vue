<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <Button variant="ghost" @click="goBack">
          <ArrowLeft class="w-5 h-5" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Inventory Audit Settings</h1>
          <p class="text-gray-500 mt-1">
            Configure inventory audit module preferences and warehouse management
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="resetToDefaults">
          <RotateCcw class="w-4 h-4 mr-2" />
          Reset to Defaults
        </Button>
        <Button variant="solid" @click="saveSettings" :loading="saving">
          <Save class="w-4 h-4 mr-2" />
          Save Settings
        </Button>
      </div>
    </div>

    <!-- Settings Tabs -->
    <div class="bg-white rounded-lg border border-gray-200 mb-6">
      <div class="border-b border-gray-200">
        <nav class="flex overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="[
              'px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
            @click="activeTab = tab.id"
          >
            <component :is="tab.icon" class="h-4 w-4 mr-2 inline" />
            {{ tab.name }}
          </button>
        </nav>
      </div>
    </div>

    <!-- Settings Form -->
    <div class="max-w-6xl">
      <div class="space-y-6">
        <!-- General Settings Tab -->
        <div v-if="activeTab === 'general'" class="space-y-6">
          <!-- General Settings -->
          <div class="bg-white rounded-lg border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Settings class="w-5 h-5 mr-2" />
              General Settings
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Auto Warehouse Creation</label>
                    <p class="text-sm text-gray-500">Automatically create warehouse records when importing stock data</p>
                  </div>
                  <Checkbox v-model="settings.enable_auto_warehouse_creation" />
                </div>

                <div v-if="settings.enable_auto_warehouse_creation">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Default Warehouse Type</label>
                  <FormControl
                    type="select"
                    v-model="settings.default_warehouse_type"
                    :options="warehouseTypeOptions"
                  />
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Auto Generate Warehouse Code</label>
                    <p class="text-sm text-gray-500">Automatically generate warehouse codes using prefix</p>
                  </div>
                  <Checkbox v-model="settings.auto_generate_warehouse_code" />
                </div>

                <div v-if="settings.auto_generate_warehouse_code">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Warehouse Code Prefix</label>
                  <FormControl
                    type="text"
                    v-model="settings.warehouse_code_prefix"
                    placeholder="WH-, ST-, etc."
                  />
                </div>
              </div>

              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Default Counting Method</label>
                  <FormControl
                    type="select"
                    v-model="settings.default_counting_method"
                    :options="countingMethodOptions"
                  />
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Allow Negative Variance</label>
                    <p class="text-sm text-gray-500">Allow negative variances in stock counts</p>
                  </div>
                  <Checkbox v-model="settings.allow_negative_variance" />
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Enable Batch Processing</label>
                    <p class="text-sm text-gray-500">Process stock items in batches for performance</p>
                  </div>
                  <Checkbox v-model="settings.enable_batch_processing" />
                </div>

                <div v-if="settings.enable_batch_processing">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Max Batch Size</label>
                  <FormControl
                    type="number"
                    v-model="settings.max_batch_size"
                    min="10"
                    max="1000"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Notification Settings Tab -->
        <div v-if="activeTab === 'notifications'" class="space-y-6">
          <!-- Notification Settings -->
          <div class="bg-white rounded-lg border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Bell class="w-5 h-5 mr-2" />
              Notification Settings
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Notify on Variance Threshold</label>
                    <p class="text-sm text-gray-500">Send notifications when variance exceeds threshold</p>
                  </div>
                  <Checkbox v-model="settings.notify_on_variance_threshold" />
                </div>

                <div v-if="settings.notify_on_variance_threshold">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Variance Notification Threshold (%)</label>
                  <FormControl
                    type="number"
                    v-model="settings.variance_notification_threshold"
                    min="0"
                    max="100"
                    step="0.1"
                  />
                </div>
              </div>

              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Notify Store Manager</label>
                    <p class="text-sm text-gray-500">Send notifications to store managers</p>
                  </div>
                  <Checkbox v-model="settings.notify_store_manager" />
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Notify HOD Inventory</label>
                    <p class="text-sm text-gray-500">Send notifications to HOD Inventory</p>
                  </div>
                  <Checkbox v-model="settings.notify_hod_inventory" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Approval Settings Tab -->
        <div v-if="activeTab === 'approvals'" class="space-y-6">
          <!-- Approval Settings -->
          <div class="bg-white rounded-lg border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <CheckCircle class="w-5 h-5 mr-2" />
              Approval Settings
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Require HOD Approval</label>
                    <p class="text-sm text-gray-500">Require HOD approval for stock take variances</p>
                  </div>
                  <Checkbox v-model="settings.require_hod_approval" />
                </div>

                <div v-if="settings.require_hod_approval">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Approval Workflow</label>
                  <FormControl
                    type="select"
                    v-model="settings.approval_workflow"
                    :options="approvalWorkflowOptions"
                  />
                </div>
              </div>

              <div class="space-y-4">
                <div v-if="settings.require_hod_approval" class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Auto Approve Below Threshold</label>
                    <p class="text-sm text-gray-500">Auto-approve variances below threshold</p>
                  </div>
                  <Checkbox v-model="settings.auto_approve_below_threshold" />
                </div>

                <div v-if="settings.require_hod_approval && settings.auto_approve_below_threshold">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Approval Threshold Amount</label>
                  <FormControl
                    type="number"
                    v-model="settings.approval_threshold_amount"
                    min="0"
                    step="0.01"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Audit Trail Settings Tab -->
        <div v-if="activeTab === 'audit'" class="space-y-6">
          <!-- Audit Trail Settings -->
          <div class="bg-white rounded-lg border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <FileText class="w-5 h-5 mr-2" />
              Audit Trail Settings
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Audit Retention Days</label>
                  <FormControl
                    type="number"
                    v-model="settings.audit_retention_days"
                    min="30"
                    max="3650"
                  />
                </div>

                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Enable Audit Trail</label>
                    <p class="text-sm text-gray-500">Enable detailed audit trail for all changes</p>
                  </div>
                  <Checkbox v-model="settings.enable_audit_trail" />
                </div>
              </div>

              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <div>
                    <label class="text-sm font-medium text-gray-700">Auto Archive Completed Audits</label>
                    <p class="text-sm text-gray-500">Automatically archive completed audits</p>
                  </div>
                  <Checkbox v-model="settings.auto_archive_completed_audits" />
                </div>

                <div v-if="settings.auto_archive_completed_audits">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Archive After Days</label>
                  <FormControl
                    type="number"
                    v-model="settings.archive_after_days"
                    min="1"
                    max="365"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Warehouse & Team Assignment Tab -->
        <div v-if="activeTab === 'warehouses'" class="space-y-6">
          <!-- Warehouse & Team Assignment -->
          <div class="bg-white rounded-lg border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Users class="w-5 h-5 mr-2" />
              Warehouse & Team Assignment
            </h3>
            <div class="space-y-6">
              <!-- Create Warehouse Section -->
              <div>
                <h4 class="text-md font-medium text-gray-900 mb-4">Create Warehouse</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Warehouse Code</label>
                    <FormControl
                      type="text"
                      v-model="newWarehouse.warehouse_code"
                      placeholder="WH-001"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Warehouse Name</label>
                    <FormControl
                      type="text"
                      v-model="newWarehouse.warehouse_name"
                      placeholder="Main Warehouse"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Warehouse Type</label>
                    <FormControl
                      type="select"
                      v-model="newWarehouse.warehouse_type"
                      :options="warehouseTypeOptions"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Branch</label>
                    <FormControl
                      type="text"
                      v-model="newWarehouse.branch"
                      placeholder="Main Branch"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">City</label>
                    <FormControl
                      type="text"
                      v-model="newWarehouse.city"
                      placeholder="Nairobi"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">County</label>
                    <FormControl
                      type="text"
                      v-model="newWarehouse.county"
                      placeholder="Nairobi"
                    />
                  </div>
                </div>
                <div class="mt-4">
                  <Button @click="createWarehouse" :loading="creatingWarehouse">
                    <Plus class="w-4 h-4 mr-2" />
                    Create Warehouse
                  </Button>
                </div>
              </div>

              <!-- Team Assignment Section -->
              <div class="border-t pt-6">
                <h4 class="text-md font-medium text-gray-900 mb-4">Assign Teams to Warehouses</h4>
                
                <!-- Existing Assignments -->
                <div class="mb-6">
                  <h5 class="text-sm font-medium text-gray-700 mb-3">Current Assignments</h5>
                  <div class="space-y-3">
                    <div
                      v-for="assignment in warehouseAssignments"
                      :key="assignment.warehouse"
                      class="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                    >
                      <div>
                        <p class="text-sm font-medium text-gray-900">{{ assignment.warehouse_name }}</p>
                        <p class="text-xs text-gray-500">{{ assignment.warehouse_code }} • {{ assignment.warehouse_type }}</p>
                      </div>
                      <div class="flex items-center space-x-2">
                        <Badge :variant="assignment.team_assigned ? 'success' : 'secondary'">
                          {{ assignment.team_assigned ? 'Assigned' : 'Unassigned' }}
                        </Badge>
                        <Button
                          variant="outline"
                          size="sm"
                          @click="manageTeamAssignment(assignment)"
                        >
                          {{ assignment.team_assigned ? 'Manage Team' : 'Assign Team' }}
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Create Team Assignment -->
                <div class="border-t pt-6">
                  <h5 class="text-sm font-medium text-gray-700 mb-3">Create New Team Assignment</h5>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Select Warehouse</label>
                      <FormControl
                        type="select"
                        v-model="newAssignment.warehouse"
                        :options="availableWarehouses"
                        placeholder="Choose warehouse"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Team Lead</label>
                      <FormControl
                        type="select"
                        v-model="newAssignment.team_lead"
                        :options="availableUsers"
                        placeholder="Select team lead"
                      />
                    </div>
                  </div>

                  <!-- Team Members -->
                  <div class="mt-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Team Members</label>
                    <div class="space-y-2">
                      <div
                        v-for="(member, index) in newAssignment.team_members"
                        :key="index"
                        class="flex items-center space-x-2"
                      >
                        <FormControl
                          type="select"
                          v-model="member.user"
                          :options="availableUsers"
                          placeholder="Select user"
                          class="flex-1"
                        />
                        <FormControl
                          type="select"
                          v-model="member.role"
                          :options="teamRoleOptions"
                          placeholder="Role"
                          class="w-32"
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          @click="removeTeamMember(index)"
                        >
                          <X class="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      @click="addTeamMember"
                      class="mt-2"
                    >
                      <Plus class="w-4 h-4 mr-2" />
                      Add Member
                    </Button>
                  </div>

                  <div class="mt-4">
                    <Button @click="createTeamAssignment" :loading="creatingAssignment">
                      <Users class="w-4 h-4 mr-2" />
                      Create Team Assignment
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { createResource } from "frappe-ui"
import {
  ArrowLeft,
  Bell,
  CheckCircle,
  FileText,
  List,
  Plus,
  RotateCcw,
  Save,
  Settings,
  Users,
  Warehouse,
  X,
} from "lucide-vue-next"
import { Button, Checkbox, Badge } from "frappe-ui"

// Router
const router = useRouter()

// Reactive state
const saving = ref(false)
const activeTab = ref('general')
const creatingWarehouse = ref(false)
const creatingAssignment = ref(false)

const settings = ref({
  // General Settings
  enable_auto_warehouse_creation: false,
  default_warehouse_type: "Store",
  auto_generate_warehouse_code: true,
  warehouse_code_prefix: "WH-",
  default_counting_method: "Manual Count",
  allow_negative_variance: false,
  enable_batch_processing: true,
  max_batch_size: 100,

  // Notification Settings
  notify_on_variance_threshold: true,
  variance_notification_threshold: 5.0,
  notify_store_manager: true,
  notify_hod_inventory: true,

  // Approval Settings
  require_hod_approval: true,
  approval_workflow: "Single Level",
  auto_approve_below_threshold: false,
  approval_threshold_amount: 0,

  // Audit Trail Settings
  audit_retention_days: 365,
  enable_audit_trail: true,
  auto_archive_completed_audits: true,
  archive_after_days: 90,
})

// Tabs configuration
const tabs = [
  { id: 'general', name: 'General', icon: Settings },
  { id: 'notifications', name: 'Notifications', icon: Bell },
  { id: 'approvals', name: 'Approvals', icon: CheckCircle },
  { id: 'audit', name: 'Audit Trail', icon: FileText },
  { id: 'warehouses', name: 'Warehouses & Teams', icon: Users },
]

// Warehouse creation state
const newWarehouse = ref({
  warehouse_code: '',
  warehouse_name: '',
  warehouse_type: 'Store',
  branch: '',
  city: '',
  county: '',
})

// Team assignment state
const newAssignment = ref({
  warehouse: '',
  team_lead: '',
  team_members: [],
})

const warehouseAssignments = ref([])
const availableWarehouses = ref([])
const availableUsers = ref([])

// Options
const warehouseTypeOptions = [
  { label: "Store", value: "Store" },
  { label: "Warehouse", value: "Warehouse" },
  { label: "Distribution Center", value: "Distribution Center" },
  { label: "Returns Center", value: "Returns Center" },
]

const countingMethodOptions = [
  { label: "Manual Count", value: "Manual Count" },
  { label: "Barcode Scan", value: "Barcode Scan" },
  { label: "RFID", value: "RFID" },
  { label: "System Integration", value: "System Integration" },
]

const approvalWorkflowOptions = [
  { label: "Single Level", value: "Single Level" },
  { label: "Multi Level", value: "Multi Level" },
]

const teamRoleOptions = [
  { label: "Counter", value: "Counter" },
  { label: "Supervisor", value: "Supervisor" },
  { label: "Auditor", value: "Auditor" },
]

// Resources
const settingsResource = createResource({
  url: "/api/method/mkaguzi.inventory_audit.doctype.inventory_audit_settings.inventory_audit_settings.get_settings",
  auto: false,
})

const saveSettingsResource = createResource({
  url: "frappe.client.set_value",
  auto: false,
})

const createWarehouseResource = createResource({
  url: "/api/resource/Warehouse Master",
  auto: false,
})

const getWarehousesResource = createResource({
  url: "/api/resource/Warehouse Master",
  method: "GET",
  auto: false,
})

const getUsersResource = createResource({
  url: "/api/resource/User",
  method: "GET",
  auto: false,
})

const createWarehouseMethodResource = createResource({
  url: "/api/method/mkaguzi.inventory_audit.doctype.inventory_audit_settings.inventory_audit_settings.create_warehouse",
  auto: false,
})

const createSampleWarehouseResource = createResource({
  url: "/api/method/mkaguzi.inventory_audit.doctype.inventory_audit_settings.inventory_audit_settings.create_sample_warehouse",
  auto: false,
})

const createTeamAssignmentResource = createResource({
  url: "/api/method/mkaguzi.inventory_audit.doctype.inventory_audit_settings.inventory_audit_settings.create_team_assignment",
  auto: false,
})

// Methods
const goBack = () => {
  router.push("/inventory-audit")
}

const goToWarehouseList = () => {
  // This would navigate to warehouse list - for now just show a message
  alert("Warehouse list functionality would be implemented here")
}

const loadSettings = async () => {
  try {
    const settingsData = await settingsResource.fetch()

    if (settingsData) {
      Object.assign(settings.value, settingsData)
    }
  } catch (error) {
    console.error("Error loading settings:", error)
    // Settings don't exist yet, use defaults
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    await saveSettingsResource.fetch({
      doctype: "Inventory Audit Settings",
      name: "Inventory Audit Settings",
      fieldname: settings.value,
    })

    // Show success message
    alert("Settings saved successfully!")
  } catch (error) {
    console.error("Error saving settings:", error)
    alert("Error saving settings. Please try again.")
  } finally {
    saving.value = false
  }
}

const resetToDefaults = () => {
  if (confirm("Are you sure you want to reset all settings to defaults? This action cannot be undone.")) {
    // Reset to default values
    settings.value = {
      enable_auto_warehouse_creation: false,
      default_warehouse_type: "Store",
      auto_generate_warehouse_code: true,
      warehouse_code_prefix: "WH-",
      default_counting_method: "Manual Count",
      allow_negative_variance: false,
      enable_batch_processing: true,
      max_batch_size: 100,
      notify_on_variance_threshold: true,
      variance_notification_threshold: 5.0,
      notify_store_manager: true,
      notify_hod_inventory: true,
      require_hod_approval: true,
      approval_workflow: "Single Level",
      auto_approve_below_threshold: false,
      approval_threshold_amount: 0,
      audit_retention_days: 365,
      enable_audit_trail: true,
      auto_archive_completed_audits: true,
      archive_after_days: 90,
    }
  }
}

const createSampleWarehouse = async () => {
  try {
    const result = await createSampleWarehouseResource.fetch()

    if (result) {
      alert(`Sample warehouse created successfully!`)
      // Refresh warehouse list
      loadWarehouseData()
    }
  } catch (error) {
    console.error("Error creating sample warehouse:", error)
    alert("Error creating sample warehouse. Please try again.")
  }
}

// Warehouse and Team Methods
const createWarehouse = async () => {
  if (!newWarehouse.value.warehouse_code || !newWarehouse.value.warehouse_name) {
    alert("Please fill in warehouse code and name")
    return
  }

  creatingWarehouse.value = true
  try {
    const result = await createWarehouseMethodResource.fetch({
      warehouse_code: newWarehouse.value.warehouse_code,
      warehouse_name: newWarehouse.value.warehouse_name,
      warehouse_type: newWarehouse.value.warehouse_type,
      branch: newWarehouse.value.branch,
      city: newWarehouse.value.city,
      county: newWarehouse.value.county
    })

    if (result) {
      alert(`Warehouse '${newWarehouse.value.warehouse_code}' created successfully!`)
      // Reset form
      newWarehouse.value = {
        warehouse_code: '',
        warehouse_name: '',
        warehouse_type: 'Store',
        branch: '',
        city: '',
        county: '',
      }
      // Refresh warehouse list
      loadWarehouseData()
    }
  } catch (error) {
    console.error("Error creating warehouse:", error)
    // Extract the actual error message from Frappe's response
    const errorMessage = error?.exc_type === 'ValidationError' 
      ? error?.message 
      : (error?.message || error?._server_messages || "Error creating warehouse. Please try again.")
    
    // Try to parse server messages if available
    let displayMessage = errorMessage
    if (error?._server_messages) {
      try {
        const serverMessages = JSON.parse(error._server_messages)
        if (serverMessages.length > 0) {
          const parsed = JSON.parse(serverMessages[0])
          displayMessage = parsed.message || errorMessage
        }
      } catch (e) {
        // Use original error message
      }
    }
    
    alert(displayMessage)
  } finally {
    creatingWarehouse.value = false
  }
}

const addTeamMember = () => {
  newAssignment.value.team_members.push({ user: '', role: 'Counter' })
}

const removeTeamMember = (index) => {
  newAssignment.value.team_members.splice(index, 1)
}

const createTeamAssignment = async () => {
  if (!newAssignment.value.warehouse || !newAssignment.value.team_lead) {
    alert("Please select a warehouse and team lead")
    return
  }

  if (newAssignment.value.team_members.length === 0) {
    alert("Please add at least one team member")
    return
  }

  creatingAssignment.value = true
  try {
    const result = await createTeamAssignmentResource.fetch({
      warehouse: newAssignment.value.warehouse,
      team_lead: newAssignment.value.team_lead,
      team_members: JSON.stringify(newAssignment.value.team_members)
    })

    if (result) {
      alert("Team assignment created successfully!")
      // Reset form
      newAssignment.value = {
        warehouse: '',
        team_lead: '',
        team_members: [],
      }
      // Refresh assignments
      loadWarehouseData()
    }
  } catch (error) {
    console.error("Error creating team assignment:", error)
    alert("Error creating team assignment. Please try again.")
  } finally {
    creatingAssignment.value = false
  }
}

const manageTeamAssignment = (assignment) => {
  // This would open a modal or navigate to team management
  alert(`Team management for ${assignment.warehouse_name} would be implemented here`)
}

const loadWarehouseData = async () => {
  try {
    // Load available warehouses
    const warehousesResult = await getWarehousesResource.fetch({
      params: {
        fields: '["name","warehouse_name","warehouse_type"]',
        limit_page_length: 100,
      },
    })

    if (warehousesResult && warehousesResult.data) {
      availableWarehouses.value = warehousesResult.data.map(w => ({
        label: `${w.warehouse_name} (${w.name})`,
        value: w.name,
      }))
    }

    // Load available users
    const usersResult = await getUsersResource.fetch({
      params: {
        fields: '["name","full_name"]',
        filters: '[["enabled","=","1"]]',
        limit_page_length: 100,
      },
    })

    if (usersResult && usersResult.data) {
      availableUsers.value = usersResult.data.map(u => ({
        label: u.full_name || u.name,
        value: u.name,
      }))
    }

    // Load warehouse assignments (this would need a custom method)
    // For now, we'll simulate some data
    warehouseAssignments.value = [
      {
        warehouse: 'WH-001',
        warehouse_name: 'Main Warehouse',
        warehouse_code: 'WH-001',
        warehouse_type: 'Warehouse',
        team_assigned: true,
      },
      {
        warehouse: 'ST-001',
        warehouse_name: 'Store A',
        warehouse_code: 'ST-001',
        warehouse_type: 'Store',
        team_assigned: false,
      },
    ]
  } catch (error) {
    console.error("Error loading warehouse data:", error)
  }
}// Lifecycle
onMounted(() => {
  loadSettings()
  loadWarehouseData()
})
</script>