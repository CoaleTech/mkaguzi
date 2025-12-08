<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <Button variant="ghost" @click="goBack" class="p-2">
          <ArrowLeft class="w-4 h-4" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ audit?.name || 'Loading...' }}</h1>
          <p class="text-gray-500 mt-1">
            {{ audit?.stock_take_type }} | {{ audit?.warehouse }} | {{ formatDate(audit?.audit_date) }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Badge :variant="statusVariant">{{ audit?.status }}</Badge>
        <AskAIButton contextType="stock-take" :contextData="getStockTakeContext()" />
        <div class="flex items-center gap-2 ml-auto">
          <Button variant="outline" @click="editAudit" v-if="canEdit">
            <Edit class="w-4 h-4 mr-2" />
            Edit
          </Button>
          <Button variant="outline" @click="printAuditReport">
            <Printer class="w-4 h-4 mr-2" />
            Print
          </Button>
          <Button variant="outline" size="sm" @click="exportToExcel">
            <Download class="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="audit" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Stock Take Preparation (for Draft status) -->
        <div v-if="audit.status === 'Draft'" class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Stock Take Preparation</h3>
          
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div class="flex items-start gap-3">
              <CheckCircle class="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 class="text-sm font-medium text-blue-900 mb-1">Stock Taker Tasks</h4>
                <ul class="text-sm text-blue-800 space-y-1">
                  <li>• Enter physical quantities for all items in the table below</li>
                  <li>• Upload the manager-signed physical stock take copy</li>
                  <li>• Review and verify all counts are accurate</li>
                  <li>• Submit for analyst review once everything is complete</li>
                </ul>
              </div>
            </div>
          </div>
          
          <!-- Signed Copy Upload -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Signed Stock Take Copy <span class="text-red-500">*</span>
              </label>
              <div class="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-blue-400 transition-colors">
                <div v-if="!audit.signed_stock_take_copy" class="space-y-2">
                  <Upload class="w-8 h-8 text-gray-400 mx-auto" />
                  <div>
                    <p class="text-sm text-gray-600">Upload the manager-signed physical stock take copy</p>
                    <p class="text-xs text-gray-500 mt-1">PDF, DOC, DOCX, JPG, PNG files accepted</p>
                  </div>
                  <input
                    type="file"
                    ref="fileInput"
                    @change="handleFileUpload"
                    accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                    class="hidden"
                  />
                  <Button variant="outline" size="sm" @click="$refs.fileInput.click()">
                    <Upload class="w-4 h-4 mr-2" />
                    Choose File
                  </Button>
                </div>
                <div v-else class="space-y-2">
                  <FileText class="w-8 h-8 text-green-500 mx-auto" />
                  <div>
                    <p class="text-sm font-medium text-green-700">Signed copy attached</p>
                    <p class="text-xs text-gray-500">{{ getFileName(audit.signed_stock_take_copy) }}</p>
                  </div>
                  <div class="flex gap-2 justify-center">
                    <Button variant="outline" size="sm" @click="viewAttachment(audit.signed_stock_take_copy)">
                      <Eye class="w-4 h-4 mr-2" />
                      View
                    </Button>
                    <Button variant="outline" size="sm" @click="removeAttachment">
                      <Trash2 class="w-4 h-4 mr-2" />
                      Remove
                    </Button>
                  </div>
                </div>
              </div>
              <p class="text-xs text-gray-500 mt-2">
                This signed document is required before submitting the physical count for review.
              </p>
            </div>

            <!-- Physical Count Status -->
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Physical Count Status</h4>
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">Items Counted:</span>
                  <span class="font-medium ml-2">{{ countedItems }} / {{ totalItems }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Ready to Submit:</span>
                  <span :class="canSubmitPhysicalCount ? 'text-green-600 font-medium' : 'text-red-600'" class="ml-2">
                    {{ canSubmitPhysicalCount ? 'Yes' : 'No' }}
                  </span>
                </div>
              </div>
              <div v-if="!canSubmitPhysicalCount" class="mt-2 text-xs text-red-600">
                <p v-if="!allItemsHavePhysicalQty">• All items must have physical quantities entered</p>
                <p v-if="!audit.signed_stock_take_copy">• Signed stock take copy must be attached</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Attached Physical Stock Take (for Analyst Review and HOD) -->
        <div v-if="audit.signed_stock_take_copy && (audit.status === 'Physical Count Submitted' || audit.status === 'Analyst Reviewed' || audit.status === 'HOD Approved')" class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Attached Physical Stock Take</h3>
          
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex items-center gap-4">
              <FileText class="w-8 h-8 text-blue-500 flex-shrink-0" />
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">Signed Stock Take Copy</p>
                <p class="text-xs text-gray-500">{{ getFileName(audit.signed_stock_take_copy) }}</p>
                <p class="text-xs text-gray-400 mt-1">Uploaded during physical count preparation</p>
              </div>
              <Button variant="outline" size="sm" @click="viewAttachment(audit.signed_stock_take_copy)">
                <Eye class="w-4 h-4 mr-2" />
                View Document
              </Button>
            </div>
          </div>
          
          <div class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p class="text-sm text-blue-800">
              <strong>Note:</strong> This is the original signed physical stock take document submitted by the stock taker. 
              Review this document to verify the authenticity and completeness of the physical count process.
            </p>
          </div>
        </div>

        <!-- Workflow Progress -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Approval Workflow</h3>
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
              <div :class="getStepClass(1)" class="w-10 h-10 rounded-full flex items-center justify-center">
                <span class="text-sm font-medium">1</span>
              </div>
              <div class="ml-2">
                <p class="text-sm font-medium">Analyst</p>
                <p class="text-xs text-gray-500">{{ audit.created_by || 'Not assigned' }}</p>
              </div>
            </div>
            <div class="flex-1 h-1 mx-4 bg-gray-200 rounded">
              <div :class="audit.status !== 'Draft' ? 'bg-green-500' : 'bg-gray-200'" class="h-full rounded" :style="{width: audit.status !== 'Draft' ? '100%' : '0%'}"></div>
            </div>
            <div class="flex items-center gap-2">
              <div :class="getStepClass(2)" class="w-10 h-10 rounded-full flex items-center justify-center">
                <span class="text-sm font-medium">2</span>
              </div>
              <div class="ml-2">
                <p class="text-sm font-medium">Stock Taker</p>
                <p class="text-xs text-gray-500">{{ audit.physical_count_submitted_by || 'Not assigned' }}</p>
              </div>
            </div>
            <div class="flex-1 h-1 mx-4 bg-gray-200 rounded">
              <div :class="audit.physical_count_submitted ? 'bg-green-500' : 'bg-gray-200'" class="h-full rounded" :style="{width: audit.physical_count_submitted ? '100%' : '0%'}"></div>
            </div>
            <div class="flex items-center gap-2">
              <div :class="getStepClass(3)" class="w-10 h-10 rounded-full flex items-center justify-center">
                <span class="text-sm font-medium">3</span>
              </div>
              <div class="ml-2">
                <p class="text-sm font-medium">Analyst Review</p>
                <p class="text-xs text-gray-500">{{ audit.stock_analyst || 'Not assigned' }}</p>
              </div>
            </div>
            <div class="flex-1 h-1 mx-4 bg-gray-200 rounded">
              <div :class="audit.analyst_reviewed ? 'bg-green-500' : 'bg-gray-200'" class="h-full rounded" :style="{width: audit.analyst_reviewed ? '100%' : '0%'}"></div>
            </div>
            <div class="flex items-center gap-2">
              <div :class="getStepClass(4)" class="w-10 h-10 rounded-full flex items-center justify-center">
                <span class="text-sm font-medium">4</span>
              </div>
              <div class="ml-2">
                <p class="text-sm font-medium">HOD</p>
                <p class="text-xs text-gray-500">{{ audit.hod_approver || 'Not assigned' }}</p>
              </div>
            </div>
          </div>

          <!-- Workflow Actions -->
          <div class="flex items-center gap-3 pt-4 border-t">
            <Button
              v-if="audit.status === 'Draft' && canSubmitPhysicalCount"
              variant="solid"
              @click="submitPhysicalCount"
              :loading="actionLoading"
            >
              <CheckCircle class="w-4 h-4 mr-2" />
              Submit Physical Count
            </Button>
            <Button
              v-if="audit.status === 'Physical Count Submitted' && canReview"
              variant="solid"
              @click="analystReview"
              :loading="actionLoading"
            >
              <CheckCircle class="w-4 h-4 mr-2" />
              Analyst Review
            </Button>
            <Button
              v-if="audit.status === 'Analyst Reviewed' && canApprove"
              variant="solid"
              @click="hodApprove"
              :loading="actionLoading"
            >
              <CheckCircle class="w-4 h-4 mr-2" />
              HOD Approve
            </Button>
            <span v-if="audit.status === 'HOD Approved'" class="text-green-600 font-medium flex items-center">
              <CheckCircle class="w-4 h-4 mr-2" />
              Fully Approved
            </span>
          </div>
        </div>

        <!-- Summary Stats -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Summary</h3>
          <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div class="text-center p-4 bg-gray-50 rounded-lg">
              <p class="text-2xl font-bold text-gray-900">{{ audit.total_items || 0 }}</p>
              <p class="text-sm text-gray-500">Total Items</p>
            </div>
            <div class="text-center p-4 bg-yellow-50 rounded-lg">
              <p class="text-2xl font-bold text-yellow-600">{{ audit.items_pending || 0 }}</p>
              <p class="text-sm text-gray-500">Pending</p>
            </div>
            <div class="text-center p-4 bg-green-50 rounded-lg">
              <p class="text-2xl font-bold text-green-600">{{ audit.items_verified_match || 0 }}</p>
              <p class="text-sm text-gray-500">Matched</p>
            </div>
            <div class="text-center p-4 bg-red-50 rounded-lg">
              <p class="text-2xl font-bold text-red-600">{{ audit.items_verified_discrepancy || 0 }}</p>
              <p class="text-sm text-gray-500">Discrepancy</p>
            </div>
            <div class="text-center p-4 bg-blue-50 rounded-lg">
              <p class="text-2xl font-bold text-blue-600">{{ audit.items_resolved || 0 }}</p>
              <p class="text-sm text-gray-500">Resolved</p>
            </div>
          </div>
          <div class="mt-4 pt-4 border-t text-center">
            <p class="text-sm text-gray-500">Total Variance Value</p>
            <p class="text-2xl font-bold" :class="audit.total_variance_value > 0 ? 'text-red-600' : 'text-green-600'">
              {{ formatCurrency(audit.total_variance_value || 0) }}
            </p>
          </div>
        </div>

        <!-- Stock Take Items ListView -->
        <div class="bg-white rounded-lg border p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Stock Take Items</h3>
            <div class="flex items-center gap-2">
              <select v-model="filterStatus" class="text-sm border rounded px-3 py-1.5">
                <option value="">All Items</option>
                <option value="Pending">Pending</option>
                <option value="Verified-Match">Matched</option>
                <option value="Verified-Discrepancy">Discrepancy</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>
          </div>

          <ListView
            :columns="[
              {
                label: '#',
                key: 'index',
                width: '60px',
              },
              {
                label: 'Item',
                key: 'item',
                width: '2fr',
              },
              {
                label: 'System Qty',
                key: 'system_quantity',
                width: '120px',
                align: 'right',
              },
              {
                label: 'Physical Qty',
                key: 'physical_quantity',
                width: '140px',
                align: 'right',
              },
              {
                label: 'Variance',
                key: 'variance',
                width: '120px',
                align: 'right',
              },
              {
                label: 'Status',
                key: 'status',
                width: '140px',
              },
              {
                label: 'Resolution',
                key: 'resolution',
                width: '140px',
              },
              {
                label: 'Actions',
                key: 'actions',
                width: '120px',
              },
            ]"
            :rows="filteredItems.map((item, index) => ({
              id: item.name,
              index: {
                label: (index + 1).toString(),
              },
              item: {
                label: item.item_code,
                description: item.item_description,
              },
              system_quantity: {
                label: (item.system_quantity || 0).toString(),
              },
              physical_quantity: {
                label: audit.status === 'Draft' ? '' : (item.physical_quantity !== null ? item.physical_quantity.toString() : '-'),
                editable: audit.status === 'Draft',
                value: item.physical_quantity,
              },
              variance: {
                label: (item.variance_quantity || 0).toString(),
                color: getVarianceColor(item.variance_quantity),
              },
              status: {
                label: item.verification_status || 'Pending',
                bg_color: getStatusBgColor(item.verification_status),
              },
              resolution: {
                label: item.resolution_type || '-',
                color: getResolutionColor(item.resolution_type),
              },
              actions: {
                item: item,
              },
            }))"
            :options="{
              onRowClick: (row) => console.log(row),
              selectable: false,
              showTooltip: true,
              resizeColumn: false,
            }"
            row-key="id"
          >
            <template #physical_quantity="{ item }">
              <div v-if="audit.status === 'Draft'" class="flex items-center justify-center">
                <FormControl
                  type="number"
                  :modelValue="item.value"
                  @update:modelValue="updatePhysicalQuantity(item.item, $event)"
                  placeholder="Count"
                  class="w-20 text-right"
                  :disabled="updatingItem === item.item.name"
                />
              </div>
              <div v-else class="text-right">
                {{ item.label }}
              </div>
            </template>

            <template #status="{ item }">
              <Badge :variant="getStatusVariant(item.label)">
                {{ item.label }}
              </Badge>
            </template>

            <template #actions="{ item }">
              <div class="flex items-center gap-1">
                <Button
                  v-if="item.item.resolution_type === 'Charge Staff' && !item.item.staff_charge_record"
                  variant="ghost"
                  size="sm"
                  @click="createStaffCharge(item.item)"
                  title="Create Staff Charge"
                  class="p-1"
                >
                  <UserMinus class="w-4 h-4 text-red-600" />
                </Button>
                <Button
                  v-if="item.item.staff_charge_record"
                  variant="ghost"
                  size="sm"
                  @click="viewStaffCharge(item.item.staff_charge_record)"
                  title="View Staff Charge"
                  class="p-1"
                >
                  <FileText class="w-4 h-4 text-blue-600" />
                </Button>
              </div>
            </template>

            <template #empty-state>
              <div class="text-center py-8 text-gray-500">
                No items found
              </div>
            </template>
          </ListView>
        </div>

        <!-- Notes -->
        <div v-if="audit.notes" class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Notes</h3>
          <div class="prose max-w-none text-gray-600" v-html="audit.notes"></div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Deadlines -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Deadlines</h3>
          <div class="space-y-4">
            <div>
              <p class="text-sm text-gray-500">Resolution Deadline</p>
              <p class="font-medium" :class="isOverdue(audit.resolution_deadline) ? 'text-red-600' : ''">
                {{ formatDate(audit.resolution_deadline) }}
                <span v-if="isOverdue(audit.resolution_deadline)" class="text-xs ml-2 bg-red-100 text-red-700 px-2 py-1 rounded">OVERDUE</span>
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Investigation Deadline</p>
              <p class="font-medium" :class="isOverdue(audit.investigation_deadline) ? 'text-red-600' : ''">
                {{ formatDate(audit.investigation_deadline) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Audit Info -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Stock Take Info</h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-500">Stock Take Type</span>
              <span class="font-medium">{{ audit.stock_take_type }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Warehouse</span>
              <span class="font-medium">{{ audit.warehouse }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Branch</span>
              <span class="font-medium">{{ audit.branch || '-' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Audit Date</span>
              <span class="font-medium">{{ formatDate(audit.audit_date) }}</span>
            </div>
          </div>
        </div>

        <!-- Approval Timeline -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Approval Timeline</h3>
          <div class="space-y-4">
            <div v-if="audit.status !== 'Draft'" class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <Check class="w-4 h-4 text-green-600" />
              </div>
              <div>
                <p class="font-medium text-sm">Data Imported</p>
                <p class="text-xs text-gray-500">{{ formatDateTime(audit.import_date) }}</p>
                <p class="text-xs text-gray-400">{{ audit.created_by }}</p>
              </div>
            </div>
            <div v-if="audit.physical_count_submitted_date" class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <Check class="w-4 h-4 text-green-600" />
              </div>
              <div>
                <p class="font-medium text-sm">Physical Count Submitted</p>
                <p class="text-xs text-gray-500">{{ formatDateTime(audit.physical_count_submitted_date) }}</p>
                <p class="text-xs text-gray-400">{{ audit.physical_count_submitted_by }}</p>
              </div>
            </div>
            <div v-if="audit.analyst_review_date" class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <Check class="w-4 h-4 text-green-600" />
              </div>
              <div>
                <p class="font-medium text-sm">Analyst Reviewed</p>
                <p class="text-xs text-gray-500">{{ formatDateTime(audit.analyst_review_date) }}</p>
                <p class="text-xs text-gray-400">{{ audit.stock_analyst }}</p>
              </div>
            </div>
            <div v-if="audit.hod_approval_date" class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <Check class="w-4 h-4 text-green-600" />
              </div>
              <div>
                <p class="font-medium text-sm">HOD Approved</p>
                <p class="text-xs text-gray-500">{{ formatDateTime(audit.hod_approval_date) }}</p>
                <p class="text-xs text-gray-400">{{ audit.hod_approver }}</p>
              </div>
            </div>
            <div v-if="audit.final_report_date" class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <Check class="w-4 h-4 text-green-600" />
              </div>
              <div>
                <p class="font-medium text-sm">Report Generated</p>
                <p class="text-xs text-gray-500">{{ formatDateTime(audit.final_report_date) }}</p>
              </div>
            </div>
            <div v-if="audit.status === 'Draft' && !audit.physical_count_submitted_date && !audit.analyst_review_date && !audit.hod_approval_date"
                 class="text-sm text-gray-500 text-center py-4">
              No actions yet
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Staff Charge Modal -->
    <Dialog v-model="showChargeModal" :options="{ title: 'Create Staff Charge' }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Employee to Charge</label>
            <FormControl
              type="select"
              v-model="chargeForm.employee"
              :options="userOptions"
              placeholder="Select employee"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Charge Reason</label>
            <FormControl
              type="textarea"
              v-model="chargeForm.reason"
              placeholder="Reason for the charge..."
              :rows="3"
            />
          </div>
          <div class="bg-gray-50 p-4 rounded-lg">
            <p class="text-sm"><strong>Item:</strong> {{ selectedItem?.item_code }} - {{ selectedItem?.item_description }}</p>
            <p class="text-sm"><strong>Variance:</strong> {{ selectedItem?.variance_quantity }} units</p>
            <p class="text-sm"><strong>Charge Amount:</strong> {{ formatCurrency(Math.abs(selectedItem?.variance_value || 0)) }}</p>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showChargeModal = false">
          Cancel
        </Button>
        <Button variant="solid" @click="confirmCreateCharge" :loading="chargeLoading">
          Create Charge
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Badge, Button, Dialog, FormControl, ListView } from "frappe-ui"
import { call } from "frappe-ui"
import {
	ArrowLeft,
	Check,
	CheckCircle,
	Download,
	Edit,
	Eye,
	FileText,
	Printer,
	Trash2,
	Upload,
	UserMinus,
} from "lucide-vue-next"
import AskAIButton from "@/components/AskAIButton.vue"
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const actionLoading = ref(false)
const chargeLoading = ref(false)
const audit = ref(null)
const filterStatus = ref("")
const showChargeModal = ref(false)
const selectedItem = ref(null)
const userOptions = ref([])
const chargeForm = ref({
	employee: "",
	reason: "",
})
const fileInput = ref(null)
const updatingItem = ref(null)

onMounted(async () => {
	await Promise.all([loadAudit(), loadUsers()])
})

async function loadAudit() {
	loading.value = true
	try {
		const doc = await call("frappe.client.get", {
			doctype: "Stock Take Audit",
			name: route.params.id,
		})
		audit.value = doc
	} catch (error) {
		console.error("Error loading audit:", error)
	} finally {
		loading.value = false
	}
}

async function loadUsers() {
	try {
		const users = await call("frappe.client.get_list", {
			doctype: "User",
			filters: { enabled: 1, user_type: "System User" },
			fields: ["name", "full_name"],
			limit_page_length: 0,
		})
		userOptions.value = users.map((u) => ({
			label: u.full_name || u.name,
			value: u.name,
		}))
	} catch (error) {
		console.error("Error loading users:", error)
	}
}

const statusVariant = computed(() => {
	const variants = {
		Draft: "subtle",
		"Physical Count Submitted": "yellow",
		"Analyst Reviewed": "blue",
		"HOD Approved": "green",
		"Under Investigation": "red",
	}
	return variants[audit.value?.status] || "subtle"
})

const canEdit = computed(() => {
	return !["HOD Approved", "Under Investigation"].includes(audit.value?.status)
})

const canSubmitPhysicalCount = computed(() => {
	if (!audit.value?.stock_take_items) return false
	// Check if all items have physical quantities
	const allHavePhysical = audit.value.stock_take_items.every(
		(item) => item.physical_quantity !== null,
	)
	// Check if signed copy is attached
	const hasSignedCopy = audit.value.signed_stock_take_copy
	return allHavePhysical && hasSignedCopy
})

const canReview = computed(() => {
	// Analyst can review if they have Stock Analyst role and status is Physical Count Submitted
	// Note: stock_analyst field gets set when review is performed, not before
	return audit.value?.status === "Physical Count Submitted"
})

const canApprove = computed(() => {
	// HOD can approve if status is Analyst Reviewed
	// Note: hod_approver field gets set when approval is performed, not before
	return audit.value?.status === "Analyst Reviewed"
})

const totalItems = computed(() => {
	return audit.value?.stock_take_items?.length || 0
})

const countedItems = computed(() => {
	if (!audit.value?.stock_take_items) return 0
	return audit.value.stock_take_items.filter(
		(item) =>
			item.physical_quantity !== null && item.physical_quantity !== undefined,
	).length
})

const allItemsHavePhysicalQty = computed(() => {
	if (!audit.value?.stock_take_items) return false
	return audit.value.stock_take_items.every(
		(item) =>
			item.physical_quantity !== null && item.physical_quantity !== undefined,
	)
})

const filteredItems = computed(() => {
	if (!audit.value?.stock_take_items) return []
	if (!filterStatus.value) return audit.value.stock_take_items
	return audit.value.stock_take_items.filter(
		(i) => i.verification_status === filterStatus.value,
	)
})

function getStepClass(step) {
	const completed = {
		1: audit.value?.status !== "Draft",
		2: audit.value?.physical_count_submitted,
		3: audit.value?.analyst_reviewed,
		4: audit.value?.hod_approved,
	}

	if (completed[step]) {
		return "bg-green-500 text-white"
	}

	// Check if it's the current step
	const prevCompleted = step === 1 ? true : completed[step - 1]
	if (prevCompleted && !completed[step]) {
		return "bg-blue-500 text-white"
	}

	return "bg-gray-200 text-gray-500"
}

function getRowClass(item) {
	if (item.verification_status === "Verified-Match") return "bg-green-50"
	if (item.verification_status === "Verified-Discrepancy") return "bg-red-50"
	if (item.verification_status === "Resolved") return "bg-blue-50"
	return ""
}

function getStatusVariant(status) {
	const variants = {
		"Verified-Match": "green",
		"Verified-Discrepancy": "red",
		Resolved: "blue",
		Pending: "yellow",
	}
	return variants[status] || "subtle"
}

function getVarianceClass(variance) {
	if (!variance || variance === 0) return "text-green-600 font-medium"
	return "text-red-600 font-medium"
}

function getVarianceColor(variance) {
	if (!variance || variance === 0) return "green"
	return "red"
}

function getStatusBgColor(status) {
	const colors = {
		"Verified-Match": "bg-surface-green-3",
		"Verified-Discrepancy": "bg-surface-red-5",
		Resolved: "bg-surface-blue-3",
		Pending: "bg-surface-yellow-3",
	}
	return colors[status] || "bg-surface-gray-3"
}

function getResolutionColor(resolution) {
	const colors = {
		"Stock Amendment": "blue",
		"Charge Staff": "red",
		"Write-off": "gray",
		"Under Investigation": "yellow",
	}
	return colors[resolution] || "gray"
}

function isOverdue(date) {
	if (!date) return false
	return new Date(date) < new Date()
}

function formatDate(date) {
	if (!date) return "-"
	return new Date(date).toLocaleDateString()
}

function formatDateTime(datetime) {
	if (!datetime) return "-"
	return new Date(datetime).toLocaleString()
}

function formatCurrency(value) {
	if (value === null || value === undefined) return "KES 0"
	return new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
	}).format(value)
}

async function submitPhysicalCount() {
	actionLoading.value = true
	try {
		await call("run_doc_method", {
			dt: "Stock Take Audit",
			dn: route.params.id,
			method: "submit_physical_count",
		})
		await loadAudit()
	} catch (error) {
		console.error("Error:", error)
		alert(error.message)
	} finally {
		actionLoading.value = false
	}
}

async function analystReview() {
	actionLoading.value = true
	try {
		await call("run_doc_method", {
			dt: "Stock Take Audit",
			dn: route.params.id,
			method: "analyst_review",
		})
		await loadAudit()
	} catch (error) {
		console.error("Error:", error)
		alert(error.message)
	} finally {
		actionLoading.value = false
	}
}

async function hodApprove() {
	actionLoading.value = true
	try {
		await call("run_doc_method", {
			dt: "Stock Take Audit",
			dn: route.params.id,
			method: "hod_approve",
		})
		await loadAudit()
	} catch (error) {
		console.error("Error:", error)
		alert(error.message)
	} finally {
		actionLoading.value = false
	}
}

function createStaffCharge(item) {
	selectedItem.value = item
	chargeForm.value = {
		employee: "",
		reason: `Stock discrepancy for ${item.item_code}`,
	}
	showChargeModal.value = true
}

async function confirmCreateCharge() {
	if (!chargeForm.value.employee) {
		alert("Please select an employee")
		return
	}

	chargeLoading.value = true
	try {
		await call("run_doc_method", {
			dt: "Stock Take Audit",
			dn: route.params.id,
			method: "create_staff_charge",
			args: {
				item_row_name: selectedItem.value.name,
				employee: chargeForm.value.employee,
				charge_reason: chargeForm.value.reason,
			},
		})
		showChargeModal.value = false
		await loadAudit()
	} catch (error) {
		console.error("Error:", error)
		alert(error.message)
	} finally {
		chargeLoading.value = false
	}
}

function viewStaffCharge(name) {
	// Navigate to staff charge record
	window.open(`/app/staff-charge-record/${name}`, "_blank")
}

function goBack() {
	router.push("/inventory-audit/stock-take")
}

function editAudit() {
	router.push(`/inventory-audit/stock-take/${route.params.id}/edit`)
}

function printAuditReport() {
	window.open(
		`/api/method/frappe.utils.print_format.download_pdf?doctype=Stock Take Audit&name=${route.params.id}&format=Stock Take Audit Daily Summary`,
		"_blank",
	)
}

function exportToExcel() {
	// Implementation for Excel export
	console.log("Export to Excel")
}

async function handleFileUpload(event) {
	const file = event.target.files[0]
	if (!file) return

	// Validate file type
	const allowedTypes = [
		"application/pdf",
		"application/msword",
		"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		"image/jpeg",
		"image/png",
	]
	if (!allowedTypes.includes(file.type)) {
		alert("Please upload a PDF, DOC, DOCX, JPG, or PNG file")
		return
	}

	// Validate file size (max 10MB)
	const maxSize = 10 * 1024 * 1024 // 10MB
	if (file.size > maxSize) {
		alert("File size must be less than 10MB")
		return
	}

	try {
		// Create FormData for file upload
		const formData = new FormData()
		formData.append("file", file)
		formData.append("is_private", "1")
		formData.append("doctype", "Stock Take Audit")
		formData.append("docname", route.params.id)
		formData.append("fieldname", "signed_stock_take_copy")

		// Upload file using fetch
		const response = await fetch("/api/method/upload_file", {
			method: "POST",
			body: formData,
			headers: {
				Accept: "application/json",
				// Don't set Content-Type header - let browser set it with boundary
			},
		})

		if (!response.ok) {
			const errorText = await response.text()
			throw new Error(`Upload failed: ${response.status} ${errorText}`)
		}

		const result = await response.json()

		if (result.message && result.message.file_url) {
			// Update the audit record with the file URL
			await call("frappe.client.set_value", {
				doctype: "Stock Take Audit",
				name: route.params.id,
				fieldname: "signed_stock_take_copy",
				value: result.message.file_url,
			})

			// Reload audit data
			await loadAudit()
		} else {
			throw new Error("Invalid response from server")
		}
	} catch (error) {
		console.error("Error uploading file:", error)
		alert("Error uploading file: " + error.message)
	}
}

function getFileName(fileUrl) {
	if (!fileUrl) return ""
	return fileUrl.split("/").pop()
}

function viewAttachment(fileUrl) {
	if (fileUrl) {
		window.open(fileUrl, "_blank")
	}
}

async function removeAttachment() {
	if (confirm("Are you sure you want to remove the signed stock take copy?")) {
		try {
			await call("frappe.client.set_value", {
				doctype: "Stock Take Audit",
				name: route.params.id,
				fieldname: "signed_stock_take_copy",
				value: "",
			})
			await loadAudit()
		} catch (error) {
			console.error("Error removing attachment:", error)
			alert("Error removing attachment: " + error.message)
		}
	}
}

async function updatePhysicalQuantity(item, newValue) {
	if (updatingItem.value) return // Prevent multiple simultaneous updates

	updatingItem.value = item.name
	try {
		// Update the item in the child table
		await call("frappe.client.set_value", {
			doctype: "Stock Take Audit Item",
			name: item.name,
			fieldname: "physical_quantity",
			value: Number.parseFloat(newValue) || 0,
		})

		// Reload audit to get updated calculations
		await loadAudit()
	} catch (error) {
		console.error("Error updating physical quantity:", error)
		alert("Error updating physical quantity: " + error.message)
	} finally {
		updatingItem.value = null
	}
}

function getStockTakeContext() {
	if (!audit.value) return null

	const items = audit.value.items || []
	const variances = items.filter(item => item.variance !== 0)
	const totalValue = items.reduce((sum, item) => sum + (item.system_quantity * item.rate), 0)
	const varianceValue = variances.reduce((sum, item) => sum + (item.variance * item.rate), 0)

	return {
		page_type: 'stock-take',
		page_title: `Stock Take: ${audit.value.name}`,
		stock_take_type: audit.value.stock_take_type,
		warehouse: audit.value.warehouse,
		audit_date: audit.value.audit_date,
		status: audit.value.status,
		total_items: items.length,
		items_with_variance: variances.length,
		total_system_value: totalValue,
		total_variance_value: Math.abs(varianceValue),
		variance_percentage: totalValue > 0 ? Math.abs(varianceValue / totalValue * 100) : 0,
		high_variance_items: variances
			.filter(item => Math.abs(item.variance) > 10)
			.map(item => ({
				item_code: item.item_code,
				item_name: item.item_name,
				system_quantity: item.system_quantity,
				physical_quantity: item.physical_quantity,
				variance: item.variance,
				variance_value: Math.abs(item.variance * item.rate),
				rate: item.rate
			})),
		risk_indicators: {
			large_variances: variances.filter(item => Math.abs(item.variance) > 50).length,
			high_value_variances: variances.filter(item => Math.abs(item.variance * item.rate) > 1000).length,
			negative_variances: variances.filter(item => item.variance < 0).length,
			positive_variances: variances.filter(item => item.variance > 0).length
		},
		summary: {
			description: `Stock take audit for ${audit.value.warehouse} conducted on ${audit.value.audit_date}`,
			key_findings: [
				`${variances.length} out of ${items.length} items have variances`,
				`Total variance value: ${Math.abs(varianceValue).toFixed(2)}`,
				`Variance percentage: ${(totalValue > 0 ? Math.abs(varianceValue / totalValue * 100) : 0).toFixed(2)}%`
			]
		}
	}
}
</script>