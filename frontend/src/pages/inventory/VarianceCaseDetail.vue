<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <Button variant="ghost" @click="goBack">
          <ArrowLeft class="w-5 h-5" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ varianceCase?.name || 'Loading...' }}</h1>
          <p class="text-gray-500 mt-1">Inventory Variance Case</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Badge :variant="statusVariant">{{ varianceCase?.status }}</Badge>
        <Badge :variant="priorityVariant">{{ varianceCase?.priority }} Priority</Badge>
        <AskAIButton contextType="variance-case" :contextData="getVarianceCaseContext()" />
        <Button variant="outline" @click="editCase">
          <Edit class="w-4 h-4 mr-2" />
          Edit
        </Button>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="varianceCase" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Variance Overview -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Variance Details</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <span class="text-sm text-gray-500">Item Code</span>
              <p class="font-medium font-mono">{{ varianceCase.item_code }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Item Name</span>
              <p class="font-medium">{{ varianceCase.item_name || '-' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Warehouse</span>
              <p class="font-medium">{{ varianceCase.warehouse || '-' }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Branch</span>
              <p class="font-medium">{{ varianceCase.branch || '-' }}</p>
            </div>
          </div>
          
          <!-- Variance Breakdown -->
          <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="p-4 bg-blue-50 rounded-lg">
              <span class="text-sm text-blue-700">System Qty</span>
              <p class="text-2xl font-bold text-blue-800">{{ varianceCase.system_qty || 0 }}</p>
            </div>
            <div class="p-4 bg-green-50 rounded-lg">
              <span class="text-sm text-green-700">Counted Qty</span>
              <p class="text-2xl font-bold text-green-800">{{ varianceCase.counted_qty || 0 }}</p>
            </div>
            <div :class="['p-4 rounded-lg', varianceQtyClass]">
              <span :class="['text-sm', varianceTextClass]">Variance Qty</span>
              <p :class="['text-2xl font-bold', varianceTextClass]">
                {{ varianceCase.variance_qty > 0 ? '+' : '' }}{{ varianceCase.variance_qty || 0 }}
              </p>
            </div>
            <div :class="['p-4 rounded-lg', varianceQtyClass]">
              <span :class="['text-sm', varianceTextClass]">Variance Value</span>
              <p :class="['text-2xl font-bold', varianceTextClass]">
                {{ formatCurrency(varianceCase.variance_value) }}
              </p>
            </div>
          </div>

          <!-- Variance Type -->
          <div class="mt-4 p-4 border rounded-lg">
            <div class="flex items-center gap-3">
              <div :class="['w-10 h-10 rounded-full flex items-center justify-center', varianceIconBg]">
                <TrendingDown v-if="varianceCase.variance_qty < 0" class="w-5 h-5 text-red-600" />
                <TrendingUp v-else class="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p class="font-medium">
                  {{ varianceCase.variance_qty < 0 ? 'Shortage' : 'Overage' }}
                </p>
                <p class="text-sm text-gray-500">
                  {{ Math.abs(varianceCase.variance_qty) }} units 
                  {{ varianceCase.variance_qty < 0 ? 'less' : 'more' }} than system
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Investigation Section -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Investigation</h3>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Root Cause</label>
              <div class="p-3 bg-gray-50 rounded-lg">
                {{ varianceCase.root_cause || 'Not yet determined' }}
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Investigation Notes</label>
              <div class="p-3 bg-gray-50 rounded-lg whitespace-pre-wrap">
                {{ varianceCase.investigation_notes || 'No investigation notes' }}
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Assigned Investigator</label>
                <div class="p-3 bg-gray-50 rounded-lg">
                  {{ varianceCase.assigned_to || 'Not assigned' }}
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                <div class="p-3 bg-gray-50 rounded-lg">
                  {{ formatDate(varianceCase.due_date) || 'Not set' }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Resolution Section -->
        <div v-if="varianceCase.status === 'Resolved' || varianceCase.resolution_type" class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Resolution</h3>
          
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Resolution Type</label>
                <Badge :variant="getResolutionVariant(varianceCase.resolution_type)">
                  {{ varianceCase.resolution_type || '-' }}
                </Badge>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Resolved Date</label>
                <p class="font-medium">{{ formatDate(varianceCase.resolved_date) || '-' }}</p>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Resolution Notes</label>
              <div class="p-3 bg-gray-50 rounded-lg whitespace-pre-wrap">
                {{ varianceCase.resolution_notes || 'No resolution notes' }}
              </div>
            </div>

            <div v-if="varianceCase.adjustment_entry" class="p-4 border rounded-lg">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <FileText class="w-5 h-5 text-blue-600" />
                  <div>
                    <p class="font-medium">Stock Adjustment Entry</p>
                    <p class="text-sm text-gray-500">{{ varianceCase.adjustment_entry }}</p>
                  </div>
                </div>
                <Button variant="outline" size="sm" @click="viewAdjustment">
                  <ExternalLink class="w-4 h-4 mr-1" />
                  View
                </Button>
              </div>
            </div>
          </div>
        </div>

        <!-- Evidence Section -->
        <div class="bg-white rounded-lg border p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Evidence & Attachments</h3>
            <Button variant="outline" size="sm" @click="addEvidence">
              <Upload class="w-4 h-4 mr-2" />
              Add Evidence
            </Button>
          </div>
          
          <div v-if="evidence.length > 0" class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div 
              v-for="item in evidence" 
              :key="item.name"
              class="p-4 border rounded-lg"
            >
              <div class="flex items-center gap-3 mb-2">
                <Image v-if="isImage(item.file_url)" class="w-5 h-5 text-gray-500" />
                <FileText v-else class="w-5 h-5 text-gray-500" />
                <span class="text-sm font-medium truncate">{{ item.file_name }}</span>
              </div>
              <div class="flex items-center gap-2">
                <Button variant="ghost" size="sm" @click="previewFile(item)">
                  <Eye class="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm" @click="downloadFile(item)">
                  <Download class="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            <Camera class="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No evidence attached yet</p>
          </div>
        </div>

        <!-- Comments/Activity -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Activity</h3>
          
          <div v-if="comments.length > 0" class="space-y-4">
            <div 
              v-for="comment in comments" 
              :key="comment.name"
              class="flex gap-3"
            >
              <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <User class="w-4 h-4 text-blue-600" />
              </div>
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-medium text-sm">{{ comment.comment_by }}</span>
                  <span class="text-xs text-gray-500">{{ formatDateTime(comment.creation) }}</span>
                </div>
                <p class="text-sm text-gray-700">{{ comment.content }}</p>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-4 text-gray-500">
            <p>No activity yet</p>
          </div>

          <!-- Add Comment -->
          <div class="mt-4 pt-4 border-t">
            <div class="flex gap-2">
              <FormControl
                type="textarea"
                v-model="newComment"
                placeholder="Add a comment..."
                :rows="2"
                class="flex-1"
              />
              <Button variant="solid" @click="addComment" :disabled="!newComment.trim()">
                <Send class="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Quick Actions -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
          <div class="space-y-2">
            <Button 
              v-if="varianceCase.status === 'Open'"
              variant="solid" 
              class="w-full justify-start"
              @click="startInvestigation"
            >
              <Search class="w-4 h-4 mr-2" />
              Start Investigation
            </Button>
            <Button 
              v-if="varianceCase.status === 'Under Investigation'"
              variant="solid" 
              class="w-full justify-start"
              @click="resolveCase"
            >
              <CheckCircle class="w-4 h-4 mr-2" />
              Mark as Resolved
            </Button>
            <Button 
              v-if="varianceCase.status === 'Under Investigation'"
              variant="outline" 
              class="w-full justify-start"
              @click="createAdjustment"
            >
              <FileText class="w-4 h-4 mr-2" />
              Create Stock Adjustment
            </Button>
            <Button 
              v-if="varianceCase.status === 'Under Investigation'"
              variant="outline" 
              class="w-full justify-start text-orange-600"
              @click="writeOff"
            >
              <AlertTriangle class="w-4 h-4 mr-2" />
              Write Off
            </Button>
          </div>
        </div>

        <!-- Linked Documents -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Linked Documents</h3>
          <div class="space-y-3">
            <div 
              v-if="varianceCase.stock_take_session"
              class="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100"
              @click="viewSession"
            >
              <div class="flex items-center gap-2">
                <ClipboardList class="w-4 h-4 text-gray-500" />
                <span class="text-sm font-medium">Stock Take Session</span>
              </div>
              <p class="text-sm text-gray-500 mt-1">{{ varianceCase.stock_take_session }}</p>
            </div>
            
            <div 
              v-if="varianceCase.audit_plan"
              class="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100"
              @click="viewAuditPlan"
            >
              <div class="flex items-center gap-2">
                <Calendar class="w-4 h-4 text-gray-500" />
                <span class="text-sm font-medium">Audit Plan</span>
              </div>
              <p class="text-sm text-gray-500 mt-1">{{ varianceCase.audit_plan }}</p>
            </div>
          </div>
        </div>

        <!-- Timeline -->
        <div class="bg-white rounded-lg border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
          <div class="space-y-4">
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Plus class="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <p class="font-medium text-sm">Created</p>
                <p class="text-xs text-gray-500">{{ formatDateTime(varianceCase.creation) }}</p>
              </div>
            </div>
            
            <div v-if="varianceCase.investigation_start_date" class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center flex-shrink-0">
                <Search class="w-4 h-4 text-yellow-600" />
              </div>
              <div>
                <p class="font-medium text-sm">Investigation Started</p>
                <p class="text-xs text-gray-500">{{ formatDate(varianceCase.investigation_start_date) }}</p>
              </div>
            </div>
            
            <div v-if="varianceCase.resolved_date" class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <CheckCircle class="w-4 h-4 text-green-600" />
              </div>
              <div>
                <p class="font-medium text-sm">Resolved</p>
                <p class="text-xs text-gray-500">{{ formatDate(varianceCase.resolved_date) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, FormControl } from "frappe-ui"
import { call } from "frappe-ui"
import {
	AlertTriangle,
	ArrowLeft,
	Calendar,
	Camera,
	CheckCircle,
	ClipboardList,
	Download,
	Edit,
	ExternalLink,
	Eye,
	FileText,
	Image,
	Plus,
	Search,
	Send,
	TrendingDown,
	TrendingUp,
	Upload,
	User,
} from "lucide-vue-next"
import AskAIButton from "@/components/AskAIButton.vue"
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const varianceCase = ref(null)
const evidence = ref([])
const comments = ref([])
const newComment = ref("")

onMounted(async () => {
	await Promise.all([loadVarianceCase(), loadEvidence(), loadComments()])
})

async function loadVarianceCase() {
	loading.value = true
	try {
		const doc = await call("frappe.client.get", {
			doctype: "Inventory Variance Case",
			name: route.params.id,
		})
		varianceCase.value = doc
	} catch (error) {
		console.error("Error loading variance case:", error)
	} finally {
		loading.value = false
	}
}

async function loadEvidence() {
	try {
		const files = await call("frappe.client.get_list", {
			doctype: "File",
			filters: {
				attached_to_doctype: "Inventory Variance Case",
				attached_to_name: route.params.id,
			},
			fields: ["name", "file_name", "file_url"],
		})
		evidence.value = files
	} catch (error) {
		console.error("Error loading evidence:", error)
	}
}

async function loadComments() {
	try {
		const result = await call("frappe.client.get_list", {
			doctype: "Comment",
			filters: {
				reference_doctype: "Inventory Variance Case",
				reference_name: route.params.id,
				comment_type: "Comment",
			},
			fields: ["name", "content", "comment_by", "creation"],
			order_by: "creation desc",
		})
		comments.value = result
	} catch (error) {
		console.error("Error loading comments:", error)
	}
}

const statusVariant = computed(() => {
	const variants = {
		Open: "warning",
		"Under Investigation": "outline",
		Resolved: "success",
		"Written Off": "subtle",
		Closed: "subtle",
	}
	return variants[varianceCase.value?.status] || "subtle"
})

const priorityVariant = computed(() => {
	const variants = {
		Critical: "solid",
		High: "warning",
		Medium: "outline",
		Low: "subtle",
	}
	return variants[varianceCase.value?.priority] || "subtle"
})

const varianceQtyClass = computed(() => {
	if (!varianceCase.value) return "bg-gray-50"
	return varianceCase.value.variance_qty < 0 ? "bg-red-50" : "bg-green-50"
})

const varianceTextClass = computed(() => {
	if (!varianceCase.value) return "text-gray-700"
	return varianceCase.value.variance_qty < 0 ? "text-red-700" : "text-green-700"
})

const varianceIconBg = computed(() => {
	if (!varianceCase.value) return "bg-gray-100"
	return varianceCase.value.variance_qty < 0 ? "bg-red-100" : "bg-green-100"
})

function formatDate(date) {
	if (!date) return "-"
	return new Date(date).toLocaleDateString()
}

function formatDateTime(datetime) {
	if (!datetime) return "-"
	return new Date(datetime).toLocaleString()
}

function formatCurrency(value) {
	if (value === null || value === undefined) return "-"
	return new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
	}).format(value)
}

function getResolutionVariant(type) {
	const variants = {
		Adjusted: "success",
		"Written Off": "warning",
		"No Action Required": "subtle",
		Transferred: "outline",
	}
	return variants[type] || "subtle"
}

function isImage(url) {
	if (!url) return false
	return /\.(jpg|jpeg|png|gif|webp)$/i.test(url)
}

function goBack() {
	router.push("/inventory-audit/variance-cases")
}

function editCase() {
	router.push(`/inventory-audit/variance-cases/${route.params.id}/edit`)
}

function viewSession() {
	if (varianceCase.value?.stock_take_session) {
		router.push(
			`/inventory-audit/sessions/${varianceCase.value.stock_take_session}`,
		)
	}
}

function viewAuditPlan() {
	if (varianceCase.value?.audit_plan) {
		router.push(`/inventory-audit/plans/${varianceCase.value.audit_plan}`)
	}
}

function viewAdjustment() {
	if (varianceCase.value?.adjustment_entry) {
		window.open(
			`/app/stock-entry/${varianceCase.value.adjustment_entry}`,
			"_blank",
		)
	}
}

async function startInvestigation() {
	try {
		await call("frappe.client.set_value", {
			doctype: "Inventory Variance Case",
			name: route.params.id,
			fieldname: {
				status: "Under Investigation",
				investigation_start_date: new Date().toISOString().split("T")[0],
			},
		})
		await loadVarianceCase()
	} catch (error) {
		console.error("Error starting investigation:", error)
	}
}

async function resolveCase() {
	// Navigate to resolution form
	router.push(`/inventory-audit/variance-cases/${route.params.id}/resolve`)
}

function createAdjustment() {
	// Navigate to create stock adjustment
	window.open(
		`/app/stock-entry/new-stock-entry-1?from_variance_case=${route.params.id}`,
		"_blank",
	)
}

async function writeOff() {
	if (!confirm("Are you sure you want to write off this variance?")) return

	try {
		await call("frappe.client.set_value", {
			doctype: "Inventory Variance Case",
			name: route.params.id,
			fieldname: {
				status: "Written Off",
				resolution_type: "Written Off",
				resolved_date: new Date().toISOString().split("T")[0],
			},
		})
		await loadVarianceCase()
	} catch (error) {
		console.error("Error writing off:", error)
	}
}

function addEvidence() {
	// Trigger file upload
	console.log("Add evidence - implement file upload")
}

function previewFile(item) {
	window.open(item.file_url, "_blank")
}

function downloadFile(item) {
	const a = document.createElement("a")
	a.href = item.file_url
	a.download = item.file_name
	a.click()
}

async function addComment() {
	if (!newComment.value.trim()) return

	try {
		await call("frappe.client.insert", {
			doc: {
				doctype: "Comment",
				comment_type: "Comment",
				reference_doctype: "Inventory Variance Case",
				reference_name: route.params.id,
				content: newComment.value,
			},
		})
		newComment.value = ""
		await loadComments()
	} catch (error) {
		console.error("Error adding comment:", error)
	}
}

function getVarianceCaseContext() {
	if (!varianceCase.value) return null

	const varianceValue = Math.abs(varianceCase.value.variance_quantity * varianceCase.value.rate)
	const isPositive = varianceCase.value.variance_quantity > 0
	const isHighValue = varianceValue > 1000

	return {
		page_type: 'variance-case',
		page_title: `Variance Case: ${varianceCase.value.name}`,
		item_code: varianceCase.value.item_code,
		item_name: varianceCase.value.item_name,
		warehouse: varianceCase.value.warehouse,
		branch: varianceCase.value.branch,
		status: varianceCase.value.status,
		priority: varianceCase.value.priority,
		system_quantity: varianceCase.value.system_quantity,
		physical_quantity: varianceCase.value.physical_quantity,
		variance_quantity: varianceCase.value.variance_quantity,
		variance_value: varianceValue,
		rate: varianceCase.value.rate,
		variance_type: isPositive ? 'positive' : 'negative',
		is_high_value: isHighValue,
		reported_date: varianceCase.value.reported_date,
		investigation_status: varianceCase.value.investigation_status,
		root_cause: varianceCase.value.root_cause,
		corrective_action: varianceCase.value.corrective_action,
		responsible_person: varianceCase.value.responsible_person,
		target_resolution_date: varianceCase.value.target_resolution_date,
		actual_resolution_date: varianceCase.value.actual_resolution_date,
		evidence_count: evidence.value.length,
		comments_count: comments.value.length,
		risk_assessment: {
			financial_impact: varianceValue,
			operational_impact: isHighValue ? 'high' : 'medium',
			urgency: varianceCase.value.priority === 'High' ? 'high' : varianceCase.value.priority === 'Medium' ? 'medium' : 'low',
			likelihood_of_fraud: varianceCase.value.suspected_fraud ? 'high' : 'low'
		},
		investigation_details: {
			has_evidence: evidence.value.length > 0,
			has_comments: comments.value.length > 0,
			has_root_cause: !!varianceCase.value.root_cause,
			has_corrective_action: !!varianceCase.value.corrective_action,
			is_overdue: varianceCase.value.target_resolution_date && new Date(varianceCase.value.target_resolution_date) < new Date()
		},
		summary: {
			description: `${isPositive ? 'Positive' : 'Negative'} variance of ${Math.abs(varianceCase.value.variance_quantity)} units for ${varianceCase.value.item_name} in ${varianceCase.value.warehouse}`,
			key_findings: [
				`Variance Value: $${varianceValue.toFixed(2)}`,
				`Priority: ${varianceCase.value.priority}`,
				`Status: ${varianceCase.value.status}`,
				`Evidence Available: ${evidence.value.length} items`
			]
		}
	}
}
</script>
