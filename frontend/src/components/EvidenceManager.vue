<template>
  <div class="evidence-manager">
    <!-- Header -->
    <div class="evidence-header">
      <div class="header-content">
        <h2 class="evidence-title">
          <FileTextIcon class="title-icon" />
          Evidence Management
        </h2>
        <p class="evidence-description">
          Manage evidence attachments, approvals, and document versions
        </p>
      </div>
      <div class="header-actions">
        <Button variant="outline" @click="refreshEvidence">
          <RefreshCwIcon class="h-4 w-4 mr-2" />
          Refresh
        </Button>
        <Button @click="showUploadModal = true">
          <UploadIcon class="h-4 w-4 mr-2" />
          Upload Evidence
        </Button>
      </div>
    </div>

    <!-- Evidence Statistics -->
    <div class="evidence-stats">
      <div class="stat-card">
        <div class="stat-icon total">
          <FileTextIcon class="h-6 w-6" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ evidenceStore.evidenceStats.total }}</div>
          <div class="stat-label">Total Evidence</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon pending">
          <ClockIcon class="h-6 w-6" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ evidenceStore.evidenceStats.pending }}</div>
          <div class="stat-label">Pending Approval</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon approved">
          <CheckCircleIcon class="h-6 w-6" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ evidenceStore.evidenceStats.approved }}</div>
          <div class="stat-label">Approved</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon attachments">
          <PaperclipIcon class="h-6 w-6" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ evidenceStore.evidenceStats.attachments }}</div>
          <div class="stat-label">File Attachments</div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="evidence-filters">
      <div class="filter-group">
        <Input
          v-model="searchQuery"
          placeholder="Search evidence..."
          class="search-input"
        >
          <template #prefix>
            <SearchIcon class="h-4 w-4" />
          </template>
        </Input>
      </div>

      <div class="filter-group">
        <Select
          v-model="statusFilter"
          :options="statusOptions"
          placeholder="Filter by status"
          class="filter-select"
        />
      </div>

      <div class="filter-group">
        <Select
          v-model="typeFilter"
          :options="evidenceStore.evidenceTypes"
          placeholder="Filter by type"
          class="filter-select"
        />
      </div>

      <div class="filter-group">
        <Select
          v-model="findingFilter"
          :options="findingOptions"
          placeholder="Filter by finding"
          class="filter-select"
        />
      </div>
    </div>

    <!-- Evidence List -->
    <div class="evidence-list">
      <div class="list-header">
        <div class="bulk-actions" v-if="selectedEvidence.length > 0">
          <Checkbox
            :checked="selectedEvidence.length === filteredEvidence.length"
            @change="toggleSelectAll"
          />
          <span class="selection-count">{{ selectedEvidence.length }} selected</span>
          <Button variant="outline" size="sm" @click="bulkApprove" v-if="canBulkApprove">
            <CheckIcon class="h-4 w-4 mr-1" />
            Approve
          </Button>
          <Button variant="outline" size="sm" @click="bulkReject" v-if="canBulkReject">
            <XIcon class="h-4 w-4 mr-1" />
            Reject
          </Button>
          <Button variant="outline" size="sm" @click="bulkDownload">
            <DownloadIcon class="h-4 w-4 mr-1" />
            Download
          </Button>
        </div>
        <div v-else class="list-title">
          {{ filteredEvidence.length }} Evidence Items
        </div>
      </div>

      <div class="evidence-grid">
        <div
          v-for="evidence in filteredEvidence"
          :key="evidence.name"
          class="evidence-card"
          :class="{ 'selected': selectedEvidence.includes(evidence.name) }"
          @click="selectEvidence(evidence.name)"
        >
          <div class="card-header">
            <Checkbox
              :checked="selectedEvidence.includes(evidence.name)"
              @change="toggleEvidence(evidence.name)"
              @click.stop
            />
            <Badge :variant="getStatusVariant(evidence.approval_status)">
              {{ evidence.approval_status || 'Pending' }}
            </Badge>
          </div>

          <div class="card-content">
            <div class="evidence-icon">
              <component :is="getFileIconComponent(evidence.file_type)" class="h-8 w-8" />
            </div>

            <div class="evidence-info">
              <h4 class="evidence-name">{{ evidence.evidence_name }}</h4>
              <p class="evidence-type">{{ evidence.evidence_type }}</p>
              
              <div class="evidence-meta">
                <div class="meta-item">
                  <UserIcon class="h-3 w-3" />
                  <span>{{ evidence.uploaded_by }}</span>
                </div>
                <div class="meta-item">
                  <CalendarIcon class="h-3 w-3" />
                  <span>{{ formatDate(evidence.upload_date) }}</span>
                </div>
                <div v-if="evidence.file_size" class="meta-item">
                  <HardDriveIcon class="h-3 w-3" />
                  <span>{{ evidenceStore.formatFileSize(evidence.file_size) }}</span>
                </div>
              </div>

              <p v-if="evidence.description" class="evidence-description">
                {{ evidence.description }}
              </p>

              <div v-if="evidence.tags" class="evidence-tags">
                <Badge v-for="tag in evidence.tags.split(',')" :key="tag" variant="secondary" size="sm">
                  {{ tag.trim() }}
                </Badge>
              </div>
            </div>
          </div>

          <div class="card-actions">
            <Button variant="ghost" size="sm" @click.stop="previewEvidence(evidence)">
              <EyeIcon class="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" @click.stop="downloadEvidence(evidence)">
              <DownloadIcon class="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              @click.stop="approveEvidence(evidence)"
              v-if="evidence.approval_status === 'Pending' && canApprove"
            >
              <CheckIcon class="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" @click.stop="showEvidenceDetails(evidence)">
              <MoreVerticalIcon class="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredEvidence.length === 0 && !evidenceStore.loading" class="empty-state">
        <FileIcon class="empty-icon" />
        <h3>No Evidence Found</h3>
        <p>Upload evidence files to get started.</p>
        <Button @click="showUploadModal = true">
          <UploadIcon class="h-4 w-4 mr-2" />
          Upload Evidence
        </Button>
      </div>

      <!-- Loading State -->
      <div v-if="evidenceStore.loading" class="loading-state">
        <Loader2Icon class="loading-icon" />
        <p>Loading evidence...</p>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">Upload Evidence</h3>
          <Button variant="ghost" size="sm" @click="showUploadModal = false">
            <XIcon class="h-4 w-4" />
          </Button>
        </div>

        <form @submit.prevent="uploadEvidence" class="upload-form">
          <div class="form-section">
            <label class="form-label">Evidence Information</label>
            
            <div class="form-group">
              <label class="field-label">Evidence Name *</label>
              <Input
                v-model="newEvidence.evidence_name"
                placeholder="Enter evidence name"
                required
              />
            </div>

            <div class="form-group">
              <label class="field-label">Evidence Type *</label>
              <Select
                v-model="newEvidence.evidence_type"
                :options="evidenceStore.evidenceTypes"
                placeholder="Select evidence type"
                required
              />
            </div>

            <div class="form-group">
              <label class="field-label">Related Finding</label>
              <Select
                v-model="newEvidence.finding_id"
                :options="findingOptions"
                placeholder="Select related finding"
              />
            </div>

            <div class="form-group">
              <label class="field-label">Description</label>
              <textarea
                v-model="newEvidence.description"
                placeholder="Enter description"
                class="form-textarea"
                rows="3"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="field-label">Tags</label>
              <Input
                v-model="newEvidence.tags"
                placeholder="Enter tags separated by commas"
              />
            </div>

            <div class="form-group">
              <div class="checkbox-group">
                <Checkbox v-model="newEvidence.is_confidential" />
                <label class="checkbox-label">Mark as confidential</label>
              </div>
            </div>
          </div>

          <div class="form-section">
            <label class="form-label">File Upload</label>
            
            <div class="file-upload-area" @drop="handleFileDrop" @dragover.prevent @dragenter.prevent>
              <div v-if="!selectedFile" class="upload-placeholder">
                <UploadIcon class="upload-icon" />
                <p class="upload-text">
                  Drag and drop a file here, or click to browse
                </p>
                <p class="upload-hint">
                  Supported formats: PDF, DOC, XLS, JPG, PNG, MP4, etc.
                </p>
                <Button variant="outline" @click="$refs.fileInput.click()" type="button">
                  Browse Files
                </Button>
              </div>

              <div v-else class="file-preview">
                <div class="file-info">
                  <component :is="getFileIconComponent(selectedFile.type)" class="h-8 w-8" />
                  <div class="file-details">
                    <div class="file-name">{{ selectedFile.name }}</div>
                    <div class="file-size">{{ evidenceStore.formatFileSize(selectedFile.size) }}</div>
                  </div>
                  <Button variant="ghost" size="sm" @click="clearSelectedFile" type="button">
                    <XIcon class="h-4 w-4" />
                  </Button>
                </div>

                <div v-if="uploadProgress.progress > 0" class="upload-progress">
                  <div class="progress-bar">
                    <div
                      class="progress-fill"
                      :style="{ width: uploadProgress.progress + '%' }"
                    ></div>
                  </div>
                  <span class="progress-text">{{ Math.round(uploadProgress.progress) }}%</span>
                </div>
              </div>

              <input
                ref="fileInput"
                type="file"
                @change="handleFileSelect"
                class="file-input"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.gif,.mp4,.mp3,.txt,.csv"
              />
            </div>
          </div>

          <div class="form-actions">
            <Button variant="outline" @click="showUploadModal = false" type="button">
              Cancel
            </Button>
            <Button type="submit" :disabled="!selectedFile || uploading">
              <Loader2Icon v-if="uploading" class="h-4 w-4 mr-2 spinning" />
              <UploadIcon v-else class="h-4 w-4 mr-2" />
              {{ uploading ? 'Uploading...' : 'Upload Evidence' }}
            </Button>
          </div>
        </form>
      </div>
    </div>

    <!-- Evidence Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay">
      <div class="modal-container large">
        <div class="modal-header">
          <h3 class="modal-title">Evidence Details</h3>
          <Button variant="ghost" size="sm" @click="showDetailsModal = false">
            <XIcon class="h-4 w-4" />
          </Button>
        </div>

        <div v-if="currentEvidence" class="evidence-details">
          <div class="details-grid">
            <div class="detail-section">
              <h4>Basic Information</h4>
              <div class="detail-rows">
                <div class="detail-row">
                  <span class="detail-label">Name:</span>
                  <span class="detail-value">{{ currentEvidence.evidence_name }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Type:</span>
                  <span class="detail-value">{{ currentEvidence.evidence_type }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Status:</span>
                  <Badge :variant="getStatusVariant(currentEvidence.approval_status)">
                    {{ currentEvidence.approval_status }}
                  </Badge>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Finding:</span>
                  <span class="detail-value">{{ currentEvidence.finding_name || 'N/A' }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>File Information</h4>
              <div class="detail-rows">
                <div class="detail-row">
                  <span class="detail-label">File Name:</span>
                  <span class="detail-value">{{ currentEvidence.file_name || 'N/A' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">File Size:</span>
                  <span class="detail-value">
                    {{ currentEvidence.file_size ? evidenceStore.formatFileSize(currentEvidence.file_size) : 'N/A' }}
                  </span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">File Type:</span>
                  <span class="detail-value">{{ currentEvidence.file_type || 'N/A' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Confidential:</span>
                  <Badge :variant="currentEvidence.is_confidential ? 'warning' : 'secondary'">
                    {{ currentEvidence.is_confidential ? 'Yes' : 'No' }}
                  </Badge>
                </div>
              </div>
            </div>
          </div>

          <div class="detail-section full-width">
            <h4>Description</h4>
            <p class="description-text">
              {{ currentEvidence.description || 'No description provided.' }}
            </p>
          </div>

          <div class="detail-section full-width">
            <h4>Approval Information</h4>
            <div class="approval-info">
              <div v-if="currentEvidence.approved_by" class="approval-row">
                <span class="approval-label">Approved By:</span>
                <span class="approval-value">{{ currentEvidence.approved_by }}</span>
              </div>
              <div v-if="currentEvidence.approved_date" class="approval-row">
                <span class="approval-label">Approved Date:</span>
                <span class="approval-value">{{ formatDateTime(currentEvidence.approved_date) }}</span>
              </div>
            </div>
          </div>

          <div class="detail-actions">
            <Button v-if="currentEvidence.file_url" variant="outline" @click="downloadEvidence(currentEvidence)">
              <DownloadIcon class="h-4 w-4 mr-2" />
              Download
            </Button>
            <Button
              v-if="currentEvidence.approval_status === 'Pending' && canApprove"
              @click="approveEvidence(currentEvidence)"
            >
              <CheckIcon class="h-4 w-4 mr-2" />
              Approve
            </Button>
            <Button
              v-if="currentEvidence.approval_status === 'Pending' && canApprove"
              variant="outline"
              @click="rejectEvidence(currentEvidence)"
            >
              <XIcon class="h-4 w-4 mr-2" />
              Reject
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useEvidenceStore } from "@/stores/evidence"
import { Badge, Button, Checkbox, Input, Select } from "frappe-ui"
import {
	CalendarIcon,
	CheckCircleIcon,
	CheckIcon,
	ClockIcon,
	DownloadIcon,
	EyeIcon,
	FileIcon,
	FileTextIcon,
	HardDriveIcon,
	Loader2Icon,
	MoreVerticalIcon,
	PaperclipIcon,
	RefreshCwIcon,
	SearchIcon,
	UploadIcon,
	UserIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, onMounted, ref, watch } from "vue"

// Props
const props = defineProps({
	findingId: {
		type: String,
		default: null,
	},
	readonly: {
		type: Boolean,
		default: false,
	},
})

// Store
const evidenceStore = useEvidenceStore()

// Reactive state
const searchQuery = ref("")
const statusFilter = ref("")
const typeFilter = ref("")
const findingFilter = ref("")
const selectedEvidence = ref([])
const showUploadModal = ref(false)
const showDetailsModal = ref(false)
const currentEvidence = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadProgress = ref({ progress: 0, status: "idle" })

// Form data
const newEvidence = ref({
	evidence_name: "",
	evidence_type: "",
	finding_id: props.findingId || "",
	description: "",
	tags: "",
	is_confidential: false,
})

// Options
const statusOptions = [
	{ label: "All Status", value: "" },
	{ label: "Pending", value: "Pending" },
	{ label: "Approved", value: "Approved" },
	{ label: "Rejected", value: "Rejected" },
]

// Mock finding options (replace with actual data)
const findingOptions = ref([
	{ label: "Finding 1 - Control Weakness", value: "finding-1" },
	{ label: "Finding 2 - Data Integrity Issue", value: "finding-2" },
	{ label: "Finding 3 - Compliance Gap", value: "finding-3" },
])

// Computed properties
const filteredEvidence = computed(() => {
	let evidence = props.findingId
		? evidenceStore.evidenceByFinding(props.findingId)
		: evidenceStore.evidence

	if (searchQuery.value) {
		const search = searchQuery.value.toLowerCase()
		evidence = evidence.filter(
			(e) =>
				e.evidence_name?.toLowerCase().includes(search) ||
				e.description?.toLowerCase().includes(search) ||
				e.tags?.toLowerCase().includes(search),
		)
	}

	if (statusFilter.value) {
		evidence = evidence.filter((e) => e.approval_status === statusFilter.value)
	}

	if (typeFilter.value) {
		evidence = evidence.filter((e) => e.evidence_type === typeFilter.value)
	}

	if (findingFilter.value) {
		evidence = evidence.filter((e) => e.finding_id === findingFilter.value)
	}

	return evidence
})

const canApprove = computed(() => {
	// Add permission logic here
	return true
})

const canBulkApprove = computed(() => {
	return (
		canApprove.value &&
		selectedEvidence.value.some((id) => {
			const evidence = evidenceStore.getEvidenceById(id)
			return evidence?.approval_status === "Pending"
		})
	)
})

const canBulkReject = computed(() => {
	return (
		canApprove.value &&
		selectedEvidence.value.some((id) => {
			const evidence = evidenceStore.getEvidenceById(id)
			return evidence?.approval_status === "Pending"
		})
	)
})

// Methods
const refreshEvidence = async () => {
	const filters = props.findingId ? { finding_id: props.findingId } : {}
	await evidenceStore.fetchEvidence(filters)
}

const selectEvidence = (evidenceId) => {
	const index = selectedEvidence.value.indexOf(evidenceId)
	if (index > -1) {
		selectedEvidence.value.splice(index, 1)
	} else {
		selectedEvidence.value.push(evidenceId)
	}
}

const toggleEvidence = (evidenceId) => {
	selectEvidence(evidenceId)
}

const toggleSelectAll = () => {
	if (selectedEvidence.value.length === filteredEvidence.value.length) {
		selectedEvidence.value = []
	} else {
		selectedEvidence.value = filteredEvidence.value.map((e) => e.name)
	}
}

const handleFileSelect = (event) => {
	const file = event.target.files[0]
	if (file) {
		if (evidenceStore.isValidFileType(file)) {
			selectedFile.value = file
			if (!newEvidence.value.evidence_name) {
				newEvidence.value.evidence_name = file.name.replace(/\.[^/.]+$/, "")
			}
		} else {
			alert("Invalid file type. Please select a supported file format.")
		}
	}
}

const handleFileDrop = (event) => {
	event.preventDefault()
	const file = event.dataTransfer.files[0]
	if (file) {
		if (evidenceStore.isValidFileType(file)) {
			selectedFile.value = file
			if (!newEvidence.value.evidence_name) {
				newEvidence.value.evidence_name = file.name.replace(/\.[^/.]+$/, "")
			}
		} else {
			alert("Invalid file type. Please select a supported file format.")
		}
	}
}

const clearSelectedFile = () => {
	selectedFile.value = null
	if (refs.fileInput) {
		refs.fileInput.value = ""
	}
}

const uploadEvidence = async () => {
	if (!selectedFile.value) return

	uploading.value = true
	uploadProgress.value = { progress: 0, status: "uploading" }

	try {
		await evidenceStore.uploadEvidence(newEvidence.value, selectedFile.value)
		showUploadModal.value = false
		resetUploadForm()
	} catch (error) {
		console.error("Error uploading evidence:", error)
		alert("Failed to upload evidence. Please try again.")
	} finally {
		uploading.value = false
		uploadProgress.value = { progress: 0, status: "idle" }
	}
}

const resetUploadForm = () => {
	newEvidence.value = {
		evidence_name: "",
		evidence_type: "",
		finding_id: props.findingId || "",
		description: "",
		tags: "",
		is_confidential: false,
	}
	selectedFile.value = null
}

const previewEvidence = (evidence) => {
	if (evidence.file_url) {
		window.open(evidence.file_url, "_blank")
	}
}

const downloadEvidence = (evidence) => {
	if (evidence.file_url) {
		const link = document.createElement("a")
		link.href = evidence.file_url
		link.download = evidence.file_name || "evidence"
		document.body.appendChild(link)
		link.click()
		document.body.removeChild(link)
	}
}

const approveEvidence = async (evidence) => {
	try {
		await evidenceStore.approveEvidence(evidence.name, {
			comments: "Approved via Evidence Manager",
		})
	} catch (error) {
		console.error("Error approving evidence:", error)
	}
}

const rejectEvidence = async (evidence) => {
	try {
		await evidenceStore.rejectEvidence(evidence.name, {
			comments: "Rejected via Evidence Manager",
			reason: "Quality issues",
		})
	} catch (error) {
		console.error("Error rejecting evidence:", error)
	}
}

const showEvidenceDetails = async (evidence) => {
	currentEvidence.value = evidence
	await evidenceStore.fetchEvidenceDetails(evidence.name)
	showDetailsModal.value = true
}

const bulkApprove = async () => {
	try {
		for (const evidenceId of selectedEvidence.value) {
			const evidence = evidenceStore.getEvidenceById(evidenceId)
			if (evidence?.approval_status === "Pending") {
				await evidenceStore.approveEvidence(evidenceId, {
					comments: "Bulk approved",
				})
			}
		}
		selectedEvidence.value = []
	} catch (error) {
		console.error("Error bulk approving evidence:", error)
	}
}

const bulkReject = async () => {
	try {
		for (const evidenceId of selectedEvidence.value) {
			const evidence = evidenceStore.getEvidenceById(evidenceId)
			if (evidence?.approval_status === "Pending") {
				await evidenceStore.rejectEvidence(evidenceId, {
					comments: "Bulk rejected",
					reason: "Review required",
				})
			}
		}
		selectedEvidence.value = []
	} catch (error) {
		console.error("Error bulk rejecting evidence:", error)
	}
}

const bulkDownload = () => {
	selectedEvidence.value.forEach((evidenceId) => {
		const evidence = evidenceStore.getEvidenceById(evidenceId)
		if (evidence) {
			downloadEvidence(evidence)
		}
	})
}

// Utility methods
const getStatusVariant = (status) => {
	const variants = {
		Pending: "warning",
		Approved: "success",
		Rejected: "danger",
	}
	return variants[status] || "secondary"
}

const getFileIconComponent = (fileType) => {
	return evidenceStore.getFileIcon(fileType) + "Icon"
}

const formatDate = (date) => {
	if (!date) return "N/A"
	return new Date(date).toLocaleDateString()
}

const formatDateTime = (dateTime) => {
	if (!dateTime) return "N/A"
	return new Date(dateTime).toLocaleString()
}

// Watchers
watch(searchQuery, () => {
	// Reset selection when search changes
	selectedEvidence.value = []
})

// Lifecycle
onMounted(async () => {
	await Promise.all([refreshEvidence(), evidenceStore.fetchEvidenceTypes()])
})
</script>

<style scoped>
.evidence-manager {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.evidence-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header-content .evidence-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.title-icon {
  color: var(--primary-color);
}

.evidence-description {
  color: var(--text-muted);
  margin: 0.5rem 0 0 0;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.evidence-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.total { background: #f3f4f6; color: #6b7280; }
.stat-icon.pending { background: #fef3c7; color: #d97706; }
.stat-icon.approved { background: #dcfce7; color: #16a34a; }
.stat-icon.attachments { background: #dbeafe; color: #2563eb; }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.evidence-filters {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.evidence-list {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
}

.list-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--background-color);
}

.bulk-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.selection-count {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.list-title {
  font-weight: 600;
  color: var(--text-color);
}

.evidence-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1rem;
  padding: 1.5rem;
}

.evidence-card {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.evidence-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.evidence-card.selected {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-content {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.evidence-icon {
  flex-shrink: 0;
  width: 3rem;
  height: 3rem;
  background: var(--background-color);
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.evidence-info {
  flex: 1;
  min-width: 0;
}

.evidence-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
  word-wrap: break-word;
}

.evidence-type {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0 0 0.5rem 0;
}

.evidence-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.evidence-description {
  font-size: 0.875rem;
  color: var(--text-color);
  margin: 0.5rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.evidence-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.card-actions {
  display: flex;
  justify-content: end;
  gap: 0.25rem;
}

.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon,
.loading-icon {
  font-size: 3rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: var(--text-muted);
  margin: 0 0 1.5rem 0;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: var(--card-background);
  border-radius: 0.5rem;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-container.large {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.upload-form {
  padding: 1.5rem;
}

.form-section {
  margin-bottom: 2rem;
}

.form-label {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 1rem;
  display: block;
}

.form-group {
  margin-bottom: 1rem;
}

.field-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.5rem;
  display: block;
}

.form-textarea {
  width: 100%;
  min-height: 80px;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  resize: vertical;
  font-family: inherit;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-label {
  font-size: 0.875rem;
  color: var(--text-color);
}

.file-upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  transition: border-color 0.15s ease;
  position: relative;
}

.file-upload-area:hover {
  border-color: var(--primary-color);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  font-size: 3rem;
  color: var(--text-muted);
}

.upload-text {
  font-size: 1rem;
  color: var(--text-color);
  margin: 0;
}

.upload-hint {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0;
}

.file-input {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.file-preview {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 0.375rem;
}

.file-details {
  flex: 1;
  text-align: left;
}

.file-name {
  font-weight: 500;
  color: var(--text-color);
}

.file-size {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  flex: 1;
  height: 0.5rem;
  background: var(--background-color);
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.875rem;
  color: var(--text-color);
  min-width: 3rem;
}

.form-actions {
  display: flex;
  justify-content: end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

/* Evidence details styles */
.evidence-details {
  padding: 1.5rem;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-section.full-width {
  grid-column: 1 / -1;
}

.detail-section h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.detail-rows {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-weight: 500;
  color: var(--text-color);
  min-width: 120px;
}

.detail-value {
  color: var(--text-muted);
  text-align: right;
  flex: 1;
}

.description-text {
  color: var(--text-color);
  line-height: 1.5;
  margin: 0;
}

.approval-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.approval-row {
  display: flex;
  justify-content: space-between;
}

.approval-label {
  font-weight: 500;
  color: var(--text-color);
}

.approval-value {
  color: var(--text-muted);
}

.detail-actions {
  display: flex;
  justify-content: end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive design */
@media (max-width: 768px) {
  .evidence-filters {
    grid-template-columns: 1fr;
  }

  .evidence-grid {
    grid-template-columns: 1fr;
    padding: 1rem;
  }

  .details-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .modal-container {
    width: 95%;
    max-height: 95vh;
  }

  .card-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .evidence-icon {
    align-self: center;
  }
}
</style>