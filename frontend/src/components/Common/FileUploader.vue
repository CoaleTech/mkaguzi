<template>
  <div class="w-full">
    <!-- Upload Area -->
    <div
      :class="[
        'relative border-2 border-dashed rounded-lg p-6 transition-colors',
        isDragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400',
        disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
      ]"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop"
      @click="disabled ? null : $refs.fileInput.click()"
    >
      <input
        ref="fileInput"
        type="file"
        :multiple="multiple"
        :accept="accept"
        class="hidden"
        @change="handleFileSelect"
      />

      <!-- Upload Content -->
      <div class="text-center">
        <div class="flex justify-center mb-4">
          <div
            :class="[
              'rounded-full p-3',
              isDragOver ? 'bg-blue-100' : 'bg-gray-100'
            ]"
          >
            <UploadIcon
              :class="[
                'h-8 w-8',
                isDragOver ? 'text-blue-600' : 'text-gray-400'
              ]"
            />
          </div>
        </div>

        <div class="space-y-2">
          <p class="text-lg font-medium text-gray-900">
            {{ isDragOver ? 'Drop files here' : 'Upload files' }}
          </p>
          <p class="text-sm text-gray-500">
            {{ multiple ? 'Select multiple files' : 'Select a file' }} or drag and drop
          </p>
          <p v-if="accept" class="text-xs text-gray-400">
            Accepted formats: {{ accept }}
          </p>
          <p v-if="maxSize" class="text-xs text-gray-400">
            Maximum file size: {{ formatFileSize(maxSize) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Selected Files -->
    <div v-if="files.length > 0" class="mt-4 space-y-2">
      <h4 class="text-sm font-medium text-gray-700">Selected Files</h4>

      <div
        v-for="(file, index) in files"
        :key="index"
        class="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-3"
      >
        <div class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <FileIcon class="h-8 w-8 text-gray-400" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-gray-900 truncate">
              {{ file.name }}
            </p>
            <p class="text-xs text-gray-500">
              {{ formatFileSize(file.size) }}
            </p>
          </div>
        </div>

        <!-- File Status -->
        <div class="flex items-center space-x-2">
          <!-- Progress Bar -->
          <div v-if="file.status === 'uploading'" class="flex-1 max-w-24">
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${file.progress || 0}%` }"
              ></div>
            </div>
          </div>

          <!-- Status Icon -->
          <div class="flex-shrink-0">
            <CheckCircleIcon
              v-if="file.status === 'completed'"
              class="h-5 w-5 text-green-500"
            />
            <XCircleIcon
              v-if="file.status === 'error'"
              class="h-5 w-5 text-red-500"
            />
            <LoaderIcon
              v-if="file.status === 'uploading'"
              class="h-5 w-5 text-blue-500 animate-spin"
            />
          </div>

          <!-- Remove Button -->
          <Button
            variant="ghost"
            size="sm"
            @click="removeFile(index)"
            :disabled="file.status === 'uploading'"
          >
            <XIcon class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>

    <!-- Upload Actions -->
    <div v-if="files.length > 0" class="mt-4 flex justify-end space-x-2">
      <Button variant="outline" @click="clearAll">
        Clear All
      </Button>
      <Button
        @click="uploadFiles"
        :disabled="!canUpload"
        :loading="isUploading"
      >
        {{ uploadButtonText }}
      </Button>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import {
	CheckCircleIcon,
	FileIcon,
	LoaderIcon,
	UploadIcon,
	XCircleIcon,
	XIcon,
} from "lucide-vue-next"
import { computed, ref } from "vue"

// Props
const props = defineProps({
	multiple: {
		type: Boolean,
		default: false,
	},
	accept: {
		type: String,
		default: "",
	},
	maxSize: {
		type: Number,
		default: 0, // in bytes, 0 means no limit
	},
	maxFiles: {
		type: Number,
		default: 0, // 0 means no limit
	},
	disabled: {
		type: Boolean,
		default: false,
	},
	uploadButtonText: {
		type: String,
		default: "Upload Files",
	},
	autoUpload: {
		type: Boolean,
		default: false,
	},
})

// Emits
const emit = defineEmits([
	"files-selected",
	"file-removed",
	"upload-start",
	"upload-progress",
	"upload-complete",
	"upload-error",
])

// Reactive state
const isDragOver = ref(false)
const files = ref([])
const isUploading = ref(false)

// Computed properties
const canUpload = computed(() => {
	return (
		files.value.length > 0 &&
		files.value.every((file) => file.status !== "uploading") &&
		!props.disabled
	)
})

// Methods
const handleFileSelect = (event) => {
	const selectedFiles = Array.from(event.target.files)
	addFiles(selectedFiles)
}

const handleDrop = (event) => {
	isDragOver.value = false
	const droppedFiles = Array.from(event.dataTransfer.files)
	addFiles(droppedFiles)
}

const addFiles = (newFiles) => {
	const validFiles = []

	for (const file of newFiles) {
		// Validate file
		const validation = validateFile(file)
		if (validation.valid) {
			validFiles.push({
				file,
				name: file.name,
				size: file.size,
				type: file.type,
				status: "pending",
				progress: 0,
				error: null,
			})
		} else {
			// Handle invalid file
			emit("upload-error", {
				file,
				error: validation.error,
			})
		}
	}

	// Check max files limit
	if (
		props.maxFiles > 0 &&
		files.value.length + validFiles.length > props.maxFiles
	) {
		emit("upload-error", {
			error: `Maximum ${props.maxFiles} files allowed`,
		})
		return
	}

	// Add valid files
	if (props.multiple) {
		files.value.push(...validFiles)
	} else {
		files.value = validFiles.slice(0, 1)
	}

	emit("files-selected", files.value)

	// Auto upload if enabled
	if (props.autoUpload && validFiles.length > 0) {
		uploadFiles()
	}
}

const validateFile = (file) => {
	// Check file size
	if (props.maxSize > 0 && file.size > props.maxSize) {
		return {
			valid: false,
			error: `File size exceeds maximum limit of ${formatFileSize(props.maxSize)}`,
		}
	}

	// Check file type
	if (props.accept) {
		const acceptedTypes = props.accept.split(",").map((type) => type.trim())
		const fileType = file.type.toLowerCase()
		const fileName = file.name.toLowerCase()

		const isAccepted = acceptedTypes.some((type) => {
			if (type.startsWith(".")) {
				return fileName.endsWith(type)
			} else {
				return fileType.includes(type.replace("*", ""))
			}
		})

		if (!isAccepted) {
			return {
				valid: false,
				error: `File type not accepted. Accepted types: ${props.accept}`,
			}
		}
	}

	return { valid: true }
}

const removeFile = (index) => {
	const removedFile = files.value.splice(index, 1)[0]
	emit("file-removed", removedFile)
}

const clearAll = () => {
	files.value = []
	emit("files-selected", [])
}

const uploadFiles = async () => {
	if (!canUpload.value) return

	isUploading.value = true
	emit("upload-start", files.value)

	try {
		// Upload each file
		for (const fileItem of files.value) {
			if (fileItem.status === "completed") continue

			fileItem.status = "uploading"
			fileItem.progress = 0

			try {
				// Simulate upload progress (replace with actual upload logic)
				await simulateUpload(fileItem)

				fileItem.status = "completed"
				fileItem.progress = 100

				emit("upload-progress", {
					file: fileItem,
					progress: 100,
				})
			} catch (error) {
				fileItem.status = "error"
				fileItem.error = error.message

				emit("upload-error", {
					file: fileItem,
					error: error.message,
				})
			}
		}

		emit("upload-complete", files.value)
	} catch (error) {
		emit("upload-error", { error: error.message })
	} finally {
		isUploading.value = false
	}
}

const simulateUpload = async (fileItem) => {
	// Simulate upload with progress
	return new Promise((resolve, reject) => {
		let progress = 0
		const interval = setInterval(() => {
			progress += Math.random() * 20
			if (progress >= 100) {
				progress = 100
				clearInterval(interval)
				resolve()
			}
			fileItem.progress = Math.round(progress)
			emit("upload-progress", {
				file: fileItem,
				progress: fileItem.progress,
			})
		}, 200)
	})
}

const formatFileSize = (bytes) => {
	if (bytes === 0) return "0 Bytes"

	const k = 1024
	const sizes = ["Bytes", "KB", "MB", "GB"]
	const i = Math.floor(Math.log(bytes) / Math.log(k))

	return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}
</script>