<template>
  <div class="file-upload-step">
    <!-- Template Selection -->
    <div class="template-section">
      <h3 class="section-title">Choose Import Template</h3>
      <p class="section-description">
        Select a template to import your data or upload a custom file
      </p>
      
      <div class="template-grid">
        <div
          v-for="template in templates"
          :key="template.id"
          class="template-card"
          :class="{ 'selected': selectedTemplate?.id === template.id }"
          @click="selectTemplate(template)"
        >
          <div class="template-icon">
            <FileTextIcon class="h-8 w-8" />
          </div>
          <div class="template-info">
            <h4 class="template-name">{{ template.name }}</h4>
            <p class="template-description">{{ template.description }}</p>
            <div class="template-stats">
              <span class="field-count">
                {{ template.required_fields.length + template.optional_fields.length }} fields
              </span>
              <span class="separator">•</span>
              <span class="required-count">
                {{ template.required_fields.length }} required
              </span>
            </div>
          </div>
          <div class="template-actions">
            <Button
              variant="ghost"
              size="sm"
              @click.stop="downloadTemplate(template.id)"
              :loading="loading && downloadingTemplate === template.id"
            >
              <DownloadIcon class="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- File Upload Section -->
    <div class="upload-section">
      <h3 class="section-title">Upload Data File</h3>
      <p class="section-description">
        Upload your CSV or Excel file containing the data to import
      </p>

      <!-- Drag & Drop Area -->
      <div
        class="upload-area"
        :class="{
          'drag-over': isDragOver,
          'has-file': uploadedFile,
          'loading': loading
        }"
        @dragenter.prevent="handleDragEnter"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".csv,.xlsx,.xls"
          @change="handleFileSelect"
          class="file-input"
        />
        
        <div v-if="loading" class="upload-loading">
          <div class="spinner"></div>
          <p>Processing file...</p>
        </div>
        
        <div v-else-if="uploadedFile" class="file-info">
          <FileCheckIcon class="h-12 w-12 text-green-500" />
          <div class="file-details">
            <h4>{{ uploadedFile.name }}</h4>
            <p>{{ formatFileSize(uploadedFile.size) }} • {{ uploadedFile.rows }} rows</p>
          </div>
          <Button variant="ghost" size="sm" @click.stop="removeFile">
            <XIcon class="h-4 w-4" />
          </Button>
        </div>
        
        <div v-else class="upload-prompt">
          <UploadIcon class="h-12 w-12 text-gray-400" />
          <h4>Drop your file here or click to browse</h4>
          <p>Supports CSV, Excel (.xlsx, .xls) files up to 10MB</p>
          <div class="upload-requirements">
            <span class="requirement">
              <CheckIcon class="h-4 w-4 text-green-500" />
              Maximum 10,000 rows
            </span>
            <span class="requirement">
              <CheckIcon class="h-4 w-4 text-green-500" />
              UTF-8 encoding recommended
            </span>
          </div>
        </div>
      </div>

      <!-- File Preview -->
      <div v-if="filePreview && !loading" class="file-preview">
        <h4 class="preview-title">File Preview</h4>
        <div class="preview-table-container">
          <table class="preview-table">
            <thead>
              <tr>
                <th v-for="(header, index) in filePreview.headers" :key="index">
                  {{ header }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rowIndex) in filePreview.rows" :key="rowIndex">
                <td v-for="(cell, cellIndex) in row" :key="cellIndex">
                  {{ cell || '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="preview-note">
          Showing {{ filePreview.rows.length }} of {{ filePreview.total_rows }} rows
        </p>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-message">
      <AlertCircleIcon class="h-5 w-5 text-red-500" />
      <span>{{ error }}</span>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import {
	AlertCircleIcon,
	CheckIcon,
	DownloadIcon,
	FileCheckIcon,
	FileTextIcon,
	UploadIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, ref } from "vue"

const props = defineProps({
	templates: {
		type: Array,
		default: () => [],
	},
	loading: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits([
	"template-selected",
	"file-uploaded",
	"template-downloaded",
])

// State
const selectedTemplate = ref(null)
const uploadedFile = ref(null)
const filePreview = ref(null)
const isDragOver = ref(false)
const downloadingTemplate = ref(null)
const error = ref(null)
const fileInput = ref(null)

// Methods
const selectTemplate = (template) => {
	selectedTemplate.value = template
	error.value = null
	emit("template-selected", template)
}

const downloadTemplate = async (templateId) => {
	try {
		downloadingTemplate.value = templateId
		emit("template-downloaded", templateId)
	} catch (err) {
		error.value = "Failed to download template"
		console.error("Template download error:", err)
	} finally {
		downloadingTemplate.value = null
	}
}

const triggerFileInput = () => {
	if (!props.loading) {
		fileInput.value?.click()
	}
}

const handleDragEnter = (e) => {
	e.preventDefault()
	isDragOver.value = true
}

const handleDragOver = (e) => {
	e.preventDefault()
	isDragOver.value = true
}

const handleDragLeave = (e) => {
	e.preventDefault()
	if (!e.relatedTarget || !e.currentTarget.contains(e.relatedTarget)) {
		isDragOver.value = false
	}
}

const handleDrop = (e) => {
	e.preventDefault()
	isDragOver.value = false

	const files = Array.from(e.dataTransfer.files)
	if (files.length > 0) {
		processFile(files[0])
	}
}

const handleFileSelect = (e) => {
	const files = Array.from(e.target.files)
	if (files.length > 0) {
		processFile(files[0])
	}
}

const processFile = async (file) => {
	try {
		error.value = null

		// Validate file
		if (!validateFile(file)) return

		// Create file preview
		const preview = await createFilePreview(file)

		uploadedFile.value = {
			name: file.name,
			size: file.size,
			type: file.type,
			rows: preview.total_rows,
			file: file,
		}

		filePreview.value = preview

		emit("file-uploaded", {
			file: file,
			preview: preview,
			template: selectedTemplate.value,
		})
	} catch (err) {
		error.value = err.message || "Failed to process file"
		console.error("File processing error:", err)
	}
}

const validateFile = (file) => {
	const maxSize = 10 * 1024 * 1024 // 10MB
	const allowedTypes = [
		"text/csv",
		"application/vnd.ms-excel",
		"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	]

	if (file.size > maxSize) {
		error.value = "File size must be less than 10MB"
		return false
	}

	if (
		!allowedTypes.includes(file.type) &&
		!file.name.match(/\.(csv|xlsx?|xls)$/i)
	) {
		error.value = "File must be CSV or Excel format"
		return false
	}

	return true
}

const createFilePreview = (file) => {
	return new Promise((resolve, reject) => {
		const reader = new FileReader()

		reader.onload = (e) => {
			try {
				const content = e.target.result
				let preview

				if (file.type === "text/csv" || file.name.endsWith(".csv")) {
					preview = parseCSVPreview(content)
				} else {
					// For Excel files, we'd need a library like xlsx
					// For now, mock the preview
					preview = {
						headers: ["Column 1", "Column 2", "Column 3"],
						rows: [
							["Sample", "Data", "Row 1"],
							["Sample", "Data", "Row 2"],
						],
						total_rows: 100,
					}
				}

				resolve(preview)
			} catch (err) {
				reject(new Error("Failed to parse file"))
			}
		}

		reader.onerror = () => reject(new Error("Failed to read file"))
		reader.readAsText(file)
	})
}

const parseCSVPreview = (content) => {
	const lines = content.split("\n").filter((line) => line.trim())
	const headers =
		lines[0]?.split(",").map((h) => h.trim().replace(/"/g, "")) || []
	const rows = lines
		.slice(1, 6)
		.map((line) => line.split(",").map((cell) => cell.trim().replace(/"/g, "")))

	return {
		headers,
		rows,
		total_rows: lines.length - 1,
	}
}

const removeFile = () => {
	uploadedFile.value = null
	filePreview.value = null
	error.value = null

	if (fileInput.value) {
		fileInput.value.value = ""
	}
}

const formatFileSize = (bytes) => {
	if (bytes === 0) return "0 Bytes"
	const k = 1024
	const sizes = ["Bytes", "KB", "MB", "GB"]
	const i = Math.floor(Math.log(bytes) / Math.log(k))
	return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}
</script>

<style scoped>
.file-upload-step {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.section-description {
  color: var(--text-muted);
  margin: 0 0 1.5rem 0;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.template-card {
  border: 2px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.template-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.template-card.selected {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.template-icon {
  color: var(--primary-color);
}

.template-info {
  flex: 1;
}

.template-name {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.template-description {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0 0 0.75rem 0;
}

.template-stats {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.separator {
  opacity: 0.5;
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 0.5rem;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.upload-area:hover {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.upload-area.drag-over {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.upload-area.has-file {
  border-style: solid;
  border-color: var(--success-color);
  background: #f0fdf4;
}

.upload-area.loading {
  cursor: not-allowed;
  opacity: 0.7;
}

.file-input {
  display: none;
}

.upload-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.file-details h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.file-details p {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0.25rem 0 0 0;
}

.upload-prompt h4 {
  font-weight: 600;
  color: var(--text-color);
  margin: 1rem 0 0.5rem 0;
}

.upload-prompt p {
  color: var(--text-muted);
  margin: 0 0 1.5rem 0;
}

.upload-requirements {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.file-preview {
  margin-top: 1.5rem;
}

.preview-title {
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.preview-table-container {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  margin-bottom: 0.5rem;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table th,
.preview-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.preview-table th {
  background: var(--background-color);
  font-weight: 600;
  color: var(--text-color);
}

.preview-table td {
  color: var(--text-muted);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-note {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  color: #dc2626;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .template-grid {
    grid-template-columns: 1fr;
  }
  
  .upload-area {
    padding: 2rem 1rem;
  }
  
  .file-info {
    flex-direction: column;
    text-align: center;
  }
  
  .upload-requirements {
    align-items: flex-start;
  }
}
</style>